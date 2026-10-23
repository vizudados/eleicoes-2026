# -*- coding: utf-8 -*-
"""desenho_t14 — gera as medidas da tela 14 · Série (contas e desenho).

    python -X utf8 pbi/scripts/desenho_t14.py

Grava pbi/dax/T14 Série/{Contas,Desenho}/*.dax. Sem filtro de UF, a série é o resultado nacional oficial (Candidato
ano, com o exterior); com UF (ou qualquer recorte de municípios), soma os municípios (Município ano). O adversário de
cada ano é o mais votado fora do PT (Alckmin, Serra, Aécio, Jair Bolsonaro duas vezes e Flávio Bolsonaro).

Oráculo: mockup/data/eleicoes.json › paginas[14] (pipeline/montar_dados_mockup.py › tela_serie).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
DAX = PBI / "dax"
TELA = "T14 Série"
GERADOR = "pbi/scripts/desenho_t14.py"
ORACULO = "mockup/data/eleicoes.json › paginas[14]"

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


ANOS = [2006, 2010, 2014, 2018, 2022, 2026]
REGIOES = ["Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul"]

# ==================================================================================================== contas
conta("T14 · PT %", "0.0%",
      "Votos do candidato do PT sobre os válidos no ano do contexto. Sem recorte de municípios, o resultado nacional "
      "oficial (com o exterior); com UF, a soma dos municípios.",
      """VAR _mun = ISCROSSFILTERED ( 'Município' )
RETURN
    IF (
        _mun,
        DIVIDE ( SUM ( 'Município ano'[VotosPT] ), SUM ( 'Município ano'[Validos] ) ),
        DIVIDE (
            CALCULATE ( SUM ( 'Candidato ano'[Votos] ), 'Candidato ano'[Partido] = "PT" ),
            MAX ( 'Candidato ano'[ValidosAno] )
        )
    )""", ORACULO + " › anos › pt › pct (2006 48,6% … 2026 45,2%)")
conta("T14 · adversário %", "0.0%",
      "Votos do mais votado fora do PT sobre os válidos no ano do contexto (nacional com o exterior; com UF, os municípios).",
      """VAR _mun = ISCROSSFILTERED ( 'Município' )
RETURN
    IF (
        _mun,
        DIVIDE ( SUM ( 'Município ano'[VotosAdversario] ), SUM ( 'Município ano'[Validos] ) ),
        DIVIDE (
            CALCULATE ( MAX ( 'Candidato ano'[Votos] ), 'Candidato ano'[Partido] <> "PT" ),
            MAX ( 'Candidato ano'[ValidosAno] )
        )
    )""", ORACULO + " › anos › adversario › pct (2018 46,0%; 2026 47,0%)")
conta("T14 · margem do PT", "0.0%", "PT % menos adversário % no ano do contexto (negativo: o PT atrás).",
      "[T14 · PT %] - [T14 · adversário %]", ORACULO + " › anos › pt_na_frente")
conta("T14 · eleições", "0", "Quantas eleições há na série (seis, de 2006 a 2026).", "COUNTROWS ( ALL ( 'Ano'[Ano] ) )")
conta("T14 · eleições com o PT atrás", "0", "Em quantas eleições da série o PT terminou o 1º turno atrás do adversário.",
      """COUNTROWS (
    FILTER ( ALL ( 'Ano'[Ano] ), [T14 · margem do PT] < 0 )
) + 0""", ORACULO + " › pt_atras_em (2018 e 2026 = 2)")
conta("T14 · vez em que o PT ficou atrás", "0",
      "No ano do contexto, se o PT ficou atrás: quantas vezes isso já tinha acontecido até ali, contando este ano "
      "(1ª, 2ª…). Vazio se o PT ficou à frente.",
      """VAR _ano = SELECTEDVALUE ( 'Ano'[Ano] )
