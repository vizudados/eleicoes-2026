# -*- coding: utf-8 -*-
"""desenho_t20 — tela 20 · Escola (dono: tela 20). Gera:

  pbi/dax/T20 Escola/Desenho/*.dax    medidas de desenho (HTML e ALT): só leem as contas de T20 Escola\\Contas
  pbi/spec/t20_contagem.json          o contorno de Contagem (malha do IBGE) no mesmo quadro de PX/PY do mapa da tela
                                      (docs/midia/mapas/escolas-contagem.png: bbox com folga de 6 %, x = lon·cos 15°)

e expõe para paginas/t20_escola.py os modelos fixos (bodyTemplate): o contorno que se desenha em rabisco, os nomes de
bairro, o papel da ficha (post-it com alfinete), o cabeçalho da lista e o cartão "como explorar".

    python -I -X utf8 pbi/scripts/desenho_t20.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import estilo  # noqa: E402

PBI = AQUI.parent
RAIZ = PBI.parent
DAX = PBI / "dax" / "T20 Escola" / "Desenho"
CONTORNO = PBI / "spec" / "t20_contagem.json"
PASTA = r"T20 Escola\Desenho"
COS = math.cos(math.radians(15))

MAPA_W, MAPA_H = 692, 860              # mesma proporção do quadro do mapa (1400 × 1740)
QUEDAS_TOPO, QUEDAS_H = 70, 88
BAIRROS = [("Nova Contagem", 16.0, 11.5, 0, 0), ("Centro", 38.0, 66.5, 0, 0), ("Nacional", 66.5, 27.6, 0, 0),
           ("Eldorado", 84.5, 64.0, 0, 0), ("Industrial", 81.0, 95.4, 0, 0)]
# margem 2026 do local → cor (faixas finas: em Contagem a margem vai de −25 a +13 pontos)
FAIXAS = [(-0.20, "#1D3C6E"), (-0.10, "#2B5797"), (-0.03, "#6F8DBE"), (0.0, "#A9B8CF"), (0.03, "#E2B3A9"),
          (0.10, "#D9877B"), (99, "#B8322A")]


# ---------------------------------------------------------------------------------------------------- contorno
def contorno() -> dict:
    """Contagem (3118601) da malha do IBGE, no quadro % do mapa (0–100 × 0–100, y para baixo)."""
    topo = json.loads((RAIZ / "dados" / "bruto" / "ibge" / "malha_municipios.json").read_text(encoding="utf-8"))
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcos = []
    for arco in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arco:
            x += dx
            y += dy
            pts.append(((x * sx + tx) * COS, y * sy + ty))
        arcos.append(pts)
    g = next(g for g in topo["objects"]["BRMU"]["geometries"] if g["properties"]["codarea"] == "3118601")
    poligonos = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    aneis = []
    for p in poligonos:
        for anel_idx in p:
            pts = []
            for i in anel_idx:
                seg = arcos[i] if i >= 0 else arcos[~i][::-1]
                pts.extend(seg if not pts else seg[1:])
            aneis.append(pts)
    externos = [a for a in aneis]
    xs = [p[0] for a in externos for p in a]
    ys = [p[1] for a in externos for p in a]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    fx, fy = (x1 - x0) * 0.06, (y1 - y0) * 0.06
    x0, x1, y0, y1 = x0 - fx, x1 + fx, y0 - fy, y1 + fy
    d = ""
    for a in aneis:
        d += "M" + " L".join(f"{100 * (x - x0) / (x1 - x0):.2f},{100 * (y1 - y) / (y1 - y0):.2f}" for x, y in a) + "Z"
    return {"viewBox": "0 0 100 100", "d": d}


# ---------------------------------------------------------------------------------------------------- DAX
def gravar(nome: str, descricao: str, expressao: str) -> None:
    destino = DAX / f"{nome}.dax"
    destino.parent.mkdir(parents=True, exist_ok=True)
    texto = f"/*\n@pasta: {PASTA}\n@formato: texto\n@descricao: {descricao}\n*/\n" + expressao.strip("\n") + "\n"
    if "\t" in texto:
        raise SystemExit(f"tab em {nome}")
    if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
        destino.write_text(texto, encoding="utf-8")


def _escapa(var: str, fonte: str) -> str:
    return (f"VAR {var}0 = {fonte}\n"
            f"VAR {var}1 = SUBSTITUTE ( SUBSTITUTE ( {var}0, \"&\", \"&amp;\" ), \"<\", \"&lt;\" )\n"
            f"VAR {var} = SUBSTITUTE ( SUBSTITUTE ( {var}1, \">\", \"&gt;\" ), \"'\", \"&#39;\" )")


def _cor(var: str) -> str:
    ramos = ",\n        ".join(f"{var} < {lim}, \"{cor}\"" for lim, cor in FAIXAS[:-1])
    return f"SWITCH (\n        TRUE (),\n        {ramos},\n        \"{FAIXAS[-1][1]}\"\n    )"


PP = '"+0.0;−0.0;0.0"'


def medidas() -> None:
    gravar("T20 · Resposta · HTML", "A resposta da tela: '12 de 112' locais com Lula à frente (contador), a manchete "
           "com o número de 2022 e quantos viraram.", rf"""
