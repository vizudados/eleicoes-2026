# Capa animada · Eleições 2026 · o voto de perto

**Conceito: o céu da bandeira vira o mapa do voto.** As 27 estrelas da bandeira, uma por UF, desenham a bandeira,
voam cada uma para o seu estado, o Brasil se desenha à volta delas, os 5.570 municípios mostram primeiro a margem
do 1º turno e depois a do 2º turno de 2026. Um brilho breve marca as 212 trocas de liderança, nos dois sentidos,
enquanto um horizonte de Norte a Sul se desenha na base. Toca uma vez e para no mapa do 2º turno.

Os arquivos abaixo serão gerados pela main; os antigos `capa.*`, `capa-final.jpg` e `capa-inicio.jpg` são preservados.

| Arquivo | O que é |
|---|---|
| `capa-2t.mp4` | H.264 High, yuv420p, BT.709, faststart · 1920 × 1080 · 30 fps · 21 s |
| `capa-2t.webm` | VP9 (duas passadas, 2,6 Mb/s) · mesmas medidas e duração |
| `capa-2t-final.jpg` | quadro 629, mapa do 2º turno (pôster e movimento reduzido), JPEG 85 |
| `capa-2t-inicio.jpg` | quadro 0 (céu escuro com estrelas fracas), JPEG 85 |

## Roteiro

| Tempo | O que acontece |
|---|---|
| 0–0,25 s | Céu noturno: fundo tinta `#1C1915` e estrelas fracas. |
| 0,25–1,45 s | As 27 estrelas surgem nas posições e grandezas oficiais do disco (ampliado 2×), da 1ª à 5ª grandeza. |
| 1,1–2,75 s | A caneta desenha o círculo, a faixa e escreve ORDEM E PROGRESSO letra a letra. |
| 1,75–3,7 s | A câmera abre do disco para a bandeira inteira; losango e retângulo se desenham a traço. |
| 3,1–4,55 s | Cores esmaecidas em lavagem de tinta: azul, amarelo, branco e verde. A bandeira completa fica um instante. |
| 4,55–7,15 s | Cada estrela voa para o centro da sua UF (da esquerda para a direita da bandeira); a bandeira vira fantasma e some até 7,9 s. |
| 5,0–8,0 s | O contorno do Brasil se desenha numa linha só (do extremo norte, sentido horário); as divisas aparecem quando as estrelas vizinhas pousam. |
| 8,0–10,1 s | As estrelas pulsam e os municípios acendem como estrelas pequenas, em ondas a partir da estrela de cada UF. |
| 9,3–12,4 s | Janela do 1º turno: cada ponto esmaece do creme para a cor da margem de 04/10/2026, com os tempos locais originais. Vermelho: Lula à frente; azul: Flávio à frente. O mapa está inteiramente pintado no quadro 372. |
| 12,4–13,2 s | Respiro de 0,8 s com o mapa completo do 1º turno. |
| 13,2–16,7 s | Segunda onda: cada ponto esmaece da sua cor do 1º turno para a margem de 25/10/2026, na mesma ordem espacial. Cada esmaecimento dura 1,05 s. Só os 211 municípios Flávio → Lula e o 1 Lula → Flávio recebem um pulso creme de 0,6 s, centrado no meio da transição local. |
| 11,0–15,7 s | O horizonte se desenha da esquerda para a direita: Amazônia, sertão, Pelourinho, Congresso, Pão de Açúcar, São Paulo, araucárias, pampa. Entram nuvens, uma garça, um bando e o brilho da água. |
| 16,7–18,0 s | O mapa já mostra integralmente o 2º turno, sem halos. O céu e o horizonte terminam de assentar. |
| 18,0–21,0 s | Toda a composição fica congelada no tempo de 18,0 s: 90 quadros, ou 3 s parados. Último quadro: 629, em 20,966666667 s. |

