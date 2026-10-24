"""Exporta as tabelas que o Power BI lê (dados/pbi/*.csv) a partir das saídas do pipeline e dos levantamentos.

O modelo do painel (pbi/scripts/gerar_modelo.py) lê estes arquivos pelo endereço raw do repositório público no GitHub;
nada aqui é calculado para a tela: são grãos limpos (município × ano, candidato × UF × ano, pesquisa, marco…), e as
contas ficam no DAX. Separador vírgula, UTF-8 sem BOM, ponto decimal, datas ISO.

Também grava a geometria que os desenhos usam (pbi/assets/mapas/): os contornos das UFs simplificados num quadro de
1000 × 1000 (para SVG inline nos HTML Content) e a mesma projeção para os pontos dos municípios (colunas x, y).

    python -I -X utf8 pipeline/exportar_pbi.py
"""

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA_DADOS = RAIZ / "dados" / "saida"
BRUTO = RAIZ / "dados" / "bruto"
DESTINO = RAIZ / "dados" / "pbi"
MAPAS = RAIZ / "pbi" / "assets" / "mapas"
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]
COS = math.cos(math.radians(15))
PORTES = [(0, 10_000, "até 10 mil"), (10_000, 50_000, "10 a 50 mil"), (50_000, 200_000, "50 a 200 mil"),
          (200_000, 1_000_000, "200 mil a 1 milhão"), (1_000_000, 10**9, "mais de 1 milhão")]
QUINTOS = ["mais pobres", "2º quinto", "3º quinto", "4º quinto", "mais ricas"]
NOMES_CURTOS = {"LULA": "Lula", "FLAVIO BOLSONARO": "Flávio Bolsonaro", "JAIR BOLSONARO": "Jair Bolsonaro",
                "GERALDO ALCKMIN": "Geraldo Alckmin", "JOSÉ SERRA": "José Serra", "AÉCIO NEVES": "Aécio Neves",
                "DILMA": "Dilma Rousseff", "FERNANDO HADDAD": "Fernando Haddad", "CIRO GOMES": "Ciro Gomes",
                "MARINA SILVA": "Marina Silva", "ESCRITOR AUGUSTO CURY": "Augusto Cury", "RENAN SANTOS": "Renan Santos",
                "RONALDO CAIADO": "Ronaldo Caiado", "HELOÍSA HELENA": "Heloísa Helena", "SIMONE TEBET": "Simone Tebet",
                "CRISTOVAM": "Cristovam Buarque", "PASTOR EVERALDO": "Pastor Everaldo"}


def nome_curto(n):
    return NOMES_CURTOS.get(str(n).upper().strip(), str(n).title())


def gravar(df, nome):
    DESTINO.mkdir(parents=True, exist_ok=True)
    df.to_csv(DESTINO / f"{nome}.csv", index=False, encoding="utf-8", lineterminator="\n")
    print(f"{nome}.csv · {len(df)} linhas · {', '.join(df.columns)}")


# ---------------------------------------------------------------------------------------------------- geometria
def decodificar(topo, objeto):
    """TopoJSON quantizada → {código: [polígono: [anel: array (lon, lat)]]}."""
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

    def anel(indices):
        pts = []
        for i in indices:
            seg = arcos[i] if i >= 0 else arcos[~i][::-1]
            pts.extend(seg if not pts else seg[1:])
        return np.array(pts)

    formas = {}
    for g in topo["objects"][objeto]["geometries"]:
        poligonos = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        formas[str(g["properties"]["codarea"])] = [[anel(a) for a in p] for p in poligonos]
    return formas


def centro(poligonos):
    """Centroide de área do maior polígono (lon, lat)."""
    melhor, area_max = None, -1
    for p in poligonos:
        a = p[0]
        x, y = a[:, 0], a[:, 1]
        cruz = x[:-1] * y[1:] - x[1:] * y[:-1]
        area = cruz.sum() / 2
        if abs(area) < 1e-12:
            c = a.mean(axis=0)
        else:
            c = np.array([((x[:-1] + x[1:]) * cruz).sum() / (6 * area), ((y[:-1] + y[1:]) * cruz).sum() / (6 * area)])
        if abs(area) > area_max:
            melhor, area_max = c, abs(area)
    return melhor