-- 1 · Leituras
VAR _lula = [T20 · locais com Lula à frente]
VAR _n = [T20 · locais]
VAR _lula22 = [T20 · locais com Lula à frente em 2022]
VAR _n22 = [T20 · locais em 2022]
VAR _viraram = [T20 · locais que viraram]
-- 2 · Textos
VAR _rotLocal = IF ( _lula = 1, "local de votação com Lula à frente em 2026", "locais de votação com Lula à frente em 2026" )
VAR _txtViraram =
    IF ( _viraram = 1, "1 local virou", _viraram & " locais viraram" ) & " de Lula para Flávio."
-- 4 · Marcação
RETURN
    "<div class='tela t20r'>"
        & "<div class='grande sobe'><span class='num'>" & _lula & "</span> de <span class='num'>" & _n & "</span></div>"
        & "<div class='rotulo sobe d2'>" & _rotLocal & "</div>"
        & "<div class='man sobe d3'>Lula ficou à frente em " & _lula & " dos " & _n
            & IF ( _n = 1, " local", " locais" ) & " de votação de Contagem; em 2022, eram <span class='num'>"
            & _lula22 & "</span></div>"
        & "<div class='txt sobe d4'>" & _txtViraram & " Em 2022, a cidade votava em " & _n22 & " locais.</div>"
    & "</div>"
""")
    gravar("T20 · Resposta · ALT", "Texto alternativo da resposta da tela 20.", r"""
-- 1 · Leituras
VAR _lula = [T20 · locais com Lula à frente]
VAR _n = [T20 · locais]
VAR _lula22 = [T20 · locais com Lula à frente em 2022]
VAR _viraram = [T20 · locais que viraram]
RETURN
    "Lula ficou à frente em " & _lula & " dos " & _n & " locais de votação de Contagem em 2026; em 2022, eram "
        & _lula22 & ". " & _viraram & IF ( _viraram = 1, " local virou", " locais viraram" ) & " de Lula para Flávio."
""")
    # --- ponto do mapa (um por local)
    gravar("T20 · Mapa · HTML", "Um ponto do mapa de Contagem (granularidade: T20 Local[Local]): posição PX/PY, "
           "tamanho pelos votos válidos, cor pela margem de 2026; brota em onda do oeste para o leste.", rf"""
-- 1 · Leituras
VAR _px = [T20 · posição x]
VAR _py = [T20 · posição y]
VAR _val = [T20 · válidos 2026]
VAR _maior = [T20 · maior válidos]
VAR _m26 = [T20 · margem 2026]
-- 2 · Textos
VAR _cor =
    {_cor("_m26")}
-- 3 · Geometria
VAR _d = 7 + 15 * SQRT ( DIVIDE ( _val, _maior ) ) -- geometria
VAR _x = _px / 100 * {MAPA_W} - _d / 2 -- geometria
VAR _y = _py / 100 * {MAPA_H} - _d / 2 -- geometria
VAR _atraso = 1700 + ROUND ( _px * 14, 0 ) -- geometria
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _px ),
        "<div class='tela t20p'><i class='pt' style='left:" & FORMAT ( _x, "0.0##", "en-US" ) & "px;top:"
            & FORMAT ( _y, "0.0##", "en-US" ) & "px;width:" & FORMAT ( _d, "0.0##", "en-US" ) & "px;height:"
            & FORMAT ( _d, "0.0##", "en-US" ) & "px;background:" & _cor & ";animation-delay:" & _atraso & "ms'></i>"
        & "</div>"
    )
""")
    gravar("T20 · Mapa · ALT", "Texto alternativo do mapa das escolas.", r"""
-- 1 · Leituras
VAR _n = [T20 · locais]
VAR _lula = [T20 · locais com Lula à frente]
RETURN
    "Mapa de Contagem com os " & _n & " locais de votação: " & _lula & IF ( _lula = 1, " com Lula à frente", " com Lula à frente" )
        & " (vermelho) e os outros com Flávio (azul). Passe o mouse num ponto para ver a escola; clique para pôr na ficha."
