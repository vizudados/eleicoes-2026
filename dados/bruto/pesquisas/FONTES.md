# FONTES — pesquisas presidenciais 2026 (1º e 2º turno)

Levantamento feito em 22/10/2026 para o painel "O que as pesquisas diziam antes do 1º turno e o que dizem agora?".

## Arquivos

- `pesquisas_1turno.csv`: 80 pesquisas de 1º turno divulgadas de 01/08 a 03/10/2026, 160 linhas (uma de `totais` e uma de `validos` por pesquisa).
- `pesquisas_2turno.csv`: 120 cenários Lula × Flávio, 240 linhas. São 79 cenários `antes_1turno` (das pesquisas do 1º turno) e 41 pesquisas `apos_1turno` (divulgadas de 05/10 a 22/10/2026).
- Separador `;`, UTF-8 sem BOM, datas AAAA-MM-DD, ponto decimal. Nenhum campo contém `;`. Na `observacao`, as notas são separadas por ` | `.

## Como foi feito

1. **Índice.** Tabelas da página da Wikipédia em inglês [Opinion polling for the 2026 Brazilian presidential election](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Brazilian_presidential_election), baixadas em 22/10/2026 (wikitexto). Seções usadas: 1º turno "Aug–Oct (Campaign period)" e o fim de "Apr–Aug"; 2º turno "October (after 1st round)", "Aug–Oct" e o fim de "Apr–Aug". A versão em português foi usada só para cruzar nomes de institutos.
2. **Conferência.** Cada pesquisa do índice foi conferida, instituto a instituto, em fonte primária: relatório/PDF do instituto (muitos hospedados por Poder360, CNN Brasil, Canal Meio, CNT, BTG e Ipespe) ou matéria do contratante. Quando a primária não abriu, a conferência foi feita em veículo grande que reproduz os números (CNN Brasil, Poder360, Gazeta do Povo, Exame, CartaCapital, Metrópoles etc.).
3. **Varredura fora do índice.** Busca por pesquisas dos mesmos institutos que faltavam no índice e por outros institutos. Para isso foram usados os dados abertos do TSE (`pesquisa_eleitoral_2026.zip` e `pesquisa_contratante_2026.zip`, cdn.tse.jus.br, atualizados em 22/10), filtrando presidente com abrangência nacional. Entraram 22 pesquisas novas (Gerp, Veritá, Alfa, DataTrends, American Analytics, Instituto França, Instituto Ranking, Instituto Phoenix e a Onda 2 v2 da Palver).
4. **Regras.** Nada foi estimado. Os votos válidos só aparecem quando o instituto ou o contratante os divulgou, inclusive quando saíram depois, em série histórica do próprio instituto (está indicado na `observacao`). Número não confirmado ficou em branco, com a razão na `observacao`. A única soma feita aqui é a coluna `outros`, que soma os percentuais publicados de Caiado, Zema e demais candidatos.

## Convenções das colunas

- **`outros`** (1º turno) = Ronaldo Caiado (PSD) + Romeu Zema (Novo) + demais candidatos, com a composição na `observacao`. Caiado teve 2,18% dos válidos no resultado oficial, por isso vale abrir `outros` se o painel precisar dele.
- **Pablo Marçal**, quando testado no cenário principal (PoderData, Futura, MDA, Vox, Veritá, Gerp), entra em `outros`. Quando havia um cenário principal sem ele, o CSV usa esse (ver "Cenários não incluídos").
- **`brancos_nulos` e `indecisos`** seguem o que cada instituto publica:
  - Gerp: `brancos_nulos` = "nenhum deles".
  - Palver: `brancos_nulos` = "branco/nulo ou não votaria".
  - AtlasIntel (2º turno) e Palver Onda 1 (2º turno): o instituto só publica branco/nulo/não sabe somados, que foram para `brancos_nulos`, com `indecisos` em branco.
  - Indexa: publica "não votariam" à parte (4% a 8%). Esse número ficou fora das duas colunas e está na `observacao`.
- **`validos`**: linha sempre presente. Fica vazia quando o instituto não divulgou. Os válidos da Quaest (02–03/10) usam modelo de eleitor provável.
- **`modo`**: presencial, telefone, telefone (URA), online ou misto. Em algumas rodadas do Datafolha e da Quaest a fonte não cita o modo e foi usado o padrão do instituto, como avisa a `observacao`.
- **`divulgacao`**: data da publicação dos números. Quando o TSE registrava outra data prevista, valeu a publicação.
- **`momento`** (2º turno): `antes_1turno` = cenário Lula × Flávio de pesquisa divulgada até 03/10; `apos_1turno` = divulgada de 05/10 em diante.

## Retrato rápido (com base nos CSVs)

### Última pesquisa de cada instituto antes do 1º turno

| Instituto | Divulgação | Campo | Lula × Flávio (válidos) | Lula × Flávio (totais) |
|---|---|---|---|---|
| American Analytics | 23/09 | 15/09–20/09 | não divulgados | 38 × 34 |
| Alfa Inteligência | 24/09 | 18/09–23/09 | não divulgados | 40 × 33 |
| Nexus | 28/09 | 25/09–27/09 | 44 × 39 | 42 × 37 |
| Veritá | 30/09 | 20/09–25/09 | 44,65 × 45,14 | não divulgados |
| Ideia | 30/09 | 25/09–28/09 | não divulgados | 39,4 × 38,4 |
| Indexa | 30/09 | 27/09–29/09 | não divulgados | 39 × 34 |
| Real Time Big Data | 01/10 | 26/09–30/09 | 46 × 41 | 43 × 39 |
| DataTrends | 02/10 | s/d–s/d | não divulgados | 41 × 39 |
| Vox Brasil | 02/10 | 29/09–01/10 | não divulgados | 40,4 × 41,2 |
| AtlasIntel | 03/10 | 27/09–02/10 | 47 × 44,1 | 46,7 × 43,8 |
| Gerp | 03/10 | 30/09–02/10 | 44 × 46 | 41 × 43 |
| Instituto França (IFP) | 03/10 | 28/09–02/10 | não divulgados | 40,62 × 37,49 |
| MDA | 03/10 | 30/09–02/10 | 47,8 × 42,1 | 43,1 × 38 |
| PoderData | 03/10 | 30/09–02/10 | 45 × 43 | 42 × 41 |
| Datafolha | 03/10 | 02/10–03/10 | 45 × 42 | 42 × 40 |
| Futura | 03/10 | 02/10–03/10 | 42,6 × 44,8 | 40,5 × 42,5 |
| Palver | 03/10 | 30/09–03/10 | não divulgados | 43 × 47 |
| Quaest | 03/10 | 02/10–03/10 | 46 × 45 | 40 × 38 |

Resultado oficial (TSE), votos válidos: Flávio 47,03 × Lula 45,16.

### 2º turno desde 05/10

- Média simples de 39 pesquisas com votos totais: Lula 45,6 × Flávio 47,8.
- Média simples de 35 pesquisas com votos válidos divulgados: Lula 48,7 × Flávio 51,3.
- Só a última de cada instituto: 20 institutos nos totais (Lula 45,9 × Flávio 47,3) e 18 nos válidos (Lula 49,2 × Flávio 50,8).
- Ficou fora das médias a Veritá de campo 26/09–02/10, com campo antes do 1º turno, divulgada em 05/10 e retirada do ar. A AtlasIntel de 03–08/10 entrou, porque quase todo o campo foi depois do 1º turno.
- As médias não ponderam por amostra, metodologia ou histórico de acerto.

## Fontes por pesquisa

Status: **C** = confirmado em fonte primária ou veículo grande; **P** = parcial. "Índice" indica se a pesquisa estava na Wikipédia em inglês.

### Alfa Inteligência

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 24/09 | 18/09–23/09 | BR-02512/2026 | 1º, 2º antes | C | não | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/alfa-inteligencia-presidente-setembro-2026/> | <https://www.tribunapr.com.br/eleicoes/2026/nova-pesquisa-para-presidente-mostra-lula-com-8-pontos-de-vantagem/> ; <https://revistaoeste.com/politica/alfa-inteligencia-lula-e-flavio-empatam-no-2o-turno/> ; <https://abcdoabc.com.br/lula-e-flavio-empatam-43-2o-turno-diz-pesquisa> |
| 20/10 | 15/10–19/10 | BR-00820/2026 | 2º após | C | sim | <https://www.dgabc.com.br/Noticia/4353692/alfa-inteligencia-flavio-tem-48-8-dos-votos-totais-contra-45-9-de-lula-em-empate-tecnico> | <https://www.cnnbrasil.com.br/eleicoes/alfa-flavio-tem-515-dos-votos-validos-no-2o-turno-lula-485/> ; <https://tmc.com.br/politica/flavio-bolsonaro-lula-segundo-turno-alfa-inteligencia-2026/> ; <https://exame.com/brasil/pesquisa-para-presidente-alfa-flavio-bolsonaro-tem-515-e-lula-485-no-2o-turno/> ; <https://www.oliberal.com/politica/alfa-inteligencia-flavio-tem-48-8-dos-votos-totais-contra-45-9-de-lula-em-empate-tecnico-1.1184555> |

### American Analytics

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 23/09 | 15/09–20/09 | BR-02587/2026 | 1º, 2º antes | C | não | <https://timesbrasil.com.br/brasil/decisao-2026-lula-e-flavio-bolsonaro-estao-empatados-numericamente-em-43-no-2o-turno-indica-pesquisa-american-analytics-times-brasil-cnbc/> | <https://www.poder360.com.br/poder-eleicoes/lula-e-flavio-empatam-no-2o-turno-com-43-diz-pesquisa/> ; <https://www.dgabc.com.br/Noticia/4348650/pesquisa-aponta-lula-e-flavio-bolsonaro-empatados-em-43-no-2-turno> ; <https://static.poder360.com.br/uploads/2026/09/american-analytics-pesquisa-presidente-setembro.pdf> |

### AtlasIntel

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 31/08 | 25/08–30/08 | BR-07972/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/atlas-bloomberg-lula-tem-471-no-2o-turno-flavio-426/> ; <https://www.congressoemfoco.com.br/noticia/121788/atlas-bloomberg-lula-abre-9-7-pontos-sobre-flavio-e-cury-chega-a-7-8> | <https://www.diariodepernambuco.com.br/politica/2026/08/11722657-atlas-bloomberg-lula-tem-471-e-flavio-bolsonaro-registra-426-no-segundo-turno.html> ; <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Pesquisa-Atlas_Bloomberg-Nacional-261003.pdf> ; <https://veja.abril.com.br/politica/atlasintel-pesquisa-mostra-disputa-presidencial-apos-primeiros-debates-e-sabatinas/> |
| 10/09 | 04/09–09/09 | BR-01452/2026 | 1º, 2º antes | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/09/Pesquisa-Atlas_Bloomberg-Nacional-260909.pdf> | <https://www.cnnbrasil.com.br/eleicoes/atlasintel-bloomberg-lula-tem-43-no-1o-turno-flavio-374/> ; <https://www.cnnbrasil.com.br/eleicoes/atlasintel-bloomberg-flavio-tem-464-no-2o-turno-lula-462/> |
| 17/09 | 11/09–16/09 | BR-06221/2026 | 1º, 2º antes | C | sim | <https://www.pollingdata.com.br/links/relatorio_BR-06221-2026_AtlasIntel.pdf> | <https://www.cnnbrasil.com.br/eleicoes/flavio-tem-472-no-2o-turno-lula-468-diz-atlas/> ; <https://www.moneytimes.com.br/pesquisa-atlasintel-bloomberg-17-de-setembro-gaep/> ; <https://www.cnnbrasil.com.br/eleicoes/lula-tem-441-no-1o-turno-flavio-417-diz-atlas/> |
| 23/09 | 17/09–22/09 | BR-04739/2026 | 1º, 2º antes | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/09/Pesquisa-Atlas_Bloomberg-Nacional-260922.pdf> | <https://www.cnnbrasil.com.br/eleicoes/atlas-bloomberg-lula-tem-458-no-1o-turno-flavio-434/> ; <https://www.cnnbrasil.com.br/eleicoes/atlas-bloomberg-lula-tem-477-no-2o-turno-flavio-474/> |
| 29/09 | 23/09–28/09 | BR-04391/2026 | 1º, 2º antes | C | sim | <https://www.pollingdata.com.br/links/relatorio_BR-04391-2026_AtlasIntel.pdf> | <https://www.diariodepernambuco.com.br/politica/2026/09/11725225-lula-tem-453-contra-422-de-flavio-bolsonaro-no-primeiro-turno-diz-pesquisa-atlas-bloomberg.html> ; <https://noticias.uol.com.br/eleicoes/2026/09/29/atlasbloomberg-lula-e-flavio-tem-empate-tecnico-no-2-turno.ghtm> |
| 03/10 | 27/09–02/10 | BR-00999/2026 | 1º, 2º antes | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Pesquisa-Atlas_Bloomberg-Nacional-261003.pdf> | <https://trademap.com.br/noticias/news-8377235> |
| 09/10 | 03/10–08/10 | BR-03663/2026 | 2º após | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Pesquisa-Atlas_Bloomberg-Nacional-261009.pdf> | <https://www.cnnbrasil.com.br/eleicoes/atlas-flavio-tem-528-dos-votos-validos-no-2o-turno-lula-472/> |
| 19/10 | 13/10–18/10 | BR-02418/2026 | 2º após | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Pesquisa-Atlas_Bloomberg-Nacional-261019.pdf> | <https://www.cnnbrasil.com.br/eleicoes/atlas-flavio-tem-511-dos-votos-validos-no-2o-turno-lula-489/> ; <https://www.brasildefato.com.br/2026/10/19/lula-reduz-diferenca-e-marca-476-no-segundo-turno-contra-498-de-flavio-bolsonaro-aponta-pesquisa-atlasbloomberg/> |

