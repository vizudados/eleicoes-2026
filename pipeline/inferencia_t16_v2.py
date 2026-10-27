"""Reinício T16: QP com bootstrap UF e regressão ecológica bayesiana DM.

Somente saídas próprias, sem integração/publicação. Logs e watchdog de 10 min.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,importlib.metadata,json,os,re,sys,threading,time
from datetime import datetime,timezone
from pathlib import Path
os.environ.setdefault('JAX_ENABLE_X64','true')
os.environ.setdefault('XLA_FLAGS','--xla_force_host_platform_device_count=4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.linalg import null_space
from scipy.optimize import minimize
import osqp

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dados/saida/2turno/inferencia_t16'
SEED=20261027
spec=importlib.util.spec_from_file_location('t16_core',Path(__file__).with_name('t16_core.py'))
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
core.SEMENTE=SEED


def save(d,name):core.gravar(d,name)
def read(name):return core.ler(name)
def js(o,name):core.json_gravar(o,name)
def utc():return datetime.now(timezone.utc).isoformat()


class Log:
    def __init__(self,name,deadline=None):
        OUT.mkdir(parents=True,exist_ok=True)
        self.path=OUT/(name+'.log');self.lock=threading.Lock();self.last=time.monotonic();self.stop=threading.Event();self.deadline=deadline
        self.emit('início',semente=SEED)
    def emit(self,event,**kw):
        with self.lock:
            with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps({'utc':utc(),'evento':event,**kw},ensure_ascii=False)+'\n')
        print(event+' '+json.dumps(kw,ensure_ascii=False),flush=True)
    def write(self,s):
        s=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',s)
        m=re.search(r'(\d+)/(\d+)',s)
        if m:
            i,total=map(int,m.groups())
            if i>0:
                self.last=time.monotonic()
                c=re.search(r'chain\s+(\d+)',s)
                self.emit('progresso_mcmc',iteracao=i,total=total,cadeia=int(c.group(1)) if c else None)
        return len(s)
    def flush(self):pass
    def isatty(self):return False
    def watch(self):
        def run():
            while not self.stop.wait(30):
                if self.deadline and datetime.now(timezone.utc).timestamp()>self.deadline:
                    self.emit('interrompido_prazo_total');os._exit(125)
                if time.monotonic()-self.last>600:
                    self.emit('interrompido_sem_progresso_10_minutos');os._exit(124)
        threading.Thread(target=run,daemon=True).start()


def qp(a,b,inicial=None):
    r,c=b.shape;scale=np.trace(a);aa=a/scale;bb=b/scale
    eq=np.kron(np.eye(r),np.ones((1,c)))
    prob=osqp.OSQP()
    prob.setup(P=sparse.csc_matrix(np.triu(2*np.kron(aa,np.eye(c)))),q=-2*bb.ravel(),
               A=sparse.csc_matrix(np.vstack([eq,np.eye(r*c)])),l=np.r_[np.ones(r),np.zeros(r*c)],u=np.ones(r+r*c),
               verbose=False,eps_abs=1e-9,eps_rel=1e-9,max_iter=30000,polishing=False)
    if inicial is not None:prob.warm_start(x=inicial.ravel())
    fit=prob.solve(raise_error=False)
    if fit.info.status_val not in (1,2) or fit.info.prim_res>1e-7 or fit.info.dual_res>1e-7:
        return SLSQP(a,b,inicial)
    t=np.maximum(fit.x.reshape(r,c),0);t/=t.sum(1,keepdims=True)
    return t,{'iteracoes':fit.info.iter,'objetivo':fit.info.obj_val,'condicao':float(np.linalg.cond(aa)),'resolvedor':'OSQP','residuo_primal':fit.info.prim_res,'residuo_dual':fit.info.dual_res}
SLSQP=core.resolver_restrito
core.resolver_restrito=qp


def prepare():
    z,nums,cat=core.carregar()
    cols=['cd_ibge','nome','uf','regiao','populacao']+[c for c in z if c.startswith('cand_') or c.startswith('y_') or c.endswith('_1') or c.endswith('_2')]
    save(z[cols],'base_municipal.csv');save(cat.reset_index(),'catalogo_candidatos.csv')
    (OUT/'.gitignore').write_text('/amostras_*.npz\n/mcmc_*.npz\n',encoding='utf-8')
    hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in core.ENTRADAS}
    js({'utc':utc(),'semente':SEED,'sha256_entradas':hashes,'exterior':'excluído nos dois turnos'},'manifesto_entradas.json')
    # Limites contábeis municipais, sem hipótese de comportamento.
    d=get_data('principal','oito');rows=[]
    grupos=[(s,d['x'][:,i]) for i,s in enumerate(d['nomes'])]
    grupos.append(('Outros candidatos (todos)',d['x'][:,2:6].sum(1)))
    for nome,a in grupos:
        for j,dest in enumerate(core.COLUNAS):
            lo=np.maximum(0,a+d['y'][:,j]-d['n']).sum();hi=np.minimum(a,d['y'][:,j]).sum()
            rows.append({'origem':nome,'destino':dest,'limite_inferior_votos':lo,'limite_superior_votos':hi,'limite_inferior_pct':100*lo/a.sum(),'limite_superior_pct':100*hi/a.sum(),'natureza':'Limite determinístico, não IC95.'})
    save(pd.DataFrame(rows),'limites_sem_hipotese.csv')


def get_data(cenario='principal',grupos='seis'):
    z=read('base_municipal.csv');cat=read('catalogo_candidatos.csv').set_index('numero')
    nums=sorted(int(c[5:]) for c in z if c.startswith('cand_'))
    base=core.preparar(z,nums,cat,cenario)
    if grupos=='seis':
        ix=[base['nomes'].index(s) for s in core.LINHAS[2:5]]
        keep=[i for i in range(len(base['nomes'])) if i not in ix]
        # Ordem fixa: Lula, Flávio, três reunidos, demais, BN, NV.
        x=base['x'];nomes=base['nomes']
        ordered=[('Lula',x[:,nomes.index('Lula')]),('Flávio',x[:,nomes.index('Flávio')]),
                 ('Cury + Renan + Caiado',x[:,ix].sum(1))]+[(nomes[i],x[:,i]) for i in keep if nomes[i] not in ['Lula','Flávio']]
        base['nomes']=[a for a,_ in ordered];base['x']=np.column_stack([b for _,b in ordered])
    base['grupos']=grupos
    return base


def restricted(cenario,grupos,boot):
    d=get_data(cenario,grupos);nome=f'restrito_{cenario}_{grupos}'
    log=Log(nome);reg=sorted(d['z'].regiao.unique());gi=pd.Categorical(d['z'].regiao,categories=reg).codes
    st=core.estatisticas_regressao(d);r=len(d['nomes']);origin=np.array([d['x'][gi==g].sum(0) for g in range(len(reg))])
    ponto=[];diag=[]
    for g in reg:
        ufs=[u for u in st if st[u][2]==g];a=sum(st[u][0] for u in ufs);b=sum(st[u][1] for u in ufs)
        t,dd=qp(a,b);ponto.append(t);diag.append({'area':g,'n_ufs':len(ufs),'posto':int(np.linalg.matrix_rank(a)),**dd})
    ponto=np.array(ponto);rng=np.random.default_rng(SEED);draws=np.empty((boot,len(reg),r,4));rank_bad=0
    for k in range(boot):
        for j,g in enumerate(reg):
            ufs=[u for u in st if st[u][2]==g];us=rng.choice(ufs,len(ufs),replace=True)
            a=sum(st[u][0] for u in us);b=sum(st[u][1] for u in us)
            rank_bad+=int(np.linalg.matrix_rank(a)<r)
            t,_=qp(a,b,ponto[j]);draws[k,j]=t*origin[j,:,None]
        if (k+1)%100==0:log.emit('bootstrap',replicacao=k+1,total=boot)
    tabelas=[core.resumo_fluxos(draws.sum(1),d['nomes'],origin.sum(0),'restrito',cenario,tipo='percentil_bootstrap_UF_95',comparavel=d['comparavel'])]
    for j,g in enumerate(reg):tabelas.append(core.resumo_fluxos(draws[:,j],d['nomes'],origin[j],'restrito',cenario,area=g,tipo='percentil_bootstrap_UF_95',comparavel=d['comparavel']))
    tab=pd.concat(tabelas,ignore_index=True);tab['grupos']=grupos;save(tab,nome+'.csv');save(pd.DataFrame(diag),'diagnostico_'+nome+'.csv')
    np.savez_compressed(OUT/('amostras_'+nome+'.npz'),fluxos=draws.sum(1),regioes=draws,nomes=np.array(d['nomes']),areas=np.array(reg),ponto=ponto)
    pred=np.sum(d['x'][:,:,None]*ponto[gi],axis=1)
    d2={**d,'cenario':cenario+'_'+grupos};core.predicoes(d2,pred,None,'restrito')
    js({'replicacoes':boot,'ajustes_com_posto_incompleto':rank_bad,'semente':SEED},nome+'_bootstrap.json')
    log.emit('concluído',linhas=len(tab),posto_incompleto_bootstrap=rank_bad)


def diagnostics(arrays):
    from scipy.stats import rankdata,norm
    from numpyro.diagnostics import split_gelman_rubin,effective_sample_size
    rows=[]
    for name,a in arrays.items():
        for ix in np.ndindex(a.shape[2:]):
            v=a[(slice(None),slice(None))+ix]
            def ranks(x):return norm.ppf((rankdata(x).reshape(x.shape)-.375)/(x.size+.25))
            def split(x):
                k=x.shape[1]//2;return np.concatenate([x[:,:k],x[:,-k:]],axis=0)
            z=ranks(v);fold=ranks(np.abs(v-np.median(v)))
            rh=max(float(split_gelman_rubin(z)),float(split_gelman_rubin(fold)))
            ess=float(effective_sample_size(split(z)));q=np.quantile(v,[.05,.95])
            tail=min(float(effective_sample_size(split((v<=q[0]).astype(float)))),float(effective_sample_size(split((v>=q[1]).astype(float)))))
            rows.append({'parametro':name,'indice':','.join(map(str,ix)),'rhat':rh,'ess_bulk':ess,'ess_tail':tail})
    return pd.DataFrame(rows)


def bayes(args):
    import jax
    import jax.numpy as jnp
    from jax import random
    from jax.nn import softmax
    from jax.flatten_util import ravel_pytree
    import numpyro
    import numpyro.distributions as dist
    from numpyro.infer import NUTS,MCMC,init_to_value
    from numpyro.infer.util import initialize_model
    d=get_data(args.cenario,args.grupos);z=d['z'];reg=sorted(z.regiao.unique());ufs=sorted(z.uf.unique())
    gi=pd.Categorical(z.regiao,categories=reg).codes;ui=pd.Categorical(z.uf,categories=ufs).codes
    ur=np.array([reg.index(z.loc[z.uf.eq(u),'regiao'].iloc[0]) for u in ufs])
    r=len(d['nomes']);ng=len(reg);nu=len(ufs);x=d['x']/d['n'][:,None];n=d['n'];y=d['y']
    bases=[]
    for g in range(ng):
        inds=np.where(ur==g)[0];h=null_space(np.ones((1,len(inds))))
        b=np.zeros((nu,h.shape[1]));b[inds]=h;bases.append(b)
    basis=np.column_stack(bases)
    X,N,Y,G,U,UR,H=jnp.array(x),jnp.array(n),jnp.array(y),jnp.array(gi),jnp.array(ui),jnp.array(ur),jnp.array(basis)
    ref=float(np.median(n));nratio=jnp.array(n/ref)
    def model():
        b=numpyro.sample('b',dist.Dirichlet(jnp.ones(4)*args.prior).expand((ng,r)))
        precisao=numpyro.sample('precisao',dist.LogNormal(np.log(1200),1.2).expand((ng,)))
        expo=numpyro.sample('expo',dist.Beta(2.,2.))
        if args.sem_uf:bu=b[UR]
        else:
            escala=numpyro.sample('escala_uf',dist.HalfNormal(.4))
            bruto=numpyro.sample('z_uf',dist.Normal(jnp.zeros((basis.shape[1],3)),1).to_event(2))
            efe=H@bruto*escala;efe=jnp.concatenate([efe,jnp.zeros((nu,1))],axis=1)
            bu=softmax(jnp.log(b[UR])+efe[:,None,:],axis=2)
        numpyro.deterministic('beta_uf',bu)
        mu=jnp.sum(X[:,:,None]*bu[U],axis=1)
        k=precisao[G]*nratio**expo
        numpyro.sample('urna',dist.DirichletMultinomial(concentration=mu*k[:,None],total_count=N),obs=Y)
    key=f'bayes_{args.cenario}_{args.grupos}'+('_sem_uf' if args.sem_uf else '')
    log=Log(key,args.deadline);log.watch();stderr=sys.stderr
    refp=OUT/f'amostras_restrito_{args.cenario}_{args.grupos}.npz'
    if not refp.exists():restricted(args.cenario,args.grupos,100)
    ponto=np.load(refp)['ponto'];ponto=np.maximum(ponto,.001);ponto/=ponto.sum(2,keepdims=True)
    initial={'b':ponto,'precisao':np.full(ng,1200.),'expo':.35}
    if not args.sem_uf:initial.update({'escala_uf':.25,'z_uf':np.random.default_rng(SEED).normal(0,.1,size=(basis.shape[1],3))})
    info=initialize_model(random.PRNGKey(SEED),model,init_strategy=init_to_value(values=initial))
    flat,unpack=ravel_pytree(info.param_info.z)
    vg=jax.jit(jax.value_and_grad(lambda v:info.potential_fn(unpack(v))))
    calls=[0]
    def objective(v):
        value,grad=vg(jnp.array(v));calls[0]+=1
        if calls[0]%100==0:log.last=time.monotonic();log.emit('inicialização',avaliacoes=calls[0],potencial=float(value))
        return float(value),np.asarray(grad)
    t0=time.time();opt=minimize(objective,np.asarray(flat),jac=True,method='L-BFGS-B',options={'maxiter':1300,'ftol':1e-12,'gtol':1e-5})
    log.emit('modo_inicial',sucesso=bool(opt.success),iteracoes=opt.nit,gradiente_max=float(np.abs(opt.jac).max()))
    hess=np.asarray(jax.jit(jax.hessian(lambda v:info.potential_fn(unpack(v))))(jnp.array(opt.x)))
    vals,vec=np.linalg.eigh((hess+hess.T)/2);cov=(vec/np.maximum(np.abs(vals),max(.25,np.max(np.abs(vals))*1e-8)))@vec.T
    names=tuple(sorted(info.param_info.z))
    kernel=NUTS(potential_fn=info.potential_fn,dense_mass=[names],inverse_mass_matrix={names:jnp.array(cov)},
                adapt_mass_matrix=False,target_accept_prob=args.target_accept,max_tree_depth=9)
    rng=np.random.default_rng(SEED+11);starts=[];chol=np.linalg.cholesky(cov)
    for chain in range(args.chains):
        noise=chol@rng.normal(size=len(flat))*.5
        for _ in range(20):
            cand=opt.x+noise;val,grad=vg(jnp.array(cand))
            if np.isfinite(float(val)) and np.isfinite(np.asarray(grad)).all():break
            noise*=.5
        else:raise RuntimeError('Inicialização não finita.')
        starts.append(unpack(jnp.array(cand)))
    init={k:jnp.stack([a[k] for a in starts]) for k in names}
    def post(v):
        a=info.postprocess_fn(v)
        return {k:a[k] for k in ['b','precisao','expo','beta_uf']+([] if args.sem_uf else ['escala_uf','z_uf'])}
    fit=MCMC(kernel,num_warmup=args.tune,num_samples=args.draws,num_chains=args.chains,chain_method='parallel',postprocess_fn=post,progress_bar=True,progress_rate=50)
    log.last=time.monotonic();log.emit('amostragem',cadeias=args.chains,aquecimento=args.tune,amostras=args.draws,parametros=len(flat))
    try:
        sys.stderr=log
        fit.run(random.split(random.PRNGKey(SEED+22),args.chains),init_params=init,extra_fields=('diverging','num_steps','accept_prob'))
        draws={k:np.asarray(v) for k,v in fit.get_samples(group_by_chain=True).items()}
        extras={k:np.asarray(v) for k,v in fit.get_extra_fields(group_by_chain=True).items()}
    finally:sys.stderr=stderr
    log.emit('amostragem_concluída',segundos=time.time()-t0)
    counts=np.array([d['x'][ui==u].sum(0) for u in range(nu)])
    beta=draws['beta_uf'];fluxu=beta*counts[None,None,:,:,None];nat=fluxu.sum(2)
    regi=np.stack([fluxu[:,:,ur==g].sum(2) for g in range(ng)],axis=2)
    diag=diagnostics({**draws,'fluxo_nacional':nat,'fluxo_regional':regi})
    div=int(extras['diverging'].sum());ok=bool(np.isfinite(diag[['rhat','ess_bulk','ess_tail']]).all().all() and diag.rhat.lt(1.01).all() and diag.ess_bulk.gt(400).all() and diag.ess_tail.gt(400).all() and div==0)
    save(diag,'diagnostico_'+key+'.csv')
    meta={'utc':utc(),'modelo':'regressão ecológica Dirichlet-multinomial com perfis regionais e efeitos comuns de UF',
          'grupos':d['nomes'],'cenario':args.cenario,'efeito_uf':not args.sem_uf,'prior_dirichlet':args.prior,
          'cadeias':args.chains,'aquecimento':args.tune,'amostras_por_cadeia':args.draws,'semente':SEED,
          'rhat_max':float(diag.rhat.max()),'ess_bulk_min':float(diag.ess_bulk.min()),'ess_tail_min':float(diag.ess_tail.min()),'divergencias':div,
          'convergiu':ok,'segundos':time.time()-t0,'aceitacao_media':float(extras['accept_prob'].mean()),'fracao_limite_arvore':float(np.mean(extras['num_steps']>=511))}
    js(meta,'diagnostico_'+key+'.json')
    if not ok:
        log.emit('REPROVADO',**{k:meta[k] for k in ['rhat_max','ess_bulk_min','ess_tail_min','divergencias']});log.stop.set();return
    nat=nat.reshape(-1,r,4);regi=regi.reshape(-1,ng,r,4)
    rows=[core.resumo_fluxos(nat,d['nomes'],d['x'].sum(0),'bayes_dm',args.cenario,tipo='credibilidade_modelo_95',comparavel=d['comparavel'])]
    for g,area in enumerate(reg):rows.append(core.resumo_fluxos(regi[:,g],d['nomes'],d['x'][gi==g].sum(0),'bayes_dm',args.cenario,area=area,tipo='credibilidade_modelo_95',comparavel=d['comparavel']))
    table=pd.concat(rows,ignore_index=True);table['grupos']=args.grupos;table['convergiu']=True;save(table,key+'.csv')
    np.savez_compressed(OUT/('amostras_'+key+'.npz'),fluxos=nat,regioes=regi,nomes=np.array(d['nomes']),areas=np.array(reg),**draws)
    flatbeta=beta.reshape(-1,nu,r,4);pred=np.sum(d['x'][:,:,None]*flatbeta.mean(0)[ui],axis=1)
    prec=draws['precisao'].reshape(-1,ng);expo=draws['expo'].reshape(-1);rng=np.random.default_rng(SEED+77);rep=[]
    for s in np.linspace(0,len(flatbeta)-1,min(400,len(flatbeta)),dtype=int):
        mu=np.sum(x[:,:,None]*flatbeta[s,ui],axis=1);k=prec[s,gi]*(n/ref)**expo[s]
        gg=rng.gamma(mu*k[:,None],1);gg/=gg.sum(1,keepdims=True)
        rep.append(rng.multinomial(n,gg))
    core.predicoes({**d,'cenario':key.removeprefix('bayes_')},pred,np.asarray(rep),'bayes_dm')
    log.emit('APROVADO',**{k:meta[k] for k in ['rhat_max','ess_bulk_min','ess_tail_min','divergencias']});log.stop.set()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--etapa',choices=['preparar','restrito','bayes','bayes-slice'],required=True)
    p.add_argument('--cenario',default='principal',choices=['principal','sem_capitais','ate_50mil_habitantes','demais_separados','sem_nao_votou','base_aptos_2turno'])
    p.add_argument('--grupos',default='seis',choices=['seis','oito'])
    p.add_argument('--bootstrap',type=int,default=500);p.add_argument('--draws',type=int,default=1500);p.add_argument('--tune',type=int,default=1000)
    p.add_argument('--chains',type=int,default=4);p.add_argument('--target-accept',type=float,default=.95);p.add_argument('--prior',type=float,default=1.)
    p.add_argument('--sem-uf',action='store_true');p.add_argument('--deadline',type=float)
    args=p.parse_args()
    if args.etapa=='preparar':prepare()
    elif args.etapa=='restrito':restricted(args.cenario,args.grupos,args.bootstrap)
    elif args.etapa=='bayes-slice':
        import subprocess
        subprocess.run([sys.executable,'-I','-X','utf8',str(Path(__file__).with_name('t16_bayes_simplex.py')),'--cenario',args.cenario,'--burn',str(args.tune),'--draws',str(args.draws),'--prior',str(args.prior),'--deadline',str(args.deadline or time.time()+5400)],check=True,cwd=ROOT)
    else:bayes(args)


if __name__=='__main__':main()
