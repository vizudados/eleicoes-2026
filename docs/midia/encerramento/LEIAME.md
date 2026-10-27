# Encerramento · rodada 2 · hemiciclo e entrada em CSS

Os votos saem do mapa dos municípios e ocupam um hemiciclo central, com Flávio à esquerda e Lula à direita. As parcelas comuns formam pares espelhados; os 89 pontos excedentes de Lula chegam por último e ficam à esquerda do eixo central, destacados na própria cor. A diferença aparece abaixo da peça, seguida da participação e dos achados, e tudo termina parado.

**15 s · 30 fps · 1920 × 1080 · 450 quadros (0–449) · sem áudio e sem repetição.** Composição Remotion `Encerramento`; a composição `Capa` não foi alterada. Somente desenho em código, sem imagem gerada, bandeira, estrelas ou horizonte.

Esta rodada substitui a versão reprovada nas capturas `pbi/qa/encerramento/desktop/e00.png…e08.png`. As mídias existentes continuam sendo da primeira rodada até a main executar o novo render, a codificação e a publicação. A sequência nova é `out/seq-encerramento-r2/`; não usar `out/seq-encerramento/`.

## O que mudou

- Foi removido `sincronizar.js`. Não há `<script>`, eventos de vídeo, `currentTime`, contadores em JavaScript ou classe de visibilidade dependente de código.
- O HTML usa as classes `sobe` da casa com atrasos CSS explícitos, derivados do mesmo roteiro JSON do Remotion. Os números entram com seu valor DAX final.
- O protagonista final é um hemiciclo de raio externo 280 px, base y 480 e 33 fileiras, com pontos de raio 2,2 px. As faixas antigas foram removidas.
- O mapa inicial cresceu de escala 0,51 para 0,64: cerca de 25%. O vídeo permanece sempre separado das caixas de texto.
- Diferença em y 558, participação em y 626, achados a partir de y 680. As caixas dos onze botões acompanham as novas linhas.

## Roteiro compartilhado

Fonte única: `capa/remotion/src/encerramento/roteiro.json`. Entrada HTML de 0,6 s, contada a partir da carga da página.

| Tempo | Quadros, base zero | O que acontece |
|---|---|---|
| 0–0,6 s | 0–18 | Entra o título em HTML. O contorno do Brasil começa em 0,15 s. |
| 0,65–2,1 s | 20–63 | Surgem os rótulos de origem e os municípios. Contorno completo em 1,8 s; mapa maior, livre de números por cima. |
| 1,7–2,5 s | 51–75 | Surgem os fragmentos de votos, com área proporcional ao peso de cada fragmento. |
| 2,6–4,0 s | 78–120 | Partem os votos das parcelas comuns das duas candidaturas, com a mesma regra de tempo e movimento. |
| 4,0–7,2 s | 120–216 | Os fragmentos ocupam seus assentos e o mapa esmaece de 4,8 a 7,2 s. Todos os pares comuns terminam de chegar até 7,2 s. |
| 6,2–6,9 s | 186–207 | Partem por último os fragmentos dos 89 lotes excedentes de Lula. |
| 7,65–8,7 s | 230–261 | Os excedentes ocupam o corredor à esquerda do eixo. A última entrega está concluída antes de 8,7 s. |
| **8,9–9,5 s** | **267–285** | Com os 2.483 assentos completos, entram juntos os resultados de Flávio e Lula e a legenda de 50 mil votos por ponto cheio. |
| **9,5–10,1 s** | **285–303** | Os excedentes acendem, sem mudar de cor. Entra a diferença final abaixo do hemiciclo. |
| **10,2–10,8 s** | **306–324** | Entra a linha de abstenção e comparecimento. |
| **10,9–11,5 s** | **327–345** | Entram os achados dos cinco atos. |
| **11,3–11,9 s** | **339–357** | Entram frase de fecho e fontes. |
| **12–15 s** | **360–449** | 90 quadros idênticos. No HTML, o vídeo cede lugar ao pôster final aos 12 s. |

Os voos não representam a cronologia da apuração nem transferências de indivíduos entre candidaturas ou turnos. Reúnem os votos finais de uma mesma eleição.

## Hemiciclo e votos exatos

| Cobertura | Lula | Flávio | Válidos |
|---|---:|---:|---:|
| Municípios de 2026 | 64.056.078 | 59.654.544 | 123.710.622 |
| Exterior, ZZ | 200.154 | 171.497 | 371.651 |
| **Nacional** | **64.256.232** | **59.826.041** | **124.082.273** |

Fontes: `dados/pbi/municipio_2turno.csv` e `dados/pbi/uf_2turno.csv`. O preparo exige 5.571 municípios únicos, 27 UFs mais exterior, as somas acima e igualdade município + exterior = nacional.

São **5.572 origens, 13.625 fragmentos e 2.483 pontos finais**. Cada fragmento preserva um inteiro positivo de votos de uma origem real; os intervalos cumulativos origem × lote mantêm as somas exatas. Municípios pequenos não são descartados.

