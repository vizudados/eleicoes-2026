"""Simulações nos tamanhos PBIR, partindo do HTML realmente avaliado pela main.

Não consulta o motor. Conserva os valores do cache; aplica correções determinísticas equivalentes às do gerador.
Opcional --render usa Chromium/Playwright local, com viewport exato e sem acessar o Power BI.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import subprocess
import html
import xml.etree.ElementTree as ET

PBI=Path(__file__).resolve().parents[1]
Q=PBI/'qa/rodada6'


class Frames(HTMLParser):
    def __init__(self):super().__init__();self.docs={}
    def handle_starttag(self,tag,attrs):
        if tag=='iframe':
            a=dict(attrs)
            if 'srcdoc'in a:self.docs[a.get('title','')]=a['srcdoc']


def fixo2(s):
    return format(Decimal(s),'.2f')


def atributo(tag,nome,valor):
    return re.sub(rf"\b{nome}=(['\"])[^'\"]*\1",lambda m:f"{nome}='{valor}'",tag,count=1)


def corrigir_svg(s):
    """Mesmo valor avaliado, representação decimal obrigatória. Novos endpoints e largura especial DF."""
    n=len(re.findall(r"<g class='etapa'>",s))
    def grupo(m):
        g=m.group(0)
        val=re.search(r"<text class='v num'[^>]*>",g).group(0)
        centro=float(re.search(r"\bx='([^']+)'",val).group(1))
        titulo=unescape(re.search(r'<title>(.*?)</title>',g).group(1))
        endpoint=titulo.startswith(('1º turno:','2º turno:'))
        rect=re.search(r'<rect\b[^>]+>',g).group(0)
        altura=float(re.search(r"height='([^']+)'",rect).group(1))
        yy=float(re.search(r"\by='([^']+)'",val).group(1))
        val_novo=atributo(val,'y','309.00'if endpoint else fixo2(str(yy if altura<9 else max(28,yy))))
        g=g.replace(val,val_novo,1)
        if n==3:
            novo=atributo(atributo(rect,'width','170.00'),'x',fixo2(str(centro-85)))
            g=g.replace(rect,novo,1)
            line=re.search(r'<line\b[^>]+>',g)
            if line:
                passo=1550/n
                novo=atributo(atributo(line.group(0),'x1',fixo2(str(centro+85))),'x2',fixo2(str(centro+passo-85)))
                g=g.replace(line.group(0),novo,1)
        return g
    s=re.sub(r"<g class='etapa'>.*?</g>",grupo,s,flags=re.S)
    # Só valores numéricos de atributos; não altera texto, datas, cores ou viewBox.
    s=re.sub(r"\b(x|y|x1|x2|y1|y2|width|height)='(-?\d+\.\d*)'",lambda m:f"{m[1]}='{fixo2(m[2])}'",s)
    return s


def corrigir_lista(s):
    pad=r"<i style='left:([-\d.]+)px;width:([-\d.]+)px;background:([^']+)'></i>"
    return re.sub(pad,lambda m:"<span class='faixa-barra'><i style='left:"+fixo2(str(Decimal(m[1])-350))+"px;width:"+fixo2(m[2])+"px;background:"+m[3]+"'></i></span>",s)


def folha(texto):
    return '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>',texto,flags=re.S))


def finalizar(doc,css,titulo):
    doc=re.sub(r'<script\b[^>]*>.*?</script>','',doc,flags=re.S|re.I)
    css+='html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#F1EBDF!important}'
    css+='*,*::before,*::after{animation:none!important;transition:none!important}'
    doc=doc.replace('</body>',f'<style>{css}</style></body>')
    doc=re.sub(r'<title>.*?</title>',f'<title>{escape(titulo)}</title>',doc,flags=re.S)
    return doc


def preparar():
    from paginas.t28_onde_flavio_perdeu import ESTILO
    from paginas._resultado_segundo_turno import ESTILO as CSS27
    import desenho_t22 as D22
    Q.mkdir(exist_ok=True)
    casos=[('T28','T28_Ponte_Html','T28-Brasil',1620,390),('T28-MG','T28_Ponte_Html','T28-MG',1620,390),
           ('T28-DF','T28_Ponte_Html','T28-DF',1620,390),('T27','T27_Lista_Cidades','T27-lista',840,270),
           ('T22','T22_Reguas_Html','T22-fundos',860,270),('T22','T22_Pesquisas_Html','T22-tabela',860,296)]
    manifesto=[]
    for pagina,visual,nome,w,h in casos:
        congelado=Q/(nome+'-original-motor.html')
        if congelado.exists():doc=congelado.read_text(encoding='utf-8')
        else:
            p=Frames();p.feed((PBI/'qa/previa'/f'{pagina}.html').read_text(encoding='utf-8'))
            doc=p.docs[visual];congelado.write_text(doc,encoding='utf-8')
        original=doc
        if nome.startswith('T28'):
            doc=corrigir_svg(doc);css=ESTILO
        elif nome=='T27-lista':doc=corrigir_lista(doc);css=CSS27
        elif nome=='T22-fundos':
            arq=PBI/'dax/T22 Simulador/Desenho/T22 · Régua abstenção · HTML.dax'
            pergunta=re.search(r"class='pergunta sobe'>([^<]+)</div>",arq.read_text(encoding='utf-8'))[1]
            doc=doc.replace('Quantos deles teriam deixado de escolher alguém?',pergunta)
            css=folha(D22.corpo_reguas())
        else:
            cab=re.search(r"<div class='cab'>.*?</div>",D22.corpo_pesquisas(),re.S)[0]
            doc=re.sub(r"<div class='cab'>.*?</div>",lambda m:cab,doc,flags=re.S)
            css=folha(D22.corpo_pesquisas())
        antes=finalizar(original,'',nome+' · antes · HTML do motor')
        depois=finalizar(doc,css,nome+' · depois · simulação por HTML avaliado')
        (Q/(nome+'-antes.html')).write_text(antes,encoding='utf-8')
        (Q/(nome+'-depois.html')).write_text(depois,encoding='utf-8')
        pb=PBI/f'pbip/Eleicoes.Report/definition/pages/{pagina.split("-")[0]}/visuals/{visual}/visual.json'
        pos=json.loads(pb.read_text(encoding='utf-8'))['position']
        assert(pos['width'],pos['height'])==(w,h),(nome,pos)
        if nome.startswith('T28'):
            svg=re.search(r'<svg viewBox=.*?</svg>',depois,re.S)[0]
            root=ET.fromstring(svg)
            rects=root.findall('.//rect')
            assert len(rects)=={'T28-Brasil':13,'T28-MG':12,'T28-DF':3}[nome]
            for r in rects:
                x,y,ww,hh=[float(r.attrib[a])for a in ['x','y','width','height']]
                assert x>=0 and y>=0 and ww>0 and hh>0 and x+ww<=1620 and y+hh<=355,(nome,r.attrib)
            assert not re.search(r"\b(?:x|y|width|height)='[-\d]+\.'",svg)
        assert '350.px'not in depois
        manifesto.append({'nome':nome,'visual':visual,'largura':w,'altura':h,'position_pbip':pos,
                          'origem':'HTML da medida já avaliada pelo motor na rodada 5; correção determinística, sem nova consulta'})
    # A manchete DF usa os valores efetivamente avaliados (79671 e -154318), com a nova redação do gerador.
    p=Frames();p.feed((PBI/'qa/previa/T28-DF.html').read_text(encoding='utf-8'))
    header=p.docs['T28_Resposta_Html']
    motor_df=(Q/'T28-DF-original-motor.html').read_text(encoding='utf-8')
    titulos=re.findall(r"<g class='etapa'><title>(.*?)</title>",motor_df)
    votos=lambda s:int(re.search(r': ([−+\d.]+) votos',unescape(s))[1].replace('.','').replace('−','-'))
    movimento=votos(titulos[1]);fim=votos(titulos[-1]);fmt=lambda n:f'{abs(n):,}'.replace(',','.')
    novo=("<div class='man'>No DF, a diferença andou <span class='num'>"+fmt(movimento)+"</span> votos para "+('Lula'if movimento>=0 else'Flávio')+"</div>"
          "<div class='txt'>"+('Flávio'if fim<0 else'Lula')+" terminou o 2º turno à frente por "+fmt(fim)+" votos.</div>")
    header=re.sub(r"<div class='man'>.*?<div class='txt'>.*?</div>",lambda m:novo,header,flags=re.S)
    (Q/'T28-DF-manchete-depois.html').write_text(finalizar(header,ESTILO,'DF · manchete nova'),encoding='utf-8')
    manifesto.append({'nome':'T28-DF-manchete','visual':'T28_Resposta_Html','largura':1620,'altura':125})
    (Q/'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    links=''.join(f"<li>{escape(c['nome'])}: <a href='{c['nome']}-depois.html'>depois</a> · {c['largura']}×{c['altura']}</li>"for c in manifesto)
    (Q/'index.html').write_text("<!doctype html><meta charset='utf-8'><title>Rodada 6 · simulações</title><h1>Simulações da rodada 6</h1>"
        "<p>HTML efetivamente avaliado na rodada 5, com correções determinísticas de formato/geometria e os CSS atuais. "
        "Não é nova execução DAX. Cada arquivo deve ser aberto no viewport do manifesto.</p><ul>"+links+'</ul>',encoding='utf-8')
    print('Preparados',len(manifesto),'casos em',Q)
    return manifesto


def renderizar(casos):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
        resultados=[]
        try:
            for c in casos:
                page=browser.new_page(viewport={'width':c['largura'],'height':c['altura']},device_scale_factor=1,reduced_motion='reduce')
                page.goto((Q/(c['nome']+'-depois.html')).as_uri())
                page.evaluate('document.fonts.ready')
                page.evaluate(JS_QA)
                prova=page.evaluate('JSON.parse(document.getElementById("qa-r6").textContent)')
                page.screenshot(path=str(Q/(c['nome']+'-depois.png')))
                validar_browser(c,prova)
                resultados.append({'nome':c['nome'],**prova})
                page.close()
        finally:browser.close()
    (Q/'prova-browser.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


JS_QA = r"""document.fonts.ready.then(()=>{
const rect=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}};
const out={viewport:{w:innerWidth,h:innerHeight},sora:document.fonts.check('20px "Sora Eleicoes"'),
  barras:[...document.querySelectorAll('g.etapa rect')].map(rect),
  textos:[...document.querySelectorAll('g.etapa text')].map(e=>({t:e.textContent,...rect(e)})),
  lista:[...document.querySelectorAll('.lista27 .item')].map(e=>({nome:rect(e.querySelector('.nome')),faixa:e.querySelector('.faixa-barra')?rect(e.querySelector('.faixa-barra')):null,barra:rect(e.querySelector('i'))})),
  perguntas:[...document.querySelectorAll('.t22c')].map(e=>({pergunta:rect(e.querySelector('.pergunta')),valor:rect(e.querySelector('.valor')),texto:e.querySelector('.pergunta').textContent})),
  colunas:[...document.querySelectorAll('.cab span')].map(e=>({t:e.textContent,scroll:e.scrollWidth,client:e.clientWidth,...rect(e)}))};
