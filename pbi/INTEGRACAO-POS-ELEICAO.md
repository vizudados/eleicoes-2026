# Integração pós-eleição · rodada 4 · acabamento

Handoff vigente, sobre a rodada 3 integrada pela main (`283a14d`, smoke sem erro e prévias reais informadas no brief).
Esta rodada altera fontes de medidas, páginas e specs. **Nenhuma tabela, coluna, relação, CSV ou fonte nova.**
São as mesmas 49 tabelas e 24 relações: não há exigência de ciclo completo por mudança estrutural nem arquivo de
dados para publicar. Desktop, PBIP gerado, commit e push ficam com a main.

## T29 · fonte independente do canvas

- Removidas todas as marcas de texto nativo do Vega nos dois specs. Os eixos mantêm linhas, grade e marcas, com
  `labels=false`; seus rótulos e os títulos de turno agora são HTML com a Sora embutida do painel.
- `T29_Mapa_Rotulos` fica atrás de `T29_Mapa_Estados`, na mesma caixa, z de conteúdo e conteúdo+1 (padrão da T21).
  Tem os textos dos contadores, legenda e anos da régua. A nota “1998 · CE: Ciro (PPS)” é uma ressalva fixa,
  explicitamente datada; não depende de sincronizar outro visual ao relógio do mapa.
- Ano, quantidade do PT, número do turno, quantidade do adversário e de outros são **cinco contadores em caminhos
  de glifos da Sora** dentro do Vega. O número do turno muda entre 1 e 2 junto com o mapa; não foi fixado no HTML.
- `T29_Grafico_Eixos` fica atrás do gráfico e usa a mesma geometria/escalas declaradas em `desenho_t29.py`.
  Nenhum texto visível desses dois canvas depende de uma fonte instalada no computador. A Sora e as setas do HTML
  continuam embutidas pelo estilo comum, sem nova fonte ou recurso externo.
- Play, pausa, régua clicável, atualização incremental, contadores, margem, cores, lacunas e contexto dos dossiês
  foram preservados. O teste local garante também que os SVGs emitidos pelos dois specs não contêm `<text>`.

Fontes: `pbi/scripts/desenho_t29.py`, `paginas/t29_historia_pt.py` e `pbi/spec/t29_mapa.json` / `t29_votos.json`.

## T23 · fecho no centro

Novo visual `T23_Resumo_Numeros`, caixa **620, 292, 680 × 245**, entre os dois candidatos, acima dos achados.
Mostra a diferença final de **4.430.191 votos**, abstenção **21,08% → 19,22%** do primeiro para o segundo turno,
e **2.960.239 a mais votaram** no segundo turno. Traço discreto abaixo da legenda, sem cruzar os dígitos.
Números com contador automático, cor neutra, diferença a 64 px e apoios a 22/24 px; os resultados espelhados ficam
com os tamanhos anteriores. O maior texto do apoio ocupa cerca de 389 dos 680 px disponíveis.

Sete contas novas em `pbi/dax/T23 Encerramento/Contas/`:

- `T23 · comparecimento 1º turno`, `T23 · comparecimento 2º turno` e `T23 · aptos 1º turno`;
- `T23 · abstenção 1º turno`, `T23 · abstenção 2º turno`;
- `T23 · comparecimento a mais` e `T23 · diferença final`.

Dois desenhos novos: `T23 · Resumo · HTML` e `T23 · Resumo · ALT`. O i do encerramento inclui o fecho e a cobertura.
O gerador `desenho_t23.py` é a fonte dessas medidas e dos achados existentes.

Conta nacional, **com exterior nos dois turnos**: comparecimento 125.275.835 → 128.236.074, saldo 2.960.239.
Os comparecimentos vêm de `PT histórico Brasil`, ano 2026, com contexto nacional fixo. A abstenção do primeiro
turno usa seus aptos; a do segundo reutiliza a conta final da T18, abstenção dividida por comparecimento mais
abstenção nas seções instaladas, como o TSE. Não usar o eleitorado cadastrado no denominador do segundo turno:
há seções não instaladas no exterior. Não confundir este ganho nacional com o municipal sem exterior da T27
(2.920.562); ambos mantêm seus universos.

## Preparação e provas

Sem atuar no Desktop ou gravar PBIP:

```powershell
python -X utf8 pbi/scripts/desenho_t29.py
python -X utf8 pbi/scripts/desenho_t23.py
python -X utf8 pbi/scripts/validar_dax_gerado.py --autoteste
python -X utf8 pbi/scripts/validar_t29.py
node pbi/tools/testar_t29.mjs
python -X utf8 pbi/scripts/validar_pos_eleicao.py
```

Checar `$LASTEXITCODE` após cada comando no PowerShell 5.1. O teste Vega usa fixtures locais em `pbi/qa/rodada3/`
(nome histórico da pasta); o JSON de resultado agora inclui `textosNativosVega: 0` e `contadoresEmGlifos: 5`.
Esses testes não substituem o DAX ou o gesto no Power BI. O validador estrutural não é parser DAX oficial.

Prova consolidada: `pbi/qa/rodada4/provas-locais.json`. Conferidos os quatro números do centro contra os CSV,
49 tabelas/24 relações sem alteração de fontes, 64 arquivos idênticos após regeneração e os testes de animação
e glifos. Validação estrutural: 1.909 medidas e dez autotestes, sem erro. Lint das duas telas: zero erro e 35
avisos de estilo/classificação. `git diff --check` sem erro; referências e caminhos do plano combinado válidos.

### A main prova nesta rodada

1. **T29, foto real em 1920 e a 61%:** textos do mapa, legendas, anos da régua, títulos e eixos do gráfico na Sora;
   nenhum fallback serifado. Conferir o alinhamento do dígito com “º turno”, dos números com “Adversário/Outros”
   e dos rótulos dos eixos com as respectivas marcas.
2. **T29 play/gesto:** 1989 → 2026 e relógio parado; clique em 1994/1998 mostra 1º turno, 1998 mostra 24 para o
   adversário e 1 para outros, Ceará de Ciro; 2026 mostra 2º turno, PT 13, adversário 14, outros 0.
   Rótulos HTML atrás do canvas não devem bloquear régua, play, hover ou dossiê.
3. **T29 gráfico e dossiês:** lacunas de 1994/1998, hover dos dois lados, dossiê do estado e da eleição, i abrir/fechar.
4. **T23, foto real em 1920 e a 61%:** centro sem contato com os blocos dos candidatos ou com os achados;
   contador e traço legíveis, rótulo “1º → 2º turno”, valores iguais aos acima. Atalhos dos cinco atos seguem livres.
5. **Smoke T23 e T29:** zero erro; testar também `previa.py T23 --animado` e T29 animada pelo fluxo da main.
   A T29 continua com a variante estática final para foto/exportação.

Prévias reais novas e aprovação de composição/interação permanecem com a main. Não foram sobrescritos os PNGs
aprovados em `pbi/qa/previa/` nem operado o Desktop nesta rodada.
