# -*- coding: utf-8 -*-
"""desenho_recorte — as medidas comuns do recorte de estado (dono: main; 24/10/2026).

O filtro de estado das telas (paginas/casca.py › _filtro) é uma árvore Região › Estado sobre 'UF'[Caminho]: o filtro
cai no estado, e marcar uma região marca os estados dela (regra L134 do dono: "se resolve a questão da hierarquia
jogando o filtro no último na hierarquia"). A escolha pode ser um estado, uma região inteira ou vários estados soltos,
de uma ou mais regiões. Toda tela lê o recorte destas medidas, nunca de SELECTEDVALUE ( 'UF'[Nome] ).

A leitura vai de cima para baixo, como o gatilho do VizuFilter (general.triggerPathSummary, 2.14.0.0):
  - região com todos os estados marcados sai pelo nome ("Nordeste");
  - estado solto sai pelo nome quando é a única parte ("Bahia") e pela sigla quando há duas ("Nordeste e MG", "MG e SP");
  - com mais de duas partes, a contagem ("3 estados", "19 estados").
O exterior (ZZ) fica fora do filtro; ele só entra pelo clique no quadrado do mapa da apuração (T18) e sai como um
lugar só, "Exterior" ("no exterior"). Um clique que cai fora do filtro (Nordeste no filtro e SP no mapa) deixa o
contexto sem UF: tipo "Vazio" e "nenhum estado" (a T18 avisa antes de chegar aqui).

Medidas gravadas em pbi/dax/_Recorte (uma por arquivo; o núcleo é o mesmo em todas):
  Recorte · com escolha   1 com estado ou região escolhido, 0 no Brasil
  Recorte · partes        quantas partes a leitura tem (0 = Brasil; 1 = um estado ou uma região; 2; 3 ou mais)
  Recorte · UFs           quantas UFs estão no recorte (27 sem escolha; o exterior não conta)
  Recorte · tipo          "Brasil" · "UF" · "Região" · "Vários" (· "Vazio": um clique fora do filtro)
  Recorte · nome          "Brasil" · "Nordeste" · "Bahia" · "MG e SP" · "Nordeste e MG" · "Norte e Nordeste" · "3 estados"
  Recorte · em            "no Brasil" · "no Nordeste" · "na Bahia" · "em Minas Gerais" · "em MG e SP" · "no Nordeste e
                          em MG" · "no Norte e no Nordeste" · "em 3 estados"
  Recorte · de            "do Brasil" · "do Nordeste" · "da Bahia" · "de Minas Gerais" · "de MG e SP" · "do Norte e do
                          Nordeste" · "de 3 estados"
  Recorte · com artigo    "o Brasil" · "o Nordeste" · "a Bahia" · "Minas Gerais" · "MG e SP" · "o Norte e o Nordeste" ·
                          "os 3 estados" (sujeito da frase)
  Recorte · plural        1 quando o recorte nomeia mais de um lugar (o verbo vai ao plural: "MG e SP deram"), 0 no
                          Brasil, num estado ou numa região

    python -X utf8 pbi/scripts/desenho_recorte.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent / "dax" / "_Recorte"

# o núcleo: a escolha lida de cima para baixo (regiões inteiras, depois os estados soltos)
NUCLEO = """-- 1 · A escolha: o filtro de estado (UF[Caminho]) ou um clique que filtra a UF (o mapa da apuração, a região da
--     origem dos votos). O recorte visual do exterior (UF[Tipo]) não conta como escolha
VAR _com =
    ISFILTERED ( 'UF'[Caminho] ) || ISFILTERED ( 'UF'[Nome] ) || ISFILTERED ( 'UF'[UF] )
        || ISFILTERED ( 'UF'[Região] )
VAR _sel =
    SUMMARIZE ( 'UF', 'UF'[UF], 'UF'[Nome], 'UF'[Região], 'UF'[RegiaoOrdem], 'UF'[Ordem], 'UF'[Artigo] )
VAR _tot =
    CALCULATETABLE ( SUMMARIZE ( 'UF', 'UF'[UF], 'UF'[Região] ), REMOVEFILTERS ( 'UF' ) )
-- 2 · Regiões inteiras (todos os estados marcados) e estados soltos
VAR _regioes =
    ADDCOLUMNS (
        DISTINCT ( SELECTCOLUMNS ( _sel, "@r", 'UF'[Região], "@o", 'UF'[RegiaoOrdem] ) ),
        "@s", COUNTROWS ( FILTER ( _sel, 'UF'[Região] = [@r] ) ),
        "@t", COUNTROWS ( FILTER ( _tot, 'UF'[Região] = [@r] ) )
    )