- Parcela comum, por candidato: 1.196 pontos de 50 mil e um de 26.041 = **59.826.041**.
- Diferença de Lula: 88 pontos de 50 mil e um de 30.191 = **4.430.191**.
- Total de pontos: 1.197 de Flávio, 1.286 de Lula. A área dos pontos incompletos representa sua fração: raio = `2,2 × raiz(votos / 50.000)`.

As 33 fileiras têm raios de 50 a 280 px. Os 1.197 pares comuns são exatamente espelhados e usam a mesma cor de candidatura da casa, opacidade, área, duração e distribuição. Os 89 excedentes ocupam duas ou três posições por fileira à esquerda do eixo, separados dos pontos azuis. O corredor central permite comparar parcelas iguais: **o eixo não é um corte de 50% dos válidos**. Não se confunde a diferença de 4.430.191 com os votos acima da metade do total.

Cores: fundo tinta `#1C1915`, mapa/eixo areia `#CBBDA2`, Flávio `#8FA8CF`, Lula `#D9877B`. No fim, pontos comuns com opacidade 0,74; excedentes com opacidade 1 e contorno fino na mesma cor.

A malha e os 5.570 centroides disponíveis são lidos do JSON existente da capa, preservado. Boa Esperança do Norte, MT (`5101837`), não tem coordenada nessa malha e parte de uma entrada separada, como o exterior. Todos os seus votos são mantidos: Lula 945, Flávio 2.353. Os rótulos de origem ficam à esquerda, fora da área dos pontos. Os hashes dos CSVs, geometria e roteiro ficam no JSON preparado.

## Layout e separação permanente

Toda a camada gráfica, incluindo mapa, trajetórias, eixo e assentos, está recortada em **x 620–1300, y 152–517**. Os voos reais também foram varridos por quadro e permanecem dentro dessa área, sem depender do recorte para esconder colisões.

| Bloco HTML | Caixa em px |
|---|---|
| Título | x 150, y 68, largura 1620, altura 74 |
| Flávio | x 140, y 272, largura 420, altura 260 |
| Lula | x 1360, y 272, largura 420, altura 260 |
| Escala | x 620, y 528, largura 680, altura 18 |
| Diferença | x 600, y 558, largura 720, altura 54 |
| Participação | x 150, y 626, largura 1620, altura 28 |
| Achados | Cabeçalhos a partir de y 680; última caixa termina em y 980 |
| Fecho / fontes | y 946 / 984, somente nas duas colunas da esquerda |
| Rodapé institucional | Mantido em y 1014 |

A diferença fica em uma linha central: rótulo, valor e “votos entre Lula e Flávio”. Abstenção e comparecimento ficam lado a lado na linha seguinte. Não há mapa atrás desses números em qualquer quadro, mesmo se CSS e vídeo perderem sincronia.

Achados com corpo 15 px, entrelinha 20 px, duas linhas por caixa de 54 px. O texto observado nas capturas foi medido com a fonte Sora real e cabe. O fecho permanece à esquerda da coluna do quinto ato, sem sobreposição com seus últimos achados. O selo é **reeleito**; medidas, máscaras numéricas, ALT e textos dos onze achados foram preservados.

## CSS e fallback, sem eventos

O HTML usa `sobe fx-resultado`, `sobe fx-diferenca`, `sobe fx-participacao`, `sobe fx-achados` e atrasos CSS. O estado base é o texto final visível; `animation-fill-mode: both` vem da classe `sobe` da casa. Sem animação ou com movimento reduzido, os dados ficam imediatamente completos.

Há uma imagem de pôster final sempre por baixo do vídeo e o mesmo endereço em `video.poster`. Uma animação CSS de `visibility` mantém o vídeo visível até 12 s e depois o oculta, deixando o pôster final. Se a reprodução falhar ou ficar presa no meio, a apresentação termina no pôster e com todos os textos completos. Com movimento reduzido ou impressão, o vídeo fica oculto desde o início.

**Limite assumido do CSS:** o relógio é a carga da página; não acompanha buffering, pausa ou início efetivo do vídeo. A separação espacial evita pontos atrás de texto mesmo nesses casos, e o pôster aos 12 s garante o desfecho. A main deve conferir a carga real no Desktop, como faz com a capa. Não se afirma sincronização por eventos.

As mídias usam o host existente da capa e os mesmos nomes finais, com `?v=hemiciclo-r2` no HTML para renovar o cache. O parâmetro não altera os arquivos no Pages. O codificador deve ser executado e os arquivos publicados antes da revisão no Desktop.

