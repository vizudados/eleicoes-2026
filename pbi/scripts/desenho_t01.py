# -*- coding: utf-8 -*-
"""desenho_t01 — medidas da tela 01 · Placar (contas e desenho). Dono: agente das telas 01–06.

    python -I -X utf8 pbi/scripts/desenho_t01.py        # grava pbi/dax/T01 Placar/{Contas,Desenho}/*.dax

Fonte única dos votos: 'Candidato UF' (2022 e 2026, com o exterior ZZ). Sem filtro, a soma das linhas é o resultado
nacional oficial do TSE (igual a 'Candidato ano'); com o filtro de UF da casca, é o resultado da UF.
Oráculo: mockup/data/eleicoes.json › paginas[1].
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from desenho_t01_t06_comum import Gravador, dax  # noqa: E402

G = Gravador("T01 Placar")
URL = "https://vizudados.github.io/eleicoes-2026/midia"
CU = "'Candidato UF'"

# Sublinhado duplo à mão embaixo do número da diferença (o laço em volta cruzava os dígitos; o Alisson, 23/10/2026:
# "os rabiscos que ficam em cima dos números não ficou muito bom"). Escala com a largura do número.
SUBLINHADO = ("<svg class='sub' viewBox='0 0 400 24' preserveAspectRatio='none' aria-hidden='true'>"
              "<defs><filter id='rbl' filterUnits='userSpaceOnUse' x='-10' y='-10' width='420' height='44'>"
              "<feTurbulence type='fractalNoise' baseFrequency='0.035' numOctaves='2' seed='3' result='r'/>"
              "<feDisplacementMap in='SourceGraphic' in2='r' scale='2.2' xChannelSelector='R' yChannelSelector='G'/>"
              "</filter></defs>"
              "<path pathLength='1' class='traco' style='animation-delay:.9s' filter='url(#rbl)' fill='none' "
              "stroke='#1C1915' stroke-width='3.6' stroke-linecap='round' d='M6,8 C120,3 280,2 394,7'/>"
              "<path pathLength='1' class='traco' style='animation-delay:1.25s' filter='url(#rbl)' fill='none' "
              "stroke='#1C1915' stroke-width='3' stroke-linecap='round' d='M44,19 C150,14 280,14 356,17'/></svg>")
RABISCO = ("<defs><filter id='rb' x='-5%' y='-5%' width='110%' height='110%'><feTurbulence type='fractalNoise' "
           "baseFrequency='0.035' numOctaves='2' seed='7' result='r'/><feDisplacementMap in='SourceGraphic' in2='r' "
           "scale='2.2' xChannelSelector='R' yChannelSelector='G'/></filter></defs>")


def literal(texto: str) -> str:
    return '"' + texto.replace('"', '""') + '"'


# ---------------------------------------------------------------------------------------------------- contas
def contas():
    c = G.conta
    c("T01 · com UF", "1 quando o filtro de UF da casca está ativo (a tela mostra a UF), 0 no Brasil.",
      "INT ( ISCROSSFILTERED ( 'UF' ) )", "0")
    c("T01 · recorte", "Nome do recorte: Brasil ou o nome da UF escolhida no filtro.",
      'IF ( [T01 · com UF] = 1, SELECTEDVALUE ( \'UF\'[Nome], "as UFs escolhidas" ), "Brasil" )', "texto")
    c("T01 · válidos", "Votos válidos do 1º turno de 2026 no recorte (com o exterior no Brasil).",
      f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026 )", "#,0", "paginas[1].validos = 119.300.788")
    for nome, num, orac in (("Flávio", 22, "56.104.503"), ("Lula", 13, "53.879.538")):
        c(f"T01 · {nome} votos", f"Votos de {nome} (número {num}) no 1º turno de 2026, no recorte.",
          f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026, {CU}[Número] = {num} )", "#,0",
          f"paginas[1].candidatos › {nome} = {orac}")
        c(f"T01 · {nome} %", f"Parcela de {nome} nos votos válidos de 2026 (0–1).",
          f"DIVIDE ( [T01 · {nome} votos], [T01 · válidos] )", "0.0%")
    c("T01 · diferença", "Diferença de votos entre Flávio e Lula em 2026, sem sinal.",
      "ABS ( [T01 · Flávio votos] - [T01 · Lula votos] )", "#,0", "paginas[1].diferenca.votos = 2.224.965")
    c("T01 · diferença em p.p.", "Diferença entre os percentuais de Flávio e Lula, em pontos percentuais, sem sinal.",
      "ABS ( [T01 · Flávio %] - [T01 · Lula %] ) * 100", "0.0", "paginas[1].diferenca.pp_txt = 1,9 p.p.")
    c("T01 · vencedor", "Quem teve mais votos no recorte: Flávio, Lula ou empate.", dax("""
        VAR _f = [T01 · Flávio votos]
        VAR _l = [T01 · Lula votos]
        RETURN
            SWITCH ( TRUE (), _f > _l, "Flávio", _l > _f, "Lula", "empate" )
        """), "texto")
    # por candidato (item da barra e da legenda: 'Candidato UF'[Candidato])
    c("T01 · votos do candidato", "Votos do candidato do item (barra/legenda) em 2026, no recorte.",
      f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026 )", "#,0")
    c("T01 · parte dos válidos", "Parcela do candidato do item nos válidos de 2026 do recorte (0–1).", dax(f"""
        DIVIDE (
            [T01 · votos do candidato],
            CALCULATE ( [T01 · válidos], REMOVEFILTERS ( {CU}[Candidato] ) )
        )
        """), "0.0%")
    todos = f"""VAR _todos =
            CALCULATETABLE (
                VALUES ( {CU}[Candidato] ),
                REMOVEFILTERS ( {CU}[Candidato] ),
                {CU}[Ano] = 2026
            )"""
    c("T01 · posição do candidato", "Colocação do candidato do item em 2026, no recorte (1 = mais votado).", dax(f"""
        VAR _v = [T01 · votos do candidato]
        {todos}
        RETURN
            IF ( _v > 0, 1 + COUNTROWS ( FILTER ( _todos, [T01 · votos do candidato] > _v ) ) )
        """), "0")
    c("T01 · início na barra", "Onde o candidato do item começa na barra dos válidos: soma das parcelas dos mais "
      "votados que ele (0–1).", dax(f"""
        VAR _v = [T01 · votos do candidato]
        {todos}
        VAR _antes = SUMX ( FILTER ( _todos, [T01 · votos do candidato] > _v ), [T01 · votos do candidato] )
        RETURN
            IF ( _v > 0, DIVIDE ( _antes, CALCULATE ( [T01 · válidos], REMOVEFILTERS ( {CU}[Candidato] ) ) ) )
        """), "0.0%")
    c("T01 · partido do candidato", "Sigla do partido do candidato do item em 2026.",
      f"CALCULATE ( SELECTEDVALUE ( {CU}[Partido] ), {CU}[Ano] = 2026 )", "texto")
    c("T01 · número do candidato", "Número de urna do candidato do item em 2026.",
      f"CALCULATE ( SELECTEDVALUE ( {CU}[Número] ), {CU}[Ano] = 2026 )", "0")
    # os demais (5º lugar em diante)
    demais = f"""VAR _lista =
            FILTER (
                ADDCOLUMNS (
                    CALCULATETABLE ( VALUES ( {CU}[Candidato] ), {CU}[Ano] = 2026 ),
                    "@v", [T01 · votos do candidato],
                    "@p", [T01 · posição do candidato]
                ),
                [@p] >= 5 && [@v] > 0
            )"""
    c("T01 · demais votos", "Votos somados dos candidatos do 5º lugar em diante, no recorte.", dax(f"""
        {demais}
        RETURN
            SUMX ( _lista, [@v] )
        """), "#,0", "paginas[1].demais.votos = 3.192.291")
    c("T01 · demais parte", "Parcela dos candidatos do 5º lugar em diante nos válidos (0–1).",
      "DIVIDE ( [T01 · demais votos], [T01 · válidos] )", "0.0%", "paginas[1].demais.pct_txt = 2,7%")
    c("T01 · demais quantidade", "Quantos candidatos ficaram do 5º lugar em diante, no recorte.", dax(f"""
        {demais}
        RETURN
            COUNTROWS ( _lista )
        """), "0", "paginas[1].demais.qtd = 8")
    c("T01 · demais nomes", "Nomes dos candidatos do 5º lugar em diante, do mais ao menos votado ('A, B e C').",
      dax(f"""
        {demais}
        VAR _n = COUNTROWS ( _lista )
        VAR _ord = ADDCOLUMNS ( _lista, "@r", RANKX ( _lista, [@v], , DESC, DENSE ) )
        RETURN
            CONCATENATEX (
                _ord,
                {CU}[Candidato] & SWITCH ( TRUE (), [@r] = _n, "", [@r] = _n - 1, " e ", ", " ),
                "",
                [@v], DESC
            )
        """), "texto", "paginas[1].demais.nomes")
    # 2022 → 2026, PT × PL (Lula nos dois anos; PL: Jair Bolsonaro em 2022, Flávio em 2026)
    c("T01 · válidos 2022", "Votos válidos do 1º turno de 2022 no recorte.",
      f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2022 )", "#,0")
    for lado, num, orac in (("PT", 13, "57.259.504"), ("PL", 22, "51.072.345")):
        c(f"T01 · {lado} 2022 votos", f"Votos do candidato do {lado} (número {num}) no 1º turno de 2022, no recorte.",
          f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2022, {CU}[Número] = {num} )", "#,0",
          f"paginas[1].de_2022_para_2026 › {lado}.de.votos = {orac}")
        c(f"T01 · {lado} 2022 %", f"Parcela do {lado} nos válidos de 2022 (0–1).",
          f"DIVIDE ( [T01 · {lado} 2022 votos], [T01 · válidos 2022] )", "0.0%")
        c(f"T01 · {lado} 2022 candidato", f"Nome de urna do candidato do {lado} em 2022.",
          f"CALCULATE ( SELECTEDVALUE ( {CU}[Candidato] ), {CU}[Ano] = 2022, {CU}[Número] = {num} )", "texto")
    c("T01 · PT variação", "Votos do PT em 2026 menos 2022, no recorte (negativo = perdeu).",
      "[T01 · Lula votos] - [T01 · PT 2022 votos]", "#,0", "paginas[1].de_2022_para_2026 › PT.variacao = −3.379.966")
    c("T01 · PL variação", "Votos do PL em 2026 menos 2022, no recorte (positivo = ganhou).",
      "[T01 · Flávio votos] - [T01 · PL 2022 votos]", "#,0", "paginas[1].de_2022_para_2026 › PL.variacao = +5.032.158")
    c("T01 · virou", "1 quando o mais votado entre PT e PL mudou de 2022 para 2026 no recorte (as linhas se cruzam).",
      dax("""
        VAR _d22 = [T01 · PT 2022 votos] - [T01 · PL 2022 votos]
        VAR _d26 = [T01 · Lula votos] - [T01 · Flávio votos]
        RETURN
            IF ( SIGN ( _d22 ) <> SIGN ( _d26 ) && _d22 <> 0 && _d26 <> 0, 1, 0 )
        """), "0")
    c("T01 · distância encolheu", "1 quando a distância entre PT e PL em 2026 é menor que em 2022, no recorte.",
      dax("""
        VAR _d22 = ABS ( [T01 · PT 2022 votos] - [T01 · PL 2022 votos] )
        VAR _d26 = ABS ( [T01 · Lula votos] - [T01 · Flávio votos] )
        RETURN
            IF ( _d26 < _d22, 1, 0 )
        """), "0")


# ---------------------------------------------------------------------------------------------------- desenho
def desenho_placar():
    G.desenho("T01 · sublinhado · SVG", "Sublinhado duplo à mão embaixo do número da diferença: escala com a largura "
              "do número (preserveAspectRatio none), traço que se desenha com o tremido de caneta. Desenho fixo.",
              literal(SUBLINHADO))
    cartao = """
        VAR _card{k} =
            "<div class='cand sobe d4'><div class='rt {rt}'><span class='selo'>" & _lugar{k} & "</span></div>"
                & "<div class='rot {cls}-esc'>{rot}</div>"
                & "<div class='v {cls}'>" & _txtV{k} & "</div>"
                & "<div class='p'><span class='pn'>" & _txtP{k} & "</span> dos votos válidos</div>"
            & "</div>\""""
    cartoes = "".join(cartao.format(k=k, rt=rt, cls=cls, rot=rot) for k, rt, cls, rot in (
        ("F", "rt-f", "flavio", "FLÁVIO BOLSONARO · PL · 22"), ("L", "rt-l", "lula", "LULA · PT · 13")))
    linha = """
            "<div class='ln'><i class='sw s{n}'></i><span class='nm'>" & @ESC({cu}[Candidato])@ & " · " & [@par]
                & "</span><span class='vv'>" & @MI([@v])@ & "</span><span class='pp'>" & @PCT([@p])@ & "</span></div>\""""
    G.desenho("T01 · Placar · HTML", "Bloco da esquerda da tela 01: a diferença (com o sublinhado à mão), a manchete, o "
              "duelo Flávio × Lula (o mais votado à esquerda) e a legenda dos outros candidatos. Só lê as contas "
              "'T01 · …'.", dax(f"""
        -- 1 · Leituras
        VAR _comUF = [T01 · com UF]
        VAR _recorte = [T01 · recorte]
        VAR _val = [T01 · válidos]
        VAR _fv = [T01 · Flávio votos]
        VAR _lv = [T01 · Lula votos]
        VAR _fp = [T01 · Flávio %]
        VAR _lp = [T01 · Lula %]
        VAR _dif = [T01 · diferença]
        VAR _difpp = [T01 · diferença em p.p.]
        VAR _venc = [T01 · vencedor]
        VAR _dv = [T01 · demais votos]
        VAR _dp = [T01 · demais parte]
        VAR _dq = [T01 · demais quantidade]
        VAR _dn = [T01 · demais nomes]
        VAR _lista =
            ADDCOLUMNS (
                VALUES ( {CU}[Candidato] ),
                "@v", [T01 · votos do candidato],
                "@p", [T01 · parte dos válidos],
                "@pos", [T01 · posição do candidato],
                "@par", [T01 · partido do candidato]
            )
        VAR _c3 = FILTER ( _lista, [@pos] = 3 ) /* lista */
        VAR _c4 = FILTER ( _lista, [@pos] = 4 ) /* lista */
        -- 2 · Textos
        VAR _txtDif = @MI(_dif)@
        VAR _txtDifCheio = @INT(_dif)@
        VAR _txtDifPP = FORMAT ( _difpp, "0.0" )
        VAR _txtVal = @INT(_val)@
        VAR _txtRec = @ESC(_recorte)@
        VAR _txtVF = @MI(_fv)@
        VAR _txtVL = @MI(_lv)@
        VAR _txtPF = @PCT(_fp)@
        VAR _txtPL = @PCT(_lp)@
        VAR _txtDV = @MI(_dv)@
        VAR _txtDP = @PCT(_dp)@
        VAR _ganhou = IF ( _venc = "Lula", "Lula", "Flávio" )
        VAR _perdeu = IF ( _venc = "Lula", "Flávio", "Lula" )
        VAR _manchete =
            IF (
                _venc = "empate",
                "Flávio e Lula empataram",
                _ganhou & " terminou " & _txtDifCheio & " votos à frente de " & _perdeu
            )
        VAR _pontos = IF ( _difpp < 2, " ponto percentual", " pontos percentuais" )
        VAR _ext = IF ( _comUF = 1, "", ", com o exterior" )
        VAR _detalhe = _txtDifPP & _pontos & " de vantagem, entre " & _txtVal & " votos válidos" & _ext
        VAR _sobDif = "A diferença · " & _txtRec
        VAR _lugarF = IF ( _venc = "Lula", "2º", "1º" )
        VAR _lugarL = IF ( _venc = "Lula", "1º", "2º" )
        VAR _txtOutros = IF ( _dq = 1, "Outro candidato", "Outros " & _dq )
        -- 4 · Marcação{cartoes}
        VAR _duelo = IF ( _venc = "Lula", _cardL & _cardF, _cardF & _cardL )
        VAR _linha3 =
            CONCATENATEX (
                _c3,{linha.format(n=3, cu=CU)}
            )
        VAR _linha4 =
            CONCATENATEX (
                _c4,{linha.format(n=4, cu=CU)}
            )
        VAR _linhaD =
            IF (
                _dq > 0,
                "<div class='ln dm'><i class='sw s5'></i><span class='nm'>" & _txtOutros & " · <em>" & @ESC(_dn)@
                    & "</em></span><span class='vv'>" & _txtDV & "</span><span class='pp'>" & _txtDP & "</span></div>"
            )
        VAR _html =
            "<div class='tela t1'>"
                & "<div class='sob sobe'>" & _sobDif & "</div>"
                & "<div class='dn'><span class='dnum sobe d1'>" & _txtDif & "</span>" & [T01 · sublinhado · SVG] & "</div>"
                & "<div class='mm sobe d3'><div class='man m1'>" & _manchete & "</div>"
                & "<div class='txt m2'>" & _detalhe & "</div></div>"
                & "<div class='duelo'>" & _duelo & "</div>"
                & "<div class='rot vtit sobe d6'>Votos válidos · " & _txtVal & "</div>"
                & "<div class='leg sobe d8'>" & _linha3 & _linha4 & _linhaD & "</div>"
            & "</div>"
        RETURN
            _html
        """))
    G.desenho("T01 · Placar · ALT", "Texto para leitor de tela do bloco do placar (≤ 250 caracteres).", dax("""
        -- 1 · Leituras
        VAR _rec = [T01 · recorte]
        VAR _fv = [T01 · Flávio votos]
        VAR _lv = [T01 · Lula votos]
        VAR _fp = [T01 · Flávio %]
        VAR _lp = [T01 · Lula %]
        VAR _dif = [T01 · diferença]
        -- 2 · Textos
        RETURN
            LEFT (
                "Placar do 1º turno, " & _rec & ": Flávio Bolsonaro " & @MI(_fv)@ & " (" & @PCT(_fp)@ & "), Lula "
                    & @MI(_lv)@ & " (" & @PCT(_lp)@ & "). Diferença de " & @INT(_dif)@ & " votos.",
                250
            )
        """))


