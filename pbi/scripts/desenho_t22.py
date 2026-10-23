# -*- coding: utf-8 -*-
"""desenho_t22 — tela 22 · Simulador (dono: tela 22). Gera pbi/dax/T22 Simulador/Desenho/*.dax (só leem as contas de
T22 Simulador\\Contas) e expõe para paginas/t22_simulador.py a geometria das réguas (as segmentações de botões
invisíveis ficam exatamente sobre as réguas desenhadas) e os modelos fixos (bodyTemplate).

    python -I -X utf8 pbi/scripts/desenho_t22.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import estilo  # noqa: E402

PBI = AQUI.parent
DAX = PBI / "dax" / "T22 Simulador" / "Desenho"
PASTA = r"T22 Simulador\Desenho"
PP = '"+0.0;−0.0;0.0"'

# ---------------------------------------------------------------------------------------------------- geometria
HEROI = (150, 140, 860, 250)
REGUA_A = (150, 410, 860, 150)          # caixa do HTML da régua "para Lula"
A_X0, A_W, A_Y = 30, 800, 44            # barra (dentro da caixa): x inicial, largura, topo; 0–100 em passos de 2
A_H = 30
REGUA_B = (150, 576, 410, 104)          # não votam: 0–50 em passos de 5
REGUA_C = (600, 576, 410, 104)          # comparecimento: −5 a +5
BC_X0, BC_W, BC_Y = 20, 370, 62         # trilho das réguas B e C (dentro de cada caixa)
PESQUISAS = (150, 704, 860, 296)
LIN_TOPO, LIN_H = 62, 28
RESULTADO = (1060, 140, 710, 300)
GRADE = (1060, 470, 400, 530)
LADO = 58
PASSO = 66
LEGENDA = (1484, 470, 286, 530)


def tiles_a() -> tuple:
    """Caixa da segmentação invisível da régua A: 51 botões centrados em 0, 2, …, 100."""
    x, y, _w, _h = REGUA_A
    passo = A_W / 50
    return (x + A_X0 - passo / 2, y + A_Y - 6, A_W + passo, A_H + 12)


def tiles_bc(caixa) -> tuple:
    x, y, _w, _h = caixa
    passo = BC_W / 10
    return (x + BC_X0 - passo / 2, y + BC_Y - 16, BC_W + passo, 32)


# ---------------------------------------------------------------------------------------------------- DAX
def gravar(nome: str, descricao: str, expressao: str) -> None:
    destino = DAX / f"{nome}.dax"
    destino.parent.mkdir(parents=True, exist_ok=True)
    texto = f"/*\n@pasta: {PASTA}\n@formato: texto\n@descricao: {descricao}\n*/\n" + expressao.strip("\n") + "\n"
    if "\t" in texto:
        raise SystemExit(f"tab em {nome}")
    if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
        destino.write_text(texto, encoding="utf-8")


def mi(v: str, casas: int = 2) -> str:
    return f'FORMAT ( {v} / 1000000, "0.{"0" * casas}" ) & " mi"'


def medidas() -> None:
    gravar("T22 · Herói · HTML", "A resposta da tela: quanto dos votos dos outros candidatos Lula precisaria para "
           "empatar (contador), a manchete e o aviso de que é simulação.", rf"""
-- 1 · Leituras
VAR _emp = [T22 · empate sem abstenção]
VAR _outros = [T22 · votos dos outros]
VAR _dif = [T22 · diferença no 1º turno]
-- 2 · Textos
VAR _txtEmp = FORMAT ( _emp * 100, "0" )
VAR _txtOutros = {mi("_outros")}
VAR _txtDif = {mi("_dif")}
-- 4 · Marcação
RETURN
    "<div class='tela t22h'>"
        & "<div class='grande sobe'><span class='num'>" & _txtEmp & "</span>%</div>"
        & "<div class='lado sobe d2'>dos <b>" & _txtOutros & "</b> de votos dos outros candidatos: o que Lula "
            & "precisaria para empatar com Flávio</div>"
        & "<div class='man sobe d3'>Flávio terminou o 1º turno <span class='num'>" & _txtDif
            & "</span> à frente. Para empatar, Lula precisaria de " & _txtEmp & "% dos votos dos outros; metade "
            & "não basta.</div>"
    & "</div>"
""")
    gravar("T22 · Herói · ALT", "Texto alternativo da resposta do simulador.", rf"""
-- 1 · Leituras
VAR _emp = [T22 · empate sem abstenção]
VAR _outros = [T22 · votos dos outros]
RETURN
    "Para empatar, Lula precisaria de " & FORMAT ( _emp * 100, "0" ) & "% dos " & {mi("_outros")}
        & " de votos dos outros candidatos. Simulação, não previsão."
