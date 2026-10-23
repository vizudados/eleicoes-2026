"""Tabela da tela 20 · Escola (dono: tela 20): os 112 locais de votação de Contagem (MG) no 1º turno de 2026, um por
linha, com os votos de 2026 e os de 2022 e 2018 do mesmo local (zona + número). Lê dados/pbi/t20_locais.csv
(pipeline/exportar_t20.py). Sem relação: a tela lê só esta tabela (o mapa, a ficha, a lista e a segmentação de escola);
a contagem de 2022 sobre os locais do próprio ano (27 de 111) vem da Local Contagem."""

from gerar_modelo import col, tabela_csv


def _votos(sigla, ano, quem):
    return col(f"{sigla}_{ano}", f"{quem}{ano}", tipo="int", oculta=True,
               descricao=f"{'Votos do PT' if quem == 'VotosPT' else 'Votos do adversário principal' if quem == 'VotosAdv' else 'Votos válidos'} "
                         f"no local em {ano}" + ("" if ano == 2026 else " (soma das seções do mesmo zona + número; vazio "
                                                                    "quando o local não existia)") + ".")


TABELAS = [
    tabela_csv(
        "T20 Local", "Os 112 locais de votação de Contagem (MG) em 2026, com os votos de presidente (1º turno) de 2026, "
                     "2022 e 2018 do mesmo local e a posição no mapa da tela 20. Nome legível no lugar das maiúsculas "
                     "do TSE; o mesmo prédio com dois números ganha o número no nome.",
        "dados/pbi/t20_locais.csv",
        [col("id", "Id", tipo="int", descricao="Identificador do local (1…112).", oculta=True, formato="0"),
         col("local", "Local", descricao="Nome do local de votação (escola), legível; único.", ordenar_por="Id"),
         col("nome_tse", "Nome TSE", descricao="Nome como o TSE escreve em 2026.", oculta=True),
         col("bairro", "Bairro", descricao="Bairro do local (cadastro do TSE de 2022)."),
         col("endereco", "Endereço", descricao="Endereço do local.", oculta=True),
         col("zona", "Zona", tipo="int", descricao="Zona eleitoral.", oculta=True, formato="0"),
         col("numero", "Número", tipo="int", descricao="Número do local na zona.", oculta=True, formato="0"),
         col("secoes", "Seções", tipo="int", descricao="Seções no local em 2026.", oculta=True),
         _votos("pt", 2026, "VotosPT"), _votos("adv", 2026, "VotosAdv"), _votos("validos", 2026, "Validos"),
         _votos("pt", 2022, "VotosPT"), _votos("adv", 2022, "VotosAdv"), _votos("validos", 2022, "Validos"),
         _votos("pt", 2018, "VotosPT"), _votos("adv", 2018, "VotosAdv"), _votos("validos", 2018, "Validos"),
         col("px", "PX", tipo="number", descricao="Posição horizontal no mapa da tela (% da largura).", oculta=True,
             formato="0.00"),
         col("py", "PY", tipo="number", descricao="Posição vertical no mapa da tela (% da altura).", oculta=True,
             formato="0.00")],
        oculta=False),
]
