# -*- coding: utf-8 -*-
"""desenho_t21 — tela 21 · 20 anos (dono: tela 21). Gera:

  pbi/dax/T21 20 anos/Desenho/*.dax   medidas de desenho: o fundo HTML (manchete, rótulos, régua dos anos) e o texto
                                      que leva ao Deneb os números de cada ano (só lê as contas de T21 20 anos\\Contas)
  pbi/spec/t21_mapa.json              Deneb (Vega 6, canvas): o mapa de pontos dos 5.571 municípios com a cor da margem
                                      do ano, o contorno das UFs que se desenha, o play que anda pelos seis anos (relógio
                                      que para, L123), a régua dos anos clicável, as barras dos municípios com o PT à
                                      frente e os contadores (ano, municípios, margem) desenhados com os glifos da Sora
                                      (o Deneb não carrega a fonte do painel: os números viram caminhos SVG)

e expõe para paginas/t21_vinte_anos.py o fundo fixo (bodyTemplate) com a MESMA geometria do spec.

    python -I -X utf8 pbi/scripts/desenho_t21.py
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import estilo  # noqa: E402

PBI = AQUI.parent
DAX = PBI / "dax" / "T21 20 anos" / "Desenho"
SPEC = PBI / "spec" / "t21_mapa.json"
PASTA = r"T21 20 anos\Desenho"
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]

W, H = 1620, 860                      # caixa do Deneb e do fundo (x 150, y 140)
MAPA_X, MAPA_Y, MAPA_K = 730, 0, 0.86  # quadro 1000 × 1000 → 860 × 860
# painel da esquerda (px dentro da caixa)
TXT = {"ano": (0, 300, 150), "cont": (0, 430, 78), "marg": (0, 556, 60)}   # x, linha de base, corpo (px); o
# rótulo da margem termina ~40 px acima do título das barras (antes encostava nele, 23/10/2026)
BARRAS_BASE, BARRAS_H = 750, 74        # barras dos municípios com o PT à frente (base e altura máxima)
REGUA_Y = 770                          # linha dos pontos da régua
PLAY = (40, 770, 30)                   # centro x, y e raio do botão
REGUA_X = [158 + i * 94 for i in range(6)]
DUR, PASSO, ENTRADA = 1000, 1750, 2600
COR_DOMINIO = [-0.6, -0.3, -0.12, 0.0, 0.12, 0.3, 0.6]
COR_FAIXA = ["azul_escuro", "azul", "azul_claro", "areia", "rosa", "vermelho", "vermelho_escuro"]


# ---------------------------------------------------------------------------------------------------- glifos
def glifos() -> dict:
    """Caminhos SVG (unidades da fonte, y para cima) dos algarismos tabulares, sinais e pontuação da Sora 700."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    f = instancer.instantiateVariableFont(TTFont(PBI / "assets" / "fontes" / "sora-wght.ttf"), {"wght": 700})
    gs = f.getGlyphSet()
    nomes = {str(i): n + ".tnum" for i, n in enumerate(["zero", "one", "two", "three", "four", "five", "six", "seven",
                                                       "eight", "nine"])}
    nomes.update({".": "period", ",": "comma", "+": "plus.tnum", "−": "minus.tnum", " ": "space"})
    saida = {}
    for ch, g in nomes.items():
        pen = SVGPathPen(gs, ntos=lambda v: str(round(v)))
        gs[g].draw(pen)
        saida[ch] = {"d": pen.getCommands() or "M0 0", "w": f["hmtx"][g][0]}
    return saida


# ---------------------------------------------------------------------------------------------------- UFs
def ufs() -> list:
    caminhos = json.loads((PBI / "assets" / "mapas" / "uf_caminhos.json").read_text(encoding="utf-8"))["caminhos"]
    rnd = random.Random(21)
    saida = []
    for uf, d in sorted(caminhos.items()):
        if uf == "ZZ":
            continue
        aneis, comp, xs = [], 0.0, []
        for parte in d.replace("Z", "").split("M")[1:]:
            pts = [tuple(map(float, p.split(","))) for p in parte.split("L") if p.strip()]
            aneis.append(pts)
            comp += sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
            xs += [p[0] for p in pts]
        tremido = "".join("M" + "L".join(f"{x + rnd.uniform(-1.1, 1.1):.1f},{y + rnd.uniform(-1.1, 1.1):.1f}"
                                         for x, y in a) for a in aneis)
        saida.append({"uf": uf, "d": d, "r": tremido, "l": round(comp, 1), "cx": round(sum(xs) / len(xs), 1)})
    return saida


