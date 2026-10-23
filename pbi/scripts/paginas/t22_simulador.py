# -*- coding: utf-8 -*-
"""22 · Simulador — e se os eleitores dos outros candidatos escolherem? (dono: tela 22)

Para empatar, Lula precisaria de 62% dos 9,32 mi de votos dos outros candidatos. Simulação, não previsão.

  T22_Heroi_Html          o "62%" (contador), a manchete e o aviso (balança): simulação, não previsão
  T22_ReguaLula_Html      a régua do controle principal: dos eleitores dos outros que votam, quantos escolhem Lula
                          (barra Lula | Flávio, a marca do empate e a faixa onde caem as 8 pesquisas)
  T22_ReguaLula_Botoes    segmentação de botões invisível sobre a barra (T22 Para Lula, 51 botões: 0, 2, …, 100)
  T22_ReguaAbst_Html/_Botoes   quantos não escolhem ninguém (T22 Não votam, 0–50 em passos de 5)
  T22_ReguaComp_Html/_Botoes   mudança no comparecimento (T22 Comparecimento, −5 a +5; metade para cada um)
  T22_Pesquisas_Html      as 8 pesquisas (granularidade Transferência[Instituto]): para onde vão os votos dos outros e o
                          2º turno que isso daria; clique leva o cenário da pesquisa ao resultado e ao mapa
  T22_Resultado_Html      o 2º turno simulado (Brasil com o exterior): Lula × Flávio, UFs à frente, diferença
  T22_Grade_Html          o mapa de quadrados das UFs (granularidade UF[UF]); tooltip: dossiê da UF (ttT22UF)
  T22_Exterior_Alvo       alvo transparente sobre o EX: o exterior no cenário e o 1º turno país a país (ttT22Exterior)
  T22_Legenda_Html        legenda e dica (fixo)

Medidas em pbi/dax/T22 Simulador (desenho gerado por pbi/scripts/desenho_t22.py); parâmetros em
pbi/modelo/t22_parametros.py.
"""
from __future__ import annotations

import desenho_t22 as D
import exterior
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual

P = "T22"
CSS = "Estilo · CSS"
VAZIO = "Casca · vazio"
Z = lib.CAMADAS["conteudo"]
TT = "ttT22UF"


def _botoes(nome, caixa, tabela, coluna, padrao, n, alt, tab):
    x, y, w, h = (round(v, 1) for v in caixa)
    return Visual(P, lib.segmentacao_botoes(
        nome, x, y, w, h, tabela=tabela, coluna=coluna, padrao=padrao, grupo=f"t22{nome.split('_')[1].lower()}",
        linhas=1, colunas=n, cores=None, z=lib.CAMADAS["acao"], tab=tab, espaco=0, invisivel=True, forcar=True,
        alt=alt))


def declarar(ctx):
    itens = [
        Visual(P, lib.visual_html("T22_Heroi_Html", *D.HEROI, "T22 · Herói · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_heroi(), alt=lib.medida("T22 · Herói · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T22_ReguaLula_Html", *D.REGUA_A, "T22 · Régua Lula · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_regua_a(), alt=lib.medida("T22 · Régua Lula · ALT"), z=Z + 1,
                                  tab=110)),
        _botoes("T22_ReguaLula_Botoes", D.tiles_a(), "T22 Para Lula", "Para Lula", 50, 51,
                "Régua: clique para escolher quantos eleitores dos outros escolhem Lula, de 0 a 100%", 111),
        Visual(P, lib.visual_html("T22_ReguaAbst_Html", *D.REGUA_B, "T22 · Régua abstenção · HTML",
                                  folha_de_estilo=CSS, modelo_corpo=D.corpo_regua_bc(),
                                  alt=lib.medida("T22 · Régua abstenção · ALT"), z=Z + 2, tab=120)),
        _botoes("T22_ReguaAbst_Botoes", D.tiles_bc(D.REGUA_B), "T22 Não votam", "Não votam", 0, 11,
                "Régua: clique para escolher quantos eleitores dos outros não escolhem ninguém, de 0 a 50%", 121),
        Visual(P, lib.visual_html("T22_ReguaComp_Html", *D.REGUA_C, "T22 · Régua comparecimento · HTML",
                                  folha_de_estilo=CSS, modelo_corpo=D.corpo_regua_bc(),
                                  alt=lib.medida("T22 · Régua comparecimento · ALT"), z=Z + 3, tab=130)),
        _botoes("T22_ReguaComp_Botoes", D.tiles_bc(D.REGUA_C), "T22 Comparecimento", "Comparecimento", 0, 11,
                "Régua: clique para mudar o comparecimento, de 5 pontos a menos a 5 a mais", 131),
        Visual(P, lib.visual_html("T22_Pesquisas_Html", *D.PESQUISAS, "T22 · Pesquisas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_pesquisas(), alt=lib.medida("T22 · Pesquisas · ALT"), z=Z + 4,
                                  tab=140, granularidade=("Transferência", "Instituto"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True)),
        Visual(P, lib.visual_html("T22_Resultado_Html", *D.RESULTADO, "T22 · Resultado · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_resultado(), alt=lib.medida("T22 · Resultado · ALT"), z=Z + 5,
                                  tab=200)),
        Visual(P, lib.visual_html("T22_Grade_Html", *D.GRADE, "T22 · UF · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_grade(), alt=lib.medida("T22 · UF · ALT"), z=Z + 6, tab=210,
                                  granularidade=("UF", "UF"), tooltip_pagina=TT)),
        Visual(P, lib.visual_html("T22_Legenda_Html", *D.LEGENDA, VAZIO, folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_legenda(), alt="Legenda do mapa de quadrados e dica",
                                  z=Z + 7, tab=220)),
        *pagina_lib.tooltip(TT, "UF · cenário", 420, 250, "T22 · Tooltip UF · HTML", ordem=320,
                            folha_de_estilo=CSS, modelo_corpo=D.corpo_tooltip()),
        # o EX da grade (coluna 5, linha 0) abre o tooltip do exterior país a país, com o cenário no topo
        *exterior.declarar(P, "T22_Exterior_Alvo", (D.GRADE[0] + 5 * D.PASSO, D.GRADE[1], D.LADO, D.LADO),
                           "Exterior · simulador · HTML", ordem=321, altura=exterior.ALTURA + 50),
    ]
    # a lista das pesquisas escolhe o cenário do resultado e do mapa; a régua segue mostrando todas as pesquisas
    for alvo in ("T22_ReguaLula_Html", "T22_Heroi_Html", "T22_ReguaAbst_Html", "T22_ReguaComp_Html",
                 "T22_ReguaLula_Botoes", "T22_ReguaAbst_Botoes", "T22_ReguaComp_Botoes"):
        itens.append(Interacao(P, "T22_Pesquisas_Html", alvo, "NoFilter"))
    return itens