RETURN
    IF (
        [T14 · margem do PT] < 0,
        COUNTROWS ( FILTER ( ALL ( 'Ano'[Ano] ), 'Ano'[Ano] <= _ano && [T14 · margem do PT] < 0 ) )
    )""", ORACULO + " › 2018 = 1ª, 2026 = 2ª")
conta("T14 · PT atrás em 2026", "0", "1 se o PT terminou 2026 atrás do adversário no recorte; 0 se não.",
      """IF ( CALCULATE ( [T14 · margem do PT], 'Ano'[Ano] = 2026 ) < 0, 1, 0 )""", ORACULO + " › 2026 atrás")
conta("T14 · melhor ano do PT", "0", "Ano do maior PT % da série no recorte.",
      """MAXX (
    TOPN ( 1, ALL ( 'Ano'[Ano] ), [T14 · PT %], DESC, 'Ano'[Ano], ASC ),
    'Ano'[Ano]
)""", ORACULO + " › 2006")
conta("T14 · pior ano do PT", "0", "Ano do menor PT % da série no recorte.",
      """MAXX (
    TOPN ( 1, ALL ( 'Ano'[Ano] ), [T14 · PT %], ASC, 'Ano'[Ano], ASC ),
    'Ano'[Ano]
)""", ORACULO + " › 2018")
conta("T14 · PT % no melhor ano", "0.0%", "O maior PT % da série no recorte.",
      "MAXX ( ALL ( 'Ano'[Ano] ), [T14 · PT %] )", ORACULO + " › 48,6%")
conta("T14 · PT % no pior ano", "0.0%", "O menor PT % da série no recorte.",
      "MINX ( ALL ( 'Ano'[Ano] ), [T14 · PT %] )", ORACULO + " › 29,3%")
conta("T14 · escala mínima", "0.0%", "Menor valor da série (PT e adversário) no recorte, para a escala do gráfico.",
      """MINX (
    ALL ( 'Ano'[Ano] ),
    MIN ( [T14 · PT %], [T14 · adversário %] )
)""")
conta("T14 · escala máxima", "0.0%", "Maior valor da série (PT e adversário) no recorte, para a escala do gráfico.",
      """MAXX (
    ALL ( 'Ano'[Ano] ),
    MAX ( [T14 · PT %], [T14 · adversário %] )
)""")
conta("T14 · candidato do PT", "texto", "Candidato do PT no ano do contexto.", "SELECTEDVALUE ( 'Ano'[Candidato do PT] )")
conta("T14 · adversário", "texto", "Adversário principal no ano do contexto.", "SELECTEDVALUE ( 'Ano'[Adversário] )")
conta("T14 · partido do adversário", "texto", "Partido do adversário principal no ano do contexto.",
      "SELECTEDVALUE ( 'Ano'[Partido do adversário] )")
conta("T14 · ano", "0", "Ano do contexto (a eleição).", "SELECTEDVALUE ( 'Ano'[Ano] )")
conta("T14 · recorte", "texto", "Nome da UF escolhida no filtro da tela (vazio = Brasil).",
      "IF ( ISFILTERED ( 'UF'[Nome] ), SELECTEDVALUE ( 'UF'[Nome] ) )")
conta("T14 · região do recorte", "texto", "Região da UF escolhida no filtro (vazio = Brasil).",
      "IF ( ISFILTERED ( 'UF'[Nome] ), SELECTEDVALUE ( 'UF'[Região] ) )")
conta("T14 · PT % na região", "0.0%", "PT % somando os municípios da região do contexto (ignora o filtro de UF).",
      "CALCULATE ( [T14 · PT %], REMOVEFILTERS ( 'UF' ) )", ORACULO + " › regioes › pt_pct (Nordeste 2026 63,8%)")
conta("T14 · adversário % na região", "0.0%", "Adversário % somando os municípios da região do contexto (ignora a UF).",
      "CALCULATE ( [T14 · adversário %], REMOVEFILTERS ( 'UF' ) )", ORACULO + " › regioes › adv_pct (Sul 2026 60,1%)")
conta("T14 · votos do candidato", "#,0", "Votos do candidato no 1º turno (nacional, com o exterior).",
      "SUM ( 'Candidato ano'[Votos] )")
conta("T14 · % do candidato", "0.0%", "Votos do candidato sobre os válidos do ano (nacional, com o exterior).",
      "DIVIDE ( SUM ( 'Candidato ano'[Votos] ), MAX ( 'Candidato ano'[ValidosAno] ) )")
conta("T14 · partido do candidato", "texto", "Partido do candidato do contexto.",
      "SELECTEDVALUE ( 'Candidato ano'[Partido] )")
conta("T14 · posição do PT", "0", "Colocação nacional do candidato do PT no 1º turno do ano do contexto.",
      """CALCULATE ( MAX ( 'Candidato ano'[Posição] ), 'Candidato ano'[Partido] = "PT" )""", "2018 e 2026 = 2")
conta("T14 · abstenção", "0.0%", "Eleitores que faltaram sobre os aptos no ano do contexto (Brasil, sem o exterior).",
      """DIVIDE ( SUM ( 'Comparecimento ano'[Abstencoes] ), SUM ( 'Comparecimento ano'[Aptos] ) )""")


# ==================================================================================================== desenho
def _pct(v: str) -> str:
    return f'FORMAT ( {v}, "0.0%" )'


def _laco(r: float = 30) -> str:
    """Laço à mão (duas voltas desencontradas) centrado em 0,0 — um path para usar com translate."""
    pts = []
    for i in range(0, 46):
        a = -2.2 + i * (2 * math.pi * 1.15) / 45
        rr = r * (1 + 0.08 * math.sin(i * 0.9)) * (1.0 + 0.06 * i / 45)
        pts.append((rr * math.cos(a) * 1.18, rr * math.sin(a) * 0.95))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


LACO = _laco()
_ESC = "( {lo} )"

desenho("T14 · Resposta · HTML",
        "Topo da tela: quantas vezes o PT terminou o 1º turno atrás (ou à frente) e em quais anos, com os candidatos. "
        "Só lê contas 'T14 · …'.",
        f"""-- 1 · Leituras