""")
    # --- anel do local escolhido (camada atrás do mapa)
    gravar("T20 · Escolhido · HTML", "O anel à mão em volta do local da ficha, na camada atrás dos pontos (recebe a "
           "escolha do filtro, do mapa e da lista), com o nome do local.", rf"""
-- 1 · Leituras
VAR _esc = [T20 · local escolhido]
VAR _ha = [T20 · há escolha]
VAR _px = CALCULATE ( [T20 · posição x], 'T20 Local'[Local] = _esc )
VAR _py = CALCULATE ( [T20 · posição y], 'T20 Local'[Local] = _esc )
-- 2 · Textos
{_escapa("_nome", "_esc")}
-- 3 · Geometria
VAR _x = _px / 100 * {MAPA_W} -- geometria
VAR _y = _py / 100 * {MAPA_H} -- geometria
VAR _direita = _x > {MAPA_W} * 0.62 -- geometria
VAR _xr = IF ( _direita, _x - 22, _x + 22 ) -- geometria
-- 4 · Marcação
RETURN
    IF (
        ISBLANK ( _px ),
        "<div class='tela t20e'><div class='sem'>" & _nome & ": sem endereço no mapa</div></div>",
        "<div class='tela t20e'>"
            & "<div class='anel' style='left:" & FORMAT ( _x - 26, "0.0##", "en-US" ) & "px;top:"
            & FORMAT ( _y - 24, "0.0##", "en-US" ) & "px'>"
            & "<svg width='52' height='48' viewBox='0 0 52 48'><path class='traco' pathLength='1' filter='url(#rbe)' "
            & "d='M8,28 C2,10 30,-2 44,10 C54,20 46,42 26,44 C8,46 2,30 12,16 C18,8 30,6 38,9'/></svg></div>"
            & "<div class='nome sobe d4" & IF ( _direita, " dir", "" ) & "' style='left:"
            & FORMAT ( _xr, "0.0##", "en-US" ) & "px;top:" & FORMAT ( _y - 12, "0.0##", "en-US" ) & "px'>"
            & _nome & "</div>"
        & "</div>"
    )
""")
    gravar("T20 · Escolhido · ALT", "Texto alternativo do anel do local escolhido.", r"""
"Local em destaque no mapa: " & [T20 · local escolhido]
""")
    # --- ficha (post-it)
    gravar("T20 · Ficha · HTML", "A ficha do local escolhido (post-it com alfinete): bairro, seções e válidos, Lula × "
           "Flávio em 2026 e a margem de Lula em 2018 → 2022 → 2026, com o selo de quem virou. Sem escolha, a Escola "
           "Estadual Nova Contagem-I.", ficha())
    gravar("T20 · Ficha · ALT", "Texto alternativo da ficha do local.", rf"""
-- 1 · Leituras
VAR _esc = [T20 · local escolhido]
VAR _m18 = CALCULATE ( [T20 · margem 2018], 'T20 Local'[Local] = _esc )
VAR _m22 = CALCULATE ( [T20 · margem 2022], 'T20 Local'[Local] = _esc )
VAR _m26 = CALCULATE ( [T20 · margem 2026], 'T20 Local'[Local] = _esc )
-- 2 · Textos
VAR _t18 = IF ( ISBLANK ( _m18 ), "sem dado", FORMAT ( _m18 * 100, {PP} ) )
VAR _t22 = IF ( ISBLANK ( _m22 ), "sem dado", FORMAT ( _m22 * 100, {PP} ) )
RETURN
    "Ficha: " & _esc & ". Margem de Lula em pontos: 2018 " & _t18 & "; 2022 " & _t22 & "; 2026 "
        & FORMAT ( _m26 * 100, {PP} ) & "."
""")
    # --- lista das maiores quedas
    gravar("T20 · Quedas · HTML", "Uma linha da lista das 5 maiores quedas da margem de Lula, 2022 → 2026 "
           "(granularidade T20 Local[Local], Top 5 pela queda): posição, nome, bairro e seções, a queda e o selo.", rf"""
