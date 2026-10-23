# -*- coding: utf-8 -*-
"""12 · Estados — como cada estado se moveu? (dono: agente das telas 11–15). Sem filtro.

Lula perdeu margem em 26 das 27 unidades; Minas Gerais e Tocantins mudaram de lado; só o Distrito Federal subiu.

  T12_Resposta_Html   coluna da resposta: "26 de 27" (contador), quem mudou de lado (sublinhado à mão), a exceção, o que
                      é margem (o Brasil 2022 e 2026 em barras) e as cinco regiões em mini setas
  T12_Corrida_Titulo  sobretítulo, a manchete das setas e a legenda
  T12_Corrida_Html    a corrida das unidades (granularidade UF, 27 + exterior): da maior queda à alta, o ponto vazado de
                      2022 e o cheio de 2026, que desliza até o lugar na entrada; eixo de −60 a +60 p.p. no bodyTemplate.
                      Tooltip: dossiê da UF (ttT12Uf)

Medidas em pbi/dax/T12 Estados (geradas por pbi/scripts/desenho_t12.py).
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual

P = "T12"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]

RESPOSTA = (150, 140, 560, 860)
TITULO = (760, 140, 1010, 96)
CORRIDA = (760, 236, 1010, 764)

CSS_RESPOSTA = (
    ".t12r .topo{position:absolute;left:-4px;top:-22px;display:flex;align-items:baseline;gap:16px}"
    ".t12r .topo .g{font-size:128px;letter-spacing:-.045em}"
    ".t12r .topo .de{font-size:46px;font-weight:600;color:var(--grafite)}"
    ".t12r .t1{position:absolute;left:0;top:126px;width:540px;font-size:24px}"
    ".t12r .t2{position:absolute;left:0;top:200px;width:540px;font-size:24px}"
    ".t12r .t2 .sub{color:var(--azul-escuro)}"
    ".t12r .t2 svg{display:block;margin-top:2px}"
    ".t12r .t3{position:absolute;left:0;top:266px;width:540px}"
    ".t12r .t3 b{color:var(--vermelho);white-space:nowrap}"
    ".t12r .margem{position:absolute;left:0;top:322px;width:540px}"
    ".t12r .margem .ex{margin:8px 0 12px 0;font-size:15px}"
    ".t12r .br .lnb{display:grid;grid-template-columns:44px 300px 1fr 74px;align-items:center;gap:10px;height:34px}"
    ".t12r .br .ano{font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--cinza)}"
    ".t12r .br .tr{position:relative;height:14px;background:var(--creme);display:flex;justify-content:space-between}"
    ".t12r .br .bl{display:block;height:14px;background:var(--vermelho)}"
    ".t12r .br .ba{display:block;height:14px;background:var(--azul)}"
    ".t12r .br .pc{font-size:15px;font-weight:600;white-space:nowrap}"
    ".t12r .br .mg{font-size:24px;text-align:right}"
    ".t12r .regioes{position:absolute;left:0;top:560px;width:560px}"
    ".t12r .rg{position:absolute;left:0;width:560px;height:44px}"
    ".t12r .rg .nm{position:absolute;left:0;top:-2px;font-size:16px;font-weight:600;white-space:nowrap}"
    ".t12r .rg .mud{font-size:24px;font-weight:600;color:var(--azul-escuro);margin-left:8px}"
    ".t12r .rg .vv{position:absolute;left:0;top:22px;font-size:13px;color:var(--cinza)}"
    ".t12r .rg .mini{position:absolute;left:170px;top:6px}"
    ".t12r .rg .dv{position:absolute;right:0;top:3px;font-size:17px;font-weight:700;color:var(--grafite)}"
    ".t12r .rg .zero{stroke:var(--grafite);stroke-width:1;stroke-dasharray:2 3}"
    ".t12r .rg line.traco-rapido{stroke:var(--grafite);stroke-width:2}"
    ".t12r .rg .m22{fill:var(--papel);stroke-width:2}"
)

CSS_TITULO = (
    ".t12t .rot{position:absolute;left:0;top:0}"
    ".t12t .man{position:absolute;left:0;top:24px;right:0;font-size:24px}"
    ".t12t .leg{position:absolute;left:0;right:0;top:68px;display:flex;gap:26px;font-size:15px;color:var(--grafite)}"
    ".t12t .leg .dir{margin-left:auto;font-size:13px;font-weight:600;letter-spacing:.04em;color:var(--cinza)}"
    ".t12t .leg i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px;vertical-align:-1px}"
    ".t12t .leg .o{border:2px solid var(--grafite);background:var(--papel)}"
    ".t12t .leg .f.vm{background:var(--vermelho);margin-right:3px}.t12t .leg .f.az{background:var(--azul)}"
    ".t12t .leg .mud{width:26px;height:12px;border-radius:2px;background:rgba(143,168,207,.45)}"
)


def _eixo() -> str:
    """Grade e rótulos fixos do eixo da corrida (−60 a +60 p.p. em 680 px a partir de x 210)."""
    partes = []
    for v in range(-60, 61, 20):
        x = 210 + 680 * (v + 60) / 120
        cls = "g zero" if v == 0 else "g"
        partes.append(f"<line class='{cls}' x1='{x:.1f}' x2='{x:.1f}' y1='0' y2='716'/>")
        txt = "0" if v == 0 else (f"+{v}" if v > 0 else f"−{-v}")
        partes.append(f"<text x='{x:.1f}' y='738' text-anchor='middle' class='tk'>{txt}</text>")
    partes.append("<text x='540' y='758' text-anchor='end' class='lado'>← Flávio à frente</text>")
    partes.append("<text x='560' y='758' class='lado'>Lula à frente →</text>")
    return ("<svg class='eixo entra' width='1010' height='764' viewBox='0 0 1010 764'>" + "".join(partes)
            + "</svg>")


CSS_CORRIDA = (
    ".t12c{position:fixed;inset:0;pointer-events:none}"
    ".t12c .eixo{position:absolute;left:0;top:0}"
    ".t12c .g{stroke:var(--areia);stroke-width:1}.t12c .g.zero{stroke:var(--grafite);stroke-width:1.2}"
    ".t12c .tk{font-family:var(--fonte);font-size:13px;fill:var(--cinza)}"
    ".t12c .lado{font-family:var(--fonte);font-size:13px;font-weight:600;fill:var(--grafite)}"
    ".lin{pointer-events:none}"
    ".lin .alvo{position:absolute;left:0;width:1010px;height:24px;pointer-events:auto;border-radius:2px;"
    "transition:background .15s}"
    ".lin .alvo:hover{background:rgba(28,25,21,.07)}"
    ".lin.mud .alvo{background:rgba(143,168,207,.24)}.lin.mud .alvo:hover{background:rgba(143,168,207,.4)}"
    ".lin .nm{position:absolute;left:4px;font-size:15px;line-height:22px;white-space:nowrap}"
    ".lin.mud .nm{font-weight:700;color:var(--azul-escuro)}"
    ".lin .mm{font-family:var(--mao);font-size:24px;font-weight:600;color:var(--azul-escuro);margin-left:10px;"
    "line-height:18px}"
    ".lin .mm.vm{color:var(--vermelho-escuro)}"
    ".lin.ext .nm{font-style:italic;color:var(--cinza)}"
    ".lin .sv{position:absolute;left:0;top:0}"
    ".lin line.traco{stroke:var(--grafite);stroke-width:2;animation-duration:1.1s}"
    ".lin .m22{fill:var(--papel);stroke-width:2;animation:uEntra .5s ease-out both}"
    "@keyframes t12vai{from{transform:translateX(var(--dx))}}"
    ".lin .vai{animation:t12vai 1.1s cubic-bezier(.45,.05,.3,1) both}"
    ".lin .dv{position:absolute;right:4px;width:90px;text-align:right;font-size:15px;font-weight:600;line-height:22px;"
    "color:var(--grafite)}"
    ".lin.sobe-m .dv{color:var(--vermelho);font-weight:700}"
)

CSS_TOOLTIP = (
    ".tt12{background:var(--branco);border:1.5px solid var(--areia);padding:22px 24px 16px 24px}"
    ".tt12 .fita{position:absolute;left:168px;top:-9px;width:112px;height:24px;background:var(--areia);opacity:.7;"
    "transform:rotate(-3deg)}"
    ".tt12 .nm{font-size:22px;font-weight:700;line-height:1.15;padding-right:140px}"
    ".tt12 .uf{font-size:14px;font-weight:600;letter-spacing:.06em;color:var(--cinza)}"
    ".tt12 .nota{margin-top:4px}"
    ".tt12 .selo{position:absolute;right:18px;top:22px;transform:rotate(6deg);border:2.5px solid currentColor;"
    "outline:1px solid currentColor;outline-offset:2px;padding:5px 9px;font-weight:700;font-size:12px;"
    "letter-spacing:.12em;color:var(--grafite);white-space:nowrap}"
    ".tt12 .selo.az{color:var(--azul)}.tt12 .selo.vm{color:var(--vermelho)}.tt12 .selo.leve{opacity:.8;font-size:10px}"
    ".tt12 .duelo{margin-top:14px}"
    ".tt12 .ln{display:grid;grid-template-columns:38px 200px 1fr;align-items:center;gap:10px;height:26px}"
    ".tt12 .ln .a{font-size:12px;font-weight:700;letter-spacing:.06em;color:var(--cinza)}"
    ".tt12 .ln .tr{position:relative;height:12px;background:var(--creme);display:flex;justify-content:space-between}"
    ".tt12 .ln .bl{display:block;height:12px;background:var(--vermelho)}"
    ".tt12 .ln .ba{display:block;height:12px;background:var(--azul)}"
    ".tt12 .ln .p{font-size:14px;white-space:nowrap}"
    ".tt12 .duelo .nota{font-size:12px;margin-top:2px}"
    ".tt12 .mun{margin-top:12px;font-size:15px;color:var(--grafite)}.tt12 .mun .num{font-size:22px;color:var(--azul)}"
    ".tt12 .mao{position:absolute;right:22px;bottom:12px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
)


def _corpo_tt(css: str) -> str:
    """bodyTemplate do tooltip: o cartão (conteúdo) e, por cima, o ícone em traço no canto de baixo."""
    img = estilo.imagem_b64("docs/midia/arte/icones/balanca-tinta.png", 96)
    return (f"<style>{css}.ttic{{position:fixed;left:22px;bottom:12px;width:42px;height:42px;opacity:.8;"
            f"background:url({img}) center/contain no-repeat;pointer-events:none}}</style>{{{{content}}}}"
            "<div class='ttic entra d5'></div>")


def _corpo(css: str) -> str:
    return f"<style>{css}</style>{{{{content}}}}"


def declarar(ctx):
    corpo_corrida = f"<style>{CSS_CORRIDA}</style><div class='t12c'>{_eixo()}</div>{{{{content}}}}"
    return [
        Visual(P, lib.visual_html("T12_Resposta_Html", *RESPOSTA, "T12 · Resposta · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_RESPOSTA), alt=lib.medida("T12 · Resposta · ALT"),
                                  z=Z, tab=100)),
        Visual(P, lib.visual_html("T12_Corrida_Titulo", *TITULO, "T12 · Corrida título · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_TITULO), alt=lib.medida("T12 · Corrida título · ALT"),
                                  z=Z + 1, tab=110)),
        Visual(P, lib.visual_html("T12_Corrida_Html", *CORRIDA, "T12 · Corrida · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_corrida, granularidade=("UF", "UF"), tooltip_pagina="ttT12Uf",
                                  alt=lib.medida("T12 · Corrida · ALT"), z=Z + 2, tab=120)),
        *pagina_lib.tooltip("ttT12Uf", "Estados · UF", 440, 300, "T12 · Tooltip UF · HTML", ordem=220,
                            folha_de_estilo=CSS, modelo_corpo=_corpo_tt(CSS_TOOLTIP)),
    ]
