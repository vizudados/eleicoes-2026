"""Verifica raízes e jacobiano contra derivação numérica independente."""
import os
os.environ['JAX_ENABLE_X64']='true'
import importlib.util
from pathlib import Path
import numpy as np
import jax
import jax.numpy as jnp
from jax.nn import softmax
sp=importlib.util.spec_from_file_location('tomografia',Path(__file__).with_name('inferencia_t16_tomografia.py'))
t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t)
rng=np.random.default_rng(2026)
for r,c in [(2,2),(3,4),(8,4)]:
    d=c-1
    x=rng.dirichlet(np.ones(r),size=80)
    a=rng.normal(0,2,size=(80,r-1,d))
    nu=rng.normal(0,1,size=(80,d))
    theta=np.asarray(softmax(jnp.array(np.column_stack([nu,np.zeros(80)])),axis=1))
    delta,(b,p,h,lp)=t.ajustar_margem(jnp.array(a),jnp.array(theta),jnp.array(x),jnp.array(nu),iteracoes=80)
    assert np.max(np.abs(np.asarray(p)-theta))<1e-9
    assert np.max(np.abs(np.asarray(b).sum(axis=2)-1))<1e-10
    # Derivada da mudança (nu,a)-> log-odds de cada linha.
    for i in range(3):
        def mapa(v):
            nn=v[:d][None,:];aa=v[d:].reshape(1,r-1,d)
            tt=softmax(jnp.concatenate([nn,jnp.zeros((1,1))],axis=1),axis=1)
            _,(_,_,_,ll)=t.ajustar_margem(aa,tt,jnp.array(x[i:i+1]),nn,iteracoes=80)
            return (ll[:,:,:d]-ll[:,:,-1:]).reshape(r*d)
        v=np.concatenate([nu[i],a[i].ravel()])
        jac=np.asarray(jax.jacfwd(mapa)(jnp.array(v)))
        logjac=np.linalg.slogdet(jac)[1]
        esperado=np.log(theta[i]).sum()-np.linalg.slogdet(np.asarray(h[i]))[1]
        assert abs(logjac-esperado)<2e-7,(r,c,logjac,esperado)
        if i==0:
            mapa_jit=jax.jit(mapa);eps=1e-4
            fd=np.column_stack([(np.asarray(mapa_jit(jnp.array(v+np.eye(len(v))[k]*eps)))-np.asarray(mapa_jit(jnp.array(v-np.eye(len(v))[k]*eps))))/(2*eps) for k in range(len(v))])
            assert np.allclose(jac,fd,rtol=2e-4,atol=2e-5)

# Média e covariância dos log-odds Dirichlet: oráculo Monte Carlo.
alpha=np.array([[18.,2.,4.,3.],[3.,17.,2.,4.],[4.,3.,2.,14.]])
media,chol=t.momentos_associacao(jnp.array(alpha))
b=np.stack([rng.dirichlet(row,size=120000) for row in alpha],axis=1)
logit=np.log(b[:,:,:3]/b[:,:,-1:]);aa=(logit[:,:-1]-logit[:,-1:]).reshape(120000,6)
assert np.max(np.abs(aa.mean(0)-np.asarray(media)))<.015
assert np.max(np.abs(np.cov(aa.T)-np.asarray(chol)@np.asarray(chol).T))<.025
print('APROVADO: margens, simplex, jacobiano implícito e momentos dos log-odds.')

# Metropolis condicional: alvo normal conhecido, distinto da normal da proposta.
from jax import random,lax
from numpyro.distributions import Normal
media=jnp.array([.8,-.5]);desvio=jnp.array([.65,1.2])
fator=lambda zz:(Normal(media,desvio).log_prob(zz)-Normal(0,1).log_prob(zz)).sum(axis=1)
def etapa(estado,_):
    z,k=estado;k,kk=random.split(k)
    z=t.pcn(kk,z,fator,passos=1,epsilon=.5,margens=0)
    return (z,k),z
_,traj=jax.jit(lambda:lax.scan(etapa,(jnp.zeros((64,2)),random.PRNGKey(38)),None,length=5000))()
amostra=np.asarray(traj)[1000:].reshape(-1,2)
assert np.max(np.abs(amostra.mean(0)-np.asarray(media)))<.035
assert np.max(np.abs(amostra.std(0)-np.asarray(desvio)))<.035
print('APROVADO: Metropolis pCN preserva alvo condicional com média e variância conhecidas.')
