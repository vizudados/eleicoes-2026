# -*- coding: utf-8 -*-
"""19 · Explorador — onde está a minha pergunta? Explore os 5.571 municípios (dono: tela 19)

  T19_Filtro_Recorte    o filtro do recorte: o próprio VizuFilter, visível, na caixa do filtro da casca (1282, 60, 424 ×
                        780: a lista abre dentro dela), ATRÁS do conteúdo (z 20, lib.CAMADAS["filtro"]; a dispersão por
                        cima segue com o mouse), com o gatilho dele: "Todos os municípios" sem escolha; com escolha, o
                        resumo de cima para baixo por grupo ("Nordeste · até 10 mil", "3 cidades"; VizuFilter 2.14,
                        triggerPathSummary) e o funil com o ponto vermelho. Árvore (modo caminho sobre T19
                        Filtro[Caminho]): o lugar numa hierarquia só — Região › Estado › Cidade, o filtro cai na
                        cidade — e os grupos Tamanho da cidade, Renda (quinto) e Virou?; busca no topo, seleção
                        múltipla e "Limpar"
  T19_Resumo_Html       o recorte em palavras e os contadores: municípios, com Lula à frente, com Flávio à frente, que
                        viraram, com a barra da proporção
  T19_Lista_Html        os 16 municípios do recorte com mais votos válidos (granularidade Município[Rótulo], Top 16 por
                        [T19 · válidos no recorte]): Lula e Flávio em 2026, a minilinha 2006–2026, a mudança 2022 →
                        2026, o selo de quem virou. Passar o mouse: dossiê (ttT19Municipio). Clique: destaca o ponto
  T19_Dispersao_Fundo   o fundo da dispersão (HTML atrás do Deneb, mesma caixa e mesma geometria): título, manchete do
                        recorte (Lula perdeu margem em N de M), grade, eixos, legenda, dica e a nota à mão
  T19_Dispersao_Pontos  Deneb (Vega 6, canvas, seleção avançada): um ponto por município do recorte, renda (log) ×
                        mudança da margem; arrastar desenha um retângulo que filtra a página (pbiCrossFilterApply, até
                        2.500 municípios); clique num ponto filtra só ele; clique no vazio limpa. Dossiê no hover

O filtro do recorte (23/10/2026, pedido do dono: "no mesmo local que os filtros sempre ficam; daí dá pra aumentar a
altura dos gráficos"; o acordeão, com região, estado e cidade em grupos separados, foi reprovado: "se resolve a questão
da hierarquia jogando o filtro no último na hierarquia"): no lugar da faixa de seis segmentações nativas, um filtro só, no
padrão da casca (paginas/casca.py › _filtro; o mesmo da T20): o próprio VizuFilter, sem pílula, botão, véu nem
marcador (24/10/2026: "eu pedi que o filtro não fosse um botão que ativa ao clicar"). A T19 Filtro não filtra o
Município (relação inativa: um
filtro numa coluna só daria OU entre os grupos): a lista e a dispersão filtram por [T19 · no recorte] = 1 (E entre os
grupos, OU dentro do mesmo grupo) e o resumo conta só os municípios no recorte. A gaveta não apaga itens incompatíveis
com as outras escolhas (papel "Disponibilidade" fora): o VizuFilter não enxerga a própria seleção na consulta dele. O
filtro nasce recolhido (startOpen e alwaysOpen desligados); a chegada (T19_CHEGADA_01, da casca) não mexe nele.

Interações (só as exceções): a lista e a dispersão não filtram o filtro; a lista destaca (realce) a dispersão e não mexe
no resumo nem na manchete da dispersão.

Medidas em pbi/dax/T19 Explorador (desenho gerado por pbi/scripts/desenho_t19.py); spec em pbi/spec/t19_dispersao.json;
tabela do filtro em pbi/modelo/t19_filtro.py.
"""
from __future__ import annotations

import json

import desenho_t19 as D
import estilo
import pagina_lib
import pbip_lib as lib
import roteiro
from pbip_lib import Interacao, Visual

P = "T19"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]
TT = "ttT19Municipio"

