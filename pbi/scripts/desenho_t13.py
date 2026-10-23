# -*- coding: utf-8 -*-
"""desenho_t13 — gera as medidas da tela 13 · Perfil (contas e desenho).

    python -X utf8 pbi/scripts/desenho_t13.py

Grava pbi/dax/T13 Perfil/{Contas,Desenho}/*.dax. A matriz cruza o porte do município (população do Censo 2022) com o
quinto de renda per capita (quintos nacionais de municípios, cada um com 1.114 cidades); a célula soma os votos das
cidades e compara a margem de Lula de 2022 com a de 2026.

Interação (23/10/2026): cada célula é um ponto de dado (T13_Matriz_Celulas, granularidade T13 Célula[Célula], tabela de
pbi/modelo/t13_celula.py): o mouse abre o dossiê da célula (ttT13Celula) e o clique filtra as cidades dela na resposta,
que passa a contar a célula escolhida. As contas da matriz inteira (maior e menor queda, posição) tiram o filtro da
célula e mantêm o recorte de UF: REMOVEFILTERS ( 'Município' ) (a tabela expandida leva a célula e a UF) seguido de
VALUES ( 'UF'[UF] ) (a UF do filtro, que a célula não alcança). Assim as contas valem igual na prévia (grão nas colunas
do Município) e no Power BI (grão na T13 Célula).

Oráculo: mockup/data/eleicoes.json › paginas[13] (pipeline/montar_dados_mockup.py › tela_perfil).
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
DAX = PBI / "dax"
TELA = "T13 Perfil"
GERADOR = "pbi/scripts/desenho_t13.py"
ORACULO = "mockup/data/eleicoes.json › paginas[13]"

MEDIDAS: list[dict] = []


def conta(nome: str, formato: str, descricao: str, expr: str, oraculo: str | None = None) -> None:
    MEDIDAS.append({"nome": nome, "sub": "Contas", "pasta": f"{TELA}\\Contas", "formato": formato,
                    "descricao": descricao, "expr": expr, "oraculo": oraculo})


def desenho(nome: str, descricao: str, expr: str) -> None:
    MEDIDAS.append({"nome": nome, "sub": "Desenho", "pasta": f"{TELA}\\Desenho", "formato": "texto",
                    "descricao": descricao, "expr": expr, "oraculo": None})


def gravar() -> None:
    feitos = set()
    for m in MEDIDAS:
        destino = DAX / TELA / m["sub"] / f"{m['nome']}.dax"
        destino.parent.mkdir(parents=True, exist_ok=True)
        cab = ["/*", f"@pasta: {m['pasta']}", f"@formato: {m['formato']}", f"@descricao: {m['descricao']}"]
        if m["oraculo"]:
            cab.append(f"@oraculo: {m['oraculo']}")
        cab += [f"@gerado: {GERADOR}", "*/"]
        corpo = "\n".join(l.rstrip() for l in m["expr"].strip("\n").splitlines())
        if "\t" in corpo:
            raise SystemExit(f"{m['nome']}: tab na expressão")
        texto = "\n".join(cab) + "\n" + corpo + "\n"
        if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
            destino.write_text(texto, encoding="utf-8", newline="\n")
        feitos.add(destino.resolve())
    for p in (DAX / TELA).rglob("*.dax"):
        if p.resolve() not in feitos and f"@gerado: {GERADOR}" in p.read_text(encoding="utf-8"):
            p.unlink()


PORTES = ["até 10 mil", "10 a 50 mil", "50 a 200 mil", "200 mil a 1 milhão", "mais de 1 milhão"]
QUINTOS = ["mais pobres", "2º quinto", "3º quinto", "4º quinto", "mais ricas"]
QUINTOS_TIT = ["MAIS POBRES", "2º QUINTO", "3º QUINTO", "4º QUINTO", "MAIS RICAS"]

# ==================================================================================================== contas
for _a in (2022, 2026):
    conta(f"T13 · saldo {_a}", "#,0", f"Votos de Lula menos os do adversário em {_a}, somados nas cidades do contexto.",
          f"""CALCULATE (
    SUM ( 'Município ano'[VotosPT] ) - SUM ( 'Município ano'[VotosAdversario] ),
    'Município ano'[Ano] = {_a}
)""")
    conta(f"T13 · válidos {_a}", "#,0", f"Votos válidos em {_a}, somados nas cidades do contexto.",
          f"""CALCULATE (
    SUM ( 'Município ano'[Validos] ),
    'Município ano'[Ano] = {_a}
)""")
    conta(f"T13 · margem {_a}", "0.0%", f"Margem de Lula em {_a} somando os votos das cidades do contexto.",
          f"DIVIDE ( [T13 · saldo {_a}], [T13 · válidos {_a}] )", ORACULO + " › celulas › margem26_txt")

conta("T13 · variação", "0.0%",
      "Variação da margem de Lula de 2022 para 2026 nas cidades do contexto (a célula, a linha, a coluna).",
      "[T13 · margem 2026] - [T13 · margem 2022]",
      ORACULO + " › celulas › variacao (até 10 mil × mais ricas = −16,5 p.p.)")
conta("T13 · cidades", "#,0", "Quantos municípios há no contexto (a célula, a linha, a coluna).",
      "COUNTROWS ( 'Município' ) + 0", ORACULO + " › celulas › municipios (465)")
conta("T13 · exemplos", "texto", "As três cidades mais populosas do contexto, separadas por vírgula e 'e'.",
      """VAR _top =
    TOPN ( 3, 'Município', 'Município'[População], DESC, 'Município'[Rótulo], ASC )
