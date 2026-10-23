# -*- coding: utf-8 -*-
"""20 · Escola — como votou cada escola de Contagem? (dono: tela 20)

Do país à escola: Lula ficou à frente em 12 dos 112 locais de votação de Contagem em 2026 (eram 27 em 2022). A
Escola Estadual Nova Contagem-I, onde o documentário começa, virou: Lula +10,3 p.p. em 2022 → Flávio +0,7 em 2026.

  T20_Filtro_Pilula     a pílula do filtro de escola (HTML, na caixa do filtro da casca): a escola escolhida no filtro
  T20_Filtro_Abre/Fora  botão sobre a pílula (abre o filtro, T20_FILTRO_ABRE_01) e o véu que fecha (T20_FILTRO_FECHA_01)
  T20_Filtro_Escola     VizuFilter alto e oculto sobre T20 Local[Local] (busca pelo nome, aberto quando aparece): leva a
                        escola à ficha e ao anel do mapa (não filtra o mapa, a lista nem a resposta)
  T20_Resposta_Html     "12 de 112" (contador), a manchete com os 27 de 2022 e quantos viraram
  T20_Ficha_Html        a ficha (post-it com alfinete) da escola escolhida, ou da Nova Contagem-I sem escolha: Lula ×
                        Flávio em 2026 e a margem de Lula 2018 → 2022 → 2026, selo de quem virou
  T20_Mapa_Escolhido    camada atrás dos pontos: o anel à mão em volta da escola da ficha, com o nome
  T20_Mapa_Html         o mapa de Contagem: o contorno se desenha em rabisco, o creme esmaece e os 110 pontos com
                        endereço brotam do oeste para o leste (granularidade T20 Local[Local]); tooltip: post-it
                        (ttT20Escola); clique leva a escola à ficha
  T20_Quedas_Html       as 5 maiores quedas da margem de Lula 2022 → 2026 (Top 5, clicáveis)
  T20_Como_Html         como explorar e a legenda (fixo)

Medidas em pbi/dax/T20 Escola (desenho gerado por pbi/scripts/desenho_t20.py); contorno em pbi/spec/t20_contagem.json.
"""
from __future__ import annotations

import desenho_t20 as D
import estilo
import pagina_lib
import pbip_lib as lib
import roteiro
from pbip_lib import Bookmark, Interacao, Visual

P = "T20"
CSS = "Estilo · CSS"
VAZIO = "Casca · vazio"
Z = lib.CAMADAS["conteudo"]
TT = "ttT20Escola"

FILTRO = (1282, 60, 424, 48)
RESPOSTA = (150, 140, 550, 270)
FICHA = (150, 430, 550, 570)
MAPA = (730, 140, D.MAPA_W, D.MAPA_H)
QUEDAS = (1452, 140, 318, D.QUEDAS_TOPO + 5 * D.QUEDAS_H)
COMO = (1452, 690, 318, 310)


# O filtro de escola no padrão da casca (paginas/casca.py › _filtro, 23/10/2026; o mesmo da T15): fechado, a tela mostra
# só a pílula (HTML com a escola em uso) e um botão nativo sobre ela; o clique aplica T20_FILTRO_ABRE_01, que mostra o
# VizuFilter alto já aberto (alwaysOpen) por cima e o véu em volta; o véu fecha (T20_FILTRO_FECHA_01). Fechado, só a
# pílula pega o mouse (antes, a lista abria dentro de uma caixa de 48 px e a caixa alta pegaria o mouse do mapa).
FILTRO_ABERTO = (1282, 60, 424, 626)     # a mesma caixa do filtro de UF da casca, aberto
FILTRO_FORA = (0, 0, 1920, 1080)
Z_FILTRO = lib.CAMADAS["drawer"]
NOMES_FILTRO = {"lista": f"{P}_Filtro_Escola", "pilula": f"{P}_Filtro_Pilula", "abre": f"{P}_Filtro_Abre",
                "fora": f"{P}_Filtro_Fora"}


