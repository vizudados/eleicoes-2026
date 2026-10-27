# Tela 19 · Os outros: o que as urnas permitem estimar

Análise reiniciada em 27/10/2026 para Alisson / Vizu Dados. As saídas antigas foram apagadas. Nenhuma matriz de uma amostragem reprovada entra nesta entrega. Não houve alteração no Power BI, commit, push ou geração de imagem.

## Leitura curta para o “i”

O voto é secreto. Sabemos quantos votos cada opção recebeu em cada município, mas não em quem a mesma pessoa votou nos dois turnos. Dois métodos estimam perfis médios de transferência a partir dessas contagens. Ambos incluem quem não votou e quem votou branco ou nulo, e respeitam quatro destinos que somam 100% de cada origem.

Os intervalos mostram incerteza dentro das hipóteses de cada método. A comparação entre métodos, regiões e recortes mostra o quanto o resultado muda com essas hipóteses. A estimativa é agregada: não identifica pessoas nem prova uma transferência individual. Um aumento líquido de participação pode combinar pessoas que voltaram a votar e pessoas que deixaram de votar.

## Universo e conferência

São 5.571 unidades eleitorais brasileiras pareadas, incluindo Brasília. Presidência e 1º turno são filtrados nos dois brutos do TSE. As chaves de UF, município, zona, candidato e voto em trânsito são verificadas antes de agregar. Os votos de cada candidato fecham com `candidato_ano.csv`, incluindo exterior; os municípios fecham com `municipio_ano.csv`, sem exterior. Aptos = comparecimento + abstenção e comparecimento = válidos + brancos + nulos precisam fechar nos dois turnos. A junção com o 2º turno é única e completa.

O exterior fica fora dos dois lados. Representa cerca de 0,58% dos aptos e 0,27%/0,30% do comparecimento no 1º/2º turno. Foram excluídos 29.595 votos dos outros candidatos no 1º turno, 0,32% do total desse grupo incluindo exterior. `exterior.csv` conserva as contagens e proporções exatas. A análise usa os arquivos locais fornecidos; seus hashes ficam em `manifesto_entradas.json`.

Os aptos mudam em 3.725 unidades: saldo de −149 e soma de diferenças absolutas de 18.863. Isso não mede quantas pessoas mudaram de cadastro: entradas e saídas podem se compensar. A base principal é o eleitorado apto do 1º turno. As proporções do 2º são multiplicadas por essa base municipal e arredondadas por maiores restos, preservando a soma inteira. O ajuste nacional é −11 para Lula, +104 para Flávio, +68 para branco/nulo e −12 para abstenção. `harmonizacao.csv` registra os valores originais e harmonizados. A sensibilidade com os aptos do 2º turno testa o efeito dessa escolha.

## Método 1: regressão com restrições

Para cada região, são ajustados simultaneamente os quatro destinos como combinações das proporções de todas as origens. A função minimiza a soma dos erros quadráticos municipais, ponderada pelos aptos. Não há intercepto separado. Cada coeficiente fica entre 0 e 1 e cada linha soma 1. O alvo é uma taxa média por origem dentro da região.

O problema quadrático convexo é resolvido por OSQP, com checagem dos resíduos primal e dual e alternativa SLSQP em caso de falha. Uma matriz conhecida e as soluções no banco real foram conferidas contra SLSQP; `validacao_qp.csv` conserva o confronto. Não há ajuste manual de taxas para obter uma narrativa.

São 500 reamostragens de UFs, com reposição dentro de cada região. Cada repetição reajusta as matrizes; a agregação nacional usa os totais de origem do universo original, e não os totais alterados pela repetição das UFs. Os intervalos são percentis 2,5% e 97,5% do bootstrap. A média bootstrap é o centro publicado. Linhas muito assimétricas e estimativas na fronteira podem ter média fora dos percentis centrais; não se troca isso por um erro normal truncado.

Em poucas repetições do Centro-Oeste, todas as UFs sorteadas podem ser o Distrito Federal, que tem uma única unidade eleitoral. O desenho perde posto nesse caso. O problema restrito continua a ser resolvido, mas a solução deixa de ser única; o início pelo ajuste completo define a convenção numérica. A quantidade dessas repetições é publicada nos arquivos `_bootstrap.json`. Elas não foram descartadas silenciosamente. O Sul tem apenas três UFs e o Centro-Oeste quatro; essa limitação também afeta a precisão do bootstrap.

