# -*- coding: utf-8 -*-
"""desenho_t11 — gera as medidas da tela 11 · Virada (contas e desenho) e o spec Vega do mapa de pontos.

    python -X utf8 pbi/scripts/desenho_t11.py

Grava:
  pbi/dax/T11 Virada/Contas/*.dax     contas (todo número que o leitor vê)
  pbi/dax/T11 Virada/Desenho/*.dax    desenho (· HTML e · ALT: só leem contas, escolhem texto, formatam e posicionam)
  pbi/spec/t11_mapa.json              Deneb (Vega 6): contorno das UFs em rabisco que se desenha, pontos esmaecendo e
                                      os que viraram acendendo em ondas a partir do centro da virada

Oráculo: mockup/data/eleicoes.json › paginas[11] (pipeline/montar_dados_mockup.py › tela_virada).
Os arquivos gerados levam "@gerado: pbi/scripts/desenho_t11.py"; um gerado que sumiu da lista é apagado.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
DAX = PBI / "dax"
TELA = "T11 Virada"
GERADOR = "pbi/scripts/desenho_t11.py"
ORACULO = "mockup/data/eleicoes.json › paginas[11]"

MEDIDAS: list[dict] = []


def conta(nome: str, formato: str, descricao: str, expr: str, oraculo: str | None = None) -> None:
    MEDIDAS.append({"nome": nome, "sub": "Contas", "pasta": f"{TELA}\\Contas", "formato": formato,
                    "descricao": descricao, "expr": expr, "oraculo": oraculo})


def desenho(nome: str, descricao: str, expr: str) -> None:
    MEDIDAS.append({"nome": nome, "sub": "Desenho", "pasta": f"{TELA}\\Desenho", "formato": "texto",
                    "descricao": descricao, "expr": expr, "oraculo": None})


def gravar() -> None:
    feitos = set()
    for m in MEDIDAS:
        destino = DAX / TELA / m["sub"] / f"{m['nome']}.dax"
        destino.parent.mkdir(parents=True, exist_ok=True)
        cab = ["/*", f"@pasta: {m['pasta']}", f"@formato: {m['formato']}", f"@descricao: {m['descricao']}"]
        if m["oraculo"]:
            cab.append(f"@oraculo: {m['oraculo']}")
        cab += [f"@gerado: {GERADOR}", "*/"]
        corpo = "\n".join(l.rstrip() for l in m["expr"].strip("\n").splitlines())
        if "\t" in corpo:
            raise SystemExit(f"{m['nome']}: tab na expressão")
        texto = "\n".join(cab) + "\n" + corpo + "\n"
        if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
            destino.write_text(texto, encoding="utf-8", newline="\n")
        feitos.add(destino.resolve())
    for p in (DAX / TELA).rglob("*.dax"):
        if p.resolve() not in feitos and f"@gerado: {GERADOR}" in p.read_text(encoding="utf-8"):
            p.unlink()


# ==================================================================================================== contas
def _ano(medida: str, coluna: str, ano: int) -> str:
    return f"""CALCULATE (
    SUM ( 'Município ano'[{coluna}] ),
    'Município ano'[Ano] = {ano}
)"""


for _a in (2022, 2026):
    conta(f"T11 · saldo {_a}", "#,0",
          f"Votos de Lula (PT) menos os do adversário (PL) em {_a}, somados no recorte. Positivo: Lula à frente.",
          f"""CALCULATE (
    SUM ( 'Município ano'[VotosPT] ) - SUM ( 'Município ano'[VotosAdversario] ),
    'Município ano'[Ano] = {_a}
)""")
    conta(f"T11 · votos de Lula {_a}", "#,0", f"Votos de Lula (PT) em {_a}, somados no recorte (sem o exterior).",
          _ano("Município ano", "VotosPT", _a))
    conta(f"T11 · votos do PL {_a}", "#,0",
          f"Votos do adversário do PL em {_a} ({'Jair' if _a == 2022 else 'Flávio'} Bolsonaro), somados no recorte.",
          _ano("Município ano", "VotosAdversario", _a))
    conta(f"T11 · válidos {_a}", "#,0", f"Votos válidos em {_a}, somados no recorte (sem o exterior).",
          _ano("Município ano", "Validos", _a))
    conta(f"T11 · margem {_a}", "0.0%",
          f"Margem de Lula em {_a}: (Lula − adversário) ÷ válidos. Tooltip e lista das maiores que viraram.",
          f"DIVIDE ( [T11 · saldo {_a}], [T11 · válidos {_a}] )", ORACULO + " › maiores_que_viraram › margem")
    conta(f"T11 · Lula % {_a}", "0.0%", f"Votos de Lula sobre os válidos em {_a}.",
          f"DIVIDE ( [T11 · votos de Lula {_a}], [T11 · válidos {_a}] )", ORACULO + " › maiores_que_viraram")
    conta(f"T11 · PL % {_a}", "0.0%", f"Votos do adversário (PL) sobre os válidos em {_a}.",
          f"DIVIDE ( [T11 · votos do PL {_a}], [T11 · válidos {_a}] )", ORACULO + " › maiores_que_viraram")

conta("T11 · situação", "0",
      "Situação do município, para o mapa: 0 Lula à frente em 2026, 1 Flávio à frente, 2 trocou Lula por Flávio, "
      "3 trocou Flávio por Lula, 4 empate. Lida no grão do município (o Deneb pinta o ponto).",
      """VAR _d22 = [T11 · saldo 2022]
VAR _d26 = [T11 · saldo 2026]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _d26 ), BLANK (),
        _d22 > 0 && _d26 < 0, 2,
        _d22 < 0 && _d26 > 0, 3,
        _d26 > 0, 0,
        _d26 < 0, 1,
        4
    )""")


def _conta_municipios(cond: str, usa22: bool = True, usa26: bool = True) -> str:
    vs = []
    if usa22:
        vs.append("        VAR _d22 = [T11 · saldo 2022]")
    if usa26:
        vs.append("        VAR _d26 = [T11 · saldo 2026]")
    return ("SUMX (\n    VALUES ( 'Município'[CodIBGE] ),\n" + "\n".join(vs)
            + f"\n        RETURN\n            IF ( {cond}, 1 )\n) + 0")


for _nome, _cond, _u22, _u26, _desc, _or in [
    ("T11 · viraram", "_d22 > 0 && _d26 < 0", True, True,
     "Municípios em que Lula estava à frente em 2022 e Flávio ficou à frente em 2026.", "viraram = 711"),
    ("T11 · voltaram", "_d22 < 0 && _d26 > 0", True, True,
     "Municípios em que o adversário estava à frente em 2022 e Lula ficou à frente em 2026.", "voltaram = 0"),
    ("T11 · seguiram com Lula", "_d22 > 0 && _d26 > 0", True, True,
     "Municípios com Lula à frente em 2022 e em 2026.", "lula_venceu 2026 = 2.663 (todos vieram de Lula em 2022)"),
    ("T11 · seguiram com o adversário", "_d22 < 0 && _d26 < 0", True, True,
     "Municípios com o adversário à frente em 2022 (Jair) e em 2026 (Flávio).", None),
    ("T11 · Lula à frente em 2022", "_d22 > 0", True, False, "Municípios com Lula à frente em 2022.",
     "lula_venceu 2022 = 3.376"),
    ("T11 · adversário à frente em 2022", "_d22 < 0", True, False,
     "Municípios com Jair Bolsonaro à frente em 2022.", "2.191 (motor, 23/10/2026)"),
    ("T11 · empates em 2022", "NOT ISBLANK ( _d22 ) && _d22 = 0", True, False,
     "Municípios com empate exato entre Lula e Jair Bolsonaro em 2022.", "4 (motor)"),
    ("T11 · Lula à frente em 2026", "_d26 > 0", False, True, "Municípios com Lula à frente em 2026.",
     "lula_venceu 2026 = 2.663"),
    ("T11 · Flávio à frente em 2026", "_d26 < 0", False, True, "Municípios com Flávio à frente em 2026.",
     "flavio_venceu_2026 = 2.906"),
    ("T11 · empates em 2026", "NOT ISBLANK ( _d26 ) && _d26 = 0", False, True,
     "Municípios com empate exato entre Lula e Flávio em 2026.", "2 (motor)"),
]:
    conta(_nome, "#,0", _desc + " Conta município a município no recorte.", _conta_municipios(_cond, _u22, _u26),
          ORACULO + f" › {_or}" if _or else None)

conta("T11 · municípios", "#,0", "Municípios com votos em 2026 no recorte (no mapa).",
      """SUMX (
    VALUES ( 'Município'[CodIBGE] ),
    IF ( [T11 · válidos 2026] > 0, 1 )
) + 0""", ORACULO + " › municipios = 5.571")
conta("T11 · variação de votos de Lula", "#,0", "Votos de Lula em 2026 menos em 2022, somados no recorte.",
      "[T11 · votos de Lula 2026] - [T11 · votos de Lula 2022]", ORACULO + " › variacao_votos › lula = −3.399.184")
conta("T11 · variação de votos do PL", "#,0", "Votos do PL em 2026 (Flávio) menos em 2022 (Jair), somados no recorte.",
      "[T11 · votos do PL 2026] - [T11 · votos do PL 2022]", ORACULO + " › variacao_votos › pl = +5.008.563")

_REGIOES = """VAR _r =
    ADDCOLUMNS ( VALUES ( 'Município'[Região] ), "@n", [T11 · viraram] )
