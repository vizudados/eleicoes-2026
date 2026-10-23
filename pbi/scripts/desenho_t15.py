# -*- coding: utf-8 -*-
"""desenho_t15 — gera as medidas da tela 15 · Minha cidade (contas e desenho).

    python -X utf8 pbi/scripts/desenho_t15.py

Grava pbi/dax/T15 Minha cidade/{Contas,Desenho}/*.dax. Tudo responde ao filtro de município da tela (VizuFilter sobre
Município[Rótulo], cidade inicial Contagem (MG)). As contas da cidade somam Município ano (sem o exterior, que não tem
município). "Entre as cidades parecidas" = mesmo porte e mesmo quinto de renda, em todo o Brasil (ignora o filtro).

Oráculo: mockup/data/eleicoes.json › paginas[15] (pipeline/montar_dados_mockup.py › ficha_cidade / tela_cidade).
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
DAX = PBI / "dax"
TELA = "T15 Minha cidade"
GERADOR = "pbi/scripts/desenho_t15.py"
ORACULO = "mockup/data/eleicoes.json › paginas[15] › cidade_guia (Contagem)"
FAIXAS = 20

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


ESC = 'SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {v}, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )'


def _soma(col: str, ano: int | None = None) -> str:
    if ano is None:
        return f"SUM ( 'Município ano'[{col}] )"
    return f"CALCULATE ( SUM ( 'Município ano'[{col}] ), 'Ano'[Ano] = {ano} )"


# ==================================================================================================== contas
conta("T15 · cidade escolhida", "0", "1 quando o contexto tem um município só (a cidade do filtro); 0 se não.",
      "IF ( HASONEVALUE ( 'Município'[CodIBGE] ), 1, 0 )")
conta("T15 · cidade", "texto", "Nome do município escolhido.", "SELECTEDVALUE ( 'Município'[Município] )",
      ORACULO + " › municipio")
conta("T15 · UF da cidade", "texto", "Sigla da UF do município escolhido.", "SELECTEDVALUE ( 'Município'[UF] )")
conta("T15 · população", "#,0", "População do município escolhido (Censo 2022).", "SUM ( 'Município'[População] )",
      ORACULO + " › populacao = 621.863")
conta("T15 · renda per capita", "#,0", "Renda domiciliar per capita do município escolhido (Censo 2022, R$/mês).",
      "MAX ( 'Município'[Renda per capita] )", ORACULO + " › renda_pc_txt = R$ 1.663")
conta("T15 · porte", "texto", "Faixa de população do município escolhido.", "SELECTEDVALUE ( 'Município'[Porte] )",
      ORACULO + " › porte")
conta("T15 · quinto de renda", "texto", "Quinto de renda do município escolhido.",
      "SELECTEDVALUE ( 'Município'[Quinto de renda] )", ORACULO + " › quinto")

for _a in (2022, 2026):
    conta(f"T15 · votos de Lula {_a}", "#,0", f"Votos de Lula (PT) em {_a} no município.", _soma("VotosPT", _a),
          ORACULO + f" › votos › lula{str(_a)[2:]}")
    conta(f"T15 · votos do PL {_a}", "#,0", f"Votos do adversário do PL em {_a} no município.",
          _soma("VotosAdversario", _a), ORACULO + f" › votos › pl{str(_a)[2:]}")
    conta(f"T15 · válidos {_a}", "#,0", f"Votos válidos em {_a} no município.", _soma("Validos", _a))
    conta(f"T15 · margem {_a}", "0.0%", f"Margem de Lula em {_a} no município: (Lula − adversário) ÷ válidos.",
          f"DIVIDE ( [T15 · votos de Lula {_a}] - [T15 · votos do PL {_a}], [T15 · válidos {_a}] )",
          ORACULO + f" › margem{str(_a)[2:]}_txt")
conta("T15 · Lula % 2026", "0.0%", "Votos de Lula sobre os válidos em 2026 no município.",
      "DIVIDE ( [T15 · votos de Lula 2026], [T15 · válidos 2026] )", ORACULO + " › serie 2026 › pt 39,3%")
conta("T15 · PL % 2026", "0.0%", "Votos de Flávio sobre os válidos em 2026 no município.",
      "DIVIDE ( [T15 · votos do PL 2026], [T15 · válidos 2026] )", ORACULO + " › serie 2026 › adv 50,3%")
conta("T15 · variação", "0.0%", "Variação da margem de Lula de 2022 para 2026 (somando os votos do contexto).",
      "[T15 · margem 2026] - [T15 · margem 2022]", ORACULO + " › variacao_txt = −5,4 p.p.")
conta("T15 · variação de votos de Lula", "#,0", "Votos de Lula em 2026 menos em 2022 no município.",
      "[T15 · votos de Lula 2026] - [T15 · votos de Lula 2022]", ORACULO + " › votos › variacao_lula_txt = −11.920")
conta("T15 · variação de votos do PL", "#,0", "Votos do PL em 2026 (Flávio) menos em 2022 (Jair) no município.",
      "[T15 · votos do PL 2026] - [T15 · votos do PL 2022]", ORACULO + " › votos › variacao_pl_txt = +6.957")

conta("T15 · nome da UF", "texto", "Nome da UF do município escolhido.",
      "LOOKUPVALUE ( 'UF'[Nome], 'UF'[UF], [T15 · UF da cidade] )")
for _a in (2022, 2026):
    conta(f"T15 · margem {_a} na UF", "0.0%",
          f"Margem de Lula em {_a} na UF da cidade, somando os municípios dela (igual à conta da tela 12).",
          f"""VAR _uf = [T15 · UF da cidade]