**Tempos exatos e sincronização do HTML (fora deste projeto):** a fórmula original do 1º turno começa em
9,314095714286 s e termina em 12,396044285714 s nesta base. A 30 fps, a primeira mudança é visível no quadro 280
(9,333333333 s), e o primeiro quadro com todos os pontos pintados é o 372 (12,4 s). O intervalo 9,3–12,8 s do
roteiro anterior era uma estimativa; a animação original foi mantida. O respiro documentado começa no quadro 372
e vai até o 396 (13,2 s); a folga contínua após o último ponto é de 0,803955714286 s. A janela do 2º turno é
exatamente 13,2–16,7 s (quadros 396–501; a primeira mudança é visível no 397). O HTML pode manter “1º turno” até
13,2 s e mudar para “2º turno” a partir de 13,2 s. Não há rótulo novo dentro do vídeo.

O congelamento global aos 18,0 s também fixa as oscilações residuais do brilho da água; somente reduzir a deriva
das nuvens não garantia um quadro inteiramente parado.

Zonas livres para o HTML por cima, herdadas da capa anterior (a main confere novamente no render): título (x 300–1620, y 110–300) sem nada;
números (x 140–560 e 1360–1780, y 380–760) só com estrelas fracas; cabeçalho (y 0–100), rodapé (y 1000–1080) e
setas (x 40–120 e 1800–1880, y 510–570) vazios. Mapa em x 688–1232, y 303–863; horizonte em x 140–1780, y 853–990.

Os novos halos têm raio máximo de 6,5 px, sem filtro de blur, e são recortados na zona do mapa
(x 688–1232, y 303–863). Os 212 halos cabem integralmente nessa zona, conforme teste de coordenadas. O raio dos
pontos não é animado na repintura. Nenhum brilho novo entra nas zonas de título, números, cabeçalho, rodapé ou setas.

## Como rerenderizar

Projeto Remotion em `capa/remotion/` (versões fixas no `package.json`; Node 24, Python 3 com numpy, pandas, scipy e
Pillow, ffmpeg no PATH). Os comandos completos para a main e a lista de quadros estão em
[`capa/remotion/RENDER-2T.md`](../../../capa/remotion/RENDER-2T.md).

```powershell
cd capa/remotion
npm ci
python -I -X utf8 scripts/preparar_dados.py # obrigatório: prepara os dois turnos em public/dados/capa.json
npx tsc --noEmit
python -I -X utf8 scripts/testar_dados.py
npm test
npm run estudio     # opcional: Remotion Studio para ver e ajustar
npm run render      # 630 quadros PNG em out/seq-2t (a main executa fora do sandbox)
npm run codificar   # capa-2t.mp4, capa-2t.webm, capa-2t-final.jpg e capa-2t-inicio.jpg em docs/midia/capa
```

Em PowerShell 5.1, confira `$LASTEXITCODE` depois de cada comando e interrompa se não for zero; o roteiro da main
já inclui essas verificações. `npm run dados` agora prepara apenas os dados; a arte existente é reutilizada.
Para refazer as imagens deliberadamente, o comando separado continua sendo
`python -I -X utf8 scripts/preparar_arte.py` (desnecessário para esta alteração). `npm run codificar` usa
`powershell`, disponível no Windows, sem depender de `pwsh`.

O codificador exige a sequência completa 000–629 e SHA-256 idêntico em todos os PNGs 540–629 antes de gerar os
arquivos finais. Também verifica o código de saída do ffmpeg e do Python. Não usa nem apaga a sequência antiga.

O roteiro fica em `src/tempo.ts` (todos os tempos em segundos). O render é determinístico: tremor do traço,
ordem de revelação e acasos usam sementes fixas. O fundo `#1C1915` decodifica a ±1 nível em 8 bits (limite do
yuv420p); a casca do Power BI na mesma cor não mostra emenda.

## De onde vêm os dados e as imagens

