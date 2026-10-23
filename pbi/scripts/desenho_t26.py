# -*- coding: utf-8 -*-
"""desenho_t26 — tela 20 · Debate na Globo (código T26): o último debate mexeu em alguma coisa? Dono: agente da T26.

    python -I -X utf8 pbi/scripts/desenho_t26.py        # grava pbi/dax/T26 Debate na Globo/{Contas,Desenho}/*.dax

A tela fica pronta ANTES dos números e se preenche quando dados/pbi/debate_globo.csv muda no repositório (tabela
'T26 Debate Globo', pbi/modelo/t26_debate_globo.py). Um estado por métrica, nunca número inventado: vazio = "aguardando",
com a hora e a fonte esperadas; com valor = o número (contador); nao_divulgado = "não divulgado". A situação do debate
(marcado, no_ar, realizado, adiado, cancelado) e a presença de cada um (confirmada, a_confirmar, ausente) também vêm
do arquivo: cancelar o debate ou registrar uma ausência não exige mexer no relatório.

  T26_Ficha_Html      a ficha da noite: o selo da situação, a hora, onde passa, a mediação, a manchete (responde à
                      pergunta com o que já se sabe) (as regras em blocos e a checagem saíram da tela em 23/10/2026)
  T26_Palco_Html      os dois púlpitos em traço (grão 'T26 Debate Globo'[Chave], só as linhas de presença): o nome, o
                      púlpito na cor do candidato (vazio e tracejado se ele faltar) e a situação; dossiê ttT26Presenca
  T26_Noite_Html      fundo da faixa de baixo: o título, a fita do tempo da sexta 21h20 ao domingo da eleição
  T26_Noite_Cartoes   os cinco cartões da noite (grão 'T26 Debate Globo'[Cartão]): buscas, audiência, streaming, redes e
                      pesquisas, cada um pendurado na fita, com a régua do debate da Band (18/10) embaixo; dossiê
                      ttT26Cartao (o que mede, quando e de onde, a ressalva e a Band em detalhe)

Contas (pasta T26 Debate na Globo\\Contas): a linha pela Chave; a situação efetiva de cada cartão; a régua da Band nas
tabelas Debate (audiência e YouTube), 'Trends tempo' (pico da noite, consulta H2) e Monitoramento (Bites); as pesquisas
na tabela Pesquisa com a regra da tela 08: antes = campo inteiro entre os dois debates (19 a 22/10), depois = campo que
começa depois do dia do debate; quem atravessa o dia fica fora das médias.
Oráculo (pandas sobre dados/pbi, 23/10/2026): antes 5 pesquisas, Lula 45,98 e Flávio 48,02; depois 0; atravessam 0; Band
15 pontos (consolidado), 5.385.394 aparelhos, buscas 100 × 91, redes 25,5 mi × 5,0 mi.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from desenho_t01_t06_comum import Gravador  # noqa: E402

G = Gravador("T26 Debate na Globo")
T = "'T26 Debate Globo'"
TT = "'Trends tempo'"


def esc(v: str) -> str:
    return (f'SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {v}, "&", "&amp;" ), "<", "&lt;" ), '
            f'">", "&gt;" ), """", "&quot;" ), "\'", "&#39;" )')


def px(v: str) -> str:
    return f'FORMAT ( {v}, "0.0##", "en-US" )'


def parte(v: str, casas_mi: int = 2) -> str:
    """Só o número de num_humano (25.500.000 → "25,5"); a unidade sai em sufixo(). casas_mi: casas de 1 a 10 mi."""
    fmt = "0." + "0" * casas_mi
    return (f'SWITCH ( TRUE (), ABS ( {v} ) >= 10000000, FORMAT ( {v} / 1000000, "0.0" ), '
            f'ABS ( {v} ) >= 1000000, FORMAT ( {v} / 1000000, "{fmt}" ), '
            f'ABS ( {v} ) >= 1000, FORMAT ( {v} / 1000, "#,0" ), FORMAT ( {v}, "#,0" ) )')


def sufixo(v: str) -> str:
    return f'SWITCH ( TRUE (), ABS ( {v} ) >= 1000000, " mi", ABS ( {v} ) >= 1000, " mil", "" )'


def num_humano(v: str) -> str:
    """aparelhos, interações: 5.385.394 → "5,39 mi"; 25.500.000 → "25,5 mi"; 950.000 → "950 mil"."""
    return (f'SWITCH ( TRUE (), ABS ( {v} ) >= 10000000, FORMAT ( {v} / 1000000, "0.0" ) & " mi", '
            f'ABS ( {v} ) >= 1000000, FORMAT ( {v} / 1000000, "0.00" ) & " mi", '
            f'ABS ( {v} ) >= 1000, FORMAT ( {v} / 1000, "#,0" ) & " mil", FORMAT ( {v}, "#,0" ) )')


def num1(v: str) -> str:
    """Uma casa só quando há fração: 15 → "15", 13,39 → "13,4" (o "0.#" do FORMAT deixa a vírgula sobrando)."""
    return f'IF ( {v} = INT ( {v} ), FORMAT ( {v}, "0" ), FORMAT ( {v}, "0.0" ) )'


def linha(chave: str, coluna: str, agg: str = "MAX") -> str:
    return f'CALCULATE ( {agg} ( {T}[{coluna}] ), REMOVEFILTERS ( {T} ), {T}[Chave] = "{chave}" )'


def moldura(w: int, h: int) -> str:
    """Retângulo à mão, tracejado (o lugar do número que ainda não chegou), como literal de texto DAX."""
    d = (f"M4 5 C {w * .3:.0f} 2, {w * .7:.0f} 4, {w - 4} 5 C {w - 2} {h * .4:.0f}, {w - 5} {h * .7:.0f}, {w - 4} {h - 4} "
         f"C {w * .65:.0f} {h - 1}, {w * .3:.0f} {h - 3}, 5 {h - 5} C 3 {h * .6:.0f}, 6 {h * .3:.0f}, 4 5 Z")
    return (f"<svg class='mold' width='{w}' height='{h}' viewBox='0 0 {w} {h}'><path d='{d}' "
            f"filter='url(#rbu)'/></svg>")


# ------------------------------------------------------------------------------------------------ contas: a linha
LINHA_COLS = [("rótulo", "Rótulo"), ("medida", "Medida"), ("texto", "Texto"), ("unidade", "Unidade"),
              ("esperado", "Esperado"), ("fonte esperada", "Fonte esperada"), ("fonte", "Fonte"),
              ("atualizado", "Atualizado"), ("observação", "Observação"), ("candidato", "Candidato"),
              ("grupo", "Grupo"), ("chave", "Chave"), ("situação", "Situação")]
for nome, coluna in LINHA_COLS:
    G.conta(f"T26 · linha · {nome}",
            f"Coluna {coluna} da linha do contexto ('T26 Debate Globo'); com mais de uma linha (um cartão), a de menor "
            "Ordem. Vazio sem linha.",
            f"VAR _o = MIN ( {T}[Ordem] )\nRETURN\n    CALCULATE ( MAX ( {T}[{coluna}] ), {T}[Ordem] = _o )", "texto")
G.conta("T26 · linha · valor", "Valor da linha do contexto (a de menor Ordem); vazio enquanto o número não chegou.",
        f"VAR _o = MIN ( {T}[Ordem] )\nRETURN\n    CALCULATE ( MAX ( {T}[Valor] ), {T}[Ordem] = _o )", "#,0.0#")
G.conta("T26 · linha · ordem", "Menor Ordem do contexto (ordena as regras e os cartões).", f"MIN ( {T}[Ordem] )", "0")

# ------------------------------------------------------------------------------------------------ contas: o debate
G.conta("T26 · arquivo · linhas",
        "Quantas linhas o arquivo do debate trouxe (dados/pbi/debate_globo.csv). Zero = a tabela existe, mas o arquivo "
        "ainda não foi lido: a tela diz isso em vez de mostrar campos vazios.", f"COUNTROWS ( ALL ( {T} ) ) + 0", "0",
        "21 (23/10/2026, 19h45)")
G.conta("T26 · debate · situação",
        "Situação do debate na linha 'debate' do arquivo: marcado, no_ar, realizado, adiado ou cancelado (outro texto "
        "ou vazio conta como marcado).",
        f"VAR _s = LOWER ( TRIM ( {linha('debate', 'Situação')} ) )\n"
        "RETURN\n"
        "    SWITCH (\n"
        "        TRUE (),\n"
        '        _s IN { "no_ar", "no ar", "ao vivo", "ao_vivo" }, "no_ar",\n'
        '        _s IN { "realizado", "adiado", "cancelado" }, _s,\n'
        '        "marcado"\n'
        "    )", "texto", "marcado (23/10/2026, 19h45)")
G.conta("T26 · debate · início", "Data e hora marcadas para o debate (Brasília).", linha("debate", "Previsto"),
        "dd/MM/yyyy HH:mm", "23/10/2026 21:20")
