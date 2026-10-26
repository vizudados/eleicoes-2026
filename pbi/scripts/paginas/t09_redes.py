# -*- coding: utf-8 -*-
"""09 · Redes — quem dominou as redes? (dono: agente das telas da campanha)

A história: na campanha do 1º turno, os dois quase empataram em interações e Flávio ganhou mais seguidores; no 2º
turno, Lula disparou (3,5 vezes as interações de Flávio, Bites) e o índice de popularidade digital da Quaest virou.
Os anúncios na Meta entram com a sua ressalva: a Biblioteca de Anúncios e os pagamentos declarados ao TSE medem coisas
diferentes e não se somam.

  T09_Heroi_Html      quantas vezes (contador), a manchete e o que é "interação"
  T09_Popularidade_Html  o IPD da Quaest de 04/10 a 19/10: duas linhas que se desenham e se cruzam
  T09_Conversa_Html   fundo do protagonista: títulos das duas janelas, o chão dos balões, as notas à mão
  T09_Conversa_Baloes um par de balões de fala por candidato (granularidade Monitoramento[Candidato]): área = média
                      de interações por dia, na campanha do 1º turno e no 2º turno → dossiê ttT09Conversa
  T09_Lado_Html       fundo da coluna da direita: seguidores ganhos e anúncios na Meta (títulos, notas, ressalva)
  T09_Lado_Linhas     a barra de seguidores e o ritmo de cada um (granularidade Seguidores[Candidato]) → dossiê
                      ttT09Lado (seguidores por rede, o 2º turno e os pagamentos ao TSE)
  T09_Popularidade_Alvos  uma faixa por data do índice da Quaest (granularidade Monitoramento[Início]) sobre o
                      desenho do índice → dossiê ttT09Ipd: o humor da conversa naquele dia (saldo de sentimento da
                      Datrix na semana, menções da FGV depois do debate ou os comentários no dia do 1º turno)

Filtro cruzado (23/10/2026, "clicar num lado filtra os balões"): o clique num candidato, nos balões ou na coluna da
direita, apaga o outro candidato nas três peças (balões, coluna e índice) e a manchete do índice conta o caminho de quem
foi clicado. Para o clique realçar sem sumir com linha nenhuma, cada lado usa uma coluna de candidato diferente e sem
relação entre si: os balões, Monitoramento[Candidato]; a coluna da direita, Seguidores[Candidato] (a tabela de
seguidores, que é o assunto dela). As contas da coluna recebem o candidato da linha por CALCULATE em
Monitoramento[Candidato]; 'T09 · foco' lê o clique de qualquer um dos dois (ISINSCOPE separa o grão do clique).
NoFilter para o herói, os fundos e os alvos do índice (não leem o candidato).

Filtro de período (pílula da casca, tabela 'Período', compartilhado com Buscas e 2º turno; pedido do dono em
23/10/2026): sem escolha, a tela é a de sempre. Com um período, cada bloco usa só a medição que cabe INTEIRA nele (o
dia do debate conta como depois; entre as que cabem, a mais longa) e escreve a janela real dela: o herói e os balões,
as interações da Bites (Antes da Band = 05 a 17/10; Depois da Band = as 24 h depois do debate); a coluna da direita,
os seguidores ganhos (Bites, 05 a 17/10; Quaest, só Instagram, 18/10); o índice da Quaest, a faixa do período com o
resto esmaecido; o dossiê do lado, os anúncios da Biblioteca que cabem (19/10). Sem medição que caiba: 'sem dado no
período', nunca zero; Depois da Globo, 'não divulgado' (como na tela da Globo).
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Interacao, Visual
from paginas import _campanha as cp

P = "T09"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]

HEROI = (150, 140, 830, 300)
IPD = (1010, 140, 760, 300)
CONVERSA = (150, 470, 1040, 530)
LADO = (1240, 470, 530, 530)

CSS_HEROI = (
    ".t09a .linha{position:absolute;left:0;top:34px;display:flex;align-items:flex-end;gap:28px}"
    ".t09a .hero{display:flex;align-items:baseline;gap:14px}"
    ".t09a .hero .num{font-size:120px;letter-spacing:-.04em}"
    ".t09a .hero .u{font-size:34px;font-weight:600;letter-spacing:-.01em}"
    ".t09a .lado{font-size:22px;font-weight:600;line-height:1.25;padding-bottom:18px;max-width:330px}"
    ".t09a .man{position:absolute;left:0;top:178px;width:820px}"
    ".t09a .txt{position:absolute;left:0;top:246px;width:820px}"
    # período sem medição que caiba ('sem dado no período') ou ausente ('não divulgado'): o lugar do número tracejado
    f".t09a .vazio{{display:inline-block;border:2px dashed {C['areia']};border-radius:8px;padding:22px 30px;"
    "font-size:30px;font-weight:600;line-height:1.1;color:var(--cinza);white-space:nowrap}"
    ".t09a .vazio.mao{font-family:var(--mao);font-size:46px;color:var(--grafite);padding:14px 34px}"
)

CSS_IPD = (
    ".t09i .man{margin-top:6px;font-size:22px}"
    ".t09i svg{position:absolute;left:0;top:72px}"
    f".t09i .g{{stroke:{C['areia']};stroke-width:1}}"
    f".t09i .ex{{font-size:13px;fill:{C['cinza']};font-family:var(--fonte)}}"
    f".t09i .deb{{stroke:{C['grafite']};stroke-width:1.2;stroke-dasharray:4 5}}"
    f".t09i .ll{{stroke:{C['vermelho']};stroke-width:3.5;fill:none;stroke-linecap:round;stroke-linejoin:round}}"
    f".t09i .lf{{stroke:{C['azul']};stroke-width:3.5;fill:none;stroke-linecap:round;stroke-linejoin:round}}"
    f".t09i .pl{{fill:{C['vermelho']}}}.t09i .pf{{fill:{C['azul']}}}"
    ".t09i .rotulo{position:absolute;font-size:20px;font-weight:700;white-space:nowrap}"
    ".t09i .rotulo.e{text-align:right}"
    ".t09i .mao{position:absolute;font-size:30px;transform:rotate(-4deg);white-space:nowrap}"
    ".t09i .nota{position:absolute;left:0;right:0;top:258px}"
    ".t09i .apaga{opacity:.14;transition:opacity .35s}"
    # período: a faixa dele no eixo, as linhas a meio tom e os pontos e rótulos de fora apagados
    f".t09i .faixa{{fill:{C['areia']};fill-opacity:.45}}"
    ".t09i .meio{opacity:.4}.t09i .fora{opacity:.2}"
)

CSS_IPD_ALVOS = (
    ".t09p{pointer-events:none}"
    ".t09p .dia{position:absolute;top:72px;height:150px;width:32px;pointer-events:auto;cursor:help}"
    f".t09p .dia .v{{position:absolute;left:15.5px;top:0;bottom:0;width:1px;background:{C['tinta']};opacity:0;"
    "transition:opacity .12s}"
    ".t09p .dia i.m{position:absolute;left:9px;width:14px;height:14px;border-radius:50%;opacity:0;"
    f"transition:opacity .12s;box-shadow:0 0 0 2px {C['papel']},0 0 0 3.5px {C['tinta']}}}"
    f".t09p .dia i.ml{{background:{C['vermelho']}}}.t09p .dia i.mf{{background:{C['azul']}}}"
    ".t09p .dia:hover .v{opacity:.35}.t09p .dia:hover i.m{opacity:1}"
)

CSS_CONVERSA = (
    ".t09c .man{margin-top:6px;font-size:24px}"
    ".t09c .jan{position:absolute;top:104px}"
    ".t09c svg{position:absolute;left:0;top:0}"
    f".t09c .chao{{stroke:{C['grafite']};stroke-width:1.8;fill:none;stroke-linecap:round}}"
    f".t09c .div{{stroke:{C['areia']};stroke-width:1.4;stroke-dasharray:4 6}}"
    ".t09c .mao{position:absolute;font-size:30px;transform:rotate(-4deg);white-space:nowrap}"
    ".t09c .seta{position:absolute;height:56px}"
    ".t09c .nota{position:absolute;left:0;top:508px}"
    # período sem medição que caiba: o lugar dos balões da direita tracejado
    f".t09c .vazio{{position:absolute;left:590px;top:190px;width:420px;height:200px;border:2px dashed {C['areia']};"
    "border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;"
    "padding:0 30px;text-align:center}"
    ".t09c .vazio .rot{font-size:20px}"
    ".t09c .vazio .mao{position:static;font-size:44px;color:var(--grafite);transform:rotate(-3deg)}"
    ".t09c .vazio .nota{position:static;font-size:15px;color:var(--grafite);line-height:1.4}"
)


def corpo_conversa() -> str:
    seta = cp.img("arte/limpos/rabiscos/seta-curva-esquerda-tinta.png", 140)
    return (f"<style>{CSS_CONVERSA}.t09c .seta{{background:url({seta}) center/contain no-repeat}}</style>"
            f"{cp.defs_rabisco()}{{{{content}}}}")


CSS_BALOES = (
    ".t09b{pointer-events:none}"
    ".t09b svg{position:absolute;left:0;top:0}"
    ".t09b .bal{pointer-events:auto;cursor:help}"
    ".t09b .aro{fill:none;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}"
    f".t09b .l .aro{{stroke:{C['vermelho']}}}.t09b .f .aro{{stroke:{C['azul']}}}"
    f".t09b .l .miolo{{fill:{C['rosa']};fill-opacity:.42}}.t09b .f .miolo{{fill:{C['azul_claro']};fill-opacity:.5}}"
    ".t09b .bal:hover .miolo{fill-opacity:.75}"
    ".t09b .lab{position:absolute;width:200px;text-align:center;transform:translateX(-50%)}"
    ".t09b .lab b{display:block;font-size:17px;font-weight:600}"
    ".t09b .lab .num{display:block;font-size:30px;margin-top:2px}"
    ".t09b .lab .sub{display:block;font-size:15px;color:var(--grafite);margin-top:3px}"
    ".t09b{transition:opacity .35s}.t09b.apaga{opacity:.18}"
)

CSS_LADO = (
    ".t09l .man{margin-top:6px;font-size:24px}"
    ".t09l .nota{margin-top:6px}"
    ".t09l .txt{margin-top:6px;font-size:15px}"
    ".t09l .bloco{position:absolute;left:0;right:0}"
    f".t09l hr{{position:absolute;left:0;right:0;top:306px;border:0;border-top:1px solid {C['areia']};margin:0}}"
    ".t09l .ress{position:absolute;left:0;right:0;top:494px;font-size:13px;line-height:1.4;color:var(--cinza)}"
    # período sem medição que caiba: o lugar das barras tracejado
    f".t09l .vazio{{position:absolute;left:0;right:0;top:150px;height:150px;border:2px dashed {C['areia']};"
    "border-radius:10px;display:flex;align-items:center;justify-content:center}"
    ".t09l .vazio .rot{font-size:20px}"
    ".t09l .vazio .mao{font-size:44px;color:var(--grafite);transform:rotate(-3deg)}"
)


def corpo_linhas() -> str:
    seta = cp.img("arte/limpos/rabiscos/seta-reta-tinta.png", 96)
    css = (
        ".t09r{pointer-events:none}"
        ".t09r .alvo{position:absolute;pointer-events:auto;cursor:help;border-radius:4px}"
        ".t09r .alvo:hover{background:rgba(203,189,162,.22)}"
        ".t09r .nome{position:absolute;font-size:20px;font-weight:600}"
        ".t09r .barra{position:absolute;height:28px;border-radius:2px}"
        f".t09r .barra.l{{background:{C['vermelho']}}}.t09r .barra.f{{background:{C['azul']}}}"
        ".t09r .num{position:absolute;font-size:30px;white-space:nowrap}"
        ".t09r .num.grande{font-size:46px}"
        ".t09r .ritmo{position:absolute;display:flex;align-items:baseline;gap:12px;white-space:nowrap}"
        ".t09r .ritmo .num{position:static;font-size:28px}"
        f".t09r .ritmo .seta-r{{display:inline-block;width:48px;height:16px;background:url({seta}) center/contain "
        "no-repeat;opacity:.8}"
        ".t09r .ritmo .sub{font-size:15px;color:var(--grafite)}"
        ".t09r{transition:opacity .35s}.t09r.apaga{opacity:.18}"
    )
    return f"<style>{css}</style>{{{{content}}}}"


CSS_TT_CONVERSA = (
    ".tt9c .tab{display:grid;grid-template-columns:1fr 92px 92px;column-gap:12px;row-gap:7px;margin-top:10px;"
    "align-items:baseline}"
    ".tt9c .tab .h{font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;text-align:right}"
    ".tt9c .tab .j{font-size:15px;color:var(--grafite);line-height:1.25}"
    ".tt9c .tab .v{font-size:17px;font-weight:600;text-align:right;font-variant-numeric:tabular-nums}"
    f".tt9c .tab .on{{background:{C['creme']};box-shadow:0 0 0 4px {C['creme']}}}"
    ".tt9c .txt{margin-top:12px}"
    ".dos .tt9c .mao{position:static;display:block;text-align:right;margin-top:4px}"
)

CSS_TT_IPD = (
    ".tt9i .par{margin:2px 0 6px 0}"
    ".dos .tt9i .par .num.vazio{color:var(--cinza);font-weight:400}"
    ".tt9i .rot{margin:2px 0 8px 0}"
    ".tt9i .hb{display:grid;grid-template-columns:70px 240px 64px;align-items:center;height:28px}"
    ".tt9i .hb .hn{font-size:15px;font-weight:600}"
    ".tt9i .hb .trilho{position:relative;height:14px}"
    f".tt9i .hb .trilho::before{{content:'';position:absolute;left:120px;top:-4px;bottom:-4px;border-left:1.5px solid {C['tinta']}}}"
    ".tt9i .hb i{position:absolute;top:1px;height:12px;animation:uCresceX .7s cubic-bezier(.2,.7,.2,1) both}"
    ".tt9i .hb i.pos{left:121px;transform-origin:left center}.tt9i .hb i.neg{right:120px;transform-origin:right center}"
    f".tt9i .hb i.l{{background:{C['vermelho']}}}.tt9i .hb i.f{{background:{C['azul']}}}"
    ".tt9i .hb b{font-size:17px;font-weight:700;text-align:right;font-variant-numeric:tabular-nums}"
    ".tt9i .mt{display:grid;grid-template-columns:90px 110px 110px;row-gap:4px;align-items:baseline}"
    ".tt9i .mt .h{font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--cinza)}"
    ".tt9i .mt span{font-size:15px;font-weight:600}.tt9i .mt b{font-size:20px;font-weight:700}"
    ".tt9i .nota{margin-top:6px;padding-right:170px}"
)

CSS_TT_LADO = (
    ".tt9l{display:grid;grid-template-columns:1fr 300px;column-gap:30px}"
    ".tt9l .tab{display:grid;grid-template-columns:84px 1fr 1fr;column-gap:10px;row-gap:6px;margin-top:8px;"
    "align-items:baseline}"
    ".tt9l .tab .h{font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;text-align:right;"
    "line-height:1.25}"
    ".tt9l .tab .r{font-size:15px;color:var(--grafite)}"
    ".tt9l .tab .v{font-size:16px;font-weight:600;text-align:right;font-variant-numeric:tabular-nums}"
    ".tt9l .txt{margin-top:8px;font-size:15px}"
    ".tt9l .ad{margin-top:10px}.tt9l .ad b{display:block;font-size:26px;font-weight:700;letter-spacing:-.02em}"
    ".tt9l .ad span{display:block;font-size:15px;color:var(--grafite)}"
    ".tt9l .ad b.vazio{font-size:20px;color:var(--cinza)}"
    f".tt9l .outra{{margin-top:12px;padding:10px 12px;border:1.5px dashed {C['areia']};font-size:15px;line-height:1.38}}"
    ".tt9l .outra .rot{margin-bottom:4px}"
    ".dos .tt9l .mao{position:static;display:block;text-align:right;margin-top:10px}"
)


def declarar(ctx):
    gran = ("Monitoramento", "Candidato")
    return [
        Visual(P, lib.visual_html("T09_Heroi_Html", *HEROI, "T09 · Herói · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_HEROI}</style>{{{{content}}}}",
                                  alt=lib.medida("T09 · Herói · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T09_Popularidade_Html", *IPD, "T09 · Popularidade · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_IPD}</style>{cp.defs_rabisco()}{{{{content}}}}",
                                  alt=lib.medida("T09 · Popularidade · ALT"), z=Z + 1, tab=110)),
        Visual(P, lib.visual_html("T09_Conversa_Html", *CONVERSA, "T09 · Conversa · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_conversa(), alt=lib.medida("T09 · Conversa · ALT"), z=Z + 2,
                                  tab=120)),
        Visual(P, lib.visual_html("T09_Popularidade_Alvos", *IPD, "T09 · Popularidade pontos · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_IPD_ALVOS}</style>{{{{content}}}}",
                                  granularidade=("Monitoramento", "Início"), tooltip_pagina="ttT09Ipd",
                                  alt=lib.medida("T09 · Popularidade pontos · ALT"), z=Z + 6, tab=115)),
        Visual(P, lib.visual_html("T09_Conversa_Baloes", *CONVERSA, "T09 · Balões · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_BALOES}</style>{cp.defs_rabisco()}{{{{content}}}}",
                                  granularidade=gran, filtro_cruzado=True, transparencia_nao_selecionados=True,
                                  tooltip_pagina="ttT09Conversa",
                                  alt=lib.medida("T09 · Balões · ALT"), z=Z + 3, tab=130)),
        Visual(P, lib.visual_html("T09_Lado_Html", *LADO, "T09 · Lado · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_LADO}</style>{{{{content}}}}",
                                  alt=lib.medida("T09 · Lado · ALT"), z=Z + 4, tab=140)),
        Visual(P, lib.visual_html("T09_Lado_Linhas", *LADO, "T09 · Linhas · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_linhas(),
                                  granularidade=("Seguidores", "Candidato"), filtro_cruzado=True,
                                  transparencia_nao_selecionados=True, tooltip_pagina="ttT09Lado",
                                  alt=lib.medida("T09 · Linhas · ALT"), z=Z + 5, tab=150)),
        # o clique num candidato (balões ou coluna) só realça: o herói, os fundos e os alvos do índice não o leem
        *[Interacao(P, origem, alvo, "NoFilter")
          for origem in ("T09_Conversa_Baloes", "T09_Lado_Linhas")
          for alvo in ("T09_Heroi_Html", "T09_Conversa_Html", "T09_Lado_Html", "T09_Popularidade_Alvos")],
        *pagina_lib.tooltip("ttT09Conversa", "Redes · interações", 520, 340, "T09 · Tooltip conversa · HTML",
                            ordem=200, folha_de_estilo=CSS, modelo_corpo=cp.dossie("celular", CSS_TT_CONVERSA)),
        *pagina_lib.tooltip("ttT09Lado", "Redes · seguidores e anúncios", 760, 420, "T09 · Tooltip lado · HTML",
                            ordem=201, folha_de_estilo=CSS, modelo_corpo=cp.dossie("pessoas", CSS_TT_LADO)),
        *pagina_lib.tooltip("ttT09Ipd", "Redes · dia do índice", 460, 330, "T09 · Tooltip IPD · HTML",
                            ordem=202, folha_de_estilo=CSS, modelo_corpo=cp.dossie("celular", CSS_TT_IPD)),
    ]
