# -*- coding: utf-8 -*-
"""25 · Apuração — resultado final do 2º turno de 25/10/2026 (dono: main).

Lula foi eleito. A curva nacional conserva os momentos da noite: Flávio passou à frente às 19h45 e Lula retomou
a liderança às 20h24min14s. O clique numa hora consulta o resultado parcial daquele momento; outro clique retorna ao
resultado final. Mapa e resultado leem as UFs escolhidas pela casca; a curva permanece nacional.
Os identificadores técnicos Placar foram preservados para manter a linhagem dos visuais e das medidas.
Não há relógio regressivo, hora de coleta nem atualização contínua.
"""
from __future__ import annotations

import estilo
import exterior
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual

P = "T18"
CSS = "Estilo · CSS"
C = estilo.COR

PLACAR = (150, 140, 900, 470)
CURVA = (150, 640, 900, 340)
MAPA = (1110, 140, 660, 860)
# o EX do mapa (coluna 5, linha 0 da grade: left 22 + 5 × 104, top 52), com 4 px de folga para o realce do mouse
EX_ALVO = (MAPA[0] + 22 + 5 * 104 - 4, MAPA[1] + 52 - 4, 96 + 8, 84 + 8)

CSS_PLACAR = (
    ".t18p .topo{position:absolute;left:0;top:30px}"
    ".t18p .par{position:absolute;left:0;right:0;top:74px;display:flex;gap:72px;align-items:flex-start}"
    ".t18p .cand{min-width:330px}"
    ".t18p .cand .pct{font-size:100px;margin:12px 0 10px 0}"
    ".t18p .cand .votos{font-size:20px;color:var(--grafite)}"
    f".t18p .selo{{position:absolute;right:6px;top:-62px;transform:rotate(-5deg);border:3px solid "
    f"{C['tinta']};outline:1.5px solid {C['tinta']};outline-offset:3px;padding:10px 16px;font-weight:700;"
    "font-size:15px;letter-spacing:.16em;white-space:nowrap}"
    ".t18p .frase{position:absolute;left:0;right:0;top:280px;font-size:23px;line-height:1.35;display:flex;align-items:center;gap:14px}"
    ".t18p .visto{font-family:var(--mao);font-size:44px;line-height:1;color:var(--tinta);margin-top:-8px}"
        ".t18p .secoes{position:absolute;left:0;right:0;top:362px}"
    f".t18p .trilho{{position:relative;height:30px;background:{C['creme']};margin:10px 0 12px 0;overflow:hidden}}"
    f".t18p .enche{{height:100%;background:{C['tinta']}}}"
    f".t18p .trilho .num{{position:absolute;left:12px;top:4px;font-size:20px;color:{C['papel']};mix-blend-mode:difference}}"
    ".t18p .secoes .nota{font-size:15px;color:var(--grafite)}"
)

CSS_CURVA = (
    ".t18c .parada{font-family:var(--mao);font-size:28px;fill:var(--grafite)}"
    ".t18c .escala{position:absolute;left:0;top:25px;font-size:13px;color:var(--grafite)}"
    ".t18c .rot{position:absolute;left:0;top:6px}"
    ".t18c svg{position:absolute;left:0;top:44px}"
    f".t18c .g{{stroke:{C['areia']};stroke-width:1}}.t18c .g.meio{{stroke:{C['grafite']};stroke-dasharray:4 5}}"
    f".t18c .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    f".t18c .ll{{stroke:{C['vermelho']};stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}}"
    f".t18c .lf{{stroke:{C['azul']};stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}}"
    f".t18c .pl{{fill:{C['vermelho']}}}.t18c .pf{{fill:{C['azul']}}}"
    f".t18c .rl{{fill:{C['vermelho_escuro']};font-size:17px;font-weight:600;font-family:var(--fonte)}}"
    f".t18c .rf{{fill:{C['azul_escuro']};font-size:17px;font-weight:600;font-family:var(--fonte)}}"
    f".t18c .vz{{font-family:var(--mao);font-size:30px;fill:{C['grafite']}}}"
)