G.conta("T26 · debate · dia", "Dia do debate (sem a hora): a fronteira das pesquisas antes e depois.",
        "VAR _i = [T26 · debate · início]\nRETURN\n    IF ( NOT ISBLANK ( _i ), DATE ( YEAR ( _i ), MONTH ( _i ), DAY ( _i ) ) )",
        "dd/MM/yyyy", "23/10/2026")
G.conta("T26 · debate · fim previsto", "Hora prevista para o fim (o Jornal da Globo, 23h30; a Globo não informou o fim).",
        linha("fim", "Previsto"), "dd/MM/yyyy HH:mm", "23/10/2026 23:30")
G.conta("T26 · debate · motivo", "Motivo de um cancelamento ou adiamento (texto da linha 'debate'); vazio se não houver.",
        linha("debate", "Texto"), "texto")
G.conta("T26 · debate · atualizado", "Quando a situação do debate foi atualizada no arquivo.",
        linha("debate", "Atualizado"), "texto", "23/10/2026 19:45")
G.conta("T26 · debate · fonte", "Fontes da data, da hora e do formato do debate.", linha("debate", "Fonte"), "texto")
for nome, chave in (("transmissão", "transmissao"), ("mediação", "mediacao"), ("local", "local"),
                    ("checagem", "checagem")):
    G.conta(f"T26 · {nome}", f"Texto da linha '{chave}' do arquivo do debate.", linha(chave, "Texto"), "texto")

# ------------------------------------------------------------------------------------------------ contas: presença
for cand, chave in (("Lula", "presenca_lula"), ("Flávio", "presenca_flavio")):
    G.conta(f"T26 · presença · {cand}",
            f"Situação da presença de {cand}: confirmada, a_confirmar ou ausente (vazio ou outro texto = a_confirmar).",
            f"VAR _s = LOWER ( TRIM ( {linha(chave, 'Situação')} ) )\n"
            "RETURN\n"
            '    SWITCH ( TRUE (), _s = "confirmada", "confirmada", _s IN { "ausente", "não vai", "nao_vai" }, "ausente", '
            '"a_confirmar" )', "texto", "confirmada (23/10/2026, 19h45)")
G.conta("T26 · presença · situação",
        "Situação da presença da linha do contexto (confirmada, a_confirmar ou ausente), com a mesma regra das duas "
        "contas por candidato.",
        "VAR _s = LOWER ( TRIM ( [T26 · linha · situação] ) )\n"
        "RETURN\n"
        '    SWITCH ( TRUE (), _s = "confirmada", "confirmada", _s IN { "ausente", "não vai", "nao_vai" }, "ausente", '
        '"a_confirmar" )', "texto")
G.conta("T26 · ausentes", "Quem não vai (ou não foi) ao debate: Lula, Flávio, Lula e Flávio, ou vazio.",
        'VAR _l = [T26 · presença · Lula] = "ausente"\n'
        'VAR _f = [T26 · presença · Flávio] = "ausente"\n'
        "RETURN\n"
        '    SWITCH ( TRUE (), _l && _f, "Lula e Flávio", _l, "Lula", _f, "Flávio", "" )', "texto", "vazio")
G.conta("T26 · 2º turno · debates",
        "Os debates marcados no 2º turno (tabela Debate), um por linha, com o que houve para o candidato da linha do "
        "contexto: esteve, não esteve, cancelado ou não aconteceu. Separados por |.",
        "VAR _cand = [T26 · linha · candidato]\n"
        "RETURN\n"
        "    CONCATENATEX (\n"
        "        CALCULATETABLE ( VALUES ( Debate[Data] ), REMOVEFILTERS ( Debate ), Debate[Turno] = 2 ),\n"
        "        VAR _d = Debate[Data]\n"
        "        VAR _emi = CALCULATE ( MAX ( Debate[Emissora] ), REMOVEFILTERS ( Debate ), Debate[Data] = _d )\n"
        "        VAR _obs = UPPER ( CALCULATE ( MAX ( Debate[Observação] ), REMOVEFILTERS ( Debate ), Debate[Data] = _d ) )\n"
        "        VAR _part = CALCULATE ( MAX ( Debate[Participantes] ), REMOVEFILTERS ( Debate ), Debate[Data] = _d )\n"
        '        VAR _curta = IF ( CONTAINSSTRING ( _emi, "," ), LEFT ( _emi, SEARCH ( ",", _emi ) - 1 ) & " e consórcio", _emi )\n'
        "        VAR _st =\n"
        "            SWITCH (\n"
        "                TRUE (),\n"
        '                LEFT ( _obs, 9 ) = "REALIZADO", IF ( _cand <> "" && CONTAINSSTRING ( _part, _cand ), "esteve", "não esteve" ),\n'
        '                LEFT ( _obs, 9 ) = "CANCELADO", "cancelado",\n'
        '                "não aconteceu"\n'
        "            )\n"
        '        RETURN FORMAT ( _d, "dd/MM" ) & " · " & _curta & ": " & _st,\n'
        '        "|",\n'
        "        Debate[Data], ASC\n"
        "    )", "texto", "11/10 · Record: cancelado | 15/10 · SBT e consórcio: não aconteceu | 18/10 · Band: esteve")
G.conta("T26 · 2º turno · realizados", "Quantos debates do 2º turno aconteceram antes deste (tabela Debate).",
        'CALCULATE ( COUNTROWS ( Debate ), REMOVEFILTERS ( Debate ), Debate[Turno] = 2, '
        'LEFT ( Debate[Observação], 9 ) = "REALIZADO" ) + 0', "0", "1 (Band, 18/10)")

# ------------------------------------------------------------------------------------------------ contas: as regras
G.conta("T26 · regras · blocos", "Quantos blocos com tempo marcado o arquivo traz (grupo regra, com valor).",
        f'CALCULATE ( COUNTROWS ( {T} ), REMOVEFILTERS ( {T} ), {T}[Grupo] = "regra", NOT ISBLANK ( {T}[Valor] ) ) + 0',
        "0", "4")

# ------------------------------------------------------------------------------------------------ contas: os números
NUMEROS = [("buscas · Lula", "buscas_lula", "Pico de Lula no Google Trends na noite do debate (0 a 100).", "0"),
           ("buscas · Flávio", "buscas_flavio", "Pico de Flávio no Google Trends na noite do debate (0 a 100).", "0"),
           ("audiência · prévia", "audiencia_previa", "Audiência do debate na Grande SP, prévia (pontos).", "0.0"),
           ("audiência · consolidado", "audiencia_consolidado",
            "Audiência do debate na Grande SP, consolidado (pontos).", "0.0"),
           ("streaming · pico", "streaming_pico", "Pico de aparelhos assistindo ao mesmo tempo na internet.", "#,0"),
           ("redes · Lula", "redes_lula", "Interações com Lula nas 24 horas depois do debate.", "#,0"),
           ("redes · Flávio", "redes_flavio", "Interações com Flávio nas 24 horas depois do debate.", "#,0")]
for nome, chave, desc, fmt in NUMEROS:
    G.conta(f"T26 · {nome}", desc + " Vazio enquanto não chega (linha '" + chave + "' do arquivo).",
            linha(chave, "Valor"), fmt, "vazio em 23/10/2026, 19h45")

# ------------------------------------------------------------------------------------------------ contas: a Band
G.conta("T26 · Band · data", "Dia do debate da Band no 2º turno (tabela Debate: Band, turno 2).",
        'CALCULATE ( MAX ( Debate[Data] ), REMOVEFILTERS ( Debate ), Debate[Emissora] = "Band", Debate[Turno] = 2 )',
        "dd/MM/yyyy", "18/10/2026")
G.conta("T26 · Band · audiência",
        "Audiência do debate da Band de 18/10 na Grande SP: consolidado Kantar IBOPE divulgado pela Band (pontos).",
        "VAR _d = [T26 · Band · data]\nRETURN\n    CALCULATE ( MAX ( Debate[Audiência] ), REMOVEFILTERS ( Debate ), "
        "Debate[Data] = _d )", "0.0", "15")
G.conta("T26 · Band · audiência · fonte", "De onde vem a audiência da Band (coluna da tabela Debate).",
        "VAR _d = [T26 · Band · data]\nRETURN\n    CALCULATE ( MAX ( Debate[Fonte da audiência] ), "
        "REMOVEFILTERS ( Debate ), Debate[Data] = _d )", "texto")
G.conta("T26 · Band · audiência prévia",
        "Prévia da audiência do debate da Band de 18/10 na Grande SP (pontos). Constante: debates.csv › observacao "
        "da linha de 18/10 (Folha via CartaCapital: 13 de média; a TV Pop deu 13,39).", "13", "0.0", "13")
G.conta("T26 · Band · pico streaming",
        "Pico de aparelhos no YouTube da Band durante o debate de 18/10 (21h30, Poder360; tabela Debate).",
        "VAR _d = [T26 · Band · data]\nRETURN\n    CALCULATE ( MAX ( Debate[Pico no streaming] ), REMOVEFILTERS ( Debate ), "
        "Debate[Data] = _d )", "#,0", "5385394")
