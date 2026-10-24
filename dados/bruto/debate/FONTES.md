# FONTES — debates da Band na eleição presidencial de 2026

Levantamento feito entre a noite de 22/10/2026 e a madrugada de 23/10/2026 para a tela "O que mudou depois do debate na Band?".

## Arquivos

- `debates.csv`: 12 linhas, uma por debate presidencial do 1º e do 2º turno marcado na campanha, inclusive os cancelados: as 11 do levantamento de 22/10/2026 e o debate da Globo de 23/10, que entrou em 24/10/2026 (ver "Debate da Globo, 23/10, em debates.csv", abaixo). Separador `;`, UTF-8 sem BOM, datas AAAA-MM-DD, ponto decimal. Nenhum campo contém `;`. A `observacao` abre com o status (`REALIZADO`, `CANCELADO`, `NÃO REALIZADO`), e as notas vêm separadas por ` | `. Em `fonte_url`, mais de um link vai separado por ` , `.
- `debate_band.json`: tudo sobre os dois debates da Band: identificação, formato, momentos com trecho curto e fonte, temas, direitos de resposta, audiência, repercussão digital, "quem venceu", pesquisas antes × depois (com as listas usadas) e atribuições. Quando um campo não foi confirmado, ele fica `null` e a razão vai no `*_obs` correspondente.
- O debate da Globo de 23/10 (2º turno) ainda não tinha acontecido no levantamento de 22/10 e ficou fora do CSV até 24/10/2026, quando entrou como linha de `debates.csv` (realizado, com os dois). O JSON guarda o que se sabia em 22/10 (`proximo_debate`), e os números da noite seguem no arquivo próprio, `dados/pbi/debate_globo.csv` (seção "Debate da Globo, 23/10/2026", no fim deste arquivo).

## Escolha de foco (ler antes de montar a tela)

A Band fez dois debates presidenciais em 2026, e o JSON cobre os dois.

1. **23/08, 1º turno.** Foi o primeiro debate da campanha, e o pedido o tratava como principal. **Lula, Flávio Bolsonaro e Zema faltaram.** Estiveram Caiado, Renan Santos e Augusto Cury. O debate teve cerca de 2 pontos de audiência. A mudança mensurável depois dele foi a **alta de Augusto Cury**: de 1,8% para 9,05% na média das pesquisas, ou +8,5 p.p. comparando o mesmo instituto. Essa alta se desfez em setembro.
2. **18/10, 2º turno.** Foi o **primeiro confronto direto entre Lula e Flávio** na campanha (o segundo e último foi na Globo, em 23/10, fora deste levantamento; ver o fim do arquivo). Teve 15 pontos em Grande SP (consolidado divulgado pela Band), a maior audiência de debate em 20 anos segundo a emissora. Nas pesquisas, **nada mudou além da margem de erro**, e a janela "depois" tem só 4 dias e 5 pesquisas.

Para Lula × Flávio, o efeito só pode ser medido no debate de 18/10. O de 23/08 mostra o efeito sobre o "resto do pelotão".

## Como foi feito

