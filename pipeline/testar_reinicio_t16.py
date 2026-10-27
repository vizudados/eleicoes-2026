"""Testes matemáticos do reinício, sem leitura de resultados anteriores."""
from pathlib import Path
import importlib.util
import numpy as np
sp=importlib.util.spec_from_file_location('v2',Path(__file__).with_name('inferencia_t16_v2.py'))
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
rng=np.random.default_rng(71)
x=rng.dirichlet(np.ones(8)*2,size=800);verdade=rng.dirichlet(np.ones(4)*2,size=8);y=x@verdade
t,_=m.qp(x.T@x,x.T@y)
assert np.max(np.abs(t-verdade))<.0002
assert np.allclose(t.sum(1),1) and t.min()>=0 and t.max()<=1
d=m.get_data('principal','oito');est=m.core.estatisticas_regressao(d);rows=[]
for reg in sorted(d['z'].regiao.unique()):
    u=[v for v in est if est[v][2]==reg];a=sum(est[v][0] for v in u);b=sum(est[v][1] for v in u)
    q,qd=m.qp(a,b);s,sd=m.SLSQP(a,b)
    erro=float(np.max(np.abs(q-s)))
    obj=lambda z:np.sum(z*(a@z))-2*np.sum(z*b)
    assert abs(obj(q)-obj(s))<1e-8,(reg,erro,obj(q)-obj(s))
    rows.append({'regiao':reg,'maior_diferenca_coeficiente_osqp_slsqp':erro,'diferenca_objetivo':obj(q)-obj(s),'simplex_fecha':bool(np.allclose(q.sum(1),1))})
m.save(__import__('pandas').DataFrame(rows),'validacao_qp.csv')
mu=np.array([.4,.35,.05,.2]);k=600;n=1200
p=rng.dirichlet(k*mu,size=80000);v=rng.multinomial(n,p)/n
var=mu*(1-mu)*(n+k)/(n*(k+1))
assert np.max(np.abs(v.mean(0)-mu))<.0005
assert np.max(np.abs(v.var(0)/var-1))<.025
for nome in ['restrito_principal_seis.csv','restrito_principal_oito.csv']:
    f=m.read(nome)
    assert np.allclose(f.groupby(['area','origem']).media_pct.sum(),100,atol=1e-6)
    assert f.inferior_95_pct.ge(-1e-8).all() and f.superior_95_pct.le(100+1e-7).all()
print('APROVADO: QP recupera matriz conhecida, concorda com SLSQP, fecha simplex e DM tem momentos corretos.')
