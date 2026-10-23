# -*- coding: utf-8 -*-
"""desenho_t19 — tela 19 · Explorador (dono: tela 19). Gera:

  pbi/dax/T19 Explorador/Desenho/*.dax   medidas de desenho (HTML e ALT): só leem as contas de T19 Explorador\\Contas
  pbi/spec/t19_dispersao.json            Deneb (Vega 6, canvas): os pontos da dispersão, o retângulo de seleção e o
                                         filtro cruzado (pbiCrossFilterApply)

e expõe para paginas/t19_explorador.py os modelos fixos (bodyTemplate): o cabeçalho da lista, o fundo da dispersão
(eixos, grade, legendas e dicas em Sora, desenhados em HTML atrás do Deneb, com a MESMA geometria do spec) e o papel do
dossiê. A pílula do filtro do recorte (T19 · Filtro · pílula · HTML) usa a folha da pílula da casca (CSS_PILULA).

    python -I -X utf8 pbi/scripts/desenho_t19.py
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
DAX = PBI / "dax" / "T19 Explorador" / "Desenho"
SPEC = PBI / "spec" / "t19_dispersao.json"
PASTA = r"T19 Explorador\Desenho"

# ---------------------------------------------------------------------------------------------------- geometria
# sem a faixa de seis segmentações (23/10/2026: o filtro virou um acordeão na pílula do canto), a lista e a dispersão
# sobem 80 px e crescem: 16 linhas em vez de 14 e a dispersão 82 px mais alta
LISTA_LINHAS = 16
LISTA_CAB = 36            # altura do cabeçalho da lista
LISTA_H = 44              # altura de cada linha
# colunas da lista (x da esquerda de cada coluna, em px dentro do visual de 700)
COL = {"nome": 14, "lula": 262, "flavio": 334, "serie": 430, "var": 584, "virou": 648}
SERIE_W, SERIE_H = 136, 30

DISP_W, DISP_H = 880, 860
PL, PR, PT, PB = 84, 856, 112, 758           # caixa do gráfico dentro do visual
RENDA = (250.0, 5000.0)                       # eixo x, escala log (R$/mês)
VAR = (-0.48, 0.16)                           # eixo y, variação da margem (fração)
TICKS_X = [(300, "R$ 300"), (500, "R$ 500"), (1000, "R$ 1 mil"), (2000, "R$ 2 mil"), (4000, "R$ 4 mil")]
TICKS_Y = [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1]
# margem 2026 → cor (as mesmas paradas do mapa de margem do pipeline: azul ← areia → vermelho)
COR_DOMINIO = [-0.6, -0.3, -0.12, 0.0, 0.12, 0.3, 0.6]
COR_FAIXA = ["azul_escuro", "azul", "azul_claro", "areia", "rosa", "vermelho", "vermelho_escuro"]


def px_x(renda: float) -> float:
    a, b = math.log(RENDA[0]), math.log(RENDA[1])
    return PL + (math.log(renda) - a) / (b - a) * (PR - PL)


def px_y(v: float) -> float:
    return PB - (v - VAR[0]) / (VAR[1] - VAR[0]) * (PB - PT)


# ---------------------------------------------------------------------------------------------------- DAX
def gravar(nome: str, descricao: str, expressao: str, formato: str = "texto") -> None:
    destino = DAX / f"{nome}.dax"
    destino.parent.mkdir(parents=True, exist_ok=True)
    texto = (f"/*\n@pasta: {PASTA}\n@formato: {formato}\n@descricao: {descricao}\n*/\n"
             + expressao.strip("\n") + "\n")
    if "\t" in texto:
        raise SystemExit(f"tab em {nome}")
    if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
        destino.write_text(texto, encoding="utf-8")


ESCAPA = """
VAR _nome0 = {fonte}
VAR _nome1 = SUBSTITUTE ( _nome0, "&", "&amp;" )
VAR _nome2 = SUBSTITUTE ( SUBSTITUTE ( _nome1, "<", "&lt;" ), ">", "&gt;" )
VAR _nome = SUBSTITUTE ( SUBSTITUTE ( _nome2, \"\"\"\", "&quot;" ), "'", "&#39;" )"""


PILULA_MAX = 40          # caracteres que cabem na pílula (424 px, Sora 16 semibold: ~8 px por letra); acima, "N filtros"
FUNIL = ("<span class='fu'><svg width='16' height='16' viewBox='0 0 16 16'><path d='M2 3h12l-4.6 5.4V13l-2.8-1.4V8.4z' "
         "fill='none' stroke='currentColor' stroke-width='1.4' stroke-linejoin='round'/></svg><i></i></span>")
SETA = ("<svg class='sv' width='12' height='12' viewBox='0 0 12 12'><path d='M3 4.5l3 3 3-3' fill='none' "
        "stroke='currentColor' stroke-width='1.4' stroke-linecap='round'/></svg>")


def _quebrado(texto: str, largura: int = 96) -> str:
    """Literal DAX longo em pedaços de até `largura` (cortados num espaço), unidos por & em linhas próprias."""
    pedacos, atual = [], ""
    for palavra in texto.split(" "):
        if atual and len(atual) + 1 + len(palavra) > largura:
            pedacos.append(atual + " ")
            atual = palavra
        else:
            atual = f"{atual} {palavra}" if atual else palavra
    pedacos.append(atual)
    return '"\n        & "'.join(pedacos)


def medidas() -> None:
    cor_css = {"lula": "var(--vermelho)", "flavio": "var(--azul)"}
    # --- pílula do filtro do recorte (o mesmo desenho da pílula de UF da casca: Casca · filtro · pílula · HTML)
    gravar("T19 · Filtro · pílula · HTML", "O botão fechado do filtro do recorte (a pílula, na caixa do filtro da "
           "casca): 'Todos os municípios' sem escolha; com escolha, o recorte em poucas palavras ('Nordeste · até 10 "
           "mil hab.') ou, quando não cabe, 'N filtros'; o funil ganha o ponto vermelho. O clique abre o acordeão "
           "(VizuFilter alto, marcador T19_FILTRO_ABRE_01). Recebe só o próprio filtro (a lista e a dispersão não "
           "mexem nela).", f"""
-- 1 · Leituras
VAR _n = [T19 · filtro · escolhas]
VAR _uso = [T19 · filtro em uso]
-- 2 · Textos
VAR _txt0 =
    SWITCH (
        TRUE (),
        _n = 0, "Todos os municípios",
        _n > 1 && LEN ( _uso ) > {PILULA_MAX}, FORMAT ( _n, "#,0" ) & " filtros",
        _uso
    )
VAR _txt1 = SUBSTITUTE ( SUBSTITUTE ( _txt0, "&", "&amp;" ), "<", "&lt;" )
VAR _txt = SUBSTITUTE ( SUBSTITUTE ( _txt1, ">", "&gt;" ), "'", "&#39;" )
-- 4 · Marcação
RETURN
    "<div class='tela pl" & IF ( _n > 0, " ativo", "" ) & "'>"
        & "{_quebrado(FUNIL)}"
        & "<b>" & _txt & "</b>"
        & "{_quebrado(SETA)}"
    & "</div>"
""")
    gravar("T19 · Filtro · ALT", "Texto alternativo da pílula do filtro do recorte: o recorte em uso e o que o "
           "acordeão oferece.", r"""
-- 1 · Leituras
VAR _n = [T19 · filtro · escolhas]
VAR _uso = [T19 · filtro em uso]
-- 2 · Textos
RETURN
    "Filtro do recorte: " & IF ( _n = 0, "todos os municípios", LEFT ( _uso, 150 ) )
        & ". Abre a lista de região, estado, tamanho, renda, virada e cidade."
""")
    # --- resumo do recorte (contadores)
    gravar("T19 · Resumo · HTML", "Faixa do recorte acima da lista: os filtros em uso e quantos municípios, com Lula à "
           "frente, com Flávio à frente e que viraram, com a barra da proporção. Só lê as contas de T19.", r"""
-- 1 · Leituras
VAR _recorte = [T19 · recorte em uso]
VAR _n = [T19 · municípios no recorte]
VAR _lula = [T19 · municípios com Lula à frente]
VAR _flavio = [T19 · municípios com Flávio à frente]
VAR _viraram = [T19 · municípios que viraram]
-- 2 · Textos
VAR _rec0 = SUBSTITUTE ( SUBSTITUTE ( _recorte, "&", "&amp;" ), "<", "&lt;" )
VAR _txtN = FORMAT ( _n, "#,0" )
VAR _txtLula = FORMAT ( _lula, "#,0" )
VAR _txtFlavio = FORMAT ( _flavio, "#,0" )
VAR _txtViraram = FORMAT ( _viraram, "#,0" )
VAR _rotN = IF ( _n = 1, "município no recorte", "municípios no recorte" )
VAR _rotViraram = IF ( _viraram = 1, "virou de Lula para Flávio", "viraram de Lula para Flávio" )
-- 3 · Geometria
VAR _total = _lula + _flavio
VAR _largLula = IF ( _total > 0, DIVIDE ( _lula, _total ) * 100, 0 ) -- geometria
VAR _largFlavio = IF ( _total > 0, DIVIDE ( _flavio, _total ) * 100, 0 ) -- geometria
-- 4 · Marcação
RETURN
    "<div class='tela t19r'>"
        & "<div class='sob sobe'>Recorte · " & _rec0 & "</div>"
        & "<div class='st sobe d1'><span class='num'>" & _txtN & "</span><span class='r'>" & _rotN & "</span></div>"
        & "<div class='st sobe d2 lula'><span class='num'>" & _txtLula & "</span><span class='r'>com Lula à frente</span></div>"
        & "<div class='st sobe d3 flavio'><span class='num'>" & _txtFlavio & "</span><span class='r'>com Flávio à frente</span></div>"
        & "<div class='st sobe d4'><span class='num'>" & _txtViraram & "</span><span class='r'>" & _rotViraram & "</span></div>"
        & "<div class='br'><i class='l barra-x' style='width:" & FORMAT ( _largLula, "0.0##", "en-US" ) & "%'></i>"
        & "<i class='f barra-x-dir' style='width:" & FORMAT ( _largFlavio, "0.0##", "en-US" ) & "%'></i></div>"
    & "</div>"
""")
    gravar("T19 · Resumo · ALT", "Texto alternativo da faixa do recorte.", r"""
-- 1 · Leituras
VAR _recorte = [T19 · recorte em uso]
VAR _n = [T19 · municípios no recorte]
VAR _lula = [T19 · municípios com Lula à frente]
VAR _flavio = [T19 · municípios com Flávio à frente]
VAR _viraram = [T19 · municípios que viraram]
-- 2 · Textos
RETURN
    "Recorte: " & _recorte & ". " & FORMAT ( _n, "#,0" ) & IF ( _n = 1, " município", " municípios" )
        & "; Lula à frente em " & FORMAT ( _lula, "#,0" ) & ", Flávio em " & FORMAT ( _flavio, "#,0" ) & "; "
        & IF ( _viraram = 0, "nenhum virou", FORMAT ( _viraram, "#,0" ) & IF ( _viraram = 1, " virou", " viraram" ) )
        & " de Lula para Flávio."
""")
    # --- linha da lista
    xs = [round(i * (SERIE_W - 8) / 5 + 4, 1) for i in range(6)]
    pontos = ", ".join(f"( {i}, {x}, _m{a} )" for i, (x, a) in enumerate(zip(xs, ("06", "10", "14", "18", "22", "26"))))
    meio = SERIE_H / 2
    gravar("T19 · Lista · HTML", "Uma linha da lista do Explorador (granularidade: Município[Rótulo]; o visual mostra "
           f"os {LISTA_LINHAS} com mais votos válidos do recorte): nome, Lula e Flávio em 2026, a minilinha da margem "
           "2006–2026, a mudança "
           "2022 → 2026 e o selo de quem virou. Posição pela conta da posição na lista.", f"""
-- 1 · Leituras
VAR _pos = [T19 · posição na lista]
VAR _lula = [T19 · Lula % 2026]
VAR _flavio = [T19 · Flávio % 2026]
VAR _var = [T19 · variação da margem]
VAR _virou = [T19 · virou]
VAR _m06 = [T19 · margem 2006]
VAR _m10 = [T19 · margem 2010]
VAR _m14 = [T19 · margem 2014]
VAR _m18 = [T19 · margem 2018]
VAR _m22 = [T19 · margem 2022]
VAR _m26 = [T19 · margem 2026]
-- 2 · Textos
{ESCAPA.format(fonte="[T19 · município]").strip()}
VAR _txtLula = FORMAT ( _lula, "0.0%" )
VAR _txtFlavio = FORMAT ( _flavio, "0.0%" )
VAR _txtVar = IF ( ISBLANK ( _var ), "—", FORMAT ( _var * 100, "+0.0;−0.0;0.0" ) )
VAR _clsVar = IF ( _var < 0, "flavio", IF ( _var > 0, "lula", "" ) )
VAR _clsFim = IF ( _m26 < 0, "f", "l" )
VAR _selo = IF ( _virou = 1, "<span class='selo'>virou</span>", "" )
VAR _atraso = "d" & MIN ( _pos, 16 )
-- 3 · Geometria
VAR _y = {LISTA_CAB} + ( _pos - 1 ) * {LISTA_H} -- geometria
VAR _base = {{ {pontos} }} /* lista */
VAR _pts =
    FILTER ( /* lista */
        SELECTCOLUMNS (
            _base,
            "i", [Value1],
            "x", [Value2],
            "y", IF ( ISBLANK ( [Value3] ), BLANK (), {meio} - MAX ( -0.6, MIN ( 0.6, [Value3] ) ) / 0.6 * {meio - 2} )
        ),
        NOT ISBLANK ( [y] )
    ) -- geometria
VAR _primeiro = MINX ( _pts, [i] ) /* lista */
VAR _d =
    CONCATENATEX (
        _pts,
        IF ( [i] = _primeiro, "M", "L" ) & FORMAT ( [x], "0.0##", "en-US" ) & "," & FORMAT ( [y], "0.0##", "en-US" ),
        " ",
        [i], ASC
    ) /* lista */
VAR _yFim = MAXX ( FILTER ( _pts, [i] = 5 ), [y] ) /* lista */
VAR _ponto =
    IF (
        NOT ISBLANK ( _yFim ),
        "<circle class='" & _clsFim & "' cx='{xs[-1]}' cy='" & FORMAT ( _yFim, "0.0##", "en-US" ) & "' r='3.6'/>"
    )
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _pos ),
        "<div class='tela t19l'><div class='ln sobe " & _atraso & "' style='top:" & _y & "px'>"
            & "<span class='c-nome' title='" & _nome & "'>" & _nome & "</span>"
            & "<span class='c-l lula tnum'>" & _txtLula & "</span>"
            & "<span class='c-f flavio tnum'>" & _txtFlavio & "</span>"
            & "<svg class='c-s' width='{SERIE_W}' height='{SERIE_H}' viewBox='0 0 {SERIE_W} {SERIE_H}'>"
                & "<line class='zero' x1='0' x2='{SERIE_W}' y1='{meio}' y2='{meio}'/>"
                & "<path class='traco-rapido' pathLength='1' d='" & _d & "'/>" & _ponto
            & "</svg>"
            & "<span class='c-v tnum " & _clsVar & "'>" & _txtVar & "</span>"
            & "<span class='c-x'>" & _selo & "</span>"
        & "</div></div>"
    )
""")
    gravar("T19 · Lista · ALT", "Texto alternativo da lista do Explorador.", r"""
-- 1 · Leituras
VAR _recorte = [T19 · recorte em uso]
VAR _n = [T19 · municípios na lista]
-- 2 · Textos
RETURN
    IF ( _n = 1, "Lista com o município do recorte (", "Lista dos " & _n & " municípios com mais votos válidos em "
        & "2026 no recorte (" ) & _recorte & "): Lula e Flávio em 2026, a margem do PT de 2006 a 2026 e a mudança de "
        & "2022 para 2026. "
        & "Passe o mouse numa linha para o dossiê; clique para destacar o ponto na dispersão."
""")
    # --- manchete da dispersão (conta do recorte)
    gravar("T19 · Dispersão · HTML", "Manchete da dispersão, no fundo HTML atrás dos pontos: em quantos municípios do "
           "recorte Lula perdeu margem de 2022 para 2026.", r"""
-- 1 · Leituras
VAR _n = [T19 · municípios no recorte]
VAR _perdeu = [T19 · municípios em que Lula perdeu margem]
VAR _com = [T19 · municípios com as duas eleições]
-- 2 · Textos
VAR _txtPerdeu = FORMAT ( _perdeu, "#,0" )
VAR _txtCom = FORMAT ( _com, "#,0" )
VAR _frase =
    SWITCH (
        TRUE (),
        _n = 0, "Nenhum município neste recorte: mude o filtro no canto de cima",
        _com = 0, "Sem 2022 para comparar neste recorte",
        _com = 1,
            IF ( _perdeu = 1, "Neste município, Lula perdeu margem", "Neste município, Lula não perdeu margem" ),
        "Lula perdeu margem em <b class='num'>" & _txtPerdeu & "</b> dos <b class='num'>" & _txtCom
            & "</b> municípios do recorte"
    )
-- 4 · Marcação
RETURN
    "<div class='tela t19m'><div class='man sobe d2'>" & _frase & "</div></div>"
""")
    gravar("T19 · Dispersão · ALT", "Texto alternativo da dispersão (renda × mudança da margem).", r"""
-- 1 · Leituras
VAR _perdeu = [T19 · municípios em que Lula perdeu margem]
VAR _com = [T19 · municípios com as duas eleições]
VAR _recorte = [T19 · recorte em uso]
-- 2 · Textos
RETURN
    "Dispersão: um ponto por município, renda por pessoa no eixo horizontal e quanto a margem de Lula mudou de 2022 "
        & "para 2026 no vertical. Recorte " & _recorte & ": Lula perdeu margem em " & FORMAT ( _perdeu, "#,0" )
        & " de " & FORMAT ( _com, "#,0" ) & ". Arraste um retângulo para filtrar a lista."
""")
    # --- dossiê (tooltip)
    gravar("T19 · Dossiê · HTML", "Dossiê do município (página de tooltip ttT19Municipio, da lista, da dispersão e "
           "do mapa da tela 21): região, população e renda, a margem do PT nas seis eleições num gráfico de linha, em "
           "quantas o PT ficou à frente, a abstenção de 2026 e o selo de quem virou.", dossie())
    gravar("T19 · Dossiê · ALT", "Texto alternativo do dossiê do município.", r"""
-- 1 · Leituras
VAR _nome = [T19 · município]
VAR _m06 = [T19 · margem 2006]
VAR _m26 = [T19 · margem 2026]
VAR _frente = [T19 · eleições com o PT à frente]
VAR _com = [T19 · eleições com voto]
-- 2 · Textos
VAR _ini = IF ( ISBLANK ( _m06 ), "", " de " & FORMAT ( _m06 * 100, "+0.0;−0.0;0.0" ) & " p.p. em 2006" )
RETURN
    IF (
        NOT ISBLANK ( _nome ),
        _nome & ": margem do PT" & _ini & " a " & FORMAT ( _m26 * 100, "+0.0;−0.0;0.0" ) & " p.p. em 2026; PT à "
            & "frente em " & _frente & " de " & _com & IF ( _com = 1, " eleição.", " eleições." )
    )
""")


def dossie() -> str:
    anos = ("06", "10", "14", "18", "22", "26")
    xs = [26 + i * 72 for i in range(6)]                       # 6 anos em 360 px
    tabela = ", ".join(f"( {i}, {x}, 20{a}, _m{a} )" for i, (x, a) in enumerate(zip(xs, anos)))
    leituras = "\n".join(f"VAR _m{a} = [T19 · margem 20{a}]" for a in anos)
    return f"""
-- 1 · Leituras
VAR _regiao = [T19 · região do município]
VAR _pop = [T19 · população]
VAR _renda = [T19 · renda]
VAR _abst = [T19 · abstenção 2026]
VAR _frente = [T19 · eleições com o PT à frente]
VAR _com = [T19 · eleições com voto]
VAR _virou = [T19 · virou]
{leituras}
-- 2 · Textos
{ESCAPA.format(fonte="[T19 · município]").strip()}
VAR _txtPop = FORMAT ( _pop, "#,0" ) & " habitantes"
VAR _txtRenda = IF ( ISBLANK ( _renda ), "", " · renda de R$ " & FORMAT ( _renda, "#,0" ) & " por pessoa" )
VAR _txtAbst = FORMAT ( _abst, "0.0%" )
VAR _txtFrente =
    SWITCH (
        TRUE (),
        _frente = _com, "PT à frente em todas as " & _com & " eleições",
        _frente = 0, "PT atrás em todas as " & _com & " eleições",
        "PT à frente em " & _frente & " de " & _com & IF ( _com = 1, " eleição", " eleições" )
    )
VAR _nota =
    SWITCH (
        TRUE (),
        _virou = 1, "virou em 2026",
        _m26 > 0 && _m22 > 0, "segue com Lula",
        _m26 < 0 && _m22 < 0, "segue com o PL",
        "lado incerto"
    )
VAR _selo = IF ( _virou = 1, "<div class='selo'>virou</div>", "" )
-- 3 · Geometria
VAR _base = {{ {tabela} }} /* lista */
VAR _serie =
    FILTER ( /* lista */
        SELECTCOLUMNS ( _base, "i", [Value1], "x", [Value2], "ano", [Value3], "m", [Value4] ),
        NOT ISBLANK ( [m] )
    ) -- geometria
VAR _maior = MAXX ( _serie, ABS ( [m] ) ) /* geometria */
VAR _escala = MAX ( 0.2, CEILING ( _maior * 10, 1 ) / 10 ) -- geometria
VAR _pts =
    ADDCOLUMNS ( _serie, "y", 70 - [m] / _escala * 52 ) -- geometria
VAR _primeiro = MINX ( _pts, [i] ) /* lista */
VAR _d =
    CONCATENATEX (
        _pts,
        IF ( [i] = _primeiro, "M", "L" ) & [x] & "," & FORMAT ( [y], "0.0##", "en-US" ),
        " ",
        [i], ASC
    ) /* lista */
VAR _marcas =
    CONCATENATEX (
        _pts,
        "<circle class='" & IF ( [m] > 0, "l", "f" ) & "' cx='" & [x] & "' cy='" & FORMAT ( [y], "0.0##", "en-US" )
            & "' r='4.6'/>"
            & "<text class='v " & IF ( [m] > 0, "l", "f" ) & "' x='" & [x] & "' y='"
            & FORMAT ( IF ( [m] > 0, [y] - 10, [y] + 19 ), "0.0##", "en-US" ) & "'>"
            & FORMAT ( [m] * 100, "+0.0;−0.0;0.0" ) & "</text>",
        "",
        [i], ASC
    ) /* lista */
VAR _anos =
    CONCATENATEX ( _serie, "<text class='a' x='" & [x] & "' y='150'>" & [ano] & "</text>", "", [i], ASC ) /* lista */
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _nome0 ),
        "<div class='tela tt19'>"
            & "<div class='nm'>" & _nome & "</div>"
            & "<div class='sub'>" & _regiao & " · " & _txtPop & _txtRenda & "</div>"
            & "<div class='rot cap'>Margem do PT, em pontos · 2006 → 2026</div>"
            & "<svg class='serie' width='410' height='158' viewBox='0 0 410 158'>"
                & "<line class='zero' x1='6' x2='404' y1='70' y2='70'/>"
                & "<text class='ze' x='404' y='66'>empate</text>"
                & "<path class='traco-rapido' pathLength='1' d='" & _d & "'/>"
                & _marcas & _anos
            & "</svg>"
            & "<div class='pe'><span>" & _txtFrente & "</span><span class='ab'>" & _txtAbst
            & " faltaram em 2026</span></div>"
            & _selo
            & "<div class='mao'>" & _nota & "</div>"
        & "</div>"
    )
"""


# ---------------------------------------------------------------------------------------------------- Deneb
def spec() -> dict:
    c = estilo.COR
    w, h = DISP_W, DISP_H
    fx = lambda v: {"signal": f"{v}*width/{w}"}  # noqa: E731
    fy = lambda v: {"signal": f"{v}*height/{h}"}  # noqa: E731
    return {
        "$schema": "https://vega.github.io/schema/vega/v6.json",
        "description": "T19 · dispersão: renda (log) × mudança da margem de Lula 2022 → 2026, um ponto por município; "
                       "arrastar desenha um retângulo que filtra a página (pbiCrossFilterApply); clique num ponto "
                       "filtra só ele; clique no vazio limpa. Eixos, textos e legenda no HTML atrás (mesma geometria).",
        "width": {"signal": "pbiContainerWidth"}, "height": {"signal": "pbiContainerHeight"}, "padding": 0,
        "autosize": {"type": "none", "contains": "padding"}, "background": None, "config": {"view": {"stroke": None}},
        "signals": [
            {"name": "estatico", "init": "!(windowSize()[0] > 0)"},
            {"name": "fim", "value": 1900},
            {"name": "t0", "init": "now()"},
            {"name": "t", "init": "estatico ? fim : 0",
             "on": [{"events": "timer{16}", "update": "estatico ? fim : min(now() - t0, fim)"}]},
            {"name": "entrada", "update": "clamp(t / 1500, 0, 1)"},
            {"name": "p0", "value": [0, 0], "on": [{"events": "mousedown", "update": "xy()"}]},
            {"name": "p1", "value": [0, 0],
             "on": [{"events": "mousedown", "update": "xy()"},
                    {"events": "[mousedown, window:mouseup] > window:mousemove", "update": "xy()"}]},
            {"name": "arrastando", "value": False,
             "on": [{"events": "mousedown", "update": "true"}, {"events": "window:mouseup", "update": "false"}]},
            {"name": "grande_o_bastante",
             "update": "abs(p1[0] - p0[0]) > 6 && abs(p1[1] - p0[1]) > 6"},
            {"name": "ret", "value": None,
             "on": [{"events": "[mousedown, window:mouseup] > window:mousemove",
                     "update": "grande_o_bastante ? {x0: min(p0[0], p1[0]), x1: max(p0[0], p1[0]), "
                               "y0: min(p0[1], p1[1]), y1: max(p0[1], p1[1])} : null"},
                    {"events": "mousedown", "update": "null"}]},
            {"name": "lr0", "update": "ret ? invert('x', ret.x0) : 0"},
            {"name": "lr1", "update": "ret ? invert('x', ret.x1) : 0"},
            {"name": "lv0", "update": "ret ? invert('y', ret.y1) : 0"},
            {"name": "lv1", "update": "ret ? invert('y', ret.y0) : 0"},
            {"name": "arrastou", "value": False,
             "on": [{"events": "window:mouseup", "update": "ret != null"}]},
            {"name": "estado", "value": "neutro",
             "on": [
                 {"events": "window:mouseup",
                  "update": "ret == null ? estado : (length(data('laco')) > 2500 ? 'grande' : "
                            "(length(data('laco')) == 0 ? 'vazio' : [pbiCrossFilterApply(event, "
                            "'datum.renda >= ' + lr0 + ' && datum.renda <= ' + lr1 + ' && datum.var >= ' + lv0 + "
                            "' && datum.var <= ' + lv1, {limit: 2500}), 'laco'][1]))"},
                 {"events": "@pontos:click", "filter": ["!event.ctrlKey"],
                  "update": "arrastou ? estado : [pbiCrossFilterApply(event), 'ponto'][1]"},
                 {"events": "click",
                  "update": "arrastou || (event.item && event.item.mark && event.item.mark.name == 'pontos') ? "
                            "estado : [pbiCrossFilterClear(), 'neutro'][1]"}]},
            {"name": "ret_fixo", "value": None,
             "on": [{"events": "window:mouseup", "update": "ret != null ? ret : ret_fixo"},
                    {"events": "click",
                     "update": "arrastou ? ret_fixo : null"}]},
            {"name": "sobre", "value": None,
             "on": [{"events": "@pontos:mouseover", "update": "datum"},
                    {"events": "@pontos:mouseout", "update": "null"}]},
        ],
        "data": [
            {"name": "dataset"},
            {"name": "pts", "source": "dataset",
             "transform": [
                 {"type": "filter", "expr": "isValid(datum.renda) && datum.renda > 0 && isValid(datum['var'])"},
                 {"type": "collect", "sort": {"field": "val", "order": "descending"}}]},
            {"name": "laco", "source": "pts",
             "transform": [{"type": "filter",
                            "expr": "ret != null && datum.renda >= lr0 && datum.renda <= lr1 && "
                                    "datum['var'] >= lv0 && datum['var'] <= lv1"}]},
        ],
        "scales": [
            {"name": "x", "type": "log", "domain": list(RENDA), "range": [fx(PL), fx(PR)], "clamp": True},
            {"name": "y", "type": "linear", "domain": list(VAR), "range": [fy(PB), fy(PT)], "clamp": True,
             "zero": False, "nice": False},
            {"name": "tamanho", "type": "sqrt", "domain": [0, 6600000], "range": [0, 520], "clamp": True},
            {"name": "cor", "type": "linear", "domain": COR_DOMINIO, "range": [c[k] for k in COR_FAIXA],
             "clamp": True, "interpolate": "rgb"},
        ],
        "marks": [
            {"type": "rect", "name": "fundo_clique", "interactive": True,
             "encode": {"enter": {"x": {"value": 0}, "y": {"value": 0}, "fill": {"value": "transparent"}},
                        "update": {"width": {"signal": "width"}, "height": {"signal": "height"}}}},
            {"type": "symbol", "name": "pontos", "from": {"data": "pts"},
             "encode": {
                 "enter": {"shape": {"value": "circle"}, "stroke": {"value": c["papel"]}},
                 "update": {
                     "x": {"scale": "x", "field": "renda"},
                     "y": {"scale": "y", "field": "var"},
                     "size": {"signal": "max(7, scale('tamanho', datum.val))"},
                     "fill": {"scale": "cor", "field": "m26"},
                     "strokeWidth": [{"test": "datum.__selected__ == 'on' || (sobre && sobre.cod == datum.cod)",
                                      "value": 1.4}, {"value": 0.5}],
                     "stroke": [{"test": "datum.__selected__ == 'on' || (sobre && sobre.cod == datum.cod)",
                                 "value": c["tinta"]}, {"value": c["papel"]}],
                     "opacity": {"signal": "(datum.__selected__ == 'off' || datum['val__highlightStatus'] == 'off' "
                                           "? 0.13 : 0.86) * clamp(entrada * 1.7 - (scale('x', datum.renda) / width) "
                                           "* 0.7, 0, 1)"},
                     "cursor": {"value": "pointer"},
                 }}},
            {"type": "rect", "name": "retangulo", "interactive": False,
             "encode": {"update": {
                 "x": {"signal": "(ret || ret_fixo || {x0: 0}).x0"},
                 "x2": {"signal": "(ret || ret_fixo || {x1: 0}).x1"},
                 "y": {"signal": "(ret || ret_fixo || {y0: 0}).y0"},
                 "y2": {"signal": "(ret || ret_fixo || {y1: 0}).y1"},
                 "fill": {"value": c["tinta"]}, "fillOpacity": {"value": 0.05},
                 "stroke": {"value": c["tinta"]}, "strokeWidth": {"value": 1.4}, "strokeDash": {"value": [5, 4]},
                 "opacity": {"signal": "ret || ret_fixo ? 1 : 0"}}}},
            {"type": "text", "name": "aviso", "interactive": False,
             "encode": {"update": {
                 "x": {"signal": f"{(PL + PR) / 2}*width/{w}"}, "y": fy(PT + 18), "align": {"value": "center"},
                 "text": {"signal": "estado == 'grande' ? 'Seleção grande demais (mais de 2.500 cidades): use o "
                                    "filtro no canto de cima' : estado == 'vazio' ? 'Nenhum município nesse "
                                    "retângulo' : ''"},
                 "fill": {"value": c["vermelho_escuro"]}, "font": {"value": "Sora Eleicoes, Segoe UI, sans-serif"},
                 "fontSize": {"value": 15}, "fontWeight": {"value": 600}}}},
        ],
    }


# ---------------------------------------------------------------------------------------------------- modelos fixos
CSS_RESUMO = (
    ".t19r .sob{position:absolute;left:0;top:0;right:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".t19r .st{position:absolute;top:26px;display:flex;flex-direction:column}"
    ".t19r .st .num{font-size:34px}"
    ".t19r .st .r{font-size:14px;color:var(--grafite);margin-top:4px;white-space:nowrap}"
    ".t19r .st:nth-of-type(2){left:0}.t19r .st:nth-of-type(3){left:166px}.t19r .st:nth-of-type(4){left:330px}"
    ".t19r .st:nth-of-type(5){left:494px}"
    ".t19r .br{position:absolute;left:0;right:0;top:94px;height:6px;display:flex;justify-content:space-between}"
    ".t19r .br i{display:block;height:6px}.t19r .br .l{background:var(--vermelho)}.t19r .br .f{background:var(--azul)}"
)


def corpo_resumo() -> str:
    return f"<style>{CSS_RESUMO}</style>{{{{content}}}}"


def css_lista() -> str:
    c = COL
    return (
        ".t19c{position:absolute;left:0;top:0;width:700px;height:" + str(LISTA_CAB) + "px;"
        "border-bottom:1.5px solid var(--grafite)}"
        ".t19c span{position:absolute;top:12px;font-size:13px;font-weight:600;letter-spacing:.08em;"
        "text-transform:uppercase;color:var(--cinza);white-space:nowrap}"
        ".t19l{pointer-events:none}"
        ".t19l .ln{position:absolute;left:0;width:700px;height:" + str(LISTA_H) + "px;pointer-events:auto;"
        "border-bottom:1px solid var(--creme);transition:background .15s,opacity .15s;cursor:pointer}"
        ".t19l .ln:hover{background:var(--creme)}"
        ".t19l .ln:hover::before{content:'';position:absolute;left:0;top:6px;bottom:6px;width:3px;"
        "background:var(--tinta)}"
        "#htmlContent:has(.ln:hover) .ln:not(:hover){opacity:.55}"
        ".t19l .ln>span{position:absolute;top:12px;font-size:16px;line-height:21px;white-space:nowrap}"
        f".t19l .c-nome{{left:{c['nome']}px;width:{c['lula'] - c['nome'] - 14}px;font-weight:600;overflow:hidden;"
        "text-overflow:ellipsis}"
        f".t19l .c-l{{left:{c['lula']}px}}.t19l .c-f{{left:{c['flavio']}px}}"
        f".t19l .c-s{{position:absolute;left:{c['serie']}px;top:7px}}"
        ".t19l .c-s .zero{stroke:var(--areia);stroke-width:1;stroke-dasharray:2 3}"
        ".t19l .c-s path{fill:none;stroke:var(--grafite);stroke-width:1.6;stroke-linejoin:round}"
        ".t19l .c-s .l{fill:var(--vermelho)}.t19l .c-s .f{fill:var(--azul)}"
        f".t19l .c-v{{left:{c['var'] - 8}px;width:60px;text-align:right;font-weight:600}}"
        f".t19l .c-x{{left:{c['virou']}px}}"
        ".t19l .selo{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
        "border:1.5px solid var(--tinta);padding:1px 4px;transform:rotate(-4deg);color:var(--tinta)}"
    )


def corpo_lista() -> str:
    c = COL
    cab = (f"<div class='t19c entra'><span style='left:{c['nome']}px'>Município</span>"
           f"<span style='left:{c['lula']}px'>Lula 26</span><span style='left:{c['flavio']}px'>Flávio 26</span>"
           f"<span style='left:{c['serie']}px'>2006 → 2026</span>"
           f"<span style='left:{c['var'] - 4}px'>Mudou</span>"
           f"<span style='left:{c['virou']}px'>Virou</span></div>")
    return f"<style>{css_lista()}</style>{cab}{{{{content}}}}"


def corpo_dispersao() -> str:
    """Fundo da dispersão (atrás do Deneb, mesma caixa): grade, zero, rótulos dos eixos, legenda, nota à mão e dica."""
    c = estilo.COR
    linhas = []
    for v in TICKS_Y:
        y = px_y(v)
        rot = ("0" if v == 0 else f"{v * 100:+.0f}".replace("-", "−")) + (" p.p." if v == TICKS_Y[-1] else "")
        cls = "zero" if v == 0 else "grade"
        linhas.append(f"<line class='{cls}' x1='{PL}' x2='{PR}' y1='{y:.1f}' y2='{y:.1f}'/>"
                      f"<text class='ty' x='{PL - 10}' y='{y + 4:.1f}'>{rot}</text>")
    for v, rot in TICKS_X:
        x = px_x(v)
        linhas.append(f"<line class='grade' x1='{x:.1f}' x2='{x:.1f}' y1='{PT}' y2='{PB}'/>"
                      f"<text class='tx' x='{x:.1f}' y='{PB + 22}'>{rot}</text>")
    y0 = px_y(0)
    svg = (f"<svg class='eixos' width='{DISP_W}' height='{DISP_H}' viewBox='0 0 {DISP_W} {DISP_H}'>"
           f"{estilo.defs_rabisco('rb19', 1.4)}{''.join(linhas)}"
           # os sentidos nos cantos vazios do alto e de baixo, à esquerda: junto da linha do zero, o rótulo ficava
           # embaixo da nuvem de pontos (o Deneb desenha por cima do fundo)
           f"<text class='lado' x='{PL + 10}' y='{px_y(0.13):.1f}'>↑ Lula ganhou margem</text>"
           f"<text class='lado' x='{PL + 10}' y='{px_y(-0.36):.1f}'>↓ Lula perdeu margem</text>"
           f"<text class='tit-x' x='{(PL + PR) / 2:.0f}' y='{PB + 48}'>renda por pessoa da cidade (R$ por mês, "
           f"Censo 2022 · escala que dobra a cada passo)</text>"

           f"</svg>")
    leg = ("<div class='leg entra d3'><span><i class='c-l'></i>Lula à frente em 2026</span>"
           "<span><i class='c-f'></i>Flávio à frente em 2026</span>"
           "<span><i class='c-t'></i>tamanho = votos válidos</span></div>")
    css = (
        ".t19d .rot{position:absolute;left:0;top:0}"
        ".t19d .sub{position:absolute;left:0;top:60px;font-size:15px;color:var(--grafite)}"
        ".t19d svg.eixos{position:absolute;left:0;top:0}"
        ".t19d .grade{stroke:var(--creme);stroke-width:1}"
        ".t19d .zero{stroke:var(--grafite);stroke-width:1.2;stroke-dasharray:4 4}"
        ".t19d text{font-family:var(--fonte);fill:var(--cinza);font-size:13px}"
        ".t19d .ty{text-anchor:end}.t19d .tx{text-anchor:middle}"
        ".t19d .lado{text-anchor:start;font-size:14px;font-weight:600;fill:var(--grafite)}"
        ".t19d .tit-x{text-anchor:middle;font-size:13px}"
        ".t19d .seta{fill:none;stroke:var(--tinta);stroke-width:1.8;stroke-linecap:round;animation-delay:1.6s}"
        f".t19d .mao{{position:absolute;left:110px;top:{PB - 48}px;font-size:26px;color:var(--tinta);"
        "transform:rotate(-3deg)}"
        ".t19d .leg{position:absolute;left:0;top:62px;display:flex;gap:22px;font-size:15px;color:var(--grafite)}"
        ".t19d .leg i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:7px;vertical-align:-1px}"
        f".t19d .c-l{{background:{c['vermelho']}}}.t19d .c-f{{background:{c['azul']}}}"
        f".t19d .c-t{{background:none;border:1.5px solid {c['grafite']};width:14px;height:14px}}"
        f".t19d .dica{{position:absolute;left:0;right:0;top:{DISP_H - 30}px;text-align:center;font-size:15px;"
        "color:var(--grafite)}"
        ".t19m .man{position:absolute;left:0;top:22px;right:0;font-size:24px}"
        ".t19m .man b{font-weight:700}"
    )
    return (f"<style>{css}</style><div class='tela t19d'>"
            f"<div class='rot sobe'>Renda × quanto a margem de Lula mudou, 2022 → 2026</div>"
            f"{svg}<div class='mao entra d16'>cada ponto é uma cidade</div>{leg}"
            f"<div class='dica entra d8'>Arraste um retângulo sobre os pontos para filtrar a lista · clique num ponto para ver só ele · no vazio, limpa</div>"
            f"</div>{{{{content}}}}")


CSS_DOSSIE = (
    ".tt19{background:var(--branco);padding:26px 24px 14px 26px;overflow:hidden;"
    "background-image:repeating-linear-gradient(to bottom,transparent 0,transparent 27px,rgba(203,189,162,.35) 27px,"
    "rgba(203,189,162,.35) 28px);border:1.5px solid var(--areia)}"
    ".tt19 .nm{font-size:22px;font-weight:700;line-height:1.15;padding-right:70px}"
    ".tt19 .sub{margin-top:5px;padding-right:40px;font-size:14px;color:var(--grafite);white-space:nowrap}"
    ".tt19 .cap{margin-top:14px;font-size:11px}"
    ".tt19 svg.serie{display:block;margin-top:2px}"
    ".tt19 .serie .zero{stroke:var(--grafite);stroke-width:1;stroke-dasharray:2 3}"
    ".tt19 .serie path{fill:none;stroke:var(--grafite);stroke-width:2;stroke-linejoin:round}"
    ".tt19 .serie circle.l{fill:var(--vermelho)}.tt19 .serie circle.f{fill:var(--azul)}"
    ".tt19 .serie text{font-family:var(--fonte);text-anchor:middle}"
    ".tt19 .serie .v{font-size:13px;font-weight:700}.tt19 .serie .v.l{fill:var(--vermelho)}"
    ".tt19 .serie .v.f{fill:var(--azul)}"
    ".tt19 .serie .a{font-size:12px;fill:var(--cinza);font-weight:600}"
    ".tt19 .serie .ze{font-size:11px;fill:var(--cinza);text-anchor:end}"
    ".tt19 .pe{display:flex;gap:16px;font-size:14px;color:var(--grafite);margin-top:4px}"
    ".tt19 .pe .ab{color:var(--cinza)}"
    ".tt19 .selo{position:absolute;right:24px;top:84px;transform:rotate(7deg);border:2.5px solid var(--tinta);"
    "outline:1px solid var(--tinta);outline-offset:2px;padding:4px 9px;font-weight:700;font-size:13px;"
    "letter-spacing:.16em;text-transform:uppercase;color:var(--tinta)}"
    ".tt19 .mao{position:absolute;right:22px;bottom:10px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
    ".tt19f{position:fixed;left:170px;top:-14px;width:120px;opacity:.85;transform:rotate(-3deg);z-index:2;"
    "pointer-events:none}"
    ".tt19i{position:fixed;right:18px;top:16px;width:30px;opacity:.9;z-index:2;pointer-events:none}"
)


def corpo_dossie() -> str:
    fita = estilo.imagem_b64("docs/midia/arte/dossie/fita-tinta.png", 160)
    pino = estilo.imagem_b64("docs/midia/arte/icones/pino-tinta.png", 48)
    return (f"<style>{CSS_DOSSIE}</style>{{{{content}}}}<img class='tt19f' alt='' src='{fita}'/>"
            f"<img class='tt19i' alt='' src='{pino}'/>")


def main() -> int:
    medidas()
    SPEC.parent.mkdir(parents=True, exist_ok=True)
    SPEC.write_text(json.dumps(spec(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"T19: medidas de desenho em {DAX} · spec {SPEC.name} ({SPEC.stat().st_size:,} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
