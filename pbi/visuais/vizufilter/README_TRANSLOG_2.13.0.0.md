# VizuFilter 2.13.0.0 · Eleições 2026 (23/10/2026)

A 2.12.1.0 do kit da casa com o **modo régua** (pedido do dono na tela 24 · Simulador: "não está arrastando … uma
versão do vizufilter com esse recurso") e a mesma fonte da 2.12.2.0: o `@font-face` embutido é a Sora recortada deste
projeto (`pbi/assets/fontes/sora-eleicoes.woff2`, eixo wght 300–800, SIL OFL 1.1), família **"Sora Vizu"**.

## Modo régua (cartão "Régua", objeto `regua`)

O Campo do filtro (uma coluna numérica) vira um trilho com um botão arrastável. Os valores distintos ficam em ordem
crescente, cada um no x proporcional ao número; o botão encaixa no valor mais próximo.

- **Arraste** com pointer events: pointerdown no botão ou no trilho → captura do ponteiro → o botão anda ao vivo →
  pointerup aplica. Pegar o botão fora do centro não o faz pular; **clique no trilho** pula para o valor.
- **Teclado** no botão (`role="slider"`, `aria-valuemin/max/now/valuetext`, nome acessível): ←/↓ e →/↑ um valor,
  PageUp/PageDown cinco, Home/End as pontas. Tecla segurada anda e grava uma vez, no keyup.
- **Filtro**: básico de seleção única (`In [valor]`) pelo mesmo `applyJsonFilter` em `general.filter` (merge) da
  lista, uma gravação ao soltar ou por tecla, nunca a cada pixel do arraste. A posição sai do filtro que o host devolve;
  sem filtro, o botão fica no **Valor padrão**. O valor recém-aplicado vence um eco atrasado do host por até 2,5 s.
  A régua não grava `persistedSelection` (a fonte da verdade é o filtro: marcadores e "Redefinir" valem).
- Opções: Modo régua (`ativo`, padrão desligado), Valor padrão, Nome para o leitor de tela; Trilho visível, espessura e
  cor, Trecho preenchido (do início · do valor padrão · sem trecho) e cor, Margem lateral; Diâmetro, borda, miolo e cor
  da borda do botão, Valor sobre o botão no arraste; Marcas (nenhuma · em cada valor · no valor padrão), cor e altura;
  Rótulos de mínimo e máximo, cor e tamanho, Sufixo (ex.: `%`) e Sinal + nos positivos (o negativo leva `−`).
- Desenho da casa: traço fino, sem sombra, gradiente nem brilho; anel de foco e valor sobre o botão só pelo teclado (ou
  durante o arraste); `prefers-reduced-motion` sem transição. Página escalada por transform: o encaixe converte o
  ponteiro para px de layout.

## O que não muda

- Com `regua.ativo` desligado (o padrão) o visual desenha e grava o mesmo que a 2.12.1.0: controle negativo com o código
  da 2.12.1.0 (DOM inteiro, chamadas ao host e estado, passo a passo, em lista, árvore, busca e numa coluna numérica),
  também com o cartão Régua inteiro gravado e desligado.
- CSS: o da 2.12.1.0 com a troca da fonte (como na 2.12.2.0) e um bloco novo, todo debaixo de `.sff-modo-regua`.
- GUID igual (`smartFilterFixed9B35E14F08BD474496777B2253A30D3A`); versão 2.13.0.0 no `package.json` e no
  `pbiviz.json`. Testes: `npm test` (422 testes, 404 passam, 15 pulados por falta de uma base antiga, 3 a fazer) e
  `npm run lint` verdes.

## Pacote

`smartFilterFixed9B35E14F08BD474496777B2253A30D3A.2.13.0.0.pbiviz`, 1.094.613 bytes, SHA-256
`bde3a8800b76b57474ee732a61a128cfb5db1c8c504db30ff1c8a8323949d9eb` (registrado em `pbi/scripts/pbip_lib.py`, que
substitui o 2.12.2.0 na pasta `CustomVisuals/` do relatório). O fonte fica fora do repositório (`pbi/visuais_src/`).
