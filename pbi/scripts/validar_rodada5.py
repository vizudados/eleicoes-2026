"""Oráculos e medidas estáticas da rodada 5. Não consulta o motor nem opera o Desktop."""
from collections import defaultdict, Counter
import csv
from html import unescape
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import sys
import subprocess
import types
from html import escape

import montar_pbip as mp
import pbip_lib as lib
import gerar_modelo as gm
import dax_para_tmdl as dpt
import estilo
from fontes_painel import corpus, usa_mao
from fontTools.ttLib import TTFont

PBI = Path(__file__).resolve().parents[1]
RAIZ = PBI.parent
QA = PBI/'qa/rodada5'


def csv_ler(nome):
    with (RAIZ/nome).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def compacto(dados):
    return len(json.dumps(dados,ensure_ascii=False,separators=(',',':')).encode('utf-8'))


def strings(dados):
    return sum(len(v) for r in dados for v in r.values() if isinstance(v,str))


def compiled(itens,pagina,nome):
    doc = next(i.doc for i in itens if isinstance(i,lib.Visual) and i.pagina==pagina and i.doc['name']==nome)
    raw = doc['visual']['objects']['vega'][0]['properties']['jsonSpec']['expr']['Literal']['Value']
    return json.loads(raw[1:-1].replace("''", "'"))


