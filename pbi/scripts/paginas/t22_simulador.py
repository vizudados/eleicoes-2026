# -*- coding: utf-8 -*-
"""22 · Simulador — e se os eleitores dos outros candidatos escolherem? (dono: tela 22)

Para empatar, Lula precisaria de 62% dos 9,32 mi de votos dos outros candidatos. Simulação, não previsão.

  T22_Heroi_Html          o "62%" (contador), a manchete e o aviso (balança): simulação, não previsão
  T22_ReguaLula_Html      a régua do controle principal: dos eleitores dos outros que votam, quantos escolhem Lula
                          (barra Lula | Flávio, a marca do empate e a faixa onde caem as 8 pesquisas)
  T22_ReguaLula_Regua     VizuFilter 2.13 no modo régua sobre a barra (T22 Para Lula, 0, 2, …, 100; padrão 50): o botão
                          arrasta (ou anda pelas setas) e o filtro é aplicado ao soltar; trilho transparente, só o botão
  T22_ReguaAbst_Html/_Regua    quantos não escolhem ninguém (T22 Não votam, 0–50 em passos de 5): o HTML traz título e
                               subtítulo; o VizuFilter, trilho, trecho, botão e os rótulos 0% e 50%
  T22_ReguaComp_Html/_Regua    mudança no comparecimento (T22 Comparecimento, −5 a +5; metade para cada um): idem, com o
                               trecho a partir do zero, a marca do zero e os rótulos −5 e +5
  T22_Pesquisas_Html      as 8 pesquisas (granularidade Transferência[Instituto]): para onde vão os votos dos outros e o
                          2º turno que isso daria; clique leva o cenário da pesquisa ao resultado e ao mapa; dossiê
                          ttT22Pesquisa (cada grupo: Cury, Renan, Caiado e os demais, e quanto cada um ganha)
  T22_Resultado_Html      o 2º turno simulado (Brasil com o exterior): Lula × Flávio, UFs à frente, diferença
  T22_Grade_Html          o mapa de quadrados das UFs (granularidade UF[UF]); tooltip: dossiê da UF (ttT22UF); clique:
                          o resultado passa a ser o daquela UF (o resto da tela segue no Brasil)
  T22_Exterior_Alvo       alvo transparente sobre o EX: o exterior no cenário e o 1º turno país a país (ttT22Exterior)
  T22_Legenda_Html        legenda e dica (fixo)

Medidas em pbi/dax/T22 Simulador (desenho gerado por pbi/scripts/desenho_t22.py); parâmetros em
pbi/modelo/t22_parametros.py. As réguas eram segmentações de botões invisíveis (um botão por valor) até 23/10/2026; o dono
testou ("não está arrastando") e pediu o VizuFilter com o recurso de arrastar (pacote 2.13.0.0, cartão Régua).
"""
from __future__ import annotations

import desenho_t22 as D
import estilo
import exterior
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual

P = "T22"
CSS = "Estilo · CSS"
VAZIO = "Casca · vazio"
Z = lib.CAMADAS["conteudo"]
TT = "ttT22UF"


C = estilo.COR
# Réguas: VizuFilter 2.13 no modo régua (cartão Régua). O valor padrão de cada uma é o da medida sem seleção
# (SELECTEDVALUE … 50, 0 e 0 em T22 Simulador\Contas): sem filtro, o botão fica onde a conta está.
# O texto do visual (valor do arraste e rótulos das pontas) sai na Sora do painel, embutida no pacote ("Sora Vizu").
ESTILO_REGUA = {"fontFamily": "Sora Vizu, Segoe UI", "fontSize": 13, "textColor": C["tinta"]}
BOTAO = {"bordaBotao": 2, "corBotao": C["branco"], "corBordaBotao": C["tinta"], "valorNoArraste": True}
# régua A: só o botão (32 px, como a alça antiga, sem sombra) sobre a barra Lula | Flávio do HTML
CFG_REGUA_A = {"ativo": True, "valorPadrao": 50, "trilhoVisivel": False, "preenchimento": "nenhum",
               "marcas": "nenhuma", "diametroBotao": D.A_BOTAO, "margemLateral": D.A_MARGEM, "sufixo": "%", **BOTAO,
               "rotuloAcessivel": "Dos eleitores dos outros candidatos que forem votar, porcentagem que escolhe Lula"}