def desenho_barra():
    """Uma entrada por candidato (granularidade 'Candidato UF'[Candidato]): o segmento da barra dos válidos."""
    G.desenho("T01 · Barra · HTML", "Segmento da barra dos votos válidos para o candidato da linha (uma entrada por "
              "candidato): começa onde terminam os mais votados, largura = parcela dos válidos.", dax("""
        -- 1 · Leituras
        VAR _v = [T01 · votos do candidato]
        VAR _p = [T01 · parte dos válidos]
        VAR _ini = [T01 · início na barra]
        VAR _pos = [T01 · posição do candidato]
        VAR _num = [T01 · número do candidato]
        -- 2 · Textos
        VAR _cor =
            SWITCH (
                TRUE (),
                _num = 22, "f",
                _num = 13, "l",
                _pos = 3, "s3",
                _pos = 4, "s4",
                "s5"
            )
        VAR _lado = IF ( _pos = 2, " dir", "" )
        VAR _txtP = IF ( _p >= 0.08, "<b>" & @PCT(_p)@ & "</b>", "" )
        -- 3 · Geometria (barra de 860 px)
        VAR _x = @CSS(_ini * 860)@ -- geometria
        VAR _w = @CSS(_p * 860)@ -- geometria
        VAR _atraso = MIN ( _pos + 3, 12 ) -- geometria
        -- 4 · Marcação
        RETURN
            IF (
                _v > 0,
                "<div class='tela br'><div class='sg " & _cor & _lado & " barra-x d" & _atraso
                    & "' style='left:" & _x & "px;width:" & _w & "px'>" & _txtP & "</div></div>"
            )
        """))
    G.desenho("T01 · Barra · ALT", "Texto para leitor de tela da barra dos válidos.", dax("""
        LEFT (
            "Barra dos votos válidos de " & [T01 · recorte]
                & ", um segmento por candidato, do mais ao menos votado. Passe o mouse num segmento para ver onde cada "
                & "um foi mais forte.",
            250
        )
        """))