VAR _k = [T14 · eleições com o PT atrás]
VAR _n = [T14 · eleições]
VAR _a26 = [T14 · PT atrás em 2026]
VAR _uf = [T14 · recorte]
VAR _anos =
    ADDCOLUMNS (
        VALUES ( 'Ano'[Ano] ),
        "@m", [T14 · margem do PT],
        "@pt", [T14 · PT %],
        "@adv", [T14 · adversário %],
        "@cpt", [T14 · candidato do PT],
        "@cadv", [T14 · adversário]
    )
-- 2 · Textos
VAR _atras = FILTER ( _anos, [@m] < 0 ) /* lista */
VAR _nAtras = COUNTROWS ( _atras ) /* lista */
VAR _txtAnos =
    CONCATENATEX (
        _atras,
        "em " & 'Ano'[Ano] & " (" & [@cpt] & " " & {_pct("[@pt]")} & " × " & [@cadv] & " " & {_pct("[@adv]")} & ")",
        "; ",
        'Ano'[Ano], ASC
    )
VAR _grande =
    SWITCH (
        TRUE (),
        _k = _n, FORMAT ( _k, "0" ) & " de " & FORMAT ( _n, "0" ),
        _a26 = 1, FORMAT ( _k, "0" ) & "ª vez",
        FORMAT ( _n - _k, "0" ) & " de " & FORMAT ( _n, "0" )
    )
VAR _onde = IF ( ISBLANK ( _uf ), "", " em " & _uf )
VAR _man =
    SWITCH (
        TRUE (),
        _k = _n, IF ( ISBLANK ( _uf ), "", _uf & ": " ) & "o PT terminou o 1º turno atrás do adversário nas seis eleições",
        _a26 = 1 && ISBLANK ( _uf ),
            "Pela " & FORMAT ( _k, "0" ) & "ª vez em seis eleições, o PT termina o 1º turno em segundo lugar",
        _a26 = 1,
            _uf & ": pela " & FORMAT ( _k, "0" ) & "ª vez em seis eleições, o PT termina o 1º turno atrás do adversário",
        _k = 0, "O PT ficou à frente nas seis eleições" & _onde & ", inclusive em 2026",
        "O PT ficou à frente em " & FORMAT ( _n - _k, "0" ) & " das seis eleições" & _onde & ", inclusive em 2026"
    )
