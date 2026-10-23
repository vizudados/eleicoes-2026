# -*- coding: utf-8 -*-
"""setas — a fonte "Sora Setas": as setas (→ ← ↑ ↓ ↗ ↘) e o visto (✓) que a Sora não tem, com as métricas dela.

Por quê (23/10/2026): a Sora não traz setas; cada "→" do painel ("2006 → 2026", "2022 → 2026", "−5,6 → −11,0") caía
no Segoe UI, menor e em outra linha de base, e o cabeçalho "2006 → 2026" da tela 21 saía desalinhado dos outros. A
fonte aqui entra logo depois da Sora na pilha (--fonte e --mao, em estilo.css_base): o navegador só a usa para os
caracteres que a Sora não tem.

Desenho: a haste no eixo matemático da Sora (o centro do sinal de menos, y 344 em 1000 unidades) e a espessura do traço
do menos no peso (76 no 400, 112 no 600); a ponta é uma divisa de dois braços a 45°. Métricas verticais iguais às da Sora
(970/−290, USE_TYPO_METRICS), para a seta não mexer na altura da linha. Duas instâncias estáticas: 400 (pesos 300–550)
e 600 (551–800).

    python -X utf8 pbi/scripts/setas.py        # grava pbi/assets/fontes/sora-setas-400.woff2 e -600.woff2
"""
from __future__ import annotations

import io
import math
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

FONTES = Path(__file__).resolve().parent.parent / "assets" / "fontes"
EIXO = 344                       # centro do sinal de menos da Sora (unidades de 1000)
TRACO = {400: 76, 600: 112}      # espessura do menos da Sora em cada peso
AVANCO = 820
# caractere → (nome do glifo, ângulo da seta em graus; 0 = para a direita)
SETAS = {"→": ("arrowright", 0), "←": ("arrowleft", 180), "↑": ("arrowup", 90), "↓": ("arrowdown", 270),
         "↗": ("arrowupright", 45), "↘": ("arrowdownright", 315)}


def _retangulo(a, b, meia):
    """Os quatro cantos (sentido horário) do traço de espessura 2·meia entre os pontos a e b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n * meia, dx / n * meia
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def _seta(angulo: float, traco: int):
    """Contornos da seta apontando para o ângulo, centrada em (AVANCO/2, EIXO)."""
    cx, cy = AVANCO / 2, EIXO
    meio = 340 if angulo % 90 == 0 else 280          # meia haste (a diagonal fica um pouco menor)
    braco = 205 + traco * 0.4
    meia = traco / 2
    rad = math.radians(angulo)
    ux, uy = math.cos(rad), math.sin(rad)
    ponta = (cx + ux * meio, cy + uy * meio)
    # a haste para antes da ponta, para o encontro dos braços não engrossar
    fim_haste = (ponta[0] - ux * meia * 1.2, ponta[1] - uy * meia * 1.2)
    contornos = [_retangulo((cx - ux * meio, cy - uy * meio), fim_haste, meia)]
    for giro in (135, -135):
        r = rad + math.radians(giro)
        recuo = meia * 0.7                            # o canto de fora do braço cai na ponta
        a = (ponta[0] - ux * recuo, ponta[1] - uy * recuo)
        b = (a[0] + math.cos(r) * braco, a[1] + math.sin(r) * braco)
        contornos.append(_retangulo(a, b, meia))
    return contornos


def _glifo(contornos):
    pen = TTGlyphPen(None)
    for pts in contornos:
        # TrueType: contorno de fora no sentido horário; os retângulos vêm anti-horários para (nx, ny) à esquerda
        pts = list(reversed(pts))
        pen.moveTo(tuple(round(v) for v in pts[0]))
        for p in pts[1:]:
            pen.lineTo(tuple(round(v) for v in p))
        pen.closePath()
    return pen.glyph()


def _visto(traco: int):
    """O visto (✓) do placar da apuração: dois traços que se encontram embaixo, na altura do x da Sora (0 a 540)."""
    meia = traco / 2
    fundo = (300, 40 + meia)
    return [_retangulo((110, 300), (fundo[0] + meia * 0.5, fundo[1] - meia * 0.5), meia),
            _retangulo((fundo[0] - meia * 0.6, fundo[1] - meia * 0.6), (700, 560), meia)]


def fonte(peso: int) -> bytes:
    ordem = [".notdef", "space"] + [n for n, _ in SETAS.values()] + ["checkmark"]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(ordem)
    fb.setupCharacterMap({0x20: "space", 0x2713: "checkmark", **{ord(c): n for c, (n, _) in SETAS.items()}})
    vazio = TTGlyphPen(None).glyph()
    glifos = {".notdef": vazio, "space": vazio, "checkmark": _glifo(_visto(TRACO[peso]))}
    for _, (nome, ang) in SETAS.items():
        glifos[nome] = _glifo(_seta(ang, TRACO[peso]))
    fb.setupGlyf(glifos)
    metricas = {n: (AVANCO if n not in (".notdef", "space") else 250, 0) for n in ordem}
    for nome, g in glifos.items():
        if nome not in (".notdef", "space"):
            g.recalcBounds(fb.font["glyf"])
            metricas[nome] = (AVANCO, g.xMin)
    fb.setupHorizontalMetrics(metricas)
    fb.setupHorizontalHeader(ascent=970, descent=-290, lineGap=0)
    fb.setupNameTable({"familyName": "Sora Setas", "styleName": "Regular" if peso == 400 else "SemiBold",
                       "uniqueFontIdentifier": f"SoraSetas-{peso}", "fullName": f"Sora Setas {peso}",
                       "psName": f"SoraSetas-{peso}", "version": "1.000",
                       "licenseDescription": "Desenho próprio (Vizu Dados) para acompanhar a Sora (SIL OFL 1.1)."})
    fb.setupOS2(sTypoAscender=970, sTypoDescender=-290, sTypoLineGap=0, usWinAscent=1220, usWinDescent=320,
                fsSelection=0b10000000, usWeightClass=peso, achVendID="VIZU")
    fb.setupPost()
    fb.font.flavor = "woff2"
    b = io.BytesIO()
    fb.font.save(b)
    return b.getvalue()


def main() -> int:
    for peso in TRACO:
        destino = FONTES / f"sora-setas-{peso}.woff2"
        destino.write_bytes(fonte(peso))
        print(f"{destino.name}: {destino.stat().st_size:,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
