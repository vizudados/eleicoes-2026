# -*- coding: utf-8 -*-
"""T01 · Placar — quem venceu o 1º turno, e por quanto? (dono: agente das telas 01–06)

Protagonista: a diferença (2,22 mi) com o sublinhado à mão. Apoios: o duelo Flávio × Lula com os retratos em traço, a
barra dos votos válidos (um segmento por candidato, com tooltip dossiê) e, à direita, as duas linhas de 2022 para 2026
que se cruzam — os quatro pontos têm alvos com grão (ano × candidato) por cima do desenho e abrem o dossiê do ponto (de
onde vieram os votos daquele ano). Filtro de UF da casca: com UF, tudo vira o resultado da UF ('Candidato UF'); sem
filtro cruzado entre as peças (clicar num candidato ou num ano mudaria as contas do placar, que somam todos).

Medidas: pbi/dax/T01 Placar (geradas por pbi/scripts/desenho_t01.py).
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual

P = "T01"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]

# geometria (área de conteúdo x 150–1770, y 140–1000)
PLACAR = (110, 140, 900, 860)
BARRA = (150, 140 + 622, 860, 56)          # a medida do placar reserva y 600–690 para o título e a barra
VIRADA = (1040, 140, 730, 860)


def _css_placar() -> str:
    rf = estilo.imagem_b64("docs/midia/arte/retrato-flavio-azul_escuro.png", 220)
    rl = estilo.imagem_b64("docs/midia/arte/retrato-lula-vermelho_escuro.png", 220)
    # a caixa começa 40 px antes da coluna (x 110) para o laço caber; o conteúdo fica em x 150 (left 40)
    return (
        ".t1>*{position:absolute;left:40px}"
        ".t1 .sob{top:0}"
        ".t1 .dn{top:52px;display:inline-block}"
        ".t1 .dnum{display:inline-block;font-size:128px;font-weight:700;letter-spacing:-.035em;line-height:1;"
        "font-variant-numeric:tabular-nums lining-nums;padding:0 4px}"
        ".t1 .sub{position:absolute;left:0;bottom:-30px;width:100%;height:24px;overflow:visible;pointer-events:none}"
        ".t1 .mm{top:232px;width:860px}.t1 .mm .m1{font-size:30px;line-height:1.2}.t1 .mm .m2{margin-top:8px}"
        ".t1 .duelo{top:352px;width:860px;display:flex;justify-content:space-between}"
        ".t1 .cand{position:relative;width:420px;height:190px;padding-left:124px}"
        ".t1 .rt{position:absolute;left:0;top:2px;width:106px;height:106px;border-radius:50%;"
        "background-color:var(--creme);background-size:118% auto;background-position:50% 8%;"
        "background-repeat:no-repeat;box-shadow:0 0 0 1.5px var(--areia)}"
        f".t1 .rt-f{{background-image:url({rf})}}.t1 .rt-l{{background-image:url({rl})}}"
        ".t1 .selo{position:absolute;right:-6px;bottom:-4px;width:40px;height:40px;border-radius:50%;"
        "background:var(--papel);border:1.6px solid var(--tinta);font-size:15px;font-weight:700;text-align:center;"
        "line-height:37px;transform:rotate(-8deg)}"
        ".t1 .cand .rot{margin:4px 0 6px 0}"
        ".t1 .cand .v{font-size:64px;font-weight:700;letter-spacing:-.03em;line-height:1.02;"
        "font-variant-numeric:tabular-nums lining-nums}"
        ".t1 .cand .p{font-size:17px;color:var(--grafite);margin-top:8px;white-space:nowrap}"
        ".t1 .cand .pn{font-size:26px;font-weight:600;color:var(--tinta);font-variant-numeric:tabular-nums}"
        ".t1 .vtit{top:590px}"
        ".t1 .leg{top:704px;width:860px}"
        ".t1 .ln{display:flex;align-items:baseline;gap:14px;padding:9px 0;border-bottom:1px solid var(--creme);"
        "font-size:16px;color:var(--tinta)}"
        ".t1 .ln .nm{flex:1;line-height:1.35}.t1 .ln em{font-style:normal;color:var(--cinza);font-size:14px}"
        ".t1 .ln .vv{width:110px;text-align:right;font-weight:600;font-variant-numeric:tabular-nums}"
        ".t1 .ln .pp{width:64px;text-align:right;color:var(--grafite);font-variant-numeric:tabular-nums}"
        ".t1 .sw{display:inline-block;width:12px;height:12px;margin-right:10px;vertical-align:0}"
        ".t1 .s3{background:var(--areia)}.t1 .s4{background:var(--creme)}"
        ".t1 .s5{background:var(--branco);box-shadow:inset 0 0 0 1px var(--areia)}"
    )


def _css_barra() -> str:
    return (
        ".br{pointer-events:none}"
        ".br .sg{position:absolute;top:0;height:56px;pointer-events:auto;cursor:default;display:flex;"
        "align-items:center;padding:0 16px;color:var(--branco);box-shadow:inset -2px 0 0 var(--papel);"
        "transition:opacity .15s ease}"
        ".br .sg b{font-size:24px;font-weight:700;letter-spacing:-.01em;font-variant-numeric:tabular-nums}"
        ".br .sg.dir{justify-content:flex-end}"
        ".br .f{background:var(--azul)}.br .l{background:var(--vermelho)}"
        ".br .s3{background:var(--areia)}.br .s4{background:var(--creme)}"
        ".br .s5{background:var(--branco)}"
        "#htmlContent:has(.sg:hover) .sg:not(:hover){opacity:.45}"
    )


def _css_virada() -> str:
    return (
        ".t1v .sob{position:absolute;left:0;top:0}"
        ".t1v .man{position:absolute;left:0;top:30px;width:730px;font-size:26px}"
        ".t1v .grafico{position:absolute;left:0;top:116px;width:720px;height:640px}"
        ".t1v .sl{position:absolute;left:0;top:0}"
        ".t1v .eixo{stroke:var(--areia);stroke-width:1.5}"
        ".t1v .lpt{fill:none;stroke:var(--vermelho);stroke-width:4;stroke-linecap:round}"
        ".t1v .lpl{fill:none;stroke:var(--azul);stroke-width:4;stroke-linecap:round}"
        ".t1v .seta{fill:none;stroke:var(--tinta);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}"
        ".t1v .rs{position:absolute;font-size:16px;line-height:1.3;color:var(--grafite);white-space:nowrap}"
        ".t1v .rs b{display:block;font-weight:600;font-size:17px}"
        ".t1v .rs.e{right:573px;text-align:right}.t1v .rs.d{left:567px}"
        ".t1v .dl{position:absolute;left:216px;width:140px;text-align:center;font-size:22px;font-weight:700;"
        "letter-spacing:-.01em}"
        ".t1v .anot{position:absolute;right:286px;top:524px;font-size:32px;color:var(--tinta);white-space:nowrap}"
        ".t1v .ano{position:absolute;top:604px;width:120px;margin-left:-60px;text-align:center;font-size:17px;"
        "font-weight:600}.t1v .a1{left:175px}.t1v .a2{left:545px}"
        ".t1v .pe{position:absolute;left:0;top:820px;width:720px}"
    )


def _css_alvos() -> str:
    """Alvos dos pontos da virada: a raiz de cada entrada sem ponteiro (L114), só o círculo transparente pega o mouse
    (fixo, sem animação: L012); no hover, um anel na cor do candidato em volta da bolinha desenhada pela virada."""
    return (
        ".vp{pointer-events:none}"
        ".vp .alvo{position:absolute;width:48px;height:48px;border-radius:50%;pointer-events:auto;cursor:default}"
        ".vp .alvo::after{content:'';position:absolute;left:10px;top:10px;width:28px;height:28px;box-sizing:border-box;"
        "border-radius:50%;border:2.4px solid currentColor;opacity:0;transform:scale(.6);"
        "transition:opacity .15s ease,transform .15s ease}"
        ".vp .alvo:hover::after{opacity:1;transform:scale(1)}"
        ".vp .lula{color:var(--vermelho-escuro)}.vp .flavio{color:var(--azul-escuro)}"
    )


def _css_tt_ponto() -> str:
    """Dossiê do ponto: a ficha branca com clipe do dossiê do candidato, uma linha por grupo (região ou porte)."""
    return (
        ".tp{position:fixed;inset:0;background:var(--papel)}"
        ".tp .ficha{position:absolute;left:14px;top:18px;right:14px;bottom:14px;background:var(--branco);"
        "border:1.5px solid var(--areia);box-shadow:3px 4px 0 rgba(28,25,21,.08)}"
        ".clipe{position:fixed;right:44px;top:4px;width:32px;transform:rotate(8deg);z-index:2}"
        ".tp .ico{position:fixed;right:30px;top:42px;width:36px;opacity:.85;z-index:2}"
        ".tp .cab{position:absolute;left:18px;top:14px;right:64px}"
        ".tp .nm{font-size:22px;font-weight:700;line-height:1.15;letter-spacing:-.01em}"
        ".tp .sub{margin-top:4px;font-size:14px;color:var(--grafite);white-space:nowrap;overflow:hidden;"
        "text-overflow:ellipsis}"
        ".tp .hd,.tp .ln{display:flex;align-items:center;gap:8px}"
        ".tp .hd{position:absolute;left:18px;right:18px;top:76px;font-size:11px;font-weight:600;letter-spacing:.08em;"
        "text-transform:uppercase;white-space:nowrap;color:var(--cinza);border-bottom:1px dashed var(--areia);"
        "padding-bottom:5px}"
        ".tp .lista{position:absolute;left:18px;right:18px;top:100px}"
        ".tp .ln{height:30px;font-size:15px;border-bottom:1px solid var(--creme)}"
        ".tp .g{width:138px;flex:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--tinta)}"
        ".tp .br{width:124px;flex:none;display:flex;align-items:center;gap:6px}"
        ".tp .br i{display:block;height:10px;flex:none}.tp .br b{font-weight:700;font-size:14px}"
        ".tp .lula-bg{background:var(--vermelho)}.tp .flavio-bg{background:var(--azul)}"
        ".tp .pc{flex:1;text-align:right;font-variant-numeric:tabular-nums;color:var(--cinza)}"
        ".tp .ln .pc.on{font-weight:700;color:var(--tinta)}.tp .hd .pc.on{color:var(--tinta)}"
        ".tp .mao{position:absolute;right:20px;bottom:6px;font-size:26px;transform:rotate(-2deg);white-space:nowrap}"
    )


def _alvos() -> dict:
    """Os quatro pontos da virada com grão (ano × candidato): o papel sampling leva 'Candidato UF'[Ano] e [Número]
    (o HTML Content aceita várias colunas no grão, L091); a medida só desenha PT e PL."""
    doc = lib.visual_html(
        "T01_Virada_Alvos", *VIRADA, "T01 · Ponto · HTML", folha_de_estilo=CSS, alt=lib.medida("T01 · Ponto · ALT"),
        z=Z + 6, tab=210, granularidade=("Candidato UF", "Ano"), tooltip_pagina="ttT01Ponto",
        modelo_corpo=f"<style>{_css_alvos()}</style>{{{{content}}}}")
    doc["visual"]["query"]["queryState"]["sampling"]["projections"].append(lib.proj_coluna("Candidato UF", "Número"))
    return doc


def declarar(ctx):
    clipe = "https://vizudados.github.io/eleicoes-2026/midia/arte/dossie/clipe-tinta.png"
    return [
        Visual(P, lib.visual_html(
            "T01_Placar_Html", *PLACAR, "T01 · Placar · HTML", folha_de_estilo=CSS,
            alt=lib.medida("T01 · Placar · ALT"), z=Z, tab=100,
            modelo_corpo=f"<style>{_css_placar()}</style>{{{{content}}}}")),
        Visual(P, lib.visual_html(
            "T01_Barra_Segmentos", *BARRA, "T01 · Barra · HTML", folha_de_estilo=CSS,
            alt=lib.medida("T01 · Barra · ALT"), z=Z + 2, tab=110,
            granularidade=("Candidato UF", "Candidato"), tooltip_pagina="ttT01Candidato",
            modelo_corpo=f"<style>{_css_barra()}</style>{{{{content}}}}")),
        Visual(P, lib.visual_html(
            "T01_Virada_Html", *VIRADA, "T01 · Virada · HTML", folha_de_estilo=CSS,
            alt=lib.medida("T01 · Virada · ALT"), z=Z + 4, tab=200,
            modelo_corpo=f"<style>{_css_virada()}</style>{{{{content}}}}")),
        *pagina_lib.tooltip("ttT01Candidato", "Candidato · dossiê", 460, 300, "T01 · Tooltip candidato · HTML",
                            ordem=110, folha_de_estilo=CSS),
        Visual(P, _alvos()),
        *pagina_lib.tooltip("ttT01Ponto", "Ponto da virada · dossiê", 460, 330, "T01 · Tooltip ponto · HTML",
                            ordem=111, folha_de_estilo=CSS,
                            modelo_corpo=f"<style>{_css_tt_ponto()}</style>{{{{content}}}}"
                                         f"<img class='clipe' alt='' src='{clipe}'/>"),
    ]
