# Integração · rodada 6

## Rodada 6 · vigente · correções do HTML avaliado

Sem mudança de tabela, coluna, relação, CSV, controles ou valores de votação. Esta rodada altera somente desenho
DAX e CSS/bodyTemplates de T28, lista T27 e fundos/cabeçalho T22. Não foi operado o Desktop nem aplicado PBIP.

### Causa confirmada e correção

O problema principal da ponte e da lista não era a caixa do PBIR: **`FORMAT(..., "0.##", "en-US")` devolveu um
ponto decimal sem dígitos em inteiros**. Os HTMLs reais avaliados pela main contêm `width='85.'`, `x='810.'`,
`y='32.'` e `left:350.px`. Esses valores são inválidos para as propriedades/atributos de comprimento do navegador:
larguras somem, posições voltam à borda e textos são cortados. A simulação anterior, que formatava em Python,
não reproduzia esse comportamento do DAX. A rodada 6 parte dos próprios HTMLs do motor, não de uma nova conta Python.

- **T28:** todas as coordenadas e dimensões calculadas passaram para `0.00` em en-US. SVG explícito de 1620×355,
  `display:block`, mais 35 px para o fecho = **1620×390**, exatamente a posição PBIR. Valores dos extremos ficam
  alinhados abaixo do desenho (y=309), rótulos superiores têm piso y=28 e nomes até y=340, dentro do SVG.
  No DF são três barras de 170 px; o texto passa a **“No DF, a diferença andou 79.671 votos para Lula”**, com
  **“Flávio terminou o 2º turno à frente por 154.318 votos.”** As contas e a ponte estadual/municipal são as mesmas.
- **T27:** além do formato decimal válido, cada barra foi colocada numa faixa física em x=350, largura 330,
  com `overflow:hidden`. Os nomes terminam em x=335, portanto há 15 px livres e a barra não pode cobrir a tinta.
  Posição/escala/ordem/valores, oito cidades, sampling e interações foram mantidos.
- **T22:** pergunta B encurtada para **“Quantos não teriam escolhido ninguém?”**, uma linha de 20 px; subtítulo
  permanece em y=24, com 4 px de intervalo. O texto mede 332,02 px em Sora 600/16, dentro dos 410 disponíveis.
  Cabeçalho da tabela vira **“Destino dos outros votos”**, com 219,02 px de texto dentro de 260; cada coluna agora
  tem largura explícita (108/260/84/290), mantendo x=6/190/466/560. Os três controles VizuFilter e suas caixas não mudaram.

### Simulações em tamanho exato

Pasta **`pbi/qa/rodada6/`**, entrada `index.html` e dimensões/posições em `manifesto.json`:

| Arquivo depois | Viewport |
|---|---:|
| `T28-Brasil-depois.html` | 1620×390 |
| `T28-MG-depois.html` | 1620×390 |
| `T28-DF-depois.html` | 1620×390 |
| `T28-DF-manchete-depois.html` | 1620×125 |
| `T27-lista-depois.html` | 840×270 |
| `T22-fundos-depois.html` | 860×270 |
| `T22-tabela-depois.html` | 860×296 |

Os arquivos `*-original-motor.html` preservam o `srcdoc` real de cada visual das prévias da rodada 5. Os arquivos
`*-antes.html` e `*-depois.html` reutilizam esses valores e fontes, com correções determinísticas equivalentes ao
gerador; não são nova avaliação DAX. O original fica congelado, mesmo se a main depois atualizar `qa/previa`.
`provas-locais.json` registra 14/21/14 atributos inválidos antes em Brasil/MG/DF e zero depois, retângulos positivos
e dentro do SVG, oito faixas separadas dos nomes e os limites dos textos. **São provas estáticas, não screenshots.**

A captura de navegador neste sandbox ficou bloqueada: Playwright falhou ao criar canais Windows (`WinError 5`),
o Chromium síncrono falhou no canal Mojo/Crashpad (`Acesso negado`) e a ferramenta de UI não tem navegador disponível.
Não foi gerado PNG fingindo ser render de HTML. A main pode executar o renderer abaixo fora do sandbox; ele espera
as fontes, usa viewport exato e verifica caixas reais no DOM antes de salvar as sete capturas e `prova-browser.json`.

### Comandos de preparação desta rodada

