# -*- coding: utf-8 -*-
"""desenho_t24 — gera as medidas da tela T24 · Quem vota (a 14ª no roteiro): contas e desenho.

    python -X utf8 pbi/scripts/desenho_t24.py

Grava pbi/dax/T24 Quem vota/{Contas,Desenho}/*.dax. A lente vem da segmentação de botões (T24 Lente, padrão Renda); o
degrau, do grão do gráfico e do tooltip (T24 Degrau). Os municípios de um degrau saem de `Social município` (lente e
degrau, pipeline/exportar_pbi.py › social()) e filtram `Município ano` por TREATAS. As pesquisas vêm de
`Perfil pesquisa`.

Oráculo (conferido em 23/10/2026 no pandas, sobre dados/pbi): Renda, degrau 1, 2026: Lula 66,3% × Flávio 29,3%;
Bolsa Família, degrau 5: Lula 66,0% × 29,5%; degrau 1: Flávio 60,7% × Lula 29,9%; IDH, degrau 1: Lula 65,5%.
"""
from __future__ import annotations

from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
DAX = PBI / "dax"
TELA = "T24 Quem vota"
GERADOR = "pbi/scripts/desenho_t24.py"
ORACULO = "pandas sobre dados/pbi/municipio_social.csv × municipio_ano.csv (23/10/2026)"

# geometria do gráfico (visual T24_Grafico_Html, 940 × 684): colunas e escala de % (de 20% a 70%)
X0, PASSO, BANDA = 130, 180, 172
Y_TOPO, Y_BASE, P_MIN, P_MAX = 40, 520, 0.20, 0.70

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


def y(expr: str) -> str:
    """Posição vertical (px) de um % no gráfico."""
    return f"( {Y_BASE} - ( MAX ( {P_MIN}, MIN ( {P_MAX}, {expr} ) ) - {P_MIN} ) * {(Y_BASE - Y_TOPO) / (P_MAX - P_MIN):g} )"


def px(expr: str) -> str:
    return f'FORMAT ( {expr}, "0.0", "en-US" )'


# ==================================================================================================== contas
conta("T24 · lente", "texto", "Lente escolhida nos botões (Renda, Escolaridade, Bolsa Família ou IDH); sem marca, Renda.",
      """SELECTEDVALUE ( 'T24 Lente'[Lente], "Renda" )""")
conta("T24 · degrau", "0", "Degrau no contexto (1 a 5): o grão do gráfico e do tooltip.",
      """SELECTEDVALUE ( 'T24 Degrau'[Degrau] )""")

_MUN = """VAR _l = [T24 · lente]
VAR _d = [T24 · degrau]
VAR _m =
    CALCULATETABLE (
        VALUES ( 'Social município'[CodIBGE] ),
        'Social município'[Lente] = _l,
        'Social município'[Degrau] = _d
    )"""


def _soma(coluna: str, ano: int) -> str:
    return f"""{_MUN}
RETURN
    CALCULATE (
        SUM ( 'Município ano'[{coluna}] ),
        'Município ano'[Ano] = {ano},
        TREATAS ( _m, 'Município'[CodIBGE] )
    )"""


for _a, _adv in ((2022, "Jair"), (2026, "Flávio")):
    conta(f"T24 · votos de Lula {_a}", "#,0", f"Votos de Lula no 1º turno de {_a} nos municípios do degrau (na lente).",
          _soma("VotosPT", _a))
    conta(f"T24 · votos de {_adv} {_a}", "#,0", f"Votos de {_adv} Bolsonaro (PL) no 1º turno de {_a} nos municípios "
          "do degrau.", _soma("VotosAdversario", _a))
    conta(f"T24 · válidos {_a}", "#,0", f"Votos válidos no 1º turno de {_a} nos municípios do degrau.",
          _soma("Validos", _a))
    conta(f"T24 · Lula % {_a}", "0.0%", f"Lula sobre os válidos de {_a} no degrau.",
          f"DIVIDE ( [T24 · votos de Lula {_a}], [T24 · válidos {_a}] )",
          ORACULO + " · Renda, degrau 1, 2026: 66,3%" if _a == 2026 else None)
    conta(f"T24 · {_adv} % {_a}", "0.0%", f"{_adv} Bolsonaro sobre os válidos de {_a} no degrau.",
          f"DIVIDE ( [T24 · votos de {_adv} {_a}], [T24 · válidos {_a}] )",
          ORACULO + " · Renda, degrau 1, 2026: 29,3%" if _a == 2026 else None)
    conta(f"T24 · margem {_a}", "0.0%", f"Margem de Lula em {_a} no degrau: (Lula − {_adv}) ÷ válidos.",
          f"[T24 · Lula % {_a}] - [T24 · {_adv} % {_a}]")
