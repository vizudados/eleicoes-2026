# -*- coding: utf-8 -*-
"""desenho_t14 — gera as medidas da tela 14 · Série (contas e desenho).

    python -X utf8 pbi/scripts/desenho_t14.py

Grava pbi/dax/T14 Série/{Contas,Desenho}/*.dax. Sem filtro de UF, a série é o resultado nacional oficial (Candidato
ano, com o exterior); com UF (ou qualquer recorte de municípios), soma os municípios (Município ano). O adversário de
cada ano é o mais votado fora do PT (Alckmin, Serra, Aécio, Jair Bolsonaro duas vezes e Flávio Bolsonaro).

Interação (23/10/2026): clicar num ano da série (filtro cruzado no Ano) leva a resposta àquela eleição (a margem, os
candidatos, a urna em destaque) e os painéis das regiões ao mesmo ano; clicar numa região (granularidade
Município[Região]) leva a série, o título e a resposta àquela região. A região clicada vale por cima do filtro de UF
(as contas da série tiram a UF quando há região clicada), e a manchete diz "no Nordeste".

Oráculo: mockup/data/eleicoes.json › paginas[14] (pipeline/montar_dados_mockup.py › tela_serie).
"""
from __future__ import annotations

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
# as UFs de cada região (a mesma lista de pbi/modelo/base.py), para o dossiê da região
UFS_REGIAO = [("AC", "Norte"), ("AL", "Nordeste"), ("AM", "Norte"), ("AP", "Norte"), ("BA", "Nordeste"),
              ("CE", "Nordeste"), ("DF", "Centro-Oeste"), ("ES", "Sudeste"), ("GO", "Centro-Oeste"),
              ("MA", "Nordeste"), ("MG", "Sudeste"), ("MS", "Centro-Oeste"), ("MT", "Centro-Oeste"), ("PA", "Norte"),
              ("PB", "Nordeste"), ("PE", "Nordeste"), ("PI", "Nordeste"), ("PR", "Sul"), ("RJ", "Sudeste"),
              ("RN", "Nordeste"), ("RO", "Norte"), ("RR", "Norte"), ("RS", "Sul"), ("SC", "Sul"), ("SE", "Nordeste"),
              ("SP", "Sudeste"), ("TO", "Norte")]
_TAB_UFS = ", ".join(f'{{ "{u}", "{r}" }}' for u, r in UFS_REGIAO)
_TAB_ANOS_R = ", ".join(f"{{ {a} }}" for a in ANOS)

# ==================================================================================================== contas
conta("T14 · PT %", "0.0%",
      "Votos do candidato do PT sobre os válidos no ano do contexto. Sem recorte de municípios, o resultado nacional "
      "oficial (com o exterior); com UF ou região, a soma dos municípios. A região (painel clicado ou do grão) vale por "
      "cima do filtro de UF.",
      """VAR _mun = ISCROSSFILTERED ( 'Município' )
VAR _reg = ISFILTERED ( 'Município'[Região] )
RETURN
    SWITCH (
        TRUE (),
        _reg,
            CALCULATE (
                DIVIDE ( SUM ( 'Município ano'[VotosPT] ), SUM ( 'Município ano'[Validos] ) ),
                REMOVEFILTERS ( 'UF' )
            ),
        _mun, DIVIDE ( SUM ( 'Município ano'[VotosPT] ), SUM ( 'Município ano'[Validos] ) ),
        DIVIDE (
            CALCULATE ( SUM ( 'Candidato ano'[Votos] ), 'Candidato ano'[Partido] = "PT" ),
            MAX ( 'Candidato ano'[ValidosAno] )
        )
    )""", ORACULO + " › anos › pt › pct (2006 48,6% … 2026 45,2%)")
conta("T14 · adversário %", "0.0%",
      "Votos do mais votado fora do PT sobre os válidos no ano do contexto (nacional com o exterior; com UF ou região, "
      "os municípios; a região vale por cima da UF).",
      """VAR _mun = ISCROSSFILTERED ( 'Município' )
VAR _reg = ISFILTERED ( 'Município'[Região] )
RETURN
    SWITCH (
        TRUE (),
        _reg,
            CALCULATE (
                DIVIDE ( SUM ( 'Município ano'[VotosAdversario] ), SUM ( 'Município ano'[Validos] ) ),
                REMOVEFILTERS ( 'UF' )
            ),
        _mun, DIVIDE ( SUM ( 'Município ano'[VotosAdversario] ), SUM ( 'Município ano'[Validos] ) ),
        DIVIDE (
            CALCULATE ( MAX ( 'Candidato ano'[Votos] ), 'Candidato ano'[Partido] <> "PT" ),
            MAX ( 'Candidato ano'[ValidosAno] )
        )
    )""", ORACULO + " › anos › adversario › pct (2018 46,0%; 2026 47,0%)")
