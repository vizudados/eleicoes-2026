# -*- coding: utf-8 -*-
"""desenho_t25 — tela 07 · Quem falta (código T25): quem mais falta às urnas, e onde? Dono: agente das telas 06 e 07.

    python -I -X utf8 pbi/scripts/desenho_t25.py        # grava pbi/dax/T25 Quem falta/… e pbi/spec/t25_mapa.json

Pedido do Alisson (23/10/2026): a ausência ganha um segundo painel, com filtro cruzado de verdade entre três peças —
"clicar no ano e o mapa e as faixas mudam; clicar numa faixa e o gráfico de anos muda e o mapa também".

  T25_Manchete_Html   a resposta que muda com o que está marcado: o % de quem faltou no recorte (número grande, com
                      contador), a frase "1 em cada N eleitores [da faixa] faltou", a comparação com a média do recorte
                      e as etiquetas do que está marcado (ano · idade · lugar), ou a dica de como cruzar
  T25_Anos_Topo/Html  os seis 1º turnos de 2006 a 2026 (granularidade Ano[Ano], filtro cruzado): uma coluna por ano,
                      com a linha tracejada da referência (a média do recorte com município marcado; todas as idades com
                      faixa marcada). Com faixa marcada, 2006 e 2010 ficam vazios ("sem idade": o TSE publica desde 2014)
  T25_Idade_Topo/Html as sete faixas de idade (granularidade T25 Faixa[Faixa], filtro cruzado) no ano e no lugar do
                      recorte, com a linha de todas as idades; * = voto facultativo
  T25_Mapa_Pontos     Deneb (Vega 6, canvas, seleção simples): um ponto por município, tamanho = quantos faltaram, cor =
                      a abstenção do município dividida pela média do recorte (0,6 ou menos = claro, na média =
                      areia escura, 1,5 ou mais = tinta). Contorno
                      das UFs em traço que se desenha, pontos que brotam em onda e a cor que esmaece de novo a cada
                      clique num ano ou numa faixa
  T25_Mapa_Legenda    como ler o ponto e a cor, com a média do recorte

Filtro cruzado (relações em pbi/modelo/t25_ausencia.py): ano → mapa, idade, manchete; faixa → mapa, anos, manchete;
município → anos, idade, manchete. A seleção de um visual não volta para ele mesmo; cada topo ignora o clique da própria
peça (Interacao NoFilter) para o título não ficar preso a um ano ou faixa. Ninguém filtra o VizuFilter de estado da
casca (árvore Região › Estado: um estado, uma região inteira ou vários estados; o nome do recorte vem das medidas comuns
Recorte · …, desenho_recorte.py).

Contas (pasta T25 Quem falta\\Contas): o ano do recorte é o marcado (o mais recente, se forem vários) ou 2026; sem faixa,
'Município ano' nos recortes de municípios e 'Comparecimento ano' (o total oficial, com o exterior) no Brasil — os mesmos
números da tela 06; com faixa, 'T25 Abstenção faixa' (+ 'T25 Abstenção exterior' no Brasil), que somam ao _BRASIL do
perfil do eleitor do TSE. Oráculo: mockup/data/eleicoes.json › paginas[6] (série e idade do Brasil).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from desenho_t01_t06_comum import URL_MIDIA, Gravador, dax  # noqa: E402
from desenho_t03_t05 import gravar_spec, ufs_geometria  # noqa: E402

P = "T25"
G = Gravador("T25 Quem falta")
MA = "'Município ano'"
CA = "'Comparecimento ano'"
FX = "'T25 Abstenção faixa'"
EX = "'T25 Abstenção exterior'"
FA = "'T25 Faixa'"
MU = "'Município'"
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]
# (faixa, ordem, rótulo curto, voto) — iguais a pbi/modelo/t25_ausencia.py
FAIXAS = [("16 e 17 anos", 1, "16–17", "facultativo"), ("18 a 24 anos", 2, "18–24", "obrigatório"),
          ("25 a 34 anos", 3, "25–34", "obrigatório"), ("35 a 44 anos", 4, "35–44", "obrigatório"),
          ("45 a 59 anos", 5, "45–59", "obrigatório"), ("60 a 69 anos", 6, "60–69", "obrigatório"),
          ("70 anos ou mais", 7, "70+", "facultativo")]
SEM_MUNICIPIO = (f"REMOVEFILTERS ( {MU}[CodIBGE], {MU}[X], {MU}[Y], {MU}[UF], {MU}[Rótulo], {MU}[Município] )")

# geometria da página (1920 × 1080; conteúdo em x 150–1770, y 140–1000)
MANCHETE = (150, 140, 760, 226)
ANOS_TOPO = (150, 372, 760, 62)
ANOS_CAIXA = (150, 436, 760, 234)
IDADE_TOPO = (150, 692, 760, 62)
IDADE_CAIXA = (150, 756, 760, 244)
MAPA = (950, 140, 820, 800)
LEGENDA = (950, 946, 820, 54)
SLOT = 760 / 6                       # largura de cada ano no bloco de anos
ALT_COL = 150                        # altura máxima da coluna (o teto da série)
TRILHO = (196, 450)                  # x e largura da barra de cada faixa
LINHA_FX = 35                        # passo vertical das faixas
TT_MUN = ("ttT25Municipio", 480, 360)
TT_ANO = ("ttT25Ano", 460, 440)
TT_IDADE = ("ttT25Idade", 440, 320)


def _media() -> str:
    return "[T25 · média (nome)]"


# ---------------------------------------------------------------------------------------------------- contas

def contas_extremo_serie() -> None:
    """Extremo recente calculado no recorte; nunca decidido por texto arredondado."""
    c = G.conta
    serie = """VAR _serie =
        ADDCOLUMNS (
            CALCULATETABLE ( VALUES ( 'Ano'[Ano] ), REMOVEFILTERS ( 'Ano' ) ),
            "@p", VAR _a = 'Ano'[Ano]
                RETURN CALCULATE ( [T25 · abstenção %], REMOVEFILTERS ( 'Ano' ), 'Ano'[Ano] = _a )
        )
    VAR _atual = CALCULATE ( [T25 · abstenção %], REMOVEFILTERS ( 'Ano' ), 'Ano'[Ano] = 2026 )
    VAR _anteriores = FILTER ( _serie, 'Ano'[Ano] < 2026 && NOT ISBLANK ( [@p] ) )"""
    for tipo, operador in (("menor", "<="), ("maior", ">=")):
        c(f"T25 · série · marco da {tipo}",
          "Último ano anterior com taxa menor/igual ou maior/igual à de 2026; vazio se extremo de toda a série.",
          serie + f"""
    RETURN MAXX ( FILTER ( _anteriores, [@p] {operador} _atual ), 'Ano'[Ano] )""", "0")
    c("T25 · série · tipo de manchete", "Variação de pelo menos um ponto: tendência; abaixo disso, extremo recente com o maior intervalo.",
      serie + """
    VAR _delta = [T25 · variação da série em p.p.]
    VAR _aMin = [T25 · série · marco da menor]
    VAR _aMax = [T25 · série · marco da maior]
    VAR _nMin = COUNTROWS ( FILTER ( _anteriores, ISBLANK ( _aMin ) || 'Ano'[Ano] > _aMin ) )
    VAR _nMax = COUNTROWS ( FILTER ( _anteriores, ISBLANK ( _aMax ) || 'Ano'[Ano] > _aMax ) )
    RETURN SWITCH ( TRUE (),
        ISBLANK ( _delta ), "sem série",
        ROUND ( ABS ( _delta ), 10 ) >= 1, "tendência",
        _nMin > 0 && _nMin >= _nMax, "menor",
        _nMax > 0, "maior",
        "estável"
    )""", "texto")
    c("T25 · série · marco do extremo", "Ano usado na manchete do extremo recente; vazio significa toda a série.",
      """SWITCH ( [T25 · série · tipo de manchete],
          "menor", [T25 · série · marco da menor],
          "maior", [T25 · série · marco da maior] )""", "0")

def contas() -> None:
    contas_extremo_serie()
    c = G.conta
    c("T25 · turno", "Turno escolhido na casca.",
      'IF ( [Eleição · pós] = 1, "2º turno", "1º turno" )', "texto")
    c("T25 · idade ano", "Pós: idade de 2026/1º turno; Pré: ano escolhido.",
      "IF ( [Eleição · pós] = 1, 2026, [T25 · ano] )", "0")
    c("T25 · idade disponível", "Existe perfil do primeiro turno para o ano da peça etária.",
      "INT ( [T25 · idade ano] >= 2014 )", "0")
    for nome in ("aptos", "abstenções"):
        c(f"T25 · idade {nome}", "Perfil etário do primeiro turno, no lugar e faixa; nunca usa o segundo turno.", dax(f"""
            VAR _a = [T25 · idade ano]
            RETURN CALCULATE ( [T25 · {nome} por idade (cru)], REMOVEFILTERS ( 'Ano' ), 'Ano'[Ano] = _a )
            """), "#,0")
    c("T25 · idade abstenção %", "Taxa da faixa no primeiro turno, no ano da peça etária.",
      "DIVIDE ( [T25 · idade abstenções], [T25 · idade aptos] )", "0.0%")
    c("T25 · idade todas as idades", "Referência oficial de todas as idades no mesmo primeiro turno; mantém a abrangência original.", dax(f"""
        VAR _a = [T25 · idade ano]
        RETURN CALCULATE (
            DIVIDE (
                IF ( [T25 · sem exterior] = 1, SUM ( {MA}[Abstencoes] ), SUM ( {CA}[Abstencoes] ) ),
                IF ( [T25 · sem exterior] = 1, SUM ( {MA}[Aptos] ), SUM ( {CA}[Aptos] ) )
            ),
            REMOVEFILTERS ( 'Ano' ), 'Ano'[Ano] = _a
        )
        """), "0.0%")
    for ano in ANOS:
        c(f"T25 · idade abstenção % em {ano}", "Série por idade exclusivamente no primeiro turno.",
          f"CALCULATE ( DIVIDE ( [T25 · abstenções por idade (cru)], [T25 · aptos por idade (cru)] ), 'Ano'[Ano] = {ano} )", "0.0%")
    # estado do que está marcado
    c("T25 · com faixa", "1 quando há faixa de idade marcada (clique no bloco de idade) ou na linha/dica de uma faixa.",
      f"INT ( [Eleição · pós] = 0 && ISFILTERED ( {FA} ) )", "0")
    c("T25 · com município", "1 quando há município marcado no mapa (ou na linha/dica de um município).",
      f"INT ( ISFILTERED ( {MU} ) )", "0")
    c("T25 · com ano", "1 quando há ano marcado no bloco de anos (ou na linha/dica de um ano).",
      "INT ( ISFILTERED ( 'Ano' ) )", "0")
    c("T25 · sem exterior", "1 quando o recorte é de municípios (filtro de UF ou município marcado): as contas somam os "
      "municípios; 0 no Brasil inteiro, que usa o total oficial, com o exterior (como a tela 06).",
      f"INT ( ISCROSSFILTERED ( {MU} ) )", "0")
    c("T25 · ano", "Ano do recorte: o marcado no bloco de anos (o mais recente, se forem vários) ou 2026; na linha de um "
      "ano, o próprio.", "MAX ( 'Ano'[Ano] )", "0")
    c("T25 · tem idade no ano", "1 quando o ano do recorte tem perfil por idade (o TSE publica desde 2014).",
      "INT ( [Eleição · pós] = 0 && [T25 · ano] >= 2014 )", "0")
    c("T25 · faixas marcadas", "Quantas faixas de idade estão marcadas (0 sem faixa).",
      f"IF ( [T25 · com faixa] = 1, COUNTROWS ( VALUES ( {FA}[Faixa] ) ), 0 )", "0")
    c("T25 · faixa", "A faixa marcada (ex.: 18 a 24 anos), ou \"N faixas de idade\"; vazio sem faixa.", dax(f"""
        SWITCH (
            TRUE (),
            [T25 · faixas marcadas] = 1, SELECTEDVALUE ( {FA}[Faixa] ),
            [T25 · faixas marcadas] > 1, FORMAT ( [T25 · faixas marcadas], "0" ) & " faixas de idade"
        )
        """), "texto")
    c("T25 · municípios marcados", "Quantos municípios estão marcados no mapa (0 sem marca).",
      f"IF ( [T25 · com município] = 1, COUNTROWS ( VALUES ( {MU}[CodIBGE] ) ), 0 )", "0")
    c("T25 · município", "Nome (UF) do município marcado ou da linha; vazio se não for um só.",
      f"IF ( [T25 · municípios marcados] = 1, SELECTEDVALUE ( {MU}[Rótulo] ) )", "texto")
    c("T25 · região do município", "Região do município da linha.", f"SELECTEDVALUE ( {MU}[Região] )", "texto")
    c("T25 · recorte", "A área das médias (ignora o município marcado), da medida comum [Recorte · nome]: 'Brasil', o "
      "estado ('Bahia'), a região inteira ('Nordeste') ou vários estados ('MG e SP', '3 estados').", "[Recorte · nome]",
      "texto")
    c("T25 · média (nome)", "Nome da média de referência (a do recorte, sem o município marcado): 'média nacional' no "
      "Brasil, 'média estadual' num estado, 'média do Nordeste' numa região inteira, 'média de MG e SP' em vários "
      "estados.", dax("""
        SWITCH (
            [Recorte · tipo],
            "Brasil", "média nacional",
            "UF", "média estadual",
            "média " & [Recorte · de]
        )
        """), "texto")
    c("T25 · lugar", "O lugar que a tela mostra: o município marcado, N municípios marcados ou o recorte de estado "
      "(Brasil, o estado, a região, os estados).",
      dax("""
        SWITCH (
            TRUE (),
            [T25 · municípios marcados] = 1, [T25 · município],
            [T25 · municípios marcados] > 1, FORMAT ( [T25 · municípios marcados], "#,0" ) & " municípios marcados",
            [T25 · recorte]
        )
        """), "texto")
    # o núcleo: quem faltou e quem estava apto, sem fixar o ano (cru) e no ano do recorte
    for nome, col_ in (("abstenções", "Abstencoes"), ("aptos", "Aptos")):
        desc = "Eleitores que faltaram" if nome == "abstenções" else "Eleitores aptos"
        c(f"T25 · {nome} por idade (cru)", f"{desc} no perfil por idade (T25 Abstenção faixa) no contexto, mais o "
          "exterior quando o recorte é o Brasil inteiro; soma os anos do contexto.",
          f"SUM ( {FX}[{col_}] ) + IF ( [T25 · sem exterior] = 0, SUM ( {EX}[{col_}] ) )", "#,0")
        c(f"T25 · {nome} (cru)", f"{desc} no contexto, sem fixar o ano: com faixa marcada, o perfil por idade; sem "
          "faixa, 'Município ano' nos recortes de municípios e o total oficial ('Comparecimento ano', com o exterior) "
          "no Brasil.", dax(f"""
            IF ( [Eleição · pós] = 1,
                IF ( [T25 · sem exterior] = 1,
                    CALCULATE ( SUM ( 'Município segundo turno'[{col_}] ), 'Município segundo turno'[Ano] = MAX ( 'Ano'[Ano] ) ),
                    CALCULATE ( SUM ( 'Comparecimento turno'[{col_}] ), 'Comparecimento turno'[Turno] = 2,
                        'Comparecimento turno'[Abrangência] = "com_exterior", 'Comparecimento turno'[Ano] = MAX ( 'Ano'[Ano] ) ) ),
                IF ( [T25 · com faixa] = 1, [T25 · {nome} por idade (cru)],
                    IF ( [T25 · sem exterior] = 1, SUM ( {MA}[{col_}] ), SUM ( {CA}[{col_}] ) ) )
            )
            """), "#,0")
        c(f"T25 · {nome}", f"{desc} no ano do recorte (o marcado ou 2026), no lugar e na faixa do contexto."
          + (" Tamanho do ponto no mapa." if nome == "abstenções" else ""), dax(f"""
            VAR _ano = [T25 · ano]
            RETURN
                CALCULATE ( [T25 · {nome} (cru)], 'Ano'[Ano] = _ano )
            """), "#,0", "Brasil 2026 = 33.469.244 (paginas[6].serie[2026].abstencoes)" if nome == "abstenções"
          else "Brasil 2026 = 158.745.502 (paginas[6].serie[2026].aptos_txt = 158,7 mi)")
    c("T25 · abstenção %", "Parcela dos aptos que faltou no ano, no lugar e na faixa do recorte (0–1): o número grande "
      "da manchete; na linha de um ano, de uma faixa ou de um município, o % dela.",
      "DIVIDE ( [T25 · abstenções], [T25 · aptos] )", "0.0%", "Brasil 2026 = 21,1% (paginas[6].abstencao_2026_txt); "
      "18 a 24 anos 2026 = 23,2% (paginas[6].idade[1].pct2026)")
    c("T25 · um em cada", "De quantos em quantos eleitores do recorte um faltou (1 em cada N), arredondado.",
      "IF ( [T25 · abstenção %] > 0, ROUND ( DIVIDE ( 1, [T25 · abstenção %] ), 0 ) )", "0", "Brasil 2026 = 5")
    c("T25 · em cada 10", "Quantos em cada 10 eleitores do recorte faltaram, arredondado (para a frase quando é 35% ou "
      "mais).", "IF ( [T25 · abstenção %] > 0, ROUND ( [T25 · abstenção %] * 10, 0 ) )", "0")
    c("T25 · abstenção % do recorte", "A mesma abstenção sem o município marcado ou da linha: a média do recorte de "
      "estado (as UFs escolhidas; ou o Brasil, com o exterior) no ano e na faixa do contexto (0–1). Referência da cor do mapa e das comparações.",
      dax(f"""
        CALCULATE (
            [T25 · abstenção %],
            {SEM_MUNICIPIO}
        )
        """), "0.0%")
    c("T25 · abstenção relativa", "Abstenção do município da linha dividida pela média do recorte (1 = na média, 2 = o "
      "dobro, 0,5 = a metade). Cor do ponto no mapa.",
      "DIVIDE ( [T25 · abstenção %], [T25 · abstenção % do recorte] )", "0.00")
    c("T25 · diferença para o recorte", "Abstenção do lugar menos a média do recorte, em pontos percentuais.",
      "IF ( NOT ISBLANK ( [T25 · abstenção %] ), ( [T25 · abstenção %] - [T25 · abstenção % do recorte] ) * 100 )",
      "0.0")
    # série dos seis anos (manchete do bloco, dossiês e ALT)
    for ano in ANOS:
        c(f"T25 · abstenção % em {ano}", f"Abstenção no 1º turno de {ano} no lugar e na faixa do contexto (0–1); vazio "
          "sem dado (por idade, só de 2014 em diante).",
          f"CALCULATE ( DIVIDE ( [T25 · abstenções (cru)], [T25 · aptos (cru)] ), 'Ano'[Ano] = {ano} )", "0.0%",
          {2006: "Brasil = 16,8% (paginas[6].abstencao_2006_txt)", 2026: "Brasil = 21,1%"}.get(ano))
    c("T25 · referência da série", "Linha tracejada do bloco de anos (0–1): com município marcado, a média do recorte "
      "(as UFs escolhidas ou o Brasil) no mesmo ano e faixa; só com faixa marcada, todas as idades do lugar; sem marca, vazio.",
      dax(f"""
        SWITCH (
            TRUE (),
            [T25 · com município] = 1, [T25 · abstenção % do recorte],
            [T25 · com faixa] = 1, CALCULATE ( [T25 · abstenção %], REMOVEFILTERS ( {FA} ) ),
            BLANK ()
        )
        """), "0.0%")
    c("T25 · referência da série (nome)", "Nome da linha de referência do bloco de anos.", dax("""
        SWITCH (
            TRUE (),
            [T25 · com município] = 1, [T25 · média (nome)],
            [T25 · com faixa] = 1, "todas as idades",
            ""
        )
        """), "texto")
    c("T25 · teto da série", "Maior valor entre os seis anos (a abstenção e a referência) no lugar e na faixa do "
      "contexto (0–1): a escala das colunas do bloco de anos.", dax("""
        MAXX (
            CALCULATETABLE ( VALUES ( 'Ano'[Ano] ), REMOVEFILTERS ( 'Ano' ) ),
            VAR _a = 'Ano'[Ano]
            RETURN
                MAX (
                    CALCULATE ( DIVIDE ( [T25 · abstenções (cru)], [T25 · aptos (cru)] ), 'Ano'[Ano] = _a ),
                    CALCULATE ( [T25 · referência da série], 'Ano'[Ano] = _a )
                )
        )
        """), "0.0%")
    c("T25 · primeiro ano da série", "Primeiro ano com dado no lugar e na faixa do contexto (2006, ou 2014 com faixa).",
      dax("""
        MINX (
            FILTER (
                CALCULATETABLE ( VALUES ( 'Ano'[Ano] ), REMOVEFILTERS ( 'Ano' ) ),
                VAR _a = 'Ano'[Ano]
                RETURN
                    NOT ISBLANK ( CALCULATE ( [T25 · aptos (cru)], 'Ano'[Ano] = _a ) )
            ),
            'Ano'[Ano]
        )
        """), "0")
    c("T25 · abstenção % no primeiro ano", "Abstenção no primeiro ano com dado (0–1).", dax("""
        VAR _a0 = [T25 · primeiro ano da série]
        RETURN
            CALCULATE ( DIVIDE ( [T25 · abstenções (cru)], [T25 · aptos (cru)] ), 'Ano'[Ano] = _a0 )
        """), "0.0%")
    c("T25 · variação da série em p.p.", "Abstenção de 2026 menos a do primeiro ano com dado, em pontos percentuais.",
      "IF ( [T25 · primeiro ano da série] < 2026, ( [T25 · abstenção % em 2026] - [T25 · abstenção % no primeiro ano] ) "
      "* 100 )", "0.0", "Brasil = +4,3 (paginas[6].serie: 16,8% → 21,1%)")
    # idade (linha de uma faixa, régua e ranking)
    c("T25 · faixa da linha", "Faixa de idade da linha (ou da dica).", f"SELECTEDVALUE ( {FA}[Faixa] )", "texto")
    c("T25 · ordem da faixa", "Ordem da faixa da linha (1 = 16 e 17 anos … 7 = 70 ou mais).",
      f"SELECTEDVALUE ( {FA}[Ordem] )", "0")
    c("T25 · voto da faixa", "obrigatório ou facultativo, na faixa da linha.", f"SELECTEDVALUE ( {FA}[Voto] )", "texto")
    c("T25 · abstenção % todas as idades", "Abstenção do lugar no ano do recorte, com todas as idades (0–1): a linha "
      "de referência do bloco de idade.", f"CALCULATE ( [T25 · abstenção %], REMOVEFILTERS ( {FA} ) )", "0.0%")
    c("T25 · teto por idade", "Maior abstenção entre as sete faixas no lugar e no ano do recorte (0–1): a escala das "
      "barras do bloco de idade.", dax(f"""
        MAXX (
            CALCULATETABLE ( VALUES ( {FA}[Ordem] ), REMOVEFILTERS ( {FA} ) ),
            VAR _k = {FA}[Ordem]
            RETURN
                CALCULATE ( [T25 · idade abstenção %], REMOVEFILTERS ( {FA} ), {FA}[Ordem] = _k )
        )
        """), "0.0%")
    ranking = f"""VAR _faixas =
            ADDCOLUMNS (
                CALCULATETABLE ( VALUES ( {FA}[Faixa] ), REMOVEFILTERS ( {FA} ) ),
                "@p",
                    VAR _f = {FA}[Faixa]
                    RETURN
                        CALCULATE ( [T25 · idade abstenção %], REMOVEFILTERS ( {FA} ), {FA}[Faixa] = _f )
            )
        VAR _comDado = FILTER ( _faixas, NOT ISBLANK ( [@p] ) )""".replace(chr(10), chr(10) + "    ")
    for qual, ordem, fn, orac in (("mais", "DESC", "MAXX", "Brasil 2026 = 70 anos ou mais, 49,2%"),
                                  ("menos", "ASC", "MINX", "Brasil 2026 = 16 e 17 anos, 12,7%")):
        c(f"T25 · faixa que {qual} falta", f"Faixa de idade com a {'maior' if qual == 'mais' else 'menor'} abstenção "
          "no lugar e no ano do recorte (ignora a faixa marcada).", dax(f"""
            {ranking}
            RETURN
                MAXX ( TOPN ( 1, _comDado, [@p], {ordem}, {FA}[Faixa], ASC ), {FA}[Faixa] )
            """), "texto", orac)
        c(f"T25 · faixa que {qual} falta %", f"Abstenção da faixa que {qual} falta (0–1).", dax(f"""
            {ranking}
            RETURN
                {fn} ( _comDado, [@p] )
            """), "0.0%")
    c("T25 · vezes entre as faixas", "Quantas vezes a faixa que mais falta falta mais que a que menos falta.",
      "DIVIDE ( [T25 · faixa que mais falta %], [T25 · faixa que menos falta %] )", "0.0", "Brasil 2026 = 3,9 (49,2% ÷ 12,7%)")
    # composição de quem faltou por idade (dica do ano)
    for nome, k, _curta, _v in FAIXAS:
        for qual, base in (("que faltaram", "abstenções"), ("aptos", "aptos")):
            c(f"T25 · parte dos {qual} · {nome}", f"Parcela dos {'faltosos' if qual == 'que faltaram' else 'eleitores aptos'}"
              f" do lugar, no ano da linha, que tinha {nome} (0–1), sem a faixa marcada.", dax(f"""
                DIVIDE (
                    CALCULATE ( [T25 · {base} por idade (cru)], REMOVEFILTERS ( {FA} ), {FA}[Ordem] = {k} ),
                    CALCULATE ( [T25 · {base} por idade (cru)], REMOVEFILTERS ( {FA} ) )
                )
                """), "0%")
    c("T25 · faixa mais acima do seu peso", "Faixa cujo peso entre os que faltaram mais passa do peso entre os aptos, "
      "no lugar e no ano da linha (a nota à mão da dica do ano).", dax(f"""
        VAR _t =
            ADDCOLUMNS (
                CALCULATETABLE ( VALUES ( {FA}[Curta] ), REMOVEFILTERS ( {FA} ) ),
                "@r",
                    VAR _c = {FA}[Curta]
                    RETURN
                        DIVIDE (
                            DIVIDE (
                                CALCULATE ( [T25 · abstenções por idade (cru)], REMOVEFILTERS ( {FA} ), {FA}[Curta] = _c ),
                                CALCULATE ( [T25 · abstenções por idade (cru)], REMOVEFILTERS ( {FA} ) )
                            ),
                            DIVIDE (
                                CALCULATE ( [T25 · aptos por idade (cru)], REMOVEFILTERS ( {FA} ), {FA}[Curta] = _c ),
                                CALCULATE ( [T25 · aptos por idade (cru)], REMOVEFILTERS ( {FA} ) )
                            )
                        )
            )
        RETURN
            MAXX ( TOPN ( 1, FILTER ( _t, NOT ISBLANK ( [@r] ) ), [@r], DESC, {FA}[Curta], ASC ), {FA}[Curta] )
        """), "texto")
    c("T25 · faixa mais acima do seu peso (vezes)", "Quantas vezes o peso dessa faixa entre os que faltaram passa o peso "
      "dela entre os aptos.", dax(f"""
        VAR _c = [T25 · faixa mais acima do seu peso]
        RETURN
            IF (
                NOT ISBLANK ( _c ),
                DIVIDE (
                    DIVIDE (
                        CALCULATE ( [T25 · abstenções por idade (cru)], REMOVEFILTERS ( {FA} ), {FA}[Curta] = _c ),
                        CALCULATE ( [T25 · abstenções por idade (cru)], REMOVEFILTERS ( {FA} ) )
                    ),
                    DIVIDE (
                        CALCULATE ( [T25 · aptos por idade (cru)], REMOVEFILTERS ( {FA} ), {FA}[Curta] = _c ),
                        CALCULATE ( [T25 · aptos por idade (cru)], REMOVEFILTERS ( {FA} ) )
                    )
                )
            )
        """), "0.0")
    # dica da faixa
    for qual, base in (("que faltaram", "abstenções"), ("aptos", "aptos")):
        c(f"T25 · parte dos {qual} (faixa)", f"Parcela dos {'faltosos' if qual == 'que faltaram' else 'aptos'} do lugar, "
          "no ano do recorte, que está na faixa da linha (0–1).", dax(f"""
            VAR _ano = [T25 · idade ano]
            RETURN
                DIVIDE (
                    CALCULATE ( [T25 · {base} por idade (cru)], 'Ano'[Ano] = _ano ),
                    CALCULATE ( [T25 · {base} por idade (cru)], REMOVEFILTERS ( {FA} ), 'Ano'[Ano] = _ano )
                )
            """), "0%")
    c("T25 · vezes a média (faixa)", "Abstenção da faixa da linha dividida pela de todas as idades, no lugar e no ano.",
      "DIVIDE ( [T25 · idade abstenção %], [T25 · idade todas as idades] )", "0.0")
    # dica do ano: quem disputou (os dois mais votados no Brasil, o primeiro antes)
    c("T25 · disputa do ano", "Os dois mais votados no 1º turno do ano da linha (Brasil, resultado oficial), o primeiro "
      "antes, com o partido.", dax("""
        VAR _1 = CALCULATE ( SELECTEDVALUE ( 'Candidato ano'[Candidato] ), 'Candidato ano'[Posição] = 1 )
        VAR _1p = CALCULATE ( SELECTEDVALUE ( 'Candidato ano'[Partido] ), 'Candidato ano'[Posição] = 1 )
        VAR _2 = CALCULATE ( SELECTEDVALUE ( 'Candidato ano'[Candidato] ), 'Candidato ano'[Posição] = 2 )
        VAR _2p = CALCULATE ( SELECTEDVALUE ( 'Candidato ano'[Partido] ), 'Candidato ano'[Posição] = 2 )
        VAR _a = [T25 · ano]
        VAR _pt = CALCULATE ( SELECTEDVALUE ( 'PT histórico Brasil'[Candidato PT] ), 'PT histórico Brasil'[Ano] = _a, 'PT histórico Brasil'[Turno] = 2 )
        VAR _adv = CALCULATE ( SELECTEDVALUE ( 'PT histórico Brasil'[Adversário] ), 'PT histórico Brasil'[Ano] = _a, 'PT histórico Brasil'[Turno] = 2 )
        VAR _saldo = CALCULATE ( SUM ( 'PT histórico Brasil'[VotosPT] ) - SUM ( 'PT histórico Brasil'[VotosAdversario] ), 'PT histórico Brasil'[Ano] = _a, 'PT histórico Brasil'[Turno] = 2 )
        RETURN IF ( [Eleição · pós] = 1, IF ( _saldo >= 0, _pt & " e " & _adv, _adv & " e " & _pt ),
            IF ( NOT ISBLANK ( _1 ), _1 & " (" & _1p & ") e " & _2 & " (" & _2p & ")" )
        )
        """), "texto")


# ---------------------------------------------------------------------------------------------------- desenho
def _sublinhado(largura: int = 250) -> str:
    """Traço à mão sob 'não foram votar' (literal DAX), que se desenha."""
    svg = (f"<svg class='subl' viewBox='0 0 300 16' preserveAspectRatio='none' aria-hidden='true' "
           f"style='width:{largura}px'><path pathLength='1' class='traco' style='animation-delay:1.1s' "
           "d='M3,10 C60,4 140,13 205,7 C240,4 270,6 297,9' fill='none' stroke='#1C1915' stroke-width='3' "
           "stroke-linecap='round'/></svg>")
    return '"' + svg.replace('"', '""') + '"'


def desenho() -> None:
    d = G.desenho
    # ------------------------------------------------------------------ manchete
    d("T25 · Manchete · HTML", "A resposta da tela 07 que muda com o que está marcado: o % de quem faltou (número "
      "grande), a frase \"1 em cada N eleitores faltou\", a comparação com a média do recorte e as etiquetas do que está "
      "marcado (ano · idade · lugar) ou a dica de como cruzar. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _pct = [T25 · abstenção %]
        VAR _ano = [T25 · ano]
        VAR _comAno = [T25 · com ano]
        VAR _comFaixa = [T25 · com faixa]
        VAR _nFaixas = [T25 · faixas marcadas]
        VAR _faixa = [T25 · faixa]
        VAR _nMun = [T25 · municípios marcados]
        VAR _lugar = [T25 · lugar]
        VAR _temIdade = [T25 · tem idade no ano]
        VAR _um = [T25 · um em cada]
        VAR _dez = [T25 · em cada 10]
        VAR _ref = [T25 · abstenção % do recorte]
        VAR _dif = [T25 · diferença para o recorte]
        VAR _todas = [T25 · abstenção % todas as idades]
        -- 2 · Textos
        VAR _semDado = ISBLANK ( _pct )
        VAR _semIdade = _comFaixa = 1 && _temIdade = 0
        VAR _txtPct = IF ( _semDado, "<span class='vz'>sem dado</span>", FORMAT ( _pct, "0.00%" ) )
        VAR _media = {_media()}
        VAR _quantos =
            IF ( _pct >= 0.35, FORMAT ( _dez, "0" ) & " em cada 10", "1 em cada " & FORMAT ( _um, "0" ) )
        VAR _verbo = IF ( _pct >= 0.35, "faltaram", "faltou" )
        VAR _quem =
            "eleitores"
                & SWITCH (
                    TRUE (),
                    _nFaixas = 1, " de " & SUBSTITUTE ( _faixa, "16 e 17", "16 ou 17" ),
                    _nFaixas > 1, " das faixas de idade marcadas",
                    ""
                )
        VAR _compara =
            SWITCH (
                TRUE (),
                _nMun > 0 && NOT ISBLANK ( _ref ),
                    IF (
                        ABS ( _dif ) < 0.05,
                        ", bem na " & _media & " (" & @PCT(_ref)@ & ")",
                        ", " & FORMAT ( ABS ( _dif ), "0.0" ) & IF ( ABS ( _dif ) < 2, " ponto ", " pontos " )
                            & IF ( _dif > 0, "acima", "abaixo" ) & " da " & _media & " (" & @PCT(_ref)@ & ")"
                    ),
                _comFaixa = 1 && NOT ISBLANK ( _todas ), "; com todas as idades, " & @PCT(_todas)@,
                ""
            )
        VAR _frase =
            SWITCH (
                TRUE (),
                _semIdade, "Em " & _ano & ", o TSE ainda não publicava a idade de quem faltou.",
                _semDado, "Sem dado neste cruzamento.",
                _quantos & " " & _quem & " " & _verbo & _compara & "."
            )
        VAR _chips =
            IF ( _comAno = 1, "<span class='chip'><b>ano</b>" & _ano & "</span>" )
                & IF ( _comFaixa = 1, "<span class='chip'><b>idade</b>" & @ESC(_faixa)@ & "</span>" )
                & IF ( _nMun > 0, "<span class='chip'><b>lugar</b>" & @ESC(_lugar)@ & "</span>" )
        VAR _linha =
            SWITCH (
                TRUE (),
                _semIdade,
                    "<div class='aviso'><span class='ast'>*</span>Escolha 2014, 2018, 2022 ou 2026 para ver por idade.</div>",
                _chips = "",
                    "<div class='dica'>" & IF ( [Eleição · pós] = 1, "Cruze ano e mapa. Idade: 1º turno de 2026.", "Cruze ano, idade e mapa." ) & "</div>"
                        & {_seta_mao()},
                "<div class='marc'>" & _chips & "<span class='dica'>clique de novo para desmarcar</span></div>"
            )
        -- 4 · Marcação
        RETURN
            "<div class='tela mq'>"
                & "<div class='sob sobe'>Quem falta · " & @ESC(_lugar)@ & " · " & [T25 · turno] & " de " & _ano & "</div>"
                & "<div class='topo'><div class='big sobe d1'>" & _txtPct & "</div>"
                & "<div class='lado sobe d2'><div class='nfv'>não foram votar</div>" & {_sublinhado(236)}
                & "<div class='txt fr'>" & @ESC(_frase)@ & "</div></div></div>"
                & "<div class='linha sobe d4'>" & _linha & "</div>"
            & "</div>"
        """))
    d("T25 · Manchete · ALT", "Texto para leitor de tela da manchete.", dax("""
        LEFT (
            [T25 · lugar] & ", " & [T25 · turno] & " de " & [T25 · ano]
                & IF ( [T25 · com faixa] = 1, ", " & [T25 · faixa] ) & ": "
                & IF ( ISBLANK ( [T25 · abstenção %] ), "sem dado neste cruzamento.",
                    @PCT([T25 · abstenção %])@ & " dos eleitores não foram votar." )
                & IF ( [Eleição · pós] = 1, " Ano e mapa no segundo turno; idade no primeiro turno de 2026.", " Clique num ano, numa idade ou num ponto do mapa para cruzar." ),
            250
        )
        """))
    # ------------------------------------------------------------------ anos
    d("T25 · Anos topo · HTML", "Título do bloco de anos: o lugar (e a faixa), quanto a abstenção mudou desde o primeiro "
      "ano com dado e a legenda da linha de referência. Ignora o clique no próprio bloco.", dax("""
        -- 1 · Leituras
        VAR _lugar = [T25 · lugar]
        VAR _faixa = [T25 · faixa]
        VAR _comFaixa = [T25 · com faixa]
        VAR _a0 = [T25 · primeiro ano da série]
        VAR _dpp = [T25 · variação da série em p.p.]
        VAR _nomeRef = [T25 · referência da série (nome)]
        -- 2 · Textos
        VAR _rot = "A ausência ano a ano · " & [T25 · turno] & " · " & @ESC(_lugar)@ & IF ( _comFaixa = 1, " · " & @ESC(_faixa)@ )
        VAR _tipo = [T25 · série · tipo de manchete]
        VAR _marco = [T25 · série · marco do extremo]
        VAR _p0 = [T25 · abstenção % no primeiro ano]
        VAR _p26 = [T25 · abstenção % em 2026]
        VAR _intervalo = IF ( ISBLANK ( _marco ), "da série", "desde " & FORMAT ( _marco, "0" ) )
        VAR _man =
            SWITCH ( _tipo,
                "menor", "Em 2026, a menor abstenção " & _intervalo,
                "maior", "Em 2026, a maior abstenção " & _intervalo,
                "estável", "Em 2026, a abstenção ficou em " & @PCT(_p26)@,
                "sem série", "Sem série neste cruzamento",
                IF ( [Eleição · pós] = 1,
                    IF ( _dpp > 0, "Subiu de ", "Caiu de " ) & @PCT(_p0)@ & " para " & @PCT(_p26)@,
                    IF ( _dpp > 0, "Subiu ", "Caiu " ) & FORMAT ( ABS ( _dpp ), "0.0" )
                        & IF ( ABS ( _dpp ) < 2, " ponto", " pontos" ) & " desde " & _a0
                )
            )
        VAR _lado =
            IF ( _nomeRef <> "", "<span class='lg'><i></i>" & _nomeRef & "</span>" )
                & IF ( _comFaixa = 1, "<span class='so'>idade só desde 2014</span>" )
        -- 4 · Marcação
        RETURN
            "<div class='tela at'><div class='l1'><div class='rot sobe'>" & _rot & "</div>"
                & "<div class='lado entra d3'>" & _lado & "</div></div><div class='man sobe d1'>" & _man & "</div></div>"
        """))
    d("T25 · Anos topo · ALT", "Texto para leitor de tela do título do bloco de anos.", dax("""
        VAR _tipo = [T25 · série · tipo de manchete]
        VAR _marco = [T25 · série · marco do extremo]
        VAR _extremo = _tipo = "menor" || _tipo = "maior"
        RETURN LEFT (
            "Abstenção no " & [T25 · turno] & ", " & [T25 · lugar] & ": "
                & IF ( _extremo,
                    "em 2026, a " & _tipo & " " & IF ( ISBLANK ( _marco ), "da série", "desde " & FORMAT ( _marco, "0" ) ) & ". ",
                    "" )
                & IF ( _tipo = "sem série", "sem série neste recorte.",
                    FORMAT ( [T25 · abstenção % no primeiro ano], "0.0%" ) & " em " & FORMAT ( [T25 · primeiro ano da série], "0" )
                        & " e " & FORMAT ( [T25 · abstenção % em 2026], "0.0%" ) & " em 2026." ), 250 )
        """))
    d("T25 · Anos · HTML", "Uma coluna por 1º turno (granularidade Ano[Ano]): a abstenção do ano no lugar e na faixa do "
      "contexto, a linha tracejada da referência e o ano; com faixa marcada, 2006 e 2010 ficam vazios (sem idade). O "
      "alvo transparente recebe o clique e a dica. Só lê contas; a escala é geometria.", dax(f"""
        -- 1 · Leituras
        VAR _ano = [T25 · ano]
        VAR _pct = [T25 · abstenção %]
        VAR _teto = [T25 · teto da série]
        VAR _ref = [T25 · referência da série]
        VAR _comFaixa = [T25 · com faixa]
        VAR _temIdade = [T25 · tem idade no ano]
        -- 2 · Textos
        VAR _sem = IF ( _comFaixa = 1 && _temIdade = 0, "sem idade", "sem dado" )
        -- 3 · Geometria (6 anos em 760 px; coluna de 0 ao teto em {ALT_COL} px sobre a base a 30 px do pé)
        VAR _i = ( _ano - 2006 ) / 4 -- geometria
        VAR _x = _i * {SLOT:.4f} -- geometria
        VAR _h = IF ( _teto > 0, DIVIDE ( _pct, _teto ) * {ALT_COL} ) -- geometria
        VAR _hr = IF ( _teto > 0, DIVIDE ( _ref, _teto ) * {ALT_COL}, 0 ) -- geometria
        VAR _coluna =
            IF (
                ISBLANK ( _pct ),
                "<div class='fant entra d" & ( _i + 2 ) & "'></div><div class='sem entra d" & ( _i + 3 ) & "'>" & _sem & "</div>",
                "<div class='pc sobe d" & ( _i + 4 ) & "' style='bottom:" & @CSS(MAX ( _h, _hr ) + 36)@ & "px'>" & @PCT(_pct)@ & "</div>"
                    & "<div class='bar barra-y d" & ( _i + 2 ) & "' style='height:" & @CSS(MAX ( _h, 2 ))@ & "px'></div>"
            )
        VAR _linhaRef =
            IF (
                NOT ISBLANK ( _ref ) && NOT ISBLANK ( _pct ),
                "<div class='ref entra d10' style='bottom:" & @CSS(_hr + 30)@ & "px'></div>"
            )
        -- 4 · Marcação
        RETURN
            "<div class='tela an'><div class='col' style='left:" & @CSS(_x)@ & "px'>" & _coluna & _linhaRef
                & "<div class='ano'>" & _ano & "</div><div class='alvo'></div></div></div>"
        """))
    serie = " & \", \" & ".join(f'"{a} " & IF ( ISBLANK ( [T25 · abstenção % em {a}] ), "sem dado", '
                                f'@PCT([T25 · abstenção % em {a}])@ )' for a in ANOS)
    d("T25 · Anos · ALT", "Texto para leitor de tela do bloco de anos.", dax(f"""
        LEFT (
            "Abstenção no " & [T25 · turno] & ", " & [T25 · lugar] & IF ( [T25 · com faixa] = 1, ", " & [T25 · faixa] ) & ": "
                & {serie} & ". Clique num ano para cruzar.",
            250
        )
        """))
    # ------------------------------------------------------------------ idade
    d("T25 · Idade topo · HTML", "Título do bloco de idade: o ano e o lugar, quantas vezes a faixa que mais falta falta "
      "mais que a que menos falta, a legenda de todas as idades e do voto facultativo. Ignora o clique no próprio "
      "bloco.", dax("""
        -- 1 · Leituras
        VAR _ano = [T25 · idade ano]
        VAR _lugar = [T25 · lugar]
        VAR _temIdade = [T25 · idade disponível]
        VAR _mais = [T25 · faixa que mais falta]
        VAR _menos = [T25 · faixa que menos falta]
        VAR _vezes = [T25 · vezes entre as faixas]
        VAR _todas = [T25 · idade todas as idades]
        -- 2 · Textos
        VAR _rot = "Por idade · 1º turno · " & _ano
        VAR _man =
            IF ( [Eleição · pós] = 1, "O TSE ainda não publicou a idade do 2º turno", SWITCH (
                TRUE (),
                _temIdade = 0, "Por idade, o TSE só publica desde 2014",
                ISBLANK ( _mais ), "Sem dado por idade neste recorte",
                "Os de " & SUBSTITUTE ( _mais, "16 e 17", "16 ou 17" ) & " faltam " & FORMAT ( _vezes, "0.0" )
                    & " vezes mais que os de " & SUBSTITUTE ( _menos, "16 e 17", "16 ou 17" )
            )
            )
        VAR _lado =
            IF ( NOT ISBLANK ( _todas ) && _temIdade = 1,
                "<span class='lg'><i></i>todas as idades · " & @PCT(_todas)@ & "</span>" )
                & "<span class='so'>* voto facultativo</span>"
        -- 4 · Marcação
        RETURN
            "<div class='tela it'><div class='l1'><div class='rot sobe'>" & _rot & "</div>"
                & "<div class='lado entra d3'>" & _lado & "</div></div><div class='man sobe d1'>" & _man & "</div></div>"
        """))
    d("T25 · Idade topo · ALT", "Texto para leitor de tela do título do bloco de idade.", dax("""
        LEFT (
            "Quem falta mais, por idade, 1º turno, " & [T25 · lugar] & ", " & [T25 · idade ano] & ": "
                & IF ( [T25 · idade disponível] = 0, "o TSE só publica a idade desde 2014.",
                    [T25 · faixa que mais falta] & " " & @PCT([T25 · faixa que mais falta %])@ & "; "
                        & [T25 · faixa que menos falta] & " " & @PCT([T25 · faixa que menos falta %])@ & "." ),
            250
        )
        """))
    x0, larg = TRILHO
    d("T25 · Idade · HTML", "Uma linha por faixa de idade (granularidade T25 Faixa[Faixa]): a barra da abstenção da "
      "faixa no ano e no lugar do recorte, o valor e a linha tracejada de todas as idades; * = voto facultativo. Sem "
      "dado (antes de 2014), a linha fica vazia. Só lê contas; posições são geometria.", dax(f"""
        -- 1 · Leituras
        VAR _k = [T25 · ordem da faixa]
        VAR _nome = [T25 · faixa da linha]
        VAR _voto = [T25 · voto da faixa]
        VAR _pct = [T25 · idade abstenção %]
        VAR _teto = [T25 · teto por idade]
        VAR _ref = [T25 · idade todas as idades]
        -- 2 · Textos
        VAR _ast = IF ( _voto = "facultativo", "<sup>*</sup>" )
        -- 3 · Geometria (linhas a cada {LINHA_FX} px; barra de 0 ao teto em {larg} px a partir de x {x0})
        VAR _top = ( _k - 1 ) * {LINHA_FX} -- geometria
        VAR _w = IF ( _teto > 0, DIVIDE ( _pct, _teto ) * {larg} ) -- geometria
        VAR _xr = {x0} + IF ( _teto > 0, DIVIDE ( _ref, _teto ) * {larg} ) -- geometria
        VAR _barra =
            IF (
                ISBLANK ( _pct ),
                "<span class='vl sem'>—</span>",
                "<i class='br barra-x d" & ( _k + 2 ) & "' style='width:" & @CSS(MAX ( _w, 2 ))@ & "px'></i>"
                    & "<span class='vl sobe d" & ( _k + 4 ) & "'>" & @PCT(_pct)@ & "</span>"
            )
        VAR _linhaRef =
            IF ( NOT ISBLANK ( _ref ) && NOT ISBLANK ( _pct ), "<i class='rf entra d11' style='left:" & @CSS(_xr)@ & "px'></i>" )
        -- 4 · Marcação
        RETURN
            IF (
                NOT ISBLANK ( _k ),
                "<div class='tela fx'><div class='ln' style='top:" & _top & "px'>"
                    & "<span class='nm'>" & @ESC(_nome)@ & _ast & "</span><i class='tr'></i>" & _barra & _linhaRef
                    & "<div class='alvo'></div></div></div>"
            )
        """))
    d("T25 · Idade · ALT", "Texto para leitor de tela do bloco de idade.", dax("""
        LEFT (
            "Abstenção por faixa de idade, 1º turno, " & [T25 · lugar] & ", " & [T25 · idade ano] & ": "
                & IF ( [T25 · idade disponível] = 0, "o TSE só publica a idade desde 2014.",
                    "a que mais falta é " & [T25 · faixa que mais falta] & " ("
                        & @PCT([T25 · faixa que mais falta %])@ & "), a que menos falta é "
                        & [T25 · faixa que menos falta] & " (" & @PCT([T25 · faixa que menos falta %])@ & ")." )
                & IF ( [Eleição · pós] = 1, " Primeiro turno de 2026; a idade do segundo ainda não foi publicada.", " Clique numa faixa para cruzar." ),
            250
        )
        """))
    # ------------------------------------------------------------------ mapa
    d("T25 · Mapa · ALT", "Texto para leitor de tela do mapa.", dax(f"""
        LEFT (
            "Mapa " & [Recorte · de] & ", " & [T25 · ano]
                & IF ( [T25 · com faixa] = 1, ", " & [T25 · faixa] )
                & ": um ponto por município, mais escuro onde se faltou mais que a " & {_media()} & " ("
                & @PCT([T25 · abstenção % do recorte])@ & "). Clique num ponto para ver o município nas outras peças.",
            250
        )
        """))
    d("T25 · Legenda · HTML", "Legenda do mapa: o ponto e a cor (abaixo e acima da média do recorte).", dax(f"""
        -- 1 · Leituras
        VAR _ref = [T25 · abstenção % do recorte]
        -- 2 · Textos
        VAR _media = {_media()}
        -- 4 · Marcação
        RETURN
            "<div class='tela lgm entra d6'>"
                & "<span class='it'><i class='bol'></i>cada ponto é um município; o tamanho segue quantos faltaram</span>"
                & "<span class='it'><span>abaixo</span><i class='esc'></i><span>acima da " & _media
                & IF ( NOT ISBLANK ( _ref ), " (" & @PCT(_ref)@ & ")" ) & "</span></span>"
            & "</div>"
        """))
    d("T25 · Legenda · ALT", "Texto para leitor de tela da legenda do mapa.", dax("""
        "Legenda: cada ponto é um município, o tamanho segue quantos faltaram; a cor vai do claro (abaixo da média do "
            & "recorte) ao escuro (metade acima da média ou mais)."
        """))
    # ------------------------------------------------------------------ dossiês
    _dossie_municipio()
    _dossie_ano()
    _dossie_idade()


