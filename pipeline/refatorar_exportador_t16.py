"""Refatoração local única: compartilha o exportador entre coordenadas exatas."""
from pathlib import Path
import ast
p=Path(__file__).with_name('inferencia_t16.py')
s=p.read_text(encoding='utf-8')
inicio=s.index('    # Diagnóstico clássico split R-hat/ESS')
fim=s.index('\n\ndef limites_sem_modelo',inicio)
bloco=s[inicio:fim]
assert bloco.rstrip().endswith('return tabela')
cabecalho='''def exportar_bayes(data,args,draws,extras,segundos,laplace_registro,energias_iniciais):
    from numpyro.diagnostics import summary
    regioes=sorted(data['z'].regiao.unique())
    gi=np.array([regioes.index(g) for g in data['z'].regiao])
    x,n,y=data['x'],data['n'],data['y']
    r=len(data['nomes']);ng=len(regioes)
    origens=np.array([x[gi==g].sum(0) for g in range(ng)])
    aproximacao=args.aproximacao
'''
substituto='    return exportar_bayes(data,args,draws,extras,segundos,laplace_registro,energias_iniciais)\n\n\n'+cabecalho+bloco
novo=s[:inicio]+substituto+s[fim:]
ast.parse(novo)
p.write_text(novo,encoding='utf-8')
print('Exportador compartilhado extraído; sintaxe validada.')
