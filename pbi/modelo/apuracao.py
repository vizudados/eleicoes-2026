"""Apuração ao vivo do 2º turno: o que o coletor (apuracao/coletar.py, no GitHub Actions) grava em dados/apuracao a
cada coleta. pPastaApuracao troca para dados/apuracao/ensaio-1turno, o 1º turno encerrado, para conferir as contas."""

from gerar_modelo import col, tabela

CAMPOS_UF = [
    ("uf", "UF", "text", "Sigla (BR = Brasil; ZZ = exterior)."),
    ("atualizado_tse", "AtualizadoTSE", "text", "Hora em que o TSE totalizou a linha (Brasília)."),
    ("secoes_pct", "SecoesPct", "number", "% de seções totalizadas publicado pelo TSE (pst)."),
    ("eleitorado", "Eleitorado", "int", "Eleitorado total (te)."),
    ("comparecimento", "Comparecimento", "int", "Votaram, nas seções totalizadas (c)."),
    ("abstencao", "Abstencao", "int", "Faltaram, nas seções totalizadas (a)."),
    ("abstencao_pct", "AbstencaoPct", "number", "% de abstenção publicado pelo TSE (pa)."),
    ("brancos", "Brancos", "int", "Votos em branco (vb)."),
    ("nulos", "Nulos", "int", "Votos nulos, inclusive anulados (tvn)."),
    ("validos", "Validos", "int", "Votos válidos (vv)."),
    ("lula_votos", "LulaVotos", "int", "Votos de Lula (13)."),
    ("lula_pct", "LulaPct", "number", "% dos válidos de Lula publicado pelo TSE."),
    ("flavio_votos", "FlavioVotos", "int", "Votos de Flávio Bolsonaro (22)."),
    ("flavio_pct", "FlavioPct", "number", "% dos válidos de Flávio publicado pelo TSE."),
    ("lider", "Lider", "text", "Lula, Flávio ou — (empate ou antes da apuração)."),
    ("diferenca_votos", "DiferencaVotos", "int", "Diferença absoluta de votos."),
    ("secoes_total", "SecoesTotal", "int", "Seções eleitorais (ts)."),
    ("secoes_totalizadas", "SecoesTotalizadas", "int", "Seções totalizadas (st)."),
    ("eleitorado_apurado", "EleitoradoApurado", "int", "Eleitorado das seções totalizadas (est)."),
]
CAMPOS_HIST = [
    ("coletado_em", "ColetadoEm", "text", "Hora da coleta que gravou a linha (Brasília)."),
    ("atualizado_tse", "AtualizadoTSE", "text", "Hora de totalização do TSE; uma linha por hora nova."),
    ("secoes_pct", "SecoesPct", "number", "% de seções totalizadas no Brasil."),
    ("lula_votos", "LulaVotos", "int", "Votos de Lula no Brasil."),
    ("lula_pct", "LulaPct", "number", "% dos válidos de Lula publicado pelo TSE."),
    ("flavio_votos", "FlavioVotos", "int", "Votos de Flávio no Brasil."),
    ("flavio_pct", "FlavioPct", "number", "% dos válidos de Flávio publicado pelo TSE."),
    ("brancos", "Brancos", "int", "Votos em branco."),
    ("nulos", "Nulos", "int", "Votos nulos."),
    ("abstencao", "Abstencao", "int", "Abstenção."),
    ("validos", "Validos", "int", "Votos válidos."),
    ("secoes_totalizadas", "SecoesTotalizadas", "int", "Seções totalizadas."),
    ("secoes_total", "SecoesTotal", "int", "Seções eleitorais."),
]
TIPO_M = {"text": "type text", "number": "type number", "int": "Int64.Type"}
HORAS = {"AtualizadoTSE", "ColetadoEm"}


def colunas(campos):
    saida = []
    for _, nome, tipo, descricao in campos:
        t = "datetime" if nome in HORAS else tipo
        saida.append(col(nome, tipo=t, descricao=descricao, oculta=nome != "UF"))
    return saida