def _sparkline(anos: list[int], largura: int, altura: int, prefixo: str = "_p") -> tuple[str, str]:
    """(VARs de geometria, marcação) da minilinha da série: pontos dos anos com dado, rótulo no primeiro e no último.
    Lê as VARs _p<ano> já declaradas; só posiciona."""
    tabela = "{ " + ", ".join(f"( {a}, {prefixo}{str(a)[2:]} )" for a in anos) + " }"
    a0, a1 = anos[0], anos[-1]
    geo = f"""VAR _serie = {tabela} /* lista */
        VAR _pts = FILTER ( _serie, NOT ISBLANK ( [Value2] ) ) /* lista */
        VAR _min = MINX ( _pts, [Value2] ) -- geometria
        VAR _max = MAXX ( _pts, [Value2] ) -- geometria
        VAR _xy =
            ADDCOLUMNS (
                _pts, /* lista */
                "@x", 8 + ( [Value1] - {a0} ) / {a1 - a0} * {largura - 16}, -- geometria
                "@y", IF ( _max > _min, {altura - 18} - ( [Value2] - _min ) / ( _max - _min ) * {altura - 30}, {altura // 2} ) -- geometria
            )
        VAR _primeiro = MINX ( _xy, [Value1] ) -- geometria
        VAR _ultimo = MAXX ( _xy, [Value1] ) -- geometria
        VAR _linha = CONCATENATEX ( _xy, @CSS([@x])@ & "," & @CSS([@y])@, " L", [Value1], ASC ) -- geometria
        VAR _bolas =
            CONCATENATEX (
                _xy,
                "<circle cx='" & @CSS([@x])@ & "' cy='" & @CSS([@y])@ & "' r='" & IF ( [Value1] = _ultimo, "4.5", "3" ) & "'/>",
                "",
                [Value1], ASC
            )
        VAR _rots =
            CONCATENATEX (
                FILTER ( _xy, [Value1] = _primeiro || [Value1] = _ultimo ), /* lista */
                "<span class='sr' style='left:" & @CSS([@x] - 40)@ & "px;top:" & @CSS([@y] - 24)@ & "px'>"
                    & @PCT([Value2])@ & "</span><span class='sa' style='left:" & @CSS([@x] - 40)@ & "px'>"
                    & [Value1] & "</span>",
                "",
                [Value1], ASC
            )"""
    marc = (f"\"<div class='sp'><svg width='{largura}' height='{altura}' viewBox='0 0 {largura} {altura}'>"
            "<path class='traco' pathLength='1' d='M\" & _linha & \"'/>\" & _bolas & \"</svg>\" & _rots & \"</div>\"")
    return geo, marc