CSS_MAPA = (
    ".mq{pointer-events:none}"
    "@keyframes qCor{from{background:var(--creme)}}"
    ".mq .q{position:absolute;width:96px;height:84px;border-radius:3px;pointer-events:auto;cursor:pointer;"
    "transform-origin:center;animation-name:eEscala,qCor;animation-duration:.6s,1.6s;"
    "animation-timing-function:cubic-bezier(.2,.9,.3,1.3),ease-out;animation-fill-mode:both,both}"
    f".mq .ql{{background:{C['rosa']}}}.mq .qf{{background:{C['azul_claro']}}}.mq .qz{{background:{C['creme']}}}"
    f".mq .ex{{border:2px dashed {C['grafite']};background-clip:padding-box}}"
    ".mq .q b{position:absolute;left:10px;top:7px;font-size:21px;font-weight:700;letter-spacing:.02em}"
    ".mq .q i{position:absolute;right:8px;top:10px;font-style:normal;font-size:12px;font-weight:600;opacity:.75}"
    ".mq .q span{position:absolute;left:10px;bottom:7px;font-size:17px;font-weight:700}"
    f".mq .ql span{{color:{C['vermelho_escuro']}}}.mq .qf span{{color:{C['azul_escuro']}}}"
    ".mq .q:hover{outline:2px solid var(--tinta);outline-offset:2px}"
    ".mapa-fixo{position:fixed;inset:0;pointer-events:none}"
    ".mapa-fixo .rot{position:absolute;left:22px;top:12px}"
    ".mapa-fixo .leg{position:absolute;left:22px;bottom:10px;display:flex;gap:22px;align-items:center;font-size:15px;"
    "color:var(--grafite)}"
    ".mapa-fixo .leg i{display:inline-block;width:16px;height:16px;border-radius:2px;margin-right:8px;"
    "vertical-align:-2px}"
    ".mapa-fixo .dica{position:absolute;right:22px;bottom:10px;font-family:var(--mao);font-size:24px;"
    "color:var(--grafite)}"
)
CORPO_MAPA = (
    f"<style>{CSS_MAPA}</style><div class='mapa-fixo'><div class='rot entra'>QUEM VENCEU EM CADA UNIDADE · "
    f"% DAS SEÇÕES NO CANTO</div><div class='leg entra d10'><span><i style='background:{C['rosa']}'></i>Lula venceu"
    f"</span><span><i style='background:{C['azul_claro']}'></i>Flávio venceu</span><span><i style='border:2px dashed "
    f"{C['grafite']}'></i>EX = exterior</span></div><div class='dica entra d12'>clique num estado</div></div>"
    "{{content}}"
)

CSS_TT = (
    f".tt18{{background:{C['branco']};border:1.5px solid {C['areia']};padding:26px 26px 18px 26px;"
    "box-shadow:0 10px 24px rgba(28,25,21,.16)}"
    f".tt18 .fita{{position:absolute;left:150px;top:-10px;width:120px;height:26px;background:{C['areia']};"
    "opacity:.7;transform:rotate(-3deg)}"
    ".tt18 .rot{margin-bottom:12px}"
    ".tt18 .linha{display:flex;align-items:baseline;gap:12px}.tt18 .linha .num{font-size:34px}"
    f".tt18 .barra{{display:flex;height:12px;margin:8px 0 10px 0;background:{C['creme']}}}"
    f".tt18 .barra .bl{{background:{C['vermelho']}}}.tt18 .barra .bf{{background:{C['azul']};margin-left:auto}}"
    ".tt18 .txt{font-size:15px;margin-top:12px;color:var(--tinta)}"
    ".tt18 .nota{margin-top:6px}"
    ".tt18 .mao{position:absolute;right:22px;top:20px;transform:rotate(-4deg)}"
)