conta("T14 · eleições com o PT à frente", "0", "Em quantas eleições da série o PT terminou o 1º turno à frente do adversário.",
      """COUNTROWS (
    FILTER ( ALL ( 'Ano'[Ano] ), [T14 · margem do PT] > 0 )
) + 0""", ORACULO + " › 4 no Brasil")
conta("T14 · região clicada", "texto", "A região clicada nos painéis (filtro cruzado em Município[Região]); vazio sem clique.",
      """IF (
    ISFILTERED ( 'Município'[Região] ),
    CALCULATE ( SELECTEDVALUE ( 'Município'[Região] ), REMOVEFILTERS ( 'UF' ) )
)""")
conta("T14 · ano escolhido", "0", "A eleição clicada na série (filtro cruzado no Ano); vazio sem clique.",
      """IF ( ISFILTERED ( 'Ano'[Ano] ) && HASONEVALUE ( 'Ano'[Ano] ), VALUES ( 'Ano'[Ano] ) )""")
conta("T14 · ano dos painéis", "0", "A eleição que os painéis das regiões destacam: a clicada na série ou 2026.",
      """VAR _a = [T14 · ano escolhido]
RETURN
    IF ( ISBLANK ( _a ), 2026, _a )""")
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
conta("T14 · recorte", "texto",
      "O lugar que a tela conta: a região clicada nos painéis ou o recorte do filtro de estado (árvore Região › Estado), "
      "pela medida comum [Recorte · nome]: 'Bahia', 'Nordeste', 'MG e SP', '3 estados'; vazio = Brasil.",
      """VAR _reg = [T14 · região clicada]
RETURN
    IF ( NOT ISBLANK ( _reg ), _reg, IF ( [Recorte · com escolha] = 1, [Recorte · nome] ) )""")
conta("T14 · onde", "texto",
      "O lugar com a preposição e o artigo certo, para as frases: 'no Nordeste' (região clicada ou inteira no filtro), "
      "'na Bahia', 'em Minas Gerais', 'em MG e SP', 'em 3 estados' (medida comum [Recorte · em]); vazio = Brasil.",
      """VAR _reg = [T14 · região clicada]
RETURN
    IF (
        NOT ISBLANK ( _reg ),
        "no " & _reg,
        IF ( [Recorte · com escolha] = 1, [Recorte · em] )
    )""")
conta("T14 · região do painel", "texto",
      "A região do painel (grão dos painéis das regiões e do dossiê da região), mesmo com uma UF de outra região no filtro.",
      "CALCULATE ( SELECTEDVALUE ( 'Município'[Região] ), REMOVEFILTERS ( 'UF' ) )")
for _q, _med in (("PT %", "T14 · PT %"), ("adversário %", "T14 · adversário %")):
    conta(f"T14 · {_q} da UF na eleição dos painéis", "0.0%",
          f"{_q} na UF do contexto, na eleição em destaque (a clicada na série ou 2026), sem a região do painel e sem o "
          "recorte do filtro de estado (só a UF do contexto fica: o dossiê da região mostra todos os estados dela, como "
          "os painéis ignoram o filtro).",
          f"""VAR _a = [T14 · ano dos painéis]
RETURN
    CALCULATE (
        [{_med}],
        REMOVEFILTERS ( 'Município'[Região] ),
        ALLEXCEPT ( 'UF', 'UF'[UF] ),
        'Ano'[Ano] = _a
    )""")
conta("T14 · UFs da região", "0", "Quantas UFs tem a região do painel.",
      """VAR _r = [T14 · região do painel]
RETURN
    COUNTROWS ( FILTER ( ALL ( 'UF'[UF], 'UF'[Região] ), 'UF'[Região] = _r ) ) + 0""", "Nordeste 9, Sul 3")
