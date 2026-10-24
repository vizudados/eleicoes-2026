# Eleições 2026 · o voto de perto

Repositório: https://github.com/vizudados/eleicoes-2026 · Painel em Power BI no estilo apresentação (Vizu Dados), que conta o 1º turno presidencial de 2026 do resultado ao porquê,
da zona eleitoral ao país, e acompanha a apuração do 2º turno ao vivo. Inspirado no documentário "Lula vs Flávio: o que os
números dizem" (Spotniks). Mockup no Figma: arquivo `f6nFM7Go5USMK1tXc46uxP` ("Eleições 2026 · Mockup").

## Pastas

| Pasta | O que é |
|---|---|
| `docs/` | roteiro (`perguntas.md`, uma tela por pergunta) e brief visual |
| `pipeline/` | extração (TSE, IBGE, seções), consolidação, mapas, artes e o montador do JSON do mockup |
| `apuracao/` | coletor da apuração ao vivo (API pública do TSE) e o gatilho de atualização do Power BI |
| `.github/workflows/apuracao.yml` | o agendamento da coleta na noite do 2º turno |
| `dados/bruto/` | levantamentos com fonte por registro (pesquisas, debate, digital, trajetória, transferência); TSE e IBGE ficam fora do repositório e se regeram |
| `dados/saida/` | tabelas consolidadas (município × ano, comparecimento, perfil, locais de Contagem) |
| `dados/apuracao/` | o que o coletor grava: `ultimo.json`, `ufs.csv`, `historico.csv` (e `ensaio-1turno/`) |
| `mockup/data/eleicoes.json` | tudo o que as telas mostram, já calculado e formatado |
| `arte/` | desenhos em traço (Codex local), mapas de dado e créditos das fotos (`arte/ref/fotos/CREDITOS.md`) |
| `dados/pbi/` | as tabelas que o Power BI lê pelo GitHub (`pipeline/exportar_pbi.py`) |
| `pbi/` | o projeto Power BI (PBIP gerado por script, ver abaixo) |
| `capa/remotion/` | a capa animada em Remotion; o vídeo sai em `docs/midia/capa/` |
| `docs/midia/` | imagens e vídeo que o painel carrega pelo GitHub Pages (`https://vizudados.github.io/eleicoes-2026/midia/`) |

## Regerar tudo

```bash
python -I pipeline/extrair_tse.py
```

```bash
python -I pipeline/extrair_tse.py --base detalhe
```

```bash
python -I pipeline/extrair_ibge.py
```

```bash
python -I -X utf8 pipeline/consolidar.py
```

```bash
python -I -X utf8 pipeline/mapas.py
```

```bash
python -I -X utf8 pipeline/montar_dados_mockup.py
```

Tela Zona eleitoral (34 cidades: as 27 capitais, as 6 maiores que viraram e Contagem): votos por seção e cadastro de locais
do TSE numa passada por ano (cache em `dados/bruto/tse`), depois `dados/pbi/t20_locais.csv` e `dados/pbi/t20_cidades.csv`
com a prova dos totais por cidade contra o TSE:

```bash
python -I -X utf8 pipeline/extrair_secoes.py --t20
```

```bash
python -I -X utf8 pipeline/exportar_t20.py
```

## O painel no Power BI (`pbi/`)

27 telas a 1920 × 1080 (00 Capa … 26 Encerramento, `pbi/scripts/roteiro.py`), em cinco atos, do antes para o depois:
I · Antes da urna, II · O 1º turno, III · O mapa, IV · Explore você mesmo e V · O 2º turno, logo antes do
encerramento. A 12 · Quem vota cruza o
voto com renda, escolaridade, Bolsa Família e IDH (`pipeline/extrair_social.py`); a 21 · Debate Band e a 22 · Debate
Globo ficam coladas, e a da Globo acompanha o último debate do 2º turno pelo arquivo `dados/pbi/debate_globo.csv`
(abaixo). Abra
`pbi/pbip/Eleicoes.pbip` no Power BI Desktop; o modelo lê os CSV de `dados/pbi` e de `dados/apuracao` pelo endereço raw
deste repositório (parâmetro `pRepositorioRaw`), então funciona em qualquer máquina e no Service sem gateway.

