"""Escreve somente a documentação autorizada para a execução reiniciada."""
from pathlib import Path
doc=Path(__file__).resolve().parents[1]/'docs/metodo-inferencia-t16.md'
doc.write_text('''# Tela 19 · Os outros: o que as urnas permitem estimar

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

## Método 2: regressão ecológica bayesiana Dirichlet–multinomial

Foi escolhido um desenho com poucos parâmetros sistemáticos, em vez de amostrar uma matriz inteira em cada município. O modelo usa todas as unidades municipais. Estima uma matriz regional de perfis médios, desvios comuns por UF e dispersão municipal. É uma regressão ecológica bayesiana de mistura; não é a hierarquia municipal de probabilidades por origem do modelo de Rosen.

Há uma versão com seis origens: Lula, Flávio, Cury + Renan + Caiado, demais candidatos, branco/nulo e não votou. Uma versão com oito origens mantém os três candidatos separados. A versão de oito só é usada se convergir. Um resultado do grupo de três nunca é repartido artificialmente entre os candidatos.

Sejam `X_ir` a proporção da origem `r` no eleitorado municipal do 1º turno; `N_i` a base harmonizada; `g(i)` a região e `u(i)` a UF. O modelo é:

```text
B_gr ~ Dirichlet(1, 1, 1, 1)
z ~ Normal(0, 1); sigma_UF ~ HalfNormal(0,4)
e_uc = sigma_UF × contraste_UF(z), com soma de e dentro da região = 0
e_u,nao_votou = 0  (referência dos log-odds)
beta_urc = softmax_c(log B_g(u),r,c + e_uc)
mu_ic = soma_r X_ir × beta_u(i),r,c
tau_g ~ LogNormal(log 1200, 1,2)
gamma ~ Beta(2, 2)
kappa_i = tau_g(i) × (N_i / mediana(N))^gamma
q_i ~ Dirichlet(kappa_i × mu_i)
Y_i ~ Multinomial(N_i, q_i)
```

`q_i` é integrado analiticamente, resultando na Dirichlet–multinomial. A dispersão evita tratar os milhões de aptos como milhões de observações independentes capazes de identificar os fluxos. O tamanho do município pode alterar a dispersão; o expoente é estimado. Os contrastes de UF são ortonormais e somam zero dentro de cada região, retirando a redundância com a matriz regional. Os desvios de UF mudam as chances dos destinos de forma comum às origens. Esse é um limite estrutural do desenho, não uma descoberta sobre o comportamento de cada candidatura em cada UF.

As priors tratam Lula e Flávio simetricamente. Não impõem fidelidade aos finalistas e não usam as pesquisas de transferência. Ainda são escolhas de regularização. O modelo supõe que, depois da região e dos efeitos de UF, a composição municipal dos destinos varia em torno da mistura média proposta. Se o comportamento se relacionar com características não incluídas, como contexto urbano, renda ou campanha local, os coeficientes podem ter viés.

### O que a matriz representa

Em cada amostra, o fluxo esperado de uma origem para um destino é `soma_i votos_ir × beta_u(i),r,c`. Divide-se pela soma da própria origem para obter o percentual nacional. Regiões usam a mesma conta no respectivo recorte. Não se faz média simples de porcentagens municipais.

As matrizes são perfis médios esperados sob o modelo, não tabelas individuais reconstruídas. A Dirichlet da dispersão atua sobre a composição municipal dos destinos, não sobre cada célula individual de transição. As colunas dos fluxos esperados podem apresentar resíduos frente à urna; eles são publicados, sem calibração posterior para escondê-los. Uma boa reprodução dos totais não prova as trajetórias das pessoas.

As médias de cada linha somam 100% antes do arredondamento. Os limites marginais de quatro intervalos não precisam somar 100%. Os intervalos bayesianos são os quantis 2,5%/97,5% das amostras aprovadas, condicionados ao modelo e às priors.

### Amostragem e regra para usar

NumPyro/JAX em precisão dupla; NUTS com quatro cadeias independentes e semente fixa. A inicialização começa na regressão restrita, com otimização e geometria local apenas para facilitar o amostrador. O critério vem das cadeias, não do sucesso dessa otimização.

Para publicar qualquer matriz bayesiana nesta entrega, exige-se **R-hat < 1,01, ESS bulk > 400, ESS tail > 400 e nenhuma divergência**, em todos os parâmetros monitorados e nas funções derivadas, incluindo perfis por UF e fluxos nacionais/regionais. R-hat usa ranks normalizados e folding; ESS usa cadeias divididas. As tabelas de diagnóstico permitem auditar cada componente. Resultados reprovados ficam somente como diagnóstico e não geram CSV de matriz ou confronto.

Cada amostragem grava progresso real a cada 50 iterações em um arquivo `.log`, com hora UTC e cadeia. Um watchdog interrompe o processo se ficar dez minutos sem progresso. O prazo absoluto da execução também é verificado. Não se confunde um processo vivo ou um texto “compilando” com uma cadeia avançando.

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

Scripts efetivos: `inferencia_t16.py` é a entrada, `inferencia_t16_v2.py` implementa a nova análise e `t16_core.py` contém leitura e contas. Os amostradores experimentais anteriores não são chamados. Não há resultado antigo lido como entrada.

```powershell
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa preparar
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa restrito --grupos seis --bootstrap 500
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/executar_restritos_t16_v2.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa bayes --grupos seis --tune 1000 --draws 1500 --target-accept 0.95
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa bayes --grupos seis --sem-uf --tune 1000 --draws 2000 --target-accept 0.99
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/inferencia_t16.py --etapa bayes --grupos oito --tune 1000 --draws 2000 --target-accept 0.99
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/testar_reinicio_t16.py
& 'pipeline/.venv-ei/Scripts/python.exe' -I -X utf8 pipeline/finalizar_t16_v2.py
```

Os parâmetros efetivos de cada execução e a seleção da principal ficam nos diagnósticos. A instalação no venv usa `requirements-inferencia-t16.txt`; nada é instalado globalmente. O reinício limpou somente arquivos regulares diretamente na pasta de saída autorizada, com validação do caminho absoluto.

## Proposta para o “Pós” da tela 19

O protagonista pode ser um fluxo agregado dos outros candidatos para os quatro destinos, com espessura pela média de votos e intervalos legíveis na seleção. O título deve ser “Destinos estimados a partir das urnas”. Lula e Flávio usam a mesma escala, precisão e acesso às ressalvas. Branco/nulo e abstenção ficam separados.

No apoio, mostrar as duas estimativas e intervalos para o grupo selecionado; uma faixa por região; e a conta do comparecimento, separando saldo observado de entradas e saídas estimadas. Se só o grupo de três convergir, ele permanece unido no fluxo bayesiano. As candidaturas individuais podem ser exploradas no método restrito, com a ressalva de ausência de confirmação bayesiana individual. Não se inventa uma divisão do grupo.

Se um destino dos eliminados mudar muito entre modelos ou recortes, a tela deve destacar essa faixa de incerteza e a dependência de hipóteses. Apoios declarados por candidatos ou governadores não explicam causalmente os fluxos. A identificação individual não é possível, mesmo com convergência numérica.

## Referências

- [NumPyro: Dirichlet–multinomial e demais distribuições](https://num.pyro.ai/en/stable/distributions.html#dirichletmultinomial).
- [NumPyro: MCMC e NUTS](https://num.pyro.ai/en/stable/mcmc.html).
- Vehtari et al. (2021), [R-hat por ranks, folding e ESS](https://arxiv.org/abs/1903.08008), DOI 10.1214/20-BA1221.
- [OSQP: programação quadrática e atualização das matrizes](https://osqp.org/docs/examples/update-matrices.html).
- Rosen, Jiang, King e Tanner (2001), [Bayesian and frequentist inference for ecological inference: the R×C case](https://gking.harvard.edu/files/em.pdf), DOI 10.1111/1467-9574.00162. Referência do problema e de outra hierarquia R×C, não o desenho municipal implementado aqui.

## Resultados desta execução

<!-- RESULTADOS_T16 -->
Em validação. Nenhum número bayesiano deve ser usado antes da aprovação registrada no diagnóstico.
<!-- FIM_RESULTADOS_T16 -->
''',encoding='utf-8')
print('Método reescrito para o desenho executado no reinício.')