""")
    # --- régua A (para Lula)
    passo_a = A_W / 100
    gravar("T22 · Régua Lula · HTML", "A régua do controle principal: a barra dividida (Lula à esquerda, Flávio à "
           "direita) na posição escolhida, a marca do empate e a faixa onde caem as pesquisas.", rf"""
-- 1 · Leituras
VAR _a = [T22 · parte para Lula]
VAR _emp = [T22 · empate com a abstenção escolhida]
VAR _min = [T22 · pesquisas · menor parte para Lula]
VAR _max = [T22 · pesquisas · maior parte para Lula]
VAR _n = [T22 · pesquisas · quantas]
VAR _pesq0 =
    ADDCOLUMNS (
        VALUES ( 'Transferência'[Instituto] ),
        "@d", [T22 · pesquisa · data],
        "@a", [T22 · pesquisa · parte para Lula entre os que votam]
    ) /* lista */
VAR _pesq = FILTER ( _pesq0, NOT ISBLANK ( [@d] ) ) /* lista */
-- 2 · Textos
VAR _txtA = FORMAT ( _a * 100, "0" ) & "% Lula"
VAR _txtF = FORMAT ( ( 1 - _a ) * 100, "0" ) & "% Flávio"
VAR _txtEmp = "empate: " & FORMAT ( _emp * 100, "0" ) & "%"
VAR _txtFaixa =
    "as " & _n & " pesquisas: de " & FORMAT ( _min * 100, "0" ) & "% a " & FORMAT ( _max * 100, "0" ) & "%"
-- 3 · Geometria
VAR _xa = {A_X0} + _a * 100 * {passo_a} -- geometria
VAR _xe = {A_X0} + MIN ( 1, _emp ) * 100 * {passo_a} -- geometria
VAR _x0 = {A_X0} + _min * 100 * {passo_a} -- geometria
VAR _x1 = {A_X0} + _max * 100 * {passo_a} -- geometria
VAR _marcas =
    CONCATENATEX (
        _pesq,
        "<i class='pq' style='left:" & FORMAT ( {A_X0} + [@a] * 100 * {passo_a} - 1, "0.0##", "en-US" ) & "px'></i>",
        ""
    ) /* lista */
-- 4 · Marcação
RETURN
    "<div class='tela t22a'>"
        & "<div class='pergunta sobe'>Dos eleitores dos outros candidatos que forem votar, quantos escolhem Lula?</div>"
        & "<div class='barra entra d2'>"
            & "<i class='l' style='width:" & FORMAT ( _xa - {A_X0}, "0.0##", "en-US" ) & "px'></i>"
            & "<i class='f' style='left:" & FORMAT ( _xa - {A_X0}, "0.0##", "en-US" ) & "px;width:"
            & FORMAT ( {A_X0 + A_W} - _xa, "0.0##", "en-US" ) & "px'></i>"
            & "<span class='tl'>" & IF ( _a >= 0.12, _txtA, "" ) & "</span>"
            & "<span class='tf'>" & IF ( _a <= 0.88, _txtF, "" ) & "</span>"
        & "</div>"
        & "<i class='alca' style='left:" & FORMAT ( _xa - 16, "0.0##", "en-US" ) & "px'></i>"
        & "<i class='emp' style='left:" & FORMAT ( _xe - 1, "0.0##", "en-US" ) & "px'></i>"
        & "<span class='emp-t mao' style='left:" & FORMAT ( _xe - 4, "0.0##", "en-US" ) & "px'>" & _txtEmp & "</span>"
        & "<i class='faixa entra d4' style='left:" & FORMAT ( _x0, "0.0##", "en-US" ) & "px;width:"
        & FORMAT ( _x1 - _x0, "0.0##", "en-US" ) & "px'></i>" & _marcas
        & "<span class='faixa-t entra d5' style='left:" & FORMAT ( _x0, "0.0##", "en-US" ) & "px'>" & _txtFaixa
        & "</span>"
    & "</div>"
""")
    gravar("T22 · Régua Lula · ALT", "Texto alternativo da régua do controle principal.", r"""
-- 1 · Leituras
VAR _a = [T22 · parte para Lula]
VAR _emp = [T22 · empate com a abstenção escolhida]
RETURN
    "Controle: " & FORMAT ( _a * 100, "0" ) & "% dos eleitores dos outros que votam escolhem Lula. Empate em "
        & FORMAT ( _emp * 100, "0" ) & "%. Clique na régua para mudar."
""")
    # --- réguas B e C
    gravar("T22 · Régua abstenção · HTML", "Régua do controle de quem não escolhe ninguém (0 a 50%).", rf"""
