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
conta("T11 · recorte", "texto", "Nome da UF escolhida no filtro da tela (vazio = Brasil).",
      "IF ( ISFILTERED ( 'UF'[Nome] ), SELECTEDVALUE ( 'UF'[Nome] ) )")
conta("T11 · município · nome", "texto", "Nome do município do contexto (tooltip e lista).",
      "SELECTEDVALUE ( 'Município'[Município] )")
conta("T11 · município · UF", "texto", "Sigla da UF do município do contexto.", "SELECTEDVALUE ( 'Município'[UF] )")
conta("T11 · população", "#,0", "População do Censo 2022, somada no contexto.", "SUM ( 'Município'[População] )",
      ORACULO + " › maiores_que_viraram › populacao")
conta("T11 · porte", "texto", "Porte do município do contexto (faixa de população).", "SELECTEDVALUE ( 'Município'[Porte] )")


# ==================================================================================================== desenho
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
        "2022 → 2026 (barras e faixas, com a faixa dos que trocaram anotada à mão). Só lê contas 'T11 · …'.",
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
-- 2 · Textos
VAR _txtVir = IF ( _vir = 0, "nenhum", FORMAT ( _vir, "#,0" ) )
VAR _txtFrase =
    IF ( _vir <= 1, "município trocou", "municípios trocaram" )
VAR _txtInv =
    SWITCH (
        TRUE (),
        _vol = 0 && _vir = 0, "e nenhum trocou Flávio por Lula",
        _vol = 0, "nenhum fez o caminho inverso",
        _vol = 1, "1 fez o caminho inverso",
        FORMAT ( _vol, "#,0" ) & " fizeram o caminho inverso"
    )
VAR _clsGrande = IF ( _vir = 0, "grande palavra", "grande" )
VAR _txtNota =
    IF ( _vir = 0, "", IF ( _vir = 1, "o 1 que trocou", "os " & FORMAT ( _vir, "#,0" ) & " que trocaram" ) & " →" )
VAR _txtEmp =
    IF (
        _e22 + _e26 > 0,
        " Empates exatos (" & FORMAT ( _e22, "#,0" ) & " em 2022, " & FORMAT ( _e26, "#,0" ) & " em 2026) ficam de fora.",
        ""
    )
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
        & "<div class='man frase sobe d2'>" & _txtFrase & " <span class='lula'>Lula</span> por "
            & "<span class='flavio'>Flávio</span> de 2022 para 2026</div>"
        & "<div class='inv entra d4'><span>" & _txtInv & "</span>"
            & "<svg width='330' height='16' viewBox='0 0 330 16'><path class='traco' style='animation-delay:900ms' "
            & "pathLength='1' d='M3,10 C70,4 170,13 326,6' fill='none' stroke='var(--tinta)' stroke-width='5' "
            & "stroke-linecap='round'/></svg></div>"
        & "<div class='fluxo'>"
            & "<div class='rot entra d5'>CIDADE A CIDADE · QUEM FICOU À FRENTE</div>"
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
-- 2 · Textos
RETURN
    FORMAT ( _vir, "#,0" ) & IF ( _vir = 1, " município trocou", " municípios trocaram" )
        & " Lula por Flávio de 2022 para 2026; " & FORMAT ( _vol, "#,0" ) & " fizeram o caminho inverso. Em 2026, "
        & "Lula ficou à frente em " & FORMAT ( _l26, "#,0" ) & " e Flávio em " & FORMAT ( _f26, "#,0" ) & " dos "
        & FORMAT ( _tot, "#,0" ) & " municípios.\"""")