RETURN
    IF (
        NOT ISBLANK ( _uf ),
        CALCULATE ( [T15 · margem {_a}], REMOVEFILTERS ( 'Município' ), REMOVEFILTERS ( 'UF' ), 'Município'[UF] = _uf )
    )""", "paginas[12] › ufs › margem" + str(_a)[2:] + " (MG +4,7 → −4,9)")
    conta(f"T15 · margem do Brasil {_a}", "0.0%",
          f"Margem de Lula no Brasil em {_a}, resultado oficial com o exterior (igual às telas 01 e 12).",
          f"""DIVIDE (
    CALCULATE ( SUM ( 'Candidato ano'[Votos] ), 'Candidato ano'[Ano] = {_a}, 'Candidato ano'[Partido] = "PT" )
        - CALCULATE ( MAX ( 'Candidato ano'[Votos] ), 'Candidato ano'[Ano] = {_a}, 'Candidato ano'[Partido] <> "PT" ),
    CALCULATE ( MAX ( 'Candidato ano'[ValidosAno] ), 'Candidato ano'[Ano] = {_a} )
)""", "paginas[14] › anos (2022 +5,2; 2026 −1,9)")
conta("T15 · margem no ano", "0.0%", "Margem do PT no ano do contexto, no município (série 2006–2026).",
      f"DIVIDE ( {_soma('VotosPT')} - {_soma('VotosAdversario')}, {_soma('Validos')} )",
      ORACULO + " › serie › margem (2006 +30,0 … 2026 −11,0)")
conta("T15 · PT % no ano", "0.0%", "Votos do PT sobre os válidos no ano do contexto, no município.",
      f"DIVIDE ( {_soma('VotosPT')}, {_soma('Validos')} )", ORACULO + " › serie › pt_pct")
conta("T15 · adversário % no ano", "0.0%", "Votos do adversário principal sobre os válidos no ano, no município.",
      f"DIVIDE ( {_soma('VotosAdversario')}, {_soma('Validos')} )", ORACULO + " › serie › adv_pct")
conta("T15 · outros % no ano", "0.0%", "Votos dos demais candidatos sobre os válidos no ano, no município.",
      f"DIVIDE ( {_soma('VotosDemais')}, {_soma('Validos')} )")
conta("T15 · abstenção no ano", "0.0%", "Eleitores que faltaram sobre os aptos no ano, no município.",
      f"DIVIDE ( {_soma('Abstencoes')}, {_soma('Aptos')} )")
conta("T15 · ano", "0", "Ano do contexto (a eleição).", "SELECTEDVALUE ( 'Ano'[Ano] )")
conta("T15 · candidato do PT", "texto", "Candidato do PT no ano do contexto.", "SELECTEDVALUE ( 'Ano'[Candidato do PT] )")
conta("T15 · adversário", "texto", "Adversário principal no ano do contexto.", "SELECTEDVALUE ( 'Ano'[Adversário] )")
conta("T15 · maior margem absoluta", "0.0%", "Maior margem (em módulo) da série do município; escala das barras.",
      "MAXX ( ALL ( 'Ano'[Ano] ), ABS ( [T15 · margem no ano] ) )")
conta("T15 · primeiro ano", "0", "Primeira eleição com votos no município (2006, salvo municípios novos).",
      """MINX (
    FILTER ( ALL ( 'Ano'[Ano] ), NOT ISBLANK ( [T15 · margem no ano] ) ),
    'Ano'[Ano]
)""")
conta("T15 · margem no primeiro ano", "0.0%", "Margem do PT no município na primeira eleição da série.",
      """VAR _a = [T15 · primeiro ano]
RETURN
    CALCULATE ( [T15 · margem no ano], 'Ano'[Ano] = _a )""", ORACULO + " › serie 2006 › +30,0 p.p.")
_TROCAS = """VAR _t =
    ADDCOLUMNS ( ALL ( 'Ano'[Ano] ), "@m", [T15 · margem no ano] )
VAR _trocas =
    FILTER (
        _t,
        VAR _a = 'Ano'[Ano]
        VAR _m = [@m]
        VAR _ant = MAXX ( FILTER ( _t, 'Ano'[Ano] = _a - 4 ), [@m] )
        RETURN
            NOT ISBLANK ( _ant ) && NOT ISBLANK ( _m ) && _m <> 0 && _ant <> 0 && SIGN ( _ant ) <> SIGN ( _m )
    )"""
conta("T15 · última troca de lado", "0", "Ano da última eleição em que o município trocou de lado (PT ↔ adversário).",
      _TROCAS + "\nRETURN\n    MAXX ( _trocas, 'Ano'[Ano] )", ORACULO + " › Contagem virou em 2014")
conta("T15 · trocas de lado", "0", "Quantas vezes o município trocou de lado de uma eleição para a seguinte.",
      _TROCAS + "\nRETURN\n    COUNTROWS ( _trocas ) + 0")
conta("T15 · PT à frente na última troca", "0", "1 se, na última troca de lado, o município passou para o PT; 0 se "
      "passou para o adversário.",
      """VAR _a = [T15 · última troca de lado]
