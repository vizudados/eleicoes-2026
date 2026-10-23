# -*- coding: utf-8 -*-
"""desenho_t06 — tela 06 · Ausência: quantos brasileiros não escolheram ninguém? Dono: agente das telas 06 e 07.

    python -I -X utf8 pbi/scripts/desenho_t06.py        # grava pbi/dax/T06 Ausência/…

Protagonista: os 33,5 milhões que não foram votar e a régua que mostra quantas vezes a diferença entre Flávio e Lula
cabe neles (15). Apoios: a abstenção subindo em duas décadas (2006 → 2026) e, no lugar do mapa e das idades (que viraram
a tela 07 · Quem falta, código T25, em 23/10/2026), a composição de quem não escolheu ninguém a cada eleição: quem
faltou, quem anulou e quem votou em branco, numa coluna por ano. Passar o mouse num ano (na coluna ou na linha) abre o
dossiê do ano: a disputa, quantas vezes a diferença entre os dois primeiros cabia em quem faltou, brancos e nulos.
Tons neutros: creme → tinta (sem vermelho/azul).

Fontes: sem filtro, o comparecimento oficial do Brasil ('Comparecimento ano', com o exterior: os 158,7 mi aptos do TSE);
com o filtro de UF, a soma dos municípios da UF ('Município ano'). Oráculo: mockup/data/eleicoes.json › paginas[6].
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from desenho_t01_t06_comum import URL_MIDIA, Gravador, dax  # noqa: E402

P = "T06"
G = Gravador("T06 Ausência")
CA = "'Comparecimento ano'"
MA = "'Município ano'"
MU = "'Município'"
AP = "'Abstenção perfil'"
CU = "'Candidato UF'"
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]
RESPOSTA = (150, 140, 780, 470)
SERIE = (150, 640, 780, 360)
SERIE_ALVOS = (150, 706, 780, 294)        # um alvo transparente por ano sobre a linha (só a dica)
COMP_TOPO = (990, 140, 780, 128)
COMP = (990, 282, 780, 718)
COMP_SLOT = 130                            # largura de cada ano na composição
COMP_ALT = 560                             # altura máxima da coluna (a maior soma da série)
TT = "ttT06Ano"
TT_W, TT_H = 440, 320


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
    # composição de quem não escolheu ninguém, ano a ano (a coluna da direita)
    c("T06 · não escolheram (ano)", "Abstenções + brancos + nulos no ano do contexto (Brasil oficial ou soma dos "
      "municípios da UF): quem não escolheu nenhum candidato.",
      "[T06 · abstenções (ano)] + [T06 · brancos (ano)] + [T06 · nulos (ano)]", "#,0",
      "paginas[6].serie[].nao_escolheram (2006 = 29.897.525; 2026 = 39.444.291)")
    c("T06 · faltaram entre quem não escolheu (ano)", "Parcela de quem não escolheu ninguém que nem foi votar, no ano "
      "do contexto (0–1).", "DIVIDE ( [T06 · abstenções (ano)], [T06 · não escolheram (ano)] )", "0%",
      "Brasil 2006 = 70,5% · 2026 = 84,9% (abstenções ÷ nao_escolheram, paginas[6].serie)")
    for ano in (2006, 2026):
        c(f"T06 · faltaram entre quem não escolheu · em cada 10 · {ano}", f"Em cada 10 que não escolheram ninguém em "
          f"{ano}, quantos nem foram votar (arredondado), no recorte.",
          f"CALCULATE ( ROUND ( [T06 · faltaram entre quem não escolheu (ano)] * 10, 0 ), 'Ano'[Ano] = {ano} )", "0",
          "Brasil = 7" if ano == 2006 else "Brasil = 8")
        c(f"T06 · brancos e nulos · {ano}", f"Brancos + nulos no 1º turno de {ano}, no recorte.",
          f"CALCULATE ( [T06 · brancos (ano)] + [T06 · nulos (ano)], 'Ano'[Ano] = {ano} )", "#,0",
          "paginas[6].serie[2006].brancos_nulos_txt = 8,8 mi" if ano == 2006
          else "paginas[6].serie[2026].brancos_nulos_txt = 6,0 mi")
    c("T06 · maior não escolheram da série", "A maior soma de quem não escolheu ninguém entre os seis anos, no recorte: "
      "a escala das colunas da composição.", dax("""
        MAXX (
            CALCULATETABLE ( VALUES ( 'Ano'[Ano] ), REMOVEFILTERS ( 'Ano' ) ),
            VAR _a = 'Ano'[Ano]
            RETURN
                CALCULATE ( [T06 · não escolheram (ano)], 'Ano'[Ano] = _a )
        )
        """), "#,0", "Brasil = 40.254.330 (2018, paginas[6].serie[2018].nao_escolheram)")
    # dossiê do ano (coluna da composição ou ponto da linha)
    c("T06 · ano", "Ano da linha (coluna da composição ou ponto da série).", "SELECTEDVALUE ( 'Ano'[Ano] )", "0")
    c("T06 · votos do PT (ano)", "Votos do candidato do PT no ano da linha, somados nos municípios do recorte.",
      f"SUM ( {MA}[VotosPT] )", "#,0")
    c("T06 · votos do adversário (ano)", "Votos do principal adversário no ano da linha, somados nos municípios do "
      "recorte.", f"SUM ( {MA}[VotosAdversario] )", "#,0")
    c("T06 · disputa do ano", "Os dois primeiros do 1º turno do ano da linha, o mais votado antes: no Brasil, o "
      "resultado oficial ('Candidato ano'); com UF, o candidato do PT e o principal adversário na ordem dos votos na UF.",
      dax("""
        VAR _1 = CALCULATE ( SELECTEDVALUE ( 'Candidato ano'[Candidato] ), 'Candidato ano'[Posição] = 1 )
        VAR _2 = CALCULATE ( SELECTEDVALUE ( 'Candidato ano'[Candidato] ), 'Candidato ano'[Posição] = 2 )
        VAR _pt = SELECTEDVALUE ( 'Ano'[Candidato do PT] )
        VAR _adv = SELECTEDVALUE ( 'Ano'[Adversário] )
        RETURN
            IF (
                [T06 · com UF] = 1,
                IF ( [T06 · votos do PT (ano)] >= [T06 · votos do adversário (ano)], _pt & " e " & _adv, _adv & " e " & _pt ),
                IF ( NOT ISBLANK ( _1 ), _1 & " e " & _2 )
            )
        """), "texto", "2026 = Flávio Bolsonaro e Lula")
    c("T06 · diferença do ano", "Diferença de votos entre os dois primeiros no 1º turno do ano da linha: no Brasil, o "
      "resultado oficial (com o exterior); com UF, PT × principal adversário nos municípios da UF.", dax("""
        IF (
            [T06 · com UF] = 1,
            ABS ( [T06 · votos do PT (ano)] - [T06 · votos do adversário (ano)] ),
            CALCULATE ( SUM ( 'Candidato ano'[Votos] ), 'Candidato ano'[Posição] = 1 )
                - CALCULATE ( SUM ( 'Candidato ano'[Votos] ), 'Candidato ano'[Posição] = 2 )
        )
        """), "#,0", "2026 = 2.224.965 (paginas[1].diferenca.votos)")
    c("T06 · vezes a diferença (ano)", "Quantas vezes a diferença entre os dois primeiros cabe em quem faltou, no ano da "
      "linha e no recorte.", "DIVIDE ( [T06 · abstenções (ano)], [T06 · diferença do ano] )", "0.0",
      "2026 = 15,0 (paginas[6].vezes_a_diferenca)")
    c("T06 · vezes a diferença em 2026", "A régua de 2026 (quem faltou ÷ a diferença entre Flávio e Lula) vista de "
      "qualquer ano: a comparação à mão no dossiê do ano.", "CALCULATE ( [T06 · vezes a diferença], 'Ano'[Ano] = 2026 )",
      "0.0", "Brasil = 15,0")

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
    # composição de quem não escolheu ninguém, ano a ano (a coluna da direita)
    G.desenho("T06 · Composição topo · HTML", "Título da composição: em cada 10 que não escolheram ninguém, quantos nem "
              "foram votar em 2026 e em 2006, a legenda das três partes e a nota à mão sobre brancos e nulos. Só lê "
              "contas.", dax("""
        -- 1 · Leituras
        VAR _recorte = [T06 · recorte]
        VAR _d26 = [T06 · faltaram entre quem não escolheu · em cada 10 · 2026]
        VAR _d06 = [T06 · faltaram entre quem não escolheu · em cada 10 · 2006]
        VAR _bn26 = [T06 · brancos e nulos · 2026]
        VAR _bn06 = [T06 · brancos e nulos · 2006]
        -- 2 · Textos
        VAR _man =
            IF (
                _d26 = _d06,
                "Desde 2006, " & _d26 & " em cada 10 que não escolhem ninguém nem vão votar",
                "Hoje, " & _d26 & " em cada 10 que não escolhem ninguém nem vão votar; em 2006, eram " & _d06
            )
        VAR _nota = IF ( _bn26 < _bn06, "brancos e nulos encolheram", "brancos e nulos cresceram" )
        -- 4 · Marcação
        RETURN
            "<div class='tela ct'>"
                & "<div class='sob sobe'>Quem não escolheu ninguém · eleição a eleição · " & @ESC(_recorte)@ & "</div>"
                & "<div class='man sobe d1'>" & _man & "</div>"
                & "<div class='leg entra d3'><span><i class='f'></i>não foram votar</span>"
                & "<span><i class='n'></i>anularam</span><span><i class='b'></i>votaram em branco</span>"
                & "<span class='mao'>" & _nota & "</span></div>"
            & "</div>"
        """))
    G.desenho("T06 · Composição topo · ALT", "Texto para leitor de tela do título da composição.", dax("""
        LEFT (
            "Quem não escolheu ninguém, " & [T06 · recorte] & ": em 2006, "
                & [T06 · faltaram entre quem não escolheu · em cada 10 · 2006] & " em cada 10 nem foram votar; em 2026, "
                & [T06 · faltaram entre quem não escolheu · em cada 10 · 2026] & ". Brancos e nulos: "
                & @MI1([T06 · brancos e nulos · 2006])@ & " em 2006 e " & @MI1([T06 · brancos e nulos · 2026])@ & " em 2026.",
            250
        )
        """))
    G.desenho("T06 · Composição · HTML", "Uma coluna por 1º turno (granularidade Ano[Ano]): quem não escolheu ninguém "
              "empilhado em quem faltou (grafite), quem anulou (marrom) e quem votou em branco (areia); o total em cima e, "
              "na parte de quem faltou, a parcela que ela é do total. O alvo transparente abre o dossiê do ano. Só lê "
              "contas; a escala é geometria.", dax(f"""
        -- 1 · Leituras
        VAR _ano = [T06 · ano]
        VAR _abst = [T06 · abstenções (ano)]
        VAR _nul = [T06 · nulos (ano)]
        VAR _bra = [T06 · brancos (ano)]
        VAR _tot = [T06 · não escolheram (ano)]
        VAR _parte = [T06 · faltaram entre quem não escolheu (ano)]
        VAR _teto = [T06 · maior não escolheram da série]
        -- 2 · Textos
        VAR _txtTot = @MI1(_tot)@
        -- 3 · Geometria (6 colunas em {COMP_SLOT} px cada; de 0 ao teto em {COMP_ALT} px sobre a base a 44 px do pé)
        VAR _i = ( _ano - 2006 ) / 4 -- geometria
        VAR _x = _i * {COMP_SLOT} -- geometria
        VAR _k = DIVIDE ( {COMP_ALT}, _teto ) -- geometria
        VAR _ha = _abst * _k -- geometria
        VAR _hn = _nul * _k -- geometria
        VAR _hb = _bra * _k -- geometria
        VAR _rotParte = IF ( _ha >= 30, "<span class='pt'>" & @PCT0(_parte)@ & "</span>" )
        -- 4 · Marcação
        RETURN
            IF (
                NOT ISBLANK ( _tot ),
                "<div class='tela cp'><div class='col' style='left:" & @CSS(_x)@ & "px'>"
                    & "<div class='tot sobe d" & ( _i + 6 ) & "' style='bottom:" & @CSS(_ha + _hn + _hb + 52)@ & "px'>"
                    & _txtTot & "</div>"
                    & "<div class='pilha barra-y d" & ( _i + 2 ) & "' style='height:" & @CSS(_ha + _hn + _hb)@ & "px'>"
                    & "<i class='b' style='height:" & @CSS(_hb)@ & "px'></i>"
                    & "<i class='n' style='height:" & @CSS(_hn)@ & "px'></i>"
                    & "<i class='f' style='height:" & @CSS(_ha)@ & "px'>" & _rotParte & "</i></div>"
                    & "<div class='ano'>" & _ano & "</div><div class='alvo'></div></div></div>"
            )
        """))
    G.desenho("T06 · Composição · ALT", "Texto para leitor de tela das colunas da composição.", dax("""
        LEFT (
            "Colunas de 2006 a 2026 com quem não escolheu ninguém em " & [T06 · recorte]
                & ": quem faltou, quem anulou e quem votou em branco. Passe o mouse num ano para ver a disputa e quantas "
                & "vezes a diferença entre os dois primeiros cabia em quem faltou.",
            250
        )
        """))
    G.desenho("T06 · Série alvos · HTML", "Alvo transparente de cada ano sobre a linha da série (granularidade "
              "Ano[Ano]): só recebe o mouse para abrir o dossiê do ano; não desenha nada.", dax("""
        -- 1 · Leituras
        VAR _ano = [T06 · ano]
        VAR _abst = [T06 · abstenções (ano)]
        -- 3 · Geometria (o x do ano na série: 60 + (ano − 2006) × 32; alvo de 128 px centrado nele)
        VAR _x = 60 + ( _ano - 2006 ) * 32 - 64 -- geometria
        -- 4 · Marcação
        RETURN
            IF (
                NOT ISBLANK ( _abst ),
                "<div class='tela sa'><div class='alvo' style='left:" & @CSS(_x)@ & "px'></div></div>"
            )
        """))
    G.desenho("T06 · Série alvos · ALT", "Texto para leitor de tela dos alvos da série.", dax("""
        "Passe o mouse num ano da linha para ver a disputa daquele 1º turno e quantas vezes a diferença entre os dois "
            & "primeiros cabia em quem faltou."
        """))
    # dossiê do ano (ficha presa com fita), aberto pela coluna da composição e pelo ponto da série
    G.desenho("T06 · Tooltip ano · HTML", "Dossiê do ano (ficha presa com fita): quem disputou, quantas vezes a "
              "diferença entre os dois primeiros cabia em quem faltou, os números de quem faltou e da diferença, quantos "
              "anularam ou votaram em branco e, à mão, a comparação com 2026. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _ano = [T06 · ano]
        VAR _recorte = [T06 · recorte]
        VAR _disputa = [T06 · disputa do ano]
        VAR _vezes = [T06 · vezes a diferença (ano)]
        VAR _vezes26 = [T06 · vezes a diferença em 2026]
        VAR _abst = [T06 · abstenções (ano)]
        VAR _dif = [T06 · diferença do ano]
        VAR _nul = [T06 · nulos (ano)]
        VAR _bra = [T06 · brancos (ano)]
        -- 2 · Textos
        VAR _txtVezes = IF ( _vezes >= 10, FORMAT ( _vezes, "0" ), FORMAT ( _vezes, "0.0" ) )
        VAR _txt26 = IF ( _vezes26 >= 10, FORMAT ( _vezes26, "0" ), FORMAT ( _vezes26, "0.0" ) )
        VAR _cabe =
            IF (
                _vezes >= 1,
                "é quantas vezes a diferença entre os dois primeiros cabia em quem faltou",
                "a diferença entre " & @ESC(_disputa)@ & " foi maior que o número de quem faltou"
            )
        VAR _nota = IF ( _ano <> 2026 && NOT ISBLANK ( _vezes26 ), "em 2026: " & _txt26 & " vezes" )
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
                & ".tt6 .big{{position:absolute;left:18px;top:80px;font-size:44px;font-weight:700;letter-spacing:-.03em;"
                & "white-space:nowrap}}"
                & ".tt6 .bs{{position:absolute;left:178px;top:82px;right:18px;font-size:15px;color:var(--grafite);"
                & "line-height:1.35}}"
                & ".tt6 .lin{{position:absolute;left:18px;right:18px;border-top:1px dashed var(--areia);"
                & "padding-top:8px;font-size:15px;color:var(--grafite)}}.tt6 .lin b{{color:var(--tinta)}}"
                & ".tt6 .mao{{position:absolute;right:18px;bottom:8px;font-size:28px;color:var(--tinta)}}"
            & "</style>"
        VAR _html =
            _css
                & "<div class='tt6'><div class='ficha'>"
                & "<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/>"
                & "<img class='ic' alt='' src='{URL_MIDIA}/arte/icones/urna-tinta.png'/>"
                & "<div class='cab sobe'><div class='nm'>1º turno de " & _ano & "</div>"
                & "<div class='rot'>" & @ESC(_disputa)@ & " · " & @ESC(_recorte)@ & "</div></div>"
                & "<div class='big sobe d1'>" & _txtVezes & "×</div>"
                & "<div class='bs sobe d2'>" & _cabe & "</div>"
                & "<div class='lin sobe d3' style='top:160px'>Faltaram <b>" & @MI1(_abst)@ & "</b>; a diferença entre "
                & "os dois foi de <b>" & @MI(_dif)@ & "</b></div>"
                & "<div class='lin sobe d4' style='top:204px'>Anularam <b>" & @MI1(_nul)@ & "</b> · votaram em branco <b>"
                & @MI1(_bra)@ & "</b></div>"
                & "<div class='mao entra d6'>" & _nota & "</div>"
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _abst ) && NOT ISBLANK ( _dif ), _html )
        """).replace("{{", "{").replace("}}", "}"))
    G.desenho("T06 · Tooltip ano · ALT", "Texto para leitor de tela do dossiê do ano.", dax("""
        LEFT (
            "1º turno de " & [T06 · ano] & " (" & [T06 · disputa do ano] & "), " & [T06 · recorte] & ": faltaram "
                & @MI1([T06 · abstenções (ano)])@ & ", " & FORMAT ( [T06 · vezes a diferença (ano)], "0.0" )
                & " vezes a diferença entre os dois primeiros; anularam " & @MI1([T06 · nulos (ano)])@
                & " e votaram em branco " & @MI1([T06 · brancos (ano)])@ & ".",
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


def _css_composicao_topo() -> str:
    return (
        ".ct>*{position:absolute;left:0}"
        ".ct .sob{top:0;width:780px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".ct .man{top:28px;width:780px;font-size:24px;line-height:1.25}"
        ".ct .leg{top:96px;width:780px;display:flex;align-items:center;gap:20px;font-size:14px;color:var(--grafite)}"
        ".ct .leg span{display:inline-flex;align-items:center;gap:7px}"
        ".ct .leg i{display:inline-block;width:14px;height:14px}"
        ".ct .leg .f{background:var(--grafite)}.ct .leg .n{background:var(--marrom)}.ct .leg .b{background:var(--areia)}"
        ".ct .leg .mao{margin-left:auto;font-size:26px;color:var(--tinta);transform:rotate(-2deg)}"
    )


def _css_composicao() -> str:
    w = COMP_SLOT
    return (
        ".cp{pointer-events:none}"
        f".cp .col{{position:absolute;top:0;width:{w}px;height:718px}}"
        f".cp .pilha{{position:absolute;left:{(w - 76) / 2:.0f}px;bottom:44px;width:76px;display:flex;"
        "flex-direction:column}"
        ".cp .pilha i{display:block;width:76px;flex:none;position:relative;box-shadow:inset 0 1.5px 0 var(--papel)}"
        ".cp .pilha .f{background:var(--grafite)}.cp .pilha .n{background:var(--marrom)}.cp .pilha .b{background:var(--areia)}"
        ".cp .pilha .pt{position:absolute;left:0;right:0;top:8px;text-align:center;font-size:15px;font-weight:700;"
        "color:var(--branco);font-style:normal}"
        f".cp .tot{{position:absolute;left:0;width:{w}px;text-align:center;font-size:20px;font-weight:700;"
        "font-variant-numeric:tabular-nums}"
        f".cp .ano{{position:absolute;left:0;bottom:12px;width:{w}px;text-align:center;font-size:17px;"
        "font-weight:600;color:var(--grafite)}"
        ".cp .col::after{content:'';position:absolute;left:10px;right:10px;bottom:43px;height:1.2px;"
        "background:var(--areia)}"
        ".cp .alvo{position:absolute;inset:0;pointer-events:auto}"
    )


def declarar_ausencia() -> list:
    import pbip_lib as lib
    import pagina_lib
    from pbip_lib import Visual
    css = "Estilo · CSS"
    z = lib.CAMADAS["conteudo"]
    # os alvos da série e as colunas da composição só abrem a dica do ano (sem filtro cruzado)
    return [
        Visual(P, lib.visual_html("T06_Resposta_Html", *RESPOSTA, "T06 · Resposta · HTML", folha_de_estilo=css, z=z,
                                  tab=100, alt=lib.medida("T06 · Resposta · ALT"),
                                  modelo_corpo=f"<style>{_css_resposta()}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T06_Serie_Html", *SERIE, "T06 · Série · HTML", folha_de_estilo=css, z=z + 2,
                                  tab=110, alt=lib.medida("T06 · Série · ALT"),
                                  modelo_corpo=f"<style>{_css_serie()}</style>" + "{{content}}")),
        # alvos transparentes sobre a linha (só a dica do ano; o desenho é o da série)
        Visual(P, lib.visual_html("T06_Serie_Alvos", *SERIE_ALVOS, "T06 · Série alvos · HTML", folha_de_estilo=css,
                                  z=z + 3, tab=115, alt=lib.medida("T06 · Série alvos · ALT"),
                                  granularidade=("Ano", "Ano"), tooltip_pagina=TT, movimento=False,
                                  modelo_corpo="<style>.sa{pointer-events:none}.sa .alvo{position:absolute;top:0;"
                                               "width:128px;height:294px;pointer-events:auto}</style>{{content}}")),
        Visual(P, lib.visual_html("T06_Composicao_Topo", *COMP_TOPO, "T06 · Composição topo · HTML",
                                  folha_de_estilo=css, z=z + 4, tab=200, alt=lib.medida("T06 · Composição topo · ALT"),
                                  modelo_corpo=f"<style>{_css_composicao_topo()}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T06_Composicao_Html", *COMP, "T06 · Composição · HTML", folha_de_estilo=css,
                                  z=z + 6, tab=210, alt=lib.medida("T06 · Composição · ALT"),
                                  granularidade=("Ano", "Ano"), tooltip_pagina=TT,
                                  ordenacao=[lib.ordem_coluna("Ano", "Ano")],
                                  modelo_corpo=f"<style>{_css_composicao()}</style>" + "{{content}}")),
        *pagina_lib.tooltip(TT, "Ano · ausência", TT_W, TT_H, "T06 · Tooltip ano · HTML", ordem=160,
                            folha_de_estilo=css),
    ]


def main() -> int:
    contas()
    desenho()
    apagados = G.limpar()
    print(G.resumo(), "· apagados:", [p.name for p in apagados])
    return 0


if __name__ == "__main__":
    sys.exit(main())