### DataTrends

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 16/09 | 12/09–14/09 | BR-08691/2026 | 1º, 2º antes | P | não | <https://revistaoeste.com/politica/flavio-bolsonaro-lidera-simulacao-de-2o-turno-contra-lula-indica-datatrends/> | — |
| 02/10 | s/d–s/d | BR-04414/2026 | 1º, 2º antes | C | não | <https://revistaoeste.com/politica/datatrends-mostra-empate-entre-lula-e-flavio-em-eventual-2o-turno/> | — |
| 11/10 | 07/10–09/10 | BR-03576/2026 | 2º após | C | não | <https://static.poder360.com.br/uploads/2026/10/pesquisa-datatrends-nacional-11out2026.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-531-e-lula-tem-469-em-votos-validos-diz-datatrends/> ; <https://timesbrasil.com.br/eleicoes-2026/pesquisa-datatrends-flavio-tem-531-contra-469-de-lula/> ; <https://revistaoeste.com/politica/datatrends-flavio-tem-50-contra-44-de-lula-no-2o-turno/> |
| 19/10 | 15/10–17/10 | BR-04454/2026 | 2º após | C | sim | <https://www.gp1.com.br/eleicoes-2026/noticia/2026/10/19/flavio-bolsonaro-tem-515-e-lula-485-aponta-datatrends-634295.html> | <https://www.poder360.com.br/poder-pesquisas/saiba-como-estao-lula-e-flavio-nas-pesquisas-a-3-dias-da-eleicao/> ; <https://www.ocafezinho.com/2026-10-20/datatrends-flavio-tem-515-e-lula-485-dos-votos-validos-lula-tem-68-no-nordeste/> ; <https://robsonpiresxerife.com/pesquisa-datatrends-flavio-bolsonaro-tem-515-dos-votos-validos-contra-485-de-lula/> |

### Datafolha

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 21/08 | 18/08–19/08 | BR-04496/2026 | 1º, 2º antes | C | sim | <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-47-e-flavio-43-em-2o-turno-diz-datafolha/> ; <https://www.cnnbrasil.com.br/eleicoes/datafolha-lula-tem-39-das-intencoes-de-voto-no-1o-turno-flavio-33/> | <https://static.poder360.com.br/uploads/2026/09/pesquisa-datafolha-17set2026.pdf> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-agosto-2026/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/08/21/datafolha-primeiro-turno-21-agosto.ghtml> |
| 03/09 | 01/09–02/09 | BR-03669/2026 | 1º, 2º antes | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-setembro-2026/> ; <https://www.cnnbrasil.com.br/eleicoes/datafolha-no-1o-turno-lula-tem-38-flavio-33-e-cury-8/> | <https://static.poder360.com.br/uploads/2026/09/pesquisa-datafolha-17set2026.pdf> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/03/datafolha-2o-turno-presidente-3-setembro.ghtml> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/03/datafolha-presidente-3-setembro.ghtml> |
| 11/09 | 08/09–10/09 | BR-01833/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/datafolha-lula-tem-39-e-flavio-35-no-1-turno/> ; <https://www.cnnbrasil.com.br/eleicoes/datafolha-lula-tem-46-no-2o-turno-flavio-44/> | <https://static.poder360.com.br/uploads/2026/09/pesquisa-datafolha-17set2026.pdf> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-setembro-2026-2/> |
| 17/09 | 15/09–17/09 | BR-04029/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/pesquisa-datafolha-17set2026.pdf> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-setembro-2026-3/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/17/datafolha-segundo-turno-presidente-17-setembro.ghtml> ; <https://www.cnnbrasil.com.br/eleicoes/datafolha-lula-tem-39-no-1o-turno-flavio-36-e-cury-6/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/17/datafolha-presidente-17-setembro.ghtml> |
| 24/09 | 22/09–23/09 | BR-00304/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/datafolha-lula-tem-47-no-2o-turno-flavio-45/> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-setembro-2026-4/> | <https://static.poder360.com.br/uploads/2026/10/datafolhanacional-1out.pdf> ; <https://static.poder360.com.br/uploads/2026/10/datafolha-presidencial-outubro.pdf> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/24/datafolha-presidente-24-setembro.ghtml> |
| 01/10 | 29/09–01/10 | BR-08039/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/10/datafolhanacional-1out.pdf> ; <https://static.poder360.com.br/uploads/2026/10/datafolha-presidencial-outubro.pdf> | <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/01/datafolha-presidente-1-outubro.ghtml> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-outubro-2026-2/> ; <https://www1.folha.uol.com.br/poder/2026/10/datafolha-lula-tem-45-e-flavio-bolsonaro-40-em-votos-validos-no-1o-turno.shtml> |
| 03/10 | 02/10–03/10 | BR-01708/2026 | 1º, 2º antes | C | sim | <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-45-e-flavio-42-dos-votos-validos-no-1o-turno-diz-datafolha/> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-outubro-2026-vespera-1-turno/> ; <https://www.cnnbrasil.com.br/eleicoes/datafolha-2-turno/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/03/datafolha-presidente-3-outubro.ghtml> |
| 08/10 | 06/10–07/10 | BR-02949/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/datafolha-presidente-2turno-8out2026.pdf> | <https://www1.folha.uol.com.br/poder/2026/10/datafolha-flavio-bolsonaro-tem-52-e-lula-48-em-votos-validos-no-segundo-turno.shtml> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-outubro-2026-segundo-turno/> ; <https://www.jornalopcao.com.br/ultimas-noticias/flavio-bolsonaro-lidera-primeiro-datafolha-do-segundo-turno-com-52-dos-votos-validos-contra-48-de-lula-877160/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/08/datafolha-presidente-8-outubro.ghtml> |
| 15/10 | 13/10–14/10 | BR-00466/2026 | 2º após | C | sim | <https://www.poder360.com.br/poder-eleicoes-2026/datafolha-confirma-poderdata-aya-e-da-flavio-com-51-e-lula-com-49/> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-outubro-2026-segundo-turno-2/> ; <https://diariodonordeste.verdesmares.com.br/pontopoder/datafolha-no-2-turno-flavio-bolsonaro-tem-51-e-lula-49-em-votos-validos-1.3798886> ; <https://www.em.com.br/politica/2026/10/7521089-datafolha-divulga-nova-pesquisa-para-presidente-no-2-turno.html> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/15/datafolha-presidente-segundo-turno-15-outubro.ghtml> |
| 22/10 | 20/10–22/10 | BR-09709/2026 | 2º após | C | sim | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-50-dos-votos-validos-contra-50-de-lula-diz-datafolha/> | <https://www.terra.com.br/noticias/eleicoes/datafolha-2-turno-flavio-bolsonaro-e-lula-empatam-com-50-em-votos-validos,178579b6fa0f17850de817b0260c73797lr3ng40.html> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/datafolha-presidente-outubro-2026-segundo-turno-3/> ; <https://www1.folha.uol.com.br/poder/2026/10/datafolha-flavio-bolsonaro-e-lula-empatam-com-50-dos-votos-validos-cada.shtml> |

### Futura

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 11/08 | 03/08–07/08 | BR-08109/2026 | 1º, 2º antes | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/futura-inteligencia-presidente-agosto-2026/> | <https://www.cnnbrasil.com.br/eleicoes/futura-lula-tem-388-no-1o-turno-flavio-341/> |
| 03/09 | 27/08–01/09 | BR-02793/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/pesquisaFutura-nacional-presidente-3set2026.pdf> | <https://www.cnnbrasil.com.br/eleicoes/futura-lula-tem-387-no-1o-turno-flavio-336/> ; <https://www.cnnbrasil.com.br/eleicoes/futura-lula-tem-456-contra-452-de-flavio-no-2o-turno/> ; <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-387-das-intencoes-de-voto-contra-336-de-flavio/> |
| 11/09 | 04/09–10/09 | BR-02322/2026 | 1º, 2º antes | P | sim | <https://www.cnnbrasil.com.br/eleicoes/futura-lula-tem-392-das-intencoes-de-voto-no-1o-turno-flavio-336/> ; <https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-454-contra-45-de-lula-no-2o-turno/> | — |
| 17/09 | 11/09–15/09 | BR-00749/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-481-no-2o-turno-lula-437/> ; <https://www.cnnbrasil.com.br/eleicoes/futura-lula-tem-383-no-1o-turno-flavio-377/> | — |
| 24/09 | 19/09–23/09 | BR-05268/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/R_BR_Setembro_3.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-404-e-lula-384-no-1o-turno-diz-futura/> ; <https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-494-no-2o-turno-lula-437/> |
| 30/09 | 25/09–29/09 | BR-01122/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-422-das-intencoes-de-voto-no-1o-turno-lula-394/> ; <https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-49-das-intencoes-de-voto-no-2o-turno-lula-435/> | — |
| 03/10 | 02/10–03/10 | BR-02431/2026 | 1º, 2º antes | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Relatorio_Tracking_Nacional_1_Turno_Final_Votos_Validos-3-1.pdf> | <https://trademap.com.br/noticias/news-8377213> |
| 13/10 | 07/10–10/10 | BR-00650/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Pesquisa-Futura-presidente.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-518-contra-482-de-lula-diz-futura/> ; <https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-518-dos-votos-validos-no-2o-turno-lula-482/> |
| 16/10 | 14/10–15/10 | BR-03764/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Relatorio_BR_Out_2_V2_ComTexto_Final.pdf> | <https://www.cnnbrasil.com.br/eleicoes/futura-flavio-tem-508-dos-votos-validos-no-2o-turno-lula-492/> ; <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-508-contra-492-de-lula-no-2o-turno-diz-futura/> |
| 19/10 | 16/10–17/10 | BR-06715/2026 | 2º após | C | sim | <https://exame.com/brasil/pesquisa-futura-para-presidente-flavio-bolsonaro-tem-504-e-lula-496-no-2o-turno/> | — |
| 21/10 | 19/10–20/10 | BR-06614/2026 | 2º após | C | sim | <https://www.cartacapital.com.br/politica/flavio-e-lula-seguem-tecnicamente-empatados-mostra-pesquisa-futura/> | — |

