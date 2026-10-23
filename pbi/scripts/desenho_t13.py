# -*- coding: utf-8 -*-
"""desenho_t13 — gera as medidas da tela 13 · Perfil (contas e desenho).

    python -X utf8 pbi/scripts/desenho_t13.py

Grava pbi/dax/T13 Perfil/{Contas,Desenho}/*.dax. A matriz cruza o porte do município (população do Censo 2022) com o
quinto de renda per capita (quintos nacionais de municípios, cada um com 1.114 cidades); a célula soma os votos das
cidades e compara a margem de Lula de 2022 com a de 2026.

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

_CELULAS = """VAR _c =
    ADDCOLUMNS (
        FILTER (
            SUMMARIZE ( 'Município', 'Município'[Porte], 'Município'[Quinto de renda] ),
            NOT ISBLANK ( 'Município'[Porte] ) && NOT ISBLANK ( 'Município'[Quinto de renda] )
        ),
        "@n", [T13 · cidades],
        "@v", [T13 · variação]
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
        'Município'[Porte] = _p,
        'Município'[Quinto de renda] = _q
    )""", ORACULO + " › celulas › exemplos")

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

desenho("T13 · Matriz · HTML",
        "Matriz porte × quinto de renda: a queda da margem de Lula em cada célula (cor mais escura, queda maior), as "
        "cidades de cada uma, os totais de linha e de coluna e, ao passar o mouse, as três maiores cidades da célula. "
        "Só lê contas 'T13 · …' com filtro de igualdade no porte e no quinto.",
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
VAR _pP = [T13 · maior queda · porte]
VAR _pQ = [T13 · maior queda · quinto]
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
VAR _cel =
    CONCATENATEX (
        CROSSJOIN ( SELECTCOLUMNS ( _portes, "p", [o], "pn", [nome] ), SELECTCOLUMNS ( _quintos, "q", [o], "qn", [nome] ) ),
        VAR _p = [p]
        VAR _q = [q]
        VAR _x = 190 + ( _q - 1 ) * 176
        VAR _y = 166 + ( _p - 1 ) * 100
        VAR _n = CALCULATE ( [T13 · cidades], 'Município'[PorteOrdem] = _p, 'Município'[QuintoOrdem] = _q )
        VAR _v = CALCULATE ( [T13 · variação], 'Município'[PorteOrdem] = _p, 'Município'[QuintoOrdem] = _q )
        VAR _m26 = CALCULATE ( [T13 · margem 2026], 'Município'[PorteOrdem] = _p, 'Município'[QuintoOrdem] = _q )
        VAR _ex = CALCULATE ( [T13 · exemplos], 'Município'[PorteOrdem] = _p, 'Município'[QuintoOrdem] = _q )
        VAR _cls =
            SWITCH (
                TRUE (),
                _n = 0 || ISBLANK ( _v ), "vazia",
                _v >= 0, "c0",
                _v > -0.05, "c1",
                _v > -0.08, "c2",
                _v > -0.11, "c3",
                _v > -0.14, "c4",
                "c5"
            )
        VAR _poucas = IF ( _n > 0 && _n < 10, " poucas", "" )
        VAR _pior = IF ( [pn] = _pP && [qn] = _pQ, " pior", "" )
        VAR _lado = IF ( [q] >= 4, " esq", "" ) & IF ( [p] >= 4, " cima", "" )
        VAR _exEsc = SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( _ex, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )
        RETURN
            "<div class='cel " & _cls & _poucas & _pior & _lado & " brota' style='left:" & _x & "px;top:" & _y
                & "px;animation-delay:" & ( 300 + ( [p] + [q] ) * 70 ) & "ms'>"
                & IF (
                    _cls = "vazia",
                    "<span class='tr'>—</span>",
                    "<span class='num'>" & {_pp("_v")} & "</span><span class='n'>" & FORMAT ( _n, "#,0" )
                        & IF ( _n = 1, " cidade", " cidades" ) & "</span>"
                        & "<div class='card'><b>" & [pn] & " × " & [qn] & "</b><span>Lula em 2026: margem de "
                        & {_pp("_m26")} & " ponto" & IF ( ABS ( _m26 ) >= 0.015, "s", "" ) & "</span><span class='ex'>"
                        & IF ( _n <= 3, "", "Maiores: " ) & _exEsc & "</span></div>"
                )
            & "</div>",
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
        & _cab & _rotLinhas & _cel
        & "<div class='todas entra d9'><b>todas</b><span class='num'>" & {_pp("_tudo")} & "</span>"
            & "<i>soma dos municípios, sem o exterior</i></div>"
        & _rodape
        & "<div class='nota pe entra d12'>Passe o mouse numa célula para ver as maiores cidades dela. — = não há "
            & "município nessa combinação; células claras e tracejadas têm menos de 10 cidades.</div>"
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

desenho("T13 · Resposta · HTML",
        "Coluna da resposta: a maior queda (célula, número e exemplos), a menor queda e como ler a célula (com o "
        "desenho de uma célula anotada e o que é margem). Só lê contas.",
        f"""-- 1 · Leituras
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
VAR _av = _pv
VAR _an = _pn
-- 2 · Textos
VAR _grupo =
    "cidades de " & _pp & IF ( RIGHT ( _pp, 3 ) = "mil", " habitantes", " de habitantes" )
        & " e de renda " & SWITCH ( _pq, "mais ricas", "mais alta", "mais pobres", "mais baixa", "no " & _pq )