O PBIP é **gerado por script**; não edite à mão (o Desktop sobrescreve o que o gerador escreveu quando salva):

| Peça | Onde |
|---|---|
| tabelas, parâmetros e relações | `pbi/modelo/*.py` → `pbi/scripts/gerar_modelo.py` |
| medidas (uma por arquivo, contas × desenho) | `pbi/dax/**/*.dax` |
| páginas, visuais, tooltips, marcadores | `pbi/scripts/paginas/*.py` → `pbi/scripts/montar_pbip.py` |
| estilo (Sora e Caveat embutidas, cores, movimento) | `pbi/scripts/estilo.py`, `pbi/scripts/movimento.js` |
| casca (cabeçalho, rodapé, setas, leitura "i", filtro de UF) | `pbi/scripts/paginas/casca.py` |
| visuais próprios (HTML Content e Deneb Standalone, VizuFilter) | `pbi/visuais/` |
| contrato das telas | `pbi/CONTRATO-PBI.md` |

Ciclo (com o Desktop deste projeto fechado):

```bash
python -I -X utf8 pbi/scripts/estilo.py
```

```bash
python -I -X utf8 pbi/scripts/gerar_modelo.py
```

```bash
python -X utf8 pbi/scripts/montar_pbip.py --aplicar
```

```bash
pwsh -NoProfile -File pbi/scripts/desktop.ps1 -Acao abrir
```

Provas: `pbi/scripts/previa.py <TELA>` (foto fora do Power BI), `pbi/scripts/cdp.py roteiro <arquivo>` (gesto dentro
do Desktop aberto com `-Cdp 9347`), `pbi/scripts/conferir_apuracao.py` (apuração contra o TSE),
`pbi/scripts/smoke_medidas.py` e `pbi/scripts/desempenho.py` (tempo de cada consulta e peso de cada página).

## Apuração ao vivo (2º turno, 25/10/2026)

1. O coletor lê `resultados.tse.jus.br/oficial/ele2026/6258/dados/<uf>/<uf>-c0001-e006258-u.json` para o Brasil e as
   27 UFs (mais o exterior) e grava `dados/apuracao/`. O código 6258 é o 2º turno da eleição federal (o 1º turno, 6257,
   serve de ensaio com o resultado final).
2. O workflow roda a cada 5 minutos das 16h às 23h55 de Brasília em 25/10, com 4 coletas por execução (uma por
   minuto), e faz commit só quando o TSE muda a hora de totalização.
3. O Power BI lê os CSV pelo endereço raw do GitHub (`pbi/m/Apuracao.m`, parâmetro `pRepositorioRaw`).
4. Para a tela andar sozinha: com os segredos `PBI_TENANT_ID`, `PBI_CLIENT_ID`, `PBI_CLIENT_SECRET`,
   `PBI_WORKSPACE_ID` e `PBI_DATASET_ID` no repositório, cada coleta pede a atualização do modelo pela API. Em
   workspace Pro há teto de 8 atualizações por dia; para a noite da eleição, use PPU, Premium ou Fabric.

Teste local:

```bash
python -I apuracao/coletar.py --eleicao 6257 --saida dados/apuracao/ensaio-1turno
```

## Debate da Globo (2º turno, 23/10/2026)

A tela 22 · Debate Globo (código T26) ficou pronta antes do debate e se preenche quando
`dados/pbi/debate_globo.csv` muda no repositório: uma linha por fato ou número (situação do debate, presença de cada
candidato, regras e os cinco números da noite: buscas, audiência, transmissão na internet, redes e pesquisas). Campo
vazio aparece como "aguardando", com a hora e a fonte esperadas; nada é estimado. O que é cada campo, de onde vem e
como atualizar está em `dados/bruto/debate/FONTES.md` (seção "Debate da Globo, 23/10/2026").

## Fontes

TSE (votação, comparecimento, perfil do eleitor, seções e locais de votação, API de divulgação), IBGE (Censo 2022 e
malhas), institutos de pesquisa com registro no TSE, emissoras e monitoramentos citados em cada `FONTES.md`. Fotos de
referência: Palácio do Planalto (CC BY 2.0) e Agência Senado, redesenhadas em traço.