```powershell
python -X utf8 pbi/scripts/desenho_t28.py --somente-desenho
python -X utf8 pbi/scripts/desenho_t27_t28.py --somente-lista
python -X utf8 pbi/scripts/desenho_t22.py
python -X utf8 pbi/scripts/validar_rodada6.py
python -X utf8 pbi/scripts/validar_dax_gerado.py --autoteste
```

O escritor de T22 só altera arquivos cujo conteúdo mudou. Os modos novos de T28/T27 não regeram contas ou specs.
Para a captura de navegador pela main:

```powershell
python -X utf8 pbi/scripts/simular_rodada6.py --render
```

Este comando não abre nem consulta o Power BI. A main integra as medidas de desenho e reaplica as páginas pelo
fluxo habitual. Depois, gerar `previa.py T28`, MG, DF, T27 e T22 no motor; conferir CE, extremos e barras no SVG,
o caso DF sem 100%, nomes da lista livres, textos da T22 sem encontro e controles ainda arrastáveis. Rodar smoke
T28/T27/T22. O preparo amplo da rodada 5 abaixo é só registro histórico, já integrado; para esta correção vale
o conjunto curto de comandos acima.

---

## Registro da rodada 5 · já integrado pela main


Registro da entrega anterior sobre `ac14ae2` / `d55cbed`. Fontes em disco, sem Desktop, refresh, PBIP aplicado, commit ou push.
**Nenhuma tabela, coluna, relação ou CSV novo:** continuam 49 tabelas e 24 relações. Há novas medidas de conta e
desenho, fontes WOFF2 subsetadas, uma composição nova para T28 e alterações de páginas/specs/helpers.
O modelo precisa receber as medidas e as páginas precisam ser reaplicadas pela main; não há nova fonte de dados
para publicar ou recarregar por mudança de esquema.
No diretório gerado apareceram regravações de navegação/serialização em T00/TIX e página ativa T28 durante o
trabalho. Foram preservadas; nenhum comando desta rodada aplicou PBIP ou salvou/operou o Desktop.

## T28 · composição e universos

- Protagonista de largura inteira: ponte da diferença **Lula menos Flávio**, de −2.224.965 no primeiro turno a
  +4.430.191 no segundo. Mudança total **6.655.156**, Brasil **com exterior**. A primeira barra é azul, a última
  vermelha; contribuições positivas/negativas seguem o mesmo sinal e tratamento.
- Nove estados pelo nome, os outros 18 agrupados, ZZ separado. SP 1.396.706; MG 697.925; RJ 670.183; BA 654.311;
  PE 469.031; CE 418.233; MA 250.999; RS 229.198; PA 227.229; outros 18, 1.626.171; exterior, 15.170.
  A conta completa aparece sob a ponte. Títulos no hover dão os volumes sem arredondamento.
- Manchete: **SP, MG e RJ somaram 41,5% da virada**: 2.764.814 / 6.655.156 = 41,5439%. Minas foi o único estado
  que mudou de vencedor. Texto, valores e labels da ponte são HTML/SVG com a Sora embutida, sem texto no canvas.
- **Filtro:** uma UF transforma a ponte em contribuições dos seus municípios, nove explícitos e demais agrupados.
  Região/várias UFs mantém a ponte estadual do recorte, sem ZZ. O DF tem uma única unidade municipal no modelo:
  a chamada concorda no singular. `T28 · ponte · resíduo` deve ser zero no país e em qualquer uma das 27 UFs.
- Apoio 1: mapa **apenas das trocas estritas** — 211 Flávio → Lula e 1 Lula → Flávio (Uirapuru, GO), sem exterior.
  Contornos estaduais, dossiê por município e seleção preservada; os cliques não refazem a ponte nem o ranking.
  Recorte sem troca mostra aviso explícito. O conjunto nacional contém 212 linhas, todas com coordenadas.
- Apoio 2: perdas de Flávio 2026 frente a Jair 2022, ambos no segundo turno, por **estado e cidade**, quatro maiores
  perdas de cada lado. Sinal negativo; município ausente em 2022 permanece sem comparação. Estados: RJ −234.861;
  SP −77.409; DF −61.789; AP −1.873 (AC também caiu, −35, fora dos quatro primeiros).
- Saíram da página o fluxo de dois candidatos da T27, o mapa de todos os municípios e a antiga lista Deneb.
  O i e o rodapé explicam universos e método. A T27 conserva a identidade municipal observada, sem regressão.

