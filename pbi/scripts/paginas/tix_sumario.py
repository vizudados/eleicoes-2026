# -*- coding: utf-8 -*-
"""Sumário — as telas por ato, cada uma clicável (dono: main). Página fora da sequência das setas: a urna do canto
de cada tela abre o sumário, e a capa tem o atalho "sumário".

  TIX_Sumario_Html   o título, os atos em colunas (número, nome e a pergunta de cada tela), o rodapé da casa
  TIX_Sumario_Ir<NN> um botão transparente por tela (vai ao marcador de chegada dela)
  TIX_Sumario_Voltar a urna: volta à capa
  TIX_CHEGADA_01     marcador de chegada do sumário (as urnas de todas as telas apontam para ele)
"""
from __future__ import annotations

import html
from functools import lru_cache

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

import estilo
import pbip_lib as lib
import roteiro
from pbip_lib import Bookmark, Pagina, Visual

P = "TIX"
CSS = "Estilo · CSS"
C = estilo.COR

# colunas do sumário: (rótulo, códigos)
COLUNAS = [
    ("ABERTURA · I · ANTES DA URNA", ["T00", "T02", "T04", "T10"]),
    ("II · O 1º TURNO", ["T01", "T03", "T05", "T06", "T25"]),
    ("III · O MAPA", ["T11", "T12", "T13", "T24", "T14", "T15"]),
    ("IV · EXPLORE VOCÊ MESMO", ["T19", "T20", "T21", "T22"]),
    ("V · O 2º TURNO · FIM", ["T16", "T17", "T07", "T26", "T08", "T09", "T18", "T27", "T28", "T29", "T23"]),
]
X0, Y0, LARGURA_COL, VAO = 150, 172, 304, 25


# Um item: respiro de 10 px, o nome (19 px, ~23 de linha), 6 px, a pergunta em Sora 14 px (19 px por linha) e 5 px
# até o traço. A pergunta que não cabe em uma linha ganha a segunda, e o item cresce (26/10/2026: a segunda linha
# atravessava o traço e, na coluna V, encostava no item de baixo).
TOPO_ITEM, LINHA_PERGUNTA, PE_ITEM = 39, 19, 5
VAO_ITEM, FIM_COLUNAS = 10, 996          # vão entre itens (aperta na coluna cheia) e o limite acima do rodapé


@lru_cache(maxsize=1)
def _sora_14():
    """Avanço de cada caractere da Sora 400 a 14 px (a fonte da pergunta)."""
    fonte = instancer.instantiateVariableFont(TTFont(estilo.FONTES / "sora-wght.ttf"), {"wght": 400})
    escala = 14 / fonte["head"].unitsPerEm
    mapa, hmtx = fonte.getBestCmap(), fonte["hmtx"]
    return lambda ch: hmtx[mapa.get(ord(ch), mapa[ord("n")])][0] * escala


def _linhas_pergunta(texto: str) -> int:
    """Quantas linhas a pergunta ocupa na largura da coluna (quebra por palavra; "º turno" não se separa)."""
    largura = _sora_14()
    linhas, atual = 1, 0.0
    for palavra in texto.replace("º turno", "º turno").split(" "):
        w = sum(largura(ch) for ch in palavra)
        espaco = largura(" ") if atual else 0
        if atual and atual + espaco + w > LARGURA_COL - 2:
            linhas, atual = linhas + 1, w
        else:
            atual += espaco + w
    return linhas


def _itens():
    """[(código, x, y, altura)] de cada tela no desenho (o botão usa a mesma caixa)."""
    saida = []
    for i, (_, cods) in enumerate(COLUNAS):
        x = X0 + i * (LARGURA_COL + VAO)
        alturas = [TOPO_ITEM + _linhas_pergunta(roteiro.POR_CODIGO[c].pergunta) * LINHA_PERGUNTA + PE_ITEM for c in cods]
        y0 = Y0 + 44
        vao = VAO_ITEM if len(cods) < 2 else min(VAO_ITEM, (FIM_COLUNAS - y0 - sum(alturas)) / (len(cods) - 1))
        if vao < 2:
            raise ValueError(f"a coluna {i + 1} do sumário não cabe acima do rodapé (vão de {vao:.1f} px)")
        y = y0
        for cod, h in zip(cods, alturas):
            saida.append((cod, x, round(y), h))
            y += h + vao
    return saida