conta("T14 · UFs da região com o PT à frente", "0",
      "Quantas UFs da região do painel tiveram o PT à frente do adversário na eleição em destaque (a clicada ou 2026); "
      "ignora o recorte do filtro de estado, como os painéis.",
      """VAR _r = [T14 · região do painel]
VAR _a = [T14 · ano dos painéis]
RETURN
    COUNTROWS (
        FILTER (
            ADDCOLUMNS (
                FILTER ( ALL ( 'UF'[UF], 'UF'[Região] ), 'UF'[Região] = _r ),
                "@m",
                    CALCULATE (
                        [T14 · margem do PT],
                        REMOVEFILTERS ( 'Município'[Região] ),
                        ALLEXCEPT ( 'UF', 'UF'[UF] ),
                        'Ano'[Ano] = _a
                    )
            ),
            [@m] > 0
        )
    ) + 0""", "Nordeste 2026: 9 de 9 (motor)")
conta("T14 · região do recorte", "texto",
      "As regiões que têm estados no recorte do filtro de estado, do Norte ao Sul ('Nordeste', 'Nordeste e Sudeste', "
      "'Norte, Nordeste e Sul'); vazio = Brasil. Os painéis dessas regiões ficam em destaque.",
      """VAR _r =
    CALCULATETABLE ( SUMMARIZE ( 'UF', 'UF'[Região], 'UF'[RegiaoOrdem] ), KEEPFILTERS ( 'UF'[Tipo] = "UF" ) )
VAR _n = COUNTROWS ( _r )
VAR _ult = MAXX ( TOPN ( 1, _r, 'UF'[RegiaoOrdem], DESC ), 'UF'[Região] )
VAR _resto = CONCATENATEX ( FILTER ( _r, 'UF'[Região] <> _ult ), 'UF'[Região], ", ", 'UF'[RegiaoOrdem], ASC )
RETURN
    IF ( [Recorte · com escolha] = 1 && _n > 0, IF ( _n = 1, _ult, _resto & " e " & _ult ) )""")
conta("T14 · UFs do recorte na região do painel", "0",
      "Quantos estados da região do painel estão no recorte do filtro de estado (0 sem escolha ou sem estado dela).",
      """VAR _r = [T14 · região do painel]
RETURN
    IF (
        [Recorte · com escolha] = 1,
        CALCULATE ( COUNTROWS ( 'UF' ), KEEPFILTERS ( 'UF'[Região] = _r ), KEEPFILTERS ( 'UF'[Tipo] = "UF" ) )
    ) + 0""")
conta("T14 · recorte na região do painel", "texto",
      "O que da região do painel está no recorte, com 'de' e o artigo (medida comum [Recorte · de] só nessa região): "
      "'da Bahia', 'de BA e SE', 'de 3 estados'; 'do Nordeste' quando a região está inteira; vazio sem estado dela.",
      """VAR _r = [T14 · região do painel]
RETURN
    IF (
        [T14 · UFs do recorte na região do painel] > 0,
        CALCULATE ( [Recorte · de], KEEPFILTERS ( 'UF'[Região] = _r ) )
    )""")
conta("T14 · sigla do recorte na região do painel", "texto",
      "A sigla do estado escolhido na região do painel, quando é um só ('MS'); vazio nos outros casos. A nota do painel "
      "usa a sigla quando o nome não cabe ao lado do nome da região.",
      """VAR _r = [T14 · região do painel]
RETURN
    IF (
        [T14 · UFs do recorte na região do painel] = 1,
        CALCULATE ( SELECTEDVALUE ( 'UF'[UF] ), KEEPFILTERS ( 'UF'[Região] = _r ), KEEPFILTERS ( 'UF'[Tipo] = "UF" ) )
    )""")
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


def _curto(v: str) -> str:
    """Nome curto do candidato (Dilma, Haddad, Alckmin, Serra, Aécio, Bolsonaro) para frases e rótulos."""
    return (f'SWITCH ( {v}, "Dilma Rousseff", "Dilma", "Fernando Haddad", "Haddad", "Geraldo Alckmin", "Alckmin", '
            f'"José Serra", "Serra", "Aécio Neves", "Aécio", "Jair Bolsonaro", "Bolsonaro", {v} )')


