"""Validação externa à UF no método restrito e concentração das origens."""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

arquivo=Path(__file__).with_name('inferencia_t16.py')
spec=importlib.util.spec_from_file_location('inferencia_t16',arquivo)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
z,nums,cat=m.carregar();data=m.preparar(z,nums,cat)
est=m.estatisticas_regressao(data)
previsao=np.empty_like(data['y'],dtype=float)
linhas=[]
for uf in sorted(est):
    regiao=est[uf][2];outros=[u for u in est if u!=uf and est[u][2]==regiao]
    a=sum(est[u][0] for u in outros);b=sum(est[u][1] for u in outros)
    t,diag=m.resolver_restrito(a,b)
    mask=data['z'].uf.eq(uf).to_numpy()
    previsao[mask]=data['x'][mask]@t
    n=data['n'][mask];erro=previsao[mask]-data['y'][mask]
    for j,c in enumerate(m.COLUNAS):
        linhas.append({'uf_retirada':uf,'regiao':regiao,'destino':c,'n_municipios_validacao':int(mask.sum()),
                       'mae_pp_aptos':float(100*np.abs(erro[:,j]).sum()/n.sum()),'erro_total_votos':float(erro[:,j].sum()),
                       'tipo_validacao':'UF inteira fora do ajuste; região treinada nas demais UFs.'})
m.gravar(pd.DataFrame(linhas),'validacao_fora_uf.csv')
m.predicoes(data,previsao,None,'restrito_fora_uf')
concentracao=[]
for i,nome in enumerate(data['nomes']):
    qtd=pd.Series(data['x'][:,i]).groupby(data['z'].uf.reset_index(drop=True)).sum().sort_values(ascending=False)
    p=qtd/qtd.sum()
    concentracao.append({'origem':nome,'total_votos':float(qtd.sum()),'uf_maior':str(qtd.index[0]),'maior_uf_pct':float(100*p.iloc[0]),
                         'tres_maiores_ufs_pct':float(100*p.iloc[:3].sum()),'indice_concentracao_hhi':float(np.sum(p*p)),
                         'numero_ufs_com_votos':int(qtd.gt(0).sum())})
m.gravar(pd.DataFrame(concentracao),'concentracao_origens_uf.csv')
print('Concluída validação em 27 UFs e concentração territorial das oito origens.')