for cand, serie, orc in (("Lula", "Lula [tópico | H2]", "100 (21h)"),
                         ("Flávio", "Flávio Bolsonaro [tópico | H2]", "91 (22h)")):
    G.conta(f"T26 · Band · buscas · {cand}",
            f"Pico de {cand} na noite do debate da Band (18/10, das 20h à meia-noite) no Google Trends, consulta H2 "
            "(tópicos, hora a hora, 15 a 22/10).",
            "VAR _d = [T26 · Band · data]\n"
            "RETURN\n"
            f"    CALCULATE (\n        MAX ( {TT}[Índice] ),\n        REMOVEFILTERS ( {TT} ),\n"
            f'        {TT}[Série] = "{serie}",\n        {TT}[Momento] >= _d + TIME ( 20, 0, 0 ),\n'
            f"        {TT}[Momento] < _d + 1\n    )", "0", orc)
for cand, nome_mon, orc in (("Lula", "Lula", "25.500.000"), ("Flávio", "Flávio Bolsonaro", "5.000.000")):
    G.conta(f"T26 · Band · redes · {cand}",
            f"Interações com {cand} nas 24 horas depois do debate da Band (Bites, via Poder360; tabela Monitoramento).",
            "CALCULATE (\n    MAX ( Monitoramento[Valor] ),\n    REMOVEFILTERS ( Monitoramento ),\n"
            '    Monitoramento[Estudo] = "Bites (agência de dados)",\n'
            '    Monitoramento[Métrica] = "interações nas 24h após o debate da Band",\n'
            f'    Monitoramento[Candidato] = "{nome_mon}"\n)', "#,0", orc)

# ------------------------------------------------------------------------------------------------ contas: pesquisas
FILTRO_P = ('REMOVEFILTERS ( Pesquisa ),\n        Pesquisa[Cenário] = "2º turno",\n        Pesquisa[Tipo] = "totais",\n'
            "        NOT ISBLANK ( Pesquisa[Lula] ),\n        NOT ISBLANK ( Pesquisa[Flavio] )")
JANELAS = {
    "antes": ("com o campo inteiro entre os dois debates (começa depois da Band, termina antes do dia da Globo)",
              "Pesquisa[Campo início] > _band,\n        Pesquisa[Campo fim] < _globo"),
    "depois": ("com o campo inteiro depois do debate da Globo (começa depois do dia do debate)",
               "Pesquisa[Campo início] > _globo"),
    "atravessam": ("com o campo que atravessa o dia do debate da Globo (ficam fora das médias)",
                   "Pesquisa[Campo início] <= _globo,\n        Pesquisa[Campo fim] >= _globo"),
}
CAB_P = "VAR _band = [T26 · Band · data]\nVAR _globo = [T26 · debate · dia]\nRETURN\n"
ORC = {"antes": {"n": "5", "Lula": "45,98", "Flávio": "48,02"}, "depois": {"n": "0"}, "atravessam": {"n": "0"}}
for jan, (desc, filtro) in JANELAS.items():
    G.conta(f"T26 · pesquisas · {jan} · n", f"Pesquisas do 2º turno (votos totais, registradas no TSE) {desc}.",
            CAB_P + f"    CALCULATE (\n        COUNTROWS ( Pesquisa ),\n        {FILTRO_P},\n        {filtro}\n    ) + 0",
            "0", ORC[jan]["n"])
    if jan == "atravessam":
        continue
    for cand, coluna in (("Lula", "Lula"), ("Flávio", "Flavio")):
        G.conta(f"T26 · pesquisas · {jan} · {cand}",
                f"Média simples de {cand} (votos totais, %) nas pesquisas {desc}.",
                CAB_P + f"    CALCULATE (\n        AVERAGE ( Pesquisa[{coluna}] ),\n        {FILTRO_P},\n        {filtro}\n    )",
                "0.0", ORC[jan].get(cand, "vazio"))
    G.conta(f"T26 · pesquisas · {jan} · primeiro campo", f"Primeiro dia de campo entre as pesquisas {desc}.",
            CAB_P + f"    CALCULATE (\n        MIN ( Pesquisa[Campo início] ),\n        {FILTRO_P},\n        {filtro}\n    )",
            "dd/MM", "19/10" if jan == "antes" else "vazio")
    G.conta(f"T26 · pesquisas · {jan} · último campo", f"Último dia de campo entre as pesquisas {desc}.",
            CAB_P + f"    CALCULATE (\n        MAX ( Pesquisa[Campo fim] ),\n        {FILTRO_P},\n        {filtro}\n    )",
            "dd/MM", "22/10" if jan == "antes" else "vazio")
G.conta("T26 · pesquisas · depois · institutos", "Os institutos das pesquisas com o campo inteiro depois do debate.",
        CAB_P + "    CONCATENATEX (\n        CALCULATETABLE (\n            VALUES ( Pesquisa[Instituto] ),\n"
        f"            {FILTRO_P.replace(chr(10) + '        ', chr(10) + '            ')},\n"
        "            Pesquisa[Campo início] > _globo\n        ),\n        Pesquisa[Instituto],\n        \", \",\n"
        "        Pesquisa[Instituto], ASC\n    )", "texto", "vazio")
G.conta("T26 · pesquisas · situação",
        "Situação do cartão das pesquisas no arquivo do debate (aguardando ou nao_divulgado): os números vêm da tabela "
        "Pesquisa.", f"LOWER ( TRIM ( {linha('pesquisas_depois', 'Situação')} ) )", "texto", "aguardando")
# uma pesquisa (o dossiê lista as da janela)
G.conta("T26 · pesquisa · janela",
        "Janela da pesquisa do contexto (Pesquisa[Id]) em relação aos debates: antes, atravessa ou depois; vazio "
        "fora do 2º turno em votos totais ou antes da Band.",
        "VAR _band = [T26 · Band · data]\nVAR _globo = [T26 · debate · dia]\n"
        "VAR _ini = MIN ( Pesquisa[Campo início] )\nVAR _fim = MAX ( Pesquisa[Campo fim] )\n"
        "VAR _ok =\n    HASONEVALUE ( Pesquisa[Id] )\n"
        '        && SELECTEDVALUE ( Pesquisa[Cenário] ) = "2º turno"\n'
        '        && SELECTEDVALUE ( Pesquisa[Tipo] ) = "totais"\n'
        "        && NOT ISBLANK ( MAX ( Pesquisa[Lula] ) )\n        && NOT ISBLANK ( MAX ( Pesquisa[Flavio] ) )\n"
        "RETURN\n    IF (\n        _ok,\n        SWITCH (\n            TRUE (),\n"
        '            _ini > _globo, "depois",\n            _ini > _band && _fim < _globo, "antes",\n'
        '            _ini <= _globo && _fim >= _globo, "atravessa"\n        )\n    )', "texto")
for nome, expr, fmt in (("instituto", "SELECTEDVALUE ( Pesquisa[Instituto] )", "texto"),
                        ("Lula", "MAX ( Pesquisa[Lula] )", "0.0"), ("Flávio", "MAX ( Pesquisa[Flavio] )", "0.0"),
                        ("campo início", "MIN ( Pesquisa[Campo início] )", "dd/MM"),
                        ("campo fim", "MAX ( Pesquisa[Campo fim] )", "dd/MM")):
    G.conta(f"T26 · pesquisa · {nome}", f"{nome.capitalize()} da pesquisa do contexto (Pesquisa[Id]).", expr, fmt)

# ------------------------------------------------------------------------------------------------ contas: cartões
G.conta("T26 · cartão · estado",
        "Estado do cartão do contexto ('T26 Debate Globo'[Cartão]): aguardando, parcial, publicado, previa, "
        "consolidado (audiência), nao_divulgado, ou a situação do debate quando ele foi cancelado ou adiado. O valor "
        "no arquivo vence a coluna situação; as pesquisas contam pela tabela Pesquisa.",
        f"VAR _c = SELECTEDVALUE ( {T}[Cartão] )\n"
        "VAR _sit = [T26 · debate · situação]\n"
        f'VAR _linhas = CALCULATE ( COUNTROWS ( {T} ), {T}[Grupo] = "metrica" )\n'
        f'VAR _com = CALCULATE ( COUNTROWS ( {T} ), {T}[Grupo] = "metrica", NOT ISBLANK ( {T}[Valor] ) )\n'
        f'VAR _nd = CALCULATE ( COUNTROWS ( {T} ), {T}[Grupo] = "metrica", {T}[Situação] = "nao_divulgado" )\n'
        "RETURN\n"
        "    SWITCH (\n"
        "        TRUE (),\n"
        '        ISBLANK ( _c ) || _c = "" || ISBLANK ( _linhas ), BLANK (),\n'
        '        _sit IN { "cancelado", "adiado" }, _sit,\n'
        '        _c = "pesquisas",\n'
        '            IF ( [T26 · pesquisas · depois · n] > 0, "publicado", IF ( _nd > 0, "nao_divulgado", "aguardando" ) ),\n'
        '        _c = "audiencia",\n'
        "            SWITCH (\n"
        "                TRUE (),\n"
        '                NOT ISBLANK ( [T26 · audiência · consolidado] ), "consolidado",\n'
        '                NOT ISBLANK ( [T26 · audiência · prévia] ), "previa",\n'
        '                _nd >= _linhas, "nao_divulgado",\n'
        '                "aguardando"\n'
        "            ),\n"
        '        _com >= _linhas, "publicado",\n'
        '        _com > 0, "parcial",\n'
        '        _nd > 0, "nao_divulgado",\n'
        '        "aguardando"\n'
        "    )", "texto", "aguardando nos cinco (23/10/2026, 19h45)")
