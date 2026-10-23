# -*- coding: utf-8 -*-
"""T24 · Quem vota — quem vota em Lula e quem vota em Flávio? (a 14ª no roteiro, depois da 13 · Perfil; dono: main)

Pedido do Alisson (23/10/2026): renda per capita, escolaridade, Bolsa Família e IDH dos eleitores de cada um, numa tela
própria ("para deixar análise no micro, cria-se outra tela, para não ficar poluindo"). O voto é secreto, então a tela
mostra os LUGARES (municípios em cinco degraus de eleitores pelo indicador, com o resultado da urna) e, ao lado, as
PESSOAS (o que os eleitores disseram às pesquisas na mesma lente). Sem filtro de UF: os degraus são nacionais.

  T24_Lentes_Html / _Botoes  as quatro lentes (Renda · Escolaridade · Bolsa Família · IDH); botões nativos invisíveis
                             por cima das abas desenhadas (T24 Lente, padrão Renda)
  T24_Fundo_Html             a manchete da lente (quem lidera em cada ponta), o que o indicador mede, a grade e o eixo
  T24_Grafico_Html           o protagonista: as linhas de Lula e Flávio que atravessam os cinco degraus (granularidade
                             T24 Degrau), a nota onde a vantagem troca de lado; tooltip: dossiê do degrau (ttT24Degrau)
  T24_Pesquisa_Html          o cartão das pessoas (pesquisa na mesma lente) e a nota "o voto é secreto"

Medidas em pbi/dax/T24 Quem vota (geradas por pbi/scripts/desenho_t24.py); tabelas em pbi/modelo/t24_social.py.
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual

P = "T24"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]
TT = "ttT24Degrau"

LENTES = (150, 140, 940, 52)
FUNDO = (150, 210, 940, 790)
GRAFICO = (150, 316, 940, 684)
PESQUISA = (1150, 140, 620, 860)

CSS_LENTES = (
    ".t24l{display:flex;gap:12px}"
    f".t24l .ab{{flex:1;height:52px;display:flex;align-items:center;justify-content:center;border:1.5px solid "
    f"{C['tinta']};border-radius:26px;font-size:17px;font-weight:600;color:{C['tinta']};transition:background .25s,"
    "color .25s}"
    f".t24l .ab.on{{background:{C['tinta']};color:{C['papel']}}}"
)
CSS_FUNDO = (
    ".t24f .man{position:absolute;left:0;top:0;width:930px;font-size:26px;line-height:1.28}"
    ".t24f .man b{font-weight:700}"
    ".t24f .mede{position:absolute;left:0;top:80px;width:930px;font-size:15px;color:var(--grafite)}"
    f".t24f .g{{position:absolute;left:44px;right:4px;height:0;border-top:1px solid {C['areia']}}}"
    f".t24f .g.meio{{border-top:1.5px dashed {C['grafite']}}}"
    ".t24f .gy{position:absolute;left:0;font-size:13px;color:var(--cinza)}"
    ".t24f .eixo{position:absolute;left:44px;right:4px;top:742px;display:flex;justify-content:space-between}"
)
CSS_GRAFICO = (
    ".t24g{pointer-events:none}"
    ".t24g .banda{position:absolute;top:0;width:172px;height:590px;pointer-events:auto;border-radius:4px;"
    "transition:background .2s}"
    ".t24g .banda:hover{background:rgba(28,25,21,.06)}"
    ".t24g .sv{position:absolute;left:0;top:0;pointer-events:none}"
    f".t24g .ll{{stroke:{C['vermelho']};stroke-width:3.6;stroke-linecap:round}}"
    f".t24g .lf{{stroke:{C['azul']};stroke-width:3.6;stroke-linecap:round}}"
    f".t24g .pl{{fill:{C['vermelho']}}}.t24g .pf{{fill:{C['azul']}}}"
    f".t24g .cz{{fill:none;stroke:{C['tinta']};stroke-width:2}}"
    # halo no papel: no cruzamento as linhas passam atrás dos números (46,8% × 46,0%) sem riscar a leitura
    ".t24g .vl{position:absolute;width:100px;text-align:center;font-size:22px;font-weight:700;"
    "font-variant-numeric:tabular-nums;text-shadow:0 0 4px var(--papel),0 0 4px var(--papel),0 0 2px var(--papel)}"
    f".t24g .cruz{{position:absolute;top:598px;width:172px;text-align:center;font-size:23px;color:{C['tinta']}}}"
    ".t24g .pe{position:absolute;top:548px;width:172px;text-align:center;display:flex;flex-direction:column;gap:4px}"
    ".t24g .pe b{font-size:13px;font-weight:600;letter-spacing:.12em;color:var(--cinza)}"
    ".t24g .pe span{font-size:15px;color:var(--grafite)}"
)
CSS_PESQUISA = (
    f".t24p .cartao{{position:absolute;left:0;top:0;width:620px;height:610px;background:{C['branco']};border:1.5px "
    f"solid {C['areia']};padding:28px 30px 18px 30px}}"
    ".t24p .tit{font-size:26px;margin:8px 0 6px 0}"
    ".t24p .cartao .txt{margin-top:12px}"
    ".t24p .leg{display:flex;gap:22px;margin:14px 0 4px 0;font-size:15px;color:var(--grafite)}"
    ".t24p .leg i{display:inline-block;width:14px;height:14px;margin-right:6px;vertical-align:-2px}"
    f".t24p .bl{{background:{C['vermelho']}}}.t24p .bf{{background:{C['azul']}}}"
    f".t24p .eixo{{position:relative;margin:18px 0 2px 170px;width:390px;height:20px;font-size:13px;font-weight:600}}"
    ".t24p .eixo span{position:absolute;top:0}.t24p .eixo span:first-child{right:203px}"
    ".t24p .eixo span:last-child{left:203px}"
    f".t24p .lin{{display:grid;grid-template-columns:170px 390px;align-items:center;min-height:86px;"
    f"border-bottom:1px solid {C['creme']}}}"
    ".t24p .cat{display:flex;flex-direction:column;gap:3px;padding-right:12px}"
    ".t24p .cat b{font-size:17px;font-weight:600;line-height:1.2}"
    ".t24p .cat i{font-style:normal;font-size:13px;color:var(--cinza)}"
    ".t24p .gr{position:relative;height:86px}"
    f".t24p .gr .ct{{position:absolute;left:195px;top:10px;bottom:10px;border-left:1.5px solid {C['tinta']}}}"
    f".t24p .gr .ref{{position:absolute;top:6px;bottom:6px;border-left:1.5px dashed {C['grafite']}}}"
    ".t24p .gr .vb{position:absolute;top:26px;height:20px}"
    ".t24p .gr .vt{position:absolute;top:24px;font-size:20px;font-weight:700;white-space:nowrap}"
    f".t24p .gr .pp{{position:absolute;left:0;right:0;top:54px;text-align:center;font-size:14px;color:var(--grafite);"
    f"text-shadow:0 0 3px {C['branco']},0 0 3px {C['branco']},0 0 2px {C['branco']}}}"
    ".t24p .gr .pp span{font-weight:600}"
    f".t24p .gr .tr{{position:absolute;right:0;top:10px;font-size:22px;color:{C['tinta']};transform:rotate(-3deg)}}"
    ".t24p .lin.tot{border-bottom:none}.t24p .lin.tot .cat b{color:var(--grafite);font-weight:500}"
    ".t24p .lin.tot .vb{opacity:.45}"
    ".t24p .nbf{margin-top:14px}"
    f".t24p .regua{{margin:30px 0 4px 0;padding-top:16px;border-top:1.5px solid {C['tinta']};color:{C['tinta']}}}"
    f".t24p .pt{{display:flex;flex-direction:column;gap:4px;padding:14px 0;border-bottom:1px solid {C['creme']}}}"
    ".t24p .pt b{font-size:22px;font-weight:700}.t24p .pt > span:last-child{font-size:18px;font-weight:700}"
    ".t24p .segredo{position:absolute;left:0;top:676px;width:620px;display:flex;gap:26px;align-items:flex-start}"
    ".t24p .segredo img{width:130px;flex:none;margin-top:4px}"
    ".t24p .segredo .mao{font-size:30px;color:var(--vermelho-escuro);transform:rotate(-2deg);transform-origin:left}"
    ".t24p .segredo .txt{margin-top:6px}"
)
CSS_TT = (
    f".tt24{{background:{C['branco']};border:1.5px solid {C['areia']};padding:26px 26px 18px 26px;"
    "box-shadow:0 10px 24px rgba(28,25,21,.16)}"
    f".tt24 .fita{{position:absolute;left:160px;top:-10px;width:130px;height:26px;background:{C['areia']};"
    "opacity:.7;transform:rotate(-3deg)}"
    ".tt24 .num-l{font-size:17px;margin:10px 0 14px 0}.tt24 .num-l b{font-weight:700}"
    ".tt24 .duas{display:flex;gap:40px}.tt24 .duas > div{display:flex;flex-direction:column;gap:4px}"
    ".tt24 .duas span:not(.rot){font-size:18px;font-weight:700}"
    ".tt24 .txt{font-size:15px;margin-top:14px;color:var(--tinta)}"
    ".tt24 .cid{font-size:15px;margin-top:10px;color:var(--grafite);line-height:1.35}"
    ".tt24 .cid .rot{display:block;margin-bottom:2px}"
)


def _corpo(css: str, extra: str = "") -> str:
    return f"<style>{css}</style>{extra}{{{{content}}}}"


def declarar(ctx):
    # o filtro de traço tremido fica uma vez no corpo do gráfico; as linhas de cada degrau usam url(#rb24)
    defs = f"<svg width='0' height='0' style='position:absolute'>{estilo.defs_rabisco('rb24', 1.6)}</svg>"
    # a nota fixa do voto secreto, com a urna de lona em traço, embaixo do cartão
    urna = estilo.imagem_b64("arte/limpos/icones/caixa-de-votos-tinta.png", 260)
    segredo = (f"<div class='tela t24p'><div class='segredo entra d12'><img alt='' src='{urna}'/><div><div class='mao'>"
               "o voto é secreto</div><div class='txt'>Ninguém sabe a renda de quem votou em quem. À esquerda, os "
               "lugares onde vivem os eleitores; aqui, o que as pessoas contaram às pesquisas antes da urna.</div></div>"
               "</div></div>")
    return [
        Visual(P, lib.visual_html("T24_Lentes_Html", *LENTES, "T24 · Lentes · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_LENTES), alt=lib.medida("T24 · Lentes · ALT"), z=Z, tab=100)),
        Visual(P, lib.segmentacao_botoes(
            "T24_Lentes_Botoes", *LENTES, tabela="T24 Lente", coluna="Lente", padrao="Renda", grupo="t24lente",
            linhas=1, colunas=4, cores=None, z=lib.CAMADAS["acao"], tab=101, espaco=12, invisivel=True, forcar=True,
            alt="Lentes: escolha Renda, Escolaridade, Bolsa Família ou IDH")),
        Visual(P, lib.visual_html("T24_Fundo_Html", *FUNDO, "T24 · Fundo · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_FUNDO), alt=lib.medida("T24 · Fundo · ALT"), z=Z + 1,
                                  tab=110)),
        Visual(P, lib.visual_html("T24_Grafico_Html", *GRAFICO, "T24 · Gráfico · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_GRAFICO, defs), granularidade=("T24 Degrau", "Degrau"),
                                  tooltip_pagina=TT, alt=lib.medida("T24 · Gráfico · ALT"), z=Z + 2, tab=120)),
        Visual(P, lib.visual_html("T24_Pesquisa_Html", *PESQUISA, "T24 · Pesquisa · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_PESQUISA) + segredo, alt=lib.medida("T24 · Pesquisa · ALT"),
                                  z=Z + 3, tab=130)),
        *pagina_lib.tooltip(TT, "Quem vota · degrau", 460, 300, "T24 · Tooltip degrau · HTML", ordem=340,
                            folha_de_estilo=CSS, modelo_corpo=_corpo(CSS_TT)),
    ]