VAR _n = COUNTROWS ( _top )
VAR _ultimo =
    MAXX ( TOPN ( 1, _top, 'Município'[População], ASC, 'Município'[Rótulo], DESC ), 'Município'[Rótulo] )
VAR _resto =
    CONCATENATEX (
        FILTER ( _top, 'Município'[Rótulo] <> _ultimo ),
        'Município'[Rótulo],
        ", ",
        'Município'[População], DESC
    )
RETURN
    SWITCH ( TRUE (), _n = 0, BLANK (), _n = 1, _ultimo, _resto & " e " & _ultimo )""",
      ORACULO + " › celulas › exemplos")
conta("T13 · renda mínima", "#,0", "Menor renda per capita do quinto do contexto, no Brasil (ignora a UF).",
      """CALCULATE (
    MIN ( 'Município'[Renda per capita] ),
    ALLEXCEPT ( 'Município', 'Município'[QuintoOrdem], 'Município'[Quinto de renda] )
)""", ORACULO + " › colunas › renda_txt")
conta("T13 · renda máxima", "#,0", "Maior renda per capita do quinto do contexto, no Brasil (ignora a UF).",
      """CALCULATE (
    MAX ( 'Município'[Renda per capita] ),
    ALLEXCEPT ( 'Município', 'Município'[QuintoOrdem], 'Município'[Quinto de renda] )
)""", ORACULO + " › colunas › renda_txt")
conta("T13 · recorte", "texto", "Nome da UF escolhida no filtro da tela (vazio = Brasil).",
      "IF ( ISFILTERED ( 'UF'[Nome] ), SELECTEDVALUE ( 'UF'[Nome] ) )")

_SEM_CELULA = "REMOVEFILTERS ( 'Município' ),\n        VALUES ( 'UF'[UF] )"
_CELULAS = """VAR _c =
    CALCULATETABLE (
        ADDCOLUMNS (
            FILTER (
                SUMMARIZE ( 'Município', 'Município'[Porte], 'Município'[Quinto de renda] ),
                NOT ISBLANK ( 'Município'[Porte] ) && NOT ISBLANK ( 'Município'[Quinto de renda] )
            ),
            "@n", [T13 · cidades],
            "@v", [T13 · variação]
        ),
        REMOVEFILTERS ( 'Município' ),
        VALUES ( 'UF'[UF] )
    )
VAR _piso =
    SWITCH (
        TRUE (),
        COUNTROWS ( FILTER ( _c, [@n] >= 10 && NOT ISBLANK ( [@v] ) ) ) > 0, 10,
        COUNTROWS ( FILTER ( _c, [@n] >= 3 && NOT ISBLANK ( [@v] ) ) ) > 0, 3,
        1
    )
VAR _validas =
    FILTER ( _c, [@n] >= _piso && NOT ISBLANK ( [@v] ) )
VAR _pior =
    TOPN ( 1, _validas, [@v], ASC, 'Município'[Porte], ASC, 'Município'[Quinto de renda], ASC )
VAR _melhor =
    TOPN ( 1, _validas, [@v], DESC, 'Município'[Porte], ASC, 'Município'[Quinto de renda], ASC )"""

for _qual, _tab, _ex in [("pior", "_pior", "maior queda"), ("melhor", "_melhor", "menor queda")]:
    _rot = "maior queda" if _qual == "pior" else "menor queda"
    conta(f"T13 · {_rot} · variação", "0.0%",
          f"Variação da margem na célula de {_rot} (só células com 10 cidades ou mais; com menos no recorte, 3 ou 1).",
          _CELULAS + f"\nRETURN\n    MINX ( {_tab}, [@v] )",
          ORACULO + (" › maior_queda = −16,5 p.p." if _qual == "pior" else " › menor_queda = −3,0 p.p."))
    conta(f"T13 · {_rot} · porte", "texto", f"Porte da célula de {_rot}.",
          _CELULAS + f"\nRETURN\n    MAXX ( {_tab}, 'Município'[Porte] )",
          ORACULO + (" › maior_queda › até 10 mil" if _qual == "pior" else " › menor_queda › mais de 1 milhão"))
    conta(f"T13 · {_rot} · quinto", "texto", f"Quinto de renda da célula de {_rot}.",
          _CELULAS + f"\nRETURN\n    MAXX ( {_tab}, 'Município'[Quinto de renda] )",
          ORACULO + f" › {'maior' if _qual == 'pior' else 'menor'}_queda › mais ricas")
    conta(f"T13 · {_rot} · cidades", "#,0", f"Quantas cidades há na célula de {_rot}.",
          _CELULAS + f"\nRETURN\n    MAXX ( {_tab}, [@n] )",
          ORACULO + (" › maior_queda › 465" if _qual == "pior" else " › menor_queda › 13"))
    conta(f"T13 · {_rot} · exemplos", "texto", f"As três cidades mais populosas da célula de {_rot}.",
          f"""VAR _p = [T13 · {_rot} · porte]
