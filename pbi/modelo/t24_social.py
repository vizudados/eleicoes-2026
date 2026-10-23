"""Tela T24 · Quem vota (a 14ª na ordem do roteiro): renda, escolaridade, Bolsa Família e IDH dos lugares e o que as
pesquisas dizem dos eleitores (pedido do Alisson, 23/10/2026, como tela própria para não poluir a 13).

  Social município   município × lente: o valor do indicador e o degrau (1 a 5, cada degrau com um quinto dos
                     eleitores) — pipeline/extrair_social.py e pipeline/exportar_pbi.py › social()
  T24 Lente          as quatro lentes, na ordem dos botões (desconectada; a tela lê com SELECTEDVALUE, padrão Renda)
  T24 Degrau         1 a 5, o grão do gráfico e do tooltip (desconectada)
  Perfil pesquisa    a intenção de voto de Lula e Flávio por renda, escolaridade e Bolsa Família nas pesquisas
                     (dados/bruto/pesquisas/perfil_lula_flavio.csv)
"""

from gerar_modelo import col, tabela, tabela_csv

_LENTE = """let
    Tabela = #table(type table [Lente = text, Ordem = Int64.Type],
        {{"Renda", 1}, {"Escolaridade", 2}, {"Bolsa Família", 3}, {"IDH", 4}})
in
    Tabela"""

_DEGRAU = """let
    Valores = List.Numbers(1, 5, 1),
    Tabela = Table.FromList(Valores, Splitter.SplitByNothing(), {"Degrau"}),
    Tipos = Table.TransformColumnTypes(Tabela, {{"Degrau", Int64.Type}})
in
    Tipos"""

TABELAS = [
    tabela_csv(
        "Social município", "Município × lente (renda, escolaridade, Bolsa Família, IDH): o valor do indicador e o "
                            "degrau, de 1 (menos) a 5 (mais), com os municípios em fila pelo indicador e a fila cortada "
                            "em cinco partes com o mesmo número de eleitores de 2026.",
        "dados/pbi/municipio_social.csv",
        [col("cd_ibge", "CodIBGE", descricao="Código IBGE do município.", oculta=True),
         col("lente", "Lente", descricao="Renda, Escolaridade, Bolsa Família ou IDH."),
         col("lente_ordem", "LenteOrdem", tipo="int", descricao="Ordem da lente.", oculta=True, formato="0"),
         col("valor", "Valor", tipo="number", descricao="Renda domiciliar per capita (R$, Censo 2022); fatia do "
             "eleitorado com ensino médio completo ou mais (TSE, 2026); famílias no Bolsa Família por 100 domicílios "
             "(ago/2026 ÷ Censo 2022); IDHM 2010.", oculta=True),
         col("degrau", "Degrau", tipo="int", descricao="Degrau de 1 a 5 (cada um com um quinto dos eleitores).",
             oculta=True, formato="0")],
        oculta=True),
    tabela("T24 Lente", "As quatro lentes da tela 14 (Quem vota), na ordem dos botões. Sem marca, a tela usa Renda.",
           [col("Lente", descricao="Renda, Escolaridade, Bolsa Família, IDH.", ordenar_por="Ordem"),
            col("Ordem", tipo="int", descricao="Ordem do botão.", oculta=True, formato="0")], _LENTE),
    tabela("T24 Degrau", "Os cinco degraus da tela 14 (Quem vota): grão do gráfico e do tooltip.",
           [col("Degrau", tipo="int", descricao="Degrau de 1 (menos) a 5 (mais).", formato="0")], _DEGRAU,
           oculta=True),
    tabela_csv(
        "Perfil pesquisa", "Intenção de voto no 1º turno em Lula e Flávio por renda, escolaridade e Bolsa Família, na "
                           "última rodada de cada instituto antes de 04/10/2026 que publicou o cruzamento.",
        "dados/pbi/perfil_pesquisa.csv",
        [col("instituto", "Instituto", descricao="Instituto da pesquisa."),
         col("divulgacao", "Divulgação", tipo="date", descricao="Data de divulgação.", oculta=True),
         col("campo", "Campo", descricao="Período de campo e registro no TSE.", oculta=True),
         col("candidato", "Candidato", descricao="Lula ou Flávio."),
         col("lente", "Lente", descricao="Renda, Escolaridade ou Bolsa Família (a mesma da tela)."),
         col("categoria", "Categoria", descricao="Faixa do instituto (ex. até 2 SM, superior, beneficiário).",
             ordenar_por="CategoriaOrdem"),
         col("categoria_ordem", "CategoriaOrdem", tipo="int", descricao="Ordem da faixa.", oculta=True, formato="0"),
         col("percentual", "Percentual", tipo="number", descricao="Intenção de voto no segmento (% do total).",
             oculta=True),
         col("fatia", "Fatia", tipo="number", descricao="Fatia do grupo na amostra (base ponderada ÷ n), quando o "
             "instituto publicou; 1 no total.", oculta=True),
         col("fonte_url", "Fonte", descricao="Endereço da fonte.", oculta=True)],
        oculta=True),
]