def desenho_virada():
    G.desenho("T01 · rabisco · SVG", "Filtro do traço tremido de caneta (defs) para os SVG da tela 01. Desenho fixo.",
              literal(RABISCO))
    G.desenho("T01 · Virada · HTML", "Bloco da direita da tela 01: de 2022 para 2026, os votos do PT e do PL (duas "
              "linhas que se cruzam quando o mais votado muda). Só lê as contas 'T01 · …'; a escala é geometria.",
              dax("""
        -- 1 · Leituras
        VAR _comUF = [T01 · com UF]
        VAR _recorte = [T01 · recorte]
        VAR _pt22 = [T01 · PT 2022 votos]
        VAR _pl22 = [T01 · PL 2022 votos]
        VAR _pt26 = [T01 · Lula votos]
        VAR _pl26 = [T01 · Flávio votos]
        VAR _ptp22 = [T01 · PT 2022 %]
        VAR _plp22 = [T01 · PL 2022 %]
        VAR _ptp26 = [T01 · Lula %]
        VAR _plp26 = [T01 · Flávio %]
        VAR _dPT = [T01 · PT variação]
        VAR _dPL = [T01 · PL variação]
        VAR _nPT22 = [T01 · PT 2022 candidato]
        VAR _nPL22 = [T01 · PL 2022 candidato]
        VAR _virou = [T01 · virou]
        VAR _encolheu = [T01 · distância encolheu]
        -- 2 · Textos
        VAR _txtDPT = @MIS(_dPT)@
        VAR _txtDPL = @MIS(_dPL)@
        VAR _verboPT = IF ( _dPT < 0, " perdeu ", " ganhou " )
        VAR _verboPL = IF ( _dPL < 0, " perdeu ", " ganhou " )
        VAR _manchete = "Lula" & _verboPT & @MI(ABS ( _dPT ))@ & " de votos; o PL" & _verboPL & @MI(ABS ( _dPL ))@
        VAR _txtPT22 = @MI(_pt22)@ & " · " & @PCT(_ptp22)@
        VAR _txtPL22 = @MI(_pl22)@ & " · " & @PCT(_plp22)@
        VAR _txtPT26 = @MI(_pt26)@ & " · " & @PCT(_ptp26)@
        VAR _txtPL26 = @MI(_pl26)@ & " · " & @PCT(_plp26)@
        VAR _nomePT22 = @ESC(_nPT22)@
        VAR _nomePL22 = @ESC(_nPL22)@
        VAR _nota =
            SWITCH ( TRUE (), _virou = 1, "as linhas se cruzaram", _encolheu = 1, "a distância encolheu", "a distância cresceu" )
        VAR _rodape =
            IF ( _comUF = 1, "Votos válidos · " & @ESC(_recorte)@ & ".", "Votos válidos, com o exterior." )
                & " Em 2022, o PL concorreu com " & _nomePL22 & "."
        -- 3 · Geometria (eixos em x 175 e 545; votos de cima para baixo em y 40–520 do gráfico)
        VAR _max = MAX ( MAX ( _pt22, _pl22 ), MAX ( _pt26, _pl26 ) ) -- geometria
        VAR _min = MIN ( MIN ( _pt22, _pl22 ), MIN ( _pt26, _pl26 ) ) -- geometria
        VAR _folga = MAX ( ( _max - _min ) * 0.18, _max * 0.02 ) -- geometria
        VAR _topo = _max + _folga -- geometria
        VAR _esc = DIVIDE ( 480, _topo - ( _min - _folga ) ) -- geometria
        VAR _yPT22 = 40 + ( _topo - _pt22 ) * _esc -- geometria
        VAR _yPL22 = 40 + ( _topo - _pl22 ) * _esc -- geometria
        VAR _yPT26 = 40 + ( _topo - _pt26 ) * _esc -- geometria
        VAR _yPL26 = 40 + ( _topo - _pl26 ) * _esc -- geometria
        -- rótulos: centros a 56 px no mínimo em cada eixo; o rótulo (2 linhas) sobe 21 px
        VAR _m22 = ( _yPT22 + _yPL22 ) / 2 -- geometria
        VAR _s22 = MAX ( ABS ( _yPT22 - _yPL22 ), 56 ) / 2 * IF ( _yPT22 <= _yPL22, -1, 1 ) -- geometria
        VAR _m26 = ( _yPT26 + _yPL26 ) / 2 -- geometria
        VAR _s26 = MAX ( ABS ( _yPT26 - _yPL26 ), 56 ) / 2 * IF ( _yPT26 <= _yPL26, -1, 1 ) -- geometria
        VAR _lPT22 = @CSS(_m22 + _s22 - 21)@ -- geometria
        VAR _lPL22 = @CSS(_m22 - _s22 - 21)@ -- geometria
        VAR _lPT26 = @CSS(_m26 + _s26 - 21)@ -- geometria
        VAR _lPL26 = @CSS(_m26 - _s26 - 21)@ -- geometria
        -- a nota à mão fica embaixo (y 548), com uma seta curva até o cruzamento (ou até o vão de 2026)
        VAR _t = DIVIDE ( _yPT22 - _yPL22, ( _yPT22 - _yPL22 ) - ( _yPT26 - _yPL26 ), 0.5 ) -- geometria
        VAR _xAlvo = IF ( _virou = 1, 175 + 370 * _t, 533 ) -- geometria
        VAR _yAlvo = IF ( _virou = 1, _yPT22 + ( _yPT26 - _yPT22 ) * _t + 14, ( _yPT26 + _yPL26 ) / 2 ) -- geometria
        VAR _seta =
            "M452,548 C" & @CSS(( 452 + _xAlvo ) / 2 + 30)@ & ",548 " & @CSS(_xAlvo + 6)@ & ","
                & @CSS(( 548 + _yAlvo ) / 2 + 30)@ & " " & @CSS(_xAlvo)@ & "," & @CSS(_yAlvo + 6)@ -- geometria
        VAR _ponta =
            "M" & @CSS(_xAlvo - 8)@ & "," & @CSS(_yAlvo + 18)@ & " L" & @CSS(_xAlvo)@ & "," & @CSS(_yAlvo + 6)@
                & " L" & @CSS(_xAlvo + 9)@ & "," & @CSS(_yAlvo + 16)@ -- geometria
        -- deltas a 30% de cada linha (longe do cruzamento), por fora do par
        VAR _mPT = _yPT22 + ( _yPT26 - _yPT22 ) * 0.3 -- geometria
        VAR _mPL = _yPL22 + ( _yPL26 - _yPL22 ) * 0.3 -- geometria
        VAR _inclPT = ABS ( _yPT26 - _yPT22 ) / 370 * 75 -- geometria
        VAR _inclPL = ABS ( _yPL26 - _yPL22 ) / 370 * 75 -- geometria
        VAR _yDPT = @CSS(_mPT + IF ( _mPT <= _mPL, -38 - _inclPT, 10 + _inclPT ))@ -- geometria
        VAR _yDPL = @CSS(_mPL + IF ( _mPL < _mPT, -38 - _inclPL, 10 + _inclPL ))@ -- geometria
        VAR _cPT22 = @CSS(_yPT22)@ -- geometria
        VAR _cPL22 = @CSS(_yPL22)@ -- geometria
        VAR _cPT26 = @CSS(_yPT26)@ -- geometria
        VAR _cPL26 = @CSS(_yPL26)@ -- geometria
        -- 4 · Marcação
        VAR _ponto = "' r='9' class='brota d6'/>"
        VAR _svg =
            "<svg class='sl' width='720' height='600' viewBox='0 0 720 600'>" & [T01 · rabisco · SVG]
                & "<line x1='175' y1='10' x2='175' y2='590' class='eixo'/>"
                & "<line x1='545' y1='10' x2='545' y2='590' class='eixo'/>"
                & "<path pathLength='1' class='lpl traco d3' filter='url(#rb)' d='M175," & _cPL22 & " L545," & _cPL26 & "'/>"
                & "<path pathLength='1' class='lpt traco d3' filter='url(#rb)' d='M175," & _cPT22 & " L545," & _cPT26 & "'/>"
                & "<circle cx='175' cy='" & _cPL22 & "' fill='#2B5797" & _ponto
                & "<circle cx='175' cy='" & _cPT22 & "' fill='#B8322A" & _ponto
                & "<circle cx='545' cy='" & _cPL26 & "' fill='#2B5797" & _ponto
                & "<circle cx='545' cy='" & _cPT26 & "' fill='#B8322A" & _ponto
                & "<path pathLength='1' class='seta traco d14' filter='url(#rb)' d='" & _seta & "'/>"
                & "<path pathLength='1' class='seta traco-rapido d16' d='" & _ponta & "'/>"
            & "</svg>"
        VAR _rotulos =
            "<div class='rs e sobe d7' style='top:" & _lPT22 & "px'><b class='lula-esc'>" & _nomePT22 & "</b>" & _txtPT22 & "</div>"
                & "<div class='rs e sobe d7' style='top:" & _lPL22 & "px'><b class='flavio-esc'>" & _nomePL22 & "</b>" & _txtPL22 & "</div>"
                & "<div class='rs d sobe d9' style='top:" & _lPT26 & "px'><b class='lula-esc'>Lula</b>" & _txtPT26 & "</div>"
                & "<div class='rs d sobe d9' style='top:" & _lPL26 & "px'><b class='flavio-esc'>Flávio Bolsonaro</b>" & _txtPL26 & "</div>"
                & "<div class='dl lula-esc sobe d8' style='top:" & _yDPT & "px'>" & _txtDPT & "</div>"
                & "<div class='dl flavio-esc sobe d8' style='top:" & _yDPL & "px'>" & _txtDPL & "</div>"
                & "<div class='mao anot entra d12'>" & _nota & "</div>"
        VAR _html =
            "<div class='tela t1v'>"
                & "<div class='sob sobe'>De 2022 para 2026 · votos no 1º turno</div>"
                & "<div class='man sobe d1'>" & _manchete & "</div>"
                & "<div class='grafico'>" & _svg & _rotulos
                    & "<div class='ano a1'>2022</div><div class='ano a2'>2026</div>"
                & "</div>"
                & "<div class='nota pe'>" & _rodape & "</div>"
            & "</div>"
        RETURN
            _html
        """))
    G.desenho("T01 · Virada · ALT", "Texto para leitor de tela do bloco de 2022 para 2026.", dax("""
        -- 1 · Leituras
        VAR _rec = [T01 · recorte]
        VAR _pt22 = [T01 · PT 2022 votos]
        VAR _pt26 = [T01 · Lula votos]
        VAR _pl22 = [T01 · PL 2022 votos]
        VAR _pl26 = [T01 · Flávio votos]
        -- 2 · Textos
        RETURN
            LEFT (
                "De 2022 para 2026, em " & _rec & ": Lula foi de " & @MI(_pt22)@ & " para " & @MI(_pt26)@
                    & " votos; o PL foi de " & @MI(_pl22)@ & " para " & @MI(_pl26)@ & ".",
                250
            )
        """))


