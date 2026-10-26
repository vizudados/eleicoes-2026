# Eleições 2026 · o voto de perto

Repositório: https://github.com/vizudados/eleicoes-2026 · Painel em Power BI no estilo apresentação (Vizu Dados), que conta os dois turnos presidenciais de 2026, do resultado ao porquê,
da zona eleitoral ao país, com roteiro e direção visual próprios. Mockup no Figma: arquivo `f6nFM7Go5USMK1tXc46uxP` ("Eleições 2026 · Mockup").

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

30 telas a 1920 × 1080 (00 Capa … 29 Encerramento, `pbi/scripts/roteiro.py`), em cinco atos, do antes para o depois:
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

## Registro da apuração do 2º turno (25/10/2026)

O coletor leu a API pública do TSE (`ele2026/6258`) para o Brasil, as 27 UFs e o exterior e gravou
`dados/apuracao/`. Na noite de 25/10, o workflow foi agendado a cada cinco minutos, com quatro coletas por execução,
uma por minuto, gravando uma nova linha no histórico a cada mudança da totalização do TSE. O modelo leu os CSV pelo
raw do GitHub; havia integração opcional de atualização pela API do Power BI.

A totalização final foi às 23h26: 100% das seções; Lula 64.256.232 votos (51,79% dos válidos), Flávio Bolsonaro
59.826.041 (48,21%); diferença de 4.430.191 votos e abstenção de 19,22%. A tela 25 conserva o resultado final e a
curva daquela noite. Os workflows **`apuracao`, `vigia` e `teste-chave` foram desligados em 26/10/2026**.

As telas 26 · De onde vieram (T27) e 27 · Onde Flávio perdeu (T28) usam o segundo turno por município, sem exterior.
A T27 fecha a identidade dos ganhos observados, sem repartir uma suposta transferência individual entre candidatos. A integração está descrita em
`pbi/INTEGRACAO-POS-ELEICAO.md`.

A 28 · História do PT (T29) percorre as dez eleições de 1989 a 2026: mapa por UF no turno decisivo, vencedor real
e vantagem sobre o segundo colocado. A série nacional separa os turnos e preserva as quedas; o recorde nominal de
2026 não é recorde percentual. Fontes e divergências de versões: `docs/video/segundo-turno/PT-HISTORICO-METODO.md`.

## Debate da Globo (2º turno, 23/10/2026)

A tela 22 · Debate Globo (T26) conserva os fatos e números do debate de 23/10/2026 em `dados/pbi/debate_globo.csv`: situação, presença, regras, buscas, audiência, transmissão na internet, redes e pesquisas. Ausência de publicação é identificada na tela; nada é estimado. O dicionário de campos e as fontes estão em `dados/bruto/debate/FONTES.md`.

## Fontes

TSE (votação, comparecimento, perfil do eleitor, seções e locais de votação, API de divulgação), IBGE (Censo 2022 e
malhas), institutos de pesquisa com registro no TSE, emissoras e monitoramentos citados em cada `FONTES.md`. Fotos de
referência: Palácio do Planalto (CC BY 2.0) e Agência Senado, redesenhadas em traço.