- **Mapa:** malhas do IBGE (`dados/bruto/ibge/malha_uf.json` e `malha_municipios.json`), projeção lon·cos 15° × lat
  como em `pipeline/mapas.py`. Cada ponto é o centroide de um município. **Raio fixo pelo 1º turno**, calculado como
  `1,05 + 1,9 × raiz(válidos1 / máximo(válidos1))` px e arredondado a duas casas; não muda entre turnos para evitar
  um salto de tamanho e preservar a abertura. Os válidos do 2º turno ficam gravados para conferência.
- **Cores dos dois turnos:** margem de 2026 = (Lula − Flávio) ÷ válidos; 1º turno de
  `dados/saida/votos_municipio.csv` (agrupado por `cd_ibge`); 2º turno de `dados/pbi/municipio_2turno.csv`
  (ano 2026, `cd_ibge, pt, adv, validos`). Ambos usam exatamente a mesma escala divergente da casa, de −60 a
  +60 p.p., com as pontas um pouco mais claras para ler sobre a tinta. Cores calculadas da margem sem arredondar;
  margens gravadas com oito casas. Empates em qualquer turno não recebem brilho.
- **Contrato em `public/dados/capa.json`:** arrays paralelos por município; `cd_ibge`, `m`/`m2`, `cor`/`cor2`,
  `validos`/`validos2` e `troca` (`1`: Flávio → Lula; `-1`: Lula → Flávio; `0`: sem troca). `x`, `y`, `r`, `d`,
  `u`, `uf` e `cor` permanecem idênticos aos da capa anterior, assim como o céu, os contornos e a bandeira.
- **Conferência executada:** 5.570 pontos; 211 trocas Flávio → Lula e 1 Lula → Flávio (Uirapuru, GO,
  `5221577`). Válidos do 2º turno no desenho = **123.707.324 = 123.710.622 − 3.298**. A parcela excluída é
  Boa Esperança do Norte, MT (`5101837`), único município do CSV sem coordenada na malha, como antes.
  A soma é municipal, conforme o CSV solicitado, sem adicionar votos do exterior. O preparador falha se houver
  município faltante, duplicação no 2º turno, cobertura inesperada, contagem de trocas divergente ou soma inválida.
- **Bandeira:** geometria da Lei 5.700/1971 (módulo M; losango a 1,7M; círculo de raio 3,5M; faixa entre arcos de
  8M e 8,5M; dístico e 27 estrelas nas posições e grandezas do desenho oficial). Correspondência estrela → UF da
  Lei 8.421/1992; a cauda do Escorpião (CE, AL, SE, PB, RN, PE) foi casada com as posições por ajuste ao céu do Rio
  em 15/11/1889, respeitando as grandezas. Cores esmaecidas, sem texto nosso dentro da bandeira.
- **Desenhos:** gerados localmente pelo Codex CLI (`arte/gerar.ps1`), prompts `arte/prompt-capa-horizonte-1…4.txt`
  e `arte/prompt-capa-nuvens.txt`; limpos em Python (`capa/remotion/scripts/preparar_arte.py`: alfa pela tinta,
  creme `#E5DBC8`, emendas em degradê, mapa de ordem do desenho). Nenhum gerador pago na nuvem.
  Os desenhos originais ficam em `arte/candidatas/` (fora do git); os limpos que o vídeo usa estão em
  `capa/remotion/public/img/`.

## Para embutir

```html
<video autoplay muted playsinline preload="auto" poster="capa-2t-final.jpg">
  <source src="capa-2t.webm" type="video/webm">
  <source src="capa-2t.mp4" type="video/mp4">
</video>
```

Sem `loop`: o vídeo para no último quadro. Com `prefers-reduced-motion: reduce`, mostre só `capa-2t-final.jpg`
e o HTML deve mostrar diretamente os dados e o rótulo do 2º turno. Esses ajustes do HTML são da integração da main.
