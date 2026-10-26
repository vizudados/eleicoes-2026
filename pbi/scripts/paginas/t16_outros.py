# -*- coding: utf-8 -*-
"""16 · Os outros — em quem os eleitores dos outros candidatos diziam votar? (dono: agente das telas da campanha)

A história: depois do 1º turno, as pesquisas perguntaram aos eleitores de Cury, Renan e Caiado (e a quem não votou) em
quem votam no 2º turno. O eleitor de Caiado e o de Renan pendem para Flávio (o de Renan com muito branco e nulo), o de
Cury se divide e quem não votou pende para Lula. Os grupos são pequenos (menos de 100 entrevistados por pesquisa): é
sinal, não medida. Os apoios declarados existem, mas só 17,2% dizem seguir o candidato.

  T16_Fluxo_Html     a manchete, a ressalva das amostras e o diagrama de fluxo (de onde → para onde): faixas com a
                     espessura da parte de cada grupo, que correm da esquerda para a direita e esmaecem na cor
  T16_Fluxo_Grupos   alvo do mouse sobre cada grupo (granularidade Transferência[Segmento]) → dossiê ttT16Segmento:
                     a última medição de cada instituto, com a faixa de variação (a distribuição)
  T16_Apoios_Html    "quem apoia quem": títulos e os governadores eleitos no 1º turno (12 × 5 × 4, quadradinhos)
  T16_Apoios_Itens   uma linha ou etiqueta por pessoa (granularidade Apoio[Quem]): para quem foi o apoio → dossiê
                     ttT16Apoio (a frase, a data, a condição)
  T16_Seguir_Html    17,2%: só uma parte diz que segue o candidato (Vox Brasil)

Filtro cruzado (23/10/2026): clique num grupo do diagrama → as faixas dos outros esmaecem, a manchete passa a ser a do
grupo (para onde pende e o que o candidato dele declarou) e, na lista dos apoios, a linha do candidato fica em destaque;
clique em Cury, Renan ou Caiado na lista → o diagrama destaca os eleitores dele, com a mesma manchete. Os governadores e
o 17,2% não mudam (contas sobre a tabela toda). Nada clicado: a tela como antes.
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual
from paginas import _campanha as cp

P = "T16"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]

FLUXO = (150, 140, 1040, 860)
APOIOS = (1250, 140, 520, 540)
SEGUIR = (1250, 712, 520, 288)


def corpo_fluxo() -> str:
    css = (
        ".t16f .cab{position:absolute;left:0;top:0;width:1040px}"
        ".t16f .cab .tit{font-size:28px;margin-top:8px}"
        ".t16f .cab .txt{margin-top:10px;font-size:15px;width:980px}"
        ".t16f svg{position:absolute;left:0;top:180px}"
        ".t16f .colrot{font-size:13px;font-weight:600;letter-spacing:.14em;fill:var(--cinza);font-family:var(--fonte)}"
        f".t16f .fx{{stroke-width:1;stroke-opacity:.55;transform-box:fill-box;"
        "animation:t16onda 1.1s cubic-bezier(.45,.05,.3,1) both}"
        f".t16f .fx.l{{fill:{C['rosa']};fill-opacity:.62;stroke:{C['vermelho']}}}"
        f".t16f .fx.f{{fill:{C['azul_claro']};fill-opacity:.66;stroke:{C['azul']}}}"
        f".t16f .fx.b{{fill:{C['areia']};fill-opacity:.8;stroke:{C['grafite']}}}"
        "@keyframes t16onda{from{clip-path:inset(0 100% 0 0)}}"
        f".t16f .no{{fill:{C['tinta']}}}"
        f".t16f .vl{{font-size:20px;font-weight:700;font-family:var(--fonte);fill:{C['vermelho_escuro']}}}"
        f".t16f .vf{{font-size:20px;font-weight:700;font-family:var(--fonte);fill:{C['azul_escuro']}}}"
        f".t16f .vb{{font-size:17px;font-weight:700;font-family:var(--fonte);fill:{C['grafite']}}}"
        ".t16f .gr{position:absolute;left:0;width:226px}"
        ".t16f .gr b{display:block;font-size:21px;font-weight:600;letter-spacing:-.01em}"
        ".t16f .gr span{display:block;font-size:15px;color:var(--grafite);margin-top:4px;line-height:1.3}"
        ".t16f .ds{position:absolute;left:818px;width:222px;display:flex;align-items:center;gap:12px}"
        ".t16f .ds .ft{width:62px;height:76px;flex:none;background-position:center;background-size:contain;"
        "background-repeat:no-repeat}"
        ".t16f .ds b{font-size:24px;font-weight:700;line-height:1.1}"
        ".t16f .ds.b b{font-size:17px;color:var(--grafite);font-weight:600}"
        f".t16f .ds .ft.l{{background-image:url({cp.img('arte/limpos/retrato-lula-tinta.png', 124)})}}"
        f".t16f .ds .ft.f{{background-image:url({cp.img('arte/limpos/retrato-flavio-tinta.png', 124)})}}"
        f".t16f .ds .ft.b{{height:54px;background-image:url({cp.icone('caixa-de-votos', 124)})}}"
        f".t16f .mao{{position:absolute;font-size:27px;color:{C['grafite']};transform:rotate(-4deg);white-space:nowrap}}"
        # grupo em destaque (clique num grupo ou num candidato da lista dos apoios): o resto esmaece
        ".t16f .fora{opacity:.16;transition:opacity .25s}.t16f .gr.fora{opacity:.3}"
        ".t16f .seta{position:absolute;width:70px;height:52px;background:url("
        f"{cp.img('arte/limpos/rabiscos/seta-curva-esquerda-tinta.png', 140)}) center/contain no-repeat;opacity:.85}}"
    )
    return f"<style>{css}</style>{cp.defs_rabisco()}{{{{content}}}}"


CSS_GRUPOS = (
    ".t16g{pointer-events:none}"
    ".t16g .alvo{position:absolute;left:-8px;width:300px;pointer-events:auto;cursor:help;border-radius:6px;"
    "transition:background .15s}"
    ".t16g .alvo:hover{background:rgba(28,25,21,.05);box-shadow:inset 3px 0 0 var(--tinta)}"
    # o grupo clicado fica marcado (o HTML Content marca os outros alvos com .unselected)
    "body:has(.t16g.unselected) .t16g:not(.unselected) .alvo{background:rgba(28,25,21,.05);"
    "box-shadow:inset 3px 0 0 var(--tinta)}"
)

CSS_APOIOS = (
    ".t16a .sob{position:absolute;left:0;top:0}"
    ".t16a .gov{position:absolute;left:0;top:404px;width:520px}"
    ".t16a .gov .rot{margin-bottom:10px}"
    ".t16a .waf{display:grid;grid-template-columns:repeat(21,20px);gap:4px;margin-bottom:12px}"
    ".t16a .waf i{display:block;width:20px;height:20px;border-radius:2px;transform-origin:center;"
    "animation:eEscala .5s cubic-bezier(.2,.9,.3,1.3) both}"
    f".t16a .waf .f{{background:{C['azul']}}}.t16a .waf .l{{background:{C['vermelho']}}}"
    f".t16a .waf .n{{background:{C['areia']}}}"
    ".t16a .cont{display:flex;gap:26px;align-items:baseline}"
    ".t16a .cont div{display:flex;align-items:baseline;gap:8px;font-size:15px;color:var(--grafite)}"
    ".t16a .cont .num{font-size:30px}"
    ".t16a .naneq{position:absolute;left:0;top:276px}"
)

CSS_ITENS = (
    ".t16i{pointer-events:none}"
    ".t16i .ln{position:absolute;left:0;width:520px;height:56px;display:flex;align-items:center;gap:14px;"
    "pointer-events:auto;cursor:help;border-bottom:1px solid var(--creme)}"
    ".t16i .ln .q{width:210px}"
    ".t16i .ln .q b{display:block;font-size:19px;font-weight:600}"
    ".t16i .ln .q span{display:block;font-size:13px;color:var(--cinza);margin-top:2px}"
    ".t16i .seta{font-size:20px;color:var(--cinza)}"
    ".t16i .bd{display:inline-block;padding:5px 12px;border-radius:3px;font-size:16px;font-weight:700;"
    "white-space:nowrap}"
    f".t16i .bd.f{{background:{C['azul']};color:{C['branco']}}}.t16i .bd.l{{background:{C['vermelho']};color:{C['branco']}}}"
    f".t16i .bd.n{{background:{C['creme']};color:{C['tinta']};box-shadow:inset 0 0 0 1.5px {C['areia']}}}"
    ".t16i .ln small{font-size:13px;color:var(--grafite);line-height:1.25}"
    ".t16i .ch{position:absolute;display:flex;align-items:center;gap:6px;height:30px;pointer-events:auto;cursor:help;"
    "font-size:15px;font-weight:600}"
    ".t16i .ch .bd{font-size:13px;padding:3px 8px}"
    ".t16i .ln:hover,.t16i .ch:hover{background:rgba(28,25,21,.05)}"
    # clique num grupo do diagrama: a linha do candidato do grupo em destaque, as outras esmaecem
    ".t16i{transition:opacity .25s}.t16i.fora{opacity:.3}"
    ".t16i.fx .ln{background:rgba(229,219,200,.6)}"
)

CSS_SEGUIR = (
    ".ic16{position:fixed;left:0;top:30px;width:96px;height:126px;background:url("
    f"{cp.icone('pessoa-duvida', 192)}) center/contain no-repeat}}"
    ".t16s .sob{position:absolute;left:0;top:0}"
    ".t16s .hero{position:absolute;left:118px;top:30px;display:flex;align-items:baseline;gap:14px}"
    ".t16s .hero .num{font-size:84px;letter-spacing:-.035em}"
    ".t16s .frase{position:absolute;left:118px;top:126px;width:400px;font-size:17px;line-height:1.4}"
    ".t16s .bar{position:absolute;left:0;top:186px;width:520px;height:16px;display:flex;background:var(--creme)}"
    ".t16s .bar i{display:block;height:100%;transform-origin:left center;"
    "animation:uCresceX .9s cubic-bezier(.2,.7,.2,1) both}"
    f".t16s .bar .s{{background:{C['tinta']}}}.t16s .bar .d{{background:{C['cinza']}}}.t16s .bar .m{{background:{C['areia']}}}"
    ".t16s .leg{position:absolute;left:0;top:212px;width:520px;font-size:15px;color:var(--grafite);line-height:1.45}"
    ".t16s .leg b{color:var(--tinta)}"
    ".t16s .nota{position:absolute;left:0;top:262px;width:520px}"
    f".t16s .mao{{position:absolute;right:4px;top:10px;font-size:28px;color:{C['vermelho_escuro']};transform:rotate(-5deg)}}"
)

CSS_TT_SEG = (
    ".tt16 .ins{display:grid;grid-template-columns:118px 210px 1fr;align-items:center;column-gap:10px;height:25px;"
    "font-size:15px}"
    ".tt16 .ins span{color:var(--grafite);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".tt16 .ins .b100{display:flex;height:11px;background:var(--creme)}"
    ".tt16 .ins .b100 i{display:block;height:100%;transform-origin:left center;"
    "animation:uCresceX .6s cubic-bezier(.2,.7,.2,1) both}"
    f".tt16 .ins .b100 .l{{background:{C['vermelho']}}}.tt16 .ins .b100 .f{{background:{C['azul']}}}"
    f".tt16 .ins .b100 .b{{background:{C['areia']}}}"
    ".tt16 .ins em{font-style:normal;font-size:13px;color:var(--grafite);white-space:nowrap}"
    ".tt16 .ins em .lula,.tt16 .ins em .flavio{font-weight:700}"
    ".tt16 .txt{margin-top:10px;font-size:15px}"
)
CSS_TT_APOIO = (
    f".tt16a .cit{{font-size:16px;line-height:1.35;margin:4px 0 8px 0;padding-left:12px;"
    f"border-left:3px solid {C['areia']};max-width:400px}}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T16_Fluxo_Html", *FLUXO, "T16 · Fluxo · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_fluxo(), alt=lib.medida("T16 · Fluxo · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T16_Fluxo_Grupos", *FLUXO, "T16 · Grupos · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_GRUPOS}</style>{{{{content}}}}",
                                  granularidade=("Transferência", "Segmento"), tooltip_pagina="ttT16Segmento",
                                  filtro_cruzado=True, transparencia_nao_selecionados=False,
                                  alt=lib.medida("T16 · Grupos · ALT"), z=Z + 1, tab=110)),
        Visual(P, lib.visual_html("T16_Apoios_Html", *APOIOS, "T16 · Apoios · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_APOIOS}</style>{{{{content}}}}",
                                  alt=lib.medida("T16 · Apoios · ALT"), z=Z + 2, tab=120)),
        Visual(P, lib.visual_html("T16_Apoios_Itens", *APOIOS, "T16 · Itens · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_ITENS}</style>{{{{content}}}}",
                                  granularidade=("Apoio", "Quem"), tooltip_pagina="ttT16Apoio",
                                  filtro_cruzado=True, transparencia_nao_selecionados=True,
                                  alt=lib.medida("T16 · Itens · ALT"), z=Z + 3, tab=130)),
        Visual(P, lib.visual_html("T16_Seguir_Html", *SEGUIR, "T16 · Seguir · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_SEGUIR}</style><div class='ic16 entra'></div>{{{{content}}}}",
                                  alt=lib.medida("T16 · Seguir · ALT"), z=Z + 4, tab=140)),
        *pagina_lib.tooltip("ttT16Segmento", "Os outros · grupo de eleitores", 520, 380,
                            "T16 · Tooltip grupo · HTML", ordem=260, folha_de_estilo=CSS,
                            modelo_corpo=cp.dossie("pessoas", CSS_TT_SEG)),
        *pagina_lib.tooltip("ttT16Apoio", "Os outros · apoio declarado", 460, 250,
                            "T16 · Tooltip apoio · HTML", ordem=261, folha_de_estilo=CSS,
                            modelo_corpo=cp.dossie("megafone", CSS_TT_APOIO)),
    ]