conta("T24 · variação da margem", "+0.0;−0.0;0.0", "Variação da margem de Lula de 2022 para 2026 no degrau, em pontos "
      "(negativa: na direção do adversário).", "( [T24 · margem 2026] - [T24 · margem 2022] ) * 100",
      ORACULO + " · Renda, degrau 1: 46,0 → 37,0 (−9,0)")
conta("T24 · eleitores", "#,0", "Eleitores aptos de 2026 nos municípios do degrau (cada degrau tem cerca de um quinto).",
      _soma("Aptos", 2026))
conta("T24 · municípios", "#,0", "Municípios no degrau, na lente escolhida.", f"""{_MUN}
RETURN
    COUNTROWS ( _m ) + 0""", ORACULO + " · Renda: 2.073, 1.507, 1.168, 671, 151")
for _f, _nome in (("MIN", "mínimo"), ("MAX", "máximo")):
    conta(f"T24 · valor {_nome}", "#,0.000", f"{_nome.capitalize()} do indicador da lente entre os municípios do degrau "
          "(R$ por pessoa; fração do eleitorado; famílias por 100 casas; IDHM).", f"""VAR _l = [T24 · lente]
VAR _d = [T24 · degrau]
RETURN
    CALCULATE (
        {_f} ( 'Social município'[Valor] ),
        'Social município'[Lente] = _l,
        'Social município'[Degrau] = _d
    )""")
for _c in ("Lula", "Flávio"):
    conta(f"T24 · {_c} % 2026 · degrau seguinte", "0.0%", f"{_c} no degrau seguinte (para o traço do gráfico ir de um "
          "degrau ao outro); vazio no 5º.", f"""VAR _d = [T24 · degrau]
RETURN
    IF ( _d < 5, CALCULATE ( [T24 · {_c} % 2026], 'T24 Degrau'[Degrau] = _d + 1 ) )""")
    for _n in (1, 5):
        conta(f"T24 · {_c} % 2026 · degrau {_n}", "0.0%", f"{_c} no {_n}º degrau da lente escolhida (manchete).",
              f"CALCULATE ( [T24 · {_c} % 2026], 'T24 Degrau'[Degrau] = {_n} )")

# pesquisas: o instituto da lente (o primeiro desta ordem que publicou o cruzamento) e o % de cada candidato na faixa
conta("T24 · instituto", "texto", "Instituto da pesquisa mostrada na lente: Datafolha, Quaest, AtlasIntel ou Ipec, o "
      "primeiro que publicou o cruzamento; vazio no IDH (nenhuma pesquisa pergunta).", """VAR _l = [T24 · lente]
VAR _tem =
    CALCULATETABLE ( VALUES ( 'Perfil pesquisa'[Instituto] ), 'Perfil pesquisa'[Lente] = _l )
RETURN
    SWITCH (
        TRUE (),
        "Datafolha" IN _tem, "Datafolha",
        "Quaest" IN _tem, "Quaest",
        "AtlasIntel" IN _tem, "AtlasIntel",
        "Ipec" IN _tem, "Ipec"
    )""")
for _c in ("Lula", "Flávio"):
    conta(f"T24 · pesquisa {_c} %", "0%", f"Intenção de voto em {_c} na faixa (no contexto: a categoria), na pesquisa "
          "da lente, em % do total da faixa.", f"""VAR _l = [T24 · lente]
VAR _i = [T24 · instituto]
RETURN
    DIVIDE (
        CALCULATE (
            MAX ( 'Perfil pesquisa'[Percentual] ),
            'Perfil pesquisa'[Candidato] = "{_c}",
            'Perfil pesquisa'[Lente] = _l,
            'Perfil pesquisa'[Instituto] = _i
        ),
        100
    )""")
for _c in ("Lula", "Flávio"):
    conta(f"T24 · pesquisa {_c} % total", "0%", f"Intenção de voto em {_c} entre todos os eleitores da pesquisa da "
          "lente (a linha de referência do cartão).", f"""VAR _i = [T24 · instituto]
RETURN
    DIVIDE (
        CALCULATE (
            MAX ( 'Perfil pesquisa'[Percentual] ),
            'Perfil pesquisa'[Candidato] = "{_c}",
            'Perfil pesquisa'[Lente] = "Todos",
            'Perfil pesquisa'[Instituto] = _i
        ),
        100
    )""")
