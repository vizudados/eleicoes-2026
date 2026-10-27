"""Atualiza a leitura final sem esconder a reprovação preditiva agregada."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dados/saida/2turno/inferencia_t16';doc=ROOT/'docs/metodo-inferencia-t16.md'
s=doc.read_text(encoding='utf-8')
a=s.index('## Método 2:');b=s.index('### O que a matriz representa',a)
s=s[:a]+'''## Método 2: Bayes DM regional com amostragem direta

O desenho aprovado tem seis origens: Lula, Flávio, Cury + Renan + Caiado, demais candidatos, branco/nulo e não votou. As três candidaturas não são repartidas artificialmente. É uma regressão ecológica bayesiana de mistura com dispersão municipal; não é a hierarquia municipal por origem de Rosen.

```text
B_gr ~ Dirichlet(2, 2, 2, 2)
mu_ic = soma_r X_ir × B_g(i),r,c
tau_g ~ LogNormal(log 1200, 1,2)
gamma_g ~ Beta(2, 2)
kappa_i = tau_g(i) × (N_i / mediana(N))^gamma_g(i)
q_i ~ Dirichlet(kappa_i × mu_i)
Y_i ~ Multinomial(N_i, q_i)
```

Integra-se q analiticamente, pela Dirichlet–multinomial. Os parâmetros são regionais; a versão aprovada não tem desvio de UF. A prior Dirichlet(2) é uma regularização simétrica e explícita. Os expoentes de dispersão são regionais. As tentativas NUTS de seis e oito origens, com outras estruturas, não passaram ou não terminaram e não fornecem matrizes nesta entrega.

''' +s[b:]
a=s.index('### Amostragem e regra para usar');b=s.index('## Sensibilidade e checagem preditiva',a)
s=s[:a]+'''### Amostragem e regra para usar

O modelo aprovado usa slice hit-and-run diretamente nas probabilidades do simplex, com direções de covariância fixa calculadas no modo, e Metropolis conjunto para log da precisão e logit do expoente. As regiões fatorizam e são executadas em paralelo. São quatro cadeias por região, sementes distintas, 1.000 iterações descartadas e 4.000 retidas por cadeia; cada iteração atualiza seis direções. Não há transformação logística dos coeficientes de transição nem Hamiltonianos.

A densidade usada é a DM exata, multiplicada pelas priors próprias e pelos jacobianos dos dois parâmetros de dispersão. As direções são independentes do estado corrente. A restrição da linha do slice é o intervalo completo que mantém todas as probabilidades não negativas e a linha somando um. A densidade condicional dos coeficientes é log-côncava. Um teste contra a posterior Dirichlet conjugada no limite multinomial recuperou média e variância; diferenças finitas validaram o gradiente utilizado apenas na inicialização.

O critério é R-hat por ranks/folding <1,01 e ESS bulk e tail >400 em todos os componentes monitorados, incluindo fluxos nacionais e regionais. Houve zero falhas numéricas. Divergência Hamiltoniana não se aplica a slice/Metropolis; isso é declarado no diagnóstico, em vez de equiparar rejeições de Metropolis a divergências. Os logs registram progresso a cada 100 iterações e têm watchdog de dez minutos e prazo absoluto.

''' +s[b:]
s=s.replace('Scripts efetivos: `inferencia_t16.py` é a entrada, `inferencia_t16_v2.py` implementa a nova análise e `t16_core.py` contém leitura e contas.', 'Scripts efetivos: `inferencia_t16.py` é a entrada das contas; `inferencia_t16_v2.py` e `t16_core.py` contêm a regressão e leitura; `t16_bayes_simplex.py` executa o Bayes aprovado.')
start=s.index('```powershell');end=s.index('```',start+3)+3
s=s[:start]+'''```powershell
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa preparar
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa restrito --grupos seis --bootstrap 500
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/executar_restritos_t16_v2.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/t16_bayes_simplex.py --cenario principal --burn 1000 --draws 4000 --prior 2 --deadline <prazo_em_segundos_UTC>
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/testar_reinicio_t16.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/testar_slice_t16.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/finalizar_t16_v2.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/fechar_reinicio_t16.py
```''' +s[end:]
s=s.replace('## Resultados desta execução','''## Decisão sobre o uso no painel

**Convergência numérica aprovada; reconstrução agregada do comparecimento insuficiente.** O Bayes superestima a abstenção nacional harmonizada em 686.818 e subestima Lula em 608.125. A cobertura preditiva municipal é 96,6% para Lula, 97,7% para Flávio, 97,5% para branco/nulo e 88,0% para abstenção. O saldo modelado de comparecimento é 2,234 milhões [2,171–2,298], abaixo dos 2,921 milhões observados. Esses erros não foram calibrados para desaparecer.

Portanto, a matriz abaixo é **condicional e exploratória**, não uma resposta factual sobre as trajetórias. Não recomendo um Sankey de espessuras pontuais apresentado como destino de fato. Para o Pós, recomendo como protagonista a contabilidade observada e três conclusões qualitativas comuns aos métodos; os fluxos estimados entram em apoio, com os dois métodos e intervalos lado a lado.

As sensibilidades do método restrito foram concluídas. **Os recortes bayesianos sem capitais e até 50 mil não foram aprovados/concluídos dentro do prazo e não entram nos achados.** A resistência das três frases refere-se aos dois métodos na base completa, às regiões e aos recortes restritos executados; não equivale a validação das sensibilidades bayesianas.

## Resultados desta execução''')
s=s.replace('## Referências\n','## Referências\n\n- Neal, [Slice Sampling](https://arxiv.org/abs/physics/0009028).\n')
doc.write_text(s,encoding='utf-8')
f=OUT/'decisao_uso.json';o=json.loads(f.read_text(encoding='utf-8'));o.update({'uso_fluxos_como_fato_recomendado':False,'motivo':'Erro agregado de 686.818 na abstenção, cobertura preditiva 88%; saldo de comparecimento fora do intervalo modelado.',
 'sensibilidades_bayesianas_aprovadas':False,'matriz_status':'exploratória e condicional; numericamente convergida'})
f.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Decisão final registrada com limitação preditiva explícita.')
