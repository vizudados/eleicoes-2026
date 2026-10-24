# Eleições 2026 · o voto de perto — roteiro (uma pergunta por tela)

Painel no estilo apresentação (linguagem visual da casa, versão de 21/10/2026), contando o 1º turno
presidencial de 2026, inspirado no documentário da Spotniks e com roteiro próprio: do placar ao porquê, do país à
escola.

- **Quem lê e onde:** público geral e clientes da Vizu (vitrine de storytelling em BI); notebook e projetor, de ponta a
  ponta, como apresentação.
- **Fio da narrativa (ordem de 23/10/2026, do antes para o depois):** a pergunta da capa — "Afinal, qual Brasil foi
  às urnas?" — se abre em cinco atos: **I · Antes da urna** (quem são os dois e o que as pesquisas diziam), **II · O 1º
  turno** (o resultado e quem não foi), **III · O mapa** (onde e em quem o voto mudou, até a sua cidade), **IV · Explore
  você mesmo** e, por último, antes do encerramento, **V · O 2º turno** (os votos dos outros, as pesquisas, os dois
  debates colados, buscas e redes com filtro de período em volta dos debates, e a apuração). Cada tela termina apontando a próxima pergunta (`proxima_pergunta` no
  JSON, encadeada automaticamente).
- **Neutralidade:** as duas páginas de candidato têm os mesmos blocos, as mesmas contas e o mesmo tratamento de arte;
  vermelho = Lula/PT e azul = Flávio/PL é convenção de cor.
- **Base:** TSE (votação, comparecimento e perfil do eleitor, 2006–2026, arquivos de 22/10/2026); IBGE Censo 2022;
  levantamento de pesquisas (dados/bruto/pesquisas), do debate (dados/bruto/debate), de redes e buscas
  (dados/bruto/digital) e da trajetória dos candidatos (dados/bruto/trajetoria), todos com fonte por registro.

| # | Ato | Pergunta | Resposta | Base |
|---|---|---|---|---|
| 00 | Abertura | Afinal, qual Brasil foi às urnas no 1º turno? (Capa, T00) | título + 3 linhas | TSE |
| 01 | I · Antes da urna | Quem é Luiz Inácio Lula da Silva? (Lula · quem é, T02) | trajetória em linha do tempo, com fotos históricas redesenhadas em traço | trajetória |
| 02 | I · Antes da urna | Quem é Flávio Bolsonaro? (Flávio · quem é, T04) | trajetória em linha do tempo, com fotos históricas redesenhadas em traço | trajetória |
| 03 | I · Antes da urna | O que as pesquisas diziam antes da urna? (Pesquisas, T10) | Na véspera, 13 de 18 institutos davam Lula à frente; a urna deu Flávio por 1,9 ponto | pesquisas |
| 04 | II · O 1º turno | Quem venceu o 1º turno, e por quanto? (Placar, T01) | Flávio terminou 2,22 mi de votos à frente de Lula | TSE |
| 05 | II · O 1º turno | Onde estão os votos de Lula? (Votos de Lula, T03) | Lula teve 45,2% e ficou à frente em 2.663 municípios; o Nordeste deu 40% dos seus votos | TSE |
| 06 | II · O 1º turno | Onde estão os votos de Flávio? (Votos de Flávio, T05) | Flávio teve 47,0% e venceu em 2.906 municípios; o Sudeste deu 44% dos seus votos | TSE |
| 07 | II · O 1º turno | Quantos brasileiros não escolheram ninguém? (Ausência, T06) | 33,5 milhões não foram votar: 15 vezes a diferença entre Flávio e Lula | TSE comparecimento e perfil |
| 08 | II · O 1º turno | Quem mais falta às urnas, e onde? (Quem falta, T25) | Quem tem 70 anos ou mais falta 3,9 vezes mais que quem tem 16 ou 17 | TSE comparecimento e perfil |
| 09 | III · O mapa | Onde os votos mudaram de lado? (Virada, T11) | 711 municípios trocaram Lula por Flávio; nenhum fez o caminho inverso | TSE × malha IBGE |
| 10 | III · O mapa | Como cada estado se moveu? (Estados, T12) | Lula perdeu margem em 26 das 27 unidades; Minas Gerais e Tocantins mudaram de lado | TSE |
| 11 | III · O mapa | Em que tipo de cidade Lula perdeu mais? (Perfil, T13) | Nas cidades de até 10 mil habitantes e de renda mais alta, a margem de Lula caiu 16,5 p.p. | TSE × IBGE |
| 12 | III · O mapa | Quem vota em Lula e quem vota em Flávio? (Quem vota, T24) | Onde mais casas recebem Bolsa Família, Lula teve 66%; onde menos, Flávio teve 61% | TSE, IBGE, Transparência |
| 13 | III · O mapa | Como o PT chegou até aqui, de 2006 a 2026? (Série, T14) | Pela 2ª vez em seis eleições, o PT termina o 1º turno em segundo lugar | TSE |
| 14 | III · O mapa | Como votou a minha cidade? (Minha cidade, T15) | Abre em Ananindeua (PA), a cidade grande que votou mais perto do Brasil: Flávio 46,2%, a margem de Lula caiu 2,9 p.p. desde 2022 | TSE + IBGE |
| 15 | IV · Explore você mesmo | Onde está a minha pergunta? Explore os 5.571 municípios (Explorador, T19) | os 5.571 municípios em árvore de região, estado e cidade | TSE × IBGE |
| 16 | IV · Explore você mesmo | Como votou cada escola da cidade? (Escola, T20) | os locais de votação de 34 cidades; abre no Rio de Janeiro | TSE × malha IBGE |
| 17 | IV · Explore você mesmo | Como o mapa mudou em 20 anos? (20 anos, T21) | o mapa de 2006 a 2026 | TSE |
| 18 | IV · Explore você mesmo | E se os eleitores dos outros candidatos escolherem? (Simulador, T22) | e se os eleitores dos outros candidatos escolherem (simulação, não previsão) | TSE |
| 19 | V · O 2º turno | Para onde vão os votos dos outros candidatos? (Os outros, T16) | para onde vão os votos dos outros candidatos, pelas pesquisas que publicaram o cruzamento | pesquisas, apoios |
| 20 | V · O 2º turno | E agora, o que as pesquisas dizem do 2º turno? (2º turno, T17) | Desde 05/10, Flávio lidera 39 de 45 pesquisas do 2º turno (até 24/10) · filtro de período em volta dos debates | pesquisas |
| 21 | V · O 2º turno | O que mudou depois do debate na Band? (Debate Band, T07) | O primeiro frente a frente, na Band (18/10), não mexeu nas pesquisas | debate, pesquisas |
| 22 | V · O 2º turno | O último debate mudou alguma coisa? (Debate Globo, T26) | o debate da Globo (23/10) número a número, em tela pronta antes dos números | debate_globo.csv |
| 23 | V · O 2º turno | O que o Brasil perguntou ao Google? (Buscas, T08) | Lula com a maior fatia das buscas nos 27 estados · o clique no estado leva a curva para ele · filtro de período em volta dos debates | Google Trends |
| 24 | V · O 2º turno | Quem dominou as redes? (Redes, T09) | seguidores, interações e anúncios dos dois · filtro de período em volta dos debates | digital |
| 25 | V · O 2º turno | Quem está na frente na apuração do 2º turno? (Apuração, T18) | a apuração do 2º turno ao vivo, no domingo, 25/10, a partir das 17h | API do TSE |
| 26 | Fim | E o que fica desta eleição? (Encerramento, T23) | Do placar à escola: os achados de cada ato + fontes + créditos das fotos | — |