for _c, _col in (("Lula", "VotosPT"), ("Flávio", "VotosAdversario")):
    conta(f"T24 · {_c} % 2026 · município", "0.0%", f"{_c} sobre os válidos de 2026 no município do contexto (as pontas "
          "da régua do IDH no cartão).", f"""DIVIDE (
    CALCULATE ( SUM ( 'Município ano'[{_col}] ), 'Município ano'[Ano] = 2026 ),
    CALCULATE ( SUM ( 'Município ano'[Validos] ), 'Município ano'[Ano] = 2026 )
)""")
conta("T24 · pesquisa fatia", "0%", "Fatia do grupo (no contexto: a categoria) na amostra da pesquisa da lente; vazia "
      "quando o instituto não publicou.", """VAR _l = [T24 · lente]
VAR _i = [T24 · instituto]
RETURN
    CALCULATE (
        MAX ( 'Perfil pesquisa'[Fatia] ),
        'Perfil pesquisa'[Lente] = _l,
        'Perfil pesquisa'[Instituto] = _i
    )""")
conta("T24 · pesquisa data", "texto", "Campo e registro da pesquisa da lente (texto da fonte).", """VAR _l = [T24 · lente]
VAR _i = [T24 · instituto]
RETURN
    CALCULATE (
        MAX ( 'Perfil pesquisa'[Campo] ),
        'Perfil pesquisa'[Lente] = _l,
        'Perfil pesquisa'[Instituto] = _i
    )""")

# ==================================================================================================== desenho
# textos de cada lente: o que é o indicador, os dois extremos e o eixo
desenho("T24 · Fundo · HTML", "Manchete da lente (quem lidera em cada ponta, com o %), o que mede o indicador, a grade "
        "de % do gráfico e o eixo de menos a mais.", f"""
-- 1 · Leituras
VAR _l = [T24 · lente]
VAR _l1 = [T24 · Lula % 2026 · degrau 1]
VAR _l5 = [T24 · Lula % 2026 · degrau 5]
VAR _f1 = [T24 · Flávio % 2026 · degrau 1]
VAR _f5 = [T24 · Flávio % 2026 · degrau 5]
-- 2 · Textos
VAR _baixo =
    SWITCH ( _l,
        "Renda", "Nas cidades de renda mais baixa",
        "Escolaridade", "Onde menos eleitores terminaram o ensino médio",
        "Bolsa Família", "Onde menos casas recebem Bolsa Família",
        "Nas cidades de IDH mais baixo" )
VAR _alto =
    SWITCH ( _l,
        "Renda", "Nas cidades de renda mais alta",
        "Escolaridade", "Onde mais eleitores terminaram o ensino médio",
        "Bolsa Família", "Onde mais casas recebem Bolsa Família",
        "Nas cidades de IDH mais alto" )
VAR _lulaEmBaixo = _l1 >= _l5
VAR _pontaLula = IF ( _lulaEmBaixo, _baixo, _alto )
VAR _pontaFlavio = IF ( _lulaEmBaixo, _alto, _baixo )
VAR _pctLula = IF ( _lulaEmBaixo, _l1, _l5 )
VAR _pctFlavio = IF ( _lulaEmBaixo, _f5, _f1 )
VAR _mede =
    SWITCH ( _l,
        "Renda", "Renda: quanto entra por mês, por pessoa, na casa (média da cidade, Censo 2022).",
        "Escolaridade", "Escolaridade: quantos eleitores da cidade têm pelo menos o ensino médio completo (TSE, 2026).",
        "Bolsa Família", "Bolsa Família: famílias pagas em agosto de 2026 para cada 100 casas da cidade (Censo 2022).",
        "IDH: a nota da cidade de 0 a 1 em renda, escola e saúde (IDHM 2010, o último por município)." )
VAR _eixo =
    SWITCH ( _l,
        "Renda", "menos renda", "Escolaridade", "menos escolaridade", "Bolsa Família", "menos Bolsa Família",
        "IDH menor" )
VAR _eixo2 =
    SWITCH ( _l,
        "Renda", "mais renda", "Escolaridade", "mais escolaridade", "Bolsa Família", "mais Bolsa Família",
        "IDH maior" )
-- 3 · Grade (% de 30 a 60; 50% tracejado)
VAR _grade =
    CONCATENATEX (
        GENERATESERIES ( 3, 6, 1 ),
        VAR _p = [Value] / 10
        VAR _y = 106 + {y("_p")}
        RETURN
            "<i class='g" & IF ( [Value] = 5, " meio", "" ) & "' style='top:" & {px("_y")} & "px'></i>"
                & "<span class='gy' style='top:" & {px("_y - 9")} & "px'>" & [Value] * 10 & "%</span>",
        "", [Value], ASC
    )
-- 4 · Marcação
RETURN
    "<div class='tela t24f'>"
        & "<div class='man sobe'>" & _pontaLula & ", <b class='lula'>Lula teve " & FORMAT ( _pctLula * 100, "0" )
        & "%</b>. " & _pontaFlavio & ", <b class='flavio'>Flávio teve " & FORMAT ( _pctFlavio * 100, "0" )
        & "%</b>.</div>"
        & "<div class='mede nota entra d3'>" & _mede & "</div>"
        & _grade
        & "<div class='eixo rot entra d10'><span>← " & _eixo & "</span><span>CADA DEGRAU: UM QUINTO DOS ELEITORES</span>"
        & "<span>" & _eixo2 & " →</span></div>"
    & "</div>"
""")