desenho("T14 · Resposta · HTML",
        "Topo da tela. Sem clique: quantas vezes o PT terminou o 1º turno atrás (ou à frente) e em quais anos, com os "
        "candidatos, e as seis urnas. Com um ano clicado na série: a margem do PT naquela eleição, a manchete do duelo e "
        "a urna do ano em destaque. Com uma região clicada, tudo no lugar dela ('no Nordeste'). Só lê contas 'T14 · …'.",
        f"""-- 1 · Leituras
VAR _k = [T14 · eleições com o PT atrás]
VAR _n = [T14 · eleições]
VAR _a26 = [T14 · PT atrás em 2026]
VAR _uf = [T14 · recorte]
VAR _ondeR = [T14 · onde]
VAR _ano = [T14 · ano escolhido]
VAR _mY = [T14 · margem do PT]
VAR _ptY = [T14 · PT %]
VAR _advY = [T14 · adversário %]
VAR _cptY = [T14 · candidato do PT]
VAR _cadvY = [T14 · adversário]
VAR _vezY = [T14 · vez em que o PT ficou atrás]
VAR _anos =
    ADDCOLUMNS (
        DATATABLE ( "a", INTEGER, {{ {_TAB_ANOS_R} }} ),
        "@m", VAR _a = [a] RETURN CALCULATE ( [T14 · margem do PT], 'Ano'[Ano] = _a ),
        "@pt", VAR _a = [a] RETURN CALCULATE ( [T14 · PT %], 'Ano'[Ano] = _a ),
        "@adv", VAR _a = [a] RETURN CALCULATE ( [T14 · adversário %], 'Ano'[Ano] = _a ),
        "@cpt", VAR _a = [a] RETURN CALCULATE ( [T14 · candidato do PT], 'Ano'[Ano] = _a ),
        "@cadv", VAR _a = [a] RETURN CALCULATE ( [T14 · adversário], 'Ano'[Ano] = _a ),
        "@vez", VAR _a = [a] RETURN CALCULATE ( [T14 · vez em que o PT ficou atrás], 'Ano'[Ano] = _a )
    ) /* lista */
-- 2 · Textos
VAR _clique = NOT ISBLANK ( _ano )
VAR _atras = FILTER ( _anos, [@m] < 0 ) /* lista */
VAR _nAtras = COUNTROWS ( _atras ) /* lista */
VAR _txtAnos =
    CONCATENATEX (
        _atras,
        "em " & [a] & " (" & [@cpt] & " " & {_pct("[@pt]")} & " × " & [@cadv] & " " & {_pct("[@adv]")} & ")",
        "; ",
        [a], ASC
    )
VAR _grande =
    SWITCH (
        TRUE (),
        _clique, FORMAT ( _mY * 100, "+0.0;−0.0;0.0" ) & "<small> p.p.</small>",
        _k = _n, FORMAT ( _k, "0" ) & " de " & FORMAT ( _n, "0" ),
        _a26 = 1, FORMAT ( _k, "0" ) & "ª vez",
        FORMAT ( _n - _k, "0" ) & " de " & FORMAT ( _n, "0" )
    )
VAR _clsGrande = IF ( _clique, IF ( _mY < 0, " flavio", " lula" ), "" )
VAR _onde = IF ( ISBLANK ( _ondeR ), "", " " & _ondeR )
VAR _abre = IF ( ISBLANK ( _ondeR ), "Em " & _ano, UPPER ( LEFT ( _ondeR, 1 ) ) & MID ( _ondeR, 2, 100 ) & ", em " & _ano )
VAR _manAno =
    _abre & ", " & {_curto("_cptY")} & " (" & {_pct("_ptY")} & ") terminou " & FORMAT ( ABS ( _mY ) * 100, "0.0" )
        & IF ( _mY < 0, " pontos atrás de ", " pontos à frente de " ) & {_curto("_cadvY")} & " (" & {_pct("_advY")} & ")"
VAR _man =
    SWITCH (
        TRUE (),
        _clique, _manAno,
        _k = _n, IF ( ISBLANK ( _uf ), "", _uf & ": " ) & "o PT terminou o 1º turno atrás do adversário nas seis eleições",
        _a26 = 1 && ISBLANK ( _uf ),
            "Pela " & FORMAT ( _k, "0" ) & "ª vez em seis eleições, o PT termina o 1º turno em segundo lugar",
        _a26 = 1,
            _uf & ": pela " & FORMAT ( _k, "0" ) & "ª vez em seis eleições, o PT termina o 1º turno atrás do adversário",
        _k = 0, "O PT ficou à frente nas seis eleições" & _onde & ", inclusive em 2026",
        "O PT ficou à frente em " & FORMAT ( _n - _k, "0" ) & " das seis eleições" & _onde & ", inclusive em 2026"
    )
VAR _soAnos = CONCATENATEX ( _atras, [a], ", ", [a], ASC )
VAR _sub =
    SWITCH (
        TRUE (),
        _clique && NOT ISBLANK ( _vezY ),
            "Foi a " & FORMAT ( _vezY, "0" ) & "ª vez em seis eleições que o PT ficou atrás" & _onde
                & ". Clique de novo no ano para voltar às seis eleições.",
        _clique, "O PT ficou à frente" & _onde & " nessa eleição. Clique de novo no ano para voltar às seis eleições.",
        _nAtras = 0, "",
        _nAtras <= 2, "Atrás " & _txtAnos & ".",
        "Atrás em " & _soAnos & "."
    )
-- 3 · Geometria e 4 · Marcação (urnas de 76 px a cada 92, a partir de x 1086)
VAR _urnas =
    CONCATENATEX (
        _anos,
        VAR _i = ( [a] - 2006 ) / 4
        VAR _vez = [@vez]
        VAR _apaga = IF ( _clique && [a] <> _ano, " apaga", "" )
        RETURN
            "<div class='ux " & IF ( [@m] < 0, "adv", "pt" ) & _apaga & " brota' style='left:" & ( 1086 + _i * 92 )
                & "px;animation-delay:" & ( 500 + _i * 140 ) & "ms'></div>"
                & "<div class='ua" & _apaga & "' style='left:" & ( 1086 + _i * 92 ) & "px'>" & [a] & "</div>"
                & IF (
                    NOT ISBLANK ( _vez ),
                    "<div class='uv mao entra" & _apaga & "' style='left:" & ( 1086 + _i * 92 ) & "px;animation-delay:"
                        & ( 900 + _i * 140 ) & "ms'>" & FORMAT ( _vez, "0" ) & "ª vez</div>"
                ),
        "",
        [a], ASC
    )
RETURN
    "<div class='tela t14r'>"
        & "<div class='num g" & _clsGrande & " sobe'>" & _grande & "</div>"
        & "<div class='man m sobe d2'>" & _man & "</div>"
        & "<div class='nota s entra d4'>" & _sub & "</div>"
        & "<div class='rot ur entra d3'>QUEM TERMINOU NA FRENTE, ELEIÇÃO A ELEIÇÃO</div>"
        & _urnas
        & "<div class='nota ul entra d8'>urna vermelha: o PT à frente · azul: o adversário</div>"
    & "</div>\"""")

