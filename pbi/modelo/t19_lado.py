"""Tabela da tela 19 · Explorador (dono: tela 19): o lado de cada município em 2022 e em 2026, para a segmentação
"Virou?". Lê dados/pbi/t19_lado.csv (pipeline/exportar_t19.py) e filtra o Município pela relação T19 Lado → Município
(um para um na prática; o Município é o lado "muitos", então o filtro desce da T19 Lado para o Município e daí para o
Município ano)."""

from gerar_modelo import col, tabela_csv

TABELAS = [
    tabela_csv(
        "T19 Lado", "De que lado cada município ficou em 2022 e em 2026 (margem do PT > 0 = PT à frente): Virou para "
                    "Flávio, Lula nas duas, Bolsonaro nas duas (Jair em 2022, Flávio em 2026) ou Empate ou cidade "
                    "nova. Só alimenta a segmentação \"Virou?\" da tela 19; as contas leem as margens.",
        "dados/pbi/t19_lado.csv",
        [col("cd_ibge", "CodIBGE", descricao="Código IBGE do município (chave; liga com Município).", oculta=True),
         col("lado", "Lado", descricao="Lado em 2022 → 2026: Virou para Flávio, Lula nas duas, Bolsonaro nas duas, "
             "Empate ou cidade nova.", ordenar_por="Ordem"),
         col("lado_ordem", "Ordem", tipo="int", descricao="Ordem do rótulo na segmentação.", oculta=True,
             formato="0")]),
]

RELACOES = [
    ("Município", "CodIBGE", "T19 Lado", "CodIBGE"),
]
