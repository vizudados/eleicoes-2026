"""Consolida somente MCMC aprovado e o bootstrap da execução reiniciada."""
from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dados/saida/2turno/inferencia_t16'
sp=importlib.util.spec_from_file_location('t16v2',ROOT/'pipeline/inferencia_t16_v2.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
L=m.core.LINHAS;DEST=m.core.COLUNAS
def br(v,n=1):return f'{v:,.{n}f}'.replace(',','X').replace('.',',').replace('X','.')


def canon(a,nomes,seis=True):
    if seis:
        grupos=[('Lula',['Lula']),('Flávio',['Flávio']),('Cury + Renan + Caiado',L[2:5]),('Demais candidatos',[]),(L[-2],[L[-2]]),(L[-1],[L[-1]])]
        if 'Cury + Renan + Caiado' in nomes:grupos[2]=(grupos[2][0],['Cury + Renan + Caiado'])
    else:grupos=[(s,[s]) for s in L]
    out=[];labs=[]
    conhecidos=set(L+['Cury + Renan + Caiado'])
    for nome,ss in grupos:
        ix=[i for i,s in enumerate(nomes) if s in ss]
        if nome=='Demais candidatos':ix=[i for i,s in enumerate(nomes) if s=='Demais candidatos' or s not in conhecidos]
        if ix:out.append(a[...,ix,:].sum(axis=-2));labs.append(nome)
    return np.stack(out,axis=-2),labs


def resumo(a,nomes,metodo,cenario,area='Brasil'):
    base=a[0].sum(axis=1)
    return m.core.resumo_fluxos(a,nomes,base,metodo,cenario,area=area,tipo='credibilidade_modelo_95' if metodo.startswith('bayes') else 'percentil_bootstrap_UF_95')


def coletar():
    casos=[];diags=[]
    for p in sorted(OUT.glob('diagnostico_bayes_*.json')):
        o=json.loads(p.read_text(encoding='utf-8'));key=p.stem.removeprefix('diagnostico_');diags.append({'execucao':key,**o})
        if o.get('efeito_uf') is False and 'modelo' in o:
            o['modelo']='regressão ecológica Dirichlet-multinomial com perfis regionais, sem efeito de UF'
            m.js(o,p.name)
        if o.get('convergiu') and (OUT/(key+'.csv')).exists():
            f=np.load(OUT/('amostras_'+key+'.npz'))
            casos.append({'key':key,'metodo':'bayes_dm','cenario':o['cenario'],'nomes':f['nomes'].tolist(),'areas':f['areas'].tolist(),'a':f['fluxos'],'reg':f['regioes'],'meta':o})
    for p in sorted(OUT.glob('amostras_restrito_*.npz')):
        f=np.load(p);key=p.stem.removeprefix('amostras_');tab=m.read(key+'.csv')
        casos.append({'key':key,'metodo':'restrito','cenario':str(tab.cenario.iloc[0]),'nomes':f['nomes'].tolist(),'areas':f['areas'].tolist(),'a':f['fluxos'],'reg':f['regioes']})
    m.save(pd.DataFrame(diags),'diagnostico.csv')
    return casos,diags


def comparar(casos,principal):
    sens=[];afirm=[];agreg=[];dom=[]
    for c in casos:
        for area,a in [('Brasil',c['a'])]+[(s,c['reg'][:,i]) for i,s in enumerate(c['areas'])]:
            for i,nome in enumerate(c['nomes']):
                v0=a[:,i];dif=100*(v0[:,0]-v0[:,1])/v0.sum(1);lo,hi=np.quantile(dif,[.025,.975])
                dom.append({'execucao':c['key'],'metodo':c['metodo'],'cenario':c['cenario'],'area':area,'origem':nome,
                            'diferenca_lula_menos_flavio_media_pp':dif.mean(),'inferior_95_pp':lo,'superior_95_pp':hi,
                            'direcao':'Lula' if lo>0 else 'Flávio' if hi<0 else 'sem direção definida','comparavel_principal':c['cenario']!='sem_nao_votou'})
            a,nomes=canon(a,c['nomes'],True);ss=resumo(a,nomes,c['metodo'],c['cenario'],area);ss['execucao']=c['key'];ss['comparavel_principal']=c['cenario']!='sem_nao_votou';sens.append(ss)
            metricas={}
            for nome,j,rot in [('Lula',0,'retencao_lula'),('Flávio',1,'retencao_flavio'),('Não votou',3,'persistencia_nao_votou')]:
                if nome in nomes:
                    v=a[:,nomes.index(nome)];metricas[rot]=100*v[:,j]/v.sum(1)
            ix=[i for i,s in enumerate(nomes) if s in ['Cury + Renan + Caiado','Demais candidatos']]
            v=a[:,ix].sum(1);metricas['outros_permanecem_validos']=100*v[:,:2].sum(1)/v.sum(1)
            for rot,v in metricas.items():
                lo,hi=np.quantile(v,[.025,.975]);afirm.append({'execucao':c['key'],'metodo':c['metodo'],'cenario':c['cenario'],'area':area,'afirmacao':rot,'media_pct':v.mean(),'inferior_95_pct':lo,'superior_95_pct':hi,'comparavel':c['cenario']!='sem_nao_votou'})
            if area=='Brasil' and c['cenario']=='principal':
                votos=a[:,ix].sum(1)
                for j,s in enumerate(DEST):
                    lo,hi=np.quantile(votos[:,j],[.025,.975]);agreg.append({'execucao':c['key'],'medida':'Outros candidatos → '+s,'media_votos':votos[:,j].mean(),'inferior_95_votos':lo,'superior_95_votos':hi})
                if 'Não votou' in nomes:
                    ni=nomes.index('Não votou');ent=a[:,ni,:3].sum(1);sai=a[:,:ni,3].sum(1)
                    for rot,v in [('Não votou 1º e votou 2º',ent),('Votou 1º e não votou 2º',sai),('Saldo de comparecimento modelado',ent-sai)]:
                        lo,hi=np.quantile(v,[.025,.975]);agreg.append({'execucao':c['key'],'medida':rot,'media_votos':v.mean(),'inferior_95_votos':lo,'superior_95_votos':hi})
    sens=pd.concat(sens,ignore_index=True);afirm=pd.DataFrame(afirm)
    m.save(sens,'sensibilidade.csv');m.save(afirm,'afirmacoes_testadas.csv');m.save(pd.DataFrame(agreg),'outros_e_comparecimento.csv');m.save(pd.DataFrame(dom),'dominancias.csv')
    ref=next(c for c in casos if c['key']==('restrito_principal_oito' if len(principal['nomes'])==8 else 'restrito_principal_seis'))
    aa,nn=canon(principal['a'],principal['nomes'],True);bb,nb=canon(ref['a'],ref['nomes'],True)
    a=resumo(aa,nn,principal['metodo'],'principal');b=resumo(bb,nb,'restrito','principal')
    comp=a.merge(b,on=['origem','destino'],suffixes=('_bayes','_restrito'))
    comp['diferenca_medias_pp']=comp.media_pct_bayes-comp.media_pct_restrito
    comp['sobreposicao_95']=(comp.inferior_95_pct_bayes<=comp.superior_95_pct_restrito)&(comp.inferior_95_pct_restrito<=comp.superior_95_pct_bayes)
    m.save(comp,'comparacao_metodos.csv')
    rotulos={'retencao_lula':'A maioria de quem votou em Lula permaneceu com Lula','retencao_flavio':'A maioria de quem votou em Flávio permaneceu com Flávio',
             'persistencia_nao_votou':'A maioria de quem não votou no 1º turno continuou sem votar','outros_permanecem_validos':'A maioria dos votos dos candidatos eliminados permaneceu válida no 2º turno'}
    ach=[]
    for chave,titulo in rotulos.items():
        q=afirm[afirm.afirmacao.eq(chave)&afirm.comparavel];prim=q[q.execucao.eq(principal['key'])&q.area.eq('Brasil')].iloc[0]
        minimo=float(q.inferior_95_pct.min());passou=bool(minimo>50 and q.metodo.nunique()==2)
        ach.append({'afirmacao':chave,'resiste_todos_testes_executados':passou,'menor_limite_95_entre_testes_pct':minimo,
                    'frase':f'{titulo}: {br(prim.media_pct)}% (95%: {br(prim.inferior_95_pct)}%–{br(prim.superior_95_pct)}%).',
                    'escopo':'Médias condicionais dos modelos; não acompanhamento de pessoas. Inclui recortes comparáveis e regiões; exclui retirada de não votou.'})
    m.save(pd.DataFrame(ach),'achados_tela.csv')
    return comp,ach


def pesquisas(casos,principal):
    p=pd.read_csv(ROOT/'dados/pbi/transferencia.csv');p=p[p.divulgacao.gt('2026-10-04')&p.divulgacao.lt('2026-10-25')].copy()
    p=p[p.divulgacao.eq(p.groupby('instituto').divulgacao.transform('max'))].copy()
    m.save(p,'pesquisas_ultimas.csv')
    nomes=principal['nomes'];a=principal['a'];base=a[0].sum(1);linhas=[];mapa={'Cury':'Augusto Cury','Renan':'Renan Santos','Caiado':'Ronaldo Caiado','nao_votou':'Não votou'}
    # Comparação por instituto evita misturar o grupo combinado da Quaest.
    for _,r in p[p.segmento_1turno.isin(mapa)].iterrows():
        origem=mapa[r.segmento_1turno];combinado=origem=='Não votou' and ('grupo combinado' in str(r.observacao).lower())
        ss=['Não votou','Branco ou nulo'] if combinado else [origem]
        if all(s in nomes for s in ss):modelo=principal;aa=a;nn=nomes
        else:modelo=next(c for c in casos if c['key']=='restrito_principal_oito');aa=modelo['a'];nn=modelo['nomes']
        idx=[nn.index(s) for s in ss];v=aa[:,idx].sum(1);den=v.sum(1)
        for j,campo in [(0,'lula'),(1,'flavio')]:
            if pd.isna(r[campo]):continue
            vals=100*v[:,j]/den;lo,hi=np.quantile(vals,[.025,.975])
            linhas.append({'instituto':r.instituto,'divulgacao':r.divulgacao,'origem':'Não votou ou branco/nulo' if combinado else origem,'destino':DEST[j],
                           'pesquisa_pct_total_segmento':r[campo],'modelo':modelo['key'],'modelo_media_pct':vals.mean(),'modelo_inferior_95_pct':lo,'modelo_superior_95_pct':hi,
                           'compativel_descritivamente':bool(lo<=r[campo]<=hi),'n_segmento':r.n_segmento,'fonte_url':r.fonte_url,
                           'ressalva':'Intenção hipotética e recall não são trajetórias observadas. Mesma base aritmética total do segmento; não renormaliza para válidos.'})
    # Agregado padronizado dos três: apenas institutos com os três segmentos.
    if 'Cury + Renan + Caiado' in nomes:
        base8=m.get_data('principal','oito');pesos=base8['x'][:,2:5].sum(0).astype(float);pesos/=pesos.sum()
        for inst,q in p.groupby('instituto'):
            q=q[q.segmento_1turno.isin(['Cury','Renan','Caiado'])].set_index('segmento_1turno')
            if not all(s in q.index for s in ['Cury','Renan','Caiado']):continue
            for j,campo in [(0,'lula'),(1,'flavio')]:
                vals=q[campo].reindex(['Cury','Renan','Caiado']).to_numpy(float)
                if not np.isfinite(vals).all():continue
                pp=float(vals@pesos);v=100*a[:,nomes.index('Cury + Renan + Caiado'),j]/base[nomes.index('Cury + Renan + Caiado')];lo,hi=np.quantile(v,[.025,.975])
                linhas.append({'instituto':inst,'origem':'Cury + Renan + Caiado','destino':DEST[j],'pesquisa_pct_total_segmento':pp,'modelo':principal['key'],
                               'modelo_media_pct':v.mean(),'modelo_inferior_95_pct':lo,'modelo_superior_95_pct':hi,'compativel_descritivamente':bool(lo<=pp<=hi),
                               'ressalva':'Pesquisa padronizada pelos votos reais de 1º turno dos três; não é média de tamanhos de amostra nem medição direta de um segmento agregado.'})
    detalhe=pd.DataFrame(linhas);m.save(detalhe,'confronto_pesquisas.csv')
    medias=detalhe.groupby(['origem','destino','modelo'],as_index=False).agg(media_pesquisas_pct=('pesquisa_pct_total_segmento','mean'),
        minimo_instituto_pct=('pesquisa_pct_total_segmento','min'),maximo_instituto_pct=('pesquisa_pct_total_segmento','max'),institutos=('instituto','nunique'),
        modelo_media_pct=('modelo_media_pct','first'),modelo_inferior_95_pct=('modelo_inferior_95_pct','first'),modelo_superior_95_pct=('modelo_superior_95_pct','first'))
    medias['media_dentro_intervalo_modelo']=(medias.media_pesquisas_pct>=medias.modelo_inferior_95_pct)&(medias.media_pesquisas_pct<=medias.modelo_superior_95_pct)
    medias['nota']='Faixa entre institutos não é IC amostral. Média simples por instituto; bases de origem separadas.'
    m.save(medias,'confronto_pesquisas_resumo.csv')
    residual=p[p.segmento_1turno.isin(mapa)][['instituto','divulgacao','segmento_1turno','branco_nulo_nao_vota','nao_sabe','observacao']].copy()
    residual['comparacao_terminal_direta']='não: definições de residual e não sabe variam; Atlas inclui não sabe no residual'
    m.save(residual,'residuos_pesquisas.csv')


def main():
    casos,diags=coletar();ap=[c for c in casos if c['metodo']=='bayes_dm' and c['cenario']=='principal']
    if not ap:
        m.js({'status':'Bayes não aprovado: não usar como resultado','execucoes':diags},'decisao_uso.json')
        tab=m.read('restrito_principal_oito.csv');m.save(tab[tab.area.eq('Brasil')],'matriz_nacional_exploratoria_restrito.csv')
        raise SystemExit('Nenhum Bayes aprovado; somente diagnóstico e exploração restrita.')
    ap.sort(key=lambda c:(bool(c['meta']['efeito_uf']),len(c['nomes'])),reverse=True);principal=ap[0]
    nacional=resumo(principal['a'],principal['nomes'],'bayes_dm','principal');nacional['execucao']=principal['key'];m.save(nacional,'matriz_nacional.csv')
    regs=pd.concat([resumo(principal['reg'][:,i],principal['nomes'],'bayes_dm','principal',area=s) for i,s in enumerate(principal['areas'])],ignore_index=True);m.save(regs,'matriz_regiao.csv')
    m.save(nacional[['origem','destino','base_origem_votos','media_votos','inferior_95_votos','superior_95_votos','tipo_intervalo']],'matriz_votos.csv')
    restr=m.read('restrito_principal_oito.csv');m.save(restr[restr.area.eq('Brasil')],'matriz_restrito_oito.csv')
    comp,ach=comparar(casos,principal);pesquisas(casos,principal)
    decisao={'principal':principal['key'],'diagnostico':principal['meta'],'achados_aprovados':sum(a['resiste_todos_testes_executados'] for a in ach),
             'celulas_comparaveis_sem_sobreposicao':int((~comp.sobreposicao_95).sum()),'aviso':'Estimativa de perfis médios condicionais. Não identifica pessoas; somente MCMC aprovado foi usado.'}
    m.js(decisao,'decisao_uso.json')
    # Catálogo explica os cabeçalhos dos CSV principais.
    defs={'media_pct':'Média do percentual da linha no modelo/reamostragens.','inferior_95_pct':'Quantil 2,5% da distribuição indicada em tipo_intervalo.','superior_95_pct':'Quantil 97,5% da distribuição indicada em tipo_intervalo.',
          'media_votos':'Média do fluxo esperado; não contagem individual observada.','inferior_95_votos':'Quantil 2,5% do fluxo esperado.','superior_95_votos':'Quantil 97,5% do fluxo esperado.',
          'base_origem_votos':'Total de votos/pessoas da origem na base do cenário.','rhat':'Split R-hat normalizado por ranks e folding. Critério <1,01.','ess_bulk':'ESS de ranks com cadeias divididas. Critério >400.','ess_tail':'Menor ESS nos quantis 5%/95%, com cadeias divididas. Critério >400.',
          'metodo':'restrito: QP regional com bootstrap UF; bayes_dm: mistura ecológica bayesiana DM.','origem':'Grupo do 1º turno.','destino':'Lula, Flávio, branco/nulo ou não votou no 2º.',
          'area':'Brasil sem exterior ou região.','cenario':'Recorte/especificação; sem_nao_votou muda a população.','tipo_intervalo':'Credibilidade posterior condicional ou percentil bootstrap UF; não inclui automaticamente viés ecológico.'}
    cat=[]
    for p in sorted(OUT.glob('*.csv')):
        if p.name=='dicionario_csv.csv':continue
        for c in m.read(p.name).columns:cat.append({'arquivo':p.name,'coluna':c,'descricao':defs.get(c,'Campo de auditoria: '+c.replace('_',' ')+'. Ver documentação do método.')})
    m.save(pd.DataFrame(cat),'dicionario_csv.csv')
    import importlib.metadata
    scripts=['inferencia_t16.py','inferencia_t16_v2.py','t16_core.py','finalizar_t16_v2.py','testar_reinicio_t16.py']
    m.js({'utc':m.utc(),'semente':m.SEED,'pacotes':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','osqp','jax','numpyro']},
          'scripts_sha256':{s:hashlib.sha256((ROOT/'pipeline'/s).read_bytes()).hexdigest() for s in scripts},'principal':principal['key']},'manifesto.json')
    texto_resultado(principal,nacional,ach,comp)
    print(json.dumps(decisao,ensure_ascii=False));print(nacional[['origem','destino','media_pct','inferior_95_pct','superior_95_pct']].to_string(index=False))


def texto_resultado(principal,nacional,ach,comp):
    o=principal['meta'];lines=[f'Execução principal: `{principal["key"]}`. Convergência aprovada: R-hat máximo **{br(o["rhat_max"],6)}**, ESS bulk mínimo **{br(o["ess_bulk_min"],0)}**, ESS tail mínimo **{br(o["ess_tail_min"],0)}**, **{o["divergencias"]} divergências**.',
                              'Médias e intervalos condicionais de 95%, em % da origem. Não são trajetórias observadas.',
                              '| Origem | Lula | Flávio | Branco/nulo | Não votou |\n|---|---:|---:|---:|---:|']
    for nome in nacional.origem.drop_duplicates():
        parts=[]
        for dest in DEST:
            r=nacional[nacional.origem.eq(nome)&nacional.destino.eq(dest)].iloc[0];parts.append(f'{br(r.media_pct)} [{br(r.inferior_95_pct)}–{br(r.superior_95_pct)}]')
        lines.append('| '+nome+' | '+' | '.join(parts)+' |')
    lines.append('### Achados testados')
    for a in ach:lines.append('- '+('Aprovado nos testes executados: ' if a['resiste_todos_testes_executados'] else 'Não aprovado como achado robusto: ')+a['frase'])
    lines.append(f'{int((~comp.sobreposicao_95).sum())} de {len(comp)} células comparáveis têm intervalos marginais sem sobreposição entre os métodos. Isso é diagnóstico descritivo, não teste de trajetória individual.')
    lines.append('As candidaturas individuais só recebem estimativa bayesiana se a execução de oito origens passar. Caso contrário, sua divisão permanece restrita ao primeiro método, sem confirmação bayesiana individual.')
    lines.append('### Votos dos outros e comparecimento')
    lines.append('| Medida | Média, votos | Intervalo 95%, votos |\n|---|---:|---:|')
    cont=m.read('outros_e_comparecimento.csv')
    for _,r in cont[cont.execucao.eq(principal['key'])].iterrows():
        lines.append(f'| {r.medida} | {br(r.media_votos,0)} | {br(r.inferior_95_votos,0)}–{br(r.superior_95_votos,0)} |')
    lines.append('O saldo observado é 2.920.562 votantes a mais sem exterior e 2.960.239 com exterior. O saldo líquido não é o fluxo bruto de retornantes.')
    body='';prev=''
    for line in lines:body+=('\n' if line.startswith('|') and prev.startswith('|') else '\n\n')+line;prev=line
    doc=ROOT/'docs/metodo-inferencia-t16.md';s=doc.read_text(encoding='utf-8');a,b=s.split('<!-- RESULTADOS_T16 -->',1);_,c=b.split('<!-- FIM_RESULTADOS_T16 -->',1)
    doc.write_text(a+'<!-- RESULTADOS_T16 -->'+body+'\n\n<!-- FIM_RESULTADOS_T16 -->'+c,encoding='utf-8')


if __name__=='__main__':main()