-- 1 · Leituras
VAR _pos = [T20 · posição na queda]
VAR _bairro = [T20 · bairro]
VAR _secoes = [T20 · seções]
VAR _var = [T20 · variação da margem]
VAR _virou = [T20 · virou]
-- 2 · Textos
{_escapa("_nome", "[T20 · nome do local]")}
VAR _txtVar = FORMAT ( _var * 100, {PP} ) & " p.p."
VAR _sub = _bairro & " · " & _secoes & IF ( _secoes = 1, " seção", " seções" )
VAR _selo = IF ( _virou = 1, "<span class='selo'>virou</span>", "" )
-- 3 · Geometria
VAR _y = {QUEDAS_TOPO} + ( _pos - 1 ) * {QUEDAS_H} -- geometria
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _pos ) && _pos <= 5,
        "<div class='tela t20q'><div class='ln sobe d" & ( _pos + 2 ) & "' style='top:" & _y & "px'>"
            & "<span class='p'>" & _pos & "</span>"
            & "<span class='nm'>" & _nome & "</span>"
            & "<span class='sb'>" & _sub & "</span>"
            & "<span class='v flavio tnum'>" & _txtVar & "</span>" & _selo
        & "</div></div>"
    )
""")
    gravar("T20 · Quedas · ALT", "Texto alternativo da lista das maiores quedas.", r"""
"As 5 escolas de Contagem onde a margem de Lula mais caiu de 2022 para 2026. Clique numa linha para pôr a escola na ficha."
""")
    # --- tooltip (post-it do hover)
    gravar("T20 · Tooltip escola · HTML", "Post-it do local sob o mouse (página de tooltip ttT20Escola): bairro, "
           "seções, Lula × Flávio em 2026 e a margem de Lula em 2018 → 2022 → 2026.", tooltip())
    gravar("T20 · Tooltip escola · ALT", "Texto alternativo do post-it do local.", rf"""
-- 1 · Leituras
VAR _nome = [T20 · nome do local]
VAR _m22 = [T20 · margem 2022]
VAR _m26 = [T20 · margem 2026]
-- 2 · Textos
VAR _t22 = IF ( ISBLANK ( _m22 ), "sem dado em 2022", FORMAT ( _m22 * 100, {PP} ) & " em 2022" )
RETURN
    IF ( NOT ISBLANK ( _nome ), _nome & ": margem de Lula " & _t22 & " e " & FORMAT ( _m26 * 100, {PP} ) & " em 2026." )
""")


def ficha() -> str:
    return rf"""
-- 1 · Leituras
VAR _esc = [T20 · local escolhido]
VAR _ha = [T20 · há escolha]
VAR _bairro = CALCULATE ( [T20 · bairro], 'T20 Local'[Local] = _esc )
VAR _secoes = CALCULATE ( [T20 · seções], 'T20 Local'[Local] = _esc )
VAR _val = CALCULATE ( [T20 · válidos 2026], 'T20 Local'[Local] = _esc )
VAR _lula = CALCULATE ( [T20 · Lula % 2026], 'T20 Local'[Local] = _esc )
VAR _flavio = CALCULATE ( [T20 · Flávio % 2026], 'T20 Local'[Local] = _esc )
VAR _m18 = CALCULATE ( [T20 · margem 2018], 'T20 Local'[Local] = _esc )
VAR _m22 = CALCULATE ( [T20 · margem 2022], 'T20 Local'[Local] = _esc )
VAR _m26 = CALCULATE ( [T20 · margem 2026], 'T20 Local'[Local] = _esc )
VAR _virou = CALCULATE ( [T20 · virou], 'T20 Local'[Local] = _esc )
-- 2 · Textos
{_escapa("_nome", "_esc")}
VAR _sobre = IF ( _ha = 1, "A escola escolhida", "Um exemplo · Nova Contagem" )
VAR _sub =
    _bairro & " · " & _secoes & IF ( _secoes = 1, " seção · ", " seções · " ) & FORMAT ( _val, "#,0" )
        & " votos válidos em 2026"
VAR _t18 = IF ( ISBLANK ( _m18 ), "—", FORMAT ( _m18 * 100, {PP} ) )
VAR _t22 = IF ( ISBLANK ( _m22 ), "—", FORMAT ( _m22 * 100, {PP} ) )
VAR _t26 = FORMAT ( _m26 * 100, {PP} )
VAR _c18 = IF ( _m18 > 0, "lula", IF ( _m18 < 0, "flavio", "" ) )
VAR _c22 = IF ( _m22 > 0, "lula", IF ( _m22 < 0, "flavio", "" ) )
VAR _c26 = IF ( _m26 > 0, "lula", "flavio" )
VAR _nota =
    SWITCH (
        TRUE (),
        _ha = 0, "onde o documentário começa",
        _virou = 1, "virou em 2026",
        _m26 > 0, "segue com Lula",
        "Flávio à frente"
    )
