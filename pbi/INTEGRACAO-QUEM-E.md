# Antes/Depois · integração do agente E · 26/10/2026

## Estado da entrega

**Preparados no sandbox, sem aplicação no PBIP:** T02/T04 e T03/T05 nos dois estados; filtro sincronizado também em T01/T11/T12/T13. Não houve Desktop, refresh, commit, push nem `montar_pbip --aplicar`.

**Checkpoint do primeiro bloco:** contas, DAX, declarações e simulações de T02/T04/T03/T05 passaram nas verificações locais. **Rodada 2: a lacuna de Flávio foi resolvida com um quadro da TV Senado de 25/10, redesenhado pelo image_gen.** As duas imagens novas foram inspecionadas isoladamente. Ainda falta a prova visual/interativa no Desktop para declarar aprovação integral. O Chromium headless foi bloqueado pelo sandbox (`CreateFile: Acesso negado`, `platform_channel.cc`); o conector de computer-use não tinha navegador disponível. Os HTMLs são simulações com CSV e CSS reais, não execução DAX nem capturas do Power BI. Detalhes da licença e da revisão pendente no Commons estão em “Rodada 2”, ao final.

O restante com dados completos foi preparado depois desse checkpoint local. A tabela abaixo separa o que foi implementado do que precisa de decisão da main.

## Contrato comum