_CSS_FICHA = (
    ".tt{position:fixed;inset:0;background:var(--papel)}"
    ".tt .ficha{position:absolute;left:14px;top:22px;right:14px;bottom:14px;background:var(--branco);"
    "border:1.5px solid var(--areia);box-shadow:3px 4px 0 rgba(28,25,21,.07)}"
    ".tt .fita{position:absolute;left:150px;top:-16px;width:96px;transform:rotate(3deg);opacity:.9}"
    ".tt .ic{position:absolute;right:16px;top:14px;width:34px}"
    ".tt .cab{position:absolute;left:18px;top:14px;right:60px}"
    ".tt .nm{font-size:22px;font-weight:700;line-height:1.15;letter-spacing:-.01em}"
    ".tt .big{position:absolute;left:18px;font-size:44px;font-weight:700;letter-spacing:-.03em;line-height:1}"
    ".tt .bs{position:absolute;left:176px;right:18px;font-size:15px;color:var(--grafite);line-height:1.35}"
    ".tt .bs b,.tt .lin b{color:var(--tinta);font-weight:700}"
    ".tt .lin{position:absolute;left:18px;right:18px;border-top:1px dashed var(--areia);padding-top:8px;"
    "font-size:15px;color:var(--grafite);line-height:1.35}"
    ".tt .mao{position:absolute;right:18px;bottom:8px;font-size:28px;color:var(--tinta)}"
    ".tt .sp{position:absolute;left:18px}.tt .sp svg{overflow:visible}"
    ".tt .sp path{fill:none;stroke:var(--tinta);stroke-width:2.4;stroke-linejoin:round;stroke-linecap:round}"
    ".tt .sp circle{fill:var(--tinta);stroke:var(--branco);stroke-width:2}"
    ".tt .sp .sr{position:absolute;width:80px;text-align:center;font-size:13px;font-weight:700}"
    ".tt .sp .sa{position:absolute;bottom:-20px;width:80px;text-align:center;font-size:13px;color:var(--cinza)}"
)


