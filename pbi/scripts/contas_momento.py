"""Adaptador restrito de T01; mantém as mesmas medidas e os mesmos grãos dos tooltips."""
from desenho_t01_t06_comum import Gravador
from momento_eleicao import segundo, soma_uf


class ContasResultado(Gravador):
    def conta(self, nome, descricao, expressao, formato='#,0', oraculo=None):
        fontes = {
            'T01 · válidos': ('Validos', 2026), 'T01 · válidos 2022': ('Validos', 2022),
            'T01 · Lula votos': ('VotosPT', 2026), 'T01 · Flávio votos': ('VotosAdversario', 2026),
            'T01 · PT 2022 votos': ('VotosPT', 2022), 'T01 · PL 2022 votos': ('VotosAdversario', 2022),
        }
        if nome in fontes:
            expressao = segundo(expressao, soma_uf(*fontes[nome]))
        elif nome == 'T01 · votos do candidato':
            post = """VAR _n = CALCULATE ( SELECTEDVALUE ( 'Candidato UF'[Número] ), 'Candidato UF'[Ano] = 2026 )
RETURN SWITCH ( _n,
    13, CALCULATE ( SUM ( 'UF segundo turno'[VotosPT] ), 'UF segundo turno'[Ano] = 2026 ),
    22, CALCULATE ( SUM ( 'UF segundo turno'[VotosAdversario] ), 'UF segundo turno'[Ano] = 2026 ),
    BLANK () )"""
            expressao = segundo(expressao, post)
        elif "'Município ano'" in expressao:
            # T01 só tem pontos de 2022 e 2026; _a vem do ponto (ano × candidato).
            expressao = segundo(expressao, expressao.replace("'Município ano'", "'Município segundo turno'"))
        return super().conta(nome, descricao.replace('1º turno', 'turno escolhido'), expressao, formato,
                             ('Pré: ' + oraculo) if oraculo else None)