RETURN
    IF ( NOT ISBLANK ( _a ), IF ( CALCULATE ( [T15 · margem no ano], 'Ano'[Ano] = _a ) > 0, 1, 0 ) )""")

_PARECIDAS = """VAR _p = SELECTEDVALUE ( 'Município'[Porte] )
VAR _q = SELECTEDVALUE ( 'Município'[Quinto de renda] )
VAR _t =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( 'Município'[CodIBGE] ), "@d", [T15 · variação] ),
        REMOVEFILTERS ( 'Município' ),
        REMOVEFILTERS ( 'UF' ),
        'Município'[Porte] = _p,
        'Município'[Quinto de renda] = _q
    )
VAR _ok =
    FILTER ( _t, NOT ISBLANK ( [@d] ) )"""
conta("T15 · parecidas · quantidade", "#,0", "Cidades com o mesmo porte e o mesmo quinto de renda da escolhida (Brasil).",
      """VAR _p = SELECTEDVALUE ( 'Município'[Porte] )
VAR _q = SELECTEDVALUE ( 'Município'[Quinto de renda] )
RETURN
    IF (
        NOT ISBLANK ( _p ) && NOT ISBLANK ( _q ),
        CALCULATE (
            COUNTROWS ( 'Município' ),
            REMOVEFILTERS ( 'Município' ),
            REMOVEFILTERS ( 'UF' ),
            'Município'[Porte] = _p,
            'Município'[Quinto de renda] = _q
        )
    )""", ORACULO + " › entre_parecidas › municipios = 78")
conta("T15 · parecidas · variação do grupo", "0.0%",
      "Variação da margem de Lula no grupo de cidades parecidas, somando os votos delas.",
      """VAR _p = SELECTEDVALUE ( 'Município'[Porte] )
VAR _q = SELECTEDVALUE ( 'Município'[Quinto de renda] )
RETURN
    IF (
        NOT ISBLANK ( _p ) && NOT ISBLANK ( _q ),
        CALCULATE (
            [T15 · variação],
            REMOVEFILTERS ( 'Município' ),
            REMOVEFILTERS ( 'UF' ),
            'Município'[Porte] = _p,
            'Município'[Quinto de renda] = _q
        )
    )""", ORACULO + " › entre_parecidas › variacao_grupo_txt = −5,6 p.p.")
conta("T15 · parecidas · posição", "0", "Posição da cidade entre as parecidas pela queda da margem (1 = a maior queda).",
      _PARECIDAS + """
VAR _d = [T15 · variação]
RETURN
    IF ( NOT ISBLANK ( _d ) && NOT ISBLANK ( _p ), COUNTROWS ( FILTER ( _ok, [@d] < _d ) ) + 1 )""",
      ORACULO + " › entre_parecidas › posicao = 45")
conta("T15 · parecidas · menor variação", "0.0%", "A menor variação de margem (a maior queda) entre as parecidas.",
      _PARECIDAS + "\nRETURN\n    MINX ( _ok, [@d] )")
conta("T15 · parecidas · maior variação", "0.0%", "A maior variação de margem entre as parecidas.",
      _PARECIDAS + "\nRETURN\n    MAXX ( _ok, [@d] )")
conta("T15 · parecidas · contagem por faixa", "texto",
      f"Lista 'n1|n2|…|n{FAIXAS}': quantas cidades parecidas caem em cada uma de {FAIXAS} faixas iguais de variação "
      "da margem, da menor à maior. Alimenta o histograma.",
      _PARECIDAS + f"""
VAR _min = MINX ( _ok, [@d] )
VAR _max = MAXX ( _ok, [@d] )
VAR _passo = ( _max - _min ) / {FAIXAS}
RETURN
    IF (
        NOT ISBLANK ( _min ),
        CONCATENATEX (
            GENERATESERIES ( 0, {FAIXAS - 1} ),
            VAR _i = [Value]
            VAR _a = _min + _i * _passo
            VAR _b = _a + _passo
            RETURN
                COUNTROWS (
                    FILTER ( _ok, [@d] >= _a && ( [@d] < _b || ( _i = {FAIXAS - 1} && [@d] <= _max ) ) )
                ) + 0,
            "|",
            [Value], ASC
        )
    )""")


# ==================================================================================================== desenho
def _pp(v: str) -> str:
    return f'FORMAT ( {v} * 100, "+0.0;−0.0;0.0" )'


def _pct(v: str) -> str:
    return f'FORMAT ( {v}, "0.0%" )'


_VAZIO = ("\"<div class='tela t15v'><div class='ic entra'></div><div class='rot entra'>ESCOLHA UMA CIDADE</div><div class='man sobe d1'>Digite o "
          "nome da sua cidade no campo <b>Município</b>, lá em cima, à direita.</div><div class='txt entra d3'>São os "
          "5.571 municípios do Brasil. A tela mostra como ela votou de 2006 a 2026 e como se compara com as cidades "
          "parecidas.</div></div>\"")

desenho("T15 · Ficha · HTML",
        "Ficha da cidade escolhida: quem venceu e com quanto, a manchete da mudança desde 2022, os dados da cidade e os "
        "votos de Lula e do PL em 2022 e 2026. Sem cidade escolhida, o convite para escolher. Só lê contas.",
        f"""-- 1 · Leituras