desenho("T24 · Fundo · ALT", "Texto alternativo da manchete da lente.", """
VAR _l = [T24 · lente]
RETURN
    "Lente " & _l & ": no 1º degrau, Lula " & FORMAT ( [T24 · Lula % 2026 · degrau 1], "0.0%" ) & " e Flávio "
        & FORMAT ( [T24 · Flávio % 2026 · degrau 1], "0.0%" ) & "; no 5º, Lula " & FORMAT ( [T24 · Lula % 2026 · degrau 5], "0.0%" )
        & " e Flávio " & FORMAT ( [T24 · Flávio % 2026 · degrau 5], "0.0%" ) & "."
""")

desenho("T24 · Gráfico · HTML", "Um degrau por entrada (granularidade T24 Degrau): a coluna que pega o mouse, os pontos "
        "de Lula e Flávio com o %, o traço a caneta até o degrau seguinte, a nota onde a vantagem troca de lado e a "
        "faixa do indicador embaixo.", f"""
-- 1 · Leituras
VAR _d = [T24 · degrau]
VAR _l = [T24 · lente]
VAR _lu = [T24 · Lula % 2026]
VAR _fl = [T24 · Flávio % 2026]
VAR _lu2 = [T24 · Lula % 2026 · degrau seguinte]
VAR _fl2 = [T24 · Flávio % 2026 · degrau seguinte]
VAR _vmin = [T24 · valor mínimo]
VAR _vmax = [T24 · valor máximo]
-- 2 · Textos (a faixa do indicador no degrau)
VAR _fmt =
    SWITCH ( _l, "Renda", "#,0", "Escolaridade", "0", "Bolsa Família", "0", "0.000" )
VAR _k = IF ( _l = "Escolaridade", 100, 1 )
VAR _a = FORMAT ( _vmin * _k, _fmt )
VAR _b = FORMAT ( _vmax * _k, _fmt )
-- nas pontas, só o limite de dentro: o extremo de fora é uma cidade só (há cidade com mais famílias que casas)
VAR _pre = SWITCH ( _l, "Renda", "R$ ", "IDH", "IDHM ", "" )
VAR _pos = SWITCH ( _l, "Escolaridade", "%", "Bolsa Família", " por 100 casas", "" )
VAR _faixa =
    SWITCH ( _d,
        1, "até " & _pre & _b & _pos,
        5, "mais de " & _pre & _a & _pos,
        _pre & _a & IF ( _l = "Escolaridade", "%", "" ) & " a " & _b & _pos )
-- 3 · Geometria
VAR _x = {X0} + ( _d - 1 ) * {PASSO}
VAR _yl = {y("_lu")}
VAR _yf = {y("_fl")}
VAR _temSeg = NOT ISBLANK ( _lu2 )
VAR _x2 = _x + {PASSO}
VAR _yl2 = {y("_lu2")}
VAR _yf2 = {y("_fl2")}
VAR _luCima = _lu >= _fl
VAR _a1 = _lu - _fl
VAR _a2 = _lu2 - _fl2
VAR _cruza = _temSeg && ( ( _a1 > 0 && _a2 < 0 ) || ( _a1 < 0 && _a2 > 0 ) )
VAR _t = DIVIDE ( _a1, _a1 - _a2 )
VAR _xc = _x + _t * {PASSO}
VAR _yc = _yl + _t * ( _yl2 - _yl )
VAR _atraso = 300 + _d * 260
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _d ) && NOT ISBLANK ( _lu ),
        "<div class='tela t24g'>"
            & "<div class='banda entra' style='left:" & ( _x - {BANDA // 2} ) & "px;animation-delay:" & ( _d * 80 )
            & "ms'></div>"
            & "<svg class='sv' width='940' height='684' viewBox='0 0 940 684'>"
            & IF (
                _temSeg,
                "<line class='traco ll' pathLength='1' filter='url(#rb24)' style='animation-delay:" & _atraso
                    & "ms' x1='" & _x & "' y1='" & {px("_yl")} & "' x2='" & _x2 & "' y2='" & {px("_yl2")} & "'/>"
                    & "<line class='traco lf' pathLength='1' filter='url(#rb24)' style='animation-delay:" & _atraso
                    & "ms' x1='" & _x & "' y1='" & {px("_yf")} & "' x2='" & _x2 & "' y2='" & {px("_yf2")} & "'/>"
            )
            & "<circle class='brota pl' style='animation-delay:" & ( _atraso - 150 ) & "ms' cx='" & _x & "' cy='"
            & {px("_yl")} & "' r='8'/>"
            & "<circle class='brota pf' style='animation-delay:" & ( _atraso - 150 ) & "ms' cx='" & _x & "' cy='"
            & {px("_yf")} & "' r='8'/>"
            & IF (
                _cruza,
                "<ellipse class='traco cz' pathLength='1' filter='url(#rb24)' style='animation-delay:"
                    & ( _atraso + 700 ) & "ms' cx='" & {px("_xc")} & "' cy='" & {px("_yc")} & "' rx='18' ry='14'/>"
            )
            & "</svg>"
            & "<span class='vl lula-esc sobe' style='left:" & ( _x - 50 ) & "px;top:"
            & {px("IF ( _luCima, _yl - 44, _yl + 14 )")} & "px;animation-delay:" & ( _atraso + 100 ) & "ms'>"
            & FORMAT ( _lu * 100, "0.0" ) & "%</span>"
            & "<span class='vl flavio-esc sobe' style='left:" & ( _x - 50 ) & "px;top:"
            & {px("IF ( _luCima, _yf + 14, _yf - 44 )")} & "px;animation-delay:" & ( _atraso + 100 ) & "ms'>"
            & FORMAT ( _fl * 100, "0.0" ) & "%</span>"
            & IF (
                _cruza,
                "<span class='cruz mao entra' style='left:" & ( IF ( _t < 0.5, _x, _x2 ) - {BANDA // 2} )
                    & "px;animation-delay:" & ( _atraso + 900 ) & "ms'>aqui troca de lado</span>"
            )
            & "<div class='pe' style='left:" & ( _x - {BANDA // 2} ) & "px'><b>" & _d & "º QUINTO</b><span>" & _faixa
            & "</span></div>"
        & "</div>"
    )
""")