Tela 16 · Escola (código T20, capítulo IV): **Como votou cada escola da cidade?** — os locais de votação de 34 cidades
(as 27 capitais, as 6 maiores que trocaram Lula por Flávio de 2022 para 2026 e Contagem; a tela abre no Rio de
Janeiro), escolhidas no filtro do topo. Resposta no Rio: 1.449 locais de votação; 31 viraram de Lula para Flávio
e 35 de Flávio para Lula, com a margem da cidade quase parada (−3,6 → −4,0 pontos). TSE (seções e cadastro de locais)
× malha do IBGE.

Tela 22 · Debate Globo (código T26, capítulo V, colada na 21 · Debate Band; o painel passa a ter 27 telas): **O último debate mudou alguma coisa?** — o debate da TV Globo de 23/10/2026, o último antes do 2º turno,
numa tela pronta antes dos números: a ficha da noite, os dois púlpitos com a presença de cada um e cinco números que
chegam ao longo da noite e do sábado (buscas, audiência, transmissão na internet, redes e pesquisas com o campo inteiro
depois do debate), cada um com a régua do debate da Band de 18/10. Resposta antes do debate: ainda não dá para dizer.
Base: `dados/pbi/debate_globo.csv` (emissora, imprensa, Kantar IBOPE, Google Trends, Bites) e pesquisas registradas no
TSE.

Decisões do Alisson (22/10/2026): fazer tudo; arquivo novo no Figma; linguagem visual da casa (21/10) "mesmo traço, mas
puxado um pouco mais pra desenho e rabisco", com liberdade criativa; paleta bege com pontos entre vermelho e azul; tela
de pesquisas "antes e agora"; depois, pediu narrativa coesa e rica com pesquisas de redes sociais, assuntos mais
pesquisados, consequências do debate na Band e abstenção crescente em duas décadas; uma página por candidato com
retrato em traço a partir da foto, arte de fundo "com o que ele representa", os dois falando com o povo, vistos de
costas ou de lado, e linha do tempo da trajetória com tooltips de fotos históricas recriadas no traço.

Fora desta rodada: emprego formal (CAGED/RAIS), Bolsa Família por município, cortes do Datafolha por renda e religião.