Fontes principais: `desenho_t28.py`, `paginas/t28_onde_flavio_perdeu.py`, `leituras/T28.json`, medidas T28 e
`spec/t28_mapa.json`. O gerador anterior `desenho_t27_t28.py` agora delega T28 ao novo, para não sobrescrever o desenho.
As antigas medidas de fluxo/apoios T28 e os specs de listas Deneb foram retirados. As entradas do roteiro mantêm a
mesma ordem e pergunta; a fonte da T28 passa a explicitar exterior na ponte do Brasil.

## Otimizações e medições estáticas

Leitura integral do diagnóstico da main em `pbi/qa/desempenho/relatorio.md`: não houve reprovação DAX. Os números
abaixo são de arquivos/plano, CSVs e cache de prévia anterior, **não são novos tempos de motor nem de navegador**.
O resumo reprodutível completo está em **`pbi/qa/rodada5/resumo.md`**, com JSONs antes/depois e oráculos na mesma pasta.

| Otimização | Antes | Depois | Como preservar a leitura |
|---|---:|---:|---|
| Folha comum, caracteres | 80.023 | **37.060** | Sora, cores, medidas e movimento iguais; Caveat separada |
| Folha completa para notas, caracteres | 80.023 | **61.631** | base + folha Caveat, somente onde há escrita à mão |
| Sora WOFF2, bytes | 28.692 | **23.156** | mesmos eixos 300–800 e métricas; 151 pontos Unicode requeridos cobertos |
| Caveat WOFF2, bytes | 26.576 | **18.316** | mesma instância 600; 118 pontos Unicode requeridos cobertos |
| T19, texto da consulta bruta | 3.425.784 | **9.608 no cache recortado** | só as 16 posições previstas; busca existente continua alcançando todos |
| T21, texto no dataset | 612.810 | **39.100** | quadros/contadores de 103 caracteres em uma única linha, não 5.571 vezes |
| T27 mapa, texto no dataset | 167.764 | **38.997** | sem rótulos e números formatados repetidos; chave original preservada |
| T27 lista, texto estimado | 167.764 / 5.571 linhas | **1.766 / 8 linhas** | HTML/Sora, mesma ordem, valores, escala, dossiê e filtro cruzado |
| T28 mapa, texto no dataset | 166.018 / 5.571 linhas | **1.484 / 212 linhas** | desenho novo, apenas as trocas estritas |
| T03/T05/T11/T25, texto por mapa | 50.139 | **38.997** | UF recuperada do prefixo IBGE, validado nos 5.571 códigos |
| T19 dispersão, texto | 38.997 | **38.997** | cinco campos necessários mantidos, inclusive precisão do laço de seleção |
| JSON normalizado de dados T21, bytes | 1.716.152 | **720.079** | inteiros de desenho, dados analíticos originais preservados |
| JSON normalizado de dados T27 mapa, bytes | 667.912 | **278.765** | quatro campos, magnitude calculada de abs(valor) |
| JSON normalizado de dados T27 lista, bytes | 667.912 | **1.937** | oito HTMLs + chaves, em vez do conjunto inteiro no canvas |
| JSON normalizado de dados T28 mapa, bytes | 663.764 | **10.602** | apenas 212 trocas |
| Visuais da T22 | 20 | **18** | três fundos HTML viram um; os três VizuFilter são idênticos aos anteriores |
| Visuais da T23 | 20 | **19** | fecho numérico incorporado ao HTML principal, mesma geometria |
| Visuais da T27 | 17 | **16** | título da lista incorporado ao HTML da lista |
| Visuais da T28 | 17 | **15** | composição nova, sem o fluxo/lista repetidos |
| Visuais da TIX | 32 | **32** | 30 atalhos + voltar nativos preservados; juntar exigiria mudar a navegação |

**Interpretação importante da T19:** o PBIR já declarava Top 16. `desempenho.py` reconstituía a consulta sem aplicar
o `filterConfig` do visual, e por isso media as 5.571 linhas. Agora a própria medida retorna BLANK fora das primeiras
16, inclusive na consulta bruta; rank considera o recorte e tem desempate estável, sem sobrepor linhas empatadas.
O cache anterior contém 3.333.241 caracteres de HTML + 92.543 da coluna de rótulos = 3.425.784, exatamente o controle
da main. Os 16 HTMLs conservados somam 9.391, mais 217 dos rótulos = 9.608. **Isso não prova que o Desktop antes
renderizava 5.571 linhas**; o ganho real nessa tela deve ser medido no navegador.

