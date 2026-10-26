# -*- coding: utf-8 -*-
"""Casca das 24 telas (dono: main). Para cada tela de roteiro.TELAS declara:

  T<nn>                    a página 1920 × 1080 (FitToPage), fundo papel #F1EBDF (tinta #1C1915 na capa e no fim)
  T<nn>_Casca_Fundo        HTML Content do tamanho da página, atrás de tudo (z 10): o desenho fixo da tela no
                           bodyTemplate — a urna em traço, "NN · NOME" e a pergunta (surgem ao abrir a página), as setas,
                           o "i", o lockup Vizu e a linha de fonte no rodapé. Sem dado: o conteúdo é [Casca · vazio]
  T<nn>_Casca_Anterior/Proxima   botões transparentes sobre as setas (realce redondo no hover)
  T<nn>_Casca_Inicio       botão sobre a urna: abre o sumário (paginas/tix_sumario.py)
  T<nn>_Casca_InfoAbre/Fecha     o "i" abre o cartão de leitura da tela (T<nn>_Leitura, oculto), o × fecha
  T<nn>_Casca_Filtro       o filtro da tela, só onde ela tem filtro (roteiro.Tela.filtro): VizuFilter visível com o
                           gatilho dele (abre e fecha a lista sozinho; sem pílula, botão, véu nem marcador, 24/10/2026),
                           ATRÁS do conteúdo (z 20, lib.CAMADAS["filtro"]): de estado, em árvore Região › Estado sobre
                           'UF'[Caminho] (sincronizado entre as telas que o têm), ou de período (Buscas, Redes e 2º
                           turno, sincronizado entre as três; tabela 'Período', 23/10/2026)
  T<nn>_CHEGADA_01         marcador de chegada (L095): toda navegação passa por ele e a tela abre com a leitura fechada
  T<nn>_LEITURA_ABRE_01 / _FECHA_01   marcadores só de exibição da leitura

O texto da leitura de cada tela vem de leituras.py (Como ler · De onde vêm os números · Para lembrar).
"""
from __future__ import annotations

import html
import math

import estilo
import leituras
import pbip_lib as lib
import roteiro
import momento_eleicao
from pbip_lib import Bookmark, Pagina, Visual

CSS = "Estilo · CSS"
VAZIO = "Casca · vazio"
# O VizuFilter é um visual próprio: a lista abre dentro da caixa dele, então a caixa vai até onde a lista desce. Ele
# é o próprio filtro, com o gatilho dele (24/10/2026, pedido do dono: "eu pedi que o filtro não fosse um botão que ativa
# ao clicar"; a pílula HTML, o botão, o véu e os marcadores de abrir e fechar saíram): fica ATRÁS do conteúdo
# (lib.CAMADAS["filtro"], acima só do fundo da casca), e os gráficos por cima da caixa seguem com o mouse ("a solução
# devia ser colocar ele pra trás na hierarquia de elementos"). O gatilho (1282–1706, 60–108) fica numa faixa sem visual
# por cima; o clique traz o filtro para a frente e a lista abre por cima de tudo.
# Estado: árvore Região › Estado (24/10/2026, regra L134: "se resolve a questão da hierarquia jogando o filtro no último
# na hierarquia"), 'UF'[Caminho]. Aberta: a busca, o Limpar, as 5 regiões e os 9 estados do Nordeste sem rolar.
FILTRO = (1282, 60, 424, 720)
FILTRO_GATILHO = 48
# o de período tem 5 itens (o 2º turno inteiro e os quatro períodos): a caixa desce só até onde a lista vai
FILTRO_PERIODO = (1282, 60, 424, 270)
# as telas com filtro próprio (T15 município, T19 recorte, T20 local) seguem o mesmo padrão: VizuFilter visível, atrás
# do conteúdo (lib.CAMADAS["filtro"]), nesta mesma caixa, com o gatilho dele
INFO = (1724, 62, 44, 44)
SETA_ESQ = (36, 500, 80, 80)
SETA_DIR = (1804, 500, 80, 80)
URNA = (40, 40, 92, 92)
LEITURA = (1180, 124, 600)          # x, y, largura; a altura sai do texto de cada tela (_altura_leitura)
TOPO_CARTAO = 14                     # o cartão começa 14 px abaixo do topo do visual (a fita fica por cima)
FECHAR = (1724, 124 + TOPO_CARTAO + 14, 40, 40)   # o × desenhado no canto do cartão: 16 px da direita, 14 do topo
FORA = (0, 0, 1920, 1080)            # véu da leitura aberta: clicar fora do cartão também fecha
GRUPO_UF = "Eleicoes_UF"
GRUPO_PERIODO = "Eleicoes_Periodo"
Z = {"fundo": 10, "filtro": lib.CAMADAS["filtro"], "leitura": lib.CAMADAS["leitura"], "nav": lib.CAMADAS["navegacao"]}


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
        f".cs{{color:{k['texto']}}}"
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
    return (f"<style>{css}</style><div class='cs tela'>"
            f"<img class='urna entra' alt='' src='{estilo.imagem_b64(k['urna'], 120)}'/>{cab}{setas}"
            f"<div class='info'>i</div>"
            f"<div class='pe'><span class='logo'>{estilo.logo_vizu(k['logo'])}</span>"
            f"<span class='fonte'>{e(momento_eleicao.fonte(t))}</span></div></div>{{{{content}}}}")