def _css_ficha() -> str:
    """CSS do cartão dossiê comum às três dicas (no texto da medida: o bodyTemplate do tooltip é o da casa)."""
    return '"<style>' + _CSS_FICHA.replace('"', '""') + '</style>"'


def _dossie_municipio() -> None:
    nome, w, h = TT_MUN
    leit = "\n".join(f"        VAR _p{str(a)[2:]} = [T25 · abstenção % em {a}]" for a in ANOS)
    geo, spark = _sparkline(ANOS, 230, 64)
    G.desenho("T25 · Tooltip município · HTML", "Dossiê do município do ponto (ficha presa com fita): o % de quem faltou "
              "no ano e na faixa do recorte, quantas pessoas, a comparação com a média do recorte, a minilinha de 2006 "
              "(ou 2014) a 2026 e, sem faixa marcada, a idade que mais e menos falta ali. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _mun = [T25 · município]
        VAR _reg = [T25 · região do município]
        VAR _ano = [T25 · ano]
        VAR _comFaixa = [T25 · com faixa]
        VAR _faixa = [T25 · faixa]
        VAR _pct = [T25 · abstenção %]
        VAR _n = [T25 · abstenções]
        VAR _aptos = [T25 · aptos]
        VAR _um = [T25 · um em cada]
        VAR _ref = [T25 · abstenção % do recorte]
        VAR _dif = [T25 · diferença para o recorte]
        VAR _mais = [T25 · faixa que mais falta]
        VAR _maisP = [T25 · faixa que mais falta %]
        VAR _menos = [T25 · faixa que menos falta]
        VAR _menosP = [T25 · faixa que menos falta %]
{leit}
        -- 2 · Textos
        VAR _media = {_media()}
        VAR _quem = IF ( _comFaixa = 1, " de " & _faixa, "" )
        VAR _compara =
            IF (
                NOT ISBLANK ( _ref ),
                IF (
                    ABS ( _dif ) < 0.05,
                    "Bem na " & _media,
                    FORMAT ( ABS ( _dif ), "0.0" ) & IF ( ABS ( _dif ) < 2, " ponto ", " pontos " )
                        & IF ( _dif > 0, "acima", "abaixo" ) & " da " & _media
                ) & " (<b>" & @PCT(_ref)@ & "</b>)"
            )
        VAR _idade =
            IF (
                _comFaixa = 0 && NOT ISBLANK ( _mais ),
                IF ( [Eleição · pós] = 1, "Por idade · 1º turno de 2026: <b>", "Quem mais falta aqui: <b>" ) & _mais & "</b> (" & @PCT(_maisP)@ & "); quem menos: <b>" & _menos
                    & "</b> (" & @PCT(_menosP)@ & ")",
                "A série" & _quem & " no município, ano a ano"
            )
        VAR _nota = IF ( _um > 0, "1 em cada " & _um & " faltou" )
        -- 3 · Geometria (minilinha de 230 × 64)
        {geo}
        -- 4 · Marcação
        VAR _html =
            {_css_ficha()}
                & "<div class='tt tm'><div class='ficha'>"
                & "<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/>"
                & "<img class='ic' alt='' src='{URL_MIDIA}/arte/icones/urna-tinta.png'/>"
                & "<div class='cab sobe'><div class='nm'>" & @ESC(_mun)@ & "</div>"
                & "<div class='rot'>" & @ESC(_reg)@ & " · " & @INT(_aptos)@ & " eleitores" & @ESC(_quem)@ & "</div></div>"
                & "<div class='big sobe d1' style='top:84px'>" & @PCT(_pct)@ & "</div>"
                & "<div class='bs sobe d2' style='top:88px'>não foram votar no " & [T25 · turno] & " de " & _ano & ": <b>" & @INT(_n)@ & "</b> "
                & IF ( _n = 1, "pessoa", "pessoas" ) & ". " & _compara & ".</div>"
                & "<div class='lin sobe d3' style='top:150px'>" & _idade & "</div>"
                & "<div style='position:absolute;left:0;top:206px'>" & {spark} & "</div>"
                & "<div class='mao entra d6'>" & _nota & "</div>"
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _mun ) && NOT ISBLANK ( _aptos ), _html )
        """))
    G.desenho("T25 · Tooltip município · ALT", "Texto para leitor de tela do dossiê do município.", dax("""
        LEFT (
            [T25 · município] & ", " & [T25 · ano] & IF ( [T25 · com faixa] = 1, ", " & [T25 · faixa] ) & ": "
                & @PCT([T25 · abstenção %])@ & " não foram votar (" & @INT([T25 · abstenções])@ & " pessoas); média do "
                & "recorte, " & @PCT([T25 · abstenção % do recorte])@ & ".",
            250
        )
        """))


def _dossie_ano() -> None:
    nome, w, h = TT_ANO
    leit_f = "\n".join(f"        VAR _f{k} = [T25 · parte dos que faltaram · {n}]\n"
                       f"        VAR _e{k} = [T25 · parte dos aptos · {n}]" for n, k, _c, _v in FAIXAS)
    tabela = "{ " + ", ".join(f"( {k}, _f{k}, _e{k} )" for _n, k, _c, _v in FAIXAS) + " }"
    nomes = "\n".join(f'                        {k}, "{c}",' for _n, k, c, _v in FAIXAS)
    G.desenho("T25 · Tooltip ano · HTML", "Dossiê do ano da coluna: quem disputou, quantos faltaram no lugar (e na faixa) "
              "e, de 2014 em diante, quem eram os que faltaram — o peso de cada idade entre os faltosos ao lado do peso "
              "entre os eleitores, com a nota à mão da idade que mais passa do seu peso. Antes de 2014, o aviso de que o "
              "TSE não publicava a idade. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _ano = [T25 · ano]
        VAR _disputa = [T25 · disputa do ano]
        VAR _lugar = [T25 · lugar]
        VAR _comFaixa = [T25 · com faixa]
        VAR _faixa = [T25 · faixa]
        VAR _pct = [T25 · abstenção %]
        VAR _n = [T25 · abstenções]
        VAR _aptos = [T25 · aptos]
        VAR _temIdade = [T25 · tem idade no ano]
        VAR _k = IF ( _comFaixa = 1, [T25 · ordem da faixa] )
        VAR _acima = [T25 · faixa mais acima do seu peso]
        VAR _acimaX = [T25 · faixa mais acima do seu peso (vezes)]
        VAR _todas = [T25 · abstenção % todas as idades]
{leit_f}
        -- 2 · Textos
        VAR _quem = IF ( _comFaixa = 1, " de " & _faixa, "" )
        VAR _nota = IF ( NOT ISBLANK ( _acimaX ), _acima & " pesam " & FORMAT ( _acimaX, "0.0" ) & " vezes mais" )
        -- 3 · Geometria (barras de 0 ao maior peso em 210 px)
        VAR _pesos = {tabela} /* lista */
        VAR _teto = MAX ( MAXX ( _pesos, [Value2] ), MAXX ( _pesos, [Value3] ) ) -- geometria
        VAR _linhas =
            CONCATENATEX (
                _pesos,
                VAR _rot =
                    SWITCH (
                        [Value1],
{nomes}
                        ""
                    )
                RETURN
                    "<div class='cp" & IF ( [Value1] = _k, " on" ) & "' style='top:" & ( 44 + ( [Value1] - 1 ) * 24 ) & "px'>"
                        & "<span class='nf'>" & _rot & "</span>"
                        & "<i class='bf barra-x' style='width:" & @CSS(DIVIDE ( [Value2], _teto ) * 210)@ & "px'></i>" -- geometria
                        & "<i class='be' style='width:" & @CSS(DIVIDE ( [Value3], _teto ) * 210)@ & "px'></i>" -- geometria
                        & "<span class='vf'>" & @PCT0([Value2])@ & "</span><span class='ve'>" & @PCT0([Value3])@
                        & "</span></div>",
                "",
                [Value1], ASC
            )
        VAR _css =
            "<style>"
                & ".ta .dp{{margin-top:3px;font-size:15px;color:var(--grafite);white-space:nowrap;overflow:hidden;"
                & "text-overflow:ellipsis}}"
                & ".ta .cps{{position:absolute;left:18px;right:18px;top:150px;height:220px;border-top:1px dashed var(--areia);"
                & "padding-top:8px}}"
                & ".ta .cps .tl{{position:absolute;left:0;top:10px;font-size:15px;font-weight:600;color:var(--tinta)}}"
                & ".ta .cps .lg2{{position:absolute;left:0;top:30px;font-size:13px;color:var(--cinza)}}"
                & ".ta .cps .lg2 i{{display:inline-block;width:12px;height:8px;margin:0 5px 0 0}}"
                & ".ta .cps .lg2 i+i,.ta .cps .lg2 span+i{{margin-left:14px}}"
                & ".ta .cp{{position:absolute;left:0;right:0;height:22px;font-size:13px;color:var(--grafite)}}"
                & ".ta .cp>*{{position:absolute}}.ta .cp .nf{{left:0;top:3px;width:48px;font-weight:600}}"
                & ".ta .cp.on .nf{{color:var(--tinta);font-weight:800}}"
                & ".ta .cp .bf{{left:52px;top:3px;height:9px;background:var(--tinta)}}"
                & ".ta .cp .be{{left:52px;top:14px;height:4px;background:var(--areia)}}"
                & ".ta .cp .vf{{left:276px;top:2px;width:44px;text-align:right;font-weight:700;color:var(--tinta)}}"
                & ".ta .cp .ve{{left:328px;top:2px;width:56px;text-align:right;color:var(--cinza)}}"
                & ".ta .si{{position:absolute;left:18px;right:18px;top:160px;font-size:17px;line-height:1.4;color:var(--grafite);"
                & "border-top:1px dashed var(--areia);padding-top:12px}}"
            & "</style>"
        -- 4 · Marcação
        VAR _corpo =
            IF (
                _temIdade = 1 && NOT ISBLANK ( _teto ),
                "<div class='cps sobe d3'><div class='tl'>Quem eram os que faltaram, por idade</div>"
                    & "<div class='lg2'><i style='background:var(--tinta)'></i>entre os que faltaram"
                    & "<span></span><i style='background:var(--areia);height:4px;margin-left:14px'></i>entre os eleitores</div>"
                    & _linhas & "</div>"
                    & "<div class='mao entra d8'>" & @ESC(_nota)@ & "</div>",
                "<div class='si sobe d3'>" & IF ( [Eleição · pós] = 1,
                    "O perfil por idade do 2º turno não está disponível nesta tela. A peça por idade usa o 1º turno de 2026.", "Em " & _ano & ", o TSE ainda não publicava a idade de quem faltou. O perfil por "
                    & "idade começa em 2014." ) & "</div>"
            )
        VAR _html =
            {_css_ficha()} & _css
                & "<div class='tt ta'><div class='ficha'>"
                & "<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/>"
                & "<img class='ic' alt='' src='{URL_MIDIA}/arte/icones/urna-tinta.png'/>"
                & "<div class='cab sobe'><div class='nm'>" & [T25 · turno] & " de " & _ano & "</div>"
                & "<div class='dp'>" & @ESC(_disputa)@ & "</div></div>"
                & IF (
                    ISBLANK ( _pct ),
                    "<div class='big sobe d1' style='top:78px'>" & @PCT(_todas)@ & "</div>"
                        & "<div class='bs sobe d2' style='top:82px'>faltaram, com todas as idades · " & @ESC(_lugar)@ & "</div>",
                    "<div class='big sobe d1' style='top:78px'>" & @MI1(_n)@ & "</div>"
                        & "<div class='bs sobe d2' style='top:82px'>de " & @MI1(_aptos)@ & " eleitores" & @ESC(_quem)@
                        & " faltaram · " & @ESC(_lugar)@ & "</div>"
                )
                & _corpo
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _aptos ) || NOT ISBLANK ( _disputa ), _html )
        """).replace("{{", "{").replace("}}", "}"))
    G.desenho("T25 · Tooltip ano · ALT", "Texto para leitor de tela do dossiê do ano.", dax("""
        LEFT (
            [T25 · turno] & " de " & [T25 · ano] & " (" & [T25 · disputa do ano] & "), " & [T25 · lugar] & ": "
                & @PCT([T25 · abstenção %])@ & " faltaram"
                & IF ( [T25 · tem idade no ano] = 1, "; a idade que mais passa do seu peso entre os que faltaram é "
                    & [T25 · faixa mais acima do seu peso] & ".", "." ),
            250
        )
        """))


