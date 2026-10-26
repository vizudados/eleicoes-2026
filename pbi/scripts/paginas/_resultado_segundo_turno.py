"""Gramática comum às T27/T28: mesmos dois candidatos, mesmas contas, mapa e lista no grão municipal."""
from __future__ import annotations
import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual, Interacao

CSS='Estilo · CSS'
Z=lib.CAMADAS['conteudo']
RESPOSTA=(150,140,1620,135)
FLUXO=(150,280,840,430)
LISTA=(150,730,840,270)
MAPA=(1030,330,740,520)
TITULO_MAPA=(1030,280,740,30)
APOIOS=(1030,890,740,110)

ESTILO=(
    '.st-res .sob{font-size:13px}.st-res .man{font-size:43px;line-height:1.15;margin:8px 0 10px;letter-spacing:-.025em}'
    '.st-res .hero{font-size:64px;line-height:1;font-weight:700}'
    '.st-res .txt{font-size:17px}'
    '.st-fluxo .antes{position:absolute;left:0;top:0}.st-fluxo .depois{position:absolute;left:590px;top:0}'
    '.st-fluxo .candidato{position:absolute;left:0;font-size:15px;font-weight:700}'
    '.st-fluxo .origem{position:absolute;left:0;font-size:36px}.st-fluxo .destino{position:absolute;left:590px;font-size:36px}'
    '.st-fluxo .ponte{position:absolute;left:260px}.st-fluxo .saldo{position:absolute;left:300px;font-size:22px}'
    '.st-fluxo .participacao{position:absolute;left:0;right:0;top:220px;font-size:15px;color:var(--grafite)}'
    '.st-fluxo .resumo-viradas{position:absolute;left:0;right:0;top:250px;border-top:1px solid var(--areia);padding-top:10px}'
    '.st-fluxo .resumo-viradas>.rot{font-size:13px;margin-bottom:8px}'
    '.st-fluxo .conta-observada{position:absolute;left:0;right:0;top:234px;border-top:1px solid var(--areia);padding-top:10px}'
    '.st-fluxo .conta-observada>.rot{font-size:13px;margin-bottom:7px}'
    '.st-fluxo .parcela{display:flex;align-items:baseline;justify-content:space-between;gap:20px;font-size:15px;line-height:29px}'
    '.st-fluxo .parcela .num{font-size:22px;line-height:29px}'
    '.st-fluxo .parcela.total{border-top:1px solid var(--areia);margin-top:5px;padding-top:4px;font-weight:600}'
    '.st-fluxo .conta-observada .nota{font-size:15px;line-height:1.35;margin-top:8px}'
    '.st-fluxo .nota{font-size:13px;margin-top:9px;line-height:1.45;color:var(--grafite)}'
    '.st-fluxo .viradas{display:grid;grid-template-columns:1fr 1fr 1.4fr;gap:28px}'
    '.st-fluxo .viradas b{display:block;font-size:40px}.st-fluxo .viradas span{font-size:15px;display:block;margin-top:8px}'
    '.st-apoios{display:grid;grid-template-columns:1fr 1fr;gap:28px;border-top:1px solid var(--areia);padding-top:8px}'
    '.st-apoios .rot{font-size:13px;margin-bottom:6px}.st-apoios>div>div:not(.rot){display:flex;gap:10px;justify-content:space-between;font-size:15px;line-height:26px}'
    '.st-apoios span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:235px}.st-apoios b{white-space:nowrap}'
    '.st-titulo .rot{font-size:13px}.st-titulo .nota{font-size:13px;margin-top:6px}'
)
TT=(
    '.st-tt{background:var(--branco);border:1px solid var(--areia);padding:24px;color:var(--tinta)}'
    '.st-tt .fita{position:absolute;top:-7px;left:180px;width:110px;height:23px;background:var(--areia);opacity:.75;transform:rotate(-3deg)}'
    '.st-tt .tit{font-size:22px;margin-bottom:15px}.st-tt .rot{font-size:13px;margin-bottom:10px}'
    '.st-tt .duo{display:flex;gap:32px;font-size:15px}.st-tt .duo b{display:block;font-size:29px;margin-top:5px}'
    '.st-tt .txt{font-size:15px;line-height:1.45;margin-top:13px}'
    '.st-tt .mao{font-size:25px;position:absolute;bottom:12px;right:24px}'
)


def campos(p):
    return [lib.campo_coluna('cod','Município','CodIBGE'),
            lib.campo_coluna('uf','Município','UF'),
            lib.campo_coluna('rotulo','Município','Rótulo'),
            lib.campo_coluna('x','Município','X'),lib.campo_coluna('y','Município','Y'),
            lib.campo_medida('val',f'{p} · mapa · valor'),
            lib.campo_medida('tam',f'{p} · mapa · tamanho'),
            lib.campo_medida('valorTexto',f'{p} · valor formatado')]


