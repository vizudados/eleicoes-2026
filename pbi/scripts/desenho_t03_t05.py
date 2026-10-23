# -*- coding: utf-8 -*-
"""desenho_t03_t05 — telas 03 (Onde estão os votos de Lula?) e 05 (… de Flávio?): MESMO gerador, o lado é parâmetro
(neutralidade). Dono: agente das telas 01–06.

    python -I -X utf8 pbi/scripts/desenho_t03_t05.py    # grava pbi/dax/T03 Lula/…, pbi/dax/T05 Flávio/… e os specs

A tela: à esquerda, a resposta (o % no recorte, os votos, em quantos municípios ficou à frente, o que mudou desde 2022),
de onde vêm os votos (regiões no Brasil; as cidades que mais deram votos numa UF) e onde foi mais forte e mais fraco.
À direita, a protagonista: o mapa de pontos (Deneb), um ponto por município, tamanho pelos votos do candidato, cor pela
margem dele (o tom do candidato onde ele ficou à frente; areia onde ficou atrás). O mapa se desenha: o contorno das UFs
em traço, depois os pontos brotam em onda a partir do centro de gravidade dos votos do candidato. Com UF, o mapa
enquadra a UF. Passar o mouse num ponto abre o dossiê do município (ficha pautada presa com fita).

Também gera o spec do mapa de abstenção da tela 06 (spec_mapa com modo "abstencao").
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from desenho_t01_t06_comum import PBI, URL_MIDIA, Gravador, dax  # noqa: E402

CU = "'Candidato UF'"
MA = "'Município ano'"
MU = "'Município'"

LADOS = {
    "T03": dict(pasta="T03 Lula", cand="Lula", completo="Luiz Inácio Lula da Silva", sigla="PT", numero=13,
                outro="Flávio", outro_num=22, col="VotosPT", col_outro="VotosAdversario", cls="lula",
                cores=("#E9B5AA", "#B8322A", "#7A1E19"), tooltip="ttT03Municipio", ordem_tt=130, tom="vermelho",
                notas=("seguiu com Lula", "virou para Flávio", "virou para Lula", "seguiu com o PL")),
    "T05": dict(pasta="T05 Flávio", cand="Flávio", completo="Flávio Bolsonaro", sigla="PL", numero=22,
                outro="Lula", outro_num=13, col="VotosAdversario", col_outro="VotosPT", cls="flavio",
                cores=("#B9C9E2", "#2B5797", "#16305A"), tooltip="ttT05Municipio", ordem_tt=150, tom="azul",
                notas=("seguiu com o PL", "virou para Lula", "virou para Flávio", "seguiu com Lula")),
}
RESUMO = (150, 140, 620, 860)
MAPA = (800, 140, 970, 800)
LEGENDA = (800, 946, 970, 54)
TT_W, TT_H = 460, 340


# ---------------------------------------------------------------------------------------------------- contas
def contas(P: str, L: dict, G: Gravador) -> None:
    c = G.conta
    n, o, col, colo = L["numero"], L["outro_num"], L["col"], L["col_outro"]
    c(f"{P} · com UF", "1 quando o filtro de UF da casca está ativo (a tela mostra a UF), 0 no Brasil.",
      "INT ( ISCROSSFILTERED ( 'UF' ) )", "0")
    c(f"{P} · recorte", "Nome do recorte: Brasil ou o nome da UF escolhida no filtro.",
      f'IF ( [{P} · com UF] = 1, SELECTEDVALUE ( \'UF\'[Nome], "UFs escolhidas" ), "Brasil" )', "texto")
    # resultado oficial do recorte ('Candidato UF', com o exterior no Brasil)
    c(f"{P} · votos", f"Votos de {L['cand']} (número {n}) no 1º turno de 2026, no recorte (com o exterior no Brasil).",
      f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026, {CU}[Número] = {n} )", "#,0",
      f"paginas[{P[2]}].votos")
    c(f"{P} · válidos", "Votos válidos do 1º turno de 2026 no recorte.",
      f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026 )", "#,0")
    c(f"{P} · %", f"Parcela de {L['cand']} nos válidos de 2026 do recorte (0–1); na linha de uma UF, o % da UF.",
      f"DIVIDE ( [{P} · votos], [{P} · válidos] )", "0.0%", f"paginas[{P[2]}].pct")
    c(f"{P} · posição", f"Colocação de {L['cand']} no 1º turno de 2026, no recorte.", dax(f"""
        VAR _v = [{P} · votos]
        VAR _todos =
            ADDCOLUMNS (
                CALCULATETABLE ( VALUES ( {CU}[Número] ), {CU}[Ano] = 2026 ),
                "@v", CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026 )
            )
        RETURN
            1 + COUNTROWS ( FILTER ( _todos, [@v] > _v ) )
        """), "0", f"paginas[{P[2]}].posicao_txt")
    c(f"{P} · votos 2022", f"Votos do candidato do {L['sigla']} no 1º turno de 2022, no recorte.",
      f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2022, {CU}[Número] = {n} )", "#,0",
      f"paginas[{P[2]}].comparacao_2022.votos_2022_txt")
    c(f"{P} · válidos 2022", "Votos válidos do 1º turno de 2022 no recorte.",
      f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2022 )", "#,0")
    c(f"{P} · % 2022", f"Parcela do {L['sigla']} nos válidos de 2022 do recorte (0–1).",
      f"DIVIDE ( [{P} · votos 2022], [{P} · válidos 2022] )", "0.0%", f"paginas[{P[2]}].comparacao_2022.pct_2022_txt")
    c(f"{P} · candidato 2022", f"Nome de urna do candidato do {L['sigla']} em 2022.",
      f"CALCULATE ( SELECTEDVALUE ( {CU}[Candidato] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2022, {CU}[Número] = {n} )",
      "texto")
    c(f"{P} · variação de votos", f"Votos do {L['sigla']} em 2026 menos 2022, no recorte.",
      f"[{P} · votos] - [{P} · votos 2022]", "#,0", f"paginas[{P[2]}].comparacao_2022.variacao_votos_txt")
    c(f"{P} · variação em p.p.", f"Variação do % do {L['sigla']} de 2022 para 2026, em pontos percentuais.",
      f"( [{P} · %] - [{P} · % 2022] ) * 100", "0.0", f"paginas[{P[2]}].comparacao_2022.variacao_pp_txt")
    # soma dos municípios ('Município ano', sem o exterior)
    for nome, coluna, ano, desc in (
            ("votos (municípios)", col, 2026, f"Votos de {L['cand']} em 2026 somados nos municípios do contexto"),
            ("votos do adversário (municípios)", colo, 2026, f"Votos de {L['outro']} em 2026 somados nos municípios"),
            ("válidos (municípios)", "Validos", 2026, "Votos válidos de 2026 somados nos municípios"),
            ("aptos (municípios)", "Aptos", 2026, "Eleitores aptos em 2026 somados nos municípios"),
            ("votos 2022 (municípios)", col, 2022, f"Votos do {L['sigla']} em 2022 somados nos municípios"),
            ("votos do adversário 2022 (municípios)", colo, 2022, "Votos do adversário em 2022 somados nos municípios"),
            ("válidos 2022 (municípios)", "Validos", 2022, "Votos válidos de 2022 somados nos municípios")):
        c(f"{P} · {nome}", desc + " (sem o exterior).",
          f"CALCULATE ( SUM ( {MA}[{coluna}] ), {MA}[Ano] = {ano} )", "#,0")
    c(f"{P} · % (municípios)", f"Parcela de {L['cand']} nos válidos de 2026 dos municípios do contexto (0–1).",
      f"DIVIDE ( [{P} · votos (municípios)], [{P} · válidos (municípios)] )", "0.0%")
    c(f"{P} · adversário % (municípios)", f"Parcela de {L['outro']} nos válidos de 2026 dos municípios do contexto.",
      f"DIVIDE ( [{P} · votos do adversário (municípios)], [{P} · válidos (municípios)] )", "0.0%")
    c(f"{P} · % 2022 (municípios)", f"Parcela do {L['sigla']} nos válidos de 2022 dos municípios do contexto.",
      f"DIVIDE ( [{P} · votos 2022 (municípios)], [{P} · válidos 2022 (municípios)] )", "0.0%")
    c(f"{P} · adversário % 2022 (municípios)", "Parcela do adversário nos válidos de 2022 dos municípios do contexto.",
      f"DIVIDE ( [{P} · votos do adversário 2022 (municípios)], [{P} · válidos 2022 (municípios)] )", "0.0%")
    c(f"{P} · margem", f"Margem de {L['cand']} em 2026: (votos dele − votos de {L['outro']}) ÷ válidos (−1 a 1). "
      "Cor do ponto no mapa.",
      f"DIVIDE ( [{P} · votos (municípios)] - [{P} · votos do adversário (municípios)], [{P} · válidos (municípios)] )",
      "0.0%")
    c(f"{P} · margem 2022", f"Margem do {L['sigla']} em 2022: (votos − votos do adversário) ÷ válidos (−1 a 1).",
      f"DIVIDE ( [{P} · votos 2022 (municípios)] - [{P} · votos do adversário 2022 (municípios)], "
      f"[{P} · válidos 2022 (municípios)] )", "0.0%")
    c(f"{P} · situação", "No município da linha: 1 = à frente nos dois anos · 2 = estava à frente em 2022 e ficou atrás "
      "em 2026 · 3 = virou a favor · 4 = atrás nos dois anos.", dax(f"""
        VAR _m22 = [{P} · margem 2022]
        VAR _m26 = [{P} · margem]
        RETURN
            SWITCH ( TRUE (), _m22 > 0 && _m26 > 0, 1, _m22 > 0, 2, _m26 > 0, 3, 4 )
        """), "0")
    mun = f"VALUES ( {MU}[CodIBGE] )"
    frente = f"[{P} · votos (municípios)] > [{P} · votos do adversário (municípios)]"
    c(f"{P} · municípios à frente", f"Municípios do recorte em que {L['cand']} teve mais votos que {L['outro']}.",
      f"COUNTROWS ( FILTER ( {mun}, {frente} ) ) + 0", "#,0", f"paginas[{P[2]}].municipios_a_frente")
    c(f"{P} · municípios", "Municípios do recorte com votos válidos em 2026.",
      f"COUNTROWS ( FILTER ( {mun}, [{P} · válidos (municípios)] > 0 ) )", "#,0", "5.571")
    c(f"{P} · eleitores nos municípios à frente", f"Parcela dos eleitores aptos do recorte que vivem nos municípios em "
      f"que {L['cand']} ficou à frente (0–1).", dax(f"""
        DIVIDE (
            SUMX ( FILTER ( {mun}, {frente} ), [{P} · aptos (municípios)] ),
            [{P} · aptos (municípios)]
        )
        """), "0%", f"paginas[{P[2]}].eleitores_nesses_municipios_txt")
    c(f"{P} · parte dos votos", f"Parcela dos votos de {L['cand']} (soma dos municípios do recorte) que veio da região ou "
      "do município da linha (0–1).", dax(f"""
        DIVIDE (
            [{P} · votos (municípios)],
            CALCULATE ( [{P} · votos (municípios)], REMOVEFILTERS ( 'UF'[Região] ), REMOVEFILTERS ( {MU}[Rótulo] ) )
        )
        """), "0%", f"paginas[{P[2]}].regioes[].parte_dos_votos")
    # de onde vêm os votos: a região (Brasil) ou o município (UF) que mais deu votos
    origem = f"""VAR _reg =
            ADDCOLUMNS ( VALUES ( 'UF'[Região] ), "@v", [{P} · votos (municípios)], "@p", [{P} · % (municípios)] )
        VAR _mun =
            ADDCOLUMNS (
                FILTER ( VALUES ( {MU}[Rótulo] ), [{P} · com UF] = 1 ),
                "@v", [{P} · votos (municípios)],
                "@p", [{P} · % (municípios)]
            )
        VAR _topReg = TOPN ( 1, _reg, [@v], DESC, 'UF'[Região], ASC )
        VAR _topMun = TOPN ( 1, _mun, [@v], DESC, {MU}[Rótulo], ASC )
        VAR _uf = [{P} · com UF] = 1"""
    c(f"{P} · origem principal", "Região (no Brasil) ou município (numa UF) que mais deu votos ao candidato.", dax(f"""
        {origem}
        RETURN
            IF ( _uf, MAXX ( _topMun, {MU}[Rótulo] ), MAXX ( _topReg, 'UF'[Região] ) )
        """), "texto", f"paginas[{P[2]}].regioes[0].regiao")
    c(f"{P} · origem principal parte", "Parcela dos votos do candidato que veio da origem principal (0–1).", dax(f"""
        {origem}
        RETURN
            DIVIDE ( IF ( _uf, MAXX ( _topMun, [@v] ), MAXX ( _topReg, [@v] ) ), [{P} · votos (municípios)] )
        """), "0%", f"paginas[{P[2]}].regioes[0].parte_dos_votos_txt")
    c(f"{P} · origem principal %", "Parcela do candidato nos válidos da origem principal (0–1).", dax(f"""
        {origem}
        RETURN
            IF ( _uf, MAXX ( _topMun, [@p] ), MAXX ( _topReg, [@p] ) )
        """), "0.0%", f"paginas[{P[2]}].regioes[0].pct_txt")
    # onde foi mais forte e mais fraco: UF (no Brasil) ou município (numa UF)
    lugares = f"""VAR _ufs =
            ADDCOLUMNS ( CALCULATETABLE ( VALUES ( 'UF'[Nome] ), 'UF'[Tipo] = "UF" ), "@p", [{P} · %] )
        VAR _mun =
            ADDCOLUMNS (
                FILTER ( VALUES ( {MU}[Rótulo] ), [{P} · com UF] = 1 && [{P} · válidos (municípios)] > 0 ),
                "@p", [{P} · % (municípios)]
            )
        VAR _uf = [{P} · com UF] = 1"""
    for qual, ordem, fn, orac in (("mais forte", "DESC", "MAXX", "ufs_mais_fortes[0]"),
                                  ("mais fraco", "ASC", "MINX", "uf_mais_fraca")):
        corpo_nome = f"""
        {lugares}
        RETURN
            IF (
                _uf,
                MAXX ( TOPN ( 1, _mun, [@p], {ordem}, {MU}[Rótulo], ASC ), {MU}[Rótulo] ),
                MAXX ( TOPN ( 1, _ufs, [@p], {ordem}, 'UF'[Nome], ASC ), 'UF'[Nome] )
            )
        """
        corpo_pct = f"""
        {lugares}
        RETURN
            IF ( _uf, {fn} ( _mun, [@p] ), {fn} ( _ufs, [@p] ) )
        """
        c(f"{P} · lugar {qual}", f"UF (no Brasil) ou município (numa UF) onde o candidato teve o {qual.split()[1]} % "
          "dos válidos.", dax(corpo_nome), "texto", f"paginas[{P[2]}].{orac}.nome")
        c(f"{P} · lugar {qual} %", f"% do candidato nos válidos do lugar {qual} (0–1).", dax(corpo_pct), "0.0%",
          f"paginas[{P[2]}].{orac}.pct_txt")
    grande = f"""VAR _gr =
            ADDCOLUMNS (
                CALCULATETABLE ( VALUES ( {MU}[Rótulo] ), {MU}[População] >= 100000 ),
                "@p", [{P} · % (municípios)],
                "@pop", CALCULATE ( SUM ( {MU}[População] ) )
            )
        VAR _top = TOPN ( 1, _gr, [@p], DESC, {MU}[Rótulo], ASC )"""
    c(f"{P} · cidade grande mais forte", "Entre as cidades de 100 mil habitantes ou mais do recorte, a de maior % do "
      "candidato (vazio se o recorte não tem cidade desse porte).", dax(f"""
        {grande}
        RETURN
            MAXX ( _top, {MU}[Rótulo] )
        """), "texto", f"paginas[{P[2]}].cidades_grandes_mais_fortes[0]")
    c(f"{P} · cidade grande mais forte %", "% do candidato na cidade grande mais forte (0–1).", dax(f"""
        {grande}
        RETURN
            MAXX ( _top, [@p] )
        """), "0.0%")
    c(f"{P} · cidade grande mais forte população", "População (Censo 2022) da cidade grande mais forte.", dax(f"""
        {grande}
        RETURN
            MAXX ( _top, [@pop] )
        """), "#,0")
    # dossiê do município (tooltip do mapa)
    c(f"{P} · município", "Nome (UF) do município da linha.", f"SELECTEDVALUE ( {MU}[Rótulo] )", "texto")
    c(f"{P} · região do município", "Região do município da linha.", f"SELECTEDVALUE ( {MU}[Região] )", "texto")
    c(f"{P} · população", "População (Censo 2022) do município da linha.", f"SUM ( {MU}[População] )", "#,0")


# ---------------------------------------------------------------------------------------------------- desenho
def desenho(P: str, L: dict, G: Gravador) -> None:
    cls, cand, outro = L["cls"], L["cand"], L["outro"]
    G.desenho(f"{P} · Resumo · HTML", f"Coluna da esquerda da tela {P[1:]}: o % de {cand} no recorte, os votos, em "
              "quantos municípios ficou à frente, o que mudou desde 2022, de onde vêm os votos (regiões no Brasil; "
              "cidades numa UF) e onde foi mais forte e mais fraco. Só lê contas; a barra é geometria.", dax(f"""
        -- 1 · Leituras
        VAR _comUF = [{P} · com UF]
        VAR _recorte = [{P} · recorte]
        VAR _votos = [{P} · votos]
        VAR _pct = [{P} · %]
        VAR _pos = [{P} · posição]
        VAR _v22 = [{P} · votos 2022]
        VAR _p22 = [{P} · % 2022]
        VAR _c22 = [{P} · candidato 2022]
        VAR _dv = [{P} · variação de votos]
        VAR _dpp = [{P} · variação em p.p.]
        VAR _nFrente = [{P} · municípios à frente]
        VAR _nMun = [{P} · municípios]
        VAR _eleit = [{P} · eleitores nos municípios à frente]
        VAR _orig = [{P} · origem principal]
        VAR _origParte = [{P} · origem principal parte]
        VAR _origPct = [{P} · origem principal %]
        VAR _forte = [{P} · lugar mais forte]
        VAR _forteP = [{P} · lugar mais forte %]
        VAR _fraco = [{P} · lugar mais fraco]
        VAR _fracoP = [{P} · lugar mais fraco %]
        VAR _grande = [{P} · cidade grande mais forte]
        VAR _grandeP = [{P} · cidade grande mais forte %]
        VAR _grandePop = [{P} · cidade grande mais forte população]
        VAR _regsBase =
            TOPN (
                IF ( _comUF = 0, 10, 0 ),
                ADDCOLUMNS (
                    VALUES ( 'UF'[Região] ),
                    "@v", [{P} · votos (municípios)],
                    "@p", [{P} · parte dos votos],
                    "@pv", [{P} · % (municípios)]
                ),
                [@v], DESC
            )
        VAR _regs =
            SELECTCOLUMNS (
                FILTER ( _regsBase, [@v] > 0 ), /* lista */
                "@nome", 'UF'[Região], "@v", [@v], "@p", [@p], "@pv", [@pv]
            )
        VAR _munsBase =
            TOPN (
                IF ( _comUF = 1, 5, 0 ),
                ADDCOLUMNS (
                    VALUES ( {MU}[Rótulo] ),
                    "@v", [{P} · votos (municípios)],
                    "@p", [{P} · parte dos votos],
                    "@pv", [{P} · % (municípios)]
                ),
                [@v], DESC
            )
        VAR _muns =
            SELECTCOLUMNS ( _munsBase, "@nome", {MU}[Rótulo], "@v", [@v], "@p", [@p], "@pv", [@pv] )
        VAR _lista = UNION ( _regs, _muns )
        -- 2 · Textos
        VAR _txtRec = @ESC(_recorte)@
        VAR _txtPct = @PCT(_pct)@
        VAR _txtVotos = @MI(_votos)@
        VAR _txtNFrente = @INT(_nFrente)@
        VAR _txtNMun = @INT(_nMun)@
        VAR _txtEleit = IF ( _eleit >= 0.995 && _nFrente < _nMun, @PCT(_eleit)@, @PCT0(_eleit)@ )
        VAR _txtMun = IF ( _nMun = 1, " município", " municípios" )
        VAR _manchete =
            SWITCH (
                TRUE (),
                _nMun = 1 && _nFrente = 1, "{cand} ficou à frente no único município do recorte",
                _nMun = 1, "{cand} ficou atrás no único município do recorte",
                _nFrente = 0, "{cand} não ficou à frente em nenhum dos " & _txtNMun & _txtMun,
                "{cand} ficou à frente em " & _txtNFrente & " dos " & _txtNMun & _txtMun & ", onde votam " & _txtEleit & " dos eleitores"
            )
        VAR _txtDV = IF ( _dv < 0, "−", "+" ) & @MI(ABS ( _dv ))@
        VAR _txtDPP = @PP(_dpp)@
        VAR _pontos = IF ( ABS ( _dpp ) < 2, " ponto", " pontos" )
        VAR _compara =
            "Em 2022, " & @ESC(_c22)@ & " teve " & @MI(_v22)@ & " (" & @PCT(_p22)@ & "). Agora: <b class='{cls}-esc'>"
                & _txtDV & IF ( ABS ( _dv ) >= 1000, " de votos", IF ( ABS ( _dv ) = 1, " voto", " votos" ) )
                & "</b> e <b class='{cls}-esc'>" & _txtDPP & _pontos & "</b>."
        VAR _rotOrigem = IF ( _comUF = 1, "De onde vêm os votos · as cidades que mais deram votos", "De onde vêm os votos · por região" )
        VAR _origNome = IF ( _comUF = 1 && RIGHT ( _orig, 1 ) = ")", LEFT ( _orig, LEN ( _orig ) - 5 ), _orig )
        VAR _frase =
            @ESC(_origNome)@ & " deu " & @PCT0(_origParte)@ & " dos votos de {cand}"
                & IF ( _comUF = 1, " no estado", "" ) & "; lá, ele teve " & @PCT(_origPct)@ & " dos válidos."
        VAR _resto = IF ( _comUF = 1, "<span class='resto entra d9'>demais municípios</span>" )
        VAR _rotForte = IF ( _comUF = 1, "Município mais forte", "UF mais forte" )
        VAR _rotFraco = IF ( _comUF = 1, "Município mais fraco", "UF mais fraca" )
        VAR _fatoGrande =
            IF (
                NOT ISBLANK ( _grande ),
                "<div class='fato sobe d10'><span class='ic g'></span><div><div class='rot'>Entre as cidades de 100 mil+</div>"
                    & "<div class='lg'>" & @ESC(_grande)@ & " <small>" & @INT(_grandePop)@ & " habitantes</small></div></div>"
                    & "<div class='vp {cls}'>" & @PCT(_grandeP)@ & "</div></div>"
            )
        -- 3 · Geometria (barra de 620 px; as fatias seguem a ordem dos votos)
        VAR _comIni =
            ADDCOLUMNS (
                _lista,
                "@ini", VAR _vv = [@v] RETURN SUMX ( FILTER ( _lista, [@v] > _vv ), [@p] ), /* lista */
                "@ord", VAR _vv = [@v] RETURN 1 + COUNTROWS ( FILTER ( _lista, [@v] > _vv ) ) /* lista */
            )
        VAR _fatias =
            CONCATENATEX (
                _comIni,
                VAR _w = [@p] * 620 -- geometria
                VAR _nm = IF ( _comUF = 1 && RIGHT ( [@nome], 1 ) = ")", LEFT ( [@nome], LEN ( [@nome] ) - 5 ), [@nome] )
                VAR _rot = IF ( _w >= 120, _nm & " " & @PCT0([@p])@, IF ( _w >= 44, @PCT0([@p])@, "" ) )
                RETURN
                    "<div class='fa o" & MIN ( [@ord], 5 ) & " barra-x d" & ( [@ord] + 5 ) & "' style='left:"
                        & @CSS([@ini] * 620)@ & "px;width:" & @CSS(_w)@ & "px'><span>" & @ESC(_rot)@ & "</span></div>",
                "",
                [@v], DESC
            )
        VAR _linhas =
            CONCATENATEX (
                _comIni,
                VAR _nm = IF ( _comUF = 1, LEFT ( [@nome], LEN ( [@nome] ) - 5 ), [@nome] )
                RETURN
                "<div class='li'><i class='sw o" & MIN ( [@ord], 5 ) & "'></i><span class='nm'>" & @ESC(_nm)@
                    & "</span><span class='a'>" & @PCT0([@p])@ & " dos votos dele · " & @MI([@v])@ & "</span>"
                    & "<span class='b'>" & @PCT([@pv])@ & " dos válidos</span></div>",
                "",
                [@v], DESC
            )
        -- 4 · Marcação
        VAR _html =
            "<div class='tela rv'>"
                & "<div class='sob sobe'>{L['completo']} · {L['sigla']} · {L['numero']} · " & _txtRec & "</div>"
                & "<div class='topo'><div class='big {cls} sobe d1'>" & _txtPct & "</div>"
                & "<div class='lado sobe d2'><div class='vv {cls}'>" & _txtVotos & "</div>"
                & "<div class='txt'>de votos · " & _pos & "º lugar</div></div></div>"
                & "<div class='man mc sobe d3'>" & _manchete & "</div>"
                & "<div class='txt cp sobe d4'>" & _compara & "</div>"
                & "<div class='rot ro sobe d5'>" & _rotOrigem & "</div>"
                & "<div class='barra'>" & _resto & _fatias & "</div>"
                & "<div class='fluxo'><div class='txt fr sobe d8'>" & _frase & "</div>"
                & "<div class='ls sobe d9'>" & _linhas & "</div>"
                & "<div class='fatos'>"
                & "<div class='fato sobe d10'><span class='ic f'></span><div><div class='rot'>" & _rotForte & "</div>"
                & "<div class='lg'>" & @ESC(_forte)@ & "</div></div><div class='vp {cls}'>" & @PCT(_forteP)@ & "</div></div>"
                & IF ( _fraco <> _forte, "<div class='fato sobe d11'><span class='ic r'></span><div><div class='rot'>" & _rotFraco & "</div>"
                & "<div class='lg'>" & @ESC(_fraco)@ & "</div></div><div class='vp'>" & @PCT(_fracoP)@ & "</div></div>" )
                & _fatoGrande & "</div></div>"
            & "</div>"
        RETURN
            _html
        """))
    G.desenho(f"{P} · Resumo · ALT", "Texto para leitor de tela da coluna do resumo.", dax(f"""
        LEFT (
            "{cand}, " & [{P} · recorte] & ": " & @PCT([{P} · %])@ & " dos válidos, " & @MI([{P} · votos])@
                & " de votos; à frente em " & [{P} · municípios à frente] & " de " & [{P} · municípios]
                & IF ( [{P} · municípios] = 1, " município", " municípios" ) & ". Mais forte: " & [{P} · lugar mais forte]
                & "; mais fraco: " & [{P} · lugar mais fraco] & ".",
            250
        )
        """))
    G.desenho(f"{P} · Legenda · HTML", "Legenda do mapa de pontos (como ler a cor e o tamanho).", dax(f"""
        -- 1 · Leituras
        VAR _comUF = [{P} · com UF]
        -- 4 · Marcação
        RETURN
            "<div class='tela lgm entra d6'>"
                & "<span class='it'><i class='bol'></i>cada ponto é um município; o tamanho segue os votos de {cand}</span>"
                & "<span class='it'><i class='esc'></i>{cand} à frente: quanto mais escuro, maior a margem</span>"
                & "<span class='it'><i class='atr'></i>{outro} à frente</span>"
                & "<span class='it dica'>passe o mouse num ponto para ver a cidade</span>"
            & "</div>"
        """))
    G.desenho(f"{P} · Legenda · ALT", "Texto para leitor de tela da legenda do mapa.", dax(f"""
        "Legenda: cada ponto é um município, o tamanho segue os votos de {cand}; a cor mostra onde {cand} ficou à "
            & "frente (mais escuro, maior margem) e, em areia, onde {outro} ficou à frente."
        """))
    G.desenho(f"{P} · Mapa · ALT", "Texto para leitor de tela do mapa de pontos.", dax(f"""
        LEFT (
            "Mapa de " & [{P} · recorte] & " com um ponto por município: {cand} ficou à frente em "
                & [{P} · municípios à frente] & " de " & [{P} · municípios]
                & IF ( [{P} · municípios] = 1, " município", " municípios" ) & ". Passe o mouse num ponto "
                & "para ver a cidade.",
            250
        )
        """))
    # dossiê do município (ficha pautada presa com fita)
    G.desenho(f"{P} · Tooltip município · HTML", f"Dossiê do município do ponto (ficha pautada presa com fita): {cand} × "
              f"{outro} em 2026, o mesmo par em 2022 e a margem antes e agora, com a nota à mão do que aconteceu. Só "
              "lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _mun = [{P} · município]
        VAR _reg = [{P} · região do município]
        VAR _pop = [{P} · população]
        VAR _p26 = [{P} · % (municípios)]
        VAR _a26 = [{P} · adversário % (municípios)]
        VAR _p22 = [{P} · % 2022 (municípios)]
        VAR _a22 = [{P} · adversário % 2022 (municípios)]
        VAR _m22 = [{P} · margem 2022]
        VAR _m26 = [{P} · margem]
        VAR _v26 = [{P} · votos (municípios)]
        VAR _sit = [{P} · situação]
        VAR _c22 = [{P} · candidato 2022]
        -- 2 · Textos
        VAR _nome22 = IF ( "{L['sigla']}" = "PT", "Lula", @ESC(_c22)@ )
        VAR _outro22 = IF ( "{L['sigla']}" = "PT", "Jair Bolsonaro", "Lula" )
        VAR _nota =
            SWITCH (
                _sit,
                1, "{L['notas'][0]}",
                2, "{L['notas'][1]}",
                3, "{L['notas'][2]}",
                "{L['notas'][3]}"
            )
        VAR _clsNota = IF ( _sit = 1 || _sit = 3, "{cls}-esc", "neutro" )
        VAR _txtM22 = @PP(_m22 * 100)@
        VAR _txtM26 = @PP(_m26 * 100)@
        -- 3 · Geometria (barras de 0 a 100% em 180 px)
        VAR _w26 = @CSS(_p26 * 180)@ -- geometria
        VAR _wa26 = @CSS(_a26 * 180)@ -- geometria
        VAR _w22 = @CSS(_p22 * 180)@ -- geometria
        VAR _wa22 = @CSS(_a22 * 180)@ -- geometria
        -- 4 · Marcação
        VAR _css =
            "<style>"
                & ".tt3{{position:fixed;inset:0;background:var(--papel)}}"
                & ".tt3 .ficha{{position:absolute;left:14px;top:22px;right:14px;bottom:14px;background:var(--branco);"
                & "border:1.5px solid var(--areia);background-image:repeating-linear-gradient(transparent 0 31px,"
                & "rgba(203,189,162,.45) 31px 32px);box-shadow:3px 4px 0 rgba(28,25,21,.07)}}"
                & ".tt3 .fita{{position:absolute;left:170px;top:-16px;width:96px;transform:rotate(-3deg);opacity:.9}}"
                & ".tt3 .pino{{position:absolute;right:16px;top:14px;width:30px}}"
                & ".tt3 .cab{{position:absolute;left:18px;top:14px;right:56px}}"
                & ".tt3 .nm{{font-size:22px;font-weight:700;line-height:1.15;letter-spacing:-.01em}}"
                & ".tt3 .an{{position:absolute;left:18px;right:18px;display:grid;grid-template-columns:52px 1fr;row-gap:6px;"
                & "align-items:center}}.tt3 .a26{{top:84px}}.tt3 .a22{{top:166px}}"
                & ".tt3 .ano{{font-size:15px;font-weight:700}}"
                & ".tt3 .lin{{display:flex;align-items:center;gap:8px;font-size:15px}}"
                & ".tt3 .lin i{{display:block;height:12px}}.tt3 .lin b{{font-weight:700;min-width:50px}}"
                & ".tt3 .lin span{{color:var(--grafite)}}"
                & ".tt3 .ci{{background:var(--{L['tom']})}}.tt3 .co{{background:var(--areia)}}"
                & ".tt3 .mg{{position:absolute;left:18px;right:18px;top:248px;font-size:15px;color:var(--grafite)}}"
                & ".tt3 .mg b{{color:var(--tinta)}}"
                & ".tt3 .mao{{position:absolute;right:18px;bottom:8px;font-size:28px}}"
                & ".tt3 .neutro{{color:var(--grafite)}}"
            & "</style>"
        VAR _lin = "<div class='lin'><i class='"
        VAR _html =
            _css
                & "<div class='tt3'><div class='ficha'>"
                & "<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/>"
                & "<img class='pino' alt='' src='{URL_MIDIA}/arte/icones/pino-tinta.png'/>"
                & "<div class='cab sobe'><div class='nm'>" & @ESC(_mun)@ & "</div>"
                & "<div class='rot'>" & @ESC(_reg)@ & " · " & @INT(_pop)@ & " habitantes</div></div>"
                & "<div class='an a26 sobe d1'><div class='ano'>2026</div><div>"
                & _lin & "ci barra-x' style='width:" & _w26 & "px'></i><b>" & @PCT(_p26)@ & "</b><span>{cand}</span></div>"
                & _lin & "co barra-x' style='width:" & _wa26 & "px'></i><b>" & @PCT(_a26)@ & "</b><span>{outro}</span></div>"
                & "</div></div>"
                & "<div class='an a22 sobe d2'><div class='ano'>2022</div><div>"
                & _lin & "ci barra-x' style='width:" & _w22 & "px;opacity:.55'></i><b>" & @PCT(_p22)@ & "</b><span>"
                & _nome22 & "</span></div>"
                & _lin & "co barra-x' style='width:" & _wa22 & "px;opacity:.55'></i><b>" & @PCT(_a22)@ & "</b><span>"
                & _outro22 & "</span></div>"
                & "</div></div>"
                & "<div class='mg sobe d3'>Margem do {L['sigla']}, em pontos: <b>" & _txtM22 & "</b> → <b>"
                & _txtM26 & "</b></div>"
                & "<div class='mao " & _clsNota & " entra d5'>" & _nota & "</div>"
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _mun ) && NOT ISBLANK ( _v26 ), _html )
        """).replace("{{", "{").replace("}}", "}"))
    G.desenho(f"{P} · Tooltip município · ALT", "Texto para leitor de tela do dossiê do município.", dax(f"""
        LEFT (
            [{P} · município] & ": {cand} " & @PCT([{P} · % (municípios)])@ & " e {outro} "
                & @PCT([{P} · adversário % (municípios)])@ & " em 2026; margem do {L['sigla']} de "
                & @PP([{P} · margem 2022] * 100)@ & " para " & @PP([{P} · margem] * 100)@ & " pontos.",
            250
        )
        """))


