# -*- coding: utf-8 -*-
"""23 · Encerramento — e o que fica desta eleição? (dono: main). Tela escura, sem filtro.

O título é "Do placar à escola." (o caminho que o painel fez); a capa abre com "O voto, de perto." Os dois substituem
"o que os números dizem", que é o título do documentário de referência (pedido do dono, 23/10/2026: nada de cópia).

  T23_Fecho_Html    o título que se sublinha à mão, os achados de cada ato (cada linha leva à tela de onde veio), a
                    urna em traço que se revela, o convite para a apuração ao vivo, fontes e créditos
  T23_Fecho_Ir<NN>  um botão transparente por achado: vai à tela (marcador de chegada)
  T23_Fecho_IrApur  o convite "domingo, 17h" vai à tela da apuração (T18)

Os achados repetem as manchetes do 1º turno (números finais do TSE de 22/10/2026), escritos aqui como texto da
apresentação: não mudam com filtro e o movimento conta cada número na entrada. Os do 2º turno seguem as pesquisas
lançadas até 24/10/2026, 12h30 (T17: 39 de 45, com 5 de Lula e 1 empate); a cada pesquisa nova, conferir contra o
modelo ([T17 · depois · pesquisas] e [T17 · depois · Flávio à frente]).
"""
from __future__ import annotations

import html

import estilo
import roteiro
import pbip_lib as lib
from pbip_lib import Visual

P = "T23"
CSS = "Estilo · CSS"
C = estilo.COR

# os grupos seguem os atos do roteiro (ordem de 23/10/2026: antes da urna, 1º turno, mapa, explore, 2º turno; o
# explore não tem achado próprio)
ACHADOS = [
    ("I · ANTES DA URNA", [("T10", "Na véspera, 13 de 18 institutos davam Lula à frente; a urna deu Flávio.")]),
    ("II · O 1º TURNO", [("T01", "Flávio terminou 2,22 mi de votos à frente de Lula."),
                         ("T06", "33,5 milhões não foram votar: 15 vezes a diferença entre os dois."),
                         ("T25", "Quem tem 70 anos ou mais falta 3,9 vezes mais que quem tem 16 ou 17.")]),
    ("III · O MAPA", [("T11", "711 municípios trocaram Lula por Flávio; nenhum fez o caminho inverso."),
                      ("T13", "Nas cidades pequenas e de renda mais alta, Lula perdeu mais terreno."),
                      ("T24", "Onde mais casas recebem Bolsa Família, Lula teve 66%; onde menos, Flávio teve 61%."),
                      ("T14", "Pela 2ª vez em seis eleições, o PT termina o 1º turno em segundo.")]),
    ("V · O 2º TURNO", [("T17", "Desde 5 de outubro, Flávio lidera 39 de 45 pesquisas do 2º turno."),
                         ("T07", "O primeiro frente a frente, na Band, não mexeu nas pesquisas."),
                         ("T26", "O último debate, na Globo em 23/10: o que se soube dele, número a número.")]),
]
# geometria da lista (o botão de cada linha segue a mesma). Com a linha da T26 (23/10/2026), a linha passou de 37 para
# 35 px e o grupo de 34 para 30: a lista mantém a altura e as fontes não descem para o rodapé.
X0, Y_ACHADOS, LINHA, GRUPO = 150, 384, 35, 30


def _linhas():
    """[(código da tela, texto, y do topo da linha)] na ordem do desenho."""
    saida, y = [], Y_ACHADOS
    for _, itens in ACHADOS:
        y += GRUPO
        for cod, texto in itens:
            saida.append((cod, texto, y))
            y += LINHA
    return saida


def _topo_fontes() -> int:
    """As fontes ficam 30 px abaixo do último achado (posição dentro de .fx, que começa em y 150)."""
    return _linhas()[-1][2] + LINHA + 30 - 150


