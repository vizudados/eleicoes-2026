"""Tabela dos períodos em volta dos dois debates do 2º turno (Band em 18/10 e Globo em 23/10): o filtro "Período" da
casca, um só, compartilhado pelas telas Buscas (T08), Redes (T09) e 2º turno (T17). Aprovada pelo dono em 23/10/2026.

Sem escolha, as três telas mostram o que já mostravam (o 2º turno inteiro, de 05/10 em diante). Os quatro períodos:

  1 · Antes da Band    05 a 17/10
  2 · Depois da Band   18 a 20/10 (a noite do debate e os dois dias seguintes)
  3 · Antes da Globo   21 e 22/10
  4 · Depois da Globo  23 e 24/10 (até a véspera da eleição)

Regra de corte de cada tela (nas medidas): em Buscas e Redes o dia do debate conta como "depois" (o pico é na própria
noite); nas pesquisas, só entra a pesquisa com o campo inteiro dentro do período (a que atravessa o dia do debate fica
fora, como na T07).

Tabela desconectada, de propósito: o VizuFilter filtra 'Período'[Período] e as medidas leem a escolha
([Período · escolhido], pbi/dax/_Período); nenhuma tabela de fatos é filtrada pela relação. Sem CSV (não há push).
"""

from gerar_modelo import col, tabela

PERIODOS = [
    # ordem, rótulo do filtro, nome curto, início, fim, debate, lado, dia do debate
    (1, "Antes da Band · 05 a 17/10", "Antes da Band", (2026, 10, 5), (2026, 10, 17), "Band", "antes", (2026, 10, 18)),
    (2, "Depois da Band · 18 a 20/10", "Depois da Band", (2026, 10, 18), (2026, 10, 20), "Band", "depois",
     (2026, 10, 18)),
    (3, "Antes da Globo · 21 e 22/10", "Antes da Globo", (2026, 10, 21), (2026, 10, 22), "Globo", "antes",
     (2026, 10, 23)),
    (4, "Depois da Globo · 23 e 24/10", "Depois da Globo", (2026, 10, 23), (2026, 10, 24), "Globo", "depois",
     (2026, 10, 23)),
]


def _d(t):
    return f"#date({t[0]}, {t[1]}, {t[2]})"


def _m() -> str:
    linhas = ",\n            ".join(
        f'{{{o}, "{r}", "{n}", {_d(i)}, {_d(f)}, "{deb}", "{lado}", {_d(dd)}}}'
        for o, r, n, i, f, deb, lado, dd in PERIODOS)
    return f"""let
    Fonte = #table(
        type table [ordem = Int64.Type, periodo = text, nome = text, inicio = date, fim = date, debate = text,
            lado = text, data_debate = date],
        {{
            {linhas}
        }})
in
    Fonte"""


TABELAS = [
    tabela(
        "Período", "Os quatro períodos em volta dos debates do 2º turno (Band 18/10, Globo 23/10) para o filtro "
                   "Período das telas Buscas, Redes e 2º turno. Desconectada: as medidas leem a escolha.",
        [col("ordem", "Ordem", tipo="int", descricao="Ordem do período (1 a 4).", oculta=True, formato="0"),
         col("periodo", "Período", descricao="Rótulo do filtro: o nome e as datas ('Antes da Band · 05 a 17/10').",
             ordenar_por="Ordem"),
         col("nome", "Nome", descricao="Nome curto ('Antes da Band').", oculta=True),
         col("inicio", "Início", tipo="date", descricao="Primeiro dia do período.", oculta=True),
         col("fim", "Fim", tipo="date", descricao="Último dia do período.", oculta=True),
         col("debate", "Debate", descricao="O debate de referência: Band ou Globo.", oculta=True),
         col("lado", "Lado", descricao="antes ou depois do debate.", oculta=True),
         col("data_debate", "Data do debate", tipo="date", descricao="Dia do debate de referência.", oculta=True)],
        _m()),
]
