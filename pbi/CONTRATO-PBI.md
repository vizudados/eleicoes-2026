# Contrato das telas · painel Eleições 2026 no Power BI

Quem constrói uma tela segue este contrato. A sessão principal (main) é dona da casca, do modelo comum, do estilo, da
integração no Desktop e do git. Cada agente é dono só das telas que recebeu.

## 1. O que o Alisson pediu (23/10/2026, valem para toda tela)

- Não poluir as páginas com gráficos: um protagonista por tela e no máximo dois ou três apoios. O detalhe vai para o
  tooltip (dossiê) e para o cartão "i" (leitura).
- Tomar decisões, implementar, revisar, consertar e melhorar sempre que puder. Ninguém vai responder perguntas.
- Boa visibilidade dos elementos, nada exagerado: corpo ≥ 15 px a 1920 (leitura a 61 %), eixo e rodapé 13 px, número
  protagonista 64–120 px.
- Bom roteiro e storytelling, linguagem humanizada e fácil: frases curtas de conversa, sem jargão ("p.p." só com o
  número ao lado; "margem" explicada uma vez). A manchete responde à pergunta da tela.
- Diagramas, ícones e fotos (os desenhos em traço) para explicar quando ajudam. Criatividade: nada de "mais do mesmo".
- Números sempre com contador (automático, ver §5), mapas desenhados com rabisco, cores surgindo por esmaecer, e outros
  efeitos que a tela pedir.
- Neutralidade: Lula (vermelho, PT, 13) e Flávio (azul, PL, 22) com o mesmo tratamento, as mesmas contas e o mesmo peso.

## 2. Arquivos: de quem é o quê

| Caminho | Dono | Regra |
|---|---|---|
| `pbi/scripts/paginas/tNN_<nome>.py` | dono da tela | declara os visuais, tooltips, marcadores e interações da tela |
| `pbi/dax/TNN <Nome>/**/*.dax` | dono da tela | uma medida por arquivo; todo nome começa por `TNN · ` |
| `pbi/scripts/leituras/TNN.json` | dono da tela | texto do cartão "i" (§7) |
| `pbi/scripts/desenho_tNN.py` (opcional) | dono da tela | gerador Python de medidas de desenho longas (grava em `pbi/dax/TNN …`) |
| `pbi/modelo/tNN_<algo>.py` (opcional) | dono da tela | tabela nova (parâmetro what-if, tabela auxiliar) — avise a main |
| `pipeline/exportar_tNN.py` (opcional) | dono da tela | CSV novo em `dados/pbi/tNN_*.csv` — avise a main (precisa de push) |
| casca, estilo, roteiro, pbip_lib, pagina_lib, gerar_modelo, montar_pbip, modelo/base\|campanha\|apuracao, `_Estilo`, `_Casca` | main | não edite; peça por mensagem |

Proibido: commit, push, abrir/fechar o Power BI Desktop, rodar `gerar_modelo.py` ou `montar_pbip.py --aplicar` (a main
integra), editar arquivo de outra tela. Toda geração de imagem é LOCAL pelo Codex CLI (`arte/gerar.ps1`); Magnific,
Firefly ou gerador pago na nuvem: proibido.

## 3. A página

- 1920 × 1080, fundo papel `#F1EBDF` (capa e encerramento: tinta `#1C1915`).
- A casca (`paginas/casca.py`) já desenha: urna em traço (40–132, 40–132), "NN · NOME" e a pergunta (x 150, y 46–115,
  até x 1260), o "i" (1724–1768, 62–106), as setas (36–116 e 1804–1884, y 500–580), o lockup Vizu e a linha de fonte no
  rodapé (y 1014–1042) e, nas telas com filtro de UF, o VizuFilter (1282–1706, 60–108). A fonte do rodapé vem de
  `roteiro.py` (peça à main para mudar).
- **Área de conteúdo: x 150–1770, y 140–1000.** Margem é respiro, não faixa vazia: use a área inteira.
- Camadas z: conteúdo 300+ (lib.CAMADAS["conteudo"]), ações 1020, leitura 4000, filtro 5000, navegação 5500.
- Nomes de visual: `TNN_<Bloco>_<Papel>` (regex em pbip_lib.RE_NOME_VISUAL), ex. `T03_Mapa_Pontos`.

## 4. Como declarar (pbi/scripts/paginas/tNN_nome.py)

```python
import pbip_lib as lib
from pbip_lib import Visual, Interacao
import pagina_lib

P = "T03"
CSS = "Estilo · CSS"

def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T03_Resposta_Html", 150, 140, 760, 420, "T03 · Resposta · HTML",
                                  folha_de_estilo=CSS, alt=lib.medida("T03 · Resposta · ALT"), tab=100)),
        Visual(P, lib.visual_deneb("T03_Mapa_Pontos", 960, 140, 810, 840, "spec/t03_mapa.json",
                                   [lib.campo_coluna("cod", "Município", "CodIBGE"),
                                    lib.campo_coluna("x", "Município", "X"), lib.campo_coluna("y", "Município", "Y"),
                                    lib.campo_medida("margem", "T03 · margem do município")],
                                   alt="Mapa de pontos: um por município", selecao=True,
                                   tooltip_pagina="ttT03Municipio", tab=200)),
        *pagina_lib.tooltip("ttT03Municipio", "Município · dossiê", 420, 300, "T03 · Tooltip município · HTML",
                            ordem=303, folha_de_estilo=CSS),
    ]
```

