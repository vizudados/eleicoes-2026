# -*- coding: utf-8 -*-
"""desenho_t20 — tela 20 · Escola (dono: tela 20). Gera as medidas de desenho (HTML e ALT) em
pbi/dax/T20 Escola/Desenho/*.dax — só leem as contas de T20 Escola\\Contas — e expõe para paginas/t20_escola.py os
modelos fixos (bodyTemplate): o filtro do rabisco do contorno, o papel da ficha (post-it com alfinete), o cabeçalho da
lista, a legenda de "como explorar" e o post-it do tooltip.

Desde 23/10/2026 a tela vale para 34 cidades (as 27 capitais, as 6 maiores que trocaram Lula por Flávio e Contagem):
o contorno, a moldura do mapa, os rótulos de bairro e o mapinha do recorte vêm do dado (T20 Cidade, de
pipeline/exportar_t20.py), não mais de um desenho fixo de Contagem. A moldura de cada cidade tem a proporção da caixa
do mapa (MAPA_W × MAPA_H), então o contorno e os pontos vão em % da caixa sem distorcer.

    python -I -X utf8 pbi/scripts/desenho_t20.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import estilo  # noqa: E402

PBI = AQUI.parent
RAIZ = PBI.parent
DAX = PBI / "dax" / "T20 Escola" / "Desenho"
PASTA = r"T20 Escola\Desenho"

MAPA_W, MAPA_H = 692, 860              # a caixa do mapa; pipeline/exportar_t20.py enquadra cada cidade nesta proporção
QUEDAS_TOPO, QUEDAS_H = 70, 88
MINI = 132                             # lado do mapinha do recorte (cidade inteira), em px
# margem 2026 do local → cor, simétrica (Lula e Flávio com as mesmas faixas): até ±3, ±10, ±20 pontos e além
FAIXAS = [(-0.20, "#1D3C6E"), (-0.10, "#2B5797"), (-0.03, "#6F8DBE"), (0.0, "#A9B8CF"), (0.03, "#E2B3A9"),
          (0.10, "#D9877B"), (0.20, "#B8322A"), (99, "#8E2620")]


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


def _no_local(medida: str) -> str:
    """A conta no local da ficha (Id escolhido), sem o filtro do clique."""
    return f"CALCULATE ( {medida}, REMOVEFILTERS ( 'T20 Local' ), 'T20 Local'[Id] = _id )"


PP = '"+0.0;−0.0;0.0"'
N = '"#,0"'


def medidas() -> None:
    gravar("T20 · Resposta · HTML", "A resposta da tela na cidade escolhida: '12 de 112' locais de votação com Lula à "
           "frente em 2026 (contador), quantos eram em 2022 e quantos viraram, nos dois sentidos.", rf"""
-- 1 · Leituras
VAR _lula = [T20 · locais com Lula à frente]
VAR _n = [T20 · locais]
VAR _lula22 = [T20 · locais com Lula à frente em 2022]
VAR _n22 = [T20 · locais em 2022]
VAR _viraram = [T20 · locais que viraram]
VAR _paraLula = [T20 · locais que viraram para Lula]
-- 2 · Textos
{_escapa("_cidade", "[T20 · cidade]")}
VAR _rotLocal = IF ( _lula = 1, "zona eleitoral com Lula à frente em 2026", "zonas eleitorais com Lula à frente em 2026" )
VAR _antes =
    SWITCH (
        TRUE (),
        _lula22 = 0 && _lula = 0, "Em 2022, também nenhuma",
        _lula22 = 0, "Em 2022, nenhuma",
        _lula22 = 1, "Em 2022, <span class='num'>1</span>",
        "Em 2022, eram <span class='num'>" & FORMAT ( _lula22, {N} ) & "</span>"
    ) & IF ( _n22 = 1, " na única zona.", " das " & FORMAT ( _n22, {N} ) & " zonas." )
VAR _txtViraram =
    SWITCH (
        TRUE (),
        -- sem virada nos dois sentidos, a frase fala dos dois (revisão do vídeo, 24/10/2026)
        _viraram = 0 && _paraLula = 0, "Nenhuma zona da cidade mudou de lado",
        _viraram = 0, "Nenhuma zona virou de Lula para Flávio",
        _viraram = 1, "1 zona virou de Lula para Flávio",
        FORMAT ( _viraram, {N} ) & " zonas viraram de Lula para Flávio"
    ) & SWITCH (
        TRUE (),
        _paraLula = 0, ".",
        _paraLula = 1, "; 1 fez o caminho inverso.",
        "; " & FORMAT ( _paraLula, {N} ) & " fizeram o caminho inverso."
    )
-- 3 · Geometria (com milhar, o número grande desce de 96 para 72 px e cabe na caixa)
VAR _classe = IF ( _n >= 1000, "grande g4", "grande" ) -- geometria
-- 4 · Marcação
RETURN
    "<div class='tela t20r'>"
        & "<div class='rot cid sobe'>" & _cidade & "</div>"
        & "<div class='" & _classe & " sobe d1'><span class='num'>" & FORMAT ( _lula, {N} ) & "</span> de "
            & "<span class='num'>" & FORMAT ( _n, {N} ) & "</span></div>"
        & "<div class='fluxo'>"
            & "<div class='rotulo sobe d2'>" & _rotLocal & "</div>"
            & "<div class='man sobe d3'>" & _antes & "</div>"
            & "<div class='txt sobe d4'>" & _txtViraram & "</div>"
        & "</div>"
    & "</div>"
""")
    gravar("T20 · Resposta · ALT", "Texto alternativo da resposta da tela 20.", rf"""
