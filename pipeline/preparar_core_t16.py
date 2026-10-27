"""Isola somente leitura e contas auditadas; não reaproveita resultados antigos."""
from pathlib import Path
import ast
p=Path(__file__).with_name('inferencia_t16.py')
s=p.read_text(encoding='utf-8');arvore=ast.parse(s)
nomes={'gravar','ler','json_gravar','arredondar_margem','carregar','preparar','estatisticas_regressao','resolver_restrito','resumo_fluxos','restrito','predicoes'}
cab='''"""Leitura e regressão restrita para a nova execução T16; nenhuma saída antiga é lida."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize
'''
constantes=['RAIZ','SAIDA','SEMENTE','LINHAS','COLUNAS','MAPA','CAPITAIS','ENTRADAS','AVISO']
partes=[cab]
for n in arvore.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in constantes for t in n.targets):partes.append(ast.get_source_segment(s,n))
    if isinstance(n,ast.FunctionDef) and n.name in nomes:partes.append(ast.get_source_segment(s,n))
novo='\n\n'.join(partes)+'\n'
ast.parse(novo)
Path(__file__).with_name('t16_core.py').write_text(novo,encoding='utf-8')
print('Core de contas extraído; nenhum amostrador ou resultado antigo importado.')
