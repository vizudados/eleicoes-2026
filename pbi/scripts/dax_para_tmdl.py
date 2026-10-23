#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a tabela de medidas (TMDL) a partir da árvore pbi/dax/**/*.dax — um arquivo por medida com cabeçalho:

    /*
    @pasta: T1 Visão geral\\Paletes\\Contas     (displayFolder; obrigatório)
    @formato: #,##0                            (formatString; "texto" = sem formatString; obrigatório)
    @descricao: o que devolve, unidade, onde aparece   (descrição ///; obrigatório)
    @oraculo: …   @oculta: sim   @nome: …   @gerado: …   (opcionais)
    */
    <expressão DAX>

O nome da medida é o nome do arquivo (sem .dax) ou @nome. Pastas chamadas _modelo são ignoradas (tabelas calculadas e
parâmetros ficam fora da tabela de medidas). lineageTag = uuid5 estável do nome; saída em CRLF, sem BOM.

    python dax_para_tmdl.py --dax pbi/dax --saida <X>.SemanticModel/definition/tables/_Medidas.tmdl --conferir
    python dax_para_tmdl.py --dax pbi/dax --saida <...>/_Medidas.tmdl --aplicar        # grava com backup .bak
    python dax_para_tmdl.py --dax pbi/dax --saida <...>/_Medidas.tmdl --aplicar --tabela _Medidas --ns meu-projeto

Rode com o Power BI Desktop FECHADO: com ele aberto, o próximo salvamento sobrescreve o arquivo gerado.
Código de saída: 0 ok/igual, 1 diferença (--conferir) ou erro de entrada, 2 uso errado.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import re
import shutil
import sys
import textwrap
import uuid
from pathlib import Path

NL = "\r\n"
CAB = re.compile(r"@(\w+)\s*:\s*(.*?)(?=\s+@\w+\s*:|\s*\*/|$)", re.S)
SIMPLES = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROIBIDO_ARQ = set('/\\:*?"<>|')


class ErroEntrada(Exception):
    pass


def citar(nome: str) -> str:
    return nome if SIMPLES.match(nome) else "'" + nome.replace("'", "''") + "'"