def declarar(p,ctx):
    medida=lambda n:f'{p} · {n}'
    corpo=lambda extra='':f'<style>{ESTILO}{extra}</style>{{{{content}}}}'
    titulo='CRESCIMENTO DE LULA · VOTOS' if p=='T27' else 'MUDANÇA DE VANTAGEM · VOTOS'
    legenda='Vermelho: Lula cresceu · azul: Lula diminuiu' if p=='T27' else 'Vermelho: saldo para Lula · azul: saldo para Flávio'
    mapa_alt=('Mapa municipal em traço. Vermelho: Lula cresceu; azul: Lula diminuiu. Tamanho representa a magnitude em votos. Clique filtra a lista.'
              if p=='T27' else 'Mapa municipal em traço. Vermelho: mudança de vantagem para Lula; azul: para Flávio. Tamanho representa a magnitude em votos. Clique filtra a lista.')
    lista='CIDADES · SALDO DE VOTOS DE LULA' if p=='T27' else 'CIDADES · MUDANÇA DE VANTAGEM'
    # Cabeçalhos ficam no corpo dos próprios visuais; nada é desenhado na casca.
    spec_lista=lib.visual_deneb(f'{p}_Lista_Cidades',*LISTA,f'spec/{p.lower()}_lista.json',campos(p),
        alt=lib.medida(medida('Resposta · ALT')),selecao=True,modo_selecao='advanced',tooltip_pagina=f'tt{p}Municipio',tab=130)
    spec_lista['position']['z']=Z+3
    itens=[
        Visual(p,lib.visual_html(f'{p}_Resposta_Html',*RESPOSTA,medida('Resposta · HTML'),
            folha_de_estilo=CSS,modelo_corpo=corpo(),alt=lib.medida(medida('Resposta · ALT')),z=Z,tab=100)),
        Visual(p,lib.visual_html(f'{p}_Fluxo_Html',*FLUXO,medida('Fluxo · HTML'),folha_de_estilo=CSS,
            modelo_corpo=corpo()+f'<svg width="0" height="0">{estilo.defs_rabisco()}</svg>',
            alt=lib.medida(medida('Fluxo · ALT')),z=Z+1,tab=110)),
        Visual(p,lib.visual_html(f'{p}_Mapa_Titulo',*TITULO_MAPA,'Casca · vazio',folha_de_estilo=CSS,
            modelo_corpo=f'<div class="tela st-titulo"><div class="rot">{titulo}</div></div>{{{{content}}}}',
            alt=titulo,z=Z+1,tab=119)),
        Visual(p,lib.visual_html(f'{p}_Mapa_Legenda',1030,854,740,32,'Casca · vazio',folha_de_estilo=CSS,
            modelo_corpo=f'<div class="tela" style="font-size:14px;color:var(--grafite)">{legenda} · tamanho = votos</div>{{{{content}}}}',
            alt=legenda,z=Z+1,tab=121)),
        Visual(p,lib.visual_deneb(f'{p}_Mapa_Municipios',*MAPA,f'spec/{p.lower()}_mapa.json',campos(p),
            alt=mapa_alt,
            selecao=True,modo_selecao='advanced',tooltip_pagina=f'tt{p}Municipio',tab=120)),
        Visual(p,spec_lista),
        Visual(p,lib.visual_html(f'{p}_Lista_Titulo',LISTA[0],LISTA[1],LISTA[2],28,'Casca · vazio',
            folha_de_estilo=CSS,modelo_corpo=f'<div class="tela st-titulo"><div class="rot">{lista}</div></div>{{{{content}}}}',
            alt=lista,z=Z+4,tab=129)),
        Visual(p,lib.visual_html(f'{p}_Apoios_Html',*APOIOS,medida('Apoios · HTML'),folha_de_estilo=CSS,
            modelo_corpo=corpo(),alt=lib.medida(medida('Apoios · ALT')),z=Z+2,tab=140)),
        *pagina_lib.tooltip(f'tt{p}Municipio','Município · dossiê',520,400,medida('Município · HTML'),
            ordem=370 if p=='T27' else 380,folha_de_estilo=CSS,modelo_corpo=f'<style>{TT}</style>{{{{content}}}}'),
    ]
    # A escolha no mapa ou na lista não encolhe a árvore de estados da casca.
    for origem in [f'{p}_Mapa_Municipios',f'{p}_Lista_Cidades']:
        itens.append(Interacao(p,origem,f'{p}_Casca_Filtro','NoFilter'))
        for alvo in [f'{p}_Resposta_Html',f'{p}_Fluxo_Html',
                     f'{p}_Lista_Cidades' if origem.endswith('Mapa_Municipios') else f'{p}_Mapa_Municipios']:
            itens.append(Interacao(p,origem,alvo,'DataFilter'))
        if p=='T28':
            # Estado inteiro e ranking contra Jair conservam o recorte do filtro de UF da casca.
            itens.append(Interacao(p,origem,f'{p}_Apoios_Html','NoFilter'))
        else:
            itens.append(Interacao(p,origem,f'{p}_Apoios_Html','DataFilter'))
    return itens