-- 1 · Leituras
VAR _lula = [T20 · locais com Lula à frente]
VAR _n = [T20 · locais]
VAR _lula22 = [T20 · locais com Lula à frente em 2022]
VAR _n22 = [T20 · locais em 2022]
VAR _viraram = [T20 · locais que viraram]
VAR _paraLula = [T20 · locais que viraram para Lula]
RETURN
    [T20 · cidade] & ": Lula ficou à frente em " & FORMAT ( _lula, {N} ) & " das " & FORMAT ( _n, {N} )
        & " zonas eleitorais em 2026; em 2022, em " & FORMAT ( _lula22, {N} ) & " das " & FORMAT ( _n22, {N} )
        & ". " & FORMAT ( _viraram, {N} ) & IF ( _viraram = 1, " zona virou", " zonas viraram" )
        & " de Lula para Flávio e " & FORMAT ( _paraLula, {N} ) & " de Flávio para Lula."
""")
    # --- ponto do mapa (um por local da cidade); o último ponto da cidade leva os rótulos de bairro, por cima de tudo
    gravar("T20 · Mapa · HTML", "Um ponto do mapa da cidade escolhida (granularidade: T20 Local[Local]; local de outra "
           "cidade ou sem posição devolve vazio): posição PX/PY em % da moldura, tamanho pelos votos válidos e pelo "
           "espaço entre locais da cidade (São Paulo não vira mancha), cor pela margem de 2026; brota em onda do oeste "
           "para o leste. O último local da cidade no mapa leva também os rótulos de bairro, e o local da ficha sem clique "
           "(a escola do filtro ou o exemplo) leva o nome dele, numa camada por cima dos pontos (z-index na entrada: "
           "não depende da ordem em que o visual entrega as linhas; em São Paulo o nome atrás dos pontos sumia).", rf"""
-- 1 · Leituras
VAR _na = [T20 · na cidade]
VAR _px = [T20 · posição x]
VAR _py = [T20 · posição y]
VAR _val = [T20 · válidos 2026]
VAR _maior = [T20 · maior válidos]
VAR _m26 = [T20 · margem 2026]
VAR _espaco = [T20 · cidade · espaço entre locais]
VAR _id = [T20 · id do local]
VAR _ultimo = [T20 · último local do mapa] = _id
VAR _bairros = IF ( _ultimo, [T20 · cidade · bairros] )
VAR _alvo = [T20 · local da ficha sem clique] = _id
-- 2 · Textos
{_escapa("_nome", "IF ( _alvo, [T20 · nome do local] )")}
VAR _cor =
    {_cor("_m26")}
VAR _rotulos =
    IF (
        _ultimo && NOT ISBLANK ( _bairros ) && _bairros <> "",
        CONCATENATEX (
            GENERATESERIES ( 1, PATHLENGTH ( _bairros ) ),
            VAR _item = SUBSTITUTE ( PATHITEM ( _bairros, [Value] ), "@", "|" )
            VAR _nome0 = PATHITEM ( _item, 1 )
            VAR _nome = SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( _nome0, "&", "&amp;" ), "<", "&lt;" ), "'", "&#39;" )
            RETURN
                "<span class='bairro entra d" & ( 10 + [Value] ) & "' style='left:" & PATHITEM ( _item, 2 ) & "%;top:"
                    & PATHITEM ( _item, 3 ) & "%'>" & _nome & "</span>",
            "",
            [Value], ASC
        ) /* lista */
    )
-- 3 · Geometria (diâmetro: o maior ponto ocupa ~2,2 vezes o espaço típico entre vizinhos, de 4,5 a 16 px: raio de
-- até 8 px, para o ponto grande não pesar nas cidades de pouca escola)
VAR _dmax = MIN ( 16, MAX ( 4.5, 2.2 * _espaco / 100 * {MAPA_W} ) ) -- geometria
VAR _dmin = MAX ( 2.5, _dmax * 0.35 ) -- geometria
VAR _d = _dmin + ( _dmax - _dmin ) * SQRT ( DIVIDE ( _val, _maior ) ) -- geometria
VAR _borda = MIN ( 1.2, _d / 6 ) -- geometria
VAR _x = _px / 100 * {MAPA_W} - _d / 2 -- geometria
VAR _y = _py / 100 * {MAPA_H} - _d / 2 -- geometria
VAR _atraso = 1700 + ROUND ( _px * 14, 0 ) -- geometria
VAR _cx = _px / 100 * {MAPA_W} -- geometria
VAR _direita = _cx > {MAPA_W} * 0.62 -- geometria
VAR _xr = IF ( _direita, _cx - 22, _cx + 22 ) -- geometria
-- 4 · Marcação
VAR _rotuloEscola =
    IF (
        _alvo,
        "<div class='nome sobe d4" & IF ( _direita, " dir", "" ) & "' style='left:" & FORMAT ( _xr, "0.0##", "en-US" )
            & "px;top:" & FORMAT ( _py / 100 * {MAPA_H} - 12, "0.0##", "en-US" ) & "px'>" & _nome & "</div>"
    )
RETURN
    IF (
        _na = 1 && NOT ISBLANK ( _px ),
        "<div class='tela t20p" & IF ( _ultimo || _alvo, " topo", "" ) & "'><i class='pt' style='left:"
            & FORMAT ( _x, "0.0##", "en-US" ) & "px;top:"
            & FORMAT ( _y, "0.0##", "en-US" ) & "px;width:" & FORMAT ( _d, "0.0##", "en-US" ) & "px;height:"
            & FORMAT ( _d, "0.0##", "en-US" ) & "px;border-width:" & FORMAT ( _borda, "0.0##", "en-US" )
            & "px;background:" & _cor & ";animation-delay:" & _atraso & "ms'></i>"
            & _rotulos & _rotuloEscola
        & "</div>"
    )
