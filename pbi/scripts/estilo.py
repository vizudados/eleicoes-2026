"""estilo — o sistema visual do painel Eleições 2026 no Power BI: cores, fontes embutidas, CSS base, kit de movimento e
ajudantes para escrever HTML/SVG dentro de medidas DAX.

Tudo que é texto fixo e grande (fontes em base64, CSS) vai na medida de folha de estilo [Estilo · CSS] (gerada em
pbi/dax/_Estilo/Estilo · CSS.dax por `python -I -X utf8 pbi/scripts/estilo.py`) ou no bodyTemplate do visual; as
medidas de desenho só montam o HTML do dado (limite de ~32 mil caracteres por valor de texto, L048).

Fontes: Sora (texto, números, títulos; eixo wght 300–800) e Caveat (as notas à mão, ≥ 24 px), as duas SIL OFL 1.1,
recortadas para Latin-1 + a pontuação tipográfica do português e embutidas como woff2 base64 (L099), sem hinting
(L112).

Movimento (pedido do Alisson, 23/10/2026: números sempre com contadores, mapas desenhados com rabiscos, cores surgindo
como esmaecer):
  - contadores: movimento.js (da casa) conta todo número de 20 px ou mais do zero na entrada e do valor anterior a cada
    filtro; nada a fazer no HTML além de escrever o número;
  - entrada: classes .sobe, .entra e .d1….d16 (atraso em passos de 80 ms);
  - traço: <path pathLength="1" class="traco"> se desenha (stroke-dashoffset 1 → 0), com o filtro de rabisco
    `filter="url(#rb)"` (defs_rabisco()) para o traço tremido de caneta;
  - cor: .cor (fill que esmaece do creme até a cor final), .esmaece (opacidade);
  - barras: .barra-x / .barra-y crescem do zero (nomes que o movimento.js reconhece para deslizar entre filtros).
Tudo respeita prefers-reduced-motion e o estado parado é o desenho final (keyframes só com 'from', L122).
"""

from __future__ import annotations

import base64
import io
import sys
from functools import lru_cache
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
RAIZ = PBI.parent
FONTES = PBI / "assets" / "fontes"

COR = {
    "papel": "#F1EBDF", "creme": "#E5DBC8", "areia": "#CBBDA2", "tinta": "#1C1915", "grafite": "#48423A",
    "cinza": "#6B6357", "vermelho": "#B8322A", "vermelho_escuro": "#8E2620", "rosa": "#D9877B", "azul": "#2B5797",
    "azul_escuro": "#1D3C6E", "azul_claro": "#8FA8CF", "marrom": "#7A5A43", "branco": "#FBF8F2",
}
FAMILIA = "Sora Eleicoes"
FAMILIA_MAO = "Caveat Eleicoes"
CARACTERES = ("".join(chr(c) for c in range(0x20, 0x7F)) + "".join(chr(c) for c in range(0xA0, 0x100))
              + "–—‘’‚“”„•…‰′″‹›€−×÷→←↑↓↗↘·•●○◆◇■□▲▼✓✗✔✕★☆№ºª")