VAR _selo = IF ( _virou = 1, "<div class='selo'>virou</div>", "" )
-- 3 · Geometria
VAR _base = {{ ( 0, 70, _m18 ), ( 1, 230, _m22 ), ( 2, 390, _m26 ) }} /* lista */
VAR _yy =
    SELECTCOLUMNS (
        FILTER ( _base, NOT ISBLANK ( [Value3] ) ) /* lista */,
        "i", [Value1], "x", [Value2], "y", 34 - MAX ( -0.3, MIN ( 0.3, [Value3] ) ) / 0.3 * 28
    ) -- geometria
VAR _primeiro = MINX ( _yy, [i] ) /* lista */
VAR _d =
    CONCATENATEX (
        _yy, IF ( [i] = _primeiro, "M", "L" ) & [x] & "," & FORMAT ( [y], "0.0##", "en-US" ), " ", [i], ASC
    ) /* lista */
VAR _bolas =
    CONCATENATEX (
        _yy,
        "<circle cx='" & [x] & "' cy='" & FORMAT ( [y], "0.0##", "en-US" ) & "' r='5'/>",
        "",
        [i], ASC
    ) /* lista */
-- 4 · Marcação
RETURN
    "<div class='tela t20f'>"
        & "<div class='rot sobe'>" & _sobre & "</div>"
        & "<div class='nm sobe d1'>" & _nome & "</div>"
        & "<div class='sub sobe d2'>" & _sub & "</div>"
        & "<div class='duelo sobe d3'>"
            & "<div class='lado lula'><span class='num'>" & FORMAT ( _lula, "0.0%" ) & "</span><span class='r'>Lula</span></div>"
            & "<div class='lado flavio'><span class='num'>" & FORMAT ( _flavio, "0.0%" ) & "</span><span class='r'>Flávio</span></div>"
        & "</div>"
        & "<div class='rot cap sobe d4'>Margem de Lula, em pontos</div>"
        & "<div class='serie sobe d5'>"
            & "<div class='c c0'><span class='a'>2018</span><span class='num " & _c18 & "'>" & _t18 & "</span></div>"
            & "<div class='c c1'><span class='a'>2022</span><span class='num " & _c22 & "'>" & _t22 & "</span></div>"
            & "<div class='c c2'><span class='a'>2026</span><span class='num " & _c26 & "'>" & _t26 & "</span></div>"
            & "<svg class='linha' width='460' height='70' viewBox='0 0 460 70'>"
                & "<line class='zero' x1='20' x2='440' y1='34' y2='34'/>"
                & "<path class='traco' pathLength='1' d='" & _d & "'/>" & _bolas
            & "</svg>"
        & "</div>"
        & _selo
        & "<div class='mao'>" & _nota & "</div>"
    & "</div>"
"""


def tooltip() -> str:
    return rf"""
-- 1 · Leituras
VAR _bairro = [T20 · bairro]
VAR _secoes = [T20 · seções]
VAR _val = [T20 · válidos 2026]
VAR _lula = [T20 · Lula % 2026]
VAR _flavio = [T20 · Flávio % 2026]
VAR _m18 = [T20 · margem 2018]
VAR _m22 = [T20 · margem 2022]
VAR _m26 = [T20 · margem 2026]
VAR _virou = [T20 · virou]
-- 2 · Textos
{_escapa("_nome", "[T20 · nome do local]")}
VAR _sub =
    _bairro & " · " & _secoes & IF ( _secoes = 1, " seção · ", " seções · " ) & FORMAT ( _val, "#,0" ) & " válidos"
VAR _t18 = IF ( ISBLANK ( _m18 ), "—", FORMAT ( _m18 * 100, {PP} ) )
VAR _t22 = IF ( ISBLANK ( _m22 ), "—", FORMAT ( _m22 * 100, {PP} ) )
VAR _t26 = FORMAT ( _m26 * 100, {PP} )
VAR _nota =
    SWITCH ( TRUE (), _virou = 1, "virou em 2026", _m26 > 0, "Lula à frente", "Flávio à frente" )
VAR _selo = IF ( _virou = 1, "<div class='selo'>virou</div>", "" )
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _nome0 ),
        "<div class='tela tt20'>"
            & "<div class='nm'>" & _nome & "</div>"
            & "<div class='sub'>" & _sub & "</div>"
            & "<div class='duelo'><span class='lula'>Lula " & FORMAT ( _lula, "0.0%" ) & "</span>"
            & "<span class='flavio'>Flávio " & FORMAT ( _flavio, "0.0%" ) & "</span></div>"
            & "<div class='rot'>Margem de Lula · 2018 → 2022 → 2026</div>"
            & "<div class='serie tnum'>" & _t18 & " <i>→</i> " & _t22 & " <i>→</i> " & _t26 & " p.p.</div>"
            & _selo
            & "<div class='mao'>" & _nota & "</div>"
        & "</div>"
    )
