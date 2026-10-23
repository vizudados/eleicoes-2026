# -*- coding: utf-8 -*-
"""desenho_t12 — gera as medidas da tela 12 · Estados (contas e desenho).

    python -X utf8 pbi/scripts/desenho_t12.py

Grava pbi/dax/T12 Estados/{Contas,Desenho}/*.dax. As contas de UF leem `Candidato UF` (votos por candidato e UF,
2022 e 2026, com o exterior ZZ): Lula = número 13, adversário = número 22 (PL: Jair em 2022, Flávio em 2026). Conferido
no motor em 23/10/2026: a soma por UF é igual à soma dos municípios (Município ano), que é a conta do oráculo.

Oráculo: mockup/data/eleicoes.json › paginas[12] (pipeline/montar_dados_mockup.py › tela_estados).
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
DAX = PBI / "dax"
TELA = "T12 Estados"
GERADOR = "pbi/scripts/desenho_t12.py"
ORACULO = "mockup/data/eleicoes.json › paginas[12]"

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


ESC = 'SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {v}, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )'

# ==================================================================================================== contas
for _a in (2022, 2026):
    _adv = "Jair Bolsonaro" if _a == 2022 else "Flávio Bolsonaro"
    conta(f"T12 · votos de Lula {_a}", "#,0", f"Votos de Lula (PT, 13) em {_a} no recorte de UF (Candidato UF).",
          f"""CALCULATE (
    SUM ( 'Candidato UF'[Votos] ),
    'Candidato UF'[Ano] = {_a},
    'Candidato UF'[Número] = 13
)""")
    conta(f"T12 · votos do PL {_a}", "#,0", f"Votos de {_adv} (PL, 22) em {_a} no recorte de UF.",
          f"""CALCULATE (
    SUM ( 'Candidato UF'[Votos] ),
    'Candidato UF'[Ano] = {_a},
    'Candidato UF'[Número] = 22
)""")
    conta(f"T12 · válidos {_a}", "#,0", f"Votos válidos (soma de todos os candidatos) em {_a} no recorte de UF.",
          f"""CALCULATE (
    SUM ( 'Candidato UF'[Votos] ),
    'Candidato UF'[Ano] = {_a}
)""")
    conta(f"T12 · margem {_a}", "0.0%", f"Margem de Lula em {_a}: (Lula − {_adv}) ÷ válidos. Positivo, Lula à frente.",
          f"DIVIDE ( [T12 · votos de Lula {_a}] - [T12 · votos do PL {_a}], [T12 · válidos {_a}] )",
          ORACULO + f" › ufs › margem{str(_a)[2:]}")
    conta(f"T12 · Lula % {_a}", "0.0%", f"Votos de Lula sobre os válidos em {_a}.",
          f"DIVIDE ( [T12 · votos de Lula {_a}], [T12 · válidos {_a}] )", ORACULO + " › ufs › lula26_txt")
    conta(f"T12 · PL % {_a}", "0.0%", f"Votos de {_adv} sobre os válidos em {_a}.",
          f"DIVIDE ( [T12 · votos do PL {_a}], [T12 · válidos {_a}] )", ORACULO + " › ufs › flavio26_txt")
    conta(f"T12 · margem do Brasil {_a}", "0.0%", f"Margem de Lula no Brasil em {_a}, com o exterior (ignora a UF).",
          f"CALCULATE ( [T12 · margem {_a}], REMOVEFILTERS ( 'UF' ) )", "paginas[14] › anos (PT − adversário)")
    conta(f"T12 · Lula % do Brasil {_a}", "0.0%", f"Lula sobre os válidos no Brasil em {_a}, com o exterior.",
          f"CALCULATE ( [T12 · Lula % {_a}], REMOVEFILTERS ( 'UF' ) )", "paginas[14] › anos › pt › pct")
    conta(f"T12 · PL % do Brasil {_a}", "0.0%", f"{_adv} sobre os válidos no Brasil em {_a}, com o exterior.",
          f"CALCULATE ( [T12 · PL % {_a}], REMOVEFILTERS ( 'UF' ) )", "paginas[14] › anos › adversario › pct")

conta("T12 · variação", "0.0%", "Variação da margem de Lula de 2022 para 2026 (pontos percentuais em fração).",
      "[T12 · margem 2026] - [T12 · margem 2022]", ORACULO + " › ufs › variacao (TO −13,4; DF +1,6)")
conta("T12 · variação do Brasil", "0.0%", "Variação da margem de Lula no Brasil, 2022 → 2026, com o exterior.",
      "[T12 · margem do Brasil 2026] - [T12 · margem do Brasil 2022]", "+5,2 → −1,9 = −7,1 p.p. (motor)")
conta("T12 · posição", "0",
      "Ordem da unidade (as 27 e o exterior) da maior queda de margem para a maior alta; posiciona a linha.",
      """VAR _v = [T12 · variação]
