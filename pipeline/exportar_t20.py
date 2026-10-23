"""Exporta os dados da tela Escola (código T20; dono: tela 20) para 34 cidades: as 27 capitais, as 6 maiores que
trocaram Lula por Flávio de 2022 para 2026 e Contagem (MG) (pedido do dono, 23/10/2026). A tela abre no Rio de
Janeiro: a margem da cidade quase não mexeu, mas por dentro locais viraram para os dois lados.

- `dados/pbi/t20_locais.csv`: um local de votação do 1º turno de 2026 por linha, com os votos de 2026 e os de 2022 e
  2018 do mesmo local (soma das seções do mesmo zona + número) e a posição no mapa da própria cidade.
- `dados/pbi/t20_cidades.csv`: uma linha por cidade com o que a tela lê por cidade: a contagem dos locais de 2022 (os do
  próprio ano), a escola de exemplo da ficha, o enquadramento do mapa, o contorno simplificado (malha do IBGE) e os
  rótulos de bairro.

O mapa: a caixa do mapa da tela tem proporção fixa (MAPA_W × MAPA_H de pbi/scripts/desenho_t20.py, 692 × 860). Cada
cidade ganha uma moldura com essa proporção, em projeção equirretangular (x = lon · cos da latitude do centro da
cidade, y = lat), e as posições (px, py) e o contorno vão em % da moldura (0–100 nas duas direções, y para baixo): na
tela, viewBox 0 0 100 100 sem preservar a proporção não distorce nada, porque a moldura já tem a proporção da caixa.
- Cidade inteira (a maioria): a moldura é a caixa do contorno (e dos locais) com folga de 6 % (como o mapa de
  Contagem de antes), alargada até a proporção da caixa.
- Recorte (cidades de território grande e mancha urbana pequena, ex.: Manaus, Rio Branco, Porto Velho): quando, com a
  cidade inteira, os pontos ficariam colados (mediana da distância ao vizinho mais próximo abaixo de 5 px), a moldura
  vai para a mancha urbana (_enquadrar) e um mapinha no canto mostra a cidade inteira com o recorte. Local fora da
  moldura fica fora do mapa (conta em todo número e aparece na lista), com aviso na tela; o contorno é cortado numa
  caixa folgada em volta da moldura.
- Ilha sem local de votação e pequena (ex.: Trindade, de Vitória) sai do contorno; local com coordenada a mais de
  LONGE km do contorno é coordenada errada e fica sem posição.

Colunas de t20_locais.csv: id (Contagem primeiro, como antes: 1…112), cod_ibge, cidade ("Contagem (MG)"), uf, local
(nome único no modelo inteiro, a chave da tabela; vazio quando é igual ao nome), nome (nome legível; repetido na mesma cidade ganha o número do local),
bairro, zona, numero, secoes, pt/adv/validos de 2026, 2022 e 2018 (vazio quando o local não existia), px, py (% da
moldura; vazio sem posição), fora_mapa ("sem endereço" ou "fora do recorte"), pos_queda (posição na lista da cidade, da
maior queda da margem de Lula 2022 → 2026 à maior alta; os locais novos no fim, por nome), ordem_nome (ordem
alfabética na cidade, para o filtro).

Entradas: dados/bruto/tse/locais_t20.csv (pipeline/extrair_secoes.py --t20), dados/bruto/ibge/malha_municipios.json,
dados/bruto/tse/presidente_2026_BR.csv (só a prova dos totais).
Uso: python -I -X utf8 pipeline/exportar_t20.py
"""
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.path import Path as Caminho

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extrair_secoes import CIDADES_T20, GRUPO_T20  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "dados" / "bruto"
DESTINO = RAIZ / "dados" / "pbi" / "t20_locais.csv"
DESTINO_CIDADES = RAIZ / "dados" / "pbi" / "t20_cidades.csv"
MAPA_W, MAPA_H = 692, 860            # a caixa do mapa da tela (pbi/scripts/desenho_t20.py)
FOLGA = 0.06                          # folga da caixa do contorno (a de antes)
LONGE = 3.0                           # km do contorno a partir dos quais a coordenada é tida como errada
# a cidade em que a tela abre (primeira no filtro e nos ids). Não é Contagem: abrir onde o documentário de referência
# começa seria copiar o roteiro dele (pedido do dono, 23/10/2026)
CIDADE_INICIAL = "3304557"     # Rio de Janeiro