# os pontos da curva da noite (23/10/2026): a faixa de clique de cada atualização; a linha e os pontos aparecem no mouse e
# ficam acesos na atualização clicada (o HTML Content marca as outras com .unselected)
CSS_PONTOS = (
    ".t18k{pointer-events:none}"
    ".t18k .al{position:absolute;top:58px;height:244px;pointer-events:auto;cursor:pointer}"
    f".t18k .gu{{position:absolute;top:58px;height:244px;width:2px;background:{C['tinta']};opacity:0;"
    "transition:opacity .15s;pointer-events:none}"
    f".t18k .pd{{position:absolute;width:12px;height:12px;border-radius:50%;box-shadow:0 0 0 2px {C['papel']};"
    "opacity:0;transition:opacity .15s;pointer-events:none}"
    f".t18k .pd.l{{background:{C['vermelho']}}}.t18k .pd.f{{background:{C['azul']}}}"
    f".t18k .hr{{position:absolute;top:34px;transform:translateX(-50%);font-size:13px;font-weight:700;"
    f"background:{C['tinta']};color:{C['papel']};padding:1px 6px;white-space:nowrap;opacity:0;pointer-events:none}}"
    ".t18k:hover .gu{opacity:.35}.t18k:hover .pd{opacity:1}"
    "body:has(.t18k.unselected) .t18k:not(.unselected) .gu{opacity:1}"
    "body:has(.t18k.unselected) .t18k:not(.unselected) .pd,body:has(.t18k.unselected) .t18k:not(.unselected) .hr"
    "{opacity:1}"
)
CSS_TT_MOMENTO = (
    ".tt18m .duo{display:flex;gap:40px;margin:2px 0 2px 0}"
    ".tt18m .duo small{display:block;font-size:13px;font-weight:600;letter-spacing:.12em}"
    ".tt18m .duo .num{font-size:32px}"
    ".tt18m .duo .vr{font-size:14px;font-weight:600;color:var(--grafite);margin-left:8px}"
    ".tt18m .txt{padding-bottom:30px}"
    ".tt18m .mao{top:auto;bottom:10px;font-size:26px}"
    ".tt18m .mao.lula{color:var(--vermelho-escuro)}.tt18m .mao.flavio{color:var(--azul-escuro)}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T18_Placar_Html", *PLACAR, "T18 · Placar · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PLACAR}</style>{{{{content}}}}",
                                  alt=lib.medida("T18 · Placar · ALT"), z=lib.CAMADAS["conteudo"], tab=100)),
        Visual(P, lib.visual_html("T18_Curva_Html", *CURVA, "T18 · Curva · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_CURVA}</style>{{{{content}}}}",
                                  alt=lib.medida("T18 · Curva · ALT"), z=lib.CAMADAS["conteudo"] + 1, tab=110)),
        Visual(P, lib.visual_html("T18_Curva_Pontos", *CURVA, "T18 · Curva pontos · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PONTOS}</style>{{{{content}}}}",
                                  granularidade=("Apuração histórico", "AtualizadoTSE"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=False, tooltip_pagina="ttT18Momento",
                                  alt=lib.medida("T18 · Curva pontos · ALT"), z=lib.CAMADAS["conteudo"] + 3, tab=115)),
        *pagina_lib.tooltip("ttT18Momento", "Apuração · atualização", 470, 300, "T18 · Tooltip momento · HTML",
                            ordem=182, folha_de_estilo=CSS,
                            modelo_corpo=f"<style>{CSS_TT}{CSS_TT_MOMENTO}</style>{{{{content}}}}"),
        # o clique numa atualização da curva muda só o placar (o retrato daquele momento): a curva de fundo não recebe
        # (o filtro em AtualizadoTSE a reduziria a um ponto), o mapa e o exterior seguem no resultado final (o histórico só tem o
        # Brasil) e o filtro de UF não tem o que mostrar com ele
        Interacao(P, "T18_Curva_Pontos", "T18_Curva_Html", "NoFilter"),
        Interacao(P, "T18_Curva_Pontos", "T18_Mapa_Html", "NoFilter"),
        Interacao(P, "T18_Curva_Pontos", "T18_Mapa_Exterior", "NoFilter"),
        Interacao(P, "T18_Curva_Pontos", "T18_Casca_Filtro", "NoFilter"),
        Visual(P, lib.visual_html("T18_Mapa_Html", *MAPA, "T18 · Mapa · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=CORPO_MAPA, granularidade=("UF", "UF"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT18Uf",
                                  alt=lib.medida("T18 · Mapa · ALT"), z=lib.CAMADAS["conteudo"] + 2, tab=120)),
        *pagina_lib.tooltip("ttT18Uf", "Apuração · UF", 440, 280, "T18 · Tooltip UF · HTML", ordem=180,
                            folha_de_estilo=CSS, modelo_corpo=f"<style>{CSS_TT}</style>{{{{content}}}}"),
        # o mapa mostra sempre todas as unidades: o filtro de estado da casca não chega nele; e o clique num quadrado não
        # encolhe a árvore do filtro (24/10/2026: com a árvore Região › Estado, a lista ficaria só com a UF clicada)
        Interacao(P, "T18_Casca_Filtro", "T18_Mapa_Html", "NoFilter"),
        Interacao(P, "T18_Mapa_Html", "T18_Casca_Filtro", "NoFilter"),
        # o exterior país a país (pedido do Alisson, 23/10/2026): o alvo fica sobre o EX e não recebe filtro do mapa
        # nem da casca (some se recebesse); o mapa também não recebe o clique do alvo
        *exterior.declarar(P, "T18_Mapa_Exterior", EX_ALVO, "Exterior · ao vivo · HTML", ordem=181, cruzar=True,
                           altura=exterior.ALTURA + 34,
                           css_alvo=".ax{cursor:pointer;border-radius:5px}.ax:hover{box-shadow:inset 0 0 0 2px "
                                    + C["tinta"] + "}"),
        Interacao(P, "T18_Casca_Filtro", "T18_Mapa_Exterior", "NoFilter"),
        Interacao(P, "T18_Mapa_Html", "T18_Mapa_Exterior", "NoFilter"),
        Interacao(P, "T18_Mapa_Exterior", "T18_Mapa_Html", "NoFilter"),
        # o filtro de UF não lista o exterior: filtrado pelo clique no EX, ficaria sem valores
        Interacao(P, "T18_Mapa_Exterior", "T18_Casca_Filtro", "NoFilter"),
    ]
