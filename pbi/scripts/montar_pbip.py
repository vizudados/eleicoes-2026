#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""montar_pbip — monta o Eleicoes.Report (painel Eleições 2026) a partir das declarações em
pbi/scripts/paginas/*.py. Idempotente. Adaptado do montador da casa (Vizu Dados).

    python -X utf8 pbi/scripts/montar_pbip.py              # SIMULAÇÃO: plano + conferência; grava nada
    python -X utf8 pbi/scripts/montar_pbip.py --aplicar    # backup datado + grava + manifesto + pbir validate
    python -X utf8 pbi/scripts/montar_pbip.py --conferir   # disco × plano

DECLARAÇÕES: cada módulo pbi/scripts/paginas/<nome>.py (que não começa por "_") define declarar(ctx) e devolve uma
lista de Pagina / Visual / Bookmark / Recurso / Interacao. `ctx` traz o inventário do modelo (ctx.tem_medida, ctx.tem_coluna) para a
regra L018 (toda medida e coluna projetada existe no TMDL — bloqueia).

O QUE GRAVA: .pbip, .gitignore e todo o VP.Report (definition.pbir, .platform, version.json, report.json, tema, papéis
de parede, pacotes CustomVisuals dos três visuais privados, páginas, visuais e bookmarks).
SEGURANÇA: manifesto spec/relatorio/_gerenciados.json — só se remove o que o montador criou (L014); recusa com o Power BI
Desktop aberto neste projeto; backup zip datado em pbi/_backups antes de gravar; caminhos < 260 / pastas < 248 (L045).
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pbip_lib as lib  # noqa: E402

RAIZ = lib.RAIZ
PBIP_DIR = lib.PBIP_DIR
R = lib.PASTA_REPORT
DIR_DECL = AQUI / "paginas"
MANIFESTO = RAIZ / "spec" / "relatorio" / "_gerenciados.json"
BACKUPS = RAIZ / "_backups"
TEMA = RAIZ / "assets" / "tema" / "Eleicoes.json"
TEMA_BASE = RAIZ / "assets" / "tema" / "CY26SU07.json"          # tema base do Desktop
VERSAO_IMPORT = {"visual": "2.11.0", "report": "3.4.0", "page": "2.3.1"}


# ----------------------------------------------------------------------------------------------------------------
# Declarações
# ----------------------------------------------------------------------------------------------------------------
Pagina, Visual, Bookmark, Recurso, Interacao = lib.Pagina, lib.Visual, lib.Bookmark, lib.Recurso, lib.Interacao


@dataclass
class Contexto:
    medidas: set = field(default_factory=set)
    colunas: set = field(default_factory=set)
    # só para fotografar a gaveta aberta (--gaveta-aberta T1); vazio no arquivo final. Era a variável de ambiente
    # QA_DRAWER, que deixava o PBIR depender do ambiente (auditoria da Fase 2, minor 11)
    gaveta_aberta: str | None = None

    def tem_medida(self, nome: str) -> bool:
        return nome in self.medidas

    def tem_coluna(self, tabela: str, coluna: str) -> bool:
        return (tabela, coluna) in self.colunas


_RE_TAB = re.compile(r"^table\s+('(?:[^']|'')*'|\S+)\s*$")
_RE_OBJ = re.compile(r"^\t(column|measure)\s+('(?:[^']|'')*'|[^\s=]+)")


def _nome_tmdl(n: str) -> str:
    return n[1:-1].replace("''", "'") if n.startswith("'") else n


def carregar_contexto() -> Contexto:
    ctx = Contexto()
    pasta = PBIP_DIR / lib.PASTA_MODELO / "definition" / "tables"
    for arq in sorted(pasta.glob("*.tmdl")):
        tabela = None
        for linha in arq.read_text(encoding="utf-8").splitlines():
            m = _RE_TAB.match(linha)
            if m:
                tabela = _nome_tmdl(m.group(1))
                continue
            m = _RE_OBJ.match(linha)
            if m and tabela:
                nome = _nome_tmdl(m.group(2))
                if m.group(1) == "measure":
                    ctx.medidas.add(nome)
                else:
                    ctx.colunas.add((tabela, nome))
    return ctx


def carregar_declaracoes(ctx: Contexto, fora: set | None = None) -> list:
    """Carrega pbi/scripts/paginas/*.py (menos os que começam com "_"). Depois de todas as declarações, os módulos que
    definem ajustar(itens, ctx) recebem a lista completa e devolvem a lista ajustada (a casca usa isso para ligar a
    navegação ao marcador de chegada de cada página, quando a tela o declara — L095)."""
    itens, mods = [], []
    for arq in sorted(DIR_DECL.glob("*.py")):
        if arq.name.startswith("_") or arq.stem in (fora or set()):
            continue
        spec = importlib.util.spec_from_file_location(f"decl_{arq.stem}", arq)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "declarar"):
            raise lib.ErroDeclaracao(f"{arq.name}: sem declarar(ctx)")
        itens += list(mod.declarar(ctx))
        mods.append(mod)
    for mod in mods:
        if hasattr(mod, "ajustar"):
            itens = list(mod.ajustar(itens, ctx))
    # completar(ctx, itens) (20/10/2026, o botão de PDF): depois de tudo ajustado, módulos que montam peças a partir das
    # páginas já declaradas (paginas/exporta.py) devolvem itens NOVOS, que entram na lista
    for mod in mods:
        if hasattr(mod, "completar"):
            itens += list(mod.completar(ctx, itens))
    return itens


# ----------------------------------------------------------------------------------------------------------------
# Conferência (L018 / nomes / referências)
# ----------------------------------------------------------------------------------------------------------------
def _refs(obj, saida):
    if isinstance(obj, dict):
        if "Measure" in obj and isinstance(obj["Measure"], dict):
            m = obj["Measure"]
            saida.append(("medida", m.get("Expression", {}).get("SourceRef", {}).get("Entity"), m.get("Property")))
        if "Column" in obj and isinstance(obj["Column"], dict):
            c = obj["Column"]
            ent = c.get("Expression", {}).get("SourceRef", {}).get("Entity")
            if ent:
                saida.append(("coluna", ent, c.get("Property")))
        for v in obj.values():
            _refs(v, saida)
    elif isinstance(obj, list):
        for v in obj:
            _refs(v, saida)
    return saida


def conferir(itens, ctx: Contexto) -> list[str]:
    erros = []
    paginas = {i.doc["name"] for i in itens if isinstance(i, Pagina)}
    nomes_visuais: dict[str, str] = {}
    for i in itens:
        if isinstance(i, Visual):
            n = i.doc["name"]
            if i.pagina not in paginas:
                erros.append(f"visual {n}: página {i.pagina} não declarada")
            chave = f"{i.pagina}/{n}"
            if chave in nomes_visuais:
                erros.append(f"visual {n} declarado duas vezes na página {i.pagina}")
            nomes_visuais[chave] = n
            for tipo, ent, prop in _refs(i.doc.get("visual", {}), []):
                if tipo == "medida" and not ctx.tem_medida(prop):
                    erros.append(f"L018 {i.pagina}/{n}: medida inexistente [{prop}]")
                if tipo == "coluna" and not ctx.tem_coluna(ent, prop):
                    erros.append(f"L018 {i.pagina}/{n}: coluna inexistente {ent}[{prop}]")
            for tipo, ent, prop in _refs(i.doc.get("filterConfig", {}), []):
                if tipo == "coluna" and not ctx.tem_coluna(ent, prop):
                    erros.append(f"L018 {i.pagina}/{n}: filtro em coluna inexistente {ent}[{prop}]")
    for i in itens:
        if isinstance(i, Bookmark):
            pag = i.doc["explorationState"]["activeSection"]
            for alvo in i.doc["options"]["targetVisualNames"]:
                if f"{pag}/{alvo}" not in nomes_visuais:
                    erros.append(f"bookmark {i.doc['name']}: alvo {pag}/{alvo} não existe")
        if isinstance(i, Recurso) and not i.origem.is_file():
            erros.append(f"recurso {i.nome}: {i.origem} não existe")
    pares: set[tuple] = set()
    for i in itens:
        if isinstance(i, Interacao):
            if i.tipo not in lib.TIPOS_INTERACAO:
                erros.append(f"interação {i.pagina}/{i.origem}→{i.alvo}: tipo {i.tipo!r} fora de {lib.TIPOS_INTERACAO}")
            for papel, n in (("origem", i.origem), ("alvo", i.alvo)):
                if f"{i.pagina}/{n}" not in nomes_visuais:
                    erros.append(f"interação {i.pagina}/{i.origem}→{i.alvo}: {papel} {n} não existe na página")
            if i.origem == i.alvo:
                erros.append(f"interação {i.pagina}/{i.origem}: origem = alvo")
            chave = (i.pagina, i.origem, i.alvo)
            if chave in pares:
                erros.append(f"interação {i.pagina}/{i.origem}→{i.alvo} declarada duas vezes")
            pares.add(chave)
    for i in itens:
        if isinstance(i, Visual):
            link = i.doc["visual"].get("visualContainerObjects", {}).get("visualLink")
            if link:
                props = link[0]["properties"]
                tipo = props.get("type", {}).get("expr", {}).get("Literal", {}).get("Value")
                if tipo == "'Bookmark'":
                    alvo = props["bookmark"]["expr"]["Literal"]["Value"].strip("'")
                    if not any(isinstance(b, Bookmark) and b.doc["name"] == alvo for b in itens):
                        erros.append(f"{i.doc['name']}: bookmark {alvo} não declarado")
                if tipo == "'PageNavigation'" and "Literal" in props["navigationSection"]["expr"]:
                    alvo = props["navigationSection"]["expr"]["Literal"]["Value"].strip("'")
                    if alvo not in paginas:
                        erros.append(f"{i.doc['name']}: página {alvo} não declarada")
    return erros


# ----------------------------------------------------------------------------------------------------------------
# Plano de arquivos
# ----------------------------------------------------------------------------------------------------------------
def plano(itens, ativa: str | None = None) -> dict[str, bytes]:
    arq: dict[str, bytes] = {}
    s = lib.serializar
    arq[f"{lib.NOME_PROJETO}.pbip"] = s({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": R}}], "settings": {"enableAutoRecovery": True}})
    arq[".gitignore"] = b"**/.pbi/localSettings.json\n**/.pbi/cache.abf\n"
    arq[f"{R}/.platform"] = s({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": lib.NOME_PROJETO},
        "config": {"version": "2.0", "logicalId": lib.id_estavel("platform:Report")}})
    arq[f"{R}/definition.pbir"] = s({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": f"../{lib.PASTA_MODELO}"}}})
    arq[f"{R}/definition/version.json"] = s({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0"})
    arq[f"{R}/StaticResources/SharedResources/BaseThemes/CY26SU07.json"] = TEMA_BASE.read_bytes()
    tema_nome = TEMA.name
    arq[f"{R}/StaticResources/RegisteredResources/{tema_nome}"] = TEMA.read_bytes()
    registrados = [{"name": tema_nome, "path": tema_nome, "type": "CustomTheme"}]
    for i in sorted((i for i in itens if isinstance(i, Recurso)), key=lambda r: r.nome):
        arq[f"{R}/StaticResources/RegisteredResources/{i.nome}"] = i.origem.read_bytes()
        registrados.append({"name": i.nome, "path": i.nome, "type": "Image"})
    # pacotes dos visuais privados em uso
    usados = {i.doc["visual"]["visualType"] for i in itens if isinstance(i, Visual)}
    pacotes = []
    for chave, cfg in lib.PACOTES.items():
        if cfg["guid"] not in usados:
            continue
        for rel, dados in lib.arquivos_pacote(chave).items():
            arq[f"{R}/CustomVisuals/{cfg['guid']}/{rel}"] = dados
        pacotes.append({"name": cfg["guid"], "type": "CustomVisual",
                        "items": [{"name": cfg["guid"] + ".pbiviz.json", "path": cfg["guid"] + ".pbiviz.json",
                                   "type": "CustomVisualMetadata"}]})
    arq[f"{R}/definition/report.json"] = s({
        "$schema": lib.ESQUEMA["report"],
        "themeCollection": {
            "baseTheme": {"name": "CY26SU07", "reportVersionAtImport": VERSAO_IMPORT, "type": "SharedResources"},
            "customTheme": {"name": tema_nome, "reportVersionAtImport": VERSAO_IMPORT, "type": "RegisteredResources"}},
        "objects": {"outspacePane": [{"properties": {"expanded": lib.lit(False), "visible": lib.lit(False)}}]},
        # sem grupo de cálculo nem filtro de relatório: o filtro por empreendimento é a segmentação sincronizada da casca
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": "CY26SU07", "path": "BaseThemes/CY26SU07.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources", "items": registrados},
        ] + pacotes,
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized",
                     "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True,
                     "useEnhancedTooltips": True, "useDefaultAggregateDisplayName": True}})
    paginas = sorted((i for i in itens if isinstance(i, Pagina)), key=lambda p: (p.ordem, p.doc["name"]))
    arq[f"{R}/definition/pages/pages.json"] = s({"$schema": lib.ESQUEMA["paginas"],
                                                 "pageOrder": [p.doc["name"] for p in paginas],
                                                 "activePageName": ativa or paginas[0].doc["name"]})
    interacoes: dict[str, list] = {}
    for i in itens:
        if isinstance(i, Interacao):
            interacoes.setdefault(i.pagina, []).append({"source": i.origem, "target": i.alvo, "type": i.tipo})
    for p in paginas:
        doc = p.doc
        if interacoes.get(doc["name"]):
            doc = {**doc, "visualInteractions": sorted(interacoes[doc["name"]], key=lambda d: (d["source"], d["target"]))}
        arq[f"{R}/definition/pages/{p.doc['name']}/page.json"] = s(doc)
    for i in itens:
        if isinstance(i, Visual):
            arq[f"{R}/definition/pages/{i.pagina}/visuals/{i.doc['name']}/visual.json"] = s(i.doc)
    bms = [i for i in itens if isinstance(i, Bookmark)]
    if bms:
        grupos: dict[str, dict] = {}
        soltos = []
        for b in bms:
            arq[f"{R}/definition/bookmarks/{b.doc['name']}.bookmark.json"] = s(b.doc)
            if b.grupo:
                g = grupos.setdefault(b.grupo[0], {"name": b.grupo[0], "displayName": b.grupo[1], "children": []})
                g["children"].append(b.doc["name"])
            else:
                soltos.append({"name": b.doc["name"]})
        arq[f"{R}/definition/bookmarks/bookmarks.json"] = s({"$schema": lib.ESQUEMA["bookmarks"],
                                                             "items": list(grupos.values()) + soltos})
    return arq


# ----------------------------------------------------------------------------------------------------------------
# Disco
# ----------------------------------------------------------------------------------------------------------------
def conferir_caminhos(arq: dict[str, bytes]) -> list[str]:
    erros = []
    for rel in arq:
        c = str(PBIP_DIR / rel)
        if len(c) >= 260:
            erros.append(f"L045 caminho com {len(c)} caracteres: {c}")
        if len(str(Path(c).parent)) >= 248:
            erros.append(f"L045 pasta com {len(str(Path(c).parent))} caracteres: {Path(c).parent}")
    return erros


def desktop_aberto() -> list[str]:
    # o console do PowerShell escreve em cp850; em UTF-8 o caminho com acento chega inteiro (auditoria da Fase 2)
    comando = ("[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
               "Get-CimInstance Win32_Process -Filter \"Name='PBIDesktop.exe'\" | "
               "ForEach-Object { if ($_.CommandLine) { $_.CommandLine } else { '<sem linha de comando>' } }")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return []           # sem PowerShell (Linux, sessão na nuvem): não há Power BI Desktop aberto
    linhas = [l.strip() for l in r.stdout.splitlines() if l.strip()]
    alvo = str(PBIP_DIR).lower()
    return [l for l in linhas if alvo in l.lower() or l == "<sem linha de comando>"]


def ler_manifesto() -> set[str]:
    if MANIFESTO.is_file():
        return set(json.loads(MANIFESTO.read_text(encoding="utf-8")).get("arquivos", []))
    return set()


def gravar_atomico(caminho: Path, dados: bytes) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_name(caminho.name + ".tmp-montar")
    tmp.write_bytes(dados)
    os.replace(tmp, caminho)


def backup(rels) -> Path | None:
    existentes = [r for r in rels if (PBIP_DIR / r).is_file()]
    if not existentes:
        return None
    BACKUPS.mkdir(parents=True, exist_ok=True)
    destino = BACKUPS / f"report-{dt.datetime.now():%Y%m%d-%H%M%S}.zip"
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for r in existentes:
            z.write(PBIP_DIR / r, r)
    return destino


def json_igual(a: bytes, b: bytes) -> bool:
    if a == b:
        return True
    try:
        return json.loads(a) == json.loads(b)
    except (ValueError, UnicodeDecodeError):
        return False


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    modo = ap.add_mutually_exclusive_group()
    modo.add_argument("--aplicar", action="store_true")
    modo.add_argument("--conferir", action="store_true")
    ap.add_argument("--ativa", help="página que o Desktop abre (padrão: a primeira); serve para fotografar outra tela "
                                    "pela janela, sem clicar")
    ap.add_argument("--gaveta-aberta", metavar="TELA",
                    help="monta a gaveta dessa tela (T1…T4) já aberta, só para fotografar; nunca no arquivo final")
    ap.add_argument("--sem-modulo", action="append", default=[],
                    help="não carrega pbi/scripts/paginas/<módulo>.py (tela em obra de outro agente; ex.: t3, tt_t3)")
    a = ap.parse_args(argv)
    ctx = carregar_contexto()
    ctx.gaveta_aberta = a.gaveta_aberta
    try:
        itens = carregar_declaracoes(ctx, set(a.sem_modulo))
        erros = conferir(itens, ctx)
        if a.ativa and not any(isinstance(i, Pagina) and i.doc["name"] == a.ativa for i in itens):
            erros.append(f"--ativa {a.ativa}: página não declarada")
        arq = plano(itens, a.ativa) if not erros else {}
    except lib.ErroDeclaracao as e:
        print(f"[BLOQUEIO] {e}")
        return 2
    erros += conferir_caminhos(arq)
    nv = sum(isinstance(i, Visual) for i in itens)
    print(f"declarações: {sum(isinstance(i, Pagina) for i in itens)} páginas · {nv} visuais · "
          f"{sum(isinstance(i, Bookmark) for i in itens)} bookmarks · {sum(isinstance(i, Recurso) for i in itens)} recursos · "
          f"{sum(isinstance(i, Interacao) for i in itens)} interações"
          f" · modelo: {len(ctx.medidas)} medidas")
    if erros:
        for e in erros:
            print("  [ERRO]", e)
        return 2
    antigos = ler_manifesto()
    mudam = sorted(r for r, d in arq.items() if not ((PBIP_DIR / r).is_file() and json_igual((PBIP_DIR / r).read_bytes(), d)))
    sobram = sorted(r for r in antigos if r not in arq and (PBIP_DIR / r).is_file())
    print(f"plano: {len(arq)} arquivos · {len(mudam)} mudam · {len(sobram)} saem (gerenciados, fora do plano)")
    for r in mudam[:30]:
        print("  ~", r)
    if len(mudam) > 30:
        print(f"  … +{len(mudam) - 30}")
    for r in sobram:
        print("  -", r)
    if a.conferir:
        return 1 if (mudam or sobram) else 0
    if not a.aplicar:
        print("simulação: nada gravado (use --aplicar)")
        return 0
    abertos = desktop_aberto()
    if abertos:
        print("[BLOQUEIO] Power BI Desktop aberto neste projeto: feche antes de montar.")
        return 3
    bak = backup(set(mudam) | set(sobram))
    if bak:
        print("backup:", bak)
    for r in mudam:
        gravar_atomico(PBIP_DIR / r, arq[r])
    for r in sobram:
        (PBIP_DIR / r).unlink(missing_ok=True)
        pasta = (PBIP_DIR / r).parent
        while pasta != PBIP_DIR and pasta.is_dir() and not any(pasta.iterdir()):
            pasta.rmdir()
            pasta = pasta.parent
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTO.write_text(json.dumps({"gerado": dt.datetime.now().isoformat(timespec="seconds"),
                                     "arquivos": sorted(arq)}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"gravado: {len(mudam)} · removidos: {len(sobram)}")
    # pelo python.exe (assinado), não pelo atalho pbir.exe do pip (sem assinatura): o Controle de Aplicativo
    # Inteligente do Windows bloqueia o atalho; o pbir-runtime.exe que o pacote chama é assinado
    r = subprocess.run([sys.executable, "-m", "pbir_binary_wheel.launcher", "--quiet", "validate", str(PBIP_DIR / R)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    saida = (r.stdout or r.stderr or "").strip().splitlines()
    print("pbir validate:", saida[-1] if saida else r.returncode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
