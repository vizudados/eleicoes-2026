"""Insere resultados auditáveis no documento permitido, após finalizar CSVs."""
from pathlib import Path
import json
import importlib.util
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dados/saida/2turno/inferencia_t16'
def ler(nome):return pd.read_csv(OUT/nome,sep=';',decimal=',',encoding='utf-8-sig')
def br(v,casas=1):return 'não finito' if v is None or pd.isna(v) else f'{v:,.{casas}f}'.replace(',','X').replace('.',',').replace('X','.')
def cel(d):
    r=d.iloc[0]
    return f'{br(r.media_pct)} [{br(r.inferior_95_pct)}–{br(r.superior_95_pct)}]'

mat=ler('matriz_nacional.csv')
diag=json.loads((OUT/'execucao_bayes_principal.json').read_text(encoding='utf-8'))
cmp=ler('concordancia_metodos.csv')
sens=ler('sensibilidade.csv')
outros=ler('outros_e_comparecimento.csv')
env=ler('envelope_especificacoes.csv')
texto=[]
aprovado=diag['convergencia_aprovada']
texto.append('**Convergência numérica do modelo completo: '+('APROVADA' if aprovado else 'REPROVADA')+'.** ')
texto.append(f'Quatro cadeias; {diag["tune"]} iterações de aquecimento e {diag["draws_por_chain"]} amostras retidas por cadeia. R-hat máximo {br(diag["rhat_max"],4)}; ESS bulk mínimo {br(diag["ess_bulk_min"],1)}; ESS tail mínimo {br(diag["ess_tail_min"],1)}; {diag["divergencias"]} divergências; {br(100*diag["fracao_limite_arvore"],2)}% no limite da árvore. Tempo sincronizado: {br(diag["segundos"]/60,1)} minutos.')
texto.append(('A matriz abaixo contém médias posteriores e intervalos marginais condicionais de 95%, em % da origem. Aprovação numérica não significa identificação individual.' if aprovado else 'A matriz abaixo contém médias e quantis 2,5%–97,5% das cadeias reprovadas, em % da origem. **Esses quantis não são intervalos de credibilidade validados. Não usar como conclusão substantiva.**'))
texto.append('| Origem no 1º turno | Lula | Flávio | Branco/nulo | Não votou |\n|---|---:|---:|---:|---:|')
for nome in mat.origem.drop_duplicates():
    row=[cel(mat[mat.origem.eq(nome)&mat.destino.eq(c)]) for c in ['Lula','Flávio','Branco ou nulo','Não votou']]
    texto.append('| '+nome+' | '+' | '.join(row)+' |')
texto.append('As médias de cada linha somam 100% antes do arredondamento. Os extremos dos intervalos não somam 100%.')
texto.append(f'No confronto entre métodos, {int((~cmp.intervalos_sobrepostos).sum())} das {len(cmp)} células nacionais têm intervalos marginais sem sobreposição. Sobreposição é um diagnóstico descritivo, não uma prova de concordância ou de ausência de viés.')

# Testa afirmações com probabilidade de maioria, preservando a correlação entre
# células em cada amostra; exige todos os recortes comparáveis e as regiões.
estat=[]
for arquivo in sorted(OUT.glob('amostras_*.npz')):
    if arquivo.name=='amostras_restrito.npz':
        if (OUT/'amostras_restrito_principal.npz').exists():continue
        metodo,cenario='restrito','principal'
    elif arquivo.name.startswith('amostras_restrito_'):metodo,cenario='restrito',arquivo.stem.removeprefix('amostras_restrito_')
    elif arquivo.name.startswith('amostras_bayes_aprox_'):metodo,cenario='bayes_aprox',arquivo.stem.removeprefix('amostras_bayes_aprox_')
    elif arquivo.name.startswith('amostras_bayes_prior_log_normal_'):metodo,cenario='bayes_prior_log_normal',arquivo.stem.removeprefix('amostras_bayes_prior_log_normal_')
    elif arquivo.name.startswith('amostras_bayes_'):metodo,cenario='bayes',arquivo.stem.removeprefix('amostras_bayes_')
    else:continue
    if cenario=='sem_nao_votou':continue
    f=np.load(arquivo);nomes=f['nomes'].tolist()
    areas=[('Brasil',f['fluxos'])]
    if cenario=='principal':areas += [(str(g),f['regioes'][:,i]) for i,g in enumerate(f['areas'])]
    for area,a in areas:
        series={}
        for nome,j,chave in [('Lula',0,'retencao_lula'),('Flávio',1,'retencao_flavio'),('Não votou',3,'persistencia_nao_votou')]:
            if nome in nomes:
                flux=a[:,nomes.index(nome)]
                series[chave]=100*flux[:,j]/flux.sum(axis=1)
        ix=[i for i,nome in enumerate(nomes) if nome not in ['Lula','Flávio','Branco ou nulo','Não votou']]
        flux=a[:,ix].sum(axis=1)
        series['outros_votos_validos']=100*flux[:,:2].sum(axis=1)/flux.sum(axis=1)
        for chave,v in series.items():
            lo,hi=np.quantile(v,[.025,.975])
            estat.append({'metodo':metodo,'cenario':cenario,'area':area,'afirmacao':chave,'media_pct':v.mean(),'inferior_95_pct':lo,'superior_95_pct':hi})