-- 1 · Leituras
VAR _b = [T22 · parte que não vota]
VAR _outros = [T22 · votos dos outros]
-- 2 · Textos
VAR _txt =
    IF ( _b = 0, "ninguém: todos votam", FORMAT ( _b * 100, "0" ) & "% · " & {mi("_outros * _b")} & " de votos a menos" )
-- 3 · Geometria
VAR _x = {BC_X0} + _b / 0.5 * {BC_W} -- geometria
-- 4 · Marcação
RETURN
    "<div class='tela t22c'>"
        & "<div class='pergunta sobe'>Quantos deles não vão escolher ninguém?</div>"
        & "<div class='valor sobe d1'>" & _txt & "</div>"
        & "<i class='trilho entra d2'></i><i class='cheio' style='width:" & FORMAT ( _x - {BC_X0}, "0.0##", "en-US" )
        & "px'></i><i class='alca' style='left:" & FORMAT ( _x - 11, "0.0##", "en-US" ) & "px'></i>"
        & "<span class='ex' style='left:{BC_X0 - 6}px'>0%</span><span class='ex' style='left:{BC_X0 + BC_W - 20}px'>50%</span>"
    & "</div>"
""")
    gravar("T22 · Régua abstenção · ALT", "Texto alternativo da régua de abstenção.", r"""
"Controle: " & FORMAT ( [T22 · parte que não vota] * 100, "0" ) & "% dos eleitores dos outros não escolhem ninguém."
""")
    gravar("T22 · Régua comparecimento · HTML", "Régua do controle de comparecimento (−5 a +5 pontos), com os votos "
           "a mais ou a menos e a regra: metade para cada um.", rf"""
-- 1 · Leituras
VAR _c = [T22 · mudança no comparecimento]
VAR _novos = [T22 · votos novos]
-- 2 · Textos
VAR _txt =
    IF (
        _c = 0,
        "como no 1º turno",
        FORMAT ( _c * 100, "+0;−0" ) & IF ( ABS ( _c ) = 0.01, " ponto · ", " pontos · " )
            & {mi("ABS ( _novos )", 1)} & IF ( _c > 0, " a mais", " a menos" ) & ", metade para cada um"
    )
-- 3 · Geometria
VAR _x = {BC_X0} + ( _c + 0.05 ) / 0.1 * {BC_W} -- geometria
VAR _xm = {BC_X0} + {BC_W} / 2 -- geometria
-- 4 · Marcação
RETURN
    "<div class='tela t22c'>"
        & "<div class='pergunta sobe'>E se o comparecimento mudar?</div>"
        & "<div class='valor sobe d1'>" & _txt & "</div>"
        & "<i class='trilho entra d2'></i><i class='cheio' style='left:" & FORMAT ( MIN ( _x, _xm ), "0.0##", "en-US" )
        & "px;width:" & FORMAT ( ABS ( _x - _xm ), "0.0##", "en-US" ) & "px'></i>"
        & "<i class='meio' style='left:" & FORMAT ( _xm - 1, "0.0##", "en-US" ) & "px'></i>"
        & "<i class='alca' style='left:" & FORMAT ( _x - 11, "0.0##", "en-US" ) & "px'></i>"
        & "<span class='ex' style='left:{BC_X0 - 8}px'>−5</span><span class='ex' style='left:{BC_X0 + BC_W - 12}px'>+5</span>"
    & "</div>"
""")
    gravar("T22 · Régua comparecimento · ALT", "Texto alternativo da régua de comparecimento.", r"""
"Controle: comparecimento " & FORMAT ( [T22 · mudança no comparecimento] * 100, "+0;−0;0" ) & " pontos sobre o 1º turno."
""")
    # --- lista das pesquisas (uma linha por instituto)
    gravar("T22 · Pesquisas · HTML", "Uma linha da lista das pesquisas (granularidade Transferência[Instituto]): para "
           "onde vão os votos dos outros segundo a última pesquisa do instituto depois do 1º turno, e o 2º turno que "
           "isso daria. Clicar leva o cenário da pesquisa ao resultado e ao mapa.", rf"""