SIGLAS = {
    # da Contagem de antes
    "CAIC", "CEDETEM", "SENAI", "CEFET", "CEMAR", "CEMEI", "CEI", "CSU", "CEC", "NEEC", "FUNEC", "PUC", "SESI", "JK",
    "UMEI", "EM", "EE", "VC-03",
    # escolas e centros (as mais comuns nas 34 cidades)
    "EMEF", "EMEI", "CMEI", "EEEF", "CIEP", "EEEFM", "EMEIF", "EEFM", "CEU", "UEB", "EEMTI", "SESC", "SENAC", "CE",
    "CETI", "EMEIEF", "EMTI", "ETEC", "NEIM", "CEF", "EEEM", "EDI", "CEJA", "CEPI", "EEF", "EC", "EBM", "CRAS", "EEB",
    "INSS", "UEI", "CEM", "IEMA", "EEEP", "EEM", "UNIP", "CMPM", "EEFEM", "EMPG", "UE", "CED", "CAEE", "CEEJA", "EMEB",
    "ETE", "CAPS", "SEAGRI", "LTDA", "CIAC", "CEAP", "CAP", "EJA", "ESEF", "FATEC", "UNINOVE", "FMU", "SEMED", "SEDUC",
    # universidades e institutos
    "UFMG", "UFRJ", "UERJ", "UFF", "IFPA", "UFPA", "UEPA", "UFRA", "UNAMA", "IFCE", "UFC", "UECE", "UNB", "IFB", "USP",
    "UNIFESP", "IFSP", "UFPE", "UPE", "IFPE", "UFRN", "IFRN", "UFPB", "IFPB", "UFPI", "IFPI", "UESPI", "UFAL", "IFAL",
    "UFS", "IFS", "UFES", "IFES", "UFG", "IFG", "UFMT", "IFMT", "UFMS", "IFMS", "UFPR", "IFPR", "UTFPR", "UFSC", "IFSC",
    "UDESC", "UFRGS", "IFRS", "PUCRS", "UFAM", "IFAM", "UEA", "UFRR", "IFRR", "UFT", "IFTO", "UNIR", "IFRO", "UFAC",
    "IFAC", "UNIFAP", "IFAP", "UFMA", "IFMA", "UEMA", "IFBA", "UNEB", "UFBA", "IFMG", "PUCMINAS", "UNIMONTES",
    "UFRPE", "UNICAP", "UNIRIO", "UFRRJ", "UVA", "UFSJ", "UEMG", "UEPB", "UNIFOR", "UNIT", "UNIFACS", "UCSAL", "UNEAL",
    "UNCISAL", "FAPAM", "MUN", "EMEFI", "EMEIEF", "EMEFM", "EEEFMI", "CEIM", "NAEI", "EMEBI", "FIEB", "ITB", "EMM",
    "EMPG", "EMEIEF", "CIEJA", "CMEB", "CEMEB", "EMEFEI",
}
MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "d'agua", "em", "na", "no", "nas", "nos", "a", "o", "à", "ao"}
ABREVIA = {"EST.": "Est.", "PROF.": "Prof.", "PROFª": "Profª", "PROFº": "Profº", "PROFA": "Profa", "PROFA.": "Profa.",
           "DR": "Dr.", "DR.": "Dr.", "DRA": "Dra.", "DRA.": "Dra.", "ESP.": "Esp.", "CONJ.": "Conj.", "E.": "E.",
           "M.": "M.", "A.": "A.", "NSTITUTO": "Instituto"}


def titulo(texto) -> str:
    """Nome do TSE (maiúsculas) → nome legível: siglas e romanos ficam, conectivos em minúscula, o resto com inicial
    maiúscula."""
    if not isinstance(texto, str) or not texto.strip():
        return ""
    palavras = re.sub(r"\s+", " ", texto.strip()).split(" ")
    saida = []
    for i, p in enumerate(palavras):
        nucleo = p.strip("(),;:")
        sem_ponto = nucleo.rstrip(".")
        partes = [x for x in sem_ponto.split("-") if x]
        # sigla: da lista (cada parte, em "UE-MUN"), romano, sem vogal (CMPM), letras com ponto (E.M.E.F.) ou curta e
        # sozinha entre parênteses ("(CEU)")
        entre_parenteses = p.startswith("(") and p.rstrip(",;:").endswith(")")
        sigla = (bool(partes) and all(x in SIGLAS or re.fullmatch(r"[IVXL]{2,6}", x) and x not in {"LI", "XI"}
                                      for x in partes)) \
            or (sem_ponto.isalpha() and len(sem_ponto) >= 2 and not re.search(r"[AEIOUÁÉÍÓÚÂÊÔÃÕÀY]", sem_ponto)) \
            or bool(re.fullmatch(r"([A-ZÀ-Ú]\.){2,}[A-ZÀ-Ú]?\.?", nucleo)) \
            or (entre_parenteses and sem_ponto.isalpha() and len(sem_ponto) <= 4)
        if nucleo in ABREVIA:
            q = p.replace(nucleo, ABREVIA[nucleo])
        elif sigla or re.search(r"\d", nucleo) or "/" in nucleo:
            q = p
        elif i > 0 and p.lower() in MINUSCULAS:
            q = p.lower()
        else:
            # inicial maiúscula em cada parte separada por hífen, parêntese ou apóstrofo
            q = re.sub(r"(^|[-(/'])([^\W\d_])", lambda m: m.group(1) + m.group(2).upper(), p.lower())
            q = re.sub(r"-(i{1,3}|iv)\b", lambda m: "-" + m.group(1).upper(), q)
        saida.append(q)
    return " ".join(saida).replace("d'agua", "d'Água").replace("D'agua", "d'Água")


