# Encerramento animado · Da zona eleitoral ao resultado.

Os votos partem dos municípios e se reúnem em duas faixas de pontos, Flávio à esquerda e Lula à direita. Cada ponto cheio representa 50 mil votos; os fragmentos preservam os votos de cada origem, e a área dos pontos incompletos é proporcional à sua fração. No fim, somente os 4.430.191 votos que fazem a diferença recebem um realce discreto na própria cor de Lula, e a composição para.

**15 s · 30 fps · 1920 × 1080 · 450 quadros, de 0 a 449 · sem áudio e sem repetição.** Tudo é desenho em SVG por código. Não há imagem gerada, bandeira, estrelas, paisagem ou horizonte da capa. A composição `Capa` e seus arquivos de mídia permanecem iguais.

## Roteiro e sincronia

Os tempos vêm de `capa/remotion/src/encerramento/roteiro.json`, lido tanto pelo Remotion quanto pelo gerador Python da T23. Entradas HTML duram 0,6 s; contadores duram 0,85 s. O relógio é `video.currentTime`: não há atraso CSS contado a partir da carga da página.

| Tempo | Quadros a 30 fps | Vídeo e HTML |
|---|---|---|
| 0–1 s | 0–30 | O título entra em HTML; o contorno do Brasil começa a se desenhar em traço areia. A legenda dos municípios começa em 0,7 s. |
| 1–2 s | 30–60 | O contorno termina em 1,8 s, as divisas esmaecem e os pontos municipais aparecem. Boa Esperança do Norte e exterior têm entradas identificadas ao lado do mapa. |
| 2–3 s | 60–90 | Todos os municípios estão visíveis em 2,1 s. Os fragmentos de voto aparecem entre 1,7 e 2,5 s; os primeiros partem em 2,6 s. |
| 3–4 s | 90–120 | As duas candidaturas se deslocam simultaneamente. A última partida ocorre em 4,0 s; a mesma semente, duração e curva governam os dois lados. |
| 4–5 s | 120–150 | Os votos seguem para as faixas sob os blocos de resultado. O mapa e seus rótulos começam a desaparecer em 4,8 s. |
| 5–6 s | 150–180 | Primeiros lotes chegam; a passagem de fragmentos para pontos completos dura 0,35 s. Não há rastros, brilho ou movimento de câmera. |
| 6–7 s | 180–210 | As duas faixas se completam. Todos os 124.082.273 votos estão entregues em 7,0 s. |
| 7–8 s | 210–240 | O mapa desaparece por completo em 7,4 s. Em **7,5 s**, entram juntos os dois blocos HTML de resultado e a escala de 50 mil votos por ponto. |
| 8–9 s | 240–270 | Resultado legível e contadores concluídos em 8,35 s. Em **8,7 s**, o HTML entrega a diferença e a faixa destaca os pontos excedentes de Lula. |
| 9–10 s | 270–300 | O realce termina em 9,5 s e fica parado. Em **9,7 s**, entram abstenção e comparecimento. |
| 10–11 s | 300–330 | Participação concluída em 10,55 s. Em **10,6 s**, entram os achados dos cinco atos, com os mesmos textos e atalhos. |
| 11–12 s | 330–360 | Em **11,2 s**, entram frase de fecho e fontes; tudo está legível em 11,8 s. |
| **12–15 s** | **360–449** | Toda a composição está parada. São 90 quadros idênticos; o último é o pôster. |

O movimento não representa a ordem ou o horário da apuração, nem acompanha indivíduos entre turnos. A movimentação reúne os votos finais de uma mesma eleição. Os valores do primeiro turno, achados, percentuais, diferença, abstenção e comparecimento continuam vindo das mesmas medidas DAX.

## Votos, frações e cobertura

| Cobertura | Lula | Flávio | Válidos |
|---|---:|---:|---:|
| Municípios do CSV de 2026 | 64.056.078 | 59.654.544 | 123.710.622 |
| Exterior (`ZZ`) | 200.154 | 171.497 | 371.651 |
| **Nacional com exterior** | **64.256.232** | **59.826.041** | **124.082.273** |

As origens vêm de `dados/pbi/municipio_2turno.csv`; o nacional e o exterior, de `dados/pbi/uf_2turno.csv`. O preparador exige as somas acima, 5.571 municípios únicos e 28 linhas de UF/exterior. Os hashes dos CSVs, da geometria da capa e do roteiro ficam no JSON de saída.

São **5.572 origens**, **13.625 fragmentos** e **2.483 pontos finais**: 1.197 para Flávio e 1.286 para Lula. Cada fragmento é a interseção exata de um intervalo de votos municipal com um lote final, tem um inteiro positivo de votos e parte da origem correspondente. Não há amostra, arredondamento dos votos, município descartado ou voto artificial.