# réguas B e C: trilho de 4 px em areia, trecho em tinta, botão de 22 px e os rótulos das pontas em cinza, 13 px
TRILHO_BC = {"ativo": True, "valorPadrao": 0, "trilhoVisivel": True, "espessuraTrilho": 4, "corTrilho": C["areia"],
             "corPreenchimento": C["tinta"], "diametroBotao": D.BC_BOTAO, "margemLateral": D.BC_MARGEM,
             "rotulosExtremos": True, "corRotulos": C["cinza"], "tamanhoRotulos": 13, **BOTAO}
CFG_REGUA_B = {**TRILHO_BC, "preenchimento": "inicio", "marcas": "nenhuma", "sufixo": "%",
               "rotuloAcessivel": "Dos eleitores dos outros candidatos, porcentagem que não escolhe ninguém"}
# régua C: o trecho sai do zero (o meio) para os dois lados, com a marca do zero; +5 e −5 com sinal
CFG_REGUA_C = {**TRILHO_BC, "preenchimento": "padrao", "marcas": "padrao", "corMarcas": C["grafite"],
               "alturaMarcas": 16, "sinalMais": True,
               "rotuloAcessivel": "Mudança no comparecimento, em pontos sobre o 1º turno"}


def _regua(nome, caixa, tabela, coluna, regua, alt, tab):
    """VizuFilter 2.13 no modo régua (cartão Régua) sobre a coluna do parâmetro; o filtro sai ao soltar o botão."""
    x, y, w, h = (round(v, 1) for v in caixa)
    return Visual(P, lib.visual_vizufilter(
        nome, x, y, w, h, categoria=(tabela, coluna, coluna), geral={}, layout={}, estilo=ESTILO_REGUA, alt=alt,
        z=lib.CAMADAS["acao"], tab=tab, sincronia=lib.grupo_sincronia(f"t22{nome.split('_')[1].lower()}"),
        regua=regua))


