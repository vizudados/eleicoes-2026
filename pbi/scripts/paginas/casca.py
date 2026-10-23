# -*- coding: utf-8 -*-
"""Casca das 24 telas (dono: main). Para cada tela de roteiro.TELAS declara:

  T<nn>                    a página 1920 × 1080 (FitToPage), fundo papel #F1EBDF (tinta #1C1915 na capa e no fim)
  T<nn>_Casca_Fundo        HTML Content do tamanho da página, atrás de tudo (z 10): o desenho fixo da tela no
                           bodyTemplate — a urna em traço, "NN · NOME" e a pergunta (surgem ao abrir a página), as setas,
                           o "i", o lockup Vizu e a linha de fonte no rodapé. Sem dado: o conteúdo é [Casca · vazio]
  T<nn>_Casca_Anterior/Proxima   botões transparentes sobre as setas (realce redondo no hover)
  T<nn>_Casca_Inicio       botão sobre a urna: volta à capa
  T<nn>_Casca_InfoAbre/Fecha     o "i" abre o cartão de leitura da tela (T<nn>_Leitura, oculto), o × fecha
  T<nn>_Casca_Filtro       VizuFilter de UF (sincronizado entre as telas que o têm) ou de município, só onde a tela tem
                           filtro (roteiro.Tela.filtro)
  T<nn>_CHEGADA_01         marcador de chegada (L095): toda navegação passa por ele e a tela abre com a leitura fechada
  T<nn>_LEITURA_ABRE_01 / _FECHA_01   marcadores só de exibição da leitura

O texto da leitura de cada tela vem de leituras.py (Como ler · De onde vêm os números · Para lembrar).
"""
from __future__ import annotations

import html

import estilo
import leituras
import pbip_lib as lib
import roteiro
from pbip_lib import Bookmark, Pagina, Visual

CSS = "Estilo · CSS"
VAZIO = "Casca · vazio"
FILTRO = (1282, 60, 424, 48)
INFO = (1724, 62, 44, 44)
SETA_ESQ = (36, 500, 80, 80)
SETA_DIR = (1804, 500, 80, 80)
URNA = (40, 40, 92, 92)
LEITURA = (1180, 124, 600, 780)
FECHAR = (1724, 140, 40, 40)        # o × desenhado no canto do cartão de leitura
GRUPO_UF = "Eleicoes_UF"
Z = {"fundo": 10, "leitura": lib.CAMADAS["leitura"], "filtro": lib.CAMADAS["drawer"],
     "nav": lib.CAMADAS["navegacao"]}


def _tom(t: roteiro.Tela) -> dict:
    c = estilo.COR
    if t.escura:
        return {"fundo": c["tinta"], "texto": c["creme"], "sob": c["areia"], "linha": c["areia"], "logo": c["areia"],
                "urna": "arte/limpos/urna-creme.png", "realce": c["creme"]}
    return {"fundo": c["papel"], "texto": c["tinta"], "sob": c["grafite"], "linha": c["grafite"], "logo": c["marrom"],
            "urna": "arte/limpos/urna.png", "realce": c["tinta"]}


def _seta(direcao: str, cor: str) -> str:
    d = "M52 40 H28 M38 30 L28 40 L38 50" if direcao == "esq" else "M28 40 H52 M42 30 L52 40 L42 50"
    return (f"<svg width='80' height='80' viewBox='0 0 80 80'><path d='{d}' fill='none' stroke='{cor}' "
            f"stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/></svg>")