VAR _ok = [T15 · cidade escolhida]
VAR _cid = [T15 · cidade]
VAR _uf = [T15 · UF da cidade]
VAR _pop = [T15 · população]
VAR _renda = [T15 · renda per capita]
VAR _porte = [T15 · porte]
VAR _quinto = [T15 · quinto de renda]
VAR _l26 = [T15 · Lula % 2026]
VAR _p26 = [T15 · PL % 2026]
VAR _m26 = [T15 · margem 2026]
VAR _var = [T15 · variação]
VAR _vl22 = [T15 · votos de Lula 2022]
VAR _vl26 = [T15 · votos de Lula 2026]
VAR _vp22 = [T15 · votos do PL 2022]
VAR _vp26 = [T15 · votos do PL 2026]
VAR _dl = [T15 · variação de votos de Lula]
VAR _dp = [T15 · variação de votos do PL]
VAR _m22 = [T15 · margem 2022]
VAR _ufNome = [T15 · nome da UF]
VAR _u22 = [T15 · margem 2022 na UF]
VAR _u26 = [T15 · margem 2026 na UF]
VAR _b22 = [T15 · margem do Brasil 2022]
VAR _b26 = [T15 · margem do Brasil 2026]
-- 2 · Textos
VAR _nome = {ESC.format(v="_cid")}
VAR _flavio = _m26 < 0
VAR _empate = _m26 = 0
VAR _venc = IF ( _flavio, "Flávio", "Lula" )
VAR _pVenc = IF ( _flavio, _p26, _l26 )
VAR _clsVenc = IF ( _flavio, "flavio", "lula" )
VAR _txtVenc = IF ( _flavio, "para Flávio Bolsonaro", "para Lula" )
VAR _txtOutro =
    IF ( _flavio, "<span class='lula'>Lula " & {_pct("_l26")} & "</span>",
        "<span class='flavio'>Flávio " & {_pct("_p26")} & "</span>" )
VAR _txtMuda =
    SWITCH (
        TRUE (),
        ISBLANK ( _var ), "a cidade não votou em 2022",
        _var < 0, "a margem de Lula caiu " & FORMAT ( ABS ( _var ) * 100, "0.0" ) & " p.p. desde 2022",
        _var > 0, "a margem de Lula subiu " & FORMAT ( _var * 100, "0.0" ) & " p.p. desde 2022",
        "a margem de Lula ficou igual à de 2022"
    )
VAR _man =
    IF (
        _empate,
        "Em " & _nome & ", Lula e Flávio empataram; " & _txtMuda,
        "Em " & _nome & ", " & _venc & " venceu com " & {_pct("_pVenc")} & "; " & _txtMuda
    )
VAR _txtQuinto =
    SWITCH ( _quinto, "mais ricas", "entre as mais ricas", "mais pobres", "entre as mais pobres",
        "no " & _quinto & " de renda" )
VAR _fatos =
    _nome & " (" & _uf & ") · " & FORMAT ( _pop, "#,0" ) & " habitantes · renda por pessoa de R$ "
        & FORMAT ( _renda, "#,0" ) & " por mês · porte " & _porte & " · " & _txtQuinto
VAR _fmtD = "+#,0;−#,0;0"
-- 3 · Geometria (três mini setas num eixo de ±escala em 300 px, zero em x 150)
VAR _esc = MAX ( 0.08, MAX ( MAX ( ABS ( _m22 ), ABS ( _m26 ) ), MAX ( MAX ( ABS ( _u22 ), ABS ( _u26 ) ), MAX ( ABS ( _b22 ), ABS ( _b26 ) ) ) ) * 1.15 ) /* geometria */
VAR _comp =
    CONCATENATEX (
        DATATABLE (
            "o", INTEGER,
            {{
                {{ 1 }}, {{ 2 }}, {{ 3 }}
            }}
        ),
        VAR _o = [o]
        VAR _rot = SWITCH ( _o, 1, _nome, 2, _ufNome, "Brasil" )
        VAR _sub = SWITCH ( _o, 1, "a cidade", 2, "o estado", "o país, com o exterior" )
        VAR _a = SWITCH ( _o, 1, _m22, 2, _u22, _b22 )
        VAR _b = SWITCH ( _o, 1, _m26, 2, _u26, _b26 )
        VAR _xa = 150 + 140 * _a / _esc
        VAR _xb = 150 + 140 * _b / _esc
        VAR _cor = IF ( _b < 0, "var(--azul)", "var(--vermelho)" )
        RETURN
            "<div class='cp sobe d" & ( 9 + _o ) & "'><div class='nm'><b>" & _rot & "</b><span>" & _sub & "</span></div>"
                & "<svg width='300' height='24' viewBox='0 0 300 24'><line x1='150' x2='150' y1='0' y2='24' class='zero'/>"
                & "<line class='traco-rapido' pathLength='1' style='animation-delay:" & ( 1300 + _o * 120 ) & "ms' x1='"
                & FORMAT ( _xa, "0.0", "en-US" ) & "' x2='" & FORMAT ( _xb, "0.0", "en-US" ) & "' y1='12' y2='12'/>"
                & "<circle cx='" & FORMAT ( _xa, "0.0", "en-US" ) & "' cy='12' r='5' class='m22'/>"
                & "<circle class='brota' style='animation-delay:" & ( 1600 + _o * 120 ) & "ms' cx='"
                & FORMAT ( _xb, "0.0", "en-US" ) & "' cy='12' r='6.5' fill='" & _cor & "'/></svg>"
                & "<div class='vv'>" & FORMAT ( _a * 100, "+0.0;−0.0;0.0" ) & " → " & FORMAT ( _b * 100, "+0.0;−0.0;0.0" )
                & "</div></div>",
        "",
        [o], ASC
    )
