"""Desenha os mapas do mockup a partir da malha do IBGE e dos votos do TSE (PNG transparente, cores da paleta).

São gráficos de dado, não ilustração: no Power BI viram Deneb (geoshape + símbolos) com a mesma malha.
Saídas em `arte/mapas/`:
- `capa-pontos-claro.png` / `capa-pontos-escuro.png`  um ponto por município, cor pela margem de 2026
- `virada.png`        municípios pelo vencedor de 2026 em tinta clara; os que viraram, em azul pleno
- `bolhas-lula.png`   votos que Lula perdeu de 2022 para 2026, por município (círculos vermelhos)
- `bolhas-pl.png`     votos que o PL ganhou de 2022 para 2026, por município (círculos azuis)
- `mg-contagem.png`   Minas Gerais pela margem de 2026, com Contagem em destaque
Uso: python -I -X utf8 pipeline/mapas.py
"""
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap, to_rgba

RAIZ = Path(__file__).resolve().parent.parent
IBGE = RAIZ / "dados" / "bruto" / "ibge"
SAIDA = RAIZ / "arte" / "mapas"
COS = math.cos(math.radians(15))

COR = {"papel": "#F1EBDF", "creme": "#E5DBC8", "areia": "#CBBDA2", "tinta": "#1C1915", "grafite": "#48423A",
       "cinza": "#6B6357",
       "vermelho": "#B8322A", "vermelho_escuro": "#8E2620", "rosa": "#D9877B",
       "azul": "#2B5797", "azul_escuro": "#1D3C6E", "azul_claro": "#8FA8CF"}
# Margem (Lula − adversário) de −60 a +60 p.p.: azul (Flávio) ← areia → vermelho (Lula).
DIVERGENTE = LinearSegmentedColormap.from_list("margem", [
    (0.0, COR["azul_escuro"]), (0.25, COR["azul"]), (0.42, COR["azul_claro"]), (0.5, COR["areia"]),
    (0.58, COR["rosa"]), (0.75, COR["vermelho"]), (1.0, COR["vermelho_escuro"])])


def decodificar(topo, objeto):
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

    def anel(indices):
        pts = []
        for i in indices:
            seg = arcos[i] if i >= 0 else arcos[~i][::-1]
            pts.extend(seg if not pts else seg[1:])
        return np.array(pts)

    formas = {}
    for g in topo["objects"][objeto]["geometries"]:
        poligonos = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        formas[g["properties"]["codarea"]] = [[anel(a) for a in p] for p in poligonos]
    return formas


def area_centro(anel):
    x, y = anel[:, 0], anel[:, 1]
    cruz = x[:-1] * y[1:] - x[1:] * y[:-1]
    area = cruz.sum() / 2
    if abs(area) < 1e-12:
        return 0.0, anel.mean(axis=0)
    cx = ((x[:-1] + x[1:]) * cruz).sum() / (6 * area)
    cy = ((y[:-1] + y[1:]) * cruz).sum() / (6 * area)
    return abs(area), np.array([cx, cy])


def centroides(formas):
    centros = {}
    for cod, poligonos in formas.items():
        maior = max((area_centro(p[0]) for p in poligonos), key=lambda t: t[0])
        centros[cod] = maior[1]
    return centros


