"""27 · Onde Flávio perdeu — ponte da diferença estadual, mapa só das viradas e perdas frente a Jair.

Brasil com exterior. Com uma UF, a ponte usa municípios. Com região/várias UFs, mantém contribuições estaduais.
O mapa e o dossiê são municipais, sem exterior. Cliques no mapa não alteram a ponte ou o ranking histórico.
"""
import pbip_lib as lib
import pagina_lib
from pbip_lib import Visual, Interacao
from paginas._resultado_segundo_turno import TT

P = 'T28'
Z = lib.CAMADAS['conteudo']
CSS = 'Estilo · CSS'
ESTILO = (
    '.perda-head .sob{font-size:13px}.perda-head .man{font-size:42px;line-height:1.2;margin:8px 0 9px}'
    '.perda-head .num{font-size:60px}.perda-head .txt{font-size:17px}'
    '.ponte svg text{font-family:var(--fonte);fill:var(--tinta);text-anchor:middle}'
    '.ponte svg{display:block;width:1620px;height:355px;overflow:visible}'
    '.ponte .v{font-size:20px;font-weight:650}.ponte .nome{font-size:13px}'
    '.ponte line{stroke:var(--cinza);stroke-width:1;stroke-dasharray:3 3}.ponte .zero{stroke:var(--areia)}'
    '.ponte .etapa{transition:opacity .18s}.ponte svg:has(.etapa:hover) .etapa:not(:hover){opacity:.4}'
    '.ponte .fecha{text-align:center;font-size:15px;height:35px;line-height:30px;color:var(--grafite)}'
    '.ponte .fecha .num{font-size:21px}'
    '.viradas-head{font-size:17px;line-height:32px}.viradas-head .num{font-size:28px}'
    '.jair>.rot{font-size:14px}.jair .colunas{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:16px}'
    '.jair h3{font-size:16px;font-weight:600;margin:0 0 12px}.perda-linha{font-size:15px;display:flex;gap:10px;'
    'justify-content:space-between;line-height:37px}.perda-linha span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
    '.perda-linha b{white-space:nowrap;font-size:20px}.jair p{font-size:14px;line-height:1.5;color:var(--grafite);margin-top:20px}'
)


def corpo():
    return f'<style>{ESTILO}</style>{{{{content}}}}'


def declarar(ctx):
    mapa = lib.visual_deneb('T28_Mapa_Municipios', 150, 700, 780, 275, 'spec/t28_mapa.json', [
        lib.campo_coluna('cod','Município','CodIBGE'), lib.campo_coluna('x','Município','X'),
        lib.campo_coluna('y','Município','Y'), lib.campo_coluna('uf','Município','UF'),
        lib.campo_medida('val','T28 · viradas · mapa')],
        alt=lib.medida('T28 · Viradas · ALT'), selecao=True, modo_selecao='advanced',
        tooltip_pagina='ttT28Municipio', tab=130, z=Z+1, uf_por_codigo=True)
    mapa['visual']['objects']['dataLimit']=[{'properties':{'enableIncrementalDataUpdates':lib.lit(True)}}]
    return [
        Visual(P,lib.visual_html('T28_Resposta_Html',150,140,1620,125,'T28 · Resposta · HTML',folha_de_estilo=CSS,
            modelo_corpo=corpo(),alt=lib.medida('T28 · Resposta · ALT'),tab=100,z=Z)),
        Visual(P,lib.visual_html('T28_Ponte_Html',150,270,1620,390,'T28 · Ponte · HTML',folha_de_estilo=CSS,
            modelo_corpo=corpo(),alt=lib.medida('T28 · Ponte · ALT'),tab=110,z=Z)),
        Visual(P,lib.visual_html('T28_Viradas_Titulo',150,660,780,42,'T28 · Viradas · HTML',folha_de_estilo=CSS,
            modelo_corpo=corpo(),alt=lib.medida('T28 · Viradas · ALT'),tab=120,z=Z)),
        Visual(P,mapa),
        Visual(P,lib.visual_html('T28_Viradas_Legenda',150,978,780,22,'Casca · vazio',folha_de_estilo=CSS,
            modelo_corpo="<div class='tela' style='font-size:13px;color:var(--grafite)'>Só trocas estritas · vermelho: Flávio → Lula · azul: Lula → Flávio (Uirapuru, GO no país)</div>{{content}}",
            alt='Mapa só das trocas de vencedor, sem exterior; empates não contam.',tab=135,z=Z)),
        Visual(P,lib.visual_html('T28_Jair_Html',1030,660,740,340,'T28 · Jair · HTML',folha_de_estilo=CSS,
            modelo_corpo=corpo(),alt=lib.medida('T28 · Jair · ALT'),tab=140,z=Z)),
        *pagina_lib.tooltip('ttT28Municipio','Município · dossiê',520,400,'T28 · Município · HTML',ordem=380,
            folha_de_estilo=CSS,modelo_corpo=f'<style>{TT}</style>{{{{content}}}}'),
        *[Interacao(P,'T28_Mapa_Municipios',alvo,'NoFilter') for alvo in
          ['T28_Casca_Filtro','T28_Resposta_Html','T28_Ponte_Html','T28_Viradas_Titulo','T28_Jair_Html']],
    ]