def _dossie_idade() -> None:
    anos = [a for a in ANOS if a >= 2014]
    leit = "\n".join(f"        VAR _p{str(a)[2:]} = [T25 · idade abstenção % em {a}]" for a in anos)
    geo, spark = _sparkline(anos, 200, 60)
    G.desenho("T25 · Tooltip idade · HTML", "Dossiê da faixa de idade da barra: quantas pessoas faltaram (o % já está na barra), o peso "
              "da faixa entre os eleitores e entre os que faltaram, a minilinha de 2014 a 2026 e a nota à mão de quantas "
              "vezes a média de todas as idades. Só lê contas.", dax(f"""
        -- 1 · Leituras
        VAR _nome = [T25 · faixa da linha]
        VAR _voto = [T25 · voto da faixa]
        VAR _ano = [T25 · idade ano]
        VAR _lugar = [T25 · lugar]
        VAR _pct = [T25 · idade abstenção %]
        VAR _n = [T25 · idade abstenções]
        VAR _aptos = [T25 · idade aptos]
        VAR _pa = [T25 · parte dos aptos (faixa)]
        VAR _pf = [T25 · parte dos que faltaram (faixa)]
        VAR _vezes = [T25 · vezes a média (faixa)]
{leit}
        -- 2 · Textos
        VAR _cab = _nome
        VAR _sub = _lugar & " · 1º turno de " & _ano & IF ( _voto = "facultativo", " · voto facultativo" )
        VAR _nota =
            SWITCH (
                TRUE (),
                ISBLANK ( _vezes ), "",
                _vezes >= 1.05, FORMAT ( _vezes, "0.0" ) & " vezes a média",
                _vezes <= 0.95, "abaixo da média",
                "bem na média"
            )
        -- 3 · Geometria (minilinha de 200 × 60)
        {geo}
        -- 4 · Marcação
        VAR _corpo =
            IF (
                ISBLANK ( _pct ),
                "<div class='lin sobe d1' style='top:84px'>Em " & _ano & ", o TSE ainda não publicava a idade de quem "
                    & "faltou. O perfil por idade começa em 2014.</div>",
                "<div class='big sobe d1' style='top:80px'>" & @MI1(_n)@ & "</div>"
                    & "<div class='bs sobe d2' style='top:84px'>de " & @MI1(_aptos)@ & " eleitores dessa idade "
                    & "faltaram</div>"
                    & "<div class='lin sobe d3' style='top:146px'>São <b>" & @PCT0(_pa)@ & "</b> dos eleitores e <b>"
                    & @PCT0(_pf)@ & "</b> de quem faltou</div>"
                    & "<div style='position:absolute;left:0;top:200px'>" & {spark} & "</div>"
                    & "<div class='mao entra d6'>" & _nota & "</div>"
            )
        VAR _html =
            {_css_ficha()}
                & "<div class='tt ti'><div class='ficha'>"
                & "<img class='fita' alt='' src='{URL_MIDIA}/arte/dossie/fita-tinta.png'/>"
                & "<img class='ic' alt='' src='{URL_MIDIA}/arte/icones/urna-tinta.png'/>"
                & "<div class='cab sobe'><div class='nm'>" & @ESC(_cab)@ & "</div>"
                & "<div class='rot'>" & @ESC(_sub)@ & "</div></div>"
                & _corpo
                & "</div></div>"
        RETURN
            IF ( NOT ISBLANK ( _nome ), _html )
        """))
    G.desenho("T25 · Tooltip idade · ALT", "Texto para leitor de tela do dossiê da faixa.", dax("""
        LEFT (
            [T25 · faixa da linha] & ", 1º turno de " & [T25 · idade ano] & ", " & [T25 · lugar] & ": "
                & IF ( ISBLANK ( [T25 · idade abstenção %] ), "o TSE só publica a idade desde 2014.",
                    @PCT([T25 · idade abstenção %])@ & " faltaram; são " & @PCT0([T25 · parte dos aptos (faixa)])@
                        & " dos eleitores e " & @PCT0([T25 · parte dos que faltaram (faixa)])@ & " de quem faltou." ),
            250
        )
        """))