G.conta("T26 · cartão · ordem", "Menor Ordem das linhas do cartão do contexto.",
        f'CALCULATE ( MIN ( {T}[Ordem] ), {T}[Grupo] = "metrica" )', "0")
G.conta("T26 · cartão · posição", "Posição do cartão do contexto na fita (1 = o primeiro a chegar), pela Ordem.",
        "VAR _o = [T26 · cartão · ordem]\n"
        "VAR _todos =\n"
        "    CALCULATETABLE (\n"
        f'        ADDCOLUMNS ( VALUES ( {T}[Cartão] ), "@o", CALCULATE ( MIN ( {T}[Ordem] ) ) ),\n'
        f'        REMOVEFILTERS ( {T} ),\n        {T}[Grupo] = "metrica"\n    )\n'
        "RETURN\n    IF ( NOT ISBLANK ( _o ), COUNTROWS ( FILTER ( _todos, [@o] <= _o ) ) )", "0",
        "buscas 1 · audiência 2 · streaming 3 · redes 4 · pesquisas 5")
_CARTOES = (f'CALCULATETABLE ( VALUES ( {T}[Cartão] ), REMOVEFILTERS ( {T} ), {T}[Grupo] = "metrica" )')
G.conta("T26 · cartões · total", "Quantos cartões a noite tem (métricas no arquivo).",
        f"COUNTROWS ( {_CARTOES} ) + 0", "0", "5")
G.conta("T26 · cartões · chegaram", "Quantos cartões já têm o número (publicado, prévia ou consolidado).",
        f"COUNTROWS (\n    FILTER (\n        {_CARTOES},\n"
        '        CALCULATE ( [T26 · cartão · estado] ) IN { "publicado", "previa", "consolidado" }\n    )\n) + 0',
        "0", "0")
G.conta("T26 · cartões · não divulgados", "Quantos cartões ficaram sem número (não divulgado).",
        f"COUNTROWS (\n    FILTER (\n        {_CARTOES},\n"
        '        CALCULATE ( [T26 · cartão · estado] ) = "nao_divulgado"\n    )\n) + 0', "0", "0")

# ================================================================================================ desenho
COMUM_LEITURA = "-- 1 · Leituras (contas de T26 Debate na Globo\\Contas)\n"

# ------------------------------------------------------------------------------------------------ a ficha
FICHA = COMUM_LEITURA + r'''VAR _sit = [T26 · debate · situação]
VAR _ini = [T26 · debate · início]
VAR _atu = [T26 · debate · atualizado]
VAR _motivo = [T26 · debate · motivo]
VAR _trans = [T26 · transmissão]
VAR _med = [T26 · mediação]
VAR _local = [T26 · local]
VAR _aus = [T26 · ausentes]
VAR _n = [T26 · cartões · chegaram]
VAR _tot = [T26 · cartões · total]
VAR _nd = [T26 · cartões · não divulgados]
VAR _audC = [T26 · audiência · consolidado]
VAR _audP = [T26 · audiência · prévia]
VAR _bandC = [T26 · Band · audiência]
VAR _bandP = [T26 · Band · audiência prévia]
VAR _pN = [T26 · pesquisas · depois · n]
VAR _pL = [T26 · pesquisas · depois · Lula]
VAR _pF = [T26 · pesquisas · depois · Flávio]
VAR _aL = [T26 · pesquisas · antes · Lula]
VAR _aF = [T26 · pesquisas · antes · Flávio]
VAR _aN = [T26 · pesquisas · antes · n]
-- 2 · Textos
VAR _sitEf = IF ( _sit IN { "marcado", "no_ar" } && _n > 0, "realizado", _sit )
VAR _selo =
    SWITCH ( _sit, "no_ar", "NO AR", "realizado", "REALIZADO", "adiado", "ADIADO", "cancelado", "CANCELADO", "MARCADO" )
VAR _hora = IF ( ISBLANK ( _ini ), "—", FORMAT ( _ini, "HH" ) & "h" & FORMAT ( _ini, "nn" ) )
VAR _dia = IF ( ISBLANK ( _ini ), "", UPPER ( FORMAT ( _ini, "dddd" ) ) & ", " & FORMAT ( _ini, "dd/MM" ) & " · " )
VAR _aud = IF ( NOT ISBLANK ( _audC ), _audC, _audP )
VAR _ref = IF ( NOT ISBLANK ( _audC ), _bandC, _bandP )
VAR _cmp = SWITCH ( TRUE (), _aud > _ref, "mais que", _aud < _ref, "menos que", "o mesmo que" )
VAR _frAus =
    SWITCH (
        TRUE (),
        _aus = "", "",
        _aus = "Lula e Flávio", IF ( _sitEf = "realizado", "Nem Lula nem Flávio foram ao debate. ", "Nem Lula nem Flávio vão ao debate. " ),
        _aus & IF ( _sitEf = "realizado", " não foi ao debate. ", " não vai ao debate. " )
    )
VAR _man =
    SWITCH (
        TRUE (),
        _sit = "cancelado", "Não houve debate: a Globo cancelou.",
        _sit = "adiado", "O debate foi adiado.",
        _aus = "Lula e Flávio", _frAus,
        _sitEf = "marcado",
            IF (
                _aus = "",
                "Ainda não dá para dizer. Os números chegam entre a noite de sexta e o sábado, véspera da eleição.",
                _frAus & "Os números da noite chegam entre sexta e sábado, véspera da eleição."
            ),
        _sitEf = "no_ar", _frAus & "O debate está no ar; os primeiros números chegam quando ele acabar.",
        _pN > 0,
            _frAus & "Nas " & IF ( _pN = 1, "pesquisa feita inteira", FORMAT ( _pN, "0" ) & " pesquisas feitas inteiras" )
                & " depois do debate, Lula tem " & FORMAT ( _pL, "0.0" ) & "% e Flávio, " & FORMAT ( _pF, "0.0" ) & "%"
                & IF ( _aN > 0, "; antes, " & FORMAT ( _aL, "0.0" ) & "% e " & FORMAT ( _aF, "0.0" ) & "%", "" ) & ".",
        NOT ISBLANK ( _aud ),
            _frAus & "Na Grande SP, a Globo marcou " & FORMAT ( _aud, "0.0" ) & " pontos"
                & IF ( ISBLANK ( _audC ), " na prévia", "" ) & ", " & _cmp & " os " & #N1(_ref)#
                & IF ( ISBLANK ( _audC ), " da prévia da Band.", " da Band." ),
        _frAus & "O debate acabou, e os números ainda não chegaram."
    )
VAR _sub =
    IF (
        _sit IN { "cancelado", "adiado" },
        IF ( LEN ( _motivo ) > 0, _motivo & " · ", "" ) & "situação em " & _atu,
        "Números da noite: " & FORMAT ( _n, "0" ) & " de " & FORMAT ( _tot, "0" )
            & IF ( _nd > 0, " · " & FORMAT ( _nd, "0" ) & IF ( _nd = 1, " não divulgado", " não divulgados" ), "" )
            & " · situação em " & _atu
    )
-- 4 · Marcação (as regras em blocos e a checagem saíram da tela em 23/10/2026, pedido do dono: "achei um pouco
-- poluída… essa questão dos blocos não precisa"; seguem em dados/pbi/debate_globo.csv)
RETURN
    IF (
        [T26 · arquivo · linhas] = 0,
        "<div class='tela t26f'><div class='selo entra'><span>SEM DADOS</span></div>"
            & "<div class='dia rot entra d1'>O ÚLTIMO DEBATE ANTES DO 2º TURNO</div>"
            & "<div class='man sobe d2' style='top:72px'>O arquivo do debate ainda não chegou ao painel. A ficha, os púlpitos "
            & "e os números da noite aparecem quando ele for lido.</div></div>",
    "<div class='tela t26f s-" & _sit & "'>"
        & "<div class='selo entra'><span>" & _selo & "</span></div>"
        & "<div class='dia rot entra d1'>" & _dia & "O ÚLTIMO DEBATE ANTES DO 2º TURNO</div>"
        & "<div class='hora sobe d2'><span class='num" & IF ( _sit IN { "cancelado", "adiado" }, " riscado", "" ) & "'>" & _hora & "</span></div>"
        & "<div class='onde sobe d3'><div class='txt'><b>" & #ESC(_trans)# & "</b></div>"
            & "<div class='txt'>mediação de " & #ESC(_med)# & " · " & #ESC(_local)# & "</div></div>"
        & "<div class='man sobe d4'>" & #ESC(_man)# & "</div>"
        & "<div class='situ nota entra d2'>" & #ESC(_sub)# & "</div>"
    & "</div>"
    )'''

