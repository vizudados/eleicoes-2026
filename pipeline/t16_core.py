"""Leitura e regressão restrita para a nova execução T16; nenhuma saída antiga é lida."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize


RAIZ = Path(__file__).resolve().parents[1]

SAIDA = RAIZ/'dados/saida/2turno/inferencia_t16'

SEMENTE = 20261026

LINHAS = ['Lula','Flávio','Augusto Cury','Renan Santos','Ronaldo Caiado','Demais candidatos','Branco ou nulo','Não votou']

COLUNAS = ['Lula','Flávio','Branco ou nulo','Não votou']

MAPA = {13:LINHAS[0],22:LINHAS[1],70:LINHAS[2],14:LINHAS[3],55:LINHAS[4]}

CAPITAIS = {1200401,2704302,1600303,1302603,2927408,2304400,5300108,3205309,5208707,2111300,5103403,5002704,3106200,1501402,2507507,4106902,2611606,2211001,3304557,2408102,4314902,1100205,1400100,4205407,2800308,3550308,1721000}

ENTRADAS = ['dados/bruto/tse/presidente_2026_BR.csv','dados/bruto/tse/detalhe_2026_BR.csv','dados/pbi/candidato_ano.csv','dados/pbi/municipio_ano.csv','dados/pbi/municipio_2turno.csv','dados/pbi/municipio.csv','dados/pbi/uf_2turno.csv','dados/pbi/transferencia.csv']

AVISO = 'Estimativa ecológica agregada, condicionada ao modelo; não identifica pessoas nem comprova transferência individual.'

def gravar(df, nome):
    SAIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA/nome, sep=';', decimal=',', encoding='utf-8-sig', index=False, float_format='%.10g',lineterminator='\n')

def ler(nome):
    return pd.read_csv(SAIDA/nome,sep=';',decimal=',',encoding='utf-8-sig')

def json_gravar(obj, nome):
    SAIDA.mkdir(parents=True,exist_ok=True)
    def limpar(v):
        if isinstance(v,dict): return {k:limpar(a) for k,a in v.items()}
        if isinstance(v,list): return [limpar(a) for a in v]
        if isinstance(v,float) and not np.isfinite(v): return None
        return v
    (SAIDA/nome).write_text(json.dumps(limpar(obj),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def arredondar_margem(y, n):
    """Maiores restos: mantém soma inteira N1 sem esconder mudança do cadastro."""
    proporcao = y/y.sum(1,keepdims=True)
    bruto = proporcao*n[:,None]
    inteiro = np.floor(bruto).astype(np.int64)
    faltas = n-inteiro.sum(1)
    ordem = np.argsort(-(bruto-inteiro),axis=1,kind='stable')
    for j in range(y.shape[1]):
        mascara = faltas>j
        inteiro[np.where(mascara)[0],ordem[mascara,j]] += 1
    return inteiro

def carregar():
    p = RAIZ/'dados/pbi'
    v = pd.read_csv(RAIZ/ENTRADAS[0],sep=';',encoding='latin1')
    d = pd.read_csv(RAIZ/ENTRADAS[1],sep=';',encoding='latin1')
    v = v.query('NR_TURNO == 1 and CD_CARGO == 1').copy()
    d = d.query('NR_TURNO == 1 and CD_CARGO == 1').copy()
    chaves = ['SG_UF','CD_MUNICIPIO','NR_ZONA','ST_VOTO_EM_TRANSITO']
    if v.duplicated(chaves+['NR_CANDIDATO']).any() or d.duplicated(chaves).any():
        raise ValueError('Duplicata nas chaves zona/candidato/trânsito.')
    catalogo = pd.read_csv(p/'candidato_ano.csv').query('ano == 2026').set_index('numero')
    totais = v.groupby('NR_CANDIDATO').QT_VOTOS_NOMINAIS_VALIDOS.sum()
    if set(totais.index)!=set(catalogo.index) or not totais.eq(catalogo.votos.reindex(totais.index)).all():
        raise ValueError('Candidato/ano diverge dos brutos, incluindo exterior.')
    ext1 = d[d.SG_UF.eq('ZZ')]
    ext2 = pd.read_csv(p/'uf_2turno.csv').query('ano == 2026 and uf == "ZZ"')
    candidatos_exterior=v[v.SG_UF.eq('ZZ')].groupby('NR_CANDIDATO').QT_VOTOS_NOMINAIS_VALIDOS.sum()
    v = v[v.SG_UF.ne('ZZ')]
    d = d[d.SG_UF.ne('ZZ')]
    nums = sorted(v.NR_CANDIDATO.unique())
    wide = v.pivot_table(index=['SG_UF','CD_MUNICIPIO'],columns='NR_CANDIDATO',values='QT_VOTOS_NOMINAIS_VALIDOS',aggfunc='sum',fill_value=0).reset_index()
    wide = wide.rename(columns={k:f'cand_{k}' for k in nums})
    campos = {'QT_APTOS':'aptos_1','QT_COMPARECIMENTO':'comparecimento_1','QT_ABSTENCOES':'abstencoes_1','QT_VOTOS_BRANCOS':'brancos_1','QT_TOTAL_VOTOS_NULOS':'nulos_1','QT_TOTAL_VOTOS_VALIDOS':'validos_1'}
    det = d.groupby(['SG_UF','CD_MUNICIPIO'],as_index=False)[list(campos)].sum().rename(columns=campos)
    z = wide.merge(det,on=['SG_UF','CD_MUNICIPIO'],how='outer',validate='one_to_one',indicator=True)
    if not z._merge.eq('both').all():
        raise ValueError('Votos e detalhe têm universos municipais distintos.')
    z = z.drop(columns='_merge')
    geo = pd.read_csv(p/'municipio.csv')
    z = z.merge(geo,left_on=['SG_UF','CD_MUNICIPIO'],right_on=['uf','cd_tse'],how='left',validate='one_to_one')
    if z[['cd_ibge','uf','regiao']].isna().any().any():
        raise ValueError('Município sem geografia.')
    a = pd.read_csv(p/'municipio_ano.csv').query('ano == 2026')
    b = pd.read_csv(p/'municipio_2turno.csv').query('ano == 2026')
    z = z.merge(a,on='cd_ibge',how='outer',validate='one_to_one',indicator=True)
    if not z._merge.eq('both').all():
        raise ValueError('Universo do 1º turno incompleto.')
    z = z.drop(columns='_merge')
    checks = {'pt':'cand_13','adv':'cand_22','aptos':'aptos_1','comparecimento':'comparecimento_1','abstencoes':'abstencoes_1','brancos':'brancos_1','nulos':'nulos_1','validos':'validos_1'}
    for c, bruto in checks.items():
        if not z[c].eq(z[bruto]).all():
            raise ValueError(f'Conferência municipal falhou: {c}')
    if not z[[f'cand_{k}' for k in nums]].sum(axis=1).eq(z.validos_1).all():
        raise ValueError('Soma de candidatos não fecha com válidos.')
    z = z.drop(columns=list(a.columns.difference(['cd_ibge'])))
    z = z.merge(b.drop(columns='ano').rename(columns={c:c+'_2' for c in b.columns if c not in ['ano','cd_ibge']}),on='cd_ibge',how='outer',validate='one_to_one',indicator=True)
    if not z._merge.eq('both').all():
        raise ValueError('Universo do 2º turno incompleto.')
    z = z.drop(columns='_merge').sort_values('cd_ibge').reset_index(drop=True)
    for s in ['1','2']:
        if not (z[f'comparecimento_{s}']+z[f'abstencoes_{s}']).eq(z[f'aptos_{s}']).all():
            raise ValueError('Comparecimento e abstenção não fecham com aptos.')
        if not (z[f'validos_{s}']+z[f'brancos_{s}']+z[f'nulos_{s}']).eq(z[f'comparecimento_{s}']).all():
            raise ValueError('Votos e comparecimento não fecham.')
    y = np.column_stack([z.pt_2,z.adv_2,z.brancos_2+z.nulos_2,z.abstencoes_2]).astype(np.int64)
    n = z.aptos_1.to_numpy(np.int64)
    yh = arredondar_margem(y,n)
    for j in range(4):
        z[f'y_{j}'] = yh[:,j]
    delta = z.aptos_2-z.aptos_1
    exterior = []
    campos_ext = {'aptos':'QT_APTOS','comparecimento':'QT_COMPARECIMENTO','abstencoes':'QT_ABSTENCOES','brancos':'QT_VOTOS_BRANCOS','nulos':'QT_TOTAL_VOTOS_NULOS','validos':'QT_TOTAL_VOTOS_VALIDOS'}
    for c,dc in campos_ext.items():
        for turno,qt,nacional in [(1,int(ext1[dc].sum()),int(z[c+'_1'].sum())),(2,int(ext2[c].sum()),int(z[c+'_2'].sum()))]:
            exterior.append({'turno':turno,'medida':c,'brasil_sem_exterior':nacional,'exterior_excluido':qt,'total_incluindo_exterior':nacional+qt,'peso_exterior_pct':100*qt/(nacional+qt)})
    for nome,numero,campo2 in [('Lula',13,'pt'),('Flávio',22,'adv')]:
        for turno,qt,br in [(1,int(candidatos_exterior.loc[numero]),int(z[f'cand_{numero}'].sum())),(2,int(ext2[campo2].sum()),int(z[campo2+'_2'].sum()))]:
            exterior.append({'turno':turno,'medida':nome,'brasil_sem_exterior':br,'exterior_excluido':qt,'total_incluindo_exterior':br+qt,'peso_exterior_pct':100*qt/(br+qt)})
    qt=int(candidatos_exterior.drop([13,22]).sum());br=int(z.validos_1.sum()-z.cand_13.sum()-z.cand_22.sum())
    exterior.append({'turno':1,'medida':'outros_candidatos','brasil_sem_exterior':br,'exterior_excluido':qt,'total_incluindo_exterior':br+qt,'peso_exterior_pct':100*qt/(br+qt)})
    gravar(pd.DataFrame(exterior),'exterior.csv')
    auditoria = [{'verificacao':'unidades_eleitorais_pareadas','valor':len(z)},
                 {'verificacao':'unidades_com_aptos_diferentes','valor':int(delta.ne(0).sum())},
                 {'verificacao':'delta_aptos_liquido','valor':int(delta.sum())},
                 {'verificacao':'soma_absoluta_delta_aptos','valor':int(delta.abs().sum())},
                 {'verificacao':'aumento_comparecimento_sem_exterior','valor':int((z.comparecimento_2-z.comparecimento_1).sum())},
                 {'verificacao':'aumento_comparecimento_incluindo_exterior','valor':int((z.comparecimento_2-z.comparecimento_1).sum()+ext2.comparecimento.sum()-ext1.QT_COMPARECIMENTO.sum())},
                 {'verificacao':'outros_candidatos_1turno_sem_exterior','valor':int(z.validos_1.sum()-z.cand_13.sum()-z.cand_22.sum())},
                 {'verificacao':'populacao_ausente','valor':int(z.populacao.isna().sum())}]
    gravar(pd.DataFrame(auditoria),'auditoria_entradas.csv')
    contas=[]
    for campo in ['validos','comparecimento','abstencoes','aptos','brancos','nulos']:
        a1=int(z[campo+'_1'].sum()); a2=int(z[campo+'_2'].sum())
        contas.append({'medida':campo,'observado_1turno_votos':a1,'observado_2turno_votos':a2,'diferenca_2menos1_votos':a2-a1,'natureza':'Contagem observada nas bases locais, sem exterior; não estimativa de fluxo individual.'})
    for nome,c1,c2 in [('Lula','cand_13','pt_2'),('Flávio','cand_22','adv_2')]:
        a1=int(z[c1].sum());a2=int(z[c2].sum())
        contas.append({'medida':nome,'observado_1turno_votos':a1,'observado_2turno_votos':a2,'diferenca_2menos1_votos':a2-a1,'natureza':'Contagem observada nas bases locais, sem exterior; não estimativa de fluxo individual.'})
    gravar(pd.DataFrame(contas),'contabilidade.csv')
    gravar(z[['cd_ibge','nome','uf','regiao','populacao','aptos_1','aptos_2']].assign(delta_aptos=delta),'cadastro_municipal.csv')
    gravar(pd.DataFrame([{'destino':COLUNAS[j],'votos_observados_2turno':int(y[:,j].sum()),'votos_harmonizados_base_1turno':int(yh[:,j].sum()),'ajuste_votos':int((yh-y)[:,j].sum()),'ajuste_absoluto_municipal':int(np.abs(yh-y)[:,j].sum())} for j in range(4)]),'harmonizacao.csv')
    return z, nums, catalogo

def preparar(z,nums,catalogo,cenario='principal'):
    z = z.copy()
    if cenario=='sem_capitais': z = z[~z.cd_ibge.isin(CAPITAIS)].copy()
    if cenario=='ate_50mil_habitantes': z = z[z.populacao.le(50000)].copy()
    if cenario.startswith('regiao_'): z = z[z.regiao.eq(cenario.removeprefix('regiao_'))].copy()
    if cenario=='demais_separados':
        nomes = [str(catalogo.loc[k,'nome']) for k in nums]
        x = z[[f'cand_{k}' for k in nums]].to_numpy(float)
        nomes = [MAPA.get(k,nomes[j]) for j,k in enumerate(nums)]
    else:
        outros = [k for k in nums if k not in MAPA]
        x = np.column_stack([z.cand_13,z.cand_22,z.cand_70,z.cand_14,z.cand_55,z[[f'cand_{k}' for k in outros]].sum(axis=1)])
        nomes = LINHAS[:6].copy()
    x = np.column_stack([x,z.brancos_1+z.nulos_1,z.abstencoes_1])
    nomes += LINHAS[-2:]
    n = z.aptos_1.to_numpy(np.int64)
    y = z[[f'y_{j}' for j in range(4)]].to_numpy(np.int64)
    comparavel = True
    if cenario=='sem_nao_votou':
        # Estresse deliberado: remover a origem não votou altera a população.
        # Mantém os quatro destinos, mas imputa o 2º turno aos votantes do 1º.
        # Seus fluxos não podem ser interpretados como a mesma estimativa.
        x = x[:,:-1]
        nomes = nomes[:-1]
        n = x.sum(1).astype(np.int64)
        y = arredondar_margem(y,n)
        comparavel = False
    if cenario=='base_aptos_2turno':
        n = z.aptos_2.to_numpy(np.int64)
        x = x/x.sum(1,keepdims=True)*n[:,None]
        y = np.column_stack([z.pt_2,z.adv_2,z.brancos_2+z.nulos_2,z.abstencoes_2]).astype(np.int64)
    if not np.allclose(x.sum(1),n) or not np.array_equal(y.sum(1),n):
        raise ValueError('Margens incompatíveis.')
    return {'z':z,'x':x,'y':y,'n':n,'nomes':nomes,'comparavel':comparavel,'cenario':cenario}

def estatisticas_regressao(data):
    x,y,n = data['x']/data['n'][:,None],data['y']/data['n'][:,None],data['n']
    est = {}
    for uf in sorted(data['z'].uf.unique()):
        mask = data['z'].uf.eq(uf).to_numpy()
        w = n[mask]/n.sum()
        est[uf] = (x[mask].T@(w[:,None]*x[mask]),x[mask].T@(w[:,None]*y[mask]),str(data['z'].loc[mask,'regiao'].iloc[0]))
    return est

def resolver_restrito(a,b,inicial=None):
    r,c = b.shape
    # Normaliza por traço, preservando o ótimo e facilitando o critério numérico.
    escala = np.trace(a)
    a,b = a/escala,b/escala
    def fun(t):
        t=t.reshape(r,c)
        return np.sum(t*(a@t))-2*np.sum(t*b)
    def jac(t): return (2*(a@t.reshape(r,c)-b)).ravel()
    eq = np.kron(np.eye(r),np.ones((1,c)))
    t0 = np.full((r,c),1/c) if inicial is None else inicial
    fit = minimize(fun,t0.ravel(),jac=jac,method='SLSQP',bounds=[(0,1)]*(r*c),
                   constraints=[{'type':'eq','fun':lambda t:eq@t-1,'jac':lambda t:eq}],
                   options={'ftol':1e-12,'maxiter':2500})
    t = fit.x.reshape(r,c)
    if not fit.success or np.max(np.abs(t.sum(1)-1))>1e-7 or t.min() < -1e-8:
        raise RuntimeError('Regressão restrita falhou: '+fit.message)
    return t,{'iteracoes':fit.nit,'objetivo':fit.fun,'condicao':float(np.linalg.cond(a))}

def resumo_fluxos(amostras,nomes,origem,metodo,cenario,area='Brasil',tipo='intervalo_modelo_95',comparavel=True):
    # amostras: amostra x linha x destino, já em votos esperados.
    pct = amostras/origem[None,:,None]*100
    result=[]
    for i,nome in enumerate(nomes):
        for j,destino in enumerate(COLUNAS):
            q=np.quantile(pct[:,i,j],[.025,.975]); v=np.quantile(amostras[:,i,j],[.025,.975])
            result.append({'metodo':metodo,'cenario':cenario,'area':area,'origem':nome,'destino':destino,'base_origem_votos':float(origem[i]),
                           'media_pct':float(pct[:,i,j].mean()),'inferior_95_pct':float(q[0]),'superior_95_pct':float(q[1]),
                           'media_votos':float(amostras[:,i,j].mean()),'inferior_95_votos':float(v[0]),'superior_95_votos':float(v[1]),
                           'tipo_intervalo':tipo,'comparavel_principal':comparavel,'aviso':AVISO})
    return pd.DataFrame(result)

def restrito(data,boot):
    est = estatisticas_regressao(data)
    regioes = sorted(data['z'].regiao.unique())
    r=len(data['nomes'])
    perfis=[]; diagnostico=[]
    for g in regioes:
        ufs=[u for u in est if est[u][2]==g]
        a=sum(est[u][0] for u in ufs); b=sum(est[u][1] for u in ufs)
        t,diag=resolver_restrito(a,b)
        perfis.append(t); diagnostico.append({'metodo':'restrito','cenario':data['cenario'],'area':g,'n_ufs':len(ufs),**diag})
    perfis=np.array(perfis)
    gi=np.array([regioes.index(g) for g in data['z'].regiao])
    origens=np.array([data['x'][gi==k].sum(0) for k in range(len(regioes))])
    rng=np.random.default_rng(SEMENTE)
    amostras=np.empty((boot,len(regioes),r,4))
    for draw in range(boot):
        for k,g in enumerate(regioes):
            ufs=[u for u in est if est[u][2]==g]
            selecionadas=rng.choice(ufs,len(ufs),replace=True)
            a=sum(est[u][0] for u in selecionadas); b=sum(est[u][1] for u in selecionadas)
            t,_=resolver_restrito(a,b,perfis[k])
            amostras[draw,k]=t*origens[k,:,None]
        if (draw+1)%100==0: print(f'Restrito {data["cenario"]}: bootstrap {draw+1}/{boot}',flush=True)
    nacional=amostras.sum(1)
    tabelas=[resumo_fluxos(nacional,data['nomes'],origens.sum(0),'restrito',data['cenario'],tipo='percentil_bootstrap_UF_95',comparavel=data['comparavel'])]
    for k,g in enumerate(regioes):
        tabelas.append(resumo_fluxos(amostras[:,k],data['nomes'],origens[k],'restrito',data['cenario'],area=g,tipo='percentil_bootstrap_UF_95',comparavel=data['comparavel']))
    tabela=pd.concat(tabelas,ignore_index=True)
    ponto=(perfis*origens[:,:,None]).sum(0)
    # Ponto SLSQP, além da média bootstrap, evita confundir viés e incerteza.
    for k,g in enumerate(['Brasil']+regioes):
        t=ponto/origens.sum(0)[:,None] if k==0 else perfis[k-1]
        for i,nome in enumerate(data['nomes']):
            for j,destino in enumerate(COLUNAS):
                mask=tabela.area.eq(g)&tabela.origem.eq(nome)&tabela.destino.eq(destino)
                tabela.loc[mask,'ponto_ajuste_pct']=100*t[i,j]
    gravar(tabela,f'restrito_{data["cenario"]}.csv')
    gravar(pd.DataFrame(diagnostico),f'diagnostico_restrito_{data["cenario"]}.csv')
    np.savez_compressed(SAIDA/f'amostras_restrito_{data["cenario"]}.npz',fluxos=nacional,regioes=amostras,nomes=np.array(data['nomes']),areas=np.array(regioes))
    if data['cenario']=='principal':
        np.savez_compressed(SAIDA/'amostras_restrito.npz',fluxos=nacional,regioes=amostras,nomes=np.array(data['nomes']),areas=np.array(regioes))
        pred=np.sum(data['x'][:,:,None]*perfis[gi],axis=1)
        predicoes(data,pred,None,'restrito')
    return tabela

def predicoes(data,pred,rep,metodo):
    # Erros na base harmonizada; números observados originais também exportados.
    rows=[]; diags=[]
    n=data['n']; y=data['y']; z=data['z']
    for j,c in enumerate(COLUNAS):
        resid=pred[:,j]-y[:,j]
        baixo=np.full(len(n),np.nan) if rep is None else np.quantile(rep[:,:,j],.025,axis=0)
        alto=np.full(len(n),np.nan) if rep is None else np.quantile(rep[:,:,j],.975,axis=0)
        cobertura=np.full(len(n),False) if rep is None else (y[:,j]>=baixo)&(y[:,j]<=alto)
        diags.append({'metodo':metodo,'cenario':data['cenario'],'destino':c,'mae_municipal_votos':float(np.abs(resid).mean()),
                      'rmse_municipal_votos':float(np.sqrt(np.mean(resid**2))),'mae_ponderado_pp_aptos':float(100*np.abs(resid).sum()/n.sum()),
                      'p95_erro_absoluto_pp_aptos':float(np.quantile(100*np.abs(resid)/n,.95)),
                      'residuo_nacional_votos':float(resid.sum()),'cobertura_preditiva_95_pct':None if rep is None else float(100*cobertura.mean())})
        for i in range(len(n)):
            rows.append({'metodo':metodo,'cenario':data['cenario'],'cd_ibge':int(z.cd_ibge.iloc[i]),'nome':z.nome.iloc[i],'uf':z.uf.iloc[i],'regiao':z.regiao.iloc[i],'destino':c,
                         'aptos_base':int(n[i]),'observado_harmonizado_votos':int(y[i,j]),'predito_media_votos':float(pred[i,j]),'erro_votos':float(resid[i]),
                         'erro_pp_aptos':float(100*resid[i]/n[i]),'preditivo_inferior_95_votos':float(baixo[i]),'preditivo_superior_95_votos':float(alto[i]),
                         'observado_no_intervalo_95':None if rep is None else bool(cobertura[i])})
    gravar(pd.DataFrame(rows),f'predicoes_{metodo}_{data["cenario"]}.csv')
    gravar(pd.DataFrame(diags),f'checagem_preditiva_{metodo}_{data["cenario"]}.csv')
