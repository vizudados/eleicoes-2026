# -*- coding: utf-8 -*-
"""15 · Minha cidade — como votou a minha cidade? (dono: agente das telas 11–15). Filtro de município, declarado aqui.

Padrão: Contagem (MG) — Flávio venceu com 50,3%; a margem de Lula caiu 5,4 p.p. desde 2022.

  T15_Filtro_Municipio  VizuFilter sobre Município[Rótulo] (os 5.571, "Nome (UF)"), lista suspensa com busca, seleção
                        única, sem "todos". Cidade inicial Contagem (MG) por dois caminhos: o filtro já gravado no PBIR
                        (general.filter, L109) e a seleção padrão do visual (defaultSelection = value, defaultValue =
                        "Contagem (MG)"), que vale na primeira carga sem seleção persistida
  T15_Ficha_Html        quem venceu na cidade e com quanto (contador), a manchete da mudança desde 2022, os dados da
                        cidade e os votos de Lula e do PL em 2022 e 2026; sem cidade, o convite para escolher
  T15_Serie_Titulo      manchete da série (de quanto a quanto, e quando a cidade virou) e a legenda
  T15_Serie_Html        a margem do PT na cidade em cada eleição (granularidade Ano): barras que crescem para cima (PT à
                        frente) ou para baixo (adversário), com a nota à mão "caiu N desde 2022" e "virou aqui".
                        Tooltip: a eleição na cidade (ttT15Ano)
  T15_Parecidas_Html    entre as cidades parecidas (mesmo porte e quinto de renda, no Brasil): a posição na queda, o
                        grupo e o histograma das variações com a cidade marcada

Medidas em pbi/dax/T15 Minha cidade (geradas por pbi/scripts/desenho_t15.py).
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual

P = "T15"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]
C = estilo.COR

FILTRO = (1282, 60, 424, 48)          # a mesma caixa do filtro da casca nas telas com UF
FICHA = (150, 140, 560, 860)
SERIE_TITULO = (760, 140, 1010, 96)
SERIE = (760, 236, 1010, 384)
PARECIDAS = (760, 650, 1010, 350)
CIDADE_INICIAL = "Contagem (MG)"


def _filtro_municipio() -> Visual:
    x, y, w, h = FILTRO
    layout = {"controlWidth": w, "controlHeight": h, "dropdownWidth": w, "dropdownHeight": 560, "gap": 6,
              "optionHeight": 40, "searchHeight": 44, "triggerIconGap": 12, "borderRadius": 6, "checkboxSize": 14,
              "checkboxRadius": 2, "scrollbarWidth": 4, "wrapOptionLabels": False}
    geral = {"mode": "dropdown", "singleSelect": True, "singleSelectAllowAll": False, "sortAscending": True,
             "startOpen": False, "alwaysOpen": False, "showSearch": True, "showSelectAll": False, "showReset": False,
             "showSelectedCount": False, "showSelectedValue": True, "selectedValueOnly": False,
             "syncSelectionWithHost": True, "triggerMode": "value", "triggerLabel": "Município",
             "placeholderText": "Escolha uma cidade", "searchPlaceholder": "Digite o nome da cidade",
             "searchScope": "list", "pathMode": False, "defaultSelection": "value", "defaultValue": CIDADE_INICIAL}
    # mesmos tokens do filtro de UF da casca (paginas/casca.py › _estilo_filtro), para os dois parecerem um só
    estilo_f = {"fontSize": 16, "optionFontSize": 16, "fontFamily": "Sora Vizu, Segoe UI",
                "enableHoverAnimations": False, "showShadow": True, "counterBadgeRadius": 0, "triggerIcon": "funnel",
                "triggerIconSize": 16, "triggerIconActive": "filledDot", "triggerIconDotColor": C["vermelho"],
                "textColor": C["tinta"], "backgroundColor": C["creme"], "dropdownBackgroundColor": C["branco"],
                "selectedBackgroundColor": C["creme"], "hoverBackgroundColor": C["papel"], "hoverTextColor": C["tinta"],
                "borderColor": C["areia"], "activeBorderColor": C["tinta"], "checkboxColor": C["tinta"],
                "checkboxMarkColor": C["tinta"], "checkboxBorderColor": C["areia"], "counterBackgroundColor": C["tinta"],
                "counterTextColor": C["papel"], "clearActionColor": C["tinta"], "mutedTextColor": C["cinza"],
                "dividerColor": C["creme"], "scrollbarThumbColor": C["areia"],
                "categorySearchBackgroundColor": C["branco"], "triggerIconColor": C["grafite"]}
    doc = lib.visual_vizufilter("T15_Filtro_Municipio", x, y, w, h, categoria=("Município", "Rótulo", "Município"),
                                geral=geral, layout=layout, estilo=estilo_f, alt="Filtro de município: escolha a cidade",
                                z=lib.CAMADAS["drawer"], tab=5)
    # a cidade inicial já gravada no filtro do visual (só general.filter vale, L109)
    doc["visual"]["objects"]["general"][0]["properties"]["filter"] = {
        "filter": lib.filtro_in("Município", "Rótulo", [CIDADE_INICIAL])}
    return Visual(P, doc)


CSS_FICHA = (
    ".t15f .topo{position:absolute;left:-4px;top:-8px;display:flex;align-items:center;gap:22px}"
    ".t15f .topo .g{font-size:96px;letter-spacing:-.04em}"
    ".t15f .quem{display:flex;flex-direction:column;gap:4px;font-size:22px;font-weight:600;line-height:1.2}"
    ".t15f .m{position:absolute;left:0;top:124px;width:550px;font-size:24px}"
    ".t15f .fatos{position:absolute;left:0;top:220px;width:540px;font-size:15px;line-height:1.45}"
    ".t15f .votos{position:absolute;left:0;top:330px;width:550px}"
    ".t15f .lv{position:relative;display:flex;align-items:center;height:76px;border-bottom:1px solid var(--creme)}"
    ".t15f .lv .q{display:block;width:14px;height:14px;border-radius:2px;margin-right:14px}"
    ".t15f .lula-q{background:var(--vermelho)}.t15f .flavio-q{background:var(--azul)}"
    ".t15f .lv .nm{flex:1}.t15f .lv .nm b{display:block;font-size:17px;font-weight:600}"
    ".t15f .lv .nm span{display:block;font-size:15px;color:var(--grafite);margin-top:2px}"
    ".t15f .lv .dv{font-size:34px}"
    ".t15f .votos .nota{margin-top:10px}"
    ".t15f .comp{position:absolute;left:0;top:610px;width:550px}"
    ".t15f .cp{position:relative;display:flex;align-items:center;height:56px}"
    ".t15f .cp .nm{width:200px}.t15f .cp .nm b{display:block;font-size:16px;font-weight:600;white-space:nowrap;"
    "overflow:hidden;text-overflow:ellipsis}"
    ".t15f .cp .nm span{display:block;font-size:13px;color:var(--cinza)}"
    ".t15f .cp svg{flex:none}"
    ".t15f .cp .zero{stroke:var(--grafite);stroke-width:1;stroke-dasharray:2 3}"
    ".t15f .cp line.traco-rapido{stroke:var(--grafite);stroke-width:2}"
    ".t15f .cp .m22{fill:var(--papel);stroke:var(--grafite);stroke-width:2}"
    ".t15f .cp .vv{margin-left:10px;font-size:14px;font-weight:600;color:var(--grafite);white-space:nowrap}"
    ".t15f .comp .nota{margin-top:6px}"
    ".t15v .ic{position:absolute;left:0;top:0;width:120px;height:120px;background-size:contain;"
    "background-repeat:no-repeat}"
    ".t15v .rot{position:absolute;left:0;top:140px}"
    ".t15v .man{position:absolute;left:0;top:168px;width:520px;font-size:28px}"
    ".t15v .txt{position:absolute;left:0;top:290px;width:500px}"
)

CSS_SERIE_TITULO = (
    ".t15t .rot{position:absolute;left:0;top:0}"
    ".t15t .man{position:absolute;left:0;top:22px;right:0;font-size:24px}"
    ".t15t .leg{position:absolute;right:0;top:0;display:flex;gap:22px;font-size:15px;color:var(--grafite)}"
    ".t15t .leg i{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:7px;vertical-align:-1px}"
    ".t15t .leg .pt{background:var(--vermelho)}.t15t .leg .adv{background:var(--azul)}"
)

CSS_SERIE = (
    ".br{pointer-events:none}"
    ".br .alvo{position:absolute;top:0;width:160px;height:370px;pointer-events:auto;border-radius:4px;"
    "transition:background .15s}"
    ".br .alvo:hover{background:rgba(28,25,21,.05)}"
    ".br .bar{position:absolute;width:100px;border-radius:2px}"
    ".br .bar.pt{background:var(--vermelho)}.br .bar.adv{background:var(--azul)}"
    ".br .bar.desce{transform-origin:center top;animation:uCresceY 1s cubic-bezier(.2,.7,.2,1) .3s both}"
    ".br .vl{position:absolute;width:140px;text-align:center;font-size:22px;font-weight:700}"
    ".br .vl.pt{color:var(--vermelho-escuro)}.br .vl.adv{color:var(--azul-escuro)}"
    ".br .xl{position:absolute;top:318px;width:168px;text-align:center}"
    ".br .xl b{display:block;font-size:20px;font-weight:700}"
    ".br .xl span{display:block;font-size:13px;color:var(--cinza);margin-top:2px}"
    ".br .zero{position:absolute;left:0;top:160px;width:1010px;border-top:1.5px solid var(--grafite)}"
    ".br .nt{position:absolute;width:300px;text-align:right;font-size:26px;color:var(--vermelho-escuro);"
    "transform:rotate(-3deg)}"
    ".br .vr{position:absolute;font-size:24px;color:var(--grafite)}"
)

CSS_PARECIDAS = (
    ".t15p .rot{position:absolute;left:0;top:0}"
    ".t15p .pos{position:absolute;left:0;top:26px;width:560px;font-size:34px;font-weight:700;letter-spacing:-.02em;"
    "white-space:nowrap}"
    ".t15p .comp{position:absolute;left:0;top:74px;width:620px;font-size:16px}"
    ".t15p .hist{position:absolute;left:0;top:30px}"
    ".t15p .eixo{stroke:var(--grafite);stroke-width:1.2}"
    ".t15p .hb{fill:var(--azul-claro);transform-box:fill-box}.t15p .hb.cid{fill:var(--azul)}"
    ".t15p .grupo{stroke:var(--grafite);stroke-width:1.6;stroke-dasharray:4 4}"
    ".t15p .cidade{stroke:var(--vermelho);stroke-width:2.4}"
    ".t15p .tk{font-family:var(--fonte);font-size:13px;fill:var(--cinza)}"
    ".t15p .rc{position:absolute;width:240px;text-align:center;font-size:15px;font-weight:700;white-space:nowrap}"
    ".t15p .rc.cid{top:156px;color:var(--vermelho-escuro)}"
    ".t15p .rc.grp{top:178px;color:var(--grafite);font-weight:600}"
    ".t15p .rc span{background:var(--papel)}"
)

CSS_TOOLTIP = (
    ".tt15{background:var(--branco);border:1.5px solid var(--areia);padding:20px 24px 16px 24px}"
    ".tt15 .fita{position:absolute;left:168px;top:-9px;width:112px;height:24px;background:var(--areia);opacity:.7;"
    "transform:rotate(-3deg)}"
    ".tt15 .an{font-size:22px;font-weight:700;padding-right:150px;line-height:1.15}"
    ".tt15 .rot{margin-top:12px;margin-bottom:6px}"
    ".tt15 .cl{display:grid;grid-template-columns:150px 200px 1fr;align-items:center;height:30px;gap:8px}"
    ".tt15 .cl .nm{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".tt15 .cl .nm i{font-style:normal;font-size:11px;font-weight:600;color:var(--cinza)}"
    ".tt15 .cl .tr{display:block;height:12px;background:var(--creme)}"
    ".tt15 .cl b{display:block;height:12px;background:var(--areia)}"
    ".tt15 .cl b.pt{background:var(--vermelho)}.tt15 .cl b.adv{background:var(--azul)}"
    ".tt15 .cl .pc{font-size:14px;font-weight:700;text-align:right}"
    ".tt15 .nota{margin-top:10px}"
    ".tt15 .selo{position:absolute;right:18px;top:20px;transform:rotate(6deg);border:2.5px solid currentColor;"
    "outline:1px solid currentColor;outline-offset:2px;padding:5px 8px;font-weight:700;font-size:10px;"
    "letter-spacing:.1em;white-space:nowrap}"
    ".tt15 .selo.az{color:var(--azul)}.tt15 .selo.vm{color:var(--vermelho)}"
    ".tt15 .mao{position:absolute;right:22px;bottom:12px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
)


def _css_lupa() -> str:
    return f".t15v .ic{{background-image:url({estilo.imagem_b64('docs/midia/arte/icones/lupa-tinta.png', 160)})}}"


def _corpo_tt(css: str) -> str:
    """bodyTemplate do tooltip: o cartão (conteúdo) e, por cima, o ícone em traço no canto de baixo."""
    img = estilo.imagem_b64("docs/midia/arte/icones/caixa-de-votos-tinta.png", 96)
    return (f"<style>{css}.ttic{{position:fixed;left:22px;bottom:12px;width:42px;height:42px;opacity:.8;"
            f"background:url({img}) center/contain no-repeat;pointer-events:none}}</style>{{{{content}}}}"
            "<div class='ttic entra d5'></div>")


def _corpo(css: str) -> str:
    return f"<style>{css}</style>{{{{content}}}}"


def declarar(ctx):
    return [
        _filtro_municipio(),
        Visual(P, lib.visual_html("T15_Ficha_Html", *FICHA, "T15 · Ficha · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_FICHA + _css_lupa()), alt=lib.medida("T15 · Ficha · ALT"),
                                  z=Z, tab=100)),
        Visual(P, lib.visual_html("T15_Serie_Titulo", *SERIE_TITULO, "T15 · Série título · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_SERIE_TITULO), alt=lib.medida("T15 · Série título · ALT"),
                                  z=Z + 1, tab=110)),
        Visual(P, lib.visual_html("T15_Serie_Html", *SERIE, "T15 · Série · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_SERIE), granularidade=("Ano", "Ano"),
                                  tooltip_pagina="ttT15Ano", alt=lib.medida("T15 · Série · ALT"), z=Z + 2, tab=120)),
        Visual(P, lib.visual_html("T15_Parecidas_Html", *PARECIDAS, "T15 · Parecidas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_PARECIDAS), alt=lib.medida("T15 · Parecidas · ALT"),
                                  z=Z + 3, tab=130)),
        *pagina_lib.tooltip("ttT15Ano", "Minha cidade · eleição", 440, 280, "T15 · Tooltip ano · HTML", ordem=250,
                            folha_de_estilo=CSS, modelo_corpo=_corpo_tt(CSS_TOOLTIP)),
    ]
