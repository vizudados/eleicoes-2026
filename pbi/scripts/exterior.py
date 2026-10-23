"""exterior — o tooltip rico do exterior país a país nas telas que mostram o exterior (12, 18 e 22). Dono: main.

Cada tela ganha um alvo (HTML Content de granularidade UF filtrado ao ZZ) sobre a linha ou o quadrado do exterior e a
página de tooltip própria do exterior, maior que a das UFs (o Power BI dá um tooltip por visual, então o exterior
precisa do seu visual). O desenho é de pbi/scripts/desenho_exterior.py.
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual

C = estilo.COR
LARGURA, ALTURA = 600, 690

CSS = (
    f".tx{{background:{C['branco']};border:1.5px solid {C['areia']};padding:30px 30px 18px 30px;"
    "box-shadow:0 12px 28px rgba(28,25,21,.18)}"
    f".tx .fita{{position:absolute;left:230px;top:-10px;width:150px;height:26px;background:{C['areia']};opacity:.75;"
    "transform:rotate(-2deg)}"
    f".tx .aviso{{font-family:var(--mao);font-size:22px;line-height:1.1;color:{C['vermelho_escuro']};margin:-8px 0 8px 0;"
    "white-space:nowrap}"
    ".tx .topo-rot{font-size:12px}"
    ".tx .topo{display:flex;gap:30px;align-items:flex-end;margin:12px 0 4px 0}"
    ".tx .topo .c{display:flex;flex-direction:column;gap:4px}"
    ".tx .topo .num{font-size:40px}"
    ".tx .topo .tot .num{font-size:24px;color:var(--grafite)}"
    ".tx .mao{font-size:24px;color:var(--grafite);margin:2px 0 10px 0;transform:rotate(-1.5deg);transform-origin:left}"
    ".tx .cab{display:grid;grid-template-columns:166px 46px 1fr 58px 62px;gap:8px;padding-bottom:6px;"
    "letter-spacing:.08em;white-space:nowrap"
    f"border-bottom:1.5px solid {C['tinta']}}}"
    ".tx .cab span:nth-child(2){text-align:right}.tx .cab span:nth-child(5){text-align:right}"
    ".tx .lp{display:grid;grid-template-columns:166px 46px 1fr 58px 62px;gap:8px;align-items:center;height:33px;"
    f"border-bottom:1px solid {C['creme']}}}"
    ".tx .lp .pn{display:flex;flex-direction:column;line-height:1.1;overflow:hidden}"
    ".tx .lp .pn b{font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".tx .lp .pn i{font-style:normal;font-size:13px;color:var(--cinza)}"
    f".tx .lp .vl{{font-size:15px;font-weight:700;color:{C['vermelho_escuro']};text-align:right}}"
    f".tx .lp .vf{{font-size:15px;font-weight:700;color:{C['azul_escuro']}}}"
    f".tx .lp .br{{position:relative;height:14px;background:{C['creme']};display:flex;justify-content:space-between;"
    "overflow:hidden}"
    f".tx .lp .br .bl{{display:block;height:14px;background:{C['vermelho']}}}"
    f".tx .lp .br .bf{{display:block;height:14px;background:{C['azul']}}}"
    ".tx .lp .dv{font-size:14px;font-weight:700;text-align:right;color:var(--grafite)}"
    f".tx .lp .dv.neg{{color:{C['azul_escuro']}}}.tx .lp .dv.pos{{color:{C['vermelho_escuro']}}}"
    ".tx .outros{margin-top:10px;font-size:15px;color:var(--tinta)}"
    ".tx .pe{margin-top:6px}"
    f".tx .cen{{display:flex;gap:22px;align-items:baseline;background:{C['creme']};margin:-8px -12px 12px -12px;"
    "padding:9px 12px;white-space:nowrap}"
    ".tx .cen .rot{color:var(--grafite);flex:1}.tx .cen b{font-size:20px;font-weight:700}"
)
# o alvo: transparente, só desenha o realce do mouse por cima do desenho da tela
CSS_ALVO = ".ax{cursor:default;border-radius:3px}.ax:hover{box-shadow:inset 0 0 0 2px " + C["tinta"] + "}"
CORPO_TT = f"<style>{CSS}</style>{{{{content}}}}"


def declarar(pagina: str, nome_alvo: str, caixa: tuple, medida_tt: str, ordem: int, *, desenho_alvo: str | None = None,
             css_alvo: str = CSS_ALVO, z: int | None = None, cruzar: bool = False, altura: int = ALTURA) -> list:
    """O alvo do exterior (visual `nome_alvo` em `caixa`, filtrado ao ZZ) e a página de tooltip tt<TELA>Exterior com
    `medida_tt`. `desenho_alvo` = medida que desenha o alvo (padrão: transparente, com o realce do mouse em `css_alvo`);
    `cruzar` liga o filtro cruzado (o clique no alvo filtra a tela pelo exterior); `altura` = altura do cartão."""
    tt = f"tt{pagina}Exterior"
    so_zz = lib.filtro_visual_categorico("soExterior", "UF", "UF", ["ZZ"])
    for f in so_zz["filters"]:
        f["isHiddenInViewMode"] = True
        f["isLockedInViewMode"] = True
    medida = desenho_alvo or "Exterior · alvo · HTML"
    alt = medida.replace("· HTML", "· ALT")
    return [
        Visual(pagina, lib.visual_html(nome_alvo, *caixa, medida, folha_de_estilo="Estilo · CSS",
                                       modelo_corpo=(f"<style>{css_alvo}</style>{{{{content}}}}" if css_alvo else None),
                                       granularidade=("UF", "UF"), filtro_cruzado=cruzar, tooltip_pagina=tt,
                                       transparencia_nao_selecionados=True if cruzar else None,
                                       alt=lib.medida(alt), z=z or lib.CAMADAS["conteudo"] + 40, tab=500,
                                       filtros=so_zz, movimento=False)),
        *pagina_lib.tooltip(tt, "Exterior · país a país", LARGURA, altura, medida_tt, ordem=ordem,
                            folha_de_estilo="Estilo · CSS", modelo_corpo=CORPO_TT),
    ]