def tooltip_candidato():
    """Dossiê do candidato (passar o mouse num segmento da barra): onde ele foi mais forte e mais fraco no Brasil e
    em quantas UFs ficou em 1º — a camada que a tela não mostra."""
    c = G.conta
    c("T01 · % do candidato na UF", "Parcela do candidato do item nos válidos de 2026 da UF da linha (0–1); vazio no "
      "exterior. Base das contas do dossiê.", dax(f"""
        IF (
            SELECTEDVALUE ( 'UF'[Tipo] ) = "UF",
            DIVIDE (
                [T01 · votos do candidato],
                CALCULATE ( [T01 · votos do candidato], REMOVEFILTERS ( {CU}[Candidato] ) )
            )
        )
        """), "0.0%")
    ufs = """VAR _ufs =
            ADDCOLUMNS (
                CALCULATETABLE ( VALUES ( 'UF'[Nome] ), REMOVEFILTERS ( 'UF' ), 'UF'[Tipo] = "UF" ),
                "@p", [T01 · % do candidato na UF]
            )"""
    for qual, ordem, orac in (("mais forte", "DESC", "Flávio: Roraima 71,1%"), ("mais fraca", "ASC", "Flávio: Piauí 24,1%")):
        c(f"T01 · UF {qual} do candidato", f"UF (no Brasil todo, sem o filtro) onde o candidato do item teve a "
          f"{'maior' if ordem == 'DESC' else 'menor'} parcela dos válidos.", dax(f"""
            {ufs}
            RETURN
                MAXX ( TOPN ( 1, _ufs, [@p], {ordem}, 'UF'[Nome], ASC ), 'UF'[Nome] )
            """), "texto", orac)
        c(f"T01 · % na UF {qual} do candidato", f"Parcela dos válidos do candidato do item na UF {qual} (0–1).",
          dax(f"""
            {ufs}
            RETURN
                {'MAXX' if ordem == 'DESC' else 'MINX'} ( _ufs, [@p] )
            """), "0.0%")
    c("T01 · UFs em 1º do candidato", "Em quantas das 27 UFs o candidato do item foi o mais votado (no Brasil todo, sem "
      "o filtro).", dax(f"""
        VAR _cand = SELECTEDVALUE ( {CU}[Candidato] )
        VAR _ufs =
            CALCULATETABLE ( VALUES ( 'UF'[Nome] ), REMOVEFILTERS ( 'UF' ), 'UF'[Tipo] = "UF" )
        VAR _lider =
            ADDCOLUMNS (
                _ufs,
                "@lider",
                    CALCULATE (
                        MAXX (
                            TOPN (
                                1,
                                ADDCOLUMNS (
                                    CALCULATETABLE ( VALUES ( {CU}[Candidato] ), REMOVEFILTERS ( {CU}[Candidato] ) ),
                                    "@v", [T01 · votos do candidato]
                                ),
                                [@v], DESC
                            ),
                            {CU}[Candidato]
                        )
                    )
            )
        RETURN
            IF ( NOT ISBLANK ( _cand ), COUNTROWS ( FILTER ( _lider, [@lider] = _cand ) ) + 0 )
        """), "0", "Flávio 18 · Lula 9 (soma 27)")
    G.desenho("T01 · Tooltip candidato · HTML", "Dossiê do candidato da barra (ficha com clipe): onde foi mais forte e "
              "mais fraco no Brasil e em quantas UFs ficou em 1º. Só lê contas 'T01 · …'.", dax(f"""
        -- 1 · Leituras
        VAR _nome = SELECTEDVALUE ( {CU}[Candidato] )
        VAR _num = [T01 · número do candidato]
        VAR _par = [T01 · partido do candidato]
        VAR _pos = [T01 · posição do candidato]
        VAR _ufF = [T01 · UF mais forte do candidato]
        VAR _pF = [T01 · % na UF mais forte do candidato]
        VAR _ufR = [T01 · UF mais fraca do candidato]
        VAR _pR = [T01 · % na UF mais fraca do candidato]
        VAR _n1 = [T01 · UFs em 1º do candidato]
        VAR _comUF = [T01 · com UF]
        -- 2 · Textos
        VAR _cor = SWITCH ( _num, 22, "flavio", 13, "lula", "neutro" )
        VAR _ic = SWITCH ( _num, 22, "urna-azul", 13, "urna-vermelho", "urna-tinta" )
        VAR _txtNome = @ESC(_nome)@
        VAR _txtPar = @ESC(_par)@ & " · " & _num
        VAR _txtPF = @PCT(_pF)@
        VAR _txtPR = @PCT(_pR)@
        VAR _onde = IF ( _comUF = 1, _pos & "º lugar nesta UF", _pos & "º lugar no Brasil" )
        VAR _nota =
            IF (
                _n1 > 0,
                "1º lugar em " & _n1 & IF ( _n1 = 1, " UF", " UFs" ),
                _onde
            )
        -- 4 · Marcação
        VAR _css =
            "<style>"
                & ".tt1{{position:fixed;inset:0;background:var(--papel)}}"
                & ".tt1 .ficha{{position:absolute;left:16px;top:18px;right:16px;bottom:16px;background:var(--branco);"
                & "border:1.5px solid var(--areia);box-shadow:3px 4px 0 rgba(28,25,21,.08)}}"
                & ".tt1 .clipe{{position:absolute;right:34px;top:-12px;width:34px;transform:rotate(8deg)}}"
                & ".tt1 .ic{{position:absolute;left:22px;top:20px;width:46px}}"
                & ".tt1 .cab{{position:absolute;left:82px;top:20px;right:70px}}"
                & ".tt1 .nm{{font-size:24px;font-weight:700;line-height:1.1;letter-spacing:-.01em}}"
                & ".tt1 .pt{{margin-top:6px}}"
                & ".tt1 .lin{{position:absolute;left:22px;right:22px;display:flex;justify-content:space-between;"
                & "align-items:baseline;border-top:1px dashed var(--areia);padding-top:12px}}"
                & ".tt1 .lin .rot{{white-space:nowrap}}.tt1 .lin .v{{text-align:right;font-size:16px}}"
                & ".tt1 .lin .v b{{font-size:24px;font-weight:700;margin-left:8px}}"
                & ".tt1 .l1{{top:108px}}.tt1 .l2{{top:164px}}"
                & ".tt1 .mao{{position:absolute;left:22px;bottom:12px;font-size:28px}}"
                & ".tt1 .neutro{{color:var(--tinta)}}"
            & "</style>"
        VAR _html =
            _css
                & "<div class='tt1'><div class='ficha'>"
                & "<img class='clipe' alt='' src='{URL}/arte/dossie/clipe-tinta.png'/>"
                & "<img class='ic entra' alt='' src='{URL}/arte/icones/" & _ic & ".png'/>"
                & "<div class='cab sobe'><div class='nm " & _cor & "'>" & _txtNome & "</div>"
                & "<div class='rot pt'>" & _txtPar & " · no Brasil</div></div>"
                & "<div class='lin l1 sobe d2'><span class='rot'>Mais forte em</span>"
                & "<span class='v'>" & @ESC(_ufF)@ & "<b class='" & _cor & "'>" & _txtPF & "</b></span></div>"
                & "<div class='lin l2 sobe d3'><span class='rot'>Mais fraco em</span>"
                & "<span class='v'>" & @ESC(_ufR)@ & "<b>" & _txtPR & "</b></span></div>"
                & "<div class='mao " & _cor & " entra d5'>" & _nota & "</div>"
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _nome ), _html )
        """))
    G.desenho("T01 · Tooltip candidato · ALT", "Texto para leitor de tela do dossiê do candidato.", dax(f"""
        -- 1 · Leituras
        VAR _nome = SELECTEDVALUE ( {CU}[Candidato] )
        VAR _ufF = [T01 · UF mais forte do candidato]
        VAR _pF = [T01 · % na UF mais forte do candidato]
        VAR _ufR = [T01 · UF mais fraca do candidato]
        VAR _pR = [T01 · % na UF mais fraca do candidato]
        -- 2 · Textos
        RETURN
            LEFT (
                _nome & ": mais forte em " & _ufF & " (" & @PCT(_pF)@ & "), mais fraco em " & _ufR & " ("
                    & @PCT(_pR)@ & ").",
                250
            )
        """))


