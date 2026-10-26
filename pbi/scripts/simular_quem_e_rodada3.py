"""QA offline de T11/T12, nos tamanhos reais. Não conecta ao Desktop nem avalia DAX.

CSV para os dois turnos; fontes/host do HTML já avaliado pela main; CSS atual dos geradores.
--render usa somente Chromium headless local para medir DOM e fotografar os componentes.
"""
from __future__ import annotations
import argparse
import ast
import csv
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
PBI=Path(__file__).resolve().parents[1]
ROOT=PBI.parent
sys.path.insert(0,str(PBI/'scripts'))
from paginas import t11_virada as P11, t12_estados as P12

OUT=PBI/'qa/quem-e/rodada3'


class Frames(HTMLParser):
    def __init__(self):super().__init__();self.docs={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='iframe' and 'srcdoc' in a:self.docs[a.get('title')]=a['srcdoc']


def ler(nome):
    with (ROOT/nome).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))


def fontes_uf():
    tree=ast.parse((PBI/'modelo/base.py').read_text(encoding='utf-8'))
    return ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='UFS'for t in n.targets)))


def resultados(turno):
    if turno==2:
        return {(r['ano'],r['uf']):[int(r[k])for k in ['pt','adv','validos']]for r in ler('dados/pbi/uf_2turno.csv')}
    out={}
    for r in ler('dados/pbi/candidato_uf.csv'):
        v=int(r['votos']);a=out.setdefault((r['ano'],r['uf']),[0,0,0]);a[2]+=v
        if r['numero']=='13':a[0]+=v
        if r['numero']=='22':a[1]+=v
    return out


def lista(xs):
    return xs[0] if len(xs)==1 else ', '.join(xs[:-1])+' e '+xs[-1] if xs else ''


def pp(v):return ('+'if v>=0 else '−')+f'{abs(v)*100:.1f}'.replace('.',',')


def pc(v):return f'{v*100:.1f}%'.replace('.',',')


def medidas(turno,cods,ufs):
    r=resultados(turno)
    por_uf={u:{'nome':n,'regiao':reg,'m22':(r[('2022',u)][0]-r[('2022',u)][1])/r[('2022',u)][2],
                           'm26':(r[('2026',u)][0]-r[('2026',u)][1])/r[('2026',u)][2]}for u,n,reg in ufs}
    for d in por_uf.values():d['delta']=d['m26']-d['m22']
    globais={'subiu':sum(v['delta']>0 for v in por_uf.values()),'caiu':sum(v['delta']<0 for v in por_uf.values()),
             'exemplos':sorted(u for u,v in por_uf.items()if v['delta']>0)[:3],
             'viraram':sorted(v['nome']for v in por_uf.values()if v['m22']>0>v['m26'])}
    globais['nome_subiu']=next((v['nome']for v in por_uf.values()if v['delta']>0),'')
    globais['alta']=max(v['delta']for v in por_uf.values())
    lugar={}
    for ano in ['2022','2026']:
        l,a,v=[sum(r[(ano,u)][i]for u in cods)for i in range(3)]
        lugar[ano]={'l':l/v,'a':a/v,'m':(l-a)/v}
    lugar['delta']=lugar['2026']['m']-lugar['2022']['m']
    lugar['caiu']=sum(por_uf[u]['delta']<0 for u in cods if u!='ZZ')
    lugar['ufs']=len([u for u in cods if u!='ZZ'])
    return globais,lugar


