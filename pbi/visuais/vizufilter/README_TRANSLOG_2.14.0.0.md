# VizuFilter 2.14.0.0 · Eleições 2026 (24/10/2026)

É a 2.13.0.0 com uma coisa a mais: o **resumo do caminho no gatilho**.

O pedido é do dono. O filtro deixa de ser a pílula HTML com botão e passa a ser o próprio VizuFilter, em árvore
Região › Estado, com o filtro na folha.

Na 2.13, marcar o Nordeste marcava os 9 estados, e o gatilho mostrava só o rótulo ("Estado"). Uma medida DAX não
resolve, porque o visual não enxerga a própria seleção na consulta dele. Por isso o resumo sai do JS.

## Resumo do caminho (objeto `general`, seção "Texto do campo")

São três propriedades novas, todas opt-in.

- `triggerPathSummary` (bool, padrão desligado). Vale só no modo caminho, com o gatilho mostrando o valor
  (`triggerMode` diferente de "count"). O gatilho lê a seleção de cima para baixo:
  - um nó com todas as folhas marcadas vira uma parte, com o nome do nó, e a descida para ali;
  - um nó com parte das folhas marcadas: a leitura desce;
  - uma folha marcada solta vira uma parte, com o nome dela (o último segmento).

  Ligado, o resumo aparece mesmo com "Mostrar valor selecionado" desligado.
- `triggerPathSummaryMax` (número, padrão 2). Até esse número de partes em cada grupo, o resumo junta os nomes ("A",
  "A e B", "A, B e C"). Acima dele, mostra a contagem das folhas marcadas no grupo ("19 estados"). O valor fica entre
  0 e 50; com 0, sai sempre a contagem ("1 estado").
- `triggerPathSummaryNoun` (texto, padrão "item|itens"). É o "singular|plural" da contagem. Também aceita uma entrada
  por raiz, sem diferença de caixa nem acento, como no `exclusiveRoots`:
  `Região, estado e cidade=cidade|cidades; Renda (quinto)=faixa|faixas`. Uma entrada sem "=" vale para as raízes que
  não têm entrada própria.

**Grupos:**
- Com as categorias como cabeçalho (`treeCategoryHeader`), cada raiz é um grupo. O nome da raiz não entra no texto, e
  os grupos com seleção se juntam por " · ", na ordem da árvore ("Nordeste · até 10 mil hab.").
- Sem cabeçalho, há um grupo só, com todas as raízes.

**Exemplos:**

| Seleção | Gatilho |
|---|---|
| a árvore de estados com o Nordeste inteiro | "Nordeste" |
| Bahia | "Bahia" |
| MG + SP | "Minas Gerais e São Paulo" |
| Nordeste + MG | "Nordeste e Minas Gerais" |
| Norte + Nordeste | "Norte e Nordeste" |
| 5 estados soltos | "5 estados" |
| Norte + Nordeste + Sul | "19 estados" |
| as 27 | "27 estados" |
| na tela 20, a cidade inteira | "São Paulo (SP)" |
| na tela 20, uma escola | o nome dela |
| na tela 20, 3 escolas | "3 escolas" |

**Texto e acessibilidade:**
- O texto visível é o resumo. Com `selectedValueOnly` desligado, vem com o prefixo de sempre ("Estado : Nordeste").
- O `title` e o `aria-label` do gatilho levam o resumo.
- Contador, classe `active-filter` e ponto do funil ficam como estavam.
- O resumo só lê as marcas (`selectedKeys`) e a árvore inteira, não a recortada pela busca. Não grava nada.
- Marca fora da árvore é ignorada. Se nada for achado, fica o texto da 2.13.

**Painel:** as três fatias ficam em Geral › Texto do campo. Só aparecem no modo caminho com o gatilho em valor; o limite
e o nome só aparecem com o resumo ligado.

## Padrão da casa para o gatilho (24/10/2026)

O dono aprovou o ícone que muda ao filtrar: "pode manter isso como recurso do vizu filter". Todo VizuFilter de lista
da casa (estado, período, município, local, o recorte da tela 19 · Explorador) grava, no objeto `style`:

