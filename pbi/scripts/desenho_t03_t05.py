# -*- coding: utf-8 -*-
"""desenho_t03_t05 — telas 03 (Onde estão os votos de Lula?) e 05 (… de Flávio?): MESMO gerador, o lado é parâmetro
(neutralidade). Dono: agente das telas 01–06.

    python -I -X utf8 pbi/scripts/desenho_t03_t05.py    # grava pbi/dax/T03 Lula/…, pbi/dax/T05 Flávio/… e os specs

A tela tem três peças que conversam (pedido do Alisson, 23/10/2026: "os mapas têm que ter crossfiltering, os gráficos
também"):
  · Resumo (HTML, sem grão): o % no recorte, os votos, em quantos municípios ficou à frente, o que mudou desde 2022 e
    três fatos (lugar mais forte, mais fraco e a cidade grande mais forte). Com um município clicado no mapa, vira a
    ficha do município: o % e os votos dele lá, a margem sobre o outro, 2022 → 2026 e três comparações (o estado, as
    cidades do mesmo porte e o Brasil).
  · Origem (HTML com grão 'UF'[Região], filtro cruzado): de onde vêm os votos. No Brasil, uma entrada por região — a
    fatia da barra e a linha da lista — e o clique numa região leva o mapa e o resumo à região (o mapa enquadra só
    ela). Passar o mouse numa região abre o dossiê da região, estado por estado. Numa UF, as cidades que mais deram
    votos; com vários estados no filtro de estado (uma região inteira ou estados soltos, 24/10/2026), os estados que
    mais deram votos; com um município clicado, o lugar dele entre as cidades do estado (as três formas sem clique).
  · Mapa (Deneb, protagonista): um ponto por município, tamanho pelos votos do candidato, cor pela margem dele. O
    contorno das UFs se desenha, depois os pontos brotam em onda a partir do centro de gravidade dos votos. Seleção
    simples do Deneb: o clique num ponto marca o município (anel em tinta, os outros esmaecem, o contorno da UF dele
    engrossa) e filtra o resumo, a origem e a legenda; o clique no vazio desmarca. O grão é só o código IBGE (x, y e UF
    vêm por medida, L072), para o filtro que sai do clique ser só 'Município'[CodIBGE].

Modos (contas "com …"): município clicado > vários estados (filtro de estado em árvore: uma região inteira, estados
soltos, regiões misturadas) > uma UF (filtro da casca) > Brasil (com ou sem região clicada na origem). O nome do recorte
vem da medida comum [Recorte · nome] (pbi/scripts/desenho_recorte.py): uma região escolhida no filtro e a mesma região
clicada na origem dão o mesmo texto.

spec_mapa ainda aceita o modo "abstencao" (o mapa antigo da tela 06), sem seleção e igual ao de antes.
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
from momento_eleicao import segundo, soma_municipal, soma_uf  # noqa: E402

CU = "'Candidato UF'"
MA = "'Município ano'"
MU = "'Município'"
REG = "'UF'[Região], 'UF'[RegiaoOrdem]"        # a coluna de ordem entra sozinha no grão do visual (L072)

LADOS = {
    "T03": dict(pasta="T03 Lula", cand="Lula", completo="Luiz Inácio Lula da Silva", sigla="PT", numero=13,
                outro="Flávio", outro_num=22, col="VotosPT", col_outro="VotosAdversario", cls="lula",
                cores=("#E9B5AA", "#B8322A", "#7A1E19"), tooltip="ttT03Municipio", ordem_tt=130, tom="vermelho",
                tt_regiao="ttT03Regiao", ordem_tt_regiao=131,
                notas=("seguiu com Lula", "virou para Flávio", "virou para Lula", "seguiu com o PL")),
    "T05": dict(pasta="T05 Flávio", cand="Flávio", completo="Flávio Bolsonaro", sigla="PL", numero=22,
                outro="Lula", outro_num=13, col="VotosAdversario", col_outro="VotosPT", cls="flavio",
                cores=("#B9C9E2", "#2B5797", "#16305A"), tooltip="ttT05Municipio", ordem_tt=150, tom="azul",
                tt_regiao="ttT05Regiao", ordem_tt_regiao=151,
                notas=("seguiu com o PL", "virou para Lula", "virou para Flávio", "seguiu com Lula")),
}
RESUMO = (150, 140, 620, 860)
ORIGEM = (140, 444, 650, 272)             # conteúdo em x 150 (10 px de folga para o realce da linha, L080)
# rótulo e dica da origem no Brasil: fixos no modelo do visual (somem quando a entrada da UF ou do município escreve
# os seus)
ORIGEM_FIXO = ("<div class='tela og fixo'><div class='oc'><div class='rot ro sobe'>De onde vêm os votos · por região</div>"
               "<div class='dica entra d14'>clique numa região para ver só ela no mapa</div></div></div>")
FATOS_TOPO = 594                          # topo dos fatos dentro do resumo (abaixo da origem)
MAPA = (800, 140, 970, 800)
LEGENDA = (800, 946, 970, 54)
TT_W, TT_H = 460, 340
TTR_W, TTR_H = 460, 400


# ---------------------------------------------------------------------------------------------------- contas
def contas(P: str, L: dict, G: Gravador) -> None:
    c = G.conta
    n, col, colo = L["numero"], L["col"], L["col_outro"]
    # ---- modos
    ufs = """VAR _ufs = CALCULATE ( DISTINCTCOUNT ( 'UF'[UF] ), 'UF'[Tipo] = "UF" )"""
    c(f"{P} · com UF", "1 quando o recorte é UMA UF (filtro de estado da casca), 0 no Brasil, numa região ou com "
      "vários estados.", dax(f"""
        {ufs}
        RETURN
            IF ( ISCROSSFILTERED ( 'UF' ) && _ufs = 1, 1, 0 )
        """), "0")
    c(f"{P} · com região", "1 quando a região foi CLICADA na origem dos votos (filtro cruzado em 'UF'[Região]); 0 nos "
      "outros casos. O filtro de estado da casca, em árvore, filtra 'UF'[Caminho] e não conta aqui (uma região escolhida "
      "nele é um recorte de vários estados: [" + P + " · vários estados]).",
      "INT ( ISFILTERED ( 'UF'[Região] ) || ISFILTERED ( 'UF'[RegiaoOrdem] ) )", "0")
    c(f"{P} · vários estados", "1 quando o filtro de estado escolheu mais de uma UF (uma região inteira, estados soltos ou "
      "regiões misturadas): a origem mostra os estados do recorte. Ignora a região da linha da origem (o grão) e a "
      "região clicada; 0 no Brasil e numa UF.", dax(f"""
        VAR _com = CALCULATE ( [Recorte · com escolha], REMOVEFILTERS ( {REG} ) )
        VAR _n = CALCULATE ( [Recorte · UFs], REMOVEFILTERS ( {REG} ) )
        RETURN
            IF ( _com = 1 && _n > 1, 1, 0 )
        """), "0")
    c(f"{P} · com município", "1 quando há município marcado (o clique no mapa filtra 'Município'[CodIBGE]).",
      f"INT ( ISFILTERED ( {MU}[CodIBGE] ) || ISFILTERED ( {MU}[Rótulo] ) )", "0")
    c(f"{P} · recorte", "Nome do recorte: o município marcado ou o recorte de estado, lido da medida comum "
      "[Recorte · nome] (Brasil; a UF; a região, escolhida no filtro ou clicada na origem; 'MG e SP'; '3 estados').",
      dax(f"""
        IF (
            [{P} · com município] = 1,
            SELECTEDVALUE ( {MU}[Rótulo], "municípios marcados" ),
            [Recorte · nome]
        )
        """), "texto")
    # ---- resultado oficial do recorte ('Candidato UF', com o exterior no Brasil)
    c(f"{P} · votos", f"Votos de {L['cand']} (número {n}) no 1º turno de 2026, no recorte (com o exterior no Brasil).",
      segundo(f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026, {CU}[Número] = {n} )", soma_uf(col)), "#,0",
      f"paginas[{P[2]}].votos")
    c(f"{P} · válidos", "Votos válidos do 1º turno de 2026 no recorte.",
      segundo(f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2026 )", soma_uf('Validos')), "#,0")
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
            IF ( [Eleição · pós] = 1,
                1 + INT ( {soma_uf(colo)} > _v ),
                1 + COUNTROWS ( FILTER ( _todos, [@v] > _v ) ) )
        """), "0", f"paginas[{P[2]}].posicao_txt")
    c(f"{P} · votos 2022", f"Votos do candidato do {L['sigla']} no 1º turno de 2022, no recorte.",
      segundo(f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2022, {CU}[Número] = {n} )", soma_uf(col, 2022)), "#,0",
      f"paginas[{P[2]}].comparacao_2022.votos_2022_txt")
    c(f"{P} · válidos 2022", "Votos válidos do 1º turno de 2022 no recorte.",
      segundo(f"CALCULATE ( SUM ( {CU}[Votos] ), {CU}[Ano] = 2022 )", soma_uf('Validos', 2022)), "#,0")
    c(f"{P} · % 2022", f"Parcela do {L['sigla']} nos válidos de 2022 do recorte (0–1).",
      f"DIVIDE ( [{P} · votos 2022], [{P} · válidos 2022] )", "0.0%", f"paginas[{P[2]}].comparacao_2022.pct_2022_txt")
    c(f"{P} · candidato 2022", f"Nome de urna do candidato do {L['sigla']} em 2022.",
      f"CALCULATE ( SELECTEDVALUE ( {CU}[Candidato] ), REMOVEFILTERS ( 'UF' ), {CU}[Ano] = 2022, {CU}[Número] = {n} )",
      "texto")
    c(f"{P} · variação de votos", f"Votos do {L['sigla']} em 2026 menos 2022, no recorte.",
      f"[{P} · votos] - [{P} · votos 2022]", "#,0", f"paginas[{P[2]}].comparacao_2022.variacao_votos_txt")
    c(f"{P} · variação em p.p.", f"Variação do % do {L['sigla']} de 2022 para 2026, em pontos percentuais.",
      f"( [{P} · %] - [{P} · % 2022] ) * 100", "0.0", f"paginas[{P[2]}].comparacao_2022.variacao_pp_txt")
    # ---- soma dos municípios ('Município ano', sem o exterior)
    for nome, coluna, ano, desc in (
            ("votos (municípios)", col, 2026, f"Votos de {L['cand']} em 2026 somados nos municípios do contexto"),
            ("votos do adversário (municípios)", colo, 2026, f"Votos de {L['outro']} em 2026 somados nos municípios"),
            ("válidos (municípios)", "Validos", 2026, "Votos válidos de 2026 somados nos municípios"),
            ("aptos (municípios)", "Aptos", 2026, "Eleitores aptos em 2026 somados nos municípios"),
            ("votos 2022 (municípios)", col, 2022, f"Votos do {L['sigla']} em 2022 somados nos municípios"),
            ("votos do adversário 2022 (municípios)", colo, 2022, "Votos do adversário em 2022 somados nos municípios"),
            ("válidos 2022 (municípios)", "Validos", 2022, "Votos válidos de 2022 somados nos municípios")):
        c(f"{P} · {nome}", desc + " (sem o exterior).",
          soma_municipal(coluna, ano), "#,0")
    c(f"{P} · % (municípios)", f"Parcela de {L['cand']} nos válidos de 2026 dos municípios do contexto (0–1).",
      f"DIVIDE ( [{P} · votos (municípios)], [{P} · válidos (municípios)] )", "0.0%")
    c(f"{P} · adversário % (municípios)", f"Parcela de {L['outro']} nos válidos de 2026 dos municípios do contexto.",
      f"DIVIDE ( [{P} · votos do adversário (municípios)], [{P} · válidos (municípios)] )", "0.0%")
    c(f"{P} · % 2022 (municípios)", f"Parcela do {L['sigla']} nos válidos de 2022 dos municípios do contexto.",
      f"DIVIDE ( [{P} · votos 2022 (municípios)], [{P} · válidos 2022 (municípios)] )", "0.0%")
    c(f"{P} · adversário % 2022 (municípios)", "Parcela do adversário nos válidos de 2022 dos municípios do contexto.",
      f"DIVIDE ( [{P} · votos do adversário 2022 (municípios)], [{P} · válidos 2022 (municípios)] )", "0.0%")
    c(f"{P} · variação de votos (municípios)", f"Votos do {L['sigla']} em 2026 menos 2022, somados nos municípios do "
      "contexto (a ficha do município marcado).",
      f"[{P} · votos (municípios)] - [{P} · votos 2022 (municípios)]", "#,0")
    c(f"{P} · variação em p.p. (municípios)", f"Variação do % do {L['sigla']} de 2022 para 2026 nos municípios do "
      "contexto, em pontos percentuais.",
      f"( [{P} · % (municípios)] - [{P} · % 2022 (municípios)] ) * 100", "0.0")
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
      "do município da linha (0–1). Tira só as colunas do item (a região e a ordem dela, o rótulo do município).",
      dax(f"""
        DIVIDE (
            [{P} · votos (municípios)],
            CALCULATE ( [{P} · votos (municípios)], REMOVEFILTERS ( {REG} ), REMOVEFILTERS ( {MU}[Rótulo] ) )
        )
        """), "0%", f"paginas[{P[2]}].regioes[].parte_dos_votos")
    # ---- a região da linha (origem no Brasil, uma entrada por região)
    c(f"{P} · região da linha", "Nome da região da linha da origem (grão 'UF'[Região]).",
      "SELECTEDVALUE ( 'UF'[Região] )", "texto")
    c(f"{P} · UF da linha", "Nome da UF da linha (lista de estados do dossiê da região e da origem com vários "
      "estados).", "SELECTEDVALUE ( 'UF'[Nome] )", "texto")
    c(f"{P} · linha da primeira região", "1 na entrada da origem (grão 'UF'[Região]) da primeira região do recorte, do "
      "Norte ao Sul: com vários estados no filtro, só ela desenha a lista de estados (as outras entradas ficam vazias).",
      dax(f"""
        VAR _primeira =
            CALCULATE ( MIN ( 'UF'[RegiaoOrdem] ), REMOVEFILTERS ( {REG} ), 'UF'[Tipo] = "UF" )
        RETURN
            INT ( SELECTEDVALUE ( 'UF'[RegiaoOrdem] ) = _primeira )
        """), "0")
    c(f"{P} · parte do estado no recorte", f"Parcela dos votos de {L['cand']} no recorte (soma dos municípios) que veio "
      "da UF da linha (0–1): a lista de estados da origem quando o filtro escolheu vários. Tira só as colunas da UF da "
      "linha; o recorte do filtro ('UF'[Caminho]) fica.", dax(f"""
        DIVIDE (
            [{P} · votos (municípios)],
            CALCULATE ( [{P} · votos (municípios)], REMOVEFILTERS ( 'UF'[UF], 'UF'[Nome], 'UF'[Ordem] ) )
        )
        """), "0%")
    c(f"{P} · ordem da região", f"Colocação da região da linha pelos votos de {L['cand']} (1 = a que mais deu votos), "
      "entre as regiões do recorte.", dax(f"""
        VAR _v = [{P} · votos (municípios)]
        VAR _maiores =
            CALCULATETABLE (
                FILTER ( VALUES ( 'UF'[Região] ), [{P} · votos (municípios)] > _v ),
                REMOVEFILTERS ( {REG} )
            )
        RETURN
            IF ( _v > 0, 1 + COUNTROWS ( _maiores ) )
        """), "0", f"paginas[{P[2]}].regioes[] (ordem)")
    c(f"{P} · início da região", "Onde a região da linha começa na barra da origem: soma das parcelas das regiões que "
      "deram mais votos que ela (0–1).", dax(f"""
        VAR _v = [{P} · votos (municípios)]
        VAR _antes =
            CALCULATE (
                SUMX ( FILTER ( VALUES ( 'UF'[Região] ), [{P} · votos (municípios)] > _v ), [{P} · votos (municípios)] ),
                REMOVEFILTERS ( {REG} )
            )
        VAR _total = CALCULATE ( [{P} · votos (municípios)], REMOVEFILTERS ( {REG} ) )
        RETURN
            IF ( _v > 0, DIVIDE ( _antes, _total ) + 0 )
        """), "0.0%")
    # ---- onde foi mais forte e mais fraco: UF (Brasil ou região) ou município (numa UF)
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
        c(f"{P} · lugar {qual}", f"UF (no Brasil ou na região) ou município (numa UF) onde o candidato teve o "
          f"{qual.split()[1]} % dos válidos.", dax(corpo_nome), "texto", f"paginas[{P[2]}].{orac}.nome")
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
    # ---- o ponto do mapa (grão só no código IBGE; o resto vem por medida, L072)
    c(f"{P} · x do município", "Centro do município no quadro 1000 × 1000 dos mapas (x), para o ponto do mapa.",
      f"SELECTEDVALUE ( {MU}[X] )", "0.00")
    c(f"{P} · y do município", "Centro do município no quadro 1000 × 1000 dos mapas (y, para baixo).",
      f"SELECTEDVALUE ( {MU}[Y] )", "0.00")
    c(f"{P} · UF do município", "Sigla da UF do município da linha (ou do município marcado).",
      f"SELECTEDVALUE ( {MU}[UF] )", "texto")
    # ---- dossiê do município (tooltip do mapa) e a ficha do município marcado
    c(f"{P} · município", "Nome (UF) do município da linha.", f"SELECTEDVALUE ( {MU}[Rótulo] )", "texto")
    c(f"{P} · região do município", "Região do município da linha.", f"SELECTEDVALUE ( {MU}[Região] )", "texto")
    c(f"{P} · população", "População (Censo 2022) do município da linha.", f"SUM ( {MU}[População] )", "#,0")
    c(f"{P} · estado do município", "Nome da UF do município marcado.",
      f"LOOKUPVALUE ( 'UF'[Nome], 'UF'[UF], [{P} · UF do município] )", "texto")
    est = f"""VAR _s = [{P} · UF do município]"""
    no_estado = f"REMOVEFILTERS ( {MU} ), REMOVEFILTERS ( 'UF' ), {MU}[UF] = _s"
    c(f"{P} · % no estado do município", f"Parcela de {L['cand']} nos válidos de 2026 da UF do município marcado "
      "(resultado oficial da UF).", dax(f"""
        {est}
        RETURN
            IF ( NOT ISBLANK ( _s ), CALCULATE ( [{P} · %], REMOVEFILTERS ( 'UF' ), 'UF'[UF] = _s ) )
        """), "0.0%")
    c(f"{P} · % no Brasil", f"Parcela de {L['cand']} nos válidos de 2026 no Brasil, com o exterior (sem recorte).",
      f"CALCULATE ( [{P} · %], REMOVEFILTERS ( 'UF' ) )", "0.0%", f"paginas[{P[2]}].pct")
    c(f"{P} · porte do município", "Faixa de população do município marcado.", f"SELECTEDVALUE ( {MU}[Porte] )", "texto")
    porte = f"""VAR _p = [{P} · porte do município]"""
    c(f"{P} · % no porte do município", f"Parcela de {L['cand']} nos válidos de 2026 somados em todas as cidades do "
      "Brasil com o mesmo porte do município marcado.", dax(f"""
        {porte}
        RETURN
            IF (
                NOT ISBLANK ( _p ),
                CALCULATE ( [{P} · % (municípios)], REMOVEFILTERS ( {MU} ), REMOVEFILTERS ( 'UF' ), {MU}[Porte] = _p )
            )
        """), "0.0%")
    c(f"{P} · cidades do porte", "Quantas cidades do Brasil têm o mesmo porte do município marcado.", dax(f"""
        {porte}
        RETURN
            IF (
                NOT ISBLANK ( _p ),
                CALCULATE ( [{P} · municípios], REMOVEFILTERS ( {MU} ), REMOVEFILTERS ( 'UF' ), {MU}[Porte] = _p )
            )
        """), "#,0")
    c(f"{P} · municípios no estado do município", "Quantos municípios tem a UF do município marcado.", dax(f"""
        {est}
        RETURN
            IF ( NOT ISBLANK ( _s ), CALCULATE ( [{P} · municípios], {no_estado} ) )
        """), "#,0")
    c(f"{P} · parte do município no estado", f"Parcela dos votos de {L['cand']} na UF (soma dos municípios) que saiu "
      "do município marcado (0–1).", dax(f"""
        {est}
        RETURN
            IF (
                NOT ISBLANK ( _s ),
                DIVIDE ( [{P} · votos (municípios)], CALCULATE ( [{P} · votos (municípios)], {no_estado} ) )
            )
        """), "0.0%")
    for qual, med, desc in (("votos", f"[{P} · votos (municípios)]", "votos"),
                            ("%", f"[{P} · % (municípios)]", "% dos válidos")):
        c(f"{P} · posição em {qual} no estado", f"Lugar do município marcado entre as cidades da UF dele pelos {desc} "
          f"de {L['cand']} (1 = o maior).", dax(f"""
            {est}
            VAR _v = {med}
            VAR _maiores =
                CALCULATETABLE (
                    FILTER ( VALUES ( {MU}[CodIBGE] ), [{P} · válidos (municípios)] > 0 && {med} > _v ),
                    {no_estado}
                )
            RETURN
                IF ( NOT ISBLANK ( _s ) && _v > 0, 1 + COUNTROWS ( _maiores ) )
            """), "0")
    # ---- dossiê da região (tooltip da origem): os estados da região
    c(f"{P} · parte do estado na região", f"Parcela dos votos de {L['cand']} na região que veio da UF da linha (0–1), "
      "resultado oficial.", dax(f"""
        DIVIDE (
            [{P} · votos],
            CALCULATE ( [{P} · votos], REMOVEFILTERS ( 'UF'[UF], 'UF'[Nome], 'UF'[Ordem] ) )
        )
        """), "0%")
    c(f"{P} · margem na região", f"Margem de {L['cand']} na região da linha em 2026, em pontos (votos dele − votos de "
      f"{L['outro']}) ÷ válidos × 100.", f"[{P} · margem] * 100", "0.0")