def corpo_casca(t: roteiro.Tela) -> str:
    """bodyTemplate da casca: desenho fixo da tela, com {{content}} no fim (o HTML Content exige o marcador)."""
    k = _tom(t)
    ant, prox = roteiro.anterior(t), roteiro.proxima(t)
    e = html.escape
    css = (
        f".cs{{position:fixed;inset:0;color:{k['texto']}}}"
        ".cs .urna{position:absolute;left:52px;top:50px;width:60px;opacity:.95}"
        ".cs .cab{position:absolute;left:150px;top:46px;right:660px}"
        f".cs .cab .sob{{color:{k['sob']}}}"
        f".cs .cab .tit{{margin-top:8px;color:{k['texto']};font-size:31px}}"
        ".cs .seta{position:absolute;top:500px;width:80px;height:80px}"
        ".cs .seta.e{left:36px}.cs .seta.d{left:1804px}"
        f".cs .info{{position:absolute;left:1730px;top:68px;width:32px;height:32px;border:1.6px solid {k['linha']};"
        f"border-radius:50%;font-size:16px;font-weight:600;text-align:center;line-height:29px;color:{k['texto']}}}"
        ".cs .pe{position:absolute;left:150px;right:150px;top:1014px;height:28px;display:flex;align-items:center;"
        "justify-content:space-between}"
        f".cs .pe .fonte{{font-size:13px;color:{k['sob']};letter-spacing:.01em}}"
        f".cs .logo{{color:{k['logo']}}}"
    )
    setas = ""
    if ant:
        setas += f"<div class='seta e' title='{e(ant.titulo_pagina)}'>{_seta('esq', k['linha'])}</div>"
    if prox:
        setas += f"<div class='seta d' title='{e(prox.titulo_pagina)}'>{_seta('dir', k['linha'])}</div>"
    cab = ""
    if t.codigo not in ("T00", "T23"):          # capa e encerramento desenham o próprio título
        cab = (f"<div class='cab'><div class='sob sobe'>{e(t.numero)} · {e(t.nome)}</div>"
               f"<div class='tit sobe d2'>{e(t.pergunta)}</div></div>")
    return (f"<style>{css}</style><div class='cs'>"
            f"<img class='urna entra' alt='' src='{estilo.imagem_b64(k['urna'], 120)}'/>{cab}{setas}"
            f"<div class='info'>i</div>"
            f"<div class='pe'><span class='logo'>{estilo.logo_vizu(k['logo'])}</span>"
            f"<span class='fonte'>{e(t.fonte)}</span></div></div>{{{{content}}}}")


def corpo_leitura(t: roteiro.Tela) -> str:
    """Cartão de leitura (o "i"): papel com orelha, título, três blocos e o × no canto."""
    k = _tom(t)
    c = estilo.COR
    texto = leituras.LEITURAS.get(t.codigo) or leituras.padrao(t)
    e = html.escape
    blocos = "".join(
        f"<div class='bl sobe d{i + 2}'><div class='rot'>{e(r)}</div><div class='txt'>{e(p)}</div></div>"
        for i, (r, p) in enumerate(texto["blocos"]))
    papel, tinta = (c["papel"], c["tinta"]) if not t.escura else (c["creme"], c["tinta"])
    css = (
        f".lt{{position:fixed;inset:0;background:{papel};color:{tinta};padding:36px 40px 32px 40px;"
        f"border:1.5px solid {c['areia']};box-shadow:0 18px 40px rgba(28,25,21,.18);"
        "clip-path:polygon(0 0,calc(100% - 46px) 0,100% 46px,100% 100%,0 100%)}"
        f".lt .orelha{{position:absolute;right:0;top:0;width:46px;height:46px;background:{c['creme']};"
        f"border-left:1.5px solid {c['areia']};border-bottom:1.5px solid {c['areia']}}}"
        ".lt .x{position:absolute;right:56px;top:16px;font-size:26px;line-height:1;color:var(--grafite)}"
        ".lt .ast{font-family:var(--mao);font-size:30px;color:var(--vermelho-escuro);margin-right:8px}"
        ".lt .tt{font-size:24px;font-weight:600;margin:0 0 22px 0;padding-right:60px}"
        ".lt .bl{margin-bottom:20px}.lt .bl .rot{margin-bottom:6px}.lt .bl .txt{font-size:16px;color:var(--tinta)}"
    )
    return (f"<style>{css}</style><div class='lt'><div class='orelha'></div><div class='x'>×</div>"
            f"<div class='tt sobe'><span class='ast'>*</span>{e(texto['titulo'])}</div>{blocos}</div>{{{{content}}}}")