# ---------------------------------------------------------------------------------------------------- spec do mapa
def spec_mapa() -> dict:
    """Vega 6 puro. Campos: cod, x, y, uf (colunas de Município) e as medidas 'tam' (quantos faltaram) e 'val' (a
    abstenção do município dividida pela média do recorte). Seleção simples do Deneb: o clique num ponto marca o
    município (filtro cruzado), o clique no vazio desmarca; o datum mantém __row__ (só filter/formula/collect sobre o
    dataset). __selected__ = on/off/neutral pinta o marcado e esmaece os outros."""
    prog = "clamp((t - datum.atraso) / 520, 0, 1)"
    sel = "(datum.__selected__ == 'on')"
    off = "(datum.__selected__ == 'off')"
    return {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": "Tela 07 · Quem falta: um ponto por município (tamanho = quantos faltaram, cor = abstenção ÷ média "
                       "do recorte, de 0,6 a 1,5); contorno das UFs em traço; pontos em onda; a cor esmaece de "
                       "novo quando o ano ou a faixa mudam; clique marca o município.",
        "width": {"signal": "pbiContainerWidth"}, "height": {"signal": "pbiContainerHeight"},
        "padding": 0, "autosize": {"type": "none", "contains": "padding"}, "background": None,
        "config": {"view": {"stroke": None}},
        "signals": [
            {"name": "estatico", "init": "!(windowSize()[0] > 0)"},
            {"name": "fim", "value": 3600},
            {"name": "t0", "init": "now()"},
            {"name": "t", "init": "estatico ? fim : 0",
             "on": [{"events": "timer{33}", "update": "estatico ? fim : min(now() - t0, fim)"}]},
            # a cor esmaece de novo quando os dados mudam (ano ou faixa marcados), não quando só a seleção muda
            {"name": "chave", "update": "length(data('soma')) ? data('soma')[0].n + ':' + format(data('soma')[0].s, '.6f') : ''"},
            {"name": "tMuda", "value": 0, "on": [{"events": {"signal": "chave"}, "update": "now()"}]},
            {"name": "tAgora", "init": "now()",
             "on": [{"events": "timer{33}", "update": "now() - tMuda < 900 ? now() : tAgora"}]},
            {"name": "pulso", "update": "estatico || t < fim ? 1 : clamp((tAgora - tMuda) / 700, 0, 1)"},
            {"name": "folga", "value": 18},
            {"name": "nAtivas", "update": "length(data('ufsDoRecorte'))"},
            {"name": "umaUF", "update": "nAtivas == 1"},
            {"name": "qx0", "update": "nAtivas ? data('quadro')[0].x0 : 0"},
            {"name": "qy0", "update": "nAtivas ? data('quadro')[0].y0 : 0"},
            {"name": "qx1", "update": "nAtivas ? max(data('quadro')[0].x1, umaUF ? 0 : data('extPontos')[0].x1) : 1000"},
            {"name": "qy1", "update": "nAtivas ? data('quadro')[0].y1 : 1000"},
            {"name": "k", "update": "min((width - 2 * folga) / max(qx1 - qx0, 30), (height - 2 * folga) / max(qy1 - qy0, 30))"},
            {"name": "ox", "update": "width / 2 - (qx0 + qx1) / 2 * k"},
            {"name": "oy", "update": "height / 2 - (qy0 + qy1) / 2 * k"},
            {"name": "rmax", "update": "umaUF ? clamp(10 + 3.2 * k, 12, 30) : 17"},
            {"name": "cvx", "update": "length(data('centro')) ? data('centro')[0].cx : 500"},
            {"name": "cvy", "update": "length(data('centro')) ? data('centro')[0].cy : 500"},
            {"name": "vazio", "update": "length(data('comLugar')) == 0"},
        ],
        "data": [
            {"name": "dataset"},
            {"name": "ufsDoRecorte", "source": "dataset", "transform": [{"type": "aggregate", "groupby": ["uf"]}]},
            {"name": "ufs", "values": ufs_geometria(),
             "transform": [{"type": "lookup", "from": "ufsDoRecorte", "key": "uf", "fields": ["uf"],
                            "as": ["noRecorte"]},
                           {"type": "formula", "as": "ativa", "expr": "datum.noRecorte ? 1 : 0"}]},
            {"name": "ativas", "source": "ufs",
             "transform": [{"type": "filter", "expr": "datum.ativa == 1"},
                           {"type": "joinaggregate", "fields": ["cx", "cx"], "ops": ["min", "max"],
                            "as": ["cmin", "cmax"]},
                           {"type": "formula", "as": "atraso",
                            "expr": "umaUF ? 0 : 700 * (datum.cx - datum.cmin) / max(datum.cmax - datum.cmin, 1)"}]},
            {"name": "contexto", "source": "ufs", "transform": [{"type": "filter", "expr": "datum.ativa == 0"}]},
            {"name": "quadro", "source": "ativas",
             "transform": [{"type": "aggregate", "fields": ["x0", "y0", "x1", "y1"], "ops": ["min", "min", "max", "max"],
                            "as": ["x0", "y0", "x1", "y1"]}]},
            {"name": "comLugar", "source": "dataset",
             "transform": [{"type": "filter", "expr": "isValid(datum.x) && isValid(datum.y) && isValid(datum.tam) "
                                                      "&& isValid(datum.val)"},
                           {"type": "formula", "as": "xv", "expr": "datum.x * max(datum.tam, 0)"},
                           {"type": "formula", "as": "yv", "expr": "datum.y * max(datum.tam, 0)"}]},
            {"name": "soma", "source": "comLugar",
             "transform": [{"type": "aggregate", "fields": ["val", "tam"], "ops": ["sum", "count"], "as": ["s", "n"]}]},
            {"name": "extPontos", "source": "comLugar",
             "transform": [{"type": "aggregate", "fields": ["x"], "ops": ["max"], "as": ["x1"]}]},
            {"name": "centro", "source": "comLugar",
             "transform": [{"type": "aggregate", "fields": ["xv", "yv", "tam"], "ops": ["sum", "sum", "sum"],
                            "as": ["sx", "sy", "st"]},
                           {"type": "formula", "as": "cx", "expr": "datum.sx / max(datum.st, 1)"},
                           {"type": "formula", "as": "cy", "expr": "datum.sy / max(datum.st, 1)"}]},
            {"name": "pontos", "source": "comLugar",
             "transform": [{"type": "joinaggregate", "fields": ["tam"], "ops": ["max"], "as": ["tmax"]},
                           {"type": "formula", "as": "dist",
                            "expr": "sqrt(pow(datum.x - cvx, 2) + pow(datum.y - cvy, 2))"},
                           {"type": "joinaggregate", "fields": ["dist"], "ops": ["max"], "as": ["dmax"]},
                           {"type": "formula", "as": "atraso",
                            "expr": "900 + 1700 * datum.dist / max(datum.dmax, 1) + (toNumber(datum.cod) % 9) * 12"},
                           {"type": "collect", "sort": {"field": "tam", "order": "descending"}}]},
            {"name": "marcados", "source": "pontos", "transform": [{"type": "filter", "expr": sel}]},
        ],
        "scales": [{"name": "cor", "type": "linear", "domain": [0.6, 1, 1.5],
                    "range": ["#E3D9C4", "#9C8D74", "#1C1915"], "clamp": True, "interpolate": "rgb"}],
        "marks": [{
            "type": "group", "name": "palco", "clip": True,
            "encode": {"update": {"x": {"value": 0}, "y": {"value": 0}, "width": {"signal": "width"},
                                  "height": {"signal": "height"}}},
            "marks": [
                {"type": "path", "from": {"data": "contexto"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "fill": {"value": "#E5DBC8"}, "fillOpacity": {"signal": "umaUF ? 0.35 : 0"},
                     "stroke": {"value": "#CBBDA2"}, "strokeWidth": {"value": 1},
                     "opacity": {"signal": "umaUF ? clamp((t - 200) / 700, 0, 1) : 0"}}}},
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "fill": {"value": "#E5DBC8"},
                     "fillOpacity": {"signal": "clamp((t - 600 - datum.atraso * 0.4) / 900, 0, 1) * 0.5"}}}},
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                     "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                     "stroke": {"value": "#48423A"}, "strokeWidth": {"signal": "umaUF ? 1.6 : 0.9"},
                     "strokeJoin": {"value": "round"}, "strokeOpacity": {"value": 0.8},
                     "strokeDash": {"signal": "t >= fim ? [] : [datum.ld * k + 4, datum.ld * k + 4]"},
                     "strokeDashOffset": {"signal": "(datum.ld * k + 4) * (1 - pow(clamp((t - datum.atraso) / 1100, 0, 1), 0.7))"}}}},
                # o rabisco: um segundo traço, levemente deslocado e mais claro, que vem logo depois (caneta que
                # passou duas vezes); no canvas não há filtro de tremido, então o "à mão" é o traço repetido
                {"type": "path", "from": {"data": "ativas"}, "interactive": False,
                 "encode": {"update": {
                     "path": {"field": "d"}, "x": {"signal": "ox + 0.9"}, "y": {"signal": "oy - 0.7"},
                     "scaleX": {"signal": "k * 1.002"}, "scaleY": {"signal": "k * 0.998"},
                     "stroke": {"value": "#48423A"}, "strokeWidth": {"signal": "umaUF ? 0.9 : 0.5"},
                     "strokeJoin": {"value": "round"}, "strokeOpacity": {"value": 0.35},
                     "strokeDash": {"signal": "t >= fim ? [] : [datum.ld * k + 4, datum.ld * k + 4]"},
                     "strokeDashOffset": {"signal": "(datum.ld * k + 4) * (1 - pow(clamp((t - 350 - datum.atraso) / 1300, 0, 1), 0.7))"}}}},
                {"type": "symbol", "name": "marcaPontos", "from": {"data": "pontos"},
                 "encode": {"update": {
                     "x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
                     "shape": {"value": "circle"},
                     "size": {"signal": f"pow(2 * max(1.7, rmax * sqrt(max(datum.tam, 0) / max(datum.tmax, 1))) * (0.35 + 0.65 * {prog}), 2)"},
                     "fill": {"signal": "scale('cor', datum.val)"},
                     "fillOpacity": {"signal": f"0.9 * {prog} * ({off} ? 0.2 : 1) * (0.35 + 0.65 * pulso)"},
                     "stroke": {"value": "#F1EBDF"}, "strokeWidth": {"signal": "umaUF ? 0.8 : 0.4"},
                     "strokeOpacity": {"signal": f"{off} ? 0.3 : 1"},
                     "cursor": {"value": "pointer"},
                     "tooltip": {"signal": "datum"}},
                     "hover": {"stroke": {"value": "#1C1915"}, "strokeWidth": {"value": 1.6},
                               "fillOpacity": {"value": 1}, "strokeOpacity": {"value": 1}}}},
                # o município marcado por cima de todos, com um anel em tinta (o mesmo datum: o clique desmarca)
                {"type": "symbol", "name": "marcaMarcados", "from": {"data": "marcados"},
                 "encode": {"update": {
                     "x": {"signal": "ox + datum.x * k"}, "y": {"signal": "oy + datum.y * k"},
                     "shape": {"value": "circle"},
                     "size": {"signal": "pow(2 * max(5, 1.25 * rmax * sqrt(max(datum.tam, 0) / max(datum.tmax, 1))), 2)"},
                     "fill": {"signal": "scale('cor', datum.val)"}, "fillOpacity": {"value": 1},
                     "stroke": {"value": "#1C1915"}, "strokeWidth": {"value": 2.4},
                     "cursor": {"value": "pointer"},
                     "tooltip": {"signal": "datum"}}}},
                {"type": "text", "interactive": False,
                 "encode": {"update": {
                     "x": {"signal": "width / 2"}, "y": {"signal": "height / 2"},
                     "align": {"value": "center"}, "baseline": {"value": "middle"},
                     "font": {"value": "Segoe UI, sans-serif"}, "fontSize": {"value": 18},
                     "fill": {"value": "#48423A"}, "lineHeight": {"value": 26},
                     "text": {"signal": "vazio ? ['Nenhum município com dado neste cruzamento.', "
                                        "'Por idade, o TSE só publica desde 2014.'] : ''"}}}},
            ]}],
    }