class Projecao:
    """lon/lat → quadro 1000 × 1000 (x para a direita, y para baixo), com o Brasil centrado e o cosseno de 15°."""

    def __init__(self, formas, lado=1000, folga=10):
        pts = np.vstack([a for ps in formas.values() for p in ps for a in p])
        self.x0, self.x1 = pts[:, 0].min() * COS, pts[:, 0].max() * COS
        self.y0, self.y1 = pts[:, 1].min(), pts[:, 1].max()
        util = lado - 2 * folga
        self.k = util / max(self.x1 - self.x0, self.y1 - self.y0)
        self.dx = folga + (util - (self.x1 - self.x0) * self.k) / 2
        self.dy = folga + (util - (self.y1 - self.y0) * self.k) / 2

    def __call__(self, lon, lat):
        return (np.asarray(lon) * COS - self.x0) * self.k + self.dx, (self.y1 - np.asarray(lat)) * self.k + self.dy


def rdp(pts, eps):
    """Douglas-Peucker iterativo."""
    if len(pts) < 3:
        return pts
    manter = np.zeros(len(pts), bool)
    manter[0] = manter[-1] = True
    pilha = [(0, len(pts) - 1)]
    while pilha:
        i, j = pilha.pop()
        a, b = pts[i], pts[j]
        seg = pts[i + 1:j]
        if len(seg) == 0:
            continue
        ab = b - a
        n = np.hypot(*ab)
        rel = seg - a
        d = np.abs(ab[0] * rel[:, 1] - ab[1] * rel[:, 0]) / n if n > 0 else np.hypot(rel[:, 0], rel[:, 1])
        k = int(np.argmax(d))
        if d[k] > eps:
            m = i + 1 + k
            manter[m] = True
            pilha += [(i, m), (m, j)]
    return pts[manter]


def caminho_svg(poligonos, proj, eps):
    partes = []
    for p in poligonos:
        for anel in p:
            x, y = proj(anel[:, 0], anel[:, 1])
            s = rdp(np.column_stack([x, y]), eps)
            if len(s) < 4:
                continue
            partes.append("M" + "L".join(f"{px:.1f},{py:.1f}" for px, py in s[:-1]) + "Z")
    return "".join(partes)