A eleição é um censo. Esse bootstrap mede sensibilidade territorial sob a hipótese de UFs reamostráveis; não é erro amostral da contagem das urnas e não cobre automaticamente o viés ecológico.

## Método 2: Bayes DM regional com amostragem direta

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

### O que a matriz representa

Em cada amostra, o fluxo esperado de uma origem para um destino é `soma_i votos_ir × beta_u(i),r,c`. Divide-se pela soma da própria origem para obter o percentual nacional. Regiões usam a mesma conta no respectivo recorte. Não se faz média simples de porcentagens municipais.

As matrizes são perfis médios esperados sob o modelo, não tabelas individuais reconstruídas. A Dirichlet da dispersão atua sobre a composição municipal dos destinos, não sobre cada célula individual de transição. As colunas dos fluxos esperados podem apresentar resíduos frente à urna; eles são publicados, sem calibração posterior para escondê-los. Uma boa reprodução dos totais não prova as trajetórias das pessoas.

As médias de cada linha somam 100% antes do arredondamento. Os limites marginais de quatro intervalos não precisam somar 100%. Os intervalos bayesianos são os quantis 2,5%/97,5% das amostras aprovadas, condicionados ao modelo e às priors.

### Amostragem e regra para usar

O modelo aprovado usa slice hit-and-run diretamente nas probabilidades do simplex, com direções de covariância fixa calculadas no modo, e Metropolis conjunto para log da precisão e logit do expoente. As regiões fatorizam e são executadas em paralelo. São quatro cadeias por região, sementes distintas, 1.000 iterações descartadas e 4.000 retidas por cadeia; cada iteração atualiza seis direções. Não há transformação logística dos coeficientes de transição nem Hamiltonianos.

A densidade usada é a DM exata, multiplicada pelas priors próprias e pelos jacobianos dos dois parâmetros de dispersão. As direções são independentes do estado corrente. A restrição da linha do slice é o intervalo completo que mantém todas as probabilidades não negativas e a linha somando um. A densidade condicional dos coeficientes é log-côncava. Um teste contra a posterior Dirichlet conjugada no limite multinomial recuperou média e variância; diferenças finitas validaram o gradiente utilizado apenas na inicialização.

O critério é R-hat por ranks/folding <1,01 e ESS bulk e tail >400 em todos os componentes monitorados, incluindo fluxos nacionais e regionais. Houve zero falhas numéricas. Divergência Hamiltoniana não se aplica a slice/Metropolis; isso é declarado no diagnóstico, em vez de equiparar rejeições de Metropolis a divergências. Os logs registram progresso a cada 100 iterações e têm watchdog de dez minutos e prazo absoluto.

## Sensibilidade e checagem preditiva

O método restrito é refeito sem as 27 capitais, com população conhecida de até 50 mil habitantes, por região, com os sete demais candidatos separados, sem a origem não votou e na base alternativa de aptos. Uma unidade sem população fica fora do recorte de 50 mil; não se confunde população com eleitorado. O agrupamento dos três candidatos também é ajustado separadamente, além de somar seus fluxos na matriz de oito origens.

Retirar “não votou” muda a população: as origens passam a representar apenas quem votou no 1º turno e o 2º é redimensionado para essa base. É um estresse deliberado da especificação e não mede os mesmos fluxos. Não serve para atribuir o retorno de abstencionistas. Fica sinalizado como não comparável e fora da seleção de achados comuns.

As sensibilidades bayesianas entram somente se convergirem, com diagnóstico próprio. A comparação inclui a versão sem efeito de UF e os recortes que efetivamente terminarem. Não se declara que um teste bayesiano foi concluído se ele não tiver matriz e diagnóstico aprovados. A composição de um grupo agregado pode variar entre municípios; agrupar candidatos é uma hipótese adicional e sua influência precisa aparecer na leitura.

`predicoes_*` contém observado harmonizado, média prevista, resíduo em votos e pontos dos aptos, e intervalos preditivos. O preditivo sorteia nova composição Dirichlet municipal e nova contagem multinomial a partir de cada amostra do modelo. `checagem_preditiva_*` informa MAE, RMSE, erro ponderado pelos aptos, percentil 95 do erro, resíduo no total nacional e cobertura do intervalo preditivo de 95%. A cobertura é um diagnóstico interno, não acompanhamento individual nem validação externa de transferências.

