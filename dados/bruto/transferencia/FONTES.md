# FONTES — eleitores dos outros candidatos e transferência para o 2º turno (presidente 2026)

Levantamento feito em 22 e 23/10/2026 para a tela do painel "Para onde vão os votos de Cury, Renan e Caiado?" e para calibrar o simulador. O índice das pesquisas é a base `..\pesquisas\` (`FONTES.md`, `pesquisas_1turno.csv`, `pesquisas_2turno.csv`). Este levantamento não refaz aquele índice: abre o relatório de cada rodada e tira dele os cruzamentos.

## Arquivos

Todos em UTF-8 sem BOM, separador `;`, ponto decimal, datas AAAA-MM-DD. Nenhum campo contém `;`. Na `observacao`, as notas são separadas por ` | `.

| Arquivo | Linhas | O que é |
|---|---|---|
| `transferencia.csv` | 237 | Voto no 2º turno (Lula × Flávio) entre os eleitores de cada candidato do 1º turno. 119 linhas de pesquisas divulgadas depois do 1º turno e 118 de simulações de agosto a 03/10. |
| `rejeicao.csv` | 374 | Rejeição de Lula e Flávio, de 01/08 a 22/10, por rodada e instituto. Também a de Cury, Renan, Caiado e Zema no eleitorado total, quando publicada. |
| `apoios.csv` | 56 | Posição no 2º turno de cada candidato derrotado, dos partidos, dos governadores eleitos e dos candidatos a governador em 2º turno. |
| `perfil_outros.csv` | 607 | Perfil dos eleitores de Cury, Renan e Caiado: região, renda, idade, religião, escolaridade, sexo, voto em 2022, imagem e avaliação do governo. |
| `comparecimento.csv` | 169 | Intenção ou certeza de ir votar no 2º turno e perguntas sobre quem não votou no 1º. Não estava no pedido original; entra porque o item 5 pedia o dado. |

### Convenções de `transferencia.csv`

- **`segmento_1turno`**: `total` (linha de referência da pesquisa), `Lula` e `Flávio` (fidelidade), `Cury`, `Renan`, `Caiado`, `Zema`, `outros` (composição na `observacao`), `agregado_3via` (soma de candidatos, composição na `observacao`), `branco_nulo`, `nao_votou` e `nao_sabe_nao_lembra`.
- **`observacao`** começa sempre com:
  - `momento=apos_1turno`: pesquisa divulgada de 05/10 em diante. O segmento é o voto declarado no 1º turno (`segmento=recall`).
  - `momento=antes_1turno`: simulação de agosto a 03/10. O segmento é a intenção de voto no 1º turno (`segmento=intencao_1t`).
- **`base`**: todas as linhas estão em `totais`. Nenhum instituto publicou o cruzamento em votos válidos.
- **`n_segmento`**: preenchido só quando o instituto publicou o n (Palver, Ideia e Gerp). Quando não publicou, fica em branco e a `observacao` traz a fatia do segmento ou a margem, se houver. Nada foi calculado multiplicando percentual por amostra.
- **Segmentos pequenos**: `AMOSTRA PEQUENA (n<100)` quando o n publicado é menor que 100; `provável n<100` quando o n não foi publicado, mas a fatia (cerca de 2 a 3% da amostra) ou a margem (10 p.p. ou mais) indica isso. **Praticamente todos os segmentos de Cury, Renan e Caiado estão nessa situação.**
- **`branco_nulo_nao_vota`** segue cada instituto:
  - AtlasIntel publica branco/nulo/não sabe juntos, e `nao_sabe` fica vazio.
  - Quaest junta branco/nulo/não vai votar.
  - Gerp usa "nenhum deles".
  - Palver usa "branco/nulo ou não votaria".
- **Segmentos combinados**:
  - Ipespe junta branco, nulo e não votou num só segmento, registrado como `branco_nulo` com nota.
  - Quaest junta não votou e branco/nulo, registrado como `nao_votou` com nota.

### Convenções dos outros arquivos

- **`rejeicao.csv`**: a `observacao` traz campo, registro TSE e a pergunta. As perguntas diferem muito entre institutos e até entre rodadas do mesmo instituto (ver "Rejeição" abaixo). O Datafolha pós-1º turno tem duas medidas, marcadas com `medida=`.
- **`perfil_outros.csv`**: a `observacao` começa com `leitura=intencao_no_segmento` (por exemplo, "Renan tem 23,4% entre 16 e 24 anos") ou `leitura=composicao` (por exemplo, "entre eleitores de Cury, 40,2% aprovam Lula"). Algumas linhas da AtlasIntel são `leitura=total_amostra` (imagem no eleitorado total).
- **`apoios.csv`**:
  - `posicao` ∈ `Lula`, `Flávio`, `neutro`, `liberou`. Fica em branco quando a posição não foi encontrada (Avante nacional).
  - O PCO orienta **voto nulo**: entrou como `neutro`, com o aviso na `observacao`.
  - Apoios condicionados (Cury, Clariana Barão, Wilson Grassi) estão marcados na `observacao`.
  - A citação tem no máximo 15 palavras e é literal.

## Como foi feito

1. **Divisão por instituto.** O trabalho foi feito em quatro frentes em paralelo, mais uma para os apoios:
   - A: Datafolha, Quaest e AtlasIntel;
   - B: PoderData, Nexus, MDA e Ipespe;
   - C: Futura, Gerp e Palver;
   - D: Vox, DataTrends, Indexa, Ideia, Real Time Big Data, Alfa, Veritá, Instituto França, Phoenix, Ranking e American Analytics;
   - apoios, governadores e conferência final.
2. **Leitura.**
   - Os PDFs foram lidos como texto (`pdftotext -layout` ou PyMuPDF).
   - As páginas de gráfico, comuns em AtlasIntel, Palver, Ideia, Nexus, MDA e PoderData, foram renderizadas em PNG e lidas na imagem. Os números-chave foram conferidos em recorte ampliado.
   - Páginas HTML foram lidas pedindo os números literais. Os resumos automáticos de busca erraram várias vezes, então nenhum número veio deles.
3. **Prioridade.**
   - Primeiro, todas as 41 pesquisas do índice divulgadas depois do 1º turno.
   - Depois, as rodadas de agosto a setembro (transferência e rejeição).
   - Por último, a última pesquisa de 1º turno de cada instituto (perfil).
4. **Regras.**
   - Nada foi estimado.
   - Número não confirmado ficou em branco, com a razão.
   - Divergências estão na `observacao` e abaixo.
   - As únicas contas feitas aqui são as médias e os intervalos do "Retrato rápido". São médias simples de percentuais publicados, sem ponderar por amostra ou método.

## Retrato rápido: para onde vai o eleitor de cada candidato (pesquisas depois do 1º turno)

Votos totais e voto declarado no 1º turno. "Todas" é a média simples de todas as medições. "Última" usa só a medição mais recente de cada instituto (7 institutos). Em todas as pesquisas os segmentos são pequenos (n efetivo abaixo de 100 ou não publicado, margem de 10 a 24 p.p.).

| Eleitor de | Medições (institutos) | Lula: média [mín–máx] | Flávio: média [mín–máx] | Branco/nulo: média [mín–máx] |
|---|---|---|---|---|
| Cury, todas | 15 (7) | 42,3 [27–64] | 43,0 [30–56] | 10,9 [2–30] |
| Cury, última | 7 | 45,8 [31–52,1] | 41,4 [33–50] | 9,4 |
| Renan, todas | 15 (7) | 26,9 [9,1–41] | 44,6 [33,5–90,9] | 27,4 [12–43] (14 medições) |
| Renan, última | 7 | 27,0 [9,1–39] | 49,1 [33,5–90,9] | 25,4 |
| Caiado, todas | 15 (7) | 26,2 [15–44] | 53,2 [42–69,8] | 15,4 [2–33] |
| Caiado, última | 7 | 27,9 [18–44] | 55,4 [44–69,8] | 12,3 |
| Zema | 3 (3) | 10,7 [0–22,2] | 76,6 [72–80] | 13,5 |
| Cury + Renan + Caiado + Zema somados | 3 (2: Datafolha 08/10 e 15/10, Ideia 21/10) | 30,3 [27–32] | 50,0 [46–58,1] | 15,6 [8,8–23] |
| Não votou no 1º turno, última | 3 (AtlasIntel, PoderData, Quaest*) | 47,9 [40–55,7] | 38,4 [36–40,2] | 12,1 |
| Fidelidade (eleitor de Lula → Lula; de Flávio → Flávio) | 10 (4) | 95,7 [92–99] | 96,2 [92–100] | — |

\* Na Quaest, o grupo "não votou" inclui quem votou branco ou nulo.

As medições que sustentam os números, segmento por segmento (Lula / Flávio / branco-nulo / não sabe):

| Pesquisa | Campo | Cury | Renan | Caiado |
|---|---|---|---|---|
| AtlasIntel 09/10 (BR-03663) | 03–08/10 | 50,4 / 38,9 / 10,7 | 28,1 / 40,3 / 31,6 | 26,9 / 54,9 / 18,2 |
| AtlasIntel 19/10 (BR-02418) | 13–18/10 | 52,1 / 42,4 / 5,6 | 31,9 / 33,5 / 34,6 | 24,5 / 69,8 / 5,7 |
| PoderData 08/10 (BR-08134) | 05–07/10 | 27 / 56 / 11 / 6 | 25 / 48 / 27 / 1 | 19 / 57 / 17 / 6 |
| PoderData 13/10 (BR-01209) | 10–12/10 | 43 / 45 / 8 / 4 | 33 / 38 / 27 / 2 | 30 / 44 / 14 / 12 |
| PoderData 16/10 (BR-04258) | 13–15/10 | 36 / 47 / 13 / 5 | 24 / 46 / 24 / 5 | 30 / 50 / 10 / 10 |
| PoderData 19/10 (BR-02586) | 16–18/10 | 31 / 56 / 9 / 4 | 29 / 36 / 29 / 6 | 19 / 46 / 25 / 11 |
| PoderData 22/10 (BR-07926) | 19–21/10 | 48 / 42 / 8 / 2 | 34 / 49 / 17 / 1 | 30 / 49 / 20 / 1 |
| Ipespe 10/10 (BR-00933) | 06–08/10 | 29 / 50 / 14 / 7 | 20 / 36 / 32 / 12 | 15 / 56 / 26 / 4 |
| Ipespe 17/10 (BR-00223) | 13–15/10 | 31 / 50 / 3 / 17 | 20 / 40 / 32 / 8 | 18 / 59 / 6 / 18 |
| Nexus 13/10 (BR-07997), fonte secundária | 10–12/10 | 41 / 43 / 13 / 4 | 30 / 37 / 33 / 0 | 27 / 55 / 11 / 7 |
| Quaest 14/10 (BR-08729) | 10–13/10 | 34 / 30 / 30 / 6 | 14 / 40 / 43 / 3 | 23 / 42 / 33 / 2 |
| Quaest 21/10 (BR-08535) | 17–20/10 | 48 / 33 / 16 / 3 | 25 / 51 / 24 | 21 / 57 / 22 |
| Palver 15/10 (BR-08028) | 10–13/10 | n=109: 64 / 32 / 2 / 2 | n=134: 41 / 41 / 18 / 0 | n=54: 35 / 61 / 2 / 1 |
| Palver 21/10 (BR-04612) | 18–20/10 | n=99: 52 / 43 / 5 / 0 | n=113: 39 / 42 / 12 / 7 | n=57: 44 / 44 / 11 / 1 |
| Ideia 21/10 (BR-08251) | 15–19/10 | n=58: 48,3 / 36,2 / 15,5 | n=33: 9,1 / 90,9 | n=39: 30,8 / 53,8 / 10,3 |

O que os números mostram (com a cautela dos segmentos pequenos):

- **Cury divide.**
  - Na última rodada de cada instituto, Lula está à frente em 5 de 7: AtlasIntel, PoderData, Quaest, Palver e Ideia.
  - Flávio está à frente no Ipespe e, por pouco, na Nexus de 13/10.
  - No PoderData, o eleitor de Cury oscila de 27 a 48% para Lula entre rodadas.
- **Renan vai mais para Flávio, mas tem a maior fatia de branco/nulo** (cerca de 1/4 a 1/3).
  - A Ideia (n=33, 91% Flávio) é o ponto fora da curva. Sem ela, Flávio fica entre 33,5 e 51.
  - Na Palver, o eleitor de Renan ia 63 a 68% para branco/nulo antes do 1º turno e passou a se dividir meio a meio depois.
- **Caiado vai para Flávio**: cerca de 55 a 25 nas últimas rodadas. A exceção é a Palver de 21/10, empatada em 44 × 44.
- **Quem não votou no 1º turno pende para Lula**: AtlasIntel 55,7 × 40,2, PoderData 48 × 39, Quaest 40 × 36.
- **Quem votou branco/nulo**: AtlasIntel 21,1 × 38,7 (40,2 de branco/nulo), PoderData 22/10 46 × 23 (7 bnu, 24 não sabe).

### Antes do 1º turno (simulações de agosto a 03/10, intenção no 1º turno)

| Eleitor de | Medições (institutos) | Lula: média [mín–máx] | Flávio: média [mín–máx] | Branco/nulo |
|---|---|---|---|---|
| Cury | 19 (5: Datafolha, Ideia, Nexus, Palver, Quaest) | 31,1 [22–55,6] | 40,3 [27,8–54] | 27,5 |
| Renan | 20 (6: + Gerp) | 12,4 [4–28] (19 medições) | 46,9 [19–82,2] | 41,6 |
| Caiado | 17 (5) | 26,5 [9–36,8] (16 medições) | 45,4 [26,4–54] | 25,7 |
| Zema | 13 (4) | 18,4 [8–37,7] (11 medições) | 62,4 [47,8–77] | 20,1 |

Comparando antes e depois do 1º turno: Lula ganhou terreno entre o eleitor de Cury (31 → 42) e de Renan (12 → 27), e o branco/nulo de Renan caiu (42 → 27). São perguntas diferentes (intenção × voto declarado) e institutos em parte diferentes. Por isso, é sinal, não medida.

## Rejeição

Série completa em `rejeicao.csv`. **Não junte institutos numa série única**, porque as perguntas são diferentes:

- **Múltipla, "não votaria de jeito nenhum"**: Datafolha pré-1º turno, AtlasIntel, PoderData, Nexus, Palver, Ideia, Futura e Gerp pré-1º turno, Vox até 29/09, Real Time Big Data até 01/10.
- **Só os dois nomes ou resposta única com "ambos"**: Futura e Gerp pós-1º turno, Vox 09/10 e 18/10, Real Time Big Data 20/10 (35 × 33, com "rejeito ambos" 28). A queda nesses institutos vem da troca de pergunta.
- **"Conhece e não votaria"**: Quaest, American Analytics. "Jamais votaria" na escala de potencial: Indexa.
- **Datafolha depois do 1º turno**: duas medidas. "Não votará de jeito nenhum": Flávio 46 → 47 e Lula 49 → 49 (08/10 → 15/10). Rejeição exclusiva (só um dos dois), que é o número noticiado pela Folha: Lula 46 e 46, Flávio 43 e 44. Em 22/10 só foi achada a exclusiva: Flávio 46 e Lula 45 (Poder360). O Terra diz 48 e 48.

Resumo, Lula / Flávio, última antes do 1º turno → última depois:

| Instituto | Antes do 1º turno | Depois do 1º turno |
|---|---|---|
| PoderData | 03/10: 47 / 46 | 22/10: 47 / 45 |
| Quaest | 21/09: 55 / 56 | 21/10: 47 / 52 |
| Nexus | 28/09: 48 / 51 | 19/10: 47,8 / 46,8 |
| MDA | 03/10: 47,6 / 51,7 | 16/10: 48,8 / 46,6 |
| Palver | 29/09: 51 / 48 | 21/10: 49 / 47 |
| Futura | 03/10: 46,9 / 43,1 | 19/10: 47,4 / 45,8 |
| Gerp | 03/10: 50 / 43 | 16/10: 49 / 46 (pergunta mudou) |
| Datafolha | 01/10: 45 / 45 | 15/10: 49 / 47 (não votará de jeito nenhum) |
| AtlasIntel | 23/09: 51,6 / 50,6 | não perguntou |
| Ipespe | — | 17/10: 47 / 47 |
| Ideia ("poderia votar") | 30/09: 49 / 48 | 21/10: 47,7 / 46,5 |
| Indexa | 30/09: 50 / 51 | 15/10: 50 / 51 (fonte única) |

- **Na maioria dos institutos, a rejeição de Flávio caiu depois do 1º turno e ficou igual ou abaixo da de Lula.** As exceções são Quaest (Flávio 52 × Lula 47 em 21/10, embora a de Flávio tenha caído de 56) e Indexa (51 × 50, igual a 30/09).
- **Rejeição entre eleitores dos outros candidatos.** Só o Datafolha de 15/10 publicou, e só para o agregado de quem votou em Cury, Renan, Caiado ou Zema: rejeitam só Lula 42, só Flávio 27, os dois 14, nenhum 16. Nenhum outro instituto cruza a rejeição pelo voto no 1º turno.
- **Rejeição de Cury, Renan e Caiado no eleitorado total** está no CSV (Nexus, MDA, AtlasIntel, Palver, Futura, Gerp, Vox, Ideia, Real Time Big Data, Indexa, Quaest, American Analytics e Veritá). Na Palver ela caiu ao longo de setembro: Renan 45 → 33, Caiado 41 → 30, Cury 37 → 28.

## Apoios declarados (resumo de `apoios.csv`)

**Candidatos derrotados:**
- **Augusto Cury (Avante):**
  - Na noite de 04/10 ficou neutro, sem citar os finalistas.
  - Em 08/10 declarou **apoio condicionado a Flávio** ("voto de confiança condicionado"). Flávio assinou oito compromissos, entre eles o fim da reeleição.
  - A direção nacional do Avante não se manifestou (nada de Luis Tibé). Os diretórios do PI e da BA ficaram com Lula, segundo a Sputnik Brasil (fonte única).
- **Renan Santos (Missão):** **liberou** o eleitor em 04/10 ("o Flávio Bolsonaro é um bandido e o Lula é um bandido"). Reafirmou em 07/10 ("asco" de Flávio) e em 08/10. Não pediu voto nulo e prevê vitória de Flávio. Não há nota própria do Missão.
- **Ronaldo Caiado (PSD):** apoio a **Flávio** em 06/10, em Goiânia, com Tarcísio e Daniel Vilela. O **PSD ficou neutro**: nota de Kassab em 04/10, que libera diretórios e filiados.
- **Romeu Zema (Novo):** **Flávio** em 05/10. O Novo formalizou em 07/10.
- **Clariana Barão (DC):** **Flávio** em 07/10, condicionado às pautas de mulheres e crianças.
- **Wilson Grassi (Democrata):** **Flávio** em 14/10, condicionado a cinco compromissos da causa animal.
- **Hertz Dias (PSTU):** **Lula** em 07/10, com "voto crítico".
- **Edmilson Costa (PCB):** **Lula**, com apoio crítico.
- **Samara Martins (UP):** **Lula**.
- **Rui Costa Pimenta (PCO):** **voto nulo**, decidido em 11/10.

**Partidos:**
- **Com Flávio:** União Progressista (União Brasil + PP, 06/10, unânime), Republicanos (07/10, "não é um cheque em branco"), Novo (07/10), Podemos (07 ou 08/10, sem fechar questão) e MDB (13/10, 17 de 27 diretórios; 10 diretórios do Norte e Nordeste com Lula).
- **Neutros ou liberados:** PSD (04/10) e PSDB (nota de Aécio Neves, publicada em 08/10).
- **Com Lula:** a coligação de Lula desde o 1º turno (PT, PSB, PDT, PCdoB, PV, PSOL, Rede), mais PSTU, PCB e UP no 2º turno.

**Governadores eleitos no 1º turno** (levantamento do O Povo, 16/10; o Mais Goiás de 14/10 dá a mesma contagem, mas devolveu 403):
- **12 com Flávio:** GO, MT, MS, MG, PA, PR, RJ, RS, RO, RR, SC e SP.
- **5 com Lula:** BA, CE, PB, PI e SE, todos do Nordeste.
- **4 neutros:** AL, AP, MA e PE.

Os candidatos a governador em 2º turno também estão no CSV, marcados como "não eleito ainda".

**O eleitor segue o apoio?** A Vox Brasil de 09/10 (BR-09623/2026, p.13) perguntou ao total da amostra: "Se o candidato em quem você votou no primeiro turno declarar apoio a Lula ou Flávio Bolsonaro, você seguirá essa orientação?". As respostas:
- sim, 17,2%;
- não, manterei minha própria escolha, 63,4%;
- depende de qual candidato receber o apoio, 15,2%;
- ainda não sei, 2,6%;
- não sabe, 1,6%.

O relatório não traz o cruzamento só com eleitores de Cury, Renan e Caiado. Fonte: <https://static.poder360.com.br/uploads/2026/10/pesquisa-vox-brasil-9out2026.pdf>.

## Perfil dos eleitores de Cury, Renan e Caiado (o que existe em `perfil_outros.csv`)

- **Intenção no segmento, última pesquisa antes do 1º turno:**
  - AtlasIntel 03/10: sexo, escolaridade, idade, região, renda, religião e **voto em 2022**. Renan tem 23,4% entre 16 e 24 anos, 15,1% no Norte, 48,8% entre quem votou branco/nulo em 2022 e 25,4% entre quem não votou em 2022.
  - PoderData 03/10: sexo, idade, instrução, região, renda e religião.
  - Nexus 28/09: inclui voto em 2022 e avaliação do governo. Cury tem 4% tanto entre eleitores de Lula 2022 quanto de Bolsonaro 2022; Caiado 4% e 5%; Renan 2% e 5%.
  - Real Time Big Data 01/10, Gerp 03/10, Palver 29/09 (Onda 5) e Futura 24/09.
- **Composição, depois do 1º turno:** aprovação de Lula e do governo entre os eleitores declarados de cada um. AtlasIntel 09/10 e 19/10, PoderData nas 5 rodadas.
  - Em 19/10, na AtlasIntel, os eleitores de Cury aprovam Lula 40,2 e desaprovam 55,5; os de Caiado, 16,7 e 80,3.
  - No Datafolha de 15/10, entre eleitores de Cury, 60 desaprovam e 32 aprovam (margem de 11 p.p.).
- **Imagem no eleitorado total:**
  - AtlasIntel 23/09, positiva / não sabe / negativa: Cury 28/32/40, Caiado 35/22/43, Renan 18/22/60, Zema 35/16/49.
  - Potencial e "não conhece": Palver, Indexa e American Analytics.
- **Comparação com 2022:**
  - AtlasIntel 03/10 e Nexus 28/09 medem o voto nos três por voto em 2022.
  - A Indexa (15/10 e 22/10) cruza o 2º turno de 2026 pelo voto em 2022. 15/10: eleitores de Bolsonaro 2022 dão Flávio 91,6 e Lula 2,6; eleitores de Lula 2022 dão Lula 88,2. 22/10: 90,5 e 4,7; 90,1 e 4,9.
  - **Nenhum instituto publicou a composição dos eleitores de Cury, Renan ou Caiado por voto em 2022** (por exemplo, "X% dos eleitores de Cury votaram em Lula em 2022"). Só existe a leitura inversa.
- **Outros indicadores fora do CSV** (detalhes nas notas por grupo):
  - Voto útil (Real Time Big Data 01/10): "pode deixar de votar no seu candidato se ele não tiver chance". Responderam sim 48% dos eleitores de Cury, 16% de Renan, 53% de Caiado e 55% de Zema.
  - Ideia 30/09, entre eleitores dos candidatos menores: 63,4% "nem pensam em votar em Flávio no 1º turno".
  - Gerp 03/10: voto totalmente decidido para 77% dos eleitores de Cury (n=95), 76% dos de Caiado (n=85) e 74% dos de Renan (n=49), contra 92 a 93% nos de Lula e Flávio.

## Comparecimento (`comparecimento.csv`)

- **PoderData 22/10:** 95% dizem que com certeza vão votar no 2º turno. Por voto no 1º turno: Flávio 99, Lula 97, Cury 92, Renan 92, Caiado 85. Entre quem não votou no 1º turno, 69% com certeza e 11% não vão votar.
- **Ipespe:** nota 10 de chance de votar para 88% (10/10) e 89% (17/10). Nesse grupo, Flávio tem 53,1 e 52,2 dos válidos.
- **Vox:** 81,6% com certeza (09/10) e 76,5% (18/10, outra pergunta).
- **Indexa:** "não iria votar" 8% (15/10) e 4,8% (22/10).
- **Palver 15/10**, entre quem não votou no 1º turno (n=359): motivo principal viagem/fora do domicílio (37%); voto hipotético Lula 59, Flávio 28.
- **Alerta:** todas as amostras têm muito menos gente que se absteve do que a abstenção real de 21,1% (por exemplo, 10% no PoderData 22/10 e 5,9% na Ideia 21/10). Quem falta está sub-representado, e o comparecimento declarado está inflado.
- Datafolha, Quaest, AtlasIntel, Futura, Gerp, MDA e Nexus (outubro): não mediram intenção de comparecer no 2º turno.

## Fontes principais da transferência (pós-1º turno)

| Pesquisa | Fonte lida |
|---|---|
| AtlasIntel 09/10 e 19/10 | <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Pesquisa-Atlas_Bloomberg-Nacional-261009.pdf> e <https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2026/10/Pesquisa-Atlas_Bloomberg-Nacional-261019.pdf> (p.9) |
| Datafolha 08/10 | reportagem da Folha em PDF no Poder360: <https://static.poder360.com.br/uploads/2026/10/datafolha-presidente-2turno-8out2026.pdf> |
| Datafolha 15/10 | relatório completo: <https://static.poder360.com.br/uploads/2026/10/datafolha-15out2026-pesquisa-nacional.pdf> (p.5) |
| PoderData (5 rodadas) | `https://static.poder360.com.br/uploads/2026/10/Relatorio-PoderData-Eleitoral-{8out26-final,12out26-2,15out26,18out26,21out26-2}.pdf` (p.10) |
| Ipespe 10/10 e 17/10 | <https://ipespe.org.br/wp-content/uploads/2026/10/TCK-CAMPANHA-01_-IPESPE-ABRAPEL_2T_-6-a-8-OUT-2026_vf.pdf> e <https://ipespe.org.br/wp-content/uploads/2026/10/TRK-CAMPANHA-02_-IPESPE-ABRAPEL_2T_-13-a-15-OUT-2026.pdf> (p.7) |
| Palver 15/10 e 21/10 | <https://static.poder360.com.br/uploads/2026/10/pesquisa-palver-presidente-nacional-15out2026-1.pdf> e <https://static.poder360.com.br/uploads/2026/10/pesquisaPalver-presidente-21out2026_compressed-compactado.pdf> |
| Ideia 21/10 | <https://www.canalmeio.com.br/wp-content/uploads/2026/10/Pesquisa-Meio_Ideia-Outubro.pdf> (p.10) |
| Quaest 14/10 | InfoMoney (<https://www.infomoney.com.br/politica/quaest-transferencia-de-votos-lula-flavio/>), Exame, TVT News e Poder360. Relatório e g1 não abriram. |
| Quaest 21/10 | Exame (<https://exame.com/brasil/para-onde-vao-os-votos-de-cury-caiado-e-renan-no-2o-turno-pesquisa-quaest-responde/>) e Jovem Pan (<https://jovempan.com.br/politica/caiado-cury-renan-quantos-votos-foram-transferidos-para-lula-e-flavio-segundo-a-quaest/>) |
| Nexus 13/10 (secundária) | NC News (<https://ncnews.com.br/2026/10/13/btg-nexus-flavio-atrai-80-dos-eleitores-de-zema-e-55-dos-de-caiado-veja-como-votam-os-demais/>) e Tribuna de Jundiaí. O estudo completo exige cadastro. |

Antes do 1º turno, as fontes de cada linha estão no CSV:
- Nexus: 9 relatórios. Os de 14/09 e 21/09 foram achados agora e não estão no índice: <https://www.canalmeio.com.br/wp-content/uploads/2026/09/BTG-Nexus-Eleicoes-2026-Rodada-14-versao-executiva-14.set_.2026.pdf> e <https://static.poder360.com.br/uploads/2026/09/BTG-Nexus-nacional-21set2026.pdf>.
- Palver: Ondas 2v1, 3, 4 e 5.
- Gerp: 11/08 e 29/09, também fora do índice. 11/08: <https://static.poder360.com.br/uploads/2026/08/PRESIDENCIA_DO_BRASIL_DIVULGACAO_26a_Relatorio_Eleicoes_2026_Presidente.pdf>. 29/09: <https://static.poder360.com.br/uploads/2026/09/pesquisa-gerp-29set2026.pdf>.
- Gerp 03/10.
- Datafolha: relatório de 17/09, g1 em PDF de 01/10, SBT, Tribuna de Jundiaí e CartaCapital.
- Quaest 03/10: g1 em PDF no Poder360.
- Ideia 30/09.

## Lacunas

**Pesquisas pós-1º turno sem cruzamento por voto no 1º turno** (24 das 41 do índice; as outras 17 têm cruzamento, sendo 2 do Datafolha só com o agregado):
- **Datafolha 22/10**: não achado. O **Datafolha 08/10 e 15/10** traz só o agregado dos quatro derrotados, sem Cury, Renan e Caiado separados nem fidelidade.
- **Nexus 19/10**: estudo atrás de cadastro, e nenhuma matéria trouxe o cruzamento.
- **MDA 16/10.**
- **Futura 13/10, 16/10, 19/10 e 21/10.**
- **Gerp 13/10, 16/10 e 21/10** (o PDF de 21/10 não foi achado).
- **Vox 09/10 e 18/10.**
- **DataTrends 11/10 e 19/10.**
- **Indexa 15/10 e 22/10** (cruzam por voto em 2022).
- **Real Time Big Data 20/10.**
- **Alfa 20/10.**
- **Veritá 05/10, 17/10 e 21/10.**
- **Instituto França 20/10.**
- **Phoenix 19/10** e **Ranking 20/10.**

**Segmentos e dados que ninguém publicou:**
- Fidelidade de Lula e Flávio na Quaest, no Datafolha e na Palver.
- Zema separado depois de 13/10 (fica em "outros").
- O n dos segmentos em AtlasIntel, Datafolha, Quaest, PoderData, Ipespe e Nexus.
- Cruzamentos em votos válidos.

**Antes do 1º turno, sem transferência:**
- AtlasIntel (todas as rodadas), PoderData (7 rodadas), MDA (3), Futura (7), Vox, Real Time Big Data, Indexa, DataTrends, Alfa, Veritá, França e American Analytics.
- Quaest de 05/08 a 28/09: o g1 é bloqueado e as reproduções não trazem o cruzamento.
- Datafolha 03/09, 11/09 isolada e 03/10.

**Rejeição não encontrada:**
- Quaest 05/08, 14/08, 28/09 e 03/10.
- Datafolha 03/10, e 22/10 na medida "não votará de jeito nenhum".
- AtlasIntel depois de 23/09 (não perguntou).
- Futura 11/09 e 21/10; Gerp 21/10; Palver 03/10; Indexa 26/08 e 22/10; Vox 02/10.

**Perfil:** nada de Datafolha e Quaest para a última pesquisa antes do 1º turno.

**Apoios não encontrados:**
- Nota da direção nacional do Avante e do Agir (coligação de Cury).
- Nota própria do Missão, do DC e do Democrata (só as falas dos candidatos).
- Solidariedade, PRD e Cidadania.
- Ciro Gomes (PSDB): até 08/10 não tinha se posicionado (O Povo).
- Professora Maria do Carmo (PL-AM).
- Datas exatas das falas de PCB e UP.

## Divergências registradas

- **Quaest 21/10, Caiado:** Exame, Jovem Pan e InfoMoney dão Caiado 21/57/22 e Renan 25/51/24. BPMoney e SpaceMoney trocam os números de Caiado e Renan. Ficou a versão das três primeiras.
- **Nexus 13/10, Zema:** a NC News dá Lula 0, Flávio 80, branco/nulo 12, NS 8 (adotada, soma 100). A Tribuna de Jundiaí diz que 12% preferem Lula.
- **Datafolha 08/10:** o campo é 06–07/10 na Folha e 06–08/10 em DGABC, O Liberal e Terra. O Diário de Pernambuco atribui ao total os 15% de branco/nulo do grupo dos derrotados.
- **Datafolha 22/10, rejeição:** Poder360 dá Flávio 46 e Lula 45, Terra dá 48 e 48.
- **Datafolha 17/09, Cury:** 44 Flávio e 32 Lula na rodada; 41 e 35 na análise da SBT que soma 08–10/09 e 15–17/09. As duas estão no CSV.
- **PoderData:** a partir de 16/10, a ponderação inclui o resultado do 1º turno. As rodadas de 08/10 e 13/10 não são diretamente comparáveis às seguintes.
- **AtlasIntel 09/10:** o campo começa em 03/10, véspera do 1º turno.
- **Gerp 11/08, rejeição de Cury:** 8 no relatório e 6 na série histórica (ficou 8). **Gerp 29/09:** não sabe 1 no texto e 2 no quadro.
- **Palver Onda 2:** as versões 1 e 2 (recalibrada) dão rejeições diferentes; as duas estão no CSV. No segmento de Renan da v1, o n de 899 é alto porque filiados ao Missão estavam sobrerrepresentados (motivo da recalibração).
- **Podemos:** DGABC dá o anúncio em 07/10; TNH1/O Globo dá a confirmação em 08/10.
- **Augusto Cury:** o apoio é de 08/10 no g1. O corpo do Diário do Nordeste diz "quinta-feira (6)" e o da Bahia Notícias "quinta-feira (10)".
- **Renan Santos:** a matéria da DGABC/AE de 07/10 diz que o 1º turno foi "domingo, 7" (erro; foi 04/10).
- **Vox 18/10:** o relatório primário existe e confirma os válidos 51 × 49, que o índice marcava como não confirmados: <https://static.poder360.com.br/uploads/2026/10/RELATORIO-VOX-BRASIL-NACIONAL-10-2-TURNO-18-10-2026.pdf>.

## Alertas e incidentes

- **Conteúdo da web tratado como dado:** duas páginas da CNN Brasil traziam um pedido embutido para extrair dados. Os dois foram ignorados:
  - Vox 02/10: <https://www.cnnbrasil.com.br/eleicoes/vox-flavio-registra-482-no-2o-turno-lula-452/>
  - Real Time Big Data 24/09: <https://www.cnnbrasil.com.br/eleicoes/real-time-big-data-lula-tem-41-no-1o-turno-flavio-37/>
- **Nenhuma outra instrução embutida** foi encontrada. Os relatórios da Futura trazem um aviso jurídico da Apex Partners contra reprodução: só os números foram usados.
- **Painel de navegador:** ao tentar abrir o PDF da Palver de 15/10 no painel do navegador, o site respondeu com download, e o painel mostrou ao usuário uma janela de "salvar arquivo". Nada foi salvo. Se a janela ainda estiver aberta, pode ser cancelada.
- **Nexus:** o site pede cadastro (nome, e-mail, empresa, cargo) para baixar o estudo completo. Não foi preenchido.
- **Arquivos:** os PDFs foram lidos só como texto ou imagem, e nenhum arquivo baixado foi executado. Os de CNT/MDA, Ipespe e Palver vieram de cópias de uma sessão anterior no scratchpad, com os mesmos nomes das URLs (o site da CNT falha na ferramenta de leitura). O PDF do Ipespe de 17/10 foi baixado de novo e confere com a cópia.
- **Escopo:** nenhuma imagem gerada. Nada foi editado fora desta pasta (além dos rascunhos no scratchpad) e não houve commit.