FICHA_ALT = r'''VAR _sit = [T26 · debate · situação]
VAR _ini = [T26 · debate · início]
VAR _aus = [T26 · ausentes]
VAR _n = [T26 · cartões · chegaram]
VAR _tot = [T26 · cartões · total]
RETURN
    "Debate da Globo, 2º turno: " & SWITCH ( _sit, "cancelado", "cancelado", "adiado", "adiado", "no_ar", "no ar", "realizado", "realizado", "marcado" )
        & IF ( ISBLANK ( _ini ), "", " para " & FORMAT ( _ini, "dd/MM" ) & ", " & FORMAT ( _ini, "HH" ) & "h" & FORMAT ( _ini, "nn" ) )
        & ", com mediação de " & [T26 · mediação] & ". "
        & IF ( _aus <> "", "Ausente: " & _aus & ". ", "" )
        & "Números da noite: " & FORMAT ( _n, "0" ) & " de " & FORMAT ( _tot, "0" ) & "."'''

# ------------------------------------------------------------------------------------------------ o palco
PULPITO = ("<g filter='url(#rbu)'><path class='tampo' pathLength='1' d='M18 44 L132 44 L124 62 L26 62 Z'/>"
           "<path class='corpo' pathLength='1' d='M34 62 L116 62 L110 134 L40 134 Z'/>"
           "<path class='base' pathLength='1' d='M26 134 L124 134 L124 144 L26 144 Z'/>"
           "<path class='filete' pathLength='1' d='M50 82 L100 82 M52 92 L98 92'/>"
           "<path class='mic' pathLength='1' d='M75 44 L75 24 C 75 16, 82 12, 90 12'/></g>")
PALCO = COMUM_LEITURA + r'''VAR _grupo = [T26 · linha · grupo]
VAR _cand = [T26 · linha · candidato]
VAR _rot = [T26 · linha · rótulo]
VAR _pres = [T26 · presença · situação]
VAR _sit = [T26 · debate · situação]
-- 2 · Textos
VAR _l = _cand = "Lula"
VAR _p = SEARCH ( " · ", _rot, 1, 0 )
VAR _nome = IF ( _p > 0, LEFT ( _rot, _p - 1 ), _rot )
VAR _resto = IF ( _p > 0, MID ( _rot, _p + 3, 40 ), "" )
VAR _fora = _sit IN { "cancelado", "adiado" }
VAR _cls =
    SWITCH ( TRUE (), _fora || _pres = "ausente", "vazio", _pres = "a_confirmar", "duvida", "ok" )
VAR _status =
    SWITCH (
        TRUE (),
        _sit = "cancelado", "debate cancelado",
        _sit = "adiado", "debate adiado",
        _pres = "ausente", IF ( _sit = "realizado", "não foi ao debate", "não vai ao debate" ),
        _pres = "a_confirmar", "presença a confirmar",
        _sit = "realizado", "esteve no debate",
        "presença confirmada"
    )
VAR _icone =
    SWITCH (
        _cls,
        "ok", "<i class='ok'></i>",
        "duvida", "<i class='qq'>?</i>",
        "<svg class='xx' width='18' height='18' viewBox='0 0 18 18'><path d='M3.5 3 L15 15.5 M15 3.5 L3 15'/></svg>"
    )
-- 3 · Geometria
VAR _x = IF ( _l, 20, 430 ) -- geometria
VAR _atraso = IF ( _l, 200, 450 ) -- geometria
-- 4 · Marcação
RETURN
    IF (
        _grupo = "presenca",
        "<div class='tela t26p'>"
            & "<div class='pu " & _cls & IF ( _l, " l", " f" ) & "' style='left:" & _x & "px'>"
                & "<div class='nm sobe' style='animation-delay:" & _atraso & "ms'><span class='" & IF ( _l, "lula-esc", "flavio-esc" ) & "'>"
                    & #ESC(_nome)# & "</span><small class='rot'>" & #ESC(_resto)# & "</small></div>"
                & "<svg class='pul' width='150' height='150' viewBox='0 0 150 150'>" & "#PULPITO#" & "</svg>"
                & "<div class='st sobe' style='animation-delay:" & _atraso + 500 & "ms'>" & _icone & "<span>" & _status & "</span></div>"
            & "</div>"
        & "</div>"
    )'''.replace("#PULPITO#", PULPITO)

PALCO_ALT = r'''"No palco, os púlpitos: Lula " & SWITCH ( [T26 · presença · Lula], "confirmada", "com presença confirmada", "ausente", "ausente", "com presença a confirmar" )
    & "; Flávio " & SWITCH ( [T26 · presença · Flávio], "confirmada", "com presença confirmada", "ausente", "ausente", "com presença a confirmar" )
    & ". Passe o mouse em cada um para o histórico e a fonte."'''

# ------------------------------------------------------------------------------------------------ a noite (fundo)
NOITE = COMUM_LEITURA + r'''VAR _sit = [T26 · debate · situação]
VAR _ini = [T26 · debate · início]
VAR _tot = [T26 · cartões · total]
-- 2 · Textos
VAR _txt =
    SWITCH (
        TRUE (),
        [T26 · arquivo · linhas] = 0, "Os números da noite aparecem aqui quando o arquivo do debate for lido.",
        _sit IN { "cancelado", "adiado" },
        "Sem debate, sem números da noite: os espaços ficam marcados como estavam.",
        FORMAT ( _tot, "0" ) & IF ( _tot = 1, " número conta", " números contam" )
            & " como foi o debate. Cada um chega numa hora; até lá, o lugar dele fica marcado, com a fonte esperada."
    )
VAR _iniTxt = IF ( ISBLANK ( _ini ), "", UPPER ( FORMAT ( _ini, "ddd dd/MM" ) ) & " · " & FORMAT ( _ini, "HH" ) & "H" & FORMAT ( _ini, "nn" ) & " · COMEÇA O DEBATE" )
-- 4 · Marcação
RETURN
    "<div class='tela t26n'>"
        & "<div class='cab'><div class='sob sobe'>A NOITE EM NÚMEROS · E A RÉGUA DA BAND, 18/10</div>"
        & IF ( [T26 · arquivo · linhas] = 0 || _sit IN { "cancelado", "adiado" }, "<div class='txt sobe d1'>" & _txt & "</div>", "" ) & "</div>"
        & "<div class='ini rot entra d3'>" & _iniTxt & "</div>"
        & "<div class='fimr rot entra d6'>DOM 25/10 · A ELEIÇÃO</div>"
        & "<svg class='fita' width='1620' height='24' viewBox='0 0 1620 24'><path class='traco' pathLength='1' "
        & "d='M8 12 C 300 10, 700 14, 1000 11 S 1450 13, 1560 12'/>"
        & "<circle class='brota' cx='8' cy='12' r='6'/></svg>"
        & "<div class='urna entra d8'></div>"
    & "</div>"'''

NOITE_ALT = r'''"Fita do tempo da noite do debate até a eleição, domingo, 25/10: " & FORMAT ( [T26 · cartões · total], "0" )
    & " números esperados; " & FORMAT ( [T26 · cartões · chegaram], "0" )
    & IF ( [T26 · cartões · chegaram] = 1, " já chegou.", " já chegaram." )'''