-- 4 · Marcação
VAR _html =
    "<div class='tela t15f'>"
        & "<div class='topo'><span class='num g " & _clsVenc & " sobe'>" & {_pct("_pVenc")} & "</span>"
            & "<span class='quem sobe d2'><b class='" & _clsVenc & "'>" & _txtVenc & "</b>" & _txtOutro & "</span></div>"
        & "<div class='man m sobe d3'>" & _man & "</div>"
        & "<div class='nota fatos entra d5'>" & _fatos & "</div>"
        & "<div class='votos'>"
            & "<div class='rot entra d6'>VOTOS NO 1º TURNO · 2022 → 2026</div>"
            & "<div class='lv sobe d7'><i class='q lula-q'></i><div class='nm'><b>Lula · PT</b><span>"
                & FORMAT ( _vl22, "#,0" ) & " → " & FORMAT ( _vl26, "#,0" ) & "</span></div><div class='num dv lula'>"
                & FORMAT ( _dl, _fmtD ) & "</div></div>"
            & "<div class='lv sobe d8'><i class='q flavio-q'></i><div class='nm'><b>Bolsonaro → Flávio · PL</b><span>"
                & FORMAT ( _vp22, "#,0" ) & " → " & FORMAT ( _vp26, "#,0" ) & "</span></div><div class='num dv flavio'>"
                & FORMAT ( _dp, _fmtD ) & "</div></div>"
            & "<div class='nota entra d9'>Votos na cidade; a diferença é de 2026 para 2022.</div>"
        & "</div>"
        & "<div class='comp'>"
            & "<div class='rot entra d9'>A CIDADE, O ESTADO E O PAÍS · MARGEM DE LULA 2022 → 2026</div>"
            & _comp
            & "<div class='nota entra d13'>Círculo vazado: 2022; cheio: 2026. À direita do traço, Lula à frente.</div>"
        & "</div>"
    & "</div>"
RETURN
    IF ( _ok = 1, _html, {_VAZIO} )""")

desenho("T15 · Ficha · ALT", "Texto alternativo da ficha da cidade.",
        f"""-- 1 · Leituras
VAR _ok = [T15 · cidade escolhida]
VAR _cid = [T15 · cidade]
VAR _l26 = [T15 · Lula % 2026]
VAR _p26 = [T15 · PL % 2026]
VAR _var = [T15 · variação]
-- 2 · Textos
RETURN
    IF (
        _ok = 1,
        _cid & ": em 2026, Lula " & {_pct("_l26")} & " e Flávio " & {_pct("_p26")} & "; a margem de Lula variou "
            & {_pp("_var")} & " pontos desde 2022.",
        "Nenhuma cidade escolhida: use o filtro de município."
    )""")

desenho("T15 · Série título · HTML", "Título da série da cidade: de onde a margem saiu, aonde chegou e quando virou.",
        f"""-- 1 · Leituras
VAR _ok = [T15 · cidade escolhida]
VAR _cid = [T15 · cidade]
VAR _a0 = [T15 · primeiro ano]
VAR _m0 = [T15 · margem no primeiro ano]
VAR _m26 = [T15 · margem 2026]
VAR _troca = [T15 · última troca de lado]
VAR _nTrocas = [T15 · trocas de lado]
VAR _paraPT = [T15 · PT à frente na última troca]
-- 2 · Textos
VAR _nome = {ESC.format(v="_cid")}
VAR _txtTroca =
    SWITCH (
        TRUE (),
        _nTrocas = 0 && _m26 > 0, "o PT ficou à frente em todas",
        _nTrocas = 0, "o adversário ficou à frente em todas",
        _paraPT = 1, _nome & " voltou para o PT em " & _troca,
        _nome & " virou para o adversário em " & _troca & IF ( _troca < 2026, ", não em 2026", "" )
    )