Referências de plataforma: [visibility em CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/visibility) e [poster do elemento video](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/video#poster). A validação do visual no Power BI continua sendo da main.

## Render e codificação · main · PowerShell 5.1

Não reinstalar dependências. Executar fora do sandbox, com a GPU em `--gl=angle`. A sequência da rodada 1 será preservada.

~~~powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições\capa\remotion'

python -I -B -X utf8 scripts/preparar_encerramento.py
if ($LASTEXITCODE -ne 0) { throw 'Falha nos dados.' }
npx tsc --noEmit
if ($LASTEXITCODE -ne 0) { throw 'Falha no TypeScript.' }
npm test
if ($LASTEXITCODE -ne 0) { throw 'Regressao na capa.' }
node --test --test-isolation=none scripts/testar_encerramento.cjs
if ($LASTEXITCODE -ne 0) { throw 'Falha no encerramento.' }
python -I -B -X utf8 ../../pbi/qa/encerramento/validar.py
if ($LASTEXITCODE -ne 0) { throw 'Falha na T23.' }

npx remotion render src/index.ts Encerramento out/seq-encerramento-r2 --sequence --image-format=png --image-sequence-pattern=element-[frame].[ext] --gl=angle
if ($LASTEXITCODE -ne 0) { throw 'Falha na sequencia PNG.' }
powershell -NoProfile -File scripts/codificar_encerramento.ps1
if ($LASTEXITCODE -ne 0) { throw 'Falha na codificacao.' }
~~~

O codificador agora lê **somente `out/seq-encerramento-r2/`**. Exige `element-000.png…element-449.png` e SHA-256 idêntico nos 90 PNGs de 360–449. Gera, em `docs/midia/encerramento/`:

- `encerramento.mp4`: H.264 High, CRF 10, yuv420p, BT.709, faixa limitada, faststart, 15 s.
- `encerramento.webm`: VP9 em duas passadas, 2,6 Mb/s, yuv420p, BT.709, 15 s.
- `encerramento-final.jpg`: quadro 449, qualidade 85, sem subamostragem.
- `encerramento-inicio.jpg`: quadro 0, somente evidência.

Sobrescreve apenas as quatro saídas finais; não apaga sequências nem muda a capa.

Quadros-chave isolados:

~~~powershell
foreach ($quadro in @(0, 60, 90, 150, 216, 240, 261, 267, 285, 303, 327, 360, 449)) {
  $saida = '../../pbi/qa/encerramento/rodada2/cromio-{0:000}.png' -f $quadro
  npx remotion still src/index.ts Encerramento $saida --frame=$quadro --image-format=png --gl=angle
  if ($LASTEXITCODE -ne 0) { throw "Falha no quadro $quadro." }
}
~~~

## Integração · somente main

Com o Desktop do projeto fechado e os módulos da sessão principal prontos:

~~~powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições'

python -I -B -X utf8 -c "import sys,runpy; sys.path.insert(0,'pbi/scripts'); runpy.run_path('pbi/scripts/desenho_t23.py',run_name='__main__')"
if ($LASTEXITCODE -ne 0) { throw 'Falha no gerador T23.' }

python -I -B -X utf8 pbi/scripts/dax_para_tmdl.py --dax pbi/dax --saida pbi/pbip/Eleicoes.SemanticModel/definition/tables/_Medidas.tmdl --tabela _Medidas --ns eleicoes-2026 --descricao 'Medidas do painel: contas (todo número que o leitor vê) e desenho (HTML, ALT, specs). Gerada a partir de pbi/dax/**/*.dax por pbi/scripts/gerar_modelo.py; não edite à mão.' --aplicar
if ($LASTEXITCODE -ne 0) { throw 'Falha nas medidas.' }

python -I -B -X utf8 pbi/scripts/montar_pbip.py --aplicar
if ($LASTEXITCODE -ne 0) { throw 'Falha no relatorio.' }
~~~

O gerador de desenho da T23 já foi executado; os comandos que escrevem no PBIP não foram executados pelo Codex. Não usar a mídia da rodada 1 com o HTML novo.

## QA e revisão no Desktop

Passaram TypeScript, 5 testes existentes da capa, 8 testes Node do encerramento e 10 conferências Python, além do parser PowerShell 5.1 e whitespace. As verificações cobrem:

- Conservação de cada voto por origem e lote, nacional e exterior.
- Simetria dos pares, frações, 33 fileiras e os 89 excedentes à esquerda chegando por último.
- Separação entre pontos finais, incluindo os contornos.
- Varredura dos voos a cada quadro e caixas de texto fora da área gráfica, independentemente da fase do CSS.
- 90 SVGs finais idênticos, composição sem imagem/texto embutido.
- HTML e declaração real de 12 visuais sem script/eventos, atrasos CSS, pôster e movimento reduzido.
- Preservação de contas, ALT, achados, “reeleito” e dos onze bookmarks; largura dos textos com Sora real.

Evidência em `pbi/qa/encerramento/rodada2/`: quadros SVG, dados de largura e texto, estado anterior da rodada e relatório de testes. As capturas antigas e os arquivos da primeira rodada ficam como **evidência reprovada**, sem ser apresentados como aprovação desta versão.

A main deve fotografar o Desktop novamente em 0, 2, 4, 6, 8, 9, 9,5, 10,2, 11 e 12 s; conferir o pôster final e Fit to Page, bloquear cada fonte e ambas, testar cache frio, movimento reduzido e os onze atalhos. Selecionar os botões e usar `Ctrl+Enter` pelo teclado físico em modo de edição. Repetir carregamento e legibilidade no Service.

**Pendentes da main:** novo render PNG, MP4/WebM, JPEGs, publicação, integração e aceite visual real. Nenhuma imagem por IA, commit, push ou escrita no PBIP foi feita pelo Codex nesta rodada.