desenho("T11 · Mapa título · HTML",
        "Título do mapa: onde a virada se concentra (regiões no Brasil; a UF no filtro) e a legenda das cores.",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _vol = [T11 · voltaram]
VAR _tot = [T11 · municípios]
VAR _uf = [T11 · recorte]
VAR _r1 = [T11 · região com mais viradas]
VAR _r2 = [T11 · segunda região com mais viradas]
VAR _n2 = [T11 · viraram nas duas regiões]
VAR _nr = [T11 · regiões com virada]
-- 2 · Textos
VAR _sVir = "<span>" & FORMAT ( _vir, "#,0" ) & "</span>"
VAR _sTot = "<span>" & FORMAT ( _tot, "#,0" ) & "</span>"
VAR _man =
    SWITCH (
        TRUE (),
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
-- 4 · Marcação
RETURN
    "<div class='tela t11t'>"
        & "<div class='rot entra'>CADA PONTO É UM MUNICÍPIO · QUEM FICOU À FRENTE EM 2026</div>"
        & "<div class='man sobe d1'>" & _man & "</div>"
        & "<div class='leg entra d3'><span><i class='c-l'></i>Lula à frente</span>"
            & "<span><i class='c-f'></i>Flávio à frente</span>"
            & "<span><i class='c-v'></i>trocou Lula por Flávio</span>" & _legVol & "</div>"
    & "</div>\"""")

desenho("T11 · Mapa título · ALT", "Texto alternativo do título do mapa.",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _uf = [T11 · recorte]
VAR _r1 = [T11 · região com mais viradas]
VAR _r2 = [T11 · segunda região com mais viradas]
VAR _n2 = [T11 · viraram nas duas regiões]
-- 2 · Textos
RETURN
    IF (
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
        & " que trocaram Lula por Flávio; em tons claros, quem ficou à frente em 2026. Passe o mouse para o dossiê."\
""")

desenho("T11 · Maiores · HTML",
        "Coluna 'As maiores que viraram': até 6 municípios que trocaram de lado, por população, com a margem "
        "2022 → 2026 num mini gráfico. Monta a lista com VALUES do município e lê as contas de cada um.",
        """-- 1 · Leituras
VAR _vir = [T11 · viraram]
VAR _lista =
    ADDCOLUMNS ( VALUES ( 'Município'[CodIBGE] ), "@s", [T11 · situação] )
VAR _viradas =
    FILTER ( _lista, [@s] = 2 || [@s] = 3 ) /* lista */
VAR _top =
    TOPN (
        6,
        ADDCOLUMNS (
            _viradas,
            "@pop", [T11 · população],
            "@nome", [T11 · município · nome],
            "@uf", [T11 · município · UF],
            "@m22", [T11 · margem 2022],
            "@m26", [T11 · margem 2026]
        ),
        [@pop], DESC,
        'Município'[CodIBGE], ASC
    )
-- 3 · Geometria (mini gráfico de 300 px: zero no meio; escala pelo maior afastamento da lista)
VAR _esc =
    MAX ( 0.05, MAXX ( _top, MAX ( ABS ( [@m22] ), ABS ( [@m26] ) ) ) ) /* geometria */
VAR _linhas =
    ADDCOLUMNS (
        _top,
        "@pos", RANKX ( _top, [@pop], , DESC, Dense ) /* geometria */,
        "@x22", 150 + 132 * [@m22] / _esc,
        "@x26", 150 + 132 * [@m26] / _esc
    )
-- 2 · Textos e 4 · Marcação
VAR _itens =
    CONCATENATEX (
        _linhas,
        VAR _y = 96 + ( [@pos] - 1 ) * 104
        VAR _cor = IF ( [@m26] < 0, "var(--azul)", "var(--vermelho)" )
        VAR _nome =
            SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( [@nome], "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )
        RETURN
            "<div class='it sobe d" & ( [@pos] + 1 ) & "' style='top:" & _y & "px'>"
                & "<span class='pos mao'>" & [@pos] & "</span>"
                & "<div class='nm'>" & _nome & " <span class='uf'>" & [@uf] & "</span></div>"
                & "<div class='nota'>" & FORMAT ( [@pop], "#,0" ) & " habitantes</div>"
                & "<svg class='db' width='300' height='22' viewBox='0 0 300 22'>"
                    & "<line x1='150' x2='150' y1='1' y2='21' class='zero'/>"
                    & "<line class='traco-rapido' pathLength='1' style='animation-delay:" & ( 700 + [@pos] * 90 )
                        & "ms' x1='" & FORMAT ( [@x22], "0.0", "en-US" ) & "' x2='" & FORMAT ( [@x26], "0.0", "en-US" )
                        & "' y1='11' y2='11'/>"
                    & "<circle cx='" & FORMAT ( [@x22], "0.0", "en-US" ) & "' cy='11' r='5' class='m22'/>"
                    & "<circle class='brota' style='animation-delay:" & ( 1100 + [@pos] * 90 ) & "ms' cx='"
                        & FORMAT ( [@x26], "0.0", "en-US" ) & "' cy='11' r='6' fill='" & _cor & "'/>"
                & "</svg>"
                & "<div class='mg'>" & FORMAT ( [@m22] * 100, "+0.0;−0.0;0.0" ) & " → "
                    & FORMAT ( [@m26] * 100, "+0.0;−0.0;0.0" ) & " p.p.</div>"
            & "</div>",
        "",
        [@pos], ASC
    )
VAR _vazio =
    "<div class='vz txt entra d2'>Nenhum município trocou de lado neste recorte.</div>"
RETURN
    "<div class='tela t11m'>"
        & "<div class='rot entra'>AS MAIORES QUE VIRARAM</div>"
        & "<div class='txt sub entra d1'>Pela população; o traço vai da margem de 2022 à de 2026</div>"
        & IF ( _vir = 0, _vazio, _itens )
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
       "cinza": "#6B6357", "vermelho": "#B8322A", "rosa": "#D9877B", "azul": "#2B5797", "azul_claro": "#8FA8CF"}


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
    spec = {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": "T11 · Virada: um ponto por município no quadro 1000 × 1000 dos mapas do painel (Município[X]/[Y]); "
                       "o contorno das UFs se desenha em rabisco, os pontos esmaecem e os que trocaram de lado acendem "
                       "em ondas. Com o filtro de UF, enquadra a UF. Estado parado (prévia, PDF) = desenho final.",
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
        ],
        "data": [
            {"name": "dataset"},
            {"name": "ufsDoRecorte", "source": "dataset",
             "transform": [{"type": "aggregate", "groupby": ["uf"]}]},
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
             "transform": [{"type": "aggregate", "fields": ["x", "y", "x", "y"], "ops": ["min", "min", "max", "max"],
                            "as": ["x0", "y0", "x1", "y1"]}]},
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
        ],
        "marks": [{
            "type": "group", "name": "palco", "clip": True,
            "encode": {"update": {"x": {"value": 0}, "y": {"value": 0}, "width": {"signal": "width"},
                                  "height": {"signal": "height"}}},
            "marks": [
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
                         "fillOpacity": {"signal": "clamp((t - datum.atraso) / 500, 0, 1) * 0.85"},
                         "stroke": {"value": None}, "tooltip": {"signal": "datum"}},
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
                         "fillOpacity": {"signal": "clamp((t - datum.atraso) / 200, 0, 1)"},
                         "stroke": {"value": c["papel"]}, "strokeWidth": {"value": 0.5},
                         "tooltip": {"signal": "datum"}},
                     "hover": {"stroke": {"value": c["tinta"]}, "strokeWidth": {"value": 1.6}}}},
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
          f"({len(spec['data'][2]['values'])} UFs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
