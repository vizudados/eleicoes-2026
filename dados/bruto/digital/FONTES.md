# Redes sociais e buscas no Google: fontes, método e lacunas

Levantamento feito entre a noite de 22/10 e a madrugada de 23/10/2026, para as telas "Quem dominou as redes?" e
"O que o Brasil perguntou ao Google?". Todos os CSV usam `;`, UTF-8 sem BOM, datas ISO e ponto decimal.
Número que não foi confirmado ficou **em branco**, com a razão na coluna `observacao`.

## Arquivos

| Arquivo | Linhas | O que tem |
|---|---|---|
| `trends_tempo.csv` | 3.478 | Séries do Google Trends (diárias e por hora), coletadas direto no Trends e na Central Google Trends Eleições 2026 |
| `trends_uf.csv` | 648 | Índice por UF (0-100) e participação % das buscas por UF, 1º e 2º turno |
| `trends_uf_tempo.csv` | 4.760 | Série diária Lula x Flávio (tópicos) em cada uma das 27 UFs e no Brasil, 01/08 a 24/10 (consulta U2, refeita em 24/10, das 21h06 às 22h06, com o dia 24/10 completo) |
| `trends_consultas.csv` | 844 | Consultas principais e em ascensão, perguntas mais buscadas divulgadas pelo Google e pela imprensa |
| `seguidores.csv` | 118 | Seguidores por candidato e rede: base de junho, Social Blade (22/09 a 23/10), imprensa (19 a 22/10), canais de WhatsApp |
| `monitoramento.csv` | 115 | Quaest IPD, Bites, DSC Lab, Datrix, FGV/EAESP, Palver, VigIA (deepfakes), processos e denúncias no TSE |
| `opiniao_redes.csv` | 92 | Datafolha, Genial/Quaest (nacional e RJ), AtlasIntel, Quaest e Indexa sobre IA, Projeto Brief, DataSenado 2024 |
| `anuncios.csv` | 37 | Gastos na Meta: Relatório da Biblioteca de Anúncios (fonte primária), pagamentos declarados ao TSE, InfoMoney |

## Google Trends: como foi coletado

Abri o Google Trends no navegador (trends.google.com, Brasil, pt-BR) e li os dados que a própria página carrega:
os gráficos, os mapas e as listas de consultas. Não baixei arquivos. A Central Google Trends Eleições 2026
(trends.withgoogle.com) traz os dados dos gráficos embutidos no HTML, e foram lidos assim. O banner de cookies do Google
era informativo e foi ignorado, sem aceite.

**O índice é relativo (0-100), nunca volume.** 100 é o ponto mais alto *dentro da mesma consulta*. Só dá para comparar
séries da mesma consulta. Por isso cada série leva o código da consulta no nome (`Lula [tópico | T2]`).

**Regra de leitura das séries diárias: o "dia" do Google vai das 21h da véspera às 21h do dia, no horário de
Brasília.** O Trends agrega a resolução diária em UTC, mesmo com `tz=180`. As séries por hora (H1, H2, H3) e por minuto
vêm no horário de Brasília. A regra vale para T1, T2, S1, S2, E1 e U2, e foi verificada em 24/10/2026 contra a H3 (seção
"Atualização de 24/10/2026", abaixo).
- **A noite do debate da Band (18/10, 20h20 às 22h04) cai no dia "19/10" da série diária.** O "18/10" só pega até as 21h.
- **A noite do debate da Globo (23/10, 21h39 às 23h49) cai no dia "24/10".** O "23/10" termina às 21h, antes do debate.
- **Ao marcar um evento numa curva diária, use o dia do Google, não o do calendário,** para todo evento depois das 21h.
  Valem também a noite do 1º turno e a da apuração.

| Código | Consulta | Período e resolução | Observação |
|---|---|---|---|
| T1 | 5 candidatos como **termos** de pesquisa | 01/08 a 24/10, diária (refeita em 25/10, com o dia 24/10 completo) | "Lula" também é o molusco e o apelido; "Flávio Bolsonaro" não pega quem busca só "flavio". Subestima Flávio |
| **T2** | 5 candidatos como **tópicos** (entidades Google) | 01/08 a 24/10, diária (refeita em 24/10, das 21h05 às 21h46, com o dia 24/10 completo; ver "Refação de 24/10, 21h") | **Use esta para comparar candidatos.** Tópicos: Lula /m/0pc9q, Flávio /g/122pdhqd, Cury /m/07s813b, Renan /g/11gh2ptx5_ (tópico "Renan Santos, Assunto": presumido do candidato), Caiado /m/04fw8x8 |
| S1 | título de eleitor, local de votação, justificar ausência, e-título, onde voto | 01/08 a 24/10, diária (refeita em 25/10, com o dia 24/10 completo) | 100 = "local de votação" em 04/10 |
| S2 | local de votação, justificar voto, justificativa eleitoral, como votar, apuração | 01/08 a 24/10, diária (refeita em 25/10, com o dia 24/10 completo) | "apuração" é 100 em 04/10 e comprime os demais |
| E1 | eleições 2026, segundo turno, pesquisa eleitoral, fake news, inteligência artificial | 01/08 a 24/10, diária (refeita em 25/10, com o dia 24/10 completo) | Os três últimos ficam perto de zero |
| H1 | Lula x Flávio (tópicos) | 01/10 00h a 08/10 00h, por hora (BRT) | Dia do 1º turno |
| H2 | Lula x Flávio (tópicos) | 15/10 00h a 22/10 00h, por hora (BRT) | Inclui o debate da Band (18/10) |
| **H3** | Lula x Flávio (tópicos), 7 dias (`now 7-d`) | 17/10 12h a 24/10 11h, por hora (BRT) | **As duas noites de debate do 2º turno (Band 18/10, Globo 23/10) na mesma consulta.** Média de 5 coletas de 24/10/2026. Ver a seção "Consulta H3" abaixo |
| G2 | Lula x Flávio (tópicos), mapa por UF | 05/10 a 22/10 | Só em `trends_uf.csv` |
| U2 | Lula x Flávio (tópicos), uma consulta por UF (geo=BR-UF) e uma nacional | 01/08 a 24/10, diária (refeita em 24/10) | Só em `trends_uf_tempo.csv`. Ver a seção "Consulta U2" abaixo |
| C1 | Central Google Trends Eleições 2026 | 22/09 a 22/10, diária | Página oficial do Google. Resumo da página: **Lula 56% x Flávio 44%** do interesse em 30 dias |