-- 1 · Leituras
VAR _data = [T22 · pesquisa · data]
VAR _pos = [T22 · pesquisa · posição]
VAR _a = [T22 · pesquisa · parte para Lula entre os que votam]
VAR _b = [T22 · pesquisa · parte que não vota]
VAR _lula = [T22 · cenário · Lula %]
VAR _flavio = [T22 · cenário · Flávio %]
-- 2 · Textos
VAR _inst0 = [T22 · pesquisa em uso]
VAR _inst = SUBSTITUTE ( SUBSTITUTE ( _inst0, "&", "&amp;" ), "<", "&lt;" )
VAR _txtData = FORMAT ( _data, "dd/MM" )
VAR _txtL = FORMAT ( _lula, "0.0%" )
VAR _txtF = FORMAT ( _flavio, "0.0%" )
-- 3 · Geometria
VAR _wl = ( 1 - _b ) * _a * 260 -- geometria
VAR _wf = ( 1 - _b ) * ( 1 - _a ) * 260 -- geometria
VAR _y = {LIN_TOPO} + ( _pos - 1 ) * {LIN_H} -- geometria
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _data ),
        "<div class='tela t22p'><div class='ln sobe d" & ( _pos + 2 ) & "' style='top:" & _y & "px'>"
            & "<span class='i'>" & _inst & "</span><span class='d'>" & _txtData & "</span>"
            & "<span class='b'><i class='l' style='width:" & FORMAT ( _wl, "0.0##", "en-US" ) & "px'></i>"
            & "<i class='f' style='width:" & FORMAT ( _wf, "0.0##", "en-US" ) & "px'></i></span>"
            & "<span class='pa tnum'>" & FORMAT ( _a * 100, "0" ) & "%</span>"
            & "<span class='r tnum'><b class='lula'>" & _txtL & "</b> × <b class='flavio'>" & _txtF & "</b></span>"
        & "</div></div>"
    )
""")
    gravar("T22 · Pesquisas · ALT", "Texto alternativo da lista das pesquisas.", r"""
"Lista das " & [T22 · pesquisas · quantas] & " pesquisas com o cruzamento dos eleitores dos outros candidatos: a parte "
    & "que vai para Lula e o 2º turno que isso daria. Clique numa linha para ver o cenário no mapa."
""")
    # --- resultado
    gravar("T22 · Resultado · HTML", "O 2º turno simulado no Brasil (com o exterior): Lula × Flávio em % dos "
           "válidos, em quantas UFs cada um fica à frente e a diferença em votos; o rótulo diz se a conta usa os "
           "controles ou uma pesquisa.", rf"""
-- 1 · Leituras
VAR _pesq = [T22 · pesquisa em uso]
VAR _data = [T22 · pesquisa · data]
VAR _lula = [T22 · cenário · Lula %]
VAR _flavio = [T22 · cenário · Flávio %]
VAR _ufL = [T22 · cenário · UFs com Lula à frente]
VAR _ufF = [T22 · cenário · UFs com Flávio à frente]
VAR _dif = [T22 · cenário · diferença]
-- 2 · Textos
VAR _rotulo =
    IF (
        ISBLANK ( _pesq ),
        "Seus controles",
        "Pesquisa " & SUBSTITUTE ( _pesq, "<", "&lt;" ) & ", " & FORMAT ( _data, "dd/MM" )
    )
VAR _txtUfL = "à frente em " & _ufL & IF ( _ufL = 1, " UF", " UFs" )
VAR _txtUfF = "à frente em " & _ufF & IF ( _ufF = 1, " UF", " UFs" )
VAR _nota =
    SWITCH (
        TRUE (),
        ABS ( _dif ) < 50000, "praticamente empatados",
        _dif > 0, "Lula vence por " & {mi("_dif", 1)} & " de votos",
        "Flávio vence por " & {mi("- _dif", 1)} & " de votos"
    )
-- 3 · Geometria
VAR _wl = _lula * 100 -- geometria
-- 4 · Marcação
RETURN
    "<div class='tela t22r'>"
        & "<div class='rot sobe'>Resultado do 2º turno simulado · " & _rotulo & "</div>"
        & "<div class='lado l sobe d1'><span class='q'>Lula</span><span class='num'>" & FORMAT ( _lula, "0.0%" )
            & "</span><span class='u'>" & _txtUfL & "</span></div>"
        & "<div class='lado f sobe d2'><span class='q'>Flávio</span><span class='num'>" & FORMAT ( _flavio, "0.0%" )
            & "</span><span class='u'>" & _txtUfF & "</span></div>"
        & "<div class='br'><i class='bl barra-x' style='width:" & FORMAT ( _wl, "0.0##", "en-US" ) & "%'></i>"
            & "<i class='bf barra-x-dir' style='width:" & FORMAT ( 100 - _wl, "0.0##", "en-US" ) & "%'></i>"
            & "<i class='meio'></i></div>"
        & "<div class='cinq'>50%</div>"
        & "<div class='mao sobe d6'>" & _nota & "</div>"
    & "</div>"
""")
    gravar("T22 · Resultado · ALT", "Texto alternativo do resultado simulado.", r"""
