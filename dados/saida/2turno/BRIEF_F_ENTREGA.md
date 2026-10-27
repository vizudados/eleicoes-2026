# Brief F · dados do segundo turno para o filtro Pré/Pós

Entrega para Alisson e para a sessão main. Consulta externa feita em 26/10/2026 (horário de Brasília).

As tarefas 1, 2, 3, 5 e 6 estão concluídas. Para 2026/2, a zona foi obtida diretamente da API oficial EA20, sem esperar o ZIP de seções. Na tarefa 4, o perfil de 2026 publicado contém apenas o primeiro turno.

Nenhum arquivo de dados/pbi ou pbi foi editado. Sem commit, push, branch ou operação no Desktop. Os scripts existentes foram importados apenas para reutilizar funções/constantes, sem executar seus entrypoints.

## 1. Segundo turno por município

| Arquivo novo em dados/saida/2turno | Linhas de dados | Cobertura |
|---|---:|---|
| municipio_2turno_2006_2018.csv | 22.272 | 2006, 2010, 2014 e 2018, sem exterior |
| municipio_2turno_completo.csv | 33.413 | 2006–2026, sem exterior |

Esquema idêntico ao de municipio_2turno.csv: ano, cd_ibge, pt, adv, demais, validos, aptos, comparecimento, abstencoes, brancos, nulos. Inteiros; UTF-8; vírgula; uma chave ano × cd_ibge. PT é o candidato 13; adversário 45 em 2006/2010/2014, 17 em 2018 e 22 em 2022/2026. Demais = zero no segundo turno.

As 11.141 linhas de 2022/2026 foram concatenadas dos bytes originais, sem reserialização. A comparação linha a linha com terminadores de linha passou, além da comparação de todas as células com a reextração dos brutos/API.

SHA-256 do arquivo original preservado: `6dcbedde294ce2bb16fa32f2d64cc493493532905a8ed3dc696e6f4e2c5383e1`.

## 2. Prova dos totais e das abrangências

`brief_f_prova_totais.csv`: 5.171 controles, todos com diferença zero. Contém ano, turno, teste, local, campo, obtido, esperado e diferença. Os controles incluem as 27 UFs e ZZ contra pt_historico_uf, Brasil com exterior contra pt_historico_brasil e Brasil municipal contra o histórico descontado de ZZ. Campos: PT, adversário, válidos, comparecimento e aptos; todos os nove campos também têm somas diretas dos brutos ou totais finais da API.

Totais municipais sem exterior (2010 com o trânsito atribuído à capital de votação):

| Ano | Turno | Municípios | PT | Adversário | Válidos | Maior diferença absoluta nos controles |
|---|---:|---:|---:|---:|---:|---:|
| 2006 | 1 | 5.565 | 46.646.814 | 39.950.856 | 95.957.656 | 0 |
| 2006 | 2 | 5.565 | 58.277.094 | 37.522.266 | 95.799.360 | 0 |
| 2010 | 1 | 5.567 | 47.620.398 | 33.098.350 | 101.505.850 | 0 |
| 2010 | 2 | 5.567 | 55.719.417 | 43.663.475 | 99.382.892 | 0 |
| 2014 | 1 | 5.570 | 43.243.315 | 34.831.498 | 103.891.063 | 0 |
| 2014 | 2 | 5.570 | 54.470.059 | 50.937.034 | 105.407.093 | 0 |
| 2018 | 1 | 5.570 | 31.322.511 | 49.163.320 | 106.857.368 | 0 |
| 2018 | 2 | 5.570 | 46.987.176 | 57.666.176 | 104.653.352 | 0 |
| 2022 | 1 | 5.570 | 57.120.571 | 50.949.797 | 117.935.194 | 0 |
| 2022 | 2 | 5.570 | 60.193.094 | 58.061.090 | 118.254.184 | 0 |
| 2026 | 1 | 5.571 | 53.722.151 | 55.960.603 | 118.969.906 | 0 |
| 2026 | 2 | 5.571 | 64.056.078 | 59.654.544 | 123.710.622 | 0 |

### Tratamento de 2010 e diferença já existente no primeiro turno