Cuidados:
- O Trends trabalha com amostra, então uma nova coleta pode mudar alguns pontos. Exemplo: em 04/10, Flávio tem 82 na Central (C1) e 79 na consulta T2.
- 22/10 era o dia em curso na coleta. O dado é parcial e está marcado.
- Em 20 e 21/09, todos os termos de S1 (e 20/09 em S2) vieram zerados: provável falha de coleta do Google, marcada na observação.
- Valor exibido como "<1" foi gravado como 0, com nota.
- "Aumento repentino", nas consultas em ascensão, significa alta acima de 5.000%.
- As consultas relacionadas trazem buscas sobre acusações ("bolsonaro mandou matar lula", "flávio bolsonaro caso ana clara", "flaviorachadinha") porque são o que as pessoas digitaram. Mostram curiosidade, não fato.
- Algumas consultas em ascensão de "título de eleitor" são questões de treinamento de mesário e estão marcadas.

## Consulta U2: Lula x Flávio por UF, dia a dia (coletada em 23/10/2026)

Para a tela de buscas trocar a curva do Brasil pela do estado clicado e para o filtro de período em volta dos dois
debates do 2º turno (Band em 18/10, Globo em 23/10).

**Método.** Mesmo caminho das demais consultas: Google Trends no navegador, Brasil, pt-BR, fuso de Brasília (`tz=180`),
sem login, sem baixar arquivo e sem aceitar cookies (o banner era informativo e ficou sem clique). Foram 28 consultas,
todas com os mesmos dois tópicos (Lula /m/0pc9q e Flávio /g/122pdhqd), de 01/08 a 23/10, resolução diária:

- uma nacional (`geo=BR`), para a curva do Brasil ter a mesma régua das UFs;
- uma por UF (`geo=BR-AC` ... `geo=BR-TO`), as 27.

Em cada página, o gráfico "Interesse ao longo do tempo" monta uma tabela de dados acessível (dia, Lula, Flávio), e foi
ela que li com JavaScript na própria página. Em AC e AL, também li a resposta bruta do widget (`widgetdata/multiline`)
para conferir que os zeros vêm com `hasData=false`. A URL exata de cada consulta está na coluna `fonte_url`.

**Data e hora.** 23/10/2026, das 20h32 (Brasil) às 20h44 (TO), horário de Brasília, uma consulta a cada 20 a 30
segundos. Não houve 429 nem CAPTCHA, e nenhuma UF ficou de fora.

**Formato.** As colunas de `trends_tempo.csv` mais `uf` no fim (`BR` para a nacional). Termos `Lula [tópico | U2]` e
`Flávio Bolsonaro [tópico | U2]`. São 28 consultas x 84 dias x 2 termos = 4.704 linhas.

**Cuidados.**
- **O índice é relativo dentro de cada consulta.** Em cada UF, 100 é o dia de maior interesse *naquela UF* (quase
  sempre Lula em 04/10). A fatia Lula/(Lula+Flávio) vale dentro da UF, mas o índice de uma UF não se compara com o de
  outra: 30 no AC e 30 em SP não são o mesmo volume. Para comparar o tamanho do interesse entre UFs, use o índice por
  UF de `trends_uf.csv`.
- **Picos diferentes.** Em RO o pico 100 é de Flávio em 04/10 (Lula 99), e em RR os dois empatam em 100 nesse dia. Nas
  outras 25 UFs e no Brasil, o 100 é de Lula em 04/10.
- **Zeros nas UFs pequenas.** Quando o volume do dia fica abaixo do mínimo da amostra, o Trends devolve 0
  (`hasData=false`); foi gravado 0, com nota. Acontece muito em RR (41 dias com Lula zerado e 47 com Flávio), AC (33 e
  52) e AP (24 e 48), e menos em RO (5 e 18), TO (5 e 15) e SE (3 e 11). O último zero é de 27/09 (Flávio em RR); de
  23/09 em diante só AC, AP, RR e RO ainda têm algum dia zerado. O 2º turno (05 a 22/10) está completo nas 27 UFs, sem
  nenhum zero. Não apareceu nenhum "<1".
- **Lacuna de 19 a 21/09.** Fora AC, AP e RR, há 12 UFs em que os dois candidatos aparecem zerados em pelo menos um
  desses dias (AM, MS, RO, SE e TO nos três; PI em 20 e 21; DF, MA, PA e RN em 20; AL e ES em 21), mesmo com volume
  normal na véspera. Em outras, só Flávio zera (por exemplo PB nos três dias, GO em 20 e 21). É o mesmo trecho em que S1
  veio zerada: provável lacuna de coleta do Google, marcada na observação. Em AC, AP e RR não dá para separar a lacuna
  do volume baixo, e a nota diz isso. A série nacional não zera nesses dias.
- **23/10 é parcial.** Era o dia em curso, lido antes do debate da Globo (21h20). Está marcado e deve ser refeito
  depois do debate. Os números de 23/10 não pegam o debate.
- **Amostra.** A nacional U2 repete T2 em 130 dos 166 pontos de 01/08 a 22/10, com diferença máxima de 2 pontos
  (Lula 37 x 35 em 21/10; Flávio 81 x 79 em 04/10). É a variação de amostra já citada acima.

**Conferência com G2.** Somando a série diária de 05 a 22/10 em cada UF, a fatia de Lula fica a 0,8 ponto percentual
de G2, em média, e a no máximo 1,9 ponto (DF). Lula tem mais da metade em todas as 27 UFs, de 53,1% (DF) a 57,5% (MA e
RN). No Brasil, a U2 dá 55,7%. G2 vem arredondado a inteiro.

| UF | Lula U2 | G2 | Dif. | UF | Lula U2 | G2 | Dif. | UF | Lula U2 | G2 | Dif. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AC | 56,4 | 56 | +0,4 | GO | 54,9 | 55 | −0,1 | RJ | 54,3 | 55 | −0,7 |
| AL | 57,2 | 57 | +0,2 | MA | 57,5 | 58 | −0,5 | RN | 57,5 | 58 | −0,5 |
| AP | 56,4 | 55 | +1,4 | MT | 56,0 | 57 | −1,0 | RS | 55,1 | 54 | +1,1 |
| AM | 56,8 | 57 | −0,2 | MS | 55,4 | 56 | −0,6 | RO | 55,2 | 57 | −1,8 |
| BA | 55,6 | 55 | +0,6 | MG | 55,4 | 56 | −0,6 | RR | 53,9 | 55 | −1,1 |
| CE | 56,1 | 55 | +1,1 | PA | 55,5 | 56 | −0,5 | SC | 55,6 | 56 | −0,4 |
| DF | 53,1 | 55 | −1,9 | PB | 56,5 | 56 | +0,5 | SP | 55,5 | 56 | −0,5 |
| ES | 55,3 | 55 | +0,3 | PR | 55,8 | 55 | +0,8 | SE | 56,7 | 56 | +0,7 |
| BR | 55,7 | – | – | PE | 56,7 | 55 | +1,7 | TO | 55,8 | 55 | +0,8 |
|  |  |  |  | PI | 56,4 | 58 | −1,6 |  |  |  |  |

Nenhuma página consultada nesta coleta trazia instruções dirigidas ao agente.

## Achados principais (com fonte)