def texto_titulo(g,loc,nome,tipo):
    d=loc['delta']
    if tipo=='uf':
        movimento='não variou'if d==0 else ('caiu 'if d<0 else 'subiu ')+f'{abs(d)*100:.1f}'.replace('.',',')+' p.p.'
        a,b=loc['2022']['m'],loc['2026']['m'];virou=a*b<0
        return nome+': a margem de Lula '+movimento+(', e mudou de lado'if virou else '')
    if tipo=='regiao':
        return f"{nome}: {loc['caiu']} de {loc['ufs']} unidades com queda; margem {pp(loc['2022']['m'])} → {pp(loc['2026']['m'])} p.p."
    maior='Lula'if g['subiu']>=g['caiu']else'Flávio';outro='Flávio'if maior=='Lula'else'Lula'
    n=g['subiu']if maior=='Lula'else g['caiu'];m=g['caiu']if maior=='Lula'else g['subiu']
    return f"{n} {'unidade foi'if n==1 else'unidades foram'} na direção de {maior}; {m}, na de {outro}"


def texto_apoio(g):
    if g['subiu']==0:return 'A margem de Lula não subiu em nenhuma unidade.'
    if g['subiu']==1:
        return ('Só '+('o 'if g['nome_subiu']=='Distrito Federal'else'')+g['nome_subiu']+
                ' foi na direção de Lula: <b>'+pp(g['alta'])+' p.p.</b>')
    return f"{g['subiu']} unidades foram na direção de Lula. Entre elas: {lista(g['exemplos'])}."


def resposta(g,loc,nome,tipo):
    d=loc['delta'];mudanca='não variou'if d==0 else ('caiu 'if d<0 else'subiu ')+f'{abs(d)*100:.1f}'.replace('.',',')
    txt_lugar=('No Brasil, foi de 'if tipo=='brasil'else'<b>'+escape(nome)+'</b>: de ')+pp(loc['2022']['m'])+' para '+pp(loc['2026']['m'])+' pontos'+(': 'if tipo=='brasil'else', ')+mudanca+'.'
    nomes=lista(g['viraram']);mudou=f"<span class='sub'>{escape(nomes)}</span> {'mudou'if len(g['viraram'])==1 else'mudaram'} de lado"if nomes else'Nenhuma unidade passou para o lado de Flávio'
    barras=''.join(f"<div class='lnb'><div class='ano'>{ano}</div><div class='tr'><i class='bl' style='width:{300*loc[ano]['l']:.3f}px'></i><i class='ba' style='width:{300*loc[ano]['a']:.3f}px'></i></div><div class='pc'><span class='lula'>{pc(loc[ano]['l'])}</span> × <span class='flavio'>{pc(loc[ano]['a'])}</span></div><div class='mg num'>{pp(loc[ano]['m'])}</div></div>"for ano in ['2022','2026'])
    return (f"<div class='tela t12r'><div class='topo'><span class='num g'>{g['caiu']}</span><span class='de'>de</span><span class='num g'>27</span></div>"
        f"<div class='man t1'>unidades em que a margem de <span class='lula'>Lula</span> caiu de 2022 para 2026</div><div class='man t2'>{mudou}<svg width='300'height='14'><path d='M3,9 C60,4 150,12 296,5'fill='none'stroke='var(--azul)'stroke-width='5'/></svg></div>"
        "<div class='apoio'><div class='txt t3'>"+texto_apoio(g)+"</div><div class='margem'><div class='rot'>O QUE É MARGEM</div>"
        "<div class='txt ex'>É a distância entre os votos de Lula e os do adversário, em pontos dos votos válidos: positiva, Lula à frente; negativa, o adversário. "+txt_lugar+"</div><div class='br'>"+barras+'</div></div></div></div>')


def titulo12(txt,selecionado):
    return ("<div class='tela t12t'><div class='rot'>MARGEM DE LULA EM CADA UNIDADE · 2022 → 2026, DA MAIOR QUEDA À ALTA</div><div class='man'>"+escape(txt)+"</div><div class='leg'><span><i class='o'></i>2022</span><span><i class='f vm'></i><i class='f az'></i>2026: vermelho, Lula à frente; azul, Flávio</span><span><i class='mud'></i>mudou de lado</span><span class='dir'>variação em pontos · "+('clique de novo para voltar'if selecionado else'clique numa unidade ou região')+'</span></div></div>')


