# -*- coding: utf-8 -*-
"""00 · Capa — a eleição de 2026, do primeiro ao segundo turno, município por município (dono: main). Tela escura, sem filtro.

Conceito (pedido do Alisson, 23/10/2026: "o mapa do Brasil e várias paisagens, a bandeira aparecendo", com uma capa
própria, que não repita a de outro painel da casa): as 27 estrelas da bandeira viram as UFs no mapa, os municípios acendem pelo primeiro turno e uma segunda onda repinta pelo segundo.
As paisagens se desenham num horizonte contínuo, de Norte a Sul. Composição simétrica e centrada: o título no alto, os dois
candidatos em blocos espelhados à esquerda e à direita, o mapa no meio.

  T00_Capa_Html   o vídeo (Remotion, GitHub Pages: midia/capa/capa-2t.mp4 e .webm, toca uma vez e para no quadro final;
                  pôster capa-2t-final.jpg; com movimento reduzido, só o pôster), o título e a composição fixa no
                  bodyTemplate, e os números (contador) da medida [T00 · Capa · HTML]
  T00_Capa_Comecar   botão sobre o convite "começar" (vai à tela 01)
"""
from __future__ import annotations

import estilo
import pbip_lib as lib
import roteiro
from paginas import casca
from paginas.casca import corpo_casca
from pbip_lib import Visual

P = "T00"
CSS = "Estilo · CSS"
C = estilo.COR
MIDIA = "https://vizudados.github.io/eleicoes-2026/midia"
# docs/midia/capa/LEIAME.md: primeiro ponto colorido no quadro 280, segunda onda no quadro 396, 30 fps.
# Se o roteiro mudar, trocar aqui: os valores vão para as variáveis CSS da capa.
ROTULO_INICIO_S = 280 / 30
ROTULO_SEGUNDO_S = 396 / 30