desenho("T14 · Resposta · ALT", "Texto alternativo do topo da tela.",
        f"""-- 1 · Leituras
VAR _k = [T14 · eleições com o PT atrás]
VAR _a26 = [T14 · PT atrás em 2026]
VAR _uf = [T14 · recorte]
VAR _ano = [T14 · ano escolhido]
VAR _mY = [T14 · margem do PT]
-- 2 · Textos
RETURN
    IF ( ISBLANK ( _uf ), "Brasil", _uf ) & ": o PT terminou o 1º turno atrás do adversário em " & FORMAT ( _k, "0" )
        & " das seis eleições de 2006 a 2026" & IF ( _a26 = 1, ", inclusive em 2026.", "; em 2026, à frente." )
        & IF ( ISBLANK ( _ano ), "", " Em " & _ano & ", a margem do PT foi de " & FORMAT ( _mY * 100, "+0.0;−0.0;0.0" )
            & " pontos." )""")

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
            & "mais votado fora do PT no ano</span><span><i class='subl'></i>PT atrás</span></div>"
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
        "até a eleição seguinte (que se desenha em sequência), o sublinhado à mão sob o PT quando ele ficou atrás e o "
        "eixo com os candidatos. A 1ª eleição desenha a grade. Escala pelas contas 'T14 · escala …'. O clique num ano "
        "leva a resposta e os painéis das regiões àquela eleição.",
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
VAR _yRotPt = IF ( _ptCima, _yPt - 38, _yPt + 12 )
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
VAR _sublinha =
    IF (
        _atras,
        VAR _yy = _yRotPt + 27
        RETURN
            "<path class='subl traco' pathLength='1' style='animation-delay:" & ( _atraso + 900 ) & "ms' d='M"
                & FORMAT ( _x - 36, "0.0", "en-US" ) & "," & FORMAT ( _yy + 1, "0.0", "en-US" ) & " C"
                & FORMAT ( _x - 12, "0.0", "en-US" ) & "," & FORMAT ( _yy - 2, "0.0", "en-US" ) & " "
                & FORMAT ( _x + 12, "0.0", "en-US" ) & "," & FORMAT ( _yy + 3, "0.0", "en-US" ) & " "
                & FORMAT ( _x + 38, "0.0", "en-US" ) & "," & FORMAT ( _yy - 1, "0.0", "en-US" ) & "'/>"
    )
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _pt ),
        "<div class='tela ano'>"
            & "<div class='alvo' style='left:" & FORMAT ( _x - 128, "0.0", "en-US" ) & "px'></div>"
            & "<svg class='sv' width='1620' height='370' viewBox='0 0 1620 370'>"
                & _grade & _seg & _sublinha
                & "<circle class='ppt brota' style='animation-delay:" & ( _atraso - 120 ) & "ms' cx='" & _f & "' cy='"
                    & FORMAT ( _yPt, "0.0", "en-US" ) & "' r='7.5'/>"
                & "<circle class='padv brota' style='animation-delay:" & ( _atraso - 120 ) & "ms' cx='" & _f & "' cy='"
                    & FORMAT ( _yAdv, "0.0", "en-US" ) & "' r='7.5'/>"
            & "</svg>"
            & "<div class='vl vpt sobe' style='left:" & FORMAT ( _x - 60, "0.0", "en-US" ) & "px;top:"
                & FORMAT ( _yRotPt, "0.0", "en-US" ) & "px;animation-delay:" & ( _atraso + 200 )
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
        & "principal em cada 1º turno de 2006 a 2026; o PT ficou atrás em " & FORMAT ( _k, "0" ) & " delas. Clique "
        & "num ano para levar a resposta e as regiões àquela eleição.\"""")

