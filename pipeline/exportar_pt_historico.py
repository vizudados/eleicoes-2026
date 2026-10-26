"""Série auditável do PT e do principal adversário nas presidenciais de 1989–2026.

Uso: python -I -X utf8 pipeline/exportar_pt_historico.py [--somente-cache] [--diagnostico]
Fontes públicas do TSE. Não altera os dados anteriores do painel.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "dados/bruto/tse/historico_pt"
SAIDA = RAIZ / "dados/saida/pt_historico"
COLUNAS = ["ano", "turno", "uf", "candidato_pt", "votos_pt", "adversario", "partido_adversario", "votos_adv", "validos", "comparecimento", "aptos"]
SOMAS = ["votos_pt", "votos_adv", "validos", "comparecimento", "aptos"]
ANOS = [1989, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]
SLUGS = dict(zip("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split(),
    "acre|alagoas|amazonas|amapa|bahia|ceara|distrito-federal|espirito-santo|goias|maranhao|minas-gerais|mato-grosso-do-sul|mato-grosso|para|paraiba|pernambuco|piaui|parana|rio-de-janeiro|rio-grande-do-norte|rondonia|roraima|rio-grande-do-sul|santa-catarina|sergipe|sao-paulo|tocantins".split("|")))
REGIOES = {uf: reg for reg, ufs in [("Norte", "AC AM AP PA RO RR TO"), ("Nordeste", "AL BA CE MA PB PE PI RN SE"),
    ("Centro-Oeste", "DF GO MS MT"), ("Sudeste", "ES MG RJ SP"), ("Sul", "PR RS SC")] for uf in ufs.split()}
FONTES = []
BASE94 = "https://www.tse.jus.br/eleicoes/eleicoes-anteriores/eleicoes-1994/resultados-das-eleicoes-1994"
URL_DIRETAS = "https://www.tse.jus.br/servicos-eleitorais/glossario/termos/eleicao-direta"
NOMES_PT = {a: "Dilma Rousseff" if a in {2010, 2014} else "Fernando Haddad" if a == 2018 else "Lula" for a in ANOS}
NOMES_ADV = {1989: "Fernando Collor", 1994: "Fernando Henrique Cardoso", 1998: "Fernando Henrique Cardoso", 2002: "José Serra",
    2006: "Geraldo Alckmin", 2010: "José Serra", 2014: "Aécio Neves", 2018: "Jair Bolsonaro", 2022: "Jair Bolsonaro", 2026: "Flávio Bolsonaro"}


def normalizar_nome(nome):
    return " ".join(unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().upper().split())


class TabelasHTML(HTMLParser):
    """Lê texto de células e links, sem executar scripts da página."""
    def __init__(self):
        super().__init__()
        self.linhas, self.links = [], []
        self.linha, self.celula, self.link = None, None, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.linha = []
        if tag in {"td", "th"}:
            self.celula = []
        if tag == "a":
            self.link = [attrs.get("href", ""), []]

    def handle_data(self, data):
        if self.celula is not None:
            self.celula.append(data)
        if self.link is not None:
            self.link[1].append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.celula is not None:
            if self.linha is not None:
                self.linha.append(" ".join("".join(self.celula).split()))
            self.celula = None
        if tag == "tr" and self.linha is not None:
            self.linhas.append(self.linha)
            self.linha = None
        if tag == "a" and self.link is not None:
            self.links.append((self.link[0], " ".join("".join(self.link[1]).split())))
            self.link = None


def gravar(df, nome):
    caminho = SAIDA / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False, encoding="utf-8", lineterminator="\n", float_format="%.12g")


def baixar(url, nome, somente_cache):
    if urllib.parse.urlparse(url).hostname not in {"www.tse.jus.br", "dadosabertos.tse.jus.br", "cdn.tse.jus.br", "apps.tre-sc.jus.br", "www.tre-rj.jus.br", "www.tre-mg.jus.br", "www.tre-pr.jus.br"}:
        raise ValueError("Fonte fora dos domínios oficiais autorizados no coletor")
    destino = CACHE / nome
    if not destino.exists():
        if somente_cache:
            raise FileNotFoundError(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        for tentativa in range(4):
            try:
                pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(pedido, timeout=45) as r:
                    corpo = r.read(10_000_001)
                if len(corpo) > 10_000_000:
                    raise ValueError("Página excedeu 10 MB")
                destino.write_bytes(corpo)
                time.sleep(.08)
                break
            except urllib.error.HTTPError as erro:
                if erro.code not in {408, 429, 500, 502, 503, 504} or tentativa == 3:
                    print(f"Falha HTTP {erro.code}: {url}", file=sys.stderr)
                    raise
                time.sleep(2 ** (tentativa + 1))
            except (urllib.error.URLError, TimeoutError):
                if tentativa == 3:
                    raise
                time.sleep(2 ** (tentativa + 1))
    FONTES.append({"url": url, "arquivo": destino.relative_to(RAIZ).as_posix(), "sha256": hashlib.sha256(destino.read_bytes()).hexdigest()})
    return destino.read_bytes()


def pagina(url, nome, somente_cache):
    b = baixar(url, nome, somente_cache)
    p = TabelasHTML()
    try:
        texto = b.decode("utf-8")
    except UnicodeDecodeError:
        texto = b.decode("latin1")
    p.feed(texto)
    return p


def inteiro(texto):
    if not re.fullmatch(r"[\d.]+", texto.strip()):
        raise ValueError(f"Contagem inesperada: {texto!r}")
    return int(texto.replace(".", ""))


def ler_tabela94(p, uf):
    candidatos, detalhe = [], {}
    for linha in p.linhas:
        if len(linha) >= 3 and re.match(r"^\d+\s+", linha[0]):
            numero, nome = linha[0].split(" ", 1)
            candidatos.append({"ano": 1994, "turno": 1, "uf": uf, "numero": int(numero), "nome": nome,
                               "partido": linha[1], "votos": inteiro(linha[2])})
        if len(linha) >= 2:
            for rotulo, campo in [("Total de votos apurados", "comparecimento"), ("Total de votos válidos", "validos"),
                                   ("Total de votos brancos", "brancos"), ("Total de votos nulos", "nulos")]:
                if linha[0].startswith(rotulo):
                    detalhe[campo] = inteiro(linha[1])
                    if campo == "comparecimento" and len(linha) >= 3:
                        m = re.search(r"de\s+([\d.]+)\s+eleitores", linha[2])
                        if m:
                            detalhe["aptos"] = inteiro(m[1])
    if not candidatos or not {"validos", "comparecimento", "aptos"}.issubset(detalhe):
        raise ValueError(f"Tabela de 1994 incompleta em {uf}: {detalhe}")
    return candidatos, {"ano": 1994, "turno": 1, "uf": uf, **detalhe}


def coletar_1994(somente_cache):
    indice_ufs = pagina(BASE94, "1994/indice.html", somente_cache)
    pais = {}
    for url, titulo in indice_ufs.links:
        slug = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode().lower().replace(" ", "-")
        if url.startswith(BASE94) and slug in SLUGS.values():
            pais.setdefault(slug, url)  # A primeira lista é o 1º turno; a segunda é de governador.
    def uf_tarefa(item):
        uf, slug = item
        pai = pagina(pais[slug], f"1994/{uf}_indice.html", somente_cache)
        links = [(u, titulo) for u, titulo in pai.links if "presidente" in u and u.startswith(BASE94)]
        if len(links) != 1:
            raise ValueError(f"Esperava um link de presidente em {uf}: {links}")
        p = pagina(links[0][0], f"1994/{uf}_presidente.html", somente_cache)
        return ler_tabela94(p, uf)
    with ThreadPoolExecutor(max_workers=4) as ex:
        resultados = list(ex.map(uf_tarefa, sorted(SLUGS.items())))
    exterior = pagina(BASE94 + "/brasil/resultados-das-eleicoes-1994-brasil", "1994/ZZ_presidente.html", somente_cache)
    resultados.append(ler_tabela94(exterior, "ZZ"))
    candidatos = pd.DataFrame([r for c, _ in resultados for r in c])
    detalhe = pd.DataFrame([d for _, d in resultados])
    indice = pagina(BASE94 + "/brasil", "1994/BR_indice.html", somente_cache)
    regionais = []
    for url, titulo in indice.links:
        if titulo.startswith("Região "):
            p = pagina(url, "1994/regiao_" + titulo.split(" ", 1)[1].replace(" ", "_") + ".html", somente_cache)
            c, d = ler_tabela94(p, titulo)
            regionais.append((c, d))
    return candidatos, detalhe, regionais


def ler_1989():
    votos, detalhe = [], []
    for tipo in ["VOTACAO_CANDIDATO", "DETALHE_VOTACAO"]:
        caminho = CACHE / "1989" / f"{tipo}_UF_1989.txt"
        with caminho.open(encoding="latin1", newline="") as f:
            for r in csv.reader(f, delimiter=";"):
                if not r:
                    continue
                if tipo == "VOTACAO_CANDIDATO":
                    assert len(r) == 26 and r[7] == "1"
                    votos.append({"ano": 1989, "turno": int(r[3]), "uf": r[5], "numero": int(r[8]),
                                  "nome": r[10], "partido": r[20], "votos": int(r[25])})
                else:
                    assert len(r) == 22 and r[7] == "1"
                    detalhe.append({"ano": 1989, "turno": int(r[3]), "uf": r[5], "aptos": int(r[9]),
                                    "comparecimento": int(r[10]), "validos": int(r[12]), "brancos": int(r[13]), "nulos": int(r[14])})
    return pd.DataFrame(votos), pd.DataFrame(detalhe)


def ler_moderno(ano, capitais=None):
    base = RAIZ / "dados/bruto/tse"
    v = pd.read_csv(base / f"presidente_{ano}_BR.csv", sep=";", encoding="latin1")
    v = v[v.CD_CARGO.eq(1)].copy()
    d = pd.read_csv(base / f"detalhe_{ano}_BR.csv", sep=";", encoding="latin1")
    d = d[d.CD_CARGO.eq(1)].copy()
    if ano == 2010:
        # O TSE informa a capital nos registros VT. Atribui à UF de votação,
        # conservando cada voto e eleitor, sem misturar trânsito com exterior.
        for tabela in [v, d]:
            vt = tabela.SG_UF.eq("VT")
            destinos = tabela.loc[vt, "NM_MUNICIPIO"].map(normalizar_nome).map(capitais)
            if destinos.isna().any():
                raise ValueError("Capital de voto em trânsito sem UF")
            tabela.loc[vt, "SG_UF"] = destinos
        mapa_vt = pd.read_csv(base / "detalhe_2010_BR.csv", sep=";", encoding="latin1")
        mapa_vt = mapa_vt[mapa_vt.SG_UF.eq("VT") & mapa_vt.CD_CARGO.eq(1)].copy()
        mapa_vt["uf_destino"] = mapa_vt.NM_MUNICIPIO.map(normalizar_nome).map(capitais)
        gravar(mapa_vt[["NR_TURNO", "CD_MUNICIPIO", "NM_MUNICIPIO", "uf_destino", "QT_APTOS", "QT_COMPARECIMENTO", "QT_TOTAL_VOTOS_VALIDOS"]], "voto_transito_2010.csv")
    campo = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in v else "QT_VOTOS_NOMINAIS"
    v = v.groupby(["NR_TURNO", "SG_UF", "NR_CANDIDATO", "NM_CANDIDATO", "SG_PARTIDO"], as_index=False)[campo].sum()
    v = v.rename(columns={"NR_TURNO": "turno", "SG_UF": "uf", "NR_CANDIDATO": "numero", "NM_CANDIDATO": "nome", "SG_PARTIDO": "partido", campo: "votos"})
    v["ano"] = ano
    campos = {"QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "QT_TOTAL_VOTOS_VALIDOS": "validos", "QT_VOTOS_BRANCOS": "brancos", "QT_TOTAL_VOTOS_NULOS": "nulos"}
    d = d.groupby(["NR_TURNO", "SG_UF"], as_index=False)[list(campos)].sum()
    d = d.rename(columns={"NR_TURNO": "turno", "SG_UF": "uf", **campos})
    d["ano"] = ano
    return v, d


def fonte_ano(ano):
    if ano == 1989:
        return "https://dadosabertos.tse.jus.br/dataset/resultados-1989"
    if ano == 1994:
        return BASE94
    return f"https://dadosabertos.tse.jus.br/dataset/resultados-{ano}"


def prova(provas, ano, turno, tipo, unidade, campo, obtido, esperado, fonte):
    provas.append({"ano": ano, "turno": turno, "tipo": tipo, "unidade": unidade, "campo": campo,
                   "obtido": int(obtido), "esperado": int(esperado), "diferenca": int(obtido) - int(esperado),
                   "bate": int(obtido) == int(esperado), "fonte": fonte})


def limites_antes_1989(somente_cache):
    p = pagina(URL_DIRETAS, "controle/eleicoes_diretas.html", somente_cache)
    linhas = []
    for r in p.linhas:
        if len(r) >= 5 and re.fullmatch(r"\d{2}", r[0]):
            ano = int(r[2].split(".")[-1])
            if ano >= 1989:
                continue
            votos = inteiro(r[3].replace("(*)", "").strip())
            linhas.append({"ano": ano, "mais_votado": r[1], "votos": votos, "fonte": URL_DIRETAS,
                            "metodo": "Limite superior: em cada eleição direta de turno único anterior a 1989 nenhum adversário recebeu mais que o mais votado; não é uma lista nominal de todos os derrotados"})
    if {r["ano"] for r in linhas} != {1894, 1898, 1902, 1906, 1910, 1914, 1918, 1919, 1922, 1926, 1930, 1945, 1950, 1955, 1960}:
        raise ValueError("Cobertura histórica anterior a 1989 incompleta")
    return pd.DataFrame(linhas)


def controles_publicados(nacional, todos, somente_cache):
    """Comparações com publicações de versões diferentes, sem alterar a série."""
    referencias = []
    def ref(ano, turno, campo, valor, url, nota):
        obtido = nacional.set_index(["ano", "turno"]).loc[(ano, turno), campo]
        referencias.append({"ano": ano, "turno": turno, "campo": campo, "valor_serie_mesma_cobertura": int(obtido),
                             "valor_publicacao": valor, "diferenca": int(obtido) - valor, "bate": int(obtido) == valor,
                             "fonte": url, "nota": nota})
    tre_rj = "https://www.tre-rj.jus.br/institucional/memoria/eleicoes-1989"
    pagina(tre_rj, "controle/tre_rj_1989.html", somente_cache)
    ref(1989, 2, "votos_pt", 31075803, tre_rj, "Publicação do TRE-RJ coincide com a versão do repositório de dados abertos")
    ref(1989, 2, "votos_adv", 35090206, tre_rj, "Publicação do TRE-RJ coincide com a versão do repositório de dados abertos")
    pr = "https://www.tre-pr.jus.br/comunicacao/noticias/2021/Julho/memorias-eleitorais-eleicoes-1989-a-primeira-com-mapas-de-totalizacao-informatizados"
    pagina(pr, "controle/tre_pr_1989.html", somente_cache)
    ref(1989, 2, "votos_pt", 31076364, pr, "Retrospectiva do TRE-PR diverge do repositório aberto e da exposição do TRE-RJ. Não misturar versões")
    for ano, turno, valor in [(1989, 2, 35089998), (1994, 1, 34377829), (1998, 1, 35936916)]:
        ref(ano, turno, "votos_adv", valor, URL_DIRETAS, "Glossário informa resultado na data da aprovação do relatório final; diverge da versão adotada. Não ajustar nem misturar versões")
    sc = "https://apps.tre-sc.jus.br/site/fileadmin/arquivos/eleicoes/histeleiweb/1998/ResultFinalE1998presidencial.htm"
    pagina(sc, "controle/tre_sc_1998.html", somente_cache)
    for c, v in [("votos_pt", 21475218), ("votos_adv", 35936540), ("validos", 67722475)]:
        ref(1998, 1, c, v, sc, "Resultado histórico publicado pelo TRE-SC em 07/08/2001; arquivo aberto posterior é diferente; causa não comprovada")
    mg = "https://www.tre-mg.jus.br/eleicoes/eleicoes-2018/informacoes-para-imprensa-2o-turno/resultados-eleicoes-anteriores-2013-presidente"
    pagina(mg, "controle/tre_mg_2002_2014.html", somente_cache)
    for ano, turno, pt, adv in [(2002, 1, 39444010, 19700549), (2002, 2, 52793364, 33370739),
                               (2006, 1, 46662365, 39968369), (2006, 2, 58295042, 37543178),
                               (2010, 1, 47651434, 33132283), (2010, 2, 55752483, 43711162),
                               (2014, 1, 43267668, 34897211)]:
        nota = "Tabela histórica do TRE-MG; 2002/1 e 2010/2 diferem do arquivo aberto. Causa e abrangência exata da diferença não estabelecidas"
        ref(ano, turno, "votos_pt", pt, mg, nota)
        ref(ano, turno, "votos_adv", adv, mg, nota)
    publicacoes = [(2014, 2, "https://www.tse.jus.br/comunicacao/noticias/2014/Dezembro/plenario-do-tse-proclama-resultado-definitivo-do-segundo-turno-da-eleicao-presidencial", [54501118,51041155,105542273,112683879,142822046]),
        (2018, 1, "https://www.tse.jus.br/comunicacao/noticias/2018/Outubro/concluida-totalizacao-de-votos-do-1o-turno-das-eleicoes-2018", [31342005,49276990,107050673,117364560,147306275]),
        (2022, 1, "https://www.tse.jus.br/comunicacao/noticias/2022/Outubro/100-das-secoes-totalizadas-confira-como-ficou-o-quadro-eleitoral-apos-o-1o-turno", [57259504,51072345,118229719,123682372,156454011]),
        (2022, 2, "https://www.tse.jus.br/comunicacao/noticias/2022/Outubro/100-das-secoes-totalizadas-confira-como-ficou-o-quadro-eleitoral-apos-o-2o-turno", [60345999,58206354,118552353,124252796,156454011])]
    for ano, turno, url, valores in publicacoes:
        pagina(url, f"controle/noticia_{ano}_{turno}.html", somente_cache)
        for campo, valor in zip(SOMAS, valores):
            ref(ano, turno, campo, valor, url, "Contagens publicadas na notícia; não comparar percentuais arredondados. A notícia de 2018/1 diverge da versão aberta posterior")
    return pd.DataFrame(referencias)


def montar_analises(uf, br, candidatos, limites):
    n = br.copy()
    for lado in ["pt", "adv"]:
        n[f"{lado}_pct_validos"] = 100 * n[f"votos_{lado}"] / n.validos
        n[f"{lado}_pct_aptos"] = 100 * n[f"votos_{lado}"] / n.aptos
    n["fonte"] = n.ano.map(fonte_ano)
    gravar(n, "nacional_percentuais.csv")
    crescimento = n.sort_values(["turno", "ano"]).copy()
    crescimento["ano_anterior"] = crescimento.groupby("turno").ano.shift()
    crescimento["intervalo_anos"] = crescimento.ano - crescimento.ano_anterior
    for coluna in SOMAS + ["pt_pct_validos", "adv_pct_validos", "pt_pct_aptos", "adv_pct_aptos"]:
        crescimento["delta_" + coluna] = crescimento.groupby("turno")[coluna].diff()
    for lado in ["pt", "adv"]:
        anterior = crescimento.groupby("turno")[f"votos_{lado}"].shift()
        crescimento[f"crescimento_{lado}_pct"] = 100 * crescimento[f"delta_votos_{lado}"] / anterior
    gravar(crescimento, "crescimento_mesmo_turno.csv")
    maior_turno = br.groupby("ano").turno.max()
    decisivo = uf[uf.turno.eq(uf.ano.map(maior_turno))].copy()
    # Vencedor verdadeiro entre todas as candidaturas, inclusive Ciro no CE/1998.
    vencedor = (candidatos.sort_values(["ano", "turno", "uf", "votos", "numero"], ascending=[True, True, True, False, True])
                .drop_duplicates(["ano", "turno", "uf"])[["ano", "turno", "uf", "numero", "nome", "partido", "votos"]]
                .rename(columns={"nome": "vencedor", "partido": "partido_vencedor", "votos": "votos_vencedor", "numero": "numero_vencedor"}))
    geo = uf.merge(vencedor, on=["ano", "turno", "uf"], validate="one_to_one")
    geo["regiao"] = geo.uf.map(REGIOES).fillna("Exterior")
    geo["pt_venceu"] = geo.partido_vencedor.eq("PT")
    geo["adversario_venceu"] = geo.partido_vencedor.eq(geo.partido_adversario)
    geo["tipo_unidade"] = geo.uf.eq("ZZ").map({True: "Exterior", False: "UF"})
    geo["turno_decisivo"] = geo.turno.eq(geo.ano.map(maior_turno))
    gravar(geo, "geografia_todos_turnos.csv")
    fim = geo[geo.turno_decisivo].copy()
    gravar(fim, "mapa_turno_decisivo.csv")
    vitorias = (fim.groupby(["ano", "turno", "tipo_unidade", "regiao", "partido_vencedor"], as_index=False)
                .agg(quantidade_ufs=("uf", "size")))
    gravar(vitorias, "vitorias_por_regiao.csv")
    nacional_ufs = fim[fim.uf.ne("ZZ")].groupby(["ano", "turno"], as_index=False).agg(ufs_pt=("pt_venceu", "sum"), ufs_adversario=("adversario_venceu", "sum"), ufs=("uf", "size"))
    nacional_ufs["ufs_nao_pt"] = nacional_ufs.ufs - nacional_ufs.ufs_pt
    nacional_ufs["ufs_outros"] = nacional_ufs.ufs - nacional_ufs.ufs_pt - nacional_ufs.ufs_adversario
    gravar(nacional_ufs, "vitorias_ufs_por_eleicao.csv")
    frames = geo[geo.uf.ne("ZZ")].groupby(["ano", "turno"], as_index=False).agg(ufs_pt=("pt_venceu", "sum"), ufs_adversario=("adversario_venceu", "sum"))
    frames["ufs_outros"] = 27 - frames.ufs_pt - frames.ufs_adversario
    frames["ordem"] = range(1, len(frames) + 1)
    frames["turno_decisivo"] = frames.turno.eq(frames.ano.map(maior_turno))
    frames["fonte"] = frames.ano.map(fonte_ano)
    gravar(frames, "frames_mapa.csv")
    regioes = geo.groupby(["ano", "turno", "regiao"], as_index=False)[SOMAS].sum()
    for lado in ["pt", "adv"]:
        regioes[f"{lado}_pct_validos"] = 100 * regioes[f"votos_{lado}"] / regioes.validos
        regioes[f"{lado}_pct_aptos"] = 100 * regioes[f"votos_{lado}"] / regioes.aptos
    gravar(regioes, "votos_por_regiao.csv")
    trocas = fim[fim.uf.ne("ZZ")].sort_values(["uf", "ano"]).copy()
    trocas["ano_anterior"] = trocas.groupby("uf").ano.shift()
    trocas["partido_anterior"] = trocas.groupby("uf").partido_vencedor.shift()
    trocas["pt_venceu_anterior"] = trocas.groupby("uf").pt_venceu.shift()
    trocas["mudou_pt_nao_pt"] = trocas.ano_anterior.notna() & trocas.pt_venceu.ne(trocas.pt_venceu_anterior)
    gravar(trocas, "mudancas_de_lado.csv")
    ranking = trocas.groupby("uf", as_index=False).agg(mudancas_pt_nao_pt=("mudou_pt_nao_pt", "sum"), eleicoes_pt=("pt_venceu", "sum"), eleicoes=("ano", "size"))
    ranking["posicao"] = ranking.mudancas_pt_nao_pt.rank(ascending=False, method="min").astype(int)
    gravar(ranking.sort_values(["mudancas_pt_nao_pt", "uf"], ascending=[False, True]), "ranking_mudancas_uf.csv")
    nacional_candidatos = candidatos.groupby(["ano", "turno", "numero", "nome", "partido"], as_index=False).votos.sum()
    nacional_candidatos["posicao_historica"] = nacional_candidatos.votos.rank(ascending=False, method="min").astype(int)
    gravar(nacional_candidatos.sort_values(["votos", "ano", "numero"], ascending=[False, False, True]), "todos_candidatos_brasil.csv")
    gravar(limites, "limites_candidatos_antes_1989.csv")
    recorde = nacional_candidatos.sort_values("votos", ascending=False).iloc[0]
    anterior = nacional_candidatos[nacional_candidatos.ano.lt(2026)].sort_values("votos", ascending=False).iloc[0]
    assert int(recorde.votos) > int(limites.votos.max())
    resumo = {"votacao_recorde": int(recorde.votos), "candidato_recorde": str(recorde["nome"]), "ano": int(recorde.ano), "turno": int(recorde.turno),
              "recorde_anterior": int(anterior.votos), "ano_anterior": int(anterior.ano), "candidato_anterior": str(anterior["nome"]),
              "supera_em_votos": int(recorde.votos - anterior.votos), "candidaturas_turnos_comparadas_desde_1989": len(nacional_candidatos),
              "eleicoes_anteriores_com_limite_superior_oficial": len(limites), "maior_votacao_antes_1989": int(limites.votos.max()),
              "limite_do_metodo": "Compara todas as candidaturas/turnos desde 1989; antes disso usa o mais votado de cada eleição direta como limite superior de todos os concorrentes, sem afirmar ter transcrito todos os derrotados"}
    (SAIDA / "recorde.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return n, crescimento, nacional_ufs, ranking, regioes, resumo


def controle_bruto_direto(ano, turno, numero_adv):
    """Segunda soma antes de qualquer junção geográfica ou redistribuição de VT."""
    total = Counter()
    if ano == 1989:
        with (CACHE / "1989/VOTACAO_CANDIDATO_UF_1989.txt").open(encoding="latin1", newline="") as f:
            for r in csv.reader(f, delimiter=";"):
                if r and int(r[3]) == turno:
                    total["validos"] += int(r[25])
                    if r[20] == "PT":
                        total["votos_pt"] += int(r[25])
                    if int(r[8]) == numero_adv:
                        total["votos_adv"] += int(r[25])
        with (CACHE / "1989/DETALHE_VOTACAO_UF_1989.txt").open(encoding="latin1", newline="") as f:
            for r in csv.reader(f, delimiter=";"):
                if r and int(r[3]) == turno:
                    total["aptos"] += int(r[9])
                    total["comparecimento"] += int(r[10])
        return total
    with (RAIZ / f"dados/bruto/tse/presidente_{ano}_BR.csv").open(encoding="latin1", newline="") as f:
        leitor = csv.DictReader(f, delimiter=";")
        coluna = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in leitor.fieldnames else "QT_VOTOS_NOMINAIS"
        for r in leitor:
            if int(r["NR_TURNO"]) != turno or int(r["CD_CARGO"]) != 1:
                continue
            if r["SG_PARTIDO"] == "PT":
                total["votos_pt"] += int(r[coluna])
            if int(r["NR_CANDIDATO"]) == numero_adv:
                total["votos_adv"] += int(r[coluna])
    with (RAIZ / f"dados/bruto/tse/detalhe_{ano}_BR.csv").open(encoding="latin1", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if int(r["NR_TURNO"]) == turno and int(r["CD_CARGO"]) == 1:
                for campo, origem in [("aptos", "QT_APTOS"), ("comparecimento", "QT_COMPARECIMENTO"), ("validos", "QT_TOTAL_VOTOS_VALIDOS")]:
                    total[campo] += int(r[origem])
    return total


def registrar_brutos(ano):
    for prefixo, pasta in [("presidente", "votacao_candidato_munzona"), ("detalhe", "detalhe_votacao_munzona")]:
        arquivo = RAIZ / f"dados/bruto/tse/{prefixo}_{ano}_BR.csv"
        FONTES.append({"url": f"https://cdn.tse.jus.br/estatistica/sead/odsele/{pasta}/{pasta}_{ano}.zip",
                       "arquivo": arquivo.relative_to(RAIZ).as_posix(), "sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest()})


def api_brasil_2026(turno, somente_cache):
    eleicao = {1: 6257, 2: 6258}[turno]
    url = f"https://resultados.tse.jus.br/oficial/ele2026/{eleicao}/dados/br/br-c0001-e{eleicao:06d}-u.json"
    arquivo = CACHE / f"2026/BR_{turno}t.json"
    if not arquivo.exists():
        if somente_cache:
            raise FileNotFoundError(arquivo)
        with urllib.request.urlopen(url, timeout=45) as r:
            b = r.read()
        json.loads(b)
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_bytes(b)
    b = json.loads(arquivo.read_text(encoding="utf-8"))
    assert int(b["ele"]) == eleicao and int(b["t"]) == turno and b["tf"] == "s"
    candidatos = {int(c["n"]): int(c["vap"]) for cargo in b["carg"] if cargo["cd"] == "1" for agr in cargo["agr"] for par in agr["par"] for c in par["cand"]}
    FONTES.append({"url": url, "arquivo": arquivo.relative_to(RAIZ).as_posix(), "sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest()})
    return {"votos_pt": candidatos[13], "votos_adv": candidatos[22], "validos": int(b["v"]["vv"]),
            "comparecimento": int(b["e"]["c"]), "aptos": int(b["e"]["te"])}, url


def numero_br(valor, casas=0, sinal=False):
    if pd.isna(valor):
        return "—"
    s = (f"{valor:+,.{casas}f}" if sinal else f"{valor:,.{casas}f}")
    return s.replace(",", "@ mil @").replace(".", ",").replace("@ mil @", ".")


def documentar(resultados, resumo):
    n, crescimento, vitorias, ranking, regioes, recorde = resultados
    linhas = ["## História do PT nas urnas", "",
        "Rodada 2 · 26/10/2026. Leia `PT-HISTORICO-METODO.md`. Foram preservadas as correções de `CONFERIDO-MAIN.md`: mercado fora do vídeo e regressão sem número de fala. Esta seção não acrescenta explicação causal para a eleição.", "",
        f"**H1. A série cobre as dez eleições de 1989 a 2026, com {resumo['turnos']} pares de ano/turno e {resumo['linhas_uf']} linhas de UF.** Há primeiro turno em todas e segundo turno em oito. 1994 e 1998 terminaram no primeiro. Cada ano/turno contém 27 UFs e ZZ; o Brasil inclui o exterior uma vez. Origem: `dados/pbi/pt_historico_uf.csv` e `pt_historico_brasil.csv`; provas em `dados/saida/pt_historico/provas.csv`. **Evidência: alta para a transcrição das fontes escolhidas; com divergências de versões históricas registradas separadamente.**", "",
        "**H2. A votação não cresceu em toda eleição.** A tabela mostra os dois candidatos e os dois denominadores, sem confundir recorde em votos com recorde percentual. Válidos incluem todos os candidatos do turno. Origem: `nacional_percentuais.csv:votos_pt,votos_adv,pt_pct_validos,adv_pct_validos,pt_pct_aptos,adv_pct_aptos`; fonte primária vinculada no ano. **Evidência: alta para as contas da versão identificada.**", "",
        "| Ano / turno | Candidato PT | Votos PT | % válidos / % aptos PT | Principal adversário (partido) | Votos adversário | % válidos / % aptos adversário |",
        "|---|---|---:|---:|---|---:|---:|"]
    for r in n.itertuples():
        linhas.append(f"| [{r.ano}](<{fonte_ano(r.ano)}>) / {r.turno}º | {r.candidato_pt} | {numero_br(r.votos_pt)} | {numero_br(r.pt_pct_validos,2)}% / {numero_br(r.pt_pct_aptos,2)}% | {r.adversario} ({r.partido_adversario}) | {numero_br(r.votos_adv)} | {numero_br(r.adv_pct_validos,2)}% / {numero_br(r.adv_pct_aptos,2)}% |")
    linhas += ["", "As versões adotadas dão 31.075.803 votos a Lula em 1989/2 e 21.475.211 em 1998/1. Há outras publicações oficiais com números diferentes. Isso está exposto no método e no CSV de comparação; não apresentar coincidência universal com todas as retrospectivas do TSE.", "",
        "**H3. O gráfico de evolução deve comparar o mesmo turno.** Esta é a variação de primeiro para primeiro turno. Entre 1989 e 1994 são cinco anos; depois, quatro. Os adversários e, em alguns anos, o candidato do PT mudam: a coluna representa a candidatura daquele ano, sem transferência individual de votos. Origem: `crescimento_mesmo_turno.csv:ano_anterior,intervalo_anos,delta_votos_pt,delta_votos_adv,delta_pt_pct_validos,delta_adv_pct_validos`. **Evidência: alta, diferença entre contagens auditadas.**", "",
        "| Intervalo, 1º turno | Variação PT, votos | Variação adversário, votos | PT, pontos dos válidos | Adversário, pontos dos válidos |",
        "|---|---:|---:|---:|---:|"]
    for r in crescimento[crescimento.turno.eq(1) & crescimento.ano_anterior.notna()].itertuples():
        linhas.append(f"| {int(r.ano_anterior)} → {r.ano} ({int(r.intervalo_anos)} anos) | {numero_br(r.delta_votos_pt,sinal=True)} | {numero_br(r.delta_votos_adv,sinal=True)} | {numero_br(r.delta_pt_pct_validos,2,True)} | {numero_br(r.delta_adv_pct_validos,2,True)} |")
    linhas += ["", "**H4. De 2014 para 2018, o PT perdeu 11.925.617 votos no primeiro turno e 7.460.212 no segundo.** A votação do principal adversário subiu 14.379.799 e 6.756.692, respectivamente, de Aécio Neves para Jair Bolsonaro. No primeiro turno de 2026, o PT também ficou 3.379.966 votos abaixo de 2022; Flávio teve 5.032.158 a mais que Jair em 2022/1. **Origem:** `crescimento_mesmo_turno.csv`, linhas 2018 e 2026, por turno, campos `delta_votos_pt,delta_votos_adv`. **Evidência: alta; as pessoas candidatas não são as mesmas em todos os intervalos.**", "",
        f"**H5. {numero_br(recorde['votacao_recorde'])} é o recorde de votos de uma candidatura em um turno presidencial direto.** Supera os {numero_br(recorde['recorde_anterior'])} de Lula em 2022 por **{numero_br(recorde['supera_em_votos'])} votos**. A busca comparou as {recorde['candidaturas_turnos_comparadas_desde_1989']} candidaturas/turnos disponíveis desde 1989, de todos os partidos. Para as 15 eleições diretas anteriores, o maior total do mais votado foi {numero_br(recorde['maior_votacao_antes_1989'])}, de Jânio Quadros em 1960; todos os concorrentes de cada eleição ficaram abaixo de seu mais votado. É uma prova por limite superior, sem alegar transcrição nominal de todos os derrotados antigos. **Origem:** `todos_candidatos_brasil.csv:votos,posicao_historica`; `limites_candidatos_antes_1989.csv`; `recorde.json`; [TSE, eleições diretas](https://www.tse.jus.br/servicos-eleitorais/glossario/termos/eleicao-direta). **Evidência: alta para o recorde absoluto; o limite anterior a 1989 usa a tabela oficial dos mais votados.**", "",
        "**H6. O recorde absoluto não é recorde de fatia dos votos.** Lula teve **51,79% dos válidos em 2026/2**, contra **61,27% em 2002/2**, a maior fatia do PT na série. Sobre todos os aptos, os mesmos turnos dão **40,48% em 2026** e **45,81% em 2002**; o maior valor do PT sobre aptos foi **46,30% em 2006/2**. O eleitorado passou de **82.074.718 em 1989** para **158.745.502 em 2026**, diferença de **76.670.784**. **Origem:** `nacional_percentuais.csv:pt_pct_validos,pt_pct_aptos,aptos`. **Evidência: alta; percentuais calculados antes de arredondar.**", "",
        "**H7. O espelho do adversário também tem recorde.** Flávio recebeu **59.826.041 votos**, terceira maior votação de uma candidatura/turno na série completa desde 1989 e a maior entre os candidatos fora do PT. Superou os **58.206.354 de Jair em 2022** por **1.619.687**, enquanto Lula acrescentou **3.910.233** na comparação de segundos turnos. Não somar votos do primeiro e do segundo turno para criar um recorde. **Origem:** `todos_candidatos_brasil.csv:partido,votos,posicao_historica`; `crescimento_mesmo_turno.csv`, linha 2026/2. **Evidência: alta, mesmo critério para os dois lados.**", "",
        "**H8. O mapa terminou com o PT à frente em 26 UFs em 2002; em 2026, em 13.** A tabela usa o segundo turno quando houve, o primeiro em 1994/1998, e conta apenas as 27 UFs. ZZ fica separado. A vitória é a maior votação entre **todos** os candidatos, sem exigir 50% no primeiro turno. Origem: `vitorias_ufs_por_eleicao.csv:ufs_pt,ufs_adversario,ufs_outros`; `mapa_turno_decisivo.csv:partido_vencedor`. **Evidência: alta para o mapa das fontes escolhidas.**", "",
        "| Ano / turno decisivo | UFs PT | UFs principal adversário | UFs outro candidato |",
        "|---|---:|---:|---:|"]
    for r in vitorias.itertuples():
        linhas.append(f"| {r.ano} / {r.turno}º | {r.ufs_pt} | {r.ufs_adversario} | {r.ufs_outros} |")
    linhas += ["", "Em 1998, o Ceará deu Ciro Gomes (PPS), enquanto FHC (PSDB) era o principal adversário nacional de Lula. Não pintar toda UF não petista como vitória de FHC. `geografia_todos_turnos.csv` fornece o vencedor efetivo.", "",
        "**H9. O Nordeste se tornou maioria petista nesta série em 2002; a vitória nos nove estados veio em 2006.** No turno decisivo de 1989, o PT venceu **1 dos 9 estados**; em 1994 e 1998, **nenhum**. Em 2002, **8 dos 9**, com **61,52% dos válidos da região**. Desde 2006, venceu os **9** em todas as seis eleições até 2026, inclusive quando perdeu no Brasil em 2018. Em 2026/2, a região deu **24.450.432 a Lula** e **10.796.736 a Flávio**, ou **69,37% e 30,63%**. “Base” aqui é uma descrição de votos e estados vencidos, sem atribuir causa. **Origem:** `vitorias_por_regiao.csv`, Nordeste/turno decisivo; `votos_por_regiao.csv:votos_pt,votos_adv,pt_pct_validos,adv_pct_validos`. **Evidência: alta, critério explícito.**", "",
        "**H10. Amazonas, Amapá, Distrito Federal, Minas Gerais e Rio de Janeiro foram os que mais alternaram entre PT e não PT: três vezes cada.** São nove transições entre as dez eleições, sempre no turno decisivo. Não significa três trocas de um mesmo candidato por outro; PSDB, PRN, PSL, PL e outros partidos permanecem identificados. **Origem:** `ranking_mudancas_uf.csv:uf,mudancas_pt_nao_pt`; `mudancas_de_lado.csv:ano,ano_anterior,partido_anterior,partido_vencedor`. **Evidência: alta, ranking simétrico de mudanças de lado.**", "",
        f"**H11. As provas de contas passam; a coincidência com toda publicação histórica, não.** São {resumo['provas_fontes_adotadas']} testes das fontes adotadas com diferença zero. Entre {resumo['comparacoes_publicacoes']} comparações com outras publicações oficiais, {resumo['comparacoes_publicacoes_que_divergem']} divergem. Além disso, em sete UFs de 1989/2 o detalhe de votos nominais difere da soma dos candidatos; o total nacional se compensa. Os válidos de 1989 foram calculados pela soma dos candidatos, sem alterar votos individuais das candidaturas. **Origem:** `provas.csv`, `comparacao_publicacoes.csv`, `controle_validos_1989.csv`; protocolo em `PT-HISTORICO-METODO.md`. **Evidência: falhas de coincidência documentadas, sem explicação causal inventada nem ajuste para forçar fechamento.**", "",
        "**Para o agente da tela e o YouTube:** os CSV do painel têm somente o contrato pedido; percentuais, crescimento, vencedores e os 18 quadros do mapa estão em `dados/saida/pt_historico/`. Para a curva, priorize primeiro turno contra primeiro turno; para o mapa final de cada eleição, use `mapa_turno_decisivo.csv`. Mantenha o rodapé de versão dos dados antigos. Não criar segundo turno em 1994/1998 nem ligar 1989/2 a 2002/2 como se fossem quatro anos.", ""]
    trecho = "\n".join(linhas)
    caminho = RAIZ / "docs/video/segundo-turno/ACHADOS.md"
    inicio, fim = "<!-- INICIO HISTORIA_PT_AUTOGERADA -->", "<!-- FIM HISTORIA_PT_AUTOGERADA -->"
    atual = caminho.read_text(encoding="utf-8")
    bloco = inicio + "\n" + trecho + fim
    if inicio in atual:
        antes, resto = atual.split(inicio, 1)
        if fim not in resto:
            raise ValueError("Bloco histórico sem marcador final; preservado para revisão")
        _, depois = resto.split(fim, 1)
        atual = antes + bloco + depois
    else:
        atual = atual.rstrip() + "\n\n" + bloco + "\n"
    caminho.write_text(atual, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--somente-cache", action="store_true")
    parser.add_argument("--diagnostico", action="store_true")
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    SAIDA.mkdir(parents=True, exist_ok=True)
    requeridos = [CACHE / "1989/VOTACAO_CANDIDATO_UF_1989.txt", CACHE / "1989/DETALHE_VOTACAO_UF_1989.txt", RAIZ / "dados/bruto/tse/presidente_1998_BR.csv"]
    if any(not p.exists() for p in requeridos):
        if args.somente_cache:
            raise FileNotFoundError("Faltam fontes antigas no cache")
        subprocess.run([sys.executable, "-I", "-X", "utf8", str(RAIZ / "pipeline/inspecionar_pt_historico.py")], check=True, cwd=RAIZ)
    # Os arquivos anteriores só são baixados quando ausentes.
    for ano in [2002, 2006, 2010, 2014, 2018, 2022, 2026]:
        for prefixo, base in [("presidente", "votacao"), ("detalhe", "detalhe")]:
            caminho = RAIZ / f"dados/bruto/tse/{prefixo}_{ano}_BR.csv"
            if not caminho.exists():
                if args.somente_cache:
                    raise FileNotFoundError(caminho)
                subprocess.run([sys.executable, "-I", "-X", "utf8", str(RAIZ / "pipeline/extrair_tse.py"), "--base", base, str(ano)], check=True, cwd=RAIZ)
    # Cadastro oficial já utilizado no pacote do 2º turno: c=s identifica a capital.
    config = json.loads((RAIZ / "dados/bruto/tse/2t2026/config.json").read_text(encoding="utf-8"))
    capitais = {normalizar_nome(m["nm"]): a["cd"].upper() for a in config["abr"] if a["cd"] != "zz" for m in a["mu"] if m["c"] == "s"}
    assert len(capitais) == 27
    v94, d94, reg94 = coletar_1994(args.somente_cache)
    gravar(v94, "candidatos_1994_tabelas.csv")
    gravar(d94, "participacao_1994_tabelas.csv")
    gravar(pd.DataFrame([x for c, _ in reg94 for x in c]), "candidatos_1994_regioes.csv")
    gravar(pd.DataFrame([d for _, d in reg94]), "participacao_1994_regioes.csv")
    diagnostico, votos, detalhes = [], [], []
    for ano in ANOS:
        v, d = ler_1989() if ano == 1989 else (v94, d94) if ano == 1994 else ler_moderno(ano, capitais)
        if ano == 1989:
            controle = d.merge(v.groupby(["ano", "turno", "uf"], as_index=False).votos.sum().rename(columns={"votos": "soma_candidatos"}),
                               on=["ano", "turno", "uf"], validate="one_to_one")
            controle["diferenca_candidatos_detalhe"] = controle.soma_candidatos - controle.validos
            gravar(controle, "controle_validos_1989.csv")
            # Válidos significa soma dos votos válidos de todos os candidatos.
            # Não altera votos dos candidatos; conserva o campo legado divergente
            # para auditoria, em vez de apresentar denominador menor que a dupla.
            d["validos"] = controle.soma_candidatos.to_numpy()
        if ano >= 1998:
            registrar_brutos(ano)
        if ano == 2026:
            segundo = pd.read_csv(RAIZ / "dados/pbi/uf_2turno.csv").query("ano==2026")
            v2 = []
            for r in segundo.itertuples():
                for numero, nome, partido, campo in [(13, "Lula", "PT", "pt"), (22, "Flávio Bolsonaro", "PL", "adv")]:
                    v2.append({"ano": 2026, "turno": 2, "uf": r.uf, "numero": numero, "nome": nome, "partido": partido, "votos": getattr(r, campo)})
            v = pd.concat([v, pd.DataFrame(v2)], ignore_index=True)
            d2 = segundo.rename(columns={"pt": "votos_pt", "adv": "votos_adv"}).assign(turno=2)
            d = pd.concat([d, d2[d.columns]], ignore_index=True)
        # Mesmo número/partido identifica a candidatura; nomes podem variar entre páginas antigas.
        nomes = (v.groupby(["numero", "nome"], as_index=False).votos.sum().sort_values("votos", ascending=False)
                 .drop_duplicates("numero").set_index("numero")["nome"])
        v["nome"] = v.numero.map(nomes)
        v = v.groupby(["ano", "turno", "uf", "numero", "nome", "partido"], as_index=False).votos.sum()
        votos.append(v)
        detalhes.append(d)
        total = v.groupby(["turno", "numero", "nome", "partido"], as_index=False).votos.sum()
        for turno, g in total.groupby("turno"):
            det = d[d.turno.eq(turno)]
            diagnostico.append({"ano": ano, "turno": turno, "ufs": len(det), "votos_pt": int(g[g.partido.eq("PT")].votos.sum()),
                                "soma_votos_todos": int(g.votos.sum()), "validos_adotados": int(det.validos.sum()),
                                "comparecimento": int(det.comparecimento.sum()), "aptos": int(det.aptos.sum())})
    gravar(pd.DataFrame(diagnostico), "diagnostico.csv")
    print(pd.DataFrame(diagnostico).to_string(index=False))
    if args.diagnostico:
        return
    todos = pd.concat(votos, ignore_index=True)
    detalhe = pd.concat(detalhes, ignore_index=True)
    provas, linhas, linhas_br = [], [], []
    for (ano, turno), cand in todos.groupby(["ano", "turno"]):
        totais = cand.groupby(["numero", "partido"], as_index=False).votos.sum()
        pt = totais[totais.partido.eq("PT")].sort_values("votos", ascending=False).iloc[0]
        adv = totais[~totais.partido.eq("PT")].sort_values("votos", ascending=False).iloc[0]
        det = detalhe[detalhe.ano.eq(ano) & detalhe.turno.eq(turno)].set_index("uf")
        assert set(det.index) == set(SLUGS) | {"ZZ"} and not det.index.duplicated().any()
        for uf, g in cand.groupby("uf"):
            total_votos = int(g.votos.sum())
            prova(provas, ano, turno, "Candidatos x válidos adotados (1989: soma nominal; demais: detalhe)", uf, "validos", total_votos, det.loc[uf, "validos"], fonte_ano(ano))
            linhas.append({"ano": ano, "turno": turno, "uf": uf, "candidato_pt": NOMES_PT[ano],
                           "votos_pt": int(g.loc[g.numero.eq(pt.numero), "votos"].sum()), "adversario": NOMES_ADV[ano],
                           "partido_adversario": adv.partido, "votos_adv": int(g.loc[g.numero.eq(adv.numero), "votos"].sum()),
                           "validos": int(det.loc[uf, "validos"]), "comparecimento": int(det.loc[uf, "comparecimento"]), "aptos": int(det.loc[uf, "aptos"])})
        linhas_ano = [r for r in linhas if r["ano"] == ano and r["turno"] == turno]
        br = {**linhas_ano[0], "uf": "BR", **{c: sum(r[c] for r in linhas_ano) for c in SOMAS}}
        linhas_br.append(br)
        if ano == 1994:
            c_reg = pd.DataFrame([r for c, _ in reg94 for r in c])
            d_reg = pd.DataFrame([d for _, d in reg94])
            zz_c = cand[cand.uf.eq("ZZ")]
            controle = {"votos_pt": int(c_reg.loc[c_reg.numero.eq(pt.numero), "votos"].sum() + zz_c.loc[zz_c.numero.eq(pt.numero), "votos"].sum()),
                        "votos_adv": int(c_reg.loc[c_reg.numero.eq(adv.numero), "votos"].sum() + zz_c.loc[zz_c.numero.eq(adv.numero), "votos"].sum())}
            controle.update({c: int(d_reg[c].sum() + det.loc["ZZ", c]) for c in ["validos", "comparecimento", "aptos"]})
            origem = BASE94 + "/brasil (cinco tabelas regionais + exterior)"
        elif ano == 2026:
            controle, origem = api_brasil_2026(turno, args.somente_cache)
        else:
            controle, origem = controle_bruto_direto(ano, turno, int(adv.numero)), fonte_ano(ano)
        for campo in SOMAS:
            prova(provas, ano, turno, "Soma 27 UFs e ZZ x controle nacional", "BR", campo, br[campo], controle[campo], origem)
    uf = pd.DataFrame(linhas)[COLUNAS].sort_values(["ano", "turno", "uf"])
    br = pd.DataFrame(linhas_br)[COLUNAS].sort_values(["ano", "turno"])
    assert len(br) == 18 and len(uf) == 504
    assert not uf.duplicated(["ano", "turno", "uf"]).any()
    for df in [uf, br]:
        assert (df[SOMAS] >= 0).all().all()
        if not df.votos_pt.add(df.votos_adv).le(df.validos).all():
            print("Dupla supera válidos", df[df.votos_pt.add(df.votos_adv).gt(df.validos)].to_string(index=False))
        assert df.votos_pt.add(df.votos_adv).le(df.validos).all()
        assert df.validos.le(df.comparecimento).all() and df.comparecimento.le(df.aptos).all()
    tabela_provas = pd.DataFrame(provas)
    gravar(tabela_provas, "provas.csv")
    if not tabela_provas.bate.all():
        print(tabela_provas[~tabela_provas.bate].to_string(index=False))
        raise ValueError("Falha nas fontes adotadas; painel não foi gravado")
    publicacoes = controles_publicados(br, todos, args.somente_cache)
    gravar(publicacoes, "comparacao_publicacoes.csv")
    limites = limites_antes_1989(args.somente_cache)
    resultados = montar_analises(uf, br, todos, limites)
    gravar(todos, "todos_candidatos_uf.csv")
    for nome, df in [("pt_historico_uf.csv", uf), ("pt_historico_brasil.csv", br)]:
        caminho = RAIZ / "dados/pbi" / nome
        temp = caminho.with_suffix(".csv.tmp")
        df.to_csv(temp, index=False, encoding="utf-8", lineterminator="\n")
        temp.replace(caminho)
    for tipo in ["votacao_candidato_uf", "detalhe_votacao_uf"]:
        arq = CACHE / f"{tipo}_1989.zip"
        FONTES.append({"url": f"https://cdn.tse.jus.br/estatistica/sead/odsele/{tipo}/{tipo}_1989.zip", "arquivo": arq.relative_to(RAIZ).as_posix(), "sha256": hashlib.sha256(arq.read_bytes()).hexdigest()})
    config_caminho = RAIZ / "dados/bruto/tse/2t2026/config.json"
    FONTES.append({"url": "https://resultados.tse.jus.br/oficial/ele2026/6258/config/mun-e006258-cm.json", "arquivo": config_caminho.relative_to(RAIZ).as_posix(), "sha256": hashlib.sha256(config_caminho.read_bytes()).hexdigest()})
    gravar(pd.DataFrame(FONTES).drop_duplicates().sort_values("arquivo"), "fontes.csv")
    resumo = {"turnos": len(br), "linhas_uf": len(uf), "provas_fontes_adotadas": len(provas), "provas_todas_batem": True,
              "comparacoes_publicacoes": len(publicacoes), "comparacoes_publicacoes_que_divergem": int((~publicacoes.bate).sum()),
              "anos_com_versoes_divergentes": sorted(map(int, publicacoes.loc[~publicacoes.bate, "ano"].unique())),
              "campos_divergentes_detalhe_nominal_1989": int(pd.read_csv(SAIDA / "controle_validos_1989.csv").diferenca_candidatos_detalhe.ne(0).sum()),
              "regra_exterior": "ZZ separado nas UFs e incluído uma vez no Brasil em todos os anos",
              "regra_transito_2010": "VT distribuído por capital declarada no bruto para a UF onde ocorreu a votação; cada registro conservado",
              "recorde": resultados[-1]}
    (SAIDA / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    documentar(resultados, resumo)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