desenho("T24 · Gráfico · ALT", "Texto alternativo do gráfico dos degraus.", """
"Gráfico da lente " & [T24 · lente] & ": cinco degraus de eleitores, de menos a mais; Lula começa com "
    & FORMAT ( [T24 · Lula % 2026 · degrau 1], "0.0%" ) & " e termina com " & FORMAT ( [T24 · Lula % 2026 · degrau 5], "0.0%" )
    & "; Flávio vai de " & FORMAT ( [T24 · Flávio % 2026 · degrau 1], "0.0%" ) & " a "
    & FORMAT ( [T24 · Flávio % 2026 · degrau 5], "0.0%" ) & ". Passe o mouse num degrau para ver 2022 e as cidades."
""")

desenho("T24 · Lentes · HTML", "As quatro abas das lentes, com a escolhida marcada (os botões nativos ficam por cima, "
        "invisíveis).", """
VAR _l = [T24 · lente]
RETURN
    "<div class='tela t24l'>"
        & CONCATENATEX (
            ALL ( 'T24 Lente' ),
            "<div class='ab" & IF ( 'T24 Lente'[Lente] = _l, " on", "" ) & " entra d" & 'T24 Lente'[Ordem] & "'>"
                & 'T24 Lente'[Lente] & "</div>",
            "", 'T24 Lente'[Ordem], ASC
        )
    & "</div>"
""")
desenho("T24 · Lentes · ALT", "Texto alternativo das abas.", """
"Lentes: Renda, Escolaridade, Bolsa Família e IDH; marcada: " & [T24 · lente] & "."
""")

