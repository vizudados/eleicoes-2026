"""Tabela da tela 13 · Perfil (dono: tela 13): a célula porte × quinto de renda de cada município, para a matriz da tela
ter um ponto de dado por célula (tooltip de página e filtro cruzado; HTML Content com granularidade numa coluna só).

Lê o MESMO dados/pbi/municipio.csv do Município (não há CSV novo nem push): o código IBGE, o porte e o quinto, e monta a
célula no Power Query ("até 10 mil × mais ricas", 25 valores) e a ordem dela (porte × 10 + quinto). Filtra o Município
pela relação T13 Célula → Município (um para um na prática; o Município é o lado "muitos", como a T19 Lado), e daí o
Município ano: clicar numa célula da matriz filtra as cidades dela no resto da tela.
"""

from gerar_modelo import col, tabela_csv

_PASSOS = """    Celula = Table.AddColumn({entrada}, "Célula", each [Porte] & " × " & [Quinto de renda], type text),
    Final = Table.AddColumn(Celula, "CelulaOrdem", each [PorteOrdem] * 10 + [QuintoOrdem], Int64.Type)"""

TABELAS = [
    tabela_csv(
        "T13 Célula", "A célula da matriz da tela 13 (porte × quinto de renda) de cada um dos 5.571 municípios. Só serve "
                      "de grão à matriz (um ponto por célula: tooltip e filtro cruzado); as contas leem o Município.",
        "dados/pbi/municipio.csv",
        [col("cd_ibge", "CodIBGE", descricao="Código IBGE do município (chave; liga com Município).", oculta=True),
         col("porte", "Porte", descricao="Faixa de população (até 10 mil … mais de 1 milhão).", oculta=True),
         col("porte_ordem", "PorteOrdem", tipo="int", descricao="Ordem do porte.", oculta=True, formato="0"),
         col("quinto", "Quinto de renda", descricao="Quinto dos municípios pela renda per capita.", oculta=True),
         col("quinto_ordem", "QuintoOrdem", tipo="int", descricao="Ordem do quinto (1 = mais pobres).", oculta=True,
             formato="0"),
         col(None, "Célula", descricao="A célula da matriz: porte × quinto de renda (25 combinações).",
             ordenar_por="CelulaOrdem"),
         col(None, "CelulaOrdem", tipo="int", descricao="Ordem da célula: porte × 10 + quinto.", oculta=True,
             formato="0")],
        passos=_PASSOS),
]

RELACOES = [
    ("Município", "CodIBGE", "T13 Célula", "CodIBGE"),
]