def corpo() -> str:
    e = html.escape
    css = (
        ".sm .cab{position:absolute;left:150px;top:46px}"
        ".sm .cab .tit{margin-top:8px}"
        ".sm .col{position:absolute;width:" + str(LARGURA_COL) + "px}"
        f".sm .col .rot{{height:30px;border-bottom:1.5px solid {C['tinta']};color:{C['tinta']}}}"
        f".sm .it{{position:absolute;left:0;width:{LARGURA_COL}px;box-sizing:border-box;padding:10px 0 0 0;"
        f"border-bottom:1px solid {C['areia']}}}"
        ".sm .it b{font-size:15px;font-weight:700;color:var(--cinza);margin-right:10px;font-variant-numeric:tabular-nums}"
        ".sm .it .nm{font-size:19px;font-weight:600}"
        ".sm .it .pg{font-size:14px;color:var(--grafite);margin-top:6px;line-height:1.35}"
        f".sm .pe{{position:absolute;left:150px;right:150px;top:1014px;height:28px;display:flex;align-items:center;"
        f"justify-content:space-between;color:{C['marrom']}}}"
        ".sm .pe .fonte{font-size:13px;color:var(--grafite)}"
    )
    partes = []
    k = 0
    for i, (rotulo, cods) in enumerate(COLUNAS):
        x = X0 + i * (LARGURA_COL + VAO)
        partes.append(f"<div class='col' style='left:{x}px;top:{Y0}px'><div class='rot sobe d{i + 1}'>{e(rotulo)}</div></div>")
    for cod, x, y, altura in _itens():
        t = roteiro.POR_CODIGO[cod]
        k += 1
        partes.append(f"<div class='it sobe d{min(16, 2 + k // 2)}' style='left:{x}px;top:{y}px;height:{altura}px'>"
                      f"<div><b>{t.numero}</b><span class='nm'>{e(t.nome)}</span></div>"
                      f"<div class='pg'>{e(t.pergunta).replace('º turno', 'º&nbsp;turno')}</div></div>")
    urna = estilo.imagem_b64("arte/limpos/urna.png", 120)
    return (
        f"<style>{css}</style><div class='tela sm'>"
        f"<img alt='' src='{urna}' style='position:absolute;left:52px;top:50px;width:60px'/>"
        f"<div class='cab'><div class='sob sobe'>SUMÁRIO</div><div class='tit sobe d1'>{len(roteiro.TELAS)} telas, "
        "cinco atos: escolha por onde começar</div></div>"
        + "".join(partes)
        + f"<div class='pe'><span>{estilo.logo_vizu(C['marrom'])}</span><span class='fonte'>Vizu Dados · dados e código "
        "em github.com/vizudados/eleicoes-2026</span></div></div>{{content}}"
    )


def declarar(ctx):
    pag = {"$schema": lib.ESQUEMA["pagina"], "name": P, "displayName": "Sumário", "displayOption": "FitToPage",
           "width": lib.LARGURA, "height": lib.ALTURA,
           "objects": {"background": [{"properties": {"color": lib.cor(C["papel"]), "transparency": lib.lit(0)}}],
                       "outspace": [{"properties": {"color": lib.cor(C["papel"]), "transparency": lib.lit(0)}}]}}
    itens = [Pagina(pag, ordem=0),          # logo depois da capa na lista de páginas
             Visual(P, lib.visual_html("TIX_Sumario_Html", 0, 0, lib.LARGURA, lib.ALTURA, "Casca · vazio",
                                       folha_de_estilo=CSS, modelo_corpo=corpo(), movimento=False,
                                       alt=f"Sumário: as {len(roteiro.TELAS)} telas do painel por ato; clique numa tela para ir até ela.",
                                       z=lib.CAMADAS["conteudo"], tab=100))]
    for cod, x, y, altura in _itens():
        t = roteiro.POR_CODIGO[cod]
        itens.append(Visual(P, lib.visual_botao(
            f"TIX_Sumario_Ir{cod[1:]}", x - 6, y, LARGURA_COL + 12, altura + 2,
            lib.acao_bookmark(f"{cod}_CHEGADA_01"), dica=f"{t.numero} · {t.nome}: {t.pergunta}",
            z=lib.CAMADAS["acao"], tab=200 + int(cod[1:]), realce=C["tinta"], realce_transp=(93, 88))))
    itens.append(Visual(P, lib.visual_botao("TIX_Sumario_Voltar", 40, 40, 92, 92, lib.acao_bookmark("T00_CHEGADA_01"),
                                            dica="Voltar à capa", z=lib.CAMADAS["navegacao"], tab=2,
                                            realce=C["tinta"], raio=40, realce_transp=(90, 82))))
    itens.append(Bookmark(lib.bookmark_chegada("TIX_CHEGADA_01", P, {"TIX_Sumario_Html": True},
                                               titulo="Chegada · Sumário"), grupo=("Chegadas", "Chegadas")))
    return itens
