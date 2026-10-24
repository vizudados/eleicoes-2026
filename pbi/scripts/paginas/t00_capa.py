# -*- coding: utf-8 -*-
"""00 · Capa — afinal, qual Brasil foi às urnas no 1º turno? (dono: main). Tela escura, sem filtro.

Conceito (pedido do Alisson, 23/10/2026: "o mapa do Brasil e várias paisagens, a bandeira aparecendo", com uma capa
própria, que não repita a de outro painel da casa): as 27 estrelas da bandeira viram as UFs no mapa, os 5.571 municípios acendem pela margem e as
paisagens se desenham num horizonte contínuo, de Norte a Sul. Composição simétrica e centrada: o título no alto, os dois
candidatos em blocos espelhados à esquerda e à direita, o mapa no meio.

  T00_Capa_Html   o vídeo (Remotion, GitHub Pages: midia/capa/capa.mp4 e .webm, toca uma vez e para no quadro final;
                  pôster capa-final.jpg; com movimento reduzido, só o pôster), o título e a composição fixa no
                  bodyTemplate, e os números (contador) da medida [T00 · Capa · HTML]
  T00_Capa_Comecar   botão sobre o convite "começar" (vai à tela 01)
"""
from __future__ import annotations

import estilo
import pbip_lib as lib
import roteiro
from paginas.casca import corpo_casca
from pbip_lib import Visual

P = "T00"
CSS = "Estilo · CSS"
C = estilo.COR
MIDIA = "https://vizudados.github.io/eleicoes-2026/midia"


def corpo() -> str:
    css = (
        ".cp{color:var(--creme)}"
        ".cp video,.cp .poster{position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover}"
        # o vídeo começa no céu escuro (pôster capa-inicio); se ele não carregar, o quadro final entra no lugar
        ".cp .poster{display:none}"
        "@media (prefers-reduced-motion:reduce){.cp video{display:none}.cp .poster{display:block}}"
        ".cp .topo{position:absolute;left:300px;right:300px;top:118px;text-align:center}"
        f".cp .topo .sob{{color:{C['areia']};font-size:16px}}"
        ".cp .topo .tg{font-size:88px;font-weight:700;letter-spacing:-.035em;line-height:1;margin-top:14px}"
        f".cp .topo .q{{font-size:24px;font-weight:500;color:{C['creme']};margin-top:16px;opacity:.92}}"
        ".cp .bl{position:absolute;top:430px;width:420px}"
        ".cp .bl.esq{left:140px}.cp .bl.dir{left:1360px;text-align:right}"
        f".cp .bl .rot{{color:{C['areia']};font-size:15px}}"
        ".cp .bl .v{font-size:76px;margin:14px 0 10px 0}"
        f".cp .flavio-c{{color:{C['azul_claro']}}}.cp .lula-c{{color:{C['rosa']}}}"
        ".cp .bl .p{font-size:22px;font-weight:500}"
        ".cp .pe-esq,.cp .pe-dir{position:absolute;top:706px;font-size:20px;font-weight:500}"
        ".cp .pe-esq{left:140px}.cp .pe-dir{right:140px;text-align:right}"
        ".cp .pe-esq .num,.cp .pe-dir .num{font-size:28px;font-weight:700}"
        ".cp .vir{position:relative;display:inline-block;padding:0 6px}"
        f".cp .sumario{{position:absolute;left:150px;top:60px;font-size:14px;font-weight:600;letter-spacing:.16em;"
        f"text-transform:uppercase;color:{C['areia']}}}"
        ".cp .sumario span{font-size:18px;margin-right:6px}"
        ".cp .comecar{position:absolute;left:1690px;top:585px;font-family:var(--mao);font-size:26px;"
        f"color:{C['areia']};transform:rotate(-6deg)}}"
    )
    # o traço à mão embaixo do número de municípios que viraram (o laço em volta cruzava os dígitos e o "m" de
    # municípios; L128: rabisco nunca cruza número). O mesmo sublinhado da tela 01, na cor creme
    import desenho_t01
    risco = (desenho_t01.SUBLINHADO.replace("#1C1915", C["creme"]).replace("id='rbl'", "id='rbc'")
             .replace("url(#rbl)", "url(#rbc)").replace("class='sub'", "class='sb'"))
    return (
        f"<style>{css}</style><div class='tela cp'>"
        f"<video autoplay muted playsinline preload='auto' poster='{MIDIA}/capa/capa-inicio.jpg' "
        "onerror=\"this.style.display='none';this.nextElementSibling.style.display='block'\">"
        f"<source src='{MIDIA}/capa/capa.mp4' type='video/mp4'/><source src='{MIDIA}/capa/capa.webm' type='video/webm' "
        "onerror=\"var v=this.parentNode;v.style.display='none';v.nextElementSibling.style.display='block'\"/>"
        "</video>"
        f"<img class='poster' alt='' src='{MIDIA}/capa/capa-final.jpg'/>"
        "<div class='topo'><div class='sob sobe d1'>ELEIÇÕES 2026 · 1º TURNO PRESIDENCIAL</div>"
        "<div class='tg sobe d2'>O voto, de perto.</div>"
        "<div class='q sobe d4'>Afinal, qual Brasil foi às urnas no 1º turno?</div></div>"
        "<div class='comecar entra d14'>começar</div>"
        "<div class='sumario entra d14'><span>☰</span> sumário</div>"
        "{{content}}"
        # o traço à mão embaixo do número de municípios que viraram (span .risco dentro do .vir, no bloco do pé)
        f"<style>.cp .vir .risco{{position:absolute;left:6px;right:6px;bottom:-9px;height:10px}}"
        f".cp .vir .risco svg{{display:block;width:100%;height:100%}}</style>"
        f"<script>(function(){{var l=document.querySelectorAll('.cp .vir .risco');for(var i=0;i<l.length;i++)"
        f"{{if(!l[i].firstChild){{l[i].innerHTML={risco!r};}}}}}})();</script>"
        "</div>"
        # a casca da capa (lockup, fonte, "i", seta) por cima do vídeo, que cobre a página inteira; sem a urna (a capa é o
        # início)
        + _casca_por_cima()
    )


def _casca_por_cima() -> str:
    c = corpo_casca(roteiro.POR_CODIGO[P]).replace("{{content}}", "")
    i = c.index("<img class='urna"); j = c.index("/>", i) + 2
    return c[:i] + c[j:]


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T00_Capa_Html", 0, 0, lib.LARGURA, lib.ALTURA, "T00 · Capa · HTML",
                                  folha_de_estilo=CSS, modelo_corpo=corpo(), alt=lib.medida("T00 · Capa · ALT"),
                                  z=lib.CAMADAS["conteudo"], tab=100)),
        Visual(P, lib.visual_botao("T00_Capa_Sumario", 136, 44, 180, 52, lib.acao_bookmark("TIX_CHEGADA_01"),
                                   dica="Sumário: todas as telas", z=lib.CAMADAS["acao"], tab=105, realce=C["creme"],
                                   raio=8, realce_transp=(92, 86))),
        Visual(P, lib.visual_botao("T00_Capa_Comecar", 1680, 560, 120, 70, lib.acao_bookmark(f"{roteiro.TELAS[1].codigo}_CHEGADA_01"),
                                   dica=f"Começar: {roteiro.TELAS[1].numero} · {roteiro.TELAS[1].nome}",
                                   z=lib.CAMADAS["acao"], tab=110, realce=C["creme"],
                                   raio=30, realce_transp=(92, 86))),
    ]