# ---------------------------------------------------------------------------------------------------- spec do mapa
def ufs_geometria() -> list[dict]:
    """Contorno de cada UF (quadro 1000 × 1000) com caixa, centro e perímetro (para o traço que se desenha)."""
    d = json.loads((PBI / "assets" / "mapas" / "uf_caminhos.json").read_text(encoding="utf-8"))
    saida = []
    for uf, caminho in sorted(d["caminhos"].items()):
        comprimento, xs, ys = 0.0, [], []
        for sub in re.findall(r"M[^M]+", caminho):
            pts = [tuple(map(float, p)) for p in re.findall(r"(-?\d+\.?\d*),(-?\d+\.?\d*)", sub)]
            if sub.rstrip().endswith("Z") and pts:
                pts.append(pts[0])
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                comprimento += math.hypot(x2 - x1, y2 - y1)
            xs += [p[0] for p in pts]
            ys += [p[1] for p in pts]
        saida.append({"uf": uf, "d": caminho, "x0": min(xs), "y0": min(ys), "x1": max(xs), "y1": max(ys),
                      "cx": round((min(xs) + max(xs)) / 2, 1), "cy": round((min(ys) + max(ys)) / 2, 1),
                      "ld": round(comprimento, 1)})
    return saida


def spec_mapa(modo: str, cores: tuple, descricao: str) -> dict:
    """Vega 6 puro. Campos do dataset: cod, x, y, uf e as medidas 'tam' (tamanho do ponto) e 'val' (cor).
    modo "margem": val = margem do candidato (−1 a 1); > 0 pinta no tom do candidato (claro → escuro), ≤ 0 em areia.
    modo "abstencao": val = abstenção do município (0–1), de creme a tinta."""
    claro, meio, escuro = cores
    if modo == "margem":
        escala = {"name": "cor", "type": "linear", "domain": [0, 0.2, 0.5], "range": [claro, meio, escuro],
                  "clamp": True, "interpolate": "rgb"}
        fill = "datum.val > 0 ? scale('cor', datum.val) : '#BBAD91'"
        opac = "datum.val > 0 ? 0.92 : 0.8"
    else:
        escala = {"name": "cor", "type": "linear", "domain": [0.12, 0.17, 0.22, 0.30],
                  "range": ["#E5DBC8", "#CBBDA2", "#7A6F60", "#1C1915"], "clamp": True, "interpolate": "rgb"}
        fill = "scale('cor', datum.val)"
        opac = "0.9"
    prog = "clamp((t - datum.atraso) / 520, 0, 1)"
    return {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": descricao,
        "width": {"signal": "pbiContainerWidth"}, "height": {"signal": "pbiContainerHeight"},
        "padding": 0, "autosize": {"type": "none", "contains": "padding"}, "background": None,
        "config": {"view": {"stroke": None}},
        "signals": [
            {"name": "estatico", "init": "!(windowSize()[0] > 0)"},
            {"name": "fim", "value": 3600},
            {"name": "t0", "init": "now()"},
            {"name": "t", "init": "estatico ? fim : 0",
             "on": [{"events": "timer{33}", "update": "estatico ? fim : min(now() - t0, fim)"}]},
            {"name": "folga", "value": 18},
            {"name": "nAtivas", "update": "length(data('ufsDoRecorte'))"},
            {"name": "umaUF", "update": "nAtivas == 1"},
            {"name": "qx0", "update": "nAtivas ? data('quadro')[0].x0 : 0"},
            {"name": "qy0", "update": "nAtivas ? data('quadro')[0].y0 : 0"},
            {"name": "qx1", "update": "nAtivas ? max(data('quadro')[0].x1, umaUF ? 0 : data('extPontos')[0].x1) : 1000"},
            {"name": "qy1", "update": "nAtivas ? data('quadro')[0].y1 : 1000"},
            {"name": "k", "update": "min((width - 2 * folga) / max(qx1 - qx0, 30), (height - 2 * folga) / max(qy1 - qy0, 30))"},
            {"name": "ox", "update": "width / 2 - (qx0 + qx1) / 2 * k"},
            {"name": "oy", "update": "height / 2 - (qy0 + qy1) / 2 * k"},
            {"name": "rmax", "update": "umaUF ? clamp(10 + 3.2 * k, 12, 30) : 17"},
            {"name": "cvx", "update": "length(data('centro')) ? data('centro')[0].cx : 500"},
            {"name": "cvy", "update": "length(data('centro')) ? data('centro')[0].cy : 500"},
        ],
        "data": [
            {"name": "dataset"},
            {"name": "ufsDoRecorte", "source": "dataset", "transform": [{"type": "aggregate", "groupby": ["uf"]}]},
            {"name": "ufs", "values": ufs_geometria(),
             "transform": [{"type": "lookup", "from": "ufsDoRecorte", "key": "uf", "fields": ["uf"],
                            "as": ["noRecorte"]},
                           {"type": "formula", "as": "ativa", "expr": "datum.noRecorte ? 1 : 0"}]},
            {"name": "ativas", "source": "ufs",
             "transform": [{"type": "filter", "expr": "datum.ativa == 1"},
                           {"type": "joinaggregate", "fields": ["cx", "cx"], "ops": ["min", "max"],
                            "as": ["cmin", "cmax"]},
                           {"type": "formula", "as": "atraso",
                            "expr": "umaUF ? 0 : 700 * (datum.cx - datum.cmin) / max(datum.cmax - datum.cmin, 1)"}]},
            {"name": "contexto", "source": "ufs", "transform": [{"type": "filter", "expr": "datum.ativa == 0"}]},
            {"name": "quadro", "source": "ativas",
             "transform": [{"type": "aggregate", "fields": ["x0", "y0", "x1", "y1"], "ops": ["min", "min", "max", "max"],
                            "as": ["x0", "y0", "x1", "y1"]}]},
            {"name": "comLugar", "source": "dataset",
             "transform": [{"type": "filter", "expr": "isValid(datum.x) && isValid(datum.y) && isValid(datum.tam)"},
                           {"type": "formula", "as": "xv", "expr": "datum.x * max(datum.tam, 0)"},
                           {"type": "formula", "as": "yv", "expr": "datum.y * max(datum.tam, 0)"}]},
            {"name": "extPontos", "source": "comLugar",
             "transform": [{"type": "aggregate", "fields": ["x"], "ops": ["max"], "as": ["x1"]}]},
            {"name": "centro", "source": "comLugar",
             "transform": [{"type": "aggregate", "fields": ["xv", "yv", "tam"], "ops": ["sum", "sum", "sum"],
                            "as": ["sx", "sy", "st"]},
                           {"type": "formula", "as": "cx", "expr": "datum.sx / max(datum.st, 1)"},
                           {"type": "formula", "as": "cy", "expr": "datum.sy / max(datum.st, 1)"}]},
            {"name": "pontos", "source": "comLugar",
             "transform": [{"type": "joinaggregate", "fields": ["tam"], "ops": ["max"], "as": ["tmax"]},
                           {"type": "formula", "as": "dist",
                            "expr": "sqrt(pow(datum.x - cvx, 2) + pow(datum.y - cvy, 2))"},
                           {"type": "joinaggregate", "fields": ["dist"], "ops": ["max"], "as": ["dmax"]},
                           {"type": "formula", "as": "atraso",
                            "expr": "900 + 1700 * datum.dist / max(datum.dmax, 1) + (toNumber(datum.cod) % 9) * 12"},
                           {"type": "collect", "sort": {"field": "tam", "order": "descending"}}]},
        ],
        "scales": [escala],
        "marks": [{
            "type": "group", "name": "palco", "clip": True,
            "encode": {"update": {"x": {"value": 0}, "y": {"value": 0}, "width": {"signal": "width"},
                                  "height": {"signal": "height"}}},
            "marks": [
                {"type": "path", "from": {"data": "contexto"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "fill": {"value": "#E5DBC8"}, "fillOpacity": {"signal": "umaUF ? 0.35 : 0"},
                     "stroke": {"value": "#CBBDA2"}, "strokeWidth": {"value": 1},
                     "opacity": {"signal": "umaUF ? clamp((t - 200) / 700, 0, 1) : 0"}}}},
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "fill": {"value": "#E5DBC8"},
                     "fillOpacity": {"signal": "clamp((t - 600 - datum.atraso * 0.4) / 900, 0, 1) * 0.5"}}}},
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "stroke": {"value": "#48423A"}, "strokeWidth": {"signal": "umaUF ? 1.6 : 0.9"},
                     "strokeJoin": {"value": "round"}, "strokeOpacity": {"value": 0.8},
                     "strokeDash": {"signal": "t >= fim ? [] : [datum.ld * k + 4, datum.ld * k + 4]"},
                     "strokeDashOffset": {"signal": "(datum.ld * k + 4) * (1 - pow(clamp((t - datum.atraso) / 1100, 0, 1), 0.7))"}}}},
                {"type": "symbol", "name": "pontos", "from": {"data": "pontos"},
                 "encode": {"update": {
                     "x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
                     "shape": {"value": "circle"},
                     "size": {"signal": f"pow(2 * max(1.35, rmax * sqrt(max(datum.tam, 0) / max(datum.tmax, 1))) * (0.35 + 0.65 * {prog}), 2)"},
                     "fill": {"signal": fill},
                     "fillOpacity": {"signal": f"({opac}) * {prog}"},
                     "stroke": {"value": "#F1EBDF"}, "strokeWidth": {"signal": "umaUF ? 0.8 : 0.4"},
                     "tooltip": {"signal": "datum"}},
                     "hover": {"stroke": {"value": "#1C1915"}, "strokeWidth": {"value": 1.6},
                               "fillOpacity": {"value": 1}}}},
            ]}],
    }