"""


# ---------------------------------------------------------------------------------------------------- modelos fixos
CSS_RESPOSTA = (
    ".t20r .grande{position:absolute;left:-4px;top:6px;font-size:96px;font-weight:700;letter-spacing:-.045em;"
    "line-height:1;white-space:nowrap}"
    ".t20r .grande .num{font-size:96px}"
    ".t20r .rotulo{position:absolute;left:0;top:108px;font-size:18px;font-weight:600;color:var(--grafite)}"
    ".t20r .man{position:absolute;left:0;top:146px;right:0;font-size:24px}"
    ".t20r .man .num{font-size:24px;font-weight:600;letter-spacing:-.01em}"
    ".t20r .txt{position:absolute;left:0;top:216px;right:0;font-size:15px;line-height:1.4}"
)


def corpo_resposta() -> str:
    return f"<style>{CSS_RESPOSTA}</style>{{{{content}}}}"


def corpo_mapa() -> str:
    """Contorno (rabisco que se desenha, depois o creme esmaece) e os nomes de alguns bairros; {{content}} = pontos."""
    c = json.loads(CONTORNO.read_text(encoding="utf-8"))
    rotulos = "".join(
        f"<span class='bairro entra d{10 + i}' style='left:{px / 100 * MAPA_W + dx:.0f}px;"
        f"top:{py / 100 * MAPA_H + dy:.0f}px'>{n}</span>" for i, (n, px, py, dx, dy) in enumerate(BAIRROS))
    css = (
        ".t20c{pointer-events:none}"
        ".t20c svg{position:absolute;left:0;top:0}"
        ".t20c .fundo{fill:var(--creme);stroke:none;animation:uEntra 1.2s ease-out 1.2s both}"
        ".t20c .borda{fill:none;stroke:var(--tinta);stroke-width:.32;stroke-linejoin:round}"
        ".t20c .bairro{position:absolute;font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;"
        "color:var(--grafite);white-space:nowrap;background:rgba(241,235,223,.8);padding:0 3px}"
        ".t20p{pointer-events:none}"
        ".t20p .pt{position:absolute;display:block;border-radius:50%;border:1.2px solid var(--papel);"
        "pointer-events:auto;cursor:pointer;transition:transform .15s;animation:t20Brota .6s cubic-bezier(.2,.9,.3,1.3) "
        "both}"
        ".t20p .pt:hover{transform:scale(1.5);border-color:var(--tinta);z-index:3}"
        "@keyframes t20Brota{from{opacity:0;transform:scale(.3)}}"
    )
    svg = (f"<svg width='{MAPA_W}' height='{MAPA_H}' viewBox='0 0 100 100' preserveAspectRatio='none'>"
           f"{estilo.defs_rabisco('rb20', 0.5, 0.6)}"
           f"<path class='borda traco' pathLength='1' filter='url(#rb20)' d='{c['d']}'/></svg>")
    return (f"<style>{css}</style><div class='tela t20c'>{svg}</div>{{{{content}}}}"
            f"<div class='tela t20c'>{rotulos}</div>")


def corpo_escolhido() -> str:
    c = json.loads(CONTORNO.read_text(encoding="utf-8"))
    css = (
        ".t20e svg.fundo{position:fixed;left:0;top:0}"
        ".t20e svg.fundo path{fill:var(--creme);stroke:none;animation:uEntra 1.2s ease-out 1.2s both}"
        ".t20e .anel{position:absolute;width:52px;height:48px}"
        ".t20e .anel path{fill:none;stroke:var(--tinta);stroke-width:2.4;stroke-linecap:round;animation-delay:2.6s}"
        ".t20e .nome{position:absolute;max-width:210px;font-size:14px;font-weight:600;line-height:1.25;"
        "color:var(--tinta);background:rgba(241,235,223,.85);padding:2px 6px;animation-delay:2.8s!important}"
        ".t20e .nome.dir{transform:translateX(-100%)}"
        ".t20e .nome .mao{display:block;font-size:24px;font-weight:600;color:var(--vermelho-escuro);margin-top:2px}"
        ".t20e .sem{position:absolute;left:0;top:0;font-size:15px;color:var(--grafite)}"
    )
    fundo = (f"<div class='tela t20e'><svg class='fundo' width='{MAPA_W}' height='{MAPA_H}' viewBox='0 0 100 100' "
             f"preserveAspectRatio='none'><path d='{c['d']}'/></svg></div>")
    return (f"<style>{css}</style>{fundo}<svg width='0' height='0' style='position:absolute'>"
            f"{estilo.defs_rabisco('rbe', 1.4)}</svg>{{{{content}}}}")


def corpo_ficha() -> str:
    alfinete = estilo.imagem_b64("docs/midia/arte/dossie/alfinete-tinta.png", 70)
    orelha = estilo.imagem_b64("docs/midia/arte/dossie/orelha-tinta.png", 70)
    css = (
        ".t20papel{position:fixed;left:6px;top:22px;right:6px;bottom:6px;background:var(--branco);"
        "border:1.5px solid var(--areia);box-shadow:0 10px 24px rgba(28,25,21,.12);transform:rotate(-.6deg);"
        "clip-path:polygon(0 0,100% 0,100% calc(100% - 52px),calc(100% - 52px) 100%,0 100%)}"
        ".t20alf{position:fixed;left:240px;top:-4px;width:56px;z-index:3;pointer-events:none}"
        ".t20ore{position:fixed;right:4px;bottom:2px;width:60px;z-index:3;pointer-events:none;opacity:.9}"
        ".t20f{left:40px;top:58px;right:34px;bottom:30px;position:fixed}"
        ".t20f .rot{position:absolute;left:0;top:0}"
        ".t20f .nm{position:absolute;left:0;top:24px;right:70px;font-size:26px;font-weight:700;line-height:1.15}"
        ".t20f .sub{position:absolute;left:0;top:90px;right:0;font-size:15px;color:var(--grafite)}"
        ".t20f .duelo{position:absolute;left:0;top:128px;right:0;height:70px}"
        ".t20f .duelo .lado{position:absolute;top:0;display:flex;flex-direction:column}"
        ".t20f .duelo .lado .num{font-size:44px}.t20f .duelo .lado .r{font-size:15px;font-weight:600;margin-top:4px}"
        ".t20f .duelo .lula{left:0}.t20f .duelo .flavio{left:190px}"
        ".t20f .duelo .ano{position:absolute;left:380px;top:16px;font-size:15px;color:var(--cinza)}"
        ".t20f .cap{position:absolute;left:0;top:226px}"
        ".t20f .serie{position:absolute;left:0;top:252px;right:0;height:160px}"
        ".t20f .serie .c{position:absolute;top:0;width:150px;display:flex;flex-direction:column;align-items:center}"
        ".t20f .serie .c0{left:-5px}.t20f .serie .c1{left:155px}.t20f .serie .c2{left:315px}"
        ".t20f .serie .a{font-size:13px;font-weight:600;letter-spacing:.12em;color:var(--cinza)}"
        ".t20f .serie .num{font-size:38px;margin-top:4px}"
        ".t20f .serie .linha{position:absolute;left:0;top:84px}"
        ".t20f .serie .zero{stroke:var(--areia);stroke-width:1;stroke-dasharray:3 4}"
        ".t20f .serie path{fill:none;stroke:var(--grafite);stroke-width:2.2;stroke-linejoin:round}"
        ".t20f .serie circle{fill:var(--tinta)}"
        ".t20f .selo{position:absolute;right:6px;top:136px;transform:rotate(8deg);border:3px solid var(--tinta);"
        "outline:1px solid var(--tinta);outline-offset:3px;padding:5px 12px;font-weight:700;font-size:16px;"
        "letter-spacing:.18em;text-transform:uppercase;color:var(--tinta);animation:uEntra .3s ease-out 2s both}"
        ".t20f .mao{position:absolute;left:0;bottom:0;font-size:30px;color:var(--vermelho-escuro);transform:rotate(-2deg)}"
    )
    return (f"<style>{css}</style><div class='t20papel entra'></div>"
            f"<img class='t20alf entra d3' alt='' src='{alfinete}'/><img class='t20ore' alt='' src='{orelha}'/>"
            f"{{{{content}}}}")


def corpo_quedas() -> str:
    css = (
        ".t20h .rot{position:absolute;left:0;top:0;width:318px;line-height:1.5}"
        ".t20h .linha{position:absolute;left:0;right:0;top:" + str(QUEDAS_TOPO - 8) + "px;"
        "border-top:1.5px solid var(--grafite)}"
        ".t20q{pointer-events:none}"
        ".t20q .ln{position:absolute;left:0;width:318px;height:" + str(QUEDAS_H - 4) + "px;pointer-events:auto;"
        "cursor:pointer;border-bottom:1px solid var(--creme);transition:background .15s,opacity .15s}"
        ".t20q .ln:hover{background:var(--creme)}"
        "#htmlContent:has(.ln:hover) .ln:not(:hover){opacity:.55}"
        ".t20q .p{position:absolute;left:2px;top:4px;font-size:22px;font-weight:700;color:var(--cinza)}"
        ".t20q .nm{position:absolute;left:30px;top:6px;right:4px;font-size:15px;font-weight:600;line-height:1.25;"
        "display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
        ".t20q .sb{position:absolute;left:30px;top:50px;font-size:13px;color:var(--cinza);white-space:nowrap;"
        "max-width:132px;overflow:hidden;text-overflow:ellipsis}"
        ".t20q .v{position:absolute;right:58px;top:47px;font-size:17px;font-weight:700}"
        ".t20q .selo{position:absolute;right:2px;top:49px;font-size:11px;font-weight:700;letter-spacing:.1em;"
        "text-transform:uppercase;border:1.5px solid var(--tinta);padding:1px 4px;transform:rotate(-4deg)}"
    )
    return (f"<style>{css}</style><div class='tela t20h'><div class='rot sobe'>As 5 maiores quedas da margem de Lula, "
            f"2022 → 2026</div><div class='linha entra'></div></div>{{{{content}}}}")


def corpo_como() -> str:
    escola = estilo.imagem_b64("docs/midia/arte/icones/escola-tinta.png", 110)
    css = (
        ".t20x img{position:absolute;right:0;top:0;width:80px;opacity:.9}"
        ".t20x .rot{position:absolute;left:0;top:14px}"
        ".t20x .txt{position:absolute;left:0;top:58px;right:0;font-size:15px;line-height:1.45}"
        ".t20x .leg{position:absolute;left:0;top:200px;right:0;font-size:14px;line-height:1.75;color:var(--grafite)}"
        ".t20x .leg i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:8px;vertical-align:-1px}"
        ".t20x .leg .a{border:2px solid var(--tinta);background:none}"
        ".t20x .leg .p{font-size:13px;color:var(--cinza)}"
    )
    return (f"<style>{css}</style><div class='tela t20x'><img class='entra' alt='' src='{escola}'/>"
            f"<div class='rot sobe'>Como explorar</div>"
            f"<div class='txt sobe d2'>Passe o mouse num ponto: um post-it traz os votos da escola. Clique num ponto "
            f"ou numa linha da lista para levar a escola à ficha; o filtro do topo procura pelo nome.</div>"
            f"<div class='leg entra d4'><div><i style='background:{FAIXAS[-1][1]}'></i>Lula à frente&nbsp;&nbsp;&nbsp;"
            f"<i style='background:{FAIXAS[1][1]}'></i>Flávio à frente</div>"
            f"<div class='p'>cor forte = vantagem maior · tamanho = votos</div>"
            f"<div><i class='a'></i>a escola da ficha</div></div></div>{{{{content}}}}")


CSS_TOOLTIP = (
    ".tt20{background:var(--branco);padding:30px 24px 14px 24px;border:1.5px solid var(--areia)}"
    ".tt20 .nm{font-size:20px;font-weight:700;line-height:1.2;padding-right:56px}"
    ".tt20 .sub{margin-top:5px;font-size:14px;color:var(--grafite)}"
    ".tt20 .duelo{margin-top:12px;display:flex;gap:22px;font-size:22px;font-weight:700}"
    ".tt20 .rot{margin-top:14px;font-size:11px}"
    ".tt20 .serie{margin-top:4px;font-size:19px;font-weight:600}"
    ".tt20 .serie i{font-style:normal;color:var(--cinza);margin:0 4px}"
    ".tt20 .selo{position:absolute;right:20px;top:112px;transform:rotate(7deg);border:2.5px solid var(--tinta);"
    "outline:1px solid var(--tinta);outline-offset:2px;padding:3px 9px;font-weight:700;font-size:13px;"
    "letter-spacing:.16em;text-transform:uppercase}"
    ".tt20 .mao{position:absolute;right:22px;bottom:8px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
    ".tt20a{position:fixed;right:34px;top:-6px;width:40px;z-index:2;pointer-events:none}"
)


def corpo_tooltip() -> str:
    alfinete = estilo.imagem_b64("docs/midia/arte/dossie/alfinete-tinta.png", 60)
    return f"<style>{CSS_TOOLTIP}</style>{{{{content}}}}<img class='tt20a' alt='' src='{alfinete}'/>"


def main() -> int:
    CONTORNO.parent.mkdir(parents=True, exist_ok=True)
    CONTORNO.write_text(json.dumps(contorno(), ensure_ascii=False) + "\n", encoding="utf-8")
    medidas()
    print(f"T20: medidas de desenho em {DAX} · contorno {CONTORNO.name} ({CONTORNO.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
