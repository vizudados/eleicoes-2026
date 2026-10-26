# -*- coding: utf-8 -*-
"""20 · 2º turno — pesquisas diante do resultado final (dono: campanha).

A manchete conta as pesquisas de votos totais depois do 1º turno e compara a direção com a urna final do TSE.
Os dois quadriculados conservam o antes/depois do 1º turno e recebem a referência final ao lado.
A curva normaliza cada pesquisa entre Lula e Flávio (soma 100%) para comparar com os válidos da urna;
o resumo superior preserva os percentuais publicados em votos totais e válidos.

O período da casca destaca apenas pesquisas de campo inteiro dentro da janela de cada debate.
Campo atravessando debate não entra no recorte. Ausência no levantamento não promete coleta futura.
O ponto grande na data da eleição é a urna; os demais pontos têm grão Pesquisa[Id] e dossiê próprio.
Clique no ponto ou quadrinho de rejeição destaca a série do instituto; a curva de fundo não recebe o clique.
A rejeição compara a última medição antes/depois somente dentro do mesmo instituto.
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual
from paginas import _campanha as cp

P = "T17"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]

PLACAR = (150, 140, 820, 350)
REJEICAO = (1010, 140, 760, 350)
CURVA = (150, 505, 1620, 495)

CSS_PLACAR = (
    ".t17a .urna-final{position:absolute;left:584px;top:232px;width:236px;border-left:1px solid var(--areia);padding-left:16px;font-size:15px;line-height:1.7}"
    ".t17a .urna-final .num{font-size:23px}.t17a .urna-final .rot{margin-bottom:2px}"

    ".t17a .linha{position:absolute;left:0;top:26px;display:flex;align-items:flex-start;gap:28px}"
    ".t17a .hero{display:flex;align-items:baseline;gap:12px;white-space:nowrap}"
    ".t17a .hero .num{font-size:112px;letter-spacing:-.04em}"
    ".t17a .hero .de{font-size:40px;font-weight:600;color:var(--grafite)}"
    ".t17a .lado{padding-top:16px;max-width:420px}"
    ".t17a .lado .man{font-size:20px;line-height:1.3}"
    ".t17a .lado .txt{font-size:15px;margin-top:6px;line-height:1.35}"
    ".t17a .manchete{position:absolute;left:0;top:160px;width:820px;font-size:24px}"
    ".t17a .waf{position:absolute;top:232px}"
    ".t17a .waf .rot{margin-bottom:8px}"
    ".t17a .grade{display:grid;grid-template-columns:repeat(16,11px);gap:3px}"
    ".t17a .grade i{display:block;width:11px;height:11px;border-radius:2px;transform-origin:center;"
    "animation-name:eEscala,qCor17;animation-duration:.5s,1.4s;animation-timing-function:cubic-bezier(.2,.9,.3,1.3),"
    "ease-out;animation-fill-mode:both,both}"
    "@keyframes qCor17{from{background:var(--creme)}}"
    f".t17a .grade .l{{background:{C['vermelho']}}}.t17a .grade .f{{background:{C['azul']}}}"
    f".t17a .grade .e{{background:{C['areia']}}}"
    ".t17a .cont{margin-top:8px;font-size:15px;color:var(--grafite);display:flex;gap:16px}"
    ".t17a .cont b{font-weight:700}"
    # instituto em destaque (clique num quadrinho da rejeição ou num ponto da curva): os quadradinhos dele com contorno,
    # os outros esmaecem; a contagem embaixo passa a ser a dele, com o nome
    ".t17a .grade i.fora{opacity:.22}"
    f".t17a .grade i.fx{{box-shadow:0 0 0 1.5px {C['papel']},0 0 0 3px {C['tinta']}}}"
    ".t17a .cont .fo{font-weight:600;color:var(--tinta);white-space:nowrap}"
    # período sem pesquisa (nenhuma registrada no recorte): o texto no lugar do número grande, nunca um zero
    ".t17a .vazio{font-size:40px;font-weight:700;letter-spacing:-.02em;line-height:1.05;color:var(--grafite);"
    "padding-top:26px;white-space:nowrap}"
)

CSS_REJ = (
    ".t17r .man{position:absolute;left:0;top:24px;width:760px;font-size:20px;line-height:1.3}"
    ".t17r .nota{position:absolute;left:0;top:82px;width:760px;font-size:13px}"
    ".t17r .nota i{display:inline-block;width:18px;height:3px;vertical-align:4px;margin:0 6px 0 0}"
)
CSS_PAINEIS = (
    ".t17q{pointer-events:none}"
    f".t17q .pn{{position:absolute;width:144px;height:104px;pointer-events:auto;cursor:help;border-top:1.5px solid "
    f"{C['areia']};padding-top:6px}}"
    f".t17q .pn:hover{{background:rgba(229,219,200,.55);box-shadow:0 0 0 4px rgba(229,219,200,.55)}}"
    ".t17q .pn b{display:block;font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".t17q .pn svg{position:absolute;left:0;top:24px}"
    ".t17q .pn span{position:absolute;left:0;bottom:0;font-size:13px;color:var(--cinza);white-space:nowrap}"
    f".t17q .vl{{fill:{C['vermelho_escuro']};font-size:13px;font-weight:700;font-family:var(--fonte)}}"
    f".t17q .vf{{fill:{C['azul_escuro']};font-size:13px;font-weight:700;font-family:var(--fonte)}}"
    ".t17q .va{font-weight:500;opacity:.85}"
    f".t17q .ll{{stroke:{C['vermelho']};stroke-width:2.6;stroke-linecap:round}}"
    f".t17q .lf{{stroke:{C['azul']};stroke-width:2.6;stroke-linecap:round}}"
    f".t17q .al{{fill:{C['papel']};stroke:{C['vermelho']};stroke-width:2}}.t17q .af{{fill:{C['papel']};stroke:{C['azul']};"
    "stroke-width:2}"
    f".t17q .dl{{fill:{C['vermelho']}}}.t17q .df{{fill:{C['azul']}}}"
    # clique num ponto da curva: o quadrinho do instituto daquela pesquisa em destaque, os outros esmaecem
    ".t17q{transition:opacity .25s}.t17q.fora{opacity:.28}"
    f".t17q.fx .pn{{background:rgba(229,219,200,.55);box-shadow:0 0 0 4px rgba(229,219,200,.55);"
    f"border-top-color:{C['tinta']}}}"
)


def _mistura(base: str, cor: str, t: float) -> str:
    """Cor de `base` com `t` de `cor` (as duas zonas da curva usam a mesma mistura: tratamento igual para os dois)."""
    a = [int(base[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(cor[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * (1 - t) + y * t):02X}" for x, y in zip(a, b))


def corpo_curva() -> str:
    css = (
        ".t17g .cab{position:absolute;left:0;top:0;right:0}"
        ".t17g .cab .man{margin-top:8px;font-size:24px}"
        ".t17g svg.pl{position:absolute;left:0;top:72px}"
        f".t17g .zf{{fill:{_mistura(C['branco'], C['azul_claro'], .3)}}}"
        f".t17g .zl{{fill:{_mistura(C['branco'], C['rosa'], .3)}}}"
        f".t17g .g{{stroke:{C['areia']};stroke-width:1}}.t17g .g0{{stroke:{C['grafite']};stroke-width:1.2}}"
        f".t17g .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
        f".t17g .ex.b{{font-weight:700;fill:{C['tinta']}}}"
        f".t17g .zt{{font-size:15px;font-weight:600;font-family:var(--fonte)}}"
        f".t17g .zt.f{{fill:{C['azul_escuro']}}}.t17g .zt.l{{fill:{C['vermelho_escuro']}}}"
        ".t17g .ur{fill:var(--vermelho);stroke:var(--papel);stroke-width:3} .t17g .ur-t{fill:var(--vermelho-escuro);font-size:15px;font-weight:700;font-family:var(--fonte)}"
        f".t17g .mk{{stroke:{C['tinta']};stroke-width:1.4;stroke-dasharray:5 6}}"
        f".t17g .mk.s{{stroke:{C['cinza']};stroke-dasharray:2 5}}"
        f".t17g .mm{{stroke:{C['tinta']};stroke-width:3.6;fill:none;stroke-linecap:round;stroke-linejoin:round}}"
        # a faixa do campo do período escolhido (filtro Período): um véu de tinta leve sobre as duas zonas
        f".t17g .per{{fill:{C['tinta']};fill-opacity:.08}}"
        ".t17g .fim{position:absolute;white-space:nowrap}"
        ".t17g .fim .rot{font-size:13px}"
        ".t17g .fim .num{font-size:24px;margin-top:2px}"
        f".t17g .mao{{position:absolute;font-size:28px;color:{C['tinta']};transform:rotate(-3deg);white-space:nowrap}}"
        f".t17g .seta{{position:absolute;width:70px;height:56px;background:url("
        f"{cp.img('arte/limpos/rabiscos/seta-curva-esquerda-tinta.png', 140)}) center/contain no-repeat}}"
        f".t17g .urna{{position:absolute;width:48px;height:44px;background:url({cp.icone('urna', 96)}) center/contain "
        "no-repeat}"
        ".t17g .leg{position:absolute;left:0;bottom:0;font-size:13px;color:var(--cinza)}"
        ".t17g .leg i{display:inline-block;width:11px;height:11px;border-radius:50%;margin:0 6px 0 0;vertical-align:-1px}"
        ".t17g .leg b{font-weight:600;color:var(--grafite);margin-right:16px}"
    )
    return f"<style>{css}</style>{cp.defs_rabisco()}{{{{content}}}}"


CSS_PONTOS = (
    ".t17p{pointer-events:none}"
    ".t17p .pt{position:absolute;width:12px;height:12px;border-radius:50%;pointer-events:auto;cursor:help;"
    "transform-origin:center;animation:eEscala .5s cubic-bezier(.2,.9,.3,1.3) both}"
    ".t17p .pt::after{content:'';position:absolute;inset:-2px;border-radius:50%}"
    f".t17p .f{{background:{C['azul']}}}.t17p .l{{background:{C['vermelho']}}}.t17p .e{{background:{C['cinza']}}}"
    f".t17p .sim.f{{background:{C['papel']};box-shadow:inset 0 0 0 2.4px {C['azul']}}}"
    f".t17p .sim.l{{background:{C['papel']};box-shadow:inset 0 0 0 2.4px {C['vermelho']}}}"
    f".t17p .sim.e{{background:{C['papel']};box-shadow:inset 0 0 0 2.4px {C['cinza']}}}"
    f".t17p .pt:hover{{outline:2px solid {C['tinta']};outline-offset:2px}}"
    # a série do instituto: o traço até a pesquisa anterior dele e o nome na última, escondidos; aparecem com a série em
    # destaque (fx = clique num quadrinho da rejeição; ou o próprio clique num ponto, pelas regras de _serie_css)
    ".t17p{transition:opacity .25s}"
    ".t17p .sg{position:absolute;left:0;top:0;overflow:visible;opacity:0;transition:opacity .25s}"
    f".t17p .sg line{{stroke:{C['marrom']};stroke-width:2.4;stroke-linecap:round;stroke-dasharray:7 4}}"
    ".t17p .nm{position:absolute;transform:translateX(-50%);opacity:0;transition:opacity .25s;font-size:15px;"
    f"font-weight:700;white-space:nowrap;color:{C['marrom']};background:{C['papel']};padding:1px 6px;"
    f"box-shadow:0 0 0 1.5px {C['marrom']}}}"
    ".t17p.fx .sg,.t17p.fx .nm{opacity:1}"
    f".t17p.fx .pt{{outline:2px solid {C['marrom']};outline-offset:1.5px}}"
    ".t17p.fora,.t17p.unselected{opacity:.18}"
)


def _serie_css(n: int = 40) -> str:
    """Clique num ponto: o HTML Content marca as outras entradas com .unselected; estas regras devolvem a cor às do
    MESMO instituto (classe i<n>, T17 · série · número do instituto) e mostram o traço e o nome da série dele."""
    regras = []
    for k in range(1, n + 1):
        cond = f"body:has(.t17p.unselected):has(.t17p.i{k}:not(.unselected))"
        regras.append(f"{cond} .t17p.i{k}{{opacity:1}}{cond} .t17p.i{k} .sg,{cond} .t17p.i{k} .nm{{opacity:1}}"
                      f"{cond} .t17p.i{k} .pt{{outline:2px solid {C['marrom']};outline-offset:1.5px}}")
    return "".join(regras)


CSS_TT_PESQ = ".tt17p .par{margin-top:2px}"
CSS_TT_REJ = (
    ".tt17r svg{display:block;margin:6px 0 2px 0}"
    f".tt17r .ll{{stroke:{C['vermelho']};stroke-width:2.4;fill:none}}.tt17r .lf{{stroke:{C['azul']};stroke-width:2.4;"
    "fill:none}"
    f".tt17r .pl{{fill:{C['vermelho']}}}.tt17r .pf{{fill:{C['azul']}}}"
    f".tt17r .g{{stroke:{C['areia']};stroke-width:1}}.tt17r .mk{{stroke:{C['tinta']};stroke-width:1.2;"
    "stroke-dasharray:4 5}"
    f".tt17r .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T17_Placar_Html", *PLACAR, "T17 · Placar · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PLACAR}</style>{{{{content}}}}",
                                  alt=lib.medida("T17 · Placar · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T17_Rejeicao_Html", *REJEICAO, "T17 · Rejeição · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_REJ}</style>{{{{content}}}}",
                                  alt=lib.medida("T17 · Rejeição · ALT"), z=Z + 1, tab=110)),
        Visual(P, lib.visual_html("T17_Rejeicao_Paineis", *REJEICAO, "T17 · Painéis · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PAINEIS}</style>{{{{content}}}}",
                                  granularidade=("Rejeição", "Instituto"), tooltip_pagina="ttT17Rejeicao",
                                  filtro_cruzado=True, transparencia_nao_selecionados=True,
                                  alt=lib.medida("T17 · Painéis · ALT"), z=Z + 2, tab=120)),
        Visual(P, lib.visual_html("T17_Curva_Html", *CURVA, "T17 · Curva · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_curva(), alt=lib.medida("T17 · Curva · ALT"), z=Z + 3, tab=130)),
        Visual(P, lib.visual_html("T17_Curva_Pontos", *CURVA, "T17 · Pontos · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PONTOS}{_serie_css()}</style>{{{{content}}}}",
                                  granularidade=("Pesquisa", "Id"), tooltip_pagina="ttT17Pesquisa",
                                  filtro_cruzado=True, transparencia_nao_selecionados=False,
                                  alt=lib.medida("T17 · Pontos · ALT"), z=Z + 4, tab=140)),
        *pagina_lib.tooltip("ttT17Pesquisa", "2º turno · pesquisa", 470, 300, "T17 · Tooltip pesquisa · HTML",
                            ordem=270, folha_de_estilo=CSS, modelo_corpo=cp.dossie("lupa", CSS_TT_PESQ)),
        *pagina_lib.tooltip("ttT17Rejeicao", "2º turno · rejeição", 480, 360, "T17 · Tooltip rejeição · HTML",
                            ordem=271, folha_de_estilo=CSS, modelo_corpo=cp.dossie("balanca", CSS_TT_REJ)),
        # filtro cruzado (23/10/2026): o quadrinho da rejeição e o ponto da curva escolhem um instituto; os pontos
        # mostram a série dele, o placar contorna os quadradinhos dele e os quadrinhos destacam o da pesquisa clicada.
        # Exceções: a curva de fundo (a média de todos) não recebe o clique do ponto (o filtro em Pesquisa[Id]
        # esvaziaria a média) nem o do quadrinho (a rejeição não mexe nela); o cabeçalho da rejeição não recebe o clique
        # do próprio quadrinho (ele já se destaca sozinho)
        Interacao(P, "T17_Curva_Pontos", "T17_Curva_Html", "NoFilter"),
        Interacao(P, "T17_Rejeicao_Paineis", "T17_Curva_Html", "NoFilter"),
        Interacao(P, "T17_Rejeicao_Paineis", "T17_Rejeicao_Html", "NoFilter"),
    ]
