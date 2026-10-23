# FONTES — indicadores sociais por município (tela "Quem vota")

Baixados em 23/10/2026 para a tela que cruza o voto do 1º turno com renda, escolaridade, Bolsa Família e IDH dos
municípios (pedido do Alisson). Os arquivos brutos são grandes e ficam fora do git; `pipeline/extrair_social.py` lê
daqui e grava `dados/saida/social_municipio.csv` (só agregados por município).

| Arquivo (nesta pasta) | Fonte | O que entra |
|---|---|---|
| `tse/perfil_eleitorado_2026.zip` (408 MB) | TSE, perfil do eleitorado 2026 (gerado em 14/07/2026): `https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip` | eleitores por município e grau de escolaridade; só os 27 arquivos das UFs (o `_BRASIL` repete todos; o `_ZZ` é o exterior). 157.826.587 eleitores em 5.571 municípios |
| `bf/202608_NovoBolsaFamilia.zip` (331 MB) | Portal da Transparência (CGU), pagamentos do Novo Bolsa Família, competência agosto de 2026: `https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia/202608` | famílias pagas por município (NIS do responsável distintos); 18.778.585 famílias. Setembro ainda não estava publicado (403) |
| `domicilios_2022.json` | IBGE/SIDRA, Censo 2022, tabela 4712, variável 381 (domicílios particulares permanentes ocupados): `https://apisidra.ibge.gov.br/values/t/4712/n6/all/v/381/p/all` | domicílios por município |
| `idhm_ipea.json` | Ipeadata, série ADH_IDHM (Atlas do Desenvolvimento Humano, PNUD/Ipea/FJP): `http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='ADH_IDHM')` | IDHM 2010, o último por município (1991, 2000 e 2010 na série) |

A renda domiciliar per capita do Censo 2022 já estava no cadastro (`dados/bruto/ibge/renda_2022.json`).

## Notas

- O arquivo do Bolsa Família traz nome e NIS de cada responsável: nada nominal sai daqui, só a contagem por município.
  O município do Portal vem pelo código SIAFI e pelo nome; o casamento com o IBGE é pelo nome (UF + nome sem acento), e
  31 grafias diferentes estão em `GRAFIAS_BF` no extrator (Parati → Paraty, Itapagé → Itapajé, Açu → Assú…).
- Bolsa Família por 100 casas = famílias ÷ domicílios × 100. Uma casa pode ter mais de uma família: é uma aproximação,
  dita na tela.
- Escolaridade = fatia com pelo menos o ensino médio completo (médio completo, superior incompleto ou completo) entre os
  eleitores que informaram a escolaridade.
- Sem IDHM 2010: os 7 municípios criados depois de 2010 (Paraíso das Águas/MS, Boa Esperança do Norte/MT, Mojuí dos
  Campos/PA, Nazária/PI, Pinto Bandeira/RS, Balneário Rincão/SC, Pescaria Brava/SC); ficam fora só da lente IDH.
  Boa Esperança do Norte/MT também não tem renda nem domicílios no Censo 2022.