# ---------------------------------------------------------------------------------------------------- fontes
def _recortar(ttf: Path, eixo) -> bytes:
    """eixo = (mín, máx) mantém a fonte variável no intervalo; um número fixa a instância estática (menor)."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    f = TTFont(ttf)
    if eixo and "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": eixo})
    o = subset.Options()
    o.layout_features = ["kern", "liga", "tnum", "lnum", "pnum", "case", "ccmp", "locl", "mark", "mkmk"]
    if isinstance(eixo, tuple):
        o.layout_features.append("calt")
    o.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    o.hinting = False                       # L112: sem hinting, a caixa de tinta fica igual à do Figma
    o.desubroutinize = True
    o.flavor = "woff2"
    cmap = f.getBestCmap()
    s = subset.Subsetter(o)
    s.populate(unicodes=sorted(ord(c) for c in set(CARACTERES) if ord(c) in cmap))
    s.subset(f)
    f.flavor = "woff2"
    b = io.BytesIO()
    f.save(b, reorderTables=False)
    return b.getvalue()


@lru_cache(maxsize=None)
def woff2(nome: str) -> bytes:
    """Recorte em cache em pbi/assets/fontes/<nome>.woff2 (L108: gravado uma vez, a montagem repete os bytes)."""
    destino = FONTES / f"{nome}.woff2"
    if destino.exists():
        return destino.read_bytes()
    origem, eixo = {"sora-eleicoes": (FONTES / "sora-wght.ttf", (300, 800)),
                    "caveat-eleicoes": (FONTES / "Caveat-wght.ttf", 600)}[nome]
    dados = _recortar(origem, eixo)
    destino.write_bytes(dados)
    return dados


def font_face(familia: str, nome: str, pesos: str) -> str:
    b64 = base64.b64encode(woff2(nome)).decode("ascii")
    return (f"@font-face{{font-family:'{familia}';font-style:normal;font-weight:{pesos};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


# ---------------------------------------------------------------------------------------------------- CSS base
def css_base() -> str:
    c = COR
    tokens = ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in c.items())
    passos = "".join(f".d{i}{{animation-delay:{i * 80}ms!important}}" for i in range(1, 17))
    return "".join([
        font_face(FAMILIA, "sora-eleicoes", "300 800"),
        font_face(FAMILIA_MAO, "caveat-eleicoes", "400 700"),
        f":root{{{tokens};--fonte:'{FAMILIA}','Segoe UI',sans-serif;--mao:'{FAMILIA_MAO}','Segoe Print',cursive}}",
        "html,body{margin:0;padding:0;background:transparent;overflow:hidden}",
        "body,#htmlViewer,#htmlContent{font-family:var(--fonte);color:var(--tinta);-webkit-font-smoothing:antialiased;"
        "font-feature-settings:'kern' 1,'lnum' 1;text-rendering:geometricPrecision}",
        # raiz de cada desenho: ocupa a caixa do visual (L037: fixed, nunca height:100%) e tem camada própria para o
        # texto sair em tons de cinza (L115). A camada fica NA raiz fixa, nunca no #htmlContent: lá ela vira o bloco de
        # contenção dos filhos fixed, que têm altura 0 e somem.
        ".tela{position:fixed;inset:0;will-change:transform}",
        "*{box-sizing:border-box}",
        "svg{overflow:visible}",
        # tipografia (pisos de leitura a 61 %: corpo ≥ 15 px; eixo e rodapé 13)
        ".tnum{font-variant-numeric:tabular-nums lining-nums}",
        ".sob{font-size:15px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--grafite)}",
        ".tit{font-size:30px;font-weight:600;letter-spacing:-.012em;line-height:1.18}",
        ".man{font-size:24px;font-weight:600;letter-spacing:-.01em;line-height:1.25}",
        ".txt{font-size:17px;font-weight:400;line-height:1.45;color:var(--grafite)}",
        ".rot{font-size:13px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--cinza)}",
        ".nota{font-size:13px;font-weight:400;color:var(--cinza);line-height:1.4}",
        ".num{font-weight:700;letter-spacing:-.025em;line-height:1;font-variant-numeric:tabular-nums lining-nums}",
        ".mao{font-family:var(--mao);font-size:26px;font-weight:600;line-height:1.05}",
        ".lula{color:var(--vermelho)}.flavio{color:var(--azul)}.lula-esc{color:var(--vermelho-escuro)}"
        ".flavio-esc{color:var(--azul-escuro)}",
        ".escuro{color:var(--creme)}.escuro .sob,.escuro .rot,.escuro .nota{color:var(--areia)}"
        ".escuro .txt{color:var(--creme)}",
        # movimento: o estado parado é o desenho final; keyframes só com 'from'
        "@keyframes uSobe{from{opacity:0;transform:translateY(14px)}}",
        "@keyframes uEntra{from{opacity:0}}",
        "@keyframes uCresceX{from{transform:scaleX(0)}}",
        "@keyframes uCresceY{from{transform:scaleY(0)}}",
        "@keyframes eTraco{from{stroke-dashoffset:1}}",
        "@keyframes eCor{from{fill:var(--creme);fill-opacity:.35}}",
        "@keyframes eCorEsc{from{fill:var(--tinta);fill-opacity:.2}}",
        "@keyframes eEscala{from{opacity:0;transform:scale(.4)}}",
        ".sobe{animation:uSobe .7s cubic-bezier(.2,.7,.2,1) both}",
        ".entra{animation:uEntra .8s ease-out both}",
        ".barra-x{transform-origin:left center;animation:uCresceX 1s cubic-bezier(.2,.7,.2,1) .3s both}",
        ".barra-x-dir{transform-origin:right center;animation:uCresceX 1s cubic-bezier(.2,.7,.2,1) .3s both}",
        ".barra-y{transform-origin:center bottom;animation:uCresceY 1s cubic-bezier(.2,.7,.2,1) .3s both}",
        ".traco{stroke-dasharray:1;stroke-dashoffset:0;animation:eTraco 1.8s cubic-bezier(.45,.05,.3,1) both}",
        ".traco-rapido{stroke-dasharray:1;stroke-dashoffset:0;animation:eTraco .9s cubic-bezier(.45,.05,.3,1) both}",
        ".cor{animation:eCor 1.4s ease-out 1.2s both}",
        ".cor-esc{animation:eCorEsc 1.4s ease-out 1.2s both}",
        ".esmaece{animation:uEntra 1.2s ease-out .9s both}",
        ".brota{transform-box:fill-box;transform-origin:center;animation:eEscala .6s cubic-bezier(.2,.9,.3,1.3) both}",
        passos,
        # realce no hover dentro de um desenho só (gráfico sem grão): o filho sob o mouse fica, os irmãos apagam
        ".realce>*{transition:opacity .18s ease}.realce:has(>:hover)>:not(:hover){opacity:.42}",
        "@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}",
    ])


def defs_rabisco(ident: str = "rb", escala: float = 2.2, frequencia: float = 0.035, semente: int = 7) -> str:
    """<defs> com o filtro de traço tremido de caneta (turbulência + deslocamento) para usar em filter="url(#rb)"."""
    # userSpaceOnUse: com a região em fração da caixa (o padrão), uma linha reta horizontal ou vertical tem caixa de
    # altura (ou largura) 0 e some com o filtro
    return (f"<defs><filter id='{ident}' filterUnits='userSpaceOnUse' x='-10%' y='-10%' width='120%' height='120%'>"
            f"<feTurbulence type='fractalNoise' baseFrequency='{frequencia}' numOctaves='2' seed='{semente}' result='r'/>"
            f"<feDisplacementMap in='SourceGraphic' in2='r' scale='{escala}' xChannelSelector='R' "
            f"yChannelSelector='G'/></filter></defs>")


def rabisco_circulo(largura: int, altura: int, cor: str = "var(--tinta)", espessura: float = 3.0,
                    atraso_ms: int = 900) -> str:
    """Laço feito à mão em volta de um número (duas voltas levemente desencontradas), que se desenha."""
    w, h = largura, altura
    d = (f"M{w * .08:.0f},{h * .55:.0f} C{w * .02:.0f},{h * .1:.0f} {w * .7:.0f},{-h * .08:.0f} {w * .95:.0f},{h * .32:.0f} "
         f"C{w * 1.06:.0f},{h * .6:.0f} {w * .62:.0f},{h * 1.02:.0f} {w * .3:.0f},{h * .94:.0f} "
         f"C{w * .02:.0f},{h * .86:.0f} {w * .0:.0f},{h * .4:.0f} {w * .26:.0f},{h * .16:.0f} "
         f"C{w * .4:.0f},{h * .04:.0f} {w * .6:.0f},{h * .05:.0f} {w * .72:.0f},{h * .1:.0f}")
    return (f"<svg width='{w}' height='{h}' viewBox='0 0 {w} {h}' style='position:absolute;inset:0;"
            f"pointer-events:none'>{defs_rabisco('rbc', 1.6)}<path d='{d}' pathLength='1' class='traco' "
            f"fill='none' stroke='{cor}' stroke-width='{espessura}' stroke-linecap='round' filter='url(#rbc)' "
            f"style='animation-delay:{atraso_ms}ms'/></svg>")


# ---------------------------------------------------------------------------------------------------- marca e ícones
@lru_cache(maxsize=None)
def logo_vizu(cor: str) -> str:
    """Lockup Vizu (ícone + wordmark) em SVG inline numa cor só."""
    svg = (RAIZ / "arte" / "ref" / "vizu-dados-logo.svg").read_text(encoding="utf-8")
    for tom in ("#111111", "#979898", "#9B9B9B"):          # o lockup da casa é bicolor; no painel, uma cor (Figma)
        svg = svg.replace(f'fill="{tom}"', f'fill="{cor}"')
    svg = svg.replace("\n", "")
    return svg.replace('<svg width="5514" height="586"', '<svg width="168" height="18" style="display:block"', 1)


@lru_cache(maxsize=None)
def imagem_b64(caminho: str, largura: int) -> str:
    """PNG reduzido para `largura` px (alfa preservado), como data URI."""
    from PIL import Image
    im = Image.open(RAIZ / caminho).convert("RGBA")
    a = round(im.height * largura / im.width)
    im = im.resize((largura, a), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------------------------------- DAX
def dax_literal(texto: str, pedaco: int = 6000) -> str:
    """Texto Python → literal DAX ("" escapa aspas), em pedaços concatenados com & (literais curtos)."""
    partes = [texto[i:i + pedaco] for i in range(0, len(texto), pedaco)] or [""]
    return "\n    & ".join('"' + p.replace('"', '""') + '"' for p in partes)


def gravar_medida(nome: str, pasta: str, descricao: str, expressao: str, formato: str = "texto",
                  subpasta: str = "_Estilo") -> Path:
    destino = PBI / "dax" / subpasta / f"{nome}.dax"
    destino.parent.mkdir(parents=True, exist_ok=True)
    texto = f"/*\n@pasta: {pasta}\n@formato: {formato}\n@descricao: {descricao}\n*/\n{expressao}\n"
    if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
        destino.write_text(texto, encoding="utf-8")
    return destino


def main() -> int:
    css = css_base()
    gravar_medida("Estilo · CSS", r"_Estilo", "Folha de estilo comum de todos os HTML Content: Sora e Caveat "
                  "embutidas (woff2 base64), cores, tipografia e o kit de movimento. Gerada por "
                  "pbi/scripts/estilo.py.", dax_literal(css))
    gravar_medida("Casca · vazio", r"_Estilo", "Conteúdo vazio para os HTML Content cujo desenho é todo fixo (o "
                  "bodyTemplate traz a casca da página).", '" "')
    print(f"Estilo · CSS: {len(css):,} caracteres · Sora {len(woff2('sora-eleicoes')):,} B · "
          f"Caveat {len(woff2('caveat-eleicoes')):,} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