RESUMO = (150, 140, 700, 104)
LISTA = (150, 252, 700, D.LISTA_CAB + D.LISTA_LINHAS * D.LISTA_H)          # até y 992
DISPERSAO = (890, 140, D.DISP_W, D.DISP_H)                                 # até y 1000

# O filtro do recorte no padrão da casca (o próprio VizuFilter, atrás do conteúdo, na caixa do filtro de UF das outras
# telas). Aberto, a caixa vai até y 840: quatro raízes, o "Limpar", a busca e ~13 linhas da raiz aberta.
FILTRO_CAIXA = (1282, 60, 424, 780)
Z_FILTRO = lib.CAMADAS["filtro"]
NOME_FILTRO = f"{P}_Filtro_Recorte"
NO_RECORTE = "T19 · no recorte"


def _so_no_recorte(nome: str) -> dict:
    """filterConfig de visual: [T19 · no recorte] = 1 (filtro de medida, oculto e travado no modo leitura)."""
    m = {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": NO_RECORTE}}
    return {"filters": [{
        "name": nome, "field": lib.campo_medida_expr(NO_RECORTE), "type": "Advanced",
        "filter": {"Version": 2, "From": [{"Name": "m", "Entity": lib.TABELA_MEDIDAS, "Type": 0}],
                   "Where": [{"Condition": {"Comparison": {"ComparisonKind": 0, "Left": m,
                                                           "Right": {"Literal": {"Value": "1L"}}}}}]},
        "isHiddenInViewMode": True, "isLockedInViewMode": True}]}


def _estilo_acordeao() -> dict:
    from paginas import casca      # os tokens do VizuFilter da casca (a casca não é editada aqui)
    c = estilo.COR
    return {**casca._estilo_filtro(roteiro.POR_CODIGO[P]), "optionFontSize": 15,
            "selectedBackgroundColor": c["papel"], "checkboxColor": c["tinta"], "checkboxMarkColor": c["branco"],
            "checkboxBorderColor": c["cinza"], "openCategoryHighlight": "pill",
            "openCategoryBackgroundColor": c["papel"], "dividerColor": c["creme"], "mutedTextColor": c["cinza"],
            "scrollbarThumbColor": c["areia"]}


def _filtro() -> list:
    from paginas import casca
    # árvore (não acordeão, 23/10/2026: no acordeão, abrir um grupo fechava o outro — "não aprovado"): o lugar é
    # uma hierarquia só, Região › Estado › Cidade, e o filtro cai na cidade (marcar uma região ou um estado marca as
    # cidades de dentro); os grupos abrem e fecham cada um por si; a busca, no topo, procura em todos (5.571 cidades).
    # O gatilho resume a escolha de cima para baixo em cada grupo (VizuFilter 2.14, triggerPathSummary): "Nordeste",
    # "Bahia", "3 cidades", "Nordeste · até 10 mil"; sem escolha, "Todos os municípios"
    geral = {"mode": "dropdown", "treeCategoryHeader": True, "listLayout": "standard", "pathMode": True,
             "pathSeparator": " › ", "singleSelect": False, "sortAscending": False, "startOpen": False,
             "alwaysOpen": False, "showSearch": True, "searchScope": "list",
             "searchPlaceholder": "Buscar região, estado ou cidade", "categoryHeaderStyle": "natural",
             "showSelectAll": False, "showReset": True, "showSelectedCount": False, "showSelectedValue": True,
             "selectedValueOnly": True, "triggerMode": "value", "triggerLabel": "Recorte",
             "placeholderText": "Todos os municípios", "triggerPathSummary": True, "triggerPathSummaryMax": 2,
             "triggerPathSummaryNoun": "Região, estado e cidade=cidade|cidades; Tamanho da cidade=tamanho|tamanhos; "
                                       "Renda (quinto)=faixa de renda|faixas de renda; Virou?=situação|situações",
             "syncSelectionWithHost": True}
    layout = casca.layout_filtro(FILTRO_CAIXA, optionHeight=36, searchHeight=40, checkboxSize=16, checkboxRadius=3)
    return [
        Visual(P, lib.visual_vizufilter(
            NOME_FILTRO, *FILTRO_CAIXA, categoria=("T19 Filtro", "Caminho", "Filtro"), geral=geral, layout=layout,
            estilo=_estilo_acordeao(), alt=lib.medida("T19 · Filtro · ALT"), z=Z_FILTRO, tab=4,
            medidas={"itemSort": "T19 · filtro · ordem"})),
    ]


def _dispersao() -> dict:
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"),
              lib.campo_coluna("renda", "Município", "Renda per capita"),
              lib.campo_medida("var", "T19 · variação da margem"),
              lib.campo_medida("m26", "T19 · margem 2026"),
              lib.campo_medida("val", "T19 · válidos 2026"),
              lib.campo_medida("pos", "Eleição · pós")]
    doc = lib.visual_deneb("T19_Dispersao_Pontos", *DISPERSAO, "spec/t19_dispersao.json", campos,
                           alt=lib.medida("T19 · Dispersão · ALT"), z=Z + 21, tab=210, selecao=True,
                           modo_selecao="advanced", max_selecao=2500, tooltip_pagina=TT, renderizacao="canvas")
    obj = doc["visual"]["objects"]
    # realce vindo da lista (HighlightFilter): o Deneb expõe val__highlightStatus
    obj["vega"][0]["properties"]["enableHighlight"] = lib.lit(True)
    sm = obj["stateManagement"][0]["properties"]
    suporte = json.loads(sm["supportFieldConfiguration"]["expr"]["Literal"]["Value"][1:-1].replace("''", "'"))
    suporte["val"].update({"highlight": True, "highlightStatus": True, "highlightComparator": True})
    sm["supportFieldConfiguration"] = lib.lit(json.dumps(suporte, ensure_ascii=False, separators=(",", ":")))
    # L123: a vista não é recompilada a cada filtro (a entrada não se repete)
    obj["dataLimit"] = [{"properties": {"enableIncrementalDataUpdates": lib.lit(True)}}]
    # só os municípios do recorte (o visual_deneb não recebe filtros: o filterConfig entra aqui)
    doc["filterConfig"] = _so_no_recorte("t19DispersaoRecorte")
    return doc