_TAB_ANOS = ", ".join(f"{{ {a} }}" for a in ANOS)
_ORDEM_REG = ", ".join(f'"{r}", {i + 1}' for i, r in enumerate(REGIOES))

desenho("T14 · Regiões · HTML",
        "Uma entrada por região (granularidade Município[Região]), todas na mesma escala (10% a 70%): as linhas do PT e "
        "do adversário de 2006 a 2026 e os valores da eleição em destaque (a clicada na série ou 2026). Ignoram o filtro "
        "de estado; cada região com estado escolhido fica em destaque, com o que dela está no filtro ('região "
        "escolhida', 'região da Bahia', 'região de BA e SE'). O clique numa região leva a série e a resposta "
        "àquela região; o mouse abre o dossiê dela (ttT14Regiao).",
        f"""-- 1 · Leituras
VAR _r = [T14 · região do painel]
VAR _nRec = [T14 · UFs do recorte na região do painel]
VAR _nUf = [T14 · UFs da região]
VAR _deRec = [T14 · recorte na região do painel]
VAR _siglaRec = [T14 · sigla do recorte na região do painel]
VAR _ano = [T14 · ano dos painéis]
VAR _clique = NOT ISBLANK ( [T14 · ano escolhido] )
VAR _anos = DATATABLE ( "a", INTEGER, {{ {_TAB_ANOS} }} )
VAR _pts =
    ADDCOLUMNS (
        _anos,
        "@pt", VAR _a = [a] RETURN CALCULATE ( [T14 · PT % na região], 'Ano'[Ano] = _a ),
        "@adv", VAR _a = [a] RETURN CALCULATE ( [T14 · adversário % na região], 'Ano'[Ano] = _a )
    )
-- 3 · Geometria e 4 · Marcação (painéis de 300 px a cada 330; x do ano de 8 a 218; y de 10% a 70% em 110 px)
VAR _o = SWITCH ( _r, {_ORDEM_REG}, 0 )
VAR _px = ( _o - 1 ) * 330
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
VAR _ptA = MAXX ( FILTER ( _xy, [a] = _ano ), [@pt] ) /* lista */
VAR _advA = MAXX ( FILTER ( _xy, [a] = _ano ), [@adv] ) /* lista */
VAR _yApt = MAXX ( FILTER ( _xy, [a] = _ano ), [@yPt] ) /* lista */
VAR _yAadv = MAXX ( FILTER ( _xy, [a] = _ano ), [@yAdv] ) /* lista */
VAR _xA = 8 + ( _ano - 2006 ) / 4 * 42
VAR _sep = IF ( ABS ( _yApt - _yAadv ) < 16, 8 - ABS ( _yApt - _yAadv ) / 2, 0 )
VAR _cls = IF ( _nRec > 0, "pn sel", "pn" )
-- a nota à mão cabe ao lado do nome no painel de 300 px (nome ~9,6 px por letra, Caveat ~8): "região da Bahia"; com
-- o nome comprido, a sigla ("região de MS" no Centro-Oeste, "região de RN" no Nordeste)
VAR _cabe = INT ( ( 292 - 9.6 * LEN ( _r ) ) / 8 ) -- geometria
VAR _nota1 = "região " & _deRec
VAR _nota =
    SWITCH (
        TRUE (),
        _nRec = _nUf, "região escolhida",
        LEN ( _nota1 ) <= _cabe || ISBLANK ( _siglaRec ), _nota1,
        "região de " & _siglaRec
    )
VAR _marca =
    IF (
        _clique,
        "<line class='mk' x1='" & FORMAT ( _xA, "0.0", "en-US" ) & "' x2='" & FORMAT ( _xA, "0.0", "en-US" )
            & "' y1='4' y2='116'/>"
            & "<text class='ex' x='" & FORMAT ( _xA, "0.0", "en-US" ) & "' y='130' text-anchor='middle'>" & _ano & "</text>"
    )
VAR _eixo =
    IF (
        _clique && _ano > 2006 && _ano < 2026,
        "<text class='ex' x='0' y='130'>2006</text>",
        "<text class='ex' x='0' y='130'>2006</text><text class='ex' x='218' y='130' text-anchor='middle'>2026</text>"
    )
RETURN
    IF (
        _o > 0,
        "<div class='tela t14g'><div class='" & _cls & " sobe d" & ( 2 + _o ) & "' style='left:" & _px & "px'>"
            & "<div class='nm'>" & _r & IF ( _nRec > 0, " <span class='mao'>" & _nota & "</span>", "" )
            & "</div>"
            & "<svg width='300' height='132' viewBox='0 0 300 132'>"
                & "<line class='b' x1='0' x2='226' y1='116' y2='116'/>"
                & _marca
                & "<polyline class='lpt traco' pathLength='1' style='animation-delay:" & ( 600 + _o * 120 )
                    & "ms' points='" & _lPt & "'/>"
                & "<polyline class='ladv traco' pathLength='1' style='animation-delay:" & ( 600 + _o * 120 )
                    & "ms' points='" & _lAdv & "'/>"
                & "<circle class='ppt' cx='" & FORMAT ( _xA, "0.0", "en-US" ) & "' cy='" & FORMAT ( _yApt, "0.0", "en-US" )
                    & "' r='4'/>"
                & "<circle class='padv' cx='" & FORMAT ( _xA, "0.0", "en-US" ) & "' cy='"
                    & FORMAT ( _yAadv, "0.0", "en-US" ) & "' r='4'/>"
                & "<text class='vpt' x='" & FORMAT ( _xA + 10, "0.0", "en-US" ) & "' y='"
                    & FORMAT ( _yApt + 5 + IF ( _yApt >= _yAadv, _sep, -_sep ), "0.0", "en-US" )
                    & "'>" & {_pct("_ptA")} & "</text>"
                & "<text class='vadv' x='" & FORMAT ( _xA + 10, "0.0", "en-US" ) & "' y='"
                    & FORMAT ( _yAadv + 5 + IF ( _yAadv > _yApt, _sep, -_sep ), "0.0", "en-US" )
                    & "'>" & {_pct("_advA")} & "</text>"
                & _eixo
            & "</svg>"
        & "</div></div>"
    )""")