RETURN
    IF (
        NOT ISBLANK ( _v ),
        COUNTROWS ( FILTER ( ALL ( 'UF' ), [T12 · variação] < _v ) ) + 1
    )""", ORACULO + " › ufs (ordem por variação)")
conta("T12 · ordem da queda", "0", "Posição da UF entre as 27 pela queda da margem (1 = a que mais caiu). Exterior fica vazio.",
      """VAR _v = [T12 · variação]
RETURN
    IF (
        NOT ISBLANK ( _v ) && SELECTEDVALUE ( 'UF'[Tipo] ) = "UF",
        COUNTROWS ( FILTER ( ALL ( 'UF' ), 'UF'[Tipo] = "UF" && [T12 · variação] < _v ) ) + 1
    )""")
conta("T12 · unidades", "0", "Unidades da federação no recorte (27 no Brasil; sem o exterior).",
      """CALCULATE ( COUNTROWS ( 'UF' ), 'UF'[Tipo] = "UF" ) + 0""", ORACULO + " › 27")
conta("T12 · unidades onde a margem caiu", "0", "UFs (sem o exterior) em que a margem de Lula caiu de 2022 para 2026.",
      """CALCULATE (
    COUNTROWS ( FILTER ( VALUES ( 'UF'[UF] ), [T12 · variação] < 0 ) ),
    'UF'[Tipo] = "UF"
) + 0""", ORACULO + " › 26")
conta("T12 · unidades onde a margem subiu", "0", "UFs (sem o exterior) em que a margem de Lula subiu.",
      """CALCULATE (
    COUNTROWS ( FILTER ( VALUES ( 'UF'[UF] ), [T12 · variação] > 0 ) ),
    'UF'[Tipo] = "UF"
) + 0""", ORACULO + " › excecoes = DF")
conta("T12 · onde a margem subiu", "texto", "Nomes das UFs em que a margem de Lula subiu, em ordem alfabética.",
      """CALCULATE (
    CONCATENATEX (
        FILTER ( VALUES ( 'UF'[Nome] ), [T12 · variação] > 0 ),
        'UF'[Nome],
        ", ",
        'UF'[Nome], ASC
    ),
    'UF'[Tipo] = "UF"
)""", ORACULO + " › excecoes › Distrito Federal")
conta("T12 · alta onde a margem subiu", "0.0%", "Variação da margem na UF em que ela subiu (quando é uma só).",
      """CALCULATE (
    MAXX ( FILTER ( VALUES ( 'UF'[UF] ), [T12 · variação] > 0 ), [T12 · variação] ),
    'UF'[Tipo] = "UF"
)""", ORACULO + " › excecoes › +1,6 p.p.")
conta("T12 · mudaram para o adversário", "texto",
      "Nomes das UFs com Lula à frente em 2022 e Flávio em 2026, em ordem alfabética, ligados por vírgula e 'e'.",
      """VAR _t =
    CALCULATETABLE (
        FILTER ( VALUES ( 'UF'[Nome] ), [T12 · margem 2022] > 0 && [T12 · margem 2026] < 0 ),
        'UF'[Tipo] = "UF"
    )
