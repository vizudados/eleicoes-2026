# -*- coding: utf-8 -*-
"""desenho_t15 — gera as medidas da tela 15 · Minha cidade (contas e desenho).

    python -X utf8 pbi/scripts/desenho_t15.py

Grava pbi/dax/T15 Minha cidade/{Contas,Desenho}/*.dax. Tudo responde ao filtro de município da tela (VizuFilter sobre
Município[Rótulo], cidade inicial Ananindeua (PA)). As contas da cidade somam Município ano (sem o exterior, que não tem
município). "Entre as cidades parecidas" = mesmo porte e mesmo quinto de renda, em todo o Brasil (ignora o filtro).

Viagem no tempo (23/10/2026): clicar numa barra da série filtra o Ano; a ficha e as parecidas passam a contar a eleição
escolhida contra a anterior (ano escolhido − 4). Sem clique, o ano escolhido é 2026 e a tela é a de antes, texto por
texto (2022 → 2026, conferido contra o oráculo). Em 2006 não há eleição anterior na série: a ficha mostra só o ano.

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

conta("T15 · nome e UF da cidade", "texto", "Nome (UF) do município escolhido no filtro, como a lista do filtro mostra.",
      "SELECTEDVALUE ( 'Município'[Rótulo] )", ORACULO + " › Contagem (MG)")

# ---- a eleição escolhida (clique numa barra da série) e a anterior
conta("T15 · ano escolhido", "0",
      "Eleição que a ficha e as parecidas contam: a barra clicada na série (filtro cruzado no Ano) ou, sem clique, 2026.",
      """IF ( ISFILTERED ( 'Ano'[Ano] ) && HASONEVALUE ( 'Ano'[Ano] ), VALUES ( 'Ano'[Ano] ), 2026 )""",
      ORACULO + " › 2026 sem clique")
conta("T15 · ano anterior", "0", "A eleição antes da escolhida (quatro anos antes); vazio em 2006, o começo da série.",
      """VAR _a = [T15 · ano escolhido]
RETURN
    IF ( _a > 2006, _a - 4 )""", ORACULO + " › 2022 sem clique")
conta("T15 · margem 2026", "0.0%", "Margem de Lula em 2026 no município: (Lula − Flávio) ÷ válidos. Fixa em 2026 (título "
      "da série), não muda com o clique.",
      f"DIVIDE ( {_soma('VotosPT', 2026)} - {_soma('VotosAdversario', 2026)}, {_soma('Validos', 2026)} )",
      ORACULO + " › margem26_txt = −11,0")

for _q, _qual in (("escolhido", "escolhido"), ("anterior", "anterior")):
    _ler = f"VAR _a = [T15 · ano {_qual}]"
    _guarda = "IF ( NOT ISBLANK ( _a ), " if _q == "anterior" else ""
    _fim = " )" if _q == "anterior" else ""
    _desc = "na eleição escolhida (2026 sem clique)" if _q == "escolhido" else "na eleição anterior à escolhida (2022 sem clique)"
    for _nome, _col, _orc in (("votos do PT", "VotosPT", "lula"), ("votos do adversário", "VotosAdversario", "pl"),
                              ("válidos", "Validos", None)):
        conta(f"T15 · {_nome} no ano {_q}", "#,0", f"{_nome.capitalize()} {_desc}, no município.",
              f"""{_ler}
RETURN
    {_guarda}CALCULATE ( SUM ( 'Município ano'[{_col}] ), 'Ano'[Ano] = _a ){_fim}""",
              (ORACULO + f" › votos › {_orc}{'26' if _q == 'escolhido' else '22'}") if _orc else None)
    conta(f"T15 · margem no ano {_q}", "0.0%", f"Margem do PT {_desc}, no município: (PT − adversário) ÷ válidos.",
          f"DIVIDE ( [T15 · votos do PT no ano {_q}] - [T15 · votos do adversário no ano {_q}], "
          f"[T15 · válidos no ano {_q}] )", ORACULO + f" › margem{'26' if _q == 'escolhido' else '22'}_txt")
    conta(f"T15 · candidato do PT no ano {_q}", "texto", f"Candidato do PT {_desc}.",
          f"""{_ler}
RETURN
    {_guarda}CALCULATE ( SELECTEDVALUE ( 'Ano'[Candidato do PT] ), 'Ano'[Ano] = _a ){_fim}""")
    conta(f"T15 · adversário no ano {_q}", "texto", f"Adversário principal (o mais votado fora do PT) {_desc}.",
          f"""{_ler}
