# -*- coding: utf-8 -*-
"""pagina_lib — peças repetidas das declarações de tela (pbi/scripts/paginas/t0X_*.py). Dono: main.
Adaptado de Participação Sócios/pbi/scripts/pagina_comum.py (a origem fica intocada).

- cabecalho(): o bloco "0X · NOME" + pergunta da tela, sempre na mesma caixa (a casca reserva o lugar).
- leituras(): o "?" de cada painel abre a LEITURA (storytelling) por cima do retângulo do próprio painel (L065), por
  marcador só de exibição (applyOnlyToTargetVisuals + suppressData + suppressActiveSection, L029).
- chegada(): o marcador de chegada da tela (L095), que a navegação da casca aplica: a página chega sempre com as
  leituras fechadas, sem tocar em filtro nem dado.
- tooltip(): página de tooltip HTML (tt<T0X><Assunto>), cantos retos e cartão do tamanho da página (L078).
"""
from __future__ import annotations

import pbip_lib as lib
from pbip_lib import Bookmark, Pagina, Visual

# Caixa do cabeçalho de cada tela (sobretítulo "0X · NOME" + pergunta), igual em todas as telas brancas.
CAB = (300, 44, 900, 80)  # §4.3 (18/10): o cabeçalho é o título do slide, na faixa do topo ao lado da logo
# Cor do realce de hover dos botões "?" e "×" (tinta); o desenho do "?" é do HTML do painel.
REALCE = "#0B0B0C"


def cabecalho(tela: str, medida_html: str, *, alt: str, folha_de_estilo: str | None = None, tab: int = 1) -> Visual:
    """Visual T0X_Cab_Pergunta na caixa CAB. A medida desenha o sobretítulo e a pergunta (classes da casca)."""
    x, y, w, h = CAB
    return Visual(tela, lib.visual_html(f"{tela}_Cab_Pergunta", x, y, w, h, medida_html, alt=alt,
                                        folha_de_estilo=folha_de_estilo, tab=tab))


def leituras(tela: str, lista: list[tuple], *, folha_de_estilo: str | None = None) -> list:
    """lista = [(chave, x, y, w, h do PAINEL, medida base, indicador do marcador em MAIÚSCULAS, título)].
    Cria, por painel: <T>_<chave>_Leitura (HTML oculto, medida '<base> · HTML', alt '<base> · ALT') na caixa do
    painel; <T>_<chave>_LeituraAbrir sobre o "?" (40 × 40, centro em x+w−28, y+28: o painel desenha o "?" ali);
    <T>_<chave>_LeituraFechar no mesmo lugar, oculto (o HTML da leitura desenha o "×" ali). Marcadores
    <T>_LEITURA_<IND>_01 (abre a do painel, fecha as outras) e <T>_LEITURA_00 (fecha todas)."""
    itens = []
    todos = {}
    for chave, *_r in lista:
        todos[f"{tela}_{chave}_Leitura"] = False
        todos[f"{tela}_{chave}_LeituraFechar"] = False
    for i, (chave, x, y, w, h, base, ind, titulo) in enumerate(lista):
        bx, by = x + w - 28 - 20, y + 28 - 20
        itens.append(Visual(tela, lib.visual_html(
            f"{tela}_{chave}_Leitura", x, y, w, h, f"{base} · HTML", alt=lib.medida(f"{base} · ALT"),
            z=lib.CAMADAS["leitura"] + 2 * i, oculto=True, tab=200 + i, folha_de_estilo=folha_de_estilo)))
        itens.append(Visual(tela, lib.visual_botao(
            f"{tela}_{chave}_LeituraAbrir", bx, by, 40, 40, lib.acao_bookmark(f"{tela}_LEITURA_{ind}_01"),
            dica=f"Como ler: {titulo}", tab=210 + i, realce=REALCE, raio=20)))
        itens.append(Visual(tela, lib.visual_botao(
            f"{tela}_{chave}_LeituraFechar", bx, by, 40, 40, lib.acao_bookmark(f"{tela}_LEITURA_00"),
            dica="Fechar a leitura", z=lib.CAMADAS["leitura"] + 2 * i + 1, oculto=True, tab=220 + i,
            realce=REALCE, raio=20)))
        aberto = dict(todos)
        aberto[f"{tela}_{chave}_Leitura"] = True
        aberto[f"{tela}_{chave}_LeituraFechar"] = True
        itens.append(Bookmark(lib.bookmark_exibicao(f"{tela}_LEITURA_{ind}_01", tela, aberto,
                                                    titulo=f"Leitura · {titulo}")))
    if lista:
        itens.append(Bookmark(lib.bookmark_exibicao(f"{tela}_LEITURA_00", tela, todos, titulo="Leituras fechadas")))
    return itens


def nomes_leitura(tela: str, lista: list[tuple]) -> list[str]:
    """Os visuais que o marcador de chegada esconde (as leituras e os × da tela)."""
    return [f"{tela}_{c}_{p}" for c, *_r in lista for p in ("Leitura", "LeituraFechar")]


def chegada(tela: str, ocultos: list[str], visiveis: list[str] | None = None) -> Bookmark:
    """Marcador <T>_CHEGADA_01 (L095): leva à página e deixa `ocultos` escondidos e `visiveis` à mostra. A casca liga
    a navegação a ele (paginas/casca.py, ajustar). Toda tela declara o seu, com ao menos um alvo (sem leitura,
    passe visiveis=[<T>_Cab_Pergunta])."""
    vis = {v: False for v in ocultos}
    vis.update({v: True for v in (visiveis or [])})
    if not vis:
        vis = {f"{tela}_Cab_Pergunta": True}
    return Bookmark(lib.bookmark_chegada(f"{tela}_CHEGADA_01", tela, vis, titulo=f"Chegada · {tela}"))


def tooltip(nome: str, titulo: str, largura: int, altura: int, medida_html: str, *, ordem: int,
            folha_de_estilo: str | None = None, modelo_corpo: str | None = None,
            cor_fundo: str = "#F1EBDF") -> list:
    """Página de tooltip tt<TNN><Assunto> com um HTML do tamanho da página (cantos retos, L078) e o ALT da medida.
    `modelo_corpo` = bodyTemplate do visual (CSS e desenho fixos do cartão, com {{content}}); `cor_fundo` = fundo da
    página de tooltip (papel por padrão: o cartão dossiê desenha o próprio papel por cima)."""
    return [Pagina(lib.pagina_tooltip(nome, titulo, altura=altura, largura=largura, cor_fundo=cor_fundo), ordem=ordem),
            Visual(nome, lib.visual_html(f"TT_{nome[2:]}_Conteudo", 0, 0, largura, altura, medida_html,
                                         alt=lib.medida(medida_html.replace("· HTML", "· ALT")),
                                         pagina_wh=(largura, altura), folha_de_estilo=folha_de_estilo,
                                         modelo_corpo=modelo_corpo))]
