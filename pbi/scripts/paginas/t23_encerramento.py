# -*- coding: utf-8 -*-
"""28 · Encerramento — os achados dos dois turnos, com retorno à tela de origem.

O resultado final substitui o convite à apuração. Os dois candidatos usam as mesmas contas de crescimento;
as telas novas T27 e T28 têm atalhos próprios. A medida T23 · Achados · HTML fornece os números finais.
"""
from __future__ import annotations
import estilo
import roteiro
import pbip_lib as lib
from pbip_lib import Visual

P = "T23"
CSS = "Estilo · CSS"
C = estilo.COR
ACHADOS = [
    ("I · ANTES DA URNA", [("T10", "Até a véspera, 13 de 18 institutos davam Lula à frente; a urna deu Flávio.")]),
    ("II · O 1º TURNO", [("T01", "Flávio terminou 2,22 mi de votos à frente de Lula."),
                          ("T06", "33,5 milhões não foram votar: 15 vezes a diferença entre os dois."),
                          ("T25", "Quem tem 70 anos ou mais falta 3,9 vezes mais que quem tem 16 ou 17.")]),
    ("III · O MAPA", [("T11", "711 municípios trocaram Lula por Flávio; nenhum fez o caminho inverso."),
                       ("T13", "Nas cidades pequenas e de renda mais alta, Lula perdeu mais terreno."),
                       ("T24", "Onde mais casas recebem Bolsa Família, Lula teve 66%; onde menos, Flávio teve 61%."),
                       ("T14", "Pela 2ª vez em seis eleições, o PT terminou o 1º turno em segundo.")]),
]
FINAIS = [("T17", "As pesquisas diante da urna"), ("T18", "O resultado final e a noite da apuração"),
          ("T27", "De onde veio o crescimento de Lula"), ("T28", "Onde a vantagem de Flávio encolheu")]

def _linhas():
    saida, y = [], 384
    for _, itens in ACHADOS:
        y += 30
        for cod, texto in itens:
            saida.append((cod, texto, 150, y, 1020, 35))
            y += 35
    for i, (cod, texto) in enumerate(FINAIS):
        saida.append((cod, texto, 1260, 610 + i * 85, 470, 85))
    return saida

def corpo():
    css = (
        ".fx{color:var(--creme);position:fixed;left:150px;top:150px;right:150px;bottom:80px}"
        ".fx .tg{font-size:88px;font-weight:700;letter-spacing:-.035em;line-height:.98}"
        ".fx .ach{position:absolute;left:0;top:234px;width:1000px}"
        ".fx .grupo{height:30px;border-bottom:1px solid rgba(203,189,162,.35);padding-top:8px;color:var(--areia)}"
        ".fx .linha{height:35px;display:flex;align-items:center;gap:20px;font-size:19px}"
        ".fx .linha b{width:34px;font-size:16px;color:var(--areia)}"
        ".fx .urna{position:absolute;left:1120px;top:0;width:360px;opacity:.9}"
        ".fx .finais{position:absolute;left:1110px;top:420px;width:470px}"
        ".fx .finais .rot{color:var(--areia);margin-bottom:18px}"
        ".fx .final{height:85px;border-top:1px solid var(--grafite);padding:12px 0;display:flex;gap:16px;font-size:18px;line-height:1.4}"
        ".fx .final b{color:var(--areia);font-size:16px;padding-top:3px}"
        ".fx .fontes{position:absolute;left:0;top:660px;width:1000px;font-size:13px;line-height:1.6;color:var(--areia)}"
    )
    return (f"<style>{css}</style><div class='fx tela'><div class='tg sobe'>Da zona eleitoral<br/>ao resultado.</div>"
            f"<img class='urna entra' alt='' src='{estilo.imagem_b64('arte/limpos/urna-creme.png',720)}'/>"
            "<div class='fontes'><b>Fontes</b> · TSE (votação, comparecimento, perfil e API de resultados), IBGE, "
            "Portal da Transparência, Atlas do Desenvolvimento Humano, pesquisas registradas no TSE, Google Trends, "
            "Bites, Quaest, Social Blade, Datrix, Meta, emissoras e imprensa.<br/>"
            "<b>Desenhos</b> · em traço, a partir de fotos de licença aberta; créditos em cada cartão.</div></div>{{content}}")

def declarar(ctx):
    itens=[Visual(P,lib.visual_html('T23_Fecho_Html',0,0,1920,1080,'T23 · Achados · HTML',
        folha_de_estilo=CSS,modelo_corpo=corpo(),alt=lib.medida('T23 · Achados · ALT'),
        z=lib.CAMADAS['conteudo'],tab=100))]
    for cod,texto,x,y,w,h in _linhas():
        itens.append(Visual(P,lib.visual_botao(f'T23_Fecho_Ir{cod[1:]}',x-5,y,w,h,
            lib.acao_bookmark(f'{cod}_CHEGADA_01'),dica=f'Voltar à tela {roteiro.numero(cod)}: {texto}',
            z=lib.CAMADAS['acao'],tab=200+int(cod[1:]),realce=C['creme'],realce_transp=(92,86))))
    return itens