Os métodos usam a mesma fonte e compartilham parte da hipótese de mistura; são diferentes algoritmos, estruturas de erro e tratamento da heterogeneidade. Concordância entre eles aumenta a estabilidade do resultado dentro desses testes, mas não constitui duas observações independentes da trajetória das pessoas. Sobreposição de intervalos é descritiva. O envelope entre especificações não é um novo intervalo probabilístico de 95%.

## Pesquisas: denominadores e definições

Usa-se a última data de cada instituto depois de 04/10 e antes de 25/10, selecionada antes de escolher os segmentos. Uma ausência na última rodada não é substituída por rodada antiga. Os percentuais são mantidos na base total do segmento, sem renormalizar entre Lula e Flávio. Não sabe e ausências não são distribuídos aos candidatos.

A Quaest rotulada como “não votou” no arquivo reúne **não votou ou votou branco/nulo**. Ela é confrontada com a soma dessas duas origens nas urnas. O grupo puro não votou é comparado separadamente. “Não sabe/não lembra” o voto anterior não é não votou. A Atlas inclui não sabe no residual branco/nulo; portanto os resíduos publicados pelas pesquisas não têm uma definição terminal comum. São preservados, mas não usados como se fossem uma medida idêntica de branco/nulo/abstenção da urna.

Quando só há Bayes para os três candidatos reunidos, o confronto individual usa explicitamente o método restrito. O grupo de três pode ser padronizado, por instituto, ponderando as três intenções condicionais pelos votos reais do 1º turno sem exterior; isso não é uma medição direta de um segmento agregado e não usa tamanhos de amostra ausentes. Agregados de terceira via com escopo diferente não são promovidos ao grupo dos três.

Intenção hipotética e recall em uma entrevista não são trajetórias de uma população acompanhada entre turnos. No PoderData, o arquivo anota que não votou representa 10% da amostra, enquanto a abstenção observada é maior. Não há informação suficiente para produzir um IC amostral conjunto de todas as pesquisas. Compatibilidade com um intervalo do modelo não é um teste de “acerto da pesquisa”.

## Limites e comparecimento

A falácia ecológica continua possível: pessoas que vivem onde uma candidatura foi forte podem ter comportamento diferente dos eleitores dessa candidatura dentro do município. Mudanças de cadastro, deslocamentos entre municípios e características omitidas também permanecem. Intervalos estreitos podem refletir hipóteses fortes; não eliminam esse problema.

Sem hipótese comportamental, cada célula municipal obedece a `max(0, origem + destino - N) ≤ fluxo ≤ min(origem, destino)`. Os limites são somados por município. Não são IC95 e os extremos de células diferentes não precisam ser realizáveis juntos. Para os 9.287.152 votos dos outros, cada finalista admite individualmente de zero ao total desse grupo nos limites municipais. Essa amplitude mostra quanto vem das hipóteses.

Sem exterior, compareceram **2.920.562** pessoas a mais. Incluindo exterior, **2.960.239**; a diferença de 39.677 fica fora da estimativa. Lula ganhou **10.333.927** votos e Flávio **3.693.941**; branco/nulo caiu **1.820.154**. Os ganhos dos finalistas fecham com votos dos eliminados, aumento de comparecimento e redução de inválidos. Essa igualdade não atribui origem individual.

Quem não votou no 1º e votou no 2º é um fluxo bruto estimado; quem votou no 1º e não no 2º é outro. Sua diferença é o saldo modelado, que precisa ser confrontado com o saldo observado e com os resíduos do modelo. Não se chama o saldo líquido de número de retornantes.

## Arquivos e reprodução

Todos os CSV ficam em `dados/saida/2turno/inferencia_t16/`, em UTF-8 BOM, separados por `;`, com vírgula decimal. `dicionario_csv.csv` explica os campos. `manifesto_entradas.json` e `manifesto.json` registram fontes, sementes, versões e hashes. NPZ conserva amostras localmente e está fora do versionamento por `.gitignore` da própria saída.