VAR _n = COUNTROWS ( _t )
VAR _ultimo = MAXX ( _t, 'UF'[Nome] )
VAR _resto = CONCATENATEX ( FILTER ( _t, 'UF'[Nome] <> _ultimo ), 'UF'[Nome], ", ", 'UF'[Nome], ASC )
RETURN
    SWITCH ( TRUE (), _n = 0, BLANK (), _n = 1, _ultimo, _resto & " e " & _ultimo )""",
      ORACULO + " › estados_que_mudaram_de_lado (Minas Gerais e Tocantins)")
conta("T12 · quantas mudaram para o adversário", "0", "Quantas UFs passaram de Lula à frente para Flávio à frente.",
      """CALCULATE (
    COUNTROWS ( FILTER ( VALUES ( 'UF'[UF] ), [T12 · margem 2022] > 0 && [T12 · margem 2026] < 0 ) ),
    'UF'[Tipo] = "UF"
) + 0""", ORACULO + " › 2")
conta("T12 · quantas mudaram para Lula", "0", "Quantas UFs passaram do adversário à frente para Lula à frente.",
      """CALCULATE (
    COUNTROWS ( FILTER ( VALUES ( 'UF'[UF] ), [T12 · margem 2022] < 0 && [T12 · margem 2026] > 0 ) ),
    'UF'[Tipo] = "UF"
) + 0""", "0 (motor)")
conta("T12 · nome da unidade", "texto", "Nome da UF da linha (Exterior para ZZ).", "SELECTEDVALUE ( 'UF'[Nome] )")
conta("T12 · sigla da unidade", "texto", "Sigla da UF da linha (EX para o exterior).",
      """VAR _s = SELECTEDVALUE ( 'UF'[UF] )
RETURN
    IF ( _s = "ZZ", "EX", _s )""")
conta("T12 · região da unidade", "texto", "Região da UF da linha.", "SELECTEDVALUE ( 'UF'[Região] )")
for _a in (2022, 2026):
    conta(f"T12 · saldo municipal {_a}", "#,0", f"Votos de Lula menos os do adversário em {_a}, pelos municípios (sem exterior).",
          f"""CALCULATE (
    SUM ( 'Município ano'[VotosPT] ) - SUM ( 'Município ano'[VotosAdversario] ),
    'Município ano'[Ano] = {_a}
)""")
conta("T12 · municípios que viraram", "#,0", "Municípios da UF com Lula à frente em 2022 e Flávio em 2026.",
      """SUMX (
    VALUES ( 'Município'[CodIBGE] ),
    VAR _d22 = [T12 · saldo municipal 2022]
    VAR _d26 = [T12 · saldo municipal 2026]
    RETURN
        IF ( _d22 > 0 && _d26 < 0, 1 )
) + 0""", ORACULO + " › ufs › municipios_que_viraram (TO 37, MG 178)")
conta("T12 · municípios", "#,0", "Municípios da UF com votos em 2026.",
      """SUMX (
    VALUES ( 'Município'[CodIBGE] ),
    IF ( NOT ISBLANK ( [T12 · saldo municipal 2026] ), 1 )
) + 0""", ORACULO + " › ufs › municipios (TO 139)")


# ==================================================================================================== desenho
def _pp(v: str) -> str:
    return f'FORMAT ( {v} * 100, "+0.0;−0.0;0.0" )'


def _x(v: str, x0: int, larg: int, lim: float) -> str:
    """posição em px de uma margem (fração) num eixo de −lim a +lim (fração) que começa em x0 e tem larg px."""
    return f"( {x0} + {larg} * ( MAX ( -{lim}, MIN ( {lim}, {v} ) ) + {lim} ) / {2 * lim} )"


desenho("T12 · Resposta · HTML",
        "Coluna da resposta: em quantas unidades a margem de Lula caiu, quem mudou de lado, a exceção, o que é "
        "margem (com o Brasil 2022 e 2026) e as cinco regiões. Só lê contas 'T12 · …'.",
        f"""-- 1 · Leituras