### Gerp

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 11/08 | 06/08–10/08 | BR-08045/2026 | 1º, 2º antes | P | não | <https://revistaoeste.com/politica/flavio-e-lula-tem-empate-tecnico-no-2turno-mostra-pesquisa/> | <https://static.poder360.com.br/uploads/2026/10/PRESIDENCIA_DO_BRASIL_32o_Relatorio_Presidencia_2026_primeiro.pdf> ; <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf> |
| 26/08 | 21/08–25/08 | BR-03547/2026 | 1º, 2º antes | C | não | <https://static.poder360.com.br/uploads/2026/08/gerp-presidente-nacional-25ago2026.pdf> | <https://www.cnnbrasil.com.br/eleicoes/gerp-flavio-tem-47-no-2o-turno-lula-42/> ; <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf> |
| 09/09 | 03/09–08/09 | BR-00251/2026 | 1º, 2º antes | C | não | <https://www.tribunapr.com.br/eleicoes/2026/pesquisa-gerp-flavio-bolsonaro-lula-2026/> | <https://www.cnnbrasil.com.br/eleicoes/gerp-flavio-tem-47-das-intencoes-de-voto-no-2o-turno-lula-40/> ; <https://static.poder360.com.br/uploads/2026/09/pesquisa-gerp-presidencia-republica-17set2026.pdf> ; <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf> |
| 17/09 | 14/09–16/09 | BR-00535/2026 | 1º, 2º antes | C | não | <https://static.poder360.com.br/uploads/2026/09/pesquisa-gerp-presidencia-republica-17set2026.pdf> | <https://www.tribunapr.com.br/noticias/brasil/flavio-bolsonaro-tem-50-contra-43-de-lula-2-turno-pesquisa/> ; <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf> |
| 29/09 | 24/09–28/09 | BR-03929/2026 | 1º, 2º antes | C | não | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-50-contra-43-de-lula-no-2o-turno-diz-gerp-2/> | <https://www.tribunapr.com.br/eleicoes/2026/flavio-supera-lula-em-novas-simulacoes-de-1o-e-2-turnos/> ; <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf> |
| 03/10 | 30/09–02/10 | BR-00509/2026 | 1º, 2º antes | C | não | <https://static.poder360.com.br/uploads/2026/10/presidente-gerp-nacional-outubro-1.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-49-contra-44-de-lula-no-2o-turno-diz-gerp/> ; <https://www.tribunapr.com.br/noticias/flavio-bolsonaro-abre-vantagem-sobre-lula-pesquisa-2026/> ; <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf> |
| 13/10 | 08/10–12/10 | BR-07877/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/PRESIDENCIA_DO_BRASIL_32o_Relatorio_Presidencia_2026_primeiro.pdf> | <https://www.cnnbrasil.com.br/eleicoes/gerp-flavio-tem-55-dos-votos-validos-no-2o-turno-lula-45/> ; <https://poder360.com.br/poder-eleicoes-2026/flavio-tem-53-contra-44-de-lula-diz-pesquisa-gerp> ; <https://acritica.net/eleicoes-2026/pesquisa-eleitoral-lula-e-flavio-gerp-segundo-turno/> |
| 16/10 | 14/10–16/10 | BR-05187/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf> | <https://revistaoeste.com/politica/gerp-flavio-tem-55-e-lula-45-dos-votos-validos/> ; <https://tmc.com.br/politica/pesquisa-gerp-flavio-bolsonaro-lidera-com-50-contra-45-de-lula/> ; <https://midiamax.com.br/brasil/2026/flavio-tem-52-votos-validos-2o-turno-lula-48-aponta-gerp/> |
| 21/10 | 19/10–21/10 | BR-03835/2026 | 2º após | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/gerp-presidente-outubro-2026-segundo-turno-3/> | <https://www.cnnbrasil.com.br/eleicoes/gerp-flavio-tem-53-dos-votos-validos-no-2o-turno-lula-47-2/> ; <https://www.tribunapr.com.br/noticias/brasil/gerp-nao-escolhem-lula-nem-flavio-bolsonaro-ou-nao-sabem-em-quem-votar/> |

### Ideia

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 05/08 | 31/07–03/08 | BR-04579/2026 | 1º, 2º antes | C | sim | <https://www.canalmeio.com.br/wp-content/uploads/2026/08/Pesquisa-Meio_Ideia-Agosto-1.pdf> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/meio-ideia-presidente-agosto-2026/> ; <https://www.opovo.com.br/noticias/politica/eleicoes/2026/08/05/pesquisa-ideia-traz-lula-liderando-no-1-e-no-2-turno.html> |
| 09/09 | 04/09–07/09 | BR-07935/2026 | 1º, 2º antes | C | sim | <https://www.canalmeio.com.br/wp-content/uploads/2026/09/Pesquisa-Meio_Ideia-Setembro.pdf> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/meio-ideia-presidente-setembro-2026/> ; <https://static.poder360.com.br/uploads/2026/09/Pesquisa-Meio_Ideia-Setembro-IMPRENSA.pdf> |
| 30/09 | 25/09–28/09 | BR-08706/2026 | 1º, 2º antes | C | sim | <https://www.canalmeio.com.br/wp-content/uploads/2026/09/Pesquisa-Meio_Ideia-Setembro2.pdf> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/meio-ideia-presidente-setembro-2026-2/> |
| 21/10 | 15/10–19/10 | BR-08251/2026 | 2º após | C | sim | <https://www.canalmeio.com.br/wp-content/uploads/2026/10/Pesquisa-Meio_Ideia-Outubro.pdf> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/meio-ideia-presidente-outubro-2026-segundo-turno/> |

### Indexa

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 26/08 | 20/08–23/08 | BR-06366/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/indexa-lula-tem-39-das-intencoes-de-voto-no-1o-turno-flavio-34/> ; <https://www.cnnbrasil.com.br/eleicoes/indexa-lula-tem-46-no-2o-turno-flavio-41/> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/indexa-broadcast-presidente-agosto-2026/> ; <https://www.cartacapital.com.br/politica/lula-lidera-a-disputa-pela-presidencia-em-primeiro-turno-mostra-pesquisa-indexa-broadcast/> ; <https://trademap.com.br/noticias/news-8232790> |
| 15/09 | 10/09–13/09 | BR-03482/2026 | 1º, 2º antes | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/indexa-broadcast-presidente-setembro-2026/> | <https://www.jota.info/eleicoes/eleicoes-2026/lula-recua-no-1o-turno-e-perde-vantagem-sobre-flavio-no-2o-mostra-indexa-broadcast> ; <https://www.folhape.com.br/politica/no-2o-turno-lula-tem-43-ante-42-de-flavio-bolsonaro-em-empate/512644/> |
| 30/09 | 27/09–29/09 | BR-00698/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/indexa-broadcast-no-2o-turno-lula-tem-43-flavio-42/> ; <https://www.cnnbrasil.com.br/eleicoes/indexa-broadcast-lula-tem-39-no-1o-turno-flavio-34/> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/indexa-broadcast-presidente-setembro-2026-2/> ; <https://www.tribunapr.com.br/noticias/brasil/indexa-lula-lidera-1o-turno-empata-com-flavio-2o-turno/> |
| 15/10 | 13/10–14/10 | BR-04629/2026 | 2º após | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/indexa-broadcast-presidente-outubro-2026-segundo-turno/> | <https://viva.com.br/politica/indexabroadcast-no-2-turno-flavio-bolsonaro-tem-44-ante-42-de-lula.html> ; <https://www.bahianoticias.com.br/noticia/322484-pesquisa-indexabroadcast-confirma-empate-tecnico-no-2-turno-flavio-tem-51-dos-votos-validos-e-lula-49> ; <https://timesbrasil.com.br/brasil/decisao-2026-flavio-bolsonaro-tem-51-dos-votos-validos-contra-49-de-lula-aponta-pesquisa-indexa-broadcast/> |
| 22/10 | 20/10–21/10 | BR-02348/2026 | 2º após | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/indexa-broadcast-presidente-outubro-2026-segundo-turno-2/> | <https://www.cnnbrasil.com.br/eleicoes/indexa-broadcast-flavio-tem-506-dos-votos-validos-lula-494/> ; <https://www.terra.com.br/noticias/eleicoes/pesquisas/flavio-tem-452-ante-441-de-lula-em-empate-tecnico-mostra-pesquisa-indexabroadcast,50389519238da1ef217383eab4485085d87yhufc.html> ; <https://www.cartacapital.com.br/cartaexpressa/pesquisa-indexa-mostra-flavio-bolsonaro-com-506-ante-494-de-lula/> |

### Instituto França (IFP)

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 03/10 | 28/09–02/10 | BR-02928/2026 | 1º, 2º antes | C | não | <https://static.poder360.com.br/uploads/2026/10/Pesquisa-Franca_Brasil_Presidente_1o-turno.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-4588-contra-4501-de-flavio-no-2o-turno-diz-pesquisa/> |
| 20/10 | 16/10–20/10 | BR-07896/2026 | 2º após | C | não | <https://static.poder360.com.br/uploads/2026/10/Pesquisa_Presidente_2T_Brasil_Out2026_Instituto_Franca.pdf> | <https://www.congressoemfoco.com.br/noticia/123423/flavio-tem-50-8-contra-49-2-de-lula-em-pesquisa-do-instituto-franca> ; <https://fanf1.com.br/2026/10/20/instituto-franca-flavio-tem-508-e-lula-492-indecisos-sao-quase-9/> |

### Instituto Phoenix

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 19/10 | 13/10–16/10 | BR-08809/2026 | 2º após | C | não | <https://www.phoenixnewsrondonia.com.br/pesquisa-do-instituto-phoenix-aponta-lula-com-51-3-e-flavio-bolsonaro-com-48-7-dos-votos-validos> | — |

### Instituto Ranking

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 20/10 | 14/10–16/10 | BR-00152/2026 | 2º após | C | não | <https://fonte83.com.br/politica/pesquisa-nacional-data-ranking-fonte83-lula-tem-504-e-flavio-496-dos-votos-validos-no-2o-turno/> | — |

### Ipespe

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 10/10 | 06/10–08/10 | BR-00933/2026 | 2º após | C | sim | <https://ipespe.org.br/wp-content/uploads/2026/10/TCK-CAMPANHA-01_-IPESPE-ABRAPEL_2T_-6-a-8-OUT-2026_vf.pdf> | <https://www.cnnbrasil.com.br/eleicoes/ipespe-flavio-tem-527-dos-votos-validos-no-2o-turno-lula-473/> ; <https://exame.com/brasil/pesquisa-presidente-2o-turno-flavio-bolsonaro-tem-49-e-lula-44-diz-ipespe/> ; <https://www.poder360.com.br/poder-eleicoes-2026/ipespe-confirma-poderdata-aya-e-da-flavio-com-527-e-lula-com-473/> ; <https://static.poder360.com.br/uploads/2026/10/pesquisa-ipespe-abrapel-10out2026.pdf> |
| 17/10 | 13/10–15/10 | BR-00223/2026 | 2º após | C | sim | <https://ipespe.org.br/wp-content/uploads/2026/10/TRK-CAMPANHA-02_-IPESPE-ABRAPEL_2T_-13-a-15-OUT-2026.pdf> | <https://www.cnnbrasil.com.br/eleicoes/ipespe-abrapel-flavio-tem-512-dos-votos-validos-no-2o-turno-lula-488/> ; <https://ipespe.org.br/pesquisa-ipespe-abrapel-2o-turno-tracking-da-campanha-weekly-tracking-rodada-02-13-a-15-de-outubro-de-2026/> ; <https://www.oliberal.com/politica/pesquisa-ipespe-flavio-tem-51-2-e-lula-48-8-vantagem-de-senador-cai-3-pontos-1.1183726> |

