# VizuFilter 2.12.2.0 · Eleições 2026 (23/10/2026)

A 2.12.1.0 do kit da casa com a fonte do painel: o `@font-face` embutido no CSS do visual passa a ser a Sora recortada
deste projeto (`pbi/assets/fontes/sora-eleicoes.woff2`, eixo wght 300–800, Latin-1 + pontuação tipográfica, SIL OFL
1.1), com a família **"Sora Vizu"**. A casca grava `style.fontFamily` = `Sora Vizu, Segoe UI`.

- `visual.js` e `capabilities.json`: iguais aos da 2.12.1.0, byte a byte.
- CSS: só a família, o intervalo de peso e o `src` da fonte mudaram.
- GUID igual (`smartFilterFixed9B35E14F08BD474496777B2253A30D3A`); versão 2.12.2.0 no `package.json` e no
  `pbiviz.json`.
- Pacote: `smartFilterFixed9B35E14F08BD474496777B2253A30D3A.2.12.2.0.pbiviz`, 1.086.950 bytes, SHA-256
  `5d1c83a7ba8cac232dac748fcb1ab228ae1ecd642c80a0420b414590cdd7dcf3` (registrado em `pbi/scripts/pbip_lib.py`).
