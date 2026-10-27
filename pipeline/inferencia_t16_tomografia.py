"""Coordenadas exatas de margens e razões de chances para Rosen R×C.

Não muda a prior ou a verossimilhança. A margem do 2º turno é uma coordenada
própria; a informação de N não curva as direções de associação desconhecidas.
"""
from __future__ import annotations
import time
from pathlib import Path
import numpy as np
import jax
import jax.numpy as jnp
from jax import random,lax
from jax.nn import softmax,log_softmax
from jax.scipy.special import gammaln,digamma,polygamma,logsumexp
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC,NUTS,HMCGibbs,init_to_value
from numpyro.infer.util import initialize_model
from jax.flatten_util import ravel_pytree


def resolver_linear(h,v):
    d=v.shape[-1]
    if d==1:return v/h[...,0,0,None]
    if d!=3:return jnp.linalg.solve(h,v[...,None])[...,0]
    a=h[...,0,0];b=h[...,0,1];c=h[...,0,2]
    e=h[...,1,1];f=h[...,1,2];g=h[...,2,2]
    aa=e*g-f*f;bb=c*f-b*g;cc=b*f-c*e
    ee=a*g-c*c;ff=b*c-a*f;gg=a*e-b*b
    det=a*aa+b*bb+c*cc
    det=jnp.maximum(det,1e-30)
    return jnp.stack([aa*v[...,0]+bb*v[...,1]+cc*v[...,2],bb*v[...,0]+ee*v[...,1]+ff*v[...,2],cc*v[...,0]+ff*v[...,1]+gg*v[...,2]],axis=-1)/det[...,None]


def probabilidades(a,delta,x):
    # a: município x (R-1) x (C-1); última origem e destino são referências.
    m,rm,d=a.shape
    inter=jnp.concatenate([a,jnp.zeros((m,1,d))],axis=1)
    logits=jnp.concatenate([inter+delta[:,None,:],jnp.zeros((m,rm+1,1))],axis=2)
    lp=log_softmax(logits,axis=2);beta=jnp.exp(lp)
    theta=jnp.sum(x[:,:,None]*beta,axis=1)
    p=beta[:,:,:d]
    h=jnp.eye(d)[None,:,:]*jnp.sum(x[:,:,None]*p,axis=1)[:,None,:]-jnp.einsum('ir,irc,ird->icd',x,p,p)
    return beta,theta,h,lp


def ajustar_margem(a,theta,x,delta_inicial,iteracoes=35):
    d=theta.shape[1]-1
    inter=jnp.concatenate([a,jnp.zeros((a.shape[0],1,d))],axis=1)
    def objetivo(delta):
        logits=jnp.concatenate([inter+delta[:,None,:],jnp.zeros((a.shape[0],a.shape[1]+1,1))],axis=2)
        return jnp.sum(x*logsumexp(logits,axis=2),axis=1)-jnp.sum(theta[:,:d]*delta,axis=1)
    def f(delta):return probabilidades(a,delta,x)[1][:,:d]-theta[:,:d]
    def solve(_f,inicio):
        def cond(estado):
            i,delta,erro=estado
            return (i<iteracoes)&(erro>2e-11)
        def body(estado):
            i,delta,_=estado
            _,pred,h,_=probabilidades(a,delta,x)
            resid=pred[:,:d]-theta[:,:d]
            passo=resolver_linear(h+jnp.eye(d)[None,:,:]*1e-13,resid)
            fator=jnp.maximum(1.,jnp.max(jnp.abs(passo),axis=1)/5)
            passo=passo/fator[:,None]
            obj=objetivo(delta)
            def ruim(p):return objetivo(delta-p)>obj-1e-4*jnp.sum(resid*p,axis=1)+1e-13
            def back_cond(st):return (st[0]<8)&jnp.any(ruim(st[1]))
            def back_body(st):return st[0]+1,jnp.where(ruim(st[1])[:,None],st[1]*.5,st[1])
            _,passo=lax.while_loop(back_cond,back_body,(jnp.array(0),passo))
            novo=delta-passo
            erro=jnp.max(jnp.abs(f(novo)))
            return i+1,novo,erro
        return lax.while_loop(cond,body,(jnp.array(0),inicio,jnp.array(jnp.inf)))[1]
    def tangent_solve(g,v):
        cols=[g(jnp.broadcast_to(jnp.eye(d)[j],v.shape)) for j in range(d)]
        h=jnp.stack(cols,axis=-1)
        return resolver_linear(h,v)
    delta=lax.custom_root(f,delta_inicial,solve,tangent_solve)
    return delta,probabilidades(a,delta,x)


