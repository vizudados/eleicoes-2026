"""Inspeção somente de leitura das entradas da inferência T16."""
from pathlib import Path
import importlib.util
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'dados/pbi'
v = pd.read_csv(ROOT / 'dados/bruto/tse/presidente_2026_BR.csv', sep=';', encoding='latin1')
d = pd.read_csv(ROOT / 'dados/bruto/tse/detalhe_2026_BR.csv', sep=';', encoding='latin1')
v = v.query('NR_TURNO == 1 and CD_CARGO == 1')
d = d.query('NR_TURNO == 1 and CD_CARGO == 1')
print('CANDIDATOS', v.groupby(['NR_CANDIDATO', 'NM_URNA_CANDIDATO']).QT_VOTOS_NOMINAIS_VALIDOS.sum().to_string())
print('DETALHE', d.groupby(d.SG_UF.eq('ZZ'))[['QT_APTOS','QT_COMPARECIMENTO','QT_ABSTENCOES','QT_VOTOS_BRANCOS','QT_TOTAL_VOTOS_NULOS']].sum().to_string())
a = pd.read_csv(p/'municipio_ano.csv').query('ano == 2026')
b = pd.read_csv(p/'municipio_2turno.csv').query('ano == 2026')
m = pd.read_csv(p/'municipio.csv')
print('TOTAIS 1', a.sum(numeric_only=True).to_dict())
print('TOTAIS 2', b.sum(numeric_only=True).to_dict())
z = a.merge(b, on='cd_ibge', suffixes=('_1','_2'), how='outer', indicator=True)
print('MERGE', z._merge.value_counts().to_dict())
print('APTOS', (z.aptos_2-z.aptos_1).describe().to_dict(), 'DIVERGENTES', (z.aptos_2!=z.aptos_1).sum())
print('FECHAMENTO1', (a.aptos-a.comparecimento-a.abstencoes).value_counts().head().to_dict())
print('FECHAMENTO2', (b.aptos-b.comparecimento-b.abstencoes).value_counts().head().to_dict())
print('GEOGRAFIA', m.columns.tolist(), m.regiao.value_counts().to_dict(), m.populacao.describe().to_dict())
t = pd.read_csv(p/'transferencia.csv')
t = t[t.divulgacao.gt('2026-10-04') & t.divulgacao.lt('2026-10-25')]
t = t[t.divulgacao.eq(t.groupby('instituto').divulgacao.transform('max'))]
print('PESQUISAS', t[['instituto','divulgacao','segmento_1turno','n_segmento','lula','flavio','branco_nulo_nao_vota','nao_sabe']].to_string(index=False))
print('PACOTES', {k: bool(importlib.util.find_spec(k)) for k in ['numpy','scipy','pandas','arviz','pymc','numpyro','jax']})
print('EXTERIOR2', pd.read_csv(p/'uf_2turno.csv').query('ano == 2026 and uf == "ZZ"').to_dict('records'))