# ------------------------------------------------------------------------------------------------ os cartões
MOLD_UM = moldura(268, 100)
MOLD_MEIO = moldura(128, 100)
CARTOES = COMUM_LEITURA + r'''VAR _c = SELECTEDVALUE ( 'T26 Debate Globo'[Cartão] )
VAR _est = [T26 · cartão · estado]
VAR _pos = [T26 · cartão · posição]
VAR _rot = [T26 · linha · rótulo]
VAR _med = [T26 · linha · medida]
VAR _sit = [T26 · debate · situação]
VAR _bLula = [T26 · buscas · Lula]
VAR _bFlavio = [T26 · buscas · Flávio]
VAR _audP = [T26 · audiência · prévia]
VAR _audC = [T26 · audiência · consolidado]
VAR _str = [T26 · streaming · pico]
VAR _rLula = [T26 · redes · Lula]
VAR _rFlavio = [T26 · redes · Flávio]
VAR _pN = [T26 · pesquisas · depois · n]
VAR _pL = [T26 · pesquisas · depois · Lula]
VAR _pF = [T26 · pesquisas · depois · Flávio]
VAR _pIni = [T26 · pesquisas · depois · primeiro campo]
VAR _pFim = [T26 · pesquisas · depois · último campo]
VAR _pInst = [T26 · pesquisas · depois · institutos]
VAR _aN = [T26 · pesquisas · antes · n]
VAR _aL = [T26 · pesquisas · antes · Lula]
VAR _aF = [T26 · pesquisas · antes · Flávio]
VAR _aIni = [T26 · pesquisas · antes · primeiro campo]
VAR _aFim = [T26 · pesquisas · antes · último campo]
VAR _xN = [T26 · pesquisas · atravessam · n]
VAR _bandC = [T26 · Band · audiência]
VAR _bandP = [T26 · Band · audiência prévia]
VAR _bandS = [T26 · Band · pico streaming]
VAR _bandBL = [T26 · Band · buscas · Lula]
VAR _bandBF = [T26 · Band · buscas · Flávio]
VAR _bandRL = [T26 · Band · redes · Lula]
VAR _bandRF = [T26 · Band · redes · Flávio]
VAR _band = [T26 · Band · data]
-- a linha que fala por este cartão: o que falta chegar (a prévia antes do consolidado) ou o que chegou por último
VAR _chaveTxt =
    SWITCH (
        _c,
        "audiencia", IF ( _est IN { "previa", "consolidado" }, "audiencia_consolidado", "audiencia_previa" ),
        "buscas", IF ( ISBLANK ( _bLula ) && NOT ISBLANK ( _bFlavio ), "buscas_flavio", "buscas_lula" ),
        "redes", IF ( ISBLANK ( _rLula ) && NOT ISBLANK ( _rFlavio ), "redes_flavio", "redes_lula" ),
        "streaming", "streaming_pico",
        "pesquisas", "pesquisas_depois"
    )
VAR _esp = CALCULATE ( [T26 · linha · esperado], 'T26 Debate Globo'[Chave] = _chaveTxt )
VAR _chaveFonte = IF ( _c = "audiencia", IF ( _est = "consolidado", "audiencia_consolidado", "audiencia_previa" ), _chaveTxt )
VAR _fonte = CALCULATE ( [T26 · linha · fonte], 'T26 Debate Globo'[Chave] = _chaveFonte )
VAR _atu = CALCULATE ( [T26 · linha · atualizado], 'T26 Debate Globo'[Chave] = _chaveFonte )
VAR _un = CALCULATE ( [T26 · linha · unidade], 'T26 Debate Globo'[Chave] = _chaveFonte )
-- 2 · Textos
VAR _chegou = _est IN { "publicado", "previa", "consolidado" }
VAR _parado = _est IN { "cancelado", "adiado" }
VAR _quando =
    SWITCH (
        TRUE (),
        _parado, "<div class='rot'>" & IF ( _est = "cancelado", "DEBATE CANCELADO", "DEBATE ADIADO" ) & "</div>",
        _est = "consolidado", "<div class='rot'>CHEGOU · CONSOLIDADO</div><div class='qt'>" & #ESC(_atu)# & "</div>",
        _est = "previa", "<div class='rot'>FALTA O CONSOLIDADO</div><div class='qt'>" & #ESC(_esp)# & "</div>",
        _est = "publicado" && _c = "pesquisas",
            "<div class='rot'>" & IF ( _pN = 1, "CHEGOU", "CHEGARAM" ) & "</div><div class='qt'>" & FORMAT ( _pN, "0" )
                & IF ( _pN = 1, " pesquisa, campo até ", " pesquisas, campo até " ) & FORMAT ( _pFim, "dd/MM" ) & "</div>",
        _est = "publicado", "<div class='rot'>CHEGOU</div><div class='qt'>" & #ESC(_atu)# & "</div>",
        _est = "nao_divulgado", "<div class='rot'>NÃO DIVULGADO</div><div class='qt'>esperado: " & #ESC(_esp)# & "</div>",
        "<div class='rot'>" & IF ( _est = "parcial", "FALTA UM DOS DOIS", "ESPERADO" ) & "</div><div class='qt'>" & #ESC(_esp)# & "</div>"
    )
VAR _humBandS = #HUM(_bandS)#
VAR _humBandRL = #HUM1(_bandRL)#
VAR _humBandRF = #HUM1(_bandRF)#
VAR _vazioUm =
    SWITCH (
        TRUE (),
        _parado, "<div class='vz pa'>#MOLD_UM#<div class='mao'>sem número</div></div>",
        _est = "nao_divulgado", "<div class='vz nd'><div class='ndt'>não divulgado</div></div>",
        "<div class='vz ag'>#MOLD_UM#<div class='mao'>aguardando</div></div>"
    )
-- o par (Lula e Flávio, o mesmo tratamento): o número de cada um, ou o lugar dele tracejado
VAR _parLula =
    SWITCH (
        _c,
        "buscas", IF ( ISBLANK ( _bLula ), BLANK (), FORMAT ( _bLula, "0" ) ),
        "redes", IF ( ISBLANK ( _rLula ), BLANK (), #PARTE1(_rLula)# ),
        "pesquisas", IF ( _pN > 0, FORMAT ( _pL, "0.0" ), BLANK () )
    )
VAR _parFlavio =
    SWITCH (
        _c,
        "buscas", IF ( ISBLANK ( _bFlavio ), BLANK (), FORMAT ( _bFlavio, "0" ) ),
        "redes", IF ( ISBLANK ( _rFlavio ), BLANK (), #PARTE1(_rFlavio)# ),
        "pesquisas", IF ( _pN > 0, FORMAT ( _pF, "0.0" ), BLANK () )
    )
-- a unidade fica fora do número (menor), para o par caber na metade do cartão
VAR _sufLula = SWITCH ( _c, "redes", #SUF(_rLula)#, "pesquisas", "%", "" )
VAR _sufFlavio = SWITCH ( _c, "redes", #SUF(_rFlavio)#, "pesquisas", "%", "" )
VAR _vazioMeio =
    SWITCH (
        TRUE (),
        _parado, "#MOLD_MEIO#<div class='mao'>sem número</div>",
        _est = "nao_divulgado", "<div class='ndt'>não saiu</div>",
        "#MOLD_MEIO#<div class='mao'>aguardando</div>"
    )
VAR _par =
    "<div class='vz par'>"
        & "<div class='lado" & IF ( ISBLANK ( _parLula ), " vazio", "" ) & "'><div class='rot lula-esc'>LULA</div>"
            & IF ( ISBLANK ( _parLula ), _vazioMeio, "<div class='nl'><span class='num lula'>" & _parLula & "</span><small>" & _sufLula & "</small></div>" ) & "</div>"
        & "<div class='lado" & IF ( ISBLANK ( _parFlavio ), " vazio", "" ) & "'><div class='rot flavio-esc'>FLÁVIO</div>"
            & IF ( ISBLANK ( _parFlavio ), _vazioMeio, "<div class='nl'><span class='num flavio'>" & _parFlavio & "</span><small>" & _sufFlavio & "</small></div>" ) & "</div>"
    & "</div>"
VAR _um =
    SWITCH (
        _c,
        "audiencia",
            IF (
                _est IN { "previa", "consolidado" },
                "<div class='vz um'><span class='num'>" & FORMAT ( IF ( _est = "consolidado", _audC, _audP ), "0.0" ) & "</span><span class='un'>"
                    & #ESC(_un)# & "</span><span class='tag'>" & IF ( _est = "consolidado", "CONSOLIDADO", "PRÉVIA" ) & "</span></div>",
                _vazioUm
            ),
        "streaming",
            IF (
                _est = "publicado",
                "<div class='vz um'><span class='num'>" & #PARTE(_str)# & "</span><span class='un'>" & TRIM ( #SUF(_str)# )
                    & IF ( _str >= 1000, " de ", "" ) & #ESC(_un)# & "</span></div>",
                _vazioUm
            )
    )
VAR _valor = IF ( _c IN { "audiencia", "streaming" }, _um, _par )
VAR _fonteTxt =
    SWITCH (
        TRUE (),
        _c = "pesquisas" && _pN > 0,
            "Fonte: " & #ESC(_pInst)# & " · campo de " & FORMAT ( _pIni, "dd/MM" ) & " a " & FORMAT ( _pFim, "dd/MM" ) & ", registro no TSE",
        _chegou || _est = "parcial", "Fonte: " & #ESC(_fonte)#,
        "" -- sem número, a fonte esperada fica só no dossiê do cartão (tela mais limpa, 23/10/2026)
    )
-- a régua da Band (a mesma medida) ou, nas pesquisas, o antes
VAR _refAud = IF ( _est = "previa", _bandP, _bandC )
VAR _vAud = IF ( _est = "consolidado", _audC, IF ( _est = "previa", _audP, BLANK () ) )
VAR _escS = MAX ( _bandS, IF ( _est = "publicado", _str, 0 ) ) -- geometria
VAR _barras =
    SWITCH (
        _c,
        "audiencia",
            VAR _esc = MAX ( _refAud, COALESCE ( _vAud, 0 ) ) -- geometria
            RETURN
                "<div class='br'><span class='bn'>Globo</span>"
                    & IF ( ISBLANK ( _vAud ), "<i class='g oca'></i>", "<i class='g barra-x' style='width:" & #PX(_vAud / _esc * 140)# & "px'></i>" ) & "</div>"
                    & "<div class='br'><span class='bn'>Band</span><i class='b barra-x' style='width:" & #PX(_refAud / _esc * 140)# & "px'></i><b class='num'>"
                    & #N1(_refAud)# & "</b></div>",
        "streaming",
            "<div class='br'><span class='bn'>Globo</span>"
                & IF ( _est = "publicado", "<i class='g barra-x' style='width:" & #PX(_str / _escS * 140)# & "px'></i>", "<i class='g oca'></i>" ) & "</div>"
                & "<div class='br'><span class='bn'>Band</span><i class='b barra-x' style='width:" & #PX(_bandS / _escS * 140)# & "px'></i><b class='num'>"
                & _humBandS & "</b></div>"
    )
VAR _naBand = "<div class='rot'>NA BAND, " & FORMAT ( _band, "dd/MM" ) & " <span class='rq'>· "
VAR _ref =
    SWITCH (
        _c,
        "buscas",
            _naBand & "pico da noite</span></div><div class='rv'><span class='lula-esc'>Lula <b class='num'>"
                & FORMAT ( _bandBL, "0" ) & "</b></span><span class='flavio-esc'>Flávio <b class='num'>" & FORMAT ( _bandBF, "0" ) & "</b></span></div>",
        "redes",
            _naBand & "Bites, 24 horas</span></div><div class='rv'><span class='lula-esc'>Lula <b class='num'>"
                & _humBandRL & "</b></span><span class='flavio-esc'>Flávio <b class='num'>" & _humBandRF & "</b></span></div>",
        "pesquisas",
            IF (
                _aN = 0,
                "<div class='rot'>ANTES <span class='rq'>· nenhuma pesquisa entre os debates</span></div>",
                "<div class='rot'>ANTES <span class='rq'>· " & FORMAT ( _aN, "0" ) & IF ( _aN = 1, " pesquisa, de ", " pesquisas, de " ) & FORMAT ( _aIni, "dd" ) & " a "
                    & FORMAT ( _aFim, "dd/MM" ) & "</span></div><div class='rv'><span class='lula-esc'>Lula <b class='num'>" & FORMAT ( _aL, "0.0" )
                    & "%</b></span><span class='flavio-esc'>Flávio <b class='num'>" & FORMAT ( _aF, "0.0" ) & "%</b></span></div>"
            ),
        "audiencia", _naBand & IF ( _est = "previa", "prévia", "consolidado" ) & "</span></div>" & _barras,
        "streaming", _naBand & "YouTube da Band</span></div>" & _barras
    )
VAR _notaP =
    IF (
        _c = "pesquisas" && NOT _chegou && NOT _parado,
        "<div class='np'>Provavelmente só as últimas de sábado, véspera da eleição, e talvez nenhuma."
            & IF ( _xN > 0, " " & FORMAT ( _xN, "0" ) & IF ( _xN = 1, " atravessa", " atravessam" ) & " o dia do debate e fica" & IF ( _xN = 1, "", "m" ) & " fora.", "" ) & "</div>",
        ""
    )
-- 3 · Geometria (cartões de 300 px com 30 de vão, pendurados na fita em y 72; o topo do cartão em y 88, no CSS)
VAR _x = ( _pos - 1 ) * 330 -- geometria
VAR _atraso = 400 + _pos * 140 -- geometria
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _est ),
        "<div class='tela t26c'>"
            & "<div class='cx " & _est & "' style='left:" & _x & "px;animation-delay:" & _atraso & "ms'>"
                & "<i class='tk'></i><i class='ic ic-" & _c & "'></i>"
                & "<div class='qd'>" & _quando & "</div>"
                & "<div class='ti'>" & #ESC(_rot)# & "</div>"
                & "<div class='me'>" & #ESC(_med)# & "</div>"
                & _valor & _notaP
                & IF ( _fonteTxt = "", "", "<div class='fo'>" & _fonteTxt & "</div>" )
                & "<div class='ref'>" & _ref & "</div>"
            & "</div>"
        & "</div>"
    )'''.replace("#MOLD_UM#", MOLD_UM).replace("#MOLD_MEIO#", MOLD_MEIO)