VAR _top1 =
    TOPN ( 1, _r, [@n], DESC, 'Município'[Região], ASC )
VAR _top2 =
    TOPN ( 2, _r, [@n], DESC, 'Município'[Região], ASC )"""
conta("T11 · região com mais viradas", "texto", "Região com mais municípios que trocaram de lado (vazio se nenhum).",
      _REGIOES + """
RETURN
    IF ( MAXX ( _r, [@n] ) > 0, MAXX ( _top1, 'Município'[Região] ) )""", ORACULO + " › viraram_por_regiao[0] = Sudeste")
conta("T11 · segunda região com mais viradas", "texto", "Segunda região com mais municípios que trocaram de lado.",
      _REGIOES + """
VAR _seg =
    EXCEPT ( _top2, _top1 )
RETURN
    IF ( MAXX ( _seg, [@n] ) > 0, MAXX ( _seg, 'Município'[Região] ) )""", ORACULO + " › viraram_por_regiao[1] = Sul")
conta("T11 · viraram nas duas regiões", "#,0",
      "Municípios que trocaram de lado nas duas regiões com mais viradas, somados.",
      _REGIOES + """
RETURN
    SUMX ( _top2, [@n] )""", ORACULO + " › Sudeste 287 + Sul 251 = 538")
conta("T11 · regiões com virada", "0", "Quantas regiões têm ao menos um município que trocou de lado.",
      """VAR _r =
    ADDCOLUMNS ( VALUES ( 'Município'[Região] ), "@n", [T11 · viraram] )
RETURN
    COUNTROWS ( FILTER ( _r, [@n] > 0 ) ) + 0""")
conta("T11 · recorte", "texto",
      "O lugar escolhido no filtro de estado da casca (árvore Região › Estado), pela medida comum [Recorte · nome]: "
      "'Bahia', 'Nordeste', 'MG e SP', '3 estados'; vazio = Brasil. O filtro cai em 'UF'[Caminho] (24/10/2026), então "
      "ISFILTERED ( 'UF'[Nome] ) não serve mais.",
      "IF ( [Recorte · com escolha] = 1, [Recorte · nome] )")
conta("T11 · município · nome", "texto", "Nome do município do contexto (tooltip e lista).",
      "SELECTEDVALUE ( 'Município'[Município] )")
conta("T11 · município · UF", "texto", "Sigla da UF do município do contexto.", "SELECTEDVALUE ( 'Município'[UF] )")
conta("T11 · população", "#,0", "População do Censo 2022, somada no contexto.", "SUM ( 'Município'[População] )",
      ORACULO + " › maiores_que_viraram › populacao")
conta("T11 · porte", "texto", "Porte do município do contexto (faixa de população).", "SELECTEDVALUE ( 'Município'[Porte] )")

# ---- a seleção no mapa (clique num ponto ou retângulo arrastado: filtro cruzado em Município) e a lista das maiores
conta("T11 · seleção", "#,0",
      "Quantos municípios estão selecionados no mapa (clique num ponto ou área arrastada) ou na lista; vazio sem "
      "seleção. O filtro cruzado chega como filtro direto nas colunas do Município (o de UF da casca, não).",
      "IF ( ISFILTERED ( 'Município' ), COUNTROWS ( VALUES ( 'Município'[CodIBGE] ) ) )")
conta("T11 · município · nome e UF", "texto", "Nome (UF) do município do contexto, como as listas mostram.",
      "SELECTEDVALUE ( 'Município'[Rótulo] )")
conta("T11 · população das que viraram", "#,0",
      "População do município quando ele trocou de lado (situação 2 ou 3); vazio nos outros. Ordena e recorta a lista "
      "das maiores que viraram (filtro Top 6 do visual).",
      """VAR _s = [T11 · situação]
RETURN
    IF ( _s = 2 || _s = 3, [T11 · população] )""", ORACULO + " › maiores_que_viraram › populacao (Osasco 728.615)")
conta("T11 · posição entre as maiores que viraram", "0",
      "Posição do município na lista das maiores que viraram (1 = a mais populosa entre as que a lista mostra: o Top 6 "
      "do visual, dentro do recorte e da seleção do mapa).",
      """IF (
    HASONEVALUE ( 'Município'[CodIBGE] ) && NOT ISBLANK ( [T11 · população das que viraram] ),
    RANKX ( ALLSELECTED ( 'Município'[CodIBGE] ), [T11 · população das que viraram], , DESC, SKIP )
)""", ORACULO + " › maiores_que_viraram (ordem)")
conta("T11 · escala das maiores", "0.0%",
      "Maior afastamento do zero (margem de 2022 ou 2026) entre as cidades da lista; escala comum dos mini gráficos.",
      """MAXX (
    FILTER (
        ADDCOLUMNS (
            ALLSELECTED ( 'Município'[CodIBGE] ),
            "@p", [T11 · população das que viraram],
            "@a", MAX ( ABS ( [T11 · margem 2022] ), ABS ( [T11 · margem 2026] ) )
        ),
        NOT ISBLANK ( [@p] )
    ),
    [@a]
)""")
conta("T11 · margem no ano", "0.0%", "Margem do PT no ano do contexto, somando os municípios do contexto (série 2006–2026).",
      """DIVIDE (
    SUM ( 'Município ano'[VotosPT] ) - SUM ( 'Município ano'[VotosAdversario] ),
    SUM ( 'Município ano'[Validos] )
)""", "paginas[15] › serie › margem (mesma conta da tela Minha cidade)")
conta("T11 · eleições com o adversário à frente", "0",
      "Em quantas das seis eleições (2006–2026) o adversário do PT ficou à frente no contexto.",
      """COUNTROWS ( FILTER ( ALL ( 'Ano'[Ano] ), [T11 · margem no ano] < 0 ) ) + 0""")
conta("T11 · eleições com votos", "0", "Em quantas das seis eleições o contexto teve votos (município novo tem menos).",
      """COUNTROWS ( FILTER ( ALL ( 'Ano'[Ano] ), NOT ISBLANK ( [T11 · margem no ano] ) ) ) + 0""")
conta("T11 · antes de 2026, a última com o adversário à frente", "0",
      "A eleição mais recente antes de 2026 em que o adversário do PT ficou à frente no contexto (vazio se nenhuma).",
      """MAXX (
    FILTER ( ALL ( 'Ano'[Ano] ), 'Ano'[Ano] < 2026 && [T11 · margem no ano] < 0 ),
    'Ano'[Ano]
)""")
conta("T11 · candidato do PT no ano", "texto", "Candidato do PT no ano do contexto.",
      "SELECTEDVALUE ( 'Ano'[Candidato do PT] )")


# ==================================================================================================== desenho
ESC = 'SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {v}, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )'


def _fmt_votos(var: str, saida: str) -> str:
    """Texto com sinal e unidade (mi, mil) para uma variação de votos já lida."""
    return f"""VAR {saida} =
    SWITCH (
        TRUE (),
        ABS ( {var} ) >= 1000000, FORMAT ( {var} / 1000000, "+0.00;−0.00;0" ) & " mi",
        ABS ( {var} ) >= 100000, FORMAT ( {var} / 1000, "+#,0;−#,0;0" ) & " mil",
        ABS ( {var} ) >= 10000, FORMAT ( {var} / 1000, "+0.0;−0.0;0" ) & " mil",
        FORMAT ( {var}, "+#,0;−#,0;0" )
    )"""


def _faixa(a0: str, a1: str, b0: str, b1: str, saida: str) -> str:
    """d de uma faixa entre a barra de cima (y 32) e a de baixo (y 268), com curvas."""
    return f"""VAR {saida} =
    "M" & FORMAT ( {a0}, "0.0", "en-US" ) & ",32 C" & FORMAT ( {a0}, "0.0", "en-US" ) & ",150 "
        & FORMAT ( {b0}, "0.0", "en-US" ) & ",150 " & FORMAT ( {b0}, "0.0", "en-US" ) & ",268 L"
        & FORMAT ( {b1}, "0.0", "en-US" ) & ",268 C" & FORMAT ( {b1}, "0.0", "en-US" ) & ",150 "
        & FORMAT ( {a1}, "0.0", "en-US" ) & ",150 " & FORMAT ( {a1}, "0.0", "en-US" ) & ",32 Z\""""