| Arquivo | Conteúdo |
|---|---|
| `matriz_nacional.csv`, `matriz_regiao.csv`, `matriz_votos.csv` | Principal bayesiano aprovado, com médias e intervalos. |
| `matriz_restrito_oito.csv` | Oito origens no método restrito, incluindo estimativas individuais dos três candidatos. |
| `comparacao_metodos.csv`, `sensibilidade.csv` | Bases compatíveis, recortes e versões aprovadas. |
| `achados_tela.csv`, `afirmacoes_testadas.csv` | Frases e verificação por método, recorte e região. |
| `outros_e_comparecimento.csv` | Destinos dos outros, retornantes, saídas e saldo modelado, com intervalos. |
| `confronto_pesquisas.csv`, `pesquisas_ultimas.csv`, `residuos_pesquisas.csv` | Linhas utilizadas, bases corretas e limites do confronto. |
| `diagnostico_*`, `*.log`, `decisao_uso.json` | R-hat, ESS, divergências, configuração e progresso real. |
| `predicoes_*`, `checagem_preditiva_*` | Erro por município e resumo preditivo. |
| `auditoria_entradas.csv`, `exterior.csv`, `harmonizacao.csv`, `contabilidade.csv` | Conferências e escopo. |

Scripts efetivos: `inferencia_t16.py` é a entrada das contas; `inferencia_t16_v2.py` e `t16_core.py` contêm a regressão e leitura; `t16_bayes_simplex.py` executa o Bayes aprovado. Os amostradores experimentais anteriores não são chamados. Não há resultado antigo lido como entrada.

```powershell
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa preparar
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa restrito --grupos seis --bootstrap 500
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/executar_restritos_t16_v2.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/t16_bayes_simplex.py --cenario principal --burn 1000 --draws 4000 --prior 2 --deadline <prazo_em_segundos_UTC>
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/testar_reinicio_t16.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/testar_slice_t16.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/finalizar_t16_v2.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/fechar_reinicio_t16.py
```

Os parâmetros efetivos de cada execução e a seleção da principal ficam nos diagnósticos. A instalação no venv usa `requirements-inferencia-t16.txt`; nada é instalado globalmente. O reinício limpou somente arquivos regulares diretamente na pasta de saída autorizada, com validação do caminho absoluto.

## Proposta para o “Pós” da tela 19

O protagonista pode ser um fluxo agregado dos outros candidatos para os quatro destinos, com espessura pela média de votos e intervalos legíveis na seleção. O título deve ser “Destinos estimados a partir das urnas”. Lula e Flávio usam a mesma escala, precisão e acesso às ressalvas. Branco/nulo e abstenção ficam separados.

No apoio, mostrar as duas estimativas e intervalos para o grupo selecionado; uma faixa por região; e a conta do comparecimento, separando saldo observado de entradas e saídas estimadas. Se só o grupo de três convergir, ele permanece unido no fluxo bayesiano. As candidaturas individuais podem ser exploradas no método restrito, com a ressalva de ausência de confirmação bayesiana individual. Não se inventa uma divisão do grupo.

Se um destino dos eliminados mudar muito entre modelos ou recortes, a tela deve destacar essa faixa de incerteza e a dependência de hipóteses. Apoios declarados por candidatos ou governadores não explicam causalmente os fluxos. A identificação individual não é possível, mesmo com convergência numérica.

## Referências