# ---------------------------------------------------------------------------------------------------- DAX
def gravar(nome: str, descricao: str, expressao: str) -> None:
    destino = DAX / f"{nome}.dax"
    destino.parent.mkdir(parents=True, exist_ok=True)
    texto = f"/*\n@pasta: {PASTA}\n@formato: texto\n@descricao: {descricao}\n*/\n" + expressao.strip("\n") + "\n"
    if "\t" in texto:
        raise SystemExit(f"tab em {nome}")
    if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
        destino.write_text(texto, encoding="utf-8")


def medidas() -> None:
    for eixo in ['X','Y']:
        estilo.gravar_medida(f'T21 · mapa · {eixo.lower()} inteiro',r'T21 20 anos\Contas',
            'Coordenada de desenho em centésimos; recupera exatamente as duas casas do CSV; ausência preservada.',
            f"VAR _v = MAX ( 'Município'[{eixo}] )\nRETURN IF ( NOT ISBLANK ( _v ), ROUND ( _v * 100, 0 ) )",'#,0',subpasta='T21 20 anos/Contas',oraculo='dados/pbi/municipio.csv; duas casas exatas')
    for ano in ANOS:
        estilo.gravar_medida(f'T21 · mapa · margem {ano} inteira',r'T21 20 anos\Contas',
            'Margem só para cor do mapa, em milionésimos; erro máximo de 0,00005 ponto percentual. Contas e tooltips originais preservados.',
            f'VAR _m = [T21 · margem {ano}]\nRETURN IF ( NOT ISBLANK ( _m ), ROUND ( _m * 1000000, 0 ) )','#,0',subpasta='T21 20 anos/Contas',oraculo=f'T21 · margem {ano}; erro máximo de fração 0,0000005')
    estilo.gravar_medida('T21 · mapa · envia quadro',r'T21 20 anos\Contas',
        'Quadros globais seguem em uma única linha do dataset, a menor chave do recorte; não repetem 5.571 vezes.',
        "VAR _primeiro = MINX ( FILTER ( ALLSELECTED ( 'Município' ), NOT ISBLANK ( 'Município'[CodIBGE] ) ), VALUE ( 'Município'[CodIBGE] ) )\n"
        "RETURN IF ( VALUE ( SELECTEDVALUE ( 'Município'[CodIBGE] ) ) = _primeiro, 1, 0 )",'0',subpasta='T21 20 anos/Contas',oraculo='Brasil: somente código 1100015 envia os quadros')
    gravar("T21 · Mapa · anos para o Deneb", "Os seis anos num texto só, para o Deneb: 'ano|municípios com o PT à "
           "frente|margem nacional' separados por ';', somente na primeira chave do recorte. Só lê as contas.", r"""
-- 1 · Leituras e 2 · Textos (uma linha por ano)
VAR _anos =
    ADDCOLUMNS (
        VALUES ( 'Ano'[Ano] ),
        "@n", CALCULATE ( [T21 · municípios com o PT à frente], 'Ano'[Ano] = EARLIER ( 'Ano'[Ano] ) ),
        "@m", CALCULATE ( [T21 · margem nacional], 'Ano'[Ano] = EARLIER ( 'Ano'[Ano] ) )
    ) /* lista */
-- 4 · Marcação
RETURN
    IF ( [T21 · mapa · envia quadro] = 1, CONCATENATEX (
        _anos,
        'Ano'[Ano] & "|" & [@n] & "|" & FORMAT ( [@m], "0.0000", "en-US" ),
        ";",
        'Ano'[Ano], ASC
    ) ) /* lista */
""")
    pares = "\n".join(
        f"VAR _pt{a % 100:02d} = CALCULATE ( [T21 · candidato do PT], 'Ano'[Ano] = {a} )\n"
        f"VAR _adv{a % 100:02d} = CALCULATE ( [T21 · adversário], 'Ano'[Ano] = {a} )" for a in ANOS)

    def curto(v: str) -> str:
        return (f"SWITCH ( {v}, \"Dilma Rousseff\", \"Dilma\", \"Fernando Haddad\", \"Haddad\", \"Geraldo Alckmin\", "
                f"\"Alckmin\", \"José Serra\", \"Serra\", \"Aécio Neves\", \"Aécio\", \"Jair Bolsonaro\", \"Jair\", "
                f"\"Flávio Bolsonaro\", \"Flávio\", {v} )")
    regua = "\n        & ".join(
        f"\"<div class='ano' style='left:{x - 52}px'><b>{a}</b><span>\" & {curto(f'_pt{a % 100:02d}')} & \" × \" & "
        f"{curto(f'_adv{a % 100:02d}')} & \"</span></div>\"" for a, x in zip(ANOS, REGUA_X))
    gravar("T21 · Fundo · HTML", "Fundo da tela 21 (atrás do Deneb, mesma caixa): a manchete com os municípios com "
           "o PT à frente em 2006 e em 2026 e, na régua, quem disputou cada eleição.", f"""
-- 1 · Leituras
VAR _n06 = CALCULATE ( [T21 · municípios com o PT à frente], 'Ano'[Ano] = 2006 )
VAR _n26 = CALCULATE ( [T21 · municípios com o PT à frente], 'Ano'[Ano] = 2026 )
{pares}
-- 2 · Textos
VAR _txt06 = FORMAT ( _n06, "#,0" )
VAR _txt26 = FORMAT ( _n26, "#,0" )
-- 4 · Marcação
RETURN
    "<div class='tela t21b'>"
        & "<div class='man sobe d2'>De <span class='num'>" & _txt06 & "</span> para <span class='num'>" & _txt26
            & "</span> municípios com o PT à frente, de 2006 a 2026</div>"
        & "<div class='regua entra d6'>"
        & {regua}
        & "</div>"
    & "</div>"
""")
    gravar("T21 · Fundo · ALT", "Texto alternativo da tela 21.", r"""
-- 1 · Leituras
VAR _n06 = CALCULATE ( [T21 · municípios com o PT à frente], 'Ano'[Ano] = 2006 )
VAR _n26 = CALCULATE ( [T21 · municípios com o PT à frente], 'Ano'[Ano] = 2026 )
RETURN
    "De " & FORMAT ( _n06, "#,0" ) & " para " & FORMAT ( _n26, "#,0" ) & " municípios com o PT à frente, de 2006 a "
        & "2026. Mapa de pontos com a margem de cada ano; o play anda pelas seis eleições."
""")
    gravar("T21 · Mapa · ALT", "Texto alternativo do mapa animado da tela 21.", r"""
-- 1 · Leituras
VAR _n26 = CALCULATE ( [T21 · municípios com o PT à frente], 'Ano'[Ano] = 2026 )
VAR _m26 = CALCULATE ( [T21 · margem nacional], 'Ano'[Ano] = 2026 )
RETURN
    "Mapa dos municípios pela margem do PT. Em 2026, " & FORMAT ( _n26, "#,0" ) & " municípios com o PT à frente e "
        & "margem nacional de " & FORMAT ( _m26 * 100, "+0.0;−0.0;0.0" ) & " pontos. Use o play ou clique num ano."
""")


