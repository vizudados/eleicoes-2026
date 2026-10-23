# -*- coding: utf-8 -*-
"""19 · Explorador — onde está a minha pergunta? Explore os 5.571 municípios (dono: tela 19)

  T19_Filtro_Pilula     a pílula do filtro do recorte (HTML, na caixa do filtro da casca, 1282, 60, 424 × 48): "Todos
                        os municípios" sem escolha; com escolha, o recorte em poucas palavras ("Nordeste · até 10 mil
                        hab.") ou "N filtros", com o funil e o ponto vermelho
  T19_Filtro_Abre/Fora  botão sobre a pílula (abre o filtro, T19_FILTRO_ABRE_01) e o véu da tela inteira que fecha
                        (T19_FILTRO_FECHA_01)
  T19_Filtro_Recorte    VizuFilter alto e oculto, já aberto (alwaysOpen), no layout Acordeão da casa: árvore em modo
                        caminho sobre T19 Filtro[Caminho], uma raiz por grupo — Região, Estado, Tamanho da cidade, Renda
                        (quinto), Virou? e Cidade (os 5.571, com a busca) —, seleção múltipla e "Limpar"
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

O filtro do recorte (23/10/2026, pedido do dono: "estilo acordeon de filtro, no mesmo local que os filtros sempre
ficam; daí dá pra aumentar a altura dos gráficos"): no lugar da faixa de seis segmentações nativas, um filtro só, no
padrão da casca (paginas/casca.py › _filtro; o mesmo da T20): fechado, a tela mostra só a pílula e o botão sobre ela; o
clique mostra o VizuFilter alto por cima e o véu em volta. A T19 Filtro não filtra o Município (relação inativa: um
filtro numa coluna só daria OU entre os grupos): a lista e a dispersão filtram por [T19 · no recorte] = 1 (E entre os
grupos, OU dentro do mesmo grupo) e o resumo conta só os municípios no recorte. A pílula mostra "Todos os municípios", o
recorte em poucas palavras ou "N filtros". A gaveta não apaga itens incompatíveis com as outras escolhas (papel
"Disponibilidade" fora): o VizuFilter não enxerga a própria seleção na consulta dele. A chegada (T19_CHEGADA_01, da
casca, por FILTROS_PROPRIOS) deixa o filtro fechado.

Interações (só as exceções): a lista e a dispersão não filtram o filtro nem a pílula; a lista destaca (realce) a
dispersão e não mexe no resumo nem na manchete da dispersão.

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
from pbip_lib import Bookmark, Interacao, Visual

P = "T19"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]
TT = "ttT19Municipio"

RESUMO = (150, 140, 700, 104)
LISTA = (150, 252, 700, D.LISTA_CAB + D.LISTA_LINHAS * D.LISTA_H)          # até y 992
DISPERSAO = (890, 140, D.DISP_W, D.DISP_H)                                 # até y 1000

# O filtro do recorte no padrão da casca (pílula + VizuFilter alto + véu), na mesma caixa do filtro de UF das outras
# telas. Aberto, a caixa vai até y 840: seis raízes de 48 px, o "Limpar", a busca e ~9 linhas da raiz aberta.
FILTRO = (1282, 60, 424, 48)
FILTRO_ABERTO = (1282, 60, 424, 780)
FILTRO_FORA = (0, 0, 1920, 1080)
Z_FILTRO = lib.CAMADAS["drawer"]
NOMES_FILTRO = {"lista": f"{P}_Filtro_Recorte", "pilula": f"{P}_Filtro_Pilula", "abre": f"{P}_Filtro_Abre",
                "fora": f"{P}_Filtro_Fora"}
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
    c = estilo.COR
    x, y, w, h = FILTRO_ABERTO
    hp = FILTRO[3]
    geral = {"mode": "dropdown", "treeCategoryHeader": True, "listLayout": "accordion", "pathMode": True,
             "pathSeparator": " › ", "singleSelect": False, "sortAscending": False, "startOpen": True,
             "alwaysOpen": True, "showSearch": True, "searchScope": "category", "searchPlaceholder": "Digite para buscar",
             "showSelectAll": False, "showReset": True, "showSelectedCount": False, "showSelectedValue": False,
             "triggerMode": "count", "triggerCountStyle": "text", "triggerLabel": "Todos os municípios",
             "triggerCountFormat": "Filtros em uso: {n}", "syncSelectionWithHost": True}
    layout = {"controlWidth": w, "controlHeight": hp, "dropdownWidth": w, "dropdownHeight": h - hp - 6, "gap": 6,
              "optionHeight": 36, "searchHeight": 40, "triggerIconGap": 12, "borderRadius": 6, "checkboxSize": 16,
              "checkboxRadius": 3, "scrollbarWidth": 4, "wrapOptionLabels": False}
    lista, pilula, abre, fora = (NOMES_FILTRO[k] for k in ("lista", "pilula", "abre", "fora"))
    return [
        Visual(P, lib.visual_html(pilula, *FILTRO, "T19 · Filtro · pílula · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{casca.CSS_PILULA}</style>{{{{content}}}}",
                                  alt=lib.medida("T19 · Filtro · ALT"), z=Z_FILTRO - 20, tab=4, movimento=False)),
        Visual(P, lib.visual_botao(abre, *FILTRO, lib.acao_bookmark(f"{P}_FILTRO_ABRE_01"),
                                   dica="Filtrar os municípios: região, estado, tamanho, renda, quem virou ou cidade",
                                   z=lib.CAMADAS["navegacao"], tab=5, realce=c["tinta"], raio=6,
                                   realce_transp=(90, 82))),
        Visual(P, lib.visual_botao(fora, *FILTRO_FORA, lib.acao_bookmark(f"{P}_FILTRO_FECHA_01"),
                                   dica="Fechar o filtro", z=Z_FILTRO - 10, tab=7, oculto=True, raio=0,
                                   fundo=(c["tinta"], 90))),
        Visual(P, lib.visual_vizufilter(
            lista, x, y, w, h, categoria=("T19 Filtro", "Caminho", "Filtro"), geral=geral, layout=layout,
            estilo=_estilo_acordeao(), alt="Filtro do recorte em acordeão: região, estado, tamanho da cidade, renda, "
            "quem virou e cidade (com busca); vários itens no mesmo grupo somam, grupos diferentes se combinam",
            z=Z_FILTRO, tab=6, oculto=True, medidas={"itemSort": "T19 · filtro · ordem"})),
        Bookmark(lib.bookmark_exibicao(f"{P}_FILTRO_ABRE_01", P, {lista: True, fora: True, abre: False},
                                       titulo=f"{P} · filtro aberto"), grupo=("Filtros", "Filtros")),
        Bookmark(lib.bookmark_exibicao(f"{P}_FILTRO_FECHA_01", P, {lista: False, fora: False, abre: True},
                                       titulo=f"{P} · filtro fechado"), grupo=("Filtros", "Filtros")),
    ]


def _dispersao() -> dict:
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"),
              lib.campo_coluna("renda", "Município", "Renda per capita"),
              lib.campo_medida("var", "T19 · variação da margem"),
              lib.campo_medida("m26", "T19 · margem 2026"),
              lib.campo_medida("val", "T19 · válidos 2026")]
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
    # exceções de interação: a lista e a dispersão não mexem no filtro nem na pílula (a pílula só mostra o filtro)
    for origem in ("T19_Dispersao_Pontos", "T19_Lista_Html"):
        for alvo in (NOMES_FILTRO["lista"], NOMES_FILTRO["pilula"]):
            itens.append(Interacao(P, origem, alvo, "NoFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Dispersao_Pontos", "HighlightFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Resumo_Html", "NoFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Dispersao_Fundo", "NoFilter"))
    return itens