""")
    gravar("T20 · Mapa · ALT", "Texto alternativo do mapa das zonas eleitorais.", rf"""
-- 1 · Leituras
VAR _n = [T20 · locais]
VAR _lula = [T20 · locais com Lula à frente]
VAR _fora = [T20 · locais sem endereço] + [T20 · locais fora do recorte]
RETURN
    "Mapa de " & [T20 · cidade] & " com " & FORMAT ( _n - _fora, {N} ) & " das " & FORMAT ( _n, {N} )
        & " zonas eleitorais: " & FORMAT ( _lula, {N} ) & " com Lula à frente (vermelho) e as outras com Flávio "
        & "(azul). Passe o mouse num ponto para ver a zona; clique para pôr na ficha."
""")
    # --- o mapa de fundo: contorno da cidade em rabisco, mapinha do recorte e o anel do local da ficha
    gravar("T20 · Escolhido · HTML", "A camada atrás dos pontos: o contorno da cidade escolhida (rabisco que se desenha, "
           "o creme esmaece), o mapinha da cidade inteira quando o mapa é um recorte e o anel à mão em volta do local "
           "da ficha (recebe a escolha do filtro, do mapa e da lista); o nome vai ao lado só quando a escola veio de um "
           "clique (com clique, os outros pontos esmaecem e o nome aparece; sem clique, o nome vai na camada da frente, "
           "em T20 · Mapa · HTML).", rf"""
-- 1 · Leituras
VAR _contorno = [T20 · cidade · contorno]
VAR _recorte = [T20 · cidade · recorte]
VAR _mapinha = [T20 · cidade · mapinha]
VAR _moldura = SUBSTITUTE ( [T20 · cidade · moldura do mapinha], " ", "|" )
VAR _canto = [T20 · cidade · canto do mapinha]
VAR _id = [T20 · id escolhido]
VAR _px = {_no_local("[T20 · posição x]")}
VAR _py = {_no_local("[T20 · posição y]")}
VAR _fora = {_no_local("[T20 · fora do mapa]")}
VAR _clique = NOT ISBLANK ( [T20 · escola clicada] )
-- 2 · Textos
{_escapa("_nome", "[T20 · local escolhido]")}
VAR _motivo = IF ( _fora = "fora do recorte", ": fora do recorte do mapa", ": sem endereço no mapa" )
-- 3 · Geometria
VAR _x = _px / 100 * {MAPA_W} -- geometria
VAR _y = _py / 100 * {MAPA_H} -- geometria
VAR _direita = _x > {MAPA_W} * 0.62 -- geometria
VAR _xr = IF ( _direita, _x - 22, _x + 22 ) -- geometria
VAR _mx = IF ( _canto = "so" || _canto = "no", 10, {MAPA_W - MINI - 10} ) -- geometria
VAR _my = IF ( _canto = "no" || _canto = "ne", 10, {MAPA_H - MINI - 46} ) -- geometria
-- 4 · Marcação
VAR _mapa =
    "<svg class='mapa" & IF ( _recorte = 1, " rec", "" ) & "' width='{MAPA_W}' height='{MAPA_H}' viewBox='0 0 100 100' "
        & "preserveAspectRatio='none'>"
        & "<path class='fundo' d='" & _contorno & "'/>"
        & "<path class='borda traco' pathLength='1' filter='url(#rb20)' d='" & _contorno & "'/>"
        & IF ( _recorte = 1, "<rect class='quadro' x='0' y='0' width='100' height='100'/>" )
    & "</svg>"
VAR _mini =
    IF (
        _recorte = 1,
        "<div class='mini entra d8' style='left:" & _mx & "px;top:" & _my & "px'>"
            & "<svg width='{MINI}' height='{MINI}' viewBox='0 0 100 100'><path class='mf' d='" & _mapinha & "'/>"
            & "<rect class='mr' x='" & PATHITEM ( _moldura, 1 ) & "' y='" & PATHITEM ( _moldura, 2 ) & "' width='"
            & PATHITEM ( _moldura, 3 ) & "' height='" & PATHITEM ( _moldura, 4 ) & "'/></svg>"
            & "<span>a cidade inteira</span>"
        & "</div>"
    )
VAR _anel =
    IF (
        ISBLANK ( _px ),
        "<div class='sem'>" & _nome & _motivo & "</div>",
        "<div class='anel' style='left:" & FORMAT ( _x - 26, "0.0##", "en-US" ) & "px;top:"
            & FORMAT ( _y - 24, "0.0##", "en-US" ) & "px'>"
            & "<svg width='52' height='48' viewBox='0 0 52 48'><path class='traco' pathLength='1' filter='url(#rbe)' "
            & "d='M8,28 C2,10 30,-2 44,10 C54,20 46,42 26,44 C8,46 2,30 12,16 C18,8 30,6 38,9'/></svg></div>"
            & IF (
                _clique,
                "<div class='nome sobe d4" & IF ( _direita, " dir", "" ) & "' style='left:"
                    & FORMAT ( _xr, "0.0##", "en-US" ) & "px;top:" & FORMAT ( _y - 12, "0.0##", "en-US" ) & "px'>"
                    & _nome & "</div>"
            )
    )
RETURN
    "<div class='tela t20e'>" & _mapa & _mini & _anel & "</div>"
""")
    gravar("T20 · Escolhido · ALT", "Texto alternativo do anel do local escolhido.", r"""