def geometria(municipios):
    uf_topo = json.loads((BRUTO / "ibge" / "malha_uf.json").read_text(encoding="utf-8"))
    mun_topo = json.loads((BRUTO / "ibge" / "malha_municipios.json").read_text(encoding="utf-8"))
    ufs = decodificar(uf_topo, next(iter(uf_topo["objects"])))
    muns = decodificar(mun_topo, next(iter(mun_topo["objects"])))
    proj = Projecao(ufs)
    cod_uf = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI",
              "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
              "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
    caminhos = {cod_uf[c]: caminho_svg(p, proj, 1.2) for c, p in ufs.items()}
    MAPAS.mkdir(parents=True, exist_ok=True)
    (MAPAS / "uf_caminhos.json").write_text(json.dumps({"viewBox": "0 0 1000 1000", "caminhos": caminhos},
                                                       ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"uf_caminhos.json · {sum(len(v) for v in caminhos.values())} caracteres de caminho")
    linhas = []
    for cod, p in muns.items():
        lon, lat = centro(p)
        x, y = proj(lon, lat)
        linhas.append((cod, round(float(lon), 5), round(float(lat), 5), round(float(x), 2), round(float(y), 2)))
    cent = pd.DataFrame(linhas, columns=["cd_ibge", "lon", "lat", "x", "y"])
    return municipios.merge(cent, on="cd_ibge", how="left")


# ---------------------------------------------------------------------------------------------------- tabelas
def municipios():
    m = pd.read_csv(SAIDA_DADOS / "municipios.csv", dtype={"cd_ibge": str})
    m["porte_ordem"] = pd.cut(m.populacao, [p[0] for p in PORTES] + [PORTES[-1][1]], labels=False, right=False) + 1
    m["porte_ordem"] = m.porte_ordem.astype("Int64")
    m["porte"] = m.porte_ordem.map({i + 1: p[2] for i, p in enumerate(PORTES)})
    m["quinto_ordem"] = pd.qcut(m.renda_pc, 5, labels=False) + 1
    m["quinto_ordem"] = m.quinto_ordem.astype("Int64")
    m["quinto"] = m.quinto_ordem.map({i + 1: q for i, q in enumerate(QUINTOS)})
    m = geometria(m)
    sem = m[m.x.isna()]
    if len(sem):
        print(f"aviso: {len(sem)} município(s) sem polígono na malha: {', '.join(sem.nome + '/' + sem.uf)}")
    m["rotulo"] = m.nome + " (" + m.uf + ")"
    cols = ["cd_ibge", "cd_tse", "nome", "uf", "regiao", "rotulo", "populacao", "renda_pc", "porte", "porte_ordem",
            "quinto", "quinto_ordem", "lon", "lat", "x", "y"]
    m = m[cols].sort_values("cd_ibge")
    m["populacao"] = m.populacao.round().astype("Int64")
    return m


def municipio_ano():
    v = pd.read_csv(SAIDA_DADOS / "votos_municipio.csv", dtype={"cd_ibge": str})
    c = pd.read_csv(SAIDA_DADOS / "comparecimento_municipio.csv", dtype={"cd_ibge": str})
    d = v.merge(c[["ano", "cd_ibge", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"]],
                on=["ano", "cd_ibge"], how="left")
    d = d[["ano", "cd_ibge", "pt", "adv", "demais", "validos", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"]]
    for col in d.columns[2:]:
        d[col] = d[col].round().astype("Int64")
    return d.sort_values(["ano", "cd_ibge"])


def candidatos():
    n = pd.read_csv(SAIDA_DADOS / "nacional.csv")
    n["nome"] = n.NM_URNA_CANDIDATO.map(nome_curto)
    n["posicao"] = n.groupby("ano").votos.rank(ascending=False, method="first").astype(int)
    n = n.rename(columns={"NR_CANDIDATO": "numero", "SG_PARTIDO": "partido", "validos_ano": "validos"})
    return n[["ano", "numero", "nome", "partido", "votos", "validos", "posicao"]].sort_values(["ano", "posicao"])


def candidatos_uf():
    """Votos por candidato e UF nos 1º turnos de 2022 e 2026 (inclui ZZ, exterior), do arquivo bruto do TSE."""
    partes = []
    for ano in (2022, 2026):
        arq = BRUTO / "tse" / f"presidente_{ano}_BR.csv"
        if not arq.exists():
            print(f"aviso: {arq.name} não está na máquina (pipeline/extrair_tse.py); candidato_uf sem {ano}")
            continue
        b = pd.read_csv(arq, sep=";", encoding="latin-1",
                        usecols=["NR_TURNO", "SG_UF", "NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO",
                                 "QT_VOTOS_NOMINAIS_VALIDOS"])
        b = b[(b.NR_TURNO == 1) & (b.SG_UF != "VT")]
        g = b.groupby(["SG_UF", "NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO"], as_index=False) \
             .QT_VOTOS_NOMINAIS_VALIDOS.sum()
        g.insert(0, "ano", ano)
        partes.append(g)
    d = pd.concat(partes)
    d.columns = ["ano", "uf", "numero", "nome", "partido", "votos"]
    d["nome"] = d.nome.map(nome_curto)
    return d.sort_values(["ano", "uf", "votos"], ascending=[True, True, False])


def pesquisas():
    partes = []
    for turno, arq in ((1, "pesquisas_1turno.csv"), (2, "pesquisas_2turno.csv")):
        p = pd.read_csv(BRUTO / "pesquisas" / arq, sep=";")
        p.insert(0, "cenario", f"{turno}º turno")
        if "momento" not in p:
            p["momento"] = ""
        partes.append(p)
    p = pd.concat(partes, ignore_index=True)
    p.insert(0, "id", range(1, len(p) + 1))
    cols = ["id", "cenario", "instituto", "contratante", "campo_inicio", "campo_fim", "divulgacao", "registro_tse",
            "amostra", "margem_pp", "modo", "tipo", "lula", "flavio", "cury", "renan", "outros", "brancos_nulos",
            "indecisos", "momento", "fonte_url"]
    return p[cols]


def copiar(origem, sep=";"):
    return pd.read_csv(origem, sep=sep)


def trajetoria():
    t = json.loads((BRUTO / "trajetoria" / "trajetoria.json").read_text(encoding="utf-8"))
    linhas = []
    for lado, nome in (("lula", "Lula"), ("flavio", "Flávio")):
        for i, m in enumerate(t[lado], 1):
            data = str(m["data"])
            ano = int(data[:4]) if data[:4].isdigit() else int(data[-4:])
            # marco sem foto livre: a ilustração recriada ocupa a coluna foto (o desenho do cartão); ver desenhos.csv, tipo
            foto = m.get("foto") or m.get("ilustracao") or {}
            linhas.append({"candidato": nome, "ordem": i, "data": data, "ano": ano, "titulo": m["titulo"],
                           "texto": m["texto"], "foto": Path(foto["arquivo"]).stem if foto else "",
                           "foto_autor": foto.get("autor", ""), "foto_licenca": foto.get("licenca", "").split(" (")[0],
                           "foto_ano": foto.get("ano_foto", ""), "fonte_url": m.get("fonte_url", "")})
    return pd.DataFrame(linhas)


def exterior():
    """Votos do 1º turno no exterior por país (2022 e 2026): as 186 cidades com seção do TSE ligadas ao país pela tabela
    dados/bruto/exterior/cidade_pais.csv (o TSE não publica o país). PT = Lula; adversário = Bolsonaro (2022) e Flávio
    (2026), os dois com o número 22."""
    mapa = pd.read_csv(BRUTO / "exterior" / "cidade_pais.csv", sep=";")
    por_cod = dict(zip(mapa.cd_tse, zip(mapa.pais, mapa.continente)))
    por_nome = dict(zip(mapa.cidade, zip(mapa.pais, mapa.continente)))
    partes = []
    for ano in (2022, 2026):
        arq = BRUTO / "tse" / f"presidente_{ano}_BR.csv"
        if not arq.exists():
            continue
        b = pd.read_csv(arq, sep=";", encoding="latin-1",
                        usecols=["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_CANDIDATO",
                                 "QT_VOTOS_NOMINAIS_VALIDOS"])
        b = b[(b.NR_TURNO == 1) & (b.SG_UF == "ZZ")]
        g = b.groupby(["CD_MUNICIPIO", "NM_MUNICIPIO"]).apply(
            lambda x: pd.Series({"pt": x.loc[x.NR_CANDIDATO == 13, "QT_VOTOS_NOMINAIS_VALIDOS"].sum(),
                                 "adv": x.loc[x.NR_CANDIDATO == 22, "QT_VOTOS_NOMINAIS_VALIDOS"].sum(),
                                 "validos": x.QT_VOTOS_NOMINAIS_VALIDOS.sum()}), include_groups=False).reset_index()
        def pais(r):
            return por_cod.get(r.CD_MUNICIPIO) or por_nome.get(r.NM_MUNICIPIO) or ("?", "?")
        g[["pais", "continente"]] = g.apply(lambda r: pd.Series(pais(r)), axis=1)
        faltam = g[g.pais == "?"]
        if len(faltam):
            print(f"aviso {ano}: cidades do exterior sem país: {', '.join(faltam.NM_MUNICIPIO)}")
        c = g.groupby(["pais", "continente"], as_index=False).agg(cidades=("NM_MUNICIPIO", "nunique"),
                                                                  pt=("pt", "sum"), adv=("adv", "sum"),
                                                                  validos=("validos", "sum"))
        c.insert(0, "ano", ano)
        partes.append(c)
    d = pd.concat(partes)
    for col in ("pt", "adv", "validos"):
        d[col] = d[col].astype(int)
    return d.sort_values(["ano", "validos"], ascending=[True, False])


# Lentes da tela "quem vota em quem" (pedido do Alisson, 23/10/2026): coluna de dados/saida/social_municipio.csv
LENTES = [("Renda", "renda_pc"), ("Escolaridade", "escol_medio"), ("Bolsa Família", "bf_100dom"), ("IDH", "idhm")]


def social():
    """Município × lente: o valor do indicador e o degrau (1 a 5) em que o município cai quando os municípios são
    postos em fila pelo indicador e a fila é cortada em cinco partes com o mesmo número de eleitores (aptos de 2026).
    O município fica inteiro no degrau em que cai o meio dos seus eleitores; sem o indicador, fica fora da lente."""
    s = pd.read_csv(SAIDA_DADOS / "social_municipio.csv", dtype={"cd_ibge": str})
    aptos = pd.read_csv(SAIDA_DADOS / "comparecimento_municipio.csv", dtype={"cd_ibge": str})
    aptos = aptos[aptos.ano == 2026][["cd_ibge", "aptos"]]
    s = s.merge(aptos, on="cd_ibge", how="inner")
    partes = []
    for ordem, (lente, coluna) in enumerate(LENTES, 1):
        d = s[["cd_ibge", coluna, "aptos"]].dropna().sort_values([coluna, "cd_ibge"]).rename(columns={coluna: "valor"})
        meio = d.aptos.cumsum() - d.aptos / 2
        d["degrau"] = np.minimum(5, np.floor(5 * meio / d.aptos.sum()) + 1).astype(int)
        d["lente"], d["lente_ordem"] = lente, ordem
        partes.append(d[["cd_ibge", "lente", "lente_ordem", "valor", "degrau"]])
    return pd.concat(partes, ignore_index=True)


LENTE_DA_DIMENSAO = {"renda": "Renda", "escolaridade": "Escolaridade", "bolsa_familia": "Bolsa Família",
                     "total": "Todos"}
# A tela mostra uma pesquisa só: o Datafolha de 29/09 a 01/10/2026 (BR-08039/2026), a última rodada do instituto com as
# três lentes (a de 02 e 03/10 não publicou Bolsa Família). As outras rodadas ficam no levantamento bruto.
PESQUISA_NA_TELA = ("Datafolha", "2026-10-01")
ROTULO_FAIXA = {"até 2 SM": "até 2 salários mínimos", "mais de 2 a 5 SM": "de 2 a 5 salários",
                "mais de 5 SM": "mais de 5 salários", "beneficiário": "recebe (ou mora com quem recebe)",
                "não beneficiário": "não recebe", "fundamental": "até o fundamental", "médio": "ensino médio",
                "superior": "ensino superior", "total": "todos os eleitores"}


def perfil_pesquisa():
    """Intenção de voto de Lula e Flávio por faixa (renda, escolaridade, Bolsa Família) da pesquisa da tela, do
    levantamento dados/bruto/pesquisas/perfil_lula_flavio.csv: a lente, a ordem da faixa (a do instituto) e o campo com
    o registro no TSE, tirados da observação. O total da pesquisa entra como lente "Todos" (a linha de referência)."""
    d = pd.read_csv(BRUTO / "pesquisas" / "perfil_lula_flavio.csv", sep=";", dtype=str)
    d = d[(d.instituto == PESQUISA_NA_TELA[0]) & (d.divulgacao == PESQUISA_NA_TELA[1])
          & d.dimensao.isin(LENTE_DA_DIMENSAO)].copy()
    d["lente"] = d.dimensao.map(LENTE_DA_DIMENSAO)
    d["percentual"] = d.percentual.astype(float)
    d["categoria_ordem"] = d.groupby("dimensao").categoria.transform(
        lambda c: c.map({v: i + 1 for i, v in enumerate(dict.fromkeys(c))}))
    d["categoria"] = d.categoria.map(lambda c: ROTULO_FAIXA.get(c, c))

    def campo(obs):
        m = re.search(r"campo (\d{4})-(\d{2})-(\d{2}) a (\d{4})-(\d{2})-(\d{2})", str(obs))
        r = re.search(r"BR-\d+/\d{4}", str(obs))
        datas = f"campo {m[3]}/{m[2]} a {m[6]}/{m[5]}/{m[4]}" if m else ""
        return " · ".join(x for x in (datas, r[0] if r else "") if x)

    d["campo"] = d.observacao.map(campo)

    def fatia(linha):
        """Fatia do grupo na amostra: a base ponderada do segmento sobre o n total (vazia se o instituto não publicou);
        a linha do total vale 1."""
        if linha.dimensao == "total":
            return 1.0
        seg = re.search(r"base ponderada (\d+) entrevistas", str(linha.observacao))
        n = re.search(r"n=(\d+)", str(linha.observacao))
        return round(int(seg[1]) / int(n[1]), 4) if seg and n else None

    d["fatia"] = d.apply(fatia, axis=1)
    return d[["instituto", "divulgacao", "campo", "candidato", "lente", "categoria", "categoria_ordem", "percentual",
              "fatia", "fonte_url"]]


def abstencao_faixa():
    """Município × faixa de idade × ano (1º turno, 2014–2026) da tela 07 · Quem falta (código T25), de
    dados/saida/abstencao_municipio_faixa.csv (pipeline/extrair_abstencao_municipio.py, perfil do eleitor do TSE): aptos
    e abstenções nas sete faixas da tela (a idade não informada fica de fora). O exterior vem numa linha por faixa e
    ano, com uf = ZZ e cd_ibge vazio; o modelo (pbi/modelo/t25_ausencia.py) separa os municípios ('T25 Abstenção
    faixa') do exterior ('T25 Abstenção exterior')."""
    d = pd.read_csv(SAIDA_DADOS / "abstencao_municipio_faixa.csv", dtype={"cd_ibge": str})
    d = d[d.faixa_ordem.between(1, 7)]
    d = d.groupby(["ano", "uf", "cd_ibge", "faixa_ordem"], as_index=False, dropna=False)[["aptos", "abstencao"]].sum()
    d = d.rename(columns={"abstencao": "abstencoes"})
    for c in ("aptos", "abstencoes"):
        d[c] = d[c].astype("int64")
    return d.sort_values(["ano", "uf", "cd_ibge", "faixa_ordem"], na_position="last")[
        ["ano", "uf", "cd_ibge", "faixa_ordem", "aptos", "abstencoes"]]


def main():
    m = municipios()
    gravar(m, "municipio")
    gravar(municipio_ano(), "municipio_ano")
    gravar(candidatos(), "candidato_ano")
    gravar(candidatos_uf(), "candidato_uf")
    gravar(pd.read_csv(SAIDA_DADOS / "comparecimento_nacional.csv"), "comparecimento_ano")
    gravar(pd.read_csv(SAIDA_DADOS / "abstencao_perfil.csv"), "abstencao_perfil")
    gravar(pesquisas(), "pesquisa")
    gravar(copiar(BRUTO / "debate" / "debates.csv"), "debate")
    gravar(copiar(BRUTO / "digital" / "trends_tempo.csv"), "trends_tempo")
    gravar(copiar(BRUTO / "digital" / "trends_uf.csv"), "trends_uf")
    # consulta U2 (23/10/2026): Lula × Flávio dia a dia, uma consulta por UF e a nacional (uf = BR); a curva da tela de
    # buscas segue o estado clicado. O modelo deixa a BR de fora (a curva do Brasil segue a T2 de trends_tempo)
    gravar(copiar(BRUTO / "digital" / "trends_uf_tempo.csv"), "trends_uf_tempo")
    gravar(copiar(BRUTO / "digital" / "seguidores.csv"), "seguidores")
    gravar(copiar(BRUTO / "digital" / "monitoramento.csv"), "monitoramento")
    gravar(copiar(BRUTO / "digital" / "anuncios.csv"), "anuncios")
    gravar(trajetoria(), "trajetoria")
    gravar(exterior(), "exterior_pais")
    gravar(social(), "municipio_social")
    gravar(perfil_pesquisa(), "perfil_pesquisa")
    for nome in ("transferencia", "rejeicao", "apoios"):
        gravar(copiar(BRUTO / "transferencia" / f"{nome}.csv"), nome if nome != "apoios" else "apoio")
    locais = pd.read_csv(SAIDA_DADOS / "locais_contagem.csv")
    pos = pd.read_csv(SAIDA_DADOS / "escolas_posicao.csv")
    # um local pode ter dois nomes no mesmo ano (zona 91, local 1350 em 2026): a posição é do local, uma linha por chave
    pos = pos.drop_duplicates(["NR_ZONA", "NR_LOCAL_VOTACAO"])
    gravar(locais.merge(pos[["NR_ZONA", "NR_LOCAL_VOTACAO", "px", "py"]], on=["NR_ZONA", "NR_LOCAL_VOTACAO"], how="left"),
           "local_contagem")
    gravar(abstencao_faixa(), "abstencao_faixa_municipio")


if __name__ == "__main__":
    main()