estat=pd.DataFrame(estat)
estat.to_csv(OUT/'afirmacoes_testadas.csv',sep=';',decimal=',',encoding='utf-8-sig',index=False,float_format='%.10g')
rotulos={
    'retencao_lula':'A maioria de quem votou em Lula no 1º turno permaneceu com Lula',
    'retencao_flavio':'A maioria de quem votou em Flávio no 1º turno permaneceu com Flávio',
    'persistencia_nao_votou':'A maioria de quem não votou no 1º turno continuou sem votar',
    'outros_votos_validos':'A maioria dos votos dos candidatos eliminados permaneceu válida no 2º turno',
}
achados=[]
texto.append('### Afirmações testadas para a tela')
for chave,rotulo in rotulos.items():
    q=estat[estat.afirmacao.eq(chave)&estat.metodo.isin(['bayes','restrito'])]
    principal=q[q.metodo.eq('bayes')&q.cenario.eq('principal')&q.area.eq('Brasil')].iloc[0]
    minimo=float(q.inferior_95_pct.min())
    robusto=bool(aprovado and minimo>50)
    frase=f'{rotulo}: {br(principal.media_pct)}% (intervalo de 95%: {br(principal.inferior_95_pct)}%–{br(principal.superior_95_pct)}%).'
    achados.append({'afirmacao':chave,'frase':frase,'resiste_metodos_recortes_e_regioes':robusto,'menor_limite_inferior_entre_testes_pct':minimo,'convergencia_aprovada':aprovado,
                    'escopo':'Dois métodos, todos os recortes comparáveis e regiões; sem_nao_votou excluído por mudar a população. Aproximação adicional listada separadamente.'})
    texto.append('- '+('**Resiste aos testes especificados:** ' if robusto else '**Não aprovado como achado para a tela:** ')+frase+f' Menor limite inferior entre os testes: {br(minimo)}%.')
achados=pd.DataFrame(achados)
achados.to_csv(OUT/'achados_tela.csv',sep=';',decimal=',',encoding='utf-8-sig',index=False)
texto.append('A quantidade de afirmações aprovadas pode ser menor que três. Não se completa uma lista editorial com números que falharam. A estabilidade refere-se aos testes executados; não elimina a hipótese comportamental nem transforma a inferência em observação individual.')

texto.append('### Votos dos outros e comparecimento')
texto.append('| Medida do modelo completo | Média em votos | Intervalo de 95% em votos |\n|---|---:|---:|')
for _,r in outros[outros.metodo.eq('bayes')].iterrows():
    nome=r.destino if r.origem=='Outros candidatos (todos)' else r.origem
    texto.append(f'| {nome} | {br(r.media_votos,0)} | {br(r.inferior_95_votos,0)}–{br(r.superior_95_votos,0)} |')
texto.append('O saldo observado de comparecimento é **2.920.562** sem exterior e **2.960.239** incluindo exterior. Os 39.677 adicionais no exterior ficam fora do modelo. A base harmonizada tem um saldo ligeiramente diferente; os resíduos são publicados em vez de forçar os dois resultados a coincidir.')