**Buscas**
- Pico de toda a série: 04/10, dia do 1º turno. Por tópico (T2): Lula 100, Flávio 79. Por hora (H1), Flávio chega a 100 às 17h (fechamento das urnas) e Lula a 94.
- Média 01/08 a 22/10, calculada da série T2: Lula 12,8 x Flávio 9,0. Na campanha do 1º turno (16/08 a 03/10): 7,7 x 4,0. No 2º turno (05 a 22/10): 31,0 x 24,9.
- Flávio passou Lula em 19/10, dia seguinte ao debate (49 x 48), e em 22/10 (32 x 29).
- Debate da Band (18/10), H2: Lula 100 às 21h; Flávio 91 às 22h. A Datrix (via Exame) cita picos minuto a minuto: Lula 85 às 20h44, Flávio 100 às 22h04.
- Por UF (tópicos), Lula tem a maior fatia das buscas nas **27 UFs**, no período todo e no 2º turno. No 2º turno, o máximo de Lula é RN 58% e o de Flávio é RS 46%. O índice de interesse pelos dois é maior no Nordeste (PB, RN, PI, BA, PE) e menor no Sul (PR, SC, RS), em RR e em MS.
- Buscas de serviço (S1): "local de votação" é 100 em 04/10, "título de eleitor" 84, "onde voto" 59 e "e-título" 34. "justificar ausência" fica perto de zero: quem justifica busca "justificar voto", "como justificar voto" e "e-título". "local de votação" volta a subir em 17 e 18/10 (46), quando aparece em ascensão a consulta "tse muda local de votação".
- Perguntas: na semana até 08/09, a newsletter do Google lista em 1º lugar "Augusto Cury é candidato a presidente?". Depois do 1º turno, a lista obtida pelo Estadão é liderada por "Quem ganhou a eleição?" e "Quando vai ser o segundo turno?". Na semana até 01/10, o Google ao UOL mostra "Que horas começa a votação eleitoral?" com +550%.

**Redes**
- Seguidores mais recentes (Social Blade, 23/10): Instagram Lula 18,57 mi x Flávio 15,37 mi; TikTok 6,2 mi x 2,5 mi; YouTube 2,43 mi x 1,57 mi; Facebook 7,28 mi x 4,81 mi. X em 19/10 (Datrix): 10,79 mi x 3,8 mi.
- Interações (Bites): na campanha do 1º turno, de 16/08 a 04/10, foram 83,8 mi (Lula) x 73,7 mi (Flávio). No 2º turno, de 05 a 17/10, foram 110,7 mi x 31,3 mi. Nas 24h após o debate, 25,5 mi x 5 mi.
- Seguidores ganhos (Bites/CNN): de 16/08 a 03/10, Flávio +2,19 mi x Lula +1,29 mi. De 04 a 08/10, +1,74 mi x +0,96 mi.
- Quaest IPD: Flávio 80,0 x Lula 70,7 em 04/10, Lula 83,3 x Flávio 76,6 em 19/10.
- Canal de WhatsApp "Exército do Lula" (André Janones): 5 mi (17/10), 8.002.710 (22/10, 11h). "Tropa do Flávio" (Nikolas Ferreira): cerca de 2,1 mi.
- Anúncios na Meta (Relatório da Biblioteca de Anúncios, 22/07 a 19/10): página de Lula R$ 11,22 mi (13.060 anúncios) x página de Flávio R$ 8,04 mi (1.065). Nos últimos 7 dias (13 a 19/10), Flávio R$ 1,09 mi x Lula R$ 0,91 mi.

## Divergências registradas

- **Instagram em 19 a 21/10:** Datrix 17,81 mi x 14,69 mi (19/10); Quaest/Folha "18 mi x 15 mi" (19/10); Mobile Time 18,2 mi x 15,1 mi (21/10); Social Blade 18,57 mi x 15,37 mi (23/10). Cada um usa uma data e uma ferramenta. Todos foram mantidos.
- **Gasto com Meta: duas bases que não batem.** O Relatório da Biblioteca de Anúncios põe a página de Lula à frente em 90 dias (R$ 11,2 mi x R$ 8,0 mi). Os pagamentos declarados ao TSE põem Flávio à frente (R$ 7,45 mi x R$ 2,59 mi; NSC, SBT e g1 convergem). O primeiro mede o que foi veiculado na página, inclusive o que foi pago por partido ou outro CNPJ. O segundo mede pagamentos da campanha à Facebook Serviços Online. As datas de corte também diferem. Não somar nem misturar as duas bases.
- **InfoMoney (21/08 a 19/09):** Lula R$ 4,41 mi x Flávio R$ 702,8 mil. É coerente com a Biblioteca de Anúncios (Lula gastou cedo, Flávio concentrou no fim: R$ 7,33 mi só entre 20/09 e 19/10).
- **Bites, ganhos logo após o 1º turno:** Poder360 (até 07/10) diz Flávio 1,2 mi x Lula 392 mil. CNN (04 a 08/10) diz 1,74 mi x 958 mil. São janelas diferentes.
- **Quaest, fonte de informação política:** a série publicada em 30/07 dá abr/2026 = redes 40, TV 33. A divulgação de 13/05 dá redes 38, TV 35. Provavelmente são rodadas diferentes; vale conferir na Quaest.
- **Crescimento das buscas por candidatos desde 16/08:** "+170%" (Folha PE, SBT) x "triplicaram" (Correio Braziliense). Os dois foram registrados.
- **Debate, volume de menções:** FGV/EAESP dá 1,2 mi para Flávio x 1,17 mi para Lula (empate em volume). A Bites dá 426 mil referências ao debate para Flávio x 288 mil para Lula, mas Lula com 5 vezes mais interações. A métrica e a janela são diferentes.

## Lacunas

- **Seguidores em agosto:** nenhum total publicado ou consultável sem login. O Social Blade só mostra cerca de 30 dias de histórico (desde 22/09) e o histórico do Instagram exige login, que não foi feito. A Bites divulgou só os ganhos desde 16/08. As linhas de 16/08 ficaram em branco. A linha de base mais próxima é de junho (Solon Data via Bahia Notícias).
- **X:** o Social Blade descontinuou o X. O único total recente é o da Datrix (19/10). Não há total de X para Cury, Renan e Caiado.
- **Kwai:** nenhum dado.
- **Quaest IPD:** só pontos soltos de 04 a 19/10, divulgados pela Folha e reproduzidos por outros veículos (o texto da Folha não foi acessado). Não há série diária nem dados de agosto e setembro. A Quaest não publicou o IPD de Cury, Renan e Caiado.
- **Palver:** só o primeiro fim de semana (15 e 16/08). Não há série de menções em WhatsApp no 2º turno. As pesquisas de voto da Palver ficaram fora (são de intenção de voto).
- **FGV ECMI/DAPP, NetLab UFRJ, AP Exata, Nexus, Torabit, Modus, Arquimedes:** nenhum dado quantitativo de 2026 localizado. O dado da FGV usado é da EAESP (Lilian Carvalho, Brandwatch), reproduzido pela Tribuna do Planalto.
- **DataSenado:** não há rodada de 2026. Entrou a de 2024, marcada como referência.
- **Google Ads:** o Google não veicula anúncios político-eleitorais no Brasil. A linha ficou em branco, com a razão.
- **Meta, página do PL em 90 dias:** não localizada nas primeiras 20 páginas da tabela. Só há o gasto de 19/10 (R$ 13.624).
- **Volume absoluto de buscas:** o Trends não divulga.