VAR _q = [T13 · {_rot} · quinto]
RETURN
    CALCULATE (
        [T13 · exemplos],
        REMOVEFILTERS ( 'Município' ),
        VALUES ( 'UF'[UF] ),
        'Município'[Porte] = _p,
        'Município'[Quinto de renda] = _q
    )""", ORACULO + " › celulas › exemplos")

# ---- a célula do contexto (a entrada da matriz, o dossiê e a resposta quando há célula clicada)
conta("T13 · ordem do porte", "0", "Ordem do porte da célula do contexto (1 = até 10 mil); posiciona a célula na matriz.",
      "SELECTEDVALUE ( 'Município'[PorteOrdem] )")
conta("T13 · ordem do quinto", "0", "Ordem do quinto de renda da célula do contexto (1 = mais pobres).",
      "SELECTEDVALUE ( 'Município'[QuintoOrdem] )")
conta("T13 · porte da célula", "texto", "Porte da célula do contexto.", "SELECTEDVALUE ( 'Município'[Porte] )")
conta("T13 · quinto da célula", "texto", "Quinto de renda da célula do contexto.",
      "SELECTEDVALUE ( 'Município'[Quinto de renda] )")
conta("T13 · população", "#,0", "População das cidades do contexto (Censo 2022).", "SUM ( 'Município'[População] )")
conta("T13 · nome da cidade", "texto", "Nome (UF) da cidade do contexto.", "SELECTEDVALUE ( 'Município'[Rótulo] )")
conta("T13 · cidades do recorte", "#,0", "Cidades do recorte de UF, sem o clique numa célula.",
      "CALCULATE (\n    [T13 · cidades],\n    REMOVEFILTERS ( 'Município' ),\n    VALUES ( 'UF'[UF] )\n)",
      ORACULO + " › 5.571")
conta("T13 · célula escolhida", "0",
      "1 quando o contexto é uma célula só, menor que o recorte de UF (a célula clicada na matriz); 0 se não. Lê o "
      "Município, não a T13 Célula, para valer também na prévia.",
      """VAR _n = [T13 · cidades]
VAR _tot = [T13 · cidades do recorte]
RETURN
    IF ( HASONEVALUE ( 'Município'[PorteOrdem] ) && HASONEVALUE ( 'Município'[QuintoOrdem] ) && _n < _tot, 1, 0 )""")
conta("T13 · é a célula da maior queda", "0", "1 se a célula do contexto é a de maior queda do recorte; 0 se não.",
      """VAR _p = SELECTEDVALUE ( 'Município'[Porte] )
VAR _q = SELECTEDVALUE ( 'Município'[Quinto de renda] )
RETURN
    IF ( NOT ISBLANK ( _p ) && _p = [T13 · maior queda · porte] && _q = [T13 · maior queda · quinto], 1, 0 )""")
conta("T13 · posição da célula na queda", "0",
      "Posição da célula do contexto entre as células do recorte pela queda da margem (1 = a maior). Só células com o "
      "mínimo de cidades da matriz (10; com menos no recorte, 3 ou 1); vazia nas outras.",
      _CELULAS + """
VAR _n = [T13 · cidades]
VAR _v = [T13 · variação]
RETURN
    IF ( NOT ISBLANK ( _v ) && _n >= _piso, COUNTROWS ( FILTER ( _validas, [@v] < _v ) ) + 1 )""")
conta("T13 · células comparáveis", "0", "Quantas células do recorte entram na comparação (com o mínimo de cidades).",
      _CELULAS + "\nRETURN\n    COUNTROWS ( _validas ) + 0", "19 células com 10 cidades ou mais (motor, 23/10/2026)")
for _nome, _cond, _desc in [
    ("T13 · cidades que viraram", "_d22 > 0 && _d26 < 0", "Cidades do contexto que tinham Lula à frente em 2022 e Flávio em 2026."),
    ("T13 · cidades com Lula à frente nas duas", "_d22 > 0 && _d26 > 0", "Cidades do contexto com Lula à frente em 2022 e em 2026."),
    ("T13 · cidades com o adversário à frente nas duas", "_d22 < 0 && _d26 < 0",
     "Cidades do contexto com o adversário à frente em 2022 (Jair) e em 2026 (Flávio)."),
]:
    conta(_nome, "#,0", _desc + " Conta cidade a cidade.",
          f"""SUMX (
    VALUES ( 'Município'[CodIBGE] ),
    VAR _d22 = [T13 · saldo 2022]
    VAR _d26 = [T13 · saldo 2026]
    RETURN
        IF ( {_cond}, 1 )
) + 0""")

_LINHAS = """VAR _r =
    ADDCOLUMNS (
        FILTER (
            SUMMARIZE ( 'Município', 'Município'[PorteOrdem], 'Município'[Porte] ),
            NOT ISBLANK ( 'Município'[PorteOrdem] )
        ),
        "@v", [T13 · variação]
    )"""
conta("T13 · porte com maior queda", "texto", "Porte (linha) em que a margem de Lula mais caiu.",
      _LINHAS + """
RETURN
    MAXX ( TOPN ( 1, _r, [@v], ASC, 'Município'[PorteOrdem], ASC ), 'Município'[Porte] )""",
      ORACULO + " › linhas (até 10 mil −12,9)")
conta("T13 · queda cresce quando a cidade diminui", "0",
      "1 se, de porte em porte (do maior ao menor), a queda da margem só aumenta; 0 se não.",
      _LINHAS + """
VAR _fora =
    FILTER (
        _r,
        VAR _o = 'Município'[PorteOrdem]
        VAR _v = [@v]
        VAR _maiorAcima = MINX ( FILTER ( _r, 'Município'[PorteOrdem] > _o ), [@v] )
        RETURN
            NOT ISBLANK ( _maiorAcima ) && _v > _maiorAcima
    )