def momentos_associacao(alpha):
    # Covariância EXATA dos log-odds de uma Dirichlet e da diferença com
    # a última origem. É usada só como transformação de coordenadas.
    r,c=alpha.shape;d=c-1
    media_t=digamma(alpha[:,:d])-digamma(alpha[:,-1:])
    media=(media_t[:-1]-media_t[-1]).reshape((r-1)*d)
    vt=jnp.eye(d)[None,:,:]*polygamma(1,alpha[:,:d])[:,None,:]+polygamma(1,alpha[:,-1])[:,None,None]
    comum=jnp.broadcast_to(vt[-1][None,:,None,:],(r-1,d,r-1,d))
    diagonal=jnp.einsum('rs,rcd->rcsd',jnp.eye(r-1),vt[:-1])
    cov=(comum+diagonal).reshape((r-1)*d,(r-1)*d)
    chol=jnp.linalg.cholesky(cov+jnp.eye((r-1)*d)*1e-10)
    return media,chol


def pcn(rng_key,z,fator,passos=5,epsilon=.5,margens=3,mistura_rw=False):
    """Metropolis por unidade; proposta reversível em relação a N(0,I)."""
    def passo(estado,_):
        z,valor,key=estado;key,kn,ku,kt=random.split(key,4)
        ruido=random.normal(kn,z.shape)
        candidato=jnp.sqrt(1-epsilon**2)*z+epsilon*ruido
        if margens:candidato=candidato.at[:,:margens].set(ruido[:,:margens])
        rw=random.bernoulli(kt,.5,(z.shape[0],)) if mistura_rw else jnp.zeros((z.shape[0],),dtype=bool)
        candidato=candidato.at[:,margens:].set(jnp.where(rw[:,None],z[:,margens:]+epsilon*ruido[:,margens:],candidato[:,margens:]))
        novo=fator(candidato)
        correcao=(dist.Normal(0,1).log_prob(candidato[:,margens:])-dist.Normal(0,1).log_prob(z[:,margens:])).sum(axis=1)
        aceita=jnp.log(random.uniform(ku,(z.shape[0],)))<novo-valor+jnp.where(rw,correcao,0.)
        return (jnp.where(aceita[:,None],candidato,z),jnp.where(aceita,novo,valor),key),None
    return lax.scan(passo,(z,fator(z),rng_key),None,length=passos)[0][0]


