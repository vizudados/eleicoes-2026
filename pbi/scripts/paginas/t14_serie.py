# -*- coding: utf-8 -*-
"""14 · Série — como o PT chegou até aqui, de 2006 a 2026? (dono: agente das telas 11–15). Filtro de UF da casca.

Pela 2ª vez em seis eleições, o PT termina o 1º turno em segundo lugar (2018 e 2026).

  T14_Resposta_Html   o "2ª vez" (ou "N de 6" quando o PT ficou à frente em 2026), a manchete e os anos em que o PT
                      ficou atrás, com os candidatos e os percentuais; com um ano clicado, a margem do PT naquela
                      eleição e a urna dela em destaque; com uma região clicada, tudo no lugar dela
  T14_Linhas_Titulo   sobretítulo (Brasil, a UF ou a região clicada), manchete do melhor e do pior ano do PT e a legenda
  T14_Linhas_Html     a série PT × adversário principal (granularidade Ano): os trechos de linha se desenham em
                      sequência, os pontos brotam e um sublinhado à mão (embaixo do número) marca os anos em que o PT
                      ficou atrás; eixo com os candidatos. Tooltip: dossiê da eleição (ttT14Ano: os mais votados no
                      Brasil, a colocação do PT e a abstenção). Clique num ano: a resposta e os painéis das regiões
                      vão para aquela eleição (os outros anos esmaecem)
  T14_Regioes_Html    as cinco regiões na mesma escala, uma entrada por região (granularidade Município[Região]);
                      ignoram o filtro de UF e destacam a região da UF escolhida; mostram os valores da eleição em
                      destaque (a clicada na série ou 2026). Tooltip: os estados da região naquela eleição
                      (ttT14Regiao). Clique numa região: a série, o título e a resposta passam a contar a região

Medidas em pbi/dax/T14 Série (geradas por pbi/scripts/desenho_t14.py).
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
import roteiro
from pbip_lib import Visual

P = "T14"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]

RESPOSTA = (150, 140, 1620, 220)
TITULO = (150, 372, 1620, 64)
LINHAS = (150, 436, 1620, 370)
REGIOES = (150, 816, 1620, 184)
# páginas de tooltip: ordem 100 + número da tela para o leitor × 10 (o número sai do roteiro e anda com ele)
ORDEM_TT = 100 + int(roteiro.numero(P)) * 10

CSS_RESPOSTA = (
    ".t14r .g{position:absolute;left:-4px;top:-8px;font-size:104px;letter-spacing:-.04em}"
    ".t14r .m{position:absolute;left:0;top:112px;width:900px;font-size:26px}"
    ".t14r .s{position:absolute;left:0;top:184px;width:900px;font-size:15px;color:var(--grafite)}"
    ".t14r .ur{position:absolute;left:1086px;top:4px}"
    ".t14r .ux{position:absolute;top:56px;width:76px;height:76px;background-size:contain;background-repeat:no-repeat;"
    "background-position:center}"
    ".t14r .ua{position:absolute;top:138px;width:76px;text-align:center;font-size:15px;font-weight:700}"
    ".t14r .uv{position:absolute;top:20px;width:76px;text-align:center;font-size:24px;color:var(--azul-escuro)}"
    ".t14r .ul{position:absolute;left:1086px;top:170px}"
    ".t14r .g small{font-size:46px;letter-spacing:0}"
    ".t14r .apaga{opacity:.28;transition:opacity .3s}"
)


def _css_urnas() -> str:
    vm = estilo.imagem_b64("docs/midia/arte/icones/caixa-de-votos-vermelho.png", 110)
    az = estilo.imagem_b64("docs/midia/arte/icones/caixa-de-votos-azul.png", 110)
    return f".t14r .ux.pt{{background-image:url({vm})}}.t14r .ux.adv{{background-image:url({az})}}"

CSS_TITULO = (
    ".t14t .rot{position:absolute;left:0;top:0}"
    ".t14t .man{position:absolute;left:0;top:22px;font-size:24px}"
    ".t14t .leg{position:absolute;right:0;top:0;display:flex;gap:22px;font-size:15px;color:var(--grafite)}"
    ".t14t .leg i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:7px;vertical-align:-1px}"
    ".t14t .leg .pt{background:var(--vermelho)}.t14t .leg .adv{background:var(--azul)}"
    ".t14t .leg .subl{width:20px;height:3px;border-radius:2px;background:var(--vermelho);vertical-align:3px}"
)

CSS_LINHAS = (
    ".ano{pointer-events:none}"
    ".ano .alvo{position:absolute;top:0;width:256px;height:350px;pointer-events:auto;border-radius:4px;"
    "transition:background .15s}"
    ".ano .alvo:hover{background:rgba(28,25,21,.05)}"
    ".ano .sv{position:absolute;left:0;top:0}"
    ".ano .g{stroke:var(--areia);stroke-width:1}.ano .base{stroke:var(--grafite);stroke-width:1.2}"
    ".ano .tk{font-family:var(--fonte);font-size:13px;fill:var(--cinza)}"
    ".ano .lpt{stroke:var(--vermelho);stroke-width:3.4;stroke-linecap:round}"
    ".ano .ladv{stroke:var(--azul);stroke-width:3.4;stroke-linecap:round}"
    ".ano .traco{animation-duration:.9s}"
    ".ano .ppt{fill:var(--vermelho);stroke:var(--papel);stroke-width:2.5}"
    ".ano .padv{fill:var(--azul);stroke:var(--papel);stroke-width:2.5}"
    ".ano .subl{fill:none;stroke:var(--vermelho);stroke-width:3;stroke-linecap:round;animation-duration:.8s}"
    ".ano .vl{position:absolute;width:120px;text-align:center;font-size:20px;font-weight:700}"
    ".ano .vpt{color:var(--vermelho-escuro)}.ano .vadv{color:var(--azul-escuro)}"
    ".ano .xl{position:absolute;top:298px;width:256px;text-align:center}"
    ".ano .xl b{display:block;font-size:20px;font-weight:700}"
    ".ano .xl span{display:block;font-size:13px;color:var(--cinza);margin-top:2px}"
)

CSS_REGIOES = (
    ".t14g0 .rot{position:absolute;left:0;top:0}"
    ".t14g{pointer-events:none}"
    ".t14g .pn{position:absolute;top:22px;width:300px;height:160px;transition:opacity .3s,background .15s;"
    "pointer-events:auto;cursor:pointer;border-radius:4px}"
    ".t14g .pn:hover{background:rgba(28,25,21,.05)}"
    ".t14g .mk{stroke:var(--grafite);stroke-width:1;stroke-dasharray:2 3}"
    ".t14g .pn .nm{font-size:16px;font-weight:600;height:24px;white-space:nowrap}"
    ".t14g .pn .mao{font-size:24px;color:var(--azul-escuro);margin-left:6px}"
    ".t14g .pn svg{position:absolute;left:0;top:26px}"
    ".t14g .b{stroke:var(--grafite);stroke-width:1}"
    ".t14g .lpt{fill:none;stroke:var(--vermelho);stroke-width:2.2;stroke-linejoin:round}"
    ".t14g .ladv{fill:none;stroke:var(--azul);stroke-width:2.2;stroke-linejoin:round}"
    ".t14g .ppt{fill:var(--vermelho)}.t14g .padv{fill:var(--azul)}"
    ".t14g .vpt{font-family:var(--fonte);font-size:14px;font-weight:700;fill:var(--vermelho-escuro)}"
    ".t14g .vadv{font-family:var(--fonte);font-size:14px;font-weight:700;fill:var(--azul-escuro)}"
    ".t14g .vpt,.t14g .vadv{paint-order:stroke;stroke:var(--papel);stroke-width:4px;stroke-linejoin:round}"
    ".t14g .ex{font-family:var(--fonte);font-size:12px;fill:var(--cinza)}"
    ".t14g .apaga{opacity:.32}"
)

CSS_TOOLTIP = (
    ".tt14{background:var(--branco);border:1.5px solid var(--areia);padding:20px 24px 16px 24px}"
    ".tt14 .fita{position:absolute;left:168px;top:-9px;width:112px;height:24px;background:var(--areia);opacity:.7;"
    "transform:rotate(-3deg)}"
    ".tt14 .an{font-size:24px;font-weight:700}"
    ".tt14 .rot{margin-top:10px;margin-bottom:6px}"
    ".tt14 .cl{display:grid;grid-template-columns:160px 140px 1fr;align-items:center;height:28px;gap:8px}"
    ".tt14 .cl .nm{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".tt14 .cl .nm i{font-style:normal;font-size:11px;font-weight:600;color:var(--cinza)}"
    ".tt14 .cl .tr{display:block;height:10px;background:var(--creme)}"
    ".tt14 .cl b{display:block;height:10px;background:var(--areia)}"
    ".tt14 .cl b.pt{background:var(--vermelho)}.tt14 .cl b.adv{background:var(--azul)}"
    ".tt14 .cl .pc{font-size:14px;font-weight:700;text-align:right}"
    ".tt14 .nota{margin-top:8px}"
    ".tt14 .selo{position:absolute;right:18px;top:20px;transform:rotate(6deg);border:2.5px solid currentColor;"
    "outline:1px solid currentColor;outline-offset:2px;padding:5px 9px;font-weight:700;font-size:13px;"
    "letter-spacing:.14em;white-space:nowrap}"
    ".tt14 .selo.az{color:var(--azul)}.tt14 .selo.vm{color:var(--vermelho)}"
    ".tt14 .mao{position:absolute;right:22px;bottom:12px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
)


CSS_TOOLTIP_REGIAO = (
    ".tt14r{background:var(--branco);border:1.5px solid var(--areia);padding:20px 24px 16px 24px}"
    ".tt14r .fita{position:absolute;left:168px;top:-9px;width:112px;height:24px;background:var(--areia);opacity:.7;"
    "transform:rotate(-3deg)}"
    ".tt14r .an{font-size:24px;font-weight:700;padding-right:170px}"
    ".tt14r .rot{margin-top:10px;margin-bottom:6px}"
    ".tt14r .ln{display:grid;grid-template-columns:34px 190px 1fr;align-items:center;gap:10px;height:25px}"
    ".tt14r .ln .a{font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--grafite)}"
    ".tt14r .ln .tr{position:relative;height:12px;background:var(--creme);display:flex;justify-content:space-between}"
    ".tt14r .ln .bl{display:block;height:12px;background:var(--vermelho)}"
    ".tt14r .ln .ba{display:block;height:12px;background:var(--azul)}"
    ".tt14r .ln .p{font-size:14px;white-space:nowrap}"
    ".tt14r .nota{margin-top:8px}"
    ".tt14r .selo{position:absolute;right:18px;top:20px;transform:rotate(6deg);border:2.5px solid currentColor;"
    "outline:1px solid currentColor;outline-offset:2px;padding:5px 8px;font-weight:700;font-size:11px;"
    "letter-spacing:.1em;white-space:nowrap}"
    ".tt14r .selo.az{color:var(--azul)}.tt14r .selo.vm{color:var(--vermelho)}"
    ".tt14r .mao{position:absolute;right:22px;bottom:12px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
)


def _corpo_tt(css: str, icone: str = "calendario-tinta.png") -> str:
    """bodyTemplate do tooltip: o cartão (conteúdo) e, por cima, o ícone em traço no canto de baixo."""
    img = estilo.imagem_b64(f"docs/midia/arte/icones/{icone}", 96)
    return (f"<style>{css}.ttic{{position:fixed;left:22px;bottom:12px;width:42px;height:42px;opacity:.8;"
            f"background:url({img}) center/contain no-repeat;pointer-events:none}}</style>{{{{content}}}}"
            "<div class='ttic entra d5'></div>")


def _corpo(css: str) -> str:
    return f"<style>{css}</style>{{{{content}}}}"


CORPO_REGIOES = (f"<style>{CSS_REGIOES}</style><div class='tela t14g0' style='pointer-events:none'><div class='rot entra'>"
                 "POR REGIÃO · MESMA ESCALA, 10% A 70% · CLIQUE NUMA REGIÃO PARA VER A SÉRIE DELA</div></div>"
                 "{{content}}")


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T14_Resposta_Html", *RESPOSTA, "T14 · Resposta · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_RESPOSTA + _css_urnas()), alt=lib.medida("T14 · Resposta · ALT"),
                                  z=Z, tab=100)),
        Visual(P, lib.visual_html("T14_Linhas_Titulo", *TITULO, "T14 · Linhas título · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_TITULO), alt=lib.medida("T14 · Linhas título · ALT"),
                                  z=Z + 1, tab=110)),
        Visual(P, lib.visual_html("T14_Linhas_Html", *LINHAS, "T14 · Linhas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=_corpo(CSS_LINHAS), granularidade=("Ano", "Ano"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT14Ano",
                                  alt=lib.medida("T14 · Linhas · ALT"), z=Z + 2, tab=120)),
        Visual(P, lib.visual_html("T14_Regioes_Html", *REGIOES, "T14 · Regiões · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=CORPO_REGIOES, granularidade=("Município", "Região"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT14Regiao",
                                  alt=lib.medida("T14 · Regiões · ALT"), z=Z + 3, tab=130)),
        *pagina_lib.tooltip("ttT14Ano", "Série · eleição", 440, 300, "T14 · Tooltip ano · HTML", ordem=ORDEM_TT,
                            folha_de_estilo=CSS, modelo_corpo=_corpo_tt(CSS_TOOLTIP)),
        *pagina_lib.tooltip("ttT14Regiao", "Série · região", 460, 400, "T14 · Tooltip região · HTML",
                            ordem=ORDEM_TT + 1, folha_de_estilo=CSS,
                            modelo_corpo=_corpo_tt(CSS_TOOLTIP_REGIAO, "pino-tinta.png")),
    ]
