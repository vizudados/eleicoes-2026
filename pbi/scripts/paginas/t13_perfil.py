# -*- coding: utf-8 -*-
"""13 · Perfil — em que tipo de cidade Lula perdeu mais? (dono: agente das telas 11–15). Filtro de UF da casca.

Nas cidades de até 10 mil habitantes e de renda mais alta, a margem de Lula caiu 16,5 pontos; quanto menor a cidade,
maior a queda.

  T13_Matriz_Html     a moldura da matriz porte × quinto de renda: título e manchete, faixas de renda, portes com o total
                      de cada linha, as células vazias, o total de cada coluna, a escala e a nota
  T13_Matriz_Celulas  as células com cidades, uma por ponto de dado (granularidade T13 Célula[Célula], tabela de
                      pbi/modelo/t13_celula.py), na mesma caixa e geometria da moldura: a queda da margem (azul mais
                      escuro, queda maior; menos de 10 cidades, esmaecida e tracejada; a maior queda com contorno
                      vermelho). Mouse: o dossiê da célula (ttT13Celula). Clique: filtra as cidades da célula na
                      resposta (as outras células esmaecem; clicar de novo volta)
  T13_Resposta_Html   sem clique, a maior queda (número grande, frase e exemplos), a menor queda e "como ler uma célula";
                      com uma célula clicada, a queda dela, as cidades dela, a comparação com a maior queda (e a
                      posição entre as células) e a célula anotada

Interações (só as exceções): o clique numa célula não mexe na moldura (que conta a matriz inteira).

Medidas em pbi/dax/T13 Perfil (geradas por pbi/scripts/desenho_t13.py).
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
import roteiro
from pbip_lib import Interacao, Visual

P = "T13"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]

MATRIZ = (150, 140, 1080, 860)
RESPOSTA = (1270, 140, 500, 860)
# páginas de tooltip: ordem 100 + número da tela para o leitor × 10 (o número sai do roteiro e anda com ele)
ORDEM_TT = 100 + int(roteiro.numero(P)) * 10

_ESCALA = [("c0", "#E7C6BC", "tinta"), ("c1", "#DADDE2", "tinta"), ("c2", "#C0CBDB", "tinta"),
           ("c3", "#98AECF", "tinta"), ("c4", "#5878A9", "branco"), ("c5", "#2B5797", "branco")]

CSS_MATRIZ = (
    ".t13m .rot{position:absolute;left:0;top:0}"
    ".t13m .man{position:absolute;left:0;top:24px;right:0;font-size:24px}"
    ".t13m .eixoP{position:absolute;left:0;top:112px}"
    ".t13m .eixoQ{position:absolute;left:190px;top:80px}"
    ".t13m .cq{position:absolute;top:104px;width:168px;padding-left:2px}"
    ".t13m .cq b{display:block;font-size:14px;font-weight:700;letter-spacing:.1em}"
    ".t13m .cq span{display:block;font-size:13px;color:var(--cinza);margin-top:3px;white-space:nowrap}"
    ".t13m .rl{position:absolute;left:0;width:180px;height:92px}"
    ".t13m .rl b{display:block;font-size:16px;font-weight:600}"
    ".t13m .rl .num{display:block;font-size:24px;margin-top:4px}"
    ".t13m .rl i{display:block;font-style:normal;font-size:13px;color:var(--cinza);margin-top:4px}"
    ".t13m .cel{position:absolute;width:168px;height:92px;border-radius:3px;padding:12px 14px}"
    ".t13m .cel.vazia{border:1.5px dashed var(--areia);background:transparent}"
    ".t13m .cel .tr{font-size:24px;color:var(--cinza)}"
    ".t13m .linha{position:absolute;left:190px;top:668px;width:872px;border-top:1.5px solid var(--grafite)}"
    ".t13m .todas{position:absolute;left:0;top:680px;width:180px}"
    ".t13m .todas b{display:block;font-size:16px;font-weight:600}.t13m .todas .num{display:block;font-size:24px}"
    ".t13m .todas i{display:block;font-style:normal;font-size:13px;color:var(--cinza);margin-top:4px;width:170px}"
    ".t13m .tq{position:absolute;top:684px;width:168px;padding-left:14px}.t13m .tq .num{font-size:26px}"
    ".t13m .pe{position:absolute;left:190px;top:740px;width:872px}"
    ".t13m .escala{position:absolute;left:190px;top:790px;display:flex;align-items:center;gap:6px;font-size:13px;"
    "color:var(--grafite)}"
    ".t13m .escala i{display:inline-block;width:44px;height:14px;border-radius:2px}"
    ".t13m .escala span{margin:0 8px}"
)
CORPO_MATRIZ = (
    f"<style>{CSS_MATRIZ}</style><div class='tela t13m' style='pointer-events:none'><div class='linha entra'></div>"
    "<div class='escala entra'><span>subiu</span>" + "".join(f"<i style='background:{h}'></i>" for _c, h, _t in _ESCALA)
    + "<span>queda maior</span></div></div>{{content}}"
)

# as células com cidades (uma entrada por célula; raiz sem ponteiro, L114: só a célula pega o mouse)
CSS_CELULAS = (
    ".t13c{pointer-events:none}"
    ".t13c .cel{position:absolute;width:168px;height:92px;border-radius:3px;padding:12px 14px;cursor:pointer;"
    "pointer-events:auto}"
    ".t13c .cel .num{display:block;font-size:26px}"
    ".t13c .cel .n{display:block;font-size:13px;margin-top:14px;opacity:.85}"
    + "".join(f".t13c .{c}{{background:{h};color:var(--{t})}}" for c, h, t in _ESCALA)
    + ".t13c .cel.poucas{opacity:.55;outline:1.5px dashed var(--grafite);outline-offset:-1.5px}"
    ".t13c .cel.pior{box-shadow:0 0 0 3px var(--papel),0 0 0 5px var(--vermelho)}"
    ".t13c .cel:hover{outline:2px solid var(--tinta);outline-offset:2px;opacity:1}"
)

CSS_TOOLTIP = (
    ".tt13{background:var(--branco);border:1.5px solid var(--areia);padding:22px 26px 16px 26px}"
    ".tt13 .fita{position:absolute;left:178px;top:-9px;width:112px;height:24px;background:var(--areia);opacity:.7;"
    "transform:rotate(-3deg)}"
    ".tt13 .nm{font-size:22px;font-weight:700;line-height:1.2;padding-right:150px}"
    ".tt13 .sub{margin-top:2px;font-size:15px;font-weight:600;color:var(--grafite)}"
    ".tt13 .nota{margin-top:2px}"
    ".tt13 .selo{position:absolute;right:18px;top:22px;transform:rotate(6deg);border:2.5px solid currentColor;"
    "outline:1px solid currentColor;outline-offset:2px;padding:5px 9px;font-weight:700;font-size:11px;"
    "letter-spacing:.12em;color:var(--grafite);white-space:nowrap}"
    ".tt13 .selo.vm{color:var(--vermelho)}"
    ".tt13 .r1{margin-top:14px}.tt13 .r2{margin-top:8px}.tt13 .r3{margin-top:14px}"
    ".tt13 .regua{display:block;margin-top:2px}"
    ".tt13 .regua .zero{stroke:var(--grafite);stroke-width:1;stroke-dasharray:2 3}"
    ".tt13 .regua line.traco-rapido{stroke:var(--grafite);stroke-width:2.2}"
    ".tt13 .regua .m22{fill:var(--branco);stroke:var(--vermelho);stroke-width:2}"
    ".tt13 .regua text{font-family:var(--fonte);font-size:13px;font-weight:600;fill:var(--grafite);paint-order:stroke;"
    "stroke:var(--branco);stroke-width:4px;stroke-linejoin:round}"
    ".tt13 .regua .lado{font-size:11px;font-weight:500;fill:var(--cinza)}"
    ".tt13 .pilha{display:flex;width:400px;height:14px;margin-top:8px;background:var(--creme)}"
    ".tt13 .pilha i{display:block;height:14px;transform-origin:left center}"
    ".tt13 i.ll{background:var(--rosa)}.tt13 i.vir{background:var(--azul)}.tt13 i.aa{background:var(--azul-claro)}"
    ".tt13 .leg{display:flex;gap:14px;margin-top:6px;font-size:13px;color:var(--grafite);white-space:nowrap}"
    ".tt13 .leg i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}"
    ".tt13 .leg b{font-weight:700;color:var(--tinta)}"
    ".tt13 .maiores{margin-top:4px;width:400px}"
    ".tt13 .mc{display:flex;justify-content:space-between;align-items:baseline;height:23px;font-size:15px;"
    "border-bottom:1px solid var(--creme)}"
    ".tt13 .mc .nm{font-size:15px;font-weight:500;padding:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
    "max-width:300px}"
    ".tt13 .mc .vv{font-weight:700}.tt13 .mc .vv.neg{color:var(--azul-escuro)}"
    ".tt13 .mc .vv.pos{color:var(--vermelho-escuro)}"
    ".tt13 .mao{position:absolute;right:24px;bottom:12px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
)


def _corpo_tt(css: str) -> str:
    """bodyTemplate do tooltip: o cartão (conteúdo) e, por cima, o ícone em traço no canto de baixo."""
    img = estilo.imagem_b64("docs/midia/arte/icones/casa-tinta.png", 96)
    return (f"<style>{css}.ttic{{position:fixed;left:24px;bottom:12px;width:42px;height:42px;opacity:.8;"
            f"background:url({img}) center/contain no-repeat;pointer-events:none}}</style>{{{{content}}}}"
            "<div class='ttic entra d5'></div>")


CSS_RESPOSTA = (
    ".t13r .g{position:absolute;left:-4px;top:-4px;font-size:108px;letter-spacing:-.045em}"
    ".t13r .g small{font-size:46px;letter-spacing:0}"
    ".t13r .m1{position:absolute;left:0;top:118px;width:500px;font-size:24px}"
    ".t13r .ex{position:absolute;left:0;top:236px;width:490px;font-size:16px}"
    ".t13r .menor{position:absolute;left:0;top:330px;width:500px}"
    ".t13r .menor .v{font-size:44px;margin:6px 0 6px 0}.t13r .menor .v small{font-size:22px;letter-spacing:0}"
    ".t13r .menor .txt{font-size:16px}"
    ".t13r .ler{position:absolute;left:0;top:530px;width:500px}"
    ".t13r .amostra{position:absolute;left:0;top:30px;width:150px;height:84px;background:#98AECF;border-radius:3px;"
    "padding:10px 12px}"
    ".t13r .amostra .num{display:block;font-size:24px}.t13r .amostra .n{display:block;font-size:13px;margin-top:12px}"
    + "".join(f".t13r .amostra.{c}{{background:{h};color:var(--{t})}}" for c, h, t in _ESCALA)
    + ".t13r .qual{position:absolute;left:0;top:118px;width:200px}"
    ".t13r .setas{position:absolute;left:150px;top:30px}"
    ".t13r .a1{position:absolute;left:220px;top:34px;font-size:24px;color:var(--grafite)}"
    ".t13r .a2{position:absolute;left:220px;top:92px;font-size:24px;color:var(--grafite)}"
    ".t13r .def{position:absolute;left:0;top:172px;width:490px;font-size:15px}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T13_Matriz_Html", *MATRIZ, "T13 · Matriz · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=CORPO_MATRIZ, alt=lib.medida("T13 · Matriz · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T13_Matriz_Celulas", *MATRIZ, "T13 · Células · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_CELULAS}</style>{{{{content}}}}",
                                  granularidade=("T13 Célula", "Célula"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT13Celula",
                                  alt=lib.medida("T13 · Células · ALT"), z=Z + 2, tab=105)),
        Visual(P, lib.visual_html("T13_Resposta_Html", *RESPOSTA, "T13 · Resposta · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_RESPOSTA}</style>{{{{content}}}}",
                                  alt=lib.medida("T13 · Resposta · ALT"), z=Z + 1, tab=110)),
        *pagina_lib.tooltip("ttT13Celula", "Perfil · célula", 460, 440, "T13 · Tooltip célula · HTML",
                            ordem=ORDEM_TT, folha_de_estilo=CSS, modelo_corpo=_corpo_tt(CSS_TOOLTIP)),
        # o clique numa célula não mexe na moldura: ela conta a matriz inteira (totais de linha e de coluna, manchete)
        Interacao(P, "T13_Matriz_Celulas", "T13_Matriz_Html", "NoFilter"),
    ]