def _texto_leitura(t: roteiro.Tela) -> dict:
    return leituras.LEITURAS.get(t.codigo) or leituras.padrao(t)


def _linhas(texto: str, por_linha: int) -> int:
    return max(1, math.ceil(len(texto) / por_linha))


def _altura_leitura(t: roteiro.Tela) -> int:
    """Altura do visual da leitura: o cartão cresce com o texto (Sora 16 px em 520 px ≈ 58 caracteres por linha; título
    24 px em 460 px ≈ 32), com folga de 24 px; assim a caixa transparente embaixo do cartão quase não sobra."""
    texto = _texto_leitura(t)
    h = TOPO_CARTAO + 40 + _linhas(texto["titulo"], 32) * 31 + 22
    h += sum(17 + 6 + _linhas(p, 58) * 23 + 20 for _, p in texto["blocos"])
    return int(min(880, h + 32 + 24))


def corpo_leitura(t: roteiro.Tela) -> str:
    """Cartão de leitura (o "i"): papel do tamanho do texto, fita no topo, título, três blocos e o × num círculo no
    canto, exatamente sobre o botão que fecha (FECHAR)."""
    c = estilo.COR
    texto = _texto_leitura(t)
    e = html.escape
    blocos = "".join(
        f"<div class='bl sobe d{i + 2}'><div class='rot'>{e(r)}</div><div class='txt'>{e(p)}</div></div>"
        for i, (r, p) in enumerate(texto["blocos"]))
    papel, tinta = (c["papel"], c["tinta"]) if not t.escura else (c["creme"], c["tinta"])
    css = (
        f".lt{{position:absolute;left:0;top:{TOPO_CARTAO}px;width:{LEITURA[2]}px;background:{papel};color:{tinta};"
        f"padding:40px 40px 32px 40px;border:1.5px solid {c['areia']};box-shadow:0 18px 40px rgba(28,25,21,.22)}}"
        f".lt .fita{{position:absolute;left:230px;top:-{TOPO_CARTAO}px;width:140px;height:26px;background:{c['areia']};"
        "opacity:.8;transform:rotate(-2deg)}"
        f".lt .x{{position:absolute;right:16px;top:14px;width:40px;height:40px;border-radius:20px;border:1.5px solid "
        f"{c['areia']};display:flex;align-items:center;justify-content:center;font-size:22px;line-height:1;"
        f"color:{c['grafite']}}}"
        ".lt .ast{font-family:var(--mao);font-size:30px;color:var(--vermelho-escuro);margin-right:8px}"
        ".lt .tt{font-size:24px;font-weight:600;margin:0 0 22px 0;padding-right:50px}"
        ".lt .bl{margin-bottom:20px}.lt .bl:last-child{margin-bottom:0}.lt .bl .rot{margin-bottom:6px}"
        ".lt .bl .txt{font-size:16px;color:var(--tinta)}"
    )
    return (f"<style>{css}</style><div class='tela'><div class='lt'><div class='fita'></div><div class='x'>×</div>"
            f"<div class='tt sobe'><span class='ast'>*</span>{e(texto['titulo'])}</div>{blocos}</div></div>"
            "{{content}}")