### MDA

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 11/08 | 05/08–09/08 | BR-06935/2026 | 1º, 2º antes | C | sim | <https://data.cnt.org.br/wp-content/uploads/2026/08/Relatorio-Pesquisa-CNT-de-Opiniao-R169-AGOSTO26_7486.pdf> | <https://data.cnt.org.br/en/destaques/pesquisa-cnt-de-opiniao-169-rodada/> ; <https://cnt.org.br/agencia-cnt/pesquisa-cntmda-atualiza-cenrio-eleitoral-e-acompanha-expectativas-dos-brasileiros> ; <https://www.cartacapital.com.br/politica/cnt-mda-lula-tem-13-pontos-de-vantagem-sobre-flavio-bolsonaro-no-1o-turno/> ; <https://data.cnt.org.br/wp-content/uploads/2026/10/Relatorio-Pesquisa-CNT-de-Opiniao-R172-OUTUBRO26.pdf> |
| 15/09 | 09/09–13/09 | BR-06902/2026 | 1º, 2º antes | C | sim | <https://data.cnt.org.br/wp-content/uploads/2026/09/Relatorio-Pesquisa-CNT-de-Opiniao-R170-SETEMBRO26.pdf> | <https://data.cnt.org.br/wp-content/uploads/2026/10/Relatorio-Pesquisa-CNT-de-Opiniao-R172-OUTUBRO26.pdf> ; <https://www.cnnbrasil.com.br/eleicoes/cnt-mda-lula-tem-473-e-flavio-40-no-2o-turno/> ; <https://data.cnt.org.br/en/sociedade/opiniao/pesquisa-cnt-de-opiniao-170-rodada/> ; <https://iclnoticias.com.br/cnt-mda-lula-tem-10-pontos-de-vantagem/> |
| 03/10 | 30/09–02/10 | BR-04756/2026 | 1º, 2º antes | C | sim | <https://data.cnt.org.br/wp-content/uploads/2026/10/Relatorio-Pesquisa-CNT-de-Opiniao-R171-OUTUBRO26-1.pdf> | <https://data.cnt.org.br/wp-content/uploads/2026/10/Relatorio-Pesquisa-CNT-de-Opiniao-R172-OUTUBRO26.pdf> ; <https://tvtnews.com.br/pesquisa-cnt-mda-na-vespera-da-eleicao-1-turno/> ; <https://www.tribunapr.com.br/eleicoes/2026/o-que-mostram-os-numeros-da-pesquisa-cnt-mda-para-presidente/> ; <https://data.cnt.org.br/en/destaques/pesquisa-cnt-de-opiniao-171-rodada/> |
| 16/10 | 13/10–15/10 | BR-00652/2026 | 2º após | C | sim | <https://data.cnt.org.br/wp-content/uploads/2026/10/Relatorio-Pesquisa-CNT-de-Opiniao-R172-OUTUBRO26.pdf> | <https://data.cnt.org.br/en/destaques/pesquisa-cnt-de-opiniao-172-rodada/> ; <https://cnt.org.br/agencia-cnt/pesquisa-cnt-mda-retrata-disputa-acirrada-no-2-turno> ; <https://noticias.uol.com.br/eleicoes/2026/10/16/cntmda-pesquisa-presidencial-2-turno.ghtm> |

### Nexus

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 03/08 | 31/07–02/08 | BR-02874/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/BTG-Nexus-nacional-3ago2026.pdf> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-3-de-agosto-de-2026/> ; <https://www.poder360.com.br/poder-eleicoes-2026/lula-e-flavio-estao-tecnicamente-empatados-no-2o-turno-diz-nexus/> |
| 10/08 | 07/08–09/08 | BR-08428/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/BTG-Nexus-Eleicoes2026-Brasil-10.ago_.2026.pdf> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-10-de-agosto-de-2026/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-no-1o-turno-lula-tem-40-e-flavio-35/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-lula-empata-com-flavio-e-caiado-no-2o-turno-2/> |
| 17/08 | 14/08–16/08 | BR-03317/2026 | 1º, 2º antes | C | sim | <https://www.canalmeio.com.br/wp-content/uploads/2026/08/BTG-Nexus-Eleicoes-2026-Rodada-10-versao-executiva-17.ago_.2026.pdf> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-17-de-agosto-de-2026/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-no-1o-turno-lula-tem-41-e-flavio-36/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-lula-empata-com-flavio-e-caiado-no-2o-turno-3/> |
| 24/08 | 21/08–23/08 | BR-09028/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/Pesquisa-BTG-Nexus-Eleicoes-24-ago-2026.pdf> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-24-de-agosto-de-2026/> ; <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-46-contra-45-de-flavio-no-2o-turno-diz-btg-nexus/> |
| 31/08 | 28/08–30/08 | BR-08900/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/BTG-Nexus-nacional-31ago2026.pdf> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-31-de-agosto-de-2026/> ; <https://noticias.uol.com.br/eleicoes/2026/08/31/pesquisa-presidencial-btgnexus-31-agosto.ghtm> |
| 08/09 | 04/09–07/09 | BR-06790/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/BTG-Nexus-nacional-8set2026.pdf> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-8-de-setembro-de-2026/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-lula-tem-39-no-1o-turno-flavio-tem-34/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-lula-tem-empate-tecnico-com-flavio-caiado-e-cury-no-2o-turno/> |
| 14/09 | 11/09–13/09 | BR-04076/2026 | 1º, 2º antes | C | sim | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-14-de-setembro-de-2026/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-lula-empata-com-flavio-e-cury-no-2-turno/> | <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-no-1-turno-lula-tem-40-flavio-36-e-cury-7/> ; <https://content.btgpactual.com/research/files/file/pt-BR/2026-09-28T010233.441_BTG_Nexus___Elei__es_2026___Rodada_16___vers_o_executiva__28_set_2026__6506.pdf> |
| 21/09 | 18/09–20/09 | BR-00485/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-2o-turno-lula-empata-com-caiado-e-tem-empate-tecnico-com-flavio/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-lula-tem-40-no-1o-turno-flavio-37-e-cury-6/> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-21-de-setembro-de-2026/> ; <https://content.btgpactual.com/research/files/file/pt-BR/2026-09-28T010233.441_BTG_Nexus___Elei__es_2026___Rodada_16___vers_o_executiva__28_set_2026__6506.pdf> |
| 28/09 | 25/09–27/09 | BR-07557/2026 | 1º, 2º antes | C | sim | <https://content.btgpactual.com/research/files/file/pt-BR/2026-09-28T010233.441_BTG_Nexus___Elei__es_2026___Rodada_16___vers_o_executiva__28_set_2026__6506.pdf> | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-28-de-setembro-de-2026/> ; <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-lula-empata-com-flavio-e-caiado-no-2o-turno-4/> |
| 13/10 | 10/10–12/10 | BR-07997/2026 | 2º após | C | sim | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-13-de-outubro-de-2026/> | <https://www.oliberal.com/politica/flavio-bolsonaro-tem-48-e-lula-45-em-empate-tecnico-aponta-pesquisa-btg-nexus-1.1181896> ; <https://www.dgabc.com.br/Noticia/4353493/flavio-tem-46-5-e-lula-45-9-mostra-btg-nexus-distancia-cai-e-empate-tecnico-permanece> ; <https://noticias.uol.com.br/eleicoes/2026/10/13/btgnexus-pesquisa-presidencial-segundo-turno.ghtm> |
| 19/10 | 16/10–18/10 | BR-04499/2026 | 2º após | C | sim | <https://www.nexus.fsb.com.br/estudos-divulgados/pesquisa-btg-nexus-de-intencao-de-votos-para-presidente-do-brasil-19-de-outubro-de-2026/> | <https://www.dgabc.com.br/Noticia/4353493/flavio-tem-46-5-e-lula-45-9-mostra-btg-nexus-distancia-cai-e-empate-tecnico-permanece> ; <https://sbtnews.sbt.com.br/noticia/politica/btg-nexus-flavio-tem-50-3-dos-votos-validos-lula-49-7> ; <https://www.jornaldocomercio.com/politica/2026/10/1267321-flavio-bolsonaro-tem-503-dos-votos-validos-e-lula-497-aponta-btg-nexus.html> |

### Palver

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 10/08 | 03/08–07/08 | BR-06596/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/pesquisa-presidente-palver-10ago2026.pdf> | <https://exame.com/brasil/lula-tem-44-contra-40-de-flavio-em-primeiro-turno-e-renan-santos-aparece-com-10-diz-palver/> |
| 09/09 | 04/09–07/09 | BR-05420/2026 | 1º, 2º antes | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/09/Pesquisa-Eleitoral-Palver-Onda-2-1.pdf> | — |
| 21/09 | 04/09–07/09 | BR-06100/2026 | 1º, 2º antes | C | não | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/09/Pesquisa-Eleitoral-Palver-Onda-3.pdf> | <https://static.poder360.com.br/uploads/2026/09/pesquisa-Palver-presidente-24set2026_compressed.pdf> ; <https://static.poder360.com.br/uploads/2026/09/pesquisa-presidencial-palver-setembro.pdf> |
| 21/09 | 15/09–18/09 | BR-00860/2026 | 1º, 2º antes | C | sim | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/09/Pesquisa-Eleitoral-Palver-Onda-3.pdf> | <https://www.jota.info/eleicoes/eleicoes-2026/palver-mostra-flavio-bolsonaro-numericamente-a-frente-de-lula-no-1o-turno-em-empate-tecnico> ; <https://static.poder360.com.br/uploads/2026/09/pesquisa-Palver-presidente-24set2026_compressed.pdf> |
| 24/09 | 20/09–23/09 | BR-09587/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/pesquisa-Palver-presidente-24set2026_compressed.pdf> | <https://www.cnnbrasil.com.br/eleicoes/palver-flavio-e-lula-empatam-no-1o-turno-em-43/> ; <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-48-contra-45-de-lula-no-2o-turno-diz-pesquisa/> ; <https://trademap.com.br/noticias/news-8341927> ; <https://www.cnnbrasil.com.br/eleicoes/palver-flavio-tem-48-das-intencoes-de-voto-no-2o-turno-lula-45/> |
| 29/09 | 24/09–27/09 | BR-02990/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/pesquisa-presidencial-palver-setembro.pdf> | <https://www.cnnbrasil.com.br/eleicoes/palver-flavio-tem-47-das-intencoes-de-voto-no-2o-turno-lula-45/> ; <https://www.cnnbrasil.com.br/eleicoes/palver-lula-e-flavio-empatam-com-44-das-intencoes-de-voto-no-1o-turno/> |
| 03/10 | 30/09–03/10 | BR-00198/2026 | 1º, 2º antes | P | sim | <https://exame.com/brasil/pesquisa-palver-para-presidente-flavio-bolsonaro-tem-47-e-lula-43-no-1o-turno/> | <https://terrabrasilnoticias.com/?p=496089> |
| 15/10 | 10/10–13/10 | BR-08028/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/pesquisa-palver-presidente-nacional-15out2026-1.pdf> | <https://viva.com.br/politica/palver-flavio-bolsonaro-tem-50-e-lula-49-em-empate-tecnico-no-2-turno.html> ; <https://www.poder360.com.br/poder-pesquisas/flavio-tem-50-e-lula-tem-49-a-10-dias-do-2o-turno-diz-palver/> |
| 21/10 | 18/10–20/10 | BR-04612/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/pesquisaPalver-presidente-21out2026_compressed-compactado.pdf> | <https://exame.com/brasil/pesquisa-palver-flavio-bolsonaro-tem-50-e-lula-48-no-2o-turno/> ; <https://www.terra.com.br/noticias/eleicoes/pesquisas/pesquisa-palver-flavio-bolsonaro-tem-50-e-lula-48-no-2-turno-candidatos-estao-em-empate-tecnico,6e99d76af4651a537219166fa78a4183lmte1cxs.html> ; <https://www.poder360.com.br/poder-pesquisas/flavio-tem-50-contra-48-de-lula-no-2o-turno-diz-pesquisa/> |