VAR _caiu = [T12 · unidades onde a margem caiu]
VAR _tot = [T12 · unidades]
VAR _nSubiu = [T12 · unidades onde a margem subiu]
VAR _subiu = [T12 · onde a margem subiu]
VAR _alta = [T12 · alta onde a margem subiu]
VAR _mudaram = [T12 · mudaram para o adversário]
VAR _nMud = [T12 · quantas mudaram para o adversário]
VAR _nMudL = [T12 · quantas mudaram para Lula]
VAR _l22 = [T12 · Lula % do Brasil 2022]
VAR _a22 = [T12 · PL % do Brasil 2022]
VAR _l26 = [T12 · Lula % do Brasil 2026]
VAR _a26 = [T12 · PL % do Brasil 2026]
VAR _m22 = [T12 · margem do Brasil 2022]
VAR _m26 = [T12 · margem do Brasil 2026]
VAR _dBr = [T12 · variação do Brasil]
VAR _reg =
    ADDCOLUMNS (
        DATATABLE ( "Região", STRING, {{ {{ "Norte" }}, {{ "Nordeste" }}, {{ "Centro-Oeste" }}, {{ "Sudeste" }}, {{ "Sul" }} }} ),
        "@m22", VAR _r = [Região] RETURN CALCULATE ( [T12 · margem 2022], 'UF'[Região] = _r ),
        "@m26", VAR _r = [Região] RETURN CALCULATE ( [T12 · margem 2026], 'UF'[Região] = _r ),
        "@d", VAR _r = [Região] RETURN CALCULATE ( [T12 · variação], 'UF'[Região] = _r )
    )
-- 2 · Textos
VAR _txtMud =
    SWITCH (
        TRUE (),
        _nMud = 0 && _nMudL = 0, "Nenhuma unidade mudou de lado",
        _nMud = 0, "Nenhuma unidade passou para o lado de Flávio",
        _nMud = 1, "<span class='sub'>" & _mudaram & "</span> mudou de lado",
        "<span class='sub'>" & _mudaram & "</span> mudaram de lado"
    )
VAR _txtSubiu =
    SWITCH (
        TRUE (),
        _nSubiu = 0, "A margem de Lula não subiu em nenhuma unidade.",
        _nSubiu = 1, "Só " & IF ( _subiu = "Distrito Federal", "o ", "" ) & _subiu & " foi na direção de Lula: <b>"
            & {_pp("_alta")} & " p.p.</b>",
        FORMAT ( _nSubiu, "0" ) & " unidades foram na direção de Lula: " & _subiu & "."
    )
VAR _txtUnid = IF ( _caiu = 1, "unidade em que", "unidades em que" )
-- 3 · Geometria (barras do Brasil: 100% = 300 px; mini eixos das regiões de −50 a +50 p.p. em 250 px)
VAR _wl22 = 300 * _l22 -- geometria
VAR _wa22 = 300 * _a22 -- geometria
VAR _wl26 = 300 * _l26 -- geometria
VAR _wa26 = 300 * _a26 -- geometria
VAR _linhasReg =
    CONCATENATEX (
        _reg,
        VAR _pos = RANKX ( _reg, [@d], , ASC, Dense ) /* geometria */
        VAR _x22 = {_x("[@m22]", 10, 290, 0.45)}
        VAR _x26 = {_x("[@m26]", 10, 290, 0.45)}
        VAR _cor = IF ( [@m26] < 0, "var(--azul)", "var(--vermelho)" )
        VAR _cor22 = IF ( [@m22] < 0, "var(--azul)", "var(--vermelho)" )
        VAR _nota =
            IF ( [@m22] > 0 && [@m26] < 0, " <span class='mao mud'>passou para Flávio</span>", "" )
        RETURN
            "<div class='rg sobe d" & ( 8 + _pos ) & "' style='top:" & ( 30 + ( _pos - 1 ) * 46 ) & "px'>"
                & "<div class='nm'>" & [Região] & _nota & "</div>"
                & "<div class='vv'>" & {_pp("[@m22]")} & " → " & {_pp("[@m26]")} & "</div>"
                & "<svg class='mini' width='310' height='20' viewBox='0 0 310 20'>"
                    & "<line x1='155' x2='155' y1='0' y2='20' class='zero'/>"
                    & "<line class='traco-rapido' pathLength='1' style='animation-delay:" & ( 1200 + _pos * 90 )
                        & "ms' x1='" & FORMAT ( _x22, "0.0", "en-US" ) & "' x2='" & FORMAT ( _x26, "0.0", "en-US" )
                        & "' y1='10' y2='10'/>"
                    & "<circle cx='" & FORMAT ( _x22, "0.0", "en-US" ) & "' cy='10' r='4.5' class='m22' stroke='"
                        & _cor22 & "'/>"
                    & "<circle class='brota' style='animation-delay:" & ( 1500 + _pos * 90 ) & "ms' cx='"
                        & FORMAT ( _x26, "0.0", "en-US" ) & "' cy='10' r='5.5' fill='" & _cor & "'/>"
                & "</svg>"
                & "<div class='dv'>" & {_pp("[@d]")} & "</div>"
            & "</div>",
        "",
        [@d], ASC
    )