# ---------------------------------------------------------------------------------------------------- desenho
def _fato(icone: str, rot: str, lg: str, valor: str, cls_valor: str, d: int) -> str:
    """Trecho DAX (já entre & … &) de uma linha de fato: ícone, rótulo, lugar e o número à direita."""
    return (f"\"<div class='fato sobe d{d}'><span class='ic {icone}'></span><div><div class='rot'>\" & {rot} & "
            f"\"</div><div class='lg'>\" & {lg} & \"</div></div><div class='vp{cls_valor}'>\" & {valor} & \"</div></div>\"")


def desenho(P: str, L: dict, G: Gravador) -> None:
    cls, cand, outro, sigla = L["cls"], L["cand"], L["outro"], L["sigla"]
    # ---------------------------------------------------------------- resumo (roteador + dois blocos)
    G.desenho(f"{P} · Resumo · HTML", f"Coluna da esquerda da tela {P[1:]}: a ficha do município marcado no mapa ou a "
              "do recorte (Brasil, região clicada ou UF do filtro). Só escolhe o bloco.", dax(f"""
        IF ( [{P} · com município] = 1, [{P} · Resumo · bloco município], [{P} · Resumo · bloco recorte] )
        """))
    G.desenho(f"{P} · Resumo · bloco recorte", f"Resumo do recorte: o % de {cand}, os votos, em quantos municípios "
              "ficou à frente, o que mudou desde 2022 e três fatos (mais forte, mais fraco, cidade grande). A faixa do "
              "meio fica livre para a origem (outro visual).", dax(f"""
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
        VAR _forte = [{P} · lugar mais forte]
        VAR _forteP = [{P} · lugar mais forte %]
        VAR _fraco = [{P} · lugar mais fraco]
        VAR _fracoP = [{P} · lugar mais fraco %]
        VAR _grande = [{P} · cidade grande mais forte]
        VAR _grandeP = [{P} · cidade grande mais forte %]
        VAR _grandePop = [{P} · cidade grande mais forte população]
        -- 2 · Textos
        VAR _txtRec = @ESC(_recorte)@
        VAR _txtPct = IF ( [Eleição · pós] = 1, FORMAT ( _pct, "0.00%" ), @PCT(_pct)@ )
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
        VAR _rotForte = IF ( _comUF = 1, "Município mais forte", "UF mais forte" )
        VAR _rotFraco = IF ( _comUF = 1, "Município mais fraco", "UF mais fraca" )
        VAR _fatoGrande =
            IF (
                NOT ISBLANK ( _grande ),
                {_fato("g", '"Entre as cidades de 100 mil+"', '@ESC(_grande)@ & " <small>" & @INT(_grandePop)@ & " habitantes</small>"', "@PCT(_grandeP)@", f" {cls}", 12)}
            )
        -- 4 · Marcação
        VAR _html =
            "<div class='tela rv'>"
                & "<div class='sob sobe'>{L['completo']} · {sigla} · {L['numero']} · " & _txtRec & "</div>"
                & "<div class='topo'><div class='big {cls} sobe d1" & IF ( [Eleição · pós] = 1, " pos", "" ) & "'>" & _txtPct & "</div>"
                & "<div class='lado sobe d2'><div class='vv {cls}'>" & _txtVotos & "</div>"
                & "<div class='txt'>de votos · " & _pos & "º lugar</div></div></div>"
                & "<div class='man mc sobe d3'>" & _manchete & "</div>"
                & "<div class='txt cp sobe d4'>" & _compara & "</div>"
                & "<div class='fatos'>"
                & {_fato("f", "_rotForte", "@ESC(_forte)@", "@PCT(_forteP)@", f" {cls}", 10)}
                & IF ( _fraco <> _forte, {_fato("r", "_rotFraco", "@ESC(_fraco)@", "@PCT(_fracoP)@", "", 11)} )
                & _fatoGrande & "</div>"
            & "</div>"
        RETURN
            _html
        """))
    G.desenho(f"{P} · Resumo · bloco município", f"Ficha do município marcado no mapa: o % e os votos de {cand} lá, a "
              f"margem sobre {outro} (e se a cidade virou desde 2022), 2022 → 2026 e três comparações: o estado, as "
              "cidades do mesmo porte no Brasil e o Brasil.", dax(f"""
        -- 1 · Leituras
        VAR _mun = [{P} · município]
        VAR _pct = [{P} · % (municípios)]
        VAR _votos = [{P} · votos (municípios)]
        VAR _m26 = [{P} · margem]
        VAR _sit = [{P} · situação]
        VAR _v22 = [{P} · votos 2022 (municípios)]
        VAR _p22 = [{P} · % 2022 (municípios)]
        VAR _c22 = [{P} · candidato 2022]
        VAR _dv = [{P} · variação de votos (municípios)]
        VAR _dpp = [{P} · variação em p.p. (municípios)]
        VAR _est = [{P} · estado do município]
        VAR _pEst = [{P} · % no estado do município]
        VAR _porte = [{P} · porte do município]
        VAR _pPorte = [{P} · % no porte do município]
        VAR _nPorte = [{P} · cidades do porte]
        VAR _pBr = [{P} · % no Brasil]
        -- 2 · Textos
        VAR _nm = IF ( RIGHT ( _mun, 1 ) = ")", LEFT ( _mun, LEN ( _mun ) - 5 ), _mun )
        VAR _txtNm = @ESC(_nm)@
        VAR _txtMun = @ESC(_mun)@
        VAR _mpp = ABS ( _m26 ) * 100
        VAR _txtM = FORMAT ( _mpp, "0.0" ) & IF ( _mpp < 2, " ponto", " pontos" )
        VAR _lado = IF ( _m26 > 0, "à frente de {outro}", "atrás de {outro}" )
        VAR _manchete =
            SWITCH (
                TRUE (),
                _m26 = 0, "Em " & _txtNm & ", {cand} e {outro} empataram",
                _sit = 2 || _sit = 3, _txtNm & " virou: {cand} ficou " & _txtM & " " & _lado,
                "Em " & _txtNm & ", {cand} ficou " & _txtM & " " & _lado & ", como em 2022"
            )
        VAR _clsMc = IF ( LEN ( _manchete ) > 74, " l", "" )
        VAR _txtLado = IF ( _m26 > 0, "à frente de {outro}", IF ( _m26 < 0, "atrás de {outro}", "empate com {outro}" ) )
        VAR _txtDV = IF ( _dv < 0, "−", "+" ) & @MI(ABS ( _dv ))@
        VAR _pontos = IF ( ABS ( _dpp ) < 2, " ponto", " pontos" )
        VAR _compara =
            "Em 2022, " & @ESC(_c22)@ & " teve " & @MI(_v22)@ & IF ( _v22 = 1, " voto", " votos" ) & " aqui ("
                & @PCT(_p22)@ & "). Agora: <b class='{cls}-esc'>" & _txtDV
                & IF ( ABS ( _dv ) >= 1000, " de votos", IF ( ABS ( _dv ) = 1, " voto", " votos" ) )
                & "</b> e <b class='{cls}-esc'>" & @PP(_dpp)@ & _pontos & "</b>."
        VAR _txtPorte = @ESC(_porte)@ & " <small>" & @INT(_nPorte)@ & IF ( _nPorte = 1, " cidade", " cidades" ) & "</small>"
        -- 4 · Marcação
        VAR _html =
            "<div class='tela rv'>"
                & "<div class='sob sobe'>{cand} · {sigla} · {L['numero']} · " & _txtMun & "</div>"
                & "<div class='topo'><div class='big {cls} sobe d1'>" & @PCT(_pct)@ & "</div>"
                & "<div class='lado sobe d2'><div class='vv {cls}'>" & @MI(_votos)@ & "</div>"
                & "<div class='txt'>de votos · " & _txtLado & "</div></div></div>"
                & "<div class='man mc" & _clsMc & " sobe d3'>" & _manchete & "</div>"
                & "<div class='txt cp sobe d4'>" & _compara & "</div>"
                & "<div class='fatos'>"
                & {_fato("f", '"Em todo o estado"', "@ESC(_est)@", "@PCT(_pEst)@", f" {cls}", 10)}
                & {_fato("g", '"Nas cidades do mesmo porte, no Brasil"', "_txtPorte", "@PCT(_pPorte)@", "", 11)}
                & {_fato("r", '"No Brasil inteiro"', '"resultado oficial, com o exterior"', "@PCT(_pBr)@", "", 12)}
                & "</div>"
            & "</div>"
        RETURN
            IF ( NOT ISBLANK ( _mun ) && NOT ISBLANK ( _votos ), _html )
        """))
    G.desenho(f"{P} · Resumo · ALT", "Texto para leitor de tela da coluna do resumo (recorte ou município marcado).",
              dax(f"""
        IF (
            [{P} · com município] = 1,
            LEFT (
                "{cand} em " & [{P} · município] & ": " & @PCT([{P} · % (municípios)])@ & " dos válidos, "
                    & @MI([{P} · votos (municípios)])@ & " de votos; no estado, " & @PCT([{P} · % no estado do município])@
                    & ".",
                250
            ),
            LEFT (
                "{cand}, " & [{P} · recorte] & ": " & @PCT([{P} · %])@ & " dos válidos, " & @MI([{P} · votos])@
                    & " de votos; à frente em " & [{P} · municípios à frente] & " de " & [{P} · municípios]
                    & IF ( [{P} · municípios] = 1, " município", " municípios" ) & ". Mais forte: "
                    & [{P} · lugar mais forte] & "; mais fraco: " & [{P} · lugar mais fraco] & ".",
                250
            )
        )
        """))
    # ---------------------------------------------------------------- origem (grão 'UF'[Região])
    G.desenho(f"{P} · Origem · HTML", f"De onde vêm os votos de {cand}, uma entrada por região: no Brasil, a fatia e a "
              "linha da região (clicáveis); com vários estados no filtro (uma região inteira ou estados soltos), os "
              "estados que mais deram votos; numa UF, as cidades que mais deram votos; com um município marcado, o "
              "lugar dele entre as cidades do estado. Só escolhe o bloco.", dax(f"""
        VAR _v = [{P} · votos (municípios)]
        RETURN
            SWITCH (
                TRUE (),
                NOT ( _v > 0 ), BLANK (),
                [{P} · com município] = 1, [{P} · Origem · bloco município],
                [{P} · vários estados] = 1, [{P} · Origem · bloco estados],
                [{P} · com UF] = 1, [{P} · Origem · bloco UF],
                [{P} · Origem · bloco região]
            )
        """))
    G.desenho(f"{P} · Origem · bloco região", "A região da linha na barra da origem (fatia proporcional aos votos, na "
              "ordem dos votos) e na lista (parte dos votos dele, votos e % dos válidos). O rótulo do bloco e a dica do "
              "clique ficam no modelo do visual (fora das entradas, não esmaecem com a seleção). Fatia e linha têm "
              "alvos de clique próprios, fixos (L012).", dax(f"""
        -- 1 · Leituras
        VAR _reg = [{P} · região da linha]
        VAR _v = [{P} · votos (municípios)]
        VAR _p = [{P} · parte dos votos]
        VAR _pv = [{P} · % (municípios)]
        VAR _ord = [{P} · ordem da região]
        VAR _ini = [{P} · início da região]
        -- 2 · Textos
        VAR _txtNome = @ESC(_reg)@
        VAR _txtP = @PCT0(_p)@
        VAR _o = MIN ( _ord, 5 )
        -- 3 · Geometria (barra de 620 px; linhas de 30 px a partir de y 92)
        VAR _w = _p * 620 -- geometria
        VAR _rot = IF ( _w >= 120, _txtNome & " " & _txtP, IF ( _w >= 44, _txtP, "" ) )
        VAR _x = @CSS(_ini * 620)@ -- geometria
        VAR _wc = @CSS(_w)@ -- geometria
        VAR _y = 92 + ( _ord - 1 ) * 30 -- geometria
        -- 4 · Marcação
        RETURN
            "<div class='tela og'><div class='oc'>"
                & "<div class='vis fa o" & _o & " barra-x d" & ( _ord + 4 ) & "' style='left:" & _x & "px;width:" & _wc
                & "px'><span>" & _rot & "</span></div>"
                & "<div class='hv' style='left:" & _x & "px;top:28px;width:" & _wc & "px;height:46px'></div>"
                & "<div class='vis li sobe d" & ( _ord + 6 ) & "' style='top:" & _y & "px'><i class='sw o" & _o & "'></i>"
                & "<span class='nm'>" & _txtNome & "</span><span class='a'>" & _txtP & " dos votos dele · " & @MI(_v)@
                & "</span><span class='b'>" & @PCT(_pv)@ & " dos válidos</span></div>"
                & "<div class='hv' style='left:-10px;top:" & _y & "px;width:640px;height:30px'></div>"
            & "</div></div>"
        """))
    G.desenho(f"{P} · Origem · bloco UF", f"Numa UF (uma entrada só): as cidades que mais deram votos a {cand} na barra "
              "(as 5 maiores e os demais municípios) e na lista. Sem clique (o clique numa cidade é no mapa).", dax(f"""
        -- 1 · Leituras
        VAR _munsBase =
            TOPN (
                5,
                ADDCOLUMNS (
                    VALUES ( {MU}[Rótulo] ),
                    "@v", [{P} · votos (municípios)],
                    "@p", [{P} · parte dos votos],
                    "@pv", [{P} · % (municípios)]
                ),
                [@v], DESC
            )
        VAR _lista =
            SELECTCOLUMNS ( FILTER ( _munsBase, [@v] > 0 ), "@nome", {MU}[Rótulo], "@v", [@v], "@p", [@p], "@pv", [@pv] ) /* lista */
        -- 3 · Geometria (barra de 620 px; as fatias seguem a ordem dos votos; linhas de 30 px a partir de y 92)
        VAR _comIni =
            ADDCOLUMNS (
                _lista,
                "@ini", VAR _vv = [@v] RETURN SUMX ( FILTER ( _lista, [@v] > _vv ), [@p] ) + 0, /* lista */
                "@ord", VAR _vv = [@v] RETURN 1 + COUNTROWS ( FILTER ( _lista, [@v] > _vv ) ) /* lista */
            )
        VAR _fatias =
            CONCATENATEX (
                _comIni,
                VAR _w = [@p] * 620 -- geometria
                VAR _nm = IF ( RIGHT ( [@nome], 1 ) = ")", LEFT ( [@nome], LEN ( [@nome] ) - 5 ), [@nome] )
                VAR _rot = IF ( _w >= 120, _nm & " " & @PCT0([@p])@, IF ( _w >= 44, @PCT0([@p])@, "" ) )
                RETURN
                    "<div class='fa o" & MIN ( [@ord], 5 ) & " barra-x d" & ( [@ord] + 4 ) & "' style='left:"
                        & @CSS([@ini] * 620)@ & "px;width:" & @CSS(_w)@ & "px'><span>" & @ESC(_rot)@ & "</span></div>",
                "",
                [@v], DESC
            )
        VAR _linhas =
            CONCATENATEX (
                _comIni,
                VAR _nm = IF ( RIGHT ( [@nome], 1 ) = ")", LEFT ( [@nome], LEN ( [@nome] ) - 5 ), [@nome] )
                RETURN
                    "<div class='li sobe d" & ( [@ord] + 6 ) & "' style='top:" & ( 92 + ( [@ord] - 1 ) * 30 ) & "px'>"
                        & "<i class='sw o" & MIN ( [@ord], 5 ) & "'></i><span class='nm'>" & @ESC(_nm)@ & "</span>"
                        & "<span class='a'>" & @PCT0([@p])@ & " dos votos dele · " & @MI([@v])@ & "</span>"
                        & "<span class='b'>" & @PCT([@pv])@ & " dos válidos</span></div>",
                "",
                [@v], DESC
            )
        -- 4 · Marcação
        RETURN
            "<div class='tela og'><div class='oc'>"
                & "<div class='rot ro sobe'>De onde vêm os votos · as cidades que mais deram votos</div>"
                & "<div class='trilho entra d3'></div><span class='resto entra d9'>demais municípios</span>"
                & _fatias & _linhas
                & "<div class='dica entra d14'>clique num ponto do mapa para ver uma cidade</div>"
            & "</div></div>"
        """))
    G.desenho(f"{P} · Origem · bloco estados", f"Com vários estados no filtro de estado (uma região inteira, estados "
              f"soltos ou regiões misturadas): os estados que mais deram votos a {cand} na barra (os 5 maiores e os "
              "demais estados) e na lista — a parte de cada um nos votos dele no recorte, os votos e o % dos válidos. "
              "Só a entrada da primeira região do recorte desenha (as outras ficam vazias). Sem clique (o clique numa "
              "cidade é no mapa).", dax(f"""
        -- 1 · Leituras
        VAR _primeira = [{P} · linha da primeira região]
        VAR _n = CALCULATE ( [Recorte · UFs], REMOVEFILTERS ( {REG} ) )
        VAR _ufsBase =
            CALCULATETABLE (
                TOPN (
                    5,
                    ADDCOLUMNS (
                        VALUES ( 'UF'[UF] ),
                        "@nome", [{P} · UF da linha],
                        "@v", [{P} · votos (municípios)],
                        "@p", [{P} · parte do estado no recorte],
                        "@pv", [{P} · % (municípios)]
                    ),
                    [@v], DESC
                ),
                REMOVEFILTERS ( {REG} ),
                'UF'[Tipo] = "UF"
            )
        VAR _lista =
            SELECTCOLUMNS ( FILTER ( _ufsBase, [@v] > 0 ), "@nome", [@nome], "@v", [@v], "@p", [@p], "@pv", [@pv] ) /* lista */
        -- 3 · Geometria (barra de 620 px; as fatias seguem a ordem dos votos; linhas de 30 px a partir de y 92)
        VAR _comIni =
            ADDCOLUMNS (
                _lista,
                "@ini", VAR _vv = [@v] RETURN SUMX ( FILTER ( _lista, [@v] > _vv ), [@p] ) + 0, /* lista */
                "@ord", VAR _vv = [@v] RETURN 1 + COUNTROWS ( FILTER ( _lista, [@v] > _vv ) ) /* lista */
            )
        VAR _sobra = ( 1 - SUMX ( _lista, [@p] ) ) * 620 -- geometria (o trilho dos demais estados)
        VAR _fatias =
            CONCATENATEX (
                _comIni,
                VAR _w = [@p] * 620 -- geometria
                VAR _cabe = ( LEN ( [@nome] ) + 4 ) * 9.4 + 16 -- geometria (nome e % em Sora 15 semibold)
                VAR _rot = IF ( _w >= _cabe, [@nome] & " " & @PCT0([@p])@, IF ( _w >= 44, @PCT0([@p])@, "" ) )
                RETURN
                    "<div class='fa o" & MIN ( [@ord], 5 ) & " barra-x d" & ( [@ord] + 4 ) & "' style='left:"
                        & @CSS([@ini] * 620)@ & "px;width:" & @CSS(_w)@ & "px'><span>" & @ESC(_rot)@ & "</span></div>",
                "",
                [@v], DESC
            )
        VAR _linhas =
            CONCATENATEX (
                _comIni,
                "<div class='li sobe d" & ( [@ord] + 6 ) & "' style='top:" & ( 92 + ( [@ord] - 1 ) * 30 ) & "px'>"
                    & "<i class='sw o" & MIN ( [@ord], 5 ) & "'></i><span class='nm'>" & @ESC([@nome])@ & "</span>"
                    & "<span class='a'>" & @PCT0([@p])@ & " dos votos dele · " & @MI([@v])@ & "</span>"
                    & "<span class='b'>" & @PCT([@pv])@ & " dos válidos</span></div>",
                "",
                [@v], DESC
            )
        -- 4 · Marcação
        RETURN
            IF (
                _primeira = 1,
                "<div class='tela og'><div class='oc'>"
                    & "<div class='rot ro sobe'>De onde vêm os votos · os estados que mais deram votos</div>"
                    & "<div class='trilho entra d3'></div>"
                    & IF ( _n > 5 && _sobra >= 136, "<span class='resto entra d9'>demais estados</span>" )
                    & _fatias & _linhas
                    & "<div class='dica entra d14'>clique num ponto do mapa para ver uma cidade</div>"
                & "</div></div>"
            )
        """))
    G.desenho(f"{P} · Origem · bloco município", f"Com um município marcado (uma entrada só): o lugar dele entre as "
              f"cidades da UF — a fatia dos votos de {cand} no estado que saiu dele e as posições em votos e em % dos "
              "válidos. Sem clique.", dax(f"""
        -- 1 · Leituras
        VAR _mun = [{P} · município]
        VAR _est = [{P} · estado do município]
        VAR _parte = [{P} · parte do município no estado]
        VAR _posV = [{P} · posição em votos no estado]
        VAR _posP = [{P} · posição em % no estado]
        VAR _n = [{P} · municípios no estado do município]
        -- 2 · Textos
        VAR _nm = IF ( RIGHT ( _mun, 1 ) = ")", LEFT ( _mun, LEN ( _mun ) - 5 ), _mun )
        VAR _txtNm = @ESC(_nm)@
        VAR _txtEst = @ESC(_est)@
        VAR _rotulo =
            IF (
                _n = 1,
                _txtNm & " · " & _txtEst & " · o único município",
                "No estado · " & _txtEst & " · " & @INT(_n)@ & " cidades"
            )
        VAR _txtParte = @PCT(_parte)@ & " dos votos de {cand} no estado saíram daqui"
        VAR _linhaV =
            IF (
                _posV = 1,
                "a cidade que mais deu votos a {cand} no estado",
                "cidade que mais deu votos a {cand} no estado"
            )
        VAR _linhaP =
            IF (
                _posP = 1,
                "onde {cand} teve o maior % dos válidos no estado",
                "no % dos válidos de {cand}, da mais forte à mais fraca"
            )
        -- 3 · Geometria (barra de 620 px)
        VAR _w = MAX ( _parte * 620, 4 ) -- geometria
        VAR _dentro = _w >= 360 -- geometria
        VAR _xr = @CSS(_w + 12)@ -- geometria
        -- 4 · Marcação
        VAR _rk =
            IF (
                _n > 1,
                "<div class='rk sobe d8' style='top:96px'><span class='n {cls}'>" & _posV & "ª</span><span class='t'>"
                    & _linhaV & "</span></div>"
                    & "<div class='rk sobe d10' style='top:160px'><span class='n'>" & _posP & "ª</span><span class='t'>"
                    & _linhaP & "</span></div>"
            )
        RETURN
            IF (
                NOT ISBLANK ( _mun ),
                "<div class='tela og'><div class='oc'>"
                    & "<div class='rot ro sobe'>" & _rotulo & "</div>"
                    & "<div class='trilho entra d3'></div>"
                    & "<div class='fa o1 barra-x d5' style='left:0;width:" & @CSS(_w)@ & "px'><span>"
                    & IF ( _dentro, _txtParte ) & "</span></div>"
                    & IF ( NOT _dentro, "<span class='lfa entra d8' style='left:" & _xr & "px'>" & _txtParte & "</span>" )
                    & _rk
                    & "<div class='dica entra d14'>clique no vazio do mapa para voltar</div>"
                & "</div></div>"
            )
        """))
    G.desenho(f"{P} · Origem · ALT", "Texto para leitor de tela da origem dos votos.", dax(f"""
        LEFT (
            SWITCH (
                TRUE (),
                [{P} · com município] = 1,
                    [{P} · município] & ": " & @PCT([{P} · parte do município no estado])@ & " dos votos de {cand} em "
                        & [{P} · estado do município] & ".",
                [{P} · vários estados] = 1,
                    "Os estados que mais deram votos a {cand} " & [Recorte · em] & ", com a parte de cada um nos "
                        & "votos dele.",
                [{P} · com UF] = 1,
                    "As cidades que mais deram votos a {cand} " & [Recorte · em] & ".",
                "De onde vêm os votos de {cand}, por região. Clique numa região para ver só ela no mapa; passe o mouse "
                    & "para ver os estados dela."
            ),
            250
        )
        """))
    # ---------------------------------------------------------------- legenda e mapa
    G.desenho(f"{P} · Legenda · HTML", "Legenda do mapa de pontos (como ler a cor e o tamanho) e a dica do que o clique "
              "faz, ou do que está marcado agora.", dax(f"""
        -- 1 · Leituras
        VAR _comMun = [{P} · com município]
        VAR _comReg = [{P} · com região]
        VAR _rec = [{P} · recorte]
        -- 2 · Textos
        VAR _dica =
            SWITCH (
                TRUE (),
                _comMun = 1, "<b>" & @ESC(_rec)@ & "</b> marcado · clique no vazio do mapa para voltar",
                _comReg = 1, "<b>" & @ESC(_rec)@ & "</b> marcado · clique de novo na região para voltar",
                "passe o mouse num ponto para ver a cidade; clique para levá-la ao painel"
            )
        -- 4 · Marcação
        RETURN
            "<div class='tela lgm entra d6'>"
                & "<span class='it'><i class='bol'></i>cada ponto é um município; o tamanho segue os votos de {cand}</span>"
                & "<span class='it'><i class='esc'></i>{cand} à frente: quanto mais escuro, maior a margem</span>"
                & "<span class='it'><i class='atr'></i>{outro} à frente</span>"
                & "<span class='it dica'>" & _dica & "</span>"
            & "</div>"
        """))
    G.desenho(f"{P} · Legenda · ALT", "Texto para leitor de tela da legenda do mapa.", dax(f"""
        "Legenda: cada ponto é um município, o tamanho segue os votos de {cand}; a cor mostra onde {cand} ficou à "
            & "frente (mais escuro, maior margem) e, em areia, onde {outro} ficou à frente. Clique num ponto para levar "
            & "a cidade ao painel."
        """))
    G.desenho(f"{P} · Mapa · ALT", "Texto para leitor de tela do mapa de pontos.", dax(f"""
        LEFT (
            "Mapa (" & [{P} · recorte] & ") com um ponto por município: {cand} ficou à frente em "
                & [{P} · municípios à frente] & " de " & [{P} · municípios]
                & IF ( [{P} · municípios] = 1, " município", " municípios" ) & ". Passe o mouse num ponto "
                & "para ver a cidade; clique para levá-la ao painel.",
            250
        )
        """))
    # ---------------------------------------------------------------- dossiê do município (ficha pautada com fita)
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
        VAR _nome22 = IF ( "{sigla}" = "PT", "Lula", @ESC(_c22)@ )
        VAR _outro22 = IF ( "{sigla}" = "PT", "Jair Bolsonaro", "Lula" )
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
                & "<div class='mg sobe d3'>Margem do {sigla}, em pontos: <b>" & _txtM22 & "</b> → <b>"
                & _txtM26 & "</b></div>"
                & "<div class='mao " & _clsNota & " entra d5'>" & _nota & "</div>"
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _mun ) && NOT ISBLANK ( _v26 ), _html )
        """).replace("{{", "{").replace("}}", "}"))
    G.desenho(f"{P} · Tooltip município · ALT", "Texto para leitor de tela do dossiê do município.", dax(f"""
        LEFT (
            [{P} · município] & ": {cand} " & @PCT([{P} · % (municípios)])@ & " e {outro} "
                & @PCT([{P} · adversário % (municípios)])@ & " em 2026; margem do {sigla} de "
                & @PP([{P} · margem 2022] * 100)@ & " para " & @PP([{P} · margem] * 100)@ & " pontos.",
            250
        )
        """))
    # ---------------------------------------------------------------- dossiê da região (passar o mouse na origem)
    G.desenho(f"{P} · Tooltip região · HTML", f"Dossiê da região da origem (ficha com clipe): os estados da região, do "
              f"que mais deu votos a {cand} ao que menos — a parte de cada um nos votos dele na região, o % dele lá e a "
              "mudança desde 2022 —, com a nota à mão da maior mudança. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _reg = [{P} · região da linha]
        VAR _mg = [{P} · margem na região]
        VAR _ufs =
            ADDCOLUMNS (
                CALCULATETABLE ( VALUES ( 'UF'[UF] ), 'UF'[Tipo] = "UF" ),
                "@nome", [{P} · UF da linha],
                "@v", [{P} · votos],
                "@s", [{P} · parte do estado na região],
                "@p", [{P} · %],
                "@d", [{P} · variação em p.p.]
            )
        VAR _lista = FILTER ( _ufs, [@v] > 0 ) /* lista */
        VAR _n = COUNTROWS ( _lista ) /* lista */
        VAR _smax = MAXX ( _lista, [@s] ) /* lista */
        VAR _top = TOPN ( 1, _lista, ABS ( [@d] ), DESC, 'UF'[UF], ASC ) /* lista */
        VAR _topNome = MAXX ( _top, [@nome] ) /* lista */
        VAR _topD = MAXX ( _top, [@d] ) /* lista */
        -- 2 · Textos
        VAR _txtReg = @ESC(_reg)@
        VAR _txtMg = "{cand} ficou " & FORMAT ( ABS ( _mg ), "0.0" ) & IF ( ABS ( _mg ) < 2, " ponto ", " pontos " )
            & IF ( _mg >= 0, "à frente de {outro}", "atrás de {outro}" ) & " na região"
        VAR _nota = IF ( _topD < 0, "maior queda: ", "maior alta: " ) & @ESC(_topNome)@
        VAR _clsNota = IF ( _topD < 0, "neutro", "{cls}-esc" )
        -- 3 · Geometria (barra da parte em até 120 px; linhas de 26 px)
        VAR _h = IF ( _n > 7, 24, 27 ) -- geometria
        VAR _linhas =
            CONCATENATEX (
                _lista,
                VAR _w = @CSS(DIVIDE ( [@s], _smax ) * 60)@ -- geometria
                RETURN
                    "<div class='ln' style='height:" & _h & "px'><span class='uf'>" & @ESC([@nome])@ & "</span>"
                        & "<span class='br'><i class='barra-x {cls}-bg' style='width:" & _w & "px'></i><b>"
                        & @PCT0([@s])@ & "</b></span><span class='pc'>" & @PCT([@p])@ & "</span>"
                        & "<span class='dd " & IF ( [@d] < 0, "neg", "pos" ) & "'>" & @PP([@d])@ & "</span></div>",
                "",
                [@v], DESC
            )
        -- 4 · Marcação
        RETURN
            IF (
                NOT ISBLANK ( _reg ) && _n > 0,
                "<div class='tt3r'><div class='ficha'>"
                    & "<div class='cab sobe'><div class='nm {cls}'>" & _txtReg & ", por estado</div>"
                    & "<div class='sub'>" & _txtMg & "</div></div>"
                    & "<div class='hd sobe d1'><span class='uf'>UF</span><span class='br'>peso</span>"
                    & "<span class='pc'>% dele</span><span class='dd'>vs. 2022</span></div>"
                    & "<div class='lista sobe d2'>" & _linhas & "</div>"
                    & "<div class='mao " & _clsNota & " entra d6'>" & _nota & "</div>"
                & "</div></div>"
            )
        """))
    G.desenho(f"{P} · Tooltip região · ALT", "Texto para leitor de tela do dossiê da região.", dax(f"""
        LEFT (
            "{cand} na região " & [{P} · região da linha] & ", estado por estado: a parte de cada estado nos votos dele, "
                & "o % dele em cada um e a mudança desde 2022.",
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


def spec_mapa(modo: str, cores: tuple, descricao: str, selecao: bool = False) -> dict:
    """Vega 6 puro. Campos do dataset: cod, x, y, uf e as medidas 'tam' (tamanho do ponto) e 'val' (cor).
    modo "margem": val = margem do candidato (−1 a 1); > 0 pinta no tom do candidato (claro → escuro), ≤ 0 em areia.
    modo "abstencao": val = abstenção do município (0–1), de creme a tinta.
    selecao=True (telas 03 e 05; a 06 continua sem): seleção simples do Deneb — o clique num ponto marca o município
    (o datum mantém __row__: só filter/formula/joinaggregate/collect sobre o dataset), o clique no vazio desmarca;
    __selected__ = on/off/neutral desenha o marcado por cima com anel em tinta, esmaece os outros e engrossa o contorno
    da UF dele. Com a atualização incremental ligada (L123) a vista não é recompilada: o relógio só recomeça quando o
    recorte muda (outra UF ou região), nunca no clique."""
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
    off = "(datum.__selected__ == 'off')"
    t0 = {"name": "t0", "init": "now()"}
    if selecao:
        t0["on"] = [{"events": {"signal": "chave"}, "update": "now()"}]
    sinais = [
        {"name": "estatico", "init": "!(windowSize()[0] > 0)"},
        {"name": "fim", "value": 3600},
        *([{"name": "chave",
            "update": "(isArray(data('comLugar')) ? length(data('comLugar')) : 0) + '|' + "
                      "(isArray(data('ufsDoRecorte')) ? join(pluck(data('ufsDoRecorte'), 'uf'), ',') : '')"}]
          if selecao else []),
        t0,
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
    ]
    contorno = {"path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                "stroke": {"value": "#48423A"}, "strokeWidth": {"signal": "umaUF ? 1.6 : 0.9"},
                "strokeJoin": {"value": "round"}, "strokeOpacity": {"value": 0.8},
                "strokeDash": {"signal": "t >= fim ? [] : [datum.ld * k + 4, datum.ld * k + 4]"},
                "strokeDashOffset": {"signal": "(datum.ld * k + 4) * (1 - pow(clamp((t - datum.atraso) / 1100, 0, 1), 0.7))"}}
    ponto = {"x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
             "shape": {"value": "circle"},
             "size": {"signal": f"pow(2 * max(1.35, rmax * sqrt(max(datum.tam, 0) / max(datum.tmax, 1))) * (0.35 + 0.65 * {prog}), 2)"},
             "fill": {"signal": fill},
             "fillOpacity": {"signal": f"({opac}) * {prog}"},
             "stroke": {"value": "#F1EBDF"}, "strokeWidth": {"signal": "umaUF ? 0.8 : 0.4"},
             "tooltip": {"signal": "datum"}}
    marcas_extra = []
    if selecao:
        # a UF do município marcado: indata (um sinal que lê data('marcados') não enxerga o dado, que depende de
        # sinais — medido no Vega 6.4: data('pontos') não é lista dentro de um sinal)
        contorno["strokeWidth"] = {"signal": "indata('marcados', 'uf', datum.uf) ? 2.6 : (umaUF ? 1.6 : 0.9)"}
        contorno["strokeOpacity"] = {"signal": "indata('marcados', 'uf', datum.uf) ? 1 : 0.8"}
        ponto["fillOpacity"] = {"signal": f"({opac}) * {prog} * ({off} ? 0.28 : 1)"}
        ponto["strokeOpacity"] = {"signal": f"{off} ? 0.35 : 1"}
        ponto["cursor"] = {"value": "pointer"}
        # o município marcado por cima de todos, com um anel em tinta (o mesmo datum: o clique nele desmarca)
        marcas_extra.append({"type": "symbol", "name": "marcados", "from": {"data": "marcados"},
                             "encode": {"update": {
                                 "x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
                                 "shape": {"value": "circle"},
                                 "size": {"signal": "pow(2 * max(5.5, 1.2 * rmax * sqrt(max(datum.tam, 0) / max(datum.tmax, 1))), 2)"},
                                 "fill": {"signal": fill}, "fillOpacity": {"value": 1},
                                 "stroke": {"value": "#1C1915"}, "strokeWidth": {"value": 2.6},
                                 "cursor": {"value": "pointer"},
                                 "tooltip": {"signal": "datum"}}}})
    dados = [
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
    ]
    if selecao:
        dados.append({"name": "marcados", "source": "pontos",
                      "transform": [{"type": "filter", "expr": "datum.__selected__ == 'on'"}]})
    return {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": descricao,
        "width": {"signal": "pbiContainerWidth"}, "height": {"signal": "pbiContainerHeight"},
        "padding": 0, "autosize": {"type": "none", "contains": "padding"}, "background": None,
        "config": {"view": {"stroke": None}},
        "signals": sinais,
        "data": dados,
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
                 "encode": {"update": contorno}},
                {"type": "symbol", "name": "pontos", "from": {"data": "pontos"},
                 "encode": {"update": ponto,
                            "hover": {"stroke": {"value": "#1C1915"}, "strokeWidth": {"value": 1.6},
                                      "fillOpacity": {"value": 1},
                                      **({"strokeOpacity": {"value": 1}} if selecao else {})}}},
                *marcas_extra,
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
        ".rv .sob{top:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".rv .topo{top:30px;display:flex;align-items:flex-end;gap:22px}"
        ".rv .big{font-size:112px;font-weight:700;letter-spacing:-.04em;line-height:.92;"
        "font-variant-numeric:tabular-nums lining-nums}"
        ".rv .big.pos{font-size:96px}"
        ".rv .lado{padding-bottom:6px}.rv .lado .vv{font-size:32px;font-weight:700;letter-spacing:-.02em}"
        ".rv .lado .txt{margin-top:2px}"
        ".rv .mc{top:162px;font-size:27px;line-height:1.22}.rv .mc.l{font-size:23px}"
        ".rv .cp{top:236px;font-size:16px}.rv .cp b{font-weight:600}"
        f".rv .fatos{{top:{FATOS_TOPO}px}}"
        ".rv .fato{display:flex;align-items:center;gap:14px;padding:10px 0;border-top:1px dashed var(--areia)}"
        ".rv .fato>div:nth-child(2){flex:1;min-width:0}.rv .fato .lg{font-size:18px;font-weight:600;margin-top:2px;"
        "white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".rv .fato .lg small{font-size:14px;font-weight:400;color:var(--cinza);margin-left:6px}"
        # 4 px de respiro à direita: a tinta do "%" de 28 px passava 2–3 px da borda do visual em alguns valores
        # ("40,4%", "62,0%" na tela 06 com o Nordeste; cortes.py, 24/10/2026)
        ".rv .fato .vp{font-size:28px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums;"
        "padding-right:4px}"
        ".rv .ic{width:30px;height:30px;flex:none;background-size:contain;background-repeat:no-repeat;"
        "background-position:center}"
        f".rv .ic.f{{background-image:url({URL_MIDIA}/arte/icones/pino-{c}.png)}}"
        f".rv .ic.r{{background-image:url({URL_MIDIA}/arte/icones/pino-tinta.png);opacity:.6}}"
        f".rv .ic.g{{background-image:url({URL_MIDIA}/arte/icones/escola-tinta.png);opacity:.8}}"
    )


def _css_origem(L: dict) -> str:
    """Origem: uma entrada por região, cada uma com a raiz fixa do tamanho do visual SEM ponteiro (L114) e só os alvos
    (.hv, fixos, sem animação: L012) com ponteiro. O mouse numa região esmaece as outras e acende a linha dela (L054);
    a região clicada fica inteira e as outras esmaecem pela transparência do próprio visual."""
    c = L["tom"]
    return (
        ".og{pointer-events:none}"
        ".og .oc{position:absolute;left:10px;top:0;width:620px;height:272px}"
        ".og .oc>*{position:absolute}"
        ".og .ro{left:0;top:0;width:620px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".og .trilho{left:0;top:28px;width:620px;height:46px;background:var(--creme)}"
        ".og .fa{top:28px;height:46px;display:flex;align-items:center;padding-left:10px;box-sizing:border-box;"
        "box-shadow:inset -2px 0 0 var(--papel);overflow:hidden;white-space:nowrap}"
        ".og .fa span{font-size:15px;font-weight:600;color:var(--branco)}"
        f".og .o1{{background:var(--{c})}}"
        # tons pela mistura com o papel, não por opacidade: com opacity o rótulo da fatia clara apagava junto ("8%")
        f".og .o2{{background:color-mix(in srgb,var(--{c}) 78%,var(--papel))}}"
        f".og .o3{{background:color-mix(in srgb,var(--{c}) 60%,var(--papel))}}"
        f".og .o4{{background:color-mix(in srgb,var(--{c}) 45%,var(--papel))}}"
        f".og .o5{{background:color-mix(in srgb,var(--{c}) 32%,var(--papel))}}"
        ".og .o3 span,.og .o4 span,.og .o5 span{color:var(--tinta)}"
        ".og .resto{right:10px;top:41px;font-size:14px;color:var(--grafite)}"
        ".og .lfa{top:41px;font-size:15px;font-weight:600;color:var(--tinta);white-space:nowrap}"
        ".og .li{left:-10px;width:640px;height:30px;box-sizing:border-box;padding:0 10px;border-radius:4px;"
        "display:flex;align-items:center;gap:10px;font-size:16px;color:var(--grafite)}"
        ".og .li .sw{display:inline-block;width:11px;height:11px;flex:none}"
        ".og .li .nm{width:178px;color:var(--tinta);font-weight:600;white-space:nowrap;overflow:hidden;"
        "text-overflow:ellipsis}.og .li .a{flex:1;white-space:nowrap}.og .li .b{text-align:right;white-space:nowrap}"
        ".og .rk{left:0;width:620px;display:flex;align-items:baseline;gap:16px}"
        ".og .rk .n{font-size:44px;font-weight:700;letter-spacing:-.02em;min-width:112px;"
        "font-variant-numeric:tabular-nums lining-nums}"
        ".og .rk .t{font-size:16px;color:var(--tinta);line-height:1.3}"
        ".og .dica{left:0;top:250px;font-size:14px;color:var(--cinza)}"
        ".og .hv{pointer-events:auto;cursor:pointer}"
        ".og .vis{transition:opacity .15s ease,background-color .15s ease}"
        "#htmlContent:has(.hv:hover) .og:not(:has(.hv:hover)) .vis{opacity:.4}"
        "#htmlContent:has(.og:not(.fixo) .ro) .fixo{display:none}"
        ".og:has(.hv:hover) .li{background:rgba(203,189,162,.3);color:var(--tinta)}"
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
        ".lgm .dica{color:var(--cinza)}.lgm .dica b{color:var(--tinta);font-weight:600}"
    )


def _css_tt_regiao(L: dict) -> str:
    """Dossiê da região: ficha branca com clipe sobre o papel (o mesmo cartão do dossiê do candidato da tela 01)."""
    c = L["tom"]
    return (
        ".tt3r{position:fixed;inset:0;background:var(--papel)}"
        ".tt3r .ficha{position:absolute;left:14px;top:18px;right:14px;bottom:14px;background:var(--branco);"
        "border:1.5px solid var(--areia);box-shadow:3px 4px 0 rgba(28,25,21,.08)}"
        ".clipe{position:fixed;right:44px;top:4px;width:32px;transform:rotate(8deg);z-index:2}"
        ".ico{position:fixed;right:30px;top:42px;width:36px;opacity:.85;z-index:2}"
        ".tt3r .cab{position:absolute;left:18px;top:14px;right:60px}"
        ".tt3r .nm{font-size:21px;font-weight:700;line-height:1.15;letter-spacing:-.01em}"
        ".tt3r .cab .sub{margin-top:4px;font-size:15px;color:var(--grafite);white-space:nowrap}"
        ".tt3r .hd,.tt3r .ln{display:flex;align-items:center;gap:8px}"
        ".tt3r .hd{position:absolute;left:18px;right:18px;top:74px;font-size:11px;font-weight:600;letter-spacing:.08em;"
        "text-transform:uppercase;white-space:nowrap;color:var(--cinza);border-bottom:1px dashed var(--areia);padding-bottom:5px}"
        ".tt3r .lista{position:absolute;left:18px;right:18px;top:102px}"
        ".tt3r .ln{font-size:14px;border-bottom:1px solid var(--creme)}"
        ".tt3r .uf{width:152px;flex:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--tinta)}"
        ".tt3r .br{width:102px;flex:none;display:flex;align-items:center;gap:6px}"
        ".tt3r .br i{display:block;height:10px;flex:none}.tt3r .br b{font-weight:700;font-size:14px}"
        f".tt3r .{L['cls']}-bg{{background:var(--{c})}}"
        ".tt3r .pc{width:54px;flex:none;text-align:right;font-weight:600;font-variant-numeric:tabular-nums}"
        ".tt3r .dd{flex:1;text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--grafite)}"
        f".tt3r .dd.pos{{color:var(--{c}-escuro)}}"
        ".tt3r .hd .br,.tt3r .hd .pc,.tt3r .hd .dd{font-weight:600;color:var(--cinza)}"
        ".tt3r .mao{position:absolute;right:20px;bottom:6px;font-size:26px;transform:rotate(-2deg)}"
        ".tt3r .neutro{color:var(--grafite)}"
    )


def declarar_votos(P: str) -> list:
    import pagina_lib
    import pbip_lib as lib
    from pbip_lib import Interacao, Pagina, Visual
    L = LADOS[P]
    css = "Estilo · CSS"
    z = lib.CAMADAS["conteudo"]
    tt, ttr = L["tooltip"], L["tt_regiao"]
    spec = f"spec/{P.lower()}_mapa.json"
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"),
              lib.campo_medida("x", f"{P} · x do município"), lib.campo_medida("y", f"{P} · y do município"),
              lib.campo_medida("uf", f"{P} · UF do município"),
              lib.campo_medida("tam", f"{P} · votos (municípios)"), lib.campo_medida("val", f"{P} · margem")]
    mapa = lib.visual_deneb(f"{P}_Mapa_Pontos", *MAPA, spec, campos, alt=lib.medida(f"{P} · Mapa · ALT"), z=z + 2,
                            tab=200, tooltip_pagina=tt, renderizacao="canvas", selecao=True, max_selecao=1,uf_por_codigo=True)
    # L123: o clique num ponto não recompila a vista (a entrada do mapa não se repete a cada clique)
    mapa["visual"]["objects"]["dataLimit"] = [{"properties": {"enableIncrementalDataUpdates": lib.lit(True)}}]
    clipe = f"{URL_MIDIA}/arte/dossie/clipe-tinta.png"
    icone = f"{URL_MIDIA}/arte/icones/barras-{L['tom']}.png"
    corpo_tt_regiao = (f"<style>{_css_tt_regiao(L)}</style>{{{{content}}}}"
                       f"<img class='clipe' alt='' src='{clipe}'/><img class='ico' alt='' src='{icone}'/>")
    itens = [
        Visual(P, lib.visual_html(f"{P}_Resumo_Html", *RESUMO, f"{P} · Resumo · HTML", folha_de_estilo=css, z=z,
                                  tab=100, alt=lib.medida(f"{P} · Resumo · ALT"),
                                  modelo_corpo=f"<style>{_css_resumo(L)}</style>" + "{{content}}")),
        Visual(P, lib.visual_html(f"{P}_Origem_Html", *ORIGEM, f"{P} · Origem · HTML", folha_de_estilo=css, z=z + 1,
                                  tab=150, alt=lib.medida(f"{P} · Origem · ALT"), granularidade=("UF", "Região"),
                                  filtro_cruzado=True, transparencia_nao_selecionados=True, tooltip_pagina=ttr,
                                  modelo_corpo=f"<style>{_css_origem(L)}</style>{ORIGEM_FIXO}" + "{{content}}")),
        Visual(P, mapa),
        Visual(P, lib.visual_html(f"{P}_Mapa_Legenda", *LEGENDA, f"{P} · Legenda · HTML", folha_de_estilo=css,
                                  z=z + 4, tab=210, alt=lib.medida(f"{P} · Legenda · ALT"),
                                  modelo_corpo=f"<style>{_css_legenda(L)}</style>" + "{{content}}")),
        Pagina(lib.pagina_tooltip(tt, f"Município · {L['cand']}", altura=TT_H, largura=TT_W), ordem=L["ordem_tt"]),
        Visual(tt, lib.visual_html(f"TT_{tt[2:]}_Conteudo", 0, 0, TT_W, TT_H, f"{P} · Tooltip município · HTML",
                                   alt=lib.medida(f"{P} · Tooltip município · ALT"), pagina_wh=(TT_W, TT_H),
                                   folha_de_estilo=css)),
        *pagina_lib.tooltip(ttr, f"Região · {L['cand']}", TTR_W, TTR_H, f"{P} · Tooltip região · HTML",
                            ordem=L["ordem_tt_regiao"], folha_de_estilo=css, modelo_corpo=corpo_tt_regiao),
    ]
    # filtro cruzado (DataFilter explícito: o Deneb aceitaria realce, que deixaria o mapa inteiro com a região só
    # destacada): o mapa e a origem filtram as outras peças; ninguém filtra o VizuFilter de estado da casca
    pecas = [f"{P}_Mapa_Pontos", f"{P}_Origem_Html"]
    leitores = [f"{P}_Resumo_Html", f"{P}_Mapa_Legenda"]
    for origem in pecas:
        for alvo in pecas + leitores:
            if alvo != origem:
                itens.append(Interacao(P, origem, alvo, "DataFilter"))
        itens.append(Interacao(P, origem, f"{P}_Casca_Filtro", "NoFilter"))
        itens.append(Interacao(P, origem, f"{P}_Filtro_Momento", "NoFilter"))
    return itens


def main() -> int:
    for P, L in LADOS.items():
        G = Gravador(L["pasta"])
        contas(P, L, G)
        desenho(P, L, G)
        apagados = G.limpar()
        gravar_spec(f"{P.lower()}_mapa.json", spec_mapa(
            "margem", L["cores"], f"Tela {P[1:]}: um ponto por município (tamanho = votos de {L['cand']}, cor = margem "
            f"de {L['cand']}); contorno das UFs em traço; pontos em onda a partir do centro dos votos; clique num "
            "ponto marca o município e filtra o painel.", selecao=True))
        print(G.resumo(), "· apagados:", [p.name for p in apagados])
    return 0


if __name__ == "__main__":
    sys.exit(main())