VAR _cheias = FILTER ( _regioes, [@s] = [@t] && [@r] <> "Exterior" )
VAR _nomesCheias = SELECTCOLUMNS ( _cheias, "@r", [@r] )
VAR _soltas = FILTER ( _sel, NOT ( 'UF'[Região] IN _nomesCheias ) )
VAR _nR = COUNTROWS ( _cheias ) + 0
VAR _nU = COUNTROWS ( _soltas ) + 0
VAR _nPartes = IF ( _com, _nR + _nU, 0 )
VAR _vazio = _com && _nR + _nU = 0
VAR _nUFs = COUNTROWS ( FILTER ( _sel, 'UF'[UF] <> "ZZ" ) ) + 0
-- 3 · As partes em ordem (regiões do Norte ao Sul, depois os estados na ordem do filtro); só valem até duas. O
--     exterior (só pelo clique no mapa da apuração) é um lugar solto, em minúscula no meio da frase
VAR _primeiraUF = MINX ( _soltas, 'UF'[Ordem] )
VAR _partes =
    UNION (
        SELECTCOLUMNS (
            _cheias,
            "@ordem", [@o],
            "@nome", [@r],
            "@em", "no " & [@r],
            "@de", "do " & [@r],
            "@art", "o " & [@r]
        ),
        SELECTCOLUMNS (
            _soltas,
            "@ordem", 100 + 'UF'[Ordem],
            "@nome", IF ( 'UF'[UF] = "ZZ", "exterior", 'UF'[UF] ),
            "@em", IF ( 'UF'[Ordem] = _primeiraUF, "em ", "" ) & IF ( 'UF'[UF] = "ZZ", "exterior", 'UF'[UF] ),
            "@de", IF ( 'UF'[Ordem] = _primeiraUF, "de ", "" ) & IF ( 'UF'[UF] = "ZZ", "exterior", 'UF'[UF] ),
            "@art", IF ( 'UF'[UF] = "ZZ", "o exterior", 'UF'[UF] )
        )
    )
