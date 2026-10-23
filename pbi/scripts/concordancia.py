# -*- coding: utf-8 -*-
"""concordancia — erro de concordância de número nos textos que o leitor vê (regra L125, 21/10/2026).

Origem: o Guia do usuário escrevia "páginas 08" quando a fonte é usada numa página só (Alisson: "um erro bobo, só há
uma página e a citação se refere como no plural. veja se esse erro ocorre em outros e corrija. adicione uma regra").

Avalia no motor do Desktop aberto cada medida que vira texto na tela (nome com "· HTML", "· ALT" ou "Fontes · lista"),
sem filtro e com cada obra (dObra[Obra]); tira estilo e script, separa o texto de cada elemento HTML (o número de um
elemento não emenda no rótulo do vizinho: "17" + "Empreendimento se conta…" não é erro) e procura:
  P1  "1" seguido de substantivo no plural ........................ "1 obras", "1 unidades", "1 vendas"
  P2  número maior que 1 seguido de substantivo no singular ...... "3 obra", "2 unidade"
  P3  rótulo no plural seguido de um código só ................... "páginas 08", "telas 05"
Varre também os textos fixos do relatório (title, alt, rótulos de botão nos visual.json).

    python -X utf8 pbi/scripts/concordancia.py [prefixo]     # ex.: "T11 ·"
Saída 0 sem achado; 1 com achado (lista medida, contexto e o trecho). Não conserta nada: o conserto é no gerador
(use o plural da casa: plural(n, "unidade", "unidades") nos desenhos e o rótulo com a contagem nos textos fixos).
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import dax  # noqa: E402

PBI = AQUI.parent
DAX_DIR = PBI / "dax"
REPORT = next((PBI / "pbip").glob("*.Report"))

# palavras que terminam em -s e são singulares (ou não são substantivo contado): não acusam em P1
SINGULAR_S = {
    "dos", "das", "os", "as", "nos", "nas", "aos", "às", "pelos", "pelas", "mais", "menos", "após", "através", "trás",
    "mês", "país", "gás", "bônus", "ônibus", "lápis", "tênis", "simples", "vírus", "atlas", "pires", "três", "seis",
    "deles", "delas", "seus", "suas", "meus", "minhas", "ambos", "vezes", "is", "es",
}
# substantivos contados nas telas: P2 acusa "N > 1" + o singular deles
CONTADOS = ("unidade", "obra", "venda", "página", "contrato", "título", "cliente", "terreno", "empreendimento",
            "permuta", "lote", "bairro", "estágio", "parcela", "mês", "ano", "dia", "SPE", "loja", "apartamento")
P1 = re.compile(r"(?<![\d.,/:\w])1\s+([a-zà-úç]+s)\b", re.I)
P2 = re.compile(r"(?<![\d.,/:\w])(?:[2-9]|[1-9]\d{1,2}|\d{1,3}(?:\.\d{3})+)\s+(" + "|".join(CONTADOS) + r")\b(?![sç])", re.I)
P3 = re.compile(r"\b(páginas|telas)\s+(\d{2})\b(?!\s*[–-]\s*\d|\s*·\s*\d|\s*e\s+\d)", re.I)


def texto(h: str) -> str:
    h = re.sub(r"(?is)<(style|script)\b.*?</\1>", " ", h or "")
    h = re.sub(r"(?s)<[^>]+>", " ¦ ", h)      # cada elemento é um trecho: o número de um não emenda no rótulo do outro
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def achados(t: str) -> list[str]:
    out = []
    for m in P1.finditer(t):
        if m.group(1).lower() not in SINGULAR_S:
            out.append(m)
    out += list(P2.finditer(t)) + list(P3.finditer(t))
    return [t[max(0, m.start() - 40):m.end() + 25] for m in out]


def nomes(prefixo: str) -> list[str]:
    out = []
    for p in sorted(DAX_DIR.rglob("*.dax")):
        if "_modelo" in p.parts:
            continue
        mm = re.search(r"@nome:\s*(.+)", p.read_text(encoding="utf-8"))
        nome = mm.group(1).strip() if mm else p.stem
        if re.search(r"· (HTML|ALT)\b|Fontes · lista", nome) and nome.startswith(prefixo):
            out.append(nome)
    return out


def estaticos() -> list[tuple[str, str]]:
    """(onde, texto) dos textos fixos do relatório: title, alt e rótulos dos visual.json."""
    out = []
    chaves = re.compile(r'"(?:text|altText|title|tooltip|displayName|Value)"\s*:\s*"((?:[^"\\]|\\.)*)"')
    for vj in REPORT.rglob("visual.json"):
        s = vj.read_text(encoding="utf-8")
        for m in chaves.finditer(s):
            v = m.group(1)
            if len(v) > 2 and not v.startswith("'"):
                out.append((vj.parent.name, json.loads('"' + v + '"')))
        for m in re.finditer(r"'((?:[^'\\]|\\.){3,})'", s):     # literais DAX/visuais ('Baixar todas as 12 páginas')
            out.append((vj.parent.name, m.group(1)))
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    prefixo = sys.argv[1] if len(sys.argv) > 1 else ""
    vistos: set[tuple[str, str]] = set()
    total = 0
    ms = nomes(prefixo)
    for nome in ms:
        ref = "[" + nome.replace("]", "]]") + "]"
        consultas = [("sem filtro", f'EVALUATE ROW ( "@t", {ref} )'),
                     ("por obra", f'EVALUATE ADDCOLUMNS ( VALUES ( dObra[Obra] ), "@t", {ref} )')]
        for ctx, q in consultas:
            try:
                linhas = dax.consultar(q)
            except dax.ErroDax as e:
                print(f"ERRO  {nome} [{ctx}]: {str(e)[:200]}")
                total += 1
                continue
            for r in linhas:
                obra = r.get("dObra[Obra]") or ""
                for trecho in achados(texto(r.get("[@t]") or "")):
                    chave = (nome, trecho)
                    if chave in vistos:
                        continue
                    vistos.add(chave)
                    total += 1
                    print(f"ACHADO  {nome} [{obra or ctx}]: …{trecho}…")
    if not prefixo:
        for onde, t in estaticos():
            for trecho in achados(texto(t)):
                if ("estático", trecho) not in vistos:
                    vistos.add(("estático", trecho))
                    total += 1
                    print(f"ACHADO  relatório · {onde}: …{trecho}…")
    print(f"\n{len(ms)} medidas de texto (sem filtro e por obra) e os textos fixos do relatório · {total} achado(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