**Os JSONs normalizados** usam os mesmos CSVs e aliases, UTF-8 e sem espaços. Não incluem todos os metadados do SDK
e não são captura de tráfego do Power BI. Os caracteres de texto reproduzem exatamente os controles da main nos
mapas antigos e na consulta T19. `desempenho.py` agora registra que caracteres não incluem números/metadados.

### Detalhes das alterações comuns

- `fontes_painel.py` varre medidas, páginas/bodyTemplates, leituras, roteiro e CSVs de nomes dinâmicos. O subset é
  conservador para notas dinâmicas em português; mantém alfabeto e acentos necessários a nomes e números. O manifesto
  de Unicode/tamanho está em `pbi/assets/fontes/subsets-painel.json`. Nenhum glifo do corpus requerido ficou ausente,
  e as métricas das fontes retidas são iguais às anteriores. Os originais foram conservados para comparação.
- `Estilo · CSS` ficou sem Caveat; `Estilo · CSS mão` contém só a fonte das notas e `Estilo · CSS com mão` compõe as
  duas. `visual_html` decide pela nota realmente presente no markup ou dependências da medida, inclusive os selos
  da capa e encerramento; uma regra CSS sem elemento correspondente não obriga a carregar Caveat.
- Na soma teórica de um carregamento de cada instância declarada, folhas passaram de **19.765.681 para cerca de
  11.929.529 caracteres (−39,65%)**. Não é memória simultânea nem rede observada; tooltips/páginas podem carregar sob demanda.
- A T21 mantém a chave do município; X/Y vão como centésimos inteiros e recuperam exatamente as duas casas do CSV.
  As seis margens de cor vão em milionésimos inteiros, com erro máximo de **0,00005 ponto percentual**, imperceptível
  na cor. Manchetes, números dos contadores, tooltips e cálculos analíticos continuam lendo as medidas originais.
- Mapas T03, T05, T11, T25, T27 e T28 não repetem UF por linha: `visual_deneb(uf_por_codigo=True)` retira o campo do
  bucket e insere o lookup validado no spec compilado. `__row__` e a chave original continuam presentes.
  A magnitude do mapa T27/T28 usa `abs(valor)` no Vega, evitando um campo numérico duplicado.
- O helper Deneb não emite `__format`/`__formatted` quando a spec não os referencia. Conferido no runtime privado
  2.0 do pacote: esses flags geram cópias por linha. Nenhuma spec atual os usa; a emissão é reativada se aparecer
  referência. Este ganho adicional no DataView **não está incluído** nas estimativas da tabela.
- JSONs de specs são minificados na compilação. O arquivo-fonte continua legível; a spec efetiva no PBIR contém
  minificação, UF derivada quando pedida e guarda de visibilidade dos relógios.
- `movimento.js` agenda quadros só quando necessário, esvazia a fila no fim e suspende callbacks por visibilidade/
  interseção. Deneb congela sinais quando o contêiner tem largura/altura zero; relógios simples retornam antes de
  consultar o DOM depois de `fim`. A guarda foi verificada contra `containerSize()` do próprio runtime do pacote.
  Não há animação CSS infinita na camada autoral; os movimentos finitos e `prefers-reduced-motion` foram mantidos.
- Fundos A/B/C da T22 foram unidos; medidas HTML antigas são reutilizadas, com deslocamentos equivalentes. IDs,
  caixas, configurações e sincronias dos **três controles** são comparados integralmente ao HEAD: iguais. Pesquisas
  e grade mantêm grãos/tooltip/interações próprios. A TIX conserva os botões nativos de bookmark.

## Preparação para integrar

```powershell
python -X utf8 pbi/scripts/desenho_t27_t28.py
python -X utf8 pbi/scripts/desenho_t19.py
python -X utf8 pbi/scripts/desenho_t21.py
python -X utf8 pbi/scripts/desenho_t22.py
python -X utf8 pbi/scripts/desenho_t23.py
python -X utf8 pbi/scripts/estilo.py
python -X utf8 pbi/scripts/validar_dax_gerado.py --autoteste
python -X utf8 pbi/scripts/peso_estatico.py --nome depois
python -X utf8 pbi/scripts/validar_rodada5.py
node pbi/tools/testar_rodada5.mjs
python -X utf8 pbi/scripts/resumo_peso.py
python -X utf8 pbi/scripts/validar_pos_eleicao.py
```

