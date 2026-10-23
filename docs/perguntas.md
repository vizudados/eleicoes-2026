# Eleições 2026 · o que os números dizem — roteiro (uma pergunta por tela)

Painel no estilo apresentação (linguagem visual da casa, versão de 21/10/2026), contando o 1º turno
presidencial de 2026 como o documentário da Spotniks: do placar ao porquê, do país à cidade de quem assiste.

- **Quem lê e onde:** público geral e clientes da Vizu (vitrine de storytelling em BI); notebook e projetor, de ponta a
  ponta, como apresentação.
- **Fio da narrativa:** a pergunta da capa — "Afinal, qual Brasil foi às urnas?" — se abre em quatro movimentos:
  **quem venceu e quem são** (o resultado e os dois candidatos), **quem não foi** (a ausência), **como se chegou lá** (a
  campanha: debate, buscas, redes, pesquisas), **onde e em quem mudou** (o mapa, o perfil, 20 anos) e, no epílogo, **a
  sua cidade e o que vem agora** (o 2º turno). Cada tela termina apontando a próxima pergunta (`proxima_pergunta` no
  JSON, encadeada automaticamente).
- **Neutralidade:** as duas páginas de candidato têm os mesmos blocos, as mesmas contas e o mesmo tratamento de arte;
  vermelho = Lula/PT e azul = Flávio/PL é convenção de cor.
- **Base:** TSE (votação, comparecimento e perfil do eleitor, 2006–2026, arquivos de 22/10/2026); IBGE Censo 2022;
  levantamento de pesquisas (dados/bruto/pesquisas), do debate (dados/bruto/debate), de redes e buscas
  (dados/bruto/digital) e da trajetória dos candidatos (dados/bruto/trajetoria), todos com fonte por registro.

| # | Ato | Pergunta | Resposta (manchete no JSON) | Base |
|---|---|---|---|---|
| 00 | Abertura | Afinal, qual Brasil foi às urnas no 1º turno? | título + 3 linhas | TSE |
| 01 | I · O resultado | Quem venceu o 1º turno, e por quanto? | Flávio terminou 2,22 mi de votos à frente de Lula | TSE |
| 02 | I | Onde estão os votos de Lula? (página do candidato, vermelho + bege; retrato em traço, comício no Nordeste ao fundo, linha do tempo da trajetória com tooltips de fotos históricas em traço) | Lula teve 45,2% e ficou à frente em 2.663 municípios; o Nordeste deu 40% dos seus votos | TSE, trajetória |
| 03 | I | Onde estão os votos de Flávio? (azul + bege; comício no Sul) | Flávio teve 47,0% e venceu em 2.906 municípios; o Sudeste deu 44% dos seus votos | TSE, trajetória |
| 04 | I | Quantos brasileiros não escolheram ninguém? | 33,5 milhões não foram votar: 15 vezes a diferença entre Flávio e Lula | TSE comparecimento e perfil |
| 05 | II · A campanha | O que mudou depois do debate na Band? | (levantamento em curso) | debate |
| 06 | II | O que o Brasil perguntou ao Google? | (levantamento em curso) | digital |
| 07 | II | Quem dominou as redes? | (levantamento em curso) | digital |
| 08 | II | O que as pesquisas diziam antes da urna? | Na véspera, 13 de 18 institutos davam Lula à frente; a urna deu Flávio por 1,9 ponto | pesquisas |
| 09 | III · O mapa | Onde os votos mudaram de lado? | 711 municípios trocaram Lula por Flávio; nenhum fez o caminho inverso | TSE × malha IBGE |
| 10 | III | Como cada estado se moveu? | Lula perdeu margem em 26 das 27 unidades; Minas Gerais e Tocantins mudaram de lado | TSE |
| 11 | III | Em que tipo de cidade Lula perdeu mais? | Nas cidades de até 10 mil habitantes e de renda mais alta, a margem de Lula caiu 16,5 p.p. | TSE × IBGE |
| 12 | III | Como o PT chegou até aqui, de 2006 a 2026? | Pela 2ª vez em seis eleições, o PT termina o 1º turno em segundo lugar | TSE |
| 13 | Epílogo | Como votou a minha cidade? | Em Contagem, Flávio venceu com 50,3%; a margem de Lula caiu 5,4 p.p. desde 2022 | TSE + IBGE |
| 14 | Epílogo | E agora, o que as pesquisas dizem do 2º turno? | Desde 05/10, Flávio lidera 34 de 39 pesquisas do 2º turno | pesquisas |
| 15 | Epílogo | O que os números dizem, afinal? (encerramento) | os achados de cada ato + fontes + créditos das fotos | — |

Decisões do Alisson (22/10/2026): fazer tudo; arquivo novo no Figma; linguagem visual da casa (21/10) "mesmo traço, mas
puxado um pouco mais pra desenho e rabisco", com liberdade criativa; paleta bege com pontos entre vermelho e azul; tela
de pesquisas "antes e agora"; depois, pediu narrativa coesa e rica com pesquisas de redes sociais, assuntos mais
pesquisados, consequências do debate na Band e abstenção crescente em duas décadas; uma página por candidato com
retrato em traço a partir da foto, arte de fundo "com o que ele representa", os dois falando com o povo, vistos de
costas ou de lado, e linha do tempo da trajetória com tooltips de fotos históricas recriadas no traço.

Fora desta rodada: emprego formal (CAGED/RAIS), Bolsa Família por município, cortes do Datafolha por renda e religião.
