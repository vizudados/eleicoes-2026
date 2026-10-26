# Integração pós-eleição · rodada 2 · 26/10/2026

Este é o handoff vigente. Substitui as instruções da rodada 1 sobre regressão e sobre três CSV.
A main já integrou a rodada anterior e aprovou T18, T17 e T23 no motor, com smoke sem erro. As fotos reais enviadas
pela main são a evidência dessas aprovações. Esta rodada altera somente fontes em disco; Desktop, PBIP, refresh,
commit e publicação continuam com a main.

## O que mudou

- **T27/T28:** corrigido o erro do gerador que emitia `RETURN` sem `VAR`. O fluxo agora declara `VAR _html = …`
  e termina em `RETURN _html`. O comentário de geometria passou para linha própria.
- **T27:** saiu toda a decomposição por regressão. Permanecem os dois fluxos com votos observados e a identidade
  dos ganhos da dupla. A tabela `T27 Estimativa`, sua relação e as seis medidas `T27 · estimativa …` foram retiradas
  das declarações/fontes DAX. Não há mais consumo de `t27_fluxo.csv` pelo modelo, medidas ou validador.
- **T23:** ganhos nacionais agora dizem “entre os turnos”; a retomada diz “Lula voltou à frente às 20h24”; o último
  achado lê a contagem de viradas e as UFs, em vez de convidar a “ver”. Saiu o rodapé “estimativa agregada”.
- **T18:** horas dos desenhos em `19h45`/`20h24`; nota em Caveat “divulgação parada até as 19h”, no trecho da
  suspensão. A leitura cita TSE e Agência Senado, conforme `docs/video/segundo-turno/CONFERIDO-MAIN.md`.
- **T00:** mesmos blocos e posições, Flávio à esquerda e Lula à direita. Números grandes e porcentagens são do
  segundo turno; a linha menor mostra o primeiro. Lula recebe o selo discreto “eleito”. A nota inferior lê as
  viradas entre turnos, 211 em um sentido e 1 no outro; o total de municípios foi mantido.

T17 não foi alterada nesta rodada. A ordem permanece T18 → T27 → T28 → T23 (posições 25–28).

## Modelo mudou: precisa do ciclo completo

Sim: é necessário regenerar o modelo e reabrir/atualizar o Desktop pela main para remover a tabela de regressão.
Não basta aplicar só páginas ou só medidas. O gerador de modelo já remove os arquivos que sobraram; no ciclo, ele
deve retirar `tables/T27 Estimativa.tmdl`, a referência no modelo e a relação correspondente.

Permanecem apenas as duas tabelas declaradas em `pbi/modelo/segundo_turno.py`:

- `Município segundo turno` → Município e Ano; a UF chega por Município → UF;
- `UF segundo turno` → UF e Ano.

**Não há CSV novo.** Os dois CSV observados já publicados permanecem. Como combinado, a main remove do git
`dados/pbi/t27_fluxo.csv` e `pipeline/exportar_t27.py`; esses dois arquivos não foram apagados por este agente.

As fontes DAX já estão geradas. Para reproduzir, ainda sem alterar PBIP ou motor:

```powershell
python -X utf8 pbi/scripts/desenho_t27_t28.py
python -X utf8 pbi/scripts/desenho_t00.py
python -X utf8 pbi/scripts/validar_dax_gerado.py --autoteste
python -X utf8 pbi/scripts/validar_pos_eleicao.py
```

Depois, a main executa seu ciclo habitual com o Desktop fechado: `gerar_modelo.py`, `montar_pbip.py --aplicar`,
reabertura e refresh. Nenhum desses passos foi executado pelo agente nesta rodada.

## T27: conta observada, sem exterior

Os valores de controle, refeitos a partir das duas fatos municipais, são:

| Parcela | Votos |
|---|---:|
| Demais candidatos no primeiro turno | 9.287.152 |
| Variação do comparecimento | +2.920.562 |
| Redução de brancos e nulos | +1.820.154 |
| Soma das parcelas / ganho conjunto | **14.027.868** |
| Ganho de Lula | +10.333.927 |
| Ganho de Flávio | +3.693.941 |

As parcelas fecham exatamente por município e, portanto, em qualquer soma de municípios. A medida
`T27 · identidade · resíduo` é controle de QA e deve retornar zero; não vira KPI na tela.

Lula respondeu por **73,6671246122%** do aumento municipal conjunto: a manchete mostra **7,4 de cada 10** e o apoio,
**73,67%** contra **26,33%**. A distribuição só aparece quando ambos os saldos são não negativos e a soma é positiva.
Em recortes como AC/RR, onde Flávio perdeu votos, a manchete passa ao saldo observado e a identidade preserva os sinais.
O aviso visual aparece uma vez: “a urna não mostra quem trocou de candidato”. Nenhuma parcela é repartida entre
candidatos por regressão, e não há “restante” modelado.