## Itens vistos e deixados de fora (não confirmados)

- "Mais de 500 mil buscas por 'Flávio miliciano'", atribuído a André Janones no Poder360: o Trends não divulga volume e o número não é verificável.
- "Média diária de mensagens falsas de 196,9 mil para 311,5 mil (UFRJ)": apareceu só num resumo de busca e não foi achado em nenhuma fonte. A matéria do Jornal de Brasília que surgiu na busca é de 2022.
- Saldo de sentimento Datrix do 1º turno (Flávio +31,4, Lula −23,2): visto só num resumo de busca; a página não foi aberta.
- Agregador e26.cog.ia.br: não usado, por não informar metodologia.
- Instituto Oyá (78% creem em fake news emocional), ObservaDF (DF) e Aláfia Lab (2025): fora do escopo nacional de 2026 ou sem fonte primária acessada.
- GazetaSP, Contigo, Revista Oeste e BNews retornaram 403; nada delas foi usado.

## Dados do dia do debate (18/10) para o agente do debate

- Trends por hora (H2): Lula 100 às 21h; Flávio 91 às 22h. Na 2ª feira (19/10), no dia todo, Flávio 49 x Lula 48 (T2).
- Bites, 24h: interações 25,5 mi (Lula) x 5 mi (Flávio). Lula ganhou 176 mil seguidores. Referências ao debate: Flávio 426 mil x Lula 288 mil. Memes e cortes: 9.500 x 7.000. Total de 1,7 mi de citações até 12h de 19/10.
- FGV/EAESP: 2,37 mi de menções, pico de cerca de 330 mil por hora entre 21h e 22h. Negativas: Lula 27%, Flávio 34%. Positivas: Lula 20%, Flávio 11%.
- Quaest: Lula com 95% de 6 mi de comentários nos perfis dos dois no dia. Ganho no Instagram no dia: Lula +178 mil, Flávio +149 mil.
- Datrix: saldo de sentimento em 18/10 de Lula +2,3 e Flávio +2,4.
- O Poder360 diz que o debate teve o maior interesse no Google "da série histórica desde 2004", sem número. Não foi verificado.

## Consulta H3: as duas noites de debate na mesma consulta (24/10/2026)

**Para que serve.** O índice do Trends só compara dentro da mesma consulta. A H2 (15 a 22/10) tem a noite da Band, mas
não a da Globo, e a coleta minuto a minuto da noite da Globo (`trends_debate_globo.csv`, janelas de 4 horas) não tem a
Band. A H3 pega as duas noites numa consulta só: tópicos Lula (`/m/0pc9q`) e Flávio Bolsonaro (`/g/122pdhqd`), Brasil,
7 dias, hora a hora.

**A coleta de 24/10, por volta das 8h, foi descartada.** Ela tinha 338 linhas, de 17/10 08h a 24/10 08h, e três defeitos:
- os dois em 0 às 23h de 18/10, no meio da noite da Band;
- 30 × 16 às 23h de 17/10, sem evento, cercado de 2 × 1;
- a noite da Band invertida em relação à H2 (Flávio 100 às 22h, Lula 67) e a Globo muito abaixo (Lula 23 às 23h), com o
  resto da semana em torno de 2.

Nenhuma das cinco coletas novas repetiu esses números, e nenhum deles bate com a H2. A causa não foi identificada
(provável erro de leitura ou de alinhamento das horas). As linhas foram substituídas, sem duplicar.

**Método.**
- Mesmo caminho das outras consultas: na página do trends.google.com, no navegador, `/trends/api/explore` (token do
  widget TIMESERIES) e depois `/trends/api/widgetdata/multiline`, com `hl=pt-BR`, `tz=180` e `geo=BR`. A página mostrava
  o título "429", mas as chamadas da API responderam normalmente. Não houve CAPTCHA, e nada foi contornado.
- O campo `time` vem em epoch UTC. O horário de Brasília é UTC−3.
- Conferência do fuso:
  - na noite da Band, os picos caem às 21h (Lula) e às 22h (Flávio), as mesmas horas da H2;
  - na noite da Globo, o pico cai às 22h e às 23h, dentro da medição do Ibope (21h39 às 23h49).

**Coletas.** Foram cinco coletas `now 7-d` em 24/10, às 11h58, 12h00, 12h01, 12h08 e 12h15 (horário de Brasília). Às
12h08 houve também uma de controle com janela fixa (`2026-10-17T15 2026-10-24T15`, UTC), que deu exatamente o mesmo que a
`now 7-d` das 12h08 e ficou fora da média.

**Estabilidade.**
- Nas 168 horas comuns às cinco coletas, 9 horas tiveram alguma diferença entre elas, nunca maior que 1 ponto.
- Nas duas noites, das 18h às 2h, a única diferença foi a de Flávio à 1h de 24/10 (13 ou 14).
- **Conclusão: a série é estável o bastante para comparar os picos das duas noites.**

**O que foi gravado.**
- A média das cinco coletas, arredondada para o inteiro mais próximo (meio para cima), porque o modelo lê o índice como
  inteiro.
- 336 linhas, de 17/10 12h a 24/10 11h.
- 24/10 11h é parcial em 3 das 5 coletas e está marcada. Quando as coletas divergiram, a `observacao` traz a faixa.

| hora (BRT) | Lula | Flávio | | hora (BRT) | Lula | Flávio |
|---|---|---|---|---|---|---|
| 18/10 19h | 18 | 13 | | 23/10 20h | 17 | 13 |
| 18/10 20h | 42 | 24 | | 23/10 21h | 28 | 18 |
| **18/10 21h** | **57** | 39 | | 23/10 22h | 72 | 26 |
| **18/10 22h** | 35 | **51** | | **23/10 23h** | **100** | **45** |
| 18/10 23h | 23 | 25 | | 24/10 00h | 38 | 22 |
| 19/10 00h | 18 | 21 | | 24/10 01h | 22 | 13 |

Picos, das 20h à meia-noite:
- **Band, 18/10:** Lula 57 (21h), Flávio 51 (22h).
- **Globo, 23/10:** Lula 100 (23h), Flávio 45 (23h).

**Conferência com a H2.** Reescalando a noite da Band na H3 para Lula às 21h = 100, as horas das 20h às 23h ficam assim:

| hora | H3 reescalada (Lula · Flávio) | H2 (Lula · Flávio) |
|---|---|---|
| 20h | 74 · 42 | 74 · 45 |
| 21h | 100 · 68 | 100 · 70 |
| 22h | 61 · 89 | 57 · 91 |
| 23h | 40 · 44 | 40 · 45 |

As duas consultas contam a mesma noite.

**Para a tela do debate da Globo (T26).**
- O cartão de buscas usa os picos da Globo na H3 (Lula 100, Flávio 45).
- A régua da Band, hoje lida na H2 (100 × 91), vem de outra consulta e só serve para comparar a proporção entre os dois.
  Para comparar o nível das duas noites, a régua precisa ser a noite da Band na H3: Lula 57, Flávio 51.

## Atualização de 24/10/2026 (16h): T2 e U2 até 24/10, e os dias da série diária em UTC

Pedido da sessão principal: o período "Depois da Globo" da tela de buscas ficava vazio, porque a T2 parava em 22/10 e a
U2 em 23/10. As duas foram refeitas como consultas novas, de 01/08 a 24/10, e as séries inteiras foram trocadas, não
anexadas, porque a escala 0–100 muda com o pico.

**Achado de método: os dias da série diária são dias em UTC.** Com `tz=180`, a série hora a hora vem no horário de
Brasília, mas a diária não: cada "dia" vai das 21h da véspera às 21h do dia, no horário de Brasília. A conferência foi
feita com a H3 hora a hora, somando as horas de cada janela:

| dia (rótulo da série diária) | T2 Lula / Flávio | H3, janela UTC (21h–21h) | Flávio/Lula diária | Flávio/Lula UTC | Flávio/Lula no dia de Brasília |
|---|---|---|---|---|---|
| 22/10 | 28 / 30 | 8,8 / 9,9 | 1,07 | 1,12 | 1,13 |
| 23/10 | 34 / 27 | 9,3 / 7,8 | 0,79 | 0,84 | 0,64 |
| 24/10 (parcial) | 100 / 51 | 30,3 / 15,7 | 0,51 | 0,52 | 0,58 |

O salto de 23 para 24/10 também bate: 2,9 vezes na diária e 3,3 na janela UTC, contra 1,3 no dia de Brasília. As
consequências para o painel:
- **O debate da Globo (23/10, 21h39 às 23h49) cai inteiro no dia "24/10"** da série diária. O "23/10" vai até as 21h
  de 23/10 e não tem o debate.
- **O debate da Band (18/10, 20h20 às 22h04) cai quase todo no dia "19/10".** O "18/10" só pega o começo, até as 21h.
  Por isso o "19/10" de Flávio (49 × 49) mistura a noite do debate com a segunda-feira. A frase antiga "na 2ª feira
  (19/10), no dia todo" precisa dessa ressalva.
- **Vale para todas as séries diárias:** T1, T2, S1, S2, E1 e U2. A observação de cada linha nova da T2 e da U2 avisa
  isso.

**Coleta.** Mesmo método das outras: fetch de `/trends/api/explore` e `/trends/api/widgetdata/multiline` na própria
página do Trends, no navegador embutido, com `hl=pt-BR`, `tz=180` e as mesmas palavras-chave e geos das séries antigas.
Foram 3 coletas de cada consulta, e grava-se a média arredondada para inteiro. O "dia em curso" (24/10) está marcado.
- **T2:** às 16h11, 16h14 e 16h19 de Brasília. Dos 415 pontos que se repetem de 01/08 a 22/10, 384 são iguais aos da T2
  antiga e nenhum difere mais de 2.
- **U2 (28 consultas):**
  - rodada 1 das 16h13 às 16h19, sem erro;
  - rodada 2 das 16h19 às 16h24, até o 429 em RO; esperei cerca de 4 minutos e completei RO, RR, SC, SP, SE e TO das
    16h28 às 16h30, com 25 segundos entre consultas;
  - rodada 3 das 16h32 às 16h44, com 25 segundos entre consultas, sem erro.
  - Não houve CAPTCHA, e o 429 não foi contornado.

**Cuidado com o dia parcial.** O 24/10 em UTC, das 21h de 23/10 até a hora da coleta, já tem o debate inteiro, e por
isso disputa o pico com o 04/10, dia do 1º turno:
- **T2:** o 100 foi de Lula em 04/10 nas duas primeiras coletas e de Lula em 24/10 na terceira. Na média, os dois ficam
  em 99.
- **U2:** o 100 passou para Lula em 24/10 em AP, AM, DF, ES, PB, PR, RJ, RS, SC e SP. Em MS e SE os dois dias ficam em
  99, e nas demais UFs continua sendo o 04/10 (Flávio em RO).

Quando o 24/10 vira o 100, a série inteira daquela UF muda de escala: no DF, o 04/10 de Lula caiu de 100 para 65. Por
isso só 54% dos pontos de 01/08 a 22/10 repetem a U2 antiga. Mesmo assim, a fatia Lula/(Lula+Flávio) de 05 a 22/10, que é
o que a tela usa, ficou a no máximo 0,6 ponto percentual da antiga em todas as UFs (Brasil: 55,7% antes, 55,6% agora).
- Onde as coletas divergiram, a observação traz a faixa.
- Zeros com `hasData=false` nas três coletas e a lacuna de 19–21/09 seguem as mesmas notas de antes.

**O que a série diz sobre o debate da Globo (dia "24/10", parcial).** Lula fica com 64,1% (DF) a 70,5% (RO) das buscas
pelos dois em todas as UFs (66,2% no Brasil). Nas outras janelas:
- no "23/10", sem o debate: 53,8% a 59,4%;
- de 05 a 22/10: 53,5% a 57,5%.

Como sempre, isso mede interesse de busca, não voto.

**T1, S1, S2 e E1 também foram refeitas até 24/10** (mesmos termos e URLs, 3 coletas cada, média arredondada, "dia em curso" marcado). A primeira tentativa levou 429 em S1 às 16h50. Esperei 9 minutos e refiz devagar, com 45 segundos entre consultas, das 16h59 às 17h07, sem novo erro. A T1 tem uma coleta das 16h49 e duas de 16h59 e 17h02. Na conferência com as séries antigas, de 01/08 a 21/10:

| série | pontos iguais | maior diferença |
|---|---|---|
| T1 | 378 de 410 | 2 |
| S1 | 374 de 410 | 7 ("onde voto" em 04/10, 59 → 66, no dia do pico) |
| S2 | 409 de 410 | 1 |
| E1 | 402 de 410 | 2 |

Nas quatro, o pico continua em 04/10. No "24/10" parcial, a T1 já chega a 96 com Lula, perto do pico, e com Flávio fica em 15, porque o termo "Flávio Bolsonaro" pega menos buscas que o tópico. Nas outras três, o "24/10" fica longe do pico: "local de votação" está em 29 na S1, e na S2 e na E1 nada passa de 7. A C1 (Central Google Trends) não foi refeita: é outra página, com janela fixa de 30 dias, e continua de 22/09 a 22/10.

