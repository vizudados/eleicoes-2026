"""Parâmetros da tela 22 · Simulador (dono: tela 22): três tabelas desconectadas de M estático, uma por controle. A
tela as lê com SELECTEDVALUE (valor padrão quando nada está marcado) e as escolhe por segmentações de botões invisíveis
sobre as réguas desenhadas em HTML (um botão por valor).

  T22 Para Lula       0, 2, …, 100   % dos eleitores dos outros candidatos que votarem que escolhem Lula (padrão 50)
  T22 Não votam       0, 5, …, 50    % dos 9,32 mi que não escolhem ninguém: branco, nulo ou falta (padrão 0)
  T22 Comparecimento  −5, −4, …, +5  pontos de comparecimento a mais (ou a menos) sobre os aptos de cada UF, metade
                                      para cada candidato (padrão 0)
"""

from gerar_modelo import col, tabela


def _serie(nome, inicio, quantos, passo, descricao):
    m = f"""let
    Valores = List.Numbers({inicio}, {quantos}, {passo}),
    Tabela = Table.FromList(Valores, Splitter.SplitByNothing(), {{"{nome}"}}),
    Tipos = Table.TransformColumnTypes(Tabela, {{{{"{nome}", Int64.Type}}}})
in
    Tipos"""
    return col(nome, tipo="int", descricao=descricao, formato="0"), m


_PARA_LULA = _serie("Para Lula", 0, 51, 2, "Dos eleitores dos outros candidatos que forem votar, quantos % escolhem "
                                           "Lula (o resto vai para Flávio).")
_NAO_VOTAM = _serie("Não votam", 0, 11, 5, "Quantos % dos votos dos outros candidatos não vão para ninguém (branco, "
                                           "nulo ou falta).")
_COMPARECIMENTO = _serie("Comparecimento", -5, 11, 1, "Pontos de comparecimento a mais (ou a menos) sobre os aptos "
                                                       "de cada UF; os votos novos se dividem ao meio.")

TABELAS = [
    tabela("T22 Para Lula", "Parâmetro do simulador (tela 22): % dos eleitores dos outros candidatos que votarem e "
                            "escolhem Lula, de 0 a 100 em passos de 2. Sem marca, a conta usa 50.",
           [_PARA_LULA[0]], _PARA_LULA[1]),
    tabela("T22 Não votam", "Parâmetro do simulador (tela 22): % dos votos dos outros candidatos que não vão para "
                            "ninguém, de 0 a 50 em passos de 5. Sem marca, a conta usa 0.",
           [_NAO_VOTAM[0]], _NAO_VOTAM[1]),
    tabela("T22 Comparecimento", "Parâmetro do simulador (tela 22): mudança no comparecimento, de −5 a +5 pontos dos "
                                 "aptos de cada UF; os votos novos se dividem ao meio entre Lula e Flávio. Sem marca, 0.",
           [_COMPARECIMENTO[0]], _COMPARECIMENTO[1]),
]