def _filtro() -> list:
    from paginas import casca      # só a folha da pílula e os tokens do VizuFilter (a casca não é editada aqui)
    c = estilo.COR
    x, y, w, h = FILTRO_ABERTO
    hp = FILTRO[3]
    geral = {"mode": "dropdown", "singleSelect": True, "singleSelectAllowAll": True, "sortAscending": True,
             "startOpen": True, "alwaysOpen": True, "showSearch": True, "showSelectAll": False, "showReset": False,
             "showSelectedCount": False, "showSelectedValue": True, "selectedValueOnly": True,
             "syncSelectionWithHost": True, "triggerMode": "value", "triggerLabel": "Escola",
             "placeholderText": "Escolha uma escola", "allOptionText": "Nenhuma (volta ao exemplo)",
             "searchPlaceholder": "Buscar escola pelo nome", "searchScope": "list", "pathMode": False}
    layout = {"controlWidth": w, "controlHeight": hp, "dropdownWidth": w, "dropdownHeight": h - hp - 6, "gap": 6,
              "optionHeight": 40, "searchHeight": 44, "triggerIconGap": 12, "borderRadius": 6, "checkboxSize": 14,
              "checkboxRadius": 2, "scrollbarWidth": 4, "wrapOptionLabels": False}
    est = {**casca._estilo_filtro(roteiro.POR_CODIGO[P]), "optionFontSize": 15}
    lista, pilula, abre, fora = (NOMES_FILTRO[k] for k in ("lista", "pilula", "abre", "fora"))
    return [
        Visual(P, lib.visual_html(pilula, *FILTRO, "T20 · Filtro · pílula · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{casca.CSS_PILULA}</style>{{{{content}}}}",
                                  alt=lib.medida("T20 · Filtro · ALT"), z=Z_FILTRO - 20, tab=4, movimento=False)),
        Visual(P, lib.visual_botao(abre, *FILTRO, lib.acao_bookmark(f"{P}_FILTRO_ABRE_01"),
                                   dica="Escolher uma escola pelo nome", z=lib.CAMADAS["navegacao"], tab=5,
                                   realce=c["tinta"], raio=6, realce_transp=(90, 82))),
        Visual(P, lib.visual_botao(fora, *FILTRO_FORA, lib.acao_bookmark(f"{P}_FILTRO_FECHA_01"),
                                   dica="Fechar o filtro", z=Z_FILTRO - 10, tab=7, oculto=True, raio=0,
                                   fundo=(c["tinta"], 90))),
        Visual(P, lib.visual_vizufilter(
            lista, x, y, w, h, categoria=("T20 Local", "Local", "Escola"), geral=geral, layout=layout, estilo=est,
            alt="Filtro de escola: escolha um local de votação de Contagem para a ficha", z=Z_FILTRO, tab=6,
            oculto=True)),
        Bookmark(lib.bookmark_exibicao(f"{P}_FILTRO_ABRE_01", P, {lista: True, fora: True, abre: False},
                                       titulo=f"{P} · filtro aberto"), grupo=("Filtros", "Filtros")),
        Bookmark(lib.bookmark_exibicao(f"{P}_FILTRO_FECHA_01", P, {lista: False, fora: False, abre: True},
                                       titulo=f"{P} · filtro fechado"), grupo=("Filtros", "Filtros")),
    ]


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
        Visual(P, lib.visual_html("T20_Quedas_Html", *QUEDAS, "T20 · Quedas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_quedas(), alt=lib.medida("T20 · Quedas · ALT"), z=Z + 20,
                                  tab=130, granularidade=("T20 Local", "Local"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina=TT,
                                  ordenacao=[lib.ordem_medida("T20 · queda da margem", "Descending")],
                                  filtros=lib.filtro_visual_topn("t20Top5", "T20 Local", "Local",
                                                                 "T20 · queda da margem", 5))),
        Visual(P, lib.visual_html("T20_Como_Html", *COMO, VAZIO, folha_de_estilo=CSS, modelo_corpo=D.corpo_como(),
                                  alt="Como explorar a tela e a legenda do mapa", z=Z + 21, tab=140)),
        *pagina_lib.tooltip(TT, "Escola · post-it", 420, 270, "T20 · Tooltip escola · HTML", ordem=300,
                            folha_de_estilo=CSS, modelo_corpo=D.corpo_tooltip()),
    ]
    # exceções: quem escolhe a escola (filtro, mapa, lista) só mexe na ficha e no anel; a pílula mostra só o que o
    # filtro escolheu (o clique no mapa ou na lista leva a escola à ficha, não ao filtro)
    for origem in ("T20_Filtro_Escola", "T20_Mapa_Html", "T20_Quedas_Html"):
        for alvo in ("T20_Filtro_Escola", "T20_Mapa_Html", "T20_Quedas_Html", "T20_Resposta_Html"):
            if origem != alvo:
                itens.append(Interacao(P, origem, alvo, "NoFilter"))
    for origem in ("T20_Mapa_Html", "T20_Quedas_Html"):
        itens.append(Interacao(P, origem, NOMES_FILTRO["pilula"], "NoFilter"))
    return itens