def amostrar(data,args,saida,semente):
    regioes=sorted(data['z'].regiao.unique());ng=len(regioes)
    gi=np.array([regioes.index(g) for g in data['z'].regiao])
    ids=[jnp.array(np.where(gi==g)[0]) for g in range(ng)]
    x=data['x']/data['n'][:,None];y=data['y'];n=data['n'];m=len(n);r=x.shape[1];d=3;q=(r-1)*d
    X,Y,I=jnp.array(x),jnp.array(y),jnp.array(gi)
    base_theta=(y+.5)/(n[:,None]+2)
    nu0=np.log(base_theta[:,:d]/base_theta[:,-1:])
    gnu=np.eye(d)[None,:,:]*base_theta[:,:d,None]-base_theta[:,:d,None]*base_theta[:,None,:d]
    fisher=n[:,None,None]*gnu
    lnu=np.linalg.inv(np.linalg.cholesky(fisher)).transpose(0,2,1)
    cache=np.load(saida/f'geometria_laplace_{data["cenario"]}.npz')
    phi0=cache['phi'];kap0=cache['kappa'];alpha0=phi0*kap0[None,:,None]
    medias=[];chols=[]
    for g in range(ng):
        mm,ll=momentos_associacao(jnp.array(alpha0[g]));medias.append(np.asarray(mm));chols.append(np.asarray(ll))
    medias=np.array(medias);a0=medias[gi].reshape(m,r-1,d)
    # Aproximação gaussiana somente para as COORDENADAS de associação, já
    # condicionada à margem. O jacobiano mantém a posterior original exata.
    from scipy.special import polygamma as psi1
    vt0=np.eye(d)[None,None,:,:]*psi1(1,alpha0[:,:,:d])[:,:,:,None]+psi1(1,alpha0[:,:,-1])[:,:,None,None]
    gp0=np.eye(d)[None,None,:,:]*phi0[:,:,:d,None]-phi0[:,:,:d,None]*phi0[:,:,None,:d]
    prod0=vt0@gp0;k0=gp0@prod0
    s0=np.einsum('ir,ircd->icd',x*x,k0[gi])+gnu/n[:,None,None]
    cruz0=x[:,:,None,None]*prod0[gi]
    c0=(cruz0[:,:-1]-cruz0[:,-1:]).reshape(m,q,d)
    l0=np.array(chols)[gi]
    br=np.linalg.solve(l0,c0)
    u=np.linalg.solve(np.linalg.cholesky(s0),br.transpose(0,2,1)).transpose(0,2,1)
    ev,vec=np.linalg.eigh(np.einsum('ijk,ijl->ikl',u,u))
    ev=np.maximum(ev,0);evc=np.minimum(ev,.9)
    rr=np.einsum('ijk,ikl->ijl',u,vec)
    ff=np.where(ev>1e-12,(np.sqrt(1-evc)-1)/np.maximum(ev,1e-12),-.5)
    logjac_t=.5*np.log1p(-evc).sum()
    for ii in np.linspace(0,m-1,min(6,m),dtype=int):
        tt=np.eye(q)+(rr[ii]*ff[ii])@rr[ii].T
        if abs(np.linalg.slogdet(tt)[1]-.5*np.log1p(-evc[ii]).sum())>1e-6:raise RuntimeError('Jacobian da geometria condicional não fecha.')
    RCOND,FCOND=jnp.array(rr),jnp.array(ff)
    mu0=np.sum(x[:,:,None]*phi0[gi],axis=1)
    desloc0=np.einsum('iqc,ic->iq',c0,np.linalg.solve(s0,(base_theta[:,:d]-mu0[:,:d])[:,:,None])[:,:,0])
    desloc0=5*np.tanh(desloc0/5)
    a0=(medias[gi]+desloc0).reshape(m,r-1,d)
    delta0=np.array(nu0)
    delta_ref,(bref,tref,href,_)=ajustar_margem(jnp.array(a0),jnp.array(base_theta),X,jnp.array(delta0),iteracoes=100)
    erro_ref=float(jnp.max(jnp.abs(tref-jnp.array(base_theta))))
    if erro_ref>1e-8:raise RuntimeError('Não convergiu o ponto inicial da tomografia: '+str(erro_ref))
    # Derivada implícita da solução de referência: início próximo para Newton.
    p=np.asarray(bref[:,:,:d]);h=np.asarray(href)
    covb=np.eye(d)[None,None,:,:]*p[:,:,:,None]-p[:,:,:,None]*p[:,:,None,:]
    j_a=(x[:,:r-1,None,None]*covb[:,:r-1]).transpose(0,2,1,3).reshape(m,d,q)
    j_delta_a=-np.linalg.solve(h,j_a)
    j_delta_nu=np.linalg.solve(h,gnu)
    NU0,LNU,A0,DREF,JA,JN=[jnp.array(z) for z in [nu0,lnu,a0,np.asarray(delta_ref),j_delta_a,j_delta_nu]]
    origem=np.array([data['x'][gi==g].sum(0) for g in range(ng)])
    contagens=jnp.array(np.bincount(gi,minlength=ng))
    def locais(phi,kappa,z):
        nu=NU0+jnp.einsum('ijk,ik->ij',LNU,z[:,:d]);theta=softmax(jnp.concatenate([nu,jnp.zeros((m,1))],axis=1),axis=1)
        alpha=phi*kappa[None,:,None]
        medias,las=jax.vmap(momentos_associacao)(alpha)
        vt=jnp.eye(d)[None,None,:,:]*polygamma(1,alpha[:,:,:d])[:,:,:,None]+polygamma(1,alpha[:,:,-1])[:,:,None,None]
        gp=jnp.eye(d)[None,None,:,:]*phi[:,:,:d,None]-phi[:,:,:d,None]*phi[:,:,None,:d]
        prod=vt@gp;kk=gp@prod
        mu=jnp.sum(X[:,:,None]*phi[I],axis=1)
        gn=jnp.eye(d)[None,:,:]*theta[:,:d,None]-theta[:,:d,None]*theta[:,None,:d]
        ss=jnp.einsum('ir,ircd->icd',X*X,kk[I])+gn/jnp.array(n)[:,None,None]
        cruz=X[:,:,None,None]*prod[I]
        cc=(cruz[:,:-1]-cruz[:,-1:]).reshape(m,q,d)
        desloc=jnp.einsum('iqc,ic->iq',cc,resolver_linear(ss,theta[:,:d]-mu[:,:d]))
        desloc=5*jnp.tanh(desloc/5)
        za=z[:,d:]+jnp.einsum('ijk,ik->ij',RCOND,FCOND*jnp.einsum('ijk,ij->ik',RCOND,z[:,d:]))
        af=jnp.zeros((m,q))
        for g,ix in enumerate(ids):af=af.at[ix].set(medias[g]+desloc[ix]+za[ix]@las[g].T)
        a=af.reshape(m,r-1,d)
        guess=DREF+jnp.einsum('icj,ij->ic',JA,(a-A0).reshape(m,q))+jnp.einsum('icj,ij->ic',JN,nu-NU0)
        _,(beta,pred,h,lp)=ajustar_margem(a,theta,X,guess)
        erro=jnp.max(jnp.abs(pred-theta),axis=1)
        sinal,logdet_h=jnp.linalg.slogdet(h)
        valida=(erro<1e-8)&(sinal>0)&jnp.all(jnp.isfinite(lp),axis=(1,2))
        norma=gammaln(alpha.sum(2))-gammaln(alpha).sum(2)
        prior=jnp.sum(alpha[I]*lp,axis=(1,2))
        jac_margem=jnp.sum(jnp.log(theta),axis=1)-logdet_h
        jac_a=jnp.sum(contagens*jnp.sum(jnp.log(jnp.diagonal(las,axis1=1,axis2=2)),axis=1))
        jac_nu=jnp.sum(jnp.log(jnp.diagonal(LNU,axis1=1,axis2=2)))+logjac_t
        loglik=jnp.sum(Y*(jnp.log(theta)-jnp.log(jnp.array(base_theta))),axis=1)
        dens=prior+jac_margem+loglik-jnp.sum(dist.Normal(0,1).log_prob(z),axis=1)
        return jnp.where(valida,dens,-jnp.inf),jnp.sum(contagens[:,None]*norma)+jac_a+jac_nu,beta,theta,jnp.max(erro)
    def model():
        if args.prior_modelo=='gamma_referencia':
            phi=numpyro.sample('phi',dist.Dirichlet(jnp.ones(4)*4*args.prior).expand((ng,r)))
            kappa=numpyro.sample('kappa',dist.Gamma(16*args.prior,.5*args.prior).expand((r,)))
        else:
            phi=numpyro.sample('phi',dist.Dirichlet(jnp.ones(4)*args.prior).expand((ng,r)))
            kappa=numpyro.sample('kappa',dist.LogNormal(4.,1.5).expand((r,)))
        z=numpyro.sample('z_tabela',dist.Normal(jnp.zeros((m,d+q)),1).to_event(2))
        dens,const,beta,theta,erro=locais(phi,kappa,z)
        numpyro.factor('rosen_com_jacobiano',jnp.sum(dens)+const)
        numpyro.deterministic('b',beta);numpyro.deterministic('theta',theta);numpyro.deterministic('erro_raiz',erro)
    # z=0: médias dos log-odds do prior e margem observada suavizada.
    ini={'phi':phi0,'kappa':kap0,'z_tabela':np.zeros((m,d+q))}
    info=initialize_model(random.PRNGKey(semente),model,init_strategy=init_to_value(values=ini))
    def post(z):
        v=info.postprocess_fn(z);b=v['b']
        flux=jnp.stack([jnp.sum(jnp.array(data['x'][np.array(ix)])[:,:,None]*b[ix],axis=0) for ix in ids])
        audit=jnp.array(np.linspace(0,m-1,min(40,m),dtype=int))
        return {'phi':v['phi'],'kappa':v['kappa'],'fluxos_regiao':flux,'fluxos_nacional':flux.sum(0),
                'b_auditoria':b[audit],'z_auditoria':v['z_tabela'][audit],'theta':v['theta'].astype(jnp.float32),'erro_raiz':v['erro_raiz']}
    if args.amostrador=='blocos':
        def gibbs_fn(*,rng_key,gibbs_sites,hmc_sites):
            fator=lambda zz:locais(hmc_sites['phi'],hmc_sites['kappa'],zz)[0]
            zz=pcn(rng_key,gibbs_sites['z_tabela'],fator,passos=8,epsilon=.5,margens=3,mistura_rw=True)
            return {'z_tabela':zz}
        inner=NUTS(model,dense_mass=[('kappa','phi')],inverse_mass_matrix={('kappa','phi'):jnp.array(cache['cov'])},
                   adapt_mass_matrix=False,target_accept_prob=args.target_accept,max_tree_depth=args.tree_depth)
        kernel=HMCGibbs(inner,gibbs_fn=gibbs_fn,gibbs_sites=['z_tabela'])
        campos=('hmc_state.diverging','hmc_state.num_steps','hmc_state.accept_prob')
    else:
        im={('kappa','phi'):jnp.array(cache['cov']),('z_tabela',):jnp.ones(m*(d+q))}
        kernel=NUTS(potential_fn=info.potential_fn,dense_mass=[('kappa','phi')],inverse_mass_matrix=im,
                    adapt_mass_matrix=False,target_accept_prob=args.target_accept,max_tree_depth=args.tree_depth)
        campos=('diverging','num_steps','accept_prob')
    inicial={k:jnp.stack([v]*args.chains) for k,v in info.param_info.z.items()}
    rng=np.random.default_rng(semente+41)
    hp,abrir=ravel_pytree({k:info.param_info.z[k] for k in ['kappa','phi']})
    ruido=rng.normal(size=(args.chains,len(hp)))@np.linalg.cholesky(cache['cov']).T*.35
    energeticas=[]
    valgrad=jax.jit(jax.value_and_grad(info.potential_fn))
    for chain in range(args.chains):
        cand={**abrir(hp+jnp.array(ruido[chain])),'z_tabela':jnp.array(rng.normal(0,.15,size=(m,d+q)))}
        for _ in range(20):
            pot,grad=valgrad(cand)
            if np.isfinite(float(pot)) and all(np.isfinite(np.asarray(v)).all() for v in grad.values()):break
            cand={k:info.param_info.z[k]+(v-info.param_info.z[k])*.5 for k,v in cand.items()}
        else:raise RuntimeError('Inicialização não finita na tomografia.')
        for k in cand:inicial[k]=inicial[k].at[chain].set(cand[k])
        energeticas.append(float(pot))
    print('Tomografia: inícios finitos '+str(energeticas)+'; erro referência '+str(erro_ref),flush=True)
    fit=MCMC(kernel,num_warmup=args.tune,num_samples=args.draws,num_chains=args.chains,chain_method='parallel',
             postprocess_fn=post,progress_bar=args.progresso,progress_rate=100)
    inicio=time.time()
    fit.run(random.split(random.PRNGKey(semente+11),args.chains),init_params=inicial,extra_fields=campos)
    amostras={k:np.asarray(v) for k,v in fit.get_samples(group_by_chain=True).items()}
    extras={k.removeprefix('hmc_state.'):np.asarray(v) for k,v in fit.get_extra_fields(group_by_chain=True).items()}
    segundos=time.time()-inicio
    meta={'metodo_geometria':'margens e razões de chances; jacobiano exato','erro_raiz_referencia':erro_ref,
          'erro_raiz_max_amostras':float(amostras.pop('erro_raiz').max()),'iteracoes_max_newton':35,
          'amostrador':args.amostrador,'passos_metropolis_locais':8 if args.amostrador=='blocos' else 0}
    return amostras,extras,segundos,meta,energeticas