**A refazer depois das 21h de 24/10.** Às 21h o dia "24/10" fecha em UTC. Uma coleta depois disso tira a escala do dia
parcial e põe o sábado inteiro na série. Depois, o dia "25/10" (das 21h de 24/10 às 21h do domingo) vai ser o dia da
eleição.

## Refação de 24/10/2026, 21h: T2 e U2 com o dia 24/10 completo

O dia "24/10" do Google fechou às 21h de Brasília, que é 00h UTC. A T2 e a U2 foram refeitas depois disso, para tirar da
série a escala do dia parcial (ver a seção das 16h). A sessão principal decidiu fechar a fila às 22h06.

**Consulta.** Mesmos termos, geos e método. As consultas vão de 01/08 a 24/10. Uma consulta até 25/10 traria o dia
"25/10" com só alguns minutos de dados (Lula 60 × Flávio 31 às 21h05, na escala de 20 a 25/10), sem valor para a série,
e ficou de fora. O 24/10 veio sem a marca de parcial.

**Coletas.**
- **T2:** 3 coletas, às 21h05, 21h20 e 21h46.
- **U2:**
  - rodada 1, das 21h06 às 21h18;
  - rodada 2, das 21h21 às 21h24, até um 429 em GO; esperei 9 minutos e retomei às 21h33, com 40 segundos entre
    consultas;
  - rodada 3, das 21h47 às 22h05.
  - A fila foi parada às 22h06, como decidido. A rodada 3 não chegou a Tocantins, que ficou com a média de 2 coletas (a
    observação de cada linha de TO diz "média de 2 coletas"). As outras 27 consultas têm 3.
  - Não houve CAPTCHA, e o 429 não foi contornado.

**Resultado.**
- **T2:** o pico continua sendo Lula em 04/10 (100). No dia "24/10" completo, Lula tem 82 e Flávio 43. As três coletas
  divergiram em 11 pontos, nunca mais de 2 (24/10 de Lula: 81 a 83).
- **U2:** o 100 de Lula fica no 24/10 no DF, no RJ, no RS e em SC. Nas outras 23 UFs e no Brasil, continua no 04/10 (em
  RO, é Flávio em 04/10).

**Conferência.**
- **T2 nova × T2 das 16h, até 23/10:** 400 de 420 pontos iguais, diferença máxima de 2.
- **T2 nova × T2 original de 22/10, até 21/10:** 379 de 410 iguais, diferença máxima de 2.
- **U2:** a fatia Lula/(Lula+Flávio) de 05 a 22/10 ficou a no máximo 0,5 ponto percentual da U2 original de 23/10 em
  todas as UFs (Brasil: 55,7% antes e 55,3% agora).

**O que a série diz sobre o debate da Globo (dia "24/10", agora completo).** Lula fica com 64,1% (DF) a 68,9% (AM) das
buscas pelos dois em todas as UFs, e 65,9% no Brasil. Nas outras janelas:
- no "23/10", que termina às 21h, antes do debate: 53,3% a 59,1%;
- de 05 a 22/10: 53,2% (DF) a 57,6% (AL).

Como sempre, isso mede interesse de busca, não voto.

**T1, S1, S2 e E1** foram refeitas na manhã de 25/10, também com o 24/10 completo (seção seguinte).

## Refação de 25/10/2026, 8h: T1, S1, S2 e E1 com o dia 24/10 completo

As quatro séries foram refeitas de 01/08 a 24/10 com o dia "24/10" já fechado. Foram 3 coletas de cada, entre 8h24 e 8h31
de Brasília, com 40 segundos entre consultas, sem 429 nem CAPTCHA. Método e notas iguais aos de antes. Cada série foi
trocada inteira, com 425 linhas, e a marca de "dia em curso" do 24/10 saiu.

**Os picos não mudaram:** Lula em 04/10 na T1, "local de votação" na S1, "apuração" na S2 e "eleições 2026" na E1. As três
coletas só divergiram em 2 pontos da T1, de 1 ponto cada.

**O dia "24/10" completo** vai das 21h de 23/10 às 21h de 24/10 e pega o debate da Globo e o sábado.
- T1: Lula 87, Flávio 14.
- S1: "local de votação" 41, "onde voto" 6, "e-título" 5, "título de eleitor" 7.
- S2: tudo perto de zero, porque "apuração" de 04/10 comprime a escala.
- E1: "segundo turno" 8.

**Conferência.**

| série | × refação das 16h (até 23/10) | × série de 22/10 (até 21/10) |
|---|---|---|
| T1 | 389 de 420 iguais, máx. 3 | 367 de 410 iguais, máx. 3 |
| S1 | 380 de 420, máx. 7 | 365 de 410, máx. 5 ("onde voto" em 04/10) |
| S2 | 418 de 420, máx. 1 | 407 de 410, máx. 1 |
| E1 | 414 de 420, máx. 2 | 404 de 410, máx. 1 |

As maiores diferenças ficam nos dias de pico (04/10) e na noite da Band (19/10 na T1, 48 → 51), onde o Google amostra
mais. Agora todas as séries diárias do arquivo (T1, T2, S1, S2, E1 e U2) vão até 24/10 completo. Só a C1 (Central)
continua até 22/10.

## Segurança e acesso

Nenhuma página consultada trazia instruções dirigidas ao agente. Nada pediu login obrigatório para os dados usados:
o Social Blade e o Relatório da Biblioteca de Anúncios da Meta foram lidos sem login. Não aceitei banners de cookies,
não resolvi CAPTCHA, não baixei arquivos e não gerei imagens.


## Brief H — 26/10/2026, noite: redes até o 2º turno, pós-eleição e renda no Datafolha

Pesquisa registrada em 2026-10-26T22:56:53-03:00, horário de Brasília. Esse é o horário do registro dos achados; as horas exatas de cada leitura de página não foram registradas. Somente dois CSV novos e esta seção foram escritos.
Arquivos de `pbi/`, `dados/pbi/`, `video/` e `web/` não foram alterados por esta pesquisa. Sem commit ou push.

### Formato e critério de integração

