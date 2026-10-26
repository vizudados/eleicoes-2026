# Integração pós-eleição · rodada 3 · 26/10/2026

Handoff vigente, após a integração e as provas reais da rodada 2 (`1bce008`, informadas pela main).
Desktop, modelo em execução, PBIP gerado, commit, push e publicação não foram operados nesta rodada.
As fotos da main em `pbi/qa/previa/` continuam sendo a evidência de motor da rodada anterior.

## O que mudou

- **T00:** rótulo do mapa em `x=1040, y=808, 270×28`, alinhado à esquerda, no céu à direita do RS, acima do horizonte
  que começa em y=853. O “começar” foi para `x=1800, y=590`, abaixo da seta e fora do bloco de números; o alvo do
  botão acompanha a posição. Os tempos do vídeo continuam em 9,333333333 s e 13,2 s, conforme o LEIAME da capa.
- **T27:** “A urna não mostra quem trocou de candidato.”, com inicial maiúscula. Conta e método preservados.
- **T28:** perda frente a Jair passa a `−144,0 mil`, `−93,6 mil` etc.; a conta positiva usada no ranking permanece
  igual. Só a representação da perda recebeu o sinal negativo.
- **T29 / 28 · História do PT:** nova página do ato V, sem filtro, entre T28 e T23. Protagonista: mapa das 27 UFs,
  dez eleições de 1989 a 2026, turno decisivo, vencedor real e intensidade da vantagem sobre o segundo colocado.
  Autoplay começa quando os dez quadros chegam, avança a cada 1,9 s e para em 2026; transição de 650 ms, pausa,
  replay e régua clicável. Atualização incremental ligada, contadores nacionais por ano e dossiê por UF.
  Apoios: gráfico de votos com dois painéis/mesma escala (PT e principal adversário nacional), e comparação dos
  denominadores. As lacunas de 1994/1998 interrompem a linha do segundo turno; a queda de 2014→2018 é preservada.
  O dossiê estadual mostra os dois turnos, incluindo traços quando não houve segundo; o dossiê do gráfico identifica
  as duas candidaturas, válidos e participação. Nota de versões históricas visível e ressalvas completas no i.
- **T23 / 29 · Encerramento:** par escuro da capa, título “Da zona eleitoral ao resultado.”, blocos espelhados
  Flávio/Lula com os mesmos tamanhos e as mesmas contas da capa: segundo turno maior, primeiro menor e selo eleito.
  A urna grande saiu. Onze achados/atalhos em cinco atos, com o ato V completo: 20, 25, 26, 27 e 28. As caixas dos
  links e o HTML usam uma única geometria em `t23_encerramento.py`; os achados encurtaram para preservar o resultado.
- **Roteiro/sumário:** 30 telas, 28 História do PT, 29 Encerramento; a última coluna do sumário usa passos de 68 px
  para caberem onze itens. Regex de visual, tooltip e bookmark aceita T29. README e perguntas acompanham a ordem.

## Modelo mudou: ciclo completo obrigatório

Novo módulo `pbi/modelo/pt_historico.py`, carregado automaticamente pelo gerador:

| Tabela | CSV | Grão / uso | Relação |
|---|---|---|---|
| PT histórico UF | `dados/pbi/pt_historico_uf.csv` | 504 linhas, UF × ano × turno; série completa do dossiê estadual | UF → UF[UF] |
| PT histórico Brasil | `dados/pbi/pt_historico_brasil.csv` | 18 linhas, ano × turno, exterior incluído uma vez; gráfico/recorde | desconectada: BR não é uma UF |
| PT histórico mapa | **`dados/pbi/t29_mapa.csv`** | 280 linhas, UF × eleição, turno decisivo e vencedor real | UF → UF[UF] |

Não ligar essas tabelas a `Ano`: a dimensão atual começa em 2006, e a série nova começa em 1989. As duas relações
novas são unidirecionais, padrão fato → dimensão na declaração do projeto; não há relacionamento entre os fatos.
UF histórico e Brasil já estavam no GitHub segundo o brief; **o único CSV novo a publicar é `t29_mapa.csv`**.

O derivado é reproduzido por `pipeline/exportar_t29.py`, lendo `mapa_turno_decisivo.csv` e
`todos_candidatos_uf.csv` das saídas históricas. Não substitui o vencedor da UF pelo principal adversário nacional:
Ceará/1998 = Ciro Gomes (PPS), vantagem de 37.112 sobre o segundo colocado. A intensidade usa a mesma conta em
todas as UFs: `(votos do vencedor − votos do segundo) / válidos`. Exterior existe nos fatos e não tem geometria;
é descartado antes de desenhar, e não entra nos contadores das 27 UFs.

Publicar o CSV derivado e confirmar resposta 200 do raw antes do refresh/ciclo (L135). Depois, a main fecha o
Desktop pelo procedimento de casa, gera o modelo, aplica as páginas e reabre com refresh. **Não é só medidas/páginas.**

Preparação segura, sem Desktop ou geração de PBIP:

```powershell
python -X utf8 pipeline/exportar_t29.py
python -X utf8 pbi/scripts/desenho_t29.py
python -X utf8 pbi/scripts/desenho_t23.py
python -X utf8 pbi/scripts/desenho_t27_t28.py
python -X utf8 pbi/scripts/validar_dax_gerado.py --autoteste
python -X utf8 pbi/scripts/validar_t29.py
node pbi/tools/testar_t29.mjs
python -X utf8 pbi/scripts/validar_pos_eleicao.py
```

Checar `$LASTEXITCODE` após cada comando no PowerShell 5.1. Os geradores de desenho gravam só suas fontes DAX/spec;
não chamam `gerar_modelo`, `montar_pbip --aplicar`, Desktop, refresh ou git.

