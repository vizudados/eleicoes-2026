"""Limpa os desenhos do Codex para o mockup: fundo transparente, tinta numa cor da paleta, recorte justo.

- Cenas e urna: `arte/candidatas/<nome>-1-1.png` -> `arte/limpos/<nome>.png` (tinta #1C1915, alfa pela escuridão).
- Rabiscos: a folha 4 × 3 vira 12 marcas soltas, em três tintas (tinta, vermelho, azul):
  `arte/limpos/rabiscos/<marca>-<cor>.png`.

Uso: python -I -X utf8 pipeline/preparar_arte.py
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parent.parent
CANDIDATAS = RAIZ / "arte" / "candidatas"
LIMPOS = RAIZ / "arte" / "limpos"
TINTAS = {"tinta": (0x1C, 0x19, 0x15), "vermelho": (0xB8, 0x32, 0x2A), "azul": (0x2B, 0x57, 0x97)}
CREME = (0xE5, 0xDB, 0xC8)
CENAS = ["regiao-sudeste", "regiao-nordeste", "regiao-norte", "regiao-centro-oeste", "regiao-sul", "urna"]
MARCAS = ["oval", "elipse", "circulo", "retangulo",
          "seta-curva-direita", "seta-curva-esquerda", "seta-reta", "seta-s",
          "sublinhado", "sublinhado-duplo", "sublinhado-onda", "chave"]


def alfa_da_tinta(img, piso=28, teto=200):
    """Alfa = escuridão do pixel, com o papel (quase branco) zerado e o traço pleno a partir de `teto`."""
    cinza = np.asarray(img.convert("L"), dtype=np.float32)
    escuro = 255.0 - cinza
    alfa = np.clip((escuro - piso) / (teto - piso), 0, 1)
    return (alfa * 255).astype(np.uint8)


def pintar(alfa, cor):
    h, w = alfa.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = cor
    rgba[..., 3] = alfa
    return Image.fromarray(rgba, "RGBA")


def recortar(alfa, margem=16, minimo=8):
    ys, xs = np.nonzero(alfa > minimo)
    y0, y1 = max(0, ys.min() - margem), min(alfa.shape[0], ys.max() + margem + 1)
    x0, x1 = max(0, xs.min() - margem), min(alfa.shape[1], xs.max() + margem + 1)
    return alfa[y0:y1, x0:x1]


def limpar_cenas():
    LIMPOS.mkdir(parents=True, exist_ok=True)
    for nome in CENAS:
        alfa = recortar(alfa_da_tinta(Image.open(CANDIDATAS / f"{nome}-1-1.png")))
        destino = LIMPOS / f"{nome}.png"
        pintar(alfa, TINTAS["tinta"]).save(destino, optimize=True)
        print(f"{destino.name}: {alfa.shape[1]}×{alfa.shape[0]}")


DOSSIE = ["fita", "fita-diagonal", "clipe", "alfinete", "post-it", "ficha", "papel-rasgado", "orelha",
          "carimbo-redondo", "carimbo-retangular", "visto", "asterisco"]
ICONES = ["urna", "caixa-de-votos", "megafone", "microfone", "celular", "lupa", "tv-debate", "jornal",
          "escola", "casa", "pino", "calendario", "pessoas", "pessoa-duvida", "barras", "balanca"]


def separar_folha(origem, nomes, pasta, linhas, cores, dilatacao=22, piso=40, teto=170):
    """Recorta uma folha de elementos soltos (grade de `linhas` linhas) em PNGs, na ordem de leitura."""
    pasta.mkdir(parents=True, exist_ok=True)
    alfa = alfa_da_tinta(Image.open(CANDIDATAS / origem), piso=piso, teto=teto)
    # Junta os traços de cada elemento (a ponta da seta, as linhas do duplo) e separa os elementos entre si.
    rotulos, _ = ndimage.label(ndimage.binary_dilation(alfa > 20, iterations=dilatacao))
    caixas = ndimage.find_objects(rotulos)
    grandes = sorted([(c, (c[0].stop - c[0].start) * (c[1].stop - c[1].start)) for c in caixas],
                     key=lambda x: -x[1])[:len(nomes)]
    altura = alfa.shape[0]
    ordenadas = sorted((c for c, _ in grandes),
                       key=lambda c: (int(((c[0].start + c[0].stop) / 2) / (altura / linhas)), c[1].start))
    for nome, caixa in zip(nomes, ordenadas):
        pedaco = recortar(alfa[caixa], margem=10)
        for cor in cores:
            pintar(pedaco, TINTAS.get(cor, CREME)).save(pasta / f"{nome}-{cor}.png", optimize=True)
        print(f"{pasta.name}/{nome}: {pedaco.shape[1]}×{pedaco.shape[0]}")


def separar_rabiscos():
    separar_folha("rabiscos-1-1.png", MARCAS, LIMPOS / "rabiscos", 3, ["tinta", "vermelho", "azul"])


TINTAS_CANDIDATO = {"lula": ("vermelho_escuro", (0x8E, 0x26, 0x20)), "flavio": ("azul_escuro", (0x1D, 0x3C, 0x6E))}



def limpar_candidatos():
    """Retrato e comício de cada candidato em três tintas: tinta, a cor dele (escura, para texto ≥ 4,5:1) e creme."""
    for quem, (nome_cor, rgb) in TINTAS_CANDIDATO.items():
        for peca in ("retrato", "comicio"):
            alfa = recortar(alfa_da_tinta(Image.open(CANDIDATAS / f"{peca}-{quem}-1-1.png")))
            for sufixo, cor in (("tinta", TINTAS["tinta"]), (nome_cor, rgb), ("creme", CREME)):
                pintar(alfa, cor).save(LIMPOS / f"{peca}-{quem}-{sufixo}.png", optimize=True)
            print(f"{peca}-{quem}: {alfa.shape[1]}×{alfa.shape[0]}")


def limpar_extras(nomes):
    """Cenas avulsas (ex.: debate-palco) em tinta e em creme."""
    for nome in nomes:
        alfa = recortar(alfa_da_tinta(Image.open(CANDIDATAS / f"{nome}-1-1.png")))
        for sufixo, cor in (("tinta", TINTAS["tinta"]), ("creme", CREME)):
            pintar(alfa, cor).save(LIMPOS / f"{nome}-{sufixo}.png", optimize=True)
        print(f"{nome}: {alfa.shape[1]}×{alfa.shape[0]}")


if __name__ == "__main__":
    import sys
    if "--extras" in sys.argv:
        limpar_extras(sys.argv[sys.argv.index("--extras") + 1:])
    elif "--dossie" in sys.argv:
        separar_folha("dossie-1-1.png", DOSSIE, LIMPOS / "dossie", 3, ["tinta", "creme"])
    elif "--icones" in sys.argv:
        separar_folha("icones-1-1.png", ICONES, LIMPOS / "icones", 4, ["tinta", "vermelho", "azul", "creme"], dilatacao=17)
    elif "--candidatos" in sys.argv:
        limpar_candidatos()
    else:
        limpar_cenas()
        separar_rabiscos()
        limpar_candidatos()