- `lib.visual_html(nome, x, y, w, h, medida, alt=..., folha_de_estilo=CSS, granularidade=(tabela, coluna),
  filtro_cruzado=True, tooltip_pagina="ttTNN…", tooltips=[medidas], modelo_corpo="…{{content}}…", movimento=None)`:
  HTML Content Standalone 2.0. Sem granularidade = um texto só. Com granularidade = uma entrada por linha (filtro
  cruzado e tooltip de página exigem granularidade). `modelo_corpo` = bodyTemplate: texto fixo grande (SVG de mapa,
  imagens base64, CSS próprio da tela) fica AQUI, nunca na medida.
- `lib.visual_deneb(nome, x, y, w, h, spec, campos, alt=..., selecao=False, tooltip_pagina=None)`: Deneb Standalone,
  **Vega 6 puro** (nunca Vega-Lite), dados no `data` chamado `dataset`, nada de `url` em data. Seleção cruzada com
  `pbiCrossFilterApply`/`pbiCrossFilterClear`; o datum mantém `__row__`. Animação por sinal `timer` que para (L123).
  Specs em `pbi/spec/tNN_*.json`.
- `lib.visual_botao(...)` (botão transparente: marcador, página), `lib.segmentacao(...)`, `lib.visual_vizufilter(...)`.
- `pagina_lib.tooltip(nome, titulo, largura, altura, medida_html, ordem=…, folha_de_estilo=CSS)`: página de tooltip
  com um HTML do tamanho dela; cria `TT_<nome>_Conteudo` e lê o ALT de `<medida_html sem "· HTML"> · ALT`.
- `Interacao(pagina, origem, alvo, "NoFilter"|"DataFilter"|"HighlightFilter")`: só as exceções.
- Ordem das páginas de tooltip: `ordem=` 100 + número da tela × 10 + i (ex. T03 → 130…139).

## 5. Contas, desenho e movimento

- **Conta × desenho (L051)**: todo número que o leitor vê sai de uma medida de conta (`TNN · …`, pasta
  `TNN Nome\Contas`); a medida de desenho (`TNN · … · HTML`, pasta `TNN Nome\Desenho`) só lê contas, escolhe texto,
  formata e posiciona. Para cada `· HTML` há um `· ALT` (texto puro, ≤ 250 caracteres, para leitor de tela).
- Formato `.dax`: cabeçalho `/* @pasta: … @formato: … (ou texto) @descricao: … */` + expressão; espaços, nunca tab.
- Texto de medida ≤ 32.000 caracteres (L048). Fontes, CSS da tela, SVG fixo e imagens: no `modelo_corpo`.
- Número em CSS/SVG/atributo: `FORMAT ( x, "0.0##", "en-US" )` (ponto decimal, L106). Número para o leitor: pt-BR
  (`FORMAT ( x, "#,0" )` com o modelo em pt-BR dá `56.104.503`; `FORMAT ( x / 1e6, "0.00" ) & " mi"` → `56,10 mi`).
- Concordância (L125): `IF ( n = 1, "município", "municípios" )`.
- Escape de texto vindo do dado dentro de HTML: `SUBSTITUTE` de `&`, `<`, `>`, `"` e `'`.
- HTML: raiz `<div class='tela'>` (position fixed, inset 0, camada própria; L037: nunca height:100%). Classes do
  `Estilo · CSS` (pbi/scripts/estilo.py): `.sob .tit .man .txt .rot .nota .num .mao .tnum .lula .flavio .lula-esc
  .flavio-esc .escuro`, cores como variáveis `--papel --creme --areia --tinta --grafite --cinza --vermelho
  --vermelho-escuro --rosa --azul --azul-escuro --azul-claro --marrom --branco`, fontes `var(--fonte)` (Sora) e
  `var(--mao)` (Caveat, só notas à mão ≥ 24 px, ≤ 6 palavras).
- **Movimento** (estado parado = desenho final; tudo some com prefers-reduced-motion):
  - contador: todo número de 20 px ou mais conta do zero na entrada e do valor anterior a cada filtro (movimento.js,
    automático; nada a fazer). Ano, data e ordinal não contam.
  - `.sobe` (sobe 14 px e aparece), `.entra` (aparece), atrasos `.d1` … `.d16` (80 ms cada);
  - `.barra-x` / `.barra-x-dir` / `.barra-y`: barra cresce do zero (desliza entre filtros);
  - traço que se desenha: `<path pathLength='1' class='traco' …>` (ou `.traco-rapido`), com o tremido de caneta
    `filter='url(#rb)'` e `estilo.defs_rabisco()` dentro do `<svg>`; `estilo.rabisco_circulo(w, h)` = laço à mão em
    volta de um número;
  - `.cor` / `.cor-esc`: o preenchimento esmaece do creme (ou da tinta) até a cor final; `.esmaece` (opacidade);
    `.brota` (escala do ponto).
  - Mapas: contorno se desenha (traço), depois a cor esmaece por região ou por onda (atrasos), depois os rótulos sobem.

