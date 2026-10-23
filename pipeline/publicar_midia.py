"""Publica as imagens que o painel carrega por URL no GitHub Pages (docs/midia → https://vizudados.github.io/eleicoes-2026/midia/).

Converte as artes limpas (arte/limpos/**) e os mapas de dado (arte/mapas/*) em versões web: largura máxima por tipo,
PNG com alfa quantizado (paleta de 256 cores, sem perda visível no traço), nomes em minúsculas e sem espaço. Grava
docs/midia/catalogo.json com nome, URL, largura, altura e bytes de cada arquivo (as telas conferem por ele).

    python -I -X utf8 pipeline/publicar_midia.py
"""

import json
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "midia"
URL = "https://vizudados.github.io/eleicoes-2026/midia"
# (pasta de origem, pasta de destino, largura máxima)
GRUPOS = [
    (RAIZ / "arte" / "limpos", "arte", 1460),
    (RAIZ / "arte" / "limpos" / "icones", "arte/icones", 160),
    (RAIZ / "arte" / "limpos" / "dossie", "arte/dossie", 520),
    (RAIZ / "arte" / "limpos" / "rabiscos", "arte/rabiscos", 640),
    (RAIZ / "arte" / "mapas", "mapas", 1400),
]


def web(origem: Path, destino: Path, largura: int) -> dict:
    im = Image.open(origem)
    im = im.convert("RGBA")
    if im.width > largura:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    destino.parent.mkdir(parents=True, exist_ok=True)
    q.save(destino, "PNG", optimize=True)
    return {"largura": im.width, "altura": im.height, "bytes": destino.stat().st_size}


def main():
    catalogo = {}
    for pasta, sub, largura in GRUPOS:
        if not pasta.exists():
            continue
        for p in sorted(pasta.glob("*.png")):
            nome = p.stem.lower().replace(" ", "-")
            rel = f"{sub}/{nome}.png"
            info = web(p, DESTINO / rel, largura)
            catalogo[rel] = {"url": f"{URL}/{rel}", **info}
    (DESTINO / "catalogo.json").write_text(json.dumps(catalogo, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(v["bytes"] for v in catalogo.values())
    print(f"{len(catalogo)} imagens · {total / 1e6:.1f} MB em docs/midia")


if __name__ == "__main__":
    main()