VAR _soAnos = CONCATENATEX ( _atras, 'Ano'[Ano], ", ", 'Ano'[Ano], ASC )
VAR _sub =
    SWITCH (
        TRUE (),
        _nAtras = 0, "",
        _nAtras <= 2, "Atrás " & _txtAnos & ".",
        "Atrás em " & _soAnos & "."
    )
-- 3 · Geometria e 4 · Marcação (urnas de 76 px a cada 92, a partir de x 1086)
VAR _urnas =
    CONCATENATEX (
        _anos,
        VAR _i = ( 'Ano'[Ano] - 2006 ) / 4
        VAR _vez = CALCULATE ( [T14 · vez em que o PT ficou atrás] )
        RETURN
            "<div class='ux " & IF ( [@m] < 0, "adv", "pt" ) & " brota' style='left:" & ( 1086 + _i * 92 )
                & "px;animation-delay:" & ( 500 + _i * 140 ) & "ms'></div>"
                & "<div class='ua' style='left:" & ( 1086 + _i * 92 ) & "px'>" & 'Ano'[Ano] & "</div>"
                & IF (
                    NOT ISBLANK ( _vez ),
                    "<div class='uv mao entra' style='left:" & ( 1086 + _i * 92 ) & "px;animation-delay:"
                        & ( 900 + _i * 140 ) & "ms'>" & FORMAT ( _vez, "0" ) & "ª vez</div>"
                ),
        "",
        'Ano'[Ano], ASC
    )
RETURN
    "<div class='tela t14r'>"
        & "<div class='num g sobe'>" & _grande & "</div>"
        & "<div class='man m sobe d2'>" & _man & "</div>"
        & "<div class='nota s entra d4'>" & _sub & "</div>"
        & "<div class='rot ur entra d3'>QUEM TERMINOU NA FRENTE, ELEIÇÃO A ELEIÇÃO</div>"
        & _urnas
        & "<div class='nota ul entra d8'>urna vermelha: o PT à frente · azul: o adversário</div>"
    & "</div>\"""")

desenho("T14 · Resposta · ALT", "Texto alternativo do topo da tela.",
        """-- 1 · Leituras
VAR _k = [T14 · eleições com o PT atrás]
VAR _a26 = [T14 · PT atrás em 2026]
VAR _uf = [T14 · recorte]
-- 2 · Textos
RETURN
    IF ( ISBLANK ( _uf ), "Brasil", _uf ) & ": o PT terminou o 1º turno atrás do adversário em " & FORMAT ( _k, "0" )
        & " das seis eleições de 2006 a 2026" & IF ( _a26 = 1, ", inclusive em 2026.", "; em 2026, à frente." )""")

desenho("T14 · Linhas título · HTML", "Sobretítulo, manchete do gráfico (melhor e pior ano do PT) e a legenda.",
        f"""-- 1 · Leituras
VAR _ma = [T14 · melhor ano do PT]
VAR _pa = [T14 · pior ano do PT]
VAR _mv = [T14 · PT % no melhor ano]
VAR _pv = [T14 · PT % no pior ano]
VAR _uf = [T14 · recorte]
-- 2 · Textos
VAR _man =
    "O PT teve o melhor resultado em " & _ma & " (" & {_pct("_mv")} & ") e o pior em " & _pa & " ("
        & {_pct("_pv")} & ")"
-- 4 · Marcação
RETURN
    "<div class='tela t14t'>"
        & "<div class='rot entra'>% DOS VOTOS VÁLIDOS NO 1º TURNO · PT × ADVERSÁRIO PRINCIPAL"
            & IF ( ISBLANK ( _uf ), " · BRASIL", " · " & UPPER ( _uf ) ) & "</div>"
        & "<div class='man sobe d1'>" & _man & "</div>"
        & "<div class='leg entra d2'><span><i class='pt'></i>PT</span><span><i class='adv'></i>adversário principal: o "
            & "mais votado fora do PT no ano</span><span><i class='laco'></i>PT atrás</span></div>"
    & "</div>\"""")

