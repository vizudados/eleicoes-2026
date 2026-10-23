"""O exterior por país no 1º turno (2022 e 2026): as cidades com seção no exterior ligadas ao país
(dados/bruto/exterior/cidade_pais.csv), agregadas por pipeline/exportar_pbi.py. Alimenta o tooltip rico do exterior
(pedido do Alisson, 23/10/2026: "um tooltip rico apenas pra ele, informando por país o percentual de cada um")."""

from gerar_modelo import col, tabela_csv

TABELAS = [
    tabela_csv(
        "Exterior país", "Votos do 1º turno no exterior por país, 2022 e 2026: PT (Lula), principal adversário "
                         "(Bolsonaro em 2022, Flávio em 2026) e válidos, somando as cidades com seção de cada país.",
        "dados/pbi/exterior_pais.csv",
        [col("ano", "Ano", tipo="int", descricao="Ano da eleição.", oculta=True, formato="0"),
         col("pais", "País", descricao="País (Guiana Francesa à parte da França; Hong Kong dentro da China)."),
         col("continente", "Continente", descricao="Continente ou região do mundo."),
         col("cidades", "Cidades", tipo="int", descricao="Cidades com seção no país.", oculta=True, formato="0"),
         col("pt", "VotosPT", tipo="int", descricao="Votos de Lula.", oculta=True),
         col("adv", "VotosAdversario", tipo="int", descricao="Votos do principal adversário (22).", oculta=True),
         col("validos", "Validos", tipo="int", descricao="Votos válidos.", oculta=True)],
        oculta=True),
]