A parcela comum é de 59.826.041 votos: 1.196 pontos de 50 mil e um de 26.041, iguais nos dois lados. O excedente de Lula tem 88 pontos de 50 mil e um de 30.191; soma **4.430.191**. Raio = `1,25 × raiz(votos / 50.000)`, para a área comunicar a fração. Os dois pontos incompletos de Lula existem porque a separação da diferença preserva exatamente o trecho comum.

**Geografia:** os 5.570 centroides disponíveis e os traços do IBGE são lidos do JSON existente da capa, sem modificá-lo. Boa Esperança do Norte, MT (`5101837`, Lula 945, Flávio 2.353), não tem coordenada nessa malha: seus 3.298 votos partem de uma entrada nomeada fora do mapa. O exterior também parte de uma entrada nomeada, sem posição geográfica inventada. Ambos integram os pontos finais e o total nacional.

## Composição e contraste

- Fundo tinta `#1C1915`; mapa areia `#CBBDA2`. Candidaturas nas cores de `pbi/scripts/estilo.py`: Flávio `#8FA8CF`, Lula `#D9877B`.
- Título, números, percentuais, selo **reeleito**, resumo, achados e fontes são HTML; o vídeo não contém texto.
- Mapa inicial centralizado em `(960, 391)`, escala 0,51 da geometria da capa, abaixo do título. Voos ficam entre o mapa e as faixas, antes da entrada dos números.
- Faixas finais começam em `(150, 544)` e `(1770, 544)`, espelhadas, 120 colunas, passo 3,5 px. A última marca fica abaixo de y 582, antes dos achados em y 590. Não se redesenha o mapa atrás da diferença.
- O selo mantém o desenho e a palavra **reeleito**; sua margem superior passa de 14 para 8 px para abrir espaço acima da faixa, sem mover números ou achados.
- O trecho comum recebe exatamente a mesma opacidade, densidade, raio e temporização nas duas cores. Na entrega da diferença, o trecho comum esmaece para 0,28 e os 89 pontos excedentes chegam a 0,82, com contorno fino na mesma cor.
- A casca é composta novamente acima do vídeo no próprio HTML, como na T00, preservando urna, seta, informação e rodapé. Os alvos nativos de navegação e os onze atalhos não mudam.

## Reprodução e falhas

O template usa `encerramento.mp4`, depois `encerramento.webm`, no mesmo host HTTPS da capa: `https://vizudados.github.io/eleicoes-2026/midia/encerramento/`. O pôster é sempre `encerramento-final.jpg`.

O HTML é emitido no estado final, completo. Somente depois de `playing` o controlador mostra o vídeo, sincroniza opacidades e contadores e esconde o pôster. Em `waiting`, `stalled` sem buffer suficiente e `pause`, a coreografia acompanha somente a posição real do vídeo; uma espera contínua de 8 s volta ao pôster e aos números finais. Autoplay negado, erro do vídeo ou falha das duas fontes fazem o mesmo. A falha apenas do MP4 permite tentar o WebM.

Com `prefers-reduced-motion: reduce`, o vídeo pausa, ficam pôster e todos os textos finais, sem contador. Sem JavaScript, o pôster e o HTML final também ficam visíveis. Ao terminar normalmente, não há `loop`, reinício ou troca de quadro: a última imagem permanece. O controlador é local ao visual, não armazena dados e não acessa rede além das mídias fixas. A T23 usa `movimento=False` para evitar que o contador genérico termine antes da entrada dos blocos.

## Comandos da main · PowerShell 5.1