1. **Índice da linha do tempo:** seção "Debates e entrevistas" da Wikipédia em português ([Eleição presidencial no Brasil em 2026](https://pt.wikipedia.org/wiki/Elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2026), wikitexto baixado em 22/10). Cada linha foi conferida em segunda fonte (ver tabela abaixo).
2. **Fontes primárias tentadas primeiro:** páginas da Band (resumo do debate, anúncios de pool e datas, balanço de audiência), páginas dos vídeos no YouTube (contagem de visualizações e horários das lives, lidos em 22/10 por volta das 23h50) e o Google Trends (coletado por aqui, ver abaixo). Os sites do Estadão e da Folha não abriram para a ferramenta. Os dados que só saíram neles estão citados pela reprodução em outro veículo, e isso fica indicado.
3. **Pesquisas:** a base local `dados/bruto/pesquisas` foi só lida, não alterada. As contas estão no JSON (`pesquisas_antes_depois`).
4. **Nada estimado.** As únicas contas feitas aqui são as médias e as variações das pesquisas e as razões de audiência indicadas no texto.

## Fontes por tema

### Debate de 23/08 (1º turno)

| Tema | Fonte principal | Conferência |
|---|---|---|
| Data, 20h, local, participantes, ausentes | [Band, resumo](https://www.band.com.br/nacional/brasil/confira-um-resumo-do-debate-da-band-para-presidente) | [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/121577/band-realiza-primeiro-debate-presidencial-veja-quem-participa), [Poder360](https://poder360.com.br/poder-eleicoes-2026/sem-lula-e-flavio-debate-na-band-tera-caiado-zema-renan-e-cury) |
| Pool | [Band, "Estadão se junta à Band"](https://www.band.com.br/noticias/jornal-da-band/ultimas/estadao-se-junta-a-band-na-cobertura-do-debate-presidencial-202608132020) | Folhapress via [Diário do Comércio](https://diariodocomercio.com.br/?p=621218) |
| Mediação (Adriana Araújo e Eduardo Oinegue) | [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/121577/band-realiza-primeiro-debate-presidencial-veja-quem-participa) | Wikipédia, e [Aos Fatos](https://www.aosfatos.org/noticias/checamos-debate-presidencial-band/) cita "Adriana" |
| Formato em 3 blocos | [Band, resumo](https://www.band.com.br/nacional/brasil/confira-um-resumo-do-debate-da-band-para-presidente) | Congresso em Foco |
| Motivos das ausências | [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/121577/band-realiza-primeiro-debate-presidencial-veja-quem-participa), [BNews](https://www.bnews.com.br/noticias/politica/record-exibe-entrevista-com-lula-no-mesmo-horario-do-debate-da-band.html) | Poder360 (nota de Zema) |
| Momentos e frases | [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/121583/ausentes-lula-e-flavio-viram-principais-alvos-do-debate-da-band), BBC News Brasil via [A Gazeta](https://www.agazeta.com.br/mundo/debate-da-band-os-principais-momentos-do-primeiro-confronto-entre-candidatos-a-presidencia-0826), [Aos Fatos](https://www.aosfatos.org/noticias/checamos-debate-presidencial-band/), [Portal N10](https://portaln10.com.br/politica/eleicoes/augusto-cury-renan-ataque-eleitores-lula-351625/) | Folhapress |
| Audiência | [Pipoca Moderna](https://pipocamoderna.com.br/2026/10/debate-band-lideranca-globo/) (prévia via TV Pop: 2,2 pontos em GSP, 4º lugar) | [Vermelho](https://vermelho.org.br/2026/08/24/audiencia-mostra-decisao-acertada-de-lula-em-dar-entrevista-ao-inves-de-ir-a-debate/), [Revista Fórum](https://revistaforum.com.br/politica/lula-record-audiencia-debate-band/), [DCM](https://www.diariodocentrodomundo.com.br/lula-record-dobro-audiencia-debate-band) |
| YouTube | [live do Band Jornalismo](https://www.youtube.com/watch?v=8ejQOXgiMvI) (4.439.881 views em 22/10) e [live da BandNews FM](https://www.youtube.com/watch?v=B856kFWqeBU) (1.063.704) | — |
| Repercussão digital | Vox Radar via [CNN Brasil 27/08](https://www.cnnbrasil.com.br/eleicoes/apos-debate-cury-e-candidato-com-maior-crescimento-de-seguidores-e-buscas/) e [31/08](https://www.cnnbrasil.com.br/eleicoes/vox-radar-cury-tem-aumento-de-seguidores-e-mencoes-apos-debate-e-sabatina/); AP Exata (Estadão) e Bites via [CartaCapital](https://www.cartacapital.com.br/politica/o-que-explica-a-ascensao-de-augusto-cury-nas-pesquisas-eleitorais/); IPD Quaest via [BP Money](https://bpmoney.com.br/politica/augusto-cury-chega-a-10-e-assume-3o-lugar-em-pesquisa-quaest-entenda-cenario/) | [DCM](https://www.diariodocentrodomundo.com.br/augusto-cury-11-popularidade-digital-pesquisa-nexus-btg), [NC News](https://ncnews.com.br/?p=39793) |
| Buscas no Google | Coleta própria (abaixo); [TradeMap](https://trademap.com.br/noticias/news-8221795); [Band/Sala Digital](https://www.band.com.br/nacional/brasil/augusto-cury-lidera-buscas-no-google-apos-debate-na-band) | CNN Brasil (Vox Radar) |
| Quem venceu | BBC via [Correio Braziliense](https://www.correiobraziliense.com.br/mundo/2026/08/7485698-quem-ganhou-o-primeiro-debate-presidencial.html); [Jovem Pan](https://jovempan.com.br/politica/campanha-de-renan-santos-defende-tom-agressivo-durante-debate-ele-e-assim/) | — |
| Atribuição da alta de Cury | [Fernando Mitre, Band](https://www.band.com.br/colunistas/fernando-mitre/o-atual-cenario-eleitoral-com-a-nova-pesquisa), [CartaCapital](https://www.cartacapital.com.br/politica/o-que-explica-a-ascensao-de-augusto-cury-nas-pesquisas-eleitorais/), [Correio da Manhã](https://www.correiodamanha.com.br/colunistas/paulo-cappelli/2026/08/314783-presidente-do-avante-diz-que-augusto-cury-furou-bolha-da-polarizacao-apos-desempenho-em-debate.html), [SBT News](https://sbtnews.sbt.com.br/noticia/eleicoes/cury-atribui-alta-nas-pesquisas-a-movimento-espontaneo), [CNN](https://www.cnnbrasil.com.br/eleicoes/nexus-cury-chega-a-11-e-e-1o-nome-da-terceira-via-a-ter-dois-digitos/), [TradeMap](https://trademap.com.br/noticias/news-8252917) | — |

### Debate de 18/10 (2º turno)

| Tema | Fonte principal | Conferência |
|---|---|---|
| Data, 20h15, mediação, formato | [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/123351/veja-o-primeiro-debate-entre-lula-e-flavio-bolsonaro-na-band), [Poder360](https://poder360.com.br/poder-eleicoes-2026/debate-de-lula-e-flavio-na-band-chega-a-539-milhoes-simultaneos) | [Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2026-10/lula-e-flavio-fazem-primeiro-debate-das-eleicoes-na-band), [Band](https://www.band.com.br/nacional/brasil/debate-historico-da-band-marca-primeiro-confronto-entre-lula-e-flavio) |
| Pool | [Aos Fatos](https://www.aosfatos.org/noticias/checamos-lula-flavio-bolsonaro-debate-band/) | Wikipédia |
| Remarcação e recuo de Flávio | [DGABC](https://www.dgabc.com.br/Noticia/4352608/flavio-bolsonaro-recua-de-desistencia-e-confirma-presenca-em-debate-da-band-no-domingo) | Diário de Pernambuco |
| Momentos, frases, direitos de resposta, checagens | [Aos Fatos](https://www.aosfatos.org/noticias/checamos-lula-flavio-bolsonaro-debate-band/), [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/123351/veja-o-primeiro-debate-entre-lula-e-flavio-bolsonaro-na-band), [Agência Brasil](https://agenciabrasil.ebc.com.br/politica/noticia/2026-10/lula-e-flavio-fazem-primeiro-debate-das-eleicoes-na-band), [Poder360 memes](https://www.poder360.com.br/poder-eleicoes-2026/veja-os-memes-do-debate-entre-lula-e-flavio-bolsonaro-na-band/) | — |
| Audiência na TV | Balanço da Band via [O Universo da TV](https://www.ouniversodatv.com/2026/10/lula-e-flavio-bolsonaro-levam-debate-da.html) e [Portal TV e Streaming](https://www.portaltvstreaming.com.br/2026/10/debate-na-band-entre-flavio-bolsonaro-e.html) (consolidado) | Prévias: [CartaCapital](https://www.cartacapital.com.br/cartaexpressa/band-lidera-audiencia-com-debate-entre-lula-e-flavio-bolsonaro/) (Folha), [Pipoca Moderna](https://pipocamoderna.com.br/2026/10/debate-band-lideranca-globo/) (TV Pop e UOL) |
| YouTube | [Poder360](https://poder360.com.br/poder-eleicoes-2026/debate-de-lula-e-flavio-na-band-chega-a-539-milhoes-simultaneos) (5.385.394 aparelhos às 21h30) | Balanço da Band (6 milhões somando canais); [live do Band Jornalismo](https://www.youtube.com/watch?v=Gqc1rQtzWUk) (32.253.806 views em 22/10) |
| Repercussão digital | Bites via [Vermelho](https://vermelho.org.br/2026/10/20/lula-dispara-nas-redes-apos-debate-na-band-e-supera-flavio-em-5-vezes/); IPD Quaest (Folha) via [DCM](https://www.diariodocentrodomundo.com.br/lula-amplia-vantagem-sobre-flavio-em-popularidade-digital-apos-debate-da-band); Ativaweb via [Brasil 247](https://www.brasil247.com/brasil/desafio-de-lula-a-flavio-bolsonaro-sobre-sigilos-domina-repercussao-do-debate-da-band/) e [Agora RN](https://agorarn.com.br/?p=2407572) | [A Crítica](https://acritica.net/nacional/buscas-flavio-lula-google-debate-band/), [SBT News](https://sbtnews.sbt.com.br/colunas/coluna-da-basilia/busca-por-miliciano-dispara-em-debate-entre-lula-e-flavio) (buscas) |
| Quem venceu | Quaest qualitativa via [O Antagonista](https://oantagonista.com.br/brasil/flavio-foi-ligeiramente-superior-no-debate-indica-quaest/) | [DCM](https://www.diariodocentrodomundo.com.br/lula-x-flavio-bolsonaro-quem-venceu-o-debate-segundo-pesquisa/); analistas e colunistas via [Agora RN](https://agorarn.com.br/?p=2407572) |

### Linha do tempo (debates.csv)

| Data | Status | Conferência além da Wikipédia |
|---|---|---|
| 23/08 Band | realizado | Band, Congresso em Foco, Poder360 |
| 14/09 consórcio SBT/CNN | cancelado em 08/09 | [Jornal Opção](https://www.jornalopcao.com.br/ultimas-noticias/sem-lula-e-flavio-bolsonaro-pool-de-veiculos-cancela-debate-presidencial-866136/), [SBT News](https://sbtnews.sbt.com.br/noticia/eleicoes/sem-lula-flavio-e-tarcisio-veiculos-cancelam-debates) |
| 18/09 Inteligência Ltda/Metrópoles/G4 | realizado | [Poder360](https://www.poder360.com.br/poder-eleicoes/debate-esvaziado-reune-zema-cury-e-samara-em-sao-paulo/) |
| 21/09 Flow/Kwai | realizado | [AUVP Analítica](https://analitica.auvp.com.br/noticias/debate-do-flow-podcast-destaca-polarizacao-e-ausencias-de-lula-e-bolsonaro) |
| 23/09 Veja | realizado | [Muita Informação](https://muitainformacao.com.br/eleicoes/caiado-e-zema-criticam-lula-flavio-bolsonaro-e-stf-em-debate-da-veja/) (Rede Brasil e mediação só na Wikipédia) |
| 26/09 MyNews/Kritikê/3 Irmãos | realizado | **só na Wikipédia**, sem segunda fonte |
| 27/09 Record | cancelado em 23/09 | [Poder360](https://www.poder360.com.br/poder-midia/sem-lula-nem-flavio-record-cancela-debate-do-dia-27/) |
| 01/10 Globo | cancelado no dia | [Congresso em Foco](https://www.congressoemfoco.com.br/noticia/122866/globo-cancela-debate-presidencial-e-fala-em-inseguranca-juridica), [Jornal Opção](https://www.jornalopcao.com.br/ultimas-noticias/globo-cancela-debate-presidencial-apos-decisoes-do-tse-e-do-stf-874361/) |
| 11/10 Record | cancelado | [Jornal Opção](https://www.jornalopcao.com.br/politica/record-cancela-debate-entre-lula-e-flavio-bolsonaro-por-incompatibilidade-de-agendas-877592/) |
| 15/10 consórcio SBT/CNN | não realizado | Wikipédia diz cancelado; o Correio, citando a Folha, disse em 09/10 que "deve ser cancelado". A Band chamou o 18/10 de primeiro confronto entre os dois. |
| 18/10 Band | realizado | Band, Congresso em Foco, Poder360, Agência Brasil |
| 23/10 Globo | realizado (entrou em 24/10/2026) | [Metrópoles, 24/10 00h29](https://www.metropoles.com/brasil/debate-globo-lula-flavio-bolsonaro); regras e mediação: [CNN Brasil, 22/10](https://www.cnnbrasil.com.br/eleicoes/globo-limita-espaco-de-flavio-e-lula-no-estudio-em-ultimo-debate-entenda/), [Exame, 23/10](https://exame.com/brasil/que-horas-termina-o-debate-da-globo-veja-duracao-do-encontro-entre-lula-e-flavio-bolsonaro/) |

## Google Trends (coleta própria)

- **Como.** Usei o endpoint público do trends.google.com (`/trends/api/explore` + `/trends/api/widgetdata/multiline`), com `geo=BR`, `hl=pt-BR`, fuso de Brasília e termos de pesquisa como texto: "Lula", "Flávio Bolsonaro", "Augusto Cury", "Renan Santos", "Ronaldo Caiado". A coleta foi em 22/10/2026 por volta das 23h50.
- **Séries no JSON:**
  - diário de 16/08 a 06/09 (5 termos);
  - hora a hora na noite de 23/08 (5 termos);
  - diário de 05/10 a 22/10 (Lula e Flávio);
  - hora a hora na noite de 18/10 (Lula e Flávio).
- **Cuidados:**
  - O índice vai de 0 a 100 e é relativo dentro de cada consulta, então séries de consultas diferentes não se comparam.
  - O Google amostra os dados, e repetir a consulta pode mudar alguns pontos.
  - "Lula" é um termo curto e mais genérico que "Flávio Bolsonaro", o que favorece Lula na comparação.
- **Resultado:**
  - Às 20h de 23/08, Lula teve 100 (entrevista na Record), Cury 50, Renan 37, Caiado 12 e Flávio 12.
  - Cury passou Lula no diário de 26/08 (51 × 38) e 27/08 (81 × 47).
  - Às 21h de 18/10, Lula teve 100 e Flávio 19.

## Antes × depois nas pesquisas (votos totais, base local)

**Debate de 23/08.**
- Antes: campo terminado entre 13/08 e 22/08, **4 pesquisas** (Quaest 10–13/08, Nexus 14–16/08, Veritá 16–20/08, Datafolha 18–19/08).
- Depois: campo iniciado de 24/08 em diante e terminado até 06/09, **10 pesquisas** (Vox, AtlasIntel, Nexus, Real Time Big Data, Futura, Quaest ×2, Datafolha, PoderData, Veritá).
- Ficaram fora 4 pesquisas com campo que inclui 23/08 (Nexus 21–23, Indexa 20–23, Gerp 21–25, PoderData 23–26).

| 1º turno, média simples | Antes (4) | Depois (10) | Mesmo instituto (4 pares) |
|---|---|---|---|
| Lula | 39,33 | 38,26 | -1,23 p.p. |
| Flávio | 34,77 | 32,90 | -1,30 p.p. |
| Cury | 1,80 | 9,05 | +8,50 p.p. |
| Renan | 3,95 | 3,94 | -0,78 p.p. |
| Outros (Caiado+Zema+demais) | 10,15 | 7,69 | -4,20 p.p. |
| 2º turno simulado Lula | 44,75 | 44,33 | -0,47 p.p. |
| 2º turno simulado Flávio | 43,58 | 44,14 | +1,05 p.p. |

**Debate de 18/10.**
- Antes: campo iniciado depois do 1º turno e terminado entre 08/10 e 17/10, **20 pesquisas listadas, 19 com totais**. A Veritá 12–16/10 não tem totais confirmados.
- Depois: campo iniciado de 19/10 em diante, **5 pesquisas** (Futura 19–20, Gerp 19–21, PoderData 19–21, Indexa 20–21, Datafolha 20–22).
- Ficaram fora 10 pesquisas com campo que atravessa 18/10 e a Instituto Phoenix, que tem amostra em 15 UFs.

| 2º turno | Antes (19) | Depois (5) | Mesmo instituto (5 pares) |
|---|---|---|---|
| Lula | 45,59 | 45,98 | +0,68 p.p. |
| Flávio | 48,02 | 48,02 | +0,76 p.p. |

**Ressalvas:**
- Os institutos são diferentes de uma janela para outra, cada um com seu viés, e por isso a comparação pareada (mesmo instituto) é a mais limpa.
- No caso de 23/08, a alta de Cury aparece nas pesquisas com campo a partir de 27–28/08. Isso coincide com o início do horário eleitoral (28/08) e com a sabatina de Cury no Jornal Nacional (29/08). A Vox Brasil (25–27/08), primeira depois do debate, ainda tinha Cury com 2,6%.
- Nenhuma fonte separa o efeito do debate do efeito desses outros eventos.

## Divergências registradas

- **Audiência de 23/08:**
  - 2,2 pontos, prévia em GSP (Pipoca Moderna/TV Pop);
  - 1,9 de média e 2,9 de pico, sem praça nem medidor (Vermelho);
  - 2,06 no minuto das 20h57 (Fórum/DCM).
  - Não há número consolidado da Kantar nem da Band.
- **Audiência de 18/10:**
  - consolidado divulgado pela Band: 15 de média, 16,5 de pico, 24% de share;
  - prévias: 13 de média e 15 de pico (Folha via CartaCapital), 13,39 e 15,21 (TV Pop).
  - O CSV usa o consolidado.
- **Pico no YouTube em 18/10:** 5,39 milhões de aparelhos no YouTube da Band (Poder360) contra 6 milhões de "usuários simultâneos" somando canais (Band). As visualizações também divergem: 38 milhões (balanço da Band) e "mais de 40 milhões" (outro comunicado da Band, citado em resumo de busca, não aberto).
- **Duração de 23/08:** cerca de 1h30 (BBC) contra "quase duas horas" (Tribuna de Jundiaí). A live do Band Jornalismo terminou às 21h31.
- **Data de 23/08:** a Band, a Folhapress, a BBC e o Congresso em Foco dizem domingo, 23/08. A CNN Brasil e o DCM escreveram "22/08" e "16 de agosto" em matérias sobre o Vox Radar, o que é erro de data.
- **Seguidores de Cury na véspera:** 8,3 milhões (Vox Radar) contra 9,3 milhões (presidente do Avante). O ganho também varia: 1,55 milhão em 5 dias (Vox), 2,6 milhões na semana (Bites), "mais de 2 milhões" até 31/08 (Vox).
- **Direito de resposta em 18/10:** o Aos Fatos diz que Lula não formalizou o pedido, e o Congresso em Foco diz que ele pediu.
- **Pool de 23/08:** o Poder360 e o Congresso em Foco citam só a Band. A própria Band, a Folhapress e a Wikipédia incluem Estadão, Cultura, Gazeta e Jovem Pan.
- **Nome do consórcio SBT/CNN:** "A Hora da Decisão" (BBC) ou "O Momento da Decisão" (Propmark, SBT News, Wikipédia).
- **Audiência de 2022 (comparação):**
  - 1º turno: 13,7 de média e 15,2 de pico (Band) contra 13,3/14,8 (prévia);
  - 2º turno: 12,4 (Pleno.News), 13,1 (Poder360) e 11,8 (prévia).
- **YouTube em 2018:** 470 mil simultâneos (Band, em 2022) contra 390 mil (TecMundo, em 2018).

## Lacunas

- **Pesquisa quantitativa de "quem se saiu melhor":** não foi encontrada para nenhum dos dois debates. Para 18/10 há só a qualitativa da Quaest (Flávio 82 × Lula 79). O Datafolha de 24/10 deve medir o debate da Globo, não o da Band.
- **Audiência consolidada da Kantar para 23/08:** não encontrada.
- **Pico simultâneo no YouTube em 23/08:** não divulgado.
- **Trending Topics de 23/08:** não encontrados.
- **Contagem de perguntas por alvo:** nenhuma fonte contou, em nenhum dos dois debates. Para 23/08 há só a leitura qualitativa de que Lula, ausente, foi o mais citado.
- **Temas sorteados:** nenhuma fonte registra sorteio de temas. Em 23/08 o sorteio definiu a posição no palco.
- **Monitoramentos fora de agregadores:** os relatórios da Bites, AP Exata, Quaest (IPD) e Ativaweb não foram abertos na origem. Os números vêm de veículos que os reproduziram: CartaCapital, Vermelho, DCM, Brasil 247, BP Money e Agora RN. Vermelho, DCM e Brasil 247 têm linha editorial de esquerda.
- **Palver, FGV ECMI e Nexus (monitoramento digital):** nada encontrado sobre os dois debates.
- **2018 em Grande SP:** só foi confirmada a média nacional (6,2). O 6,1/7,5 em GSP apareceu em resumo de busca e não foi confirmado.
- **Debate de 26/09 (MyNews/Kritikê/3 Irmãos):** fonte única, a Wikipédia.
- **Janela "depois" de 18/10:** tem só 4 dias. As pesquisas com campo inteiro depois do debate e divulgadas a partir de 23/10 não estão na base.

## Conteúdo da web com instruções

Nenhuma página consultada trouxe instruções dirigidas ao agente.

---

# Debate da Globo, 23/10/2026 (2º turno) · tela 20 · Debate na Globo (código T26)

Levantamento de 23/10/2026, das 19h às 19h45 (Brasília), para a tela "O último debate mudou alguma coisa?". O debate é
hoje, sexta, 23/10, às 21h20, e a tela fica pronta antes de haver qualquer número: ela se preenche sozinha quando o
arquivo abaixo muda no repositório (o modelo lê o CSV pelo endereço raw do GitHub, como a apuração ao vivo).

## Arquivo

- `dados/pbi/debate_globo.csv` (não `dados/bruto`: é escrito à mão, já no formato que o Power BI lê). Separador
  vírgula, UTF-8 sem BOM, ponto decimal, aspas só onde o texto tem vírgula. Uma linha por fato ou por número. Campo
  vazio = ainda não chegou: a tela mostra "aguardando", com a hora e a fonte esperadas. **Nada estimado**: número só
  entra com fonte publicada.
- No modelo: tabela `T26 Debate Globo` (`pbi/modelo/t26_debate_globo.py`), sem relação com as outras; as contas leem a
  linha pela `chave` (`pbi/scripts/desenho_t26.py` → `pbi/dax/T26 Debate na Globo`).
- Desde 24/10/2026 o debate também é linha de `debates.csv` / `dados/pbi/debate.csv` (seção "Debate da Globo, 23/10, em debates.csv", abaixo). Antes de a linha entrar, toda conta que achava "o debate em que Lula e Flávio estiveram" pelo `MAX(Data)` passou a escolher a Band pela emissora e pelo turno; a lista está naquela seção.

## Colunas

| coluna | o que é |
|---|---|
| `chave` | identificador estável da linha; as contas procuram por ela (não renomeie) |
| `grupo` | `debate` (fatos do evento), `regra` (os blocos), `presenca` (um por candidato), `metrica` (os números da noite) |
| `cartao` | nas métricas, o cartão da tela: `buscas`, `audiencia`, `streaming`, `redes`, `pesquisas`; vazio nos outros grupos |
| `ordem` | ordem da linha; a dos cartões na fita sai da menor ordem de cada cartão |
| `candidato` | `Lula` ou `Flávio` nas linhas de um candidato; vazio nas outras |
| `rotulo` | o título que a tela mostra |
| `medida` | o que o número mede, exatamente (a linha sob o título do cartão); nos blocos, a quantidade de rodadas |
| `situacao` | `debate`: `marcado`, `no_ar`, `realizado`, `adiado`, `cancelado` · `presenca`: `confirmada`, `a_confirmar`, `ausente` · `metrica`: `aguardando`, `publicado`, `nao_divulgado` |
| `valor` | o número publicado (ponto decimal, sem separador de milhar); vazio enquanto não chega. O valor manda: com ele, o cartão aparece como publicado mesmo que `situacao` tenha ficado `aguardando` |
| `texto` | o fato em texto: mediação, onde passa, regras, o histórico da presença; em `adiado`, `cancelado` ou `ausente`, o motivo, com a fonte |
| `unidade` | unidade do valor (`pontos`, `aparelhos`, `interações`, `índice 0 a 100`, `%`; nos blocos, `min cada, por rodada`) |
| `esperado` | quando o número deve chegar, como a tela escreve |
| `previsto_para` | hora prevista (`aaaa-mm-dd hh:mm`, Brasília); na linha `debate`, o início; na `fim`, o fim previsto |
| `fonte_esperada` | de onde o número deve vir (a tela mostra enquanto ele não chega) |
| `fonte` | de onde veio, com veículo e hora (a tela mostra quando ele chega) |
| `fonte_url` | link(s) da fonte, separados por ` , ` |
| `atualizado_em` | quando a linha foi atualizada (`dd/mm/aaaa hh:mm`, Brasília); na linha `debate`, é a "situação em" da tela |
| `observacao` | ressalva para o leitor (vai para o dossiê do cartão); escreva para quem lê a tela, não para quem mantém |

## As métricas: fonte e hora esperadas

| chave | cartão | o que é | fonte esperada | quando | régua da Band (18/10), já no modelo |
|---|---|---|---|---|---|
| `buscas_lula`, `buscas_flavio` | buscas | pico de cada um na noite, 0 a 100 | Google Trends, coleta própria: tópicos Lula (`/m/0pc9q`) e Flávio Bolsonaro (`/g/122pdhqd`), Brasil, hora a hora, numa consulta só que cubra a noite (como a H2 de `trends_tempo`) | sexta, depois das 23h30 | `Trends tempo`, consulta H2, 18/10 das 20h à meia-noite: Lula 100 (21h), Flávio 91 (22h) |
| `audiencia_previa` | audiência | pontos na Grande SP, prévia | Kantar IBOPE (prévia), via imprensa (colunas de TV, Folha, UOL) | sexta, perto da meia-noite | 13 (Folha via CartaCapital; a TV Pop deu 13,39), da observação de `debates.csv` |
| `audiencia_consolidado` | audiência | pontos na Grande SP, consolidado | Kantar IBOPE (consolidado), divulgado pela Globo ou pela imprensa | sábado à tarde (ou segunda, 26/10) | 15 (consolidado divulgado pela Band, `debates.csv`) |
| `streaming_pico` | streaming | pico de aparelhos assistindo ao mesmo tempo | balanço da Globo (g1, Globoplay, YouTube) ou contador da transmissão; anote a plataforma em `fonte` | sexta, fim do debate ou madrugada | 5.385.394 aparelhos no YouTube da Band (Poder360, `debates.csv`) |
| `redes_lula`, `redes_flavio` | redes | interações nas 24 horas depois do debate | Bites, via imprensa (a mesma medida usada depois da Band). Se só sair outra medida (IPD Quaest, Ativaweb), troque `medida`, `unidade` e `fonte` para ela: a régua da Band vale só para a mesma medida da mesma agência | sábado à noite | `Monitoramento`, Bites: Lula 25,5 mi, Flávio 5,0 mi |
| `pesquisas_depois` | pesquisas | média das pesquisas com o campo inteiro depois do debate (votos totais) | institutos com registro no TSE | sábado à noite ou domingo cedo | "antes": as 5 pesquisas com o campo inteiro entre os dois debates (19 a 22/10): Lula 45,98%, Flávio 48,02% |

As pesquisas não têm número nesta linha: o cartão conta pela tabela `Pesquisa`, com a regra da tela 08 (campo inteiro
depois = começa depois do dia do debate; quem atravessa o dia fica fora das médias). Basta lançar a pesquisa em
`dados/bruto/pesquisas/pesquisas_2turno.csv`, como as outras, e exportar (`pipeline/exportar_pbi.py`). Como a eleição é
no domingo, o campo teria de caber no sábado: provavelmente só as últimas de sábado, talvez nenhuma. Se nenhuma sair,
marque `situacao = nao_divulgado` nesta linha.

## O que já está preenchido (fatos de 23/10/2026, 19h45)

| linha | valor | fonte |
|---|---|---|
| `debate` | marcado; sexta, 23/10, 21h20, depois do Jornal Nacional | [CNN Brasil, 22/10 17h48](https://www.cnnbrasil.com.br/eleicoes/globo-limita-espaco-de-flavio-e-lula-no-estudio-em-ultimo-debate-entenda/); [Exame, 23/10 07h02](https://exame.com/brasil/que-horas-termina-o-debate-da-globo-veja-duracao-do-encontro-entre-lula-e-flavio-bolsonaro/); [Diário do Pará, 23/10 11h06](https://diariodopara.com.br/eleicoes-2026/lula-e-flavio-bolsonaro-fazem-ultimo-debate-na-globo-hoje-veja-o-horario-regras-transmissao-e-como-sera-a-checagem-de-informacoes/) |
| `fim` | a Globo não informou; o Jornal da Globo está previsto para as 23h30 (pelo menos duas horas de debate) | Exame, 23/10 |
| `transmissao` | TV Globo, GloboNews e g1 (e Globoplay) | Exame; [NSC Total, 23/10 10h](https://www.nsctotal.com.br/politica/quem-vai-mediar-debate-globo-segundo-turno-2026) |
| `mediacao`, `local` | César Tralli · Estúdios Globo, Rio de Janeiro | CNN Brasil; Exame |
| `checagem` | Fato ou Fake do g1, durante e depois (cerca de 30 jornalistas, com O Globo, Extra, Valor e CBN; sem correção ao vivo na TV) | CNN Brasil; Diário do Pará |
| `bloco1` a `bloco4`, `finais` | quatro blocos e as considerações finais: 1, as regiões do país e um tema nacional (seis rodadas); 2 e 3, temas escolhidos num telão; 3 min por rodada para cada um, divididos entre pergunta e réplica ou resposta e tréplica; 4, tema livre, 8 min para cada um, sem limite de intervenções; depois, até 10 min de entrevista para cada um, na ordem sorteada | CNN Brasil; Exame; Diário do Pará |
| `presenca_lula` | confirmada. Em 20/10, as duas campanhas assinaram a ata com as regras, e Lula disse em Juazeiro (BA) que só haveria debate se Flávio autorizasse a quebra dos próprios sigilos; em 22/10, a equipe de comunicação do PT confirmou a presença dele; em 23/10, o ministro Sidônio Palmeira disse que Lula vai tratar de propostas no debate | [Diário do Nordeste, com a Folha, 20/10](https://diariodonordeste.verdesmares.com.br/pontopoder/flavio-bolsonaro-e-lula-confirmam-presenca-em-debate-na-globo-veja-regras-1.3799938); [Poder360, 20/10 19h51](https://www.poder360.com.br/poder-eleicoes-2026/lula-condiciona-debate-na-globo-a-abertura-de-sigilo-de-flavio/); [ND Mais, 22/10 19h28](https://ndmais.com.br/politica/lula-vai-no-debate-da-globo/); [Metrópoles, 23/10 14h56](https://www.metropoles.com/brasil/lula-fara-debate-propositivo-e-nao-vai-aceitar-provocacoes-diz-sidonio) |
| `presenca_flavio` | confirmada. Em 20/10, as duas campanhas assinaram a ata com as regras; em 21/10, Flávio disse que aceitaria abrir os próprios sigilos, com condições; em 23/10, o Metrópoles registra que as duas campanhas aceitaram as regras de circulação no palco | Diário do Nordeste, com a Folha, 20/10; [CNN Brasil, 21/10 13h47](https://www.cnnbrasil.com.br/eleicoes/flavio-impoe-condicoes-para-aceitar-desafio-de-lula-sobre-sigilo/); Metrópoles, 23/10 |
| métricas | vazias, `aguardando` | — |

Conferência (não entrou no CSV): [Congresso em Foco, 21/10 8h57](https://www.congressoemfoco.com.br/noticia/123448/lula-condiciona-ida-ao-debate-na-globo-a-abertura-de-sigilos-de-flavio)
repete a condição de Lula; [Metrópoles, 23/10 12h45](https://www.metropoles.com/brasil/lula-se-reune-com-coordenacao-de-campanha-em-dia-de-debate-da-globo)
relata a reunião de Lula com a coordenação da campanha para acertar os últimos detalhes do debate.

## Divergências registradas

- **Data:** a NSC Total (23/10) fala, num trecho, em "domingo (25)" e, no resto, em sexta (23); o Diário do Nordeste
  escreveu "sexta-feira (22)"; a ND Mais (20/10) chegou a dar 25/10. Vale sexta, 23/10, como em CNN Brasil, Exame,
  Diário do Pará e Metrópoles. O domingo, 25/10, é o 2º turno.
- **Formato:** em 20/10 (ND Mais, Diário do Nordeste), o formato era de três blocos (regiões sorteadas, seis de dez
  temas no telão, tema livre). A versão de 22 e 23/10 (CNN Brasil, Exame, Diário do Pará) tem quatro blocos e as
  considerações finais; o arquivo usa esta.
- **Presença de Lula:** a condição dele (20/10) é do mesmo dia em que as campanhas assinaram a ata das regras. Nenhuma
  fonte de 23/10 diz que a condição foi atendida ou retirada; o que há é a confirmação do PT (22/10) e a fala do
  ministro da Secom (23/10). Se Lula ou Flávio não for, troque `situacao` para `ausente` e escreva o motivo em `texto`,
  com a fonte.

## Como atualizar (sexta à noite e sábado)

Edite `dados/pbi/debate_globo.csv` (planilha ou editor de texto; mantenha a vírgula como separador e o ponto decimal),
faça commit e push e atualize o modelo (o Service com atualização agendada, ou "Atualizar" no Desktop). O raw do
GitHub guarda cópia por até 5 minutos.

1. **Começou (21h20):** linha `debate`, `situacao = no_ar` (opcional) e `atualizado_em`. Se alguém faltar: a linha de
   presença dele com `situacao = ausente` e o motivo em `texto`, com `fonte` e `fonte_url`.
2. **Acabou (~23h30):** `debate`, `situacao = realizado`, `atualizado_em`.
3. **Buscas (depois das 23h30):** consulta no Google Trends com os dois tópicos juntos, Brasil, hora a hora, cobrindo a
   noite; o maior índice de cada um entre 21h e meia-noite vai em `valor` de `buscas_lula` e `buscas_flavio` (os dois
   da mesma consulta), com `fonte` (ex.: "Google Trends, coleta de 24/10, 00h10") e `atualizado_em`.
4. **Audiência, prévia (perto da meia-noite):** `audiencia_previa`, `valor` em pontos (ex.: `16.4`), `fonte` com o
   veículo e a hora.
5. **Pico na internet:** `streaming_pico`, `valor` em aparelhos (número inteiro), `fonte` com a plataforma.
6. **Redes (sábado):** `redes_lula` e `redes_flavio`, a mesma medida para os dois.
7. **Audiência, consolidado (sábado à tarde ou segunda):** `audiencia_consolidado`.
8. **Pesquisas (sábado à noite ou domingo cedo):** lance cada pesquisa nova em `pesquisas_2turno.csv` e exporte; se não
   sair nenhuma com o campo inteiro depois do debate, `pesquisas_depois` com `situacao = nao_divulgado`.
9. Número que não sair até a eleição: `situacao = nao_divulgado` na linha (a tela troca "aguardando" por "não
   divulgado"). Se o debate cair: `debate`, `situacao = cancelado` (ou `adiado`), o motivo em `texto`, com fonte.

## Conteúdo da web com instruções

Nenhuma página consultada para esta seção trouxe instruções dirigidas ao agente.

## Debate da Globo, 23/10, em debates.csv (24/10/2026)

O debate aconteceu e entrou como linha de `debates.csv` (e, pelo `pipeline/exportar_pbi.py`, de `dados/pbi/debate.csv`),
com os campos que o arquivo já tinha. Nada estimado.

| campo | valor | fonte |
|---|---|---|
| `data`, `turno`, `emissora` | 2026-10-23, 2, Globo | CNN Brasil (22/10), Exame (23/10), Metrópoles (24/10) |
| `pool` | Grupo Globo (TV Globo, GloboNews, g1, Globoplay) | Exame (23/10); NSC Total (23/10) |
| `participantes` | Lula (PT), Flávio Bolsonaro (PL); `ausentes` vazio | [Metrópoles, 24/10 00h29](https://www.metropoles.com/brasil/debate-globo-lula-flavio-bolsonaro): os dois compareceram e se enfrentaram |
| `mediacao` | César Tralli | CNN Brasil (22/10); Exame (23/10); Metrópoles (24/10) |
| `audiencia_pontos_gsp`, `audiencia_fonte`, `pico_streaming` | vazios | ainda não divulgados: entram quando sair o número (a sessão principal preenche), com a fonte |
| `observacao` | REALIZADO; marcado para as 21h20, durou quase 2h30 e terminou por volta das 23h50 | Metrópoles (24/10 00h29); horário marcado: CNN Brasil e Exame |

Os números da noite (buscas, audiência, streaming, redes, pesquisas) continuam chegando primeiro em
`dados/pbi/debate_globo.csv`, que a tela do debate da Globo (T26) lê. Quando a audiência e o pico saírem, repita-os
aqui, na linha de 23/10, com a mesma fonte; a régua da Band na T26 não muda, porque lê a linha da Band.

**As contas que liam a tabela Debate e o que mudou nelas.** Com a Globo na tabela, quem procurava "o debate com os dois"
pelo `MAX(Data)` passaria a pegar a Globo onde a tela fala da Band. Todas passaram a escolher a Band pela regra
explícita **Emissora = "Band" e Turno = 2**, a mesma que `T26 · Band · data` já usava:

- `T07 · debate · data` (tela do debate da Band: audiência, YouTube, janelas das pesquisas, palco);
- `T08 · debate · data` (buscas: a marca do debate e a virada do dia seguinte);
- `T09 · debate · data` (redes: a marca do debate no índice de popularidade);
- `T17 · debate · data` (2º turno: a primeira das duas marcas de debate da curva; a da Globo é `T17 · debate da Globo · data`);
- `T26 · Band · data` (já era explícita; ganhou a descrição da regra).

E as que contavam "os debates do 2º turno antes deste" na tela da Globo (`T26 · 2º turno · debates` e
`T26 · 2º turno · realizados`) passaram a filtrar a data anterior ao dia do debate da Globo. A tela da Band passou a
contar 2 de 12 debates com os dois, com o eixo até 23/10, e fecha a janela "depois" das pesquisas na véspera do debate
da Globo (`T07 · debate seguinte · data`).

---

# Revisão dos dois debates do 2º turno (24/10/2026, das 11h50 às 12h20)

Pedido do Alisson: "designa uma sessão para pesquisar novamente sobre os debates". Foram revistos o debate da Band
(18/10) e o da Globo (23/10). Só entrou fato com fonte, com veículo e hora. Quando duas fontes divergiram, as duas
ficaram registradas. Os números de outros eventos ficaram de fora: o debate cancelado de 1º/10, as entrevistas no Jornal
Nacional, o Flow e a "intenção de assistir".

## O que mudou em cada arquivo

| arquivo | mudança |
|---|---|
| `dados/pbi/debate_globo.csv` | `buscas_lula` 100 e `buscas_flavio` 45 (`publicado`, consulta H3); `checagem` com a contagem do Fato ou Fake; `debate` com a janela do Ibope; `audiencia_previa` com as praças e a divergência; `streaming_pico` e `pesquisas_depois` com o que se sabe às 12h (seguem `aguardando`); `esperado` e `previsto_para` do consolidado (segunda, 26/10), da Bites (sábado, 18h), das pesquisas (sábado, 18h40) e do pico na internet (sem previsão; marcado para segunda, 26/10) |
| `debates.csv` e `dados/pbi/debate.csv` | Globo: `audiencia_pontos_gsp` = 25 (prévia), com a fonte, e a `observacao` com a janela, as praças, a divergência e as checagens. Band: a `observacao` ganhou o consolidado com uma casa (14,9 e 23,8%) e o YouTube no encerramento. O `debate.csv` foi regravado como no `pipeline/exportar_pbi.py` (`read_csv` → `to_csv`), e só as duas linhas mudaram |
| `ao_vivo_globo.csv` | 30 linhas novas: início e fim, prévia por praça e a divergência da Outro Canal, streaming, checagens, as 12 pesquisas de sábado com o campo do registro, a fonte original da Palver e a ausência da Bites. Uma linha antiga (21h50, `streaming`) tinha `;` dentro do texto e foi corrigida, com o mesmo conteúdo |
| `../digital/trends_tempo.csv` | Consulta H3 refeita: média de 5 coletas, 336 linhas no lugar das 338 da coleta descartada, sem duplicar (método em `../digital/FONTES.md`, seção "Consulta H3") |

**Formato de `ao_vivo_globo.csv`.** Separador `;`, UTF-8 sem BOM, sem aspas, e nenhum campo contém `;`. Colunas:
`coletado_em` (hora da leitura, horário de Brasília), `tipo`, `valor` (ponto decimal), `unidade`, `texto`, `fonte`,
`fonte_url` e `publicado_em`. Os tipos são:
- `situacao`, `audiencia_previa`, `audiencia_pico`, `streaming`, `presenca` e `outro`, da coleta ao vivo;
- `checagem` e `pesquisa`, desde esta revisão.

## Globo, 23/10: o que foi achado

| fato | número | fonte |
|---|---|---|
| Início | marcado para 21h20; o Ibope mediu a partir das 21h39; o ao vivo do Terra postou "Debate começa" às 21h43 | [Poder360, 24/10 01h49](https://www.poder360.com.br/poder-eleicoes-2026/debate-de-lula-e-flavio-na-globo-chega-a-30-pontos-de-audiencia/); [Terra ao vivo](https://www.terra.com.br/ao-vivo/noticias/eleicoes/flavio-bolsonaro-e-lula-se-enfrentam-em-debate-da-globo-acompanhe-ao-vivo,7d83b51290333be5351e46de92306d3c5knbcs8b.html) (hora da postagem, no JSON da página) |
| Fim | o Ibope mediu até 23h49; o Metrópoles diz que terminou por volta das 23h50; as considerações finais saíram no Terra às 23h53 e 23h57 (horas de postagem) | Poder360; [Metrópoles, 24/10 00h29](https://www.metropoles.com/brasil/debate-globo-lula-flavio-bolsonaro); Terra |
| Audiência, prévia, Grande SP | 25 de média e 28 de pico (21h39 às 23h49); 1 ponto = 199 mil pessoas | Poder360, 24/10 01h49 (cita "Ibope"); repetido pelo [Brasil 247](https://www.brasil247.com/midia/debate-entre-lula-e-flavio-bolsonaro-na-globo-alcanca-audiencia-comparavel-a-copa-do-mundo/) e pelo [TV Foco](https://tvfoco.uai.com.br/debate-da-globo-entre-lula-e-flavio-explode-na-audiencia/), este dizendo que o número é da Folha |
| Audiência, prévia, PNT | 28 de média e 30 de pico; 1 ponto = 699 mil pessoas | Poder360 |
| Audiência, prévia, por praça | Rio 33,39 (51,95% de share), Recife 31,84 (59,26%), DF 31,65 (54,38%), Salvador 29,98 (54,69%), São Paulo 25,07 (43,30%) | [Portal Alta Definição, 24/10 00h39](https://portalaltadefinicao.com/debate-na-globo-tem-ibope-de-copa-do-mundo-e-ultrapassa-33-pontos-confira-a-audiencia-pelo-brasil/) |
| Audiência, consolidado | não saiu até 12h20 de 24/10 | — |
| Pico simultâneo na internet | não divulgado até 12h20; o debate não passou no YouTube da Globo | [Exame, 23/10](https://exame.com/brasil/debate-da-globo-entre-lula-e-flavio-bolsonaro-sera-transmitido-no-youtube-veja-onde-assistir/) |
| Interações (Bites) | não saíram até 12h20; nada da AP Exata nem da Ativaweb sobre este debate | — |
| Fato ou Fake (g1) | 54 falas checadas. Flávio: 29 (12 fato, 12 não é bem assim, 5 fake). Lula: 25 (15 fato, 7 não é bem assim, 3 fake) | [g1, 23/10 22h15, atualizado 24/10 10h38](https://g1.globo.com/fato-ou-fake/eleicoes/noticia/2026/10/23/veja-o-que-e-fato-ou-fake-nas-falas-de-flavio-bolsonaro-e-lula-no-debate-da-globo-no-2o-turno-das-eleicoes-2026.ghtml) |
| Buscas no Google | pico na noite: Lula 100 (23h), Flávio 45 (23h); na mesma consulta, a Band teve Lula 57 (21h) e Flávio 51 (22h) | consulta H3, coleta própria (ver `../digital/FONTES.md`) |

**Como a contagem do Fato ou Fake foi feita.** Os selos foram contados na própria página, aberta no navegador às
12h05. A página separa as checagens em duas seções, "Flávio Bolsonaro (PL)" e "Lula (PT)", e cada checagem termina em
"Veja por quê" com o selo. Detalhes:
- um selo grafado `#/FATO`, na seção de Lula, foi contado como FATO;
- uma fala com duas afirmações e dois selos (há uma assim na seção de Lula, sobre a fome) conta como duas checagens;
- uma das 5 checagens #FAKE de Flávio é um vídeo publicado no perfil dele no Instagram durante o debate.

A contagem é das falas que a equipe escolheu checar, não de tudo o que cada um disse. Outras agências (Lupa, UOL
Confere, Estadão Verifica, Aos Fatos) fizeram as próprias seleções. Elas apareceram resumidas no
[Só Notícia Boa](https://www.sonoticiaboa.com.br/2026/10/24/quem-mentiu-mais-debate-globo-flavio-lula), mas não foram
abertas na origem e ficaram de fora. A página do g1 foi atualizada às 10h38 de 24/10 e pode ganhar checagens depois da
contagem.

**Pesquisas com o campo inteiro depois do debate: até 12h20, nenhuma.** O Poder360
([24/10 06h15](https://www.poder360.com.br/poder-eleicoes-2026/saiba-quais-pesquisas-eleitorais-podem-sair-neste-sabado-24-out/),
tabela com os registros no TSE) lista 12 pesquisas nacionais de 2º turno para sábado. Pelas datas de campo do registro,
todas começam antes de 24/10:

| instituto (quem paga) | campo no registro |
|---|---|
| 100% Cidades (Futura) | 21 a 24/10 |
| AtlasIntel | 18 a 23/10 |
| Colectta (Brazil Economy) | 23/10 |
| Datafolha (Folha da Manhã) | 23 e 24/10 |
| Instituto França | 21 a 23/10 |
| Veritá | 19 a 23/10 |
| MDA Pesquisa (CNT) | 21 a 23/10 |
| Nexus (BTG Pactual) | 23 e 24/10 |
| Palver | 22 a 24/10 |
| Quaest (Globo) | 23 e 24/10 |
| Seta Pesquisa | 23 e 24/10 |
| Simplex | 19 a 23/10 |

A única dúvida é a Datafolha: registro BR-09540/2026, 4.050 entrevistas, divulgação por volta das 18h40.
- O registro (Poder360) e o [Brasil de Fato](https://www.brasildefato.com.br/2026/10/23/datafolha-atlasintel-quaest-quando-saem-as-ultimas-pesquisas-do-segundo-turno-das-eleicoes/)
  (23/10 16h42) dão campo "entre sexta e sábado".
- A [CartaCapital](https://www.cartacapital.com.br/politica/os-detalhes-da-ultima-pesquisa-datafolha-sobre-lula-x-flavio-bolsonaro-no-2o-turno/)
  (23/10 18h28) diz que as entrevistas foram "todas realizadas no sábado".
- Vale a ficha técnica divulgada com a pesquisa:
  - se o campo for só 24/10, ela entra em `pesquisas_2turno.csv` como "depois do debate";
  - se não, `pesquisas_depois` vira `nao_divulgado` depois das 19h.

As outras entram na base como de costume, com o campo que atravessa o dia do debate.

## Band, 18/10: conferência

Os números registrados continuam certos, e nada foi corrigido. Saiu um detalhe novo, anotado na `observacao`.

| número | situação | fonte |
|---|---|---|
| Consolidado: 15 de média, pico de 16,5 e 24% de share (Grande SP, 20h20 às 22h04, 2,7 milhões de pessoas) | confirmado | balanço da Band via [O Universo da TV, 19/10](https://www.ouniversodatv.com/2026/10/lula-e-flavio-bolsonaro-levam-debate-da.html) (fontes: Kantar IBOPE/GSP, YouTube Studio, Emplifi) |
| Consolidado com uma casa: 14,9 de média e 23,8% de share | novo, é o mesmo consolidado | [Poder360, 24/10 01h49](https://www.poder360.com.br/poder-eleicoes-2026/debate-de-lula-e-flavio-na-globo-chega-a-30-pontos-de-audiencia/) |
| Prévia: 13 de média e 15 de pico (20h15 às 22h11); no PNT, 13 × 12 do Fantástico | confirmado | coluna F5 da Folha via [A Tarde, 19/10 07h52](https://atarde.com.br/televisao/debate-entre-lula-e-flavio-faz-band-bater-recorde-e-superar-a-globo-1406201); a Band contestou a prévia pela exibição simultânea em várias TVs |
| YouTube: 5.385.394 aparelhos às 21h30 no @bandjornalismo; 5,13 milhões no encerramento (22h10) | confirmado; o encerramento é novo | [Poder360, 18/10 22h32](https://poder360.com.br/poder-eleicoes-2026/debate-de-lula-e-flavio-na-band-chega-a-539-milhoes-simultaneos) |
| Bites, 24h: Lula 25,5 mi × Flávio 5,0 mi de interações | confirmado; saiu às 17h45 do dia seguinte | [Poder360, 19/10 17h45](https://www.poder360.com.br/poder-eleicoes-2026/lula-tem-5-vezes-mais-interacoes-nas-redes-que-flavio-apos-debate/) |

Os "14,89 de média e 16,51 de pico" citados em `pbi/tmp/coleta_debate_brief.md` não aparecem em nenhuma fonte encontrada
e não foram usados.

## Divergências novas

- **Audiência da Globo, prévia:**
  - o Poder360 (01h49), o Brasil 247 (05h29) e o TV Foco (11h00) dão 25 na Grande SP e 28 no PNT;
  - a primeira versão da coluna Outro Canal (F5, 24/10 00h00), citada pelo fórum
    [BCharts](https://bcharts.com.br/t/lula-x-flavio-bolsonaro-na-globo-tem-indices-de-audiencia-semelhantes-a-copa-na-mundo-veja-numeros/105954)
    às 03h30, deu 27 e 29;
  - o O Planeta TV (07h24) fala em 8,7% acima dos 23 pontos da novela, o que bate com 25;
  - o arquivo usa 25 e 28.
- **Início da Globo:** marcado para 21h20 (CNN Brasil, Exame); o Portal Alta Definição diz que o programa começou às
  21h30; o Ibope mediu a partir das 21h39.
- **Duração da Globo:** "quase 2h30" (Metrópoles) contra 2h10 da janela medida pelo Ibope (21h39 às 23h49). O Metrópoles
  provavelmente conta desde o horário marcado.
- **Campo da Datafolha de sábado:** 23 e 24/10 (registro, Brasil de Fato) ou só 24/10 (CartaCapital).

## O que ainda falta e quando deve sair

| pendência | quando | de onde |
|---|---|---|
| Pesquisas de sábado (Datafolha decide o cartão) | Datafolha por volta das 18h40; AtlasIntel ~18h; Nexus depois das 16h; Quaest à tarde | institutos e imprensa |
| Interações (Bites) | sábado, no fim da tarde ou à noite (depois da Band, saiu às 17h45 do dia seguinte) | Bites, via Poder360 ou outros veículos |
| Audiência consolidada da Globo | provavelmente segunda, 26/10 (o da Band saiu na segunda seguinte); antes, só se a Globo divulgar | Kantar IBOPE, via Globo ou imprensa |
| Pico simultâneo no g1, no Globoplay ou na GloboNews | sem previsão; a Globo pode não divulgar. Se nada sair até segunda, `nao_divulgado` | balanço da Globo |

## Conteúdo da web com instruções

Nenhuma página consultada nesta revisão trouxe instruções dirigidas ao agente. Os banners de cookies ficaram sem clique.