desenho("T24 · Pesquisa · HTML", "Cartão das pessoas: em cada faixa da lente, a vantagem na pesquisa (barra que sai do "
        "centro: à direita, Lula à frente; à esquerda, Flávio), os dois % e o tamanho do grupo; a marca tracejada é a "
        "vantagem entre todos os eleitores, e a nota marca a faixa em que a vantagem troca de lado. No IDH, por que não "
        "há pesquisa e as pontas da régua. A nota do voto secreto é fixa (corpo do visual).", """
-- 1 · Leituras
VAR _l = [T24 · lente]
VAR _i = [T24 · instituto]
VAR _campo = [T24 · pesquisa data]
VAR _lt = [T24 · pesquisa Lula % total]
VAR _ft = [T24 · pesquisa Flávio % total]
VAR _cats =
    CALCULATETABLE (
        SUMMARIZE ( 'Perfil pesquisa', 'Perfil pesquisa'[Categoria], 'Perfil pesquisa'[CategoriaOrdem] ),
        'Perfil pesquisa'[Lente] = _l,
        'Perfil pesquisa'[Instituto] = _i
    )
VAR _t =
    ADDCOLUMNS (
        _cats,
        "@l", [T24 · pesquisa Lula %],
        "@f", [T24 · pesquisa Flávio %],
        "@s", [T24 · pesquisa fatia]
    )
VAR _t2 =
    ADDCOLUMNS (
        _t,
        "@v", ( [@l] - [@f] ) * 100,
        "@vAnt",
            VAR _o = 'Perfil pesquisa'[CategoriaOrdem]
            RETURN MAXX ( FILTER ( _t, 'Perfil pesquisa'[CategoriaOrdem] = _o - 1 ), ( [@l] - [@f] ) * 100 )
    )
-- 2 · Geometria: o centro da régua em 195 px da coluna do gráfico; 40 pontos de vantagem = 160 px
VAR _ref = ( _lt - _ft ) * 100
VAR _xRef = 195 + MAX ( -40, MIN ( 40, _ref ) ) / 40 * 160
VAR _linhas =
    CONCATENATEX (
        _t2,
        VAR _v = [@v]
        VAR _w = MIN ( ABS ( _v ), 40 ) / 40 * 160
        VAR _x = IF ( _v >= 0, 195, 195 - _w )
        VAR _troca = NOT ISBLANK ( [@vAnt] ) && SIGN ( [@vAnt] ) <> SIGN ( _v ) && _v <> 0
        RETURN
            "<div class='lin sobe d" & ( 'Perfil pesquisa'[CategoriaOrdem] + 3 ) & "'><div class='cat'><b>"
                & 'Perfil pesquisa'[Categoria] & "</b>"
                & IF ( NOT ISBLANK ( [@s] ), "<i>" & FORMAT ( [@s], "0%" ) & " dos entrevistados</i>" )
                & "</div><div class='gr'><i class='ref' style='left:" & FORMAT ( _xRef, "0.0", "en-US" ) & "px'></i>"
                & "<i class='ct'></i><i class='vb " & IF ( _v >= 0, "bl", "bf" ) & " " & IF ( _v >= 0, "barra-x", "barra-x-dir" )
                & "' style='left:" & FORMAT ( _x, "0.0", "en-US" ) & "px;width:" & FORMAT ( _w, "0.0", "en-US" ) & "px'></i>"
                & "<span class='vt " & IF ( _v >= 0, "lula-esc", "flavio-esc" ) & "' style='"
                & IF ( _v >= 0, "left:" & FORMAT ( 195 + _w + 8, "0.0", "en-US" ) & "px",
                    "right:" & FORMAT ( 390 - ( 195 - _w ) + 8, "0.0", "en-US" ) & "px" ) & "'>"
                & IF ( _v >= 0, "Lula +", "Flávio +" ) & FORMAT ( ABS ( _v ), "0" ) & "</span>"
                & "<span class='pp'><span class='lula-esc'>" & FORMAT ( [@l] * 100, "0" ) & "%</span> × "
                & "<span class='flavio-esc'>" & FORMAT ( [@f] * 100, "0" ) & "%</span></span>"
                & IF ( _troca, "<span class='tr mao'>troca de lado</span>" )
                & "</div></div>",
        "", 'Perfil pesquisa'[CategoriaOrdem], ASC
    )
VAR _total =
    "<div class='lin tot sobe d9'><div class='cat'><b>todos os eleitores</b><i>a marca tracejada</i></div>"
        & "<div class='gr'><i class='ct'></i><i class='vb " & IF ( _ref >= 0, "bl", "bf" ) & "' style='left:"
        & FORMAT ( IF ( _ref >= 0, 195, 195 - MIN ( ABS ( _ref ), 40 ) / 40 * 160 ), "0.0", "en-US" ) & "px;width:"
        & FORMAT ( MIN ( ABS ( _ref ), 40 ) / 40 * 160, "0.0", "en-US" ) & "px'></i>"
        & "<span class='vt " & IF ( _ref >= 0, "lula-esc", "flavio-esc" ) & "' style='left:"
        & FORMAT ( 195 + IF ( _ref >= 0, MIN ( ABS ( _ref ), 40 ) / 40 * 160, 0 ) + 8, "0.0", "en-US" ) & "px'>"
        & IF ( _ref >= 0, "Lula +", "Flávio +" ) & FORMAT ( ABS ( _ref ), "0" ) & "</span>"
        & "<span class='pp'><span class='lula-esc'>" & FORMAT ( _lt * 100, "0" ) & "%</span> × <span class='flavio-esc'>"
        & FORMAT ( _ft * 100, "0" ) & "%</span></span></div></div>"
VAR _pergunta =
    SWITCH ( _l,
        "Renda", "por renda da família",
        "Escolaridade", "por escolaridade",
        "Bolsa Família", "entre quem recebe e quem não recebe Bolsa Família",
        "" )
VAR _notaBF =
    IF ( _l = "Bolsa Família",
        "<div class='nota nbf entra d10'>Recebe = recebe Bolsa Família ou mora com quem recebe. O Datafolha não publicou "
            & "o tamanho de cada grupo nesta pergunta.</div>" )
-- 3 · As pontas da régua do IDH (a cidade de IDH mais baixo e a de mais alto, com o voto de 2026)
VAR _idh =
    CALCULATETABLE (
        SUMMARIZE ( 'Social município', 'Social município'[CodIBGE], 'Social município'[Valor] ),
        'Social município'[Lente] = "IDH"
    )
VAR _cBaixo = MINX ( TOPN ( 1, _idh, 'Social município'[Valor], ASC ), 'Social município'[CodIBGE] )
VAR _cAlto = MINX ( TOPN ( 1, _idh, 'Social município'[Valor], DESC ), 'Social município'[CodIBGE] )
VAR _ponta =
    CONCATENATEX (
        { ( 1, _cBaixo, "O MAIS BAIXO" ), ( 2, _cAlto, "O MAIS ALTO" ) },
        VAR _cod = [Value2]
        VAR _nome = LOOKUPVALUE ( 'Município'[Rótulo], 'Município'[CodIBGE], _cod )
        VAR _v = MAXX ( FILTER ( _idh, 'Social município'[CodIBGE] = _cod ), 'Social município'[Valor] )
        VAR _lu = CALCULATE ( [T24 · Lula % 2026 · município], TREATAS ( { _cod }, 'Município'[CodIBGE] ) )
        VAR _fl = CALCULATE ( [T24 · Flávio % 2026 · município], TREATAS ( { _cod }, 'Município'[CodIBGE] ) )
        RETURN
            "<div class='pt sobe d" & ( [Value1] + 4 ) & "'><span class='rot'>" & [Value3] & " · IDHM "
                & FORMAT ( _v, "0.000" ) & "</span><b>" & _nome & "</b><span><span class='lula-esc'>Lula "
                & FORMAT ( _lu * 100, "0" ) & "%</span> × <span class='flavio-esc'>Flávio " & FORMAT ( _fl * 100, "0" )
                & "%</span></span></div>",
        "", [Value1], ASC
    )
-- 4 · Marcação
VAR _cartao =
    IF (
        ISBLANK ( _i ),
        "<div class='rot entra'>NAS PESQUISAS, AS PESSOAS</div>"
            & "<div class='tit sobe d1'>O IDH não se pergunta</div>"
            & "<div class='txt sobe d2'>É uma nota do lugar, não da pessoa: junta renda, escola e saúde da cidade. "
            & "Por isso, nesta lente, só aparecem os lugares.</div>"
            & "<div class='txt sobe d3'>O último IDH por município é de 2010. As 7 cidades criadas depois ficam de fora.</div>"
            & "<div class='rot regua entra d4'>A RÉGUA, NAS PONTAS</div>" & _ponta,
        "<div class='rot entra'>NAS PESQUISAS, AS PESSOAS</div>"
            & "<div class='tit sobe d1'>O que os eleitores disseram ao " & _i & "</div>"
            & "<div class='nota sobe d2'>intenção de voto no 1º turno " & _pergunta & " · " & _campo & "</div>"
            & "<div class='eixo entra d3'><span class='flavio-esc'>← Flávio à frente</span>"
            & "<span class='lula-esc'>Lula à frente →</span></div>"
            & "<div class='lista realce'>" & _linhas & _total & "</div>" & _notaBF
    )
RETURN
    "<div class='tela t24p'><div class='cartao'>" & _cartao & "</div></div>"
""")