def _chave_pt(texto: str) -> str:
    """Chave de ordem alfabética pt-BR (acento não manda na ordem)."""
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").casefold()


# ---------------------------------------------------------------------------------------------------- geometria
def _malha():
    topo = json.loads((BRUTO / "ibge" / "malha_municipios.json").read_text(encoding="utf-8"))
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcos = []
    for arco in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arco:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcos.append(pts)
    return arcos, {g["properties"]["codarea"]: g for g in topo["objects"]["BRMU"]["geometries"]}


def _aneis(arcos, g):
    poligonos = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    saida = []
    for p in poligonos:
        for indices in p:
            pts = []
            for i in indices:
                seg = arcos[i] if i >= 0 else arcos[~i][::-1]
                pts.extend(seg if not pts else seg[1:])
            saida.append(np.array(pts))
    return saida


def _area(anel):
    x, y = anel[:, 0], anel[:, 1]
    return abs(np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])) / 2


def _distancia(pts, aneis):
    """Distância (nas unidades dos anéis) de cada ponto ao contorno mais próximo."""
    melhor = np.full(len(pts), np.inf)
    for a in aneis:
        ini, fim = a[:-1], a[1:]
        ab = fim - ini
        comp = np.maximum((ab ** 2).sum(1), 1e-18)
        for k, p in enumerate(pts):
            ap = p - ini
            t = np.clip((ap * ab).sum(1) / comp, 0, 1)
            d = np.sqrt(((ap - ab * t[:, None]) ** 2).sum(1)).min()
            melhor[k] = min(melhor[k], d)
    return melhor


def _simplificar(pts, tolerancia):
    """Douglas–Peucker (anel fechado: o primeiro ponto fica)."""
    if len(pts) < 5:
        return pts
    manter = np.zeros(len(pts), bool)
    manter[0] = manter[-1] = True
    pilha = [(0, len(pts) - 1)]
    while pilha:
        i, j = pilha.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        ab = b - a
        n = math.hypot(*ab)
        seg = pts[i + 1:j]
        if n < 1e-12:
            d = np.sqrt(((seg - a) ** 2).sum(1))
        else:
            d = np.abs(ab[0] * (seg[:, 1] - a[1]) - ab[1] * (seg[:, 0] - a[0])) / n
        k = int(np.argmax(d))
        if d[k] > tolerancia:
            m = i + 1 + k
            manter[m] = True
            pilha += [(i, m), (m, j)]
    return pts[manter]


def _moldura(x0, x1, y0, y1):
    """Alarga a caixa (centrada) até a proporção da caixa do mapa."""
    w, h = x1 - x0, y1 - y0
    alvo = MAPA_W / MAPA_H
    if w / h < alvo:
        extra = (h * alvo - w) / 2
        x0, x1 = x0 - extra, x1 + extra
    else:
        extra = (w / alvo - h) / 2
        y0, y1 = y0 - extra, y1 + extra
    return x0, x1, y0, y1


def _caminho(aneis, conv, casas=1):
    partes = []
    for a in aneis:
        p = conv(a)
        partes.append("M" + "L".join(f"{x:.{casas}f} {y:.{casas}f}" for x, y in p) + "Z")
    return "".join(partes)