O bruto separa voto em trânsito como SG_UF = VT e informa a capital no nome do município. A regra de exportar_pt_historico.py atribui esse voto à UF de votação. Neste trabalho, ele também foi atribuído ao código TSE/IBGE da capital, antes da soma municipal. Não há redistribuição proporcional nem alteração de voto. O de-para é o cadastro do painel, com a lista de capitais já usada em extrair_secoes.py.

O municipio_ano.csv atual exclui VT/2010. Por isso, a soma daquele arquivo, literalmente, NÃO fecha com a série histórica de 2010 apenas retirando ZZ. Faltam 25.331 votos do PT, 20.173 do adversário e 19.194 dos demais: 64.698 válidos; 80.419 aptos, 66.086 comparecimentos, 14.333 abstenções, 443 brancos e 945 nulos. Esses valores foram demonstrados por UF/campo e por célula municipal. A diferença reconciliada é zero. O primeiro turno não foi alterado.

**Implicação para a main:** a nova série municipal do segundo turno inclui o trânsito interno de 2010; o primeiro turno atual não. Antes de comparar os turnos de 2010 nas capitais, alinhar conscientemente essa abrangência. `brief_f_primeiro_turno_reconciliacao.csv` conserva tanto a diferença original quanto o ajuste demonstrado; `brief_f_voto_transito_2010.csv` registra os códigos originais e seus destinos.

### Municípios e cidades do exterior

Não houve código brasileiro sem par, nem município descartado, nem duplicação de ano × IBGE. A quantidade de municípios é a de cada eleição; não foram inventadas linhas históricas para municípios criados depois. Cidades de ZZ que só aparecem no detalhe, com aptos e sem comparecimento/votos, foram conservadas nos totais com zero apenas nos votos ausentes. Evidência: brief_f_exterior_sem_votacao.csv. Elas não entram nos arquivos municipais.

### Dois caminhos de conferência

1. Exportação por pandas, agrupamento por município e cruzamento com os históricos Brasil/UF; comparação dos candidatos com o detalhe e das somas municipais com as somas diretas de cada bruto. Em 2026/2, cada município é normalizado e somado contra os JSON finais de UF e BR.
2. `brief_f_validar.py`, sem pandas: csv.DictReader, Counter e inteiros Python. Reconstrói 601.434 células municipais, 180 células nacionais, 1.595 células de zona e confere 5.853 hashes das entradas. Nenhuma diferença. Evidência: brief_f_validacao_independente.json.

Os resíduos aritméticos que já constam dos brutos (por exemplo, aptos em seções não instaladas e comparecimento que não vira válido/branco/nulo) foram preservados, não corrigidos por estimativa. Estão discriminados por município e zona em brief_f_residuos_fonte.csv. A diferença zero das provas significa igualdade entre as fontes e as saídas, não que toda identidade aritmética do TSE foi forçada.

## 3. Comparecimento por ano e turno

`comparecimento_turno.csv`: 36 linhas, 6 eleições × 2 turnos × 3 abrangências: com_exterior, sem_exterior e exterior. Sem exterior inclui voto em trânsito dentro do Brasil. Colunas: ano, turno, abrangencia, aptos, comparecimento, abstencoes, brancos, nulos. Não somar as três abrangências entre si: exterior + sem_exterior = com_exterior.

O primeiro turno de comparecimento_ano.csv usa **com exterior e com trânsito interno de 2010**. Os seus cinco campos fecharam em todos os anos (30 provas). O segundo turno de 2026 vem dos JSON finais da eleição 6258, com tf = s, conferidos contra as somas de municípios, ZZ, UFs e BR.

| 2026 · 2º turno | Aptos | Comparecimento | Abstenções | Brancos | Nulos |
|---|---:|---:|---:|---:|---:|
| com_exterior | 158.745.502 | 128.236.074 | 30.509.005 | 1.430.496 | 2.723.305 |
| sem_exterior | 157.828.819 | 127.854.631 | 29.974.188 | 1.425.821 | 2.718.188 |
| exterior | 916.683 | 381.443 | 534.817 | 4.675 | 5.117 |