### PoderData

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 13/08 | 09/08–12/08 | BR-06868/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/Relatorio-PoderData-Eleitoral-12ago26-final.pdf> | <https://www.poder360.com.br/poderdata/lula-tem-46-contra-45-de-flavio-no-2o-turno-diz-poderdata-aya/> ; <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-21out26-2.pdf> |
| 27/08 | 23/08–26/08 | BR-04974/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/Relatorio-PoderData-Eleitoral-26ago26-1.pdf> | <https://www.poder360.com.br/poderdata/lula-tem-45-contra-44-de-flavio-no-2o-turno-diz-poderdata-aya/> ; <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-21out26-2.pdf> |
| 03/09 | 30/08–02/09 | BR-07561/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/Relatorio-PoderData-Eleitoral-2set26.pdf> | <https://www.poder360.com.br/poderdata/flavio-tem-45-e-lula-registra-44-no-2o-turno-diz-poderdata-aya/> ; <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-21out26-2.pdf> |
| 10/09 | 06/09–09/09 | BR-04914/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/Relatorio-PoderData-Eleitoral-9set26-1.pdf> | <https://www.poder360.com.br/poderdata/flavio-tem-47-e-lula-45-no-2o-turno-diz-poderdata-aya/> ; <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-21out26-2.pdf> |
| 17/09 | 13/09–16/09 | BR-00360/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/Relatorio-PoderData-Eleitoral-16set26.pdf> | <https://www.poder360.com.br/poderdata/poderdata-aya-lula-tem-37-contra-36-de-flavio-no-1o-turno/> ; <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-21out26-2.pdf> |
| 24/09 | 20/09–23/09 | BR-01739/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/Relatorio-PoderData-Eleitoral-23set26-final.pdf> | <https://www.poder360.com.br/poderdata/em-votos-validos-lula-tem-43-contra-42-de-flavio-no-1o-turno/> ; <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-21out26-2.pdf> |
| 03/10 | 30/09–02/10 | BR-03519/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-3out26-1.pdf> | <https://www.poder360.com.br/poderdata/lula-e-flavio-tem-46-cada-um-no-2o-turno-diz-poderdata-aya/> |
| 08/10 | 05/10–07/10 | BR-08134/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-8out26-final.pdf> | <https://www.poder360.com.br/poderdata/flavio-tem-53-contra-47-de-lula-no-2o-turno-diz-pesquisa-poderdata-aya/> |
| 13/10 | 10/10–12/10 | BR-01209/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-12out26-2.pdf> | <https://www.poder360.com.br/poderdata/lula-reage-e-vai-a-49-contra-51-de-flavio-diz-poderdata-aya/> ; <https://www.cnnbrasil.com.br/eleicoes/poderdata-aya-flavio-tem-51-dos-votos-validos-no-2o-turno-lula-49/> |
| 16/10 | 13/10–15/10 | BR-04258/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-15out26.pdf> | <https://www.poder360.com.br/poderdata/flavio-e-lula-empatam-em-50-dos-votos-validos-diz-poderdata-aya/> ; <https://noticias.uol.com.br/eleicoes/2026/10/16/poderdata-lula-flavio-bolsonaro-presidencia-republica-segundo-turno.ghtm> |
| 19/10 | 16/10–18/10 | BR-02586/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-18out26.pdf> | <https://www.poder360.com.br/poderdata/flavio-reage-e-vai-a-52-contra-48-de-lula-diz-poderdata-aya/> ; <https://www.poder360.com.br/poderdata/pesquisa-poderdata-aya-leia-os-resultados-de-lula-e-flavio-no-2o-turno-19out2026/> |
| 22/10 | 19/10–21/10 | BR-07926/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-21out26-2.pdf> | <https://www.poder360.com.br/poderdata/flavio-tem-51-e-lula-tem-49-dos-votos-validos-diz-poderdata-aya/> |

### Quaest

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 05/08 | 31/07–03/08 | BR-06591/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/quaest-lula-tem-44-e-flavio-39-das-intencoes-de-voto-no-2o-turno/> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/genial-quaest-presidente-agosto-2026/> | <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-44-ante-39-de-flavio-no-2o-turno-diz-quaest/> ; <https://www.cnnbrasil.com.br/eleicoes/quaest-lula-tem-39-no-primeiro-turno-flavio-30/> |
| 14/08 | 10/08–13/08 | BR-06773/2026 | 1º, 2º antes | C | sim | <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-43-ante-40-de-flavio-bolsonaro-no-2o-turno-diz-quaest/> | <https://www.cnnbrasil.com.br/eleicoes/quaest-lula-tem-38-e-flavio-31-das-intencoes-de-voto-1oturno/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/08/14/quaest-presidente-1o-turno-14-agosto.ghtml> |
| 02/09 | 30/08–01/09 | BR-07065/2026 | 1º, 2º antes | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-setembro-2026/> | <https://www.cnnbrasil.com.br/eleicoes/quaest-lula-tem-37-no-1o-turno-flavio-30-e-cury-10/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/02/quaest-presidente-2-setembro.ghtml> |
| 07/09 | 03/09–06/09 | BR-01720/2026 | 1º, 2º antes | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-setembro-2026-2/> | <https://www.cnnbrasil.com.br/eleicoes/quaest-no-1o-turno-lula-tem-36-flavio-29-e-cury-8/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/07/quaest-presidente-7-setembro.ghtml> ; <https://www.cnnbrasil.com.br/eleicoes/quaest-segundo-turno-setembro/> |
| 14/09 | 10/09–13/09 | BR-03607/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/quaest-flavio-aparece-numericamente-a-frente-de-lula-no-2o-turno-pela-1a-vez-na-campanha/> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-setembro-2026-3/> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-42-contra-40-de-lula-no-2o-turno-diz-quaest/> |
| 21/09 | 17/09–20/09 | BR-06004/2026 | 1º, 2º antes | C | sim | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-42-e-lula-41-em-2o-turno-diz-quaest/> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-setembro-2026-4/> ; <https://www.cnnbrasil.com.br/eleicoes/quaest-flavio-tem-42-no-2o-turno-lula-41/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/21/quaest-presidente-1o-turno-21-setembro.ghtml> |
| 28/09 | 24/09–27/09 | BR-06520/2026 | 1º, 2º antes | C | sim | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-setembro-2026-5/> | <https://static.poder360.com.br/uploads/2026/10/Pesquisa-Quaest_-Lula-tem-46-e-Flavio-Bolsonaro-45-_-G1.pdf> ; <https://www.poder360.com.br/poder-eleicoes-2026/lula-e-flavio-empatam-com-42-no-2o-turno-diz-quaest/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/28/quaest-presidente-1o-turno-28-setembro.ghtml> |
| 03/10 | 02/10–03/10 | BR-02197/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/10/Pesquisa-Quaest_-Lula-tem-46-e-Flavio-Bolsonaro-45-_-G1.pdf> | <https://www.cnnbrasil.com.br/eleicoes/quaest-2-turno/> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-outubro-2026/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/03/quaest-2o-turno-flavio-bolsonaro-44percent-lula-42percent.ghtml> ; <https://www.cnnbrasil.com.br/eleicoes/quaest-lula-tem-46-dos-votos-validos-no-1o-turno-flavio-45/> |
| 14/10 | 10/10–13/10 | BR-08729/2026 | 2º após | C | sim | <https://www.cnnbrasil.com.br/eleicoes/quaest-flavio-tem-46-no-2o-turno-lula-44/> | <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-outubro-2026-segundo-turno/> ; <https://www.poder360.com.br/poder-eleicoes-2026/saiba-como-estao-lula-e-flavio-nas-pesquisas-a-4-dias-do-2o-turno/> ; <https://www.bloomberglinea.com.br/brasil/quaest-flavio-tem-51-dos-votos-validos-no-segundo-turno-contra-49-de-lula/> ; <https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/14/quaest-presidente-14-outubro.ghtml> |
| 21/10 | 17/10–20/10 | BR-08535/2026 | 2º após | C | sim | <https://exame.com/brasil/pesquisa-para-presidente-quaest-flavio-bolsonaro-tem-45-e-lula-44-a-4-dias-do-2o-turno/> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-45-contra-44-de-lula-no-2o-turno-diz-quaest/> ; <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/quaest-presidente-outubro-2026-segundo-turno-2/> ; <https://oglobo.globo.com/blogs/pulso/post/2026/10/pesquisa-quaest-flavio-tem-45percent-e-lula-marca-44percent-distancia-diminui-a-quatro-dias-da-eleicao.ghtml> |

### Real Time Big Data

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 01/09 | 27/08–31/08 | BR-03490/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/Pesquisa-presidencial-Brasil-Real-Time-Big-Data-1-set-2026.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/lula-e-flavio-bolsonaro-empatam-com-44-no-2o-turno-diz-pesquisa/> ; <https://www.bloomberglinea.com.br/brasil/real-time-big-data-lula-e-flavio-aparecem-empatados-no-segundo-turno-com-44/> ; <https://diariodocomercio.com.br/politica/lula-flavio-pesquisa-votos/> ; <https://www.oliberal.com/politica/real-time-big-data-lula-tem-38-dos-votos-totais-no-1-turno-flavio-marca-30-e-cury-11-1.1163497> |
| 24/09 | 19/09–23/09 | BR-04202/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/real-time-big-data-flavio-tem-45-no-2o-turno-lula-44/> ; <https://www.cnnbrasil.com.br/eleicoes/real-time-big-data-lula-tem-41-no-1o-turno-flavio-37/> | <https://static.poder360.com.br/uploads/2026/10/Presidencial-BR-09503-2026-Out26.pdf> ; <https://static.poder360.com.br/uploads/2026/10/Presidencial-BR-02952-2026-Out26.pdf> |
| 01/10 | 26/09–30/09 | BR-09503/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/10/Presidencial-BR-09503-2026-Out26.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-46-no-2o-turno-contra-45-de-lula-diz-pesquisa/> ; <https://www.cnnbrasil.com.br/eleicoes/real-time-big-data-flavio-tem-46-no-2o-turno-lula-45/> ; <https://www.dgabc.com.br/Noticia/4353712/real-time-big-data-flavio-tem-52-dos-votos-validos-e-lula-48-em-empate-tecnico> ; <https://www.cnnbrasil.com.br/eleicoes/real-time-big-data-lula-tem-43-no-1o-turno-flavio-39/> |
| 20/10 | 15/10–19/10 | BR-02952/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/Presidencial-BR-02952-2026-Out26.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-48-contra-45-de-lula-diz-real-time-big-data/> ; <https://www.bloomberglinea.com.br/brasil/real-time-big-data-flavio-tem-52-dos-votos-validos-e-lula-48-a-cinco-dias-do-2-turno/> ; <https://www.infomoney.com.br/politica/real-time-big-data-flavio-tem-52-dos-votos-validos-e-lula-48-no-2o-turno/> ; <https://www.riotimesonline.com/real-time-big-data-poll-flavio-52-lula-48-runoff-2026/> |

### Veritá

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 21/08 | 16/08–20/08 | BR-04006/2026 | 1º, 2º antes | C | não | <https://pleno.news/brasil/eleicoes-2026/verita-flavio-bolsonaro-venceria-lula-em-disputa-no-2o-turno.html> ; <https://tribunadejundiai.com.br/politica/eleicoes-2026/pesquisa-eleitoral-2026-flavio-bolsonaro-lula-segundo-turno/> | <https://terrabrasilnoticias.com/?p=489895> |
| 06/09 | 01/09–04/09 | BR-09426/2026 | 1º, 2º antes | C | não | <https://midiamax.com.br/brasil/2026/pesquisa-aponta-flavio-bolsonaro-485-intencao-votos-ganharia-lula-2o-turno/> ; <https://tribunadoplanalto.com.br/verita-aponta-empate-entre-flavio-e-lula-cury-aparece-em-terceiro-com-122/> | — |
| 30/09 | 20/09–25/09 | vários (ver nota) | 1º | P | não | <https://revistaoeste.com/politica/verita-flavio-lula-1-turno/> | <https://www.bahianoticias.com.br/noticia/322563-pesquisa-verita-aponta-flavio-vencendo-com-511-e-lula-ficando-em-489-na-simulacao-de-segundo-turno> ; <https://www.bahianoticias.com.br/noticia/322025-apenas-quatro-de-11-institutos-previram-vitoria-de-flavio-confira-quais-pesquisas-acertaram-e-as-que-mais-erraram> |
| 05/10 | 26/09–02/10 | vários (ver nota) | 2º após | P | não | <https://pleno.news/brasil/eleicoes-2026/pesquisa-verita-flavio-amplia-vantagem-sobre-lula-em-2o-turno.html> | — |
| 17/10 | 12/10–16/10 | BR-01107/2026 | 2º após | P | sim | <https://www.cnnbrasil.com.br/eleicoes/verita-flavio-tem-511-dos-votos-validos-no-2o-turno-lula-489/> | <https://www.bahianoticias.com.br/noticia/322563-pesquisa-verita-aponta-flavio-vencendo-com-511-e-lula-ficando-em-489-na-simulacao-de-segundo-turno> ; <https://timesbrasil.com.br/eleicoes-2026/decisao-2026-flavio-bolsonaro-tem-511-e-lula-489-aponta-pesquisa-verita/> ; <https://www.poder360.com.br/poder-pesquisas/saiba-como-estao-lula-e-flavio-nas-pesquisas-a-3-dias-da-eleicao/> |
| 21/10 | 15/10–19/10 | BR-06396/2026 | 2º após | C | sim | <https://revistaforum.com.br/politica/verita-aproximou-resultado-1o-turno-lula/> | <https://www.cnnbrasil.com.br/eleicoes/verita-flavio-tem-507-dos-votos-validos-no-2o-turno-lula-493/> ; <https://timesbrasil.com.br/eleicoes-2026/decisao-2026-flavio-tem-507-e-lula-493-dos-votos-validos-mostra-pesquisa-verita/> |

