"""Provas offline do Antes/Depois. Não conecta ao Desktop nem avalia DAX.

Concilia CSV, contratos declarativos e referências; simula HTML com dados reais e CSS do gerador.
Render opcional em Chromium headless, viewport real. Interação/sincronia requerem prova posterior no Desktop.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import html
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import desenho_t02_t04 as Q
import desenho_t03_t05 as V
import gerar_modelo as gm
import momento_eleicao as M
import montar_pbip as mp
import pbip_lib as lib
import roteiro
import estilo
import dax_para_tmdl as dpt
from paginas import casca
from validar_dax_gerado import problemas

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'pbi/qa/quem-e'
esc = html.escape


def ler(nome):
    with (ROOT / nome).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def num(v):
    return f'{v:,}'.replace(',', '.')


def pct(v, n=1):
    return f'{100*v:.{n}f}'.replace('.', ',') + '%'


def mi(v):
    return f'{v/1000000:.2f}'.replace('.', ',') + ' mi'


def documento(conteudo, css=''):
    # Mesma árvore de host que previa.py, sem consulta ao motor.
    doc = ("<!doctype html><html><head><meta charset='utf-8'><style>" + estilo.css_base() + css +
           "html,body{margin:0;overflow:hidden;background:transparent}*,*::before,*::after{animation:none!important;transition:none!important}"
           "</style></head><body><div id='sandbox-host'><div id='htmlViewer'><div class='os-padding'>"
           "<div class='os-viewport'><div class='os-content'><div id='htmlContent'>" + conteudo +
           "</div></div></div></div></div></div></body></html>")
    return doc.replace(Q.URL_MIDIA + '/', (ROOT / 'docs/midia').as_uri() + '/')


def ficha(p, pos, uf):
    l = Q.LADOS[p]
    n = 'pt' if p == 'T02' else 'adv'
    rows = [r for r in uf if r['ano'] == '2026']
    if pos:
        votos = sum(int(r[n]) for r in rows); validos = sum(int(r['validos']) for r in rows)
    else:
        cu = [r for r in ler('dados/pbi/candidato_uf.csv') if r['ano'] == '2026']
        votos = sum(int(r['votos']) for r in cu if int(r['numero']) == l['numero'])
        validos = sum(int(r['votos']) for r in cu)
    desde = 1975 if p == 'T02' else 2002
    fotos = (8 if p == 'T02' else 10) - int(pos and p not in Q.imagens_pos())
    foto_txt = 'todos com foto da época' if fotos == 10 else f'{fotos} com foto da época'
    foto_txt += ', 2 em ilustração recriada' if p == 'T02' else ''
    situacao = ('eleito' if p == 'T02' else '2º lugar') if pos else ('2º lugar' if p == 'T02' else '1º lugar')
    linhas = [('Na vida pública desde', str(desde), f'há {2026-desde} anos', ''),
              (f'No {2 if pos else 1}º turno de 2026', mi(votos), f'de votos · {pct(votos/validos, 2 if pos else 1)} · {situacao}', l['cls']),
              ('Na linha do tempo abaixo', '10', 'marcos, ' + foto_txt, '')]
    return "<div class='tela fc'>" + ''.join(
        f"<div class='lin'><div class='rot'>{a}</div><div class='val'><span class='{cl}'>{b}</span><small>{c}</small></div></div>"
        for a,b,c,cl in linhas) + '</div>'


def marcos(p, pos):
    rows = [r for r in ler('dados/pbi/trajetoria.csv') if r['candidato'] == Q.LADOS[p]['cand']]
    rows.sort(key=lambda r:int(r['ordem']))
    if pos:
        rows[-1] = {**rows[-1], 'titulo': 'Reeleito com recorde histórico' if p == 'T02' else 'Ficou em segundo lugar', 'data':'2026-10-25'}
    ini = int(rows[0]['ano']); seg = int(rows[1]['ano']); fim = 2026
    corte = seg-ini>8; t0=math.floor((ini-1)/5)*5; t1=math.ceil((fim+2)/5)*5
    xano = lambda a: 30+(a-(ini-1.5))*200/3 if corte and a<=ini+1.5 else (274+(a-(seg-1))*1316/(fim+1-(seg-1)) if corte else 30+(a-t0)*1560/(t1-t0))
    anos = [ini]+list(range(math.ceil((seg-1)/5)*5, math.floor((fim+1)/5)*5+1, 5)) if corte else list(range(t0,t1+1,5))
    regua = ("<div class='cab'><span class='sob'>Trajetória política · 10 marcos</span><span class='dica'>"
             "passe o mouse num marco para ver a foto da época, redesenhada em traço</span></div>"
             "<svg class='regua' width='1620' height='364'>")
    if corte:
        regua += "<path class='eixo' d='M30 296H230 M274 296H1590'/><path class='eixo' d='M242 304l8-16m4 16l8-16'/>"
    else:regua += "<path class='eixo' d='M30 296H1590'/>"
    regua += "<g class='anos'>" + ''.join(f"<path stroke='#49443E' d='M{xano(a):.2f} 290v12'/><text x='{xano(a):.2f}' y='324'>{a}</text>" for a in anos) + '</g></svg>'
    out=[]
    for i,r in enumerate(rows):
        a=int(r['ano']); date=r['data']; tm=a+0.5
        if len(date)==10:tm=a+(dt.date.fromisoformat(date)-dt.date(a,1,1)).days/365
        x=xano(tm); xs=(i+.5)*162; destaque=pos and p=='T02' and i==9
        ico='✎' if i<2 and p=='T02' else '▣'
        if pos and i==9 and p not in Q.imagens_pos():ico=''
        out.append("<div class='tela m'>" + (regua if i==0 else '') +
            f"<svg class='liga' width='1620' height='364'><path class='fio' d='M{xs} {232 if destaque else 176}L{xs} {242 if destaque else 200}L{x:.2f} 262V287'/>"
            f"<circle class='ponto' cx='{x:.2f}' cy='296' r='{12 if destaque else 7}'/></svg>"
            f"<div class='alvo card {'recorde' if destaque else ''}' style='left:{xs-76}px'><div class='ano nc'>{a} {ico}</div>"
            f"<div class='tt'>{esc(r['titulo'])}</div>" + ("<div class='mao nota-recorde'>recorde</div>" if destaque else '') + '</div></div>')
    return ''.join(out)


def dados_votos(p, pos, uf=None):
    col = 'pt' if p=='T03' else 'adv'
    other = 'adv' if col=='pt' else 'pt'
    m = {r['cd_ibge']:r for r in ler('dados/pbi/municipio.csv')}
    ano = ler('dados/pbi/municipio_2turno.csv' if pos else 'dados/pbi/municipio_ano.csv')
    a = {r['cd_ibge']:r for r in ano if r['ano']=='2026' and (not uf or m[r['cd_ibge']]['uf']==uf)}
    if pos:
        us = [r for r in ler('dados/pbi/uf_2turno.csv') if r['ano']=='2026' and (not uf or r['uf']==uf)]
        votos=sum(int(r[col]) for r in us); validos=sum(int(r['validos']) for r in us)
    else:
        us=[r for r in ler('dados/pbi/candidato_uf.csv') if r['ano']=='2026' and (not uf or r['uf']==uf)]
        votos=sum(int(r['votos']) for r in us if int(r['numero'])==(13 if col=='pt' else 22));validos=sum(int(r['votos']) for r in us)
    frente=[r for r in a.values() if int(r[col])>int(r[other])]
    reg={}
    for cod,r in a.items():
        regiao=m[cod]['regiao'];v=int(r[col]);va=int(r['validos'])
        acc=reg.setdefault(regiao,[0,0]);acc[0]+=v;acc[1]+=va
    dados=[{'cod':cod,'uf':m[cod]['uf'],'x':float(m[cod]['x']),'y':float(m[cod]['y']),
            'tam':int(r[col]),'val':(int(r[col])-int(r[other]))/int(r['validos'])} for cod,r in a.items() if m[cod]['x'] and m[cod]['y']]
    return dict(votos=votos,validos=validos,municipios=len(a),frente=len(frente),
                eleitores=sum(int(r['aptos']) for r in frente)/sum(int(r['aptos']) for r in a.values()),regioes=reg,dados=dados)


def resumo_votos(p, pos, data):
    l=V.LADOS[p];cl=l['cls'];col='pt' if p=='T03' else 'adv'
    if pos:
        u=[r for r in ler('dados/pbi/uf_2turno.csv') if r['ano']=='2026' and r['uf']!='ZZ']
        u22=[r for r in ler('dados/pbi/uf_2turno.csv') if r['ano']=='2022']
        v22=sum(int(r[col]) for r in u22);p22=v22/sum(int(r['validos']) for r in u22)
        ufs={r['uf']:int(r[col])/int(r['validos']) for r in u}
    else:
        u=[r for r in ler('dados/pbi/candidato_uf.csv') if r['ano']=='2026' and r['uf']!='ZZ']
        total={r['uf']:sum(int(x['votos']) for x in u if x['uf']==r['uf']) for r in u}
        ufs={r['uf']:int(r['votos'])/total[r['uf']] for r in u if int(r['numero'])==l['numero']}
        u22=[r for r in ler('dados/pbi/candidato_uf.csv') if r['ano']=='2022']
        v22=sum(int(r['votos']) for r in u22 if int(r['numero'])==l['numero']);p22=v22/sum(int(r['votos']) for r in u22)
    v=data['votos'];pc=v/data['validos'];dv=v-v22;pp=(pc-p22)*100
    nm='Lula' if p=='T03' else 'Flávio';nm22='Lula' if p=='T03' else 'Jair Bolsonaro'
    mun={r['cd_ibge']:r for r in ler('dados/pbi/municipio.csv')}
    a=[r for r in ler('dados/pbi/municipio_2turno.csv' if pos else 'dados/pbi/municipio_ano.csv') if r['ano']=='2026']
    grandes=[r for r in a if int(mun[r['cd_ibge']]['populacao'] or 0)>=100000]
    g=max(grandes,key=lambda r:int(r[col])/int(r['validos']))
    forte=max(ufs,key=ufs.get);fraco=min(ufs,key=ufs.get)
    uf_nome={r['uf']:r['nome'] for r in ler('dados/dimensoes/uf.csv')} if (ROOT/'dados/dimensoes/uf.csv').exists() else {}
    # Nomes do modelo, sem nova fonte externa.
    nomes={'PI':'Piauí','RR':'Roraima','AC':'Acre','SC':'Santa Catarina','BA':'Bahia'}
    fatos=[('UF mais forte',nomes.get(forte,uf_nome.get(forte,forte)),pct(ufs[forte]),cl),
           ('UF mais fraca',nomes.get(fraco,uf_nome.get(fraco,fraco)),pct(ufs[fraco]),''),
           ('Entre as cidades de 100 mil+',mun[g['cd_ibge']]['rotulo'],pct(int(g[col])/int(g['validos'])),cl)]
    posicao=(1 if p=='T03' else 2) if pos else (2 if p=='T03' else 1)
    signed=lambda x:('−' if x<0 else '+')+mi(abs(x))
    txt_pp=('−' if pp<0 else '+')+f'{abs(pp):.1f}'.replace('.',',')
    corpo=(f"<div class='tela rv'><div class='sob'>{l['completo']} · {l['sigla']} · {l['numero']} · BRASIL</div>"
        f"<div class='topo'><div class='big {cl} {'pos' if pos else ''}'>{pct(pc,2 if pos else 1)}</div>"
        f"<div class='lado'><div class='vv {cl}'>{mi(v)}</div><div class='txt'>de votos · {posicao}º lugar</div></div></div>"
        f"<div class='man mc'>{nm} ficou à frente em {num(data['frente'])} dos {num(data['municipios'])} municípios, onde votam {pct(data['eleitores'],0)} dos eleitores</div>"
        f"<div class='txt cp'>Em 2022, {nm22} teve {mi(v22)} ({pct(p22)}). Agora: <b class='{cl}-esc'>{signed(dv)} de votos</b> e "
        f"<b class='{cl}-esc'>{txt_pp} pontos</b>.</div><div class='fatos'>")
    corpo+=''.join(f"<div class='fato'><span class='ic {ico}'></span><div><div class='rot'>{rot}</div><div class='lg'>{esc(nome)}</div></div><div class='vp {c}'>{valor}</div></div>" for (rot,nome,valor,c),ico in zip(fatos,['f','r','g']))
    return corpo+'</div></div>'


def origem_votos(data):
    regs=sorted(data['regioes'].items(),key=lambda a:-a[1][0]);total=sum(x[0] for _,x in regs);inicio=0;out=V.ORIGEM_FIXO
    for i,(reg,(v,va)) in enumerate(regs,1):
        parte=v/total;w=parte*620;rot=reg+' '+pct(parte,0) if w>=120 else pct(parte,0) if w>=44 else ''
        out+=(f"<div class='tela og'><div class='oc'><div class='fa o{i}' style='left:{inicio:.2f}px;width:{w:.2f}px'><span>{rot}</span></div>"
              f"<div class='li' style='top:{92+(i-1)*30}px'><i class='sw o{i}'></i><span class='nm'>{reg}</span>"
              f"<span class='a'>{pct(parte,0)} dos votos dele · {mi(v)}</span><span class='b'>{pct(v/va)} dos válidos</span></div></div></div>")
        inicio+=w
    return out


def preparar():
    OUT.mkdir(parents=True,exist_ok=True)
    tabelas,_,_=gm.carregar_declaracoes()
    medidas=dpt.coletar(ROOT/'pbi/dax')
    ctx=mp.Contexto(medidas={m['nome'] for m in medidas},colunas={(t['nome'],c['nome']) for t in tabelas for c in t['colunas']})
    itens=casca.declarar(ctx)
    for p in ['T02','T04']:itens+=Q.declarar_quem_e(p)
    for p in ['T03','T05']:itens+=V.declarar_votos(p)
    # Casca referencia páginas de outras telas. As provas incluem o plano completo, sem gravar no PBIP.
    itens=mp.carregar_declaracoes(ctx)
    erros=mp.conferir(itens,ctx)
    assert not erros, erros
    for m in medidas:
        if m['nome'].startswith(('T02 ·','T03 ·','T04 ·','T05 ·','Eleição ·')):
            assert not problemas('\n'.join(m['linhas'])), m['nome']
    seletores=[]
    for p in sorted(M.TELAS):
        doc=next(i.doc for i in itens if isinstance(i,lib.Visual) and i.pagina==p and i.doc['name']==p+'_Filtro_Momento')
        assert doc['visual']['syncGroup']==lib.grupo_sincronia(M.GRUPO)
        assert tuple(doc['position'][k] for k in ['x','y','width','height'])==M.CAIXA
        assert doc['position']['z']==lib.CAMADAS['filtro']<lib.CAMADAS['conteudo']
        existente=next((i.doc for i in itens if isinstance(i,lib.Visual) and i.pagina==p and i.doc['name']==p+'_Casca_Filtro'),None)
        if existente:
            assert M.CAIXA[0]+M.CAIXA[2]+16<=existente['position']['x']
        seletores.append({'pagina':p,'position':doc['position'],'sync':doc['visual']['syncGroup']})
    uf=ler('dados/pbi/uf_2turno.csv')
    rows=[r for r in uf if r['ano']=='2026']
    assert [sum(int(r[c]) for r in rows) for c in ['pt','adv','validos']]==[64256232,59826041,124082273]
    hist=ler('dados/pbi/pt_historico_brasil.csv')
    ranking=sorted([int(r[c]) for r in hist for c in ['votos_pt','votos_adv']],reverse=True)
    assert ranking[:2]==[64256232,60345999]
    provas_imagens={}
    for p,meta in Q.imagens_pos().items():
        arq=ROOT/'docs/midia/trajetoria'/(meta['arquivo']+'.png')
        raw=arq.read_bytes()
        assert raw[:8]==b'\x89PNG\r\n\x1a\n',arq
        w,h=struct.unpack('>II',raw[16:24])
        assert w*2==h*3,(arq,w,h)
        registro=Q.desenhos_csv()[meta['arquivo']]
        assert registro['credito_curto']==meta['credito'] and registro['legenda']==meta['legenda']
        trajetoria=[r for r in ler('dados/pbi/trajetoria.csv') if r['candidato']==Q.LADOS[p]['cand']]
        assert len(trajetoria)==10
        texto_cena=(ROOT/'pbi/dax'/Q.LADOS[p]['pasta']/'Desenho'/f'{p} · Cena · HTML.dax').read_text(encoding='utf-8')
        assert '/trajetoria/'+meta['arquivo']+'.png' in texto_cena
        provas_imagens[p]={'arquivo':str(arq.relative_to(ROOT)),'largura':w,'altura':h,
                          'marcos':len(trajetoria),'credito_coerente':True,'cena_resolve_imagem':True}
        if p=='T04':
            assert meta['data_legenda']=='2026-10-25' and meta['cidade'] is None
            assert meta['quadro_pts_segundos']==105.012
            assert registro['autor']=='TV Senado'
            assert len([r for r in trajetoria if r['foto']])==10
    casos=[]
    for p in ['T02','T04']:
        l=Q.LADOS[p]
        for pos in [False,True]:
            nome=f'{p}-{"pos" if pos else "pre"}'
            topo=(f"<div class='tela qe'><div class='rot rotc {l['cls']}-esc'>{l['rot'].upper()}</div><h1>{l['completo']}</h1>"
                  f"<img class='ret' alt='' src='{Q.URL_MIDIA}/arte/{l['retrato']}.png'/>"
                  f"<div class='nota cred'>{l['cred_retrato']}</div>"+Q.cena_html(l,Q.imagens_pos().get(p),pos)+'</div>')
            frames=[('topo',Q.TOPO,documento(topo,Q._css_topo(l))),
                    ('ficha',(150,268,560,250),documento(ficha(p,pos,uf),Q._css_ficha(l))),
                    ('traj',Q.TRAJ,documento(marcos(p,pos),Q._css_traj(l)))]
            shell=documento(casca.corpo_casca(roteiro.POR_CODIGO[p]).replace('{{content}}',''))
            frames.insert(0,('casca',(0,0,1920,1080),shell))
            filtros=f"<div class='filtro' style='left:{M.CAIXA[0]}px;top:60px;width:{M.CAIXA[2]}px'>"+('◈ '+(M.POS if pos else M.PRE))+'⌄</div>'
            # Abertura da lista é representação do controle; sincronia real só no Desktop.
            fs=''.join(f"<iframe title='{n}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px' srcdoc='{esc(doc,quote=True)}'></iframe>"for n,(x,y,w,h),doc in frames)
            page="<!doctype html><meta charset='utf-8'><style>body{margin:0;background:#F1EBDF}iframe{position:absolute;border:0}.filtro{position:absolute;z-index:20;height:48px;box-sizing:border-box;background:#E8DFCF;border:1px solid #CBBDA2;border-radius:6px;padding:12px;font:600 16px 'Segoe UI';display:flex;justify-content:space-between}</style>"+fs+filtros
            (OUT/(nome+'.html')).write_text(page,encoding='utf-8')
            for n,box,doc in frames:
                (OUT/(nome+'-'+n+'.html')).write_text(doc,encoding='utf-8')
            casos.append({'nome':nome,'largura':1920,'altura':1080})
            r=next(r for r in ler('dados/pbi/trajetoria.csv') if r['candidato']==l['cand'] and r['ordem']=='10')
            meta=Q.imagens_pos().get(p) if pos else Q.desenhos_csv().get(r['foto'],{})
            titulo=('Reeleito com recorde histórico' if p=='T02' else 'Ficou em segundo lugar') if pos else r['titulo']
            if pos:
                arq=ROOT/'pbi/dax'/l['pasta']/'Contas'/f'{p} · Trajetória · texto do marco.dax'
                txt=re.search(r'= 1, "((?:[^"]|"")*)",',arq.read_text(encoding='utf-8'))[1].replace('""','"')
            else:txt=r['texto']
            posicao_tt=l.get('foto_posicao_tooltip','15% 50%') if pos else '50% 30%'
            img=(f"<img class='foto' style='object-position:{posicao_tt}' src='{Q.URL_MIDIA}/trajetoria/{meta.get('arquivo',r['foto'])}.png'/>" if meta else
                 f"<img class='foto reserva' src='{Q.URL_MIDIA}/arte/icones/jornal-tinta.png'/><div class='sem mao'>sem foto de licença aberta</div>")
            leg=meta.get('legenda','') if meta else '';cred=(meta.get('credito') or meta.get('credito_curto','')) if meta else ''
            tt=(f"<div class='tt2 {'final' if pos else ''}'><div class='pol'>{img}<div class='ano mao nc'>2026</div><img class='fita' src='{Q.URL_MIDIA}/arte/dossie/fita-tinta.png'/></div>"
                f"<div class='col'><div class='rot {l['cls']}-esc'>{'25' if pos else '4'} de outubro de 2026</div><div class='man'>{titulo}</div>"
                f"<div class='txt'>{esc(txt)}</div>"+(f"<div class='pe'><div class='nota lg'>{esc(leg)}</div><div class='nota cr'>{esc(cred)}</div></div>" if meta else '')+'</div></div>')
            (OUT/(nome+'-tooltip.html')).write_text(documento(tt,Q._css_tooltip(l)),encoding='utf-8')
            casos.append({'nome':nome+'-tooltip','largura':640,'altura':400})
    oraculos={}
    for p in ['T03','T05']:
        for pos in [False,True]:
            for uf_ in [None,'MG','RR','PI']:
                data=dados_votos(p,pos,uf_);nome=f'{p}-{"pos" if pos else "pre"}-'+(uf_ or 'Brasil')
                payload={'spec':V.spec_mapa('margem',V.LADOS[p]['cores'],nome,selecao=True),'dados':data.pop('dados'),'largura':970,'altura':800}
                data['pontos_com_coordenadas']=len(payload['dados'])
                (OUT/(nome+'-mapa.json')).write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
                assert sum(r['tam'] for r in payload['dados'])<=data['votos']
                if uf_:assert sum(r['tam'] for r in payload['dados'])==data['votos']
                else:assert data['municipios']==5571
                oraculos[nome]=data
                if not uf_:
                    # Executa o spec real no runtime Vega local, sem host Power BI.
                    svg=OUT/(nome+'-mapa.svg')
                    subprocess.run(['node',str(ROOT/'pbi/tools/render_vega.mjs'),str(OUT/(nome+'-mapa.json')),str(svg)],check=True,capture_output=True,timeout=30)
                    l=V.LADOS[p]
                    frames=[('casca',(0,0,1920,1080),documento(casca.corpo_casca(roteiro.POR_CODIGO[p]).replace('{{content}}',''))),
                            ('resumo',V.RESUMO,documento(resumo_votos(p,pos,data),V._css_resumo(l))),
                            ('origem',V.ORIGEM,documento(origem_votos(data),V._css_origem(l))),
                            ('mapa',V.MAPA,documento(svg.read_text(encoding='utf-8'))),
                            ('legenda',V.LEGENDA,documento(f"<div class='tela lgm'>Cada ponto é um município; tamanho = votos de {l['cand']} · cor = margem<br>{l['cand']} à frente: quanto mais escuro, maior a margem</div>",V._css_legenda(l)))]
                    fs=''.join(f"<iframe title='{n}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px' srcdoc='{esc(doc,quote=True)}'></iframe>"for n,(x,y,w,h),doc in frames)
                    page="<!doctype html><meta charset='utf-8'><style>body{margin:0;background:#F1EBDF}iframe{position:absolute;border:0}.filtro{position:absolute;top:60px;z-index:20;box-sizing:border-box;height:48px;padding:12px;background:#E8DFCF;border:1px solid #CBBDA2;border-radius:6px;font:600 16px 'Segoe UI'}</style>"+fs
                    page+=f"<div class='filtro' style='left:952px;width:314px'>◈ {M.POS if pos else M.PRE} ⌄</div><div class='filtro' style='left:1282px;width:424px'>▽ Todo o Brasil ⌄</div>"
                    (OUT/(nome+'.html')).write_text(page,encoding='utf-8')
                    for n,box,doc in frames:(OUT/(nome+'-'+n+'.html')).write_text(doc,encoding='utf-8')
                    casos.append({'nome':nome,'largura':1920,'altura':1080})
    (OUT/'oraculos.json').write_text(json.dumps(oraculos,ensure_ascii=False,indent=2),encoding='utf-8')
    # Specs e declarações de preparação; o destino é exclusivamente QA.
    docs=[{'tipo':type(i).__name__,'pagina':getattr(i,'pagina',None),'doc':i.doc}for i in itens if isinstance(i,(lib.Pagina,lib.Visual)) and (getattr(i,'pagina',i.doc.get('name')) in M.TELAS or i.doc.get('name') in {'ttT02Marco','ttT04Marco'})]
    (OUT/'declaracoes.json').write_text(json.dumps(docs,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'Momento eleição.tmdl').write_text(gm.tmdl_tabela(next(t for t in tabelas if t['nome']=='Momento eleição')),encoding='utf-8')
    rel={'escopo':'Offline: sem Desktop, sem execução DAX, sem aplicação PBIP','seletores':seletores,'referencias_erros':erros,
         'total_lula':64256232,'total_flavio':59826041,'diferenca':4430191,'recorde_anterior':60345999,
         'imagens_prontas':list(Q.imagens_pos()),'provas_imagens':provas_imagens,'casos':casos}
    (OUT/'validacao.json').write_text(json.dumps(rel,ensure_ascii=False,indent=2),encoding='utf-8')
    links=''.join(f"<li><a href='{c['nome']}.html'>{esc(c['nome'])}</a> · {c['largura']}×{c['altura']}</li>"for c in casos)
    (OUT/'index.html').write_text("<!doctype html><meta charset='utf-8'><title>Quem é · Antes/Depois · QA</title>"
        "<h1>Simulações locais de Antes/Depois</h1><p>HTML e CSS dos geradores com números dos CSV. "
        "Sem execução DAX, sem Power BI. Os seletores são representações do gatilho, não o runtime VizuFilter. "
        + ("Imagem Pós de Flávio: quadro da TV Senado com atribuição conferida. " if 'T04' in Q.imagens_pos() else "Foto Pós de Flávio pendente de licença aberta. ")
        + "Abrir as páginas a 1920×1080 e os tooltips a 640×400.</p>"
        '<ul>'+links+'</ul>',encoding='utf-8')
    print('Declarações e fontes: OK; 4 estados quem-é; 16 recortes municipais; TMDL somente em QA.')
    return casos


def extensao():
    """Oráculo independente para as quatro páginas seguintes, em todos os municípios/UFs."""
    mun={r['cd_ibge']:r for r in ler('dados/pbi/municipio.csv')}
    out={}
    for turno,arq in [(1,'municipio_ano.csv'),(2,'municipio_2turno.csv')]:
        rows=ler('dados/pbi/'+arq)
        ix={(r['ano'],r['cd_ibge']):r for r in rows if r['ano'] in {'2022','2026'}}
        cells={};virou=voltou=0;faltam=0
        for cod,m in mun.items():
            a=ix.get(('2022',cod));b=ix[('2026',cod)]
            if a:
                da=int(a['pt'])-int(a['adv']);db=int(b['pt'])-int(b['adv'])
                virou+=int(da>0 and db<0);voltou+=int(da<0 and db>0)
            else:faltam+=1
            key=m['porte']+' / '+m['quinto']
            acc=cells.setdefault(key,{'2022':[0,0],'2026':[0,0]})
            for yr,r in [('2022',a),('2026',b)]:
                if r:acc[yr][0]+=int(r['pt'])-int(r['adv']);acc[yr][1]+=int(r['validos'])
        delta={k:(v['2026'][0]/v['2026'][1]-v['2022'][0]/v['2022'][1])*100 for k,v in cells.items() if v['2022'][1] and v['2026'][1]}
        us=ler('dados/pbi/uf_2turno.csv') if turno==2 else ler('dados/pbi/candidato_uf.csv')
        nacional={}
        for ano in ['2022','2026']:
            uu=[r for r in us if r['ano']==ano]
            if turno==2:tot=[sum(int(r[c]) for r in uu) for c in ['pt','adv','validos']]
            else:tot=[sum(int(r['votos']) for r in uu if r['numero']==n)for n in ['13','22']]+[sum(int(r['votos']) for r in uu)]
            nacional[ano]={'lula':tot[0],'adversario':tot[1],'validos':tot[2]}
            # Soma municipal + ZZ = total nacional, para os três volumes.
            zz=[r for r in uu if r['uf']=='ZZ']
            soma=[sum(int(r[c])for (yr,_),r in ix.items()if yr==ano)for c in ['pt','adv','validos']]
            if turno==2:ex=[sum(int(r[c])for r in zz)for c in ['pt','adv','validos']]
            else:ex=[sum(int(r['votos'])for r in zz if r['numero']==n)for n in ['13','22']]+[sum(int(r['votos'])for r in zz)]
            assert [s+z for s,z in zip(soma,ex)]==tot,(turno,ano,soma,ex,tot)
        out[str(turno)]={'nacional':nacional,'viraram_para_adversario':virou,'voltaram_para_lula':voltou,
                         'sem_registro_municipal_2022':faltam,'variacao_celulas_pp':delta}
    (OUT/'oraculo-extensao.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Extensão: somas municipal + exterior conferem em 2022/2026, nos dois turnos; viradas e células calculadas.')


def render(casos):
    chrome=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    for c in casos:
        nome=c['nome'];png=OUT/(nome+'.png')
        r=subprocess.run([str(chrome),'--headless=new','--disable-gpu','--hide-scrollbars','--no-first-run',
                          '--disable-background-networking','--allow-file-access-from-files',
                          '--force-prefers-reduced-motion',f'--user-data-dir={OUT / "perfil-chromium"}',
                          f'--window-size={c["largura"]},{c["altura"]}', '--force-device-scale-factor=1',
                          '--virtual-time-budget=2500',f'--screenshot={png}',(OUT/(nome+'.html')).as_uri()],
                         capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
        if r.returncode!=0 or not png.exists():
            (OUT/'captura-local.json').write_text(json.dumps({'caso':nome,'exit_code':r.returncode,
                'png_criado':png.exists(),'stderr':r.stderr,'escopo':'Chromium local, sem Desktop'},ensure_ascii=False,indent=2),encoding='utf-8')
            raise RuntimeError('Captura local falhou; evidência em captura-local.json: '+r.stderr[-300:])
        assert struct.unpack('>II',png.read_bytes()[16:24])==(c['largura'],c['altura'])
        print('Render',nome)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--render',action='store_true');args=a.parse_args()
    cases=preparar()
    extensao()
    if args.render:render(cases)