VAR _man =
    "De " & {_pp("_m0")} & " p.p. em " & _a0 & " a " & {_pp("_m26")} & " p.p. em 2026; " & _txtTroca
-- 4 · Marcação
RETURN
    IF (
        _ok = 1,
        "<div class='tela t15t'>"
            & "<div class='rot entra'>MARGEM DO PT EM " & UPPER ( _nome ) & " · " & _a0 & " → 2026</div>"
            & "<div class='man sobe d1'>" & _man & "</div>"
            & "<div class='leg entra d2'><span><i class='pt'></i>PT à frente</span><span><i class='adv'></i>adversário à "
                & "frente</span></div>"
        & "</div>"
    )""")

desenho("T15 · Série título · ALT", "Texto alternativo do título da série.",
        """-- 1 · Leituras
VAR _cid = [T15 · cidade]
VAR _troca = [T15 · última troca de lado]
-- 2 · Textos
RETURN
    "Margem do PT em " & _cid & " a cada eleição de 2006 a 2026"
        & IF ( ISBLANK ( _troca ), ".", "; a última troca de lado foi em " & _troca & "." )""")

desenho("T15 · Série · HTML",
        "Uma entrada por eleição (granularidade Ano): a barra da margem do PT na cidade (para cima, PT à frente; para "
        "baixo, o adversário), o valor, o ano e os percentuais. Na de 2026, a nota à mão com a mudança desde 2022.",
        f"""-- 1 · Leituras
VAR _ok = [T15 · cidade escolhida]
VAR _ano = [T15 · ano]
VAR _m = [T15 · margem no ano]
VAR _pt = [T15 · PT % no ano]
VAR _adv = [T15 · adversário % no ano]
VAR _esc = [T15 · maior margem absoluta]
VAR _var = [T15 · variação]
VAR _troca = [T15 · última troca de lado]
-- 2 · Textos
VAR _cls = IF ( _m < 0, "adv", "pt" )
VAR _nota =
    IF (
        _ano = 2026 && NOT ISBLANK ( _var ),
        "<div class='mao nt entra' style='left:" & FORMAT ( 84 + 5 * 168 - 290, "0", "en-US" ) & "px;top:"
            & IF ( _m >= 0, "200", "34" ) & "px'>" & IF ( _var < 0, "caiu ", "subiu " ) & FORMAT ( ABS ( _var ) * 100, "0.0" )
            & " desde 2022</div>"
    )
VAR _virou =
    IF ( _ano = _troca, "<div class='mao vr entra' style='left:{{X}}px;top:{{Y}}px'>virou aqui</div>" )
-- 3 · Geometria (anos a cada 168 px; barra de 100 px; zero em y 160; maior margem = 110 px)
VAR _i = ( _ano - 2006 ) / 4
VAR _xc = 84 + _i * 168
VAR _h = 110 * ABS ( _m ) / MAX ( _esc, 0.02 )
VAR _top = IF ( _m >= 0, 160 - _h, 160 )
VAR _yRot = IF ( _m >= 0, 160 - _h - 32, 160 + _h + 4 )
-- 4 · Marcação
RETURN
    IF (
        _ok = 1 && NOT ISBLANK ( _m ),
        "<div class='tela br'>"
            & "<div class='alvo' style='left:" & FORMAT ( _xc - 80, "0.0", "en-US" ) & "px'></div>"
            & "<div class='bar " & _cls & IF ( _m >= 0, " barra-y", " desce" ) & "' style='left:"
                & FORMAT ( _xc - 50, "0.0", "en-US" ) & "px;top:" & FORMAT ( _top, "0.0", "en-US" ) & "px;height:"
                & FORMAT ( MAX ( _h, 1.5 ), "0.0", "en-US" ) & "px;animation-delay:" & ( 200 + _i * 120 ) & "ms'></div>"
            & "<div class='vl " & _cls & " sobe' style='left:" & FORMAT ( _xc - 70, "0.0", "en-US" ) & "px;top:"
                & FORMAT ( _yRot, "0.0", "en-US" ) & "px;animation-delay:" & ( 500 + _i * 120 ) & "ms'>" & {_pp("_m")}
                & "</div>"
            & "<div class='xl' style='left:" & FORMAT ( _xc - 84, "0.0", "en-US" ) & "px'><b>" & _ano & "</b><span>"
                & {_pct("_pt")} & " × " & {_pct("_adv")} & "</span></div>"
            & IF ( _ano = 2006, "<div class='zero'></div>", "" )
            & _nota
            & SUBSTITUTE (
                SUBSTITUTE ( _virou, "{{X}}", FORMAT ( _xc - 46, "0.0", "en-US" ) ),
                "{{Y}}",
                FORMAT ( IF ( _m >= 0, _yRot - 30, _yRot + 30 ), "0.0", "en-US" )
            )
        & "</div>"
    )""")

desenho("T15 · Série · ALT", "Texto alternativo da série da cidade.",
        """-- 1 · Leituras
VAR _cid = [T15 · cidade]
-- 2 · Textos
RETURN
    "Barras da margem do PT em " & _cid & " em cada 1º turno de 2006 a 2026: para cima, PT à frente; para baixo, o "
        & "adversário. Passe o mouse num ano para ver a votação daquele ano.\"""")

