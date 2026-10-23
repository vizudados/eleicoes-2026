"""Tabelas da tela T25 · Quem falta (a 07 na ordem do roteiro, logo depois da 06 · Ausência): onde e quem falta, com
filtro cruzado entre o mapa dos municípios, os anos e as faixas de idade (pedido do Alisson, 23/10/2026).

  T25 Faixa               as sete faixas de idade das telas 06 e 07, na ordem da tela; é o grão do bloco de idade e
                          o filtro que o clique numa faixa manda para o mapa e para os anos
  T25 Abstenção faixa     município × faixa × ano (1º turno, 2014–2026): aptos e abstenções, do perfil do eleitor do
                          TSE (membros por UF de perfil_comparecimento_abstencao_<ano>.zip) —
                          pipeline/extrair_abstencao_municipio.py e pipeline/exportar_pbi.py › abstencao_faixa()
  T25 Abstenção exterior  as mesmas contas do exterior (ZZ), por faixa × ano: sem município, só entra no total do
                          Brasil (sem filtro de UF nem município marcado), para o Brasil por idade bater com o _BRASIL
                          do TSE e com a tela 06 (que mostra o total oficial, com o exterior)

Relações (todas muitos-para-um, filtro numa direção, da dimensão para o fato):
  T25 Abstenção faixa[CodIBGE]    → Município[CodIBGE]   o filtro de UF da casca (UF → Município) e o clique num ponto
                                                         do mapa (Município) chegam ao fato: os anos e as faixas
                                                         passam a mostrar a UF ou o município
  T25 Abstenção faixa[Ano]        → Ano[Ano]             o clique num ano (o grão do bloco de anos é Ano[Ano]) filtra
                                                         o fato: o mapa e as faixas mostram aquele ano
  T25 Abstenção faixa[FaixaOrdem] → T25 Faixa[Ordem]     o clique numa faixa filtra o fato: o mapa mostra a abstenção
                                                         daquela faixa por município e os anos, a série da faixa
  T25 Abstenção exterior[Ano]        → Ano[Ano]           idem, para a parcela do exterior no total do Brasil
  T25 Abstenção exterior[FaixaOrdem] → T25 Faixa[Ordem]
Sem relação com 'Município ano' nem com 'Abstenção perfil': sem faixa marcada, as contas da tela leem 'Município ano'
(e 'Comparecimento ano' no Brasil) como a tela 06; com faixa, leem estas tabelas. A seleção de um visual não volta para
ele mesmo (o mapa não se filtra pelo próprio clique), e a dimensão 'T25 Faixa' só filtra o fato desta tela.
"""

from gerar_modelo import col, tabela, tabela_csv

# (faixa, ordem, rótulo curto, voto) — as faixas do TSE agrupadas como na tela 06 (desenho_t06.py) e no extrator
FAIXAS = [
    ("16 e 17 anos", 1, "16–17", "facultativo"),
    ("18 a 24 anos", 2, "18–24", "obrigatório"),
    ("25 a 34 anos", 3, "25–34", "obrigatório"),
    ("35 a 44 anos", 4, "35–44", "obrigatório"),
    ("45 a 59 anos", 5, "45–59", "obrigatório"),
    ("60 a 69 anos", 6, "60–69", "obrigatório"),
    ("70 anos ou mais", 7, "70+", "facultativo"),
]


def _m_faixa():
    corpo = ",\n        ".join(f'{{"{f}", {o}, "{c}", "{v}"}}' for f, o, c, v in FAIXAS)
    return f"""let
    Faixas = #table(
        type table [Faixa = text, Ordem = Int64.Type, Curta = text, Voto = text],
        {{
        {corpo}
        }}
    )
in
    Faixas"""


def _colunas_fato():
    return [col("ano", "Ano", tipo="int", descricao="Ano da eleição (2014, 2018, 2022, 2026).", oculta=True,
                formato="0"),
            col("uf", "UF", descricao="Sigla da UF do município (ZZ = exterior).", oculta=True),
            col("cd_ibge", "CodIBGE", descricao="Código IBGE do município (vazio no exterior).", oculta=True),
            col("faixa_ordem", "FaixaOrdem", tipo="int", descricao="Ordem da faixa de idade (1 = 16 e 17 anos … 7 = "
                "70 anos ou mais); liga com T25 Faixa.", oculta=True, formato="0"),
            col("aptos", "Aptos", tipo="int", descricao="Eleitores aptos na faixa.", oculta=True),
            col("abstencoes", "Abstencoes", tipo="int", descricao="Eleitores da faixa que faltaram.", oculta=True)]


TABELAS = [
    tabela("T25 Faixa", "As sete faixas de idade das telas 06 e 07, na ordem da tela, com o rótulo curto e se o voto "
                        "é obrigatório ou facultativo (16 e 17 anos e 70 ou mais). Grão do bloco de idade da tela 07; "
                        "o clique numa faixa filtra o mapa e os anos.",
           [col("Faixa", descricao="Faixa de idade (ex.: 18 a 24 anos).", ordenar_por="Ordem"),
            col("Ordem", tipo="int", descricao="Ordem da faixa, da mais nova para a mais velha.", oculta=True,
                formato="0"),
            col("Curta", descricao="Rótulo curto (ex.: 18–24).", oculta=True, ordenar_por="Ordem"),
            col("Voto", descricao="obrigatório ou facultativo (16 e 17 anos e 70 ou mais).", oculta=True)],
           _m_faixa()),
    tabela_csv(
        "T25 Abstenção faixa", "Município × faixa de idade × eleição (1º turno, 2014–2026): eleitores aptos e quantos "
                               "faltaram, do perfil do eleitor do TSE (somado por município e faixa). Sem o exterior.",
        "dados/pbi/abstencao_faixa_municipio.csv", _colunas_fato(), oculta=True, filtro='[UF] <> "ZZ"'),
    tabela_csv(
        "T25 Abstenção exterior", "Exterior (ZZ) × faixa de idade × eleição (1º turno, 2014–2026): aptos e "
                                  "abstenções, que só entram no total do Brasil (sem filtro de UF nem município).",
        "dados/pbi/abstencao_faixa_municipio.csv", _colunas_fato(), oculta=True, filtro='[UF] = "ZZ"'),
]

RELACOES = [
    ("T25 Abstenção faixa", "CodIBGE", "Município", "CodIBGE"),
    ("T25 Abstenção faixa", "Ano", "Ano", "Ano"),
    ("T25 Abstenção faixa", "FaixaOrdem", "T25 Faixa", "Ordem"),
    ("T25 Abstenção exterior", "Ano", "Ano", "Ano"),
    ("T25 Abstenção exterior", "FaixaOrdem", "T25 Faixa", "Ordem"),
]