## Números conferidos localmente

- **Recorde:** Lula 64.256.232 em 2026/2; marca anterior, dele, 60.345.999 em 2022/2; diferença **3.910.233**.
  Ranking por candidatura em um único turno, sem somar eleições ou turnos. A formulação presidencial direta vem
  do método H5: 127 candidaturas/turnos desde 1989 e limites dos mais votados nas eleições diretas anteriores.
- **Fatia dos válidos:** 61,27% em 2002/2 e 51,79% em 2026/2; eleitorado 82.074.718 em 1989 e 158.745.502 em 2026.
- **UFs com PT à frente:** 1989: 4; 1994: 2; 1998: 2; 2002: 26; 2006: 20; 2010: 16; 2014: 15; 2018: 11;
  2022: 13; 2026: 13. Em 1998 são 24 para o adversário nacional, 2 para o PT e 1 para Ciro.
- **Queda 2014→2018:** PT −11.925.617 no primeiro turno; −7.460.212 no segundo.
- **Resultados da capa/encerramento:** Lula 64.256.232, 51,79%; Flávio 59.826.041, 48,21%; diferença 4.430.191.
  A T27 continua sem exterior, com ganhos +10.333.927 e +3.693.941 e identidade total +14.027.868; o encerramento
  usa a conta nacional da rodada anterior, +10,38 mi e +3,72 mi, com exterior.

## Provas locais e limite da evidência

`pbi/qa/rodada3/validacao-t29.json`: 504 linhas estaduais, 18 nacionais e 280 decisivas; 90 fechamentos por campo;
280 vencedores conferidos contra o ranking de todas as candidaturas; recorde, diferença, quedas e contadores.
`validacao-vega.json`: specs executadas no Vega local, 27 caminhos, autoplay pelos dez anos, relógio parado no fim,
ano preservado após atualização incremental, Ciro/1998 e quatro lacunas (dois anos × dois lados). `__row__`
permanece nos mapas e nos pontos válidos do gráfico, para o tooltip resolver o contexto original.

Os componentes foram renderizados em SVG e revisados localmente em `pbi/qa/rodada3/T29-mapa-local.svg` e
`T29-votos-local.svg`; são fixtures de CSV, **não prévias do motor**. Não substituem os PNG reais em `qa/previa`.
O validador estrutural verificou 1.900 medidas e dez casos de autoteste sem erro; ele não é parser DAX oficial.
O plano combinado com as novas declarações não apontou referências/caminhos inválidos. Lint conta × desenho:
zero erro, avisos de estilo/linhas longas, escapes e classificações dos campos serializados.
Os quatro geradores foram repetidos: **168 arquivos idênticos**, incluindo CSV, medidas e specs. As 26 referências
distintas de colunas da T29 existem nas declarações; o modelo passa a 49 tabelas e 24 relações declaradas.

A mecânica segue a T21/L123 e os contratos de [signals](https://vega.github.io/vega/docs/signals/) e
[event streams do Vega](https://vega.github.io/vega/docs/event-streams/). `estatico` mostra 2026 na prévia/PDF;
o sinal `reduceMotion=true` fixa a variante sem animação para exportação, além do botão de pausa disponível na tela.

## O que a main precisa provar após integrar

1. **Smoke T00, T23, T27, T28 e T29.** Novas tabelas e 46 medidas T29 só passam no motor após o ciclo completo.
2. **T00 a 1920 e 61%:** céu livre atrás do rótulo, sem horizonte sob o texto; “começar” afastado de porcentagem,
   primeira votação e selo. Ver vídeo nas janelas 1º/2º e movimento reduzido, mantendo os tempos anteriores.
3. **T23 a 1920 e 61%:** título, resultado espelhado, selo, todos os onze achados sem corte. Clicar nos cinco links
   do ato V e voltar; validar que 28 abre História e 29 é Encerramento. Fonte/crédito no i.
4. **T27/T28, Brasil e MG:** inicial maiúscula, identidade igual à rodada 2; perdas de Jair com sinal de menos.
   Roraima/AC continuam com o tratamento de recortes em que um dos candidatos perdeu votos.
5. **T29 Brasil, foto estática e play real:** esperar cerca de 20 s desde o dado chegar; inicia em 1989, termina
   em 2026 e não reinicia ao atualizar a seleção/tooltip. Pausar, retomar, clicar em 1998 e 2002, replay do fim.
   Conferir os contadores da lista acima; 1998/CE marrom/Ciro, 1994/1998 indicados como primeiro turno.
6. **T29 gráfico:** turnos separados, mesma escala 0–70 mi, lacuna visível entre 1989/2 e 2002/2, sem inventar
   pontos em 1994/1998. Queda 2014→2018; nota à mão do recorde sem encostar em linha/número; hover realça um lado.
7. **T29 tooltips:** no mapa, CE e MG abrem o dossiê estadual inteiro (710 px de altura) com dez linhas e os dois
   turnos, sem cortar as notas finais; 1994/1998 com traço no segundo turno. No gráfico, 2026/2 e 1989/2 abrem o
   dossiê nacional com candidaturas, votos e participação, sem levar o contexto de outra linha.
8. **T29 i / navegação / sumário:** fontes e ressalvas H11 legíveis, abrir/fechar, setas T28 → T29 → T23, novo item
   no sumário sem colidir com rodapé. Não exigir coincidência com todas as publicações históricas do TSE: as versões
   divergentes estão preservadas e documentadas, sem ajuste artificial.

Não há mudança de vídeo, arte gerada, coletor ou infraestrutura nesta rodada. A prova de composição completa e de
interação no Power BI permanece pendente da main; não foi alegada aprovação visual de motor para estas alterações.