def _pagina(t: roteiro.Tela) -> dict:
    cor = _tom(t)["fundo"]
    return {"$schema": lib.ESQUEMA["pagina"], "name": t.codigo, "displayName": t.titulo_pagina,
            "displayOption": "FitToPage", "width": lib.LARGURA, "height": lib.ALTURA,
            "objects": {"background": [{"properties": {"color": lib.cor(cor), "transparency": lib.lit(0)}}],
                        "outspace": [{"properties": {"color": lib.cor(cor), "transparency": lib.lit(0)}}]}}


def _estilo_filtro(t: roteiro.Tela) -> dict:
    c = estilo.COR
    comum = {"fontSize": 16, "optionFontSize": 16, "fontFamily": "Sora Vizu, Segoe UI",
             "enableHoverAnimations": False, "showShadow": True, "counterBadgeRadius": 0, "triggerIcon": "funnel",
             "triggerIconSize": 16, "triggerIconActive": "filledDot", "triggerIconDotColor": c["vermelho"]}
    return {**comum, "textColor": c["tinta"], "backgroundColor": c["creme"], "dropdownBackgroundColor": c["branco"],
            "selectedBackgroundColor": c["creme"], "hoverBackgroundColor": c["papel"], "hoverTextColor": c["tinta"],
            "borderColor": c["areia"], "activeBorderColor": c["tinta"], "checkboxColor": c["tinta"],
            "checkboxMarkColor": c["tinta"], "checkboxBorderColor": c["areia"], "counterBackgroundColor": c["tinta"],
            "counterTextColor": c["papel"], "clearActionColor": c["tinta"], "mutedTextColor": c["cinza"],
            "dividerColor": c["creme"], "scrollbarThumbColor": c["areia"], "categorySearchBackgroundColor": c["branco"],
            "triggerIconColor": c["grafite"]}


def _filtro(t: roteiro.Tela) -> list:
    x, y, w, h = FILTRO
    layout = {"controlWidth": w, "controlHeight": h, "dropdownWidth": w, "dropdownHeight": 560, "gap": 6,
              "optionHeight": 40, "searchHeight": 44, "triggerIconGap": 12, "borderRadius": 6, "checkboxSize": 14,
              "checkboxRadius": 2, "scrollbarWidth": 4, "wrapOptionLabels": False}
    if t.filtro == "UF":
        geral = {"mode": "dropdown", "singleSelect": True, "singleSelectAllowAll": True, "sortAscending": True,
                 "startOpen": False, "alwaysOpen": False, "showSearch": True, "showSelectAll": False,
                 "showReset": False, "showSelectedCount": False, "showSelectedValue": True,
                 "selectedValueOnly": True, "syncSelectionWithHost": True, "triggerMode": "value",
                 "triggerLabel": "UF", "placeholderText": "Todo o Brasil", "allOptionText": "Todo o Brasil",
                 "searchPlaceholder": "Buscar estado", "searchScope": "list", "pathMode": False}
        extras = {"groupHeaders": True, "groupHeaderFontSize": 13, "groupHeaderHeight": 30, "groupHeaderBold": True,
                  "groupHeaderUppercase": True, "groupHeaderColor": estilo.COR["cinza"], "sortDirection": "asc"}
        recorte = lib.filtro_visual_categorico("ufSemExterior", "UF", "Tipo", ["UF"])
        for f in recorte["filters"]:
            f["isHiddenInViewMode"] = True
            f["isLockedInViewMode"] = True
        return [Visual(t.codigo, lib.visual_vizufilter(
            f"{t.codigo}_Casca_Filtro", x, y, w, h, categoria=("UF", "Nome", "Estado"), geral=geral, layout=layout,
            estilo=_estilo_filtro(t), alt=lib.medida("Casca · filtro · ALT"), z=Z["filtro"], tab=5,
            sincronia=lib.grupo_sincronia(GRUPO_UF), filtros=recorte,
            medidas={"itemGroup": "Casca · filtro · região", "itemSort": "Casca · filtro · ordem"}, extras=extras))]
    return []                     # município (T15) e local (T20) são declarados pelas próprias telas