def _pagina(t: roteiro.Tela) -> dict:
    cor = _tom(t)["fundo"]
    return {"$schema": lib.ESQUEMA["pagina"], "name": t.codigo, "displayName": t.titulo_pagina,
            "displayOption": "FitToPage", "width": lib.LARGURA, "height": lib.ALTURA,
            "objects": {"background": [{"properties": {"color": lib.cor(cor), "transparency": lib.lit(0)}}],
                        "outspace": [{"properties": {"color": lib.cor(cor), "transparency": lib.lit(0)}}]}}


def _estilo_filtro(t: roteiro.Tela) -> dict:
    """Tokens do VizuFilter da casa. O gatilho é o funil que ganha o ponto vermelho quando há escolha (24/10/2026, o
    dono: "pode manter isso como recurso do vizu filter"): triggerIcon funnel, triggerIconActive filledDot, ponto no
    vermelho da casa e funil em grafite, em TODOS os filtros (estado, período, município da T15, local da T20 e T19)."""
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


def layout_filtro(caixa: tuple, **extra) -> dict:
    """layout do VizuFilter na caixa: o gatilho com a altura de sempre (48 px) e a lista com o resto da caixa (L028: a
    altura da caixa nunca vai para controlHeight)."""
    _x, _y, w, h = caixa
    base = {"controlWidth": w, "controlHeight": FILTRO_GATILHO, "dropdownWidth": w,
            "dropdownHeight": h - FILTRO_GATILHO - 6, "gap": 6, "optionHeight": 40, "searchHeight": 44,
            "triggerIconGap": 12, "borderRadius": 6, "checkboxSize": 14, "checkboxRadius": 2, "scrollbarWidth": 4,
            "wrapOptionLabels": False}
    base.update(extra)
    return base


