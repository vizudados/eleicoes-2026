"""Tabela da tela 19 · Explorador (dono: tela 19): o filtro do recorte em acordeão (VizuFilter em modo caminho).

Uma linha por município × grupo do filtro ("raiz"): Região, Estado, Tamanho da cidade, Renda (quinto), Virou? e
Cidade (6 × 5.571, menos as lacunas: Boa Esperança do Norte/MT, criada em 2025, não tem porte nem quinto). A coluna
Caminho ("Região › Nordeste", "Cidade › Contagem (MG)") é o campo único do VizuFilter; a ordem do acordeão sai de Ordem
(raiz × 10.000 + a ordem do valor: as regiões do Norte ao Sul, os estados e as cidades em ordem alfabética pt-BR, o porte
e o quinto do menor ao maior, o lado na ordem da T19 Lado).

Sem relação ATIVA com o Município, de propósito: o filtro não desce para o Município (um filtro numa coluna só daria OU
entre os grupos). A medida [T19 · no recorte] faz a regra certa (E entre grupos, OU dentro do mesmo grupo): um município
está no recorte quando, em cada grupo com escolha, a linha dele está entre as escolhidas. Para isso ela liga, só dentro
dela (USERELATIONSHIP), a relação INATIVA T19 Filtro[CodIBGE] → Município[CodIBGE]: o município da linha filtra as
linhas dele na T19 Filtro (sentido único, do Município para cá), uma junção que o motor resolve de uma vez, em vez de um
TREATAS por município. A lista e a dispersão filtram por [T19 · no recorte] = 1.

Lê os MESMOS dados/pbi/municipio.csv e dados/pbi/t19_lado.csv do Município e da T19 Lado (não há CSV novo nem push); o
nome de cada UF vem de modelo/base.py (UFS), gravado no M.
"""

import importlib.util
from pathlib import Path

from gerar_modelo import col, tabela

