# -*- coding: utf-8 -*-
"""07 · Debate — o que mudou depois do debate na Band? (dono: agente das telas da campanha)

A história: Lula e Flávio só se encontraram uma vez (Band, 18/10). A TV parou para ver (15 pontos na Grande SP) e as
pesquisas não se mexeram (antes: 24 pesquisas; depois: 5; as 10 com campo atravessando o dia do debate ficam fora).

  T07_Audiencia_Html   o número da noite (15 pontos, contador), o pico, o share, o YouTube e a manchete
  T07_Palco_Html       o palco em traço (debate-frente) no bodyTemplate; a medida desenha a legenda e o alvo do
                       mouse (granularidade Debate[Data], só a linha de 18/10) → dossiê ttT07Palco: o que se disse,
                       a nota da Quaest e a audiência dos debates da Band em 2022 e 2026
  T07_Pesquisas_Html   fundo do gráfico: grade, datas, a linha do debate, as médias antes e depois (traço que se
                       desenha) e a nota à mão
  T07_Pesquisas_Pontos um ponto por pesquisa (granularidade Pesquisa[Id]): Lula e Flávio no último dia de campo;
                       dossiê ttT07Pesquisa (o instituto, o campo, a margem e a pesquisa anterior do mesmo instituto)
  T07_Debates_Html     os 11 debates marcados: o eixo, o corte do 1º turno e "1 de 11"
  T07_Debates_Marcas   uma marca por debate (granularidade Debate[Data]); dossiê ttT07Debate (quem foi, por que caiu)
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual
from paginas import _campanha as cp

P = "T07"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]

AUDIENCIA = (150, 140, 840, 300)
PALCO = (1010, 140, 760, 300)
PESQ = (150, 468, 1620, 384)
DEBATES = (150, 872, 1620, 132)

CSS_AUDIENCIA = (
    ".t07a .linha{position:absolute;left:0;top:34px;display:flex;align-items:flex-end;gap:40px}"
    ".t07a .hero{display:flex;align-items:baseline;gap:14px}"
    ".t07a .hero .num{font-size:120px;letter-spacing:-.04em}"
    ".t07a .hero .u{font-size:34px;font-weight:600;letter-spacing:-.01em}"
    ".t07a .tri{display:flex;gap:30px;padding-bottom:16px}"
    ".t07a .tri .num{font-size:34px}"
    ".t07a .tri .rot{margin-top:6px;font-size:13px;letter-spacing:.1em;line-height:1.35}"
    ".t07a .man{position:absolute;left:0;top:192px;width:820px}"
    ".t07a .txt{position:absolute;left:0;top:236px;width:820px}"
)


def corpo_palco() -> str:
    css = (
        ".arte-palco{position:fixed;right:0;top:0;width:560px;pointer-events:none}"
        ".t07s .leg{position:absolute;left:0;top:0;width:184px}"
        ".t07s .leg .txt{font-size:15px;margin-top:10px}"
        ".t07s .leg .nota{margin-top:10px}"
        f".t07s .dica{{position:absolute;left:0;top:228px;font-family:var(--mao);font-size:26px;"
        f"color:{C['vermelho_escuro']};transform:rotate(-4deg)}}"
        ".t07s .alvo{position:absolute;left:190px;top:0;right:0;bottom:0;pointer-events:auto;cursor:help}"
        ".t07s{pointer-events:none}"
    )
    return (f"<style>{css}</style><img class='arte-palco entra' alt='' "
            f"src='{cp.img('arte/limpos/debate-frente-tinta.png', 560)}'/>{{{{content}}}}")


CSS_PESQ = (
    ".t07g .cab{position:absolute;left:0;top:0;right:0}"
    ".t07g .cab .man{margin-top:8px;font-size:24px}"
    ".t07g svg{position:absolute;left:0;top:76px}"
    f".t07g .g{{stroke:{C['areia']};stroke-width:1}}"
    f".t07g .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    f".t07g .ex.b{{font-weight:700;fill:{C['tinta']}}}"
    f".t07g .deb{{stroke:{C['tinta']};stroke-width:1.6;stroke-dasharray:5 6}}"
    f".t07g .ml{{stroke:{C['vermelho']};stroke-width:4;stroke-linecap:round;fill:none}}"
    f".t07g .mf{{stroke:{C['azul']};stroke-width:4;stroke-linecap:round;fill:none}}"
    f".t07g .fl{{stroke:{C['rosa']};stroke-width:2;stroke-dasharray:3 7;stroke-linecap:round;fill:none}}"
    f".t07g .ff{{stroke:{C['azul_claro']};stroke-width:2;stroke-dasharray:3 7;stroke-linecap:round;fill:none}}"
    f".t07g .rl{{fill:{C['vermelho_escuro']};font-size:20px;font-weight:700;font-family:var(--fonte)}}"
    f".t07g .rf{{fill:{C['azul_escuro']};font-size:20px;font-weight:700;font-family:var(--fonte)}}"
    ".t07g .rotulo{position:absolute;font-size:20px;font-weight:700;white-space:nowrap}"
    ".t07g .rotulo.e{text-align:right}"
    f".t07g .mao{{position:absolute;font-size:30px;color:{C['tinta']};transform:rotate(-3deg);white-space:nowrap}}"
    ".t07g .seta{position:absolute;width:74px;opacity:.9}"
    ".t07g .tv{position:absolute;width:58px}"
    ".t07g .leg{position:absolute;left:0;bottom:0;font-size:13px;color:var(--cinza)}"
    ".t07g .leg i{display:inline-block;width:11px;height:11px;border-radius:50%;margin:0 6px 0 0;vertical-align:-1px}"
    ".t07g .leg b{font-weight:600;color:var(--grafite);margin-right:16px}"
)


def corpo_pesquisas() -> str:
    css = (CSS_PESQ
           + f".t07g .tv{{height:50px;background:url({cp.icone('tv-debate', 116)}) center/contain no-repeat}}"
           + f".t07g .seta{{height:60px;background:url("
             f"{cp.img('arte/limpos/rabiscos/seta-curva-esquerda-tinta.png', 148)}) center/contain no-repeat}}")
    return f"<style>{css}</style>{cp.defs_rabisco()}{{{{content}}}}"


CSS_PONTOS = (
    ".t07p{pointer-events:none}"
    ".t07p .pt{position:absolute;width:15px;height:15px;border-radius:50%;pointer-events:auto;cursor:help;"
    "transform-origin:center;animation:eEscala .55s cubic-bezier(.2,.9,.3,1.3) both}"
    ".t07p .pt::after{content:'';position:absolute;inset:-4px;border-radius:50%}"
    f".t07p .l{{background:{C['vermelho']}}}.t07p .f{{background:{C['azul']}}}"
    f".t07p .atr.l{{background:{C['rosa']};opacity:.75}}.t07p .atr.f{{background:{C['azul_claro']};opacity:.8}}"
    f".t07p .pt:hover{{box-shadow:0 0 0 3px {C['papel']},0 0 0 5px {C['tinta']}}}"
)

CSS_DEBATES = (
    ".t07d .esq{position:absolute;left:0;top:0;width:520px}"
    ".t07d .esq .linha{display:flex;align-items:baseline;gap:10px;margin-top:6px}"
    ".t07d .esq .num{font-size:46px}"
    ".t07d .esq .man{font-size:22px}"
    ".t07d .esq .txt{font-size:15px;margin-top:4px;line-height:1.35}"
    ".t07d > svg{position:absolute;left:0;top:0}.t07d .leg svg{flex:none}"
    f".t07d .eixo{{stroke:{C['grafite']};stroke-width:1.6;stroke-linecap:round}}"
    f".t07d .corte{{stroke:{C['cinza']};stroke-width:1.2;stroke-dasharray:3 5}}"
    f".t07d .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    ".t07d .leg{position:absolute;left:600px;bottom:0;font-size:13px;color:var(--cinza);display:flex;gap:22px}"
    ".t07d .leg span{display:flex;align-items:center;gap:7px}"
    f".t07d .leg .o{{width:11px;height:11px;border:2px solid {C['tinta']};border-radius:50%}}"
    f".t07d .leg .x{{font-weight:700;color:{C['cinza']};font-size:15px}}"
    f".t07d .leg .ff{{width:13px;height:13px;border-radius:50%;background:linear-gradient(90deg,{C['vermelho']} 50%,"
    f"{C['azul']} 50%)}}"
)

CSS_MARCAS = (
    ".t07m{pointer-events:none}"
    ".t07m .mc{position:absolute;pointer-events:auto;cursor:help;transform-origin:center;"
    "animation:eEscala .55s cubic-bezier(.2,.9,.3,1.3) both}"
    f".t07m .re{{width:16px;height:16px;border:2.2px solid {C['tinta']};border-radius:50%;background:{C['papel']}}}"
    ".t07m .ca{width:18px;height:18px}.t07m .ca svg{display:block}"
    f".t07m .ff{{width:24px;height:24px;border-radius:50%;background:linear-gradient(90deg,{C['vermelho']} 50%,"
    f"{C['azul']} 50%);box-shadow:0 0 0 3px {C['papel']},0 0 0 5px {C['tinta']}}}"
    ".t07m .mc::after{content:'';position:absolute;inset:-3px}"
    ".t07m .dt{position:absolute;font-size:13px;color:var(--cinza);white-space:nowrap;transform:translateX(-50%)}"
    ".t07m .dt.b{font-weight:700;color:var(--tinta);font-size:15px}"
    ".t07m .mc:hover{outline:2px solid var(--tinta);outline-offset:3px}"
)

CSS_TT_PESQ = (
    ".tt7p .par{margin-top:2px}"
    ".tt7p .dif{font-size:15px;margin-top:2px}"
)
CSS_TT_PALCO = (
    ".tt7s .cit{font-size:16px;line-height:1.35;margin:6px 0 8px 0;padding-left:12px;max-width:430px}"
    f".tt7s .cit.l{{border-left:3px solid {C['vermelho']}}}.tt7s .cit.f{{border-left:3px solid {C['azul']}}}"
    ".tt7s .cit small{display:block;font-size:13px;color:var(--cinza);margin-top:2px}"
    ".tt7s .bar{display:grid;grid-template-columns:190px 1fr;align-items:center;column-gap:10px;height:24px}"
    ".tt7s .bar span{font-size:13px;color:var(--grafite)}"
    ".tt7s .bar div{display:flex;align-items:center;gap:8px}"
    f".tt7s .bar i{{display:block;height:12px;background:{C['areia']};transform-origin:left center;"
    "animation:uCresceX .7s cubic-bezier(.2,.7,.2,1) both}"
    f".tt7s .bar.n i{{background:{C['tinta']}}}.tt7s .bar.n span,.tt7s .bar.n b{{font-weight:700;color:var(--tinta)}}"
    ".tt7s .bar b{font-size:15px;font-weight:600}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T07_Audiencia_Html", *AUDIENCIA, "T07 · Audiência · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_AUDIENCIA}</style>{{{{content}}}}",
                                  alt=lib.medida("T07 · Audiência · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T07_Palco_Html", *PALCO, "T07 · Palco · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_palco(), granularidade=("Debate", "Data"),
                                  tooltip_pagina="ttT07Palco", alt=lib.medida("T07 · Palco · ALT"), z=Z + 1,
                                  tab=110)),
        Visual(P, lib.visual_html("T07_Pesquisas_Html", *PESQ, "T07 · Pesquisas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_pesquisas(), alt=lib.medida("T07 · Pesquisas · ALT"), z=Z + 2,
                                  tab=120)),
        Visual(P, lib.visual_html("T07_Pesquisas_Pontos", *PESQ, "T07 · Pontos · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PONTOS}</style>{{{{content}}}}",
                                  granularidade=("Pesquisa", "Id"), tooltip_pagina="ttT07Pesquisa",
                                  alt=lib.medida("T07 · Pontos · ALT"),
                                  z=Z + 3, tab=130)),
        Visual(P, lib.visual_html("T07_Debates_Html", *DEBATES, "T07 · Debates · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_DEBATES}</style>{{{{content}}}}",
                                  alt=lib.medida("T07 · Debates · ALT"), z=Z + 4, tab=140)),
        Visual(P, lib.visual_html("T07_Debates_Marcas", *DEBATES, "T07 · Marcas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_MARCAS}</style>{{{{content}}}}",
                                  granularidade=("Debate", "Data"), tooltip_pagina="ttT07Debate",
                                  alt=lib.medida("T07 · Marcas · ALT"),
                                  z=Z + 5, tab=150)),
        *pagina_lib.tooltip("ttT07Pesquisa", "Debate · pesquisa", 460, 280, "T07 · Tooltip pesquisa · HTML",
                            ordem=170, folha_de_estilo=CSS, modelo_corpo=cp.dossie("lupa", CSS_TT_PESQ)),
        *pagina_lib.tooltip("ttT07Debate", "Debate · debate marcado", 460, 230, "T07 · Tooltip debate · HTML",
                            ordem=171, folha_de_estilo=CSS, modelo_corpo=cp.dossie("tv-debate")),
        *pagina_lib.tooltip("ttT07Palco", "Debate · palco", 560, 420, "T07 · Tooltip palco · HTML",
                            ordem=172, folha_de_estilo=CSS, modelo_corpo=cp.dossie("microfone", CSS_TT_PALCO)),
    ]