# ---------------------------------------------------------------------------------------------------- Deneb
def spec() -> dict:
    c = estilo.COR
    sx = f"(width / {W})"
    cfg = {k: {"x": x, "y": y, "s": s} for k, (x, y, s) in TXT.items()}
    slots = [{"k": k, "i": i} for k in TXT for i in range(8)]
    campos = [f"m{a % 100:02d}" for a in ANOS]
    vivo = (f"estado.tocando || (estado.t0 > 0 && now() - estado.t0 < {DUR + 120}) || now() - t0 < {ENTRADA + 120}")
    return {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": "T21 · 20 anos: um ponto por município com a cor da margem do PT no ano; o play anda de 2006 a "
                       "2026 (a cor desliza de um ano para o outro), a régua dos anos é clicável, as barras e os "
                       "contadores (ano, municípios com o PT à frente, margem nacional) contam a cada passo. Os números "
                       "vêm do DAX (campo 'anos'); os algarismos são glifos da Sora em caminho SVG. Estado parado (prévia, "
                       "PDF) = 2026.",
        "width": {"signal": "pbiContainerWidth"}, "height": {"signal": "pbiContainerHeight"}, "padding": 0,
        "autosize": {"type": "none", "contains": "padding"}, "background": None, "config": {"view": {"stroke": None}},
        "signals": [
            {"name": "estatico", "init": "!(windowSize()[0] > 0)"},
            {"name": "t0", "init": "now()"},
            {"name": "campos", "value": campos},
            {"name": "glifos", "value": glifos()},
            {"name": "cfg", "value": cfg},
            {"name": "estado", "value": {"de": 5, "para": 5, "t0": 0, "tocando": False},
             "on": [
                 {"events": "@play:click, @playIcone:click",
                  "update": "estado.tocando ? {de: estado.para, para: estado.para, t0: 0, tocando: false} : "
                            "{de: estado.para, para: 0, t0: now(), tocando: true}"},
                 {"events": "@anoBola:click, @anoAlvo:click",
                  "update": "{de: estado.para, para: datum.i, t0: now(), tocando: false}"},
                 {"events": "timer{16}",
                  "update": f"estado.tocando && now() - estado.t0 >= {PASSO} ? (estado.para < 5 ? "
                            f"{{de: estado.para, para: estado.para + 1, t0: now(), tocando: estado.para + 1 < 5}} : "
                            f"{{de: 5, para: 5, t0: estado.t0, tocando: false}}) : estado"}]},
            {"name": "agora", "init": "now()",
             "on": [{"events": "timer{16}", "update": f"estatico ? agora : ({vivo} ? now() : agora)"}]},
            {"name": "entrada", "update": f"estatico ? 1 : clamp((agora - t0) / {ENTRADA}, 0, 1)"},
            {"name": "prog", "update": f"estatico || estado.t0 == 0 ? 1 : clamp((agora - estado.t0) / {DUR}, 0, 1)"},
            {"name": "e", "update": "prog < 0.5 ? 4 * prog * prog * prog : 1 - pow(-2 * prog + 2, 3) / 2"},
            {"name": "campoDe", "update": "campos[estado.de]"},
            {"name": "campoPara", "update": "campos[estado.para]"},
            {"name": "temAnos", "update": "length(data('anos')) == 6"},
            {"name": "nAgora",
             "update": "temAnos ? round(data('anos')[estado.de].n + (data('anos')[estado.para].n - "
                       "data('anos')[estado.de].n) * e) : 0"},
            {"name": "mAgora",
             "update": "temAnos ? 100 * (data('anos')[estado.de].m + (data('anos')[estado.para].m - "
                       "data('anos')[estado.de].m) * e) : 0"},
            {"name": "txtAno", "update": "temAnos ? '' + data('anos')[estado.para].ano : ''"},
            {"name": "txtCont", "update": "temAnos ? replace(format(nAgora, ',d'), ',', '.') : ''"},
            {"name": "txtMarg",
             "update": "temAnos ? (mAgora >= 0.05 ? '+' : (mAgora <= -0.05 ? '−' : '')) + "
                       "replace(format(abs(mAgora), '.1f'), '.', ',') : ''"},
            {"name": "k", "update": f"{MAPA_K} * {sx}"},
            {"name": "ox", "update": f"{MAPA_X} * {sx}"},
            {"name": "oy", "update": f"{MAPA_Y} * {sx}"},
            # o ano sob o mouse (coluna ou ponto da régua): a coluna escurece e a bola cresce, antes do clique
            {"name": "anoSobre", "value": -1,
             "on": [{"events": "@anoAlvo:mouseover, @anoBola:mouseover", "update": "datum.i"},
                    {"events": "@anoAlvo:mouseout, @anoBola:mouseout", "update": "-1"}]},
            {"name": "sobre", "value": None,
             "on": [{"events": "@pontos:mouseover", "update": "datum"}, {"events": "@pontos:mouseout",
                                                                         "update": "null"}]},
        ],
        "data": [
            {"name": "dataset"},
            {"name": "anos", "source": "dataset",
             "transform": [
                 {"type": "filter", "expr": "isValid(datum.anos) && datum.anos != ''"},
                 {"type": "aggregate", "groupby": ["anos"]},
                 {"type": "formula", "as": "partes", "expr": "split(datum.anos, ';')"},
                 {"type": "flatten", "fields": ["partes"], "as": ["parte"]},
                 {"type": "formula", "as": "ano", "expr": "toNumber(split(datum.parte, '|')[0])"},
                 {"type": "formula", "as": "n", "expr": "toNumber(split(datum.parte, '|')[1])"},
                 {"type": "formula", "as": "m", "expr": "toNumber(split(datum.parte, '|')[2])"},
                 {"type": "collect", "sort": {"field": "ano"}},
                 {"type": "window", "sort": {"field": "ano"}, "ops": ["row_number"], "as": ["i1"]},
                 {"type": "formula", "as": "i", "expr": "datum.i1 - 1"},
                 {"type": "joinaggregate", "fields": ["n"], "ops": ["max"], "as": ["nmax"]}]},
            {"name": "pts", "source": "dataset",
             "transform": [
                 {"type": "filter", "expr": "isValid(datum.x) && isValid(datum.y)"},
                  {"type": "formula", "as": "onda", "expr": "datum.y / 100000"}]},
            {"name": "ufs", "values": ufs(),
             "transform": [{"type": "formula", "as": "atraso", "expr": "200 + 700 * datum.cx / 1000"}]},
            {"name": "letras", "values": slots,
             "transform": [
                 {"type": "formula", "as": "txt",
                  "expr": "datum.k == 'ano' ? txtAno : (datum.k == 'cont' ? txtCont : txtMarg)"},
                 {"type": "filter", "expr": "datum.i < length(datum.txt)"},
                 {"type": "formula", "as": "ch", "expr": "substring(datum.txt, datum.i, datum.i + 1)"},
                 {"type": "formula", "as": "w", "expr": "glifos[datum.ch] ? glifos[datum.ch].w : 0"},
                 {"type": "window", "sort": {"field": "i"}, "groupby": ["k"], "ops": ["sum"], "fields": ["w"],
                  "as": ["cum"]},
                 {"type": "formula", "as": "x0", "expr": "datum.cum - datum.w"}]},
        ],
        "scales": [
            {"name": "cor", "type": "linear", "domain": [round(v*1000000) for v in COR_DOMINIO], "range": [c[k] for k in COR_FAIXA],
             "clamp": True, "interpolate": "rgb"},
        ],
        "marks": [
            # contorno das UFs: o traço se desenha (dash em px da tela), depois some para 45 %
            {"type": "path", "from": {"data": "ufs"}, "interactive": False,
             "encode": {"update": {
                 "path": {"field": "r"}, "x": {"signal": "ox"}, "y": {"signal": "oy"},
                 "scaleX": {"signal": "k"}, "scaleY": {"signal": "k"},
                 "stroke": {"value": c["grafite"]}, "strokeWidth": {"value": 1}, "strokeJoin": {"value": "round"},
                 "strokeOpacity": {"signal": "estatico ? 0.4 : 0.75 - 0.35 * clamp((agora - t0 - 1800) / 900, 0, 1)"},
                 "strokeDash": {"signal": "[datum.l * k + 4, datum.l * k + 4]"},
                 "strokeDashOffset": {"signal": "(datum.l * k + 4) * (1 - pow(clamp((entrada * "
                                                f"{ENTRADA} - datum.atraso) / 1000, 0, 1), 0.7))"}}}},
            # pontos dos municípios: a cor desliza da margem do ano de partida para a do ano de chegada
            {"type": "symbol", "name": "pontos", "from": {"data": "pts"},
             "encode": {"update": {
                  "x": {"signal": "ox + datum.x / 100 * k"}, "y": {"signal": "oy + datum.y / 100 * k"},
                 "shape": {"value": "circle"}, "size": {"signal": "pow(3.1 * sqrt(k / 0.86), 2)"},
                 "fill": {"signal": "isValid(datum[campoDe]) && isValid(datum[campoPara]) ? "
                                    "scale('cor', datum[campoDe] + (datum[campoPara] - datum[campoDe]) * e) : "
                                    "(isValid(datum[campoPara]) ? scale('cor', datum[campoPara]) : '"
                                    + c["creme"] + "')"},
                 "fillOpacity": {"signal": "clamp((entrada * 2.6 - 1.0) - datum.onda * 0.9, 0, 1) * 0.92"},
                 "stroke": {"signal": f"sobre && sobre.cod == datum.cod ? '{c['tinta']}' : null"},
                 "strokeWidth": {"value": 1.4}, "cursor": {"value": "pointer"}}}},
            # barras: municípios com o PT à frente em cada ano (a do ano em tela em tinta)
            {"type": "rect", "from": {"data": "anos"}, "interactive": False,
             "encode": {"update": {
                 "xc": {"signal": f"({json.dumps(REGUA_X)})[datum.i] * {sx}"}, "width": {"signal": f"40 * {sx}"},
                 "y2": {"signal": f"{BARRAS_BASE} * {sx}"},
                 "y": {"signal": f"({BARRAS_BASE} - {BARRAS_H} * datum.n / datum.nmax * clamp(entrada * 2 - 0.6, 0, 1))"
                                 f" * {sx}"},
                 "fill": {"signal": f"datum.i == estado.para ? '{c['tinta']}' : (datum.i == anoSobre ? "
                                    f"'{c['grafite']}' : '{c['areia']}')"}}}},
            # régua: linha, alvos de clique e pontos
            {"type": "rule", "interactive": False,
             "encode": {"update": {"x": {"signal": f"{REGUA_X[0]} * {sx}"}, "x2": {"signal": f"{REGUA_X[-1]} * {sx}"},
                                   "y": {"signal": f"{REGUA_Y} * {sx}"}, "stroke": {"value": c["grafite"]},
                                   "strokeWidth": {"value": 1.2}}}},
            {"type": "rect", "name": "anoAlvo", "from": {"data": "anos"},
             "encode": {"update": {
                 "xc": {"signal": f"({json.dumps(REGUA_X)})[datum.i] * {sx}"}, "width": {"signal": f"90 * {sx}"},
                 "y": {"signal": f"({BARRAS_BASE - BARRAS_H}) * {sx}"}, "y2": {"signal": f"({REGUA_Y + 64}) * {sx}"},
                 "fill": {"value": "transparent"}, "cursor": {"value": "pointer"}}}},
            {"type": "symbol", "name": "anoBola", "from": {"data": "anos"},
             "encode": {"update": {
                 "x": {"signal": f"({json.dumps(REGUA_X)})[datum.i] * {sx}"}, "y": {"signal": f"{REGUA_Y} * {sx}"},
                 "shape": {"value": "circle"},
                 "size": {"signal": f"datum.i == estado.para ? pow(22 * {sx}, 2) : (datum.i == anoSobre ? "
                                    f"pow(19 * {sx}, 2) : pow(15 * {sx}, 2))"},
                 "fill": {"signal": f"datum.i == estado.para ? '{c['tinta']}' : '{c['papel']}'"},
                 "stroke": {"value": c["tinta"]}, "strokeWidth": {"value": 1.8}, "cursor": {"value": "pointer"}}}},
            # play / pausa
            {"type": "symbol", "name": "play",
             "encode": {"update": {
                 "x": {"signal": f"{PLAY[0]} * {sx}"}, "y": {"signal": f"{PLAY[1]} * {sx}"},
                 "shape": {"value": "circle"}, "size": {"signal": f"pow(2 * {PLAY[2]} * {sx}, 2)"},
                 "fill": {"value": c["tinta"]}, "cursor": {"value": "pointer"}},
                 "hover": {"fill": {"value": c["grafite"]}}}},
            {"type": "path", "name": "playIcone",
             "encode": {"update": {
                 "x": {"signal": f"{PLAY[0]} * {sx}"}, "y": {"signal": f"{PLAY[1]} * {sx}"},
                 "scaleX": {"signal": sx}, "scaleY": {"signal": sx},
                 "path": {"signal": "estado.tocando ? 'M-8,-10 L-3,-10 L-3,10 L-8,10 Z M3,-10 L8,-10 L8,10 L3,10 Z' : "
                                    "'M-6,-11 L11,0 L-6,11 Z'"},
                 "fill": {"value": c["papel"]}, "cursor": {"value": "pointer"}}}},
            # contadores com os glifos da Sora
            {"type": "path", "from": {"data": "letras"}, "interactive": False,
             "encode": {"update": {
                 "path": {"signal": "glifos[datum.ch] ? glifos[datum.ch].d : ''"},
                 "x": {"signal": f"(cfg[datum.k].x + datum.x0 * cfg[datum.k].s / 1000) * {sx}"},
                 "y": {"signal": f"cfg[datum.k].y * {sx}"},
                 "scaleX": {"signal": f"cfg[datum.k].s / 1000 * {sx}"},
                 "scaleY": {"signal": f"-cfg[datum.k].s / 1000 * {sx}"},
                 "fill": {"signal": f"datum.k == 'marg' ? (mAgora >= 0 ? '{c['vermelho']}' : '{c['azul']}') : "
                                    f"'{c['tinta']}'"},
                 "opacity": {"signal": "clamp(entrada * 3 - 0.4, 0, 1)"}}}},
        ],
    }