- `pos_2turno.csv`: mesmas nove colunas, ordem, separador `;` e UTF-8 sem BOM do `monitoramento.csv` bruto. Há 14 valores confirmados e 46 lacunas explícitas. Campo `valor` vazio significa **não encontrado**, nunca zero.
- `../pesquisas/datafolha_2turno_renda.csv`: seis linhas (três faixas x dois candidatos), com as oito colunas iniciais de `perfil_lula_flavio.csv` e metadados adicionais de campo, registro, base e peso amostral.
- Nas lacunas, as datas identificam a janela solicitada, não uma medição observada. A ausência de publicação nesta pesquisa não prova que a empresa não tenha dados privados.
- Não juntar Bites, Projeto Brief, Datrix, HypeAuditor, Ativaweb ou Quaest numa mesma série. Não completar dias ausentes, repetir o último IPD ou somar janelas sobrepostas. O ponto IPD de 19/10 é uma reconfirmação: deduplicar com o existente na integração.
- Todos os horários de notícias abaixo são os exibidos nas páginas, tratados como Brasília. A Meta não informa hora de atualização nem explicita o fuso dos dias na tabela; o horário de registro da pesquisa consta nos CSVs e não deve ser chamado de hora de publicação ou de atualização da fonte.

### 1. Interações nos perfis oficiais — Bites

**Achado novo confirmado:** de **19 a 24/10/2026, com 24/10 parcial**, Lula **92.000.000** e Flávio **24.600.000** interações. X, YouTube, TikTok, Instagram e Facebook, nos perfis oficiais. A fonte não informa a hora de corte desses totais. O horário de meio-dia citado para visualizações de um vídeo não foi transferido para a série de interações.