def _botao(t: roteiro.Tela, nome: str, caixa: tuple, acao: tuple, dica: str, tab: int, **extra) -> Visual:
    k = _tom(t)
    args = dict(dica=dica, z=Z["nav"], tab=tab, realce=k["realce"], raio=40, realce_transp=(90, 82))
    args.update(extra)
    return Visual(t.codigo, lib.visual_botao(f"{t.codigo}_Casca_{nome}", *caixa, acao, **args))


def declarar(ctx):
    itens = []
    for i, t in enumerate(roteiro.TELAS):
        p = t.codigo
        itens.append(Pagina(_pagina(t), ordem=i))
        itens.append(Visual(p, lib.visual_html(
            f"{p}_Casca_Fundo", 0, 0, lib.LARGURA, lib.ALTURA, VAZIO, folha_de_estilo=CSS, modelo_corpo=corpo_casca(t),
            alt=f"{t.numero} · {t.nome}: {t.pergunta}", z=Z["fundo"], tab=1, movimento=False)))
        ant, prox = roteiro.anterior(t), roteiro.proxima(t)
        if ant:
            itens.append(_botao(t, "Anterior", SETA_ESQ, lib.acao_bookmark(f"{ant.codigo}_CHEGADA_01"),
                                f"Voltar: {ant.titulo_pagina}", 900))
        if prox:
            itens.append(_botao(t, "Proxima", SETA_DIR, lib.acao_bookmark(f"{prox.codigo}_CHEGADA_01"),
                                f"Próxima: {prox.titulo_pagina} — {prox.pergunta}", 901))
        if p != "T00":
            itens.append(_botao(t, "Inicio", URNA, lib.acao_bookmark("T00_CHEGADA_01"), "Voltar à capa", 2))
        # leitura da tela (o "i")
        itens.append(Visual(p, lib.visual_html(
            f"{p}_Casca_Leitura", *LEITURA, VAZIO, folha_de_estilo=CSS, modelo_corpo=corpo_leitura(t),
            alt=f"Como ler a tela {t.numero} · {t.nome}", z=Z["leitura"], tab=950, oculto=True, movimento=False)))
        itens.append(_botao(t, "InfoAbre", INFO, lib.acao_bookmark(f"{p}_LEITURA_ABRE_01"),
                            "Como ler esta tela e de onde vêm os números", 6))
        itens.append(_botao(t, "InfoFecha", FECHAR, lib.acao_bookmark(f"{p}_LEITURA_FECHA_01"), "Fechar a leitura",
                            951, oculto=True, raio=20))
        aberta = {f"{p}_Casca_Leitura": True, f"{p}_Casca_InfoFecha": True, f"{p}_Casca_InfoAbre": False}
        fechada = {f"{p}_Casca_Leitura": False, f"{p}_Casca_InfoFecha": False, f"{p}_Casca_InfoAbre": True}
        itens.append(Bookmark(lib.bookmark_exibicao(f"{p}_LEITURA_ABRE_01", p, aberta, titulo=f"{p} · leitura aberta"),
                              grupo=("Leituras", "Leituras")))
        itens.append(Bookmark(lib.bookmark_exibicao(f"{p}_LEITURA_FECHA_01", p, fechada,
                                                    titulo=f"{p} · leitura fechada"), grupo=("Leituras", "Leituras")))
        itens.append(Bookmark(lib.bookmark_chegada(f"{p}_CHEGADA_01", p, fechada, titulo=f"Chegada · {t.titulo_pagina}"),
                              grupo=("Chegadas", "Chegadas")))
        itens += _filtro(t)
    return itens
