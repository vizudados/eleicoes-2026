"""Prepara os dados da capa animada (Remotion): mapa em pixels com traço de caneta, estrelas da bandeira e municípios.

- Malhas do IBGE (TopoJSON, `dados/bruto/ibge/`) e votos do TSE (1º turno em `dados/saida/votos_municipio.csv`,
  2º turno em `dados/pbi/municipio_2turno.csv`), como em `pipeline/mapas.py`: projeção lon·cos(15°) × lat,
  margens de 2026 = (Lula − Flávio) ÷ válidos. O raio do 1º turno fica fixo nos dois mapas.
- Traço de caneta: cada arco da malha é simplificado, reamostrado e ganha um tremor suave com semente fixa
  (render determinístico). O contorno do Brasil vira um anel só, que a caneta percorre do extremo norte, no sentido
  horário; as divisas entre UFs são arcos soltos, com pequenas sobras nas pontas, como num esboço.
- Bandeira: geometria oficial (Lei 5.700/1971, anexo; módulo M = 210 unidades, 4200 × 2940), as 27 estrelas nas
  posições e grandezas do desenho oficial e a estrela de cada UF pela Lei 8.421/1992.

Uso: python -I -X utf8 capa/remotion/scripts/preparar_dados.py
Saída: capa/remotion/public/dados/capa.json
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from scipy import ndimage

RAIZ = Path(__file__).resolve().parents[3]
IBGE = RAIZ / "dados" / "bruto" / "ibge"
SAIDA = RAIZ / "capa" / "remotion" / "public" / "dados" / "capa.json"
COS = math.cos(math.radians(15))
LARG, ALT = 1920, 1080
CENTRO = (960.0, 583.0)   # centro do mapa e da bandeira
ALTURA_MAPA = 560.0       # do extremo norte (RR) ao Chuí, em px

SIGLA = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI",
         "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
         "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}

# Estrelas do desenho oficial (unidades da bandeira, centro do círculo na origem, y para baixo) e grandeza 1–5.
# Correspondência estrela → UF: Lei 8.421/1992. A cauda do Escorpião foi casada com as posições por ajuste
# astronômico (céu do Rio em 15/11/1889), respeitando as grandezas.
ESTRELAS = [
    ("Procyon", "Cão Menor", -600, -132, 1, "AM"), ("Sirius", "Cão Maior", -535, 177, 1, "MT"),
    ("Mirzam", "Cão Maior", -625, 243, 2, "AP"), ("Muliphen", "Cão Maior", -463, 132, 4, "RO"),
    ("Wezen", "Cão Maior", -382, 250, 2, "RR"), ("Adhara", "Cão Maior", -404, 323, 3, "TO"),
    ("Canopus", "Carina", -295, 390, 1, "GO"), ("Spica", "Virgem", 228, -228, 1, "PA"),
    ("Alphard", "Hidra", -280, 30, 2, "MS"), ("Gama da Hidra", "Hidra", 200, -37, 3, "AC"),
    ("Acrux", "Cruzeiro do Sul", 0, 330, 1, "SP"), ("Mimosa", "Cruzeiro do Sul", 85, 184, 2, "RJ"),
    ("Gacrux", "Cruzeiro do Sul", 0, 118, 2, "BA"), ("Pálida", "Cruzeiro do Sul", -74, 184, 3, "MG"),
    ("Intrometida", "Cruzeiro do Sul", -37, 235, 4, "ES"), ("Antares", "Escorpião", 515, 258, 1, "PI"),
    ("Graffias", "Escorpião", 617, 265, 3, "MA"), ("Wei", "Escorpião", 545, 323, 2, "CE"),
    ("Sargas", "Escorpião", 368, 477, 2, "AL"), ("Iota do Escorpião", "Escorpião", 367, 551, 3, "SE"),
    ("Girtab", "Escorpião", 441, 419, 3, "PB"), ("Shaula", "Escorpião", 500, 382, 2, "RN"),
    ("Mu do Escorpião", "Escorpião", 365, 405, 3, "PE"), ("Atria", "Triângulo Austral", 220, 495, 2, "RS"),
    ("Beta do Triângulo", "Triângulo Austral", 283, 430, 3, "SC"),
    ("Gama do Triângulo", "Triângulo Austral", 162, 412, 3, "PR"), ("Sigma do Oitante", "Oitante", 0, 575, 5, "DF"),
]

# Margem de 2026 no fundo escuro: azul (Flávio à frente) ← areia → vermelho (Lula à frente), −60 a +60 p.p.
# Mesma escala da casa (pipeline/mapas.py), com as pontas um pouco mais claras para ler sobre a tinta #1C1915.
ESCALA = [(0.0, "#3D69B3"), (0.25, "#4F7BC0"), (0.42, "#8FA8CF"), (0.5, "#CBBDA2"),
          (0.58, "#D9877B"), (0.75, "#C9443A"), (1.0, "#BE3329")]


def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def cor_margem(m):
    t = float(np.clip((m + 0.6) / 1.2, 0, 1))
    for (t0, c0), (t1, c1) in zip(ESCALA, ESCALA[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            rgb = hex_rgb(c0) * (1 - f) + hex_rgb(c1) * f
            return "#%02X%02X%02X" % tuple(int(round(v)) for v in rgb)
    return ESCALA[-1][1]


def direcao_troca(pt1, adv1, pt2, adv2):
    """+1: Flávio → Lula; −1: Lula → Flávio; empates em qualquer turno não são troca."""
    if pt1 < adv1 and pt2 > adv2:
        return 1
    if pt1 > adv1 and pt2 < adv2:
        return -1
    return 0


def arcos_topo(topo):
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
        arcos.append(np.array(pts))
    return arcos


def poligonos(g):
    return g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]


def anel(arcos, indices):
    pts = []
    for i in indices:
        seg = arcos[i] if i >= 0 else arcos[~i][::-1]
        pts.extend(seg if not pts else seg[1:])
    return np.array(pts)


def area_centro(a):
    x, y = a[:, 0], a[:, 1]
    cruz = x[:-1] * y[1:] - x[1:] * y[:-1]
    area = cruz.sum() / 2
    if abs(area) < 1e-12:
        return 0.0, a.mean(axis=0)
    return abs(area), np.array([((x[:-1] + x[1:]) * cruz).sum() / (6 * area), ((y[:-1] + y[1:]) * cruz).sum() / (6 * area)])


def rdp(pts, tol):
    """Douglas–Peucker iterativo."""
    if len(pts) < 3:
        return pts
    manter = np.zeros(len(pts), bool)
    manter[0] = manter[-1] = True
    pilha = [(0, len(pts) - 1)]
    while pilha:
        a, b = pilha.pop()
        if b - a < 2:
            continue
        p, q = pts[a], pts[b]
        d = q - p
        n = math.hypot(*d)
        seg = pts[a + 1:b]
        if n < 1e-9:
            dist = np.hypot(*(seg - p).T)
        else:
            dist = np.abs(d[0] * (seg[:, 1] - p[1]) - d[1] * (seg[:, 0] - p[0])) / n
        i = int(np.argmax(dist))
        if dist[i] > tol:
            k = a + 1 + i
            manter[k] = True
            pilha += [(a, k), (k, b)]
    return pts[manter]


def tremer(pts, rng, amp, passo=2.0, ondas=(30.0, 9.0), fechado=False):
    """Reamostra a linha e desloca cada ponto na normal por um ruído suave (soma de senos com fase sorteada)."""
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    total = d[-1]
    if total < 1e-6:
        return pts, 0.0
    n = max(2, int(total / passo) + 1)
    s = np.linspace(0, total, n)
    x, y = np.interp(s, d, pts[:, 0]), np.interp(s, d, pts[:, 1])
    tx, ty = np.gradient(x), np.gradient(y)
    norma = np.hypot(tx, ty) + 1e-9
    nx, ny = -ty / norma, tx / norma
    ruido = np.zeros(n)
    for lam, peso in ((ondas[0], 1.0), (ondas[1], 0.45), (ondas[0] * 3.1, 0.6)):
        lam *= rng.uniform(0.8, 1.25)
        if fechado:  # periódico no anel, para não ter degrau na emenda
            lam = total / max(1, round(total / lam))
        ruido += peso * np.sin(2 * np.pi * s / lam + rng.uniform(0, 2 * np.pi))
    ruido *= amp / 2.05
    out = np.c_[x + nx * ruido, y + ny * ruido]
    return out, float(np.hypot(*np.diff(out, axis=0).T).sum())


def sobrar(pts, rng, minimo, maximo):
    """Estende as duas pontas na direção da tangente, como a caneta que passa do ponto."""
    if len(pts) < 2:
        return pts
    a = pts[0] - pts[min(3, len(pts) - 1)]
    b = pts[-1] - pts[max(-4, -len(pts))]
    a /= np.hypot(*a) + 1e-9
    b /= np.hypot(*b) + 1e-9
    return np.vstack([pts[0] + a * rng.uniform(minimo, maximo), pts, pts[-1] + b * rng.uniform(minimo, maximo)])


def caminho(pts, fechar=False, casas=1):
    f = f"{{:.{casas}f}}"
    partes = [f"M{f.format(pts[0, 0])} {f.format(pts[0, 1])}"]
    partes += [f"L{f.format(x)} {f.format(y)}" for x, y in pts[1:]]
    return "".join(partes) + ("Z" if fechar else "")


def encadear(arcos_px, indices):
    """Junta arcos exteriores pelas pontas em anéis fechados."""
    chave = lambda p: (round(p[0], 4), round(p[1], 4))
    pontas = {}
    for i in indices:
        for lado in (0, -1):
            pontas.setdefault(chave(arcos_px[i][lado]), []).append(i)
    livres = set(indices)
    aneis = []
    while livres:
        i = livres.pop()
        pts = list(arcos_px[i])
        while True:
            fim = chave(pts[-1])
            if fim == chave(pts[0]) and len(pts) > 2:
                break
            prox = [j for j in pontas.get(fim, []) if j in livres]
            if not prox:
                break
            j = prox[0]
            livres.discard(j)
            seg = arcos_px[j] if chave(arcos_px[j][0]) == fim else arcos_px[j][::-1]
            pts.extend(seg[1:])
        aneis.append(np.array(pts))
    return aneis


def main():
    rng = np.random.default_rng(2026)
    topo_uf = json.loads((IBGE / "malha_uf.json").read_text(encoding="utf-8"))
    arcos = arcos_topo(topo_uf)
    geoms = topo_uf["objects"]["BRUF"]["geometries"]

    # Enquadramento: continente (sem Trindade e Noronha) com altura fixa, centrado.
    aneis_uf = {g["properties"]["codarea"]: [anel(arcos, p[0]) for p in poligonos(g)] for g in geoms}
    todos = np.vstack([a for lista in aneis_uf.values() for a in lista if a[:, 0].mean() < -34.6 * COS])
    (x0, y0), (x1, y1) = todos.min(axis=0), todos.max(axis=0)
    esc = ALTURA_MAPA / (y1 - y0)
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2

    def px(p):
        p = np.asarray(p, float)
        return np.c_[CENTRO[0] + (p[:, 0] - xc) * esc, CENTRO[1] - (p[:, 1] - yc) * esc]

    arcos_px = [px(a) for a in arcos]

    # Uso de cada arco pelas UFs: 1 = contorno do país (costa e fronteira), 2 = divisa entre UFs.
    uso = {}
    for g in geoms:
        uf = SIGLA[g["properties"]["codarea"]]
        for p in poligonos(g):
            for r in p:
                for i in r:
                    uso.setdefault(i if i >= 0 else ~i, []).append(uf)
    exteriores = [i for i, u in uso.items() if len(u) == 1]
    interiores = [i for i, u in uso.items() if len(u) >= 2]

    # Contorno: anel do continente + ilhas, com tremor de caneta.
    aneis = sorted(encadear(arcos_px, exteriores), key=lambda a: -len(a))
    continente = aneis[0]
    xs, ys = continente[:, 0], continente[:, 1]
    area = ((xs[:-1] * ys[1:] - xs[1:] * ys[:-1]).sum()) / 2
    if area < 0:  # sentido horário na tela (y para baixo)
        continente = continente[::-1]
    norte = int(np.argmin(continente[:-1, 1]))
    continente = np.vstack([continente[norte:-1], continente[:norte + 1]])
    simpl = rdp(continente, 0.3)
    traco1, comp1 = tremer(simpl, rng, 0.9, passo=2.0, ondas=(34, 10), fechado=True)
    traco2, comp2 = tremer(simpl, rng, 1.5, passo=2.5, ondas=(52, 14), fechado=True)
    # Pontos do traço a cada 6 px: a ponta da caneta segue o contorno enquanto ele se desenha.
    dist = np.r_[0, np.cumsum(np.hypot(*np.diff(traco1, axis=0).T))]
    passos = np.arange(0, dist[-1], 6.0)
    amostras = np.c_[np.interp(passos, dist, traco1[:, 0]), np.interp(passos, dist, traco1[:, 1])]
    ilhas = []
    for a in aneis[1:]:
        if len(a) < 4:
            continue
        perim = float(np.hypot(*np.diff(a, axis=0).T).sum())
        if perim < 5:
            continue
        t, c = tremer(rdp(a, 0.3), rng, 0.4, passo=1.5, ondas=(12, 5), fechado=True)
        ilhas.append({"d": caminho(t, True), "comp": round(c, 1), "x": round(float(a[:, 0].mean()), 1),
                      "y": round(float(a[:, 1].mean()), 1)})

    divisas = []
    for i in interiores:
        a = rdp(arcos_px[i], 0.3)
        perim = float(np.hypot(*np.diff(a, axis=0).T).sum())
        if perim < 1.5:
            continue
        t, c = tremer(sobrar(a, rng, 1.0, 3.5), rng, 0.7, passo=2.0, ondas=(26, 8))
        meio = a[len(a) // 2]
        divisas.append({"d": caminho(t), "comp": round(c, 1), "ufs": sorted(set(uso[i])),
                        "x": round(float(meio[0]), 1), "y": round(float(meio[1]), 1)})

    # Âncora de cada UF: centroide do maior polígono (a estrela pousa ali e a onda de municípios parte dali).
    ancora = {}
    for cod, lista in aneis_uf.items():
        maior = max((area_centro(px(a)) for a in lista), key=lambda t: t[0])
        ancora[SIGLA[cod]] = maior[1]

    estrelas = []
    for nome, const, sx, sy, grandeza, uf in ESTRELAS:
        ax, ay = ancora[uf]
        estrelas.append({"nome": nome, "constelacao": const, "x": sx, "y": sy, "g": grandeza, "uf": uf,
                         "ax": round(float(ax), 1), "ay": round(float(ay), 1)})

    # Municípios: centroide do maior polígono, duas margens e raio fixo pelo 1º turno de 2026.
    topo_mu = json.loads((IBGE / "malha_municipios.json").read_text(encoding="utf-8"))
    arcos_mu = arcos_topo(topo_mu)
    centros = {}
    for g in topo_mu["objects"]["BRMU"]["geometries"]:
        maior = max((area_centro(anel(arcos_mu, p[0])) for p in poligonos(g)), key=lambda t: t[0])
        centros[g["properties"]["codarea"]] = maior[1]
    votos = pd.read_csv(RAIZ / "dados" / "saida" / "votos_municipio.csv", dtype={"cd_ibge": str})
    v26 = votos[votos.ano == 2026].groupby("cd_ibge")[["pt", "adv", "validos"]].sum()
    v26 = v26[v26.index.isin(centros.keys()) & (v26.validos > 0)]
    v26["m"] = (v26.pt - v26.adv) / v26.validos
    votos2 = pd.read_csv(RAIZ / "dados" / "pbi" / "municipio_2turno.csv", dtype={"cd_ibge": str})
    v2 = votos2[votos2.ano == 2026].set_index("cd_ibge")[["pt", "adv", "validos"]]
    if v2.index.has_duplicates:
        raise ValueError("2º turno de 2026: cd_ibge duplicado")
    numeros = v2.to_numpy(dtype=float)
    if not np.isfinite(numeros).all() or (numeros < 0).any() or (numeros != np.floor(numeros)).any():
        raise ValueError("2º turno de 2026: votos ausentes, negativos ou não inteiros")
    if (v2.validos <= 0).any() or not (v2.pt + v2.adv == v2.validos).all():
        raise ValueError("2º turno de 2026: válidos devem ser positivos e iguais a pt + adv")
    faltantes = v26.index.difference(v2.index)
    fora = v2.index.difference(v26.index)
    if len(faltantes) or set(fora) != {"5101837"} or "5101837" in centros:
        raise ValueError(f"Cobertura inesperada: sem 2º turno {list(faltantes)}; fora do desenho {list(fora)}")
    desenhados2 = v2.loc[v26.index].copy()  # mesma ordem, mesma posição, mesma semente por município
    desenhados2["m"] = (desenhados2.pt - desenhados2.adv) / desenhados2.validos
    trocas = [direcao_troca(a.pt, a.adv, b.pt, b.adv)
              for (_, a), (_, b) in zip(v26.iterrows(), desenhados2.iterrows())]
    if (trocas.count(1), trocas.count(-1)) != (211, 1):
        raise ValueError(f"Trocas inesperadas: Flávio → Lula {trocas.count(1)}; Lula → Flávio {trocas.count(-1)}")
    soma_csv = int(v2.validos.sum())
    soma_fora = int(v2.loc[fora, "validos"].sum())
    soma_desenho = int(desenhados2.validos.sum())
    if soma_desenho != soma_csv - soma_fora:
        raise ValueError("A soma de válidos do desenho não reconcilia com o CSV")
    xy = px(np.array([centros[c] for c in v26.index]))
    vmax = v26.validos.max()
    mun = {k: [] for k in ("cd_ibge", "x", "y", "r", "cor", "cor2", "d", "u", "uf", "m", "m2",
                           "validos", "validos2", "troca")}
    for (cod, r), (_, r2), (x, y), troca in zip(v26.iterrows(), desenhados2.iterrows(), xy, trocas):
        uf = SIGLA[cod[:2]]
        ax, ay = ancora[uf]
        mun["cd_ibge"].append(cod)
        mun["x"].append(round(float(x), 1))
        mun["y"].append(round(float(y), 1))
        mun["r"].append(round(float(1.05 + 1.9 * math.sqrt(r.validos / vmax)), 2))
        mun["cor"].append(cor_margem(r.m))
        mun["cor2"].append(cor_margem(r2.m))
        mun["d"].append(round(float(math.hypot(x - ax, y - ay)), 1))
        mun["u"].append(round(float(rng.uniform()), 3))
        mun["uf"].append(uf)
        mun["m"].append(round(float(r.m), 8))
        mun["m2"].append(round(float(r2.m), 8))
        mun["validos"].append(int(r.validos))
        mun["validos2"].append(int(r2.validos))
        mun["troca"].append(troca)

    # Céu de fundo: estrelas fracas fora do título, das setas, do cabeçalho/rodapé e do mapa.
    mascara = Image.new("L", (LARG, ALT), 0)
    desenho = ImageDraw.Draw(mascara)
    for a in aneis:
        desenho.polygon([tuple(p) for p in a], fill=255)
    perto_mapa = ndimage.binary_dilation(np.asarray(mascara) > 0, iterations=16)
    ceu = []
    for _ in range(1400):
        x, y = rng.uniform(20, LARG - 20), rng.uniform(104, 836)
        if 300 <= x <= 1620 and 104 <= y <= 306:      # título
            continue
        if (30 <= x <= 130 or 1790 <= x <= 1890) and 500 <= y <= 580:  # setas
            continue
        if perto_mapa[int(y), int(x)]:
            continue
        bloco = (140 <= x <= 560 or 1360 <= x <= 1780) and 380 <= y <= 760
        if rng.uniform() > (0.22 if bloco else 0.55):
            continue
        brilho = rng.uniform() ** 2.2
        ceu.append({"x": round(x, 1), "y": round(y, 1), "r": round(0.45 + 0.75 * brilho, 2),
                    "a": round((0.05 + 0.07 * brilho) if bloco else (0.07 + 0.3 * brilho), 3), "f": round(float(rng.uniform()), 3)})

    # Bandeira em traço: linhas da construção oficial, com tremor leve (unidades da bandeira; 1 px ≈ 5,5 u).
    def linha_reta(p, q, amp=3.5):
        pts = np.array([p, q], float)
        t, c = tremer(sobrar(pts, rng, 12, 34), rng, amp, passo=10, ondas=(380, 120))
        return {"d": caminho(t, casas=0), "comp": round(c)}

    retangulo = [linha_reta(a, b) for a, b in (((-2100, -1470), (2100, -1470)), ((2100, -1470), (2100, 1470)),
                                                ((2100, 1470), (-2100, 1470)), ((-2100, 1470), (-2100, -1470)))]
    losango = [linha_reta(a, b) for a, b in (((0, -1113), (1743, 0)), ((1743, 0), (0, 1113)),
                                              ((0, 1113), (-1743, 0)), ((-1743, 0), (0, -1113)))]
    ang = np.radians(np.linspace(-100, 272, 400))
    circ, c_circ = tremer(np.c_[735 * np.cos(ang), 735 * np.sin(ang)], rng, 4.0, passo=10, ondas=(300, 90))
    circulo = {"d": caminho(circ, casas=0), "comp": round(c_circ)}
    faixa = []
    for raio in (1680, 1785):
        th = np.radians(np.linspace(180, 360, 4000))
        pts = np.c_[-420 + raio * np.cos(th), 1470 + raio * np.sin(th)]
        dentro = pts[np.hypot(pts[:, 0], pts[:, 1]) <= 735]
        t, c = tremer(sobrar(dentro, rng, 6, 18), rng, 3.0, passo=10, ondas=(260, 80))
        faixa.append({"d": caminho(t, casas=0), "comp": round(c)})

    dados = {
        "quadro": {"largura": LARG, "altura": ALT, "centro": CENTRO, "escala_mapa": round(esc, 4)},
        "contorno": {"d1": caminho(traco1, True), "comp1": round(comp1, 1),
                     "d2": caminho(traco2, True), "comp2": round(comp2, 1),
                     "passo": 6.0, "amostras": [round(float(v), 1) for v in amostras.ravel()]},
        "ilhas": ilhas,
        "divisas": divisas,
        "estrelas": estrelas,
        "municipios": mun,
        "ceu": ceu,
        "bandeira": {"retangulo": retangulo, "losango": losango, "circulo": circulo, "faixa": faixa},
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    caixa = np.vstack([continente])
    print(f"{SAIDA.relative_to(RAIZ)}: {SAIDA.stat().st_size / 1024:.0f} KB · {len(mun['x'])} municípios · "
          f"{len(divisas)} divisas · {len(ilhas)} ilhas · {len(ceu)} estrelas de fundo")
    print(f"mapa x {caixa[:, 0].min():.0f}–{caixa[:, 0].max():.0f} · y {caixa[:, 1].min():.0f}–{caixa[:, 1].max():.0f}"
          f" · contorno {comp1:.0f} px")
    print(f"Trocas entre os pontos: Flávio → Lula {trocas.count(1)} · Lula → Flávio {trocas.count(-1)}")
    print(f"Válidos 2º turno: desenho {soma_desenho:,} = CSV {soma_csv:,} − sem coordenada {soma_fora:,}")
    for e in estrelas:
        print(f"  {e['uf']} {e['nome']:<20} grandeza {e['g']} → ({e['ax']:.0f}, {e['ay']:.0f})")


if __name__ == "__main__":
    main()