def uma_linha(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip()


def ler(p: Path) -> dict:
    t = p.read_text(encoding="utf-8").lstrip("﻿").replace("\r\n", "\n")
    s = t.lstrip()
    if not (s.startswith("/*") and "*/" in s):
        raise ErroEntrada(f"{p}: falta o cabeçalho /* @pasta @formato @descricao */")
    ini = t.index("/*")
    fim = t.index("*/", ini) + 2
    cab = {k.lower(): uma_linha(v) for k, v in CAB.findall(t[ini:fim])}
    faltam = [k for k in ("pasta", "formato", "descricao") if not cab.get(k)]
    if faltam:
        raise ErroEntrada(f"{p}: faltam @" + ", @".join(faltam))
    corpo = t[fim:]
    linhas = corpo.split("\n")
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    while linhas and not linhas[-1].strip():
        linhas.pop()
    if not linhas:
        raise ErroEntrada(f"{p}: expressão vazia")
    if any("\t" in l for l in linhas):
        raise ErroEntrada(f"{p}: tab na expressão — use espaços (o TMDL usa tab como estrutura)")
    # recuo comum fora e 1ª linha sem recuo: no TMDL a 1ª linha da expressão fixa a margem, e uma linha seguinte com
    # menos recuo quebra o arquivo inteiro (caso real, 23/10/2026: "    VAR _a =" seguido de "VAR _b =")
    linhas = textwrap.dedent("\n".join(linhas)).split("\n")
    linhas[0] = linhas[0].lstrip()
    nome = cab.get("nome") or p.stem
    return {"nome": nome, "pasta": cab["pasta"], "formato": cab["formato"], "descricao": cab["descricao"],
            "oculta": bool(cab.get("oculta")) and cab.get("oculta", "").lower() not in ("não", "nao", "no", "false", "0"),
            "linhas": [l.rstrip() for l in linhas], "arquivo": str(p)}


def coletar(raiz: Path) -> list[dict]:
    if not raiz.is_dir():
        raise ErroEntrada(f"não é pasta: {raiz}")
    medidas, vistos = [], {}
    for p in sorted(raiz.rglob("*.dax"), key=lambda p: str(p).casefold()):
        if "_modelo" in p.relative_to(raiz).parts:
            continue
        m = ler(p)
        chave = m["nome"].casefold()
        if chave in vistos:
            raise ErroEntrada(f"nome repetido '{m['nome']}': {vistos[chave]} e {p}")
        vistos[chave] = str(p)
        medidas.append(m)
    if not medidas:
        raise ErroEntrada(f"nenhum .dax em {raiz}")
    return medidas


def gerar(medidas: list[dict], tabela: str, ns: str, descricao_tabela: str) -> str:
    base = uuid.uuid5(uuid.NAMESPACE_URL, "https://vizudados.com.br/" + ns)

    def tag(chave: str) -> str:
        return str(uuid.uuid5(base, chave))

    out = []
    if descricao_tabela:
        out.append("/// " + uma_linha(descricao_tabela))
    out += ["table " + citar(tabela), "\tlineageTag: " + tag("tabela:" + tabela), ""]
    for m in sorted(medidas, key=lambda x: (x["pasta"].casefold(), x["nome"].casefold())):
        out.append("\t/// " + m["descricao"])
        out.append("\tmeasure " + citar(m["nome"]) + " =")
        out += [("\t\t\t" + l) if l.strip() else "" for l in m["linhas"]]
        if m["formato"].casefold() != "texto":
            out.append("\t\tformatString: " + m["formato"])
        if m["oculta"]:
            out.append("\t\tisHidden")
        out.append("\t\tdisplayFolder: " + m["pasta"])
        out.append("\t\tlineageTag: " + tag("medida:" + m["nome"]))
        out.append("")
    out += ["\tcolumn Value", "\t\tdataType: int64", "\t\tisHidden",
            "\t\tlineageTag: " + tag(f"coluna:{tabela}.Value"), "\t\tsummarizeBy: none",
            "\t\tisNameInferred", "\t\tsourceColumn: [Value]", "",
            "\tpartition " + citar(tabela) + " = calculated", "\t\tmode: import", "\t\tsource = {BLANK()}", ""]
    return NL.join(out) + NL


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dax", required=True, help="raiz da árvore de medidas (ex.: pbi/dax)")
    ap.add_argument("--saida", required=True, help="arquivo _Medidas.tmdl de destino")
    ap.add_argument("--tabela", default="_Medidas", help="nome da tabela de medidas (padrão _Medidas)")
    ap.add_argument("--ns", default=None, help="namespace dos lineageTag (padrão: nome da pasta do projeto)")
    ap.add_argument("--descricao", default="Medidas do relatório. Gerada a partir de pbi/dax/**/*.dax; não edite à mão.",
                    help="descrição da tabela")
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument("--conferir", action="store_true", help="só compara com o arquivo atual")
    modo.add_argument("--aplicar", action="store_true", help="grava (com backup .bak se o arquivo existir)")
    a = ap.parse_args(argv)

    raiz, saida = Path(a.dax), Path(a.saida)
    modelo = next((p for p in saida.resolve().parents if p.name.endswith(".SemanticModel")), None)
    ns = a.ns or (modelo.name[: -len(".SemanticModel")] if modelo else raiz.resolve().parent.name)
    try:
        medidas = coletar(raiz)
    except ErroEntrada as e:
        print(f"ERRO {e}", file=sys.stderr)
        return 1
    for m in medidas:
        if PROIBIDO_ARQ & set(m["nome"]) and m["nome"] == Path(m["arquivo"]).stem:
            print(f"ERRO nome com caractere proibido: {m['nome']}", file=sys.stderr)
            return 1
    novo = gerar(medidas, a.tabela, ns, a.descricao)
    atual = saida.read_bytes().decode("utf-8-sig") if saida.exists() else ""
    pastas = len({m["pasta"] for m in medidas})
    print(f"{len(medidas)} medidas em {pastas} pastas · tabela {a.tabela} · ns {ns}")

    if a.conferir:
        if atual == novo:
            print("igual: o TMDL já corresponde à árvore")
            return 0
        dif = list(difflib.unified_diff(atual.splitlines(), novo.splitlines(), "atual", "gerado", n=1, lineterm=""))
        print(f"DIFERENTE: {sum(1 for d in dif if d[:1] in '+-' and d[:3] not in ('+++', '---'))} linhas mudam")
        for d in dif[:60]:
            print(d)
        if len(dif) > 60:
            print(f"… (+{len(dif) - 60} linhas de diff)")
        return 1

    if atual == novo:
        print("nada a gravar (igual)")
        return 0
    saida.parent.mkdir(parents=True, exist_ok=True)
    if saida.exists():
        # backup fora de definition/: o Desktop carrega a pasta do modelo e não deve ver arquivos estranhos nela
        modelo = next((p for p in saida.resolve().parents if p.name.endswith(".SemanticModel")), None)
        pasta_bak = (modelo.parent if modelo else saida.parent) / "_backups"
        pasta_bak.mkdir(parents=True, exist_ok=True)
        bak = pasta_bak / (saida.stem + "." + dt.datetime.now().strftime("%Y%m%d-%H%M%S") + ".tmdl.bak")
        shutil.copy2(saida, bak)
        print(f"backup: {bak}")
    with open(saida, "w", encoding="utf-8", newline="") as fh:
        fh.write(novo)
    print(f"gravado: {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