_spec = importlib.util.spec_from_file_location("modelo_base_t19", Path(__file__).with_name("base.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

SEPARADOR = " › "        # o mesmo de general.pathSeparator do VizuFilter (paginas/t19_explorador.py)
# raízes na ordem do acordeão: (ordem, nome). As medidas de T19 leem a raiz pela ordem (RaizOrdem), não pelo nome.
RAIZES = [(1, "Região"), (2, "Estado"), (3, "Tamanho da cidade"), (4, "Renda (quinto)"), (5, "Virou?"), (6, "Cidade")]
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def _sem_acento(texto: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").casefold()


def _m() -> str:
    ufs = sorted(_base.UFS, key=lambda u: _sem_acento(u[1]))
    linhas_uf = ", ".join(f'{{"{s}", "{n}", {i + 1}}}' for i, (s, n, _r) in enumerate(ufs))
    linhas_reg = ", ".join(f'{{"{r}", {i + 1}}}' for i, r in enumerate(REGIOES))
    nome = dict(RAIZES)
    return f"""let
    Fonte = fxCsv("dados/pbi/municipio.csv", ","),
    Mun = Table.TransformColumnTypes(
        Table.SelectColumns(Fonte, {{"cd_ibge", "uf", "regiao", "rotulo", "porte", "porte_ordem", "quinto",
            "quinto_ordem"}}, MissingField.UseNull),
        {{{{"cd_ibge", type text}}, {{"uf", type text}}, {{"regiao", type text}}, {{"rotulo", type text}},
         {{"porte", type text}}, {{"porte_ordem", Int64.Type}}, {{"quinto", type text}}, {{"quinto_ordem", Int64.Type}}}},
        "en-US"),
    LadoFonte = fxCsv("dados/pbi/t19_lado.csv", ","),
    Lado = Table.TransformColumnTypes(
        Table.RenameColumns(Table.SelectColumns(LadoFonte, {{"cd_ibge", "lado", "lado_ordem"}}, MissingField.UseNull),
            {{{{"cd_ibge", "cd_lado"}}}}),
        {{{{"cd_lado", type text}}, {{"lado", type text}}, {{"lado_ordem", Int64.Type}}}}, "en-US"),
    UFs = #table(type table [uf_k = text, uf_nome = text, uf_ordem = Int64.Type], {{{linhas_uf}}}),
    Regioes = #table(type table [regiao_k = text, regiao_ordem = Int64.Type], {{{linhas_reg}}}),
    ComLado = Table.Join(Mun, "cd_ibge", Lado, "cd_lado", JoinKind.LeftOuter),
    ComUF = Table.Join(ComLado, "uf", UFs, "uf_k", JoinKind.LeftOuter),
    Base = Table.Join(ComUF, "regiao", Regioes, "regiao_k", JoinKind.LeftOuter),
    // cidades em ordem alfabética pt-BR (acento não manda na ordem: Águas Lindas fica entre os A)
    Nomes = List.Sort(List.Distinct(Base[rotulo]), Comparer.FromCulture("pt-BR", true)),
    OrdemCidade = Table.FromColumns({{Nomes, {{1..List.Count(Nomes)}}}},
        type table [rotulo_k = text, cidade_ordem = Int64.Type]),
    Tudo = Table.Join(Base, "rotulo", OrdemCidade, "rotulo_k", JoinKind.LeftOuter),
    N = Table.RowCount(Tudo),
    Quinto = List.Transform(Tudo[quinto_ordem], each if _ = null then null else Text.From(_) & "º quinto"
        & (if _ = 1 then " (mais pobres)" else if _ = 5 then " (mais ricas)" else "")),
    Raiz = (ordem as number, raiz as text, valores as list, curtos as list, ordens as list) as table =>
        Table.FromColumns(
            {{Tudo[cd_ibge], List.Repeat({{raiz}}, N), List.Repeat({{ordem}}, N), valores, curtos, ordens}},
            type table [CodIBGE = text, Raiz = text, RaizOrdem = Int64.Type, Valor = text, Curto = text,
                        ValorOrdem = Int64.Type]),
    Todas = Table.Combine({{
        Raiz(1, "{nome[1]}", Tudo[regiao], Tudo[regiao], Tudo[regiao_ordem]),
        Raiz(2, "{nome[2]}", Tudo[uf_nome], Tudo[uf], Tudo[uf_ordem]),
        Raiz(3, "{nome[3]}", Tudo[porte], Tudo[porte], Tudo[porte_ordem]),
        Raiz(4, "{nome[4]}", Quinto, Tudo[quinto], Tudo[quinto_ordem]),
        Raiz(5, "{nome[5]}", Tudo[lado], Tudo[lado], Tudo[lado_ordem]),
        Raiz(6, "{nome[6]}", Tudo[rotulo], Tudo[rotulo], Tudo[cidade_ordem])}}),
    ComValor = Table.SelectRows(Todas, each [Valor] <> null and [Valor] <> "" and [ValorOrdem] <> null),
    Caminho = Table.AddColumn(ComValor, "Caminho", each [Raiz] & "{SEPARADOR}" & [Valor], type text),
    Ordem = Table.AddColumn(Caminho, "Ordem", each [RaizOrdem] * 10000 + [ValorOrdem], Int64.Type),
    Final = Table.SelectColumns(Ordem, {{"CodIBGE", "Raiz", "RaizOrdem", "Valor", "Curto", "Caminho", "Ordem"}})
in
    Final"""


TABELAS = [
    tabela(
        "T19 Filtro", "O filtro do recorte da tela 19 (acordeão do VizuFilter, um campo só): uma linha por município × "
                      "grupo (Região, Estado, Tamanho da cidade, Renda, Virou?, Cidade). Sem relação ativa com o "
                      "Município: a medida [T19 · no recorte] aplica E entre os grupos e OU dentro do mesmo grupo.",
        [col("CodIBGE", descricao="Código IBGE do município da linha (relação INATIVA com o Município, ligada só "
             "em [T19 · no recorte]).", oculta=True),
         col("Raiz", descricao="O grupo do filtro: Região, Estado, Tamanho da cidade, Renda (quinto), Virou? ou "
             "Cidade.", oculta=True, ordenar_por="RaizOrdem"),
         col("RaizOrdem", tipo="int", descricao="Ordem do grupo no acordeão (1 = Região … 6 = Cidade); as medidas "
             "leem o grupo por ela.", oculta=True, formato="0"),
         col("Valor", descricao="O valor escolhível dentro do grupo (Nordeste, Minas Gerais, até 10 mil, 1º quinto "
             "(mais pobres), Virou para Flávio, Contagem (MG)…).", oculta=True),
         col("Curto", descricao="Forma curta do valor para o texto do recorte (sigla da UF; o quinto como no "
             "Município).", oculta=True),
         col("Caminho", descricao="Grupo › valor: o campo do VizuFilter em modo caminho (uma raiz por grupo).",
             ordenar_por="Ordem"),
         col("Ordem", tipo="int", descricao="Ordem do caminho no acordeão: grupo × 10.000 + a ordem do valor.",
             oculta=True, formato="0")],
        _m(), renomeada=True),
]

# inativa: só [T19 · no recorte] a liga (USERELATIONSHIP); fora dela a T19 Filtro não filtra nem é filtrada pelo Município
RELACOES = [
    ("T19 Filtro", "CodIBGE", "Município", "CodIBGE", {"inativa": True}),
]