desenho("T11 · Resposta · HTML",
        "Coluna da resposta: quantos municípios trocaram Lula por Flávio, o caminho inverso e a fila das cidades "
        "2022 → 2026 (barras e faixas, com a faixa dos que trocaram anotada à mão). Com seleção no mapa, conta a área "
        "marcada; com uma cidade só, diz o que ela fez. Só lê contas 'T11 · …'.",
        f"""-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _vol = [T11 · voltaram]
VAR _l22 = [T11 · Lula à frente em 2022]
VAR _a22 = [T11 · adversário à frente em 2022]
VAR _e22 = [T11 · empates em 2022]
VAR _l26 = [T11 · Lula à frente em 2026]
VAR _f26 = [T11 · Flávio à frente em 2026]
VAR _e26 = [T11 · empates em 2026]
VAR _ll = [T11 · seguiram com Lula]
VAR _ff = [T11 · seguiram com o adversário]
VAR _tot = [T11 · municípios]
VAR _nSel = [T11 · seleção]
VAR _nome1 = [T11 · município · nome e UF]
VAR _sit1 = [T11 · situação]
VAR _m22 = [T11 · margem 2022]
VAR _m26 = [T11 · margem 2026]
-- 2 · Textos
VAR _um = _nSel = 1
VAR _area = _nSel > 1
VAR _virou1 = _sit1 = 2 || _sit1 = 3
VAR _txtNome1 = {ESC.format(v="_nome1")}
VAR _txtVir =
    SWITCH ( TRUE (), _um && _virou1, "virou", _um, "não virou", _vir = 0, "nenhum", FORMAT ( _vir, "#,0" ) )
VAR _txtFrase =
    IF ( _vir <= 1, "município", "municípios" ) & IF ( _area, " da área marcada", "" )
        & IF ( _vir <= 1, " trocou", " trocaram" )
VAR _lula = "<span class='lula'>Lula</span>"
VAR _flavio = "<span class='flavio'>Flávio</span>"
VAR _frase =
    SWITCH (
        TRUE (),
        _um && _sit1 = 2, _txtNome1 & " trocou " & _lula & " por " & _flavio & " de 2022 para 2026",
        _um && _sit1 = 3, _txtNome1 & " trocou " & _flavio & " por " & _lula & " de 2022 para 2026",
        _um && _sit1 = 0, _txtNome1 & " seguiu com " & _lula & " de 2022 para 2026",
        _um && _sit1 = 1, _txtNome1 & " seguiu com o adversário de 2022 para 2026",
        _um, _txtNome1 & ": empate exato em 2026",
        _area, _txtFrase & " " & _lula & " por " & _flavio,
        _txtFrase & " " & _lula & " por " & _flavio & " de 2022 para 2026"
    )
VAR _txtInv =
    SWITCH (
        TRUE (),
        _um, "margem de Lula: " & FORMAT ( _m22 * 100, "+0.0;−0.0;0.0" ) & " → " & FORMAT ( _m26 * 100, "+0.0;−0.0;0.0" )
            & " p.p.",
        _vol = 0 && _vir = 0, "e nenhum trocou Flávio por Lula",
        _vol = 0, "nenhum fez o caminho inverso",
        _vol = 1, "1 fez o caminho inverso",
        FORMAT ( _vol, "#,0" ) & " fizeram o caminho inverso"
    )
VAR _clsGrande = IF ( _vir = 0 || _um, "grande palavra", "grande" )
VAR _txtNota =
    IF ( _vir = 0 || _um, "", IF ( _vir = 1, "o 1 que trocou", "os " & FORMAT ( _vir, "#,0" ) & " que trocaram" ) & " →" )
VAR _txtEmp =
    IF (
        _e22 + _e26 > 0,
        " Empates exatos (" & FORMAT ( _e22, "#,0" ) & " em 2022, " & FORMAT ( _e26, "#,0" ) & " em 2026) ficam de fora.",
        ""
    )
VAR _rotFila =
    SWITCH ( TRUE (), _um, "A CIDADE ESCOLHIDA", _area, "NA ÁREA MARCADA", "CIDADE A CIDADE" ) & " · QUEM FICOU À FRENTE"
-- 3 · Geometria (fila de 420 px com 6 px entre os blocos: uma cidade = 408 ÷ total)
VAR _s = DIVIDE ( 408, _tot ) -- geometria
VAR _xE22 = _l22 * _s + 6 -- geometria
VAR _xA22 = ( _l22 + _e22 ) * _s + 12 -- geometria
VAR _xE26 = _l26 * _s + 6 -- geometria
VAR _xF26 = ( _l26 + _e26 ) * _s + 12 -- geometria
{_faixa("0", "_ll * _s", "0", "_ll * _s", "_dLL")}
{_faixa("_ll * _s", "( _ll + _vir ) * _s", "420 - _vir * _s", "420", "_dLF")}
{_faixa("_xA22", "_xA22 + _vol * _s", "_ll * _s", "( _ll + _vol ) * _s", "_dFL")}
{_faixa("_xA22 + _vol * _s", "_xA22 + ( _vol + _ff ) * _s", "_xF26", "_xF26 + _ff * _s", "_dFF")}
VAR _xNota = ( _ll * _s + 420 - _vir * _s ) / 2 - 14 -- geometria
VAR _rect =
    "<rect class='barra-x' y='0' height='32' x='"
VAR _rect2 =
    "<rect class='barra-x d6' y='268' height='32' x='"
-- 4 · Marcação
VAR _svg =
    "<svg class='fila' width='420' height='300' viewBox='0 0 420 300'>"
        & "<path class='fx esmaece d7' fill='var(--rosa)' fill-opacity='.38' d='" & _dLL & "'/>"
        & "<path class='fx esmaece d8' fill='var(--azul-claro)' fill-opacity='.42' d='" & _dFF & "'/>"
        & "<path class='fx esmaece d8' fill='var(--vermelho)' fill-opacity='.85' d='" & _dFL & "'/>"
        & "<path class='fx forte' fill='var(--azul)' fill-opacity='.9' d='" & _dLF & "'/>"
        & _rect & "0' width='" & FORMAT ( _l22 * _s, "0.0", "en-US" ) & "' fill='var(--vermelho)'/>"
        & _rect & FORMAT ( _xA22, "0.0", "en-US" ) & "' width='" & FORMAT ( _a22 * _s, "0.0", "en-US" )
            & "' fill='var(--azul-claro)'/>"
        & _rect2 & "0' width='" & FORMAT ( _l26 * _s, "0.0", "en-US" ) & "' fill='var(--vermelho)'/>"
        & _rect2 & FORMAT ( _xF26, "0.0", "en-US" ) & "' width='" & FORMAT ( _f26 * _s, "0.0", "en-US" )
            & "' fill='var(--azul)'/>"
    & "</svg>"
VAR _html =
    "<div class='tela t11r'>"
        & "<div class='num " & _clsGrande & " sobe'>" & _txtVir & "</div>"
        & "<div class='man frase sobe d2'>" & _frase & "</div>"
        & "<div class='inv entra d4'><span>" & _txtInv & "</span>"
            & "<svg width='330' height='16' viewBox='0 0 330 16'><path class='traco' style='animation-delay:900ms' "
            & "pathLength='1' d='M3,10 C70,4 170,13 326,6' fill='none' stroke='var(--tinta)' stroke-width='5' "
            & "stroke-linecap='round'/></svg></div>"
        & "<div class='fluxo'>"
            & "<div class='rot entra d5'>" & _rotFila & "</div>"
            & "<div class='lb cima'><span class='e'><span class='ano'>2022</span><b class='num lula'>" & FORMAT ( _l22, "#,0" )
                & "</b><span> com Lula</span></span><span class='d'><b class='num flavio'>" & FORMAT ( _a22, "#,0" )
                & "</b><span> com Bolsonaro</span></span></div>"
            & "<div class='palco'>" & _svg
                & "<div class='mao anota entra d11' style='width:" & FORMAT ( MAX ( 120, _xNota ), "0.0", "en-US" ) & "px'>"
                & _txtNota & "</div></div>"
            & "<div class='lb baixo'><span class='e'><span class='ano'>2026</span><b class='num lula'>" & FORMAT ( _l26, "#,0" )
                & "</b><span> com Lula</span></span><span class='d'><b class='num flavio'>" & FORMAT ( _f26, "#,0" )
                & "</b><span> com Flávio</span></span></div>"
            & "<div class='nota entra d9'>Cada cidade ocupa o mesmo espaço na fila. A faixa azul forte são as que "
                & "trocaram Lula por Flávio." & _txtEmp & "</div>"
        & "</div>"
    & "</div>"
RETURN
    _html""")