texto.append('### Erro por município')
texto.append('| Previsão / destino | MAE ponderado, pp dos aptos | RMSE municipal, votos | Cobertura preditiva 95%, % |\n|---|---:|---:|---:|')
for nome in ['bayes','bayes_ajustado','restrito','restrito_fora_uf']:
    p=OUT/f'checagem_preditiva_{nome}_principal.csv'
    if not p.exists():continue
    for _,r in ler(p.name).iterrows():
        cobertura='—' if pd.isna(r.cobertura_preditiva_95_pct) else br(r.cobertura_preditiva_95_pct)
        texto.append(f'| {nome} / {r.destino} | {br(r.mae_ponderado_pp_aptos,3)} | {br(r.rmse_municipal_votos,0)} | {cobertura} |')
texto.append('O erro ajustado dos efeitos locais usa as próprias urnas como informação. O preditivo bayesiano sorteia uma nova Dirichlet por município. O teste restrito fora da UF retira a UF inteira do treino. São avaliações diferentes e estão nomeadas separadamente.')

texto.append('### Pesquisas na mesma base total')
texto.append('| Origem | Destino | Média das pesquisas, % | Modelo completo, % [95%] |\n|---|---|---:|---:|')
for _,r in ler('confronto_pesquisas.csv').iterrows():
    texto.append(f'| {r.origem} | {r.destino_comparado} | {br(r.pesquisa_media_pct)} | {br(r.urna_media_pct)} [{br(r.urna_inferior_95_pct)}–{br(r.urna_superior_95_pct)}] |')
texto.append('As médias das pesquisas são descritivas, sem um IC conjunto disponível. Ausências e “não sabe” não são redistribuídos. Concordância aqui significa apenas compatibilidade descritiva sob um modelo aprovado; não é validação de trajetórias individuais.')

texto.append('### Números que exigem cautela')
texto.append('| Origem / destino | Menor–maior média entre especificações nacionais, % | Envelope dos intervalos 95%, % |\n|---|---:|---:|')
for _,r in env[env.origem.isin(['Augusto Cury','Renan Santos','Ronaldo Caiado','Demais candidatos','Não votou'])&env.destino.isin(['Lula','Flávio'])].iterrows():
    texto.append(f'| {r.origem} / {r.destino} | {br(r.menor_media_pct)}–{br(r.maior_media_pct)} | {br(r.menor_limite_95_pct)}–{br(r.maior_limite_95_pct)} |')
texto.append('O envelope não tem cobertura probabilística de 95%. Exclui o teste que retira “não votou”, pois ele altera a população. Os fluxos específicos para candidatos menores, o saldo bruto de mobilização e zeros na fronteira não devem ganhar uma precisão editorial que os diagnósticos não sustentam.')

decisao={'convergencia_completo_aprovada':aprovado,'afirmacoes_maioria_aprovadas':int(achados.resiste_metodos_recortes_e_regioes.sum()),
          'celulas_sem_sobreposicao_intervalos_metodos':int((~cmp.intervalos_sobrepostos).sum()),
          'integracao_automatica_autorizada':False,'motivo':'Entrega de análise para a sessão principal revisar; convergência e estabilidade devem acompanhar qualquer uso. Não houve integração ao painel.'}
(OUT/'decisao_uso.json').write_text(json.dumps(decisao,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=ROOT/'docs/metodo-inferencia-t16.md'
conteudo=doc.read_text(encoding='utf-8')
antes,resto=conteudo.split('<!-- RESULTADOS_T16 -->',1)
_,depois=resto.split('<!-- FIM_RESULTADOS_T16 -->',1)
corpo=''
anterior=''
for trecho in texto:
    separador='\n' if trecho.startswith('|') and anterior.startswith('|') else '\n\n'
    corpo+=separador+trecho
    anterior=trecho
doc.write_text(antes+'<!-- RESULTADOS_T16 -->'+corpo+'\n\n<!-- FIM_RESULTADOS_T16 -->'+depois,encoding='utf-8')
spec=importlib.util.spec_from_file_location('inferencia_t16',ROOT/'pipeline/inferencia_t16.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.catalogar_csv()
print(json.dumps(decisao,ensure_ascii=False))
print(mat[['origem','destino','media_pct','inferior_95_pct','superior_95_pct']].to_string(index=False))