def _filtro(t: roteiro.Tela) -> list:
    """O filtro da tela: o próprio VizuFilter, visível, atrás do conteúdo, que abre e fecha a lista sozinho (sem
    pílula, botão, véu nem marcador). Recolhido ao chegar (alwaysOpen e startOpen desligados)."""
    p = t.codigo
    if t.filtro == "Período":
        # um filtro só para as três telas (sincronia entre páginas); sem escolha = o 2º turno inteiro, a tela de sempre
        caixa = FILTRO_PERIODO
        geral = {"mode": "dropdown", "singleSelect": True, "singleSelectAllowAll": True, "sortAscending": True,
                 "startOpen": False, "alwaysOpen": False, "showSearch": False, "showSelectAll": False,
                 "showReset": False, "showSelectedCount": False, "showSelectedValue": True,
                 "selectedValueOnly": True, "syncSelectionWithHost": True, "triggerMode": "value",
                 "triggerLabel": "Período", "placeholderText": "2º turno inteiro", "allOptionText": "2º turno inteiro",
                 "searchPlaceholder": "Buscar período", "searchScope": "list", "pathMode": False}
        doc = lib.visual_vizufilter(
            f"{p}_Casca_Filtro", *caixa, categoria=("Período", "Período", "Período"), geral=geral,
            layout=layout_filtro(caixa), estilo=_estilo_filtro(t), alt=lib.medida("Casca · período · ALT"),
            z=Z["filtro"], tab=4, sincronia=lib.grupo_sincronia(GRUPO_PERIODO),
            medidas={"itemSort": "Casca · período · ordem"}, extras={"sortDirection": "asc"})
        return [Visual(p, doc)]
    if t.filtro == "UF":
        # árvore Região › Estado ('UF'[Caminho]): marcar a região marca os estados dela; um estado, uma região
        # inteira ou vários estados soltos, de uma ou mais regiões (o texto do recorte lê a escolha de cima para
        # baixo: medidas Recorte · …, pbi/scripts/desenho_recorte.py). As regiões são linhas da árvore, com caixa de
        # marcar e seta própria (abrem e fecham cada uma por si, sem acordeão); a busca única fica no topo. O gatilho
        # resume a escolha do mesmo jeito (VizuFilter 2.14, triggerPathSummary): "Nordeste", "Bahia", "Minas Gerais
        # e São Paulo", "5 estados". Ordem da árvore: Norte → Sul e o nome (itemSort = 'UF'[Ordem]).
        caixa = FILTRO
        geral = {"mode": "dropdown", "pathMode": True, "pathSeparator": " › ", "listLayout": "standard",
                 "treeCategoryHeader": False, "singleSelect": False, "sortAscending": False, "startOpen": False,
                 "alwaysOpen": False, "showSearch": True, "searchScope": "list",
                 "searchPlaceholder": "Buscar região ou estado", "showSelectAll": False, "showReset": True,
                 "showSelectedCount": False, "showSelectedValue": True, "selectedValueOnly": True,
                 "syncSelectionWithHost": True, "triggerMode": "value", "triggerLabel": "Estado",
                 "placeholderText": "Todo o Brasil", "triggerPathSummary": True, "triggerPathSummaryMax": 2,
                 "triggerPathSummaryNoun": "estado|estados"}
        recorte = lib.filtro_visual_categorico("ufSemExterior", "UF", "Tipo", ["UF"])
        for f in recorte["filters"]:
            f["isHiddenInViewMode"] = True
            f["isLockedInViewMode"] = True
        doc = lib.visual_vizufilter(
            f"{p}_Casca_Filtro", *caixa, categoria=("UF", "Caminho", "Estado"), geral=geral,
            layout=layout_filtro(caixa), estilo=_estilo_filtro(t), alt=lib.medida("Casca · filtro · ALT"),
            z=Z["filtro"], tab=4, sincronia=lib.grupo_sincronia(GRUPO_UF), filtros=recorte,
            medidas={"itemSort": "Casca · filtro · ordem"}, extras={"sortDirection": "asc"})
        return [Visual(p, doc)]
    return []                     # município (T15), recorte (T19) e local (T20) são declarados pelas próprias telas


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
            itens.append(_botao(t, "Inicio", URNA, lib.acao_bookmark("TIX_CHEGADA_01"), "Sumário: todas as telas", 2))
        # leitura da tela (o "i")
        itens.append(Visual(p, lib.visual_html(
            f"{p}_Casca_Leitura", *LEITURA, _altura_leitura(t), VAZIO, folha_de_estilo=CSS,
            modelo_corpo=corpo_leitura(t), alt=f"Como ler a tela {t.numero} · {t.nome}", z=Z["leitura"], tab=950,
            oculto=True, movimento=False)))
        itens.append(_botao(t, "InfoAbre", INFO, lib.acao_bookmark(f"{p}_LEITURA_ABRE_01"),
                            "Como ler esta tela e de onde vêm os números", 6))
        itens.append(_botao(t, "InfoFecha", FECHAR, lib.acao_bookmark(f"{p}_LEITURA_FECHA_01"), "Fechar a leitura",
                            951, oculto=True, raio=20))
        # véu da leitura aberta (embaixo do cartão): escurece a tela de leve e fecha a leitura no clique fora
        itens.append(_botao(t, "InfoFora", FORA, lib.acao_bookmark(f"{p}_LEITURA_FECHA_01"), "Fechar a leitura",
                            949, oculto=True, raio=0, z=Z["leitura"] - 10, realce=None,
                            fundo=(estilo.COR["tinta"], 86)))
        aberta = {f"{p}_Casca_Leitura": True, f"{p}_Casca_InfoFecha": True, f"{p}_Casca_InfoFora": True,
                  f"{p}_Casca_InfoAbre": False}
        fechada = {f"{p}_Casca_Leitura": False, f"{p}_Casca_InfoFecha": False, f"{p}_Casca_InfoFora": False,
                   f"{p}_Casca_InfoAbre": True}
        itens.append(Bookmark(lib.bookmark_exibicao(f"{p}_LEITURA_ABRE_01", p, aberta, titulo=f"{p} · leitura aberta"),
                              grupo=("Leituras", "Leituras")))
        itens.append(Bookmark(lib.bookmark_exibicao(f"{p}_LEITURA_FECHA_01", p, fechada,
                                                    titulo=f"{p} · leitura fechada"), grupo=("Leituras", "Leituras")))
        itens.append(Bookmark(lib.bookmark_chegada(f"{p}_CHEGADA_01", p, fechada, titulo=f"Chegada · {t.titulo_pagina}"),
                              grupo=("Chegadas", "Chegadas")))
        itens += _filtro(t)
        # Um único grupo Antes/Depois, sem interferir nos filtros existentes.
        if p in momento_eleicao.TELAS:
            itens.append(momento_eleicao.filtro(t))
    return itens