RETURN
    IF ( COUNTROWS ( _r ) >= 3 && ISEMPTY ( _fora ), 1, 0 )""", ORACULO + " › linhas −12,9 · −10,0 · −8,0 · −5,4 · −2,9")
_COLUNAS = """VAR _q =
    ADDCOLUMNS (
        FILTER ( SUMMARIZE ( 'Município', 'Município'[QuintoOrdem] ), NOT ISBLANK ( 'Município'[QuintoOrdem] ) ),
        "@v", [T13 · variação]
    )"""
conta("T13 · menor queda por renda", "0.0%", "A menor queda entre os cinco quintos de renda (o valor mais alto).",
      _COLUNAS + "\nRETURN\n    MAXX ( _q, [@v] )", ORACULO + " › colunas › mais ricas −6,3")
conta("T13 · maior queda por renda", "0.0%", "A maior queda entre os cinco quintos de renda (o valor mais baixo).",
      _COLUNAS + "\nRETURN\n    MINX ( _q, [@v] )", ORACULO + " › colunas › 4º quinto −9,8")


# ==================================================================================================== desenho
def _pp(v: str) -> str:
    return f'FORMAT ( {v} * 100, "+0.0;−0.0;0.0" )'


_TAB_PORTES = ",\n        ".join(f'{{ {i + 1}, "{p}" }}' for i, p in enumerate(PORTES))
_TAB_QUINTOS = ",\n        ".join(f'{{ {i + 1}, "{q}", "{t}" }}' for i, (q, t) in enumerate(zip(QUINTOS, QUINTOS_TIT)))

def _grupo(porte: str, quinto: str, saida: str) -> str:
    """'cidades de até 10 mil habitantes e de renda mais alta' a partir do porte e do quinto (textos das contas)."""
    return f"""VAR {saida} =
    "cidades de " & {porte} & IF ( RIGHT ( {porte}, 3 ) = "mil", " habitantes", " de habitantes" )
        & " e de renda " & SWITCH ( {quinto}, "mais ricas", "mais alta", "mais pobres", "mais baixa", "no " & {quinto} )"""


_CLASSE_VAR = """SWITCH (
                TRUE (),
                {n} = 0 || ISBLANK ( {v} ), "vazia",
                {v} >= 0, "c0",
                {v} > -0.05, "c1",
                {v} > -0.08, "c2",
                {v} > -0.11, "c3",
                {v} > -0.14, "c4",
                "c5"
            )"""

desenho("T13 · Matriz · HTML",
        "A moldura da matriz porte × quinto de renda: título e manchete, as faixas de renda, os portes com o total de "
        "cada linha, as células vazias (sem município no recorte), o total de cada coluna e a nota. As células com "
        "cidades são desenhadas por cima, uma por ponto de dado ('T13 · Células · HTML'). Só lê contas 'T13 · …'.",
        f"""-- 1 · Leituras
VAR _portes =
    DATATABLE (
        "o", INTEGER, "nome", STRING,
        {{
        {_TAB_PORTES}
        }}
    )
VAR _quintos =
    DATATABLE (
        "o", INTEGER, "nome", STRING, "tit", STRING,
        {{
        {_TAB_QUINTOS}
        }}
    )
VAR _cres = [T13 · queda cresce quando a cidade diminui]
VAR _pPorte = [T13 · porte com maior queda]
VAR _qMin = [T13 · menor queda por renda]
VAR _qMax = [T13 · maior queda por renda]
VAR _tudo = [T13 · variação]
-- 2 · Textos
VAR _man =
    IF ( _cres = 1, "Quanto menor a cidade, maior a queda", "A queda foi maior nas cidades de " & _pPorte )
        & "; por renda, entre " & {_pp("_qMax")} & " e " & {_pp("_qMin")} & " pontos"
-- 3 · Geometria e 4 · Marcação (células de 168 × 92 px; colunas a partir de x 190, passo 176; linhas a partir de y 166, passo 100)
VAR _cab =
    CONCATENATEX (
        _quintos,
        VAR _o = [o]
        VAR _x = 190 + ( _o - 1 ) * 176
        VAR _rmin = CALCULATE ( [T13 · renda mínima], 'Município'[QuintoOrdem] = _o )
        VAR _rmax = CALCULATE ( [T13 · renda máxima], 'Município'[QuintoOrdem] = _o )
        RETURN
            "<div class='cq entra d" & [o] & "' style='left:" & _x & "px'><b>" & [tit] & "</b><span>R$ "
                & FORMAT ( _rmin, "#,0" ) & " a R$ " & FORMAT ( _rmax, "#,0" ) & "</span></div>",
        "",
        [o], ASC
    )
VAR _rotLinhas =
    CONCATENATEX (
        _portes,
        VAR _o = [o]
        VAR _y = 166 + ( _o - 1 ) * 100
        VAR _v = CALCULATE ( [T13 · variação], 'Município'[PorteOrdem] = _o )
        VAR _n = CALCULATE ( [T13 · cidades], 'Município'[PorteOrdem] = _o )
        RETURN
            "<div class='rl sobe d" & [o] & "' style='top:" & _y & "px'><b>" & [nome] & "</b><span class='num'>"
                & IF ( _n = 0, "—", {_pp("_v")} ) & "</span><i>" & FORMAT ( _n, "#,0" )
                & IF ( _n = 1, " cidade", " cidades" ) & "</i></div>",
        "",
        [o], ASC
    )
VAR _vazias =
    CONCATENATEX (
        CROSSJOIN ( SELECTCOLUMNS ( _portes, "p", [o] ), SELECTCOLUMNS ( _quintos, "q", [o] ) ),
        VAR _p = [p]
        VAR _q = [q]
        VAR _n = CALCULATE ( [T13 · cidades], 'Município'[PorteOrdem] = _p, 'Município'[QuintoOrdem] = _q )
        RETURN
            IF (
                _n = 0,
                "<div class='cel vazia entra' style='left:" & ( 190 + ( _q - 1 ) * 176 ) & "px;top:"
                    & ( 166 + ( _p - 1 ) * 100 ) & "px'><span class='tr'>—</span></div>"
            ),
        "",
        [p], ASC, [q], ASC
    )