CARTOES_ALT = r'''"Os " & FORMAT ( [T26 · cartões · total], "0" ) & " números da noite (buscas, audiência, transmissão na internet, redes e pesquisas), cada um com a hora e a fonte esperadas e a régua do debate da Band; "
    & FORMAT ( [T26 · cartões · chegaram], "0" ) & IF ( [T26 · cartões · chegaram] = 1, " já chegou", " já chegaram" )
    & ". Passe o mouse num cartão para o detalhe."'''

# ------------------------------------------------------------------------------------------------ dossiê do cartão
TT_CARTAO = COMUM_LEITURA + r'''VAR _c = SELECTEDVALUE ( 'T26 Debate Globo'[Cartão] )
VAR _est = [T26 · cartão · estado]
VAR _rot = [T26 · linha · rótulo]
VAR _med = [T26 · linha · medida]
VAR _obs = [T26 · linha · observação]
VAR _band = [T26 · Band · data]
VAR _bandC = [T26 · Band · audiência]
VAR _bandP = [T26 · Band · audiência prévia]
VAR _bandFonte = [T26 · Band · audiência · fonte]
VAR _bandS = [T26 · Band · pico streaming]
VAR _bandBL = [T26 · Band · buscas · Lula]
VAR _bandBF = [T26 · Band · buscas · Flávio]
VAR _bandRL = [T26 · Band · redes · Lula]
VAR _bandRF = [T26 · Band · redes · Flávio]
VAR _aN = [T26 · pesquisas · antes · n]
VAR _pN = [T26 · pesquisas · depois · n]
VAR _xN = [T26 · pesquisas · atravessam · n]
-- as linhas do cartão: o que se espera de cada uma (a audiência tem duas: prévia e consolidado)
VAR _linhas =
    CONCATENATEX (
        FILTER ( VALUES ( 'T26 Debate Globo'[Chave] ), [T26 · linha · grupo] = "metrica" && [T26 · linha · candidato] <> "Flávio" ),
        VAR _v = [T26 · linha · valor]
        VAR _ch = [T26 · linha · chave]
        VAR _nome = SWITCH ( _ch, "audiencia_previa", "Prévia", "audiencia_consolidado", "Consolidado", "" )
        RETURN
            "<div class='li'>" & IF ( _nome <> "", "<b>" & _nome & "</b> · ", "" )
                & SWITCH (
                    TRUE (),
                    _ch = "pesquisas_depois" && _pN > 0,
                        "chegaram " & FORMAT ( _pN, "0" ) & IF ( _pN = 1, " pesquisa", " pesquisas" ) & " com o campo inteiro depois do debate.",
                    _ch = "pesquisas_depois",
                        "esperadas " & #ESC([T26 · linha · esperado])# & ", de " & #ESC([T26 · linha · fonte esperada])# & ".",
                    ISBLANK ( _v ),
                        "esperado " & #ESC([T26 · linha · esperado])# & ", de " & #ESC([T26 · linha · fonte esperada])# & ".",
                    "chegou: " & #ESC([T26 · linha · fonte])#
                        & IF ( LEN ( [T26 · linha · atualizado] ) > 0, " (" & #ESC([T26 · linha · atualizado])# & ")", "" ) & "."
                ) & "</div>",
        "",
        [T26 · linha · ordem], ASC
    )
VAR _lista =
    CONCATENATEX (
        FILTER ( ALL ( Pesquisa[Id] ), [T26 · pesquisa · janela] IN { "antes", "depois" } ),
        "<div class='ps" & IF ( [T26 · pesquisa · janela] = "depois", " dep", "" ) & "'><span>" & #ESC([T26 · pesquisa · instituto])# & " · "
            & FORMAT ( [T26 · pesquisa · campo início], "dd" ) & "–" & FORMAT ( [T26 · pesquisa · campo fim], "dd/MM" )
            & IF ( [T26 · pesquisa · janela] = "depois", " · depois", "" ) & "</span><b class='lula-esc'>" & FORMAT ( [T26 · pesquisa · Lula], "0.0" )
            & "</b><b class='flavio-esc'>" & FORMAT ( [T26 · pesquisa · Flávio], "0.0" ) & "</b></div>",
        "",
        [T26 · pesquisa · campo fim], ASC
    )
-- 2 · Textos
VAR _bandTxt =
    SWITCH (
        _c,
        "buscas", "Na noite de " & FORMAT ( _band, "dd/MM" ) & ", das 20h à meia-noite, o pico foi " & FORMAT ( _bandBL, "0" ) & " para Lula e "
            & FORMAT ( _bandBF, "0" ) & " para Flávio (Google Trends, tópicos, a consulta hora a hora do levantamento). Só a proporção entre os dois se compara.",
        "audiencia", "Consolidado: " & #N1(_bandC)# & " pontos; prévia: " & #N1(_bandP)# & ". Fonte: " & _bandFonte & ".",
        "streaming", FORMAT ( _bandS, "#,0" ) & " aparelhos ao mesmo tempo, só no canal da Band no YouTube (Poder360).",
        "redes", "Lula " & FORMAT ( _bandRL, "#,0" ) & " e Flávio " & FORMAT ( _bandRF, "#,0" ) & " interações nas 24 horas depois do debate (Bites, via Poder360).",
        ""
    )
VAR _rotRef = IF ( _c = "pesquisas", "AS PESQUISAS · LULA × FLÁVIO, VOTOS TOTAIS (%)", "NA BAND, " & FORMAT ( _band, "dd/MM" ) & " · A MESMA MEDIDA" )
VAR _mao =
    SWITCH (
        _est,
        "publicado", "chegou",
        "consolidado", "chegou o consolidado",
        "previa", "falta o consolidado",
        "parcial", "falta um dos dois",
        "nao_divulgado", "não saiu",
        "cancelado", "sem debate",
        "adiado", "debate adiado",
        "ainda não chegou"
    )
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _est ),
        "<div class='sob sobe'>" & #ESC(UPPER ( _rot ))# & "</div>"
            & "<div class='tt sobe'>" & #ESC(_med)# & "</div>"
            & IF ( LEN ( _obs ) > 0, "<div class='txt sobe'>" & #ESC(_obs)# & ".</div>", "" )
            & "<hr/><div class='rot sobe'>QUANDO E DE ONDE</div><div class='txt lis sobe'>" & _linhas & "</div>"
            & "<hr/><div class='rot sobe'>" & _rotRef & "</div>"
            & IF (
                _c = "pesquisas",
                "<div class='lst sobe'>" & _lista & "</div><div class='nota sobe'>Antes: " & FORMAT ( _aN, "0" ) & " com o campo inteiro entre os dois debates"
                    & IF ( _xN > 0, "; " & FORMAT ( _xN, "0" ) & " atravessa" & IF ( _xN = 1, "", "m" ) & " o dia do debate e fica" & IF ( _xN = 1, "", "m" ) & " fora", "" )
                    & ". Cada instituto mede do seu jeito: compare cada um com ele mesmo.</div>",
                "<div class='txt sobe'>" & #ESC(_bandTxt)# & "</div>"
            )
            & "<div class='mao ti'>" & _mao & "</div>"
    )'''

