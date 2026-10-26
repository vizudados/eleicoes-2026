"""Segundo turno municipal (2022/2026) e totalizações por UF, somente volumes observados.

Publicar os dois CSV antes de gerar o modelo. Município segundo turno liga a Município e Ano;
UF é alcançada por Município → UF, sem um segundo caminho ativo. UF segundo turno liga a UF e Ano.
"""
from gerar_modelo import col, tabela_csv


def campos_voto():
    return [col('ano', 'Ano', tipo='int', oculta=True, formato='0', descricao='Ano, somente segundo turno.'),
            *[col(origem, nome, tipo='int', oculta=True, descricao=desc) for origem, nome, desc in [
                ('pt', 'VotosPT', 'Votos de Lula.'),
                ('adv', 'VotosAdversario', 'Votos de Flávio em 2026 e Jair Bolsonaro em 2022.'),
                ('demais', 'VotosDemais', 'Demais candidatos; zero no segundo turno.'),
                ('validos', 'Validos', 'Votos válidos.'), ('aptos', 'Aptos', 'Eleitores aptos.'),
                ('comparecimento', 'Comparecimento', 'Comparecimento registrado pelo TSE.'),
                ('abstencoes', 'Abstencoes', 'Abstenções registradas pelo TSE.'),
                ('brancos', 'Brancos', 'Votos brancos.'), ('nulos', 'Nulos', 'Votos nulos.')]]]


TABELAS = [
    tabela_csv('Município segundo turno',
               'Segundo turno por município, 2022 e 2026, sem exterior. Município ausente em 2022 permanece ausente; '
               'não equivale a zero. Fonte: TSE, exportação validada por pipeline/exportar_2turno.py.',
               'dados/pbi/municipio_2turno.csv',
               [col('cd_ibge', 'CodIBGE', oculta=True, descricao='Código IBGE, chave da dimensão Município.'),
                *campos_voto()], oculta=True),
    tabela_csv('UF segundo turno',
               'Segundo turno por UF, 2022 e 2026, com exterior ZZ. Os totais nacionais incluem o exterior; '
               'as análises municipais das telas T27 e T28 não incluem.',
               'dados/pbi/uf_2turno.csv',
               [col('uf', 'UF', oculta=True, descricao='Sigla da UF ou ZZ, exterior.'), *campos_voto()], oculta=True),
]

RELACOES = [
    ('Município segundo turno', 'CodIBGE', 'Município', 'CodIBGE'),
    ('Município segundo turno', 'Ano', 'Ano', 'Ano'),
    ('UF segundo turno', 'UF', 'UF', 'UF'),
    ('UF segundo turno', 'Ano', 'Ano', 'Ano'),
]