VAR _rodape =
    CONCATENATEX (
        _quintos,
        VAR _o = [o]
        VAR _x = 190 + ( _o - 1 ) * 176
        VAR _v = CALCULATE ( [T13 · variação], 'Município'[QuintoOrdem] = _o )
        RETURN
            "<div class='tq entra d" & ( 8 + [o] ) & "' style='left:" & _x & "px'><span class='num'>"
                & IF ( ISBLANK ( _v ), "—", {_pp("_v")} ) & "</span></div>",
        "",
        [o], ASC
    )
RETURN
    "<div class='tela t13m'>"
        & "<div class='rot entra'>QUEDA DA MARGEM DE LULA, 2022 → 2026 · EM PONTOS</div>"
        & "<div class='man sobe d1'>" & _man & "</div>"
        & "<div class='eixoP rot'>PORTE ↓</div><div class='eixoQ rot'>RENDA POR PESSOA →</div>"
        & _cab & _rotLinhas & _vazias
        & "<div class='todas entra d9'><b>todas</b><span class='num'>" & {_pp("_tudo")} & "</span>"
            & "<i>soma dos municípios, sem o exterior</i></div>"
        & _rodape
        & "<div class='nota pe entra d12'>Passe o mouse numa célula para o dossiê dela; clique para ver a célula na "
            & "resposta, ao lado (clique de novo para voltar). — = não há município nessa combinação; células claras e "
            & "tracejadas têm menos de 10 cidades.</div>"
    & "</div>\"""")

desenho("T13 · Matriz · ALT", "Texto alternativo da matriz porte × renda.",
        f"""-- 1 · Leituras
VAR _v = [T13 · maior queda · variação]
VAR _p = [T13 · maior queda · porte]
VAR _q = [T13 · maior queda · quinto]
VAR _cres = [T13 · queda cresce quando a cidade diminui]
-- 2 · Textos
RETURN
    "Matriz de porte por renda com a queda da margem de Lula em cada grupo de cidades. "
        & IF ( _cres = 1, "Quanto menor a cidade, maior a queda. ", "" )
        & "A maior queda: " & _p & " e " & _q & ", " & {_pp("_v")} & " pontos.\"""")

desenho("T13 · Células · HTML",
        "Uma entrada por célula da matriz (granularidade T13 Célula[Célula]): a queda da margem de Lula e as cidades "
        "da célula, na cor da escala, com contorno vermelho na célula de maior queda e tracejado quando há menos de 10 "
        "cidades. Passar o mouse abre o dossiê (ttT13Celula); o clique filtra as cidades da célula na resposta. Vazia "
        "fora de uma célula com cidades. Só lê contas.",
        f"""-- 1 · Leituras
VAR _p = [T13 · ordem do porte]
VAR _q = [T13 · ordem do quinto]
VAR _n = [T13 · cidades]
VAR _v = [T13 · variação]
VAR _pior = [T13 · é a célula da maior queda]
-- 2 · Textos
VAR _cls =
    {_CLASSE_VAR.format(n="_n", v="_v")}
VAR _poucas = IF ( _n < 10, " poucas", "" )
VAR _clsPior = IF ( _pior = 1, " pior", "" )
-- 3 · Geometria (a mesma da moldura: colunas a partir de x 190, passo 176; linhas a partir de y 166, passo 100)
VAR _x = 190 + ( _q - 1 ) * 176
VAR _y = 166 + ( _p - 1 ) * 100
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _p ) && NOT ISBLANK ( _q ) && _cls <> "vazia",
        "<div class='tela t13c'><div class='cel " & _cls & _poucas & _clsPior & " brota' style='left:" & _x & "px;top:"
            & _y & "px;animation-delay:" & ( 300 + ( _p + _q ) * 70 ) & "ms'>"
            & "<span class='num'>" & {_pp("_v")} & "</span><span class='n'>" & FORMAT ( _n, "#,0" )
            & IF ( _n = 1, " cidade", " cidades" ) & "</span></div></div>"
    )""")

desenho("T13 · Células · ALT", "Texto alternativo da camada de células da matriz.",
        """-- 1 · Leituras
VAR _v = [T13 · maior queda · variação]
-- 2 · Textos
RETURN
    "Células da matriz: passe o mouse para o dossiê de cada grupo de cidades e clique para vê-lo na resposta. A maior "
        & "queda é de " & FORMAT ( _v * 100, "+0.0;−0.0;0.0" ) & " pontos.\"""")

