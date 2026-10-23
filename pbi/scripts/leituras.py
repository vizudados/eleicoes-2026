"""leituras — o texto do cartão "i" de cada tela (Como ler · De onde vêm os números · Para lembrar).

Linguagem de conversa, frases curtas, sem jargão (pedido do Alisson, 23/10/2026: "linguagem humanizada e de fácil
entendimento"). Cada tela pode ter o seu em LEITURAS[código]; sem ele, padrao() monta um a partir do roteiro.
"""

LEITURAS: dict[str, dict] = {}


def padrao(t) -> dict:
    return {"titulo": t.pergunta,
            "blocos": [("Como ler", "A frase grande responde à pergunta da tela. Passe o mouse nos gráficos para ver "
                                    "o detalhe de cada ponto; onde houver filtro, ele muda todas as contas da tela."),
                       ("De onde vêm os números", t.fonte.replace("Fonte: ", "").replace("Fontes: ", "")),
                       ("Para lembrar", "Os percentuais são sobre os votos válidos (sem brancos e nulos), como o TSE "
                                        "divulga. 1º turno de 2026, resultado de 22/10/2026.")]}