### Vox Brasil

| Divulgação | Campo | Registro TSE | Turnos no CSV | Status | Índice | Fonte primária | Outras fontes |
|---|---|---|---|---|---|---|---|
| 29/08 | 25/08–27/08 | BR-05519/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/08/RELATORIO-TSE-VOX-BRASIL-NACIONAL-6-29-08-2026-TSE.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-e-lula-empatam-no-2o-turno-diz-pesquisa-3/> ; <https://www.cnnbrasil.com.br/eleicoes/vox-brasil-flavio-tem-451-e-lula-445-no-2o-turno/> ; <https://www.cnnbrasil.com.br/eleicoes/vox-brasil-lula-tem-371-e-flavio-348-no-1o-turno/> |
| 29/09 | 26/09–28/09 | BR-00895/2026 | 1º, 2º antes | C | sim | <https://static.poder360.com.br/uploads/2026/09/pesquisa-vox-nacional-29set2026.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-452-contra-447-de-lula-no-2o-turno-diz-pesquisa/> ; <https://www.cnnbrasil.com.br/eleicoes/vox-flavio-tem-452-das-intencoes-de-voto-no-2o-turno-lula-447/> ; <https://www.cnnbrasil.com.br/eleicoes/vox-lula-tem-411-das-intencoes-de-voto-no-1o-turno-flavio-378/> |
| 02/10 | 29/09–01/10 | BR-00148/2026 | 1º, 2º antes | C | sim | <https://www.cnnbrasil.com.br/eleicoes/vox-flavio-registra-482-no-2o-turno-lula-452/> | <https://midiamax.com.br/brasil/2026/flavio-tem-482-contra-452-lula-2o-turno-diz-pesquisa-vox-brasil/> ; <https://www.bnewssaopaulo.com.br/amp/noticias/politica/vox-brasil-lula-e-flavio-aparecem-tecnicamente-empatados-no-2-turno.html> |
| 09/10 | 05/10–07/10 | BR-09623/2026 | 2º após | C | sim | <https://static.poder360.com.br/uploads/2026/10/pesquisa-vox-brasil-9out2026.pdf> | <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-442-e-flavio-427-no-2o-turno-diz-vox-brasil/> ; <https://www.cnnbrasil.com.br/eleicoes/vox-lula-tem-442-das-intencoes-de-voto-no-2o-turno-flavio-427/> |
| 18/10 | 15/10–17/10 | BR-04332/2026 | 2º após | C | sim | <https://www.metropoles.com/brasil/vox-brasil-com-empate-tecnico-lula-tem-464-e-flavio-bolsonaro-446> | <https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-51-contra-49-de-flavio-em-votos-validos-diz-vox/> ; <https://timesbrasil.com.br/eleicoes-2026/decisao-2026-lula-tem-51-dos-votos-validos-contra-49-de-flavio-aponta-pesquisa-vox-brasil/> ; <https://www.poder360.com.br/poder-eleicoes-2026/saiba-como-estao-lula-e-flavio-nas-pesquisas-a-4-dias-do-2o-turno/> |

**Veritá, registros por UF.**

- Campo 20/09–25/09 (divulgada 30/09): Registros: AC BR-03117; AL BR-03222; AM BR-04439; AP BR-07097; BA BR-02546; CE BR-09888; DF BR-06774; ES BR-04515; GO BR-08745; MA BR-02757; MG BR-09269; MS BR-03436; MT BR-04418; PA BR-01684; PB BR-05105; PE BR-06969; PI BR-05209; PR BR-06446; RJ BR-05600; RN BR-02817; RO BR-03566; RR BR-05265; RS BR-04324; SC BR-07078; SE BR-04761; SP BR-04131; TO BR-00467 (todos /2026).
- Campo 26/09–02/10 (divulgada 05/10): Registros (texto da Pleno News): BR-02268, BR-09649, BR-08027, BR-05342, BR-029816 (assim no texto), BR-08782, BR-08274, BR-01346, BR-05946, BR-01770, BR-09434, BR-02068, BR-06095, BR-09847, BR-03172, BR-06091, BR-02454, BR-01993, BR-00437, BR-05406, BR-02958, BR-09126, BR-01717, BR-00261, BR-04355, BR-01487 e BR-09668/2026.

## Divergências entre fontes

Em todas, o CSV usa a fonte primária (relatório do instituto) ou, sem ela, a fonte indicada. Textos registrados na conferência:

### American Analytics

- **23/09 (2º turno, campo 15/09–20/09)**: Mesmas do registro de 1º turno (número do registro grafado BR-032587/26 nas matérias; margem 2,2 no TSE x 2,5 na divulgação; divulgação prevista 21/09 x publicada 23/09).
- **23/09 (1º turno, campo 15/09–20/09)**: Registro: Times Brasil e Poder360 grafam 'BR-032587/26'; dados abertos do TSE e Correio Braziliense (21/09) trazem BR-02587/2026 (adotado). Margem: registro no TSE/Correio Braziliense dizem 2,2 p.p.; Times Brasil e Poder360 (divulgação dos resultados) dizem 2,5 p.p. (adotado). Data: o TSE registra divulgação prevista para 21/09/2026, mas os resultados só aparecem publicados em 23/09/2026 (Times Brasil 09h00; Poder360 14h48).

### AtlasIntel

- **31/08 (1º turno, campo 25/08–30/08)**: Índice da Wikipédia: demais = 4.0; Congresso em Foco lista Marçal 1,9 + Samara 0,9 + Rui Costa Pimenta 0,1 + Wilson Grassi 0,1 = 3,0, e a série 'Outros' do relatório Atlas de 03/out marca 3% em Ago/26. Ficou 3.0.
- **10/09 (1º turno, campo 04/09–09/09)**: A série temporal do relatório de 03/out rotula Cury com 6,5% em '09 Set'; o relatório desta rodada e a CNN dizem 6,6%. Ficou 6.6.

### DataTrends

- **11/10 (2º turno, campo 07/10–09/10)**: No próprio PDF, o painel-resumo (p. 4) traz 'Branco/Nulo 5% | NS/NR 2%' e válidos arredondados 53/47; a lâmina do resultado (p. 12) traz Nenhum/Branco/Nulo 5% e NS/NR 1%, e a de válidos 53,1/46,9 (usados aqui; a Times Brasil também dá 5% e 1%).

### Datafolha

- **21/08 (2º turno, campo 18/08–19/08)**: Campo: índice e Gazeta 18-20/08; relatório Datafolha e Poder360 18-19/08 (adotado).
- **21/08 (1º turno, campo 18/08–19/08)**: Campo: índice Wikipédia e Gazeta do Povo dizem 18-20/08; relatório Datafolha (série histórica), CNN e Poder360 dizem 18-19/08 (adotado). Brancos/nulos: leitura da CNN trouxe 8%, mas o relatório Datafolha traz 6% (soma fecha 100 com 6%); adotado 6%. Gazeta destaca o cenário com Pablo Marçal (Lula 39, Flávio 32, Caiado 5, Renan 4, Zema 3, Marçal 2, Cury 2, branco/nulo 7, indecisos 4).
- **03/09 (2º turno, campo 01/09–02/09)**: Campo: Gazeta 1º a 3/09; relatório Datafolha 01-02/09 (adotado).
- **03/09 (1º turno, campo 01/09–02/09)**: Campo: CNN e Gazeta dizem 1º a 3/09; relatório Datafolha e índice dizem 01-02/09 (adotado). Gazeta tem resumo inconsistente (Lula 38 x Flávio 32) e cenário com Marçal (Lula 39, Flávio 32, Cury 7, Renan 4, Caiado 4, Zema 2, Marçal 2, Samara 1, branco/nulo 6, indecisos 3).
- **11/09 (1º turno, campo 08/09–10/09)**: Gazeta traz também cenário com Marçal (Lula 39, Flávio 33, Cury 5, Caiado 4, Renan 3, Marçal 2, Zema 2, branco/nulo 6, indecisos 3).
- **17/09 (2º turno, campo 15/09–17/09)**: Campo: índice 15-16/09; relatório 15-17/09 (adotado). Amostra: relatório 2.001; índice 2.002.
- **17/09 (1º turno, campo 15/09–17/09)**: Campo: índice diz 15-16/09; Gazeta se contradiz (15-16 e 15-17); relatório Datafolha e CNN dizem 15-17/09 (adotado). Amostra: relatório Datafolha 2.001 entrevistas (adotado); CNN, Gazeta e índice dizem 2.002.
- **24/09 (2º turno, campo 22/09–23/09)**: Campo: índice 22-24/09; CNN e Gazeta 22-23/09 (adotado).
- **24/09 (1º turno, campo 22/09–23/09)**: Campo: índice diz 22-24/09; CNN e Gazeta dizem 22-23/09 (adotado).
- **01/10 (2º turno, campo 29/09–01/10)**: Campo: índice 28-30/09; g1/Folha 29/09-01/10 (adotado).
- **01/10 (1º turno, campo 29/09–01/10)**: Campo: índice diz 28-30/09; Gazeta diz 28/09 a 01/10; g1 ('entre os dias 29 e 1º de outubro') e Folha ('de terça-feira (29) a esta quinta (1º)') dizem 29/09-01/10 (adotado). g1 grafa o registro como 'BR-BR-08039/2026'. Números da Gazeta (totais e válidos) iguais aos de g1/Folha.
- **03/10 (2º turno, campo 02/10–03/10)**: Campo: Poder360 2-3/10; Gazeta 3/10. CNN com metadados errados (ver registro de 1º turno).
- **03/10 (1º turno, campo 02/10–03/10)**: Campo: Poder360 diz 2 a 3/10 (adotado); Gazeta diz '3 de outubro'; índice '3 Oct'. A matéria da CNN (cnnbrasil.com.br/eleicoes/datafolha-2-turno/) traz metadados de outra rodada (BR-03669/2026, 2.002 eleitores, 'entre 1º e 3 de outubro') — erro da CNN, descartado.
- **15/10 (2º turno, campo 13/10–14/10)**: Campo: Poder360 e Gazeta dizem 13-14/10 (adotado); Diário do Nordeste, Estado de Minas (texto pré-divulgação: 'entre terça-feira (13/10) e esta quinta') e índice dizem 13-15/10. Contratante: Poder360, Estado de Minas e Gazeta citam só a Folha (Folha da Manhã, 'recursos próprios', R$ 384.552); Diário do Nordeste diz Folha e TV Globo. Ref do índice com data 2026-10-08 e título em inglês, mas a pesquisa é de 15/10.
- **22/10 (2º turno, campo 20/10–22/10)**: Contratante: Poder360 e Gazeta dizem Folha e Globo (custo R$ 384.552); Terra cita só a Folha. Amostra: Gazeta diz 2.154 (provável troca com a Quaest); Poder360 e Terra dizem 2.520 (adotado).

### Futura

- **11/09 (1º turno, campo 04/09–10/09)**: Augusto Cury: CNN diz 6,9%; o índice da Wikipédia diz 6,4%. Com 6,9 a soma dá 100,4%; com 6,4, 99,9% (as outras rodadas da Futura somam 99,9-100,1), o que sugere possível erro de digitação na CNN. O PDF desta rodada não foi localizado. Mantido o número da CNN (fonte lida).
- **24/09 (2º turno, campo 19/09–23/09)**: Índice da Wikipédia: campo 18-24 set e margem ±2,4 pp; relatório da Futura, Poder360 e CNN: campo 19-23 set e margem ±2,2 pp.
- **30/09 (1º turno, campo 25/09–29/09)**: O subtítulo da matéria de 1º turno da CNN cita campo de 19 a 23 de setembro (datas da rodada anterior); a metodologia da mesma matéria, a de 2º turno e o registro próprio (BR-01122/2026) indicam 25 a 29 de setembro.
- **03/10 (1º turno, campo 02/10–03/10)**: O índice da Wikipédia põe bnu = 2,6, que é só brancos/nulos; faltam os 2,4% de indecisos (a linha do índice soma 97,6%). Pelo relatório, brancos/nulos 2,6 + indecisos 2,4 = 5,0. A data de divulgação não consta no índice; o relatório e a Trademap indicam sábado, 03/10/2026.
- **16/10 (2º turno, campo 14/10–15/10)**: Datas de campo: a capa do relatório diz 13 a 15 de outubro, a página de metodologia, a CNN e o Poder360 dizem 14 a 15 (a linha de apoio do Poder360 tem o erro '14 a 15 de setembro'). Usado 14-15 out.