# A escala da virada (as mesmas linhas do bloco 3 de 'T01 · Virada · HTML'; main() confere que continuam iguais):
# os alvos dos pontos ficam exatamente sobre as bolinhas desenhadas.
ESCALA_VIRADA = """VAR _max = MAX ( MAX ( _pt22, _pl22 ), MAX ( _pt26, _pl26 ) ) -- geometria
        VAR _min = MIN ( MIN ( _pt22, _pl22 ), MIN ( _pt26, _pl26 ) ) -- geometria
        VAR _folga = MAX ( ( _max - _min ) * 0.18, _max * 0.02 ) -- geometria
        VAR _topo = _max + _folga -- geometria
        VAR _esc = DIVIDE ( 480, _topo - ( _min - _folga ) ) -- geometria"""
MA = "'Município ano'"
MU = "'Município'"
GRUPO = "REMOVEFILTERS ( 'UF'[Região], 'UF'[RegiaoOrdem] ), REMOVEFILTERS ( 'Município'[Porte], 'Município'[PorteOrdem] )"


def pontos_virada():
    """Os quatro pontos da virada (ano × candidato) ganham grão: um HTML de alvos por cima do desenho (grão 'Candidato
    UF'[Ano] × [Número], só PT e PL), com o dossiê do ponto: de onde vieram os votos daquele candidato naquele ano —
    por região no Brasil, por tamanho de cidade numa UF —, o % dele em cada grupo em 2022 e em 2026 e a nota à mão com
    a maior perda/ganho (2026) ou a base mais forte (2022). A camada nova é composição × tempo; o total do ponto, que já
    está na tela, não se repete."""
    c = G.conta
    c("T01 · ponto · ano", "Ano do ponto da virada (linha do grão 'Candidato UF'[Ano]).",
      f"SELECTEDVALUE ( {CU}[Ano] )", "0")
    c("T01 · ponto · número", "Número do candidato do ponto da virada (13 = PT, 22 = PL).",
      f"SELECTEDVALUE ( {CU}[Número] )", "0")
    c("T01 · ponto · candidato", "Nome de urna do candidato do ponto da virada.",
      f"SELECTEDVALUE ( {CU}[Candidato] )", "texto")
    c("T01 · ponto · partido", "Sigla do partido do candidato do ponto da virada.",
      f"SELECTEDVALUE ( {CU}[Partido] )", "texto")
    for nome, ano, desc in (("votos no grupo", "_a", "no ano do ponto"), ("votos no grupo em 2022", "2022", "em 2022"),
                            ("votos no grupo em 2026", "2026", "em 2026")):
        c(f"T01 · ponto · {nome}", f"Votos do partido do ponto (PT ou PL) {desc}, somados nos municípios do contexto "
          "(sem o exterior): a região ou o porte da linha do dossiê.", dax(f"""
            VAR _a = [T01 · ponto · ano]
            VAR _n = [T01 · ponto · número]
            RETURN
                SWITCH (
                    _n,
                    13, CALCULATE ( SUM ( {MA}[VotosPT] ), {MA}[Ano] = {ano} ),
                    22, CALCULATE ( SUM ( {MA}[VotosAdversario] ), {MA}[Ano] = {ano} )
                )
            """), "#,0")
    c("T01 · ponto · parte do grupo", "Parcela dos votos do partido do ponto, no ano do ponto, que veio da região ou do "
      "porte da linha (0–1). Tira só as colunas do grupo.", dax(f"""
        DIVIDE ( [T01 · ponto · votos no grupo], CALCULATE ( [T01 · ponto · votos no grupo], {GRUPO} ) )
        """), "0%", "Lula 2026 › Nordeste 40% (paginas[3].regioes)")
    for ano in (2022, 2026):
        c(f"T01 · ponto · % no grupo em {ano}", f"Parcela do partido do ponto nos válidos de {ano} da região ou do "
          "porte da linha (0–1).", dax(f"""
            DIVIDE ( [T01 · ponto · votos no grupo em {ano}], CALCULATE ( SUM ( {MA}[Validos] ), {MA}[Ano] = {ano} ) )
            """), "0.0%", "Lula 2026 › Nordeste 63,8% (paginas[3].regioes)" if ano == 2026 else None)
    c("T01 · ponto · variação no grupo", "Votos do partido do ponto em 2026 menos 2022 na região ou no porte da linha.",
      "[T01 · ponto · votos no grupo em 2026] - [T01 · ponto · votos no grupo em 2022]", "#,0")
    c("T01 · ordem do porte", "Ordem do porte da linha (1 = até 10 mil habitantes), para listar do menor ao maior.",
      f"MIN ( {MU}[PorteOrdem] )", "0")
    # ---- os alvos (um por ponto, sobre a bolinha desenhada pela virada)
    G.desenho("T01 · Ponto · HTML", "Alvo do ponto da virada (uma entrada por ano × candidato, só PT e PL): um círculo "
              "transparente sobre a bolinha desenhada, com um anel no hover; abre o dossiê do ponto. A posição usa a "
              "mesma escala do bloco da virada.", dax(f"""
        -- 1 · Leituras
        VAR _a = [T01 · ponto · ano]
        VAR _n = [T01 · ponto · número]
        VAR _pt22 = [T01 · PT 2022 votos]
        VAR _pl22 = [T01 · PL 2022 votos]
        VAR _pt26 = [T01 · Lula votos]
        VAR _pl26 = [T01 · Flávio votos]
        -- 2 · Textos
        VAR _cls = IF ( _n = 13, "lula", "flavio" )
        -- 3 · Geometria (a escala da virada; eixos em x 175 e 545; o gráfico começa em y 116 do visual)
        {ESCALA_VIRADA}
        VAR _v =
            SWITCH (
                TRUE (),
                _a = 2022 && _n = 13, _pt22,
                _a = 2022 && _n = 22, _pl22,
                _a = 2026 && _n = 13, _pt26,
                _a = 2026 && _n = 22, _pl26
            ) -- geometria
        VAR _cx = IF ( _a = 2022, 175, 545 ) -- geometria
        VAR _cy = 116 + 40 + ( _topo - _v ) * _esc -- geometria
        -- 4 · Marcação
        RETURN
            IF (
                _v > 0,
                "<div class='tela vp'><div class='alvo " & _cls & "' style='left:" & @CSS(_cx - 24)@ & "px;top:"
                    & @CSS(_cy - 24)@ & "px'></div></div>"
            )
        """))
    G.desenho("T01 · Ponto · ALT", "Texto para leitor de tela dos alvos da virada.", dax("""
        "Pontos da virada: Lula e o PL em 2022 e em 2026. Passe o mouse num ponto para ver de onde vieram os votos "
            & "daquele ano."
        """))
    # ---- o dossiê do ponto
    G.desenho("T01 · Tooltip ponto · HTML", "Dossiê do ponto da virada (ficha com clipe): de onde vieram os votos do "
              "candidato naquele ano — por região no Brasil, por tamanho de cidade numa UF —, com o % dele em cada "
              "grupo em 2022 e em 2026 e a nota à mão com a maior perda ou ganho (2026) ou a base mais forte (2022). Só "
              "lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _a = [T01 · ponto · ano]
        VAR _n = [T01 · ponto · número]
        VAR _nome = [T01 · ponto · candidato]
        VAR _par = [T01 · ponto · partido]
        VAR _comUF = [T01 · com UF]
        VAR _rec = [T01 · recorte]
        VAR _regs =
            TOPN (
                IF ( _comUF = 0, 10, 0 ),
                ADDCOLUMNS (
                    VALUES ( 'UF'[Região] ),
                    "@v", [T01 · ponto · votos no grupo],
                    "@p", [T01 · ponto · parte do grupo],
                    "@p22", [T01 · ponto · % no grupo em 2022],
                    "@p26", [T01 · ponto · % no grupo em 2026],
                    "@d", [T01 · ponto · variação no grupo]
                ),
                [@v], DESC
            )
        VAR _portes =
            TOPN (
                IF ( _comUF = 1, 10, 0 ),
                ADDCOLUMNS (
                    VALUES ( {MU}[Porte] ),
                    "@v", [T01 · ponto · votos no grupo],
                    "@p", [T01 · ponto · parte do grupo],
                    "@p22", [T01 · ponto · % no grupo em 2022],
                    "@p26", [T01 · ponto · % no grupo em 2026],
                    "@d", [T01 · ponto · variação no grupo],
                    "@o", [T01 · ordem do porte]
                ),
                [@v], DESC
            )
        VAR _lista =
            UNION (
                SELECTCOLUMNS (
                    FILTER ( _regs, [@v] > 0 ), /* lista */
                    "@g", 'UF'[Região], "@v", [@v], "@p", [@p], "@p22", [@p22], "@p26", [@p26], "@d", [@d], "@o", - [@v]
                ),
                SELECTCOLUMNS (
                    FILTER ( _portes, [@v] > 0 && LEN ( {MU}[Porte] ) > 0 ), /* lista */
                    "@g", {MU}[Porte], "@v", [@v], "@p", [@p], "@p22", [@p22], "@p26", [@p26], "@d", [@d], "@o", [@o]
                )
            )
        VAR _pmax = MAXX ( _lista, [@p] ) /* lista */
        VAR _topD = TOPN ( 1, _lista, ABS ( [@d] ), DESC, [@g], ASC ) /* lista */
        VAR _topP = TOPN ( 1, _lista, IF ( _a = 2022, [@p22], [@p26] ), DESC, [@g], ASC ) /* lista */
        VAR _gD = MAXX ( _topD, [@g] ) /* lista */
        VAR _dD = MAXX ( _topD, [@d] ) /* lista */
        VAR _gP = MAXX ( _topP, [@g] ) /* lista */
        -- 2 · Textos
        VAR _cls = IF ( _n = 13, "lula", "flavio" )
        VAR _ic = IF ( _n = 13, "barras-vermelho", "barras-azul" )
        VAR _txtNome = @ESC(_nome)@ & " · " & _a
        VAR _sub = @ESC(_par)@ & " · " & _n & " · " & IF ( _comUF = 1, @ESC(_rec)@, "Brasil, sem o exterior" )
        VAR _rotG = IF ( _comUF = 1, "cidades de", "região" )
        VAR _nota =
            IF (
                _a = 2026,
                IF ( _dD < 0, "maior perda: ", "maior ganho: " ) & @ESC(_gD)@ & ", " & @MIS(_dD)@,
                "base mais forte: " & @ESC(_gP)@
            )
        VAR _on22 = IF ( _a = 2022, " on", "" )
        VAR _on26 = IF ( _a = 2026, " on", "" )
        -- 3 · Geometria (barra do peso em até 84 px; linhas de 30 px)
        VAR _linhas =
            CONCATENATEX (
                _lista,
                VAR _w = @CSS(DIVIDE ( [@p], _pmax ) * 84)@ -- geometria
                RETURN
                    "<div class='ln'><span class='g'>" & @ESC([@g])@ & "</span><span class='br'><i class='barra-x "
                        & _cls & "-bg' style='width:" & _w & "px'></i><b>" & @PCT0([@p])@ & "</b></span>"
                        & "<span class='pc" & _on22 & "'>" & @PCT([@p22])@ & "</span>"
                        & "<span class='pc" & _on26 & "'>" & @PCT([@p26])@ & "</span></div>",
                "",
                [@o], ASC
            )
        -- 4 · Marcação
        RETURN
            IF (
                NOT ISBLANK ( _nome ) && NOT ISEMPTY ( _lista ),
                "<div class='tp'><div class='ficha'>"
                    & "<img class='ico entra' alt='' src='{URL}/arte/icones/" & _ic & ".png'/>"
                    & "<div class='cab sobe'><div class='nm " & _cls & "'>" & _txtNome & "</div>"
                    & "<div class='sub'>" & _sub & "</div></div>"
                    & "<div class='hd sobe d1'><span class='g'>" & _rotG & "</span><span class='br'>peso nos votos</span>"
                    & "<span class='pc" & _on22 & "'>% 2022</span><span class='pc" & _on26 & "'>% 2026</span></div>"
                    & "<div class='lista sobe d2'>" & _linhas & "</div>"
                    & "<div class='mao " & _cls & "-esc entra d6'>" & _nota & "</div>"
                & "</div></div>"
            )
        """))
    G.desenho("T01 · Tooltip ponto · ALT", "Texto para leitor de tela do dossiê do ponto da virada.", dax("""
        LEFT (
            [T01 · ponto · candidato] & " em " & [T01 · ponto · ano] & ": de onde vieram os votos, por "
                & IF ( [T01 · com UF] = 1, "tamanho de cidade", "região" ) & ", e o % dele em cada grupo em 2022 e 2026.",
            250
        )
        """))


def main() -> int:
    contas()
    desenho_placar()
    desenho_barra()
    desenho_virada()
    tooltip_candidato()
    pontos_virada()
    virada = (G.raiz / "Desenho" / "T01 · Virada · HTML.dax").read_text(encoding="utf-8")
    if "\n".join(l.strip() for l in ESCALA_VIRADA.splitlines()) not in virada:
        raise SystemExit("a escala dos alvos (ESCALA_VIRADA) não é mais a da virada: alinhe as duas")
    apagados = G.limpar()
    print(G.resumo(), "· apagados:", [p.name for p in apagados])
    return 0


if __name__ == "__main__":
    sys.exit(main())