def declarar(ctx):
    filtros_lista = {"filters": lib.filtro_visual_topn("t19Top16", "Município", "Rótulo", "T19 · válidos no recorte",
                                                       D.LISTA_LINHAS)["filters"]
                     + _so_no_recorte("t19ListaRecorte")["filters"]}
    itens = [
        *_filtro(),
        Visual(P, lib.visual_html("T19_Resumo_Html", *RESUMO, "T19 · Resumo · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_resumo(), alt=lib.medida("T19 · Resumo · ALT"), z=Z + 1,
                                  tab=100)),
        Visual(P, lib.visual_html("T19_Lista_Html", *LISTA, "T19 · Lista · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_lista(), alt=lib.medida("T19 · Lista · ALT"), z=Z + 2,
                                  tab=110, granularidade=("Município", "Rótulo"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina=TT,
                                  ordenacao=[lib.ordem_medida("T19 · válidos 2026", "Descending")],
                                  filtros=filtros_lista)),
        Visual(P, lib.visual_html("T19_Dispersao_Fundo", *DISPERSAO, "T19 · Dispersão · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_dispersao(), alt="Eixos e legenda da dispersão", z=Z + 20,
                                  tab=200)),
        Visual(P, _dispersao()),
        *pagina_lib.tooltip(TT, "Município · dossiê", 460, 350, "T19 · Dossiê · HTML", ordem=290,
                            folha_de_estilo=CSS, modelo_corpo=D.corpo_dossie()),
    ]
    # exceções de interação: a lista e a dispersão não mexem no filtro
    for origem in ("T19_Dispersao_Pontos", "T19_Lista_Html"):
        itens.append(Interacao(P, origem, NOME_FILTRO, "NoFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Dispersao_Pontos", "HighlightFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Resumo_Html", "NoFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Dispersao_Fundo", "NoFilter"))
    return itens