desenho("T14 · Linhas título · ALT", "Texto alternativo do título do gráfico.",
        """-- 1 · Leituras
VAR _ma = [T14 · melhor ano do PT]
VAR _pa = [T14 · pior ano do PT]
-- 2 · Textos
RETURN
    "Linhas do PT e do adversário principal, de 2006 a 2026. Melhor ano do PT: " & _ma & "; pior: " & _pa & ".\"""")

desenho("T14 · Linhas · HTML",
        "Uma entrada por eleição (granularidade Ano): os pontos do PT e do adversário com o rótulo, o trecho de linha "
        "até a eleição seguinte (que se desenha em sequência), o laço à mão quando o PT ficou atrás e o eixo com os "
        "candidatos. A 1ª eleição desenha a grade. Escala pelas contas 'T14 · escala …'.",
        f"""-- 1 · Leituras
VAR _ano = [T14 · ano]
VAR _pt = [T14 · PT %]
VAR _adv = [T14 · adversário %]
VAR _ptN = CALCULATE ( [T14 · PT %], 'Ano'[Ano] = _ano + 4 )
VAR _advN = CALCULATE ( [T14 · adversário %], 'Ano'[Ano] = _ano + 4 )
VAR _cpt = [T14 · candidato do PT]
VAR _cadv = [T14 · adversário]
VAR _part = [T14 · partido do adversário]
VAR _min = [T14 · escala mínima]
VAR _max = [T14 · escala máxima]
-- 2 · Textos
VAR _cptCurto = SWITCH ( _cpt, "Dilma Rousseff", "Dilma", "Fernando Haddad", "Haddad", _cpt )
VAR _cadvCurto =
    SWITCH ( _cadv, "Geraldo Alckmin", "Alckmin", "José Serra", "Serra", "Aécio Neves", "Aécio",
        "Jair Bolsonaro", "Bolsonaro", _cadv )
VAR _atras = _pt < _adv
-- 3 · Geometria (anos a cada 276 px a partir de x 120; valores de y 30 a 270 entre o piso e o teto da escala)
VAR _lo = FLOOR ( _min * 100 - 4, 10 ) / 100
VAR _hi = CEILING ( _max * 100 + 4, 10 ) / 100
VAR _i = ( _ano - 2006 ) / 4
VAR _x = 120 + _i * 276
VAR _yPt = 270 - 240 * ( _pt - _lo ) / ( _hi - _lo )
VAR _yAdv = 270 - 240 * ( _adv - _lo ) / ( _hi - _lo )
VAR _yPtN = 270 - 240 * ( _ptN - _lo ) / ( _hi - _lo )
VAR _yAdvN = 270 - 240 * ( _advN - _lo ) / ( _hi - _lo )
VAR _f = FORMAT ( _x, "0.0", "en-US" )
VAR _fN = FORMAT ( _x + 276, "0.0", "en-US" )
VAR _atraso = 300 + _i * 380
VAR _ptCima = _pt >= _adv
VAR _grade =
    IF (
        _ano = 2006,
        CONCATENATEX (
            GENERATESERIES ( _lo * 100, _hi * 100, 10 ),
            VAR _yy = 270 - 240 * ( [Value] / 100 - _lo ) / ( _hi - _lo )
            RETURN
                "<line class='g' x1='70' x2='1560' y1='" & FORMAT ( _yy, "0.0", "en-US" ) & "' y2='"
                    & FORMAT ( _yy, "0.0", "en-US" ) & "'/><text class='tk' x='58' y='" & FORMAT ( _yy + 4, "0.0", "en-US" )
                    & "' text-anchor='end'>" & [Value] & "%</text>",
            ""
        ) & "<line class='base' x1='70' x2='1560' y1='290' y2='290'/>"
    )
VAR _seg =
    IF (
        NOT ISBLANK ( _ptN ),
        "<line class='lpt traco' pathLength='1' style='animation-delay:" & _atraso & "ms' x1='" & _f & "' y1='"
            & FORMAT ( _yPt, "0.0", "en-US" ) & "' x2='" & _fN & "' y2='" & FORMAT ( _yPtN, "0.0", "en-US" ) & "'/>"
            & "<line class='ladv traco' pathLength='1' style='animation-delay:" & _atraso & "ms' x1='" & _f & "' y1='"
            & FORMAT ( _yAdv, "0.0", "en-US" ) & "' x2='" & _fN & "' y2='" & FORMAT ( _yAdvN, "0.0", "en-US" ) & "'/>"
    )
VAR _laco =
    IF (
        _atras,
        "<path class='laco traco' pathLength='1' style='animation-delay:" & ( _atraso + 900 ) & "ms' transform='translate("
            & _f & "," & FORMAT ( _yPt, "0.0", "en-US" ) & ")' d='{LACO}'/>"
    )
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _pt ),
        "<div class='tela ano'>"
            & "<div class='alvo' style='left:" & FORMAT ( _x - 128, "0.0", "en-US" ) & "px'></div>"
            & "<svg class='sv' width='1620' height='370' viewBox='0 0 1620 370'>"
                & _grade & _seg & _laco
                & "<circle class='ppt brota' style='animation-delay:" & ( _atraso - 120 ) & "ms' cx='" & _f & "' cy='"
                    & FORMAT ( _yPt, "0.0", "en-US" ) & "' r='7.5'/>"
                & "<circle class='padv brota' style='animation-delay:" & ( _atraso - 120 ) & "ms' cx='" & _f & "' cy='"
                    & FORMAT ( _yAdv, "0.0", "en-US" ) & "' r='7.5'/>"
            & "</svg>"
            & "<div class='vl vpt sobe' style='left:" & FORMAT ( _x - 60, "0.0", "en-US" ) & "px;top:"
                & FORMAT ( IF ( _ptCima, _yPt - 38, _yPt + IF ( _atras, 30, 12 ) ), "0.0", "en-US" ) & "px;animation-delay:" & ( _atraso + 200 )
                & "ms'>" & {_pct("_pt")} & "</div>"
            & "<div class='vl vadv sobe' style='left:" & FORMAT ( _x - 60, "0.0", "en-US" ) & "px;top:"
                & FORMAT ( IF ( _ptCima, _yAdv + 12, _yAdv - 38 ), "0.0", "en-US" ) & "px;animation-delay:" & ( _atraso + 200 )
                & "ms'>" & {_pct("_adv")} & "</div>"
            & "<div class='xl entra' style='left:" & FORMAT ( _x - 128, "0.0", "en-US" ) & "px;animation-delay:" & _atraso
                & "ms'><b>" & _ano & "</b><span>" & _cptCurto & " × " & _cadvCurto & " · " & _part & "</span></div>"
        & "</div>"
    )""")