Checar `$LASTEXITCODE` após cada comando no PowerShell 5.1. Esses comandos gravam fontes DAX/spec/fontes/QA,
não operam o Desktop ou aplicam PBIP. **Não refazer `peso-antes.json`**: é o snapshot da base recebida na rodada.
Os novos WOFF2, manifesto e medidas `_Estilo` precisam acompanhar o código para reproduzir o build em outra máquina.
Arquivos de fonte: `pbi/assets/fontes/sora-painel.woff2`, `caveat-notas.woff2` e `subsets-painel.json`.

## Provas locais e o que falta no motor/navegador

`provas-locais.json` fecha a ponte nacional e as 27 pontes municipais, confirma 211 + 1 trocas, ganhos e pesos,
fontes sem glifos ausentes, métricas iguais e controles T22 idênticos. `runtime-local.json` executa os specs
compilados: mapa T28 com 212 pontos, T27 com os mesmos 5.570 pontos posicionáveis, quadro único da T21 e contador
2.663; pausa de relógio oculto, fim estável, fila de contador vazia e movimento reduzido. São testes locais,
**não smoke DAX nem gesto no Power BI**. As simulações da ponte e mapas ficam em `pbi/qa/rodada5/`, sem sobrescrever
as fotos reais de `qa/previa/`.
O lint das 295 medidas das seis pastas envolvidas terminou sem erro; os pontos/séries do T19 foram escritos sem
filtro de contexto no desenho, preservando a omissão dos anos sem dado. As 64 combinações possíveis de lacunas
nos seis anos geram o mesmo caminho geométrico. O validador estrutural passou em 1.953 medidas e dez autotestes.
Os seis geradores foram repetidos: 306 arquivos gerados idênticos. `git diff --check` sem erro.

A main integra medidas, fontes e páginas pelo fluxo da casa e prova:

1. **T28 Brasil, foto 1920 e 61%:** manchete 41,5%, nove estados + outros 18 + exterior, fechamento sem cortes;
   valores dos seis estados do brief e exterior 15.170. Mapa com 211 vermelhos/1 azul, tooltip de Uirapuru e de
   uma cidade de MG. Jair: perdas negativas por estado e cidade, sem mistura de turnos.
2. **T28 MG, RR, DF e região/várias UFs:** ponte passa a municípios só com uma UF; caso DF no singular;
   `T28 · ponte · resíduo = 0` em todos. Onde não houve troca, aviso explícito. Cliques no mapa não alteram ponte,
   ranking nem árvore da casca. i abrir/fechar e fonte com cobertura coerente.
3. **T27:** mesma identidade, regiões/portes e oito cidades/valores, agora na Sora. Mapa ↔ lista, dossiê e seleção
   da cidade; testar valores empatados, para não sobrepor linhas. Nenhum texto da lista em Deneb.
4. **Fontes em todo o painel:** capa com a frase do `d55cbed`, encerramento, notas à mão, percentuais, setas e nomes
   acentuados em TT. Sem fallback ou glifos faltantes. Contadores/cores/movimentos iguais nos estados visíveis.
5. **T19:** Brasil, busca de cidade, filtro por porte/região/renda, clique e laço na dispersão; resumo continua no
   universo inteiro, lista só das 16 primeiras do recorte e dossiê funcionando. Busca pode alcançar qualquer cidade.
6. **T21:** seis anos, mesmos totais/margem nacional/cores, régua/play/hover e atualização incremental sem reinício.
   Conferir que o dataset tem **um** `anos` não vazio; os outros 5.570 registros desse campo devem estar vazios.
7. **T22/T23/TIX:** arrastar as três réguas e usar teclado, pesquisas/UF/exterior mantidos; fecho numérico e todos
   os atalhos de T23; 30 links do sumário. Controles não podem ser bloqueados pelos HTMLs consolidados.
8. **Motor:** rerodar `desempenho.py`, guardar antes/depois de frio/quente, linhas e caracteres, além de smoke das
   telas alteradas e T29 (helper comum). Verificar T19 ~16 linhas, T27 lista ~8, T28 mapa ~212 e T21 sem quadros
   repetidos. Tempos novos não foram medidos no sandbox; nenhuma promessa de redução em ms foi feita.
9. **Navegador/Desktop/Service:** medir entrada, troca de filtro e de página, memória e CPU após a animação acabar.
   O script de desempenho mede DAX/leitura, não paint/layout/decodificação. Confirmar que página oculta entrega
   contêiner zero/visibilidade ao visual e não repinta; esse ciclo do SDK só a main pode provar no estado real.