-- 4 · Marcação
VAR _barra =
    "<div class='ano'>{{ANO}}</div><div class='tr'><i class='bl barra-x' style='width:{{WL}}px'></i>"
        & "<i class='ba barra-x-dir' style='width:{{WA}}px'></i></div>"
VAR _brasil =
    "<div class='br'>"
        & "<div class='lnb'>" & SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( _barra, "{{ANO}}", "2022" ), "{{WL}}",
            FORMAT ( _wl22, "0.0", "en-US" ) ), "{{WA}}", FORMAT ( _wa22, "0.0", "en-US" ) )
            & "<div class='pc'><span class='lula'>" & FORMAT ( _l22, "0.0%" ) & "</span> × <span class='flavio'>"
            & FORMAT ( _a22, "0.0%" ) & "</span></div><div class='mg num'>" & {_pp("_m22")} & "</div></div>"
        & "<div class='lnb'>" & SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( _barra, "{{ANO}}", "2026" ), "{{WL}}",
            FORMAT ( _wl26, "0.0", "en-US" ) ), "{{WA}}", FORMAT ( _wa26, "0.0", "en-US" ) )
            & "<div class='pc'><span class='lula'>" & FORMAT ( _l26, "0.0%" ) & "</span> × <span class='flavio'>"
            & FORMAT ( _a26, "0.0%" ) & "</span></div><div class='mg num'>" & {_pp("_m26")} & "</div></div>"
    & "</div>"
RETURN
    "<div class='tela t12r'>"
        & "<div class='topo sobe'><span class='num g'>" & FORMAT ( _caiu, "0" ) & "</span><span class='de'>de</span>"
            & "<span class='num g'>" & FORMAT ( _tot, "0" ) & "</span></div>"
        & "<div class='man t1 sobe d2'>" & _txtUnid & " a margem de <span class='lula'>Lula</span> caiu de 2022 "
            & "para 2026</div>"
        & "<div class='man t2 sobe d3'>" & _txtMud
            & "<svg width='300' height='14' viewBox='0 0 300 14'><path class='traco' style='animation-delay:1100ms' "
            & "pathLength='1' d='M3,9 C60,4 150,12 296,5' fill='none' stroke='var(--azul)' stroke-width='5' "
            & "stroke-linecap='round'/></svg></div>"
        & "<div class='txt t3 entra d5'>" & _txtSubiu & "</div>"
        & "<div class='margem'>"
            & "<div class='rot entra d6'>O QUE É MARGEM</div>"
            & "<div class='txt ex entra d6'>É a distância entre os votos de Lula e os do adversário, em pontos dos "
                & "votos válidos: positiva, Lula à frente; negativa, o adversário. No Brasil, foi de "
                & {_pp("_m22")} & " para " & {_pp("_m26")} & " pontos: " & IF ( _dBr < 0, "caiu ", "subiu " )
                & FORMAT ( ABS ( _dBr ) * 100, "0.0" ) & ".</div>"
            & _brasil
        & "</div>"
        & "<div class='regioes'>"
            & "<div class='rot entra d8'>POR REGIÃO · MARGEM DE LULA 2022 → 2026</div>"
            & _linhasReg
        & "</div>"
    & "</div>\"""")