-- 4 · A parte única: o estado pelo nome, com o artigo dele ("na Bahia", "em Minas Gerais"); a região com "o"; o
--     exterior com "o" e em minúscula ("no exterior")
VAR _ufNome = MAXX ( _soltas, 'UF'[Nome] )
VAR _ufMin = IF ( MAXX ( _soltas, 'UF'[UF] ) = "ZZ", "exterior", _ufNome )
VAR _ufArtigo = MAXX ( _soltas, 'UF'[Artigo] )
VAR _regNome = MAXX ( _cheias, [@r] )"""

MEDIDAS = [
    ("Recorte · com escolha", "0",
     "1 quando há estado ou região escolhido (o filtro de estado da casca, em árvore Região › Estado, ou um clique que "
     "filtra a UF, como o mapa da apuração); 0 no Brasil. O recorte visual do exterior não conta.",
     "INT (\n    ISFILTERED ( 'UF'[Caminho] ) || ISFILTERED ( 'UF'[Nome] ) || ISFILTERED ( 'UF'[UF] )\n"
     "        || ISFILTERED ( 'UF'[Região] )\n)", False),
    ("Recorte · UFs", "0",
     "Quantas UFs estão no recorte (27 sem escolha; o exterior não conta): a base das contagens 'N de M estados'.",
     "CALCULATE ( COUNTROWS ( 'UF' ), KEEPFILTERS ( 'UF'[Tipo] = \"UF\" ) ) + 0", False),
    ("Recorte · partes", "0",
     "Quantas partes a leitura do recorte tem, de cima para baixo: 0 no Brasil; 1 num estado ou numa região inteira; 2 "
     "em duas partes ('Nordeste e MG', 'MG e SP'); 3 ou mais, quando o texto vira a contagem ('5 estados').",
     "_nPartes", True),
    ("Recorte · tipo", "texto",
     "O tipo do recorte, para as telas escolherem as palavras: 'Brasil' (sem escolha), 'UF' (um estado; 'o estado'), "
     "'Região' (uma região inteira; 'a região') ou 'Vários' (duas ou mais regiões, região e estados, estados soltos; "
     "'os estados escolhidos'). 'Vazio' quando um clique cai fora do filtro e o contexto fica sem UF.",
     "SWITCH (\n    TRUE (),\n    _vazio, \"Vazio\",\n    _nPartes = 0, \"Brasil\",\n"
     "    _nPartes = 1 && _nR = 1, \"Região\",\n    _nPartes = 1, \"UF\",\n    \"Vários\"\n)", True),
    ("Recorte · nome", "texto",
     "O nome do recorte, a medida comum das telas com filtro de estado (pílula, títulos '… · BAHIA', ALTs, manchetes): "
     "'Brasil' sem escolha; a região pelo nome quando está inteira ('Nordeste'); o estado pelo nome quando é um só "
     "('Bahia'); duas partes juntas, com os estados soltos pela sigla ('Nordeste e MG', 'MG e SP', 'Norte e Nordeste'); "
     "com mais de duas, a contagem de estados ('3 estados').",
     "SWITCH (\n    TRUE (),\n    _vazio, \"nenhum estado\",\n    _nPartes = 0, \"Brasil\",\n"
     "    _nPartes = 1 && _nR = 1, _regNome,\n    _nPartes = 1, _ufNome,\n    _nPartes = 2, CONCATENATEX ( _partes, [@nome], \" e \", [@ordem], ASC ),\n"
     "    FORMAT ( _nUFs, \"0\" ) & IF ( _nUFs = 1, \" estado\", \" estados\" )\n)", True),
    ("Recorte · em", "texto",
     "O recorte com a preposição 'em' e o artigo certo, para as frases: 'no Brasil', 'no Nordeste', 'na Bahia', "
     "'no Pará', 'em Minas Gerais', 'em MG e SP', 'no Nordeste e em MG', 'no Norte e no Nordeste', 'em 3 estados'.",
     "SWITCH (\n    TRUE (),\n    _vazio, \"em nenhum estado\",\n    _nPartes = 0, \"no Brasil\",\n"
     "    _nPartes = 1 && _nR = 1, \"no \" & _regNome,\n"
     "    _nPartes = 1, SWITCH ( _ufArtigo, \"a\", \"na \", \"o\", \"no \", \"em \" ) & _ufMin,\n"
     "    _nPartes = 2, CONCATENATEX ( _partes, [@em], \" e \", [@ordem], ASC ),\n"
     "    \"em \" & FORMAT ( _nUFs, \"0\" ) & IF ( _nUFs = 1, \" estado\", \" estados\" )\n)", True),
    ("Recorte · de", "texto",
     "O recorte com a preposição 'de' e o artigo certo, para as frases: 'do Brasil', 'do Nordeste', 'da Bahia', 'do "
     "Pará', 'de Minas Gerais', 'de MG e SP', 'do Nordeste e de MG', 'do Norte e do Nordeste', 'de 3 estados'.",
     "SWITCH (\n    TRUE (),\n    _vazio, \"de nenhum estado\",\n    _nPartes = 0, \"do Brasil\",\n"
     "    _nPartes = 1 && _nR = 1, \"do \" & _regNome,\n"
     "    _nPartes = 1, SWITCH ( _ufArtigo, \"a\", \"da \", \"o\", \"do \", \"de \" ) & _ufMin,\n"
     "    _nPartes = 2, CONCATENATEX ( _partes, [@de], \" e \", [@ordem], ASC ),\n"
     "    \"de \" & FORMAT ( _nUFs, \"0\" ) & IF ( _nUFs = 1, \" estado\", \" estados\" )\n)", True),
    ("Recorte · com artigo", "texto",
     "O recorte como sujeito da frase, com o artigo: 'o Brasil', 'o Nordeste', 'a Bahia', 'o Pará', 'Minas Gerais', "
     "'MG e SP', 'o Nordeste e MG', 'o Norte e o Nordeste', 'os 3 estados'.",
     "SWITCH (\n    TRUE (),\n    _vazio, \"nenhum estado\",\n    _nPartes = 0, \"o Brasil\",\n"
     "    _nPartes = 1 && _nR = 1, \"o \" & _regNome,\n"
     "    _nPartes = 1, IF ( _ufArtigo = \"\", \"\", _ufArtigo & \" \" ) & _ufMin,\n"
     "    _nPartes = 2, CONCATENATEX ( _partes, [@art], \" e \", [@ordem], ASC ),\n"
     "    IF ( _nUFs = 1, \"o estado\", \"os \" & FORMAT ( _nUFs, \"0\" ) & \" estados\" )\n)", True),
    ("Recorte · plural", "0",
     "1 quando o recorte nomeia mais de um lugar ('MG e SP', 'Norte e Nordeste', '3 estados': o verbo vai ao plural); 0 "
     "no Brasil, num estado ou numa região inteira.",
     "IF ( _nPartes >= 2, 1, 0 )", True),
]


def texto(nome: str, formato: str, descricao: str, corpo: str, com_nucleo: bool) -> str:
    cab = f"/*\n@pasta: _Recorte\n@formato: {formato}\n@descricao: {descricao}\n*/\n"
    if not com_nucleo:
        return cab + corpo + "\n"
    ret = "\n".join("    " + l for l in corpo.splitlines())
    return cab + NUCLEO + "\nRETURN\n" + ret + "\n"


def main() -> int:
    PASTA.mkdir(parents=True, exist_ok=True)
    gravados = set()
    for nome, formato, descricao, corpo, nucleo in MEDIDAS:
        destino = PASTA / f"{nome}.dax"
        t = texto(nome, formato, descricao, corpo, nucleo)
        if "\t" in t:
            raise SystemExit(f"{nome}: tab")
        if not destino.exists() or destino.read_text(encoding="utf-8") != t:
            destino.write_text(t, encoding="utf-8", newline="\n")
        gravados.add(destino.name)
    apagados = [p.name for p in PASTA.glob("*.dax") if p.name not in gravados]
    for n in apagados:
        (PASTA / n).unlink()
    print(f"{len(gravados)} medidas em {PASTA} · apagados: {apagados}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
