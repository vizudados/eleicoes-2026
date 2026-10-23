# -*- coding: utf-8 -*-
"""19 · Explorador — onde está a minha pergunta? Explore os 5.571 municípios (dono: tela 19)

  T19_Filtros_Rotulos   os rótulos das seis segmentações (HTML fixo)
  T19_Regiao_Seletor … T19_Busca_Seletor   seis suspensas nativas: Região, Estado, Tamanho da cidade, Renda (quinto),
                        Virou? (T19 Lado) e Buscar cidade (Município[Rótulo], com busca); todas recolhidas, no mesmo
                        lugar, e filtram a página inteira
  T19_Resumo_Html       o recorte em palavras e os contadores: municípios, com Lula à frente, com Flávio à frente, que
                        viraram, com a barra da proporção
  T19_Lista_Html        os 14 municípios do recorte com mais votos válidos (granularidade Município[Rótulo], Top 14):
                        Lula e Flávio em 2026, a minilinha 2006–2026, a mudança 2022 → 2026, o selo de quem virou.
                        Passar o mouse: dossiê (ttT19Municipio). Clique: destaca o ponto na dispersão
  T19_Dispersao_Fundo   o fundo da dispersão (HTML atrás do Deneb, mesma caixa e mesma geometria): título, manchete do
                        recorte (Lula perdeu margem em N de M), grade, eixos, legenda, dica e a nota à mão
  T19_Dispersao_Pontos  Deneb (Vega 6, canvas, seleção avançada): um ponto por município, renda (log) × mudança da
                        margem; arrastar desenha um retângulo que filtra a página (pbiCrossFilterApply, até 2.500
                        municípios); clique num ponto filtra só ele; clique no vazio limpa. Dossiê no hover

Interações (só as exceções): a dispersão e a lista não filtram as segmentações; a lista destaca (realce) a dispersão e
não mexe no resumo nem na manchete da dispersão.

Medidas em pbi/dax/T19 Explorador (desenho gerado por pbi/scripts/desenho_t19.py); spec em pbi/spec/t19_dispersao.json.
"""
from __future__ import annotations

import json

import desenho_t19 as D
import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual

P = "T19"
CSS = "Estilo · CSS"
VAZIO = "Casca · vazio"
Z = lib.CAMADAS["conteudo"]
TT = "ttT19Municipio"

ROTULOS = (150, 140, 1620, 18)
Y_SEL, H_SEL = 160, 40
SELETORES = [  # nome, x, largura, tabela, coluna, rótulo, alt, busca
    ("T19_Regiao_Seletor", 150, 210, "UF", "Região", "Região",
     "Filtro de região: Norte, Nordeste, Centro-Oeste, Sudeste ou Sul", False),
    ("T19_Estado_Seletor", 372, 230, "UF", "Nome", "Estado", "Filtro de estado", False),
    ("T19_Porte_Seletor", 614, 250, "Município", "Porte", "Tamanho da cidade",
     "Filtro do tamanho da cidade pela população", False),
    ("T19_Renda_Seletor", 876, 220, "Município", "Quinto de renda", "Renda",
     "Filtro do quinto de renda da cidade (dos 20% mais pobres aos 20% mais ricos)", False),
    ("T19_Virou_Seletor", 1108, 240, "T19 Lado", "Lado", "Virou?",
     "Filtro de quem virou: de Lula para Flávio, Lula nas duas, Bolsonaro nas duas", False),
    ("T19_Busca_Seletor", 1360, 410, "Município", "Rótulo", "Cidade", "Buscar uma ou mais cidades pelo nome", True),
]
RESUMO = (150, 220, 700, 104)
LISTA = (150, 330, 700, D.LISTA_CAB + D.LISTA_LINHAS * D.LISTA_H)
DISPERSAO = (890, 222, D.DISP_W, D.DISP_H)


def _tokens() -> dict:
    c = estilo.COR
    return {"fundo": c["branco"], "texto": c["tinta"], "borda": c["areia"], "seta": c["grafite"], "marca": c["tinta"],
            "pesquisa_fundo": c["branco"], "pesquisa_borda": c["areia"]}


def _seletores() -> list:
    itens = []
    so_ufs = lib.filtro_visual_categorico("t19SoUFs", "UF", "Tipo", ["UF"])
    for i, (nome, x, w, tab, col, rot, alt, busca) in enumerate(SELETORES):
        doc = lib.segmentacao(nome, x, Y_SEL, w, H_SEL, tabela=tab, coluna=col, rotulo=rot, alt=alt,
                              grupo=f"t19{nome.split('_')[1].lower()}", modo="Dropdown", pesquisa=busca,
                              tokens=_tokens(), corpo_pt=12, tab=20 + i)
        if tab == "UF":
            doc["filterConfig"] = json.loads(json.dumps(so_ufs))
            for f in doc["filterConfig"]["filters"]:
                f["name"] = f"t19SoUFs{i}"
                f["isHiddenInViewMode"] = True
                f["isLockedInViewMode"] = True
        itens.append(Visual(P, doc))
    return itens


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
    return doc


def declarar(ctx):
    seletores = [s[0] for s in SELETORES]
    itens = [
        Visual(P, lib.visual_html("T19_Filtros_Rotulos", *ROTULOS, VAZIO, folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_rotulos(), alt="Rótulos dos filtros da tela", z=Z, tab=10,
                                  movimento=False)),
        *_seletores(),
        Visual(P, lib.visual_html("T19_Resumo_Html", *RESUMO, "T19 · Resumo · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_resumo(), alt=lib.medida("T19 · Resumo · ALT"), z=Z + 1,
                                  tab=100)),
        Visual(P, lib.visual_html("T19_Lista_Html", *LISTA, "T19 · Lista · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_lista(), alt=lib.medida("T19 · Lista · ALT"), z=Z + 2,
                                  tab=110, granularidade=("Município", "Rótulo"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina=TT,
                                  ordenacao=[lib.ordem_medida("T19 · válidos 2026", "Descending")],
                                  filtros=lib.filtro_visual_topn("t19Top14", "Município", "Rótulo",
                                                                 "T19 · válidos 2026", D.LISTA_LINHAS))),
        Visual(P, lib.visual_html("T19_Dispersao_Fundo", *DISPERSAO, "T19 · Dispersão · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_dispersao(), alt="Eixos e legenda da dispersão", z=Z + 20,
                                  tab=200)),
        Visual(P, _dispersao()),
        *pagina_lib.tooltip(TT, "Município · dossiê", 460, 350, "T19 · Dossiê · HTML", ordem=290,
                            folha_de_estilo=CSS, modelo_corpo=D.corpo_dossie()),
    ]
    # exceções de interação
    for alvo in seletores:
        itens.append(Interacao(P, "T19_Dispersao_Pontos", alvo, "NoFilter"))
        itens.append(Interacao(P, "T19_Lista_Html", alvo, "NoFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Dispersao_Pontos", "HighlightFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Resumo_Html", "NoFilter"))
    itens.append(Interacao(P, "T19_Lista_Html", "T19_Dispersao_Fundo", "NoFilter"))
    return itens