# ---------------------------------------------------------------------------------------------------- página
def _css_manchete() -> str:
    return (
        ".mq>*{position:absolute;left:0}"
        ".mq .sob{top:0;width:760px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".mq .topo{top:30px;display:flex;align-items:flex-end;gap:24px;width:760px}"
        ".mq .big{font-size:96px;font-weight:700;letter-spacing:-.04em;line-height:.9;white-space:nowrap;"
        "font-variant-numeric:tabular-nums lining-nums}"
        ".mq .lado{position:relative;flex:1;padding-bottom:2px}"
        ".mq .big .vz{font-size:44px;font-weight:600;letter-spacing:-.01em;color:var(--areia)}"
        ".mq .nfv{font-size:28px;font-weight:600;letter-spacing:-.01em}"
        ".mq .subl{position:absolute;left:-4px;top:34px;height:14px;overflow:visible}"
        ".mq .fr{margin-top:14px;font-size:17px;line-height:1.35;color:var(--tinta)}"
        ".mq .linha{top:156px;width:760px}"
        ".mq .marc{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px}"
        ".mq .chip{display:inline-flex;align-items:baseline;gap:8px;padding:6px 12px;background:var(--creme);"
        "border:1.5px solid var(--areia);font-size:15px;font-weight:600;color:var(--tinta)}"
        ".mq .chip b{font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--cinza)}"
        ".mq .dica{max-width:570px;font-size:15px;color:var(--cinza);line-height:1.4}"
        ".mq .aviso{font-size:15px;line-height:1.4;color:var(--tinta)}"
        ".mq .cruza{position:absolute;left:592px;top:-10px;width:168px;pointer-events:none}"
        ".mq .aviso .ast{font-family:var(--mao);font-size:26px;color:var(--tinta);margin-right:6px;"
        "vertical-align:-4px}"
    )