desenho("T13 · Resposta · HTML",
        "Coluna da resposta. Sem clique: a maior queda (célula, número e exemplos), a menor queda e como ler a célula. "
        "Com uma célula clicada na matriz: a queda dessa célula, as cidades dela, a comparação com a maior queda (e a "
        "posição entre as células) e a célula anotada. Só lê contas.",
        f"""-- 1 · Leituras
VAR _sel = [T13 · célula escolhida]
VAR _pv = [T13 · maior queda · variação]
VAR _pp = [T13 · maior queda · porte]
VAR _pq = [T13 · maior queda · quinto]
VAR _pn = [T13 · maior queda · cidades]
VAR _pe = [T13 · maior queda · exemplos]
VAR _mv = [T13 · menor queda · variação]
VAR _mp = [T13 · menor queda · porte]
VAR _mq = [T13 · menor queda · quinto]
VAR _mn = [T13 · menor queda · cidades]
VAR _me = [T13 · menor queda · exemplos]
VAR _uf = [T13 · recorte]
VAR _cv = [T13 · variação]
VAR _cp = [T13 · porte da célula]
VAR _cq = [T13 · quinto da célula]
VAR _cn = [T13 · cidades]
VAR _ce = [T13 · exemplos]
VAR _pos = [T13 · posição da célula na queda]
VAR _ncel = [T13 · células comparáveis]
-- 2 · Textos
VAR _av = IF ( _sel = 1, _cv, _pv )
VAR _an = IF ( _sel = 1, _cn, _pn )
VAR _ap = IF ( _sel = 1, _cp, _pp )
VAR _aq = IF ( _sel = 1, _cq, _pq )
VAR _ae = IF ( _sel = 1, _ce, _pe )
{_grupo("_ap", "_aq", "_grupo")}
VAR _grupoM =
    IF ( _mn = 1, "na única cidade", "nas " & FORMAT ( _mn, "#,0" ) & " cidades" ) & " "
        & "de " & _mp & IF ( RIGHT ( _mp, 3 ) = "mil", " habitantes", " de habitantes" )
        & " e de renda " & SWITCH ( _mq, "mais ricas", "mais alta", "mais pobres", "mais baixa", "no " & _mq )
VAR _grupoP =
    IF ( _pn = 1, "na única cidade", "nas " & FORMAT ( _pn, "#,0" ) & " cidades" ) & " "
        & "de " & _pp & IF ( RIGHT ( _pp, 3 ) = "mil", " habitantes", " de habitantes" )
        & " e de renda " & SWITCH ( _pq, "mais ricas", "mais alta", "mais pobres", "mais baixa", "no " & _pq )
VAR _verbo = IF ( _av < 0, "caiu", "subiu" )
VAR _man =
    IF ( NOT ISBLANK ( _uf ), _uf & ": n", "N" ) & "as " & _grupo & ", a margem de Lula " & _verbo & " "
        & FORMAT ( ABS ( _av ) * 100, "0.0" ) & " pontos"
VAR _txtEx =
    IF ( _an = 1, "Só uma cidade: ", "São " & FORMAT ( _an, "#,0" ) & " cidades, como " )
        & SUBSTITUTE ( SUBSTITUTE ( _ae, "&", "&amp;" ), "<", "&lt;" ) & "."
VAR _txtMenor =
    _grupoM & IF ( _mn > 3, ", como ", ": " ) & SUBSTITUTE ( SUBSTITUTE ( _me, "&", "&amp;" ), "<", "&lt;" ) & "."
VAR _txtPos =
    SWITCH (
        TRUE (),
        ISBLANK ( _pos ), "Com tão poucas cidades, a célula escolhida fica fora da comparação: um caso só pesa demais.",
        _pos = 1, "A célula escolhida é a própria maior queda.",
        _pos = _ncel, "A célula escolhida tem a menor queda entre as " & FORMAT ( _ncel, "0" )
            & " células que entram na comparação.",
        "A célula escolhida é a " & FORMAT ( _pos, "0" ) & "ª maior queda entre as " & FORMAT ( _ncel, "0" )
            & " células que entram na comparação."
    )
VAR _blocoMenor =
    IF (
        _sel = 1,
        "<div class='rot entra d6'>PARA COMPARAR · A MAIOR QUEDA</div>"
            & "<div class='num v sobe d7'>" & {_pp("_pv")} & "<small> p.p.</small></div>"
            & "<div class='txt entra d8'>" & _grupoP & ". " & _txtPos & "</div>",
        "<div class='rot entra d6'>" & IF ( _mv > 0, "ONDE A MARGEM DE LULA MAIS SUBIU", "A MENOR QUEDA" ) & "</div>"
            & "<div class='num v sobe d7'>" & {_pp("_mv")} & "<small> p.p.</small></div>"
            & "<div class='txt entra d8'>" & _txtMenor & "</div>"
    )
VAR _clsAmostra =
    SWITCH (
        TRUE (),
        ISBLANK ( _av ), "",
        _av >= 0, " c0",
        _av > -0.05, " c1",
        _av > -0.08, " c2",
        _av > -0.11, " c3",
        _av > -0.14, " c4",
        " c5"
    )
VAR _qual =
    IF ( _sel = 1, "a célula que você clicou; clique nela de novo para voltar",
        "a célula com contorno vermelho, na matriz" )
-- 4 · Marcação
RETURN
    "<div class='tela t13r'>"
        & "<div class='g num lula sobe'>" & {_pp("_av")} & "<small> p.p.</small></div>"
        & "<div class='man m1 sobe d2'>" & _man & "</div>"
        & "<div class='txt ex entra d4'>" & _txtEx & "</div>"
        & "<div class='menor'>" & _blocoMenor & "</div>"
        & "<div class='ler'>"
            & "<div class='rot entra d9'>COMO LER UMA CÉLULA</div>"
            & "<div class='amostra" & _clsAmostra & " entra d10'><span class='num'>" & IF ( ISBLANK ( _av ), "—", {_pp("_av")} )
                & "</span><span class='n'>" & FORMAT ( _an, "#,0" ) & IF ( _an = 1, " cidade", " cidades" ) & "</span></div>"
            & "<div class='nota qual entra d10'>" & _qual & "</div>"
            & "<div class='mao a1 entra d11'>quanto a margem caiu</div>"
            & "<div class='mao a2 entra d12'>quantas cidades</div>"
            & "<svg class='setas' width='200' height='110' viewBox='0 0 200 110'>"
                & "<path class='traco-rapido' style='animation-delay:1300ms' pathLength='1' d='M6,22 C30,18 46,20 62,26' "
                & "fill='none' stroke='var(--grafite)' stroke-width='1.6' stroke-linecap='round'/>"
                & "<path class='traco-rapido' style='animation-delay:1500ms' pathLength='1' d='M6,86 C30,84 46,80 62,72' "
                & "fill='none' stroke='var(--grafite)' stroke-width='1.6' stroke-linecap='round'/>"
            & "</svg>"
            & "<div class='txt def entra d13'><b>Margem</b> é a diferença entre os votos de Lula e os do adversário, em "
                & "pontos dos votos válidos. Cada célula soma os votos das suas cidades e compara 2022 com 2026; quanto "
                & "mais escuro o azul, maior a queda.</div>"
        & "</div>"
    & "</div>\"""")

