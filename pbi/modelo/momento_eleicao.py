"""Duas escolhas locais, desconectadas; não depende de publicar CSV."""
from gerar_modelo import col

TABELAS = [{
    'nome': 'Momento eleição',
    'descricao': 'Antes/depois da eleição de 2026. Desconectada; medidas leem a escolha. Sem seleção = Pós.',
    'colunas': [col('Momento', ordenar_por='Ordem'), col('Ordem', tipo='int', oculta=True)],
    'dax': 'DATATABLE ( "Momento", STRING, "Ordem", INTEGER, '
           '{ { "Pré Eleições 2026", 1 }, { "Pós Eleições 2026", 2 } } )',
}]