def _css_topo(raiz: str) -> str:
    return (
        f".{raiz}>*{{position:absolute;left:0;width:760px}}"
        f".{raiz} .l1{{top:0;display:flex;align-items:center;gap:16px;height:18px}}"
        f".{raiz} .l1 .rot{{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}"
        f".{raiz} .man{{top:24px;font-size:22px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}"
        f".{raiz} .lado{{flex:none;display:flex;gap:16px;align-items:center;font-size:13px;color:var(--grafite)}}"
        f".{raiz} .lg{{display:inline-flex;align-items:center;gap:6px}}"
        f".{raiz} .lg i{{display:inline-block;width:22px;height:0;border-top:2.5px dashed var(--marrom)}}"
        f".{raiz} .so{{color:var(--cinza)}}"
    )


def _css_anos() -> str:
    w = SLOT
    return (
        ".an{pointer-events:none}"
        f".an .col{{position:absolute;top:0;width:{w:.2f}px;height:234px}}"
        f".an .bar{{position:absolute;left:{(w - 58) / 2:.2f}px;bottom:30px;width:58px;background:var(--grafite)}}"
        f".an .pc{{position:absolute;left:0;width:{w:.2f}px;text-align:center;font-size:20px;font-weight:700;"
        "font-variant-numeric:tabular-nums}"
        f".an .ano{{position:absolute;left:0;bottom:2px;width:{w:.2f}px;text-align:center;font-size:15px;"
        "font-weight:600;color:var(--grafite)}"
        f".an .ref{{position:absolute;left:{(w - 86) / 2:.2f}px;width:86px;height:0;border-top:2.5px dashed var(--marrom)}}"
        f".an .fant{{position:absolute;left:{(w - 58) / 2:.2f}px;bottom:30px;width:58px;height:44px;"
        "border:1.5px dashed var(--areia);border-bottom:0}"
        f".an .sem{{position:absolute;left:0;bottom:82px;width:{w:.2f}px;text-align:center;font-size:13px;"
        "color:var(--cinza)}"
        ".an .alvo{position:absolute;inset:0;pointer-events:auto;cursor:pointer}"
        ".an .col::after{content:'';position:absolute;left:8px;right:8px;bottom:29px;height:1.2px;"
        "background:var(--areia)}"
    )


def _css_idade() -> str:
    x0, larg = TRILHO
    return (
        ".fx{pointer-events:none}"
        f".fx .ln{{position:absolute;left:0;width:760px;height:{LINHA_FX}px}}"
        ".fx .ln>*{position:absolute}"
        ".fx .nm{left:0;top:6px;font-size:15px;font-weight:600;color:var(--grafite);white-space:nowrap}"
        ".fx .nm sup{font-size:13px;margin-left:2px;color:var(--cinza)}"
        f".fx .tr{{left:{x0}px;top:16px;width:{larg}px;height:2px;background:var(--creme)}}"
        f".fx .br{{left:{x0}px;top:7px;height:20px;background:var(--grafite)}}"
        f".fx .vl{{left:{x0 + larg + 8}px;top:2px;width:{760 - x0 - larg - 8}px;text-align:right;font-size:20px;"
        "font-weight:700;font-variant-numeric:tabular-nums}"
        ".fx .vl.sem{color:var(--areia)}"
        f".fx .rf{{top:0;width:0;height:{LINHA_FX}px;border-left:2.5px dashed var(--marrom)}}"
        ".fx .alvo{left:0;top:0;width:760px;height:" + str(LINHA_FX) + "px;pointer-events:auto;cursor:pointer}"
    )


def _css_legenda() -> str:
    return (
        ".lgm{display:flex;flex-wrap:wrap;gap:4px 22px;align-items:center;font-size:14px;color:var(--grafite);"
        "padding-top:6px}"
        ".lgm .it{display:flex;align-items:center;gap:8px}"
        ".lgm i{display:inline-block;flex:none}"
        ".lgm .bol{width:22px;height:14px;background:radial-gradient(circle at 4px 9px,var(--grafite) 2.5px,"
        "transparent 3px),radial-gradient(circle at 15px 7px,var(--grafite) 6px,transparent 6.5px)}"
        ".lgm .esc{width:96px;height:10px;background:linear-gradient(90deg,#E3D9C4,#9C8D74,#1C1915)}"
    )


def _seta_mao() -> str:
    """Literal DAX: nota à mão "clique para cruzar" com a seta que aponta para o mapa (só sem nada marcado)."""
    return '"' + ("<div class='cruza' aria-hidden='true'>"
            "<div class='mao entra d10' style='font-size:26px;color:var(--tinta);transform:rotate(-3deg)'>"
            "clique para cruzar</div>"
            "<svg width='150' height='40' viewBox='0 0 150 40' style='position:absolute;left:10px;top:30px'>"
            "<path class='traco' pathLength='1' style='animation-delay:1.6s' d='M6,6 C50,30 96,34 140,22 M128,14 "
            "L141,22 L127,30' fill='none' stroke='#1C1915' stroke-width='2.2' stroke-linecap='round' "
            "stroke-linejoin='round'/></svg></div>").replace('"', '""') + '"'


def declarar_quem_falta() -> list:
    import pbip_lib as lib
    import pagina_lib
    from pbip_lib import Interacao, Visual
    css = "Estilo · CSS"
    z = lib.CAMADAS["conteudo"]
    tt_mun, tt_ano, tt_idade = TT_MUN[0], TT_ANO[0], TT_IDADE[0]
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"), lib.campo_coluna("x", "Município", "X"),
              lib.campo_coluna("y", "Município", "Y"), lib.campo_coluna("uf", "Município", "UF"),
              lib.campo_medida("tam", "T25 · abstenções"), lib.campo_medida("val", "T25 · abstenção relativa")]
    mapa = lib.visual_deneb("T25_Mapa_Pontos", *MAPA, "spec/t25_mapa.json", campos,
                            alt=lib.medida("T25 · Mapa · ALT"), z=z + 10, tab=300, selecao=True, max_selecao=50,
                            tooltip_pagina=tt_mun, renderizacao="canvas",uf_por_codigo=True)
    # L123: a vista do Deneb não é recompilada a cada filtro (a entrada não se repete; o clique não zera o relógio)
    mapa["visual"]["objects"]["dataLimit"] = [{"properties": {"enableIncrementalDataUpdates": lib.lit(True)}}]
    itens = [
        Visual(P, lib.visual_html("T25_Manchete_Html", *MANCHETE, "T25 · Manchete · HTML", folha_de_estilo=css, z=z,
                                  tab=100, alt=lib.medida("T25 · Manchete · ALT"),
                                  modelo_corpo=f"<style>{_css_manchete()}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T25_Anos_Topo", *ANOS_TOPO, "T25 · Anos topo · HTML", folha_de_estilo=css, z=z + 2,
                                  tab=110, alt=lib.medida("T25 · Anos topo · ALT"),
                                  modelo_corpo=f"<style>{_css_topo('at')}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T25_Anos_Html", *ANOS_CAIXA, "T25 · Anos · HTML", folha_de_estilo=css, z=z + 4,
                                  tab=120, alt=lib.medida("T25 · Anos · ALT"), granularidade=("Ano", "Ano"),
                                  filtro_cruzado=True, transparencia_nao_selecionados=True, tooltip_pagina=tt_ano,
                                  ordenacao=[lib.ordem_coluna("Ano", "Ano")],
                                  modelo_corpo=f"<style>{_css_anos()}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T25_Idade_Topo", *IDADE_TOPO, "T25 · Idade topo · HTML", folha_de_estilo=css,
                                  z=z + 6, tab=200, alt=lib.medida("T25 · Idade topo · ALT"),
                                  modelo_corpo=f"<style>{_css_topo('it')}</style>" + "{{content}}")),
        Visual(P, lib.visual_html("T25_Idade_Html", *IDADE_CAIXA, "T25 · Idade · HTML", folha_de_estilo=css, z=z + 8,
                                  tab=210, alt=lib.medida("T25 · Idade · ALT"), granularidade=("T25 Faixa", "Faixa"),
                                  filtro_cruzado=True, transparencia_nao_selecionados=True, tooltip_pagina=tt_idade,
                                  ordenacao=[lib.ordem_coluna("T25 Faixa", "Faixa")],
                                  modelo_corpo=f"<style>{_css_idade()}</style>" + "{{content}}")),
        Visual(P, mapa),
        Visual(P, lib.visual_html("T25_Mapa_Legenda", *LEGENDA, "T25 · Legenda · HTML", folha_de_estilo=css,
                                  z=z + 12, tab=310, alt=lib.medida("T25 · Legenda · ALT"),
                                  modelo_corpo=f"<style>{_css_legenda()}</style>" + "{{content}}")),
        *pagina_lib.tooltip(tt_mun, "Município · quem falta", TT_MUN[1], TT_MUN[2], "T25 · Tooltip município · HTML",
                            ordem=350, folha_de_estilo=css),
        *pagina_lib.tooltip(tt_ano, "Ano · quem falta", TT_ANO[1], TT_ANO[2], "T25 · Tooltip ano · HTML", ordem=351,
                            folha_de_estilo=css),
        *pagina_lib.tooltip(tt_idade, "Idade · quem falta", TT_IDADE[1], TT_IDADE[2], "T25 · Tooltip idade · HTML",
                            ordem=352, folha_de_estilo=css),
    ]
    # filtro cruzado: as três peças se filtram (DataFilter explícito: o Deneb aceitaria realce, que deixaria o mapa com
    # as contas sem o ano/faixa); cada topo ignora a própria peça; ninguém filtra o filtro de estado da casca (o
    # VizuFilter)
    pecas = ["T25_Anos_Html", "T25_Idade_Html", "T25_Mapa_Pontos"]
    leitores = ["T25_Manchete_Html", "T25_Anos_Topo", "T25_Idade_Topo", "T25_Mapa_Legenda"]
    for origem in pecas:
        for alvo in pecas + leitores:
            if alvo == origem:
                continue
            tipo = "NoFilter" if (origem, alvo) in (("T25_Anos_Html", "T25_Anos_Topo"),
                                                    ("T25_Idade_Html", "T25_Idade_Topo")) else "DataFilter"
            itens.append(Interacao(P, origem, alvo, tipo))
        itens.append(Interacao(P, origem, f"{P}_Casca_Filtro", "NoFilter"))
    return itens


def main() -> int:
    contas()
    desenho()
    apagados = G.limpar()
    gravar_spec("t25_mapa.json", spec_mapa())
    print(G.resumo(), "· apagados:", [p.name for p in apagados])
    return 0


if __name__ == "__main__":
    sys.exit(main())