def main():
    QA.mkdir(exist_ok=True)
    erros=[]
    def exigir(c,m):
        if not c:erros.append(m)
    mun=csv_ler('dados/pbi/municipio.csv')
    m={r['cd_ibge']:r for r in mun}
    anos=csv_ler('dados/pbi/municipio_ano.csv')
    a={(r['ano'],r['cd_ibge']):r for r in anos}
    seg=csv_ler('dados/pbi/municipio_2turno.csv')
    b={(r['ano'],r['cd_ibge']):r for r in seg}
    uf1=csv_ler('dados/pbi/candidato_uf.csv')
    uf2=csv_ler('dados/pbi/uf_2turno.csv')
    ini=defaultdict(int);fim=defaultdict(int)
    for r in uf1:
        if r['ano']=='2026':ini[r['uf']]+=int(r['votos'])*(1 if r['numero']=='13' else -1 if r['numero']=='22' else 0)
    for r in uf2:
        if r['ano']=='2026':fim[r['uf']]+=int(r['pt'])-int(r['adv'])
    mov={u:fim[u]-ini[u] for u in ini}
    top=sorted((u for u in mov if u!='ZZ'),key=lambda u:(-mov[u],u))[:9]
    total=sum(mov.values());primeiro=sum(ini.values());ultimo=sum(fim.values())
    exigir((primeiro,total,ultimo)==(-2224965,6655156,4430191),'Fechamento nacional da ponte')
    exigir(sum(mov[u] for u in top[:3])==2764814,'SP/MG/RJ no topo da ponte')
    exigir(all(v>0 for v in mov.values()),'Nem toda UF andou para Lula')
    etapas=[{'nome':'1º turno','de':0,'ate':primeiro,'v':primeiro}]
    pos=primeiro
    for u in top:
        etapas.append({'nome':u,'de':pos,'ate':pos+mov[u],'v':mov[u]});pos+=mov[u]
    outros=sum(v for u,v in mov.items() if u not in top and u!='ZZ')
    etapas.append({'nome':'Outros 18 estados','de':pos,'ate':pos+outros,'v':outros});pos+=outros
    etapas.append({'nome':'Exterior','de':pos,'ate':pos+mov['ZZ'],'v':mov['ZZ']});pos+=mov['ZZ']
    etapas.append({'nome':'2º turno','de':0,'ate':ultimo,'v':ultimo})
    exigir(pos==ultimo,'Etapas agrupadas não fecham')
    # Refatoração geométrica do T19: omitir vazios no desenho equivale a filtrar a tabela de pontos.
    for mask in range(64):
        pts=[(i,round(i*25.6+4,1),None if mask&(1<<i) else (i-2)*.13) for i in range(6)]
        validos=[p for p in pts if p[2] is not None]
        antigo=' '.join(('M'if j==0 else'L')+f'{p[1]},{p[2]}'for j,p in enumerate(validos))
        primeiro_valido=min((p[0]for p in validos),default=None)
        novo=' '.join(' '.join(('M'if p[0]==primeiro_valido else'L')+f'{p[1]},{p[2]}'if p[2] is not None else''for p in pts).split())
        exigir(antigo==novo,'Caminho do T19 mudou na máscara '+str(mask))
    pontes_ufs={}
    viradas=[];t27antes=[];t27depois=[];t28antes=[]
    for r in mun:
        cod=r['cd_ibge'];f=a[('2026',cod)];s=b[('2026',cod)]
        d1=int(f['pt'])-int(f['adv']);d2=int(s['pt'])-int(s['adv']);delta=d2-d1;ganho=int(s['pt'])-int(f['pt'])
        pontes_ufs[r['uf']]=pontes_ufs.get(r['uf'],[0,0,0])
        pontes_ufs[r['uf']][0]+=d1;pontes_ufs[r['uf']][1]+=delta;pontes_ufs[r['uf']][2]+=d2
        xy={k:float(r[k]) if r[k] else None for k in ['x','y']}
        form=lambda v:('+' if v>0 else '-' if v<0 else '')+f'{abs(v):,}'.replace(',','.')
        for lista,valor in [(t27antes,ganho),(t28antes,delta)]:
            lista.append({'cod':cod,'uf':r['uf'],'rotulo':r['rotulo'],**xy,'val':valor,'tam':abs(valor),'valorTexto':form(valor)})
        t27depois.append({'cod':cod,**xy,'val':ganho})
        if d1*d2<0:
            viradas.append({'cod':cod,**xy,'val':delta})
    exigir(len(viradas)==212,'Mapa de viradas precisa ter 212 linhas')
    exigir(sum(r['val']>0 for r in viradas)==211 and sum(r['val']<0 for r in viradas)==1,'Sentidos das viradas')
    exigir(next(r['cod'] for r in viradas if r['val']<0)=='5221577','Uirapuru, GO, sentido contrário')
    exigir(all(x+y==z for x,y,z in pontes_ufs.values()),'Ponte municipal de alguma UF não fecha')
    exigir(all(v[0]==ini[u] and v[2]==fim[u] for u,v in pontes_ufs.items()),'Municipal e UF têm universos incompatíveis no voto')
    exigir(strings(t27antes)==167764 and strings(t28antes)==166018,'Simulação não reproduz caracteres do motor nos mapas antigos')
    # As mesmas oito linhas da antiga janela Vega, agora emitidas como HTML e com Top N no servidor.
    lista27=[]
    for i,r in enumerate(sorted(t27depois,key=lambda r:(-r['val'],r['cod']))[:8]):
        v=r['val'];larg=330*v/900000
        fmt=lambda x:format(x,'.2f').rstrip('0').rstrip('.')
        rot=escape(m[r['cod']]['rotulo'],quote=True).replace('&#x27;','&#39;')
        valor=('+'if v>0 else'−'if v<0 else'')+f'{abs(v):,}'.replace(',','.')
        texto=(f"<div class='tela lista27'><div class='item' style='top:{30+i*29}px'><span class='nome'>{rot}</span>"
               f"<i style='left:350px;width:{fmt(larg)}px;background:var(--vermelho)'></i><b class='valor num'>{valor}</b></div></div>")
        lista27.append({'cod':r['cod'],'html':texto})
    # T21: quadros iguais, apenas um portador; margens de desenho em inteiros, números analíticos não mudam.
    cand=csv_ler('dados/pbi/candidato_ano.csv');years=[2006,2010,2014,2018,2022,2026];quadros=[]
    for ano in years:
        rows=[r for r in cand if int(r['ano'])==ano]
        pt=sum(int(r['votos']) for r in rows if r['partido']=='PT');adv=max(int(r['votos']) for r in rows if r['partido']!='PT')
        margem=(pt-adv)/int(rows[0]['validos'])
        n=sum(int(r['pt'])>int(r['adv']) for r in anos if int(r['ano'])==ano)
        quadros.append(f'{ano}|{n}|{margem:.4f}')
    packed=';'.join(quadros);primeiro_cod=min(m)
    t21antes=[];t21depois=[];erro_cor=0
    for cod,r in m.items():
        xy={k:float(r[k]) if r[k] else None for k in ['x','y']}
        orig={'cod':cod,**xy,'anos':packed};novo={'cod':cod,**{k:round(v*100) if v is not None else None for k,v in xy.items()},'anos':packed if cod==primeiro_cod else None}
        for ano in years:
            ar=a.get((str(ano),cod));margem=(int(ar['pt'])-int(ar['adv']))/int(ar['validos']) if ar and int(ar['validos']) else None
            campo=f'm{ano%100:02d}';orig[campo]=margem;novo[campo]=round(margem*1000000) if margem is not None else None
            if margem is not None:erro_cor=max(erro_cor,abs(novo[campo]/1000000-margem))
        t21antes.append(orig);t21depois.append(novo)
    exigir(strings(t21antes)==612810,'Fixture T21 não reproduz caracteres medidos pela main')
    exigir(erro_cor<=0.000000500001,'Quantização da cor excede 0,00005 ponto percentual')
    exigir(all(o[k]==n[k]/100 for o,n in zip(t21antes,t21depois) for k in ['x','y'] if o[k] is not None),'Coordenada não preservada em centésimos')
    # Cache real da prévia anterior: conserva exatamente os primeiros 16 HTMLs, corta os demais.
    class Frames(HTMLParser):
        def __init__(self):super().__init__();self.docs=[]
        def handle_starttag(self,t,attrs):
            if t=='iframe':
                d=dict(attrs)
                if 'srcdoc'in d:self.docs.append(d['srcdoc'])
    html19=PBI/'qa/previa/T19.html';cache19={}
    if html19.exists():
        import re
        parser=Frames();parser.feed(html19.read_text(encoding='utf-8'))
        doc=next((s for s in parser.docs if "class='tela t19l'"in s),'')
        linhas=re.findall(r"<div class='tela t19l'>.*?</div></div>",doc,re.S)
        if linhas:
            # A ordem de chegada do dataset não é o ranking; a posição visual está no top da linha.
            top16=sorted((s for s in linhas if (p:=re.search(r"style='top:(\d+)px'",s)) and int(p.group(1))<=36+15*44),
                         key=lambda s:int(re.search(r"style='top:(\d+)px'",s).group(1)))
            exigir(len(top16)==16,'Cache do Explorador não contém exatamente as 16 primeiras posições')
            maiores=sorted(mun,key=lambda r:-int(a[('2026',r['cd_ibge'])]['validos']))[:16]
            html_antes=sum(map(len,linhas));html_depois=sum(len(s) for s in top16)
            cache19={'origem':'prévia real anterior em cache; não é nova execução do motor','linhas_antes':len(linhas),'caracteres_antes':sum(map(len,linhas)),
                     'linhas_depois':len(top16),'caracteres_depois':html_depois,
                     'consulta_texto_antes':html_antes+sum(len(r['rotulo'])for r in mun),
                     'consulta_texto_depois':html_depois+sum(len(r['rotulo'])for r in maiores)}
            exigir(cache19['consulta_texto_antes']==3425784,'HTML mais coluna de rótulo não reproduz controle da main')
    # Fontes: todos os pontos do corpus que existiam na fonte de origem continuam no subset correspondente.
    cobertura={}
    for familia,nome,original in [('sora','sora-painel','sora-eleicoes'),('caveat','caveat-notas','caveat-eleicoes')]:
        old=TTFont(PBI/f'assets/fontes/{original}.woff2');new=TTFont(PBI/f'assets/fontes/{nome}.woff2')
        required={ord(c) for c in corpus()[familia]}&set(old.getBestCmap())
        exigir(required<=set(new.getBestCmap()),'Faltam glifos em '+familia)
        oc=old.getBestCmap();nc=new.getBestCmap()
        metricas_iguais=all(old['hmtx'][oc[c]]==new['hmtx'][nc[c]] for c in required)
        exigir(metricas_iguais,'Métricas da fonte mudaram em '+familia)
        cobertura[familia]={'bytes_antes':(PBI/f'assets/fontes/{original}.woff2').stat().st_size,'bytes_depois':(PBI/f'assets/fontes/{nome}.woff2').stat().st_size,'glifos_requeridos':len(required),'faltantes':len(required-set(new.getBestCmap()))}
        cobertura[familia]['metricas_iguais']=metricas_iguais
    ctx=mp.carregar_contexto();meds=[dpt.ler(p) for p in (PBI/'dax').rglob('*.dax') if '_modelo'not in p.parts]
    ctx.medidas.update(r['nome'] for r in meds);tabs,rels,_=gm.carregar_declaracoes();ctx.colunas.update((t['nome'],c['nome']) for t in tabs for c in t['colunas'])
    itens=mp.carregar_declaracoes(ctx);erros+=mp.conferir(itens,ctx)
    # Comparação de configuração completa: os controles arrastáveis mantêm IDs, caixas e propriedades.
    antigo=types.ModuleType('t22_baseline')
    fonte_antiga=subprocess.run(['git','show','HEAD:pbi/scripts/paginas/t22_simulador.py'],capture_output=True,check=True).stdout.decode('utf-8')
    exec(compile(fonte_antiga,'t22_baseline','exec'),antigo.__dict__)
    controles=lambda xs:{i.doc['name']:i.doc for i in xs if isinstance(i,lib.Visual) and i.pagina=='T22' and i.doc['name'].endswith('_Regua')}
    controle_antes=controles(antigo.declarar(ctx));controle_depois=controles(itens)
    exigir(len(controle_depois)==3 and controle_antes==controle_depois,'Configurações dos três VizuFilter mudaram')
    fixtures=[('T27','T27_Mapa_Municipios',t27depois,740,520),('T28','T28_Mapa_Municipios',viradas,780,275),('T21','T21_Mapa_Deneb',t21depois,1620,860)]
    for pagina,nome,dados,w,h in fixtures:
        spec=compiled(itens,pagina,nome)
        (QA/f'{pagina}-mapa.json').write_text(json.dumps({'spec':spec,'dados':dados,'largura':w,'altura':h},ensure_ascii=False),encoding='utf-8')
    medidas_peso={'T27 mapa':{'antes_linhas':5571,'depois_linhas':5571,'antes_texto':strings(t27antes),'depois_texto':strings(t27depois),'antes_json_bytes':compacto(t27antes),'depois_json_bytes':compacto(t27depois)},
                   'T27 lista':{'antes_linhas':5571,'depois_linhas':8,'antes_texto':strings(t27antes),'depois_texto':strings(lista27),'antes_json_bytes':compacto(t27antes),'depois_json_bytes':compacto(lista27)},
                   'T28 mapa':{'antes_linhas':5571,'depois_linhas':len(viradas),'antes_texto':strings(t28antes),'depois_texto':strings(viradas),'antes_json_bytes':compacto(t28antes),'depois_json_bytes':compacto(viradas)},
                   'T21 mapa':{'antes_linhas':5571,'depois_linhas':5571,'antes_texto':strings(t21antes),'depois_texto':strings(t21depois),'antes_json_bytes':compacto(t21antes),'depois_json_bytes':compacto(t21depois)}}
    r={'escopo':'CSV, cache anterior e plano local; sem motor DAX ou Desktop','ponte':{'inicio':primeiro,'movimento':total,'fim':ultimo,'top3':sum(mov[u]for u in top[:3]),'parcela':sum(mov[u]for u in top[:3])/total,'etapas':etapas,'ponte_ufs':len(pontes_ufs)},
       'payloads_estimados':medidas_peso,'T19_cache':cache19,'fontes':cobertura,'T21_erro_maximo_fracao':erro_cor,'quadros_t21_caracteres':len(packed),
       'controles_t22_identicos':controle_antes==controle_depois,'mascaras_geometria_t19':64,'tabelas':len(tabs),'relacoes':len(rels),'erros':erros}
    (QA/'provas-locais.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2))
    return bool(erros)


if __name__=='__main__':
    raise SystemExit(main())