RETURN
    {_guarda}CALCULATE ( SELECTEDVALUE ( 'Ano'[Adversário] ), 'Ano'[Ano] = _a ){_fim}""")
    conta(f"T15 · partido do adversário no ano {_q}", "texto", f"Partido do adversário principal {_desc}.",
          f"""{_ler}
RETURN
    {_guarda}CALCULATE ( SELECTEDVALUE ( 'Ano'[Partido do adversário] ), 'Ano'[Ano] = _a ){_fim}""")
    conta(f"T15 · margem na UF no ano {_q}", "0.0%",
          f"Margem do PT {_desc} na UF da cidade, somando os municípios dela (igual à conta da tela 12).",
          f"""VAR _uf = [T15 · UF da cidade]
{_ler}
RETURN
    IF (
        NOT ISBLANK ( _uf ) && NOT ISBLANK ( _a ),
        CALCULATE (
            [T15 · margem no ano],
            REMOVEFILTERS ( 'Município' ),
            REMOVEFILTERS ( 'UF' ),
            'Município'[UF] = _uf,
            'Ano'[Ano] = _a
        )
    )""", "paginas[12] › ufs › margem (MG +4,7 → −4,9)")
    conta(f"T15 · margem do Brasil no ano {_q}", "0.0%",
          f"Margem do PT no Brasil {_desc}, resultado oficial com o exterior (igual às telas 01, 12 e 15).",
          f"""{_ler}
RETURN
    {_guarda}DIVIDE (
        CALCULATE ( SUM ( 'Candidato ano'[Votos] ), 'Ano'[Ano] = _a, 'Candidato ano'[Partido] = "PT" )
            - CALCULATE ( MAX ( 'Candidato ano'[Votos] ), 'Ano'[Ano] = _a, 'Candidato ano'[Partido] <> "PT" ),
        CALCULATE ( MAX ( 'Candidato ano'[ValidosAno] ), 'Ano'[Ano] = _a )
    ){_fim}""", "paginas[14] › anos (2022 +5,2; 2026 −1,9)")

conta("T15 · PT % no ano escolhido", "0.0%", "Votos do PT sobre os válidos na eleição escolhida, no município.",
      "DIVIDE ( [T15 · votos do PT no ano escolhido], [T15 · válidos no ano escolhido] )",
      ORACULO + " › serie 2026 › pt 39,3%")
conta("T15 · adversário % no ano escolhido", "0.0%",
      "Votos do adversário principal sobre os válidos na eleição escolhida, no município.",
      "DIVIDE ( [T15 · votos do adversário no ano escolhido], [T15 · válidos no ano escolhido] )",
      ORACULO + " › serie 2026 › adv 50,3%")
conta("T15 · variação", "0.0%",
      "Variação da margem do PT da eleição anterior para a escolhida (sem clique, 2022 → 2026), somando os votos do "
      "contexto; vazia em 2006.",
      """VAR _ant = [T15 · margem no ano anterior]
RETURN
    IF ( NOT ISBLANK ( _ant ), [T15 · margem no ano escolhido] - _ant )""", ORACULO + " › variacao_txt = −5,4 p.p.")
conta("T15 · variação de votos do PT", "#,0", "Votos do PT na eleição escolhida menos na anterior, no município.",
      """VAR _ant = [T15 · votos do PT no ano anterior]
RETURN
    IF ( NOT ISBLANK ( _ant ), [T15 · votos do PT no ano escolhido] - _ant )""",
      ORACULO + " › votos › variacao_lula_txt = −11.920")
conta("T15 · variação de votos do adversário", "#,0",
      "Votos do adversário principal na eleição escolhida menos os do adversário na anterior, no município.",
      """VAR _ant = [T15 · votos do adversário no ano anterior]
