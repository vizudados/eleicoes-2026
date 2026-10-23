# Eleições 2026 · o que os números dizem

Repositório: https://github.com/vizudados/eleicoes-2026 · Painel em Power BI no estilo apresentação (Vizu Dados), que conta o 1º turno presidencial de 2026 do placar ao porquê,
do país à escola, e acompanha a apuração do 2º turno ao vivo. Inspirado no documentário "Lula vs Flávio: o que os
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
| `pbi/m/` | Power Query das tabelas que vêm de fora (apuração) |

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

## Fontes

TSE (votação, comparecimento, perfil do eleitor, seções e locais de votação, API de divulgação), IBGE (Censo 2022 e
malhas), institutos de pesquisa com registro no TSE, emissoras e monitoramentos citados em cada `FONTES.md`. Fotos de
referência: Palácio do Planalto (CC BY 2.0) e Agência Senado, redesenhadas em traço.