desenho("T12 · Resposta · ALT", "Texto alternativo da coluna da resposta.",
        """-- 1 · Leituras
VAR _caiu = [T12 · unidades onde a margem caiu]
VAR _tot = [T12 · unidades]
VAR _mudaram = [T12 · mudaram para o adversário]
VAR _subiu = [T12 · onde a margem subiu]
-- 2 · Textos
RETURN
    "A margem de Lula caiu em " & FORMAT ( _caiu, "0" ) & " de " & FORMAT ( _tot, "0" ) & " unidades. "
        & IF ( NOT ISBLANK ( _mudaram ), _mudaram & " passaram de Lula para Flávio. ", "" )
        & IF ( NOT ISBLANK ( _subiu ) && _subiu <> "", "Subiu em: " & _subiu & ".", "" )""")

desenho("T12 · Corrida título · HTML", "Título da corrida das unidades: a direção das setas e a legenda.",
        f"""-- 1 · Leituras
VAR _nSubiu = [T12 · unidades onde a margem subiu]
VAR _subiu = [T12 · onde a margem subiu]
-- 2 · Textos
VAR _man =
    SWITCH (
        TRUE (),
        _nSubiu = 0, "Todas as setas apontam para a esquerda, a direção do adversário",
        _nSubiu = 1, "Quase todas as setas vão para a esquerda; só " & IF ( _subiu = "Distrito Federal", "o ", "" )
            & _subiu & " foi na direção de Lula",
        "A maioria das setas vai para a esquerda; " & FORMAT ( _nSubiu, "0" ) & " unidades foram na direção de Lula"
    )
-- 4 · Marcação
RETURN
    "<div class='tela t12t'>"
        & "<div class='rot entra'>MARGEM DE LULA EM CADA UNIDADE · 2022 → 2026, DA MAIOR QUEDA À ALTA</div>"
        & "<div class='man sobe d1'>" & _man & "</div>"
        & "<div class='leg entra d3'><span><i class='o'></i>2022</span><span><i class='f vm'></i><i class='f az'></i>"
            & "2026: vermelho, Lula à frente; azul, Flávio</span><span><i class='mud'></i>mudou de lado</span>"
            & "<span class='dir'>variação, em pontos</span></div>"
    & "</div>\"""")

desenho("T12 · Corrida título · ALT", "Texto alternativo do título da corrida.",
        """-- 1 · Leituras
VAR _nSubiu = [T12 · unidades onde a margem subiu]
-- 2 · Textos
RETURN
    "Margem de Lula em cada unidade, de 2022 para 2026, ordenada da maior queda à alta; "
        & FORMAT ( _nSubiu, "0" ) & IF ( _nSubiu = 1, " unidade subiu.", " unidades subiram." )""")