def m_arquivo(arquivo, campos, filtro=None):
    tipos = ", ".join(f'{{"{c}", {TIPO_M[t]}}}' for c, _, t, _ in campos)
    nomes = ", ".join(f'{{"{c}", "{n}"}}' for c, n, _, _ in campos)
    horas = ", ".join(f'{{"{n}", fxHora, type nullable datetime}}' for _, n, _, _ in campos if n in HORAS)
    linhas = ["let",
              f'    Fonte = fxCsv(pPastaApuracao & "/{arquivo}", ","),',
              f"    Colunas = Table.SelectColumns(Fonte, {{{', '.join(chr(34) + c + chr(34) for c, _, _, _ in campos)}}}, "
              "MissingField.UseNull),",
              f'    Tipos = Table.TransformColumnTypes(Colunas, {{{tipos}}}, "en-US"),',
              f"    Nomes = Table.RenameColumns(Tipos, {{{nomes}}}),",
              f"    Horas = Table.TransformColumns(Nomes, {{{horas}}})"]
    fim = "Horas"
    if filtro:
        linhas[-1] += ","
        linhas.append(f"    Filtro = Table.SelectRows(Horas, each {filtro})")
        fim = "Filtro"
    return "\n".join(linhas + ["in", f"    {fim}"])


TABELAS = [
    tabela("Apuração Brasil", "A linha do Brasil (BR) da última coleta, como o TSE totaliza (não é a soma das UFs, "
                              "que o TSE atualiza em horas diferentes).",
           colunas(CAMPOS_UF), m_arquivo("ufs.csv", CAMPOS_UF, '[UF] = "BR"'), oculta=True),
    tabela("Apuração UF", "Uma linha por UF e o exterior (ZZ) na última coleta. Liga com a dimensão UF.",
           colunas(CAMPOS_UF), m_arquivo("ufs.csv", CAMPOS_UF, '[UF] <> "BR"'), oculta=True),
    tabela("Apuração histórico", "A curva da noite no Brasil: uma linha por nova hora de totalização do TSE "
                                 "(historico.csv); antes da primeira divulgação, só o cabeçalho.",
           colunas(CAMPOS_HIST), m_arquivo("historico.csv", CAMPOS_HIST), oculta=True),
    tabela("Apuração status", "O estado da apuração na última coleta (ultimo.json): eleição, turno, fase, horas e "
                              "as UFs que faltaram na coleta.",
           [col("Eleicao", tipo="int", descricao="Código da eleição no TSE (6257 = 1º turno; 6258 = 2º).", formato="0"),
            col("Turno", tipo="int", descricao="Turno (1 ou 2).", formato="0"),
            col("Status", descricao="aguardando · apurando · definido (o TSE marcou o eleito) · encerrada (100%)."),
            col("AtualizadoTSE", tipo="datetime", descricao="Hora de totalização do Brasil no TSE."),
            col("ColetadoEm", tipo="datetime", descricao="Hora da coleta (Brasília)."),
            col("Fonte", descricao="Fonte declarada pelo coletor."),
            col("Faltaram", descricao="UFs cujo arquivo não veio na coleta (vazio = nenhuma).")],
           """let
    Json = fxJson(pPastaApuracao & "/ultimo.json"),
    Linha = #table(
        type table [Eleicao = Int64.Type, Turno = Int64.Type, Status = text, AtualizadoTSE = nullable datetime,
                    ColetadoEm = nullable datetime, Fonte = text, Faltaram = text],
        {{Json[eleicao], Json[turno], Json[status], fxHora(Json[atualizado_tse]), fxHora(Json[coletado_em]),
          Json[fonte], Text.Combine(List.Transform(Json[faltaram], Text.From), ", ")}}
    )
in
    Linha""", oculta=True),
]

RELACOES = [("Apuração UF", "UF", "UF", "UF")]
