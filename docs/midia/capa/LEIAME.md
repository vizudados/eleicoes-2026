# Capa animada · Eleições 2026 · o voto de perto

**Conceito: o céu da bandeira vira o mapa do voto.** As 27 estrelas da bandeira, uma por UF, desenham a bandeira,
voam cada uma para o seu estado, o Brasil se desenha à volta delas, os 5.570 municípios acendem pela margem de 2026 e
um horizonte de Norte a Sul se desenha na base. Toca uma vez e para no último quadro.

| Arquivo | O que é |
|---|---|
| `capa.mp4` | H.264 High, yuv420p, BT.709, faststart · 1920 × 1080 · 30 fps · 18 s · ≈ 2,9 MB |
| `capa.webm` | VP9 (duas passadas, 2,6 Mb/s) · mesmas medidas · ≈ 4,4 MB |
| `capa-final.jpg` | último quadro (pôster e movimento reduzido), JPEG 85 |
| `capa-inicio.jpg` | quadro 0 (céu escuro com estrelas fracas), JPEG 85 |

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
| 9,3–12,8 s | Cada ponto esmaece do creme para a cor da margem de 2026: vermelho (Lula à frente), azul (Flávio à frente). |
| 11,0–15,7 s | O horizonte se desenha da esquerda para a direita: Amazônia, sertão, Pelourinho, Congresso, Pão de Açúcar, São Paulo, araucárias, pampa. Entram nuvens, uma garça, um bando e o brilho da água. |
| 15,7–18 s | Assenta. A partir de 16,6 s o quadro fica parado; o último quadro é a composição completa. |

Zonas livres para o HTML por cima, conferidas quadro a quadro: título (x 300–1620, y 110–300) sem nada;
números (x 140–560 e 1360–1780, y 380–760) só com estrelas fracas; cabeçalho (y 0–100), rodapé (y 1000–1080) e
setas (x 40–120 e 1800–1880, y 510–570) vazios. Mapa em x 688–1232, y 303–863; horizonte em x 140–1780, y 853–990.

## Como rerenderizar

Projeto Remotion em `capa/remotion/` (versões fixas no `package.json`; Node 24, Python 3 com numpy, pandas, scipy e
Pillow, ffmpeg no PATH).

```powershell
cd capa/remotion
npm ci
npm run dados       # opcional: refaz public/dados e public/img a partir das malhas, dos votos e dos desenhos
npm run estudio     # opcional: Remotion Studio para ver e ajustar
npm run render      # 540 quadros PNG em out/seq (≈ 25 s)
npm run codificar   # capa.mp4, capa.webm, capa-final.jpg e capa-inicio.jpg nesta pasta
```

O roteiro fica em `src/tempo.ts` (todos os tempos em segundos). O render é determinístico: tremor do traço,
ordem de revelação e acasos usam sementes fixas. O fundo `#1C1915` decodifica a ±1 nível em 8 bits (limite do
yuv420p); a casca do Power BI na mesma cor não mostra emenda.

## De onde vêm os dados e as imagens

- **Mapa:** malhas do IBGE (`dados/bruto/ibge/malha_uf.json` e `malha_municipios.json`), projeção lon·cos 15° × lat
  como em `pipeline/mapas.py`. Cada ponto é o centroide de um município; o raio cresce com a raiz dos votos válidos.
- **Cor:** margem de 2026 = (Lula − Flávio) ÷ válidos, de `dados/saida/votos_municipio.csv` (TSE), escala
  divergente da casa de −60 a +60 p.p., com as pontas um pouco mais claras para ler sobre a tinta.
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
<video autoplay muted playsinline preload="auto" poster="capa-final.jpg">
  <source src="capa.webm" type="video/webm">
  <source src="capa.mp4" type="video/mp4">
</video>
```

Sem `loop`: o vídeo para no último quadro. Com `prefers-reduced-motion: reduce`, mostre só `capa-final.jpg`.
