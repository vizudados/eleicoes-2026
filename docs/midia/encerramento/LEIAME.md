# Encerramento · rodada 3 · o mapa vira o resultado

O mapa entra com aproximadamente 620 px de altura, centrado em (960, 560), e os votos sobem para um hemiciclo clássico de arcos contínuos. Flávio ocupa os assentos a partir da esquerda e Lula a partir da direita; a diferença forma uma cunha de 89 assentos, simétrica em torno do eixo vertical. A cunha acende na própria cor de Lula, os números entram em HTML e o quadro termina parado.

**15 s · 30 fps · 1920 × 1080 · 450 quadros (0–449).** Sem áudio, repetição, imagens geradas, bandeira, estrelas ou horizonte. Composição `Encerramento`; a composição `Capa` está preservada.

Esta rodada substitui o corredor e a coluna solta da rodada 2. As mídias publicadas só serão atualizadas quando a main renderizar e publicar esta versão. A sequência nova é **`out/seq-encerramento-r3/`**.

## Roteiro

Fonte única dos tempos e das caixas: `src/encerramento/roteiro.json`.

| Tempo | Quadros | Vídeo e HTML |
|---|---|---|
| 0–0,6 s | 0–18 | Entra o título. O mapa começa a se desenhar em 0,15 s, grande e centrado. |
| 0,65–2,1 s | 20–63 | Os municípios acendem. Contorno completo em 1,8 s; a base inclui ilhas e divisas. Sem pontos isolados ou rótulos fora do mapa. |
| 1,7–2,5 s | 51–75 | Fragmentos de votos aparecem nas posições dos municípios, com área proporcional ao peso. O exterior ainda não aparece. |
| 2,6–4,0 s | 78–120 | Partem as parcelas comuns, subindo para os assentos. O exterior entra como um fio discreto a partir da borda direita, sem texto ou ponto de origem solto. |
| 4,0–7,2 s | 120–216 | Formam-se os arcos. O mapa esmaece entre 4,8 e 7,2 s. Todas as parcelas comuns chegam até 7,2 s. |
| 6,2–6,9 s | 186–207 | Partem por último os fragmentos dos assentos da cunha. |
| 7,65–8,7 s | 230–261 | A cunha se completa. O fio do exterior desaparece até 8,7 s. |
| 8,8 s | 264 | O recorte CSS do vídeo diminui antes de qualquer bloco de resultado aparecer. No fluxo normal, o mapa e o fio já sumiram. |
| **8,9–9,5 s** | **267–285** | Entram os resultados dos dois candidatos e a escala de 50 mil votos, centralizada sob o hemiciclo, em **16 px**. |
| **9,5–10,1 s** | **285–303** | A cunha acende com preenchimento e contorno fino na mesma cor; o resto esmaece de 0,82 para 0,64. Entra a diferença e o aceno “a cunha do meio: 89 pontos”. |
| **10,2–10,8 s** | **306–324** | Entra a participação, com as mesmas medidas de abstenção e comparecimento. |
| **10,9–11,5 s** | **327–345** | Entram os achados, preservados. |
| **11,3–11,9 s** | **339–357** | Entram o fecho e as fontes. |
| **12–15 s** | **360–449** | 90 quadros idênticos. O CSS oculta o vídeo aos 12 s e deixa o pôster final no lugar. |

A reunião de pontos não representa a ordem da apuração ou transferências de indivíduos. Mostra os votos finais de uma mesma eleição.

## Hemiciclo sem vão

As 36 fileiras têm raios de 0 a 280 px, centro x 960 e base y 470. A primeira é o único assento central na base; as outras 35 vão de 0 a π, com espaçamento angular uniforme, incluindo as duas pontas na base. O semicírculo fecha até o centro da base, sem corredor, vazio interno ou entalhe.

A quantidade por fileira é proporcional ao raio e fecha em **2.483 assentos**. Para garantir simetria exata, 1.241 pares são distribuídos entre as fileiras e uma única fileira recebe o assento do eixo. Todas as fileiras são ordenadas **juntas pelo ângulo**, com ordem espelhada para empates.

Na ordem do ângulo crescente, da direita para a esquerda:

- Índices 0–1196: parcela comum de Lula, 1.197 assentos.
- Índices 1197–1285: cunha de Lula, **89 assentos**.
- Índices 1286–2482: Flávio, 1.197 assentos.

