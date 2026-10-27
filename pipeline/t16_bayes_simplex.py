"""Bayes DM regional: slice hit-and-run diretamente no simplex.

Remove a geometria curva dos logits; usa densidade DM exata, priors próprias,
direções de covariância fixa e Metropolis para a dispersão. Sem Hamiltonianos.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,importlib.util,json,subprocess,sys,time,os
import numpy as np
from scipy.special import gammaln,digamma,polygamma,expit,log_expit
from scipy.optimize import minimize

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dados/saida/2turno/inferencia_t16'
sp=importlib.util.spec_from_file_location('v2',ROOT/'pipeline/inferencia_t16_v2.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)


def linha_slice(rng,beta,mu,k,logp,x,y,gy,chol,prior=2.,global_move=True):
    r=beta.shape[0]
    if global_move:
        free=(chol@rng.normal(size=r*3)).reshape(r,3)
        direcao=np.column_stack([free,-free.sum(1)])
    else:
        direcao=np.zeros_like(beta);i=rng.integers(r);a,b=rng.choice(4,2,replace=False);direcao[i,a]=1;direcao[i,b]=-1
    md=x@direcao
    pos=direcao>1e-30;neg=direcao < -1e-30
    lo=float(np.max(-beta[pos]/direcao[pos]));hi=float(np.min(-beta[neg]/direcao[neg]))
    alvo=logp-rng.exponential()
    for _ in range(150):
        passo=rng.uniform(lo,hi);bb=beta+passo*direcao;mm=mu+passo*md
        if bb.min()<=0 or mm.min()<=0:ll=-np.inf
        else:ll=float(np.sum(gammaln(y+mm*k[:,None])-gammaln(mm*k[:,None])-gy)+(prior-1)*np.log(bb).sum())
        if ll>=alvo:return bb,mm,ll
        if passo<0:lo=passo
        else:hi=passo
    raise RuntimeError('Slice não encontrou ponto; nenhuma amostra pode ser aprovada.')


class Regiao:
    def __init__(self,x,y,n,ref,prior=2.):
        self.x=x;self.y=y;self.n=n;self.r=x.shape[1];self.ref=ref;self.lr=np.log(n/ref);self.prior=prior
        self.gy=gammaln(y+1);self.gn=gammaln(n+1)
    def beta(self,p):
        v=p[:self.r*3].reshape(self.r,3);return np.column_stack([v,1-v.sum(1)])
    def kappa(self,eta):return np.exp(eta[0]+self.lr*expit(eta[1]))
    def beta_lp(self,b,mu,k):
        if b.min()<=0 or mu.min()<=0:return -np.inf
        return float(np.sum(gammaln(self.y+mu*k[:,None])-gammaln(mu*k[:,None])-self.gy)+(self.prior-1)*np.log(b).sum())
    def hp_lp(self,eta,k):
        return float(np.sum(self.gn+gammaln(k)-gammaln(k+self.n))-.5*((eta[0]-np.log(1200))/1.2)**2+2*log_expit(eta[1])+2*log_expit(-eta[1]))
    def value_grad(self,p):
        b=self.beta(p);eta=p[-2:];mu=self.x@b;k=self.kappa(eta);gamma=expit(eta[1])
        if b.min()<=0 or not np.isfinite(k).all():return 1e50,np.zeros_like(p)
        alpha=mu*k[:,None];dif=digamma(self.y+alpha)-digamma(alpha)
        gb=self.x.T@(k[:,None]*(dif[:,:3]-dif[:,-1:]))+(self.prior-1)*(1/b[:,:3]-1/b[:,-1:])
        dk=digamma(k)-digamma(k+self.n)+np.sum(mu*dif,axis=1)
        gh=np.array([np.sum(dk*k)-(eta[0]-np.log(1200))/1.2**2,np.sum(dk*k*self.lr)*gamma*(1-gamma)+2-4*gamma])
        lp=self.beta_lp(b,mu,k)+self.hp_lp(eta,k)
        return -lp,-np.r_[gb.ravel(),gh]
    def mode(self,b0):
        b=np.maximum(b0,.002);b/=b.sum(1,keepdims=True);p=np.r_[b[:,:3].ravel(),np.log(1200),-.6]
        eq=np.zeros((self.r,len(p)))
        for i in range(self.r):eq[i,i*3:i*3+3]=1
        fit=minimize(self.value_grad,p,jac=True,method='SLSQP',bounds=[(1e-8,1-1e-8)]*(self.r*3)+[(0,16),(-9,9)],
                     constraints=[{'type':'ineq','fun':lambda p:1-1e-8-eq@p,'jac':lambda p:-eq}],options={'maxiter':600,'ftol':1e-8})
        pp=fit.x if np.isfinite(fit.fun) and self.beta(fit.x).min()>0 else p
        b=self.beta(pp);eta=pp[-2:];k=self.kappa(eta);mu=self.x@b
        be=np.maximum(b,1e-4);be/=be.sum(1,keepdims=True)
        aa=mu*k[:,None];w=k[:,None]**2*(polygamma(1,aa)-polygamma(1,aa+self.y))
        h=np.zeros((self.r*3,self.r*3))
        for c in range(3):
            for d in range(3):
                wc=w[:,-1]+(w[:,c] if c==d else 0)
                a=self.x.T@(wc[:,None]*self.x)
                h[np.ix_(np.arange(self.r)*3+c,np.arange(self.r)*3+d)]=a
        for i in range(self.r):h[i*3:i*3+3,i*3:i*3+3]+=(self.prior-1)*(np.diag(1/be[i,:3]**2)+np.ones((3,3))/be[i,3]**2)
        ev,vec=np.linalg.eigh((h+h.T)/2);cov=(vec/np.maximum(ev,1.))@vec.T;chol=np.linalg.cholesky(cov)
        hh=np.empty((2,2));eps=1e-4
        for j in range(2):
            plus=pp.copy();minus=pp.copy();plus[-2+j]+=eps;minus[-2+j]-=eps
            hh[:,j]=(self.value_grad(plus)[1][-2:]-self.value_grad(minus)[1][-2:])/(2*eps)
        ee,vv=np.linalg.eigh((hh+hh.T)/2);hc=(vv/np.maximum(np.abs(ee),1.))@vv.T
        return b,eta,chol,np.linalg.cholesky(hc),{'sucesso_modo':bool(fit.success),'iteracoes_modo':int(fit.nit),'mensagem_modo':str(fit.message)}


def worker(args):
    data=m.get_data(args.cenario,'seis');g=sorted(data['z'].regiao.unique()).index(args.regiao);mask=data['z'].regiao.eq(args.regiao).to_numpy()
    x=data['x'][mask]/data['n'][mask,None];y=data['y'][mask];n=data['n'][mask];ref=float(np.median(data['n']))
    reg=Regiao(x,y,n,ref,args.prior);ponto=np.load(OUT/f'amostras_restrito_{args.cenario}_seis.npz')['ponto'][g]
    log=m.Log(f'bayes_slice_{args.cenario}_seis_{args.regiao}',args.deadline);log.watch()
    b0,e0,chol,hchol,opt=reg.mode(ponto);log.last=time.monotonic();log.emit('modo',**opt)
    bs=[];ps=[];gs=[];ace=[]
    for chain in range(4):
        rng=np.random.default_rng(m.SEED+g*100+chain*701);b=b0.copy();eta=e0.copy();mu=x@b;k=reg.kappa(eta)
        lb=reg.beta_lp(b,mu,k);lp=lb+reg.hp_lp(eta,k);savedb=[];savedp=[];savedg=[];accepted=0;scale=1.
        for t in range(args.burn+args.draws):
            for j in range(6):
                b,mu,lb=linha_slice(rng,b,mu,k,lb,x,y,reg.gy,chol,args.prior,global_move=j<5)
            lp=lb+reg.hp_lp(eta,k)
            en=eta+hchol@rng.normal(size=2)*1.7*scale;kn=reg.kappa(en)
            ln=reg.beta_lp(b,mu,kn)+reg.hp_lp(en,kn) if np.isfinite(kn).all() else -np.inf
            ok=np.log(rng.uniform())<ln-lp
            if ok:eta=en;k=kn;lb=reg.beta_lp(b,mu,k);lp=ln;accepted+=1
            if t<args.burn:scale=float(np.clip(scale*np.exp((float(ok)-.35)/(t+20)**.6),.15,4))
            if t>=args.burn:savedb.append(b.copy());savedp.append(np.exp(eta[0]));savedg.append(expit(eta[1]))
            if (t+1)%100==0:
                log.last=time.monotonic();log.emit('progresso_slice',cadeia=chain,iteracao=t+1,total=args.burn+args.draws)
            if (t+1)%25==0:mu=x@b;lb=reg.beta_lp(b,mu,k)
        bs.append(savedb);ps.append(savedp);gs.append(savedg);ace.append(accepted/(args.burn+args.draws))
    np.savez_compressed(OUT/f'mcmc_slice_{args.cenario}_{args.regiao}.npz',b=np.array(bs),precisao=np.array(ps),expo=np.array(gs),aceitacao=np.array(ace))
    log.emit('concluído');log.stop.set()


def run(args):
    data=m.get_data(args.cenario,'seis');regions=sorted(data['z'].regiao.unique());processos=[]
    for g in regions:
        argv=[sys.executable,'-I','-X','utf8',str(Path(__file__)),'--regiao',g,'--cenario',args.cenario,'--burn',str(args.burn),'--draws',str(args.draws),'--prior',str(args.prior),'--deadline',str(args.deadline)]
        f=(OUT/f'console_slice_{args.cenario}_{g}.log').open('w',encoding='utf-8')
        proc=subprocess.Popen(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        processos.append((proc,f,g))
    try:
        while any(p.poll() is None for p,_,_ in processos):
            if time.time()>args.deadline:
                for p,_,_ in processos:
                    if p.poll() is None:p.terminate()
                raise RuntimeError('Prazo absoluto: amostragem interrompida sem publicar matriz.')
            time.sleep(2)
        if any(p.returncode!=0 for p,_,_ in processos):raise RuntimeError('Uma região não concluiu; ver logs. Nenhuma matriz publicada.')
    finally:
        for p,f,_ in processos:
            if p.poll() is None:p.terminate()
            f.close()
    b=np.stack([np.load(OUT/f'mcmc_slice_{args.cenario}_{g}.npz')['b'] for g in regions],axis=2)
    prec=np.stack([np.load(OUT/f'mcmc_slice_{args.cenario}_{g}.npz')['precisao'] for g in regions],axis=2)
    expo=np.stack([np.load(OUT/f'mcmc_slice_{args.cenario}_{g}.npz')['expo'] for g in regions],axis=2)
    gi=pd_codes(data['z'].regiao,regions);counts=np.array([data['x'][gi==j].sum(0) for j in range(len(regions))])
    fluxreg=b*counts[None,None,:,:,None];nat=fluxreg.sum(2)
    diag=m.diagnostics({'b':b,'precisao':prec,'expo':expo,'fluxo_nacional':nat,'fluxo_regional':fluxreg})
    ok=bool(np.isfinite(diag[['rhat','ess_bulk','ess_tail']]).all().all() and diag.rhat.lt(1.01).all() and diag.ess_bulk.gt(400).all() and diag.ess_tail.gt(400).all())
    key=f'bayes_slice_{args.cenario}_seis';m.save(diag,'diagnostico_'+key+'.csv')
    meta={'utc':m.utc(),'modelo':'regressão ecológica DM regional; slice no simplex e Metropolis para dispersão','cenario':args.cenario,'grupos':data['nomes'],'efeito_uf':False,
          'prior_dirichlet':args.prior,'expoente_regional':True,'cadeias':4,'aquecimento':args.burn,'amostras_por_cadeia':args.draws,'semente':m.SEED,
          'rhat_max':float(diag.rhat.max()),'ess_bulk_min':float(diag.ess_bulk.min()),'ess_tail_min':float(diag.ess_tail.min()),'divergencias':0,
          'divergencia_hamiltoniana_aplicavel':False,'falhas_numericas':0,'convergiu':ok}
    m.js(meta,'diagnostico_'+key+'.json')
    if not ok:print('REPROVADO '+json.dumps(meta),flush=True);return
    nats=nat.reshape(-1,len(data['nomes']),4);regs=fluxreg.reshape(-1,len(regions),len(data['nomes']),4)
    tabs=[m.core.resumo_fluxos(nats,data['nomes'],data['x'].sum(0),'bayes_dm',args.cenario,tipo='credibilidade_modelo_95')]
    for j,g in enumerate(regions):tabs.append(m.core.resumo_fluxos(regs[:,j],data['nomes'],counts[j],'bayes_dm',args.cenario,area=g,tipo='credibilidade_modelo_95'))
    import pandas as pd
    table=pd.concat(tabs,ignore_index=True);table['convergiu']=True;table['grupos']='seis';m.save(table,key+'.csv')
    np.savez_compressed(OUT/f'amostras_{key}.npz',fluxos=nats,regioes=regs,nomes=np.array(data['nomes']),areas=np.array(regions),b=b,precisao=prec,expo=expo)
    bf=b.reshape(-1,len(regions),len(data['nomes']),4);pr=prec.reshape(-1,len(regions));ex=expo.reshape(-1,len(regions));x=data['x']/data['n'][:,None];rng=np.random.default_rng(m.SEED+81);rep=[]
    pred=np.sum(data['x'][:,:,None]*bf.mean(0)[gi],axis=1)
    for s in np.linspace(0,len(bf)-1,400,dtype=int):
        mu=np.sum(x[:,:,None]*bf[s,gi],axis=1);k=pr[s,gi]*(data['n']/np.median(data['n']))**ex[s,gi]
        gg=rng.gamma(mu*k[:,None],1);gg/=gg.sum(1,keepdims=True);rep.append(rng.multinomial(data['n'],gg))
    m.core.predicoes({**data,'cenario':'slice_'+args.cenario+'_seis'},pred,np.array(rep),'bayes_dm')
    print('APROVADO '+json.dumps(meta),flush=True)


def pd_codes(s,levels):return np.array([levels.index(v) for v in s])


def main():
    p=argparse.ArgumentParser();p.add_argument('--cenario',default='principal');p.add_argument('--regiao');p.add_argument('--draws',type=int,default=4000);p.add_argument('--burn',type=int,default=1000);p.add_argument('--prior',type=float,default=2.);p.add_argument('--deadline',type=float,required=True)
    a=p.parse_args()
    if a.regiao:worker(a)
    else:run(a)


if __name__=='__main__':main()