def declarar(ctx):
    itens = [
        Visual(P, lib.visual_html("T22_Heroi_Html", *D.HEROI, "T22 · Herói · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_heroi(), alt=lib.medida("T22 · Herói · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T22_ReguaLula_Html", *D.REGUA_A, "T22 · Régua Lula · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_regua_a(), alt=lib.medida("T22 · Régua Lula · ALT"), z=Z + 1,
                                  tab=110)),
        _regua("T22_ReguaLula_Regua", D.caixa_regua_a(), "T22 Para Lula", "Para Lula", CFG_REGUA_A,
               "Régua: arraste o botão (ou use as setas) para escolher quantos eleitores dos outros escolhem Lula, de 0 "
               "a 100%", 111),
        Visual(P, lib.visual_html("T22_ReguaAbst_Html", *D.REGUA_B, "T22 · Régua abstenção · HTML",
                                  folha_de_estilo=CSS, modelo_corpo=D.corpo_regua_bc(),
                                  alt=lib.medida("T22 · Régua abstenção · ALT"), z=Z + 2, tab=120)),
        _regua("T22_ReguaAbst_Regua", D.caixa_regua_bc(D.REGUA_B), "T22 Não votam", "Não votam", CFG_REGUA_B,
               "Régua: arraste o botão (ou use as setas) para escolher quantos eleitores dos outros não escolhem "
               "ninguém, de 0 a 50%", 121),
        Visual(P, lib.visual_html("T22_ReguaComp_Html", *D.REGUA_C, "T22 · Régua comparecimento · HTML",
                                  folha_de_estilo=CSS, modelo_corpo=D.corpo_regua_bc(),
                                  alt=lib.medida("T22 · Régua comparecimento · ALT"), z=Z + 3, tab=130)),
        _regua("T22_ReguaComp_Regua", D.caixa_regua_bc(D.REGUA_C), "T22 Comparecimento", "Comparecimento",
               CFG_REGUA_C, "Régua: arraste o botão (ou use as setas) para mudar o comparecimento, de 5 pontos a "
               "menos a 5 a mais", 131),
        Visual(P, lib.visual_html("T22_Pesquisas_Html", *D.PESQUISAS, "T22 · Pesquisas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_pesquisas(), alt=lib.medida("T22 · Pesquisas · ALT"), z=Z + 4,
                                  tab=140, granularidade=("Transferência", "Instituto"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT22Pesquisa")),
        Visual(P, lib.visual_html("T22_Resultado_Html", *D.RESULTADO, "T22 · Resultado · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_resultado(), alt=lib.medida("T22 · Resultado · ALT"), z=Z + 5,
                                  tab=200)),
        Visual(P, lib.visual_html("T22_Grade_Html", *D.GRADE, "T22 · UF · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_grade(), alt=lib.medida("T22 · UF · ALT"), z=Z + 6, tab=210,
                                  granularidade=("UF", "UF"), tooltip_pagina=TT, filtro_cruzado=True,
                                  transparencia_nao_selecionados=True)),
        Visual(P, lib.visual_html("T22_Legenda_Html", *D.LEGENDA, VAZIO, folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_legenda(), alt="Legenda do mapa de quadrados e dica",
                                  z=Z + 7, tab=220)),
        *pagina_lib.tooltip(TT, "UF · cenário", 420, 250, "T22 · Tooltip UF · HTML", ordem=320,
                            folha_de_estilo=CSS, modelo_corpo=D.corpo_tooltip()),
        # a lista das pesquisas ganha o dossiê (23/10/2026): para onde vai cada grupo de eleitores dos outros
        *pagina_lib.tooltip("ttT22Pesquisa", "Pesquisa · para onde vão", 500, 360, "T22 · Tooltip pesquisa · HTML",
                            ordem=322, folha_de_estilo=CSS, modelo_corpo=D.corpo_tooltip_pesquisa()),
        # o EX da grade (coluna 5, linha 0) abre o tooltip do exterior país a país, com o cenário no topo
        *exterior.declarar(P, "T22_Exterior_Alvo", (D.GRADE[0] + 5 * D.PASSO, D.GRADE[1], D.LADO, D.LADO),
                           "Exterior · simulador · HTML", ordem=321, altura=exterior.ALTURA + 50),
    ]
    # a lista das pesquisas escolhe o cenário do resultado e do mapa; a régua segue mostrando todas as pesquisas
    for alvo in ("T22_ReguaLula_Html", "T22_Heroi_Html", "T22_ReguaAbst_Html", "T22_ReguaComp_Html",
                 "T22_ReguaLula_Regua", "T22_ReguaAbst_Regua", "T22_ReguaComp_Regua"):
        itens.append(Interacao(P, "T22_Pesquisas_Html", alvo, "NoFilter"))
    # o clique numa UF do mapa (23/10/2026) leva o resultado àquela UF (e o rótulo diz qual); a resposta, as réguas, a
    # lista das pesquisas (o 2º turno de cada uma é o do Brasil) e o alvo do exterior seguem no Brasil
    for alvo in ("T22_Heroi_Html", "T22_ReguaLula_Html", "T22_ReguaAbst_Html", "T22_ReguaComp_Html",
                 "T22_ReguaLula_Regua", "T22_ReguaAbst_Regua", "T22_ReguaComp_Regua", "T22_Pesquisas_Html",
                 "T22_Exterior_Alvo"):
        itens.append(Interacao(P, "T22_Grade_Html", alvo, "NoFilter"))
    return itens