-- 1 · Leituras
VAR _lula = [T22 · cenário · Lula %]
VAR _flavio = [T22 · cenário · Flávio %]
VAR _ufL = [T22 · cenário · UFs com Lula à frente]
VAR _ufF = [T22 · cenário · UFs com Flávio à frente]
RETURN
    "2º turno simulado: Lula " & FORMAT ( _lula, "0.0%" ) & ", Flávio " & FORMAT ( _flavio, "0.0%" ) & ". Lula à frente "
        & "em " & _ufL & IF ( _ufL = 1, " UF", " UFs" ) & ", Flávio em " & _ufF & IF ( _ufF = 1, " UF.", " UFs." )
""")
    # --- quadrado da UF
    gravar("T22 · UF · HTML", "Um quadrado do mapa de quadrados (granularidade UF[UF], com o exterior): a cor de quem "
           "fica à frente no cenário, mais forte quanto maior a vantagem, a sigla e o % de Lula.", rf"""
-- 1 · Leituras
VAR _uf = [T22 · UF · sigla]
VAR _col = [T22 · UF · coluna na grade]
VAR _lin = [T22 · UF · linha na grade]
VAR _lula = [T22 · cenário · Lula %]
-- 2 · Textos
VAR _sigla = IF ( _uf = "ZZ", "EX", _uf )
VAR _m = _lula - 0.5
VAR _cor =
    SWITCH (
        TRUE (),
        _m <= -0.15, "#1D3C6E",
        _m <= -0.05, "#2B5797",
        _m < 0, "#8FA8CF",
        _m < 0.05, "#D9877B",
        _m < 0.15, "#B8322A",
        "#8E2620"
    )
VAR _clara = _m > -0.05 && _m < 0.05
VAR _cls = IF ( _clara, "q clara", "q" ) & IF ( _uf = "ZZ", " ex", "" )
-- 3 · Geometria
VAR _x = _col * {PASSO} -- geometria
VAR _y = _lin * {PASSO} -- geometria
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _lula ),
        "<div class='tela t22g'><div class='" & _cls & " cor-q' style='left:" & _x & "px;top:" & _y
            & "px;background:" & _cor & ";animation-delay:" & ( 400 + ( _col + _lin ) * 70 ) & "ms'>"
            & "<b>" & _sigla & "</b><span>" & FORMAT ( _lula, "0%" ) & "</span></div></div>"
    )
""")
    gravar("T22 · UF · ALT", "Texto alternativo do mapa de quadrados.", r"""
-- 1 · Leituras
VAR _ufL = [T22 · cenário · UFs com Lula à frente]
VAR _ufF = [T22 · cenário · UFs com Flávio à frente]
RETURN
    "Mapa de quadrados das UFs no cenário: Lula à frente em " & _ufL & ", Flávio em " & _ufF
        & ". Passe o mouse num estado para ver o detalhe."
""")
    # --- dossiê da UF (tooltip)
    gravar("T22 · Tooltip UF · HTML", "Dossiê da UF no cenário (página de tooltip ttT22UF): Lula × Flávio no cenário, "
           "no 1º turno (só os dois) e o peso dos outros candidatos ali.", rf"""
-- 1 · Leituras
VAR _nome = [T22 · UF · nome]
VAR _lula = [T22 · cenário · Lula %]
VAR _flavio = [T22 · cenário · Flávio %]
VAR _lula1 = [T22 · Lula % no 1º turno]
VAR _outros = [T22 · parte dos outros nos válidos]
VAR _dif = [T22 · cenário · diferença]
-- 2 · Textos
VAR _quem = IF ( _dif > 0, "Lula à frente", IF ( _dif < 0, "Flávio à frente", "empate" ) )
VAR _mudou = ( _lula - _lula1 ) * 100
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _nome ),
        "<div class='tela tt22'>"
            & "<div class='nm'>" & _nome & "</div>"
            & "<div class='rot'>No cenário</div>"
            & "<div class='duelo'><span class='lula'>Lula " & FORMAT ( _lula, "0.0%" ) & "</span>"
            & "<span class='flavio'>Flávio " & FORMAT ( _flavio, "0.0%" ) & "</span></div>"
            & "<div class='rot'>No 1º turno, só os dois</div>"
            & "<div class='duelo menor'><span class='lula'>Lula " & FORMAT ( _lula1, "0.0%" ) & "</span>"
            & "<span class='flavio'>Flávio " & FORMAT ( 1 - _lula1, "0.0%" ) & "</span></div>"
            & "<div class='pe'>Os outros candidatos tiveram " & FORMAT ( _outros, "0.0%" ) & " dos votos aqui. No "
            & "cenário, Lula " & IF ( _mudou < 0, "perde ", "ganha " ) & FORMAT ( ABS ( _mudou ), "0.0" )
            & IF ( ROUND ( ABS ( _mudou ), 1 ) = 1, " ponto", " pontos" ) & " em relação ao 1º turno.</div>"
            & "<div class='mao'>" & _quem & "</div>"
        & "</div>"
    )