def corpo() -> str:
    e = html.escape
    css = (
        ".fx{color:var(--creme)}"
        ".fx .tg{position:absolute;left:0;top:0;width:1000px;font-size:88px;font-weight:700;letter-spacing:-.035em;line-height:.98}"
        ".fx .tg .sub{position:relative;display:inline-block}"
        ".fx .tg svg{position:absolute;left:-6px;bottom:-16px}"
        f".fx .ach{{position:absolute;left:0;top:{Y_ACHADOS - 150}px;width:1000px}}"
        f".fx .ach > .rot:first-child{{position:absolute;top:-30px;left:0;color:{C['areia']}}}"
        f".fx .grupo{{height:{GRUPO}px;display:flex;align-items:flex-end;padding-bottom:6px;border-bottom:1px solid "
        "rgba(203,189,162,.35)}"
        f".fx .linha{{height:{LINHA}px;display:flex;align-items:center;gap:20px;font-size:19px;font-weight:500}}"
        f".fx .linha b{{width:34px;font-size:16px;font-weight:700;color:{C['areia']}}}"
        ".fx .linha .seta{margin-left:auto;opacity:0;transition:opacity .2s}"
        f".fx .urna{{position:absolute;left:1110px;top:20px;width:470px;"
        "-webkit-mask-image:linear-gradient(100deg,#000 45%,transparent 55%);-webkit-mask-size:260% 100%;"
        "-webkit-mask-position:0 0;animation:revela 2.6s cubic-bezier(.4,0,.2,1) .4s both}"
        "@keyframes revela{from{-webkit-mask-position:100% 0}}"
        f".fx .convite{{position:absolute;left:1110px;top:560px;width:470px;border:1.5px solid {C['areia']};"
        "padding:22px 26px}"
        ".fx .convite .mao{font-size:30px;color:var(--rosa)}"
        ".fx .convite .txt{color:var(--creme);margin-top:6px}"
        ".fx .convite .ir{margin-top:14px;font-size:15px;font-weight:600;letter-spacing:.12em;color:var(--areia)}"
        f".fx .fontes{{position:absolute;left:0;top:{_topo_fontes()}px;width:1000px;font-size:13px;line-height:1.55;"
        f"color:{C['areia']}}}"
        ".fx .fontes b{color:var(--creme);font-weight:600}"
    )
    sublinhado = ("<svg width='300' height='30' viewBox='0 0 300 30'>" + estilo.defs_rabisco("rbt", 1.4)
                  + "<path d='M6 18 C 70 8, 160 6, 292 14 M30 24 C 110 16, 200 16, 270 21' pathLength='1' "
                  f"class='traco' fill='none' stroke='{C['creme']}' stroke-width='5' stroke-linecap='round' "
                  "filter='url(#rbt)' style='animation-delay:1.1s'/></svg>")
    lista = []
    i = 0
    for rotulo, itens in ACHADOS:
        lista.append(f"<div class='grupo rot sobe d{min(16, i + 3)}'>{e(rotulo)}</div>")
        for cod, texto in itens:
            i += 1
            lista.append(f"<div class='linha sobe d{min(16, i + 3)}'><b>{roteiro.numero(cod)}</b>"
                         f"<span>{e(texto)}</span></div>")
    urna = estilo.imagem_b64("arte/limpos/urna-creme.png", 940)
    return (
        f"<style>{css}</style><div class='tela fx' style='left:{X0}px;top:150px;right:150px;bottom:80px'>"
        "<div class='tg sobe'>Do placar à <span class='sub'>escola." + sublinhado + "</span></div>"
        f"<div class='ach'><div class='rot entra d2'>OS ACHADOS, POR ATO · CLIQUE PARA VOLTAR À TELA</div>{''.join(lista)}</div>"
        f"<img class='urna' alt='' src='{urna}'/>"
        "<div class='convite sobe d12'><div class='mao'>domingo, 25/10, 17h</div>"
        f"<div class='txt'>A apuração do 2º turno entra na tela {roteiro.numero('T18')}, com os números que o TSE "
        "divulga ao longo da noite.</div><div class='ir'>IR PARA A APURAÇÃO →</div></div>"
        "<div class='fontes entra d14'><b>Fontes</b> · TSE (votação, comparecimento, perfil do eleitor e API de "
        "resultados), IBGE (Censo 2022 e malhas), Portal da Transparência (Bolsa Família), Atlas do Desenvolvimento "
        "Humano (IDHM), pesquisas registradas no TSE, Google Trends, Bites, Quaest, Social "
        "Blade, Datrix, Biblioteca de Anúncios da Meta, emissoras e imprensa. <b>Desenhos</b> · em traço, a partir de "
        "fotos de licença aberta; os créditos estão em cada cartão.</div>"
        "</div>{{content}}"
    )


def declarar(ctx):
    itens = [Visual(P, lib.visual_html(
        "T23_Fecho_Html", 0, 0, lib.LARGURA, lib.ALTURA, "Casca · vazio", folha_de_estilo=CSS, modelo_corpo=corpo(),
        alt="Do placar à escola: os achados de cada ato, as fontes e o convite para a apuração ao vivo.",
        z=lib.CAMADAS["conteudo"], tab=100))]
    for cod, texto, y in _linhas():
        itens.append(Visual(P, lib.visual_botao(
            f"T23_Fecho_Ir{cod[1:]}", X0 - 10, 150 + y - 150, 1020, LINHA, lib.acao_bookmark(f"{cod}_CHEGADA_01"),
            dica=f"Voltar à tela {roteiro.numero(cod)}: {texto}", z=lib.CAMADAS["acao"], tab=200 + int(cod[1:]),
            realce=C["creme"], realce_transp=(92, 86))))
    itens.append(Visual(P, lib.visual_botao(
        "T23_Fecho_IrApur", 1260, 710, 470, 150, lib.acao_bookmark("T18_CHEGADA_01"),
        dica=f"Ir para a apuração ao vivo (tela {roteiro.numero('T18')})", z=lib.CAMADAS["acao"], tab=300,
        realce=C["creme"],
        realce_transp=(92, 86))))
    return itens