def corpo() -> str:
    css = (
        f".cp{{--rotulo-inicio:{ROTULO_INICIO_S:.9f}s;--rotulo-segundo:{ROTULO_SEGUNDO_S:.9f}s;color:var(--creme)}}"
        ".cp video,.cp .poster{position:absolute;left:0;top:0;width:1920px;height:1080px;object-fit:cover}"
        # o vídeo começa no céu escuro (pôster capa-inicio); se ele não carregar, o quadro final entra no lugar
        ".cp .poster{display:none}"
        ".cp .topo{position:absolute;left:300px;right:300px;top:118px;text-align:center}"
        f".cp .topo .sob{{color:{C['areia']};font-size:16px}}"
        ".cp .topo .tg{font-size:88px;font-weight:700;letter-spacing:-.035em;line-height:1;margin-top:14px}"
        f".cp .topo .q{{font-size:24px;font-weight:500;color:{C['creme']};margin-top:16px;opacity:.92}}"
        ".cp .bl{position:absolute;top:430px;width:420px}"
        ".cp .bl.esq{left:140px}.cp .bl.dir{left:1360px;text-align:right}"
        f".cp .bl .rot{{color:{C['areia']};font-size:15px}}"
        ".cp .bl .etapa{font-size:13px;margin-top:9px;letter-spacing:.10em}"
        ".cp .bl .v{font-size:76px;margin:10px 0 10px 0}"
        f".cp .flavio-c{{color:{C['azul_claro']}}}.cp .lula-c{{color:{C['rosa']}}}"
        ".cp .bl .p{font-size:22px;font-weight:500}"
        ".cp .bl .primeiro{font-size:16px;font-weight:500;color:var(--areia);margin-top:18px}"
        ".cp .bl .primeiro .num{font-size:20px;line-height:1.2}"
        ".cp .selo-eleito{display:inline-block;font-family:var(--mao);font-size:26px;line-height:1;letter-spacing:.04em;"
        "color:var(--creme);border:1.5px solid var(--areia);padding:3px 12px 5px;margin-top:14px;transform:rotate(-4deg)}"
        ".cp .pe-esq,.cp .pe-dir{position:absolute;top:706px;font-size:20px;font-weight:500}"
        ".cp .pe-esq{left:140px;width:450px;font-size:16px;line-height:28px}.cp .pe-dir{right:140px;text-align:right}"
        ".cp .pe-esq .num{font-size:24px;line-height:28px}"
        ".cp .pe-esq .num,.cp .pe-dir .num{font-size:28px;font-weight:700}"
        ".cp .vir{position:relative;display:inline-block;padding:0 6px}"
        ".cp .mapa-rotulo{position:absolute;left:1040px;top:808px;width:270px;height:28px;display:grid;align-items:center;justify-items:start;"
        "color:var(--areia);font-size:14px;font-weight:500;pointer-events:none;text-shadow:0 0 5px var(--tinta),0 0 5px var(--tinta);"
        "animation:rotuloEntra .35s ease var(--rotulo-inicio) both}"
        ".cp .mapa-rotulo span{grid-area:1/1}.cp .mapa-rotulo .t1{opacity:0;animation:rotuloSai .35s ease var(--rotulo-segundo) both}"
        ".cp .mapa-rotulo .t2{opacity:1;animation:rotuloEntra .35s ease var(--rotulo-segundo) both}"
        "@keyframes rotuloEntra{from{opacity:0}to{opacity:1}}@keyframes rotuloSai{from{opacity:1}to{opacity:0}}"
        ".cp .mapa-rotulo,.cp .mapa-rotulo span{animation-play-state:var(--mapa-movimento,paused)}"
        ".cp.sem-video .mapa-rotulo,.cp.sem-video .mapa-rotulo span{animation:none}"
        "@media (prefers-reduced-motion:reduce){.cp video{display:none}.cp .poster{display:block}"
        ".cp .mapa-rotulo,.cp .mapa-rotulo span{animation:none}}"
        f".cp .sumario{{position:absolute;left:150px;top:60px;font-size:14px;font-weight:600;letter-spacing:.16em;"
        f"text-transform:uppercase;color:{C['areia']}}}"
        ".cp .sumario span{font-size:18px;margin-right:6px}"
        # o card da Lia (27/10/2026, refeito a pedido do Alisson: "isso aqui vai ficar animado? senão, melhora essa
        # capa"): um quadro de giz no céu da capa, a Lia de tronco saindo por cima dele e trocando de pose a cada 3 s
        # (corte com um pulo, como nos vídeos: fusão de duas poses mostra dois rostos), o play em giz que se desenha e
        # pulsa, e a legenda à mão. Só CSS; com movimento reduzido, a 1ª pose parada. O botão nativo
        # T00_Casca_VideoAbre (casca.VIDEO_CAPA) cobre o quadro e a legenda.
        + (".cp .lia-card{position:absolute;left:140px;top:60px;width:330px;height:270px}"
        ".cp .lia-card .qd{position:absolute;left:0;top:50px;width:320px;height:170px;border-radius:14px;"
        "background:radial-gradient(1.2px 1.2px at 38px 34px,rgba(241,235,223,.9),transparent),"
        "radial-gradient(1px 1px at 96px 22px,rgba(241,235,223,.7),transparent),"
        "radial-gradient(1.4px 1.4px at 128px 64px,rgba(241,235,223,.8),transparent),"
        "radial-gradient(1px 1px at 70px 140px,rgba(241,235,223,.6),transparent),"
        "radial-gradient(1px 1px at 18px 96px,rgba(241,235,223,.7),transparent),"
        "radial-gradient(120% 140% at 30% 30%,#2b2620 0%,#1a1714 62%,#110f0d 100%);"
        "box-shadow:0 22px 44px -24px rgba(0,0,0,.95)}"
        ".cp .lia-card .qd svg.giz{position:absolute;left:-3px;top:-3px;width:326px;height:176px;overflow:visible}"
        ".cp .lia-card .lia{position:absolute;left:100px;top:-10px;width:220px;height:230px}"
        ".cp .lia-card .lia img{position:absolute;left:0;top:0;width:220px;height:230px;opacity:0;"
        "animation:liaPose 9s linear infinite both}"
        ".cp .lia-card .lia img.p2{animation-delay:-6s}.cp .lia-card .lia img.p3{animation-delay:-3s}"
        "@keyframes liaPose{0%{opacity:1;transform:translateY(7px) scale(.985)}"
        "3%{opacity:1;transform:translateY(0) scale(1)}33.3%{opacity:1;transform:none}33.34%{opacity:0}100%{opacity:0}}"
        ".cp .lia-card .pl{position:absolute;left:24px;top:38px;width:60px;height:60px}"
        ".cp .lia-card .pl svg{position:absolute;left:0;top:0;width:60px;height:60px;overflow:visible}"
        ".cp .lia-card .pl .anel{stroke-dasharray:190;stroke-dashoffset:190;animation:giz .9s ease-out 1.6s forwards}"
        ".cp .lia-card .pl .eco{position:absolute;left:0;top:0;width:60px;height:60px;border-radius:50%;"
        "border:1.5px solid rgba(241,235,223,.55);opacity:0;animation:eco 3s ease-out 2.6s infinite}"
        "@keyframes giz{to{stroke-dashoffset:0}}"
        "@keyframes eco{0%{opacity:.7;transform:scale(1)}55%{opacity:0;transform:scale(1.45)}100%{opacity:0}}"
        ".cp .lia-card .dur{position:absolute;left:26px;top:110px;font-size:12px;font-weight:600;letter-spacing:.14em;"
        "color:var(--areia)}"
        ".cp .lia-card .leg{position:absolute;left:6px;top:234px;font-family:var(--mao);font-size:27px;line-height:1;"
        "color:var(--creme);transform:rotate(-2.5deg);transform-origin:left center;white-space:nowrap}"
        "@media (prefers-reduced-motion:reduce){.cp .lia-card .lia img,.cp .lia-card .pl .anel,.cp .lia-card .pl .eco"
        "{animation:none}.cp .lia-card .lia img.p1{opacity:1}.cp .lia-card .pl .anel{stroke-dashoffset:0}}"
           if casca.VIDEOS_LIA else "")
        +
        ".cp .comecar{position:absolute;left:1800px;top:590px;font-family:var(--mao);font-size:26px;"
        f"color:{C['areia']};transform:rotate(-6deg)}}"
    )
    # o traço à mão embaixo do número de municípios que viraram (o laço em volta cruzava os dígitos e o "m" de
    # municípios; L128: rabisco nunca cruza número). O mesmo sublinhado da tela 01, na cor creme
    import desenho_t01
    risco = (desenho_t01.SUBLINHADO.replace("#1C1915", C["creme"]).replace("id='rbl'", "id='rbc'")
             .replace("url(#rbl)", "url(#rbc)").replace("class='sub'", "class='sb'"))
    return (
        f"<style>{css}</style><div class='tela cp'>"
        f"<video autoplay muted playsinline preload='auto' poster='{MIDIA}/capa/capa-2t-inicio.jpg' "
        "onplaying=\"this.closest('.cp').style.setProperty('--mapa-movimento','running')\" "
        "onwaiting=\"this.closest('.cp').style.setProperty('--mapa-movimento','paused')\" "
        "onpause=\"this.closest('.cp').style.setProperty('--mapa-movimento','paused')\" "
        "onerror=\"this.style.display='none';this.nextElementSibling.style.display='block';this.closest('.cp').classList.add('sem-video')\">"
        f"<source src='{MIDIA}/capa/capa-2t.mp4' type='video/mp4'/><source src='{MIDIA}/capa/capa-2t.webm' type='video/webm' "
        "onerror=\"var v=this.parentNode;v.style.display='none';v.nextElementSibling.style.display='block';v.closest('.cp').classList.add('sem-video')\"/>"
        "</video>"
        f"<img class='poster' alt='' src='{MIDIA}/capa/capa-2t-final.jpg'/>"
        "<div class='topo'><div class='sob sobe d1'>ELEIÇÕES 2026 · OS DOIS TURNOS</div>"
        "<div class='tg sobe d2'>O voto, de perto.</div>"
        "<div class='q sobe d4'>A eleição de 2026, do primeiro ao segundo turno, município por município.</div></div>"
        "<div class='comecar entra d14'>começar</div>"
        "<div class='sumario entra d14'><span>☰</span> sumário</div>"
        + ("<div class='lia-card entra d12'><div class='qd'>"
           "<svg class='giz' viewBox='0 0 326 176' aria-hidden='true'><path d='M17 4C90 2 220 6 309 3C318 4 323 10 322 19"
           "C324 60 321 120 323 157C322 167 316 172 306 173C220 175 100 171 18 174C9 173 4 168 4 158C2 110 5 60 3 18"
           "C4 9 9 4 19 4' fill='none' stroke='#F1EBDF' stroke-opacity='.72' stroke-width='1.6' stroke-linecap='round'/></svg>"
           "<div class='pl'><div class='eco'></div><svg viewBox='0 0 60 60' aria-hidden='true'>"
           "<path class='anel' d='M31 4C46 3 57 15 56 31C55 46 43 57 29 56C14 55 4 44 4 29C5 15 16 5 33 5' fill='none' "
           "stroke='#F1EBDF' stroke-width='2.2' stroke-linecap='round'/>"
           "<path d='M24 19L42 30L24 41Z' fill='#F1EBDF'/></svg></div>"
           "<div class='dur'>VÍDEO · 0:28</div></div>"
           "<div class='lia'>"
           + "".join(f"<img class='p{i}' alt='' src='{MIDIA}/lia/card-pose-{i}.webp'/>" for i in (1, 2, 3))
           + "</div><div class='leg'>a Lia apresenta o painel</div></div>"
           if casca.VIDEOS_LIA else "")
        + 
        "<div class='mapa-rotulo' aria-hidden='true'><span class='t1'>1º turno · 4 de outubro</span>"
        "<span class='t2'>2º turno · 25 de outubro</span></div>"
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
        Visual(P, lib.visual_botao("T00_Capa_Comecar", 1792, 584, 100, 60, lib.acao_bookmark(f"{roteiro.TELAS[1].codigo}_CHEGADA_01"),
                                   dica=f"Começar: {roteiro.TELAS[1].numero} · {roteiro.TELAS[1].nome}",
                                   z=lib.CAMADAS["acao"], tab=110, realce=C["creme"],
                                   raio=30, realce_transp=(92, 86))),
    ]