RETURN
    IF ( NOT ISBLANK ( _ant ), [T15 · votos do adversário no ano escolhido] - _ant )""",
      ORACULO + " › votos › variacao_pl_txt = +6.957")

conta("T15 · nome da UF", "texto", "Nome da UF do município escolhido.",
      "LOOKUPVALUE ( 'UF'[Nome], 'UF'[UF], [T15 · UF da cidade] )")
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

def _curto(v: str) -> str:
    """Nome curto do candidato (Dilma, Haddad, Aécio, Bolsonaro, Flávio…) para frases e rótulos."""
    return (f'SWITCH ( {v}, "Dilma Rousseff", "Dilma", "Fernando Haddad", "Haddad", "Geraldo Alckmin", "Alckmin", '
            f'"José Serra", "Serra", "Aécio Neves", "Aécio", "Jair Bolsonaro", "Bolsonaro", "Flávio Bolsonaro", '
            f'"Flávio", {v} )')


desenho("T15 · Ficha · HTML",
        "Ficha da cidade escolhida na eleição escolhida (sem clique, 2026 contra 2022): quem ficou à frente e com "
        "quanto, a manchete da mudança desde a eleição anterior, os dados da cidade, os votos do PT e do adversário nas "
        "duas eleições e a margem na cidade, no estado e no país. Sem cidade escolhida, o convite para escolher. Só lê "
        "contas.",
        f"""-- 1 · Leituras
VAR _ok = [T15 · cidade escolhida]
VAR _cid = [T15 · cidade]
VAR _uf = [T15 · UF da cidade]
VAR _pop = [T15 · população]
VAR _renda = [T15 · renda per capita]
VAR _porte = [T15 · porte]
VAR _quinto = [T15 · quinto de renda]
VAR _y = [T15 · ano escolhido]
VAR _y0 = [T15 · ano anterior]
VAR _pt = [T15 · PT % no ano escolhido]
VAR _ad = [T15 · adversário % no ano escolhido]
VAR _mB = [T15 · margem no ano escolhido]
VAR _mA = [T15 · margem no ano anterior]
VAR _var = [T15 · variação]
VAR _vt0 = [T15 · votos do PT no ano anterior]
VAR _vt1 = [T15 · votos do PT no ano escolhido]
VAR _va0 = [T15 · votos do adversário no ano anterior]
VAR _va1 = [T15 · votos do adversário no ano escolhido]
VAR _dt = [T15 · variação de votos do PT]
VAR _da = [T15 · variação de votos do adversário]
VAR _cpt1 = [T15 · candidato do PT no ano escolhido]
VAR _cpt0 = [T15 · candidato do PT no ano anterior]
VAR _cad1 = [T15 · adversário no ano escolhido]
VAR _cad0 = [T15 · adversário no ano anterior]
VAR _pad1 = [T15 · partido do adversário no ano escolhido]
VAR _pad0 = [T15 · partido do adversário no ano anterior]
VAR _ufNome = [T15 · nome da UF]
VAR _uA = [T15 · margem na UF no ano anterior]
VAR _uB = [T15 · margem na UF no ano escolhido]
VAR _bA = [T15 · margem do Brasil no ano anterior]
VAR _bB = [T15 · margem do Brasil no ano escolhido]
-- 2 · Textos
VAR _nome = {ESC.format(v="_cid")}
VAR _clique = _y <> 2026
VAR _tem0 = NOT ISBLANK ( _y0 )
VAR _sPt = {_curto("_cpt1")}
VAR _sPt0 = {_curto("_cpt0")}
VAR _sAd = {_curto("_cad1")}
VAR _sAd0 = {_curto("_cad0")}
VAR _flavio = _mB < 0
VAR _empate = _mB = 0
VAR _venc = IF ( _flavio, _sAd, _sPt )
VAR _pVenc = IF ( _flavio, _ad, _pt )
VAR _clsVenc = IF ( _flavio, "flavio", "lula" )
VAR _txtVenc = "para " & IF ( _flavio, _cad1, _cpt1 )
VAR _txtOutro =
    IF ( _flavio, "<span class='lula'>" & _sPt & " " & {_pct("_pt")} & "</span>",
        "<span class='flavio'>" & _sAd & " " & {_pct("_ad")} & "</span>" )
VAR _dono = IF ( _tem0 && _cpt0 = _cpt1, "de " & _sPt, "do PT" )
VAR _txtMuda =
    SWITCH (
        TRUE (),
        NOT _tem0, "é o começo da série",
        ISBLANK ( _var ), "a cidade não votou em " & _y0,
        _var < 0, "a margem " & _dono & " caiu " & FORMAT ( ABS ( _var ) * 100, "0.0" ) & " p.p. desde " & _y0,
        _var > 0, "a margem " & _dono & " subiu " & FORMAT ( _var * 100, "0.0" ) & " p.p. desde " & _y0,
        "a margem " & _dono & " ficou igual à de " & _y0
    )