- [Jamildo, 24/10/2026 às 20h48](https://jamildo.com/politica/debate-da-globo-bites-aponta-ana-clara-e-fala-de-lula-como-destaques-nas-redes.html), análise da Bites intitulada “A véspera do segundo turno”.
- [JC, 24/10/2026 às 17h39](https://jc.uol.com.br/politica/2026/10/24/debate-entre-lula-e-flavio-bolsonaro-gera-15-milhao-de-citacoes-nas-redes-video-sobre-policia-alcanca-67-milhoes-de-visualizacoes.html), mesmo par de valores e mesma janela.

**Não encontrado:** a janela exata 18–25/10, o total de 05–25/10 e as 24 horas depois da eleição. A janela 19–24/10 é o recorte substituto publicado, permitido pelo brief; não equivale ao fechamento solicitado. Não somar 05–17/10, as 24 horas pós-Band e 19–24/10: as horas não fecham nem garantem ausência de sobreposição.

Buscas realizadas, com variações de acentos e datas: `Bites Lula Flávio interações redes sociais outubro 2026 25 26 segundo turno`; `"Bites" "Lula" "Flávio" "26/10/2026"`; `"Bites" "25 de outubro de 2026" "interações"`; `"Bites" "18 a 25" Lula`; `"Bites" "5 a 25" Lula`; `"Bites" "05 a 25"`; `"Bites" Lula Flávio "pós-eleição" "2026"`; `"Bites" "Lula" "Flávio" "24 horas" eleição -debate`.

Consultados resultados e matérias de Jamildo, JC, CNN Brasil, Poder360 e Folha. Resultados de agregadores foram usados apenas como pistas. AP/Projeto Brief (outro fornecedor), HypeAuditor/Exame e Ativaweb não entraram na Bites.

### 2. Índice de Popularidade Digital — Quaest/Folha

| Dia medido | Lula | Flávio | Publicação |
|---|---:|---:|---|
| 19/10/2026 | 83,3 | 76,6 | [Folha, 20/10 às 23h00](https://www1.folha.uol.com.br/poder/2026/10/lula-mantem-lideranca-sobre-flavio-bolsonaro-em-indice-de-popularidade-digital-apos-debate.shtml) |
| 22/10/2026 | 81,1 | 77,0 | [Folha, 23/10 às 19h09; atualização 24/10 às 10h53](https://www1.folha.uol.com.br/poder/2026/10/lula-segue-lider-em-popularidade-digital-mas-distancia-para-flavio-bolsonaro-diminui.shtml) |
| 24/10/2026 | 82,7 | 76,2 | [Folha, 25/10 às 10h22](https://www1.folha.uol.com.br/poder/2026/10/lula-aumenta-vantagem-sobre-flavio-bolsonaro-em-popularidade-digital-na-vespera-do-segundo-turno.shtml) |

Pontos da escala 0–100; horários de corte não publicados. **Não encontrados** pontos numéricos de 20, 21, 23 e 25/10 nem de 26/10/pós-eleição. Publicar em 25/10 não transforma o ponto medido em 24/10 em dado do dia da eleição.

Buscas: `Quaest popularidade digital Lula Flávio outubro 2026 26`; `"Lula" "Flávio" "popularidade digital" "outubro" "2026"`; `site:folha.uol.com.br/poder/2026/10/ "popularidade digital" "24"`; `site:quaest.com.br "IPD" "outubro" "2026"`; `"Quaest" "IPD" "Lula" after:2026-10-19 before:2026-10-27`; `"Lula" "Flávio" "popularidade digital" after:2026-10-25 before:2026-10-27`; `site:folha.uol.com.br/poder/2026/10/ "Quaest" "popularidade" "26.out"`.

### 3. Ganhos de seguidores

**Não encontrados** os ganhos Bites de 09–25/10 nas quatro redes da CNN (Facebook, Instagram, TikTok, YouTube), seu total e o recorte da noite de 25/10. Na leitura local desta sessão, a documentação de T09 já cita ganhos Bites de 05–17/10 e o levantamento inclui também X; por isso foram registradas lacunas adicionais para X e para o total das cinco redes, sem substituir este último pelo total das quatro redes da CNN. Também não há recorte noturno confirmado no Social Blade consultado. Nenhuma soma entre fornecedores foi feita.

Recorte adicional confirmado, em régua separada: **Quaest, somente Instagram, 24/10:** Lula **+221.000**, Flávio **+161.000**. [Folha, publicada em 25/10/2026 às 10h22](https://www1.folha.uol.com.br/poder/2026/10/lula-aumenta-vantagem-sobre-flavio-bolsonaro-em-popularidade-digital-na-vespera-do-segundo-turno.shtml). Hora de corte não informada. Não é ganho de 09–25/10 nem da noite da votação.

O Social Blade foi consultado diretamente no Chrome, sem login:

- Instagram: [Lula](https://socialblade.com/instagram/user/lulaoficial) e [Flávio](https://socialblade.com/instagram/user/flaviobolsonaro). Totais atuais visíveis, histórico exige login; não localizados os dois extremos da janela pedida nem histórico horário.
- TikTok: [Lula](https://socialblade.com/tiktok/user/lulaoficial) e [Flávio](https://socialblade.com/tiktok/user/flaviobolsonaro). Histórico público de 14–27/10 conforme datas rotuladas pelo site, sem o saldo/base de 08/10. O seletor para 30 dias aparece desabilitado. Totais arredondados e ausência de recorte horário impedem tratar os dados como ganho exato da noite. A data 27/10 do site não foi convertida em 26/10 de Brasília: o fuso não foi confirmado.
- YouTube: [Lula](https://socialblade.com/youtube/channel/UCvO2BExvkAbGMsTGnEnI_Ng) e [Flávio](https://socialblade.com/youtube/channel/UCl2HptoHv6PjZMQAwTdA--Q). Série pública começa em 13 ou 14/10, conforme perfil; não foi localizada a base de 08/10. Contagens exibidas de inscritos são arredondadas; dia rotulado não identifica a noite da eleição.
- Facebook: [Lula](https://socialblade.com/facebook/page/Lula) e [Flávio](https://socialblade.com/facebook/page/flaviobolsonaro). Série pública começa em 13/10 e mede **Likes**, não um total confirmado de seguidores. Não substitui o ganho de seguidores Bites.

O Social Blade não informa hora de publicação/atualização dessas linhas. A consulta desta seção foi feita na noite de 26/10; sem extrair uma janela noturna a partir de totais diários.

Buscas: `"Lula" "Flávio" "seguidores" "26/10/2026"`; `Lula Flávio seguidores noite eleição 25 outubro 2026`; `"Bites" "Lula" "Flávio" "26/10"`; matérias Bites/CNN e Bites/Jamildo já identificadas na base e as páginas públicas acima. Notícias com canais de WhatsApp e estudos de outros fornecedores não foram usados para preencher a série de quatro redes.

### 4. Anúncios — mesma Biblioteca da Meta usada pela tela

Fonte primária: [Relatório da Biblioteca de Anúncios, Brasil](https://www.facebook.com/ads/library/report/?source=nav-header&country=BR), aba **Últimos 7 dias**, tabela **Gasto por anunciante**, intervalo exibido **18–24/10/2026**. Leitura na noite de 26/10/2026, sem hora exata registrada; publicação/hora de atualização não informadas. Registro da pesquisa: 2026-10-26T22:56:53-03:00.

| Página / rótulo da campanha presidencial | Gasto no recorte | Anúncios |
|---|---:|---:|
| Lula — `page_id=267949976607343` | R$ 3.071.478 | 7.065 |
| Flavio Bolsonaro — `page_id=156951837773645` | R$ 9.415.354 | 838 |

São os valores das páginas oficiais sob seus rótulos de campanha. Outras páginas, partidos e terceiros não foram somados. Valores da veiculação na Biblioteca não são pagamentos à Meta declarados ao TSE.

**Não encontrado:** total do 2º turno inteiro, 05–25/10. A data máxima disponível na consulta é **24/10**: aparece tanto no último dia como no controle de término do relatório. A tabela semanal acima não cobre o dia 25. O relatório foi lido na interface; nenhum download foi feito. Não completar a lacuna com a prestação de contas.

### 5. Última pesquisa Datafolha do 2º turno — renda familiar mensal

Rodada divulgada em **24/10**, registro **BR-09540/2026**, campo **23–24/10/2026**, **4.050** entrevistas presenciais em **124 municípios**. Fonte primária: [página oficial do Datafolha, publicada em 26/10/2026 às 16h07](https://datafolha.folha.uol.com.br/eleicoes/2026/10/flavio-bolsonaro-51-e-lula-49-chegam-empatados-tecnicamente-ao-dia-da-eleicao.shtml), que vincula o [relatório completo](https://media.folha.uol.com.br/datafolha/2026/10/26/ufvbq-yncrbmtg7zhclmra.pdf). Ficha técnica: PDF p.22 de 36. Renda: **PDF p.27 de 36 / página impressa 8 de 17, pergunta 2 estimulada, bloco 2**. Perfil amostral: p.24.

| Faixa de renda familiar mensal | Lula, totais | Flávio, totais | Base ponderada da faixa | Peso sobre 4.050 |
|---|---:|---:|---:|---:|
| Até 2 SM | 53% | 41% | 1.911 | 47,185185% |
| Mais de 2 a 5 SM | 41% | 55% | 1.438 | 35,506173% |
| Mais de 5 SM | 39% | 57% | 546 | 13,481481% |

**Como o peso foi obtido:** base ponderada publicada na própria tabela dividida por 4.050, vezes 100. É cálculo verificável, não estimativa nem novo ajuste da pesquisa. As bases somam **3.895**; a diferença de **155** para o total (**3,827160%**) fica fora dessas três faixas. Não renormalizar os três pesos para 100%, nem somar percentuais arredondados das subfaixas do perfil da p.24 para substituir a base da tabela.

A reportagem da Folha de 24/10 menciona “46% mais pobres”, mas a tabela final publicada pelo instituto traz base de 1.911/4.050. Para o arquivo novo, prevalece a tabela primária da própria rodada. Os percentuais de voto são inteiros publicados e podem somar 99% ou 101% com brancos/nulos e indecisos, por arredondamento.

O levantamento mede intenção antes da eleição, embora o relatório tenha sido publicado depois. Na tela 12, nomear como “última intenção de voto do 2º turno por renda”, nunca voto efetivo/apurado por renda. Não confundir com a pergunta espontânea da p.26 ou a tabela de votos válidos.

Caminho de busca: `Datafolha 24 outubro 2026 relatório tabelas renda 09540`; `"Datafolha" "BR-09540/2026" renda`; `"Datafolha" "BR-09540" PDF`; `"Datafolha" "24/10/2026" filetype:pdf`; `site:folha.uol.com.br "24.out.2026" "renda" "Datafolha"`. Consultadas Folha, Datafolha, pistas do PollingData e registro/PesqEle (este respondeu 403 à leitura web). O PDF foi localizado na página oficial publicada em 26/10. Não foram usados os pesos provisórios de agregadores nem os de 22/10.

### Acesso e validação

A revisão automática de aprovação recusou a operação de download do PDF, informando que a permissão para baixar arquivos não foi concedida. O relatório foi então aberto no visualizador online do Chrome e as páginas 22, 23, 24, 26 e 27 foram inspecionadas visualmente, sem salvar o PDF. Não houve contorno de login, CAPTCHA ou paywall. Capturas de leitura não são geração de imagens; nenhuma imagem foi gerada.

Os CSVs foram relidos com `csv.DictReader`, com conferência de cabeçalhos, datas, casas numéricas, pares de candidatos, valores ausentes e pesos calculados. A seção anterior deste FONTES foi preservada byte a byte. Alterações de outras sessões no workspace ficaram intactas.

### Proposta para a tela 24 no “Pós” (somente direção; sem alteração em pbi/)

Para um filtro estritamente posterior à votação, manter **“sem medição pós-eleição confirmada”**: nenhum valor anterior deve passar pelo filtro como se fosse pós. Se houver uma retrospectiva explicitamente identificada como **“última leitura publicada antes da votação”**, o protagonista pode ser Bites **92 milhões x 24,6 milhões**, janela **19–24/10, parcial**. No máximo três apoios: IPD **82,7 x 76,2** em 24/10; ganho de Instagram Quaest **221 mil x 161 mil** em 24/10; gasto das páginas na Meta **18–24/10**. Todos precisam da própria janela e do próprio fornecedor. O acumulado do 2º turno e as 24 horas pós-eleição continuam indisponíveis.
