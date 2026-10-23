"""Do país à escola: votação de presidente (1º turno) por local de votação em uma cidade, 2018–2026.

Lê em fluxo `votacao_secao_<ano>_BR.zip` (presidente, o país inteiro, ~250 MB comprimido; os arquivos por UF só trazem a
eleição estadual), guarda só o município no 1º turno e soma os votos por local de votação (zona + número do local). O
recorte filtrado fica em cache em `dados/bruto/tse/secoes_<ano>_<uf>_<cd>.csv`. As coordenadas vêm de
`eleitorado_local_votacao_2022.zip` (o arquivo de 2026 está corrompido no servidor do TSE em 22/10/2026); o cruzamento
é por zona + número do local e, sem par, pelo nome do local.

Saída: `dados/saida/locais_<municipio>.csv` (ano, zona, local, nome, endereço, bairro, lat, lon, aptos se houver, votos
do PT, do adversário principal, válidos).
Uso: python -I -X utf8 pipeline/extrair_secoes.py [--uf MG --cd 43710 --nome contagem] [ano ...]
"""
import io
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extrair_tse import BLOCO, ArquivoRemoto  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://cdn.tse.jus.br/estatistica/sead/odsele/"
ANOS = [2018, 2022, 2026]
# Número do PT e do adversário principal no 1º turno de cada ano (o mais votado fora do PT no país).
NUMEROS = {2018: (13, 17), 2022: (13, 22), 2026: (13, 22)}


def ler_membro_csv(url, filtro, colunas):
    remoto = ArquivoRemoto(url)
    with zipfile.ZipFile(io.BufferedReader(remoto, buffer_size=BLOCO)) as z:
        nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(nome) as bruto:
            partes = []
            for bloco in pd.read_csv(io.TextIOWrapper(bruto, encoding="latin1"), sep=";", dtype=str,
                                     chunksize=400_000, usecols=lambda c: c in colunas):
                partes.append(filtro(bloco))
    print(f"  {nome}: baixados {remoto.baixado / 1e6:,.0f} MB")
    return pd.concat(partes, ignore_index=True)


def normalizar(txt):
    txt = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode().upper()
    return "".join(c for c in txt if c.isalnum())


def votos_por_local(ano, uf, cd):
    colunas = {"NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "DS_CARGO", "NR_VOTAVEL", "QT_VOTOS",
               "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_LOCAL_VOTACAO_ENDERECO"}

    def filtro(b):
        b = b[(b.NR_TURNO == "1") & (b.SG_UF == uf) & (b.CD_MUNICIPIO.astype(int) == cd)]
        return b[b.DS_CARGO.str.upper().str.startswith("PRESIDENTE")]

    cache = RAIZ / "dados" / "bruto" / "tse" / f"secoes_{ano}_{uf}_{cd}.csv"
    if cache.exists():
        d = pd.read_csv(cache, dtype=str)
    else:
        d = ler_membro_csv(f"{BASE}votacao_secao/votacao_secao_{ano}_BR.zip", filtro, colunas)
        d.to_csv(cache, index=False)
    if d.empty:
        raise SystemExit(f"{ano}: nenhuma linha de presidente para {uf}/{cd}")
    d["QT_VOTOS"] = d.QT_VOTOS.astype(int)
    d["NR_VOTAVEL"] = d.NR_VOTAVEL.astype(int)
    pt, adv = NUMEROS[ano]
    # Brancos (95) e nulos (96) ficam fora dos válidos.
    validos = d[~d.NR_VOTAVEL.isin([95, 96])]
    chave = ["NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_LOCAL_VOTACAO_ENDERECO"]
    g = validos.groupby(chave).apply(lambda x: pd.Series({
        "pt": x.loc[x.NR_VOTAVEL == pt, "QT_VOTOS"].sum(), "adv": x.loc[x.NR_VOTAVEL == adv, "QT_VOTOS"].sum(),
        "validos": x.QT_VOTOS.sum(), "secoes": x.NR_SECAO.nunique()}), include_groups=False).reset_index()
    g.insert(0, "ano", ano)
    return g


def coordenadas(uf, cd):
    colunas = {"SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "NM_BAIRRO",
               "NR_LATITUDE", "NR_LONGITUDE", "QT_ELEITOR_SECAO", "NR_TURNO"}

    def filtro(b):
        return b[(b.SG_UF == uf) & (b.CD_MUNICIPIO.astype(int) == cd) & (b.NR_TURNO == "1")]

    d = ler_membro_csv(f"{BASE}eleitorado_locais_votacao/eleitorado_local_votacao_2022.zip", filtro, colunas)
    d["QT_ELEITOR_SECAO"] = pd.to_numeric(d.QT_ELEITOR_SECAO, errors="coerce")
    return (d.groupby(["NR_ZONA", "NR_LOCAL_VOTACAO"], as_index=False)
            .agg(nome_2022=("NM_LOCAL_VOTACAO", "first"), bairro=("NM_BAIRRO", "first"),
                 lat=("NR_LATITUDE", "first"), lon=("NR_LONGITUDE", "first"), eleitores_2022=("QT_ELEITOR_SECAO", "sum")))


if __name__ == "__main__":
    args = sys.argv[1:]
    uf = args[args.index("--uf") + 1] if "--uf" in args else "MG"
    cd = int(args[args.index("--cd") + 1]) if "--cd" in args else 43710
    nome = args[args.index("--nome") + 1] if "--nome" in args else "contagem"
    anos = [int(a) for a in args if a.isdigit() and len(a) == 4] or ANOS
    coord = coordenadas(uf, cd)
    coord["chave_nome"] = coord.nome_2022.map(normalizar)
    saidas = []
    for ano in anos:
        g = votos_por_local(ano, uf, cd)
        g = g.merge(coord, on=["NR_ZONA", "NR_LOCAL_VOTACAO"], how="left")
        sem = g.lat.isna()
        if sem.any():
            por_nome = coord.drop_duplicates("chave_nome").set_index("chave_nome")
            chaves = g.loc[sem, "NM_LOCAL_VOTACAO"].map(normalizar)
            for col in ("bairro", "lat", "lon", "eleitores_2022", "nome_2022"):
                g.loc[sem, col] = chaves.map(por_nome[col])
        print(f"{ano}: {len(g)} locais · {int(g.validos.sum()):,} válidos · sem coordenada: {int(g.lat.isna().sum())}")
        saidas.append(g)
    destino = RAIZ / "dados" / "saida" / f"locais_{nome}.csv"
    pd.concat(saidas).drop(columns=["chave_nome"]).to_csv(destino, index=False)
    print(f"gravado {destino}")