desenho("T13 · Resposta · ALT", "Texto alternativo da coluna da resposta.",
        f"""-- 1 · Leituras
VAR _sel = [T13 · célula escolhida]
VAR _pv = [T13 · maior queda · variação]
VAR _pp = [T13 · maior queda · porte]
VAR _pq = [T13 · maior queda · quinto]
VAR _mv = [T13 · menor queda · variação]
VAR _cv = [T13 · variação]
VAR _cp = [T13 · porte da célula]
VAR _cq = [T13 · quinto da célula]
-- 2 · Textos
RETURN
    IF (
        _sel = 1,
        "A célula escolhida, cidades " & _cp & " e " & _cq & ": " & {_pp("_cv")} & " pontos. A maior queda: "
            & {_pp("_pv")} & " pontos.",
        "A margem de Lula caiu mais nas cidades " & _pp & " e " & _pq & ": " & {_pp("_pv")} & " pontos. A menor queda: "
            & {_pp("_mv")} & " pontos."
    )""")

desenho("T13 · Tooltip célula · HTML",
        "Dossiê da célula no tooltip da matriz: o carimbo com a posição na queda, o grupo de cidades e a população, a "
        "margem de Lula de 2022 a 2026 numa régua, como ficaram as cidades (seguiram com Lula, trocaram para Flávio, "
        "seguiram com o adversário) e as três maiores, cada uma com a sua variação. Só lê contas.",
        f"""-- 1 · Leituras
VAR _cp = [T13 · porte da célula]
VAR _cq = [T13 · quinto da célula]
VAR _uf = [T13 · recorte]
VAR _n = [T13 · cidades]
VAR _pop = [T13 · população]
VAR _m22 = [T13 · margem 2022]
VAR _m26 = [T13 · margem 2026]
VAR _v = [T13 · variação]
VAR _vir = [T13 · cidades que viraram]
VAR _ll = [T13 · cidades com Lula à frente nas duas]
VAR _aa = [T13 · cidades com o adversário à frente nas duas]
VAR _pos = [T13 · posição da célula na queda]
VAR _ncel = [T13 · células comparáveis]
VAR _top =
    TOPN (
        3,
        ADDCOLUMNS (
            VALUES ( 'Município'[CodIBGE] ),
            "@pop", [T13 · população],
            "@nome", [T13 · nome da cidade],
            "@v", [T13 · variação]
        ),
        [@pop], DESC,
        'Município'[CodIBGE], ASC
    ) /* lista */
-- 2 · Textos
{_grupo("_cp", "_cq", "_grupo")}
VAR _tit = UPPER ( LEFT ( _cp, 1 ) ) & MID ( _cp, 2, 100 ) & IF ( RIGHT ( _cp, 3 ) = "mil", " habitantes", " de habitantes" )
VAR _renda =
    "renda " & SWITCH ( _cq, "mais ricas", "entre as mais ricas", "mais pobres", "entre as mais pobres", "no " & _cq )
VAR _selo =
    SWITCH (
        TRUE (),
        ISBLANK ( _pos ), "POUCAS CIDADES",
        _v > 0, "SUBIU",
        _pos = 1, "A MAIOR QUEDA",
        _pos = _ncel, "A MENOR QUEDA",
        FORMAT ( _pos, "0" ) & "ª MAIOR QUEDA"
    )
VAR _clsSelo = IF ( _pos = 1, "selo vm", "selo" )
VAR _txtPop =
    SWITCH (
        TRUE (),
        _pop >= 1000000, FORMAT ( _pop / 1000000, "0.0" ) & " mi de habitantes",
        _pop >= 10000, FORMAT ( _pop / 1000, "#,0" ) & " mil habitantes",
        FORMAT ( _pop, "#,0" ) & " habitantes"
    )
VAR _txtNota =
    FORMAT ( _n, "#,0" ) & IF ( _n = 1, " cidade", " cidades" ) & " · " & _txtPop
        & IF ( ISBLANK ( _uf ), "", " · " & _uf )
VAR _txtM22 = FORMAT ( _m22 * 100, "+0.0;−0.0;0.0" )
VAR _txtM26 = FORMAT ( _m26 * 100, "+0.0;−0.0;0.0" )
VAR _mao =
    SWITCH (
        TRUE (),
        _vir = 0 && _ll > _aa, "Lula segue à frente",
        _vir = 0, "nenhuma virou",
        _vir * 2 >= _n, "metade ou mais virou",
        _vir * 10 >= _n, "1 em cada " & FORMAT ( ROUND ( _n / _vir, 0 ), "0" ) & " virou",
        "poucas viraram"
    )
VAR _maiores =
    CONCATENATEX (
        _top,
        VAR _nome = SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( [@nome], "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )
        RETURN
            "<div class='mc'><span class='nm'>" & _nome & "</span><span class='vv " & IF ( [@v] < 0, "neg", "pos" )
                & "'>" & FORMAT ( [@v] * 100, "+0.0;−0.0;0.0" ) & "</span></div>",
        "",
        [@pop], DESC
    )
-- 3 · Geometria (régua de 400 px: zero no meio, ±130 px; os valores ao lado dos pontos; barra das cidades de 400 px)
VAR _esc = MAX ( 0.1, MAX ( ABS ( _m22 ), ABS ( _m26 ) ) ) /* geometria */
VAR _x22 = 200 + 130 * _m22 / _esc
VAR _x26 = 200 + 130 * _m26 / _esc
VAR _esq22 = _x22 <= _x26
VAR _sxE = FORMAT ( MIN ( _x22, _x26 ) - 12, "0.0", "en-US" )
VAR _sxD = FORMAT ( MAX ( _x22, _x26 ) + 12, "0.0", "en-US" )
VAR _cor = IF ( _m26 < 0, "var(--azul)", IF ( _m26 > 0, "var(--vermelho)", "var(--cinza)" ) )
VAR _sx22 = FORMAT ( _x22, "0.0", "en-US" )
VAR _sx26 = FORMAT ( _x26, "0.0", "en-US" )
VAR _tot = MAX ( 1, _ll + _vir + _aa ) /* geometria */
VAR _wll = 400 * _ll / _tot
VAR _wvir = 400 * _vir / _tot
VAR _waa = 400 * _aa / _tot
-- 4 · Marcação
RETURN
    "<div class='tela tt13'><div class='fita'></div>"
        & "<div class='" & _clsSelo & "'>" & _selo & "</div>"
        & "<div class='nm sobe'>" & _tit & "</div>"
        & "<div class='sub sobe d1'>" & _renda & "</div>"
        & "<div class='nota sobe d1'>" & _txtNota & "</div>"
        & "<div class='rot r1 entra d2'>MARGEM DE LULA NA CÉLULA · 2022 → 2026</div>"
        & "<svg class='regua' width='400' height='54' viewBox='0 0 400 54'>"
            & "<line x1='200' x2='200' y1='4' y2='38' class='zero'/>"
            & "<text x='196' y='52' text-anchor='end' class='lado'>← adversário</text>"
            & "<text x='204' y='52' class='lado'>Lula →</text>"
            & "<line class='traco-rapido' pathLength='1' style='animation-delay:300ms' x1='" & _sx22 & "' x2='" & _sx26
                & "' y1='22' y2='22'/>"
            & "<circle cx='" & _sx22 & "' cy='22' r='6' class='m22'/>"
            & "<circle class='brota' style='animation-delay:700ms' cx='" & _sx26 & "' cy='22' r='7' fill='" & _cor & "'/>"
            & "<text x='" & _sxE & "' y='27' text-anchor='end'>" & IF ( _esq22, _txtM22, _txtM26 ) & "</text>"
            & "<text x='" & _sxD & "' y='27'>" & IF ( _esq22, _txtM26, _txtM22 ) & "</text>"
        & "</svg>"
        & "<div class='rot r2 entra d3'>COMO FICARAM AS CIDADES · 2022 → 2026</div>"
        & "<div class='pilha entra d4'>"
            & "<i class='ll barra-x' style='width:" & FORMAT ( _wll, "0.0", "en-US" ) & "px'></i>"
            & "<i class='vir barra-x' style='width:" & FORMAT ( _wvir, "0.0", "en-US" ) & "px'></i>"
            & "<i class='aa barra-x' style='width:" & FORMAT ( _waa, "0.0", "en-US" ) & "px'></i>"
        & "</div>"
        & "<div class='leg entra d5'><span><i class='ll'></i>Lula nas duas <b>" & FORMAT ( _ll, "#,0" ) & "</b></span>"
            & "<span><i class='vir'></i>viraram <b>" & FORMAT ( _vir, "#,0" ) & "</b></span>"
            & "<span><i class='aa'></i>adversário nas duas <b>" & FORMAT ( _aa, "#,0" ) & "</b></span></div>"
        & "<div class='rot r3 entra d6'>" & IF ( _n <= 3, "AS CIDADES", "AS MAIORES" ) & " · VARIAÇÃO DA MARGEM</div>"
        & "<div class='maiores entra d7'>" & _maiores & "</div>"
        & "<div class='mao entra d8'>" & _mao & "</div>"
    & "</div>\"""")

desenho("T13 · Tooltip célula · ALT", "Texto alternativo do dossiê da célula.",
        f"""-- 1 · Leituras
VAR _cp = [T13 · porte da célula]
VAR _cq = [T13 · quinto da célula]
VAR _n = [T13 · cidades]
VAR _vir = [T13 · cidades que viraram]
VAR _m22 = [T13 · margem 2022]
VAR _m26 = [T13 · margem 2026]
-- 2 · Textos
RETURN
    "Cidades " & _cp & " e " & _cq & ": " & FORMAT ( _n, "#,0" ) & IF ( _n = 1, " cidade", " cidades" )
        & "; a margem de Lula foi de " & {_pp("_m22")} & " para " & {_pp("_m26")} & " pontos; "
        & FORMAT ( _vir, "#,0" ) & IF ( _vir = 1, " trocou", " trocaram" ) & " Lula por Flávio.\"""")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gravar()
    print(f"T13: {len(MEDIDAS)} medidas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