desenho("T12 · Corrida · HTML",
        "Uma linha por unidade (granularidade UF): o ponto de 2022, a seta até 2026 (que desliza na entrada), a "
        "variação e a marca de quem mudou de lado. Posição vertical pela conta 'T12 · posição'.",
        f"""-- 1 · Leituras
VAR _pos = [T12 · posição]
VAR _nome = [T12 · nome da unidade]
VAR _m22 = [T12 · margem 2022]
VAR _m26 = [T12 · margem 2026]
VAR _d = [T12 · variação]
-- 2 · Textos
VAR _txtNome = {ESC.format(v="_nome")}
VAR _mud = _m22 > 0 && _m26 < 0
VAR _mudL = _m22 < 0 && _m26 > 0
VAR _clsLinha =
    "lin" & IF ( _mud || _mudL, " mud", "" ) & IF ( _d > 0, " sobe-m", "" ) & IF ( _nome = "Exterior", " ext", "" )
VAR _cor26 = IF ( _m26 < 0, "var(--azul)", "var(--vermelho)" )
VAR _cor22 = IF ( _m22 < 0, "var(--azul)", "var(--vermelho)" )
VAR _marca =
    SWITCH ( TRUE (), _mud, "<span class='mm'>mudou de lado</span>", _mudL, "<span class='mm vm'>mudou de lado</span>", "" )
-- 3 · Geometria (eixo de −60 a +60 p.p. em 680 px, a partir de x 210; zero em 550)
VAR _y = 18 + ( _pos - 1 ) * 25.4
VAR _x22 = {_x("_m22", 210, 680, 0.6)}
VAR _x26 = {_x("_m26", 210, 680, 0.6)}
VAR _sy = FORMAT ( _y, "0.0", "en-US" )
VAR _atraso = 250 + _pos * 45
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _pos ),
        "<div class='tela " & _clsLinha & "'>"
            & "<div class='alvo' style='top:" & FORMAT ( _y - 12, "0.0", "en-US" ) & "px'></div>"
            & "<div class='nm sobe' style='top:" & FORMAT ( _y - 11, "0.0", "en-US" ) & "px;animation-delay:"
                & _atraso & "ms'>" & _txtNome & _marca & "</div>"
            & "<svg class='sv' width='1010' height='760' viewBox='0 0 1010 760'>"
                & "<line class='traco' pathLength='1' style='animation-delay:" & ( _atraso + 500 ) & "ms' x1='"
                    & FORMAT ( _x22, "0.0", "en-US" ) & "' x2='" & FORMAT ( _x26, "0.0", "en-US" ) & "' y1='" & _sy
                    & "' y2='" & _sy & "'/>"
                & "<circle cx='" & FORMAT ( _x22, "0.0", "en-US" ) & "' cy='" & _sy & "' r='5.5' class='m22' stroke='"
                    & _cor22 & "' style='animation-delay:" & _atraso & "ms'/>"
                & "<circle class='vai' style='--dx:" & FORMAT ( _x22 - _x26, "0.0", "en-US" ) & "px;animation-delay:"
                    & ( _atraso + 500 ) & "ms' cx='" & FORMAT ( _x26, "0.0", "en-US" ) & "' cy='" & _sy
                    & "' r='7' fill='" & _cor26 & "'/>"
            & "</svg>"
            & "<div class='dv entra' style='top:" & FORMAT ( _y - 11, "0.0", "en-US" ) & "px;animation-delay:"
                & ( _atraso + 900 ) & "ms'>" & {_pp("_d")} & "</div>"
        & "</div>"
    )""")

desenho("T12 · Corrida · ALT", "Texto alternativo da corrida das unidades.",
        """-- 1 · Leituras
VAR _mudaram = [T12 · mudaram para o adversário]
VAR _subiu = [T12 · onde a margem subiu]
-- 2 · Textos
RETURN
    "Cada linha é uma unidade: o círculo vazado é a margem de Lula em 2022 e o cheio, a de 2026. Mudaram de lado: "
        & IF ( ISBLANK ( _mudaram ), "nenhuma", _mudaram ) & ". Subiu: "
        & IF ( ISBLANK ( _subiu ) || _subiu = "", "nenhuma", _subiu ) & \".\"""")