VAR _onde = IF ( _clique, "Em " & _y, "Em " & _nome )
VAR _man =
    SWITCH (
        TRUE (),
        _empate, _onde & ", " & _sPt & " e " & _sAd & " empataram; " & _txtMuda,
        _clique, _onde & ", " & _venc & " ficou à frente com " & {_pct("_pVenc")} & "; " & _txtMuda,
        _onde & ", " & _venc & " venceu com " & {_pct("_pVenc")} & "; " & _txtMuda
    )
VAR _txtQuinto =
    SWITCH ( _quinto, "mais ricas", "entre as mais ricas", "mais pobres", "entre as mais pobres",
        "no " & _quinto & " de renda" )
VAR _fatos =
    _nome & " (" & _uf & ") · " & FORMAT ( _pop, "#,0" ) & " habitantes · renda por pessoa de R$ "
        & FORMAT ( _renda, "#,0" ) & " por mês · porte " & _porte & " · " & _txtQuinto
VAR _fmtD = "+#,0;−#,0;0"
VAR _anos = IF ( _tem0, _y0 & " → " & _y, FORMAT ( _y, "0" ) )
VAR _rotPt = IF ( _tem0 && _cpt0 <> _cpt1, _sPt0 & " → ", "" ) & _sPt & " · PT"
VAR _rotAd =
    SWITCH (
        TRUE (),
        NOT _tem0 || _cad0 = _cad1, _sAd & " · " & _pad1,
        _pad0 = _pad1, _sAd0 & " → " & _sAd & " · " & _pad1,
        _sAd0 & " · " & _pad0 & " → " & _sAd & " · " & _pad1
    )
VAR _txtVotosPt = IF ( _tem0, FORMAT ( _vt0, "#,0" ) & " → " & FORMAT ( _vt1, "#,0" ), "votos em " & _y )
VAR _txtVotosAd = IF ( _tem0, FORMAT ( _va0, "#,0" ) & " → " & FORMAT ( _va1, "#,0" ), "votos em " & _y )
VAR _numPt = IF ( _tem0, FORMAT ( _dt, _fmtD ), FORMAT ( _vt1, "#,0" ) )
VAR _numAd = IF ( _tem0, FORMAT ( _da, _fmtD ), FORMAT ( _va1, "#,0" ) )
VAR _notaVotos =
    IF ( _tem0, "Votos na cidade; a diferença é de " & _y & " para " & _y0 & ".",
        "Votos na cidade em " & _y & ", o começo da série." )
VAR _mesmo = NOT _tem0 || _cpt0 = _cpt1
VAR _quemMargem = IF ( _mesmo, UPPER ( "de " & _sPt ), "DO PT" )
VAR _notaComp =
    IF ( _tem0, "Círculo vazado: " & _y0 & "; cheio: " & _y & ".", "Cada círculo é " & _y & "." )
        & " À direita do traço, " & IF ( _mesmo, _sPt, "o PT" ) & " à frente."
