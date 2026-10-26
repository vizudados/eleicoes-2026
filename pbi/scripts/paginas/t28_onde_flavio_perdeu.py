"""27 · Onde Flávio perdeu — mudança de vantagem em votos, viradas e Jair no segundo turno de 2022.

Mesma gramática e mesmas contas da T27, com sinal e unidade explícitos. O ranking mostra redução da vantagem,
não queda absoluta de votos. Empates não são viradas; município sem 2022 nunca vira zero.
"""
from paginas import _resultado_segundo_turno as comum

def declarar(ctx):
    return comum.declarar('T28',ctx)