desenho("T14 · Regiões · ALT", "Texto alternativo das regiões.",
        """-- 1 · Leituras
VAR _sel = [T14 · região do recorte]
-- 2 · Textos
RETURN
    "Cinco pequenos gráficos, um por região, com o PT e o adversário de 2006 a 2026 na mesma escala"
        & IF ( ISBLANK ( _sel ), ".", "; em destaque, " & _sel & "." ) & " Clique numa região para ver a série dela.\"""")

desenho("T14 · Tooltip região · HTML",
        "Dossiê da região no tooltip dos painéis: os estados dela na eleição em destaque (a clicada na série ou 2026), "
        "cada um com o duelo PT × adversário em barras, do mais petista ao menos; quantos tiveram o PT à frente e em "
        "quantas das seis eleições o PT ficou à frente na região. Só lê contas.",
        f"""-- 1 · Leituras
VAR _r = [T14 · região do painel]
VAR _ano = [T14 · ano dos painéis]
VAR _fr = [T14 · eleições com o PT à frente]
VAR _n = [T14 · eleições]
VAR _nUf = [T14 · UFs da região]
VAR _nPt = [T14 · UFs da região com o PT à frente]
VAR _cpt = CALCULATE ( [T14 · candidato do PT], 'Ano'[Ano] = _ano )
VAR _cadv = CALCULATE ( [T14 · adversário], 'Ano'[Ano] = _ano )
VAR _todas = DATATABLE ( "uf", STRING, "reg", STRING, {{ {_TAB_UFS} }} )
VAR _daRegiao = FILTER ( _todas, [reg] = _r ) /* lista */
VAR _ufs =
    ADDCOLUMNS (
        _daRegiao,
        "@pt", VAR _u = [uf] RETURN CALCULATE ( [T14 · PT % da UF na eleição dos painéis], 'UF'[UF] = _u ),
        "@adv", VAR _u = [uf] RETURN CALCULATE ( [T14 · adversário % da UF na eleição dos painéis], 'UF'[UF] = _u )
    ) /* lista */
-- 2 · Textos
VAR _selo = "PT À FRENTE EM " & FORMAT ( _fr, "0" ) & " DE " & FORMAT ( _n, "0" )
VAR _clsSelo = IF ( _fr * 2 > _n, "selo vm", "selo az" )
VAR _mao =
    SWITCH (
        TRUE (),
        _nPt = _nUf, "todos com o PT",
        _nPt = 0, "nenhum com o PT",
        "dividida: " & FORMAT ( _nPt, "0" ) & " a " & FORMAT ( _nUf - _nPt, "0" )
    )
-- 3 · Geometria e 4 · Marcação (barras de duelo: 100% = 190 px)
VAR _linhas =
    CONCATENATEX (
        _ufs,
        "<div class='ln'><span class='a'>" & [uf] & "</span><span class='tr'><i class='bl barra-x' style='width:"
            & FORMAT ( 190 * [@pt], "0.0", "en-US" ) & "px'></i><i class='ba barra-x-dir' style='width:"
            & FORMAT ( 190 * [@adv], "0.0", "en-US" ) & "px'></i></span><span class='p'><b class='lula'>"
            & {_pct("[@pt]")} & "</b> × <b class='flavio'>" & {_pct("[@adv]")} & "</b></span></div>",
        "",
        [@pt] - [@adv], DESC
    )
RETURN
    "<div class='tela tt14r'><div class='fita'></div>"
        & "<div class='" & _clsSelo & "'>" & _selo & "</div>"
        & "<div class='an sobe'>" & _r & " · " & _ano & "</div>"
        & "<div class='rot entra d1'>OS ESTADOS · " & UPPER ( {_curto("_cpt")} ) & " × " & UPPER ( {_curto("_cadv")} )
            & "</div>"
        & "<div class='lista entra d2'>" & _linhas & "</div>"
        & "<div class='nota entra d3'>Votos válidos de cada estado, somando os municípios (sem o exterior).</div>"
        & "<div class='mao entra d5'>" & _mao & "</div>"
    & "</div>\"""")

desenho("T14 · Tooltip região · ALT", "Texto alternativo do dossiê da região.",
        """-- 1 · Leituras
VAR _r = [T14 · região do painel]
VAR _ano = [T14 · ano dos painéis]
VAR _nUf = [T14 · UFs da região]
VAR _nPt = [T14 · UFs da região com o PT à frente]
-- 2 · Textos
RETURN
    _r & ", " & _ano & ": o PT ficou à frente em " & FORMAT ( _nPt, "0" ) & " de " & FORMAT ( _nUf, "0" )
        & IF ( _nUf = 1, " estado.", " estados." )""")

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