### Gerp

- **09/09 (1º turno, campo 03/09–08/09)**: Contratante: CNN Brasil diz 'contratada pela AESP Rádio'; Tribuna PR diz 'contratada pelo próprio instituto'.
- **09/09 (2º turno, campo 03/09–08/09)**: Contratante: AESP Rádio (CNN) x próprio instituto (Tribuna PR).
- **29/09 (1º turno, campo 24/09–28/09)**: Tribuna PR publica como 'votos válidos' Flávio 44, Lula 42, Cury 5, Caiado 3, Renan 3, Samara 1, Zema 1, Rui Costa Pimenta 1; o Poder360 publica os totais (Flávio 42, Lula 40, ..., Rui Costa Pimenta 0%, 'nenhum' 2, 'não sabe' 3). As duas leituras são compatíveis (totais x válidos); 'demais' válidos = Samara 1 + Rui Costa Pimenta 1 segundo a Tribuna PR.
- **13/10 (2º turno, campo 08/10–12/10)**: Índice da Wikipédia: brancos/nulos/indecisos = 3; o relatório da Gerp traz 'nenhum deles' 1% + 'não sabe' 3% = 4 (soma pode variar 99-101%).
- **16/10 (2º turno, campo 14/10–16/10)**: O resumo automático (IA) da Revista Oeste no topo da matéria repete os números da rodada anterior (55/45 e 53/44); o texto da própria matéria e o PDF trazem 50/45 totais e 52/48 válidos.
- **21/10 (2º turno, campo 19/10–21/10)**: Índice da Wikipédia: brancos/nulos/indecisos = 5; Gazeta do Povo e Tribuna PR trazem 'nenhum deles' 2% + 'não sabe' 2% = 4.

### Indexa

- **26/08 (1º turno, campo 20/08–23/08)**: Contratante: CNN (matéria do 2º turno) diz 'recursos do próprio instituto'; Gazeta do Povo diz Agência Estado S.A.; trademap/CartaCapital dizem Broadcast. Usado Agência Estado (Broadcast).
- **26/08 (2º turno, campo 20/08–23/08)**: trademap agrupa 'brancos, nulos ou nenhum' = 11% (5 brancos/nulos + 6 não votariam). Contratante: esta matéria da CNN diz 'recursos do próprio instituto'; Gazeta do Povo diz Agência Estado S.A.
- **30/09 (1º turno, campo 27/09–29/09)**: Índice da Wikipédia: bnu 11 (4+7) — omite os 4% que não votariam.
- **15/10 (2º turno, campo 13/10–14/10)**: Na divulgação seguinte (22/10), Terra/Estadão citam os números desta rodada com decimais: Flávio 43,6% e Lula 42,1% (outras matérias dizem 42,3% para Lula). Registrados aqui os inteiros publicados em 15/10.

### Instituto França (IFP)

- **03/10 (1º turno, campo 28/09–02/10)**: Wikipédia PT dá campo 29/09–02/10; relatório do instituto, Poder360 e TSE dão 28/09–02/10 (adotado). O TSE registra divulgação em 02/10/2026; a matéria do Poder360 e o PDF do relatório são de 03/10/2026 (adotado).
- **03/10 (2º turno, campo 28/09–02/10)**: Mesmas do registro de 1º turno (campo 28/09 x 29/09 na Wikipédia PT; divulgação 02/10 no TSE x 03/10 na publicação).

### Instituto Phoenix

- **19/10 (2º turno, campo 13/10–16/10)**: A matéria grafa o registro como 'TRE-RO nº 08809-2026'; nos dados abertos do TSE é BR-08809/2026 (nacional, empresa J J Coelho / Instituto Phoenix & Associados). O TSE registra divulgação em 18/10/2026; a matéria é de 19/10/2026 (adotado).

### Instituto Ranking

- **20/10 (2º turno, campo 14/10–16/10)**: O TSE registra divulgação em 19/10/2026; a matéria do Fonte83 (parceiro/contratante) é de 20/10/2026 (adotado). Margem: 2,15 p.p. na metodologia; o texto principal fala em 'dois pontos'.

### Ipespe

- **10/10 (2º turno, campo 06/10–08/10)**: Índice da Wikipédia: brancos/nulos/indecisos = 7; o relatório traz branco/nulo 5 + não sabe 3 = 8 (a soma dos totais dá 101 por arredondamento). Modo de coleta: CNN Brasil e Midiamax falam em 'recrutamento digital aleatório'; o relatório do Ipespe diz 'entrevistas realizadas através do Sistema CATI IPESPE, com equipe de pesquisadores' (telefone). Usado o do relatório.
- **17/10 (2º turno, campo 13/10–15/10)**: Modo de coleta: CNN Brasil e Midiamax falam em 'recrutamento digital aleatório'; o relatório do Ipespe diz 'entrevistas realizadas através do Sistema CATI IPESPE, com equipe de pesquisadores' (telefone). Usado o do relatório.

### MDA

- **11/08 (1º turno, campo 05/08–09/08)**: CartaCapital lista 'Outros: 0,9%'; no relatório 0,9% é só a barra 'Outros', à parte de Samara Martins (1,6%) e Rui Costa Pimenta (0,9%). 'demais' = 1,6 + 0,9 + 0,9 = 3,4.
- **15/09 (1º turno, campo 09/09–13/09)**: O Povo publicou Lula 40,6%; o relatório da CNT/MDA (p. 8) e o ICL trazem 40,5%. Adotado 40,5.
- **03/10 (2º turno, campo 30/09–02/10)**: O índice da Wikipédia arredonda para Lula 47 / Flávio 43 / bnu 10; o relatório traz 47,3 / 43,1 / branco-nulo 7,6 / indeciso 1,9 (bnu somado 9,5).
- **03/10 (1º turno, campo 30/09–02/10)**: Campo: CNN Brasil e o índice da Wikipédia dizem 29/09 a 02/10; o relatório diz 30/09 a 02/10 (30/09: 38%, 01/10: 42%, 02/10: 20%). Amostra: CNN Brasil e TVT News dizem 2.002; relatório, Estado de Minas e Agência CNT dizem 2.007. TVT News publicou Flávio 38,1%; relatório traz 38,0%. Adotado o relatório.

### Nexus

- **08/09 (1º turno, campo 04/09–07/09)**: A manchete da CNN (Lula 39%, Flávio 34%) usa o cenário com Pablo Marçal; a Nexus trata o cenário sem Marçal (Flávio 35%) como principal, e é ele que entra na série histórica do relatório de 28/09.
- **14/09 (1º turno, campo 11/09–13/09)**: O título da CNN (Lula 40%, Flávio 36%, Cury 7%) é o cenário COM Pablo Marçal. A página da Nexus chama de 'principal cenário' o sem Marçal (Lula 42%, Flávio 37%), que é o da tabela do índice; a série histórica do relatório de 28/09 também registra 42%/37% para 14/set. As duas leituras estão certas, cada uma para um cenário; o principal é 42/37.
- **13/10 (2º turno, campo 10/10–12/10)**: Amostra: o índice da Wikipédia diz 2.000; Nexus e O Liberal dizem 2.002. Válidos: divulgados como 52% x 48% em 13/10; na divulgação de 19/10 a Nexus converteu a série para uma casa decimal e matérias (SBT News, Jornal do Comércio) citam esta rodada como Flávio 51,6% x Lula 48,4%.

### Palver

- **10/08 (1º turno, campo 03/08–07/08)**: Fim do campo: relatório da Onda 1 e Exame dizem 07/08; a tabela de ondas dos relatórios posteriores diz 03/08–06/08. Margem: ±3% no relatório da Onda 1; ±2,9% na tabela de ondas posterior.
- **09/09 (1º turno, campo 04/09–07/09)**: Margem: tabela de amostra da íntegra ±2,5%; texto de metodologia fala em máxima de ±3,0 calculada preliminarmente; índice da Wikipédia ±3.
- **21/09 (1º turno, campo 15/09–18/09)**: Índice da Wikipédia: campo 15–20 Sep e margem ±3; a íntegra diz 15/09–18/09 e ±2,8% (Revista Oeste também cita 15 a 18/09 e 2,8 pp).
- **24/09 (1º turno, campo 20/09–23/09)**: Margem: íntegra e Poder360 dizem ±2,5; CNN e índice da Wikipédia dizem 3 pp. Poder360 agrupa 'Outros' 2% (Zema 1 + outros 1) e omite Caiado.
- **24/09 (2º turno, campo 20/09–23/09)**: Margem: íntegra e Poder360 dizem ±2,5; CNN e índice da Wikipédia dizem 3 pp.
- **03/10 (1º turno, campo 30/09–03/10)**: Índice da Wikipédia põe demais 0 e bnu 0; a Exame diz apenas 'abaixo de 1%' para Zema, demais, brancos/nulos/não votaria e indecisos; Terra Brasil Notícias dá Zema 0%.
- **21/10 (2º turno, campo 18/10–20/10)**: Poder360 diz campo de 16 a 20/10; a íntegra, Exame e Terra dizem 18 a 20/10.

### PoderData

- **19/10 (2º turno, campo 16/10–18/10)**: Índice da Wikipédia: brancos+nulos+indecisos = 5; relatório PDF: branco/nulo 4 + não sabe 2 = 6 (soma publicada 101% por arredondamento). Ficou o PDF.

### Quaest

- **02/09 (1º turno, campo 30/08–01/09)**: A CNN destaca o cenário com Pablo Marçal (Lula 37, Flávio 30, Cury 10, Renan 3, Caiado 1, Zema 1, Marçal 1, Samara 1, branco/nulo 7, indecisos 10). Adotado o cenário sem Marçal, que é o do título do g1 (Lula 37, Flávio 29, Cury 10) e o do índice.
- **02/09 (2º turno, campo 30/08–01/09)**: Amostra: índice diz 2.005 neste cenário; fontes dizem 2.004 (adotado).
- **07/09 (1º turno, campo 03/09–06/09)**: Cenário com Marçal (CNN e Gazeta): Lula 36, Flávio 29, Cury 8, Caiado 3, Renan 3, Zema 2, Marçal 1, Samara 1, branco/nulo 8, indecisos 9. Adotado o cenário sem Marçal (bate com o índice). Campo: subtítulo da CNN diz 4-7/09, a metodologia da CNN e a Gazeta dizem 3-6/09 (adotado).
- **03/10 (2º turno, campo 02/10–03/10)**: A Gazeta do Povo registra correção: a versão inicial trocava os percentuais de Lula e Flávio no 2º turno.
- **14/10 (2º turno, campo 10/10–13/10)**: Válidos: Bloomberg Línea atribui à Quaest 51% (Flávio) x 49% (Lula); o Poder360 diz que recalculou os válidos (51,1 x 48,9); CNN e Gazeta não trazem válidos. Não confirmei divulgação de válidos pela Quaest/Globo, por isso ficaram null. Gazeta registra correção (percentuais de Lula e Flávio estavam invertidos).

### Real Time Big Data

- **01/09 (2º turno, campo 27/08–31/08)**: Bloomberg Línea chama os 44% de 'votos válidos'; no PDF (p. 22) são votos totais, com nulo/branco 9% e NS/NR 3%.
- **01/09 (1º turno, campo 27/08–31/08)**: Diário do Comércio e O Liberal publicaram NS/NR 2% neste cenário; o PDF do instituto (p. 15) traz 3% (a soma fecha 100). Adotado o PDF.
- **20/10 (2º turno, campo 15/10–19/10)**: O título da ref. do índice (Rio Times, 'Flávio 52% and Lula 48%') refere-se a votos válidos; os totais são 48/45, como na tabela do índice.

### Veritá

