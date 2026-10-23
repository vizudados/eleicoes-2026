# -*- coding: utf-8 -*-
"""11 · Virada — onde os votos mudaram de lado? (dono: agente das telas 11–15)

A história é o mapa: 711 municípios trocaram Lula por Flávio de 2022 para 2026 e nenhum fez o caminho inverso.

  T11_Resposta_Html   coluna da resposta: o 711 (contador), "nenhum fez o caminho inverso" sublinhado à mão, a fila das
                      5.571 cidades 2022 → 2026 (barras e faixas: a faixa azul forte são as que trocaram) e os votos
                      que mudaram de mão
  T11_Mapa_Titulo     sobretítulo, manchete do mapa (regiões no Brasil; a UF no filtro) e a legenda
  T11_Mapa_Pontos     Deneb (Vega 6, canvas): um ponto por município no quadro 1000 × 1000; o contorno das UFs se
                      desenha em rabisco, os pontos esmaecem do norte ao sul e os que viraram acendem em ondas a partir
                      do centro da virada; com UF no filtro, enquadra a UF (vizinhas em traço claro). Tooltip: dossiê
                      do município (ttT11Municipio)
  T11_Maiores_Html    as maiores que viraram (até 6, pela população) com a margem 2022 → 2026 num mini gráfico e a
                      explicação de "margem"

Medidas em pbi/dax/T11 Virada (geradas por pbi/scripts/desenho_t11.py); spec em pbi/spec/t11_mapa.json.
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual

P = "T11"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]

RESPOSTA = (150, 140, 420, 860)
TITULO = (610, 140, 820, 100)
MAPA = (610, 240, 820, 760)
MAIORES = (1460, 140, 310, 860)

CSS_RESPOSTA = (
    ".t11r .grande{position:absolute;left:-6px;top:-22px;font-size:150px;letter-spacing:-.045em;color:var(--tinta)}"
    ".t11r .grande.palavra{font-size:92px;top:4px}"
    ".t11r .frase{position:absolute;left:0;top:146px;width:420px;font-size:25px;line-height:1.22}"
    ".t11r .inv{position:absolute;left:0;top:226px;font-size:20px;font-weight:500;color:var(--grafite)}"
    ".t11r .inv svg{position:absolute;left:-3px;top:25px}"
    ".t11r .fluxo{position:absolute;left:0;top:304px;width:420px}"
    ".t11r .fluxo>.rot{margin-bottom:12px}"
    ".t11r .lb{display:flex;justify-content:space-between;align-items:baseline;font-size:15px;color:var(--grafite)}"
    ".t11r .lb .num{font-size:28px}"
    ".t11r .lb .ano{font-size:13px;font-weight:700;letter-spacing:.08em;color:var(--cinza);margin-right:10px}"
    ".t11r .lb.cima{margin-bottom:8px}.t11r .lb.baixo{margin-top:6px}"
    ".t11r .palco{position:relative;width:420px;height:300px}"
    ".t11r svg.fila{display:block}"
    ".t11r .fila .barra-x{transform-box:fill-box}"
    ".t11r .fila .forte{animation:uEntra 1s ease-out 1.6s both}"
    ".t11r .anota{position:absolute;left:0;top:132px;text-align:right;font-size:27px;color:var(--azul-escuro);"
    "white-space:nowrap;text-shadow:0 0 6px var(--papel),0 0 3px var(--papel)}"
    ".t11r .fluxo .nota{margin-top:12px;font-size:13px}"
)

CSS_TITULO = (
    ".t11t .rot{position:absolute;left:0;top:0}"
    ".t11t .man{position:absolute;left:0;top:24px;right:0;font-size:24px}"
    ".t11t .leg{position:absolute;left:0;top:70px;display:flex;gap:24px;font-size:15px;color:var(--grafite)}"
    ".t11t .leg i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:8px;vertical-align:-1px}"
    ".t11t .c-l{background:var(--rosa)}.t11t .c-f{background:var(--azul-claro)}"
    ".t11t .c-v{background:var(--azul)}.t11t .c-vl{background:var(--vermelho)}"
)

CSS_MAIORES = (
    ".t11m .rot{position:absolute;left:0;top:0}"
    ".t11m .sub{position:absolute;left:0;top:22px;width:300px;font-size:15px;line-height:1.35}"
    ".t11m .it{position:absolute;left:0;width:310px;height:96px}"
    ".t11m .pos{position:absolute;left:0;top:-6px;font-size:30px;color:var(--cinza)}"
    ".t11m .nm{position:absolute;left:28px;top:0;width:280px;font-size:18px;font-weight:600;white-space:nowrap;"
    "overflow:hidden;text-overflow:ellipsis}"
    ".t11m .uf{font-size:13px;font-weight:600;letter-spacing:.06em;color:var(--cinza)}"
    ".t11m .it .nota{position:absolute;left:28px;top:25px}"
    ".t11m .db{position:absolute;left:4px;top:46px}"
    ".t11m .db .zero{stroke:var(--grafite);stroke-width:1;stroke-dasharray:2 3}"
    ".t11m .db line.traco-rapido{stroke:var(--grafite);stroke-width:2}"
    ".t11m .db .m22{fill:var(--papel);stroke:var(--vermelho);stroke-width:2}"
    ".t11m .mg{position:absolute;left:28px;top:70px;font-size:15px;font-weight:600;color:var(--grafite)}"
    ".t11m .vz{position:absolute;left:0;top:96px;width:290px}"
    ".t11m .pe{position:absolute;left:0;bottom:0;width:305px}"
)

CSS_TOOLTIP = (
    ".tt11{background:var(--branco);border:1.5px solid var(--areia);padding:22px 24px 16px 24px}"
    ".tt11 .fita{position:absolute;left:168px;top:-9px;width:112px;height:24px;background:var(--areia);opacity:.7;"
    "transform:rotate(-3deg)}"
    ".tt11 .nm{font-size:22px;font-weight:700;line-height:1.15;padding-right:136px}"
    ".tt11 .uf{font-size:14px;font-weight:600;letter-spacing:.06em;color:var(--cinza)}"
    ".tt11 .nota{margin-top:4px}"
    ".tt11 .selo{position:absolute;right:18px;top:22px;transform:rotate(6deg);border:2.5px solid currentColor;"
    "outline:1px solid currentColor;outline-offset:2px;padding:5px 9px;font-weight:700;font-size:13px;"
    "letter-spacing:.14em;color:var(--grafite);white-space:nowrap}"
    ".tt11 .selo.az{color:var(--azul)}.tt11 .selo.vm{color:var(--vermelho)}"
    ".tt11 .selo.leve{font-size:10px;letter-spacing:.1em;opacity:.8}"
    ".tt11 .r1{margin-top:14px}"
    ".tt11 .regua{display:block;margin-top:2px}"
    ".tt11 .regua .zero{stroke:var(--grafite);stroke-width:1;stroke-dasharray:2 3}"
    ".tt11 .regua line.traco-rapido{stroke:var(--grafite);stroke-width:2.2}"
    ".tt11 .regua .m22{fill:var(--branco);stroke:var(--vermelho);stroke-width:2}"
    ".tt11 .regua text{font-family:var(--fonte);font-size:13px;font-weight:600;fill:var(--grafite)}"
    ".tt11 .regua .lado{font-size:11px;font-weight:500;fill:var(--cinza)}"
    ".tt11 .duas{margin-top:4px;font-size:15px;line-height:1.65}"
    ".tt11 .duas .rot{font-size:11px}"
    ".tt11 .mao{position:absolute;right:22px;bottom:12px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
)


def _corpo_tt(css: str) -> str:
    """bodyTemplate do tooltip: o cartão (conteúdo) e, por cima, o ícone em traço no canto de baixo."""
    img = estilo.imagem_b64("docs/midia/arte/icones/pino-tinta.png", 96)
    return (f"<style>{css}.ttic{{position:fixed;left:22px;bottom:12px;width:42px;height:42px;opacity:.8;"
            f"background:url({img}) center/contain no-repeat;pointer-events:none}}</style>{{{{content}}}}"
            "<div class='ttic entra d5'></div>")


def _corpo(css: str) -> str:
    return f"<style>{css}</style>{{{{content}}}}"


def declarar(ctx):
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"), lib.campo_coluna("x", "Município", "X"),
              lib.campo_coluna("y", "Município", "Y"), lib.campo_coluna("uf", "Município", "UF"),
              lib.campo_medida("sit", "T11 · situação")]
    return [
        Visual(P, lib.visual_html("T11_Resposta_Html", *RESPOSTA, "T11 · Resposta · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_RESPOSTA), alt=lib.medida("T11 · Resposta · ALT"),
                                  z=Z, tab=100)),
        Visual(P, lib.visual_html("T11_Mapa_Titulo", *TITULO, "T11 · Mapa título · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_TITULO), alt=lib.medida("T11 · Mapa título · ALT"),
                                  z=Z + 1, tab=110)),
        Visual(P, lib.visual_deneb("T11_Mapa_Pontos", *MAPA, "spec/t11_mapa.json", campos,
                                   alt=lib.medida("T11 · Mapa · ALT"), z=Z + 2, tab=120,
                                   tooltip_pagina="ttT11Municipio", renderizacao="canvas")),
        Visual(P, lib.visual_html("T11_Maiores_Html", *MAIORES, "T11 · Maiores · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_MAIORES), alt=lib.medida("T11 · Maiores · ALT"),
                                  z=Z + 3, tab=130)),
        *pagina_lib.tooltip("ttT11Municipio", "Virada · município", 440, 300, "T11 · Tooltip município · HTML",
                            ordem=210, folha_de_estilo=CSS, modelo_corpo=_corpo_tt(CSS_TOOLTIP)),
    ]