def figura(largura_px, limites, fundo=None):
    (x0, x1), (y0, y1) = limites
    altura_px = largura_px * (y1 - y0) / (x1 - x0)
    fig = plt.figure(figsize=(largura_px / 100, altura_px / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    if fundo:
        fig.patch.set_facecolor(fundo)
    else:
        fig.patch.set_alpha(0)
    return fig, ax


def limites_de(formas, folga=0.02):
    todos = np.vstack([p[0] for poligonos in formas.values() for p in poligonos])
    x0, y0 = todos.min(axis=0)
    x1, y1 = todos.max(axis=0)
    fx, fy = (x1 - x0) * folga, (y1 - y0) * folga
    return (x0 - fx, x1 + fx), (y0 - fy, y1 + fy)


def contornos(ax, formas, cor, largura, alfa=1.0, z=3):
    aneis = [anel for poligonos in formas.values() for p in poligonos for anel in p]
    ax.add_collection(PolyCollection(aneis, facecolors="none", edgecolors=to_rgba(cor, alfa), linewidths=largura,
                                     zorder=z))


def preencher(ax, formas, cores, borda=None, largura=0.0, z=1):
    aneis, faces = [], []
    for cod, poligonos in formas.items():
        if cod not in cores:
            continue
        for p in poligonos:
            aneis.append(p[0])
            faces.append(cores[cod])
    ax.add_collection(PolyCollection(aneis, facecolors=faces, edgecolors=borda or faces, linewidths=largura, zorder=z))


def salvar(fig, nome):
    SAIDA.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA / nome, transparent=fig.patch.get_alpha() == 0)
    plt.close(fig)
    print(nome)


def main():
    mun = decodificar(json.loads((IBGE / "malha_municipios.json").read_text(encoding="utf-8")), "BRMU")
    uf = decodificar(json.loads((IBGE / "malha_uf.json").read_text(encoding="utf-8")), "BRUF")
    centros = centroides(mun)
    votos = pd.read_csv(RAIZ / "dados" / "saida" / "votos_municipio.csv", dtype={"cd_ibge": str})
    v = votos.pivot_table(index="cd_ibge", columns="ano", values=["pt", "adv", "validos"], aggfunc="sum")
    v.columns = [f"{c}{a}" for c, a in v.columns]
    v["m22"] = (v.pt2022 - v.adv2022) / v.validos2022
    v["m26"] = (v.pt2026 - v.adv2026) / v.validos2026
    v["dpt"] = v.pt2026 - v.pt2022
    v["dadv"] = v.adv2026 - v.adv2022
    v["virou"] = (v.m22 > 0) & (v.m26 < 0)
    # Município criado depois da malha (ex.: Boa Esperança do Norte · MT, 5101837) fica fora só do desenho.
    fora = sorted(set(v.index) - set(centros))
    if fora:
        print(f"sem polígono na malha, fora do mapa: {', '.join(fora)}")
    v = v[v.index.isin(centros.keys())]
    lim = limites_de(uf)

    # Capa: um ponto por município, área ∝ raiz dos válidos (cidades grandes pesam, sem engolir o interior).
    xy = np.array([centros[c] for c in v.index])
    tam = 7 + 140 * np.sqrt(v.validos2026.values / v.validos2026.max())
    cor = DIVERGENTE(np.clip((v.m26.values + 0.6) / 1.2, 0, 1))
    ordem = np.argsort(v.validos2026.values)
    for nome, borda in (("capa-pontos-claro.png", COR["papel"]), ("capa-pontos-escuro.png", COR["tinta"])):
        fig, ax = figura(1600, lim)
        contornos(ax, uf, COR["areia"], 0.6, 0.55, z=1)
        ax.scatter(xy[ordem, 0], xy[ordem, 1], s=tam[ordem], c=cor[ordem], linewidths=0.35, edgecolors=borda, zorder=2)
        salvar(fig, nome)

    # Virada: vencedor de 2026 em tinta clara; os 711 que viraram em azul pleno.
    claro_lula, claro_flavio = to_rgba(COR["rosa"], 0.38), to_rgba(COR["azul_claro"], 0.38)
    cores = {c: (to_rgba(COR["azul"]) if r.virou else (claro_lula if r.m26 > 0 else claro_flavio))
             for c, r in v.iterrows()}
    fig, ax = figura(1600, lim)
    preencher(ax, mun, cores, largura=0.15)
    contornos(ax, uf, COR["tinta"], 0.7, 0.75)
    salvar(fig, "virada.png")

    # Bolhas: votos perdidos por Lula e ganhos pelo PL, na mesma escala de área nas duas.
    escala = 2600 / max(v.dpt.abs().max(), v.dadv.abs().max())
    for nome, serie, tom in (("bolhas-lula.png", -v.dpt.clip(upper=0), COR["vermelho"]),
                             ("bolhas-pl.png", v.dadv.clip(lower=0), COR["azul"])):
        fig, ax = figura(1600, lim)
        preencher(ax, uf, {c: to_rgba(COR["creme"], 0.55) for c in uf}, z=0)
        contornos(ax, uf, COR["areia"], 0.7, z=1)
        tamanhos = serie.values * escala
        o = np.argsort(-tamanhos)
        ax.scatter(xy[o, 0], xy[o, 1], s=tamanhos[o], c=[to_rgba(tom, 0.42)], edgecolors=[to_rgba(tom, 0.9)],
                   linewidths=0.5, zorder=2)
        salvar(fig, nome)

    # Abstenção de 2026 por município, em tons neutros (areia → tinta): o Brasil que não foi votar.
    comp = pd.read_csv(RAIZ / "dados" / "saida" / "comparecimento_municipio.csv", dtype={"cd_ibge": str})
    c26 = comp[comp.ano == 2026].groupby("cd_ibge")[["abstencoes", "aptos"]].sum()
    taxa = (c26.abstencoes / c26.aptos).clip(0.10, 0.32)
    neutro = LinearSegmentedColormap.from_list("abst", [COR["creme"], COR["areia"], COR["grafite"], COR["tinta"]])
    cores_abst = {c: neutro((t - 0.10) / 0.22) for c, t in taxa.items() if c in mun}
    fig, ax = figura(1600, lim)
    preencher(ax, mun, cores_abst, largura=0.12)
    contornos(ax, uf, COR["papel"], 0.9)
    salvar(fig, "abstencao-2026.png")
    print("escala abstencao-2026: 10% (creme) → 17% (areia) → 25% (grafite) → 32% ou mais (tinta)")

    # 20 anos em movimento: um quadro por eleição, municípios pela margem do ano, mesma escala.
    todos = votos.pivot_table(index="cd_ibge", columns="ano", values=["pt", "adv", "validos"], aggfunc="sum")
    for ano in sorted(votos.ano.unique()):
        m = (todos[("pt", ano)] - todos[("adv", ano)]) / todos[("validos", ano)]
        cores_ano = {c: DIVERGENTE(np.clip((v + 0.6) / 1.2, 0, 1)) for c, v in m.dropna().items() if c in mun}
        fig, ax = figura(1000, lim)
        preencher(ax, mun, cores_ano, largura=0.1)
        contornos(ax, uf, COR["papel"], 0.8)
        salvar(fig, f"movimento-{ano}.png")

    # Explorador: dispersão renda × variação da margem, ponto por município (área ∝ válidos, cor = margem 2026).
    muns = pd.read_csv(RAIZ / "dados" / "saida" / "municipios.csv", dtype={"cd_ibge": str}).set_index("cd_ibge")
    e = v.join(muns[["renda_pc", "populacao"]]).dropna(subset=["renda_pc"])
    e["dm"] = 100 * (e.m26 - e.m22)
    q5 = e.renda_pc.quantile(0.8)
    laco = (e.renda_pc >= q5) & (e.populacao >= 20_000) & (e.dm <= -15)
    for nome_arq, destaque in (("explorador-dispersao.png", None), ("explorador-dispersao-selecao.png", laco)):
        fig = plt.figure(figsize=(9.6, 6.4), dpi=100)
        ax = fig.add_axes([0.08, 0.1, 0.9, 0.86])
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        tam = 2 + 220 * np.sqrt(e.validos2026 / e.validos2026.max())
        cores_e = DIVERGENTE(np.clip((e.m26.values + 0.6) / 1.2, 0, 1))
        if destaque is not None:
            cores_e[~destaque.values, 3] = 0.12
        o = np.argsort(-tam.values)
        ax.scatter(e.renda_pc.values[o], e.dm.values[o], s=tam.values[o], c=cores_e[o],
                   linewidths=0.3, edgecolors=to_rgba(COR["papel"], 0.9))
        ax.set_xscale("log")
        ax.axhline(0, color=COR["grafite"], lw=0.8)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            ax.spines[lado].set_color(COR["areia"])
        ax.tick_params(colors=COR["cinza"], labelsize=11)
        ax.set_xticks([300, 500, 1000, 2000, 4000])
        ax.set_xticklabels(["R$ 300", "R$ 500", "R$ 1 mil", "R$ 2 mil", "R$ 4 mil"])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylim(-40, 25)
        salvar(fig, nome_arq)
    print(f"seleção do laço: {int(laco.sum())} municípios (renda ≥ R$ {q5:,.0f}, 20 mil hab. ou mais, queda ≥ 15 p.p.)")

    # Do país à escola: os locais de votação de Contagem (2026), ponto por escola, cor = margem, área ∝ válidos.
    locais = pd.read_csv(RAIZ / "dados" / "saida" / "locais_contagem.csv")
    l26 = locais[(locais.ano == 2026)].dropna(subset=["lat", "lon"]).copy()
    l26["x"], l26["y"] = l26.lon * COS, l26.lat
    l26["m"] = (l26.pt - l26.adv) / l26.validos
    contagem = {"3118601": mun["3118601"]}
    lim_c = limites_de(contagem, 0.06)
    fig, ax = figura(1400, lim_c)
    preencher(ax, contagem, {"3118601": to_rgba(COR["creme"], 0.7)}, z=0)
    contornos(ax, contagem, COR["tinta"], 1.6, z=1)
    ax.scatter(l26.x, l26.y, s=40 + 900 * l26.validos / l26.validos.max(),
               c=DIVERGENTE(np.clip((l26.m.values + 0.6) / 1.2, 0, 1)), edgecolors=COR["papel"], linewidths=1.2, zorder=3)
    salvar(fig, "escolas-contagem.png")
    (x0, x1), (y0, y1) = lim_c
    pos = l26.assign(px=100 * (l26.x - x0) / (x1 - x0), py=100 * (y1 - l26.y) / (y1 - y0))
    pos[["NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "px", "py"]].to_csv(
        RAIZ / "dados" / "saida" / "escolas_posicao.csv", index=False)
    print(f"escolas-contagem: {len(l26)} locais com coordenada")

    # Minas Gerais com Contagem.
    mg = {c: p for c, p in mun.items() if c.startswith("31")}
    lim_mg = limites_de(mg, 0.03)
    cores_mg = {c: to_rgba(DIVERGENTE(np.clip((v.loc[c, "m26"] + 0.6) / 1.2, 0, 1)), 0.55) for c in mg if c in v.index}
    fig, ax = figura(1400, lim_mg)
    preencher(ax, mg, cores_mg, borda=to_rgba(COR["papel"], 0.9), largura=0.3)
    contornos(ax, {c: p for c, p in uf.items() if c == "31"}, COR["tinta"], 1.2)
    contornos(ax, {"3118601": mg["3118601"]}, COR["tinta"], 2.4, z=4)
    salvar(fig, "mg-contagem.png")
    cx, cy = centros["3118601"]
    (x0, x1), (y0, y1) = lim_mg
    print(f"Contagem no mg-contagem.png: x {100 * (cx - x0) / (x1 - x0):.1f}% · y {100 * (y1 - cy) / (y1 - y0):.1f}%")


if __name__ == "__main__":
    main()