-- 3 · Geometria (três mini setas num eixo de ±escala em 300 px, zero em x 150)
VAR _esc = MAX ( 0.08, MAX ( MAX ( ABS ( _mA ), ABS ( _mB ) ), MAX ( MAX ( ABS ( _uA ), ABS ( _uB ) ), MAX ( ABS ( _bA ), ABS ( _bB ) ) ) ) * 1.15 ) /* geometria */
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
        VAR _a = SWITCH ( _o, 1, _mA, 2, _uA, _bA )
        VAR _b = SWITCH ( _o, 1, _mB, 2, _uB, _bB )
        VAR _xa = 150 + 140 * _a / _esc
        VAR _xb = 150 + 140 * _b / _esc
        VAR _cor = IF ( _b < 0, "var(--azul)", "var(--vermelho)" )
        RETURN
            "<div class='cp sobe d" & ( 9 + _o ) & "'><div class='nm'><b>" & _rot & "</b><span>" & _sub & "</span></div>"
                & "<svg width='300' height='24' viewBox='0 0 300 24'><line x1='150' x2='150' y1='0' y2='24' class='zero'/>"
                & IF (
                    _tem0,
                    "<line class='traco-rapido' pathLength='1' style='animation-delay:" & ( 1300 + _o * 120 ) & "ms' x1='"
                        & FORMAT ( _xa, "0.0", "en-US" ) & "' x2='" & FORMAT ( _xb, "0.0", "en-US" ) & "' y1='12' y2='12'/>"
                        & "<circle cx='" & FORMAT ( _xa, "0.0", "en-US" ) & "' cy='12' r='5' class='m22'/>"
                )
                & "<circle class='brota' style='animation-delay:" & ( 1600 + _o * 120 ) & "ms' cx='"
                & FORMAT ( _xb, "0.0", "en-US" ) & "' cy='12' r='6.5' fill='" & _cor & "'/></svg>"
                & "<div class='vv'>" & IF ( _tem0, FORMAT ( _a * 100, "+0.0;−0.0;0.0" ) & " → ", "" )
                & FORMAT ( _b * 100, "+0.0;−0.0;0.0" ) & "</div></div>",
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
            & "<div class='rot entra d6'>VOTOS NO 1º TURNO · " & _anos & "</div>"
            & "<div class='lv sobe d7'><i class='q lula-q'></i><div class='nm'><b>" & _rotPt & "</b><span>"
                & _txtVotosPt & "</span></div><div class='num dv lula'>" & _numPt & "</div></div>"
            & "<div class='lv sobe d8'><i class='q flavio-q'></i><div class='nm'><b>" & _rotAd & "</b><span>"
                & _txtVotosAd & "</span></div><div class='num dv flavio'>" & _numAd & "</div></div>"
            & "<div class='nota entra d9'>" & _notaVotos & "</div>"
        & "</div>"
        & "<div class='comp'>"
            & "<div class='rot entra d9'>A CIDADE, O ESTADO E O PAÍS · MARGEM " & _quemMargem & " "
                & IF ( _tem0, _anos, "EM " & _y ) & "</div>"
            & _comp
            & "<div class='nota entra d13'>" & _notaComp & "</div>"
        & "</div>"
    & "</div>"
RETURN
    IF ( _ok = 1, _html, {_VAZIO} )""")

desenho("T15 · Ficha · ALT", "Texto alternativo da ficha da cidade.",
        f"""-- 1 · Leituras
VAR _ok = [T15 · cidade escolhida]
VAR _cid = [T15 · cidade]
VAR _y = [T15 · ano escolhido]
VAR _y0 = [T15 · ano anterior]
VAR _pt = [T15 · PT % no ano escolhido]
VAR _ad = [T15 · adversário % no ano escolhido]
VAR _var = [T15 · variação]
VAR _cpt1 = [T15 · candidato do PT no ano escolhido]
VAR _cpt0 = [T15 · candidato do PT no ano anterior]
VAR _cad1 = [T15 · adversário no ano escolhido]
-- 2 · Textos
VAR _sPt = {_curto("_cpt1")}
VAR _sAd = {_curto("_cad1")}
VAR _dono = IF ( NOT ISBLANK ( _y0 ) && _cpt0 = _cpt1, "de " & _sPt, "do PT" )
RETURN
    IF (
        _ok = 1,
        _cid & ": em " & _y & ", " & _sPt & " " & {_pct("_pt")} & " e " & _sAd & " " & {_pct("_ad")}
            & IF (
                ISBLANK ( _var ),
                ".",
                "; a margem " & _dono & " variou " & {_pp("_var")} & " pontos desde " & _y0 & "."
            ),
        "Nenhuma cidade escolhida: use o filtro de município."
    )""")

desenho("T15 · Filtro · pílula · HTML",
        "O botão fechado do filtro de município (a pílula, no lugar do filtro da casca): a cidade em uso ou o convite, "
        "com o funil e a seta. O clique abre o VizuFilter alto por cima (marcador T15_FILTRO_ABRE_01).",
        f"""-- 1 · Leituras
VAR _cid = [T15 · nome e UF da cidade]
-- 2 · Textos
VAR _txt = IF ( ISBLANK ( _cid ), "Escolha uma cidade", _cid )
VAR _esc = {ESC.format(v="_txt")}
-- 4 · Marcação
RETURN
    "<div class='tela pl" & IF ( ISBLANK ( _cid ), "", " ativo" ) & "'><span class='fu'><svg width='16' height='16' "
        & "viewBox='0 0 16 16'><path d='M2 3h12l-4.6 5.4V13l-2.8-1.4V8.4z' fill='none' stroke='currentColor' "
        & "stroke-width='1.4' stroke-linejoin='round'/></svg><i></i></span><span class='rt'>Município</span><b>" & _esc
        & "</b><svg class='sv' width='12' height='12' viewBox='0 0 12 12'><path d='M3 4.5l3 3 3-3' fill='none' "
        & "stroke='currentColor' stroke-width='1.4' stroke-linecap='round'/></svg></div>\"""")