VAR _grupoM =
    IF ( _mn = 1, "na única cidade", "nas " & FORMAT ( _mn, "#,0" ) & " cidades" ) & " "
        & "de " & _mp & IF ( RIGHT ( _mp, 3 ) = "mil", " habitantes", " de habitantes" )
        & " e de renda " & SWITCH ( _mq, "mais ricas", "mais alta", "mais pobres", "mais baixa", "no " & _mq )
VAR _verbo = IF ( _pv < 0, "caiu", "subiu" )
VAR _man =
    IF ( NOT ISBLANK ( _uf ), _uf & ": n", "N" ) & "as " & _grupo & ", a margem de Lula " & _verbo & " "
        & FORMAT ( ABS ( _pv ) * 100, "0.0" ) & " pontos"
VAR _txtEx =
    IF ( _pn = 1, "Só uma cidade: ", "São " & FORMAT ( _pn, "#,0" ) & " cidades, como " )
        & SUBSTITUTE ( SUBSTITUTE ( _pe, "&", "&amp;" ), "<", "&lt;" ) & "."
VAR _txtMenor =
    _grupoM & IF ( _mn > 3, ", como ", ": " ) & SUBSTITUTE ( SUBSTITUTE ( _me, "&", "&amp;" ), "<", "&lt;" ) & "."
-- 4 · Marcação
RETURN
    "<div class='tela t13r'>"
        & "<div class='g num lula sobe'>" & {_pp("_pv")} & "<small> p.p.</small></div>"
        & "<div class='man m1 sobe d2'>" & _man & "</div>"
        & "<div class='txt ex entra d4'>" & _txtEx & "</div>"
        & "<div class='menor'>"
            & "<div class='rot entra d6'>" & IF ( _mv > 0, "ONDE A MARGEM DE LULA MAIS SUBIU", "A MENOR QUEDA" ) & "</div>"
            & "<div class='num v sobe d7'>" & {_pp("_mv")} & "<small> p.p.</small></div>"
            & "<div class='txt entra d8'>" & _txtMenor & "</div>"
        & "</div>"
        & "<div class='ler'>"
            & "<div class='rot entra d9'>COMO LER UMA CÉLULA</div>"
            & "<div class='amostra entra d10'><span class='num'>" & IF ( ISBLANK ( _av ), "—", {_pp("_av")} )
                & "</span><span class='n'>" & FORMAT ( _an, "#,0" ) & IF ( _an = 1, " cidade", " cidades" ) & "</span></div>"
            & "<div class='nota qual entra d10'>a célula com contorno vermelho, na matriz</div>"
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
VAR _pv = [T13 · maior queda · variação]
VAR _pp = [T13 · maior queda · porte]
VAR _pq = [T13 · maior queda · quinto]
VAR _mv = [T13 · menor queda · variação]
-- 2 · Textos
RETURN
    "A margem de Lula caiu mais nas cidades " & _pp & " e " & _pq & ": " & {_pp("_pv")} & " pontos. A menor queda: "
        & {_pp("_mv")} & " pontos.\"""")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gravar()
    print(f"T13: {len(MEDIDAS)} medidas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