""")
    gravar("T22 · Tooltip UF · ALT", "Texto alternativo do dossiê da UF.", r"""
-- 1 · Leituras
VAR _nome = [T22 · UF · nome]
VAR _lula = [T22 · cenário · Lula %]
RETURN
    IF ( NOT ISBLANK ( _nome ), _nome & " no cenário: Lula " & FORMAT ( _lula, "0.0%" ) & ", Flávio "
        & FORMAT ( 1 - _lula, "0.0%" ) & "." )
""")


# ---------------------------------------------------------------------------------------------------- modelos fixos
def corpo_heroi() -> str:
    balanca = estilo.imagem_b64("docs/midia/arte/icones/balanca-tinta.png", 90)
    css = (
        ".t22h .grande{position:absolute;left:-4px;top:-4px;font-size:112px;font-weight:700;letter-spacing:-.045em;"
        "line-height:1}"
        ".t22h .grande .num{font-size:112px}"
        ".t22h .lado{position:absolute;left:250px;top:14px;width:560px;font-size:22px;font-weight:600;line-height:1.3;"
        "color:var(--grafite)}"
        ".t22h .lado b{color:var(--tinta)}"
        ".t22h .man{position:absolute;left:0;top:124px;width:840px;font-size:20px;font-weight:500;line-height:1.35}"
        ".t22h .man .num{font-size:20px;font-weight:700}"
        ".t22v{position:fixed;left:0;right:0;top:196px;height:46px;background:var(--creme);display:flex;"
        "align-items:center;gap:14px;padding:0 16px;font-size:16px;font-weight:600;color:var(--tinta)}"
        ".t22v img{width:42px}"
    )
    return (f"<style>{css}</style><div class='t22v entra d5'><img alt='' src='{balanca}'/>Simulação, não previsão: "
            f"você decide para onde vão os votos; o painel só faz a conta.</div>{{{{content}}}}")


def corpo_regua_a() -> str:
    css = (
        ".t22a{pointer-events:none}"
        ".t22a .pergunta{position:absolute;left:0;top:0;font-size:18px;font-weight:600}"
        f".t22a .barra{{position:absolute;left:{A_X0}px;top:{A_Y}px;width:{A_W}px;height:{A_H}px}}"
        f".t22a .barra i{{position:absolute;top:0;height:{A_H}px;transition:width .5s,left .5s}}"
        ".t22a .barra .l{left:0;background:var(--vermelho)}"
        f".t22a .barra .f{{background:var(--azul)}}"
        ".t22a .barra span{position:absolute;top:6px;font-size:14px;font-weight:700;color:var(--branco)}"
        ".t22a .barra .tl{left:12px}.t22a .barra .tf{right:12px}"
        f".t22a .alca{{position:absolute;top:{A_Y + A_H / 2 - 16}px;width:32px;height:32px;border-radius:50%;"
        "background:var(--branco);border:2px solid var(--tinta);box-shadow:0 2px 6px rgba(28,25,21,.25);"
        "transition:left .5s}"
        f".t22a .emp{{position:absolute;top:{A_Y - 10}px;height:{A_H + 22}px;width:0;border-left:2px dashed "
        "var(--tinta)}"
        f".t22a .emp-t{{position:absolute;top:{A_Y + A_H + 14}px;font-size:24px;color:var(--tinta);white-space:nowrap}}"
        f".t22a .faixa{{position:absolute;top:{A_Y + A_H + 16}px;height:8px;background:var(--areia);border-radius:4px}}"
        f".t22a .pq{{position:absolute;top:{A_Y + A_H + 13}px;width:2px;height:14px;background:var(--grafite)}}"
        f".t22a .faixa-t{{position:absolute;top:{A_Y + A_H + 34}px;font-size:14px;color:var(--grafite);"
        "white-space:nowrap}"
        f".t22a .zero{{position:absolute;left:{A_X0 - 8}px;top:{A_Y - 22}px;font-size:13px;color:var(--cinza)}}"
    )
    return (f"<style>{css}</style><div class='tela t22a'><span class='zero' style='left:{A_X0 - 4}px'>0%</span>"
            f"<span class='zero' style='left:{A_X0 + A_W - 22}px'>100%</span></div>{{{{content}}}}")


def corpo_regua_bc() -> str:
    css = (
        ".t22c{pointer-events:none}"
        ".t22c .pergunta{position:absolute;left:0;top:0;font-size:16px;font-weight:600}"
        ".t22c .valor{position:absolute;left:0;top:24px;font-size:14px;color:var(--grafite);white-space:nowrap}"
        f".t22c .trilho{{position:absolute;left:{BC_X0}px;top:{BC_Y - 2}px;width:{BC_W}px;height:4px;"
        "background:var(--areia);border-radius:2px}"
        f".t22c .cheio{{position:absolute;left:{BC_X0}px;top:{BC_Y - 2}px;height:4px;background:var(--tinta);"
        "transition:width .4s,left .4s}"
        f".t22c .meio{{position:absolute;top:{BC_Y - 8}px;height:16px;width:2px;background:var(--grafite)}}"
        f".t22c .alca{{position:absolute;top:{BC_Y - 11}px;width:22px;height:22px;border-radius:50%;"
        "background:var(--branco);border:2px solid var(--tinta);transition:left .4s}"
        f".t22c .ex{{position:absolute;top:{BC_Y + 16}px;font-size:13px;color:var(--cinza)}}"
    )
    return f"<style>{css}</style>{{{{content}}}}"


def corpo_pesquisas() -> str:
    css = (
        ".t22t .rot{position:absolute;left:0;top:0}"
        ".t22t .sub{position:absolute;left:0;top:22px;font-size:14px;color:var(--grafite)}"
        f".t22t .cab{{position:absolute;left:0;right:0;top:{LIN_TOPO - 20}px;font-size:12px;font-weight:600;"
        "letter-spacing:.1em;text-transform:uppercase;color:var(--cinza)}"
        ".t22t .cab span{position:absolute}"
        ".t22p{pointer-events:none}"
        f".t22p .ln{{position:absolute;left:0;width:860px;height:{LIN_H}px;pointer-events:auto;cursor:pointer;"
        "border-bottom:1px solid var(--creme);transition:background .15s,opacity .15s}"
        ".t22p .ln:hover{background:var(--creme)}"
        "#htmlContent:has(.ln:hover) .ln:not(:hover){opacity:.55}"
        ".t22p .ln>span{position:absolute;top:4px;font-size:15px;white-space:nowrap}"
        ".t22p .i{left:6px;font-weight:600}.t22p .d{left:126px;color:var(--cinza)}"
        ".t22p .b{left:190px;top:8px!important;width:260px;height:12px;background:var(--creme);display:flex}"
        ".t22p .b i{display:block;height:12px}.t22p .b .l{background:var(--vermelho)}.t22p .b .f{background:var(--azul)}"
        ".t22p .pa{left:466px;font-weight:700;color:var(--vermelho)}"
        ".t22p .r{left:560px}"
    )
    cab = ("<div class='cab'><span style='left:6px'>Instituto</span><span style='left:190px'>Para onde vão os "
           "9,3 mi</span><span style='left:466px'>Lula leva</span>"
           "<span style='left:560px'>2º turno daria</span></div>")
    return (f"<style>{css}</style><div class='tela t22t'><div class='rot sobe'>E se os outros votarem como diz cada "
            f"pesquisa?</div><div class='sub sobe d1'>A última de cada instituto depois do 1º turno. Clique numa "
            f"linha para ver o cenário que ela sugere.</div>"
            f"{cab}</div>{{{{content}}}}")


def corpo_resultado() -> str:
    css = (
        ".t22r .rot{position:absolute;left:0;top:0;right:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".t22r .lado{position:absolute;top:30px;display:flex;flex-direction:column}"
        ".t22r .lado.l{left:0}.t22r .lado.f{right:0;align-items:flex-end}"
        ".t22r .lado .q{font-size:15px;font-weight:700;letter-spacing:.14em;text-transform:uppercase}"
        ".t22r .l .q,.t22r .l .num{color:var(--vermelho)}.t22r .f .q,.t22r .f .num{color:var(--azul)}"
        ".t22r .lado .num{font-size:76px;margin-top:4px}"
        ".t22r .lado .u{font-size:15px;color:var(--grafite);margin-top:6px}"
        ".t22r .br{position:absolute;left:0;right:0;top:184px;height:26px;display:flex;justify-content:space-between}"
        ".t22r .br i{display:block;height:26px}.t22r .br .bl{background:var(--vermelho)}"
        ".t22r .br .bf{background:var(--azul)}"
        ".t22r .br .meio{position:absolute;left:50%;top:-8px;height:42px;width:2px;background:var(--tinta)}"
        ".t22r .cinq{position:absolute;left:0;right:0;top:216px;text-align:center;font-size:13px;color:var(--cinza)}"
        ".t22r .mao{position:absolute;left:0;top:240px;font-size:30px;color:var(--tinta)}"
    )
    return f"<style>{css}</style>{{{{content}}}}"


def corpo_grade() -> str:
    css = (
        ".t22g{pointer-events:none}"
        f".t22g .q{{position:absolute;width:{LADO}px;height:{LADO}px;pointer-events:auto;cursor:default;"
        "display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--branco);"
        "transition:background .5s,transform .15s}"
        ".t22g .q:hover{transform:scale(1.08);outline:2px solid var(--tinta)}"
        ".t22g .q b{font-size:16px;font-weight:700;letter-spacing:.02em}"
        ".t22g .q span{font-size:12px;font-weight:500;opacity:.9}"
        ".t22g .q.clara{color:var(--tinta)}"
        ".t22g .q.ex{outline:2px dashed var(--tinta);outline-offset:-4px}"
        "@keyframes t22Cor{from{background:var(--creme);opacity:.4}}"
        ".t22g .cor-q{animation:t22Cor 1s ease-out both}"
    )
    return f"<style>{css}</style>{{{{content}}}}"


def corpo_legenda() -> str:
    clipe = estilo.imagem_b64("docs/midia/arte/dossie/clipe-tinta.png", 70)
    itens = [("#8E2620", "Lula à frente por 15 pontos ou mais"), ("#B8322A", "Lula à frente por 5 a 15"),
             ("#D9877B", "Lula à frente por menos de 5"), ("#8FA8CF", "Flávio à frente por menos de 5"),
             ("#2B5797", "Flávio à frente por 5 a 15"), ("#1D3C6E", "Flávio à frente por 15 ou mais")]
    leg = "".join(f"<div><i style='background:{c}'></i>{t}</div>" for c, t in itens)
    css = (
        ".t22l .rot{position:absolute;left:0;top:0;width:280px;line-height:1.5}"
        ".t22l .leg{position:absolute;left:0;top:64px;font-size:14px;line-height:1.9;color:var(--grafite)}"
        ".t22l .leg i{display:inline-block;width:14px;height:14px;margin-right:8px;vertical-align:-2px}"
        ".t22l .ex{position:absolute;left:0;top:254px;font-size:14px;color:var(--grafite);line-height:1.45}"
        ".t22l .ex i{display:inline-block;width:14px;height:14px;outline:2px dashed var(--tinta);outline-offset:-3px;"
        "margin-right:8px;vertical-align:-2px}"
        ".t22l .dica{position:absolute;left:0;top:330px;width:280px;font-size:15px;line-height:1.45}"
        ".t22l img{position:absolute;left:0;top:430px;width:52px;opacity:.85}"
        ".t22l .mao{position:absolute;left:60px;top:440px;font-size:24px;transform:rotate(-3deg)}"
    )
    return (f"<style>{css}</style><div class='tela t22l'><div class='rot sobe'>Quem fica à frente em cada UF, no "
            f"cenário</div><div class='leg entra d3'>{leg}</div>"
            f"<div class='ex entra d4'><i></i>EX = votos do exterior</div>"
            f"<div class='dica sobe d5'>Passe o mouse num estado: o dossiê mostra o cenário ao lado do 1º turno e o "
            f"peso dos outros candidatos ali.</div>"
            f"<img class='entra d6' alt='' src='{clipe}'/><div class='mao entra d8'>conta voto, não estado</div>"
            f"</div>{{{{content}}}}")


CSS_TOOLTIP = (
    ".tt22{background:var(--branco);padding:24px 24px 14px 24px;border:1.5px solid var(--areia)}"
    ".tt22 .nm{font-size:22px;font-weight:700;padding-right:40px}"
    ".tt22 .rot{margin-top:12px;font-size:11px}"
    ".tt22 .duelo{margin-top:2px;display:flex;gap:22px;font-size:22px;font-weight:700}"
    ".tt22 .duelo.menor{font-size:16px;font-weight:600}"
    ".tt22 .pe{margin-top:12px;font-size:14px;line-height:1.4;color:var(--grafite);padding-right:6px}"
    ".tt22 .mao{position:absolute;right:20px;bottom:6px;font-size:25px;color:var(--vermelho-escuro);"
    "transform:rotate(-2deg)}"
    ".tt22c{position:fixed;right:16px;top:-8px;width:34px;z-index:2;pointer-events:none}"
)


def corpo_tooltip() -> str:
    clipe = estilo.imagem_b64("docs/midia/arte/dossie/clipe-tinta.png", 50)
    return f"<style>{CSS_TOOLTIP}</style>{{{{content}}}}<img class='tt22c' alt='' src='{clipe}'/>"


def main() -> int:
    medidas()
    print(f"T22: medidas de desenho em {DAX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