desenho("T15 · Parecidas · HTML",
        "Entre as cidades parecidas (mesmo porte e quinto de renda): a posição da cidade na queda, a variação do grupo "
        "e o histograma das variações com a cidade marcada. Só lê contas.",
        f"""-- 1 · Leituras
VAR _ok = [T15 · cidade escolhida]
VAR _cid = [T15 · cidade]
VAR _n = [T15 · parecidas · quantidade]
VAR _pos = [T15 · parecidas · posição]
VAR _vg = [T15 · parecidas · variação do grupo]
VAR _var = [T15 · variação]
VAR _min = [T15 · parecidas · menor variação]
VAR _max = [T15 · parecidas · maior variação]
VAR _lista = [T15 · parecidas · contagem por faixa]
VAR _porte = [T15 · porte]
VAR _quinto = [T15 · quinto de renda]
-- 2 · Textos
VAR _nome = {ESC.format(v="_cid")}
VAR _grupo =
    "cidades de " & _porte & IF ( RIGHT ( _porte, 3 ) = "mil", " habitantes", " de habitantes" ) & " e renda "
        & SWITCH ( _quinto, "mais ricas", "entre as mais ricas", "mais pobres", "entre as mais pobres", "no " & _quinto )
VAR _txtPos =
    IF ( _n = 1, "a única do grupo", FORMAT ( _pos, "0" ) & "ª maior queda de " & FORMAT ( _n, "#,0" ) )
VAR _txtComp =
    IF (
        _n = 1,
        _nome & " é a única entre as " & _grupo & ": não há com quem comparar.",
        _grupo & "; o grupo " & IF ( _vg < 0, "caiu ", "subiu " ) & FORMAT ( ABS ( _vg ) * 100, "0.0" ) & " p.p., "
            & _nome & IF ( _var < 0, " caiu ", " subiu " ) & FORMAT ( ABS ( _var ) * 100, "0.0" ) & " p.p."
    )
-- 3 · Geometria (histograma de {FAIXAS} faixas em 1000 px; altura até 104 px, base em y 280)
VAR _faixas =
    ADDCOLUMNS (
        GENERATESERIES ( 1, {FAIXAS} ),
        "@n", VALUE ( PATHITEM ( _lista, [Value] ) )
    )
VAR _nMax = MAXX ( _faixas, [@n] ) /* geometria */
VAR _larg = 1000 / {FAIXAS}
VAR _passo = ( _max - _min ) / {FAIXAS}
VAR _faixaCid = IF ( _passo = 0, {FAIXAS}, MIN ( {FAIXAS}, INT ( ( _var - _min ) / _passo ) + 1 ) )
VAR _xCid = 1000 * DIVIDE ( _var - _min, _max - _min, 0.5 ) /* geometria */
VAR _xGrupo = 1000 * DIVIDE ( _vg - _min, _max - _min, 0.5 ) /* geometria */
VAR _barras =
    CONCATENATEX (
        _faixas,
        VAR _h = 104 * DIVIDE ( [@n], _nMax ) /* geometria */
        RETURN
            "<rect class='" & IF ( [Value] = _faixaCid, "hb cid", "hb" ) & " barra-y' style='animation-delay:"
                & ( 300 + [Value] * 30 ) & "ms' x='" & FORMAT ( ( [Value] - 1 ) * _larg + 2, "0.0", "en-US" )
                & "' y='" & FORMAT ( 280 - _h, "0.0", "en-US" ) & "' width='" & FORMAT ( _larg - 4, "0.0", "en-US" )
                & "' height='" & FORMAT ( _h, "0.0", "en-US" ) & "'/>",
        "",
        [Value], ASC
    )
-- 4 · Marcação
RETURN
    IF (
        _ok = 1 && NOT ISBLANK ( _n ),
        "<div class='tela t15p'>"
            & "<div class='rot entra'>" & IF ( _n = 1, "SEM CIDADES PARECIDAS", "ENTRE AS " & FORMAT ( _n, "#,0" )
                & " CIDADES PARECIDAS" ) & " · MESMO PORTE E MESMA RENDA</div>"
            & "<div class='pos sobe d1'>" & _txtPos & "</div>"
            & "<div class='txt comp entra d3'>" & _txtComp & "</div>"
            & IF (
                _n > 1,
                "<svg class='hist' width='1010' height='300' viewBox='0 0 1010 300'>"
                    & "<line class='eixo' x1='0' x2='1000' y1='280' y2='280'/>"
                    & _barras
                    & "<line class='grupo traco' pathLength='1' style='animation-delay:1100ms' x1='"
                        & FORMAT ( _xGrupo, "0.0", "en-US" ) & "' x2='" & FORMAT ( _xGrupo, "0.0", "en-US" )
                        & "' y1='168' y2='282'/>"
                    & "<line class='cidade traco' pathLength='1' style='animation-delay:1300ms' x1='"
                        & FORMAT ( _xCid, "0.0", "en-US" ) & "' x2='" & FORMAT ( _xCid, "0.0", "en-US" ) & "' y1='150' y2='282'/>"
                    & "<text class='tk' x='0' y='298'>" & {_pp("_min")} & "</text>"
                    & "<text class='tk' x='1000' y='298' text-anchor='end'>" & {_pp("_max")} & "</text>"
                    & "<text class='tk' x='500' y='298' text-anchor='middle'>quanto variou a margem de Lula em cada cidade "
                        & "parecida, 2022 → 2026, em pontos; cada barra junta as cidades de uma faixa"
                        & "</text>"
                & "</svg>"
                & "<div class='rc cid entra d8' style='left:" & FORMAT ( _xCid - 120, "0.0", "en-US" ) & "px'><span>" & _nome
                    & " " & {_pp("_var")} & "</span></div>"
                & "<div class='rc grp entra d9' style='left:" & FORMAT ( _xGrupo - 120, "0.0", "en-US" ) & "px'><span>grupo "
                    & {_pp("_vg")} & "</span></div>",
                ""
            )
        & "</div>"
    )""")