## 6. Dados (modelo em pbi/modelo/*.py; CSV em dados/pbi)

- `UF` (UF, Nome, Região, Tipo UF/Exterior, Grade…) · `Município` (CodIBGE, Município, Rótulo, UF, População, Renda per
  capita, Porte, Quinto de renda, Longitude, Latitude, X, Y no quadro 1000×1000 dos mapas) · `Município ano`
  (VotosPT, VotosAdversario, VotosDemais, Validos, Aptos, Comparecimento, Abstencoes, Brancos, Nulos; 2006–2026,
  sem o exterior) · `Ano` (2006–2026, Candidato do PT, Adversário) · `Candidato ano` (resultado nacional oficial, com
  exterior) · `Candidato UF` (2022 e 2026 por UF, com ZZ) · `Comparecimento ano` · `Abstenção perfil` · `Pesquisa` ·
  `Debate` · `Trends tempo` · `Trends UF` · `Seguidores` · `Monitoramento` · `Anúncios` · `Trajetória` · `Transferência`
  · `Rejeição` · `Apoio` · `Local Contagem` · `Apuração …`.
- Relações: Município→UF; Município ano→Município e →Ano; Candidato ano→Ano; Candidato UF→UF e →Ano; Trends UF→UF;
  Apuração UF→UF. O filtro de UF da casca filtra `UF[Nome]` (com Tipo = UF).
- Em 2026, "adversário" = Flávio Bolsonaro; em 2022 = Jair Bolsonaro (PL). Margem do PT = (VotosPT − VotosAdversario)
  ÷ Validos.
- **Oráculo**: `mockup/data/eleicoes.json` (números da tela no mockup, calculados pelo pipeline em Python). As contas
  da tela têm de reproduzir esses números sem filtro; confira e anote.
- Geometria: `pbi/assets/mapas/uf_caminhos.json` (contorno de cada UF simplificado no quadro 1000×1000; o mesmo
  quadro de `Município[X]/[Y]`). Para pontos de município, Deneb com X/Y (5.571 linhas é ok em canvas).
- Imagens (traço): `docs/midia/catalogo.json` lista o que está no GitHub Pages
  (`https://vizudados.github.io/eleicoes-2026/midia/arte/…`, `…/mapas/…`): cenas das regiões, retratos, urna, debate,
  ícones (16), kit dossiê (ficha, fita, clipe, alfinete, carimbos, orelha, asterisco), rabiscos. Comícios sobre fotos
  reais e fotos históricas redesenhadas chegam em `…/midia/comicio/` e `…/midia/trajetoria/` (outro agente está
  gerando; créditos em `dados/bruto/trajetoria/desenhos.csv`). Imagem pequena e fixa pode ir em base64 no
  `modelo_corpo` (`estilo.imagem_b64(caminho, largura)`); imagem por linha de dado vai por URL.

## 7. Leitura (o "i") e tooltips

- `pbi/scripts/leituras/TNN.json`: `{"titulo": "…", "blocos": [["Como ler", "…"], ["De onde vêm os números", "…"],
  ["Para lembrar", "…"]]}` — cada bloco ≤ 3 frases.
- Tooltips "dossiê" (componentes do Figma na página Interações): papel com fita, clipe ou alfinete, ícone em traço no
  canto, nota em Caveat com o achado. Mergulham numa camada nova (composição, tempo, comparação), nunca repetem o
  número que já está na tela.

## 8. Provar

- Prévia fora do Power BI (o Desktop fica aberto pela main; a prévia avalia as medidas EM DISCO no motor dele):
  `python -X utf8 pbi/scripts/previa.py T03` → `pbi/qa/previa/T03.png`; com filtro:
  `--filtro "UF[Nome]=Minas Gerais"`; tooltip: `previa.py ttT03Municipio --tooltip "Município[Rótulo]=Contagem (MG)"`;
  `--animado` para ver em movimento. **Olhe cada PNG** (a 1920 e reduzida a 61 %).
- `python -X utf8 pbi/scripts/smoke_medidas.py "T03 ·"`: avalia toda medida `· HTML` sem filtro, com Minas Gerais,
  Roraima e Contagem; reprova erro e texto > 32.760.
- Consulta avulsa: `python -X utf8 pbi/scripts/dax.py --consulta "EVALUATE …"`.
- Se a prévia falhar porque o Desktop está fechado (a main está integrando), espere 2–3 minutos e tente de novo.
- Tabela ou coluna nova só existe no motor depois da integração: peça à main.

## 9. Entrega

Mensagem final à main com: telas prontas, arquivos criados, números conferidos contra o oráculo (e onde diferem, por
quê), o que precisa de integração (tabela, CSV, parâmetro), interações a testar no Desktop e pendências.