desenho("T11 · Resposta · ALT", "Texto alternativo da coluna da resposta (leitor de tela).",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _vol = [T11 · voltaram]
VAR _l26 = [T11 · Lula à frente em 2026]
VAR _f26 = [T11 · Flávio à frente em 2026]
VAR _tot = [T11 · municípios]
VAR _nSel = [T11 · seleção]
-- 2 · Textos
RETURN
    IF ( _nSel > 0, IF ( _nSel = 1, "Na cidade escolhida no mapa: ", "Na área marcada no mapa: " ), "" )
        & FORMAT ( _vir, "#,0" ) & IF ( _vir = 1, " município trocou", " municípios trocaram" )
        & " Lula por Flávio de 2022 para 2026; " & FORMAT ( _vol, "#,0" ) & " fizeram o caminho inverso. Em 2026, "
        & "Lula ficou à frente em " & FORMAT ( _l26, "#,0" ) & " e Flávio em " & FORMAT ( _f26, "#,0" )
        & IF ( _tot = 1, " do único município.", " dos " & FORMAT ( _tot, "#,0" ) & " municípios." )""")

desenho("T11 · Mapa título · HTML",
        "Título do mapa: onde a virada se concentra (regiões no Brasil; a UF no filtro; a área marcada ou a cidade "
        "escolhida no mapa ou na lista), a legenda das cores e a dica do gesto.",
        f"""-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _vol = [T11 · voltaram]
VAR _tot = [T11 · municípios]
VAR _uf = [T11 · recorte]
VAR _r1 = [T11 · região com mais viradas]
VAR _r2 = [T11 · segunda região com mais viradas]
VAR _n2 = [T11 · viraram nas duas regiões]
VAR _nr = [T11 · regiões com virada]
VAR _nSel = [T11 · seleção]
VAR _nome1 = [T11 · município · nome e UF]
VAR _sit1 = [T11 · situação]
VAR _m22 = [T11 · margem 2022]
VAR _m26 = [T11 · margem 2026]
-- 2 · Textos
VAR _sVir = "<span>" & FORMAT ( _vir, "#,0" ) & "</span>"
VAR _sTot = "<span>" & FORMAT ( _tot, "#,0" ) & "</span>"
VAR _txtNome1 = {ESC.format(v="_nome1")}
VAR _oQue1 =
    SWITCH ( _sit1, 2, "trocou Lula por Flávio", 3, "trocou Flávio por Lula", 0, "Lula seguiu à frente",
        1, "o adversário seguiu à frente", "empate exato em 2026" )
VAR _man =
    SWITCH (
        TRUE (),
        _nSel = 1, _txtNome1 & ": " & _oQue1,
        _nSel > 1 && _vir = 0, "Na área marcada, nenhum dos " & _sTot & " municípios trocou de lado",
        _nSel > 1,
            "Na área marcada, " & _sVir & " dos " & _sTot & IF ( _vir = 1, " municípios trocou", " municípios trocaram" )
                & " Lula por Flávio",
        NOT ISBLANK ( _uf ) && _tot = 1 && _vir = 0, _uf & ": o único município não trocou de lado",
        NOT ISBLANK ( _uf ) && _tot = 1, _uf & ": o único município trocou Lula por Flávio",
        NOT ISBLANK ( _uf ) && _vir = 0, _uf & ": nenhum dos " & _sTot & " municípios trocou de lado",
        NOT ISBLANK ( _uf ),
            _uf & ": " & _sVir & " dos " & _sTot & IF ( _vir = 1, " municípios trocou", " municípios trocaram" )
                & " Lula por Flávio",
        _nr = 0, "Nenhum município trocou de lado",
        _nr = 1, "Todos os que viraram estão na região " & _r1,
        _r1 & " e " & _r2 & " somam <span>" & FORMAT ( _n2, "#,0" ) & "</span> dos " & _sVir & " que viraram"
    )
VAR _legVol =
    IF ( _vol > 0, "<span><i class='c-vl'></i>trocou Flávio por Lula</span>", "" )
VAR _dica =
    IF ( _nSel > 0, "clique fora dos pontos para limpar", "clique num ponto ou arraste uma área" )
-- 4 · Marcação
RETURN
    "<div class='tela t11t'>"
        & "<div class='rot entra'>CADA PONTO É UM MUNICÍPIO · QUEM FICOU À FRENTE EM 2026</div>"
        & "<div class='man sobe d1'>" & _man & "</div>"
        & "<div class='leg entra d3'><span><i class='c-l'></i>Lula à frente</span>"
            & "<span><i class='c-f'></i>Flávio à frente</span>"
            & "<span><i class='c-v'></i>trocou Lula por Flávio</span>" & _legVol
            & "<span class='dica'>" & _dica & "</span></div>"
    & "</div>\"""")

desenho("T11 · Mapa título · ALT", "Texto alternativo do título do mapa.",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _uf = [T11 · recorte]
VAR _r1 = [T11 · região com mais viradas]
VAR _r2 = [T11 · segunda região com mais viradas]
VAR _n2 = [T11 · viraram nas duas regiões]
VAR _nSel = [T11 · seleção]
VAR _nome1 = [T11 · município · nome e UF]
-- 2 · Textos
RETURN
    SWITCH (
        TRUE (),
        _nSel = 1, "Cidade escolhida no mapa: " & _nome1 & ".",
        _nSel > 1, "Área marcada no mapa: " & FORMAT ( _vir, "#,0" ) & " municípios trocaram Lula por Flávio.",
        ISBLANK ( _uf ),
            "A virada se concentra em " & _r1 & " e " & _r2 & ": " & FORMAT ( _n2, "#,0" ) & " dos "
                & FORMAT ( _vir, "#,0" ) & " municípios que trocaram de lado.",
        _uf & ": " & FORMAT ( _vir, "#,0" ) & " municípios trocaram Lula por Flávio."
    )""")

desenho("T11 · Mapa · ALT", "Texto alternativo do mapa de pontos (Deneb).",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _tot = [T11 · municípios]
-- 2 · Textos
RETURN
    "Mapa de pontos, um por município (" & FORMAT ( _tot, "#,0" ) & "). Em azul forte, os " & FORMAT ( _vir, "#,0" )
        & " que trocaram Lula por Flávio. Passe o mouse para o dossiê; clique num ponto ou arraste uma área para "
        & "filtrar a tela."\
""")

desenho("T11 · Maiores · HTML",
        "A moldura da lista 'As maiores que viraram': o título, a explicação do mini gráfico (com a seleção do mapa, "
        "'na área marcada'), o aviso quando nenhuma cidade trocou de lado e a explicação de margem. As cidades são "
        "desenhadas por cima, uma por ponto de dado ('T11 · Lista · HTML').",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _nSel = [T11 · seleção]
-- 2 · Textos
VAR _onde =
    SWITCH ( TRUE (), _nSel = 1, " · na cidade escolhida", _nSel > 1, " · na área marcada", "" )
VAR _vazio =
    "<div class='vz txt entra d2'>Nenhum município trocou de lado "
        & IF ( _nSel > 0, "na seleção do mapa", "neste recorte" ) & ".</div>"
-- 4 · Marcação
RETURN
    "<div class='tela t11m'>"
        & "<div class='rot entra'>AS MAIORES QUE VIRARAM</div>"
        & "<div class='txt sub entra d1'>Pela população; o traço vai da margem de 2022 à de 2026" & _onde & "</div>"
        & IF ( _vir = 0, _vazio, "" )
        & "<div class='pe nota entra d10'><b>Margem</b> é a diferença entre os votos de Lula e os do adversário, "
            & "em pontos percentuais dos votos válidos. À direita do traço do meio, Lula à frente; à esquerda, o "
            & "adversário.</div>"
    & "</div>\"""")

desenho("T11 · Maiores · ALT", "Texto alternativo da lista das maiores que viraram.",
        """-- 1 · Leituras
VAR _lista =
    ADDCOLUMNS ( VALUES ( 'Município'[CodIBGE] ), "@s", [T11 · situação] )
VAR _viradas =
    FILTER ( _lista, [@s] = 2 || [@s] = 3 ) /* lista */
VAR _top =
    TOPN (
        3,
        ADDCOLUMNS ( _viradas, "@pop", [T11 · população], "@nome", [T11 · município · nome] ),
        [@pop], DESC,
        'Município'[CodIBGE], ASC
    )
-- 2 · Textos
VAR _nomes = CONCATENATEX ( _top, [@nome], ", ", [@pop], DESC )
RETURN
    IF (
        ISBLANK ( _nomes ) || _nomes = "",
        "Nenhum município trocou de lado neste recorte.",
        "As maiores cidades que trocaram Lula por Flávio: " & _nomes & "."
    )""")