"Mapa de " & [T20 · cidade] & "; zona em destaque: " & [T20 · local escolhido]
""")
    # --- ficha (post-it)
    gravar("T20 · Ficha · HTML", "A ficha do local escolhido (post-it com alfinete): bairro, seções e válidos, Lula × "
           "Flávio em 2026 e a margem do PT em 2018 → 2022 → 2026 (Haddad em 2018), com o selo de quem virou. Sem "
           "escolha, o exemplo "
           "da cidade: em todas, a "
           "escola que virou com mais votos válidos (ou a de maior queda).", ficha())
    gravar("T20 · Ficha · ALT", "Texto alternativo da ficha do local.", rf"""
-- 1 · Leituras
VAR _id = [T20 · id escolhido]
VAR _m18 = {_no_local("[T20 · margem 2018]")}
VAR _m22 = {_no_local("[T20 · margem 2022]")}
VAR _m26 = {_no_local("[T20 · margem 2026]")}
-- 2 · Textos
VAR _t18 = IF ( ISBLANK ( _m18 ), "sem dado", FORMAT ( _m18 * 100, {PP} ) )
VAR _t22 = IF ( ISBLANK ( _m22 ), "sem dado", FORMAT ( _m22 * 100, {PP} ) )
RETURN
    "Ficha: " & [T20 · local escolhido] & " (" & [T20 · cidade] & "). Margem do PT em pontos (Haddad em 2018, Lula em 2022 e 2026): 2018 " & _t18
        & "; 2022 " & _t22 & "; 2026 " & FORMAT ( _m26 * 100, {PP} ) & "."
""")
    # --- lista dos locais pela queda
    gravar("T20 · Quedas · HTML", "Uma linha da lista de todos os locais da cidade escolhida, da maior queda à maior "
           "alta da margem de Lula, 2022 → 2026 (granularidade T20 Local[Local]; local de outra cidade devolve vazio): "
           "posição, nome, bairro e seções, a variação (ou 'novo', sem 2022) e o selo de quem virou. A ordem vem da "
           "posição (order no CSS, com quatro dígitos: a lista não depende da ordem em que o visual entrega as linhas) "
           "e a lista rola dentro da caixa.", rf"""
-- 1 · Leituras
VAR _na = [T20 · na cidade]
VAR _pos = [T20 · posição na queda]
VAR _bairroL = [T20 · bairro]
VAR _secoes = [T20 · seções]
VAR _var = [T20 · variação da margem]
VAR _virou = [T20 · virou] + [T20 · virou para Lula]
-- 2 · Textos
{_escapa("_nome", "[T20 · nome do local]")}
{_escapa("_bairro", "_bairroL")}
VAR _txtVar = IF ( ISBLANK ( _var ), "novo", FORMAT ( _var * 100, {PP} ) & " p.p." )
VAR _sub =
    IF ( _bairro <> "", _bairro & " · ", "" ) & _secoes & IF ( _secoes = 1, " seção", " seções" )
VAR _selo = IF ( _virou = 1, "<span class='selo'>virou</span>", "" )
VAR _cor = IF ( ISBLANK ( _var ), "novo", IF ( _var < 0, "flavio", "lula" ) )
-- 3 · Geometria (a ordem na lista e a cascata de entrada das primeiras linhas)
VAR _ordem = FORMAT ( _pos, "0000" ) -- geometria
VAR _d = MIN ( _pos + 2, 12 ) -- geometria
-- 4 · Marcação
RETURN
    IF (
        _na = 1 && NOT ISBLANK ( _pos ),
        "<div class='t20q' style='order:" & _ordem & "'><div class='ln sobe d" & _d & "' data-p='" & _pos & "'>"
            & "<span class='p'>" & _pos & "</span>"
            & "<span class='dir'><span class='v " & _cor & " tnum'>" & _txtVar & "</span></span>"
            & "<span class='nm'>" & _nome & "</span>"
            & "<span class='sb'><span class='bt'>" & _sub & "</span>" & _selo & "</span>"
        & "</div></div>"
    )
""")
    gravar("T20 · Quedas · ALT", "Texto alternativo da lista dos locais pela queda.", rf"""
"Os " & FORMAT ( [T20 · locais], {N} ) & " zonas eleitorais de " & [T20 · cidade]
    & ", da maior queda à maior alta da margem de Lula de 2022 para 2026; a lista rola. Clique numa linha para pôr a zona na ficha."
""")
    # --- o aviso honesto do mapa (no cartão "como explorar")
    gravar("T20 · Como · HTML", "O aviso do cartão 'como explorar', por cidade: quantos locais não aparecem no mapa (sem "
           "endereço no cadastro do TSE ou fora do recorte da mancha urbana) e que eles entram nas contas e na lista.",
           rf"""
-- 1 · Leituras
VAR _sem = [T20 · locais sem endereço]
VAR _fora = [T20 · locais fora do recorte]
-- 2 · Textos
VAR _txtSem = FORMAT ( _sem, {N} ) & IF ( _sem = 1, " zona sem endereço", " zonas sem endereço" )
VAR _txtFora = FORMAT ( _fora, {N} ) & IF ( _fora = 1, " zona fora do recorte", " zonas fora do recorte" )
VAR _quem =
    SWITCH (
        TRUE (),
        _sem > 0 && _fora > 0, _txtSem & " e " & FORMAT ( _fora, {N} ) & " fora do recorte não aparecem no mapa",
        _sem > 0, _txtSem & IF ( _sem = 1, " não aparece no mapa", " não aparecem no mapa" ),
        _fora > 0, _txtFora & IF ( _fora = 1, " não aparece no mapa", " não aparecem no mapa" )
    )
