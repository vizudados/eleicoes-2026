#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""previa — fotografa uma página do relatório FORA do Power BI (L046: o Desktop é um só e não é bancada de teste).

Lê as declarações de pbi/scripts/paginas/*.py (as mesmas do montar_pbip), avalia no motor do Desktop aberto (porta em
pbi/qa/porta.txt) as medidas de cada visual HTML Content e o dataset de cada Deneb — com TODAS as medidas da árvore
pbi/dax definidas na consulta (DEFINE MEASURE), então a prévia vê a versão em disco de cada medida, sem regenerar o
modelo —, monta a página 1920×1080 com o papel de parede e cada visual na sua caixa (HTML na árvore real do visual,
dentro de um iframe do tamanho do visual, L037; Deneb desenhado pelo Vega 6 em pbi/tools) e tira a foto no Edge
headless.

    python -X utf8 pbi/scripts/previa.py T02                       # pbi/qa/previa/T02.png (+ .html)
    python -X utf8 pbi/scripts/previa.py T02 --marcador T02_LEITURA_VENDAS_01   # aplica a visibilidade do marcador
    python -X utf8 pbi/scripts/previa.py T02 --filtro "UF[Nome]=Minas Gerais"       # recorte (filtro na consulta)
    python -X utf8 pbi/scripts/previa.py T02 --animado              # sem congelar as animações (foto em tempo real)
    python -X utf8 pbi/scripts/previa.py T02 --guias                # contorno tracejado dos visuais nativos e caixas
    python -X utf8 pbi/scripts/previa.py ttT02Ano --tooltip "fVenda[Ano]=2025"   # página de tooltip

Por padrão as animações são congeladas no estado final (animation/transition com duração 0): a foto mostra o que fica
na tela. Visuais nativos (botão, segmentação, VizuFilter) não são desenhados (use --guias para ver as caixas).
Códigos de saída: 0 ok · 1 algum visual falhou (o erro vai na foto, em vermelho, e no console) · 2 uso/ambiente.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import dax  # noqa: E402
import dax_para_tmdl as dpt  # noqa: E402
import montar_pbip as mp  # noqa: E402
import pbip_lib as lib  # noqa: E402

PBI = AQUI.parent
SAIDA = PBI / "qa" / "previa"
TOOLS = PBI / "tools"
# o Chrome primeiro (20/10/2026: o Edge, no meio de uma atualização, saía do --screenshot sem erro e sem arquivo);
# os dois são o mesmo motor
EDGE = [Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")]
CONGELA = ("*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;"
           "transition-duration:0s!important;transition-delay:0s!important}")


# ---------------------------------------------------------------------------------------------------- medidas
def medidas_em_disco() -> dict[str, dict]:
    """{nome: medida} de pbi/dax (fora de _modelo); arquivo com cabeçalho quebrado vira aviso, não erro."""
    saida = {}
    for p in sorted((PBI / "dax").rglob("*.dax"), key=lambda p: str(p).casefold()):
        if "_modelo" in p.relative_to(PBI / "dax").parts:
            continue
        try:
            m = dpt.ler(p)
        except dpt.ErroEntrada as e:
            print(f"aviso: {e}")
            continue
        saida[m["nome"]] = m
    return saida


_REF = re.compile(r"\[([^\[\]]+)\]")


def bloco_define(raizes: set[str], tabela: str = lib.TABELA_MEDIDAS) -> str:
    """DEFINE com as medidas de pbi/dax que a página usa e as que elas citam (a versão em disco vence a do modelo
    dentro da consulta; só as dependências entram, então uma medida quebrada de outra tela não derruba a prévia)."""
    todas = medidas_em_disco()
    usadas, fila = set(), [r for r in raizes if r in todas]
    while fila:
        n = fila.pop()
        if n in usadas:
            continue
        usadas.add(n)
        for ref in _REF.findall("\n".join(todas[n]["linhas"])):
            if ref in todas and ref not in usadas:
                fila.append(ref)
    if not usadas:
        return ""
    partes = ["DEFINE"]
    for n in sorted(usadas):
        corpo = "\n".join("    " + l for l in todas[n]["linhas"])
        partes.append(f"MEASURE '{tabela}'[{n.replace(']', ']]')}] =\n{corpo}")
    return "\n".join(partes) + "\n"


def medidas_do_visual(doc: dict) -> set[str]:
    nomes = set()
    lib_refs = mp._refs(doc.get("visual", {}), [])
    for tipo, _ent, prop in lib_refs:
        if tipo == "medida":
            nomes.add(prop)
    return nomes


def ref_medida(nome: str) -> str:
    return "[" + nome.replace("]", "]]") + "]"


def ref_coluna(tab: str, col: str) -> str:
    return "'" + tab.replace("'", "''") + "'[" + col.replace("]", "]]") + "]"


def filtro_dax(texto: str | None) -> str:
    """'UF[Nome]=Minas Gerais' → TREATAS ( { "Minas Gerais" }, 'UF'[Nome] ) (texto) ou número se for número."""
    if not texto:
        return ""
    m = re.match(r"^\s*([^\[]+)\[([^\]]+)\]\s*=\s*(.+?)\s*$", texto)
    if not m:
        raise SystemExit(f"--filtro {texto!r}: use Tabela[Coluna]=valor")
    tab, col, val = m.groups()
    lit_ = val if re.match(r"^-?\d+(\.\d+)?$", val) else '"' + val.replace('"', '""') + '"'
    return f"TREATAS ( {{ {lit_} }}, {ref_coluna(tab, col)} )"


def _literal_dax(v: str) -> str:
    """Literal de filtro PBIR ('texto', 12L, 1.5D, true) → literal DAX."""
    if v.startswith("'") and v.endswith("'"):
        return '"' + v[1:-1].replace("''", "'").replace('"', '""') + '"'
    if v in ("true", "false"):
        return v.upper() + " ()"
    if re.match(r"^-?\d+(\.\d+)?[LDM]$", v):
        return v[:-1]
    raise ValueError(f"literal de filtro não suportado: {v!r}")


def filtro_do_visual(doc: dict) -> str:
    """filterConfig do visual (só categórico 'In' de uma coluna) → TREATAS. Antes a prévia ignorava o recorte do
    visual (a tira da T06 saía sem o estágio e o TemERP; crítica B P16, 19/10/2026). TopN e outros tipos ficam de fora."""
    partes = []
    for f in doc.get("filterConfig", {}).get("filters", []):
        if f.get("type") != "Categorical":
            continue
        fil = f.get("filter") or {}
        fontes = {x.get("Name"): x.get("Entity") for x in fil.get("From", [])}
        for w in fil.get("Where", []):
            cond = (w.get("Condition") or {}).get("In") or {}
            exps, vals = cond.get("Expressions") or [], cond.get("Values")
            if len(exps) != 1 or "Column" not in exps[0] or not vals:
                continue
            col = exps[0]["Column"]
            tab = fontes.get(col["Expression"]["SourceRef"].get("Source")) or col["Expression"]["SourceRef"].get("Entity")
            lits = ", ".join(_literal_dax(v[0]["Literal"]["Value"]) for v in vals)
            partes.append(f"TREATAS ( {{ {lits} }}, {ref_coluna(tab, col['Property'])} )")
    return " , ".join(partes)


def consultar(define: str, corpo: str) -> list[dict]:
    try:
        return dax.consultar(define + corpo)
    except dax.ErroDax as e:
        raise RuntimeError(e.mensagem_curta()[:600]) from None


# ---------------------------------------------------------------------------------------------------- visuais
def literal(obj) -> str | None:
    try:
        v = obj["expr"]["Literal"]["Value"]
    except (KeyError, TypeError):
        return None
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1].replace("''", "'")
    return v


def medida_de(proj) -> str | None:
    try:
        return proj["field"]["Measure"]["Property"]
    except (KeyError, TypeError):
        return None


def coluna_de(proj) -> tuple[str, str] | None:
    try:
        c = proj["field"]["Column"]
        return c["Expression"]["SourceRef"]["Entity"], c["Property"]
    except (KeyError, TypeError):
        return None


def html_content(doc: dict, define: str, filtro: str) -> str:
    v = doc["visual"]
    est = v["query"]["queryState"]
    conteudo = medida_de(est["content"]["projections"][0])
    gran = coluna_de(est["sampling"]["projections"][0]) if "sampling" in est else None
    obj = v.get("objects", {})
    css_m = None
    if "stylesheet" in obj:
        css_m = obj["stylesheet"][0]["properties"]["stylesheet"]["expr"]["Measure"]["Property"]
    corpo_tpl = literal(obj["templates"][0]["properties"]["bodyTemplate"]) if "templates" in obj else None
    css = ""
    if css_m:
        r = consultar(define, f"EVALUATE ROW ( \"s\", {ref_medida(css_m)} )")
        css = (r[0].get("[s]") if r else "") or ""
    filtro_arg = (", " + filtro) if filtro else ""
    if gran:
        ordem = ""
        sort = v["query"].get("sortDefinition", {}).get("sort", [])
        if sort and "Measure" in sort[0]["field"]:
            ordem = " ORDER BY [c] " + ("DESC" if sort[0]["direction"] == "Descending" else "ASC")
        elif sort and "Column" in sort[0]["field"]:
            ordem = (" ORDER BY " + ref_coluna(sort[0]["field"]["Column"]["Expression"]["SourceRef"]["Entity"],
                                               sort[0]["field"]["Column"]["Property"])
                     + (" DESC" if sort[0]["direction"] == "Descending" else " ASC"))
        else:
            ordem = " ORDER BY " + ref_coluna(*gran)
        linhas = consultar(define, f"EVALUATE SUMMARIZECOLUMNS ( {ref_coluna(*gran)}{filtro_arg}, "
                                   f"\"c\", {ref_medida(conteudo)} ){ordem}")
        entradas = [r.get("[c]") or "" for r in linhas]
    else:
        if filtro:
            r = consultar(define, f"EVALUATE CALCULATETABLE ( ROW ( \"c\", {ref_medida(conteudo)} ){filtro_arg} )")
        else:
            r = consultar(define, f"EVALUATE ROW ( \"c\", {ref_medida(conteudo)} )")
        entradas = [(r[0].get("[c]") if r else "") or ""]
    entradas_html = "".join(f"<div class=\"htmlViewerEntry\">{e}</div>" for e in entradas)
    conteudo_html = corpo_tpl.replace("{{content}}", entradas_html) if corpo_tpl else entradas_html
    # árvore real do visual (L037): html > body > #sandbox-host > #htmlViewer > .os-padding > .os-viewport >
    # .os-content > #htmlContent > .htmlViewerEntry
    return ("<!doctype html><html><head><meta charset=\"utf-8\"><style>html,body{margin:0;padding:0;overflow:hidden;"
            "background:transparent}</style><style>" + css + "</style><style id=\"congela\"></style></head><body>"
            "<div id=\"sandbox-host\"><div id=\"htmlViewer\"><div class=\"os-padding\"><div class=\"os-viewport\">"
            "<div class=\"os-content\"><div id=\"htmlContent\">" + conteudo_html + "</div></div></div></div></div></div>"
            "</body></html>")


def deneb_svg(doc: dict, define: str, filtro: str, tmp: Path) -> str:
    v = doc["visual"]
    spec = json.loads(literal(v["objects"]["vega"][0]["properties"]["jsonSpec"]))
    projs = v["query"]["queryState"]["dataset"]["projections"]
    cols, meds = [], []
    for p in projs:
        alias = p.get("nativeQueryRef")
        c = coluna_de(p)
        if c:
            cols.append((alias, c))
        else:
            meds.append((alias, medida_de(p)))
    partes = [ref_coluna(*c) for _a, c in cols]
    if filtro:
        partes.append(filtro)
    partes += [f"\"{a}\", {ref_medida(m)}" for a, m in meds]
    if cols:
        q = "EVALUATE SUMMARIZECOLUMNS ( " + ", ".join(partes) + " ) ORDER BY " + ", ".join(
            ref_coluna(*c) for _a, c in cols)
    else:
        q = "EVALUATE CALCULATETABLE ( ROW ( " + ", ".join(f"\"{a}\", {ref_medida(m)}" for a, m in meds) + " )" + (
            (", " + filtro) if filtro else "") + " )"
    linhas = consultar(define, q)
    dados = []
    for r in linhas:
        d = {}
        for a, (t, c) in cols:
            d[a] = r.get(f"{t}[{c}]")
        for a, _m in meds:
            d[a] = r.get(f"[{a}]")
        dados.append(d)
    w, h = doc["position"]["width"], doc["position"]["height"]
    ent = tmp / f"{doc['name']}.json"
    sai = tmp / f"{doc['name']}.svg"
    ent.write_text(json.dumps({"spec": spec, "dados": dados, "largura": w, "altura": h}, ensure_ascii=False),
                   encoding="utf-8")
    r = subprocess.run(["node", str(TOOLS / "render_vega.mjs"), str(ent), str(sai)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(TOOLS), timeout=120)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[:600])
    return sai.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------------------------------- página
def carregar_tolerante(ctx) -> list:
    """Como montar_pbip.carregar_declaracoes, mas um módulo de outra tela que falha só gera aviso (a prévia de uma tela
    não depende de as outras estarem prontas)."""
    import importlib.util
    itens, mods = [], []
    for arq in sorted(mp.DIR_DECL.glob("*.py")):
        if arq.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"decl_{arq.stem}", arq)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            itens += list(mod.declarar(ctx))
            mods.append(mod)
        except Exception as e:  # noqa: BLE001
            print(f"aviso: módulo {arq.name} não carregou ({type(e).__name__}: {str(e)[:200]})")
    for mod in mods:
        if hasattr(mod, "ajustar"):
            try:
                itens = list(mod.ajustar(itens, ctx))
            except Exception as e:  # noqa: BLE001
                print(f"aviso: ajustar de {mod.__name__} falhou ({e})")
    return itens


def visibilidade(itens, pagina: str, marcador: str | None) -> dict[str, bool]:
    if not marcador:
        return {}
    for i in itens:
        if isinstance(i, lib.Bookmark) and i.doc["name"] == marcador:
            sec = i.doc["explorationState"]["sections"].get(pagina, {}).get("visualContainers", {})
            return {v: ("display" not in c.get("singleVisual", {})) for v, c in sec.items()}
    raise SystemExit(f"marcador {marcador} não declarado")


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("pagina")
    ap.add_argument("--marcador")
    ap.add_argument("--filtro", help="recorte, ex.: UF[Nome]=Minas Gerais")
    ap.add_argument("--tooltip", help="contexto da página de tooltip, ex.: fVenda[Ano]=2025")
    ap.add_argument("--animado", action="store_true")
    ap.add_argument("--guias", action="store_true")
    ap.add_argument("--saida", help="arquivo .png (padrão pbi/qa/previa/<pagina>[-sufixo].png)")
    ap.add_argument("--espera", type=int, default=2500, help="ms de tempo virtual antes da foto")
    a = ap.parse_args(argv)

    ctx = mp.carregar_contexto()
    itens = carregar_tolerante(ctx)
    pag = next((i for i in itens if isinstance(i, lib.Pagina) and i.doc["name"] == a.pagina), None)
    if not pag:
        print(f"página {a.pagina} não declarada")
        return 2
    largura, altura = pag.doc["width"], pag.doc["height"]
    vis = visibilidade(itens, a.pagina, a.marcador)
    filtro = " , ".join(x for x in (filtro_dax(a.filtro), filtro_dax(a.tooltip)) if x)
    raizes = set()
    for i in itens:
        if isinstance(i, lib.Visual) and i.pagina == a.pagina:
            raizes |= medidas_do_visual(i.doc)
    define = bloco_define(raizes)
    fundo = ""
    bg = pag.doc.get("objects", {}).get("background", [{}])[0].get("properties", {})
    cor_fundo = "#FFFFFF"
    try:
        cor_fundo = literal(bg["color"]["solid"]["color"]) or cor_fundo
        nome_img = bg["image"]["image"]["name"]
        rec = next(i for i in itens if isinstance(i, lib.Recurso) and i.nome == literal(nome_img))
        fundo = rec.origem.read_text(encoding="utf-8") if rec.origem.suffix == ".svg" else ""
    except (KeyError, StopIteration, TypeError):
        pass

    visuais = sorted((i.doc for i in itens if isinstance(i, lib.Visual) and i.pagina == a.pagina),
                     key=lambda d: d["position"]["z"])
    camadas, erros = [], 0
    tmp = Path(tempfile.mkdtemp(prefix="previa_"))
    for d in visuais:
        oculto = d.get("isHidden", False)
        if d["name"] in vis:
            oculto = not vis[d["name"]]
        if oculto:
            continue
        p = d["position"]
        caixa = f"left:{p['x']}px;top:{p['y']}px;width:{p['width']}px;height:{p['height']}px;z-index:{p['z']}"
        tipo = d["visual"]["visualType"]
        try:
            filtro_v = " , ".join(x for x in (filtro, filtro_do_visual(d)) if x)
            if tipo == lib.GUID_HTML:
                doc_html = html_content(d, define, filtro_v)
                if not a.animado:
                    doc_html = doc_html.replace("<style id=\"congela\"></style>", f"<style id=\"congela\">{CONGELA}</style>")
                camadas.append(f"<iframe title=\"{d['name']}\" style=\"position:absolute;border:0;{caixa}\" "
                               f"srcdoc=\"{html.escape(doc_html, quote=True)}\"></iframe>")
            elif tipo == lib.GUID_DENEB:
                svg = deneb_svg(d, define, filtro_v, tmp)
                camadas.append(f"<div title=\"{d['name']}\" style=\"position:absolute;{caixa}\">{svg}</div>")
            elif a.guias:
                camadas.append(f"<div style=\"position:absolute;{caixa};outline:1px dashed #E0115F;"
                               f"font:11px monospace;color:#E0115F\">{d['name']}</div>")
            print(f"ok    {d['name']}")
        except Exception as e:  # noqa: BLE001 — um visual que falha não derruba a foto
            erros += 1
            msg = html.escape(str(e))
            print(f"ERRO  {d['name']}: {e}")
            camadas.append(f"<div style=\"position:absolute;{caixa};outline:2px solid #E0115F;background:#fff0f4;"
                           f"font:12px monospace;color:#B00020;overflow:hidden;padding:4px\">{d['name']}<br>{msg}</div>")
    pagina_html = (f"<!doctype html><html><head><meta charset=\"utf-8\"><style>html,body{{margin:0;width:{largura}px;"
                   f"height:{altura}px;overflow:hidden;background:{cor_fundo}}}#fundo{{position:absolute;inset:0}}"
                   f"#fundo svg{{width:{largura}px;height:{altura}px}}</style></head><body>"
                   f"<div id=\"fundo\">{fundo}</div>{''.join(camadas)}</body></html>")
    SAIDA.mkdir(parents=True, exist_ok=True)
    sufixo = "".join(f"-{re.sub(r'[^A-Za-z0-9]+', '_', x)}" for x in (a.marcador, a.filtro, a.tooltip) if x)
    # resolve(): com --saida relativo, as_uri() recusava o caminho (crítica B P16, 19/10/2026)
    png = (Path(a.saida) if a.saida else SAIDA / f"{a.pagina}{sufixo}.png").resolve()
    png.parent.mkdir(parents=True, exist_ok=True)
    arq_html = png.with_suffix(".html")
    arq_html.write_text(pagina_html, encoding="utf-8")
    edge = next((e for e in EDGE if e.is_file()), None)
    if not edge:
        print("sem Edge/Chrome para a foto; HTML em", arq_html)
        return 2
    perfil = tmp / "perfil"
    # a foto parada pede movimento reduzido: o kit de movimento (movimento.js, 20/10/2026) não conta os números; sem
    # isto, o tempo virtual pegava o contador no meio (T09: "R$ 1,4 mil/m²" a caminho de 14,5) e a miniatura do guia
    # sairia com o número errado
    parado = [] if a.animado else ["--force-prefers-reduced-motion"]
    r = subprocess.run([str(edge), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", *parado,
                        f"--user-data-dir={perfil}", f"--window-size={largura},{altura}",
                        f"--virtual-time-budget={a.espera}", f"--screenshot={png}", arq_html.as_uri()],
                       capture_output=True, text=True, timeout=180)
    if not png.is_file():
        print("foto falhou:", (r.stderr or r.stdout)[-800:])
        return 2
    print(f"foto: {png}  ·  {len(camadas)} visuais desenhados  ·  {erros} com erro")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