desenho("T14 · Linhas · ALT", "Texto alternativo do gráfico de linhas.",
        """-- 1 · Leituras
VAR _k = [T14 · eleições com o PT atrás]
VAR _uf = [T14 · recorte]
-- 2 · Textos
RETURN
    "Gráfico de linhas, " & IF ( ISBLANK ( _uf ), "Brasil", _uf ) & ": % dos votos válidos do PT e do adversário "
        & "principal em cada 1º turno de 2006 a 2026; o PT ficou atrás em " & FORMAT ( _k, "0" ) & " delas.\"""")

_TAB_REG = ", ".join(f'{{ {i + 1}, "{r}" }}' for i, r in enumerate(REGIOES))
_TAB_ANOS = ", ".join(f"{{ {a} }}" for a in ANOS)

desenho("T14 · Regiões · HTML",
        "As cinco regiões na mesma escala (10% a 70%): linhas do PT e do adversário e os valores de 2026. Ignoram o "
        "filtro de UF; com uma UF escolhida, a região dela fica em destaque.",
        f"""-- 1 · Leituras
VAR _reg = DATATABLE ( "o", INTEGER, "nome", STRING, {{ {_TAB_REG} }} )
VAR _anos = DATATABLE ( "a", INTEGER, {{ {_TAB_ANOS} }} )
VAR _sel = [T14 · região do recorte]
VAR _uf = [T14 · recorte]
-- 3 · Geometria e 4 · Marcação (painéis de 300 px a cada 330; x do ano de 8 a 218; y de 10% a 70% em 110 px)
VAR _paineis =
    CONCATENATEX (
        _reg,
        VAR _o = [o]
        VAR _r = [nome]
        VAR _px = ( _o - 1 ) * 330
        VAR _pts =
            ADDCOLUMNS (
                _anos,
                "@pt",
                    VAR _a = [a]
                    RETURN
                        CALCULATE ( [T14 · PT % na região], 'Município'[Região] = _r, 'Ano'[Ano] = _a ),
                "@adv",
                    VAR _a = [a]
                    RETURN
                        CALCULATE ( [T14 · adversário % na região], 'Município'[Região] = _r, 'Ano'[Ano] = _a )
            )
        VAR _xy =
            ADDCOLUMNS (
                _pts,
                "@x", 8 + ( [a] - 2006 ) / 4 * 42,
                "@yPt", 112 - 96 * ( MAX ( 0.1, MIN ( 0.7, [@pt] ) ) - 0.1 ) / 0.6,
                "@yAdv", 112 - 96 * ( MAX ( 0.1, MIN ( 0.7, [@adv] ) ) - 0.1 ) / 0.6
            )
        VAR _lPt =
            CONCATENATEX ( _xy, FORMAT ( [@x], "0.0", "en-US" ) & "," & FORMAT ( [@yPt], "0.0", "en-US" ), " ", [a], ASC )
        VAR _lAdv =
            CONCATENATEX ( _xy, FORMAT ( [@x], "0.0", "en-US" ) & "," & FORMAT ( [@yAdv], "0.0", "en-US" ), " ", [a], ASC )
        VAR _pt26 = MAXX ( FILTER ( _xy, [a] = 2026 ), [@pt] ) /* lista */
        VAR _adv26 = MAXX ( FILTER ( _xy, [a] = 2026 ), [@adv] ) /* lista */
        VAR _y26pt = MAXX ( FILTER ( _xy, [a] = 2026 ), [@yPt] ) /* lista */
        VAR _y26adv = MAXX ( FILTER ( _xy, [a] = 2026 ), [@yAdv] ) /* lista */
        VAR _sep = IF ( ABS ( _y26pt - _y26adv ) < 16, 8 - ABS ( _y26pt - _y26adv ) / 2, 0 )
        VAR _cls = IF ( ISBLANK ( _sel ), "pn", IF ( _sel = _r, "pn sel", "pn apaga" ) )
        RETURN
            "<div class='" & _cls & " sobe d" & ( 2 + _o ) & "' style='left:" & _px & "px'>"
                & "<div class='nm'>" & _r & IF ( _sel = _r, " <span class='mao'>região de " & _uf & "</span>", "" )
                & "</div>"
                & "<svg width='300' height='132' viewBox='0 0 300 132'>"
                    & "<line class='b' x1='0' x2='226' y1='116' y2='116'/>"
                    & "<polyline class='lpt traco' pathLength='1' style='animation-delay:" & ( 600 + _o * 120 )
                        & "ms' points='" & _lPt & "'/>"
                    & "<polyline class='ladv traco' pathLength='1' style='animation-delay:" & ( 600 + _o * 120 )
                        & "ms' points='" & _lAdv & "'/>"
                    & "<circle class='ppt' cx='218' cy='" & FORMAT ( _y26pt, "0.0", "en-US" ) & "' r='4'/>"
                    & "<circle class='padv' cx='218' cy='" & FORMAT ( _y26adv, "0.0", "en-US" ) & "' r='4'/>"
                    & "<text class='vpt' x='228' y='" & FORMAT ( _y26pt + 5 + IF ( _y26pt >= _y26adv, _sep, -_sep ), "0.0", "en-US" )
                        & "'>" & {_pct("_pt26")} & "</text>"
                    & "<text class='vadv' x='228' y='" & FORMAT ( _y26adv + 5 + IF ( _y26adv > _y26pt, _sep, -_sep ), "0.0", "en-US" )
                        & "'>" & {_pct("_adv26")} & "</text>"
                    & "<text class='ex' x='0' y='130'>2006</text><text class='ex' x='218' y='130' text-anchor='middle'>2026</text>"
                & "</svg>"
            & "</div>",
        "",
        [o], ASC
    )
RETURN
    "<div class='tela t14g'>"
        & "<div class='rot entra'>POR REGIÃO · MESMA ESCALA, 10% A 70%" & IF ( ISBLANK ( _uf ), "", " · TODO O BRASIL" )
            & "</div>"
        & _paineis
    & "</div>\"""")

