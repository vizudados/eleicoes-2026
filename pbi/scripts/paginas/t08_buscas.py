# -*- coding: utf-8 -*-
"""08 · Buscas — o que o Brasil perguntou ao Google? (dono: agente das telas da campanha)

A história: nos candidatos, Lula foi o mais buscado quase todo dia (consulta T2, tópicos); o pico foi no dia do 1º
turno e Flávio passou Lula no dia seguinte ao debate. Nas perguntas, o Brasil quis saber a hora de votar, onde votar,
quem ganhou e quando seria o 2º turno. No 2º turno, Lula teve a maior parte das buscas nas 27 UFs. Lembrete visível:
o Trends dá um índice relativo (0–100 dentro de cada consulta), não o número de buscas.

  T08_Placar_Html    Central do Google (30 dias) Lula × Flávio, a manchete e o lembrete do índice
  T08_Perguntas_Html a caixa de busca desenhada com as perguntas, na ordem do tempo (antes, no dia, depois)
  T08_Curva_Html     fundo da curva diária T2 (01/08 a 22/10): grade, datas, as duas linhas que se desenham, o pico do
                     1º turno e a virada depois do debate
  T08_Curva_Dias     uma faixa por dia (granularidade 'Trends tempo'[DataTexto]) com a marca do dia no mouse; dossiê
                     ttT08Dia (o dia e, de 01 a 07/10 e de 15 a 21/10, a curva hora a hora)
  T08_Mapa_Html      cabeçalho do mapa (27 de 27) e a legenda
  T08_Mapa_Ufs       mapa de quadrados (granularidade UF[UF]): a parte de cada um nas buscas do 2º turno, o fundo pelo
                     interesse; dossiê ttT08Uf (interesse no estado e o período todo entre os 5 candidatos)
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual
from paginas import _campanha as cp

P = "T08"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]

PLACAR = (150, 140, 860, 310)
PERGUNTAS = (1050, 140, 720, 316)
CURVA = (150, 476, 1130, 524)
MAPA = (1320, 476, 450, 524)

CSS_PLACAR = (
    ".t08a .par{position:absolute;left:0;top:34px;display:flex;align-items:flex-end;gap:26px}"
    ".t08a .cand .rot{font-size:15px;font-weight:700;letter-spacing:.14em}"
    ".t08a .cand .num{font-size:112px;letter-spacing:-.04em;margin-top:2px}"
    ".t08a .cand.l .rot,.t08a .cand.l .num{color:var(--vermelho)}"
    ".t08a .cand.f .rot,.t08a .cand.f .num{color:var(--azul)}"
    ".t08a .x{font-size:44px;font-weight:300;color:var(--cinza);padding-bottom:22px}"
    ".t08a .lado{padding-bottom:20px;font-size:17px;line-height:1.35;color:var(--grafite);width:200px}"
    ".t08a .man{position:absolute;left:0;top:186px;width:850px}"
    ".t08a .txt{position:absolute;left:0;top:254px;width:850px;font-size:15px}"
)


def corpo_perguntas() -> str:
    css = (
        "@keyframes t08dig{from{max-width:0}}"
        "@keyframes t08pisca{from{opacity:0}}"
        f".t08q .busca{{position:absolute;left:0;top:30px;width:716px;height:58px;border:2px solid {C['tinta']};"
        f"border-radius:30px;background:{C['branco']};display:flex;align-items:center;gap:14px;padding:0 22px;"
        "box-shadow:2px 3px 0 rgba(28,25,21,.12)}"
        ".t08q .busca .dig{display:inline-block;max-width:600px;overflow:hidden;white-space:nowrap;font-size:21px;"
        "font-weight:500;color:var(--tinta);animation:t08dig 1.5s steps(30) .5s both}"
        f".t08q .busca .cursor{{display:inline-block;width:2px;height:24px;background:{C['tinta']};margin-left:-10px;"
        "animation:t08pisca .8s steps(1) 2s 4}"
        ".t08q .lupa{width:26px;height:26px;flex:none}"
        f".t08q .lista{{position:absolute;left:12px;right:12px;top:88px;background:{C['branco']};border:1.5px solid "
        f"{C['areia']};border-top:0;padding:6px 0 4px 0}}"
        ".t08q .it{display:grid;grid-template-columns:136px 22px 1fr auto;align-items:center;column-gap:12px;"
        "height:46px;padding:0 18px}"
        f".t08q .it + .it{{border-top:1px solid {C['creme']}}}"
        ".t08q .it .qd{font-size:13px;color:var(--cinza);letter-spacing:.02em}"
        ".t08q .it .lp{width:18px;height:18px;opacity:.6}"
        ".t08q .it .q{font-size:18px;color:var(--tinta)}"
        ".t08q .it .v{text-align:right;white-space:nowrap}"
        ".t08q .it .v .num{font-size:22px}"
        ".t08q .it .v small{display:block;font-size:13px;color:var(--cinza);margin-top:1px}"
        ".t08q .it .v .ord{font-size:20px;font-weight:700}"
        ".t08q .nota{position:absolute;left:0;right:0;bottom:0}"
        f".t08q .lupa,.t08q .lp{{background:url({cp.icone('lupa', 52)}) center/contain no-repeat}}"
    )
    return f"<style>{css}</style>{{{{content}}}}"


def corpo_curva() -> str:
    css = (
        ".t08c .cab{position:absolute;left:0;top:0;right:0}"
        ".t08c .cab .man{margin-top:8px;font-size:21px}"
        ".t08c svg{position:absolute;left:0;top:80px}"
        f".t08c .g{{stroke:{C['areia']};stroke-width:1}}"
        f".t08c .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
        f".t08c .ex.b{{font-weight:700;fill:{C['tinta']}}}"
        f".t08c .ev{{stroke:{C['grafite']};stroke-width:1.3;stroke-dasharray:4 6}}"
        f".t08c .ll{{stroke:{C['vermelho']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round;fill:none}}"
        f".t08c .lf{{stroke:{C['azul']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round;fill:none}}"
        f".t08c .al{{fill:{C['rosa']};opacity:.16}}.t08c .af{{fill:{C['azul_claro']};opacity:.2}}"
        f".t08c .pl{{fill:{C['vermelho']}}}.t08c .pf{{fill:{C['azul']}}}"
        ".t08c .pl,.t08c .pf{stroke:var(--papel);stroke-width:2}"
        ".t08c .rotulo{position:absolute;font-size:20px;font-weight:700;white-space:nowrap}"
        ".t08c .rotulo.e{text-align:right}"
        f".t08c .mao{{position:absolute;font-size:28px;color:{C['tinta']};white-space:nowrap}}"
        ".t08c .seta{position:absolute}"
        ".t08c .leg{position:absolute;left:0;right:0;bottom:0;font-size:13px;color:var(--cinza);line-height:1.4}"
        ".t08c .leg i{display:inline-block;width:18px;height:3px;margin:0 6px 0 0;vertical-align:4px}"
        ".t08c .leg b{font-weight:600;color:var(--grafite);margin-right:16px}"
        f".t08c .seta.d{{background:url({cp.img('arte/limpos/rabiscos/seta-curva-direita-tinta.png', 140)}) "
        "center/contain no-repeat}"
        f".t08c .seta.e{{background:url({cp.img('arte/limpos/rabiscos/seta-curva-esquerda-tinta.png', 140)}) "
        "center/contain no-repeat}"
    )
    return f"<style>{css}</style>{cp.defs_rabisco()}{{{{content}}}}"


CSS_DIAS = (
    ".t08d{pointer-events:none}"
    ".t08d .dia{position:absolute;top:100px;height:330px;width:13px;pointer-events:auto;cursor:help}"
    f".t08d .dia .v{{position:absolute;left:6px;top:0;bottom:0;width:1px;background:{C['tinta']};opacity:0;"
    "transition:opacity .12s}"
    ".t08d .dia i.m{position:absolute;left:1px;width:11px;height:11px;border-radius:50%;opacity:0;"
    f"transition:opacity .12s;box-shadow:0 0 0 2px {C['papel']}}}"
    f".t08d .dia i.ml{{background:{C['vermelho']}}}.t08d .dia i.mf{{background:{C['azul']}}}"
    ".t08d .dia:hover .v{opacity:.35}.t08d .dia:hover i.m{opacity:1}"
)

CSS_MAPA = (
    ".t08m .sob{width:440px;line-height:1.45}"
    ".t08m .linha{display:flex;align-items:baseline;gap:10px;margin-top:4px}"
    ".t08m .linha .num{font-size:56px}"
    ".t08m .linha .man{font-size:22px}"
    ".t08m .linha .de{font-size:22px;font-weight:600}"
    ".t08m .txt{font-size:15px;margin-top:2px;width:440px;line-height:1.35}"
    ".t08m .leg{position:absolute;left:230px;top:430px;width:216px;font-size:13px;color:var(--cinza);"
    "line-height:1.35}"
    ".t08m .leg .bar{display:flex;height:6px;width:64px;margin:2px 0 6px 0}"
    f".t08m .leg .bar i{{display:block}}.t08m .leg .bar .l{{background:{C['vermelho']};width:57%}}"
    f".t08m .leg .bar .f{{background:{C['azul']};width:43%}}"
    ".t08m .leg .fundo{display:flex;gap:4px;margin:2px 0 4px 0}"
    ".t08m .leg .fundo i{display:block;width:20px;height:12px;border-radius:2px}"
)

CSS_UFS = (
    ".t08u{pointer-events:none}"
    ".t08u .q{position:absolute;width:68px;height:44px;border-radius:3px;pointer-events:auto;cursor:help;"
    "transform-origin:center;animation:eEscala .6s cubic-bezier(.2,.9,.3,1.3) both}"
    ".t08u .q b{position:absolute;left:7px;top:3px;font-size:15px;font-weight:700;letter-spacing:.02em;line-height:1.1}"
    ".t08u .q .vl,.t08u .q .vf{position:absolute;top:21px;font-size:13px;font-weight:700;line-height:1}"
    f".t08u .q .vl{{left:7px;color:{C['vermelho_escuro']}}}.t08u .q .vf{{right:7px;color:{C['azul_escuro']}}}"
    f".t08u .q .br{{position:absolute;left:7px;right:7px;bottom:4px;height:5px;display:flex;background:{C['papel']}}}"
    f".t08u .q .br .l{{background:{C['vermelho']}}}.t08u .q .br .f{{background:{C['azul']};margin-left:auto}}"
    ".t08u .q:hover{outline:2px solid var(--tinta);outline-offset:2px}"
)

CSS_TT_DIA = (
    ".tt8d .par{margin:2px 0 6px 0}"
    ".tt8d svg{display:block;margin-top:6px}"
    f".tt8d .g{{stroke:{C['areia']};stroke-width:1}}"
    f".tt8d .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    f".tt8d .hl{{stroke:{C['vermelho']};stroke-width:2.6;fill:none;stroke-linejoin:round}}"
    f".tt8d .hf{{stroke:{C['azul']};stroke-width:2.6;fill:none;stroke-linejoin:round}}"
)
CSS_TT_UF = (
    ".tt8u .par{margin:4px 0 8px 0}"
    ".tt8u .par .num{font-size:30px}"
    ".tt8u .txt + .txt{margin-top:6px}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T08_Placar_Html", *PLACAR, "T08 · Placar · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PLACAR}</style>{{{{content}}}}",
                                  alt=lib.medida("T08 · Placar · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T08_Perguntas_Html", *PERGUNTAS, "T08 · Perguntas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_perguntas(), alt=lib.medida("T08 · Perguntas · ALT"), z=Z + 1,
                                  tab=110)),
        Visual(P, lib.visual_html("T08_Curva_Html", *CURVA, "T08 · Curva · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_curva(), alt=lib.medida("T08 · Curva · ALT"), z=Z + 2, tab=120)),
        Visual(P, lib.visual_html("T08_Curva_Dias", *CURVA, "T08 · Dias · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_DIAS}</style>{{{{content}}}}",
                                  granularidade=("Trends tempo", "DataTexto"), tooltip_pagina="ttT08Dia",
                                  alt=lib.medida("T08 · Dias · ALT"), z=Z + 3, tab=130)),
        Visual(P, lib.visual_html("T08_Mapa_Html", *MAPA, "T08 · Mapa · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_MAPA}</style>{{{{content}}}}",
                                  alt=lib.medida("T08 · Mapa · ALT"), z=Z + 4, tab=140)),
        Visual(P, lib.visual_html("T08_Mapa_Ufs", *MAPA, "T08 · UFs · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_UFS}</style>{{{{content}}}}",
                                  granularidade=("UF", "UF"), tooltip_pagina="ttT08Uf",
                                  alt=lib.medida("T08 · UFs · ALT"), z=Z + 5, tab=150)),
        *pagina_lib.tooltip("ttT08Dia", "Buscas · dia", 460, 340, "T08 · Tooltip dia · HTML", ordem=180,
                            folha_de_estilo=CSS, modelo_corpo=cp.dossie("lupa", CSS_TT_DIA)),
        *pagina_lib.tooltip("ttT08Uf", "Buscas · UF", 460, 290, "T08 · Tooltip UF · HTML", ordem=181,
                            folha_de_estilo=CSS, modelo_corpo=cp.dossie("pino", CSS_TT_UF)),
    ]
