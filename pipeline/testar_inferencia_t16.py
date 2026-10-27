"""Verificação matemática e de integridade; não altera entradas nem saídas."""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

arquivo=Path(__file__).with_name('inferencia_t16.py')
spec=importlib.util.spec_from_file_location('inferencia_t16',arquivo)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
rng=np.random.default_rng(17)

# Recuperação de uma matriz conhecida em um problema misto de posto completo.
x=rng.dirichlet(np.ones(8)*2,size=600)
verdade=rng.dirichlet(np.ones(4)*2,size=8)
y=x@verdade
obtido,_=mod.resolver_restrito(x.T@x,x.T@y)
assert np.max(np.abs(obtido-verdade))<.0002
assert np.allclose(obtido.sum(axis=1),1,atol=1e-9)
assert obtido.min()>=0 and obtido.max()<=1

# Maiores restos: preserva eleitorado, inclusive células com zero.
votos=np.array([[10,20,0,0],[0,0,2,3],[3,1,1,4]])
n=np.array([29,7,11])
ajuste=mod.arredondar_margem(votos,n)
assert np.array_equal(ajuste.sum(axis=1),n)
assert (ajuste>=0).all()
assert np.max(np.abs(ajuste-votos/votos.sum(axis=1,keepdims=True)*n[:,None]))<1

# Verifica os momentos usados na integração por Monte Carlo independente.
phi=np.array([[.65,.2,.05,.1],[.15,.55,.1,.2]])
k=np.array([40.,25.]); shares=np.array([.6,.4]); count=300
b=rng.gamma(phi[None,:,:]*k[None,:,None],1,size=(80000,2,4))
b/=b.sum(axis=2,keepdims=True)
theta=np.sum(b*shares[None,:,None],axis=1)
urna=rng.multinomial(count,theta)/count
mu=shares@phi
var=sum(shares[i]**2*(np.diag(phi[i])-np.outer(phi[i],phi[i]))/(k[i]+1) for i in range(2))
var=(1-1/count)*var+(np.diag(mu)-np.outer(mu,mu))/count
assert np.max(np.abs(urna.mean(axis=0)-mu))<.001
assert np.max(np.abs(np.cov(urna.T)-var))<.0001

# Oráculo conjugado: em uma tabela de uma origem, a posterior é conhecida.
# Importance sampling verifica a transformação usada no modelo completo,
# inclusive o jacobiano; não depende de recuperar a própria implementação.
import jax
import jax.numpy as jnp
from numpyro.distributions import Dirichlet,Multinomial,Normal
from numpyro.distributions.transforms import StickBreakingTransform
jax.config.update('jax_enable_x64',True)
t=StickBreakingTransform()
alpha=np.array([2.,3.,4.,5.]); obs=np.array([45,30,10,15])
post=alpha+obs; mu=post/post.sum()
z0=np.asarray(t.inv(jnp.array(mu)))
sticks=mu[:3]/np.cumsum(mu[::-1])[::-1][:3]
curv=np.cumsum(post[::-1])[::-1][:3]*sticks*(1-sticks)
l=np.diag(1/np.sqrt(curv)); logdet=np.linalg.slogdet(l)[1]
w=rng.normal(size=(100000,3)); zz=z0+w@l.T; beta=t(jnp.array(zz))
logpeso=(Dirichlet(jnp.array(alpha)).log_prob(beta)+Multinomial(total_count=obs.sum(),probs=beta).log_prob(jnp.array(obs))
         +t.log_abs_det_jacobian(jnp.array(zz),beta)+logdet-Normal(0,1).log_prob(jnp.array(w)).sum(axis=1))
pesos=np.exp(np.asarray(logpeso)-np.max(np.asarray(logpeso))); pesos/=pesos.sum()
assert 1/np.sum(pesos**2)>50000
assert np.max(np.abs(np.sum(np.asarray(beta)*pesos[:,None],axis=0)-mu))<.001
from jax.nn import log_sigmoid
from jax.scipy.special import gammaln
u=jnp.array(zz)-jnp.log(jnp.arange(3,0,-1))
tail=np.cumsum(alpha[::-1])[::-1][1:]
fator=(jnp.array(alpha[:3])*log_sigmoid(u)+jnp.array(tail)*log_sigmoid(-u)).sum(axis=1)+gammaln(alpha.sum())-gammaln(jnp.array(alpha)).sum()
original=Dirichlet(jnp.array(alpha)).log_prob(beta)+t.log_abs_det_jacobian(jnp.array(zz),beta)
assert np.max(np.abs(np.asarray(fator-original)))<1e-9

# A geometria de baixo posto deve ter a mesma covariância e centro da densa.
dim=24; dp=np.exp(rng.normal(size=dim)); jj=rng.normal(size=(4,dim)); ww=np.exp(rng.normal(size=4))
ss=1/np.sqrt(dp); uu=ss[:,None]*jj.T*np.sqrt(ww)[None,:]
ev,vec=np.linalg.eigh(uu.T@uu);ev=np.maximum(ev,0);rr=uu@vec
raiz=np.sqrt(1+ev); ff=-1/(raiz*(1+raiz));gg=-1/(1+ev)
ll=np.diag(ss)@(np.eye(dim)+(rr*ff)@rr.T)
aa=np.diag(ss)@(np.eye(dim)+(rr*gg)@rr.T)@np.diag(1/ss)
hh=np.diag(dp)+jj.T@np.diag(ww)@jj
assert np.allclose(ll@ll.T,np.linalg.inv(hh),rtol=1e-9,atol=1e-10)
assert np.allclose(aa,np.linalg.solve(hh,np.diag(dp)),rtol=1e-9,atol=1e-10)
assert abs(np.linalg.slogdet(ll)[1]-(np.log(ss).sum()-.5*np.log1p(ev).sum()))<1e-9

# CSV de matriz: pontos nas fronteiras podem ter média fora dos percentis
# centrais por assimetria. Isso não autoriza trocar quantis por erro normal.
for p in mod.SAIDA.glob('restrito_*.csv'):
    d=pd.read_csv(p,sep=';',decimal=',',encoding='utf-8-sig')
    assert d[['media_pct','inferior_95_pct','superior_95_pct']].notna().all().all(),p
    assert d.inferior_95_pct.ge(-1e-8).all() and d.superior_95_pct.le(100+1e-8).all(),p
    assert d.inferior_95_pct.le(d.superior_95_pct+1e-8).all(),p
    assert np.allclose(d.groupby(['area','origem']).media_pct.sum(),100,atol=1e-6),p
for p in mod.SAIDA.glob('amostras_*.npz'):
    with np.load(p) as a:
        f=a['fluxos']
        assert np.isfinite(f).all() and f.min()>=-1e-5,p
        assert np.allclose(f.sum(axis=2),f.sum(axis=2)[0],rtol=1e-7,atol=.1),p
print('APROVADO: matriz conhecida, simplex, maiores restos, momentos, jacobiano contra posterior conjugada e integridade dos arquivos.')
