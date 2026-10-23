# -*- coding: utf-8 -*-
"""13 · Perfil — em que tipo de cidade Lula perdeu mais? (dono: agente das telas 11–15). Filtro de UF da casca.

Nas cidades de até 10 mil habitantes e de renda mais alta, a margem de Lula caiu 16,5 pontos; quanto menor a cidade,
maior a queda.

  T13_Matriz_Html     a matriz porte × quinto de renda: queda da margem em cada célula (azul mais escuro, queda maior;
                      células com menos de 10 cidades esmaecidas), totais de linha e coluna; ao passar o mouse, um
                      cartão com as três maiores cidades da célula e a margem de 2026
  T13_Resposta_Html   a maior queda (número grande, frase e exemplos), a menor queda e "como ler uma célula" (uma célula
                      anotada à mão e o que é margem, em linguagem simples)

Medidas em pbi/dax/T13 Perfil (geradas por pbi/scripts/desenho_t13.py).
"""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Visual

P = "T13"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]

MATRIZ = (150, 140, 1080, 860)
RESPOSTA = (1270, 140, 500, 860)

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
    ".t13m .cel{position:absolute;width:168px;height:92px;border-radius:3px;padding:12px 14px;cursor:default}"
    ".t13m .cel .num{display:block;font-size:26px}"
    ".t13m .cel .n{display:block;font-size:13px;margin-top:14px;opacity:.85}"
    + "".join(f".t13m .{c}{{background:{h};color:var(--{t})}}" for c, h, t in _ESCALA)
    + ".t13m .cel.poucas{opacity:.55;outline:1.5px dashed var(--grafite);outline-offset:-1.5px}"
    ".t13m .cel.vazia{border:1.5px dashed var(--areia);background:transparent}"
    ".t13m .cel .tr{font-size:24px;color:var(--cinza)}"
    ".t13m .cel.pior{box-shadow:0 0 0 3px var(--papel),0 0 0 5px var(--vermelho)}"
    ".t13m .cel:hover{outline:2px solid var(--tinta);outline-offset:2px;opacity:1;z-index:10}"
    ".t13m .card{position:absolute;left:0;top:98px;width:300px;padding:12px 14px;background:var(--branco);"
    "border:1px solid var(--areia);box-shadow:0 8px 20px rgba(28,25,21,.18);color:var(--tinta);opacity:0;"
    "pointer-events:none;transition:opacity .15s;z-index:30}"
    ".t13m .cel.esq .card{left:auto;right:0}.t13m .cel.cima .card{top:auto;bottom:98px}"
    ".t13m .cel:hover .card{opacity:1}"
    ".t13m .card b{display:block;font-size:14px;font-weight:700}"
    ".t13m .card span{display:block;font-size:13px;line-height:1.4;margin-top:4px;color:var(--grafite)}"
    ".t13m .card .ex{color:var(--tinta)}"
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
    ".t13r .qual{position:absolute;left:0;top:118px;width:200px}"
    ".t13r .setas{position:absolute;left:150px;top:30px}"
    ".t13r .a1{position:absolute;left:220px;top:34px;font-size:24px;color:var(--grafite)}"
    ".t13r .a2{position:absolute;left:220px;top:92px;font-size:24px;color:var(--grafite)}"
    ".t13r .def{position:absolute;left:0;top:172px;width:490px;font-size:15px}"
)


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T13_Matriz_Html", *MATRIZ, "T13 · Matriz · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=CORPO_MATRIZ, alt=lib.medida("T13 · Matriz · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T13_Resposta_Html", *RESPOSTA, "T13 · Resposta · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_RESPOSTA}</style>{{{{content}}}}",
                                  alt=lib.medida("T13 · Resposta · ALT"), z=Z + 1, tab=110)),
    ]