def _bairros(loc, px, py, exemplo=None):
    """Até 4 bairros com mais locais no mapa, cada rótulo no centro (mediana) dos seus locais, sem encostar em outro,
    sem sair da caixa e sem cobrir o nome da escola de exemplo (o anel da ficha, na chegada à cidade). Cidade com menos
    de 25 locais no mapa fica sem rótulo (pouco ponto: o rótulo só polui)."""
    no_mapa = loc[px.notna()].assign(px=px, py=py)
    if len(no_mapa) < 25:
        return ""
    escolhidos = []
    if exemplo is not None and not np.isnan(exemplo[0]):
        # o anel (52 × 48 px) e o nome ao lado (até 210 × 40 px), como em T20 · Escolhido · HTML
        ex, ey = exemplo
        x_px, y_px = ex / 100 * MAPA_W, ey / 100 * MAPA_H
        x0, x1 = (x_px - 26, x_px + 22 + 222) if x_px <= MAPA_W * 0.62 else (x_px - 22 - 222, x_px + 26)
        escolhidos.append(("", (100 * x0 / MAPA_W, 100 * (y_px - 26) / MAPA_H, 100 * x1 / MAPA_W,
                                100 * (y_px + 32) / MAPA_H)))
    contagem = no_mapa.groupby("bairro").size().sort_values(ascending=False)
    for bairro, n in contagem.items():
        if n < 3 or sum(1 for t, _c in escolhidos if t) == 4 or not isinstance(bairro, str) or not bairro.strip():
            continue
        # "Zona rural" não é lugar: os pontos se espalham e a mediana cai no meio da cidade
        if re.search(r"\bRURAL\b", bairro.upper()):
            continue
        g = no_mapa[no_mapa.bairro == bairro]
        cx, cy = float(g.px.median()), float(g.py.median())
        if np.median(np.hypot(g.px - cx, (g.py - cy) * MAPA_H / MAPA_W)) > 9:
            continue                                        # bairro espalhado demais para um rótulo só
        texto = re.sub(r"\s*-\s*ZONA URBANA$", "", bairro.upper())
        w = (9.2 * len(texto) + 8) / MAPA_W * 100          # 12 px, caixa alta com espaçamento ≈ 9 px por letra
        h = 18 / MAPA_H * 100
        caixa = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        if caixa[0] < 1 or caixa[2] > 99 or caixa[1] < 1 or caixa[3] > 97:
            continue
        if any(not (caixa[2] + 1 < o[0] or o[2] + 1 < caixa[0] or caixa[3] + 0.6 < o[1] or o[3] + 0.6 < caixa[1])
               for _t, o in escolhidos):
            continue
        escolhidos.append((texto, caixa))
    escolhidos = [(t, c) for t, c in escolhidos if t]
    if len(escolhidos) < 2:
        return ""
    limpa = lambda t: re.sub(r"[|@]", " ", t)  # noqa: E731
    return "|".join(f"{limpa(t)}@{(c[0] + c[2]) / 2:.1f}@{(c[1] + c[3]) / 2:.1f}" for t, c in escolhidos)


def _espaco(px, py):
    """Mediana da distância ao vizinho mais próximo, em % da largura da moldura (dá o tamanho dos pontos)."""
    xy = np.column_stack([px, py * MAPA_H / MAPA_W])
    if len(xy) < 2:
        return 10.0
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(2))
    np.fill_diagonal(d, np.inf)
    return float(np.median(d.min(1)))


