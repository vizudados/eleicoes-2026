"""História presidencial do PT, 1989–2026. Sem relação com Ano (que começa em 2006).

Brasil inclui ZZ uma vez. Mapa usa o turno decisivo e todos os candidatos para identificar o vencedor.
Publicar t29_mapa.csv antes do ciclo completo da main. Fontes históricas têm versões divergentes: ver método.
"""
from gerar_modelo import col, tabela_csv


def campos():
    return [col('ano', 'Ano', tipo='int', formato='0', oculta=True),
            col('turno', 'Turno', tipo='int', formato='0', oculta=True),
            col('uf', 'UF', oculta=True),
            col('candidato_pt', 'Candidato PT', oculta=True),
            col('adversario', 'Adversário', oculta=True),
            col('partido_adversario', 'Partido adversário', oculta=True),
            *[col(origem, nome, tipo='int', formato='#,0', oculta=True) for origem, nome in [
                ('votos_pt', 'VotosPT'), ('votos_adv', 'VotosAdversario'), ('validos', 'Validos'),
                ('comparecimento', 'Comparecimento'), ('aptos', 'Aptos')]]]


TABELAS = [
    tabela_csv('PT histórico UF', '18 pares de ano/turno, 27 UFs e ZZ. Fonte TSE, versões documentadas.',
               'dados/pbi/pt_historico_uf.csv', campos(), oculta=True),
    tabela_csv('PT histórico Brasil', 'Resultado nacional com exterior; não somar turnos ou eleições.',
               'dados/pbi/pt_historico_brasil.csv', campos(), oculta=True),
    tabela_csv('PT histórico mapa', 'Turno decisivo de cada eleição. Vencedor e segundo colocado efetivos de todas '
               'as candidaturas; 1998/CE = Ciro, PPS. Fonte: pipeline/exportar_t29.py.',
               'dados/pbi/t29_mapa.csv', [*campos(),
                   col('vencedor', 'Vencedor', oculta=True), col('partido_vencedor', 'Partido vencedor', oculta=True),
                   col('segundo', 'Segundo colocado', oculta=True), col('grupo_vencedor', 'Grupo vencedor', oculta=True),
                   *[col(a, b, tipo='int', formato='#,0', oculta=True) for a, b in [
                       ('votos_vencedor', 'Votos vencedor'), ('votos_segundo', 'Votos segundo'),
                       ('vantagem_vencedor', 'Vantagem vencedor')]]], oculta=True),
]

RELACOES = [('PT histórico UF', 'UF', 'UF', 'UF'), ('PT histórico mapa', 'UF', 'UF', 'UF')]