A contagem de UFs no gerador também foi corrigida: guarda a UF iterada e a reaplica depois de limpar Município.
Isso evita que a remoção dos filtros da [tabela expandida](https://www.sqlbi.com/articles/differences-between-all-and-allcrossfiltered/)
apague a UF da iteração. Conferir no motor: uma única UF mudou de vencedor, Minas Gerais, e 211 municípios
passaram de Flávio para Lula (1 no sentido contrário).

## Capa e vídeo

O HTML aponta para:

- `midia/capa/capa-2t.mp4` e `capa-2t.webm`;
- `midia/capa/capa-2t-inicio.jpg` e `capa-2t-final.jpg`.

Os quatro arquivos já existem localmente em `docs/midia/capa/`; render e publicação no GitHub Pages são da main
e do agente do vídeo. Publicar antes do QA visual do vídeo pela URL de produção.

O LEIAME novo foi lido. Em `paginas/t00_capa.py`, as constantes `ROTULO_INICIO_S` e `ROTULO_SEGUNDO_S` viram
variáveis CSS: primeiro rótulo no quadro 280 / 30 fps (**9,333333333 s**) e troca no quadro 396 (**13,2 s**), quando
começa a segunda onda. Se o roteiro mudar, trocar essas duas constantes conforme `docs/midia/capa/LEIAME.md`.
Os rótulos fazem uma transição curta; o relógio CSS começa junto com `onplaying` e pausa em `onwaiting`/`onpause`.
Com movimento reduzido ou falha do vídeo, ficam somente pôster final e rótulo do segundo turno.

O rótulo fica sob o mapa, em y 866, com sombra de tinta e sem uma faixa opaca cobrindo a ilustração. Conferir a
legibilidade sobre o horizonte no render real. Os blocos continuam em x 140 / 1360 e y 430; as notas, em y 706.

Controles nacionais da capa, com exterior: Flávio **59.826.041 / 48,21%**, Lula **64.256.232 / 51,79%**; primeiro
turno menor **56.104.503** e **53.879.538**, respectivamente. A fonte da casca foi atualizada para os dois turnos.

## Validações desta rodada e próximas provas da main

- `validar_dax_gerado.py` varre toda a árvore DAX para detectar RETURN sem VAR no escopo e delimitadores/literais
  abertos; tem dez casos de autoteste, incluindo a falha recebida. Os geradores T00 e T27/T28 também o chamam
  antes de gravar e rejeitam comentários no fim de uma linha de código. **É checagem estrutural, não parser DAX.**
- `validar_pos_eleicao.py` verifica as 5.571 identidades municipais, a soma nacional, chaves, nomes e referências
  futuras, ausência da tabela/medidas de regressão, specs e caminhos do plano. Relatório em
  `pbi/qa/previa/validacao-pos-eleicao.json`. Não consulta o Desktop.
- Python/JSON, lint conta × desenho e idempotência da emissão são checagens locais. Não substituirão as provas
  reais no motor. As fotos aprovadas da rodada anterior não foram sobrescritas por prévias de simulação.

Resultado local desta entrega: **1.854 medidas varridas**, dez casos do guard passaram, **129 arquivos** tiveram
emissão idempotente, **5.571 identidades municipais** e **38 agrupamentos** (UF, região e porte) fecharam sem erro.
O lint de T00/T23/T27/T28 teve zero erro; permanece com avisos de estilo/linhas longas, sem aprovação sintática do motor.
O relatório adicional está em `pbi/qa/rodada2/provas-locais.json`.

Depois do ciclo, executar prévias e smoke de **T27, T28, T00, T18 e T23**; T17 serve como regressão da página já
aprovada. Para T27/T28: Brasil, MG e RR/AC; verificar soma, troca da manchete quando um candidato perde votos,
mapa ↔ lista, tooltip, “i” e contadores. Confirmar `T27 · identidade · resíduo = 0` nos recortes.

Conferir T23 no motor: **211 municípios**, **1 UF** e **Minas** no último achado, além das horas com “h”. Na T18,
conferir nota sem colisão com curva/eixos. Na capa, conferir números finais, linha do primeiro turno, selo,
notas, movimento reduzido/fallback e a troca do rótulo aos 13,2 s com os quatro assets novos publicados.

Todas as novas capturas, smoke e testes por gesto continuam com a main, como combinado. O sandbox não autentica
no motor; nesta rodada o agente não repetiu tentativas de conexão, não integrou e não abriu o Desktop.