- Neal, [Slice Sampling](https://arxiv.org/abs/physics/0009028).

- [NumPyro: Dirichlet–multinomial e demais distribuições](https://num.pyro.ai/en/stable/distributions.html#dirichletmultinomial).
- [NumPyro: MCMC e NUTS](https://num.pyro.ai/en/stable/mcmc.html).
- Vehtari et al. (2021), [R-hat por ranks, folding e ESS](https://arxiv.org/abs/1903.08008), DOI 10.1214/20-BA1221.
- [OSQP: programação quadrática e atualização das matrizes](https://osqp.org/docs/examples/update-matrices.html).
- Rosen, Jiang, King e Tanner (2001), [Bayesian and frequentist inference for ecological inference: the R×C case](https://gking.harvard.edu/files/em.pdf), DOI 10.1111/1467-9574.00162. Referência do problema e de outra hierarquia R×C, não o desenho municipal implementado aqui.

## Decisão sobre o uso no painel

**Convergência numérica aprovada; reconstrução agregada do comparecimento insuficiente.** O Bayes superestima a abstenção nacional harmonizada em 686.818 e subestima Lula em 608.125. A cobertura preditiva municipal é 96,6% para Lula, 97,7% para Flávio, 97,5% para branco/nulo e 88,0% para abstenção. O saldo modelado de comparecimento é 2,234 milhões [2,171–2,298], abaixo dos 2,921 milhões observados. Esses erros não foram calibrados para desaparecer.

Portanto, a matriz abaixo é **condicional e exploratória**, não uma resposta factual sobre as trajetórias. Não recomendo um Sankey de espessuras pontuais apresentado como destino de fato. Para o Pós, recomendo como protagonista a contabilidade observada e três conclusões qualitativas comuns aos métodos; os fluxos estimados entram em apoio, com os dois métodos e intervalos lado a lado.

As sensibilidades do método restrito foram concluídas. **Os recortes bayesianos sem capitais e até 50 mil não foram aprovados/concluídos dentro do prazo e não entram nos achados.** A resistência das três frases refere-se aos dois métodos na base completa, às regiões e aos recortes restritos executados; não equivale a validação das sensibilidades bayesianas.

## Resultados desta execução

<!-- RESULTADOS_T16 -->

Execução principal: `bayes_slice_principal_seis`. Convergência aprovada: R-hat máximo **1,008533**, ESS bulk mínimo **1.032**, ESS tail mínimo **1.131**, **0 divergências**.

Médias e intervalos condicionais de 95%, em % da origem. Não são trajetórias observadas.

| Origem | Lula | Flávio | Branco/nulo | Não votou |
|---|---:|---:|---:|---:|
| Lula | 98,9 [98,6–99,1] | 0,1 [0,0–0,1] | 0,3 [0,2–0,4] | 0,8 [0,5–1,0] |
| Flávio | 0,2 [0,1–0,3] | 98,9 [98,7–99,1] | 0,5 [0,4–0,6] | 0,4 [0,3–0,6] |
| Cury + Renan + Caiado | 46,8 [44,3–49,3] | 37,0 [34,6–39,3] | 12,4 [11,2–13,5] | 3,8 [2,6–5,1] |
| Demais candidatos | 48,4 [35,0–61,5] | 32,1 [19,1–45,6] | 9,6 [6,2–13,4] | 9,9 [4,7–16,9] |
| Branco ou nulo | 52,2 [49,0–55,2] | 5,9 [3,3–8,9] | 40,5 [39,0–42,0] | 1,4 [0,7–2,2] |
| Não votou | 8,4 [7,8–8,9] | 1,2 [0,8–1,6] | 0,6 [0,4–0,8] | 89,8 [89,4–90,3] |

### Achados testados

- Aprovado nos testes executados: A maioria de quem votou em Lula permaneceu com Lula: 98,9% (95%: 98,6%–99,1%).

- Aprovado nos testes executados: A maioria de quem votou em Flávio permaneceu com Flávio: 98,9% (95%: 98,7%–99,1%).

- Aprovado nos testes executados: A maioria de quem não votou no 1º turno continuou sem votar: 89,8% (95%: 89,4%–90,3%).

- Não aprovado como achado robusto: A maioria dos votos dos candidatos eliminados permaneceu válida no 2º turno: 83,6% (95%: 82,0%–85,2%).

6 de 24 células comparáveis têm intervalos marginais sem sobreposição entre os métodos. Isso é diagnóstico descritivo, não teste de trajetória individual.

As candidaturas individuais só recebem estimativa bayesiana se a execução de oito origens passar. Caso contrário, sua divisão permanece restrita ao primeiro método, sem confirmação bayesiana individual.

### Votos dos outros e comparecimento

| Medida | Média, votos | Intervalo 95%, votos |
|---|---:|---:|
| Outros candidatos → Lula | 4.357.124 | 4.141.931–4.570.868 |
| Outros candidatos → Flávio | 3.408.354 | 3.211.528–3.604.636 |
| Outros candidatos → Branco ou nulo | 1.131.675 | 1.030.794–1.229.608 |
| Outros candidatos → Não votou | 389.999 | 284.288–508.331 |
| Não votou 1º e votou 2º | 3.342.101 | 3.199.130–3.494.729 |
| Votou 1º e não votou 2º | 1.108.197 | 959.493–1.266.657 |
| Saldo de comparecimento modelado | 2.233.905 | 2.170.514–2.298.328 |

O saldo observado é 2.920.562 votantes a mais sem exterior e 2.960.239 com exterior. O saldo líquido não é o fluxo bruto de retornantes.

<!-- FIM_RESULTADOS_T16 -->
