# -*- coding: utf-8 -*-
"""desenho_t06 — tela 06 · Ausência: quantos brasileiros não escolheram ninguém? Dono: agente das telas 01–06.

    python -I -X utf8 pbi/scripts/desenho_t06.py        # grava pbi/dax/T06 Ausência/… e pbi/spec/t06_mapa.json

Protagonista: os 33,5 milhões que não foram votar e a régua que mostra quantas vezes a diferença entre Flávio e Lula
cabe neles (15). Apoios: a abstenção subindo em duas décadas (2006 → 2026), quem falta mais (por idade, 2014 → 2026)
e onde (mapa de pontos por município, Deneb, que se desenha em onda). Tons neutros: creme → tinta (sem vermelho/azul).

Fontes: sem filtro, o comparecimento oficial do Brasil ('Comparecimento ano', sem o exterior); com o filtro de UF, a
soma dos municípios da UF ('Município ano'). O perfil por idade ('Abstenção perfil') só existe para o Brasil.
Oráculo: mockup/data/eleicoes.json › paginas[6].
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from desenho_t01_t06_comum import URL_MIDIA, Gravador, dax  # noqa: E402
from desenho_t03_t05 import gravar_spec, spec_mapa  # noqa: E402

P = "T06"
G = Gravador("T06 Ausência")
CA = "'Comparecimento ano'"
MA = "'Município ano'"
MU = "'Município'"
AP = "'Abstenção perfil'"
CU = "'Candidato UF'"
FAIXAS = [
    ("16 e 17 anos", ["16 anos", "17 anos"]),
    ("18 a 24", ["18 anos", "19 anos", "20 anos", "21 a 24 anos"]),
    ("25 a 34", ["25 a 29 anos", "30 a 34 anos"]),
    ("35 a 44", ["35 a 39 anos", "40 a 44 anos"]),
    ("45 a 59", ["45 a 49 anos", "50 a 54 anos", "55 a 59 anos"]),
    ("60 a 69", ["60 a 64 anos", "65 a 69 anos"]),
    ("70 ou mais", ["70 a 74 anos", "75 a 79 anos", "80 a 84 anos", "85 a 89 anos", "90 a 94 anos", "95 a 99 anos",
                    "100 anos ou mais"]),
]
RESPOSTA = (150, 140, 780, 470)
SERIE = (150, 640, 780, 360)
MAPA = (990, 140, 780, 540)
LEGENDA = (990, 684, 780, 44)
IDADE = (990, 744, 780, 256)
TT_W, TT_H = 420, 270


def contas() -> None:
    c = G.conta
    c("T06 · com UF", "1 quando o filtro de UF da casca está ativo (a tela mostra a UF), 0 no Brasil.",
      "INT ( ISCROSSFILTERED ( 'UF' ) )", "0")
    c("T06 · recorte", "Nome do recorte: Brasil ou o nome da UF escolhida no filtro.",
      'IF ( [T06 · com UF] = 1, SELECTEDVALUE ( \'UF\'[Nome], "UFs escolhidas" ), "Brasil" )', "texto")
    # no ano do contexto (série) e em 2026
    for nome, col, desc in (("aptos", "Aptos", "Eleitores aptos"), ("abstenções", "Abstencoes", "Eleitores que faltaram"),
                            ("brancos", "Brancos", "Votos em branco"), ("nulos", "Nulos", "Votos nulos")):
        c(f"T06 · {nome} (ano)", f"{desc} no ano do contexto: Brasil oficial ('Comparecimento ano') sem filtro; soma "
          "dos municípios com o filtro de UF.", dax(f"""
            IF ( [T06 · com UF] = 1, SUM ( {MA}[{col}] ), SUM ( {CA}[{col}] ) )
            """), "#,0")
        c(f"T06 · {nome}", f"{desc} no 1º turno de 2026, no recorte.",
          f"CALCULATE ( [T06 · {nome} (ano)], 'Ano'[Ano] = 2026 )", "#,0",
          {"aptos": "paginas[6].serie[2026].aptos_txt = 158,7 mi",
           "abstenções": "paginas[6].serie[2026].abstencoes = 33.469.244"}.get(nome))
    c("T06 · abstenção % (ano)", "Parcela dos aptos que faltaram no ano do contexto (0–1).",
      "DIVIDE ( [T06 · abstenções (ano)], [T06 · aptos (ano)] )", "0.0%", "paginas[6].serie[].abstencao_pct")
    c("T06 · abstenção %", "Parcela dos aptos que faltaram em 2026, no recorte (0–1).",
      "DIVIDE ( [T06 · abstenções], [T06 · aptos] )", "0.0%", "paginas[6].abstencao_2026_txt = 21,1%")
    c("T06 · abstenção % 2006", "Parcela dos aptos que faltaram em 2006, no recorte (0–1).",
      "CALCULATE ( [T06 · abstenção % (ano)], 'Ano'[Ano] = 2006 )", "0.0%", "paginas[6].abstencao_2006_txt = 16,8%")
    c("T06 · variação da abstenção em p.p.", "Variação da abstenção de 2006 para 2026, em pontos percentuais.",
      "( [T06 · abstenção %] - [T06 · abstenção % 2006] ) * 100", "0.0", "+4,3")
    c("T06 · não escolheram", "Abstenções + brancos + nulos em 2026, no recorte: quem não escolheu nenhum candidato.",
      "[T06 · abstenções] + [T06 · brancos] + [T06 · nulos]", "#,0", "paginas[6].nao_escolheram_2026_txt = 39,4 mi")
    c("T06 · não escolheram %", "Parcela dos aptos que não escolheu ninguém em 2026 (0–1).",
      "DIVIDE ( [T06 · não escolheram], [T06 · aptos] )", "0.0%", "paginas[6].nao_escolheram_2026_pct_txt = 24,8%")
    c("T06 · diferença Flávio Lula", "Diferença de votos entre Flávio e Lula no 1º turno de 2026, no recorte, sem sinal.",
      dax(f"""
        ABS (
            CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026, {CU}[Número] = 22 )
                - CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026, {CU}[Número] = 13 )
        )
        """), "#,0", "paginas[1].diferenca.votos = 2.224.965")
    c("T06 · vencedor", "Quem teve mais votos no recorte em 2026: Flávio ou Lula.", dax(f"""
        IF (
            CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026, {CU}[Número] = 13 )
                > CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026, {CU}[Número] = 22 ),
            "Lula",
            "Flávio"
        )
        """), "texto")
    c("T06 · vezes a diferença", "Quantas vezes a diferença entre Flávio e Lula cabe nas abstenções de 2026, no recorte.",
      "DIVIDE ( [T06 · abstenções], [T06 · diferença Flávio Lula] )", "0.0", "paginas[6].vezes_a_diferenca = 15")
    # perfil por idade (Brasil; o TSE publica desde 2014)
    for faixa, cats in FAIXAS:
        lista = ", ".join(f'"{x}"' for x in cats)
        for ano in (2014, 2026):
            c(f"T06 · idade {faixa} · {ano}", f"Abstenção da faixa {faixa} no 1º turno de {ano}, no Brasil (0–1): "
              "faltosos ÷ aptos da faixa.", dax(f"""
                CALCULATE (
                    DIVIDE ( SUM ( {AP}[Abstencao] ), SUM ( {AP}[Aptos] ) ),
                    {AP}[Ano] = {ano},
                    {AP}[Dimensão] = "faixa_etaria",
                    {AP}[Categoria] IN {{ {lista} }}
                )
                """), "0.0%", f"paginas[6].idade[{faixa}].pct{ano}")
    # município (mapa e dossiê)
    c("T06 · abstenções (município)", "Eleitores que faltaram em 2026 nos municípios do contexto (sem o exterior).",
      f"CALCULATE ( SUM ( {MA}[Abstencoes] ), {MA}[Ano] = 2026 )", "#,0")
    c("T06 · aptos (município)", "Eleitores aptos em 2026 nos municípios do contexto.",
      f"CALCULATE ( SUM ( {MA}[Aptos] ), {MA}[Ano] = 2026 )", "#,0")
    c("T06 · abstenção % (município)", "Abstenção de 2026 nos municípios do contexto (0–1). Cor do ponto no mapa.",
      "DIVIDE ( [T06 · abstenções (município)], [T06 · aptos (município)] )", "0.0%")
    c("T06 · abstenção % 2006 (município)", "Abstenção de 2006 nos municípios do contexto (0–1).",
      f"CALCULATE ( DIVIDE ( SUM ( {MA}[Abstencoes] ), SUM ( {MA}[Aptos] ) ), {MA}[Ano] = 2006 )", "0.0%")
    c("T06 · um em cada (município)", "De quantos em quantos eleitores um faltou em 2026 no município (arredondado).",
      "ROUND ( DIVIDE ( [T06 · aptos (município)], [T06 · abstenções (município)] ), 0 )", "0")
    c("T06 · abstenção % Brasil", "Abstenção oficial do Brasil em 2026 (referência no dossiê do município).",
      f"CALCULATE ( DIVIDE ( SUM ( {CA}[Abstencoes] ), SUM ( {CA}[Aptos] ) ), {CA}[Ano] = 2026 )", "0.0%", "21,1%")
    c("T06 · município", "Nome (UF) do município da linha.", f"SELECTEDVALUE ( {MU}[Rótulo] )", "texto")
    c("T06 · região do município", "Região do município da linha.", f"SELECTEDVALUE ( {MU}[Região] )", "texto")


def desenho() -> None:
    G.desenho("T06 · Resposta · HTML", "Bloco da resposta da tela 06: quantos não foram votar, a régua de quantas vezes "
              "a diferença entre os dois primeiros cabe nesse número e quem não escolheu ninguém. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _comUF = [T06 · com UF]
        VAR _recorte = [T06 · recorte]
        VAR _abst = [T06 · abstenções]
        VAR _pct = [T06 · abstenção %]
        VAR _aptos = [T06 · aptos]
        VAR _dif = [T06 · diferença Flávio Lula]
        VAR _vezes = [T06 · vezes a diferença]
        VAR _venc = [T06 · vencedor]
        VAR _nao = [T06 · não escolheram]
        VAR _naoP = [T06 · não escolheram %]
        -- 2 · Textos
        VAR _txtAbst = @MI1(_abst)@
        VAR _txtAptos = @MI1(_aptos)@
        VAR _txtDif = @MI(_dif)@
        VAR _par = IF ( _venc = "Lula", "Lula e Flávio", "Flávio e Lula" )
        VAR _n = INT ( _vezes )
        VAR _txtVezes = IF ( _vezes >= 10, FORMAT ( _n, "0" ), FORMAT ( _vezes, "0.0" ) )
        VAR _manchete =
            IF (
                _vezes >= 1,
                "É " & _txtVezes & " vezes a diferença entre " & _par,
                "A diferença entre " & _par & " foi maior que o número de quem faltou"
            )
        VAR _txtNota = IF ( _vezes >= 1, "cabe " & _txtVezes & " vezes", "não cabe nem uma vez" )
        VAR _rodape =
            "Somando brancos e nulos, " & @MI1(_nao)@ & " (" & @PCT(_naoP)@ & " dos aptos) não escolheram ninguém."
        -- 3 · Geometria (régua de 760 px = quem faltou; a diferença é um pedaço dela)
        VAR _wDif = IF ( _vezes >= 1, MAX ( 3, DIVIDE ( 760, _vezes ) ), 760 ) -- geometria
        VAR _wAbst = IF ( _vezes >= 1, 760, MAX ( 3, 760 * _vezes ) ) -- geometria
        VAR _passo = SWITCH ( TRUE (), _n <= 40, 1, _n <= 200, 5, _n <= 1000, 25, 100 ) -- geometria
        VAR _cortes = GENERATESERIES ( _passo, MAX ( _n, _passo ), _passo ) /* lista */
        VAR _marcas =
            CONCATENATEX (
                FILTER ( _cortes, [Value] * _wDif < 758 && _vezes >= 1 ), /* lista */
                VAR _x = @CSS([Value] * _wDif)@ -- geometria
                RETURN
                    "<line x1='" & _x & "' y1='4' x2='" & _x & "' y2='40'/>",
                "",
                [Value], ASC
            )
        VAR _txtW = @CSS(_wDif)@ -- geometria
        VAR _txtWA = @CSS(_wAbst)@ -- geometria
        VAR _clsNota = IF ( _vezes >= 1, "mao nota1", "mao nota1 baixa" )
        -- 4 · Marcação
        VAR _html =
            "<div class='tela rp'>"
                & "<div class='sob sobe'>Quem não foi votar · " & @ESC(_recorte)@ & "</div>"
                & "<div class='topo'><div class='big sobe d1'>" & _txtAbst & "</div>"
                & "<div class='lado sobe d2'><div class='nfv'>não foram votar</div>" & [T06 · sublinhado · SVG]
                & "<div class='txt'>" & @PCT(_pct)@ & " dos " & _txtAptos & " de eleitores aptos em 2026</div></div></div>"
                & "<div class='man mc sobe d3'>" & _manchete & "</div>"
                & "<div class='regua'>"
                & "<div class='rot rt1 sobe d4'>Quem faltou · " & _txtAbst & "</div>"
                & "<svg class='r1' width='760' height='44' viewBox='0 0 760 44'><rect class='cheia barra-x d5' x='0' y='4' width='" & _txtWA & "' height='36'/>"
                & "<g class='cortes entra d9'>" & _marcas & "</g></svg>"
                & "<div class='dif' style='width:" & _txtW & "px'><div class='barra-x d8'></div></div>"
                & "<div class='rot rt2 sobe d8'>A diferença entre " & _par & " · " & _txtDif & "</div>"
                & "<div class='" & _clsNota & " entra d12'>" & _txtNota & "</div>"
                & "</div>"
                & "<div class='txt pe sobe d10'>" & _rodape & "</div>"
            & "</div>"
        RETURN
            _html
        """))
    G.desenho("T06 · sublinhado · SVG", "Sublinhado à mão sob 'não foram votar' (traço que se desenha). Desenho fixo.",
              '"' + ("<svg class='subl' viewBox='0 0 300 16' preserveAspectRatio='none' aria-hidden='true'>"
                     "<path pathLength='1' class='traco' style='animation-delay:1.1s' d='M3,10 C60,4 140,13 205,7 "
                     "C240,4 270,6 297,9' fill='none' stroke='#1C1915' stroke-width='3' stroke-linecap='round'/>"
                     "</svg>").replace('"', '""') + '"')
    G.desenho("T06 · Resposta · ALT", "Texto para leitor de tela do bloco da resposta.", dax("""
        LEFT (
            [T06 · recorte] & ": " & @MI([T06 · abstenções])@ & " não foram votar em 2026 (" & @PCT([T06 · abstenção %])@
                & " dos aptos), " & FORMAT ( [T06 · vezes a diferença], "0.0" ) & " vezes a diferença entre Flávio e "
                & "Lula. Com brancos e nulos, " & @MI([T06 · não escolheram])@ & " não escolheram ninguém.",
            250
        )
        """))
    # série 2006–2026
    G.desenho("T06 · Série · HTML", "A abstenção em cada 1º turno de 2006 a 2026, no recorte: uma linha que se desenha "
              "com o % em cada eleição. Só lê contas; a escala é geometria.", dax("""
        -- 1 · Leituras
        VAR _p06 = [T06 · abstenção % 2006]
        VAR _p26 = [T06 · abstenção %]
        VAR _dpp = [T06 · variação da abstenção em p.p.]
        VAR _anos =
            ADDCOLUMNS ( VALUES ( 'Ano'[Ano] ), "@p", [T06 · abstenção % (ano)], "@n", [T06 · abstenções (ano)] )
        -- 2 · Textos
        VAR _verbo = IF ( _dpp >= 0, "subiu", "caiu" )
        VAR _manchete = "Em 20 anos, a abstenção " & _verbo & " de " & @PCT(_p06)@ & " para " & @PCT(_p26)@
        -- 3 · Geometria (anos em x 60–700; % de cima para baixo em y 30–220, de 10% a 26% — ou o que couber)
        VAR _min = MIN ( 0.10, MINX ( _anos, [@p] ) - 0.01 ) -- geometria
        VAR _max = MAX ( 0.26, MAXX ( _anos, [@p] ) + 0.01 ) -- geometria
        VAR _pts =
            ADDCOLUMNS (
                _anos,
                "@x", 60 + ( 'Ano'[Ano] - 2006 ) / 20 * 640, -- geometria
                "@y", 220 - ( [@p] - _min ) / ( _max - _min ) * 190 -- geometria
            )
        VAR _caminho =
            CONCATENATEX ( _pts, @CSS([@x])@ & "," & @CSS([@y])@, " L", 'Ano'[Ano], ASC ) -- geometria
        VAR _area =
            "M60,250 L" & _caminho & " L700,250 Z" -- geometria
        VAR _rotulos =
            CONCATENATEX (
                _pts,
                "<div class='pt sobe d" & ( ( 'Ano'[Ano] - 2006 ) / 4 + 6 ) & "' style='left:" & @CSS([@x] - 50)@
                    & "px;top:" & @CSS([@y] - 40)@ & "px'>" & @PCT([@p])@ & "</div>"
                    & "<div class='an' style='left:" & @CSS([@x] - 50)@ & "px'>" & 'Ano'[Ano] & "</div>",
                "",
                'Ano'[Ano], ASC
            )
        VAR _pontos =
            CONCATENATEX (
                _pts,
                "<circle class='brota d" & ( ( 'Ano'[Ano] - 2006 ) / 4 + 5 ) & "' cx='" & @CSS([@x])@ & "' cy='"
                    & @CSS([@y])@ & "' r='6'/>",
                "",
                'Ano'[Ano], ASC
            )
        -- 4 · Marcação
        VAR _html =
            "<div class='tela se'>"
                & "<div class='sob sobe'>A ausência em duas décadas · 1º turno</div>"
                & "<div class='man sobe d1'>" & _manchete & "</div>"
                & "<div class='gr'><svg width='760' height='270' viewBox='0 0 760 270'>"
                & "<path class='area esmaece' d='" & _area & "'/>"
                & "<path class='linha traco d3' pathLength='1' d='M" & _caminho & "'/>"
                & "<line class='base' x1='40' y1='250' x2='720' y2='250'/>" & _pontos & "</svg>" & _rotulos
                & "<div class='mao dpp entra d14'>" & @PP(_dpp)@ & IF ( ABS ( _dpp ) < 2, " ponto", " pontos" ) & " em 20 anos</div></div>"
            & "</div>"
        RETURN
            _html
        """))
    G.desenho("T06 · Série · ALT", "Texto para leitor de tela da série da abstenção.", dax("""
        LEFT (
            "Abstenção no 1º turno, " & [T06 · recorte] & ": " & @PCT([T06 · abstenção % 2006])@ & " em 2006 e "
                & @PCT([T06 · abstenção %])@ & " em 2026.",
            250
        )
        """))
    # idade
    leit = "\n".join(f"        VAR _a{i} = [T06 · idade {f} · 2014]\n        VAR _b{i} = [T06 · idade {f} · 2026]"
                     for i, (f, _c) in enumerate(FAIXAS))
    linhas = "\n".join(
        f"""        VAR _l{i} =
            VAR _xa = 140 + _a{i} * 700 -- geometria
            VAR _xb = 140 + _b{i} * 700 -- geometria
            VAR _d = ( _b{i} - _a{i} ) * 100
            RETURN
                "<div class='fx" & IF ( {i} = 1, " dest", "" ) & " sobe d" & ( {i} + 4 ) & "' style='top:" & {68 + i * 26} & "px'>"
                    & "<span class='nm'>{f}</span>"
                    & "<i class='lig' style='left:" & @CSS(MIN ( _xa, _xb ))@ & "px;width:" & @CSS(ABS ( _xb - _xa ))@ & "px'></i>"
                    & "<i class='p14' style='left:" & @CSS(_xa - 6)@ & "px'></i>"
                    & "<i class='p26' style='left:" & @CSS(_xb - 6)@ & "px'></i>"
                    & "<span class='vl'>" & @PCT(_b{i})@ & "</span>"
                    & "<span class='dd'>" & @PP(_d)@ & "</span></div>\""""
        for i, (f, _c) in enumerate(FAIXAS))
    soma = " & ".join(f"_l{i}" for i in range(len(FAIXAS)))
    G.desenho("T06 · Idade · HTML", "Quem falta mais: a abstenção por faixa de idade em 2014 e 2026 (Brasil), um "
              "haltere por faixa. Só lê contas; posições são geometria.", dax(f"""
        -- 1 · Leituras
        VAR _comUF = [T06 · com UF]
{leit}
        -- 2 · Textos
        VAR _manchete =
            "Dos 18 aos 24 anos, foi de " & @PCT(_a1)@ & " para " & @PCT(_b1)@ & "; acima dos 70, caiu de " & @PCT(_a6)@
                & " para " & @PCT(_b6)@
        VAR _rot = "Quem falta mais · por idade, 2014 → 2026" & IF ( _comUF = 1, " · Brasil (o TSE não publica por UF)", "" )
        -- 3 · Geometria (0% a 70% em x 140–630)
{linhas}
        -- 4 · Marcação
        VAR _html =
            "<div class='tela ida'>"
                & "<div class='rot sobe'>" & _rot & "</div>"
                & "<div class='man sobe d1'>" & _manchete & "</div>"
                & "<div class='leg entra d3'><i class='p14'></i>2014 <i class='p26'></i>2026 · % dos aptos da faixa que não foram votar · variação em pontos</div>"
                & {soma}
            & "</div>"
        RETURN
            _html
        """))
    G.desenho("T06 · Idade · ALT", "Texto para leitor de tela do bloco por idade.", dax("""
        LEFT (
            "Abstenção por idade no Brasil: dos 18 aos 24 anos, " & @PCT([T06 · idade 18 a 24 · 2014])@ & " em 2014 e "
                & @PCT([T06 · idade 18 a 24 · 2026])@ & " em 2026; acima dos 70, " & @PCT([T06 · idade 70 ou mais · 2014])@
                & " e " & @PCT([T06 · idade 70 ou mais · 2026])@ & ".",
            250
        )
        """))
    # mapa: legenda, ALT e dossiê do município
    G.desenho("T06 · Legenda · HTML", "Legenda do mapa da abstenção.", dax("""
        "<div class='tela lgm entra d6'>"
            & "<span class='it'><i class='bol'></i>cada ponto é um município; o tamanho segue quantos faltaram</span>"
            & "<span class='it'><span>12%</span><i class='esc'></i><span>30% ou mais faltaram</span></span>"
        & "</div>"
        """))
    G.desenho("T06 · Legenda · ALT", "Texto para leitor de tela da legenda do mapa da abstenção.", dax("""
        "Legenda: cada ponto é um município; o tamanho segue quantos faltaram e a cor vai do creme (12%) à tinta (30% ou mais de abstenção)."
        """))
    G.desenho("T06 · Mapa · ALT", "Texto para leitor de tela do mapa da abstenção.", dax("""
        LEFT (
            "Mapa da abstenção de 2026 por município, " & [T06 · recorte]
                & ": cada ponto é um município, mais escuro onde mais gente faltou. Passe o mouse num ponto para ver a cidade.",
            250
        )
        """))
    G.desenho("T06 · Tooltip município · HTML", "Dossiê do município do ponto (ficha presa com fita): a abstenção em "
              "2026 e em 2006, quantas pessoas faltaram e a comparação com o Brasil. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _mun = [T06 · município]
        VAR _reg = [T06 · região do município]
        VAR _p26 = [T06 · abstenção % (município)]
        VAR _p06 = [T06 · abstenção % 2006 (município)]
        VAR _n = [T06 · abstenções (município)]
        VAR _aptos = [T06 · aptos (município)]
        VAR _um = [T06 · um em cada (município)]
        VAR _br = [T06 · abstenção % Brasil]
        -- 2 · Textos
        VAR _nota = IF ( _um > 0, "1 em cada " & _um & " faltou", "" )
        VAR _compara = IF ( _p26 > _br, "acima", IF ( _p26 < _br, "abaixo", "igual" ) )
        -- 4 · Marcação
        VAR _css =
            "<style>"
                & ".tt6{{position:fixed;inset:0;background:var(--papel)}}"
                & ".tt6 .ficha{{position:absolute;left:14px;top:22px;right:14px;bottom:14px;background:var(--branco);"
                & "border:1.5px solid var(--areia);box-shadow:3px 4px 0 rgba(28,25,21,.07)}}"
                & ".tt6 .fita{{position:absolute;left:150px;top:-16px;width:96px;transform:rotate(3deg);opacity:.9}}"
                & ".tt6 .ic{{position:absolute;right:16px;top:14px;width:34px}}"
                & ".tt6 .cab{{position:absolute;left:18px;top:14px;right:60px}}"
                & ".tt6 .nm{{font-size:22px;font-weight:700;line-height:1.15}}"
                & ".tt6 .big{{position:absolute;left:18px;top:82px;font-size:44px;font-weight:700;letter-spacing:-.03em}}"
                & ".tt6 .bs{{position:absolute;left:178px;top:90px;right:18px;font-size:15px;color:var(--grafite);line-height:1.35}}"
                & ".tt6 .lin{{position:absolute;left:18px;right:18px;top:150px;border-top:1px dashed var(--areia);"
                & "padding-top:8px;font-size:15px;color:var(--grafite)}}.tt6 .lin b{{color:var(--tinta)}}"
                & ".tt6 .mao{{position:absolute;right:18px;bottom:8px;font-size:28px;color:var(--tinta)}}"
            & "</style>"
        VAR _html =
            _css
                & "<div class='tt6'><div class='ficha'>"
                & "<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/>"
                & "<img class='ic' alt='' src='{URL_MIDIA}/arte/icones/urna-tinta.png'/>"
                & "<div class='cab sobe'><div class='nm'>" & @ESC(_mun)@ & "</div>"
                & "<div class='rot'>" & @ESC(_reg)@ & " · " & @INT(_aptos)@ & " eleitores</div></div>"
                & "<div class='big sobe d1'>" & @PCT(_p26)@ & "</div>"
                & "<div class='bs sobe d2'>não foram votar em 2026: <b>" & @INT(_n)@ & "</b> pessoas</div>"
                & "<div class='lin sobe d3'>Em 2006: <b>" & @PCT(_p06)@ & "</b> · " & _compara & " da média do Brasil em 2026 (<b>"
                & @PCT(_br)@ & "</b>)</div>"
                & "<div class='mao entra d5'>" & _nota & "</div>"
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _mun ) && NOT ISBLANK ( _aptos ), _html )
        """).replace("{{", "{").replace("}}", "}"))
    G.desenho("T06 · Tooltip município · ALT", "Texto para leitor de tela do dossiê do município (abstenção).", dax("""
        LEFT (
            [T06 · município] & ": " & @PCT([T06 · abstenção % (município)])@ & " não foram votar em 2026 ("
                & @INT([T06 · abstenções (município)])@ & " pessoas); em 2006, " & @PCT([T06 · abstenção % 2006 (município)])@ & ".",
            250
        )
        """))


# ---------------------------------------------------------------------------------------------------- página
def _css_resposta() -> str:
    return (
        ".rp>*{position:absolute;left:0}"
        ".rp .sob{top:0}"
        ".rp .topo{top:30px;display:flex;align-items:flex-end;gap:26px;width:780px}"
        ".rp .big{font-size:120px;font-weight:700;letter-spacing:-.04em;line-height:.9;white-space:nowrap;"
        "font-variant-numeric:tabular-nums lining-nums}"
        ".rp .lado{position:relative;padding-bottom:2px;flex:1}"
        ".rp .nfv{font-size:32px;font-weight:600;letter-spacing:-.01em}"
        ".rp .subl{position:absolute;left:-4px;top:38px;width:250px;height:14px;overflow:visible}"
        ".rp .lado .txt{margin-top:14px;font-size:16px;line-height:1.35}"
        ".rp .mc{top:166px;width:780px;font-size:28px;line-height:1.22}"
        ".rp .regua{top:246px;width:780px;height:150px}"
        ".rp .regua>*{position:absolute;left:0}"
        ".rp .rt1{top:0}.rp .r1{top:22px}"
        ".rp .r1 .cheia{fill:var(--tinta)}"
        ".rp .r1 .cortes line{stroke:var(--papel);stroke-width:2}"
        ".rp .dif{top:72px;height:22px}"
        ".rp .dif div{height:22px;background:repeating-linear-gradient(-45deg,var(--grafite) 0 3px,var(--creme) 3px 6px);"
        "box-shadow:inset 0 0 0 1.5px var(--tinta)}"
        ".rp .rt2{top:102px}"
        ".rp .nota1{left:auto;right:16px;top:86px;font-size:30px}.rp .nota1.baixa{top:110px}"
        ".rp .pe{top:398px;width:780px;font-size:16px}"
    )


def _css_serie() -> str:
    return (
        ".se>*{position:absolute;left:0}"
        ".se .sob{top:0}.se .man{top:28px;width:780px;font-size:24px}"
        ".se .gr{top:66px;width:760px;height:280px}"
        ".se svg{position:absolute;left:0;top:0}"
        ".se .area{fill:var(--creme)}"
        ".se .linha{fill:none;stroke:var(--tinta);stroke-width:3;stroke-linejoin:round;stroke-linecap:round}"
        ".se .base{stroke:var(--areia);stroke-width:1.2}"
        ".se circle{fill:var(--tinta);stroke:var(--papel);stroke-width:2.5}"
        ".se .pt{position:absolute;width:100px;text-align:center;font-size:20px;font-weight:700;"
        "font-variant-numeric:tabular-nums}"
        ".se .dpp{position:absolute;left:470px;top:150px;font-size:30px;color:var(--tinta)}"
        ".se .an{position:absolute;top:258px;width:100px;text-align:center;font-size:15px;font-weight:600;"
        "color:var(--grafite)}"
    )


def _css_idade() -> str:
    return (
        ".ida>*{position:absolute;left:0}"
        ".ida .rot{top:0}.ida .man{top:20px;width:780px;font-size:18px;line-height:1.25}"
        ".ida .leg{top:48px;font-size:13px;color:var(--cinza);display:flex;align-items:center;gap:6px}"
        ".ida .leg i{position:relative;display:inline-block;margin-left:6px}"
        ".ida .fx{width:780px;height:24px}"
        ".ida .fx>*{position:absolute}"
        ".ida .fx .nm{left:0;top:2px;font-size:15px;font-weight:600;color:var(--grafite)}"
        ".ida .fx.dest .nm{color:var(--tinta)}"
        ".ida .lig{top:11px;height:2px;background:var(--areia)}"
        ".ida .p14,.ida .p26{width:12px;height:12px;border-radius:50%;top:6px}"
        ".ida .p14{background:var(--papel);box-shadow:inset 0 0 0 2px var(--grafite)}"
        ".ida .p26{background:var(--tinta)}"
        ".ida .leg .p14,.ida .leg .p26{position:relative;top:0}"
        ".ida .fx .vl{left:650px;top:2px;font-size:15px;font-weight:700;font-variant-numeric:tabular-nums}"
        ".ida .fx .dd{left:700px;width:80px;top:2px;text-align:right;font-size:15px;color:var(--grafite);"
        "font-variant-numeric:tabular-nums}"
        ".ida .fx.dest .lig{background:var(--tinta);height:3px}"
    )


def _css_legenda() -> str:
    return (
        ".lgm{display:flex;flex-wrap:wrap;gap:4px 22px;align-items:center;font-size:14px;color:var(--grafite)}"
        ".lgm .it{display:flex;align-items:center;gap:8px}"
        ".lgm i{display:inline-block;flex:none}"
        ".lgm .bol{width:22px;height:14px;background:radial-gradient(circle at 4px 9px,var(--grafite) 2.5px,"
        "transparent 3px),radial-gradient(circle at 15px 7px,var(--grafite) 6px,transparent 6.5px)}"
        ".lgm .esc{width:90px;height:10px;background:linear-gradient(90deg,#E5DBC8,#CBBDA2,#7A6F60,#1C1915)}"
    )


def declarar_ausencia() -> list:
    import pbip_lib as lib
    from pbip_lib import Pagina, Visual
    css = "Estilo · CSS"
    z = lib.CAMADAS["conteudo"]
    tt = "ttT06Municipio"
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"), lib.campo_coluna("x", "Município", "X"),
              lib.campo_coluna("y", "Município", "Y"), lib.campo_coluna("uf", "Município", "UF"),
              lib.campo_medida("tam", "T06 · abstenções (município)"),
              lib.campo_medida("val", "T06 · abstenção % (município)")]
    return [
        Visual(P, lib.visual_html("T06_Resposta_Html", *RESPOSTA, "T06 · Resposta · HTML", folha_de_estilo=css, z=z,
                                  tab=100, alt=lib.medida("T06 · Resposta · ALT"),
                                  modelo_corpo=f"<style>{_css_resposta()}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T06_Serie_Html", *SERIE, "T06 · Série · HTML", folha_de_estilo=css, z=z + 2,
                                  tab=110, alt=lib.medida("T06 · Série · ALT"),
                                  modelo_corpo=f"<style>{_css_serie()}</style>" + "{{content}}")),
        Visual(P, lib.visual_deneb("T06_Mapa_Pontos", *MAPA, "spec/t06_mapa.json", campos,
                                   alt=lib.medida("T06 · Mapa · ALT"), z=z + 4, tab=200, tooltip_pagina=tt,
                                   renderizacao="canvas")),
        Visual(P, lib.visual_html("T06_Mapa_Legenda", *LEGENDA, "T06 · Legenda · HTML", folha_de_estilo=css,
                                  z=z + 6, tab=210, alt=lib.medida("T06 · Legenda · ALT"),
                                  modelo_corpo=f"<style>{_css_legenda()}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T06_Idade_Html", *IDADE, "T06 · Idade · HTML", folha_de_estilo=css, z=z + 8,
                                  tab=220, alt=lib.medida("T06 · Idade · ALT"),
                                  modelo_corpo=f"<style>{_css_idade()}</style>" + "{{content}}")),
        Pagina(lib.pagina_tooltip(tt, "Município · ausência", altura=TT_H, largura=TT_W), ordem=160),
        Visual(tt, lib.visual_html(f"TT_{tt[2:]}_Conteudo", 0, 0, TT_W, TT_H, "T06 · Tooltip município · HTML",
                                   alt=lib.medida("T06 · Tooltip município · ALT"), pagina_wh=(TT_W, TT_H),
                                   folha_de_estilo=css)),
    ]


def main() -> int:
    contas()
    desenho()
    apagados = G.limpar()
    gravar_spec("t06_mapa.json", spec_mapa(
        "abstencao", ("#E5DBC8", "#7A6F60", "#1C1915"), "Tela 06: um ponto por município (tamanho = quantos faltaram, "
        "cor = abstenção de 2026, do creme à tinta); contorno das UFs em traço; pontos em onda."))
    print(G.resumo(), "· apagados:", [p.name for p in apagados])
    return 0


if __name__ == "__main__":
    sys.exit(main())