def titulo11(volta,selecionado):
    return ("<div class='tela t11t'><div class='rot'>CADA PONTO É UM MUNICÍPIO · QUEM FICOU À FRENTE EM 2026</div><div class='man'>Sul e Sudeste somam 202 dos 278 que viraram</div>"
        "<div class='leg'><span><i class='c-l'></i>Lula à frente</span><span><i class='c-f'></i>Flávio à frente</span><span><i class='c-v'></i>trocou Lula por Flávio</span>"+
        ("<span><i class='c-vl'></i>trocou Flávio por Lula</span>"if volta else'')+"<span class='dica'>"+('clique fora para limpar'if selecionado else'clique ou arraste')+'</span></div></div>')


def documento(cache,corpo,css):
    cab=cache.split('<body>',1)[0]
    return cab+"<body><div id='sandbox-host'><div id='htmlViewer'><div class='os-padding'><div class='os-viewport'><div class='os-content'><div id='htmlContent'><style>"+css+"html,body{background:var(--papel)!important}*,*::before,*::after{animation:none!important;transition:none!important}</style><div class='htmlViewerEntry'>"+corpo+'</div></div></div></div></div></div></div></body></html>'


def preparar():
    OUT.mkdir(parents=True,exist_ok=True)
    cache={};originais={}
    for p in ['T11','T12']:
        s=(PBI/'qa/previa'/f'{p}.html').read_text(encoding='utf-8');originais[p]=s
        f=Frames();f.feed(s);cache.update(f.docs)
    ufs=fontes_uf();casos=[];oraculos={};full={}
    recortes=[('Brasil','brasil',[u for u,_,_ in ufs]+['ZZ']),*[(n,'uf',[u])for u,n,_ in ufs],('Exterior','uf',['ZZ']),
              *[(r,'regiao',[u for u,_,reg in ufs if reg==r])for r in sorted({r for _,_,r in ufs if r!='Exterior'})]]
    for turno in [1,2]:
        estado='pre'if turno==1 else'pos'
        for idx,(nome,tipo,cods)in enumerate(recortes):
            g,loc=medidas(turno,cods,ufs);man=texto_titulo(g,loc,nome,tipo)
            if tipo=='brasil':
                assert(g['caiu'],g['subiu'])==((26,1)if turno==1 else(11,16))
                assert man==('26 unidades foram na direção de Flávio; 1, na de Lula'if turno==1 else'16 unidades foram na direção de Lula; 11, na de Flávio')
            oraculos[f'{estado}-{nome}']={'caiu_brasil':g['caiu'],'subiu_brasil':g['subiu'],'manchete':man,'apoio':texto_apoio(g),'delta_local':loc['delta'],'caiu_local':loc['caiu'],'ufs_local':loc['ufs'],'m22_txt':pp(loc['2022']['m']),'m26_txt':pp(loc['2026']['m'])}
            for bloco,w,h,corpo,css,visual in [
                ('resposta',560,560,resposta(g,loc,nome,tipo),P12.CSS_RESPOSTA,'T12_Resposta_Html'),
                ('titulo',1010,96,titulo12(man,tipo!='brasil'),P12.CSS_TITULO,'T12_Corrida_Titulo')]:
                n=f'T12-{estado}-{idx:02d}-{bloco}';doc=documento(cache[visual],corpo,css)
                (OUT/(n+'.html')).write_text(doc,encoding='utf-8')
                casos.append({'nome':n,'largura':w,'altura':h,'tipo':bloco,'recorte':nome,
                              'foto':tipo=='brasil'or nome in ['Minas Gerais','Sul','Distrito Federal','Amapá','Exterior']})
                if turno==2 and tipo=='brasil':full[visual]=doc
    for volta in [False,True]:
        for selecionado in [False,True]:
            n=f'T11-legenda-{int(volta)}-{int(selecionado)}';doc=documento(cache['T11_Mapa_Titulo'],titulo11(volta,selecionado),P11.CSS_TITULO)
            (OUT/(n+'.html')).write_text(doc,encoding='utf-8')
            casos.append({'nome':n,'largura':820,'altura':100,'tipo':'legenda','foto':True})
            if volta and not selecionado:full['T11_Mapa_Titulo']=doc
    for p in ['T11','T12']:
        def trocar(m):
            tag=m[0];nome=re.search(r'title="([^"]+)"',tag)
            return re.sub(r'srcdoc="[^"]*"',lambda _:'srcdoc="'+escape(full[nome[1]],quote=True)+'"',tag)if nome and nome[1]in full else tag
        s=re.sub(r'<iframe\b[^>]*>',trocar,originais[p])
        (OUT/(p+'-pos-pagina.html')).write_text(s,encoding='utf-8')
    (OUT/'oraculos.json').write_text(json.dumps(oraculos,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'manifesto.json').write_text(json.dumps(casos,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    medir_fontes(oraculos)
    links=''.join(f"<li><a href='{c['nome']}.html'>{escape(c['nome'])}</a> · {c['largura']}×{c['altura']}</li>"for c in casos if c['foto'])
    (OUT/'index.html').write_text("<!doctype html><meta charset='utf-8'><title>Rodada 3 · T11/T12</title><h1>Rodada 3 · simulações locais</h1><p>Valores dos CSV nos dois turnos, CSS atual e host/fontes do HTML real já avaliado pela main. Não executa DAX nem consulta Desktop. Os HTMLs de página completa preservam os outros visuais do cache Pós.</p><p><a href='T11-pos-pagina.html'>T11 Pós · página</a> · <a href='T12-pos-pagina.html'>T12 Pós · página</a></p><ul>"+links+'</ul>',encoding='utf-8')
    print(f'Preparados {len(casos)} componentes: todos os recortes de T12 nos dois turnos e 4 estados de legenda T11.',flush=True)
    return casos


def medir_fontes(oraculos):
    """Prova de limite com métricas da Sora e alturas CSS; não substitui o DOM do Chromium."""
    from PIL import ImageFont
    ttf=str(PBI/'assets/fontes/sora-wght.ttf')
    def fonte(t,w=400):
        f=ImageFont.truetype(ttf,t);f.set_variation_by_axes([w]);return f
    f17=fonte(17,600);f15=fonte(15,600);f24=fonte(24,600)
    def limpar(s):return unescape(re.sub('<[^>]+>','',s))
    def linhas(s,f,w=540):
        n=1;atual=''
        for word in limpar(s).split():
            candidato=(atual+' '+word).strip()
            if atual and f.getlength(candidato)>w:n+=1;atual=word
            else:atual=candidato
        return n
    medidas=[]
    for nome,v in oraculos.items():
        man_w=f24.getlength(v['manchete'])
        assert man_w<=1010,(nome,'manchete',man_w,v['manchete'])
        # Nome mais longo do lugar real. Fonte 600 em todo o parágrafo é limite conservador.
        lugar=nome.split('-',1)[1];delta=v['delta_local']
        # Prefixo e limites reais das margens; reservados os sinais/dígitos mais largos.
        texto='É a distância entre os votos de Lula e os do adversário, em pontos dos votos válidos: positiva, Lula à frente; negativa, o adversário. '
        texto+=(('No Brasil, foi de 'if lugar=='Brasil'else lugar+': de ')+v['m22_txt']+' para '+v['m26_txt']+' pontos'+(': 'if lugar=='Brasil'else', ')+('não variou'if delta==0 else('caiu 'if delta<0 else'subiu ')+f'{abs(delta)*100:.1f}')+'.')
        apoio_linhas=linhas(v['apoio'],f17);ex_linhas=linhas(texto,f15)
        bottom=266+apoio_linhas*17*1.45+20+20+8+ex_linhas*15*1.45+12+68
        assert bottom<=560,(nome,'apoio e margem',bottom,apoio_linhas,ex_linhas)
        medidas.append({'caso':nome,'manchete_largura_conservadora':round(man_w,2),'apoio_linhas_limite':apoio_linhas,'definicao_linhas_limite':ex_linhas,'margem_bottom_limite':round(bottom,2),'gap_por_flex':20})
    fleg=fonte(15);fdica=fonte(13)
    legendas=[]
    for volta in [False,True]:
        labels=['Lula à frente','Flávio à frente','trocou Lula por Flávio']+(['trocou Flávio por Lula']if volta else[])
        for selecionado in [False,True]:
            dica='clique fora para limpar'if selecionado else'clique ou arraste'
            largura=sum(fleg.getlength(t)+20 for t in labels)+fdica.getlength(dica)+12*len(labels)
            assert largura<=820,(volta,selecionado,largura)
            legendas.append({'quarta_categoria':volta,'selecao':selecionado,'largura_medida':round(largura,2),'folga':round(820-largura,2)})
    (OUT/'prova-fontes.json').write_text(json.dumps({'metodo':'Métricas Sora; texto medido em peso 600 conservador; alturas/flow CSS. Não é prova DOM.','T12':medidas,'T11':legendas},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Métricas Sora: todos os títulos/legendas couberam; apoio + margem dentro dos 560 px.',flush=True)


JS=r"""() => {
const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
const q=s=>document.querySelector(s);
return{viewport:{w:innerWidth,h:innerHeight},apoio:rect(q('.t12r .t3')),margem:rect(q('.t12r .margem')),mudaram:rect(q('.t12r .t2')),fluxo:rect(q('.t12r .apoio')),
 man:rect(q('.t12t .man')),legenda:rect(q('.t12t .leg')),
 itens:[...document.querySelectorAll('.leg>span')].map(e=>({texto:e.textContent,...rect(e),scroll:e.scrollWidth,client:e.clientWidth})),
 dica:rect(q('.t11t .dica'))};
}"""


def validar(c,d):
    assert d['viewport']=={'w':c['largura'],'h':c['altura']}
    if c['tipo']=='resposta':
        assert d['margem']['y']-d['apoio']['bottom']>=19.9,(c,d)
        assert d['fluxo']['y']-d['mudaram']['bottom']>=10,(c,d)
        assert d['margem']['bottom']<=c['altura'],(c,d)
    else:
        for i in d['itens']:
            assert i['x']>=-.1 and i['right']<=c['largura']+.1 and i['bottom']<=c['altura']+.1,(c,i)
            assert i['scroll']<=i['client']+1,(c,i)
        for a,b in zip(d['itens'],d['itens'][1:]):assert a['right']<=b['x']+.1,(c,a,b)
        if c['tipo']=='titulo':assert d['man']['bottom']+4<=d['legenda']['y'],(c,d)


def render(casos):
    from playwright.sync_api import sync_playwright
    (OUT/'falha-render.txt').unlink(missing_ok=True)
    resultados=[]
    with sync_playwright()as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
        try:
            for c in casos:
                page=browser.new_page(viewport={'width':c['largura'],'height':c['altura']},device_scale_factor=1,reduced_motion='reduce')
                page.goto((OUT/(c['nome']+'.html')).as_uri());page.evaluate('document.fonts.ready')
                d=page.evaluate(JS);resultados.append({'caso':c['nome'],**d})
                (OUT/'prova-browser.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2),encoding='utf-8')
                validar(c,d)
                if c['foto']:page.screenshot(path=str(OUT/(c['nome']+'.png')))
                page.close()
            for nome in ['T11-pos-pagina','T12-pos-pagina']:
                page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1,reduced_motion='reduce')
                page.goto((OUT/(nome+'.html')).as_uri());page.screenshot(path=str(OUT/(nome+'.png')));page.close()
        finally:browser.close()
    print(f'Chromium: {len(resultados)} componentes medidos, sem colisão nem corte nos alvos da rodada.',flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
    cases=preparar()
    if args.render:
        try:render(cases)
        except Exception as e:
            (OUT/'falha-render.txt').write_text(str(e),encoding='utf-8')
            raise