def _cortar(anel, caixa):
    """Sutherland–Hodgman: o anel cortado no retângulo (x0, x1, y0, y1)."""
    x0, x1, y0, y1 = caixa
    pts = [tuple(p) for p in anel[:-1]] if len(anel) > 1 and np.allclose(anel[0], anel[-1]) else [tuple(p) for p in anel]
    for dentro, cruza in (
            (lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
            (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
            (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
            (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))):
        if not pts:
            break
        saida = []
        for i, b in enumerate(pts):
            a = pts[i - 1]
            if dentro(b):
                if not dentro(a):
                    saida.append(cruza(a, b))
                saida.append(b)
            elif dentro(a):
                saida.append(cruza(a, b))
        pts = saida
    if not pts:
        return np.empty((0, 2))
    return np.array(pts + [pts[0]])


def _nn(xy):
    if len(xy) < 2:
        return np.inf
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(2))
    np.fill_diagonal(d, np.inf)
    return float(np.median(d.min(1)))


def _enquadrar(pts, inteira):
    """Moldura da cidade inteira ou recorte na mancha urbana. Mede a leitura pelo espaço entre vizinhos (mediana da
    distância ao local mais próximo, em px da caixa do mapa): com 5 px ou mais na cidade inteira, fica a cidade inteira.
    Abaixo disso:
    1. a mancha urbana: o maior grupo de locais encadeados a até 3 km um do outro (4 km se o de 3 km não tiver 65 % dos
       locais), com 8 % de folga; vale se tiver 65 % dos locais ou mais, nenhum outro grupo tiver o tamanho de uma
       cidade-satélite (12 locais ou 5 %) e a leitura melhorar 1,6 vez;
    2. senão (cidade sem uma mancha só, como o DF), caixas na proporção do mapa que cobrem 97 %, 95 % … 85 % dos locais
       (centradas onde a caixa fica menor, com 12 % de folga): a primeira com 5 px, deixando de fora até 5 % dos locais
       (senão a de mais espaço), se ganhar 1,6 vez; e, se a leitura ainda ficar abaixo de 3 px, até 15 % de fora, se
       ganhar 2,5 vezes.
    Devolve (moldura ou None, texto para o registro)."""
    from scipy.cluster.hierarchy import fcluster, linkage
    x0, x1, y0, y1 = inteira
    px_unid = MAPA_W / (x1 - x0)
    n = len(pts)
    nn_inteira = _nn(pts) * px_unid
    texto = f"inteira {nn_inteira:.1f} px"
    if nn_inteira >= 5 or n < 10:
        return None, texto
    arvore = linkage(pts, "single")
    q = None
    for km in (3.0, 4.0):
        grupo = fcluster(arvore, km / 111.2, "distance")
        tamanhos = np.sort(np.bincount(grupo))[::-1]
        # mancha única: o maior grupo com 65 % dos locais e nenhum outro do tamanho de uma cidade-satélite (o DF)
        if tamanhos[0] >= 0.65 * n and (len(tamanhos) < 2 or tamanhos[1] < max(12, 0.05 * n)):
            q = pts[grupo == np.bincount(grupo).argmax()]
            break
    if q is not None:
        (gx0, gy0), (gx1, gy1) = q.min(0), q.max(0)
        mx, my = (gx1 - gx0) * 0.08 + 0.5 / 111.2, (gy1 - gy0) * 0.08 + 0.5 / 111.2
        caixa = _moldura(gx0 - mx, gx1 + mx, gy0 - my, gy1 + my)
        dentro = ((pts[:, 0] > caixa[0]) & (pts[:, 0] < caixa[1]) & (pts[:, 1] > caixa[2]) & (pts[:, 1] < caixa[3]))
        nn = _nn(pts[dentro]) * MAPA_W / (caixa[1] - caixa[0])
        if nn >= 1.6 * nn_inteira:
            return caixa, (f"{texto} → mancha urbana ({len(q) / n:.0%} dos locais, {km:.0f} km): {nn:.1f} px, "
                           f"{int(n - dentro.sum())} de fora")
    alvo = MAPA_W / MAPA_H
    d = np.maximum(np.abs(pts[:, None, 0] - pts[None, :, 0]) / alvo, np.abs(pts[:, None, 1] - pts[None, :, 1]))
    ordenada = np.sort(d, 1)
    opcoes = []
    for frac in (0.97, 0.95, 0.92, 0.90, 0.87, 0.85):
        rk = ordenada[:, math.ceil(frac * n) - 1]
        i = int(rk.argmin())
        r = max(rk[i] * 1.12, 3 / 111.2 / 2)
        cx, cy = pts[i]
        caixa = (cx - r * alvo, cx + r * alvo, cy - r, cy + r)
        dentro = ((pts[:, 0] > caixa[0]) & (pts[:, 0] < caixa[1]) & (pts[:, 1] > caixa[2]) & (pts[:, 1] < caixa[3]))
        opcoes.append((frac, caixa, _nn(pts[dentro]) * MAPA_W / (caixa[1] - caixa[0]), int(n - dentro.sum())))

    def escolher(limite, meta):
        ok = [o for o in opcoes if o[3] <= limite * n]
        if not ok:
            return None
        return next((o for o in ok if o[2] >= meta), max(ok, key=lambda o: o[2]))

    o1 = escolher(0.05, 5)
    o1 = o1 if o1 and o1[2] >= 1.6 * nn_inteira else None
    melhor = o1[2] if o1 else nn_inteira
    if melhor < 3:
        o2 = escolher(0.15, 4)
        if o2 and o2[2] >= 2.5 * nn_inteira and o2[2] > melhor:
            o1 = o2
    if o1:
        return o1[1], f"{texto} → recorte {o1[0]:.0%}: {o1[2]:.1f} px, {o1[3]} de fora"
    return None, texto


def geometria(cod_ibge, loc, arcos, geo):
    """Moldura, contorno e posições de uma cidade. Devolve (px, py, fora, registro)."""
    aneis = _aneis(arcos, geo[cod_ibge])
    lat0 = np.mean([a[:, 1].mean() for a in aneis])
    cos0 = math.cos(math.radians(lat0))
    proj = lambda a: np.column_stack([a[:, 0] * cos0, a[:, 1]])  # noqa: E731
    aneis = [proj(a) for a in aneis]
    tem = loc.lat.notna().values
    pts = np.column_stack([loc.lon.values * cos0, loc.lat.values])
    # anéis: o maior, os que têm local dentro e os grandes (ilha sem eleitor e pequena sai)
    areas = [_area(a) for a in aneis]
    maior = max(areas)
    com_local = [Caminho(a).contains_points(pts[tem]).any() for a in aneis]
    aneis = [a for a, ar, c in zip(aneis, areas, com_local) if ar == maior or c or ar >= 0.3 * maior]
    # coordenada longe do contorno: errada
    dentro = np.zeros(len(pts), bool)
    for a in aneis:
        dentro[tem] |= Caminho(a).contains_points(pts[tem])
    longe = np.zeros(len(pts), bool)
    fora_idx = np.where(tem & ~dentro)[0]
    if len(fora_idx):
        dist_km = _distancia(pts[fora_idx], aneis) * 111.2
        longe[fora_idx[dist_km > LONGE]] = True
    valido = tem & ~longe
    todos = np.vstack([np.vstack(aneis), pts[valido]])
    cx0, cy0 = todos.min(0)
    cx1, cy1 = todos.max(0)
    fx, fy = (cx1 - cx0) * FOLGA, (cy1 - cy0) * FOLGA
    caixa_c = (cx0 - fx, cx1 + fx, cy0 - fy, cy1 + fy)
    x0, x1, y0, y1 = _moldura(*caixa_c)
    recorte, info = _enquadrar(pts[valido], (x0, x1, y0, y1))
    if recorte:
        x0, x1, y0, y1 = recorte
    em_x = lambda v: 100 * (v - x0) / (x1 - x0)  # noqa: E731
    em_y = lambda v: 100 * (y1 - v) / (y1 - y0)  # noqa: E731
    px = np.where(valido, em_x(pts[:, 0]), np.nan)
    py = np.where(valido, em_y(pts[:, 1]), np.nan)
    fora_moldura = valido & ((px < 0.5) | (px > 99.5) | (py < 0.5) | (py > 99.5))
    fora = np.where(~valido, "sem endereço", np.where(fora_moldura, "fora do recorte", ""))
    px = np.where(fora == "", px, np.nan)
    py = np.where(fora == "", py, np.nan)
    tol = 0.0012 * max(x1 - x0, y1 - y0)
    # no recorte, o contorno é cortado numa caixa folgada em volta da moldura (o que fica fora não aparece e só pesaria)
    folga_x, folga_y = (x1 - x0) * 0.25, (y1 - y0) * 0.25
    corte = (x0 - folga_x, x1 + folga_x, y0 - folga_y, y1 + folga_y)
    simples = [_simplificar(a, tol) for a in (_cortar(a, corte) for a in aneis) if len(a) >= 4]
    contorno = _caminho(simples, lambda a: np.column_stack([em_x(a[:, 0]), em_y(a[:, 1])]))
    reg = {"recorte": int(bool(recorte)), "contorno": contorno, "inteiro": "", "moldura": "", "canto": "",
           "_enquadramento": info}
    if recorte:
        # o mapinha: a cidade inteira num quadrado, com o retângulo do recorte
        qx0, qx1, qy0, qy1 = caixa_c
        lado_q = max(qx1 - qx0, qy1 - qy0)
        mx, my = (qx0 + qx1) / 2, (qy0 + qy1) / 2
        qx0, qy1 = mx - lado_q / 2, my + lado_q / 2
        qx = lambda v: 100 * (v - qx0) / lado_q  # noqa: E731
        qy = lambda v: 100 * (qy1 - v) / lado_q  # noqa: E731
        grossos = [_simplificar(a, 0.006 * lado_q) for a in aneis]
        reg["inteiro"] = _caminho(grossos, lambda a: np.column_stack([qx(a[:, 0]), qy(a[:, 1])]))
        reg["moldura"] = f"{qx(x0):.1f} {qy(y1):.1f} {100 * (x1 - x0) / lado_q:.1f} {100 * (y1 - y0) / lado_q:.1f}"
        # canto com menos pontos (o mapinha tem ~130 px de lado)
        cw, ch = 140 / MAPA_W * 100, 140 / MAPA_H * 100
        cantos = {"so": (0, 100 - ch, cw, 100), "se": (100 - cw, 100 - ch, 100, 100), "no": (0, 0, cw, ch),
                  "ne": (100 - cw, 0, 100, ch)}
        ok = ~np.isnan(px)
        n = {k: int(((px[ok] >= a) & (px[ok] <= c) & (py[ok] >= b) & (py[ok] <= d)).sum())
             for k, (a, b, c, d) in cantos.items()}
        reg["canto"] = min(["so", "se", "no", "ne"], key=lambda k: n[k])
    return px, py, fora, reg


# ---------------------------------------------------------------------------------------------------- tabela
def _cidade(uf, cd_tse, cod_ibge, nome, loc_c, arcos, geo):
    chave = ["NR_ZONA", "NR_LOCAL_VOTACAO"]
    antes = loc_c[loc_c.ano < 2026].groupby(["ano"] + chave)[["pt", "adv", "validos"]].sum().unstack("ano")
    antes.columns = [f"{c}_{a}" for c, a in antes.columns]
    a26 = loc_c[loc_c.ano == 2026].rename(columns={"pt": "pt_2026", "adv": "adv_2026", "validos": "validos_2026"})
    a26 = a26.merge(antes, left_on=chave, right_index=True, how="left")
    a26 = a26.sort_values(chave + ["NM_LOCAL_VOTACAO"]).reset_index(drop=True)
    for c in ("pt_2022", "adv_2022", "validos_2022", "pt_2018", "adv_2018", "validos_2018"):
        if c not in a26:
            a26[c] = np.nan
    a26["nome"] = a26.NM_LOCAL_VOTACAO.map(titulo)
    repetidos = a26.nome.duplicated(keep=False)
    a26.loc[repetidos, "nome"] = a26.loc[repetidos].apply(lambda r: f"{r.nome} (local {r.NR_LOCAL_VOTACAO})", axis=1)
    repetidos = a26.nome.duplicated(keep=False)          # mesmo nome e número em zonas diferentes
    a26.loc[repetidos, "nome"] = a26.loc[repetidos].apply(
        lambda r: r.nome.replace(" (local ", f" (zona {r.NR_ZONA}, local "), axis=1)
    if a26.nome.duplicated().any():
        raise SystemExit(f"{nome}: nome de local repetido na cidade")
    a26["bairro"] = a26.bairro.map(titulo)
    px, py, fora, reg = geometria(cod_ibge, a26, arcos, geo)
    a26["px"], a26["py"], a26["fora_mapa"] = px, py, fora
    # a lista da tela: da maior queda da margem de Lula à maior alta; os locais novos no fim, por nome
    m22 = (a26.pt_2022 - a26.adv_2022) / a26.validos_2022
    m26 = (a26.pt_2026 - a26.adv_2026) / a26.validos_2026
    a26["_var"] = m26 - m22
    a26["_nome"] = a26.nome.map(_chave_pt)
    ordem = a26.sort_values(["_var", "_nome"], na_position="last").index
    a26.loc[ordem, "pos_queda"] = range(1, len(a26) + 1)
    ordem = a26.sort_values("_nome").index
    a26.loc[ordem, "ordem_nome"] = range(1, len(a26) + 1)
    # exemplo da ficha: em todas as cidades, a escola que virou com mais votos válidos
    # ou, se nenhuma virou, a de maior queda — entre as que estão no mapa (o anel aparece), se houver
    virou = (m22 > 0) & (m26 < 0)
    no_mapa = a26.fora_mapa == ""
    if virou.any():
        i_ex, tipo = a26[virou & no_mapa if (virou & no_mapa).any() else virou].validos_2026.idxmax(), "virou"
    else:
        i_ex, tipo = a26[no_mapa if (no_mapa & a26._var.notna()).any() else a26._var.notna()]._var.idxmin(), "queda"
    # locais de 2022 como o TSE os listou naquele ano (zona, número, nome e endereço), e em quantos Lula ficou à frente
    l22 = loc_c[loc_c.ano == 2022]
    registro = {
        "cod_ibge": cod_ibge, "cod_tse": cd_tse, "uf": uf, "nome": nome, "cidade": f"{nome} ({uf})",
        "grupo": GRUPO_T20[cod_ibge], "locais_2022": len(l22), "lula_2022": int((l22.pt > l22.adv).sum()),
        "_i_exemplo": i_ex, "exemplo": tipo, "espaco": round(_espaco(px[~np.isnan(px)], py[~np.isnan(py)]), 2),
        "bairros": _bairros(a26, a26.px, a26.py, (a26.px[i_ex], a26.py[i_ex])), **reg}
    a26["cod_ibge"], a26["uf"], a26["cidade"] = cod_ibge, uf, f"{nome} ({uf})"
    return a26, registro


def prova(loc, cidades):
    """Soma dos válidos de 2026 por local × válidos de presidente do município (TSE, arquivo por município e zona)."""
    p = pd.read_csv(BRUTO / "tse" / "presidente_2026_BR.csv", sep=";", encoding="latin1", dtype=str,
                    usecols=["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "QT_VOTOS_NOMINAIS_VALIDOS"])
    p = p[p.NR_TURNO == "1"]
    p["v"] = p.QT_VOTOS_NOMINAIS_VALIDOS.astype(int)
    tse = p.groupby([p.SG_UF, p.CD_MUNICIPIO.astype(int)]).v.sum()
    linhas = []
    for _i, c in cidades.iterrows():
        t = loc[loc.cod_ibge == c.cod_ibge]
        lula26 = int((t.pt_2026 > t.adv_2026).sum())
        viraram = int(((t.pt_2022 > t.adv_2022) & (t.pt_2026 < t.adv_2026)).sum())
        para_lula = int(((t.pt_2022 < t.adv_2022) & (t.pt_2026 > t.adv_2026)).sum())
        soma = int(t.validos_2026.sum())
        oficial = int(tse.get((c.uf, int(c.cod_tse)), -1))
        linhas.append({"cidade": c.cidade, "locais": len(t), "lula_2026": lula26, "locais_2022": c.locais_2022,
                       "lula_2022": c.lula_2022, "viraram": viraram, "para_lula": para_lula, "validos_locais": soma, "validos_tse": oficial,
                       "diferenca": soma - oficial, "sem_endereco": int((t.fora_mapa == "sem endereço").sum()),
                       "fora_recorte": int((t.fora_mapa == "fora do recorte").sum()), "recorte": c.recorte})
    return pd.DataFrame(linhas)


def main():
    bruto = pd.read_csv(BRUTO / "tse" / "locais_t20.csv", dtype={"cd_ibge": str})
    arcos, geo = _malha()
    # ordem das cidades no filtro e nos ids: a cidade inicial e as outras em ordem alfabética
    ordem = sorted(CIDADES_T20, key=lambda c: (c[2] != CIDADE_INICIAL, _chave_pt(c[3])))
    partes, regs = [], []
    for k, (uf, cd_tse, cod_ibge, nome) in enumerate(ordem, start=1):
        t, r = _cidade(uf, cd_tse, cod_ibge, nome, bruto[bruto.cd_ibge == cod_ibge], arcos, geo)
        r["ordem"] = k
        partes.append(t)
        regs.append(r)
    loc = pd.concat(partes, ignore_index=True)
    loc["id"] = range(1, len(loc) + 1)
    # a chave da tabela (Local, ordenada por Id) é única no modelo inteiro: nome repetido em outra cidade ganha a cidade
    loc["local"] = loc.nome
    rep = loc.local.duplicated(keep=False)
    loc.loc[rep, "local"] = loc.loc[rep, "nome"] + " · " + loc.loc[rep, "cidade"]
    if loc.local.duplicated().any():
        raise SystemExit(f"Local repetido: {loc.local[loc.local.duplicated()].tolist()[:5]}")
    # o exemplo de cada cidade vira id
    base = 0
    for t, r in zip(partes, regs):
        r["id_exemplo"] = int(loc.id.iloc[base + t.index.get_loc(r.pop("_i_exemplo"))])
        base += len(t)
    saida = loc.rename(columns={"NR_ZONA": "zona", "NR_LOCAL_VOTACAO": "numero"})[
        ["id", "cod_ibge", "cidade", "uf", "local", "nome", "bairro", "zona", "numero", "secoes", "pt_2026", "adv_2026",
         "validos_2026", "pt_2022", "adv_2022", "validos_2022", "pt_2018", "adv_2018", "validos_2018", "px", "py",
         "fora_mapa", "pos_queda", "ordem_nome"]]
    for c in ("pt_2022", "adv_2022", "validos_2022", "pt_2018", "adv_2018", "validos_2018", "pos_queda", "ordem_nome"):
        saida[c] = saida[c].astype("Int64")
    # a chave só vai escrita quando difere do nome (o M da T20 Local completa com o nome): 400 kB a menos no CSV
    saida["local"] = saida.local.where(saida.local != saida.nome, "")
    saida["px"] = saida.px.round(2)
    saida["py"] = saida.py.round(2)
    saida.to_csv(DESTINO, index=False, encoding="utf-8", lineterminator="\n")
    cidades = pd.DataFrame(regs)[["cod_ibge", "cod_tse", "uf", "nome", "cidade", "grupo", "ordem", "locais_2022",
                                  "lula_2022", "id_exemplo", "exemplo", "recorte", "espaco", "canto", "bairros",
                                  "moldura", "contorno", "inteiro"]]
    cidades.to_csv(DESTINO_CIDADES, index=False, encoding="utf-8", lineterminator="\n")
    for r in regs:
        print(f"{r['cidade']:24s} {r['_enquadramento']} · espaço {r['espaco']} % · rótulos: {r['bairros'] or '—'}")
    tab = prova(saida, cidades)
    pd.set_option("display.width", 200)
    print(tab.to_string(index=False))
    print(f"\nt20_locais.csv · {len(saida):,} locais · {DESTINO.stat().st_size / 1e6:.2f} MB")
    print(f"t20_cidades.csv · {len(cidades)} cidades · {DESTINO_CIDADES.stat().st_size / 1e3:.0f} kB · maior contorno "
          f"{cidades.contorno.str.len().max():,} caracteres")
    if (tab.diferenca != 0).any():
        raise SystemExit("soma dos válidos por local diferente do total do município: ver a tabela")
    return tab


if __name__ == "__main__":
    main()