desenho("T11 · Lista · HTML",
        "Uma cidade da lista 'As maiores que viraram' (granularidade Município[CodIBGE], Top 6 pela população entre as "
        "que trocaram de lado): a posição à mão, o nome e a UF, os habitantes e a margem 2022 → 2026 num mini gráfico "
        "com escala comum. Vazia fora das 6. Mouse: a série da cidade (ttT11Serie); clique: o mapa vai até ela. Só lê "
        "contas.",
        f"""-- 1 · Leituras
VAR _pos = [T11 · posição entre as maiores que viraram]
VAR _pop = [T11 · população]
VAR _nome = [T11 · município · nome]
VAR _uf = [T11 · município · UF]
VAR _m22 = [T11 · margem 2022]
VAR _m26 = [T11 · margem 2026]
VAR _esc0 = [T11 · escala das maiores]
-- 2 · Textos
VAR _txtNome = {ESC.format(v="_nome")}
VAR _cor = IF ( _m26 < 0, "var(--azul)", "var(--vermelho)" )
-- 3 · Geometria (mini gráfico de 300 px: zero no meio; itens a cada 104 px a partir de y 96)
VAR _esc = MAX ( 0.05, _esc0 )
VAR _x22 = 156 + 132 * _m22 / _esc
VAR _x26 = 156 + 132 * _m26 / _esc
VAR _y = 96 + ( _pos - 1 ) * 104
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _pos ) && _pos <= 6,
        "<div class='tela t11l'><div class='it sobe d" & ( _pos + 1 ) & "' style='top:" & _y & "px'>"
            & "<span class='pos mao'>" & _pos & "</span>"
            & "<div class='nm'>" & _txtNome & " <span class='uf'>" & _uf & "</span></div>"
            & "<div class='nota'>" & FORMAT ( _pop, "#,0" ) & " habitantes</div>"
            & "<svg class='db' width='306' height='22' viewBox='0 0 306 22'>"
                & "<line x1='156' x2='156' y1='1' y2='21' class='zero'/>"
                & "<line class='traco-rapido' pathLength='1' style='animation-delay:" & ( 700 + _pos * 90 )
                    & "ms' x1='" & FORMAT ( _x22, "0.0", "en-US" ) & "' x2='" & FORMAT ( _x26, "0.0", "en-US" )
                    & "' y1='11' y2='11'/>"
                & "<circle cx='" & FORMAT ( _x22, "0.0", "en-US" ) & "' cy='11' r='5' class='m22'/>"
                & "<circle class='brota' style='animation-delay:" & ( 1100 + _pos * 90 ) & "ms' cx='"
                    & FORMAT ( _x26, "0.0", "en-US" ) & "' cy='11' r='6' fill='" & _cor & "'/>"
            & "</svg>"
            & "<div class='mg'>" & FORMAT ( _m22 * 100, "+0.0;−0.0;0.0" ) & " → "
                & FORMAT ( _m26 * 100, "+0.0;−0.0;0.0" ) & " p.p.</div>"
        & "</div></div>"
    )""")

desenho("T11 · Lista · ALT", "Texto alternativo da lista das maiores que viraram (a camada clicável).",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
-- 2 · Textos
RETURN
    "Lista das maiores cidades que trocaram de lado (" & FORMAT ( _vir, "#,0" ) & " no recorte): passe o mouse para a "
        & "série de 2006 a 2026 de cada uma; clique para levar o mapa até ela.\"""")

_ANOS_SERIE = [2006, 2010, 2014, 2018, 2022, 2026]
_TAB_ANOS_SERIE = ", ".join(f"{{ {a} }}" for a in _ANOS_SERIE)

desenho("T11 · Tooltip série · HTML",
        "Dossiê da cidade no tooltip da lista: a margem do PT em cada eleição de 2006 a 2026 em barras (para cima, PT à "
        "frente; para baixo, o adversário), com o candidato do PT de cada ano, e em quantas o adversário ficou à frente. "
        "Só lê contas.",
        f"""-- 1 · Leituras
VAR _nome = [T11 · município · nome]
VAR _uf = [T11 · município · UF]
VAR _sit = [T11 · situação]
VAR _nAdv = [T11 · eleições com o adversário à frente]
VAR _nVot = [T11 · eleições com votos]
VAR _ult = [T11 · antes de 2026, a última com o adversário à frente]
VAR _anos =
    ADDCOLUMNS (
        DATATABLE ( "a", INTEGER, {{ {_TAB_ANOS_SERIE} }} ),
        "@m", VAR _a = [a] RETURN CALCULATE ( [T11 · margem no ano], 'Ano'[Ano] = _a ),
        "@c", VAR _a = [a] RETURN CALCULATE ( [T11 · candidato do PT no ano], 'Ano'[Ano] = _a )
    ) /* lista */
-- 2 · Textos
VAR _txtNome = {ESC.format(v="_nome")}
VAR _selo = SWITCH ( _sit, 2, "VIROU EM 2026", 3, "VOLTOU AO PT", 0, "PT À FRENTE", 1, "ADVERSÁRIO À FRENTE", "EMPATE" )
VAR _clsSelo = IF ( _sit = 2 || _sit = 1, "selo az", "selo vm" )
VAR _mao =
    SWITCH (
        TRUE (),
        _sit = 2 && _nAdv = 1, "1ª vez sem o PT na frente",
        _sit = 2, "já tinha virado em " & _ult,
        _nAdv = 0, "sempre com o PT",
        _nAdv = _nVot, "nunca com o PT",
        "virou e voltou"
    )
VAR _txtConta =
    "O adversário do PT ficou à frente aqui em " & FORMAT ( _nAdv, "0" ) & " de " & FORMAT ( _nVot, "0" )
        & IF ( _nVot = 1, " eleição", " eleições" ) & "."
-- 3 · Geometria (barras de 44 px a cada 64; zero em y 70; maior margem da cidade = 54 px)
VAR _esc = MAX ( 0.05, MAXX ( _anos, ABS ( [@m] ) ) ) /* geometria */
VAR _barras =
    CONCATENATEX (
        FILTER ( _anos, NOT ISBLANK ( [@m] ) ), /* lista */
        VAR _i = ( [a] - 2006 ) / 4
        VAR _x = 10 + _i * 64
        VAR _h = MAX ( 1.5, 54 * ABS ( [@m] ) / _esc )
        VAR _cima = [@m] >= 0
        VAR _yb = IF ( _cima, 70 - _h, 70 )
        VAR _yt = IF ( _cima, 70 - _h - 6, 70 + _h + 15 )
        VAR _c = SWITCH ( [@c], "Dilma Rousseff", "Dilma", "Fernando Haddad", "Haddad", [@c] )
        RETURN
            "<rect class='" & IF ( _cima, "pt", "adv" ) & IF ( _cima, " barra-y", " desce" ) & "' style='animation-delay:"
                & ( 150 + _i * 70 ) & "ms' x='" & FORMAT ( _x, "0.0", "en-US" ) & "' y='" & FORMAT ( _yb, "0.0", "en-US" )
                & "' width='44' height='" & FORMAT ( _h, "0.0", "en-US" ) & "'/>"
                & "<text class='v " & IF ( _cima, "pt", "adv" ) & "' x='" & FORMAT ( _x + 22, "0.0", "en-US" ) & "' y='"
                & FORMAT ( _yt, "0.0", "en-US" ) & "'>" & FORMAT ( [@m] * 100, "+0;−0;0" ) & "</text>"
                & "<text class='an' x='" & FORMAT ( _x + 22, "0.0", "en-US" ) & "' y='158'>" & [a] & "</text>"
                & "<text class='cd' x='" & FORMAT ( _x + 22, "0.0", "en-US" ) & "' y='172'>" & _c & "</text>",
        "",
        [a], ASC
    )
-- 4 · Marcação
RETURN
    "<div class='tela tt11s'><div class='fita'></div>"
        & "<div class='" & _clsSelo & "'>" & _selo & "</div>"
        & "<div class='nm sobe'>" & _txtNome & " <span class='uf'>" & _uf & "</span></div>"
        & "<div class='rot entra d1'>MARGEM DO PT, ELEIÇÃO A ELEIÇÃO</div>"
        & "<svg class='serie' width='392' height='176' viewBox='0 0 392 176'>"
            & "<line class='zero' x1='0' x2='392' y1='70' y2='70'/>" & _barras
        & "</svg>"
        & "<div class='nota entra d4'>" & _txtConta & "</div>"
        & "<div class='mao entra d6'>" & _mao & "</div>"
    & "</div>\"""")

desenho("T11 · Tooltip série · ALT", "Texto alternativo da série da cidade no tooltip da lista.",
        """-- 1 · Leituras
VAR _nome = [T11 · município · nome]
VAR _nAdv = [T11 · eleições com o adversário à frente]
VAR _nVot = [T11 · eleições com votos]
-- 2 · Textos
RETURN
    _nome & ": o adversário do PT ficou à frente em " & FORMAT ( _nAdv, "0" ) & " de " & FORMAT ( _nVot, "0" )
        & " eleições de 2006 a 2026.\"""")

