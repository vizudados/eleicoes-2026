"""Prepara a arte da capa animada a partir dos desenhos do Codex (arte/candidatas/capa-*.png).

- Horizonte: quatro painéis em traço (Norte → Sul) viram UMA faixa contínua de 1640 px, em creme sobre transparente,
  com as linhas de chão alinhadas e as emendas em degradê. Junto sai o mapa de ordem do desenho (cinza: 0 = primeiro
  traço, 255 = último), que o vídeo usa como máscara para a caneta ir revelando o horizonte da esquerda para a direita,
  e o perfil do topo do desenho (a ponta da caneta sobe e desce por ele).
- Céu: a folha de nuvens e aves (grade 3 × 4) vira peças soltas em creme.

Alfa = escuridão do traço (mesma regra de pipeline/preparar_arte.py), tinta creme #E5DBC8, fundo transparente;
tudo local, em Python.
Uso: python -I -X utf8 capa/remotion/scripts/preparar_arte.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = Path(__file__).resolve().parents[3]
CANDIDATAS = RAIZ / "arte" / "candidatas"
PUBLICO = RAIZ / "capa" / "remotion" / "public"
CREME = (0xE5, 0xDB, 0xC8)

# Painéis escolhidos (vez de cada um) e a linha de chão de cada desenho original (y em px, 1536 × 1024).
PAINEIS = [("capa-horizonte-1-1-1.png", "Amazônia → sertão"), ("capa-horizonte-2-1-1.png", "Pelourinho → Congresso"),
           ("capa-horizonte-3-2-1.png", "Pão de Açúcar → São Paulo"), ("capa-horizonte-4-2-1.png", "araucárias → pampa")]
LARGURA = 1640          # x 140–1780 no quadro
X0, CHAO = 140, 990     # canto esquerdo e linha de chão no quadro
SOBREPOR = 40           # px de emenda entre painéis (no quadro)


def alfa_da_tinta(img, piso=28, teto=200):
    cinza = np.asarray(img.convert("L"), dtype=np.float32)
    return np.clip((255.0 - cinza - piso) / (teto - piso), 0, 1)


def linha_de_chao(alfa):
    linhas = (alfa > 0.25).sum(axis=1)
    longas = np.nonzero(linhas > 1000)[0]
    return int(longas.max()) if len(longas) else int(np.nonzero(linhas > 3)[0].max())


def reduzir(alfa, largura, altura):
    img = Image.fromarray((alfa * 255).astype(np.uint8), "L").resize((largura, altura), Image.LANCZOS)
    a = np.asarray(img, dtype=np.float32) / 255
    # Traço fino some na redução: devolve corpo à linha sem engrossar o desenho.
    return np.clip(a ** 0.72 * 1.12, 0, 1)


def rgba(alfa, cor=CREME):
    h, w = alfa.shape
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = cor
    out[..., 3] = (np.clip(alfa, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def horizonte():
    escala = (LARGURA + 3 * SOBREPOR) / (4 * 1536)
    pecas = []
    for nome, _ in PAINEIS:
        alfa = alfa_da_tinta(Image.open(CANDIDATAS / nome))
        chao = linha_de_chao(alfa)
        topo = int(np.nonzero((alfa > 0.25).sum(axis=1) > 2)[0].min())
        corte = alfa[max(0, topo - 6):chao + 4]
        w, h = round(1536 * escala), round(corte.shape[0] * escala)
        pecas.append((reduzir(corte, w, h), h - round(4 * escala)))  # (alfa, y da linha de chão na peça)
    acima = max(chao_y for _, chao_y in pecas)
    abaixo = max(a.shape[0] - chao_y for a, chao_y in pecas)
    alt = acima + abaixo
    tela = np.zeros((alt, LARGURA), np.float32)
    x = 0
    for i, (a, chao_y) in enumerate(pecas):
        w = a.shape[1]
        peso = np.ones(w, np.float32)
        if i > 0:
            peso[:SOBREPOR] = np.linspace(0, 1, SOBREPOR)
        if i < len(pecas) - 1:
            peso[-SOBREPOR:] = np.minimum(peso[-SOBREPOR:], np.linspace(1, 0, SOBREPOR))
        y = acima - chao_y
        x1 = min(LARGURA, x + w)
        bloco = a[:, :x1 - x] * peso[:x1 - x]
        regiao = tela[y:y + a.shape[0], x:x1]
        tela[y:y + a.shape[0], x:x1] = 1 - (1 - regiao) * (1 - bloco)
        x += w - SOBREPOR
    rgba(tela).save(PUBLICO / "img" / "horizonte.png", optimize=True)

    # Ordem do desenho: da esquerda para a direita, cada grupo de traços entra junto e cresce do chão para cima.
    rng = np.random.default_rng(7)
    tinta = tela > 0.08
    grupos, n = ndimage.label(ndimage.binary_dilation(tinta, iterations=2))
    atraso = np.r_[0, rng.uniform(0, 1, n)]
    xs = np.linspace(0, 1, LARGURA)[None, :]
    ys = np.linspace(0, 1, alt)[:, None]
    ordem = 0.86 * xs + 0.06 * (1 - ys) + 0.08 * atraso[grupos]
    ordem = ndimage.gaussian_filter(ordem, 1.2)
    ordem = (ordem - ordem.min()) / (ordem.max() - ordem.min())
    Image.fromarray((ordem * 255).astype(np.uint8), "L").save(PUBLICO / "img" / "horizonte-ordem.png", optimize=True)

    # Perfil do topo do desenho (a cada 4 px), para a ponta da caneta.
    cols = tela > 0.2
    topo_col = np.where(cols.any(axis=0), cols.argmax(axis=0), acima)
    perfil = ndimage.uniform_filter1d(topo_col.astype(float), 9)[::4]
    # Ordem em que a tinta aparece junto ao chão, por coluna: a ponta da caneta anda exatamente na frente visível.
    baixo = tinta.copy()
    baixo[: int(alt * 0.6)] = False
    chao_ordem = np.full(LARGURA, np.nan)
    for x in range(LARGURA):
        v = ordem[baixo[:, x], x]
        if len(v):
            chao_ordem[x] = np.percentile(v, 25)
    idx = np.arange(LARGURA)
    ok = ~np.isnan(chao_ordem)
    chao_ordem = np.maximum.accumulate(np.interp(idx, idx[ok], chao_ordem[ok]))
    info = {"x": X0, "y": CHAO - acima, "largura": LARGURA, "altura": alt, "chao": acima,
            "perfil": [round(float(p), 1) for p in perfil],
            "ordem_chao": [round(float(v), 4) for v in chao_ordem[::4]], "paineis": [d for _, d in PAINEIS]}
    (PUBLICO / "dados" / "horizonte.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    print(f"horizonte.png: {LARGURA}×{alt} · chão em y {CHAO} · topo em y {CHAO - acima} (escala {escala:.4f})")


CEU = {  # célula da folha 3 × 4 → nome; escala da peça em relação ao desenho original
    (0, 0): ("nuvem-1", 0.30), (0, 1): ("nuvem-2", 0.30), (0, 2): ("nuvem-3", 0.30), (0, 3): ("nuvem-4", 0.30),
    (1, 0): ("fiapo-1", 0.32), (1, 2): ("fiapo-3", 0.32),
    (2, 2): ("garca", 0.20), (2, 3): ("bando", 0.22),
}


def ceu():
    alfa = alfa_da_tinta(Image.open(CANDIDATAS / "capa-nuvens-1-1.png"))
    h, w = alfa.shape
    pecas = {}
    for (lin, col), (nome, esc) in CEU.items():
        cel = alfa[lin * h // 3:(lin + 1) * h // 3, col * w // 4:(col + 1) * w // 4]
        ys, xs = np.nonzero(cel > 0.1)
        cel = cel[max(0, ys.min() - 6):ys.max() + 7, max(0, xs.min() - 6):xs.max() + 7]
        # 2× o tamanho de exibição: a peça se move, e o navegador reduz pela metade com folga.
        a = reduzir(cel, round(cel.shape[1] * esc * 2), round(cel.shape[0] * esc * 2))
        rgba(a).save(PUBLICO / "img" / f"{nome}.png", optimize=True)
        pecas[nome] = {"largura": a.shape[1] / 2, "altura": a.shape[0] / 2}
    (PUBLICO / "dados" / "ceu.json").write_text(json.dumps(pecas), encoding="utf-8")
    print("céu:", ", ".join(f"{k} {v['largura']:.0f}×{v['altura']:.0f}" for k, v in pecas.items()))


if __name__ == "__main__":
    (PUBLICO / "img").mkdir(parents=True, exist_ok=True)
    horizonte()
    ceu()