- Tabela calculada DAX desconectada **Momento eleição**, duas linhas, sem CSV novo. Coluna `Momento`, ordenada por `Ordem`. Não há relações. Partição `calculated` e colunas seguem o [exemplo oficial Microsoft](https://github.com/microsoft/skills-for-fabric/blob/main/skills/semantic-model-authoring/references/tmdl-guidelines.md).
- Um VizuFilter em cada uma das oito telas: **Pré Eleições 2026 / Pós Eleições 2026**, seleção única, `defaultSelection=value`, `defaultValue=Pós Eleições 2026`. Sem escolha ou escolha múltipla, `[Eleição · pós]` assume Pós.
- Grupo único `Eleicoes2026Momento`, `fieldChanges=true`, `filterChanges=true`, sempre no mesmo campo. A navegação não grava a seleção em bookmark.
- Caixa **x=952, y=60, w=314, h=208**, gatilho de 48 px, lista de 154 px. `z=20`, atrás dos visuais de conteúdo. Funil/ponto vermelho e tokens herdados da casca. O filtro de UF fica em x=1282, com **16 px** de intervalo; não foi movido. As propriedades são validadas contra as capabilities locais do VizuFilter.
- Não há pílula HTML, botão nem bookmark para abrir o filtro. Nos HTMLs de QA, o gatilho é apenas representado; não prova o runtime do visual.
- As contas mantêm o grão e as relações existentes. UF segundo turno inclui ZZ; Município segundo turno exclui exterior. Comparação de 2022 usa o mesmo turno escolhido em 2026.

## Primeiro bloco

**T02/T04:** Pré conserva a ficha do 1º turno, o comício e os dez marcos originais. Pós substitui a leitura do último marco por 25/10, sem editar `trajetoria.csv` nem criar uma 11ª linha. Ficha com a mesma geometria e peso: Lula **64,26 mi · 51,79% · eleito**; Flávio **59,83 mi · 48,21% · 2º lugar**. O retrato oficial permanece. Lula recebe cartão de 180 px, preenchimento discreto, ponto de raio 12 e nota Caveat “recorde”; os comuns têm 124 px e raio 7. O dossiê do desfecho usa a mesma imagem da cena, com recorte no candidato e tipografia ajustada ao host 640×400. Na rodada 2, Flávio voltou a **10 marcos com imagem no Pós**, assim como no Pré. Lula conserva 8 fotos + 2 ilustrações. O recorte do tooltip Pós é centrado em Flávio, preservando o rosto frontal.

**T03/T05:** totais nacionais/UF, votos municipais, válidos, margem, mapa, manchete, origem regional, extremos, rankings e comparações com 2022 respondem ao momento. O percentual nacional Pós usa duas casas; o valor grande passa a 96 px nos dois lados para acomodá-las. UF/região/clique municipal mantêm o grão existente. Mapa e origem não filtram o seletor de momento. São 5.571 municípios nas contas e 5.570 pontos com coordenadas, como na base; nenhuma coordenada foi inventada.

## Conferência dos números

`dados/pbi/uf_2turno.csv`, somado com ZZ, fecha em **64.256.232 + 59.826.041 = 124.082.273** válidos; percentuais exatos arredondam a **51,79% / 48,21%** e a diferença é **4.430.191**. Confrontados com `dados/saida/2turno/resultado_nacional.csv` e `prova_totais.csv`. A base histórica usada pela T29 confirma **60.345.999** (Lula/2022) como a segunda maior votação por candidatura em um turno. T23/T29 e seus geradores foram apenas consultados.

O oráculo adicional fecha, nos dois turnos de 2022 e 2026, **municípios + ZZ = UF/Brasil** para PT, adversário e válidos. Viradas de Lula para o adversário: Pré **711**, Pós **278**; no sentido inverso: **0 / 31**. Ausência de registro municipal em 2022 não vira zero de votação. `oraculo-extensao.json` inclui todas as células de porte × renda, inclusive variações positivas no Pós.

## Fotos, licenças e publicação

| Uso | Autor / data / lugar | Licença e evidência | Situação |
|---|---|---|---|
| Flávio · cena e último marco Pós · rodada 2 | TV Senado · noite de 25/10/2026 · cidade não confirmada | [Commons, vídeo](https://commons.wikimedia.org/wiki/File:Fl%C3%A1vio_Bolsonaro_cita_ministro_ao_aventar_possibilidade_de_anula%C3%A7%C3%A3o_do_resultado_das_elei%C3%A7%C3%B5es.webm), template Attribution-TVSenadoBr e política oficial de uso com atribuição; LicenseReview pendente | Quadro **01:45.012**, recortado antes de gerar; desenho pronto e inspecionado. |
| Lula · cena e último marco Pós | Ricardo Stuckert/Lula Oficial · noite de 25/10/2026 · São Paulo (SP) | [Flickr 55612564286](https://www.flickr.com/photos/157736962@N05/55612564286/), [Commons](https://commons.wikimedia.org/wiki/File:25.10.2026_-_Lula_%C3%A9_reeleito_Presidente_do_Brasil_-_55612564286.jpg), **CC BY-SA 4.0**, metadados e template da API arquivados | Desenho gerado pelo `image_gen` do Codex; arquivo isolado inspecionado. A fonte descreve discurso de reeleição. EXIF 26/10 02:03:36 sem fuso; legenda oficial identifica 25/10. A legenda do painel usa a data do evento sem inventar conversão. |
| Flávio · pronunciamento após resultado | Joédson Alves/Agência Brasil · 25/10/2026 · Brasília (DF) | [Página da foto](https://agenciabrasil.ebc.com.br/de/foto/2026-10/flavio-bolsonaro-fala-com-jornalistas-apos-derrota-no-segundo-1792980117-3) declara todos os direitos reservados; não há CC confirmada | **Não usado, não redesenhado.** Parada neste ponto conforme a regra do pedido. |
| Flávio · alternativa pesquisada | Foto do debate de 23/10, Ricardo Stuckert/Lula Oficial | Commons/Flickr, CC BY-SA 4.0, metadados arquivados | Rejeitada após inspeção: Flávio não tem enquadramento útil. |
| Flávio · alternativa já catalogada | Carlos Moura/Agência Senado · 01/09/2026 · Senado, Brasília | CC BY-SA 4.0, referência existente em FONTES.md | Alternativa da rodada 1, não usada. Superada pelo vídeo da TV Senado na rodada 2. |

Crédito publicado de Lula: **“Desenho CC BY-SA 4.0 a partir de foto de Ricardo Stuckert/Lula Oficial (CC BY-SA 4.0)”**. Registro em `dados/bruto/trajetoria/{FONTES.md,desenhos.csv,pos_eleicao.json}`; original em `arte/ref/historicas/lula-2026-reeleicao.jpg`; prompt em `arte/prompts-fotos/lula-2026-reeleicao.txt`.

**Arquivos novos de mídia que precisam de push para `URL_MIDIA`:** `docs/midia/trajetoria/lula-2026-reeleicao.png` e **`docs/midia/trajetoria/flavio-2026-pronunciamento.png`** (ambos 1536×1024). Cada URL serve à cena e ao respectivo tooltip; não há cópia duplicada. O vídeo original e o recorte ficam nas referências locais. Os metadados/fontes de QA são evidência, não mídia do painel.

## Avaliação de todas as telas, na ordem do roteiro

| Tela | Cabe? / entrega | Pré | Pós | Dado usado ou ausente | Risco / decisão |
|---|---|---|---|---|---|
| T00 Capa | Não | Abertura | Abertura | Texto institucional | Sem pergunta analítica comparável. Intacta. |
| T02 Lula · quem é | Sim · preparado | Ficha 1º turno e candidatura | Reeleição e recorde | Trajetória, UF 2º, foto licenciada | Recorte final no Desktop pendente. |
| T04 Flávio · quem é | Sim · preparado, imagem resolvida na rodada 2 | Ficha 1º e candidatura | 2º lugar no 2º | Trajetória, UF 2º e quadro da TV Senado | Imagem pronta; recorte do cartão/tooltip e interação ainda precisam de Desktop. |
| T10 Pesquisas | Não | Pesquisas anteriores | — | Pesquisas 1º | Assunto de antes; intacta. |
| T01 Resultado | Sim · implementado | 1º turno | Resultado 2º | Candidato UF; UF/Município segundo turno | Só 13/22 têm valor no Pós, demais ficam BLANK. Título passa a “Quem ficou à frente, e por quanto?”. |
| T03 Votos Lula | Sim · implementado | 1º turno | 2º turno | Município/UF segundo turno | Exterior no topo, fora das regiões/mapa; UF preservada. |
| T05 Votos Flávio | Sim · implementado | 1º turno | 2º turno | Mesmo contrato de T03 | Mesmos cálculos/peso. |
| T06 Ausência | Parcial · main decide | Série/composição 2006–2026, 1º | Resposta 2026 teria dado 2º | UF/Município 2º só 2022/2026; falta série completa de brancos/nulos/abstenções do 2º | Não trocar só o KPI e deixar composição histórica com turno implícito. Sem filtro nesta entrega. |
| T25 Quem falta | Não cabe integralmente por falta de dado | Idade × município e série | — | `abstencao_faixa_municipio`/perfil não distinguem 2º | Não copiar perfil etário do 1º para o 2º. Intacta. |
| T11 Virada | Sim · implementado | 2022→2026 no 1º | 2022→2026 no 2º | Município segundo turno | Tooltip da série longa permanece explicitamente **histórico do 1º turno**; mapa/lista/dossiê principal usam o momento. |
| T12 Estados | Sim · implementado | 2022→2026 no 1º | 2022→2026 no 2º | UF/Município 2º; Apuração exterior por país | Dossiê exterior também muda; não deixa países do 1º sob resultado 2º. |
| T13 Perfil | Sim · implementado | Margem por porte/renda 1º | Mesmas cidades, margem 2º | Município segundo turno + dimensão Município | Há células com alta no Pós; redação de comparação admite alta/queda. |
| T24 Quem vota | Duvidosa · main decide | Voto municipal e intenção de pesquisa 1º | Voto municipal 2º existe | Município 2º pronto; Perfil pesquisa continua 1º | Mistura de observado e declarado, escala do gráfico hoje limitada a 70%; decidir se mantém pesquisa como contexto datado e ampliar escala antes de integrar. Intacta. |
| T14 Série | Parcial · main decide | Série municipal/regional, dossiê de candidatos/abstenção | Há série por UF 2º em `pt_historico_uf` | Município 2º só 2022/2026; dossiê atual usa Candidato/Comparecimento ano 1º | Requer outra rota de dados/contrato do dossiê; não trocar só a curva. Intacta. |
| T15 Minha cidade | Parcial · main decide | Viagem por seis eleições 1º | Comparação municipal 2022/2026 2º existe | Falta 2º municipal 2006–2018 | Não preencher a série nem os cliques antigos com 1º sob filtro Pós. Intacta. |
| T19 Explorador | Parcial · main decide | Lista/dispersão e minissérie 2006–2026 1º | Último par e dispersão teriam dado 2º | Falta 2º municipal 2006–2018 | Não misturar a minissérie; filtro “Virou?” e domínio da dispersão também precisam seguir a nova regra. Intacta. |
| T20 Zona eleitoral | Não cabe por falta de dado | Seções somadas por zona, 1º | — | Não há votação por seção/zona 2º na base do modelo | Não ratear município entre zonas. Intacta. |
| T21 20 anos | Não cabe integralmente por falta de dado | Mapa municipal 2006–2026, 1º | — | Falta 2º municipal 2006–2018 | Não animar uma série misturada. Intacta. |
| T22 Simulador | Não | Cenários do antes | — | Modelo de simulação | Proibido mexer; intacto por este agente. |
| T16 Os outros | Não | Pesquisas/apoios do antes | — | Intenção declarada | Não inferir transferência individual. Intacta. |
| T17 2º turno | Não | Pesquisas e sua comparação com urna | — | Série de intenção, resultado já final | Pergunta de pesquisa; sem novo filtro. |
| T07 Debate Band | Não | Efeito do debate | — | Debate/pesquisas | Intacta. |
| T26 Debate Globo | Não | — | Tela específica já datada | Debate/chegadas | Regra do pedido: sem filtro. Intacta. |
| T08 Buscas | Não | Interesse nas buscas | — | Trends | Período existente preservado. |
| T09 Redes | Não | Interesse nas redes | — | Redes/pesquisas | Período existente preservado. |
| T18 Apuração | Não | — | Apuração do 2º | Totalização final | Regra do pedido: só depois. Intacta. |
| T27 De onde vieram | Não | — | Explicação do resultado | Dois turnos | Proibido mexer; intacta por este agente. |
| T28 Onde Flávio perdeu | Não | — | Explicação do resultado | Dois turnos/2022 | Proibido mexer; intacta por este agente. |
| T29 História do PT | Não | — | Série até o recorde | PT histórico | Regra do pedido: só depois; apenas consultada. |
| T23 Encerramento | Não | — | Síntese final | Resultados finais | Intacta. |

## Arquivos compartilhados alterados

1. `pbi/scripts/gerar_modelo.py`: somente suporte a `t['dax']` na coluna (`sourceColumn` com colchetes) e na partição `calculated`. Caminho M anterior preservado. Não foi executado para gravar o modelo.
2. `pbi/scripts/paginas/casca.py`: uma integração comum do seletor nas oito telas e rodapés das mesmas. Usa `_estilo_filtro` e `layout_filtro` existentes. Não muda os outros filtros.
3. `pbi/scripts/roteiro.py`: somente a pergunta da T01, para servir aos dois turnos. A ordem foi preservada.

Demais mudanças ficam nos módulos de T01/T02/T03/T04/T05/T11/T12/T13, seus DAX e leituras. Novos módulos próprios: `momento_eleicao.py` (modelo e script), `contas_momento.py`, pesquisa de fotos e validador. Não alterei `estilo.py`, `pbip_lib.py`, `movimento.js`, T22/T27/T28 ou seus geradores. O repositório já tinha numerosas alterações de outros agentes; não as reverti.

## Preparação, na ordem

Executar a partir da raiz do repositório. Os geradores abaixo escrevem somente DAX/specs; não aplicam o PBIP.

```powershell
python -I -X utf8 pbi/scripts/momento_eleicao.py
python -I -X utf8 pbi/scripts/desenho_t02_t04.py
python -I -X utf8 pbi/scripts/desenho_t03_t05.py
python -I -X utf8 pbi/scripts/validar_quem_e.py
# Checkpoint do primeiro bloco: conferir os HTMLs; imagens resolvidas na rodada 2, Desktop ainda pendente.
python -I -X utf8 pbi/scripts/desenho_t01.py
python -I -X utf8 pbi/scripts/desenho_t11.py
python -I -X utf8 pbi/scripts/desenho_t12.py
python -I -X utf8 pbi/scripts/desenho_t13.py
python -I -X utf8 pbi/scripts/validar_dax_gerado.py
python -I -X utf8 pbi/scripts/validar_quem_e.py
git diff --check
```

Não precisa repetir a pesquisa/download de fotos para preparar o painel. `validar_quem_e.py --render` tenta capturas locais com Chromium; falhou neste sandbox. Não usar `previa.py`, que consulta o motor do Desktop. A tabela calculada preparada pode ser examinada em `pbi/qa/quem-e/Momento eleição.tmdl`; o PBIP e o modelo vivos não foram escritos.

## Provas e validação restante da main

- `pbi/qa/quem-e/index.html`: índice das simulações 1920×1080 e tooltips 640×400.
- `validacao.json`: projeções/referências sem ausências, geometria/sincronia declarada dos oito filtros, totais e ranking histórico.
- `oraculos.json`: 16 recortes (Brasil, MG, RR e PI; Lula/Flávio; Pré/Pós), origem regional e contagens. `*-mapa.json`: datasets reais; os quatro Brasil foram executados pelo Vega local, com saída SVG.
- `oraculo-extensao.json`: conciliação de 2022/2026 por turno, viradas e células. O mockup antigo é oráculo do **Pré**; não usar seus números para aprovar Pós.
- Lint estrutural de toda a árvore DAX e `git diff --check` passaram. Na rodada 1, o lint conta/desenho de T02/T04 e do módulo comum teve **0 erros e 107 avisos** (69 linhas longas, 36 contas sem anotação individual de oráculo e 2 avisos de aninhamento); o relatório daquela rodada é `lint-conta-desenho.json`. O resultado atualizado da rodada 2 está abaixo. Os oráculos numéricos estão nos JSONs de QA, sem suprimir esses avisos. Não equivale ao parser/motor DAX, ao parser TMDL do Desktop nem à aprovação visual.

Na integração da main: incluir a nova declaração do modelo, gerar o modelo/relatório pelo ciclo autorizado e garantir que a mídia já publicada corresponde aos dois PNGs novos. No Desktop, provar **Pós na primeira abertura**, Pré↔Pós em ambas as fichas e ambos os mapas, limpar/sem escolha=Pós, persistência entre as oito páginas e navegação sem reset. Abrir a lista de momento, conferir as duas opções inteiras e fechar; com ela fechada, testar o hover/clique nos visuais sob a reserva transparente. Conferir dois filtros juntos em UF única, região e várias UFs; clicar município e região nos mapas, dossiês e retorno ao Brasil. Provar T02 último card/nota/ponto maior e tooltip com foto nova; T04 último marco neutro e contagem **10/10**, com a imagem da TV Senado na cena e no dossiê. Medir overflow/última linha dos créditos, ficha e tooltip no tamanho real. Provar na T01 que os demais candidatos somem no Pós e que todos os pontos da comparação usam o mesmo turno; na T12, testar exterior por país no 2º; na T11, a série histórica explicitamente 1º; na T13, recortes com alta e queda. Só então aprovar o checkpoint e salvar/publicar pelo processo da main.

## Rodada 2 · imagem Pós de Flávio

**Imagem resolvida e integrada no gerador.** O novo `docs/midia/trajetoria/flavio-2026-pronunciamento.png` (1536×1024, 4.326.095 bytes) serve à cena Pós e ao último marco/dossiê T04. Crédito: **“Desenho CC BY-SA 4.0 a partir de imagem da TV Senado (atribuição)”**. Legenda: **“Pronunciamento após o resultado, 25 de outubro de 2026”**. Sem cidade: a descrição do arquivo e a fonte pública do Senado consultada não confirmaram o local. A data 26/10 do registro corresponde à publicação; a descrição identifica a noite de domingo, 25/10.

**Licença conferida:** a API da página Commons e o template `Attribution-TVSenadoBr` (texto PT) confirmam atribuição à TV Senado. A [política primária do Senado](https://www12.senado.leg.br/noticias/politica-de-uso) permite o uso com crédito ao canal e aos autores explicitados e sem descaracterizar o contexto. O autor informado é TV Senado. **O marcador `LicenseReview` está vazio e a revisão do Commons ainda é pendente**; sua presença não foi tratada como aprovação. A fonte é de atribuição, e **CC BY-SA 4.0 é a licença do desenho novo**, sem alegar que o vídeo original tenha essa licença.

**Quadro escolhido:** busca **01:45**, PTS exato **105,012 s** (`00:01:45.012`). Vídeo [Commons](https://commons.wikimedia.org/wiki/File:Fl%C3%A1vio_Bolsonaro_cita_ministro_ao_aventar_possibilidade_de_anula%C3%A7%C3%A3o_do_resultado_das_elei%C3%A7%C3%B5es.webm), fonte [YouTube TV Senado, bB0z-mMDk3A](https://www.youtube.com/watch?v=bB0z-mMDk3A). Original 1920×1080, 173,948 s, 58.202.488 bytes. `ffmpeg` aplicou **`crop=660:600:576:135` antes da geração**, retirando Libras, tarjas, logos/rodapé e microfones com marcas. Foram examinados seis quadros; a escolha privilegia rosto frontal, olhos abertos e expressão contida. Desenho somente por `image_gen` do Codex, com o PNG de Lula como referência de estilo. A inspeção do arquivo isolado confirmou traço/papel coerentes, camisa e pose preservadas, sem texto, símbolos de TV ou caricatura.

**Arquivos novos desta rodada:**

- **Para push de mídia:** `docs/midia/trajetoria/flavio-2026-pronunciamento.png`.
- Referências locais: `arte/ref/historicas/flavio-2026-pronunciamento-tv-senado.webm` e `flavio-2026-pronunciamento-quadro-0105-corte.png`.
- Prompt: `arte/prompts-fotos/flavio-2026-pronunciamento.txt`.
- Evidências: `pbi/qa/quem-e/fontes/{flavio-2026-pos-video-metadados.json,tv-senado-template-atribuicao.json,tv-senado-template-texto.json,flavio-video-download.json}` e `pbi/qa/quem-e/rodada2/{analise-quadros.md,flavio-referencia.json,extracao-quadro-0105.log,lint-conta-desenho.json}`. O manifesto guarda SHA-256 do vídeo e do quadro.

**Integração:** registros atualizados em `FONTES.md`, `desenhos.csv` e `pos_eleicao.json`; T02/T04 regeneradas. A contagem Pós de Flávio voltou a **10 marcos com imagem**, sem criar marco extra. O crop do tooltip T04 Pós passou a `object-position:50% 40%` para preservar o rosto frontal; o crop de Lula e ambos os estados Pré permanecem. O validador agora confere os PNGs 3:2, a cadeia metadado/registro/cena, os dez marcos e o PTS de Flávio. O índice de QA deixou de mostrar a pendência resolvida.

**Validação:** lint estrutural DAX sem erros; referências e provas numéricas locais passaram. Lint conta/desenho de T02/T04 + módulo comum: **0 erros, 108 avisos** (71 linhas longas, 35 anotações individuais de oráculo ausentes, 2 avisos de aninhamento), preservados no relatório. A prova de render/interação no Desktop continua a cargo da main. Não houve Desktop, refresh, aplicação PBIP, commit ou push. Não alterei T22/T27/T28 nem estilo/pbip_lib/movimento nesta rodada.

Comandos da rodada 2, na ordem, a partir da raiz:

```powershell
# Conferência pública reproduzível; não é necessária para regenerar o DAX já preparado.
python -I -X utf8 pbi/scripts/pesquisar_fotos_quem_e.py --flavio-video
# Recorte já guardado; este comando o reproduz a partir do vídeo local.
ffmpeg -hide_banner -y -ss 105 -copyts -i arte/ref/historicas/flavio-2026-pronunciamento-tv-senado.webm -frames:v 1 -vf "crop=660:600:576:135,showinfo" -update 1 arte/ref/historicas/flavio-2026-pronunciamento-quadro-0105-corte.png
python -I -X utf8 pbi/scripts/desenho_t02_t04.py
python -I -X utf8 pbi/scripts/validar_dax_gerado.py
python -I -X utf8 pbi/scripts/validar_quem_e.py
git diff --check
```

Não há comando de API paga para reproduzir o desenho: o prompt foi executado na ferramenta local `image_gen`, e o arquivo final já está no projeto. No Desktop da main, conferir o rosto inteiro no cartão e no tooltip, crédito/legenda completos, T04 com dez imagens nos dois estados e Lula sem mudança. Publicar o PNG novo junto aos demais arquivos de mídia antes da prova final das URLs.

## Rodada 3 · T12 direção/colisão e T11 dica cortada

**Correções preparadas nos geradores e DAX, sem Desktop nem aplicação PBIP.** As prévias reais fornecidas pela main foram usadas como evidência dos defeitos e como cache de host/fontes nas simulações. Os PNGs de Lula/Flávio otimizados pela main não foram alterados ou regenerados.

**T12 — direção da margem.** A manchete do Brasil deixou de presumir maioria para Flávio. Agora lê as duas contagens e apresenta primeiro a maior: **Pós: “16 unidades foram na direção de Lula; 11, na de Flávio”**; **Pré: “26 unidades foram na direção de Flávio; 1, na de Lula”**. O clique em UF ou região continua usando a variação/contagem daquele lugar; os 27 da resposta geral continuam sendo o Brasil, conforme o contrato original. A manchete de UF ficou mais curta (o ranking continua no tooltip), e a regional apresenta quantidade com queda e margem 2022→2026. Foram revistos os tooltips: “foi contra a maré” virou uma descrição factual da alta; mudanças para Lula também são reconhecidas; variação nula não é chamada de alta. A descrição acessível da corrida informa as duas contagens.

**T12 — colisão à esquerda.** A conta nova **`T12 · exemplos onde a margem subiu`** devolve no máximo três siglas, em ordem alfabética. No Pós, o apoio ficou: **“16 unidades foram na direção de Lula. Entre elas: AC, AL e AM.”** O caso de uma única unidade (DF no Pré) conserva o nome e a variação. Mais importante: o apoio e “O QUE É MARGEM” agora são irmãos em um fluxo vertical (`.apoio`, `flex-direction:column`, `gap:20px`), em vez de dois blocos absolutos separados por 56 px. A altura do texto passa a deslocar o bloco inferior naturalmente. Caixa da resposta preservada: **560×560**.

**T11 — dica.** A legenda usa toda a largura de **820 px**, com intervalo de 12 px e a dica sem encolhimento. Texto normal: **“clique ou arraste”**; com seleção: **“clique fora para limpar”**. Foram mantidos os quatro significados/cores da legenda e as fontes de 15/13 px. O mapa e a caixa de título **820×100** não mudaram.

**Arquivos de fonte alterados nesta rodada:** `pbi/scripts/desenho_t12.py`, `paginas/t12_estados.py`, `desenho_t11.py`, `paginas/t11_virada.py`; DAX correspondentes regenerados. Novo helper de QA: `pbi/scripts/simular_quem_e_rodada3.py`. Para T11 foi chamada somente `gravar()`: **o spec do mapa não foi regenerado**. Não houve edição de T22/T27/T28, estilo, pbip_lib ou movimento, nem commit/push.

**Provas locais:** `pbi/qa/quem-e/rodada3/index.html` contém as simulações. Foram preparados **140 componentes**: resposta/título de T12 em **68 contextos** (Brasil com ZZ nas barras, 27 UFs, exterior e cinco regiões; dois turnos) e quatro combinações da legenda de T11 (três/quatro categorias, com/sem seleção). Também há `T11-pos-pagina.html` e `T12-pos-pagina.html`, preservando os outros visuais do cache real Pós da main.

- `oraculos.json`: contagens/direções conferidas contra os CSV dos dois turnos; Brasil **26/1** e **11/16**.
- `prova-fontes.json`: métricas da Sora, usando peso 600 como limite conservador para os textos de T12. Maior largura de manchete: **862,11 de 1.010 px**. Limite calculado para o fim do bloco inferior: **483,90 de 560 px**. Folga mínima da legenda de T11: **20,86 px**. O espaço entre apoio e margem é garantido pelo fluxo de 20 px.
- Lint estrutural: **1.968 medidas, zero erros**. Validador geral `validar_quem_e.py`: referências, imagens e oráculos passaram. Lint conta/desenho nos oito arquivos DAX novos/alterados da rodada: **zero erros, 14 avisos de linhas longas**, em `lint-conta-desenho.json`.
- **Render DOM/PNG não concluído neste sandbox:** `--render` foi executado, mas o driver Playwright falhou ao abrir o canal local com **`[WinError 5] Acesso negado`** antes de iniciar o navegador. Evidência em `falha-render.txt`. As métricas de fonte e o modelo de fluxo CSS não são apresentadas como captura nem como prova do motor DAX.

Comandos específicos da rodada, a partir da raiz:

```powershell
python -I -X utf8 pbi/scripts/desenho_t12.py
python -I -X utf8 -c "import sys; sys.path.insert(0,'pbi/scripts'); import desenho_t11; desenho_t11.gravar()"
python -I -X utf8 pbi/scripts/validar_dax_gerado.py
python -I -X utf8 pbi/scripts/validar_quem_e.py
python -I -X utf8 pbi/scripts/simular_quem_e_rodada3.py
git diff --check
# Para a main executar onde o Chromium puder iniciar, sem consultar o Desktop:
python -I -X utf8 pbi/scripts/simular_quem_e_rodada3.py --render
```

Na integração da main, incorporar a **conta nova de exemplos** ao modelo e os **dois bodyTemplates/CSS de página**, além do DAX. Depois conferir no motor/na prévia real T12 Pré/Pós Brasil, UF (inclusive Amapá/DF/exterior) e região; o apoio deve ficar pelo menos 20 px acima da definição. Em T11, provar legenda com a quarta categoria e com seleção do mapa, sem corte da dica. A renderização da rodada 3 continua pendente da main; não repetir refresh nesta sessão do agente E.