A cunha é a fatia entre a fronteira de Flávio e o seu espelho. Contém **44 assentos à esquerda, um no eixo e 44 à direita**. O ponto parcial da cunha está no eixo; os demais formam pares com a mesma posição espelhada, área e quantidade de votos. O vermelho passa do meio em 44 assentos. A linha fina tracejada areia marca o eixo dos 50%.

Cores da casa: fundo `#1C1915`, traço/eixo `#CBBDA2`, Flávio `#8FA8CF`, Lula `#D9877B`. Os dois lados usam o mesmo raio e o mesmo tratamento. O contorno da cunha tem 0,55 px, sem brilho externo, pulso ou nova cor.

## Dados, frações e cobertura

| Cobertura | Lula | Flávio | Válidos |
|---|---:|---:|---:|
| Municípios | 64.056.078 | 59.654.544 | 123.710.622 |
| Exterior | 200.154 | 171.497 | 371.651 |
| **Nacional** | **64.256.232** | **59.826.041** | **124.082.273** |

Fontes: `dados/pbi/municipio_2turno.csv` e `dados/pbi/uf_2turno.csv`, ano 2026. O preparo exige 5.571 municípios únicos, 27 UFs e exterior e as somas acima. Não altera os arquivos de dados.

Os **2.483 assentos** se decompõem, com precisão, em **2.480 pontos cheios e três frações**:

- Flávio: 1.196 × 50.000 + 26.041 = **59.826.041**.
- Parcela comum de Lula, espelhada: os mesmos **59.826.041**.
- Cunha: 88 × 50.000 + 30.191 = **4.430.191**.
- Lula total: **64.256.232**.

O raio é `2,2 × raiz(votos / 50.000)`, para a área representar a fração. Não são 2.482 pontos cheios: isso excederia o total nacional. A divisão conserva exatamente cada voto de cada origem e gera 13.625 fragmentos, sem amostra ou descarte de cidades pequenas.

O HTML mantém as medidas originais para resultados, percentuais, diferença, participação, ALT, achados e **reeleito**. Uma conta nova, `T23 · diferença em pontos`, calcula `ROUNDUP(DIVIDE([T23 · diferença final], 50000), 0)` para alimentar o novo aceno. Não se calcula esse número no desenho ou em JavaScript.

## Mapa e Boa Esperança do Norte

A geometria e os 5.570 centroides existentes vêm do JSON da capa, derivado das malhas do IBGE. O fator 620/560 amplia a altura de referência para 620 px, com centro em (960, 560). Os contornos das ilhas também são desenhados.