| Propriedade | Valor da casa |
|---|---|
| `triggerIcon` | `funnel` (o funil antes do texto) |
| `triggerIconActive` | `filledDot` (o ponto aparece quando há escolha) |
| `triggerIconDotColor` | o vermelho da casa (`estilo.COR["vermelho"]`) |
| `triggerIconColor` | o grafite da casa (`estilo.COR["grafite"]`) |

No painel Eleições, os tokens saem de `pbi/scripts/paginas/casca.py` › `_estilo_filtro`, que as telas 15, 19 e 20 também
usam. **O padrão de fábrica do visual não muda:** sem esses valores gravados, o gatilho fica como sempre foi. A casa é
quem liga o funil.

## O que não muda

- Desligado (o padrão), ou com o gatilho em Contagem de filtros, o visual desenha e grava o mesmo que a 2.13.0.0.
- Para provar isso há um controle negativo contra o `src/` da 2.13.0.0 (pasta irmã, só leitura,
  `tests/diferencial-2.14-resumo.test.cjs`). Ele compara a árvore DOM inteira (com `title` e `aria-label`), as chamadas
  ao host e o estado aberto ou fechado, passo a passo, em três casos:
  - a árvore de estados sem as propriedades novas;
  - a mesma árvore com o resumo desligado e o limite e o nome gravados;
  - a árvore cidade e escola da tela 20 em Contagem de filtros, com o resumo ligado.
- Há também um controle do controle: com o resumo ligado, a comparação acusa a diferença.
- O CSS é byte a byte o da 2.13.0.0.
- No `capabilities.json` só entram as três propriedades novas. Papéis, mapeamentos, privileges,
  `supportsKeyboardFocus` e `supportsSynchronizingFilterState` não mudam.
- O GUID é o mesmo (`smartFilterFixed9B35E14F08BD474496777B2253A30D3A`), e a API continua 5.3.0.

## Testes

Rodados na pasta de fonte `pbi/visuais_src/VizuFilter-2.14.0`, com o `node_modules` copiado da 2.13.

- `npm test`: **451 testes, 433 passam, 0 falha**, 15 pulados (falta a base antiga de outro projeto, como na 2.13) e 3
  a fazer. São os 422 da 2.13 e 29 novos:
  - 24 em `tests/resumo-caminho-2.14.test.cjs`: os exemplos acima, por filtro do host e pelo clique; limite 3 e 0;
    nome padrão; prefixo do campo; chaves fora da árvore; desligado; Contagem; árvore de três campos;
  - 5 no controle negativo.
- Os testes dos manifestos passam a esperar 2.14.0.0.
- `tsc --noEmit --skipLibCheck` e `eslint .`: verdes.
- `pbiviz package --certification-audit`: "No external requests found in the visual." Foi rodado à parte; o pacote
  final é o do `pbiviz package` simples.

## Pacote

`smartFilterFixed9B35E14F08BD474496777B2253A30D3A.2.14.0.0.pbiviz`:
- **1.096.240 bytes**;
- SHA-256 `5bbfc7d951189828f3741a592d94a02048e3c214e1081f2e9edc928d9d5d4600`;
- registrado em `pbi/scripts/pbip_lib.py › PACOTES["vizufilter"]`, ao lado da 2.13.0.0, que fica nesta pasta.

Dentro do pacote:
- `visual.js`: 180.272 caracteres, SHA-256 `2cf9d72936a7824e773f18429784d91c1647954753cab51366e92163095f054f`;
- CSS: 94.316 caracteres, SHA-256 `7ba1c02efe502dbb251529436d80a71e218302015a01e3f38d0866d28bac1f51`, igual ao da 2.13.

O fonte fica fora do repositório (`pbi/visuais_src/`).

## Só o Desktop prova

Nada disto foi conferido no Power BI Desktop.

- O texto do gatilho com a fonte real:
  - "Minas Gerais e São Paulo" e "Nordeste e Minas Gerais" cabem no campo ou saem com reticências;
  - o resumo depois do eco do host e na sincronia entre páginas (`Eleicoes_UF`).
- O leitor de tela lê o resumo no gatilho.