def gravar_spec(nome: str, spec: dict) -> Path:
    destino = PBI / "spec" / nome
    texto = json.dumps(spec, ensure_ascii=False, indent=1) + "\n"
    if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
        destino.write_text(texto, encoding="utf-8", newline="\n")
    return destino


# ---------------------------------------------------------------------------------------------------- página
def _css_resumo(L: dict) -> str:
    c = L["tom"]
    return (
        ".rv>*{position:absolute;left:0;width:620px}"
        ".rv .sob{top:0}"
        ".rv .topo{top:30px;display:flex;align-items:flex-end;gap:22px}"
        ".rv .big{font-size:112px;font-weight:700;letter-spacing:-.04em;line-height:.92;"
        "font-variant-numeric:tabular-nums lining-nums}"
        ".rv .lado{padding-bottom:6px}.rv .lado .vv{font-size:32px;font-weight:700;letter-spacing:-.02em}"
        ".rv .lado .txt{margin-top:2px}"
        ".rv .mc{top:162px;font-size:27px;line-height:1.22}"
        ".rv .cp{top:236px;font-size:16px}.rv .cp b{font-weight:600}"
        ".rv .ro{top:304px}"
        ".rv .barra{top:332px;height:46px;background:var(--creme)}"
        ".rv .fa{position:absolute;top:0;height:46px;display:flex;align-items:center;padding-left:10px;"
        "box-shadow:inset -2px 0 0 var(--papel);overflow:hidden;white-space:nowrap}"
        ".rv .fa span{font-size:15px;font-weight:600;color:var(--branco)}"
        f".rv .o1{{background:var(--{c})}}"
        f".rv .o2{{background:var(--{c});opacity:.78}}.rv .o3{{background:var(--{c});opacity:.6}}"
        f".rv .o4{{background:var(--{c});opacity:.45}}.rv .o5{{background:var(--{c});opacity:.32}}"
        ".rv .o4 span,.rv .o5 span{color:var(--tinta)}"
        ".rv .fluxo{top:388px}.rv .fluxo .fr{font-size:16px;color:var(--tinta)}"
        ".rv .resto{position:absolute;right:10px;top:13px;font-size:14px;color:var(--grafite)}"
        ".rv .ls{margin-top:12px}"
        ".rv .li{display:flex;align-items:baseline;gap:10px;padding:3px 0;font-size:15px;color:var(--grafite)}"
        ".rv .li .sw{display:inline-block;width:11px;height:11px;flex:none}"
        ".rv .li .nm{width:180px;color:var(--tinta);font-weight:600;white-space:nowrap;overflow:hidden;"
        "text-overflow:ellipsis}.rv .li .a{flex:1}.rv .li .b{text-align:right}"
        ".rv .fatos{margin-top:30px}"
        ".rv .fato{display:flex;align-items:center;gap:14px;padding:10px 0;border-top:1px dashed var(--areia)}"
        ".rv .fato>div:nth-child(2){flex:1}.rv .fato .lg{font-size:18px;font-weight:600;margin-top:2px}"
        ".rv .fato .lg small{font-size:14px;font-weight:400;color:var(--cinza);margin-left:6px}"
        ".rv .fato .vp{font-size:28px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums}"
        ".rv .ic{width:30px;height:30px;flex:none;background-size:contain;background-repeat:no-repeat;"
        "background-position:center}"
        f".rv .ic.f{{background-image:url({URL_MIDIA}/arte/icones/pino-{c}.png)}}"
        f".rv .ic.r{{background-image:url({URL_MIDIA}/arte/icones/pino-tinta.png);opacity:.6}}"
        f".rv .ic.g{{background-image:url({URL_MIDIA}/arte/icones/escola-tinta.png);opacity:.8}}"
    )


