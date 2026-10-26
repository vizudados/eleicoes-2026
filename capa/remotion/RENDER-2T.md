# Render da capa com os dois turnos · entrega para a main

Pronto para renderizar em Remotion. **21 s, 30 fps, 1920 × 1080, 630 quadros (0–629)**.
Não foi executado render no sandbox do Codex: o Chromium encontra `spawn EPERM`. Não há imagem nova.
O HTML T00 e sua sincronização ficam com a main/outro agente.

## Comandos exatos · PowerShell 5.1

Execute fora do sandbox que bloqueia o Chromium. As dependências locais já estão instaladas; se necessário,
rode `npm ci` nesta pasta e confira o código de saída antes de continuar. Não é preciso refazer a arte.

```powershell
Set-Location -LiteralPath 'C:\Users\lucas\Downloads\Eleições\capa\remotion'

# 1. Dados dos dois turnos; somente leitura dos CSVs/malhas, escrita em public/dados/capa.json.
python -I -X utf8 scripts/preparar_dados.py
if ($LASTEXITCODE -ne 0) { throw 'Falha ao preparar os dados.' }

# 2. Conferências sem Chromium.
npx tsc --noEmit
if ($LASTEXITCODE -ne 0) { throw 'Falha no TypeScript.' }
python -I -X utf8 scripts/testar_dados.py
if ($LASTEXITCODE -ne 0) { throw 'Falha nas conferências dos CSVs.' }
npm test
if ($LASTEXITCODE -ne 0) { throw 'Falha nas conferências da animação.' }

# 3. Sequência nova, preservando out/seq e os vídeos antigos.
npx remotion render src/index.ts Capa out/seq-2t --sequence --image-format=png
if ($LASTEXITCODE -ne 0) { throw 'Falha ao renderizar a sequência.' }

# 4. Codificação: valida 000–629 e igualdade de todos os PNGs 540–629 antes de gerar os novos nomes.
powershell -NoProfile -File scripts/codificar.ps1
if ($LASTEXITCODE -ne 0) { throw 'Falha ao codificar os arquivos finais.' }
```

Equivalentes: `npm run dados`, `npm run render` e `npm run codificar`. O teste Node usa
`--test-isolation=none` e a API local do TypeScript, dispensando processos filhos no sandbox.
Os arquivos novos em `docs/midia/capa/` são:

- `capa-2t.mp4`
- `capa-2t.webm`
- `capa-2t-final.jpg` (quadro 629; mapa do 2º turno)
- `capa-2t-inicio.jpg` (quadro 0)

O codificador preserva os arquivos antigos. O tamanho final dos novos arquivos depende do render e não foi medido.

## Roteiro para sincronizar o HTML

| Trecho | Segundos | Quadros, base zero |
|---|---|---|
| Abertura, bandeira, voo, contorno e surgimento dos pontos | Tempos originais mantidos | 0 em diante |
| Cor do 1º turno | 9,314095714286–12,396044285714; janela visível 9,333333333–12,4 | primeira alteração 280; completo no 372 |
| Respiro com o 1º turno completo | 12,4–13,2 | 372–396 |
| Repintura do 2º turno | 13,2–16,7; primeira alteração visível em 13,233333333 | 396–501; primeira alteração 397 |
| Mapa do 2º turno pronto; ambiente assenta | 16,7–18,0 | 501–540 |
| Composição inteira parada | 18,0–21,0 | 540–629, 90 quadros |

O primeiro esmaecimento mantém a fórmula e todos os tempos originais. A janela de 9,3–12,8 s no LEIAME anterior
era aproximada. A segunda onda segue a mesma ordem local da primeira; cada ponto leva 1,05 s para mudar de cor.
O rótulo externo pode trocar de “1º turno” para “2º turno” em **13,2 s**; durante a repintura o mapa é uma transição.
No modo de movimento reduzido, pôster e HTML já devem representar o 2º turno. Nenhum texto novo foi posto no vídeo.

## Quadros que a main deve olhar

Os PNGs completos já estarão em `out/seq-2t/element-NNN.png`. Para gerar os mesmos quadros avulsos:

```powershell
node scripts/quadros.mjs 0 120 240 372 396 436 449 501 540 629
if ($LASTEXITCODE -ne 0) { throw 'Falha nos quadros de revisão.' }
python -I -X utf8 scripts/folha.py out/contato-2t.jpg q000 q120 q240 q372 q396 q436 q449 q501 q540 q629
if ($LASTEXITCODE -ne 0) { throw 'Falha na folha de contato.' }
```

| Quadro | Tempo | Conferir |
|---|---|---|
| 0, 120, 240 | 0; 4; 8 s | Abertura, bandeira e chegada ao mapa preservadas. Comparar com a capa antiga. |
| **372** | **12,4 s** | Todos os pontos na cor do 1º turno, sem halo novo. |
| 396 | 13,2 s | Mesmo mapa do 1º turno ao fim do respiro; a repintura ainda está em progresso zero. |
| **436** | **14,533333333 s** | Uirapuru, GO (`5221577`), em **x 1021,4; y 581,8**, brilho no sentido Lula → Flávio. Pico contínuo em 14,538608682447 s. |
| **449** | **14,966666667 s** | Meio da repintura; um dos 211 municípios Flávio → Lula, `5209150`, em **x 1018,7; y 644,3**, praticamente no pico do brilho (14,966678817799 s). Ver também os demais pontos só esmaecendo. |
| **501** | **16,7 s** | Todos os pontos na cor do 2º turno; nenhum halo de troca permanece. |
| **540 e 629** | **18,0 e 20,966666667 s** | Composição completa e idêntica, sem deriva de nuvem, cintilação ou oscilação da água. |

Os halos são creme, duram 0,6 s, têm o mesmo tempo/força nos dois sentidos e são recortados na zona do mapa.
Nenhum ponto muda de posição ou raio durante a repintura. O raio do 1º turno foi mantido nos dois mapas para
evitar salto visual; o 2º turno altera a cor, e seus válidos ficam disponíveis no JSON para conferência.

Após codificar, conferir MP4 e WebM decodificados, a ausência de emenda do fundo `#1C1915`, o pôster final,
e a sobreposição real do HTML (título, números, rodapé e setas) com os novos nomes. O vídeo toca uma vez, sem `loop`.
A revisão do SVG no sandbox valida dados/atributos, mas não substitui essa conferência visual do Chromium e dos codecs.

## Dados e verificações já executadas no sandbox

- Preparador executado: **5.570 pontos**, com `m`/`m2`, `cor`/`cor2`, `validos`/`validos2`, `cd_ibge` e `troca`.
- **211** trocas Flávio → Lula; **1** Lula → Flávio, Uirapuru, GO (`5221577`); empates não contam.
- Válidos municipais do 2º turno: **123.707.324 no desenho = 123.710.622 no CSV − 3.298** de
  Boa Esperança do Norte, MT (`5101837`), sem coordenada. Votos do exterior não são adicionados a essa soma municipal.
- Comparação com o JSON anterior à edição: `x`, `y`, `r`, `cor`, `d`, `u`, `uf`, céu, bandeira, contornos,
  ilhas, divisas e estrelas preservados integralmente. Somente `m` ganha maior precisão, sem alterar a cor original.
- `npx tsc --noEmit`; 4 testes Python (cobertura/somas, valores por município, empates, paleta/limites dos halos);
  5 testes Node (SVG real dos turnos, respiro, onda, posição/raio, brilho e duração).
- Sintaxe do codificador analisada pelo parser do Windows PowerShell 5.1. A codificação real depende do render da main.
