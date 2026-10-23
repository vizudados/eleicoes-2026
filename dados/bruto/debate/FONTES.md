# FONTES — debates da Band na eleição presidencial de 2026

Levantamento feito entre a noite de 22/10/2026 e a madrugada de 23/10/2026 para a tela "O que mudou depois do debate na Band?".

## Arquivos

- `debates.csv`: 11 linhas, uma por debate presidencial do 1º e do 2º turno marcado até 22/10/2026, inclusive os cancelados. Separador `;`, UTF-8 sem BOM, datas AAAA-MM-DD, ponto decimal. Nenhum campo contém `;`. A `observacao` abre com o status (`REALIZADO`, `CANCELADO`, `NÃO REALIZADO`), e as notas vêm separadas por ` | `. Em `fonte_url`, mais de um link vai separado por ` , `.
- `debate_band.json`: tudo sobre os dois debates da Band: identificação, formato, momentos com trecho curto e fonte, temas, direitos de resposta, audiência, repercussão digital, "quem venceu", pesquisas antes × depois (com as listas usadas) e atribuições. Quando um campo não foi confirmado, ele fica `null` e a razão vai no `*_obs` correspondente.
- O debate da Globo de 23/10 (2º turno) ainda não tinha acontecido e ficou fora do CSV. Ele aparece só em `proximo_debate`, no JSON.

## Escolha de foco (ler antes de montar a tela)

A Band fez dois debates presidenciais em 2026, e o JSON cobre os dois.

1. **23/08, 1º turno.** Foi o primeiro debate da campanha, e o pedido o tratava como principal. **Lula, Flávio Bolsonaro e Zema faltaram.** Estiveram Caiado, Renan Santos e Augusto Cury. O debate teve cerca de 2 pontos de audiência. A mudança mensurável depois dele foi a **alta de Augusto Cury**: de 1,8% para 9,05% na média das pesquisas, ou +8,5 p.p. comparando o mesmo instituto. Essa alta se desfez em setembro.
2. **18/10, 2º turno.** Foi o **único confronto direto entre Lula e Flávio** na campanha. Teve 15 pontos em Grande SP (consolidado divulgado pela Band), a maior audiência de debate em 20 anos segundo a emissora. Nas pesquisas, **nada mudou além da margem de erro**, e a janela "depois" tem só 4 dias e 5 pesquisas.

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