VAR _nota =
    IF (
        _sem + _fora > 0,
        _quem & IF ( _sem + _fora = 1, ", mas entra nas contas e na lista.", ", mas entram nas contas e na lista." ),
        "Todas as zonas da cidade estão no mapa."
    )
-- 4 · Marcação
RETURN
    "<div class='tela t20n'><div class='nota entra d6'>" & _nota & "</div></div>"
""")
    gravar("T20 · Como · ALT", "Texto alternativo do cartão 'como explorar'.", r"""
"Como explorar: passe o mouse num ponto para ver a zona; clique num ponto ou numa linha para levá-la à ficha; o filtro do topo troca a cidade e procura a zona. "
    & IF ( [T20 · locais sem endereço] + [T20 · locais fora do recorte] > 0,
        FORMAT ( [T20 · locais sem endereço] + [T20 · locais fora do recorte], "#,0" ) & " zonas não aparecem no mapa.", "" )
""")
    # --- tooltip (post-it do hover)
    gravar("T20 · Tooltip escola · HTML", "Post-it do local sob o mouse (página de tooltip ttT20Escola): bairro, "
           "seções, Lula × Flávio em 2026 e a margem do PT em 2018 → 2022 → 2026 (Haddad em 2018).", tooltip())
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
    gravar("T20 · Filtro · ALT", "Texto alternativo do filtro da tela (o VizuFilter em árvore, com o gatilho dele; sem pílula desde 24/10/2026): a cidade e a escola em uso.", rf"""
-- 1 · Leituras
VAR _escola = [T20 · escola do filtro]
VAR _marcadas = [T20 · escolas no filtro]
VAR _locais = [T20 · locais]
VAR _id = _escola
RETURN
    "Filtro de cidade e zona: " & [T20 · cidade]
        & SWITCH (
            TRUE (),
            NOT ISBLANK ( _escola ), " · " & {_no_local("[T20 · nome do local]")},
            _marcadas > 1 && _marcadas < _locais, " · " & FORMAT ( _marcadas, {N} ) & " zonas marcadas",
            " (nenhuma zona escolhida)"
        )
""")


def ficha() -> str:
    return rf"""
-- 1 · Leituras
VAR _id = [T20 · id escolhido]
VAR _ha = [T20 · há escolha]
VAR _exemplo = [T20 · exemplo]
VAR _bairroL = {_no_local("[T20 · bairro]")}
VAR _secoes = {_no_local("[T20 · seções]")}
VAR _val = {_no_local("[T20 · válidos 2026]")}
VAR _lula = {_no_local("[T20 · Lula % 2026]")}
VAR _flavio = {_no_local("[T20 · Flávio % 2026]")}
VAR _m18 = {_no_local("[T20 · margem 2018]")}
VAR _m22 = {_no_local("[T20 · margem 2022]")}
VAR _m26 = {_no_local("[T20 · margem 2026]")}
VAR _virou = {_no_local("[T20 · virou]")}
VAR _virouLula = {_no_local("[T20 · virou para Lula]")}
-- 2 · Textos
{_escapa("_nome", "[T20 · local escolhido]")}
{_escapa("_bairro", "_bairroL")}
{_escapa("_cidade", "[T20 · cidade (nome)]")}
VAR _sobre = IF ( _ha = 1, "A zona escolhida", "Um exemplo · " & _cidade )
-- a zona: quantos locais de votação (a coluna Bairro), seções e válidos de 2026, numa linha só
VAR _sub =
    IF ( _bairro <> "", _bairro & " · ", "" ) & _secoes & IF ( _secoes = 1, " seção · ", " seções · " )
        & FORMAT ( _val, "#,0" ) & " válidos"
VAR _t18 = IF ( ISBLANK ( _m18 ), "—", FORMAT ( _m18 * 100, {PP} ) )
VAR _t22 = IF ( ISBLANK ( _m22 ), "—", FORMAT ( _m22 * 100, {PP} ) )
VAR _t26 = FORMAT ( _m26 * 100, {PP} )
VAR _c18 = IF ( _m18 > 0, "lula", IF ( _m18 < 0, "flavio", "" ) )
VAR _c22 = IF ( _m22 > 0, "lula", IF ( _m22 < 0, "flavio", "" ) )
VAR _c26 = IF ( _m26 > 0, "lula", IF ( _m26 < 0, "flavio", "" ) )
VAR _nota =
    SWITCH (
        TRUE (),
        _ha = 0 && _exemplo = "virou", "a maior zona que virou",
        _ha = 0, "a maior queda da cidade",
        _virou = 1, "virou para Flávio",
        _virouLula = 1, "virou para Lula",
        _m26 > 0, "Lula à frente",
        _m26 < 0, "Flávio à frente",
        "empate"
    )
VAR _selo = IF ( _virou + _virouLula = 1, "<div class='selo'>virou</div>", "" )
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
    "<div class='tela t20f'><div class='fl'>"
        & "<div class='rot sobe'>" & _sobre & "</div>"
        & "<div class='nm sobe d1'>" & _nome & "</div>"
        & "<div class='sub sobe d2'>" & _sub & "</div>"
        & "<div class='duelo sobe d3'>"
            & "<div class='lado lula'><span class='num'>" & FORMAT ( _lula, "0.0%" ) & "</span><span class='r'>Lula</span></div>"
            & "<div class='lado flavio'><span class='num'>" & FORMAT ( _flavio, "0.0%" ) & "</span><span class='r'>Flávio</span></div>"
            & _selo
        & "</div>"
        & "<div class='rot cap sobe d4'>Margem do PT, em pontos</div>"
        & "<div class='serie sobe d5'>"
            & "<div class='c c0'><span class='a'>2018</span><span class='num " & _c18 & "'>" & _t18 & "</span></div>"
            & "<div class='c c1'><span class='a'>2022</span><span class='num " & _c22 & "'>" & _t22 & "</span></div>"
            & "<div class='c c2'><span class='a'>2026</span><span class='num " & _c26 & "'>" & _t26 & "</span></div>"
            & "<svg class='linha' width='460' height='70' viewBox='0 0 460 70'>"
                & "<line class='zero' x1='20' x2='440' y1='34' y2='34'/>"
                & "<path class='traco' pathLength='1' d='" & _d & "'/>" & _bolas
            & "</svg>"
        & "</div>"
        & "</div>"
        & "<div class='mao'>" & _nota & "</div>"
    & "</div>"