TT_CARTAO_ALT = r'''VAR _rot = [T26 · linha · rótulo]
RETURN
    "Dossiê do cartão " & _rot & ": o que mede, quando e de onde o número chega, e a mesma medida no debate da Band."'''

# ------------------------------------------------------------------------------------------------ dossiê da presença
TT_PRESENCA = COMUM_LEITURA + r'''VAR _grupo = [T26 · linha · grupo]
VAR _rot = [T26 · linha · rótulo]
VAR _txt = [T26 · linha · texto]
VAR _fonte = [T26 · linha · fonte]
VAR _atu = [T26 · linha · atualizado]
VAR _pres = [T26 · presença · situação]
VAR _sit = [T26 · debate · situação]
VAR _hist = [T26 · 2º turno · debates]
VAR _real = [T26 · 2º turno · realizados]
VAR _cand = [T26 · linha · candidato]
-- 2 · Textos
VAR _tit =
    SWITCH (
        TRUE (),
        _sit = "cancelado", "O debate foi cancelado",
        _pres = "ausente", IF ( _sit = "realizado", "Não foi ao debate", "Não vai ao debate" ),
        _pres = "a_confirmar", "Presença a confirmar",
        _sit = "realizado", "Esteve no debate",
        "Presença confirmada"
    )
VAR _linhas = "<div class='li'>" & SUBSTITUTE ( #ESC(_hist)#, "|", "</div><div class='li'>" ) & "</div>"
VAR _mao = IF ( _real = 1, "antes, só um debate", FORMAT ( _real, "0" ) & " debates antes" )
-- 4 · Marcação
RETURN
    IF (
        _grupo = "presenca",
        "<div class='sob sobe" & IF ( _cand = "Lula", " lula-esc", " flavio-esc" ) & "'>" & #ESC(UPPER ( _rot ))# & "</div>"
            & "<div class='tt sobe'>" & _tit & "</div>"
            & "<div class='txt sobe'>" & #ESC(_txt)# & "</div>"
            & "<div class='nota sobe'>Fontes: " & #ESC(_fonte)# & " · atualizado em " & #ESC(_atu)# & "</div>"
            & "<hr/><div class='rot sobe'>DEBATES DO 2º TURNO, ANTES DESTE</div><div class='txt lis sobe'>" & _linhas & "</div>"
            & "<div class='mao ti'>" & _mao & "</div>"
    )'''

TT_PRESENCA_ALT = r'''"Dossiê da presença de " & [T26 · linha · rótulo] & ": a situação, o histórico com a fonte e os debates do 2º turno antes deste."'''


def expandir(texto: str) -> str:
    """#ESC(x)# → SUBSTITUTE de & < > " ' em x (texto vindo do dado); #PX(x)# → número para CSS; #HUM(x)# → mi/mil."""
    import re
    texto = re.sub(r"#ESC\((.+?)\)#", lambda m: esc(m.group(1)), texto)
    texto = re.sub(r"#PX\((.+?)\)#", lambda m: px(m.group(1)), texto)
    texto = re.sub(r"#HUM\((.+?)\)#", lambda m: num_humano(m.group(1)), texto)
    texto = re.sub(r"#N1\((.+?)\)#", lambda m: num1(m.group(1)), texto)
    texto = re.sub(r"#PARTE\((.+?)\)#", lambda m: parte(m.group(1)), texto)
    texto = re.sub(r"#PARTE1\((.+?)\)#", lambda m: parte(m.group(1), 1), texto)
    texto = re.sub(r"#HUM1\((.+?)\)#", lambda m: parte(m.group(1), 1) + " & " + sufixo(m.group(1)), texto)
    texto = re.sub(r"#SUF\((.+?)\)#", lambda m: sufixo(m.group(1)), texto)
    sobra = re.search(r"#[A-Z_]+\(", texto)
    if sobra:
        raise SystemExit("marcador sem expandir: " + texto[sobra.start():sobra.start() + 80])
    return texto


DESENHOS = [
    ("T26 · Ficha · HTML", "A ficha da noite: selo da situação, a hora, onde passa, mediação, local e checagem, a manchete "
     "(responde à pergunta com o que já se sabe: ausência, pesquisas depois do debate, audiência contra a Band ou a "
     "espera), a linha dos números que chegaram (as regras em blocos e a checagem saíram em 23/10/2026).", FICHA),
    ("T26 · Ficha · ALT", "Texto puro da ficha para leitor de tela.", FICHA_ALT),
    ("T26 · Palco · HTML", "Um púlpito por candidato (grão 'T26 Debate Globo'[Chave]; só as linhas de presença): o nome na "
     "cor dele, o púlpito em traço (vazio e tracejado se faltar ou se o debate cair) e a situação. Alvo do dossiê "
     "ttT26Presenca.", PALCO),
    ("T26 · Palco · ALT", "Texto puro do palco.", PALCO_ALT),
    ("T26 · Noite · HTML", "Fundo da faixa da noite: título, a fita do tempo do início do debate à eleição de domingo.",
     NOITE),
    ("T26 · Noite · ALT", "Texto puro da fita da noite.", NOITE_ALT),
    ("T26 · Cartões · HTML", "Um cartão por métrica da noite (grão 'T26 Debate Globo'[Cartão]): quando chega, o título, o "
     "que mede, o número (contador) ou o lugar dele tracejado com 'aguardando', a fonte (ou a esperada) e a régua do "
     "debate da Band na mesma medida; nas pesquisas, o antes. Alvo do dossiê ttT26Cartao.", CARTOES),
    ("T26 · Cartões · ALT", "Texto puro dos cartões.", CARTOES_ALT),
    ("T26 · Tooltip cartão · HTML", "Dossiê do cartão: o que mede, a ressalva, quando e de onde chega cada número e a "
     "mesma medida no debate da Band (nas pesquisas, a lista do antes e do depois).", TT_CARTAO),
    ("T26 · Tooltip cartão · ALT", "Texto puro do dossiê do cartão.", TT_CARTAO_ALT),
    ("T26 · Tooltip presença · HTML", "Dossiê da presença: a situação, o histórico com fonte e os debates do 2º turno antes "
     "deste, com o que houve para o candidato.", TT_PRESENCA),
    ("T26 · Tooltip presença · ALT", "Texto puro do dossiê da presença.", TT_PRESENCA_ALT),
]
for nome, desc, expr in DESENHOS:
    G.desenho(nome, desc, expandir(expr))


if __name__ == "__main__":
    apagados = G.limpar()
    print(G.resumo(), f"· {len(apagados)} órfão(s) apagado(s)")
