# -*- coding: utf-8 -*-
"""20 · Escola — como votou cada escola da cidade? (dono: tela 20)

Do país à escola, em 34 cidades (23/10/2026, pedido do dono: "eu não queria esse painel focado em contagem, não dá pra
variar ele mais?"): as 27 capitais, as 6 maiores que trocaram Lula por Flávio de 2022 para 2026 e Contagem. A tela
abre no Rio de Janeiro, não em Contagem (abrir onde o documentário de referência começa seria copiar o roteiro dele):
a margem da cidade quase não mexeu (−3,6 → −4,0 pontos), mas por dentro 31 locais viraram para Flávio e 35 para Lula.

  T20_Filtro_Escola     o filtro da tela: o próprio VizuFilter, visível, na caixa do filtro da casca (1282, 60, 424 × 780:
                        a lista abre dentro dela), ATRÁS do conteúdo (z 20, lib.CAMADAS["filtro"]; o mapa e a lista
                        por cima seguem com o mouse), com o gatilho dele: "Rio de Janeiro (RJ)" sem escolha; com
                        escolha, o resumo de cima para baixo ("São Paulo (SP)", o nome da escola, "3 escolas";
                        VizuFilter 2.14, triggerPathSummary) e o funil com o ponto vermelho. Sem pílula, botão, véu
                        nem marcador (24/10/2026). Em árvore (o mesmo da tela 21): uma hierarquia
                        só, Cidade e escola › cidade › escola, e o filtro cai na escola (regra do dono, 23/10/2026: "se
                        resolve a questão da hierarquia jogando o filtro no último na hierarquia"; o acordeão de duas
                        raízes foi reprovado na tela 21). Marcar a cidade marca as escolas dela = a tela vai para a
                        cidade; marcar uma escola = a cidade dela e a escola na ficha e no anel; várias escolas da mesma
                        cidade = a cidade, com o exemplo na ficha. Uma cidade por vez (exclusiveRoots: marcar escola de
                        outra cidade desmarca a anterior). Busca no topo, em cidades e escolas
  T20_Resposta_Html     a cidade, "12 de 112" (contador), quantos eram em 2022 e quantos viraram nos dois sentidos
  T20_Ficha_Html        a ficha (post-it com alfinete) da escola escolhida ou do exemplo da cidade: Lula × Flávio em
                        2026 e a margem de Lula 2018 → 2022 → 2026, selo de quem virou
  T20_Mapa_Escolhido    camada de trás: o contorno da cidade em rabisco (o creme esmaece), o mapinha da cidade inteira
                        nas cidades em recorte e o anel à mão em volta da escola da ficha, com o nome
  T20_Mapa_Html         os pontos da cidade (granularidade T20 Local[Local]; local de outra cidade sai vazio), que
                        brotam do oeste para o leste; o tamanho acompanha o espaço entre locais (São Paulo não vira
                        mancha); o último ponto leva os rótulos de bairro. Tooltip: post-it (ttT20Escola); clique leva a
                        escola à ficha
  T20_Quedas_Html       os locais da cidade, da maior queda à maior alta da margem de Lula 2022 → 2026 (a lista rola;
                        clicáveis; a ordem vem da posição, em order no CSS)
  T20_Como_Html         como explorar, a legenda e o aviso de quantos locais não aparecem no mapa

Medidas em pbi/dax/T20 Escola (desenho gerado por pbi/scripts/desenho_t20.py); tabelas em pbi/modelo/t20_locais.py;
dados de pipeline/exportar_t20.py.
"""
from __future__ import annotations

import desenho_t20 as D
import estilo
import pagina_lib
import pbip_lib as lib
import roteiro
from pbip_lib import Interacao, Visual

P = "T20"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]
TT = "ttT20Escola"
RAIZ = "Cidade e zona"   # a raiz única da árvore: a mesma de pbi/modelo/t20_locais.py (RAIZ) e de exclusiveRoots

RESPOSTA = (150, 140, 550, 270)
FICHA = (150, 430, 550, 570)
MAPA = (730, 140, D.MAPA_W, D.MAPA_H)
QUEDAS = (1452, 140, 318, D.QUEDAS_TOPO + 5 * D.QUEDAS_H)
COMO = (1452, 690, 318, 310)


# O filtro no padrão da casca (paginas/casca.py › _filtro; o mesmo da tela 21): o próprio VizuFilter, visível, atrás do
# conteúdo (lib.CAMADAS["filtro"]), com o gatilho dele; nasce recolhido e a chegada (T20_CHEGADA_01) não mexe nele.
FILTRO_CAIXA = (1282, 60, 424, 780)     # a busca, o Limpar e ~18 linhas da árvore
Z_FILTRO = lib.CAMADAS["filtro"]
NOME_FILTRO = f"{P}_Filtro_Escola"
CONTEUDO = ("T20_Resposta_Html", "T20_Ficha_Html", "T20_Mapa_Escolhido", "T20_Mapa_Html", "T20_Quedas_Html",
            "T20_Como_Html")


def _estilo_arvore() -> dict:
    from paginas import casca      # os tokens do VizuFilter da casca (a casca não é editada aqui)
    c = estilo.COR
    return {**casca._estilo_filtro(roteiro.POR_CODIGO[P]), "optionFontSize": 15,
            "selectedBackgroundColor": c["papel"], "checkboxColor": c["tinta"], "checkboxMarkColor": c["branco"],
            "checkboxBorderColor": c["cinza"], "openCategoryHighlight": "pill",
            "openCategoryBackgroundColor": c["papel"], "dividerColor": c["creme"], "mutedTextColor": c["cinza"],
            "scrollbarThumbColor": c["areia"]}


