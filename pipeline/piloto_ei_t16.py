"""Piloto computacional do modelo exato multinomial-Dirichlet."""
import os
os.environ['JAX_ENABLE_X64'] = 'true'
os.environ['XLA_FLAGS'] = '--xla_force_host_platform_device_count=4'
from pathlib import Path
import numpy as np
import pandas as pd
import jax.numpy as jnp
from jax import random
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, init_to_value

root = Path(__file__).resolve().parents[1]
m = pd.read_csv(root/'dados/pbi/municipio.csv')
d = pd.read_csv(root/'dados/bruto/tse/detalhe_2026_BR.csv',sep=';',encoding='latin1').query('NR_TURNO==1 and CD_CARGO==1 and SG_UF!="ZZ"')
v = pd.read_csv(root/'dados/bruto/tse/presidente_2026_BR.csv',sep=';',encoding='latin1').query('NR_TURNO==1 and CD_CARGO==1 and SG_UF!="ZZ"')
v['grupo'] = v.NR_CANDIDATO.map({13:'Lula',22:'Flavio',70:'Cury',14:'Renan',55:'Caiado'}).fillna('Demais')
wide = v.pivot_table(index=['SG_UF','CD_MUNICIPIO'],columns='grupo',values='QT_VOTOS_NOMINAIS_VALIDOS',aggfunc='sum',fill_value=0).reset_index()
d = d.groupby(['SG_UF','CD_MUNICIPIO'],as_index=False)[['QT_APTOS','QT_VOTOS_BRANCOS','QT_TOTAL_VOTOS_NULOS','QT_ABSTENCOES']].sum()
a = wide.merge(d,on=['SG_UF','CD_MUNICIPIO'],validate='one_to_one').merge(m,left_on=['SG_UF','CD_MUNICIPIO'],right_on=['uf','cd_tse'],validate='one_to_one')
a = a.merge(pd.read_csv(root/'dados/pbi/municipio_2turno.csv').query('ano==2026'),on='cd_ibge',validate='one_to_one').sort_values('cd_ibge')
x = a[['Lula','Flavio','Cury','Renan','Caiado','Demais']].to_numpy(float)
x = np.column_stack([x,a.QT_VOTOS_BRANCOS+a.QT_TOTAL_VOTOS_NULOS,a.QT_ABSTENCOES])
x /= x.sum(1,keepdims=True)
y = np.column_stack([a.pt,a.adv,a.brancos+a.nulos,a.abstencoes])
n = y.sum(1)
idx = pd.Categorical(a.regiao).codes
X,Y,N,I = jnp.array(x),jnp.array(y),jnp.array(n),jnp.array(idx)
def model():
    phi = numpyro.sample('phi',dist.Dirichlet(jnp.ones(4)).expand((5,8)))
    kappa = numpyro.sample('kappa',dist.LogNormal(4.,1.).expand((8,)))
    b = numpyro.sample('b',dist.Dirichlet(phi[I]*kappa[None,:,None]))
    p = jnp.sum(X[:,:,None]*b,axis=1)
    numpyro.sample('y',dist.Multinomial(total_count=N,probs=p),obs=Y)
kernel = NUTS(model,target_accept_prob=.9,max_tree_depth=7,init_strategy=init_to_value(values={'phi':np.tile(y.sum(0)/y.sum(),(5,8,1)),'kappa':np.full(8,50.),'b':np.tile(y/y.sum(1,keepdims=True),(8,1,1)).transpose(1,0,2)}))
fit = MCMC(kernel,num_warmup=40,num_samples=20,num_chains=1,progress_bar=False)
import time
t=time.time()
fit.run(random.PRNGKey(20261026),extra_fields=('diverging','num_steps','accept_prob'))
print('SEGUNDOS',time.time()-t,flush=True)
print({k:np.asarray(z).mean().item() for k,z in fit.get_extra_fields().items()},flush=True)