const p=document.createElement('pre');p.id='qa-r6';p.style.display='none';p.textContent=JSON.stringify(out);document.body.appendChild(p);
});"""


def validar_browser(c,prova):
    nome=c['nome']
    assert prova['viewport']=={'w':c['largura'],'h':c['altura']},(nome,prova['viewport'])
    if nome.startswith('T28') and prova['barras']:
        assert all(b['w']>0 and b['h']>0 and b['x']>=0 and b['y']>=0 and b['x']+b['w']<=c['largura']+.1 and b['y']+b['h']<=355.1 for b in prova['barras']),nome
        assert all(t['x']>=-.1 and t['y']>=-.1 and t['x']+t['w']<=c['largura']+.1 and t['y']+t['h']<=355.1 for t in prova['textos']),nome
    for l in prova['lista']:
        assert l['faixa'] and l['nome']['x']+l['nome']['w']<=l['faixa']['x'],nome
    for p in prova['perguntas']:
        assert p['pergunta']['y']+p['pergunta']['h']<=p['valor']['y'],nome
    for p in prova['colunas']:assert p['scroll']<=p['client'],(nome,p)


def render_cli(casos):
    """Mesmo executável/caminho síncrono do previa.py, sem driver nem canais nomeados do Playwright."""
    chrome=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    perfil=Q/'perfil-chromium'
    relatorio=[]
    for c in casos:
        nome=c['nome'];doc=(Q/(nome+'-depois.html')).read_text(encoding='utf-8')
        doc=doc.replace('</body>',f'<script>{JS_QA}</script></body>')
        alvo=Q/(nome+'-captura.html');alvo.write_text(doc,encoding='utf-8')
        png=Q/(nome+'-depois.png');window_h=c['altura']
        for tentativa in range(2):
            r=subprocess.run([str(chrome),'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',
                '--disable-background-networking','--force-prefers-reduced-motion',f'--user-data-dir={perfil}',
                f'--window-size={c["largura"]},{window_h}','--virtual-time-budget=2000','--dump-dom',f'--screenshot={png}',alvo.as_uri()],
                capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=25)
            (Q/(nome+'-chromium.log')).write_text(r.stderr,encoding='utf-8')
            m=re.search(r'<pre id="qa-r6"[^>]*>(.*?)</pre>',r.stdout,re.S)
            if not m:
                raise RuntimeError('Chromium não retornou a prova DOM: '+r.stderr[-400:])
            prova=json.loads(html.unescape(m[1]))
            if prova['viewport']=={'w':c['largura'],'h':c['altura']}:break
            window_h+=c['altura']-prova['viewport']['h']
        assert prova['viewport']=={'w':c['largura'],'h':c['altura']},(nome,prova['viewport'])
        assert png.exists(),nome
        medidas=struct.unpack('>II',png.read_bytes()[16:24])
        assert medidas==(c['largura'],c['altura']),(nome,medidas)
        if nome.startswith('T28') and prova['barras']:
            assert all(b['w']>0 and b['h']>0 and b['x']>=0 and b['y']>=0 and b['x']+b['w']<=c['largura']+.1 and b['y']+b['h']<=355.1 for b in prova['barras']),nome
            assert all(t['x']>=-.1 and t['y']>=-.1 and t['x']+t['w']<=c['largura']+.1 and t['y']+t['h']<=355.1 for t in prova['textos']),nome
        for l in prova['lista']:
            assert l['faixa'] and l['nome']['x']+l['nome']['w']<=l['faixa']['x'],nome
        for p in prova['perguntas']:
            assert p['pergunta']['y']+p['pergunta']['h']<=p['valor']['y'],nome
        for p in prova['colunas']:assert p['scroll']<=p['client'],(nome,p)
        relatorio.append({'nome':nome,**prova,'png':png.name})
    (Q/'prova-browser.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Chromium:',len(relatorio),'capturas com viewport e geometrias conferidos.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--render-cli',action='store_true');args=ap.parse_args()
    casos=preparar()
    if args.render:renderizar(casos)
    if args.render_cli:render_cli(casos)