def _filtro() -> list:
    from paginas import casca      # o layout do VizuFilter da casca (gatilho de 48 px, a lista no resto da caixa)
    # árvore, como a da tela 21 (t19_explorador._filtro, testada no Desktop em 23/10/2026): seleção múltipla para o nó
    # da cidade ser marcável; exclusiveRoots com o nome da raiz deixa uma cidade por vez (no modo caminho o grupo é o
    # nível logo acima das folhas, a cidade). O gatilho resume a escolha (VizuFilter 2.14, triggerPathSummary): a
    # cidade inteira pelo nome, uma escola pelo nome, várias pela contagem ("3 escolas")
    geral = {"mode": "dropdown", "treeCategoryHeader": True, "listLayout": "standard", "pathMode": True,
             "pathSeparator": " › ", "singleSelect": False, "exclusiveRoots": RAIZ, "sortAscending": False,
             "startOpen": False, "alwaysOpen": False, "showSearch": True, "searchScope": "list",
             "searchPlaceholder": "Buscar cidade ou zona", "categoryHeaderStyle": "natural",
             "showSelectAll": False, "showReset": True, "showSelectedCount": False, "showSelectedValue": True,
             "selectedValueOnly": True, "triggerMode": "value", "triggerLabel": "Cidade e zona",
             "placeholderText": "Rio de Janeiro (RJ)", "triggerPathSummary": True, "triggerPathSummaryMax": 2,
             "triggerPathSummaryNoun": "zona|zonas", "syncSelectionWithHost": True}
    layout = casca.layout_filtro(FILTRO_CAIXA, optionHeight=36, searchHeight=40, checkboxSize=16, checkboxRadius=3)
    return [
        Visual(P, lib.visual_vizufilter(
            NOME_FILTRO, *FILTRO_CAIXA, categoria=("T20 Filtro", "Caminho", "Filtro"), geral=geral, layout=layout,
            estilo=_estilo_arvore(), alt=lib.medida("T20 · Filtro · ALT"), z=Z_FILTRO, tab=4,
            medidas={"itemSort": "T20 · filtro · ordem"})),
    ]


def _lista() -> dict:
    doc = lib.visual_html("T20_Quedas_Html", *QUEDAS, "T20 · Quedas · HTML", folha_de_estilo=CSS,
                          modelo_corpo=D.corpo_quedas(), alt=lib.medida("T20 · Quedas · ALT"), z=Z + 20, tab=130,
                          granularidade=("T20 Local", "Local"), filtro_cruzado=True,
                          transparencia_nao_selecionados=True, tooltip_pagina=TT,
                          ordenacao=[lib.ordem_medida("T20 · posição na queda", "Ascending")])
    # cada linha é a própria entrada do visual (rowTemplate {{row}}: com um elemento só, o HTML Content põe a classe
    # htmlViewerEntry nele), e o `order` que a linha traz ordena a lista no #htmlContent flexível
    doc["visual"]["objects"]["templates"][0]["properties"]["rowTemplate"] = lib.lit("{{row}}")
    return doc


def declarar(ctx):
    itens = [
        *_filtro(),
        Visual(P, lib.visual_html("T20_Resposta_Html", *RESPOSTA, "T20 · Resposta · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_resposta(), alt=lib.medida("T20 · Resposta · ALT"), z=Z,
                                  tab=100)),
        Visual(P, lib.visual_html("T20_Ficha_Html", *FICHA, "T20 · Ficha · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_ficha(), alt=lib.medida("T20 · Ficha · ALT"), z=Z + 1,
                                  tab=110)),
        Visual(P, lib.visual_html("T20_Mapa_Escolhido", *MAPA, "T20 · Escolhido · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_escolhido(), alt=lib.medida("T20 · Escolhido · ALT"),
                                  z=Z + 10, tab=121)),
        Visual(P, lib.visual_html("T20_Mapa_Html", *MAPA, "T20 · Mapa · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_mapa(), alt=lib.medida("T20 · Mapa · ALT"), z=Z + 11, tab=120,
                                  granularidade=("T20 Local", "Local"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina=TT)),
        Visual(P, _lista()),
        Visual(P, lib.visual_html("T20_Como_Html", *COMO, "T20 · Como · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_como(), alt=lib.medida("T20 · Como · ALT"), z=Z + 21,
                                  tab=140)),
        *pagina_lib.tooltip(TT, "Zona · post-it", 420, 270, "T20 · Tooltip escola · HTML", ordem=300,
                            folha_de_estilo=CSS, modelo_corpo=D.corpo_tooltip()),
    ]
    # exceções: o filtro (cidade e escola) chega a todos (a cidade filtra tudo pelas medidas; a escola só muda a
    # ficha e o anel). O clique no mapa ou na lista leva a escola à ficha e ao anel; não mexe no filtro, na resposta,
    # no aviso nem no outro visual de pontos
    for origem in ("T20_Mapa_Html", "T20_Quedas_Html"):
        for alvo in (NOME_FILTRO, "T20_Mapa_Html", "T20_Quedas_Html",
                     "T20_Resposta_Html", "T20_Como_Html"):
            if origem != alvo:
                itens.append(Interacao(P, origem, alvo, "NoFilter"))
    return itens