"""


def tooltip() -> str:
    return rf"""
-- 1 · Leituras
VAR _bairroL = [T20 · bairro]
VAR _secoes = [T20 · seções]
VAR _val = [T20 · válidos 2026]
VAR _lula = [T20 · Lula % 2026]
VAR _flavio = [T20 · Flávio % 2026]
VAR _m18 = [T20 · margem 2018]
VAR _m22 = [T20 · margem 2022]
VAR _m26 = [T20 · margem 2026]
VAR _virou = [T20 · virou]
VAR _virouLula = [T20 · virou para Lula]
-- 2 · Textos
{_escapa("_nome", "[T20 · nome do local]")}
{_escapa("_bairro", "_bairroL")}
VAR _sub =
    IF ( _bairro <> "", _bairro & " · ", "" ) & _secoes & IF ( _secoes = 1, " seção · ", " seções · " )
        & FORMAT ( _val, "#,0" ) & " válidos"
VAR _t18 = IF ( ISBLANK ( _m18 ), "—", FORMAT ( _m18 * 100, {PP} ) )
VAR _t22 = IF ( ISBLANK ( _m22 ), "—", FORMAT ( _m22 * 100, {PP} ) )
VAR _t26 = FORMAT ( _m26 * 100, {PP} )
VAR _nota =
    SWITCH (
        TRUE (),
        _virou = 1, "virou para Flávio",
        _virouLula = 1, "virou para Lula",
        _m26 > 0, "Lula à frente",
        _m26 < 0, "Flávio à frente",
        "empate"
    )
VAR _selo = IF ( _virou + _virouLula = 1, "<div class='selo'>virou</div>", "" )
-- 4 · Marcação
RETURN
    IF (
        NOT ISBLANK ( _nome0 ),
        "<div class='tela tt20'>"
            & "<div class='nm'>" & _nome & "</div>"
            & "<div class='sub'>" & _sub & "</div>"
            & "<div class='duelo'><span class='lula'>Lula " & FORMAT ( _lula, "0.0%" ) & "</span>"
            & "<span class='flavio'>Flávio " & FORMAT ( _flavio, "0.0%" ) & "</span></div>"
            & "<div class='rot'>Margem do PT · 2018 → 2022 → 2026</div>"
            & "<div class='serie tnum'>" & _t18 & " <i>→</i> " & _t22 & " <i>→</i> " & _t26 & " p.p.</div>"
            & _selo
            & "<div class='mao'>" & _nota & "</div>"
        & "</div>"
    )
