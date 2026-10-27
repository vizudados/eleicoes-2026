"""Oráculo conjugado e diferenças finitas para o amostrador direto."""
from pathlib import Path
import importlib.util
import numpy as np
from scipy.special import gammaln
sp=importlib.util.spec_from_file_location('slice',Path(__file__).with_name('t16_bayes_simplex.py'));s=importlib.util.module_from_spec(sp);sp.loader.exec_module(s)
rng=np.random.default_rng(31)
x=np.ones((1,1));y=np.array([[40,35,5,20]]);k=np.array([1e8]);alpha=y[0]+2;media=alpha/alpha.sum()
cov=(np.diag(media)-np.outer(media,media))/(alpha.sum()+1);chol=np.linalg.cholesky(cov[:3,:3]);am=[]
for chain in range(4):
    b=media[None,:].copy();mu=b.copy();gy=gammaln(y+1)
    lp=float((gammaln(y+mu*k[:,None])-gammaln(mu*k[:,None])-gy).sum()+np.log(b).sum())
    for t in range(1400):
        for _ in range(4):b,mu,lp=s.linha_slice(rng,b,mu,k,lp,x,y,gy,chol,2.)
        if t>=400:am.append(b[0].copy())
a=np.array(am)
assert np.max(np.abs(a.mean(0)-media))<.006
assert np.max(np.abs(a.var(0)/np.diag(cov)-1))<.12
xx=rng.dirichlet(np.ones(3),size=20);bb=rng.dirichlet(np.ones(4)*3,size=3);nn=np.full(20,1200);yy=rng.multinomial(nn,xx@bb)
reg=s.Regiao(xx,yy,nn,1200,2.);p=np.r_[bb[:,:3].ravel(),np.log(1200),-.6]
val,g=reg.value_grad(p);fd=[]
for j in range(len(p)):
    e=np.zeros_like(p);e[j]=1e-5;fd.append((reg.value_grad(p+e)[0]-reg.value_grad(p-e)[0])/2e-5)
assert np.max(np.abs(g-np.array(fd))/(1+np.abs(g)))<.003
print('APROVADO: slice reproduz posterior Dirichlet conjugada no limite multinomial; gradiente DM validado por diferenças finitas.')