desenho("T12 · Tooltip UF · HTML",
        "Dossiê da unidade no tooltip da corrida: carimbo, as fatias de Lula e do adversário em 2022 e 2026, a "
        "posição na queda e os municípios que viraram. Só lê contas.",
        f"""-- 1 · Leituras
VAR _nome = [T12 · nome da unidade]
VAR _sigla = [T12 · sigla da unidade]
VAR _reg = [T12 · região da unidade]
VAR _l22 = [T12 · Lula % 2022]
VAR _a22 = [T12 · PL % 2022]
VAR _l26 = [T12 · Lula % 2026]
VAR _a26 = [T12 · PL % 2026]
VAR _m22 = [T12 · margem 2022]
VAR _m26 = [T12 · margem 2026]
VAR _ordem = [T12 · ordem da queda]
VAR _vir = [T12 · municípios que viraram]
VAR _mun = [T12 · municípios]
VAR _val = [T12 · válidos 2026]
-- 2 · Textos
VAR _txtNome = {ESC.format(v="_nome")}
VAR _selo =
    SWITCH (
        TRUE (),
        _m22 > 0 && _m26 < 0, "MUDOU DE LADO",
        _m22 < 0 && _m26 > 0, "MUDOU DE LADO",
        _m26 > 0, "LULA À FRENTE",
        "FLÁVIO À FRENTE"
    )
VAR _clsSelo = IF ( _m26 < 0, "selo az", "selo vm" ) & IF ( ( _m22 > 0 ) = ( _m26 > 0 ), " leve", "" )
VAR _txtOrdem =
    IF (
        ISBLANK ( _ordem ),
        "votos de brasileiros que moram fora: " & FORMAT ( _val, "#,0" ) & " válidos em 2026",
        IF ( _m26 > _m22, "a margem de Lula subiu aqui",
            FORMAT ( _ordem, "0" ) & "ª maior queda entre as 27 unidades" )
    )
VAR _txtMun =
    IF (
        ISBLANK ( _ordem ),
        "",
        "<div class='mun'>"
            & SWITCH (
                TRUE (),
                _mun = 1 && _vir = 0, "O único município não trocou de lado",
                _mun = 1, "O único município trocou Lula por Flávio",
                _vir = 0, "Nenhum dos <b class='num'>" & FORMAT ( _mun, "#,0" ) & "</b> municípios trocou de lado",
                "<b class='num'>" & FORMAT ( _vir, "#,0" ) & "</b> dos " & FORMAT ( _mun, "#,0" )
                    & IF ( _vir = 1, " municípios trocou Lula por Flávio", " municípios trocaram Lula por Flávio" )
            )
        & "</div>"
    )
VAR _mao =
    SWITCH (
        TRUE (),
        _m22 > 0 && _m26 < 0, "virou o estado",
        _m26 > _m22, "foi contra a maré",
        _vir = 0 && NOT ISBLANK ( _ordem ), "nenhuma cidade virou",
        "caiu, sem mudar de lado"
    )
-- 3 · Geometria (barras: 100% = 200 px)
VAR _bl22 = FORMAT ( 200 * _l22, "0.0", "en-US" )
VAR _ba22 = FORMAT ( 200 * _a22, "0.0", "en-US" )
VAR _bl26 = FORMAT ( 200 * _l26, "0.0", "en-US" )
VAR _ba26 = FORMAT ( 200 * _a26, "0.0", "en-US" )
-- 4 · Marcação
RETURN
    "<div class='tela tt12'><div class='fita'></div>"
        & "<div class='" & _clsSelo & "'>" & _selo & "</div>"
        & "<div class='nm sobe'>" & _txtNome & " <span class='uf'>" & _sigla & "</span></div>"
        & "<div class='nota sobe d1'>" & _reg & " · " & _txtOrdem & "</div>"
        & "<div class='duelo entra d2'>"
            & "<div class='ln'><span class='a'>2022</span><span class='tr'><i class='bl barra-x' style='width:" & _bl22
                & "px'></i><i class='ba barra-x-dir' style='width:" & _ba22 & "px'></i></span><span class='p'><b class='lula'>"
                & FORMAT ( _l22, "0.0%" ) & "</b> × <b class='flavio'>" & FORMAT ( _a22, "0.0%" ) & "</b></span></div>"
            & "<div class='ln'><span class='a'>2026</span><span class='tr'><i class='bl barra-x' style='width:" & _bl26
                & "px'></i><i class='ba barra-x-dir' style='width:" & _ba26 & "px'></i></span><span class='p'><b class='lula'>"
                & FORMAT ( _l26, "0.0%" ) & "</b> × <b class='flavio'>" & FORMAT ( _a26, "0.0%" ) & "</b></span></div>"
            & "<div class='nota'>Lula (vermelho) × Jair, em 2022, e Flávio, em 2026 (azul)</div>"
        & "</div>"
        & _txtMun
        & "<div class='mao entra d6'>" & _mao & "</div>"
    & "</div>\"""")

desenho("T12 · Tooltip UF · ALT", "Texto alternativo do dossiê da unidade.",
        """-- 1 · Leituras
VAR _nome = [T12 · nome da unidade]
VAR _l26 = [T12 · Lula % 2026]
VAR _a26 = [T12 · PL % 2026]
VAR _vir = [T12 · municípios que viraram]
-- 2 · Textos
RETURN
    _nome & ": em 2026, Lula " & FORMAT ( _l26, "0.0%" ) & " e Flávio " & FORMAT ( _a26, "0.0%" ) & "; "
        & FORMAT ( _vir, "#,0" ) & " municípios trocaram Lula por Flávio.\"""")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gravar()
    print(f"T12: {len(MEDIDAS)} medidas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