"""


# ---------------------------------------------------------------------------------------------------- modelos fixos
CSS_RESPOSTA = (
    ".t20r .cid{position:absolute;left:0;top:0;right:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".t20r .grande{position:absolute;left:0;top:22px;font-size:96px;font-weight:700;letter-spacing:-.045em;"
    "line-height:1;white-space:nowrap}"
    ".t20r .grande .num{font-size:96px}"
    ".t20r .grande.g4{top:34px;font-size:72px}.t20r .grande.g4 .num{font-size:72px}"
    ".t20r .fluxo{position:absolute;left:0;top:126px;right:0}"
    ".t20r .rotulo{font-size:18px;font-weight:600;color:var(--grafite)}"
    ".t20r .man{margin-top:12px;font-size:24px}"
    ".t20r .man .num{font-size:24px;font-weight:600;letter-spacing:-.01em}"
    ".t20r .txt{margin-top:10px;font-size:15px;line-height:1.4}"
)


def corpo_resposta() -> str:
    return f"<style>{CSS_RESPOSTA}</style>{{{{content}}}}"


def corpo_mapa() -> str:
    """Os pontos ({{content}}, um por local) e, no último ponto da cidade, os rótulos de bairro. O contorno vai na
    camada de trás (corpo_escolhido), que tem o filtro do rabisco."""
    css = (
        ".t20p{pointer-events:none}"
        ".t20p .pt{position:absolute;display:block;border-radius:50%;border:1.2px solid var(--papel);"
        "pointer-events:auto;cursor:pointer;transition:transform .15s;animation:t20Brota .6s cubic-bezier(.2,.9,.3,1.3) "
        "both}"
        ".t20p .pt:hover{transform:scale(1.6);border-color:var(--tinta)!important;z-index:3}"
        "@keyframes t20Brota{from{opacity:0;transform:scale(.3)}}"
        ".t20p.topo{z-index:2}"
        ".t20p .nome{position:absolute;max-width:210px;font-size:14px;font-weight:600;line-height:1.25;"
        "color:var(--tinta);background:rgba(241,235,223,.9);padding:2px 6px;pointer-events:none;"
        "animation-delay:2.8s!important}"
        ".t20p .nome.dir{transform:translateX(-100%)}"
        ".t20p .bairro{position:absolute;transform:translate(-50%,-50%);font-size:12px;font-weight:600;"
        "letter-spacing:.12em;text-transform:uppercase;color:var(--grafite);white-space:nowrap;"
        "background:rgba(241,235,223,.82);padding:0 4px;pointer-events:none}"
    )
    return f"<style>{css}</style>{{{{content}}}}"


def corpo_escolhido() -> str:
    css = (
        ".t20e{pointer-events:none}"
        ".t20e svg.mapa{position:absolute;left:0;top:0}"
        ".t20e svg.mapa .fundo{fill:var(--creme);fill-rule:evenodd;stroke:none;animation:uEntra 1.2s ease-out 1.2s both}"
        ".t20e svg.mapa .borda{fill:none;stroke:var(--tinta);stroke-width:.32;stroke-linejoin:round}"
        # no recorte, o mapa é um quadro de zoom: o creme e o contorno cortados pela moldura, com borda fina e nítida
        # na cor do retângulo do mapinha (o mesmo recorte)
        ".t20e svg.mapa.rec{overflow:hidden}"
        ".t20e svg.mapa .quadro{fill:none;stroke:var(--vermelho-escuro);stroke-width:3;vector-effect:non-scaling-stroke;"
        "animation:uEntra .8s ease-out 1s both}"
        f".t20e .mini{{position:absolute;width:{MINI}px;background:rgba(241,235,223,.92);padding:0}}"
        ".t20e .mini svg{display:block;overflow:hidden}"
        ".t20e .mini .mf{fill:var(--creme);fill-rule:evenodd;stroke:var(--grafite);stroke-width:.9;"
        "stroke-linejoin:round}"
        ".t20e .mini .mr{fill:rgba(142,38,32,.12);stroke:var(--vermelho-escuro);stroke-width:2.2}"
        ".t20e .mini span{display:block;margin-top:4px;font-size:12px;font-weight:600;letter-spacing:.12em;"
        "text-transform:uppercase;color:var(--grafite);text-align:center}"
        ".t20e .anel{position:absolute;width:52px;height:48px}"
        ".t20e .anel path{fill:none;stroke:var(--tinta);stroke-width:2.4;stroke-linecap:round;animation-delay:2.6s}"
        ".t20e .nome{position:absolute;max-width:210px;font-size:14px;font-weight:600;line-height:1.25;"
        "color:var(--tinta);background:rgba(241,235,223,.85);padding:2px 6px;animation-delay:2.8s!important}"
        ".t20e .nome.dir{transform:translateX(-100%)}"
        ".t20e .sem{position:absolute;left:8px;top:8px;max-width:420px;font-size:15px;color:var(--grafite);"
        "background:rgba(241,235,223,.9);padding:2px 6px}"
    )
    return (f"<style>{css}</style><svg width='0' height='0' style='position:absolute'>"
            f"{estilo.defs_rabisco('rb20', 0.5, 0.6)}{estilo.defs_rabisco('rbe', 1.4)}</svg>{{{{content}}}}")


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
        # em fluxo (pedido de 23/10/2026: sem vão entre o nome e a linha de baixo): o nome tem uma ou duas linhas e o
        # resto sobe junto; só a nota à mão fica presa no pé do papel
        ".t20f .fl{position:absolute;left:0;top:0;right:0}"
        ".t20f .rot{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:60px}"
        ".t20f .nm{margin-top:6px;padding-right:70px;font-size:26px;font-weight:700;line-height:1.15;"
        "display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
        ".t20f .sub{margin-top:6px;font-size:15px;line-height:1.35;color:var(--grafite);white-space:nowrap;"
        "overflow:hidden;text-overflow:ellipsis}"
        ".t20f .duelo{position:relative;margin-top:18px;height:70px}"
        ".t20f .duelo .lado{position:absolute;top:0;display:flex;flex-direction:column}"
        ".t20f .duelo .lado .num{font-size:44px}.t20f .duelo .lado .r{font-size:15px;font-weight:600;margin-top:4px}"
        ".t20f .duelo .lula{left:0}.t20f .duelo .flavio{left:190px}"
        ".t20f .cap{margin-top:28px;padding-right:0}"
        ".t20f .serie{position:relative;margin-top:10px;height:160px}"
        ".t20f .serie .c{position:absolute;top:0;width:150px;display:flex;flex-direction:column;align-items:center}"
        ".t20f .serie .c0{left:-5px}.t20f .serie .c1{left:155px}.t20f .serie .c2{left:315px}"
        ".t20f .serie .a{font-size:13px;font-weight:600;letter-spacing:.12em;color:var(--cinza)}"
        ".t20f .serie .num{font-size:38px;margin-top:4px}"
        ".t20f .serie .linha{position:absolute;left:0;top:84px}"
        ".t20f .serie .zero{stroke:var(--areia);stroke-width:1;stroke-dasharray:3 4}"
        ".t20f .serie path{fill:none;stroke:var(--grafite);stroke-width:2.2;stroke-linejoin:round}"
        ".t20f .serie circle{fill:var(--tinta)}"
        ".t20f .selo{position:absolute;right:6px;top:8px;transform:rotate(8deg);border:3px solid var(--tinta);"
        "outline:1px solid var(--tinta);outline-offset:3px;padding:5px 12px;font-weight:700;font-size:16px;"
        "letter-spacing:.18em;text-transform:uppercase;color:var(--tinta);animation:uEntra .3s ease-out 2s both}"
        ".t20f .mao{position:absolute;left:0;bottom:0;font-size:30px;color:var(--vermelho-escuro);transform:rotate(-2deg)}"
    )
    return (f"<style>{css}</style><div class='t20papel entra'></div>"
            f"<img class='t20alf entra d3' alt='' src='{alfinete}'/><img class='t20ore' alt='' src='{orelha}'/>"
            f"{{{{content}}}}")


def corpo_quedas() -> str:
    """A lista de todos os locais da cidade, da maior queda à maior alta (23/10/2026, pedido do Alisson: "dá pra
    expandir essa parte das escolas?"). Cada linha é a própria entrada do visual (rowTemplate {{row}} em
    paginas/t20_escola.py) e traz `order` com a posição: a lista sai na ordem certa qualquer que seja a ordem em que o
    visual entrega as linhas (antes eram 130 regras :has, que não chegariam às 2.060 de São Paulo). As linhas têm a
    altura do nome (uma a quatro linhas, sem corte). A caixa rola (o HTML Content usa OverlayScrollbars); o cabeçalho
    fica fixo por cima, no papel, e as linhas passam por baixo dele."""
    css = (
        "#htmlContent{display:flex;flex-direction:column;padding-top:" + str(QUEDAS_TOPO) + "px;padding-bottom:40px}"
        ".t20h{z-index:3;pointer-events:none}"
        ".t20h .cab{position:absolute;left:0;top:0;width:318px;height:" + str(QUEDAS_TOPO - 6) + "px;"
        "background:var(--papel)}"
        ".t20h .rot{position:absolute;left:0;top:0;width:318px;line-height:1.5}"
        ".t20h .linha{position:absolute;left:0;right:0;top:" + str(QUEDAS_TOPO - 8) + "px;"
        "border-top:1.5px solid var(--grafite)}"
        ".t20h .fim{position:absolute;left:0;right:0;bottom:0;height:44px;"
        "background:linear-gradient(rgba(241,235,223,0),var(--papel))}"
        # a linha em fluxo (23/10/2026: sem vão quando o nome cabe numa linha): a variação e o selo à direita, na 1ª linha
        # do nome (float, o nome contorna); o bairro e as seções logo abaixo do nome
        ".t20q .ln{position:relative;width:318px;padding:7px 2px 10px 46px;margin-bottom:2px;cursor:pointer;"
        "border-bottom:1px solid var(--creme);transition:background .15s,opacity .15s}"
        ".t20q .ln:hover{background:var(--creme)}"
        "#htmlContent:has(.ln:hover) .ln:not(:hover){opacity:.55}"
        ".t20q .p{position:absolute;left:2px;top:6px;width:40px;font-size:17px;font-weight:700;color:var(--cinza);"
        "font-variant-numeric:tabular-nums}"
        ".t20q .dir{float:right;margin-left:10px;line-height:18px;white-space:nowrap}"
        ".t20q .v{font-size:17px;font-weight:700}"
        ".t20q .v.novo{font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--cinza)}"
        # o selo vai na linha do bairro, à direita (23/10/2026: na 1ª linha ele e a variação empurravam o nome e
        # sobrava só "Escola" antes da quebra)
        ".t20q .selo{flex:none;display:inline-block;font-size:10px;font-weight:700;letter-spacing:.06em;"
        "text-transform:uppercase;color:var(--tinta);border:1.4px solid var(--tinta);padding:0 3px;line-height:13px;"
        "vertical-align:2px;transform:rotate(-5deg)}"
        ".t20q .nm{display:block;font-size:15px;font-weight:600;line-height:1.2}"
        ".t20q .sb{display:flex;align-items:center;gap:8px;clear:right;margin-top:4px;font-size:13px;"
        "line-height:17px;color:var(--cinza)}"
        ".t20q .sb .bt{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    )
    return (f"<style>{css}</style><div class='tela t20h'><div class='cab'></div><div class='rot sobe'>Da maior queda à maior alta "
            f"da margem de Lula, 2022 → 2026</div><div class='linha entra'></div><div class='fim'></div></div>"
            f"{{{{content}}}}")


def corpo_como() -> str:
    """O cartão 'como explorar' e a legenda (fixos) e, no {{content}}, o aviso de quantos locais ficam fora do mapa na
    cidade escolhida (T20 · Como · HTML)."""
    escola = estilo.imagem_b64("docs/midia/arte/icones/urna-tinta.png", 110)
    css = (
        ".t20x img{position:absolute;right:0;top:0;width:72px;opacity:.9}"
        ".t20x .rot{position:absolute;left:0;top:14px}"
        ".t20x .txt{position:absolute;left:0;top:50px;right:0;font-size:15px;line-height:1.4}"
        ".t20x .leg{position:absolute;left:0;top:176px;right:0;font-size:14px;line-height:1.7;color:var(--grafite)}"
        ".t20x .leg i{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:8px;vertical-align:-1px}"
        ".t20x .leg .a{border:2px solid var(--tinta);background:none}"
        ".t20x .leg .p{font-size:13px;color:var(--cinza)}"
        ".t20n .nota{position:absolute;left:0;top:252px;right:0}"
    )
    return (f"<style>{css}</style><div class='tela t20x'><img class='entra' alt='' src='{escola}'/>"
            f"<div class='rot sobe'>Como explorar</div>"
            f"<div class='txt sobe d2'>Passe o mouse num ponto para ver o post-it da zona; clique num ponto ou numa "
            f"linha para levá-la à ficha. O filtro do topo troca a cidade e acha a zona pelo número.</div>"
            f"<div class='leg entra d4'><div><i style='background:{FAIXAS[-2][1]}'></i>Lula à frente&nbsp;&nbsp;&nbsp;"
            f"<i style='background:{FAIXAS[1][1]}'></i>Flávio à frente</div>"
            f"<div class='p'>cor forte = vantagem maior · tamanho = votos</div>"
            f"<div><i class='a'></i>a zona da ficha</div></div></div>{{{{content}}}}")


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
    medidas()
    print(f"T20: medidas de desenho em {DAX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
