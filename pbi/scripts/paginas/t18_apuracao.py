# -*- coding: utf-8 -*-
"""18 · Apuração — quem está na frente na apuração do 2º turno (dono: main). A tela se atualiza sozinha: o coletor
(apuracao/coletar.py) grava a API do TSE no GitHub a cada minuto e o Power BI lê os arquivos (pbi/modelo/apuracao.py).

  T18_Placar_Html   placar: horas do TSE e da coleta, os dois candidatos (contador), selo do estado, frase do momento,
                    relógio até as 17h de 25/10 (aguardando; conta no navegador) e a barra de seções
  T18_Curva_Html    a curva da noite (Brasil): as linhas se desenham a cada hora nova do TSE
  T18_Mapa_Html     mapa de quadrados (granularidade UF): cor de quem lidera; clique filtra o placar; dossiê da UF no
                    tooltip ttT18Uf. Não recebe o filtro de UF da casca (mostra sempre as 27 + exterior)
  T18_Mapa_Exterior alvo transparente sobre o EX do mapa: abre o tooltip do exterior país a país (ttT18Exterior) e,
                    no clique, filtra o placar pelo exterior como o quadrado de baixo
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
    ".t18p .frase{position:absolute;left:0;right:0;top:300px;display:flex;align-items:center;gap:14px}"
    ".t18p .visto{font-family:var(--mao);font-size:44px;line-height:1;color:var(--tinta);margin-top:-8px}"
    ".t18p .relogio{position:absolute;left:0;top:368px;display:flex;align-items:baseline;gap:18px}"
    ".t18p .relogio .num{font-size:56px;font-variant-numeric:tabular-nums}"
    ".t18p .relogio + .txt{position:absolute;left:0;top:446px}"
    ".t18p .secoes{position:absolute;left:0;right:0;top:362px}"
    f".t18p .trilho{{position:relative;height:30px;background:{C['creme']};margin:10px 0 12px 0;overflow:hidden}}"
    f".t18p .enche{{height:100%;background:{C['tinta']}}}"
    f".t18p .trilho .num{{position:absolute;left:12px;top:4px;font-size:20px;color:{C['papel']};mix-blend-mode:difference}}"
    ".t18p .secoes .nota{font-size:15px;color:var(--grafite)}"
)

# relógio regressivo até as 17h de 25/10 (20h UTC), no navegador: a tela "anda" mesmo sem nova coleta
JS_RELOGIO = (
    "<script>(function(){var W=window;function t(){var e=document.getElementById('t18rel');if(!e){return;}"
    "var d=Date.UTC(2026,9,25,20,0,0)-Date.now();if(d<=0){e.textContent='as urnas já fecharam';return;}"
    "var D=Math.floor(d/864e5),h=Math.floor(d%864e5/36e5),m=Math.floor(d%36e5/6e4),s=Math.floor(d%6e4/1e3);"
    "e.textContent=(D?D+(D===1?' dia, ':' dias, '):'')+h+' h '+(m<10?'0':'')+m+' min '+(s<10?'0':'')+s+' s';}"
    "if(W.__t18){clearInterval(W.__t18);}t();W.__t18=setInterval(t,1000);})();</script>"
)

CSS_CURVA = (
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
    f"<style>{CSS_MAPA}</style><div class='mapa-fixo'><div class='rot entra'>QUEM LIDERA EM CADA UNIDADE · "
    f"% DAS SEÇÕES NO CANTO</div><div class='leg entra d10'><span><i style='background:{C['rosa']}'></i>Lula lidera"
    f"</span><span><i style='background:{C['azul_claro']}'></i>Flávio lidera</span><span><i style='border:2px dashed "
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


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T18_Placar_Html", *PLACAR, "T18 · Placar · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_PLACAR}</style>{{{{content}}}}{JS_RELOGIO}",
                                  alt=lib.medida("T18 · Placar · ALT"), z=lib.CAMADAS["conteudo"], tab=100)),
        Visual(P, lib.visual_html("T18_Curva_Html", *CURVA, "T18 · Curva · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_CURVA}</style>{{{{content}}}}",
                                  alt=lib.medida("T18 · Curva · ALT"), z=lib.CAMADAS["conteudo"] + 1, tab=110)),
        Visual(P, lib.visual_html("T18_Mapa_Html", *MAPA, "T18 · Mapa · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=CORPO_MAPA, granularidade=("UF", "UF"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT18Uf",
                                  alt=lib.medida("T18 · Mapa · ALT"), z=lib.CAMADAS["conteudo"] + 2, tab=120)),
        *pagina_lib.tooltip("ttT18Uf", "Apuração · UF", 440, 280, "T18 · Tooltip UF · HTML", ordem=180,
                            folha_de_estilo=CSS, modelo_corpo=f"<style>{CSS_TT}</style>{{{{content}}}}"),
        # o mapa mostra sempre todas as unidades: o filtro de UF da casca não chega nele
        Interacao(P, "T18_Casca_Filtro", "T18_Mapa_Html", "NoFilter"),
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