As dependências já existem; não há instalação ou atualização. Renderizar **fora do sandbox**, na GPU com `--gl=angle`. A sequência PNG e a codificação seguem o [CLI oficial do Remotion](https://www.remotion.dev/docs/cli/render).

```powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições\capa\remotion'

python -I -B -X utf8 scripts/preparar_encerramento.py
if ($LASTEXITCODE -ne 0) { throw 'Falha nos dados do encerramento.' }
npx tsc --noEmit
if ($LASTEXITCODE -ne 0) { throw 'Falha no TypeScript.' }
npm test
if ($LASTEXITCODE -ne 0) { throw 'Regressao na capa.' }
node --test --test-isolation=none scripts/testar_encerramento.cjs
if ($LASTEXITCODE -ne 0) { throw 'Falha nos testes do encerramento.' }
python -I -B -X utf8 ../../pbi/qa/encerramento/validar.py
if ($LASTEXITCODE -ne 0) { throw 'Falha na preservacao da T23.' }

npx remotion render src/index.ts Encerramento out/seq-encerramento --sequence --image-format=png --image-sequence-pattern=element-[frame].[ext] --gl=angle
if ($LASTEXITCODE -ne 0) { throw 'Falha no render PNG.' }
powershell -NoProfile -File scripts/codificar_encerramento.ps1
if ($LASTEXITCODE -ne 0) { throw 'Falha ao codificar as midias.' }
```

O codificador exige `element-000.png` a `element-449.png`, confere o SHA-256 idêntico dos quadros 360–449 e gera:

| Saída em `docs/midia/encerramento/` | Formato |
|---|---|
| `encerramento.mp4` | H.264 High, CRF 10, yuv420p, BT.709, faixa limitada, faststart |
| `encerramento.webm` | VP9 em duas passadas, 2,6 Mb/s, yuv420p, BT.709 |
| `encerramento-final.jpg` | Quadro 449, qualidade 85, sem subamostragem de cor |
| `encerramento-inicio.jpg` | Quadro 0, qualidade 85; evidência, não usado como fallback |

O codificador sobrescreve apenas essas quatro saídas quando executado novamente; não apaga sequências nem altera mídias da capa. O tamanho final depende do render da main.

Para gerar quadros-chave isolados, sem codificar:

```powershell
foreach ($quadro in @(0, 60, 90, 150, 210, 225, 261, 285, 360, 449)) {
  $saida = '../../pbi/qa/encerramento/cromio-{0:000}.png' -f $quadro
  npx remotion still src/index.ts Encerramento $saida --frame=$quadro --image-format=png --gl=angle
  if ($LASTEXITCODE -ne 0) { throw "Falha no quadro $quadro." }
}
```

## Integração no Power BI · somente main

Os dois DAX de desenho da T23 já estão gerados. Com o Desktop do projeto fechado e o estado da sessão principal preservado, a main pode integrar pelo gerador existente. Os comandos abaixo afetam o PBIP e **não foram executados pelo Codex**:

```powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições'

# Regera somente os .dax da T23; -I exige inserir explicitamente os imports locais.
python -I -B -X utf8 -c "import sys,runpy; sys.path.insert(0,'pbi/scripts'); runpy.run_path('pbi/scripts/desenho_t23.py',run_name='__main__')"
if ($LASTEXITCODE -ne 0) { throw 'Falha no gerador T23.' }

# Integra a arvore DAX atual da main; o gerador guarda backup do TMDL.
python -I -B -X utf8 pbi/scripts/dax_para_tmdl.py --dax pbi/dax --saida pbi/pbip/Eleicoes.SemanticModel/definition/tables/_Medidas.tmdl --tabela _Medidas --ns eleicoes-2026 --descricao 'Medidas do painel: contas (todo número que o leitor vê) e desenho (HTML, ALT, specs). Gerada a partir de pbi/dax/**/*.dax por pbi/scripts/gerar_modelo.py; não edite à mão.' --aplicar
if ($LASTEXITCODE -ne 0) { throw 'Falha ao integrar medidas.' }

# Monta o relatorio da main, com backup; nao executar se outros modulos estiverem incompletos.
python -I -B -X utf8 pbi/scripts/montar_pbip.py --aplicar
if ($LASTEXITCODE -ne 0) { throw 'Falha ao montar relatorio.' }
```

Depois da publicação das quatro mídias pelo fluxo da main, abrir a tela **29 / T23** no Desktop e repetir no destino Service. Confirmar o carregamento das URLs finais, o uso real do codec, as fontes, contraste e tamanho dos pontos no Fit to Page; percorrer os quadros-chave com o HTML sobreposto. Conferir especialmente selo × faixa em y 544, faixa × achados em y 590, rótulos das origens antes de 7,4 s e diferença central depois de 8,7 s. Testar voltar à T23, pausa/buffering, bloquear cada fonte, bloquear ambas, autoplay negado, movimento reduzido e os onze atalhos. Em modo de edição, selecionar o botão e pressionar `Ctrl+Enter` pelo teclado físico.

## Evidência e limites

No sandbox passaram TypeScript, os cinco testes existentes da capa, nove testes Node do encerramento, seis conferências Python da T23/dados, sintaxe do PowerShell 5.1 e `git diff --check`. Os testes cobrem conservação por origem/lote, somas, frações, simetria, limite das faixas, 90 SVGs finais idênticos, sincronia por currentTime, contadores, falhas e fallback.

`pbi/qa/encerramento/` guarda o estado anterior da T23, hashes dos fontes da capa, dez quadros SVG de revisão e `validar.py`. A comparação prova que as contas, ALT e textos dos achados foram preservados em relação ao início desta tarefa, inclusive **reeleito** e os filtros de momento já corrigidos pela main.

**Pendentes da main:** render Chromium, codificação real, pôsteres JPEG, inspeção visual do resultado composto, teste no Desktop/Service e publicação. Os SVGs e o DOM simulado são evidência de código; não equivalem ao render final do Power BI. Não houve commit, push, escrita no PBIP ou geração de imagem por IA.