desenho("T15 · Filtro · pílula · ALT", "Texto alternativo do filtro de município (pílula e lista).",
        """-- 1 · Leituras
VAR _cid = [T15 · nome e UF da cidade]
-- 2 · Textos
RETURN
    IF ( ISBLANK ( _cid ), "Filtro de município: nenhuma cidade escolhida", "Filtro de município: " & _cid )""")

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
        _nome & " virou para o adversário em " & _troca & IF ( _troca < 2026, " e não voltou mais", "" )
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
        & "adversário. Passe o mouse num ano para ver a votação; clique para levar a ficha àquela eleição.\"""")

desenho("T15 · Parecidas · HTML",
        "Entre as cidades parecidas (mesmo porte e quinto de renda): a posição da cidade na queda da eleição anterior "
        "para a escolhida (sem clique, 2022 → 2026), a variação do grupo e o histograma das variações com a cidade "
        "marcada; em 2006, o começo da série, o convite para escolher outra eleição. Só lê contas.",
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
VAR _y = [T15 · ano escolhido]
VAR _y0 = [T15 · ano anterior]
VAR _cpt1 = [T15 · candidato do PT no ano escolhido]
VAR _cpt0 = [T15 · candidato do PT no ano anterior]
-- 2 · Textos
VAR _nome = {ESC.format(v="_cid")}
VAR _dono = IF ( _cpt0 = _cpt1, "de " & {_curto("_cpt1")}, "do PT" )
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
VAR _html =
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
                    & "<text class='tk' x='500' y='298' text-anchor='middle'>quanto variou a margem " & _dono
                        & " em cada cidade parecida, " & _y0 & " → " & _y & ", em pontos; cada barra junta as cidades de "
                        & "uma faixa</text>"
                & "</svg>"
                & "<div class='rc cid entra d8' style='left:" & FORMAT ( MAX ( 0, MIN ( 770, _xCid - 120 ) ), "0.0", "en-US" )
                    & "px;text-align:" & SWITCH ( TRUE (), _xCid < 120, "left", _xCid > 890, "right", "center" ) & "'><span>"
                    & _nome & " " & {_pp("_var")} & "</span></div>"
                & "<div class='rc grp entra d9' style='left:" & FORMAT ( MAX ( 0, MIN ( 770, _xGrupo - 120 ) ), "0.0", "en-US" )
                    & "px;text-align:" & SWITCH ( TRUE (), _xGrupo < 120, "left", _xGrupo > 890, "right", "center" )
                    & "'><span>grupo " & {_pp("_vg")} & "</span></div>",
                ""
            )
        & "</div>"
    )
VAR _inicio =
    "<div class='tela t15p'>"
        & "<div class='rot entra'>" & IF ( _n = 1, "SEM CIDADES PARECIDAS", "ENTRE AS " & FORMAT ( _n, "#,0" )
            & " CIDADES PARECIDAS" ) & " · MESMO PORTE E MESMA RENDA</div>"
        & "<div class='pos sobe d1'>" & _y & ", o começo da série</div>"
        & "<div class='txt comp entra d3'>Não há eleição antes desta para comparar. Clique em outro ano na série para "
            & "ver como " & _nome & " mudou contra as " & _grupo & ".</div>"
    & "</div>"
RETURN
    IF ( _ok = 1 && NOT ISBLANK ( _n ) && ISBLANK ( _y0 ), _inicio, _html )""")

desenho("T15 · Parecidas · ALT", "Texto alternativo das cidades parecidas.",
        f"""-- 1 · Leituras
VAR _cid = [T15 · cidade]
VAR _n = [T15 · parecidas · quantidade]
VAR _pos = [T15 · parecidas · posição]
VAR _vg = [T15 · parecidas · variação do grupo]
VAR _y = [T15 · ano escolhido]
VAR _y0 = [T15 · ano anterior]
-- 2 · Textos
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _cid ), "Escolha uma cidade para compará-la com as cidades parecidas.",
        ISBLANK ( _y0 ),
        _cid & ": " & _y & " é o começo da série; não há eleição anterior para comparar com as cidades parecidas.",
        _cid & ": " & FORMAT ( _pos, "0" ) & "ª maior queda de margem entre " & FORMAT ( _n, "#,0" )
            & " cidades parecidas, de " & _y0 & " para " & _y & "; o grupo variou " & {_pp("_vg")} & " pontos."
    )""")

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