Com exterior, a taxa é 30.509.005 ÷ 158.745.502 = 19,22%. Os 423 aptos que não se repartem entre comparecimento e abstenções já constam da totalização; estão no exterior e foram preservados. Não calcular abstenções por subtração de aptos.

## 4. Perfil de comparecimento e abstenção de 2026

**Segundo turno ainda não publicado nas fontes consolidadas consultadas.** Não foram criados abstencao_perfil_2turno.csv nem abstencao_faixa_municipio_2turno.csv vazios ou estimados.

Fontes consultadas:

- [Catálogo Comparecimento e Abstenção 2026](https://dadosabertos.tse.jus.br/dataset/comparecimento-e-abstencao-2026) e seu package_show na API CKAN; fonte ELO, frequência a cada eleição.
- [ZIP oficial do perfil](https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_comparecimento_abstencao/perfil_comparecimento_abstencao_2026.zip). Leitura completa do membro BRASIL: 11.060.908 linhas, todas NR_TURNO = 1. Geração interna em 13/10/2026; membros do ZIP datados de 21/10/2026. O diretório não oferece índice utilizável; o arquivo concreto foi consultado e preservado.
- [Cronograma do Cadastro Eleitoral, Resolução TSE 23.750/2026](https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-750-de-26-de-fevereiro-de-2026), anexo: processamento do segundo turno a partir de 25/10, envio até 29/10, conclusão até 02/11/2026.

O catálogo não informa data garantida para liberar o CSV de perfil. Nesta eleição, a geração do primeiro turno ocorreu 9 dias após a votação e o empacotamento disponível, 17 dias após. Isso aponta para dias/semanas após consolidação cadastral, mas não comprova uma data de publicação do segundo turno; 02/11 é prazo de processamento, não promessa de disponibilização do ZIP. Registrar como dado pendente na integração.

## 5. Votação por seção e zona

**2022 pronto:** t20_secoes_2turno_2022.csv tem 420.904 linhas de seção × votável; t20_zonas_2turno_2022.csv tem 319 zonas nas 34 cidades, com PT, adversário, válidos, brancos, nulos, seções e locais. A soma por cidade fecha com municipio_2turno.csv; PT e adversário por zona fecham com presidente_2022_BR.csv: 808 provas, diferença zero (brief_f_prova_zonas_2022.csv). A soma seção → zona foi refeita independentemente pelo validador.

Chave para integrar: cd_ibge + zona (e ano/turno no formato longo). Os 320 registros de t20_locais.csv são o desenho atual de 2026; o conjunto de 2022 tem 319. Preservar a cobertura de cada ano e não inventar votação para zona inexistente. Não foi copiada a posição px/py de 2026, que depende do peso dos válidos do próprio ano.

**2026 pronto por zona:** `t20_zonas_2turno_2026.csv`: 320 zonas, 34 cidades e 110.412 seções totalizadas. Foram coletados os arquivos finais EA20 por município/zona da eleição 6258, conforme os códigos de zona da configuração oficial. Todos têm tf = s e seções totalizadas = seções totais. As chaves são exatamente as 320 zonas da tela atual. Cada cidade fecha nos nove campos de municipio_2turno.csv e, por outro caminho, no JSON municipal da API: 612 provas, diferença zero. Evidências: brief_f_prova_zonas_2026.csv e brief_f_fontes_zonas_2026.csv (320 URLs, caminhos e hashes). Os JSON estão em dados/bruto/tse/brief_f_zonas_2026/.

`t20_zonas_2turno_2022_2026.csv`: 639 linhas em formato longo, com ano e turno explícitos; os votos de 2022 vêm das seções e os aptos/comparecimento/abstenções, do detalhe por zona. Em 2026, os nove campos vêm do resultado final por zona. A contagem de locais de 2026 está vazia porque o EA20 não a informa; não se reutilizou como se fosse do segundo turno a contagem do primeiro. A quantidade de seções é a da própria fonte do ano. O validador refaz a leitura dos 320 JSON sem a função de normalização do exportador e compara todas as células do combinado.

Fonte e contrato: [EA20 – Arquivo de resultado unificado, páginas 1–3](https://www.tse.jus.br/eleicoes/eleicoes-2026-content/arquivos/divulgacao-de-resultados/tse-ea20-arquivo-de-resultado-unificado). O contrato prevê o arquivo de abrangência zona e o nome UF + município + z + zona + cargo + eleição. Exemplo consultado: https://resultados.tse.jus.br/oficial/ele2026/6258/dados/rj/rj60011-z0004-c0001-e006258-u.json . Nenhuma votação de zona foi inferida dos totais municipais.

**Seções de 2026 ainda pendentes no ZIP:** leitura integral de [votacao_secao_2026_BR.zip](https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip): 3.800.511 linhas, todas do primeiro turno, geradas em 06/10/2026. O [catálogo Resultados 2026](https://dadosabertos.tse.jus.br/dataset/resultados-2026) lista atualização do arquivo por turno, mas o conteúdo ainda não contém o segundo. Isso não impede a entrega das zonas pela API.

O [catálogo Boletim de Urna 2026](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna) foi lido por HTML e API CKAN: os 56 recursos listados são 28 ZIPs do primeiro turno e seus 28 hashes; nenhum lote do segundo turno. Sua descrição genérica menciona ambos os turnos, o que não significa que ambos já estejam publicados. BUs individuais podem ser consultados no aplicativo Resultados; não foi confundida essa consulta individual com a disponibilidade de um lote consolidado e auditado das 34 cidades.

O detalhe de seção depende do arquivo nacional contendo NR_TURNO = 2 ou dos lotes de BU do segundo turno por UF. A necessidade atual da tela, que agrega por zona, foi atendida integralmente pelo EA20.

## 6. Inventário das medidas

49 medidas leem diretamente 'Município segundo turno'; todas filtram [Ano] explicitamente dentro do CALCULATE que envolve a leitura. Nenhuma soma irrestrita foi encontrada. O filtro variável _a de T01 usa [T01 · ponto · ano]. Esta é uma auditoria estática dos DAX, sem execução no Desktop. Os arquivos DAX e seus hashes estão no inventário CSV.

| Medida | Filtra Ano | Valor |
|---|---|---|
| T01 · ponto · % no grupo em 2022 | Sim | 2022 |
| T01 · ponto · % no grupo em 2026 | Sim | 2026 |
| T01 · ponto · votos no grupo em 2022 | Sim | 2022 |
| T01 · ponto · votos no grupo em 2026 | Sim | 2026 |
| T01 · ponto · votos no grupo | Sim | _a |
| T03 · aptos (municípios) | Sim | 2026 |
| T03 · votos (municípios) | Sim | 2026 |
| T03 · votos 2022 (municípios) | Sim | 2022 |
| T03 · votos do adversário (municípios) | Sim | 2026 |
| T03 · votos do adversário 2022 (municípios) | Sim | 2022 |
| T03 · válidos (municípios) | Sim | 2026 |
| T03 · válidos 2022 (municípios) | Sim | 2022 |
| T05 · aptos (municípios) | Sim | 2026 |
| T05 · votos (municípios) | Sim | 2026 |
| T05 · votos 2022 (municípios) | Sim | 2022 |
| T05 · votos do adversário (municípios) | Sim | 2026 |
| T05 · votos do adversário 2022 (municípios) | Sim | 2022 |
| T05 · válidos (municípios) | Sim | 2026 |
| T05 · válidos 2022 (municípios) | Sim | 2022 |
| T11 · saldo 2022 | Sim | 2022 |
| T11 · saldo 2026 | Sim | 2026 |
| T11 · votos de Lula 2022 | Sim | 2022 |
| T11 · votos de Lula 2026 | Sim | 2026 |
| T11 · votos do PL 2022 | Sim | 2022 |
| T11 · votos do PL 2026 | Sim | 2026 |
| T11 · válidos 2022 | Sim | 2022 |
| T11 · válidos 2026 | Sim | 2026 |
| T12 · saldo municipal 2022 | Sim | 2022 |
| T12 · saldo municipal 2026 | Sim | 2026 |
| T13 · saldo 2022 | Sim | 2022 |
| T13 · saldo 2026 | Sim | 2026 |
| T13 · válidos 2022 | Sim | 2022 |
| T13 · válidos 2026 | Sim | 2026 |
| T27 · abstenções 2º | Sim | 2026 |
| T27 · brancos 2º | Sim | 2026 |
| T27 · comparecimento 2º | Sim | 2026 |
| T27 · Flávio 2º | Sim | 2026 |
| T27 · Jair 2022 | Sim | 2022 |
| T27 · Lula 2022 | Sim | 2022 |
| T27 · Lula 2º | Sim | 2026 |
| T27 · nulos 2º | Sim | 2026 |
| T28 · abstenções 2º | Sim | 2026 |
| T28 · brancos 2º | Sim | 2026 |
| T28 · comparecimento 2º | Sim | 2026 |
| T28 · Flávio 2º | Sim | 2026 |
| T28 · Jair 2022 | Sim | 2022 |
| T28 · Lula 2022 | Sim | 2022 |
| T28 · Lula 2º | Sim | 2026 |
| T28 · nulos 2º | Sim | 2026 |

Inventários completos: brief_f_inventario_medidas.csv e brief_f_inventario_medidas.md (com caminhos individuais). A main decide a troca da tabela e valida o modelo no Desktop.

## Arquivos de evidência e reprodução

Os três ZIPs oficiais foram preservados em dados/bruto/tse/brief_f/ (662.122.642 bytes no total), junto dos metadados CKAN. brief_f_publicacoes.json contém URLs, nomes de membros, datas, SHA-256, contagens de turnos e recursos do catálogo. brief_f_entradas_sha256.csv contém o manifesto das entradas locais usadas na exportação e no inventário.

| CSV novo em dados/saida/2turno | Linhas de dados |
|---|---:|
| municipio_2turno_2006_2018.csv | 22.272 |
| municipio_2turno_completo.csv | 33.413 |
| comparecimento_turno.csv | 36 |
| t20_secoes_2turno_2022.csv | 420.904 |
| t20_zonas_2turno_2022.csv | 319 |
| t20_zonas_2turno_2026.csv | 320 |
| t20_zonas_2turno_2022_2026.csv | 639 |
| brief_f_prova_zonas_2026.csv | 612 |
| brief_f_fontes_zonas_2026.csv | 320 |
| brief_f_prova_totais.csv | 5.171 |
| brief_f_prova_zonas_2022.csv | 808 |
| brief_f_resumo_totais.csv | 12 |
| brief_f_primeiro_turno_reconciliacao.csv | 1.458 |
| brief_f_voto_transito_2010.csv | 108 |
| brief_f_exterior_sem_votacao.csv | 196 |
| brief_f_residuos_fonte.csv | 12.920 |
| brief_f_inventario_medidas.csv | 49 |
| brief_f_entradas_sha256.csv | 5.853 |

Reproduzir no PowerShell 5.1, a partir da raiz do projeto (cada comando deve terminar com código 0):

```powershell
python -I -X utf8 pipeline/brief_f_2turno.py
python -I -X utf8 pipeline/brief_f_publicacoes.py --somente-cache
python -I -X utf8 pipeline/brief_f_zonas_2026.py --somente-cache
python -I -X utf8 pipeline/brief_f_validar.py
python -I -X utf8 pipeline/brief_f_relatorio.py
git diff --check
```

Sem cache local, omitir --somente-cache nos comandos de publicações e zonas. Para consultar uma publicação futura sem sobrescrever os brutos, usar --cache-novo com nome inédito em brief_f_publicacoes.py, por exemplo `--cache-novo brief_f_20261103`. Se um perfil do segundo turno aparecer, o script interrompe e exige a implementação/conferência da exportação por perfil antes de publicar. Os comandos acima reproduzem a entrega da consulta atual.

Diagnósticos opcionais: `python -I -X utf8 pipeline/brief_f_diagnostico.py` (esquemas locais), `--chaves` (cidades sem votação) e `--remoto` (diretório central e amostras dos ZIPs, sem baixá-los integralmente).
