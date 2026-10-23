# -*- coding: utf-8 -*-
"""10 · Pesquisas — o que as pesquisas diziam antes da urna? (dono: agente das telas da campanha)

A história: na véspera do 1º turno, 13 dos 18 institutos davam Lula à frente; a urna deu Flávio por 1,9 ponto. Cada
pesquisa é um ponto numa régua (Lula à frente ← empate → Flávio à frente) e a urna é a linha. O erro foi quase todo no
número de Flávio: na média dos 10 institutos que divulgaram votos válidos, Lula saiu certo e Flávio, 3,8 pontos abaixo.

  T10_Resposta_Html     "13 de 18" (contadores), a manchete e o como ler da régua
  T10_Erro_Html         onde foi o erro: média das pesquisas com válidos × urna, Lula e Flávio (setas desenhadas)
  T10_Regua_Html        fundo da régua: título, as duas metades tingidas, o empate, a urna (traço à mão com laço), os
                        números do eixo, a legenda e a nota à mão
  T10_Regua_Institutos  uma linha por instituto (granularidade Pesquisa[Instituto]): nome, haste a partir do empate,
                        marca (círculo = válidos, quadrado = totais) e a vantagem; dossiê ttT10Instituto com a
                        trajetória do instituto no 1º turno. Filtro cruzado (23/10/2026, revisão de interação): o
                        clique num instituto leva o quadro "onde foi o erro" para a última pesquisa dele contra a urna
                        (nos válidos, Lula e Flávio um a um; nos totais, só a diferença); os outros institutos
                        esmaecem. A resposta e o fundo da régua não mudam (NoFilter: são o retrato de todos).
  T10_Erro_Alvos        faixas transparentes sobre as linhas de Lula e de Flávio do quadro do erro (granularidade
                        'Candidato ano'[Partido]: PT, PL) → dossiê ttT10Erro: o que cada instituto com válidos deu ao
                        candidato, um por linha, contra a urna (a média esconde o espalhamento)
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual
from paginas import _campanha as cp

P = "T10"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]

RESPOSTA = (150, 140, 560, 400)
ERRO = (150, 572, 560, 428)
REGUA = (740, 140, 1030, 860)

CSS_RESPOSTA = (
    ".t10r .hero{position:absolute;left:0;top:30px;display:flex;align-items:baseline;gap:18px}"
    ".t10r .hero .num{font-size:120px;letter-spacing:-.04em}"
    ".t10r .hero .de{font-size:40px;font-weight:600;color:var(--grafite)}"
    ".t10r .sub{position:absolute;left:0;top:170px;font-size:26px;font-weight:600;letter-spacing:-.01em}"
    ".t10r .tit{position:absolute;left:0;top:222px;width:540px;font-size:34px}"
    ".t10r .txt{position:absolute;left:0;top:300px;width:530px}"
)

CSS_ERRO = (
    ".t10e .man{margin-top:8px;width:540px}"
    ".t10e svg{position:absolute;left:0;top:96px}"
    f".t10e .trilho{{stroke:{C['areia']};stroke-width:1.5;stroke-dasharray:2 5}}"
    f".t10e .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    f".t10e .nm{{font-size:17px;font-weight:600;font-family:var(--fonte)}}"
    f".t10e .nm.l{{fill:{C['vermelho_escuro']}}}.t10e .nm.f{{fill:{C['azul_escuro']}}}"
    f".t10e .vl{{font-size:15px;font-family:var(--fonte);fill:{C['grafite']}}}"
    ".t10e .vl b{font-weight:700}"
    f".t10e .seta{{stroke:{C['azul']};stroke-width:3;fill:none;stroke-linecap:round;stroke-linejoin:round}}"
    ".t10e .mao{position:absolute;font-size:30px;white-space:nowrap;transform:rotate(-3deg)}"
    ".t10e .ok{position:absolute;font-size:26px;white-space:nowrap;transform:rotate(-3deg);font-family:var(--mao);"
    "font-weight:600;line-height:1.05}"
    ".t10e .txt{position:absolute;left:0;width:540px}"
    ".t10e .expl{position:absolute;left:0;width:540px;font-size:15px;line-height:1.42;color:var(--grafite)}"
)


CSS_ALVOS = (
    ".t10a{pointer-events:none}"
    ".t10a .alvo{position:absolute;left:0;width:560px;height:64px;pointer-events:auto;cursor:help;border-radius:6px;"
    "transition:background .15s}"
    ".t10a .alvo:hover{background:rgba(203,189,162,.2)}"
)


def corpo_erro() -> str:
    return f"<style>{CSS_ERRO}</style>{cp.defs_rabisco('rbu10')}{{{{content}}}}"


CSS_REGUA = (
    ".t10g .cab{position:absolute;left:0;top:0;right:0}"
    ".t10g .cab .txt{margin-top:6px}"
    ".t10g svg{position:absolute;left:0;top:0}"
    f".t10g .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    f".t10g .emp{{stroke:{C['grafite']};stroke-width:1.4;stroke-dasharray:4 6}}"
    f".t10g .tk{{stroke:{C['areia']};stroke-width:1}}"
    f".t10g .urna{{stroke:{C['tinta']};stroke-width:3.2;fill:none;stroke-linecap:round}}"
    ".t10g .uro{position:absolute;height:46px;display:flex;align-items:center;justify-content:center;"
    "font-size:18px;font-weight:700;white-space:nowrap;transform:translateX(-50%)}"
    ".t10g .uro .num{font-size:22px;margin-left:6px}"
    ".t10g .lado{position:absolute;font-size:15px;font-weight:600;white-space:nowrap}"
    ".t10g .leg{position:absolute;left:0;font-size:13px;color:var(--cinza);display:flex;gap:16px;align-items:center}"
    ".t10g .leg span{display:flex;align-items:center;gap:6px}"
    f".t10g .leg .c{{width:12px;height:12px;border-radius:50%;background:{C['grafite']}}}"
    f".t10g .leg .q{{width:11px;height:11px;background:{C['grafite']}}}"
    f".t10g .mao{{position:absolute;font-size:28px;white-space:nowrap;transform:rotate(-4deg);color:{C['tinta']}}}"
)


def corpo_regua() -> str:
    chave = cp.img("arte/limpos/rabiscos/chave-tinta.png", 44)
    return (f"<style>{CSS_REGUA}.t10g .chave{{position:absolute;background:url({chave}) center/100% 100% no-repeat}}"
            f"</style>{cp.defs_rabisco('rbu10g', 2.0)}{{{{content}}}}")


CSS_INST = (
    ".t10i{pointer-events:none}"
    ".t10i .ln{position:absolute;left:0;right:0;height:38px;pointer-events:auto;cursor:help}"
    f".t10i .ln:hover{{background:{C['creme']};box-shadow:inset 3px 0 0 {C['tinta']}}}"
    ".t10i .nome{position:absolute;right:calc(100% - 220px);top:9px;font-size:16px;white-space:nowrap;"
    "color:var(--tinta)}"
    ".t10i .haste{position:absolute;top:17px;height:4px;border-radius:2px}"
    f".t10i .haste.l{{background:{C['rosa']}}}.t10i .haste.f{{background:{C['azul_claro']}}}"
    ".t10i .mk{position:absolute;transform-origin:center;animation:eEscala .55s cubic-bezier(.2,.9,.3,1.3) both}"
    ".t10i .mk.v{width:17px;height:17px;top:10.5px;border-radius:50%}"
    ".t10i .mk.t{width:15px;height:15px;top:11.5px}"
    f".t10i .mk.l{{background:{C['vermelho']}}}.t10i .mk.f{{background:{C['azul']}}}"
    ".t10i .vl{position:absolute;top:6px;font-size:20px;font-weight:700;white-space:nowrap}"
    ".t10i .vl.l{color:var(--vermelho-escuro)}.t10i .vl.f{color:var(--azul-escuro)}"
)

CSS_TT_ERRO = (
    ".tt10e .lista{position:relative;margin-top:6px;padding-top:24px}"
    ".tt10e .li{display:grid;grid-template-columns:150px 220px 50px;align-items:center;height:22px}"
    ".tt10e .in{font-size:13px;color:var(--grafite);text-align:right;padding-right:12px;white-space:nowrap;overflow:hidden;"
    "text-overflow:ellipsis}"
    ".tt10e .tr{position:relative;height:22px}"
    f".tt10e .tr::before{{content:'';position:absolute;left:0;right:0;top:11px;border-top:1px dashed {C['areia']}}}"
    ".tt10e .pt{position:absolute;top:5px;width:12px;height:12px;border-radius:50%}"
    f".tt10e .pt.lula{{background:{C['vermelho']}}}.tt10e .pt.flavio{{background:{C['azul']}}}"
    ".tt10e .vv{font-size:13px;font-weight:600;text-align:right;font-variant-numeric:tabular-nums;color:var(--grafite)}"
    ".tt10e .li.on .in,.tt10e .li.on .vv{font-weight:700;color:var(--tinta)}"
    f".tt10e .li.on .pt{{box-shadow:0 0 0 3px {C['papel']},0 0 0 5px {C['tinta']}}}"
    f".tt10e .urna{{position:absolute;top:2px;width:0;border-left:2px solid {C['tinta']}}}"
    ".tt10e .urna b{position:absolute;left:6px;top:-2px;font-size:13px;font-weight:700;white-space:nowrap}"
    ".tt10e .nota{margin-top:10px;padding-right:200px}"
)

CSS_TT = (
    ".tt10 .par{margin:2px 0 6px 0}"
    ".tt10 .par{gap:22px}"
    ".tt10 .par .mao{position:static;margin-left:auto;align-self:center;font-size:26px;white-space:nowrap}"
    ".tt10 .txt b{font-weight:700}"
    ".tt10 .tj{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--cinza);"
    "margin-top:10px}"
    ".tt10 svg{display:block;margin-top:4px}"
    f".tt10 .g{{stroke:{C['areia']};stroke-width:1}}"
    f".tt10 .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    f".tt10 .ll{{stroke:{C['vermelho']};stroke-width:2.6;fill:none;stroke-linejoin:round;stroke-linecap:round}}"
    f".tt10 .lf{{stroke:{C['azul']};stroke-width:2.6;fill:none;stroke-linejoin:round;stroke-linecap:round}}"
    f".tt10 .pl{{fill:{C['vermelho']}}}.tt10 .pf{{fill:{C['azul']}}}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T10_Resposta_Html", *RESPOSTA, "T10 · Resposta · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_RESPOSTA}</style>{{{{content}}}}",
                                  alt=lib.medida("T10 · Resposta · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T10_Erro_Html", *ERRO, "T10 · Erro · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_erro(), alt=lib.medida("T10 · Erro · ALT"), z=Z + 1, tab=110)),
        Visual(P, lib.visual_html("T10_Regua_Html", *REGUA, "T10 · Régua · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_regua(), alt=lib.medida("T10 · Régua · ALT"), z=Z + 2,
                                  tab=120)),
        Visual(P, lib.visual_html("T10_Erro_Alvos", *ERRO, "T10 · Erro alvos · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_ALVOS}</style>{{{{content}}}}",
                                  granularidade=("Candidato ano", "Partido"), tooltip_pagina="ttT10Erro",
                                  alt=lib.medida("T10 · Erro alvos · ALT"), z=Z + 4, tab=115)),
        Visual(P, lib.visual_html("T10_Regua_Institutos", *REGUA, "T10 · Institutos · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_INST}</style>{{{{content}}}}",
                                  granularidade=("Pesquisa", "Instituto"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT10Instituto",
                                  alt=lib.medida("T10 · Institutos · ALT"), z=Z + 3, tab=130)),
        # o clique num instituto mexe só no quadro do erro (e nos alvos dele): a resposta e o fundo da régua são o
        # retrato dos 18 e não leem o instituto
        Interacao(P, "T10_Regua_Institutos", "T10_Resposta_Html", "NoFilter"),
        Interacao(P, "T10_Regua_Institutos", "T10_Regua_Html", "NoFilter"),
        *pagina_lib.tooltip("ttT10Instituto", "Pesquisas · instituto", 480, 404, "T10 · Tooltip instituto · HTML",
                            ordem=210, folha_de_estilo=CSS, modelo_corpo=cp.dossie("barras", CSS_TT)),
        *pagina_lib.tooltip("ttT10Erro", "Pesquisas · erro um a um", 480, 440, "T10 · Tooltip erro · HTML",
                            ordem=211, folha_de_estilo=CSS, modelo_corpo=cp.dossie("lupa", CSS_TT_ERRO)),
    ]