desenho("T24 · Pesquisa · ALT", "Texto alternativo do cartão das pesquisas.", """
VAR _i = [T24 · instituto]
RETURN
    IF (
        ISBLANK ( _i ),
        "Nesta lente não há pesquisa: o IDH é uma nota do lugar. O voto é secreto; o gráfico mostra os lugares.",
        "Pesquisa " & _i & " na lente " & [T24 · lente] & ": intenção de voto de Lula e Flávio em cada faixa. O voto é "
            & "secreto; o gráfico mostra os lugares."
    )
""")

desenho("T24 · Tooltip degrau · HTML", "Dossiê do degrau (página de tooltip ttT24Degrau): municípios e eleitores, a "
        "faixa do indicador, Lula e o adversário em 2022 e 2026, a variação da margem e as maiores cidades.", """
-- 1 · Leituras
VAR _d = [T24 · degrau]
VAR _l = [T24 · lente]
VAR _mun = [T24 · municípios]
VAR _ele = [T24 · eleitores]
VAR _l22 = [T24 · Lula % 2022]
VAR _j22 = [T24 · Jair % 2022]
VAR _l26 = [T24 · Lula % 2026]
VAR _f26 = [T24 · Flávio % 2026]
VAR _var = [T24 · variação da margem]
VAR _codigos =
    CALCULATETABLE (
        VALUES ( 'Social município'[CodIBGE] ),
        'Social município'[Lente] = _l,
        'Social município'[Degrau] = _d
    )
VAR _cidades =
    CALCULATETABLE (
        TOPN ( 3, VALUES ( 'Município'[Rótulo] ), CALCULATE ( SUM ( 'Município'[População] ) ), DESC ),
        TREATAS ( _codigos, 'Município'[CodIBGE] )
    )
-- 2 · Textos
VAR _txtCid = CONCATENATEX ( _cidades, 'Município'[Rótulo], ", ", CALCULATE ( SUM ( 'Município'[População] ) ), DESC )
VAR _ponta =
    SWITCH ( _d, 1, " · o de menos ", 5, " · o de mais ", " · " )
    & SWITCH ( _l, "Renda", "renda", "Escolaridade", "escolaridade", "Bolsa Família", "Bolsa Família", "IDH" )
VAR _ponta2 = IF ( _d = 1 || _d = 5, _ponta, "" )
VAR _frase =
    IF ( _var < 0,
        "A margem de Lula aqui caiu " & FORMAT ( ABS ( _var ), "0.0" ) & IF ( ROUND ( ABS ( _var ), 1 ) = 1, " ponto", " pontos" )
            & " desde 2022.",
        "A margem de Lula aqui subiu " & FORMAT ( _var, "0.0" ) & IF ( ROUND ( _var, 1 ) = 1, " ponto", " pontos" )
            & " desde 2022." )
-- 3 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _d ),
        "<div class='tela tt24'><div class='fita'></div>"
            & "<div class='rot'>" & _d & "º QUINTO DOS ELEITORES" & UPPER ( _ponta2 ) & "</div>"
            & "<div class='num-l'><b>" & FORMAT ( _mun, "#,0" ) & "</b> " & IF ( _mun = 1, "município", "municípios" )
            & " · <b>" & FORMAT ( _ele / 1e6, "0.0" ) & " mi</b> de eleitores</div>"
            & "<div class='duas'><div><span class='rot'>2022</span><span class='lula-esc'>Lula " & FORMAT ( _l22 * 100, "0.0" )
            & "%</span><span class='flavio-esc'>Jair " & FORMAT ( _j22 * 100, "0.0" ) & "%</span></div>"
            & "<div><span class='rot'>2026</span><span class='lula-esc'>Lula " & FORMAT ( _l26 * 100, "0.0" )
            & "%</span><span class='flavio-esc'>Flávio " & FORMAT ( _f26 * 100, "0.0" ) & "%</span></div></div>"
            & "<div class='txt'>" & _frase & "</div>"
            & "<div class='cid'><span class='rot'>MAIORES CIDADES</span>" & _txtCid & "</div>"
        & "</div>"
    )
""")
desenho("T24 · Tooltip degrau · ALT", "Texto alternativo do dossiê do degrau.", """
"Degrau " & [T24 · degrau] & " da lente " & [T24 · lente] & ": " & FORMAT ( [T24 · municípios], "#,0" ) & " municípios; Lula "
    & FORMAT ( [T24 · Lula % 2022], "0.0%" ) & " em 2022 e " & FORMAT ( [T24 · Lula % 2026], "0.0%" ) & " em 2026."
""")


def main() -> int:
    gravar()
    print(f"{len(MEDIDAS)} medidas em pbi/dax/{TELA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