# ---------------------------------------------------------------------------------------------------- fundo fixo
def corpo_fundo() -> str:
    c = estilo.COR
    ancora = {k: (x, y, s) for k, (x, y, s) in TXT.items()}
    leg_x, leg_y = 1300, 800
    grad = ", ".join(f"{c[k]} {i / 6 * 100:.0f}%" for i, k in enumerate(COR_FAIXA))
    css = (
        ".t21b .rot{position:absolute;left:0;top:0}"
        ".t21b .man{position:absolute;left:0;top:24px;width:640px;font-size:30px;font-weight:600;line-height:1.2}"
        ".t21b .man .num{font-size:30px;font-weight:700}"
        ".t21b .sub{position:absolute;left:0;top:104px;width:620px;font-size:15px;line-height:1.4;color:var(--grafite)}"
        ".t21b .lb{position:absolute;left:0;font-size:17px;font-weight:600;color:var(--grafite)}"
        ".t21b .lb small{display:block;font-size:13px;font-weight:400;color:var(--cinza);margin-top:2px}"
        ".t21b .regua .ano{position:absolute;top:" + str(REGUA_Y + 26) + "px;width:104px;text-align:center}"
        ".t21b .regua .ano b{display:block;font-size:15px;font-weight:700}"
        ".t21b .regua .ano span{display:block;font-size:12px;color:var(--cinza);white-space:nowrap;margin-top:2px}"
        ".t21b .barras{position:absolute;left:" + str(REGUA_X[0] - 52) + "px;top:" + str(BARRAS_BASE - BARRAS_H - 28)
        + "px;font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--cinza)}"
        ".t21b .mao{position:absolute;left:4px;top:" + str(PLAY[1] - 104) + "px;font-size:24px;transform:rotate(-6deg)}"
        ".t21b .seta{position:absolute;left:30px;top:" + str(PLAY[1] - 76) + "px}"
        ".t21b .seta path{fill:none;stroke:var(--tinta);stroke-width:1.8;stroke-linecap:round;animation-delay:2.2s}"
        f".t21b .leg{{position:absolute;left:{leg_x}px;top:{leg_y}px;width:300px}}"
        f".t21b .leg .g{{height:10px;background:linear-gradient(90deg,{grad})}}"
        ".t21b .leg .e{display:flex;justify-content:space-between;font-size:13px;color:var(--cinza);margin-top:4px}"
        ".t21b .leg .t{font-size:13px;color:var(--grafite);margin-bottom:6px}"
    )
    lbls = (f"<div class='lb sobe d4' style='top:{ancora['cont'][1] + 14}px'>municípios com o PT à frente</div>"
            f"<div class='lb sobe d5' style='top:{ancora['marg'][1] + 12}px'>margem do PT no país, em pontos"
            f"<small>votos do PT menos os do adversário, sobre os válidos</small></div>")
    seta = (f"<svg class='seta' width='60' height='50'>{estilo.defs_rabisco('rb21', 1.2)}"
            f"<path class='traco' pathLength='1' filter='url(#rb21)' d='M30,4 C40,14 30,30 18,38 M18,38 L27,37 M18,38 "
            f"L19,29'/></svg>")
    return (f"<style>{css}</style><div class='tela t21b'>"
            f"<div class='rot sobe'>De 2006 a 2026 · PT × o adversário mais votado</div>"
            f"<div class='sub sobe d3'>Cada ponto é um município, na cor de quem ficou à frente naquele ano. "
            f"Aperte o play ou clique num ano.</div>"
            f"{lbls}<div class='barras entra d6'>municípios com o PT à frente, por eleição</div>"
            f"<div class='mao entra d16'>aperte o play</div>{seta}"
            f"<div class='leg entra d8'><div class='t'>margem do PT no município, em pontos</div><div class='g'></div>"
            f"<div class='e'><span>−60 · adversário</span><span>0</span><span>PT · +60</span></div></div>"
            f"</div>{{{{content}}}}")


def main() -> int:
    medidas()
    SPEC.write_text(json.dumps(spec(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"T21: medidas de desenho em {DAX} · spec {SPEC.name} ({SPEC.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