desenho("T11 · Tooltip município · HTML",
        "Dossiê do município no tooltip do mapa: carimbo da situação, a margem 2022 → 2026 numa régua, as fatias "
        "de Lula e do adversário e os votos que mudaram. Só lê contas.",
        f"""-- 1 · Leituras
VAR _nome = [T11 · município · nome]
VAR _uf = [T11 · município · UF]
VAR _pop = [T11 · população]
VAR _porte = [T11 · porte]
VAR _sit = [T11 · situação]
VAR _m22 = [T11 · margem 2022]
VAR _m26 = [T11 · margem 2026]
VAR _l22 = [T11 · Lula % 2022]
VAR _l26 = [T11 · Lula % 2026]
VAR _p22 = [T11 · PL % 2022]
VAR _p26 = [T11 · PL % 2026]
VAR _dLula = [T11 · variação de votos de Lula]
VAR _dPL = [T11 · variação de votos do PL]
-- 2 · Textos
VAR _txtNome =
    SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( _nome, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )
VAR _selo =
    SWITCH ( _sit, 2, "VIROU", 3, "VIROU", 0, "SEGUIU COM LULA", 1, "SEGUIU COM FLÁVIO", "EMPATE" )
VAR _clsSelo =
    SWITCH ( _sit, 2, "selo az", 3, "selo vm", 0, "selo vm leve", 1, "selo az leve", "selo" )
VAR _mao =
    SWITCH (
        _sit,
        2, "trocou Lula por Flávio",
        3, "trocou Flávio por Lula",
        0, IF ( _m26 < _m22, "Lula na frente, com menos folga", "Lula ampliou a frente" ),
        1, IF ( _m26 < _m22, "Flávio ampliou a frente", "Flávio na frente, com menos folga" ),
        "empate exato em 2026"
    )
VAR _txtM22 = FORMAT ( _m22 * 100, "+0.0;−0.0;0.0" )
VAR _txtM26 = FORMAT ( _m26 * 100, "+0.0;−0.0;0.0" )
{_fmt_votos("_dLula", "_txtDLula")}
{_fmt_votos("_dPL", "_txtDPL")}
-- 3 · Geometria (régua de 360 px: zero no meio)
VAR _esc = MAX ( 0.1, MAX ( ABS ( _m22 ), ABS ( _m26 ) ) * 1.15 ) /* geometria */
VAR _x22 = 180 + 165 * _m22 / _esc
VAR _x26 = 180 + 165 * _m26 / _esc
VAR _cor = IF ( _m26 < 0, "var(--azul)", IF ( _m26 > 0, "var(--vermelho)", "var(--cinza)" ) )
VAR _sx22 = FORMAT ( _x22, "0.0", "en-US" )
VAR _sx26 = FORMAT ( _x26, "0.0", "en-US" )
-- 4 · Marcação
RETURN
    "<div class='tela tt11'><div class='fita'></div>"
        & "<div class='" & _clsSelo & "'>" & _selo & "</div>"
        & "<div class='nm sobe'>" & _txtNome & " <span class='uf'>" & _uf & "</span></div>"
        & "<div class='nota sobe d1'>" & FORMAT ( _pop, "#,0" ) & " habitantes · " & _porte & "</div>"
        & "<div class='rot r1 entra d2'>MARGEM DE LULA · 2022 → 2026</div>"
        & "<svg class='regua' width='360' height='58' viewBox='0 0 360 58'>"
            & "<line x1='180' x2='180' y1='4' y2='40' class='zero'/>"
            & "<text x='176' y='54' text-anchor='end' class='lado'>← adversário</text>"
            & "<text x='184' y='54' class='lado'>Lula →</text>"
            & "<line class='traco-rapido' pathLength='1' style='animation-delay:300ms' x1='" & _sx22 & "' x2='" & _sx26
                & "' y1='22' y2='22'/>"
            & "<circle cx='" & _sx22 & "' cy='22' r='6' class='m22'/>"
            & "<circle class='brota' style='animation-delay:700ms' cx='" & _sx26 & "' cy='22' r='7' fill='" & _cor
                & "'/>"
            & "<text x='" & _sx22 & "' y='10' text-anchor='middle' class='v22'>" & _txtM22 & "</text>"
            & "<text x='" & _sx26 & "' y='10' text-anchor='middle' class='v26'>" & _txtM26 & "</text>"
        & "</svg>"
        & "<div class='duas entra d4'>"
            & "<div><span class='rot'>LULA</span> <b class='lula'>" & FORMAT ( _l22, "0.0%" ) & " → "
                & FORMAT ( _l26, "0.0%" ) & "</b><span class='nota'> " & _txtDLula & " votos</span></div>"
            & "<div><span class='rot'>BOLSONARO → FLÁVIO</span> <b class='flavio'>" & FORMAT ( _p22, "0.0%" )
                & " → " & FORMAT ( _p26, "0.0%" ) & "</b><span class='nota'> " & _txtDPL & " votos</span></div>"
        & "</div>"
        & "<div class='mao entra d6'>" & _mao & "</div>"
    & "</div>\"""")

desenho("T11 · Tooltip município · ALT", "Texto alternativo do dossiê do município.",
        """-- 1 · Leituras
VAR _nome = [T11 · município · nome]
VAR _uf = [T11 · município · UF]
VAR _m22 = [T11 · margem 2022]
VAR _m26 = [T11 · margem 2026]
VAR _sit = [T11 · situação]
-- 2 · Textos
RETURN
    _nome & " (" & _uf & "): margem de Lula de " & FORMAT ( _m22 * 100, "+0.0;−0.0;0.0" ) & " p.p. em 2022 para "
        & FORMAT ( _m26 * 100, "+0.0;−0.0;0.0" ) & " p.p. em 2026"
        & IF ( _sit = 2 || _sit = 3, "; virou.", "." )""")


# ==================================================================================================== spec Vega
CAMINHOS = PBI / "assets" / "mapas" / "uf_caminhos.json"
SPEC = PBI / "spec" / "t11_mapa.json"
COR = {"papel": "#F1EBDF", "creme": "#E5DBC8", "areia": "#CBBDA2", "tinta": "#1C1915", "grafite": "#48423A",
       "cinza": "#6B6357", "vermelho": "#B8322A", "rosa": "#D9877B", "azul": "#2B5797", "azul_claro": "#8FA8CF",
       "vermelho_escuro": "#8E2620"}


def _aneis(d: str) -> list[list[tuple[float, float]]]:
    aneis, atual = [], []
    for cmd, xs, ys in re.findall(r"([MLZ])\s*(?:(-?[\d.]+),(-?[\d.]+))?", d):
        if cmd == "M":
            if atual:
                aneis.append(atual)
            atual = [(float(xs), float(ys))]
        elif cmd == "L":
            atual.append((float(xs), float(ys)))
        elif cmd == "Z" and atual:
            aneis.append(atual)
            atual = []
    if atual:
        aneis.append(atual)
    return aneis


def _ruido(x: float, y: float, semente: int) -> tuple[float, float]:
    """Deslocamento determinístico pelo vértice (fronteira comum treme igual nas duas UFs)."""
    h = math.sin(round(x, 1) * 12.9898 + round(y, 1) * 78.233 + semente * 37.719) * 43758.5453
    g = math.sin(round(x, 1) * 39.3468 + round(y, 1) * 11.135 + semente * 19.313) * 24634.6345
    return (h - math.floor(h)) - .5, (g - math.floor(g)) - .5


def _caminho(aneis, amp: float = 0.0, semente: int = 0, casas: int = 1) -> tuple[str, float]:
    partes, comp = [], 0.0
    for anel in aneis:
        pts = []
        for x, y in anel:
            if amp:
                dx, dy = _ruido(x, y, semente)
                x, y = x + dx * amp, y + dy * amp
            pts.append((x, y))
        fmt = (lambda v: f"{v:.{casas}f}".rstrip("0").rstrip(".")) if casas else (lambda v: str(round(v)))
        partes.append("M" + "L".join(f"{fmt(x)},{fmt(y)}" for x, y in pts) + "Z")
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            comp += math.hypot(x1 - x0, y1 - y0)
    return "".join(partes), round(comp, 1)