- **17/10 (2º turno, campo 12/10–16/10)**: Válidos: CNN Brasil e Poder360 arredondam para 51,1 x 48,9; Bahia Notícias traz 51,07 x 48,93 (usado aqui). Times Brasil apresenta 51,1/48,9 como se fossem votos totais ('totalizam 100%'). Totais do índice (Lula 47,7, Flávio 49,7, brancos/nulos/indecisos 2,6) não foram achados em nenhuma fonte.

### Vox Brasil

- **29/08 (1º turno, campo 25/08–27/08)**: O lide do Poder360 cita campo 'de 23 a 29 de agosto'; a ficha técnica do PDF traz 25/08 a 27/08 (registro em 23/08, divulgação 29/08). Adotado o PDF.
- **29/09 (2º turno, campo 26/09–28/09)**: Registro: a CNN Brasil publicou BR-07553/2026; o PDF do instituto (capa e ficha técnica) e o Poder360 trazem BR-00895/2026. Adotado o PDF.
- **29/09 (1º turno, campo 26/09–28/09)**: Lula: o índice da Wikipédia traz 41,4; o PDF, a CNN Brasil (inclusive no título) e o Poder360 trazem 41,1. Registro: a CNN Brasil publicou BR-07553/2026; o PDF do instituto (capa e ficha técnica) e o Poder360 trazem BR-00895/2026. Adotado o PDF.

### Índice da Wikipédia (resumo)

O índice tinha erros pontuais, todos corrigidos nos CSVs:

- **Datas de campo:** Datafolha 18–19/08, 15–17/09, 22–23/09 e 29/09–01/10; Palver Onda 3; Futura 19–23/09; MDA 30/09–02/10.
- **Números:** Vox 29/09 (Lula 41,1, não 41,4); Atlas 25–30/08 (demais 3,0).
- **Brancos, nulos e indecisos somados:** Futura 02–03/10, Indexa, Gerp, Ipespe 06–08/10, PoderData 16–18/10.
- **Amostras:** Nexus 10–12/10 (2.002) e Quaest 30/08 (2.004).
- **Fontes ruins:** URLs com `?utm_source=chatgpt.com` e títulos em inglês em algumas referências de outubro (PoderData, Nexus, Alfa, Real Time). As matérias existem e foram conferidas.
- **Sem fonte:** os totais da Veritá 12–16/10 não estão em nenhuma fonte e ficaram em branco.

## Cenários e pesquisas não incluídos nos CSVs

**Cenários alternativos de 1º turno.** O CSV fica com o cenário principal (lista oficial, sem Pablo Marçal, ou a lista completa). Os alternativos foram conferidos e estão abaixo:

- Nexus 21–23/08, cenário 2 com Pablo Marçal (BR-09028/2026): Lula 40, Flávio 34, Cury 2, Renan 3, Caiado 5, Zema 2, demais 7, brancos/nulos 4, indecisos 3. Fonte: <https://static.poder360.com.br/uploads/2026/08/Pesquisa-BTG-Nexus-Eleicoes-24-ago-2026.pdf>
- Nexus 28–30/08, cenário 2 com Pablo Marçal (BR-08900/2026): Lula 37, Flávio 31, Cury 11, Renan 3, Caiado 6, Zema 2, demais 5, brancos/nulos 3, indecisos 2. Fonte: <https://static.poder360.com.br/uploads/2026/08/BTG-Nexus-nacional-31ago2026.pdf>
- Nexus 04–07/09, cenário 2 com Pablo Marçal (manchete da CNN: 39 x 34) (BR-06790/2026): Lula 39, Flávio 34, Cury 9, Renan 4, Caiado 4, Zema 2, demais 4, brancos/nulos 3, indecisos 1. Fonte: <https://static.poder360.com.br/uploads/2026/09/BTG-Nexus-nacional-8set2026.pdf>
- Nexus 11–13/09, cenário com Pablo Marçal (manchete da CNN: 40 x 36, Cury 7) (BR-04076/2026): Lula 40, Flávio 36, Cury 7, Renan 4, Caiado 4, Zema 1, demais 3, brancos/nulos 3, indecisos 2. Fonte: <https://www.cnnbrasil.com.br/eleicoes/nexus-btg-no-1-turno-lula-tem-40-flavio-36-e-cury-7/>
- Indexa 20–23/08, cenário com Pablo Marçal (BR-06366/2026): Lula 39, Flávio 33, Cury 0, Renan 4, Caiado 5, Zema 1, demais 2, brancos/nulos 6, indecisos 10. Fonte: <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/indexa-broadcast-presidente-agosto-2026/>
- Palver Onda 2 (v1) 04–07/09, cenário 1 com Pablo Marçal (BR-05420/2026): Lula 40, Flávio 40, Cury 4, Renan 11, Caiado 1, Zema 1, demais 2, brancos/nulos 0, indecisos 1. Fonte: <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/09/Pesquisa-Eleitoral-Palver-Onda-2-1.pdf>
- Palver Onda 1 03–07/08, cenário 2 reduzido (sem Cury) (BR-06596/2026): Lula 45, Flávio 40, Cury n/d, Renan 10, Caiado 2, Zema 1, demais 0, brancos/nulos 1, indecisos 0. Fonte: <https://static.poder360.com.br/uploads/2026/08/pesquisa-presidente-palver-10ago2026.pdf>
- Futura 03–07/08, cenário 2 reduzido (7 candidatos) (BR-08109/2026): Lula 36.3, Flávio 32.7, Cury 1.6, Renan 3.8, Caiado 7.7, Zema 4.4, demais 1.2, brancos/nulos 8.3, indecisos 3.9. Fonte: <https://www.gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/futura-inteligencia-presidente-agosto-2026/>
- Real Time Big Data 27–31/08, cenário 1 com Pablo Marçal (BR-03490/2026): Lula 38, Flávio 29, Cury 10, Renan 6, Caiado 4, Zema 2, demais 5, brancos/nulos 3, indecisos 3. Fonte: <https://static.poder360.com.br/uploads/2026/09/Pesquisa-presidencial-Brasil-Real-Time-Big-Data-1-set-2026.pdf>

**Excluídos por falta de confirmação.**

- Veritá, 1º turno '47 x 45' nos válidos: só aparece em matérias publicadas depois do 1º turno; sem datas de campo, amostra, registro nem matéria de divulgação até 03/10. Fontes vistas: <https://exame.com/brasil/como-o-verita-cravou-resultado-do-1o-turno-das-eleicoes-de-2026-fundador-explica/>
- Gerp, medição '03/10' de 2º turno (46 x 49 totais; 48 x 52 válidos): só aparece na série histórica dos relatórios da Gerp de 13/10 e 16/10; sem registro próprio nem data de divulgação confirmada. Fontes vistas: <https://static.poder360.com.br/uploads/2026/10/PesquisaGerp-presidente-16out2026.pdf>
- Gerp, uma "leitura" de 15–19/10 (53 × 47 nos válidos) citada por um agregador (quenty.com.br) como divulgada por Claudio Dantas em 20/10. Não confirmada.
- JOTA, pesquisas próprias pela internet (6 mil entrevistas): BR-07806/2026 (campo de 27/07 a 24/08, só 2º turno) e BR-05869/2026 (campo de 03/09 a 28/09). Estão registradas no TSE, mas os resultados não foram localizados, porque o site bloqueia a leitura e não há reprodução.
- Fora da janela (divulgação prevista depois de 22/10): Vetor Arrow BR-06957 (campo de 22 a 23/10), Phoenix BR-06173 e IFP BR-04863 (as duas com divulgação em 24/10).

## Lacunas e o que não deu para confirmar

- **Válidos de 1º turno não divulgados** (pesquisas por instituto): Alfa Inteligência 1, American Analytics 1, AtlasIntel 2, DataTrends 2, Futura 6, Gerp 2, Ideia 3, Indexa 3, Instituto França (IFP) 1, MDA 2, Nexus 8, Palver 7, PoderData 5, Quaest 7, Real Time Big Data 2, Veritá 2, Vox Brasil 3.
- **Válidos de 2º turno após 05/10 não divulgados:** Palver, Quaest, Vox Brasil.
- **Íntegra (PDF) não localizada.** Os números vieram de veículo grande nestas pesquisas:
  - Futura: 04–10/09, 11–15/09, 25–29/09, 16–17/10 (só Exame) e 19–20/10 (só CartaCapital).
  - Nexus: 11–13/09 e 18–20/09.
  - Real Time Big Data: 19–23/09.
  - Vox Brasil: 29/09–01/10 e 15–17/10.
  - Palver: Onda 6 (30/09–03/10).
  - AtlasIntel: 25–30/08.
  - Veritá: todas as rodadas.
  - Indexa: página do Estadão/Broadcast.
- **Futura 04–10/09, Cury:** 6,9% na CNN Brasil e 6,4% no índice. A soma com 6,9 dá 100,4% e com 6,4 dá 99,9%, o que sugere erro de digitação da CNN, mas o PDF não foi achado. O CSV mantém 6,9, que é a fonte lida.
- **Fontes de qualidade menor:**
  - Veritá (veículos regionais e um post retirado do ar).
  - Instituto Ranking (só o contratante Fonte83).
  - Instituto Phoenix (só site ligado ao instituto; amostra em 15 UFs).
  - Instituto França 16–20/10 (cruzamentos que não fecham).
  - DataTrends de setembro e 02/10 (só Revista Oeste, sem datas de campo na de 02/10).
- **Sites bloqueados à ferramenta de leitura:** g1, Folha, O Globo, Estadão e UOL. Os números de Datafolha e Quaest foram conferidos em reproduções:
  - Poder360, que hospeda PDFs das páginas g1/Folha e o relatório Datafolha de 17/09;
  - CNN Brasil, Gazeta do Povo, Exame, Terra e outros.
- **Contratante não informado:** AtlasIntel 25–30/08, Futura 02–03/10 e 19–20/10, DataTrends (exceto 07–09/10), Veritá 26/09–02/10.
- **Contratante que diverge entre fontes:**
  - Datafolha 13–14/10: só Folha, ou Folha e TV Globo.
  - Gerp 03–08/09: AESP Rádio ou recursos próprios.
  - Indexa de agosto: Agência Estado ou recursos próprios.
  - Futura: recursos próprios, Futura Consultoria ou 100% Cidades, conforme o veículo.
- **Ipec e Paraná Pesquisas:** sem pesquisa nacional de presidente nas duas janelas.
  - Ipec: só estadual do Ceará, avaliação de governo e uma nacional de dez/2025.
  - Paraná Pesquisas: a última nacional foi BR-00873/2026 (março). Depois disso, só Tocantins.
- **Ipespe:** sem pesquisa nacional de 1º turno entre 01/08 e 03/10. As duas rodadas de outubro (com a Abrapel) são as primeiras de Lula × Flávio.
- **Institutos verificados sem pesquisa nacional nas janelas** (TSE e buscas):
  - Sem registro de presidente em 2026: Ipsos, Ipri, Equilíbrio e Gualimp.
  - Sem registro de presidente nas janelas: Methodus e Veritas.
  - Só pesquisas estaduais ou municipais: Badra (DF, Baixada Santista, PE), Brasmarket (RS), Seta (RN, PB), Data Tempo (MG), AgoraSei (RN), Ágili (ES), Colectta (SP; a nacional foi em fevereiro), Ranking Brasil Inteligência (Campo Grande), Datavero, IGAPE, Doxa, Neokemp, Exatus, Data Capital, Insight Brasil, Perfil, Nova Ibrape e Percent.

## Alertas (conteúdo da web tratado como dado)

- **CNN Brasil, Futura 03–07/08** (<https://www.cnnbrasil.com.br/eleicoes/futura-lula-tem-388-no-1o-turno-flavio-341/>): no fim da página, um bloco "Buscar" pedia para reproduzir o levantamento completo. Foi ignorado.
- **Exame, matéria de abril, fora da janela** (<https://exame.com/brasil/pesquisa-futura-no-2o-turno-flavio-tem-48-e-lula-426/>): tinha uma instrução embutida pedindo para reproduzir literalmente um bloco de metadados. Foi ignorada. Não está ligada a nenhum registro.
- **Revista Oeste, Gerp 14–16/10:** o resumo automático no topo da matéria repete números da rodada anterior (55/45). O CSV usa o texto da matéria e o PDF (50/45 nos totais, 52/48 nos válidos).
- Nenhuma outra página trouxe instruções. Nada baixado foi executado. Os PDFs foram lidos só como texto ou imagem.