desenho("T15 · Parecidas · ALT", "Texto alternativo das cidades parecidas.",
        f"""-- 1 · Leituras
VAR _cid = [T15 · cidade]
VAR _n = [T15 · parecidas · quantidade]
VAR _pos = [T15 · parecidas · posição]
VAR _vg = [T15 · parecidas · variação do grupo]
-- 2 · Textos
RETURN
    _cid & ": " & FORMAT ( _pos, "0" ) & "ª maior queda de margem entre " & FORMAT ( _n, "#,0" )
        & " cidades parecidas; o grupo variou " & {_pp("_vg")} & " pontos.\"""")

desenho("T15 · Tooltip ano · HTML",
        "Dossiê da eleição na cidade: PT, adversário e os demais candidatos em barras, a abstenção e os nomes. Só lê "
        "contas.",
        f"""-- 1 · Leituras
VAR _cid = [T15 · cidade]
VAR _ano = [T15 · ano]
VAR _pt = [T15 · PT % no ano]
VAR _adv = [T15 · adversário % no ano]
VAR _out = [T15 · outros % no ano]
VAR _abs = [T15 · abstenção no ano]
VAR _cpt = [T15 · candidato do PT]
VAR _cadv = [T15 · adversário]
VAR _troca = [T15 · última troca de lado]
VAR _m = [T15 · margem no ano]
-- 2 · Textos
VAR _nome = {ESC.format(v="_cid")}
VAR _selo = IF ( _m < 0, "ADVERSÁRIO À FRENTE", "PT À FRENTE" )
VAR _clsSelo = IF ( _m < 0, "selo az", "selo vm" )
VAR _mao =
    SWITCH (
        TRUE (),
        _ano = _troca, "o ano da virada",
        _out >= 0.15, "muito voto em outros nomes",
        "PT × adversário, só os dois"
    )
-- 3 · Geometria (barras: 70% = 200 px)
VAR _wpt = FORMAT ( 200 * MIN ( 1, _pt / 0.7 ), "0.0", "en-US" )
VAR _wadv = FORMAT ( 200 * MIN ( 1, _adv / 0.7 ), "0.0", "en-US" )
VAR _wout = FORMAT ( 200 * MIN ( 1, _out / 0.7 ), "0.0", "en-US" )
-- 4 · Marcação
RETURN
    "<div class='tela tt15'><div class='fita'></div>"
        & "<div class='" & _clsSelo & "'>" & _selo & "</div>"
        & "<div class='an sobe'>" & _ano & " em " & _nome & "</div>"
        & "<div class='rot entra d1'>VOTOS VÁLIDOS NO 1º TURNO</div>"
        & "<div class='cl entra d2'><span class='nm'>" & _cpt & " <i>PT</i></span><span class='tr'><b class='barra-x pt' "
            & "style='width:" & _wpt & "px'></b></span><span class='pc'>" & {_pct("_pt")} & "</span></div>"
        & "<div class='cl entra d3'><span class='nm'>" & _cadv & "</span><span class='tr'><b class='barra-x adv' "
            & "style='width:" & _wadv & "px'></b></span><span class='pc'>" & {_pct("_adv")} & "</span></div>"
        & "<div class='cl entra d4'><span class='nm'>os demais</span><span class='tr'><b class='barra-x' style='width:"
            & _wout & "px'></b></span><span class='pc'>" & {_pct("_out")} & "</span></div>"
        & "<div class='nota entra d5'>Faltaram " & {_pct("_abs")} & " dos eleitores da cidade.</div>"
        & "<div class='mao entra d6'>" & _mao & "</div>"
    & "</div>\"""")

desenho("T15 · Tooltip ano · ALT", "Texto alternativo do dossiê da eleição na cidade.",
        f"""-- 1 · Leituras
VAR _cid = [T15 · cidade]
VAR _ano = [T15 · ano]
VAR _pt = [T15 · PT % no ano]
VAR _adv = [T15 · adversário % no ano]
-- 2 · Textos
RETURN
    _cid & " em " & _ano & ": PT " & {_pct("_pt")} & ", adversário " & {_pct("_adv")} & \".\"""")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gravar()
    print(f"T15: {len(MEDIDAS)} medidas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
