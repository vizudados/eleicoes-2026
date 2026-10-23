# Redes sociais e buscas no Google: fontes, método e lacunas

Levantamento feito entre a noite de 22/10 e a madrugada de 23/10/2026, para as telas "Quem dominou as redes?" e
"O que o Brasil perguntou ao Google?". Todos os CSV usam `;`, UTF-8 sem BOM, datas ISO e ponto decimal.
Número que não foi confirmado ficou **em branco**, com a razão na coluna `observacao`.

## Arquivos

| Arquivo | Linhas | O que tem |
|---|---|---|
| `trends_tempo.csv` | 3.092 | Séries do Google Trends (diárias e por hora), coletadas direto no Trends e na Central Google Trends Eleições 2026 |
| `trends_uf.csv` | 648 | Índice por UF (0-100) e participação % das buscas por UF, 1º e 2º turno |
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

| Código | Consulta | Período e resolução | Observação |
|---|---|---|---|
| T1 | 5 candidatos como **termos** de pesquisa | 01/08 a 22/10, diária | "Lula" também é o molusco e o apelido; "Flávio Bolsonaro" não pega quem busca só "flavio". Subestima Flávio |
| **T2** | 5 candidatos como **tópicos** (entidades Google) | 01/08 a 22/10, diária | **Use esta para comparar candidatos.** Tópicos: Lula /m/0pc9q, Flávio /g/122pdhqd, Cury /m/07s813b, Renan /g/11gh2ptx5_ (tópico "Renan Santos, Assunto": presumido do candidato), Caiado /m/04fw8x8 |
| S1 | título de eleitor, local de votação, justificar ausência, e-título, onde voto | 01/08 a 22/10, diária | 100 = "local de votação" em 04/10 |
| S2 | local de votação, justificar voto, justificativa eleitoral, como votar, apuração | 01/08 a 22/10, diária | "apuração" é 100 em 04/10 e comprime os demais |
| E1 | eleições 2026, segundo turno, pesquisa eleitoral, fake news, inteligência artificial | 01/08 a 22/10, diária | Os três últimos ficam perto de zero |
| H1 | Lula x Flávio (tópicos) | 01/10 00h a 08/10 00h, por hora (BRT) | Dia do 1º turno |
| H2 | Lula x Flávio (tópicos) | 15/10 00h a 22/10 00h, por hora (BRT) | Inclui o debate da Band (18/10) |
| G2 | Lula x Flávio (tópicos), mapa por UF | 05/10 a 22/10 | Só em `trends_uf.csv` |
| C1 | Central Google Trends Eleições 2026 | 22/09 a 22/10, diária | Página oficial do Google. Resumo da página: **Lula 56% x Flávio 44%** do interesse em 30 dias |

Cuidados:
- O Trends trabalha com amostra, então uma nova coleta pode mudar alguns pontos. Exemplo: em 04/10, Flávio tem 82 na Central (C1) e 79 na consulta T2.
- 22/10 era o dia em curso na coleta. O dado é parcial e está marcado.
- Em 20 e 21/09, todos os termos de S1 (e 20/09 em S2) vieram zerados: provável falha de coleta do Google, marcada na observação.
- Valor exibido como "<1" foi gravado como 0, com nota.
- "Aumento repentino", nas consultas em ascensão, significa alta acima de 5.000%.
- As consultas relacionadas trazem buscas sobre acusações ("bolsonaro mandou matar lula", "flávio bolsonaro caso ana clara", "flaviorachadinha") porque são o que as pessoas digitaram. Mostram curiosidade, não fato.
- Algumas consultas em ascensão de "título de eleitor" são questões de treinamento de mesário e estão marcadas.

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

## Segurança e acesso

Nenhuma página consultada trazia instruções dirigidas ao agente. Nada pediu login obrigatório para os dados usados:
o Social Blade e o Relatório da Biblioteca de Anúncios da Meta foram lidos sem login. Não aceitei banners de cookies,
não resolvi CAPTCHA, não baixei arquivos e não gerei imagens.