def _css_legenda(L: dict) -> str:
    claro, meio, escuro = L["cores"]
    return (
        ".lgm{display:flex;flex-wrap:wrap;gap:4px 22px;align-items:center;font-size:14px;color:var(--grafite);"
        "padding-top:6px}"
        ".lgm .it{display:flex;align-items:center;gap:8px}"
        ".lgm i{display:inline-block;flex:none}"
        ".lgm .bol{width:22px;height:14px;background:radial-gradient(circle at 4px 9px,var(--grafite) 2.5px,"
        "transparent 3px),radial-gradient(circle at 15px 7px,var(--grafite) 6px,transparent 6.5px)}"
        f".lgm .esc{{width:54px;height:10px;background:linear-gradient(90deg,{claro},{meio},{escuro})}}"
        ".lgm .atr{width:12px;height:12px;border-radius:50%;background:#BBAD91}"
        ".lgm .dica{color:var(--cinza)}"
    )


def declarar_votos(P: str) -> list:
    import pbip_lib as lib
    from pbip_lib import Pagina, Visual
    L = LADOS[P]
    css = "Estilo · CSS"
    z = lib.CAMADAS["conteudo"]
    tt = L["tooltip"]
    spec = f"spec/{P.lower()}_mapa.json"
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"), lib.campo_coluna("x", "Município", "X"),
              lib.campo_coluna("y", "Município", "Y"), lib.campo_coluna("uf", "Município", "UF"),
              lib.campo_medida("tam", f"{P} · votos (municípios)"), lib.campo_medida("val", f"{P} · margem")]
    return [
        Visual(P, lib.visual_html(f"{P}_Resumo_Html", *RESUMO, f"{P} · Resumo · HTML", folha_de_estilo=css, z=z,
                                  tab=100, alt=lib.medida(f"{P} · Resumo · ALT"),
                                  modelo_corpo=f"<style>{_css_resumo(L)}</style>" + "{{content}}")),
        Visual(P, lib.visual_deneb(f"{P}_Mapa_Pontos", *MAPA, spec, campos, alt=lib.medida(f"{P} · Mapa · ALT"),
                                   z=z + 2, tab=200, tooltip_pagina=tt, renderizacao="canvas", max_selecao=1)),
        Visual(P, lib.visual_html(f"{P}_Mapa_Legenda", *LEGENDA, f"{P} · Legenda · HTML", folha_de_estilo=css,
                                  z=z + 4, tab=210, alt=lib.medida(f"{P} · Legenda · ALT"),
                                  modelo_corpo=f"<style>{_css_legenda(L)}</style>" + "{{content}}")),
        Pagina(lib.pagina_tooltip(tt, f"Município · {L['cand']}", altura=TT_H, largura=TT_W), ordem=L["ordem_tt"]),
        Visual(tt, lib.visual_html(f"TT_{tt[2:]}_Conteudo", 0, 0, TT_W, TT_H, f"{P} · Tooltip município · HTML",
                                   alt=lib.medida(f"{P} · Tooltip município · ALT"), pagina_wh=(TT_W, TT_H),
                                   folha_de_estilo=css)),
    ]


def main() -> int:
    for P, L in LADOS.items():
        G = Gravador(L["pasta"])
        contas(P, L, G)
        desenho(P, L, G)
        apagados = G.limpar()
        gravar_spec(f"{P.lower()}_mapa.json", spec_mapa(
            "margem", L["cores"], f"Tela {P[1:]}: um ponto por município (tamanho = votos de {L['cand']}, cor = margem "
            f"de {L['cand']}); contorno das UFs em traço; pontos em onda a partir do centro dos votos."))
        print(G.resumo(), "· apagados:", [p.name for p in apagados])
    return 0


if __name__ == "__main__":
    sys.exit(main())