desenho("T14 · Regiões · ALT", "Texto alternativo das regiões.",
        """-- 1 · Leituras
VAR _sel = [T14 · região do recorte]
-- 2 · Textos
RETURN
    "Cinco pequenos gráficos, um por região, com o PT e o adversário de 2006 a 2026 na mesma escala"
        & IF ( ISBLANK ( _sel ), ".", "; em destaque, " & _sel & "." )""")

desenho("T14 · Tooltip ano · HTML",
        "Dossiê da eleição no tooltip da série: os quatro mais votados no Brasil (com o exterior), a colocação do PT e "
        "a abstenção. Só lê contas.",
        f"""-- 1 · Leituras
VAR _ano = [T14 · ano]
VAR _pos = [T14 · posição do PT]
VAR _abs = [T14 · abstenção]
VAR _cand =
    TOPN (
        4,
        ADDCOLUMNS (
            VALUES ( 'Candidato ano'[Candidato] ),
            "@v", [T14 · votos do candidato],
            "@p", [T14 · % do candidato],
            "@pa", [T14 · partido do candidato]
        ),
        [@v], DESC,
        'Candidato ano'[Candidato], ASC
    )
-- 2 · Textos
VAR _selo = "PT EM " & FORMAT ( _pos, "0" ) & "º"
VAR _clsSelo = IF ( _pos = 1, "selo vm", "selo az" )
VAR _mao = IF ( _pos = 1, "o PT venceu o 1º turno", "o PT ficou em " & FORMAT ( _pos, "0" ) & "º" )
-- 3 · Geometria e 4 · Marcação (barras: 60% = 140 px)
VAR _maxOutro = MAXX ( FILTER ( _cand, [@pa] <> "PT" ), [@v] ) /* lista */
VAR _linhas =
    CONCATENATEX (
        _cand,
        VAR _cor = SWITCH ( TRUE (), [@pa] = "PT", "pt", [@v] = _maxOutro, "adv", "o" )
        VAR _w = MIN ( 140, 140 * [@p] / 0.6 )
        RETURN
            "<div class='cl'><span class='nm'>" & 'Candidato ano'[Candidato] & " <i>" & [@pa] & "</i></span>"
                & "<span class='tr'><b class='barra-x " & _cor & "' style='width:" & FORMAT ( _w, "0.0", "en-US" )
                & "px'></b></span><span class='pc'>" & {_pct("[@p]")} & "</span></div>",
        "",
        [@v], DESC
    )
RETURN
    "<div class='tela tt14'><div class='fita'></div>"
        & "<div class='" & _clsSelo & "'>" & _selo & "</div>"
        & "<div class='an sobe'>" & _ano & " · 1º turno</div>"
        & "<div class='rot entra d1'>OS MAIS VOTADOS NO BRASIL</div>"
        & "<div class='lista entra d2'>" & _linhas & "</div>"
        & "<div class='nota entra d4'>Faltaram " & {_pct("_abs")} & " dos eleitores. Votos válidos, com o exterior.</div>"
        & "<div class='mao entra d6'>" & _mao & "</div>"
    & "</div>\"""")

desenho("T14 · Tooltip ano · ALT", "Texto alternativo do dossiê da eleição.",
        """-- 1 · Leituras
VAR _ano = [T14 · ano]
VAR _pos = [T14 · posição do PT]
-- 2 · Textos
RETURN
    "Eleição de " & _ano & ": o PT ficou em " & FORMAT ( _pos, "0" ) & "º lugar no 1º turno.\"""")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    gravar()
    print(f"T14: {len(MEDIDAS)} medidas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