Boa Esperança do Norte, MT, código **5101837**, não existe na malha local. A página [IBGE Cidades e Estados](https://www.ibge.gov.br/cidades-e-estados/mt/boa-esperanca-do-norte.html) confirma o código. Nas consultas desta rodada, o Cidades retornou 403 e a API de malhas retornou 500, inclusive com os períodos 2024 e 2025.

Foi aplicada a alternativa autorizada no brief: **média dos centroides de Nova Ubiratã (5106224) e Sorriso (5107925)**. Na projeção original da capa, eles são (936,2; 574,3) e (942,1; 561,5), cuja média é (939,15; 567,9). O ponto é transformado pelo mesmo enquadramento dos demais municípios. Trata-se de uma **posição aproximada**, não de coordenada oficial da sede. O método e os códigos de origem ficam no JSON preparado. Seus votos, Lula 945 e Flávio 2.353, são integralmente preservados.

Assim, aparecem **5.571 posições municipais no mapa**: as 5.570 originais e o município acrescentado. Nenhum ponto municipal fica em uma entrada artificial fora do país. O exterior não aparece como marcador na abertura: seus fragmentos só entram durante o voo, a partir da borda direita (1920, 650), acompanhados pelo fio areia. Não há “Boa Esperança do Norte”, “Exterior” ou qualquer outro texto dentro do vídeo.

## Fidelidade geométrica com a T23

As caixas fixas e os grupos de achados agora têm uma fonte única no roteiro JSON. A T23 usa `_caixa()` para gerar o CSS e lê `GRUPOS` desse JSON para o HTML e os botões. A prova lê a mesma fonte.

| Bloco | Caixa em pixels |
|---|---|
| Título | 150, 68, 1620 × 74 |
| Flávio / Lula | 140 / 1360, 272, 420 × 260 |
| Escala, 16 px | 620, 510, 680 × 22 |
| Diferença com aceno | 600, 558, 720 × 54 |
| Participação | 150, 626, 1620 × 28 |
| Achados | Cabeçalhos a partir de y 680; última caixa termina em y 980 |
| Fecho / fontes | 150, 946 / 984, largura 940 |
| Rodapé | 150, 1014, 1620 × 28 |

As fontes reais da Sora são usadas nas conferências de largura dos achados, da escala e da diferença com a nota nova.

### Script de prova

~~~powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições\capa\remotion'
node scripts/provar_encerramento.cjs
if ($LASTEXITCODE -ne 0) { throw 'Sobreposicao na T23.' }
~~~

Saídas em `pbi/qa/encerramento/rodada3/`:

- **`final-com-caixas.svg`**: quadro final da composição real, com as caixas usadas pelo HTML desenhadas por cima, em 1920 × 1080.
- **`sobreposicoes.json`**: contatos por quadro e no final, contagem de assentos, cunha, marcas conferidas e hashes das fontes.
- `quadro-*.svg`: quadros-chave da composição, gerados pelos testes.

O script compila com a API TypeScript local e usa o SVG real de `DesenhoEncerramento`. A composição e a varredura leem as mesmas primitivas de `geometria.ts`, sem reimplementar trajetórias em outro código. A conferência cobre **450 quadros e 3.596.975 marcas visíveis**, incluindo o raio do contorno da cunha. Durante as entradas, considera conservadoramente mais 14 px de altura, cobrindo o deslocamento da classe `sobe`.

Resultado: **zero contatos na animação, zero no quadro final e zero entre os recortes CSS e as caixas visíveis**. Os testes Python também confirmam que a T23 gera o CSS a partir dessas posições, que o gabarito da casca coincide e que os hashes da prova são atuais.

A prova é de dados e coordenadas do desenho/HTML. O render dos codecs, fontes no host e composição real no Desktop ainda precisam do aceite da main; não se apresenta essa prova como comparação já executada de pixels decodificados do MP4 com o Power BI.

## CSS e proteção quando o vídeo atrasa

Continuam somente CSS e classes `sobe`, com estado final legível sem animação. Não há `<script>`, controlador, eventos de vídeo ou contador em JavaScript.

A abertura permite o mapa grande em **x 0–1920, y 160–900**. Aos **8,8 s**, antes de os números entrarem em 8,9 s, o recorte CSS diminui para **x 620–1300, y 160–490**. Esse recorte e as entradas compartilham o relógio da página. Assim, mesmo se o vídeo estiver atrasado no mapa, nenhum ponto ou traço passa por trás dos números, da escala ou dos achados.

O pôster final está sempre por baixo do vídeo e também em `video.poster`. Aos 12 s, o CSS oculta o vídeo e deixa esse pôster. Com movimento reduzido, impressão ou animação desativada, o estado base já é o pôster e os textos finais. O vídeo não tem `loop`.

As URLs usam `?v=hemiciclo-r3` para renovar o cache. Publicar as mídias novas antes de revisar o HTML novo no Desktop. O CSS continua sem acompanhar buffering ou pausa; a proteção espacial e o pôster garantem o desfecho.

## Render e codificação · main · PowerShell 5.1

Não reinstalar dependências. Usar a GPU com `--gl=angle`, fora do sandbox. O codificador lê somente **`out/seq-encerramento-r3`**, preservando r1/r2.

~~~powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições\capa\remotion'

python -I -B -X utf8 scripts/preparar_encerramento.py
if ($LASTEXITCODE -ne 0) { throw 'Falha nos dados.' }
npx --no-install tsc --noEmit
if ($LASTEXITCODE -ne 0) { throw 'Falha no TypeScript.' }
npm test
if ($LASTEXITCODE -ne 0) { throw 'Regressao na capa.' }
node --test --test-isolation=none scripts/testar_encerramento.cjs
if ($LASTEXITCODE -ne 0) { throw 'Falha nos testes do encerramento.' }
node scripts/provar_encerramento.cjs
if ($LASTEXITCODE -ne 0) { throw 'Sobreposicao na T23.' }
python -I -B -X utf8 ../../pbi/qa/encerramento/validar.py
if ($LASTEXITCODE -ne 0) { throw 'Falha no HTML ou no DAX.' }

npx remotion render src/index.ts Encerramento out/seq-encerramento-r3 --sequence --image-format=png --image-sequence-pattern=element-[frame].[ext] --gl=angle
if ($LASTEXITCODE -ne 0) { throw 'Falha na sequencia PNG.' }
powershell -NoProfile -File scripts/codificar_encerramento.ps1
if ($LASTEXITCODE -ne 0) { throw 'Falha na codificacao.' }
~~~

O codificador exige 450 PNGs, `element-000.png…element-449.png`, e SHA-256 idêntico nos quadros 360–449. Gera em `docs/midia/encerramento/`:

- `encerramento.mp4`: H.264 High, CRF 10, yuv420p, BT.709, faixa limitada, faststart.
- `encerramento.webm`: VP9 em duas passadas, 2,6 Mb/s, yuv420p, BT.709.
- `encerramento-final.jpg`: quadro 449, qualidade 85, sem subamostragem.
- `encerramento-inicio.jpg`: quadro 0, para evidência.

As quatro saídas finais são substituídas quando a main executar o codificador. O tamanho final depende do novo render.

Quadros isolados:

~~~powershell
foreach ($quadro in @(0, 60, 90, 150, 216, 240, 261, 267, 285, 303, 327, 360, 449)) {
  $saida = '../../pbi/qa/encerramento/rodada3/cromio-{0:000}.png' -f $quadro
  npx remotion still src/index.ts Encerramento $saida --frame=$quadro --image-format=png --gl=angle
  if ($LASTEXITCODE -ne 0) { throw "Falha no quadro $quadro." }
}
~~~

## Integração · somente main

Com o Desktop fechado e os módulos da sessão principal prontos:

~~~powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições'

python -I -B -X utf8 -c "import sys,runpy; sys.path.insert(0,'pbi/scripts'); runpy.run_path('pbi/scripts/desenho_t23.py',run_name='__main__')"
if ($LASTEXITCODE -ne 0) { throw 'Falha no gerador T23.' }

python -I -B -X utf8 pbi/scripts/dax_para_tmdl.py --dax pbi/dax --saida pbi/pbip/Eleicoes.SemanticModel/definition/tables/_Medidas.tmdl --tabela _Medidas --ns eleicoes-2026 --descricao 'Medidas do painel: contas (todo número que o leitor vê) e desenho (HTML, ALT, specs). Gerada a partir de pbi/dax/**/*.dax por pbi/scripts/gerar_modelo.py; não edite à mão.' --aplicar
if ($LASTEXITCODE -ne 0) { throw 'Falha nas medidas.' }

python -I -B -X utf8 pbi/scripts/montar_pbip.py --aplicar
if ($LASTEXITCODE -ne 0) { throw 'Falha no relatorio.' }
~~~

Há uma medida de conta nova, `T23 · diferença em pontos`, além dos dois desenhos HTML atualizados. Os arquivos DAX já foram gerados; nenhuma integração no PBIP foi executada pelo Codex.

## Testes e revisão

Passaram TypeScript, **5 testes da capa + 10 do encerramento + 12 conferências Python**, a prova de sobreposição, parser PowerShell 5.1 e `git diff --check`.

Os testes cobrem assentos e somas, arcos sem vão, ordenação angular global, cunha com 44 pares e um centro, simetria das áreas/votos, frações, mapa de 620 px, cobertura geográfica inicial, ausência de marcador do exterior na abertura, chegada da cunha por último, distância entre pontos, 90 quadros finais idênticos e zero colisões. Conferem também medidas/achados preservados, nota de 89 pontos, CSS sem script, larguras com Sora e acoplamento entre caixas, T23 e prova.

Na revisão, a main deve conferir o mapa em q60, a continuidade dos arcos na base e no eixo, a cunha em q303, legenda a 16 px, aceno em HTML, pôster final e as caixas da prova. Repetir as capturas do Desktop com vídeo novo, cache frio, movimento reduzido, mídias bloqueadas e os onze atalhos; em edição, selecionar o botão e usar `Ctrl+Enter` pelo teclado físico.

**Pendentes da main:** render PNG, codecs/JPEGs, publicação, integração e aceite visual no Desktop/Service. Não houve geração de imagem por IA, commit, push ou escrita no PBIP.