def gerar_spec() -> dict:
    cam = json.loads(CAMINHOS.read_text(encoding="utf-8"))["caminhos"]
    ufs = []
    for uf, d in sorted(cam.items()):
        aneis = _aneis(d)
        xs = [x for a in aneis for x, _ in a]
        ys = [y for a in aneis for _, y in a]
        d0, l0 = _caminho(aneis)
        d1, l1 = _caminho(aneis, amp=2.2, semente=3, casas=0)
        ufs.append({"uf": uf, "d": d0, "r": d1, "lr": l1, "ld": l0, "x0": round(min(xs), 1),
                    "y0": round(min(ys), 1), "x1": round(max(xs), 1), "y1": round(max(ys), 1),
                    "cx": round((min(xs) + max(xs)) / 2, 1)})
    c = COR
    # tempo (ms): contorno 0–1900 (onda de oeste a leste); fundo creme 500–1600; pontos apagados 900–2300 (norte →
    # sul); os que viraram 2300–4400 (onda a partir do centro da virada); fim 4600
    # gesto (23/10/2026): clique num ponto filtra a tela por ele; arrastar desenha um retângulo que filtra pelos pontos
    # de dentro (pbiCrossFilterApply avançado, até 2.500; o filtro lê cada linha por datum.campo: no Deneb 2.0,
    # _{campo}_ vira o VALOR do item sob o evento, e no mouseup do arraste não há item, então o filtro não pegava
    # nada e a seleção era limpa, 23/10/2026); clique no vazio limpa. Realce vindo da lista (sit__highlight
    # Status = 'on'): a câmera vai até a UF da cidade, que ganha um anel; os outros pontos esmaecem.
    st = "datum['sit__highlightStatus']"
    apaga = (f"(datum.__selected__ == 'off' || {st} == 'off' ? 0.3 : 1)")
    rx = "(ret.x0 - ox) / k"
    spec = {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": "T11 · Virada: um ponto por município no quadro 1000 × 1000 dos mapas do painel (Município[X]/[Y]); "
                       "o contorno das UFs se desenha em rabisco, os pontos esmaecem e os que trocaram de lado acendem "
                       "em ondas. Com o filtro de UF, enquadra a UF; com uma cidade realçada pela lista, vai até a UF "
                       "dela. Clique num ponto ou arraste uma área para filtrar a tela; clique no vazio limpa. Estado "
                       "parado (prévia, PDF) = desenho final.",
        "width": {"signal": "pbiContainerWidth"},
        "height": {"signal": "pbiContainerHeight"},
        "padding": 0,
        "autosize": {"type": "none", "contains": "padding"},
        "background": None,
        "config": {"view": {"stroke": None}},
        "signals": [
            {"name": "estatico", "init": "!(windowSize()[0] > 0)"},
            {"name": "fim", "value": 4600},
            {"name": "t0", "init": "now()"},
            {"name": "t", "init": "estatico ? fim : 0",
             "on": [{"events": "timer{33}", "update": "estatico ? fim : min(now() - t0, fim)"}]},
            {"name": "folga", "value": 22},
            {"name": "temFoco", "update": "length(data('foco')) > 0"},
            {"name": "nSel", "update": "length(data('selecionados'))"},
            {"name": "temSel", "update": "nSel > 0"},
            {"name": "nAtivas", "update": "length(data('ufsDoRecorte'))"},
            {"name": "temPts", "update": "length(data('extPontos')) > 0"},
            {"name": "qx0", "update": "nAtivas ? min(data('quadro')[0].x0, temPts ? data('extPontos')[0].x0 : 1e9) : 0"},
            {"name": "qy0", "update": "nAtivas ? min(data('quadro')[0].y0, temPts ? data('extPontos')[0].y0 : 1e9) : 0"},
            {"name": "qx1", "update": "nAtivas ? max(data('quadro')[0].x1, temPts ? data('extPontos')[0].x1 : -1e9) : 1000"},
            {"name": "qy1", "update": "nAtivas ? max(data('quadro')[0].y1, temPts ? data('extPontos')[0].y1 : -1e9) : 1000"},
            {"name": "k", "update": "min((width - 2 * folga) / max(qx1 - qx0, 30), (height - 2 * folga) / max(qy1 - qy0, 30))"},
            {"name": "ox", "update": "width / 2 - (qx0 + qx1) / 2 * k"},
            {"name": "oy", "update": "height / 2 - (qy0 + qy1) / 2 * k"},
            {"name": "raio", "update": "clamp(1.7 * sqrt(k / 0.78), 1.6, 6.5)"},
            {"name": "umaUF", "update": "nAtivas == 1"},
            {"name": "cvx", "update": "length(data('centro')) ? data('centro')[0].cx : 500"},
            {"name": "cvy", "update": "length(data('centro')) ? data('centro')[0].cy : 500"},
            # gesto: retângulo arrastado (em px da vista) e o estado da seleção
            {"name": "p0", "value": [0, 0], "on": [{"events": "mousedown", "update": "xy()"}]},
            {"name": "p1", "value": [0, 0],
             "on": [{"events": "mousedown", "update": "xy()"},
                    {"events": "[mousedown, window:mouseup] > window:mousemove", "update": "xy()"}]},
            {"name": "grande_o_bastante", "update": "abs(p1[0] - p0[0]) > 6 && abs(p1[1] - p0[1]) > 6"},
            {"name": "ret", "value": None,
             "on": [{"events": "[mousedown, window:mouseup] > window:mousemove",
                     "update": "grande_o_bastante ? {x0: min(p0[0], p1[0]), x1: max(p0[0], p1[0]), "
                               "y0: min(p0[1], p1[1]), y1: max(p0[1], p1[1])} : null"},
                    {"events": "mousedown", "update": "null"}]},
            {"name": "mx0", "update": f"ret ? {rx} : 0"},
            {"name": "mx1", "update": "ret ? (ret.x1 - ox) / k : 0"},
            {"name": "my0", "update": "ret ? (ret.y0 - oy) / k : 0"},
            {"name": "my1", "update": "ret ? (ret.y1 - oy) / k : 0"},
            {"name": "arrastou", "value": False, "on": [{"events": "window:mouseup", "update": "ret != null"}]},
            {"name": "estado", "value": "neutro",
             "on": [
                 {"events": "window:mouseup",
                  "update": "ret == null ? estado : (length(data('laco')) > 2500 ? 'grande' : "
                            "(length(data('laco')) == 0 ? 'vazio' : [pbiCrossFilterApply(event, "
                            "'datum.x >= ' + mx0 + ' && datum.x <= ' + mx1 + ' && datum.y >= ' + my0 + "
                            "' && datum.y <= ' + my1, {limit: 2500}), 'area'][1]))"},
                 {"events": "@pontosApagados:click", "filter": ["!event.ctrlKey"],
                  "update": "arrastou ? estado : [pbiCrossFilterApply(event), 'ponto'][1]"},
                 {"events": "@pontosViradas:click", "filter": ["!event.ctrlKey"],
                  "update": "arrastou ? estado : [pbiCrossFilterApply(event), 'ponto'][1]"},
                 {"events": "@fundoClique:click",
                  "update": "arrastou ? estado : [pbiCrossFilterClear(), 'neutro'][1]"}]},
            {"name": "ret_fixo", "value": None,
             "on": [{"events": "window:mouseup", "update": "ret != null ? ret : ret_fixo"},
                    {"events": "@fundoClique:click", "update": "arrastou ? ret_fixo : null"},
                    {"events": "@pontosApagados:click", "update": "arrastou ? ret_fixo : null"},
                    {"events": "@pontosViradas:click", "update": "arrastou ? ret_fixo : null"}]},
        ],
        "data": [
            {"name": "dataset"},
            {"name": "foco", "source": "dataset",
             "transform": [{"type": "filter", "expr": f"{st} == 'on'"}]},
            {"name": "selecionados", "source": "dataset",
             "transform": [{"type": "filter", "expr": "datum.__selected__ == 'on'"}]},
            {"name": "ufsDoRecorte", "source": "dataset",
             "transform": [{"type": "filter", "expr": f"!temFoco || {st} == 'on'"},
                           {"type": "aggregate", "groupby": ["uf"]}]},
            {"name": "ufs", "values": ufs,
             "transform": [
                 {"type": "lookup", "from": "ufsDoRecorte", "key": "uf", "fields": ["uf"], "as": ["noRecorte"]},
                 {"type": "formula", "as": "ativa", "expr": "datum.noRecorte ? 1 : 0"},
             ]},
            {"name": "ativas", "source": "ufs",
             "transform": [
                 {"type": "filter", "expr": "datum.ativa == 1"},
                 {"type": "joinaggregate", "fields": ["cx", "cx"], "ops": ["min", "max"], "as": ["cmin", "cmax"]},
                 {"type": "formula", "as": "atraso",
                  "expr": "umaUF ? 0 : 900 * (datum.cx - datum.cmin) / max(datum.cmax - datum.cmin, 1)"},
             ]},
            {"name": "contexto", "source": "ufs", "transform": [{"type": "filter", "expr": "datum.ativa == 0"}]},
            {"name": "quadro", "source": "ativas",
             "transform": [{"type": "aggregate", "fields": ["x0", "y0", "x1", "y1"], "ops": ["min", "min", "max", "max"],
                            "as": ["x0", "y0", "x1", "y1"]}]},
            {"name": "comLugar", "source": "dataset",
             "transform": [{"type": "filter", "expr": "isValid(datum.x) && isValid(datum.y)"}]},
            {"name": "extPontos", "source": "comLugar",
             "transform": [{"type": "filter", "expr": f"!temFoco || {st} == 'on'"},
                           {"type": "aggregate", "fields": ["x", "y", "x", "y"], "ops": ["min", "min", "max", "max"],
                            "as": ["x0", "y0", "x1", "y1"]}]},
            {"name": "laco", "source": "comLugar",
             "transform": [{"type": "filter",
                            "expr": "ret != null && datum.x >= mx0 && datum.x <= mx1 && datum.y >= my0 && datum.y <= my1"}]},
            {"name": "viradas", "source": "comLugar",
             "transform": [{"type": "filter", "expr": "datum.sit == 2 || datum.sit == 3"}]},
            {"name": "centro", "source": "viradas",
             "transform": [{"type": "aggregate", "fields": ["x", "y"], "ops": ["mean", "mean"], "as": ["cx", "cy"]}]},
            {"name": "onda", "source": "viradas",
             "transform": [
                 {"type": "formula", "as": "dist", "expr": "sqrt(pow(datum.x - cvx, 2) + pow(datum.y - cvy, 2))"},
                 {"type": "joinaggregate", "fields": ["dist"], "ops": ["max"], "as": ["dmax"]},
                 {"type": "formula", "as": "atraso",
                  "expr": "2300 + 1500 * datum.dist / max(datum.dmax, 1) + (toNumber(datum.cod) % 9) * 22"},
             ]},
            {"name": "apagados", "source": "comLugar",
             "transform": [
                 {"type": "filter", "expr": "datum.sit != 2 && datum.sit != 3"},
                 {"type": "formula", "as": "atraso",
                  "expr": "900 + 900 * clamp((datum.y - qy0) / max(qy1 - qy0, 1), 0, 1) + (toNumber(datum.cod) % 7) * 15"},
             ]},
            # o anel: a cidade realçada pela lista ou a única cidade selecionada no mapa
            {"name": "anel", "source": "comLugar",
             "transform": [{"type": "filter", "expr": f"{st} == 'on' || (nSel == 1 && datum.__selected__ == 'on')"}]},
        ],
        "marks": [{
            "type": "group", "name": "palco", "clip": True,
            "encode": {"update": {"x": {"value": 0}, "y": {"value": 0}, "width": {"signal": "width"},
                                  "height": {"signal": "height"}}},
            "marks": [
                # o fundo que recebe o clique no vazio (limpa a seleção) e o começo do arrasto
                {"type": "rect", "name": "fundoClique", "interactive": True,
                 "encode": {"enter": {"x": {"value": 0}, "y": {"value": 0}, "fill": {"value": "transparent"}},
                            "update": {"width": {"signal": "width"}, "height": {"signal": "height"}}}},
                # UFs vizinhas (só quando o recorte é uma UF): contorno fino, sem animação de traço
                {"type": "path", "from": {"data": "contexto"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "fill": {"value": c["papel"]}, "stroke": {"value": c["areia"]}, "strokeWidth": {"value": 1},
                     "opacity": {"signal": "umaUF ? clamp((t - 300) / 900, 0, 1) * 0.9 : 0"}}}},
                # papel creme das UFs do recorte (cor que esmaece)
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "fill": {"value": c["creme"]},
                     "fillOpacity": {"signal": "clamp((t - 500 - datum.atraso * 0.4) / 1100, 0, 1) * 0.55"}}}},
                # rabisco: traço tremido que se desenha (dash do comprimento do contorno, em px)
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"signal": "umaUF ? datum.d : datum.r"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "stroke": {"value": c["grafite"]}, "strokeWidth": {"signal": "umaUF ? 1.6 : 1.1"},
                     "strokeJoin": {"value": "round"}, "strokeCap": {"value": "round"}, "strokeOpacity": {"value": 0.85},
                     "strokeDash": {"signal": "[(umaUF ? datum.ld : datum.lr) * k + 4, (umaUF ? datum.ld : datum.lr) * k + 4]"},
                     "strokeDashOffset": {"signal": "((umaUF ? datum.ld : datum.lr) * k + 4) * (1 - pow(clamp((t - datum.atraso) / 1000, 0, 1), 0.7))"}}}},
                # segunda passada do lápis, levemente deslocada e mais clara
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox + 0.9"}, "y": {"signal": "oy + 0.7"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "stroke": {"value": c["cinza"]}, "strokeWidth": {"value": 0.6}, "strokeOpacity": {"value": 0.5},
                     "strokeJoin": {"value": "round"},
                     "strokeDash": {"signal": "[datum.ld * k + 4, datum.ld * k + 4]"},
                     "strokeDashOffset": {"signal": "(datum.ld * k + 4) * (1 - pow(clamp((t - 250 - datum.atraso) / 1100, 0, 1), 0.7))"}}}},
                # municípios que não trocaram de lado: tons apagados que esmaecem do norte para o sul
                {"type": "symbol", "name": "pontosApagados", "from": {"data": "apagados"},
                 "encode": {
                     "update": {
                         "x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
                         "shape": {"value": "circle"}, "size": {"signal": "pow(2 * raio, 2)"},
                         "fill": {"signal": f"datum.sit == 0 ? '{c['rosa']}' : datum.sit == 1 ? '{c['azul_claro']}' : '{c['areia']}'"},
                         "fillOpacity": {"signal": f"clamp((t - datum.atraso) / 500, 0, 1) * 0.85 * {apaga}"},
                         "stroke": {"value": None},
                         "cursor": {"value": "pointer"}, "tooltip": {"signal": "datum"}},
                     "hover": {"stroke": {"value": c["tinta"]}, "strokeWidth": {"value": 1.4},
                               "fillOpacity": {"value": 1}}}},
                # os que trocaram de lado: acendem em azul (ou vermelho, o caminho inverso) em ondas
                {"type": "symbol", "name": "pontosViradas", "from": {"data": "onda"},
                 "encode": {
                     "update": {
                         "x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
                         "shape": {"value": "circle"},
                         "size": {"signal": "pow(2 * raio * 1.3 * (1 + 2.2 * pow(clamp((t - datum.atraso) / 420, 0, 1) - 1, 3) + 1.2 * pow(clamp((t - datum.atraso) / 420, 0, 1) - 1, 2)), 2)"},
                         "fill": {"signal": f"datum.sit == 3 ? '{c['vermelho']}' : '{c['azul']}'"},
                         "fillOpacity": {"signal": f"clamp((t - datum.atraso) / 200, 0, 1) * {apaga}"},
                         "stroke": {"value": c["papel"]}, "strokeWidth": {"value": 0.5},
                         "cursor": {"value": "pointer"}, "tooltip": {"signal": "datum"}},
                     "hover": {"stroke": {"value": c["tinta"]}, "strokeWidth": {"value": 1.6}}}},
                # a cidade realçada pela lista (ou a única selecionada no mapa): dois anéis à mão em volta do ponto
                {"type": "symbol", "from": {"data": "anel"}, "interactive": False,
                 "encode": {"update": {
                     "x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
                     "shape": {"value": "circle"}, "size": {"signal": "pow(2 * raio + 14, 2)"},
                     "fill": {"value": None}, "stroke": {"value": c["tinta"]}, "strokeWidth": {"value": 1.8}}}},
                {"type": "symbol", "from": {"data": "anel"}, "interactive": False,
                 "encode": {"update": {
                     "x": {"signal": "ox + datum.x * k + 1"}, "y": {"signal": "oy + datum.y * k - 1"},
                     "shape": {"value": "circle"}, "size": {"signal": "pow(2 * raio + 26, 2)"},
                     "fill": {"value": None}, "stroke": {"value": c["grafite"]}, "strokeWidth": {"value": 0.9},
                     "strokeOpacity": {"value": 0.6}}}},
                # o retângulo arrastado (e o que ficou depois de soltar, enquanto a seleção vale)
                {"type": "rect", "name": "retangulo", "interactive": False,
                 "encode": {"update": {
                     "x": {"signal": "(ret || ret_fixo || {x0: 0}).x0"},
                     "x2": {"signal": "(ret || ret_fixo || {x1: 0}).x1"},
                     "y": {"signal": "(ret || ret_fixo || {y0: 0}).y0"},
                     "y2": {"signal": "(ret || ret_fixo || {y1: 0}).y1"},
                     "fill": {"value": c["tinta"]}, "fillOpacity": {"value": 0.04},
                     "stroke": {"value": c["tinta"]}, "strokeWidth": {"value": 1.4}, "strokeDash": {"value": [5, 4]},
                     "opacity": {"signal": "ret || (ret_fixo && temSel) ? 1 : 0"}}}},
                {"type": "text", "name": "aviso", "interactive": False,
                 "encode": {"update": {
                     "x": {"signal": "width / 2"}, "y": {"value": 18}, "align": {"value": "center"},
                     "text": {"signal": "estado == 'grande' ? 'Área grande demais (mais de 2.500 cidades): marque uma "
                                        "menor ou use o filtro de estado' : estado == 'vazio' ? 'Nenhum município "
                                        "nessa área' : ''"},
                     "fill": {"value": c["vermelho_escuro"]}, "font": {"value": "Sora Eleicoes, Segoe UI, sans-serif"},
                     "fontSize": {"value": 15}, "fontWeight": {"value": 600}}}},
            ],
        }],
    }
    SPEC.parent.mkdir(parents=True, exist_ok=True)
    SPEC.write_text(json.dumps(spec, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return spec


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gravar()
    spec = gerar_spec()
    print(f"T11: {len(MEDIDAS)} medidas · spec {SPEC.name} {SPEC.stat().st_size:,} B "
          f"({len(next(d for d in spec['data'] if d['name'] == 'ufs')['values'])} UFs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
