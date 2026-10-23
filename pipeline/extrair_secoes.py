"""Do país à escola: votação de presidente (1º turno) por local de votação, 2018–2026, numa cidade ou numa lista delas.

Lê em fluxo `votacao_secao_<ano>_BR.zip` (presidente, o país inteiro, ~160–250 MB comprimido; os arquivos por UF só
trazem a eleição estadual) UMA vez por ano, guarda só os municípios pedidos no 1º turno e soma os votos por local de
votação (zona + número do local). O recorte filtrado de cada município fica em cache em
`dados/bruto/tse/secoes_<ano>_<uf>_<cd>.csv` (cidade com cache não pede o zip de novo). As coordenadas vêm de
`eleitorado_local_votacao_2022.zip` (o arquivo de 2026 estava corrompido no servidor do TSE em 22/10/2026), também numa
passada só e com cache em `dados/bruto/tse/locais2022_<uf>_<cd>.csv`; o cruzamento é por zona + número do local e, sem
par, pelo nome do local normalizado (local sem par nenhum fica sem coordenada: entra nas contas, fica fora do mapa).

Saídas:
- uma cidade: `dados/saida/locais_<nome>.csv` (ano, zona, local, nome, endereço, votos do PT, do adversário principal,
  válidos, seções, nome em 2022, bairro, lat, lon, eleitores em 2022) — a de Contagem alimenta a Local Contagem e o
  mockup;
- `--t20`: as 34 cidades da tela Escola (CIDADES_T20) em `dados/bruto/tse/locais_t20.csv` (as mesmas colunas e mais
  uf, cd_tse e cd_ibge; bruto, fora do repositório: o que vai ao modelo é `dados/pbi/t20_locais.csv`, de
  pipeline/exportar_t20.py).

Uso: python -I -X utf8 pipeline/extrair_secoes.py [--uf MG --cd 43710 --nome contagem] [ano ...]
     python -I -X utf8 pipeline/extrair_secoes.py --t20 [ano ...]
"""
import functools
import io
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extrair_tse import BLOCO, ArquivoRemoto  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TSE = RAIZ / "dados" / "bruto" / "tse"
BASE = "https://cdn.tse.jus.br/estatistica/sead/odsele/"
ANOS = [2018, 2022, 2026]
# Número do PT e do adversário principal no 1º turno de cada ano (o mais votado fora do PT no país).
NUMEROS = {2018: (13, 17), 2022: (13, 22), 2026: (13, 22)}

# As 34 cidades da tela Escola (pedido do dono, 23/10/2026: "não dá pra variar ele mais? colocar outras além de
# contagem"): as 27 capitais, as 6 maiores que trocaram Lula por Flávio de 2022 para 2026 (a lista "As maiores que
# viraram" da tela Virada) e Contagem, onde o documentário começa. (UF, código TSE, código IBGE, nome) — os códigos
# saem de dados/saida/municipios.csv (depara TSE × IBGE do pipeline) e o nome é conferido contra o TSE na extração.
CIDADES_T20 = [
    ("AC", 1392, "1200401", "Rio Branco"), ("AL", 27855, "2704302", "Maceió"), ("AP", 6050, "1600303", "Macapá"),
    ("AM", 2550, "1302603", "Manaus"), ("BA", 38490, "2927408", "Salvador"), ("CE", 13897, "2304400", "Fortaleza"),
    ("DF", 97012, "5300108", "Brasília"), ("ES", 57053, "3205309", "Vitória"), ("GO", 93734, "5208707", "Goiânia"),
    ("MA", 9210, "2111300", "São Luís"), ("MT", 90670, "5103403", "Cuiabá"), ("MS", 90514, "5002704", "Campo Grande"),
    ("MG", 41238, "3106200", "Belo Horizonte"), ("PA", 4278, "1501402", "Belém"), ("PB", 20516, "2507507", "João Pessoa"),
    ("PR", 75353, "4106902", "Curitiba"), ("PE", 25313, "2611606", "Recife"), ("PI", 12190, "2211001", "Teresina"),
    ("RJ", 60011, "3304557", "Rio de Janeiro"), ("RN", 17612, "2408102", "Natal"), ("RS", 88013, "4314902", "Porto Alegre"),
    ("RO", 35, "1100205", "Porto Velho"), ("RR", 3018, "1400100", "Boa Vista"), ("SC", 81051, "4205407", "Florianópolis"),
    ("SP", 71072, "3550308", "São Paulo"), ("SE", 31054, "2800308", "Aracaju"), ("TO", 73440, "1721000", "Palmas"),
    ("SP", 67890, "3534401", "Osasco"), ("PA", 4154, "1500800", "Ananindeua"), ("MG", 48658, "3143302", "Montes Claros"),
    ("MG", 41335, "3106705", "Betim"), ("MG", 50911, "3154606", "Ribeirão das Neves"), ("SP", 62138, "3505708", "Barueri"),
    ("MG", 43710, "3118601", "Contagem"),
]
# grupo de cada cidade na tela (ordem do filtro e texto da ficha): capital, virou (as 6) ou início (Contagem)
GRUPO_T20 = {**{c[2]: "capital" for c in CIDADES_T20[:27]}, **{c[2]: "virou" for c in CIDADES_T20[27:33]},
             "3118601": "início"}

COLUNAS_SECAO = {"NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "DS_CARGO", "NR_VOTAVEL", "QT_VOTOS",
                 "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_LOCAL_VOTACAO_ENDERECO"}
COLUNAS_LOCAL = {"SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO",
                 "NM_BAIRRO", "NR_LATITUDE", "NR_LONGITUDE", "QT_ELEITOR_SECAO", "NR_TURNO"}


def normalizar(txt):
    txt = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode().upper()
    return "".join(c for c in txt if c.isalnum())


def _cache_secoes(ano, uf, cd):
    return TSE / f"secoes_{ano}_{uf}_{cd}.csv"


def _cache_locais(uf, cd):
    return TSE / f"locais2022_{uf}_{cd}.csv"


def _passada(url, cidades, filtro, destino):
    """Lê o membro .csv do zip remoto em fluxo e grava, por cidade, as linhas que passam no `filtro` (bloco → bloco) em
    `destino(uf, cd)`. Grava em .parcial e só troca pelo nome final no fim: uma passada interrompida não deixa cache
    pela metade. Cidade sem linha nenhuma derruba a extração (código errado)."""
    alvo = {(uf, int(cd)) for uf, cd in cidades}
    parciais = {k: destino(*k).with_suffix(".parcial") for k in alvo}
    for p in parciais.values():
        p.unlink(missing_ok=True)
    remoto = ArquivoRemoto(url)
    with zipfile.ZipFile(io.BufferedReader(remoto, buffer_size=BLOCO)) as z:
        nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(nome) as bruto:
            colunas = None
            for bloco in pd.read_csv(io.TextIOWrapper(bruto, encoding="latin1"), sep=";", dtype=str,
                                     chunksize=400_000, usecols=lambda c: c in filtro.colunas):
                b = filtro(bloco)
                if b.empty:
                    continue
                cd = b.CD_MUNICIPIO.astype(int)
                dentro = pd.MultiIndex.from_arrays([b.SG_UF, cd]).isin(list(alvo))
                b, cd = b[dentro], cd[dentro]
                colunas = list(b.columns)
                for (uf, cdm), g in b.groupby([b.SG_UF, cd], sort=False):
                    p = parciais[(uf, int(cdm))]
                    g.to_csv(p, mode="a", header=not p.exists(), index=False)
    print(f"  {nome}: baixados {remoto.baixado / 1e6:,.0f} MB")
    vazias = [k for k, p in parciais.items() if not p.exists()]
    if vazias:
        raise SystemExit(f"{url.rsplit('/', 1)[-1]}: nenhuma linha para {vazias} (código TSE errado?)")
    for k, p in parciais.items():
        p.replace(destino(*k))
    return colunas


def baixar_secoes(ano, cidades):
    """Uma passada no zip nacional do ano para as cidades sem cache."""
    faltam = [(uf, cd) for uf, cd in cidades if not _cache_secoes(ano, uf, cd).exists()]
    if not faltam:
        return

    def filtro(b):
        b = b[b.NR_TURNO == "1"]
        return b[b.DS_CARGO.str.upper().str.startswith("PRESIDENTE")]

    filtro.colunas = COLUNAS_SECAO
    print(f"{ano}: lendo o zip nacional para {len(faltam)} cidade(s)")
    _passada(f"{BASE}votacao_secao/votacao_secao_{ano}_BR.zip", faltam, filtro,
             lambda uf, cd: _cache_secoes(ano, uf, cd))


def baixar_locais(cidades):
    """Uma passada no cadastro de locais de 2022 (coordenadas, bairro) para as cidades sem cache."""
    faltam = [(uf, cd) for uf, cd in cidades if not _cache_locais(uf, cd).exists()]
    if not faltam:
        return

    def filtro(b):
        return b[b.NR_TURNO == "1"]

    filtro.colunas = COLUNAS_LOCAL
    print(f"locais 2022: lendo o cadastro para {len(faltam)} cidade(s)")
    _passada(f"{BASE}eleitorado_locais_votacao/eleitorado_local_votacao_2022.zip", faltam, filtro, _cache_locais)


@functools.lru_cache
def numeros_validos(ano):
    """Números com voto válido no 1º turno do ano, do arquivo de presidente por município e zona do TSE
    (`dados/bruto/tse/presidente_<ano>_BR.csv`, pipeline/extrair_tse.py). A seção também traz o voto em candidato com
    registro negado (o 28 em 2026: 20 votos em Contagem, 361 em São Paulo), que o TSE anula: fica fora dos válidos,
    como no total do município."""
    p = pd.read_csv(TSE / f"presidente_{ano}_BR.csv", sep=";", encoding="latin1", dtype=str,
                    usecols=["NR_TURNO", "NR_CANDIDATO", "QT_VOTOS_NOMINAIS_VALIDOS"])
    p = p[(p.NR_TURNO == "1") & (p.QT_VOTOS_NOMINAIS_VALIDOS.astype(int) > 0)]
    return frozenset(p.NR_CANDIDATO.astype(int))


def votos_por_local(ano, uf, cd):
    baixar_secoes(ano, [(uf, cd)])
    d = pd.read_csv(_cache_secoes(ano, uf, cd), dtype=str)
    if d.empty:
        raise SystemExit(f"{ano}: nenhuma linha de presidente para {uf}/{cd}")
    d["QT_VOTOS"] = d.QT_VOTOS.astype(int)
    d["NR_VOTAVEL"] = d.NR_VOTAVEL.astype(int)
    pt, adv = NUMEROS[ano]
    # Válidos = votos nos candidatos com voto válido no ano: brancos (95), nulos (96) e anulados ficam fora.
    validos = d[d.NR_VOTAVEL.isin(numeros_validos(ano))].copy()
    validos["pt"] = validos.QT_VOTOS.where(validos.NR_VOTAVEL == pt, 0)
    validos["adv"] = validos.QT_VOTOS.where(validos.NR_VOTAVEL == adv, 0)
    chave = ["NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "DS_LOCAL_VOTACAO_ENDERECO"]
    g = (validos.groupby(chave, dropna=False)
         .agg(pt=("pt", "sum"), adv=("adv", "sum"), validos=("QT_VOTOS", "sum"), secoes=("NR_SECAO", "nunique"))
         .reset_index())
    # local só com brancos e nulos (não acontece nas 34; fica por segurança com zero válidos)
    sem_validos = d.groupby(chave, dropna=False).size().index.difference(g.set_index(chave).index)
    if len(sem_validos):
        print(f"  aviso {ano} {uf}/{cd}: {len(sem_validos)} local(is) sem voto válido, fora")
    g.insert(0, "ano", ano)
    return g


def coordenadas(uf, cd):
    baixar_locais([(uf, cd)])
    d = pd.read_csv(_cache_locais(uf, cd), dtype=str)
    d["QT_ELEITOR_SECAO"] = pd.to_numeric(d.QT_ELEITOR_SECAO, errors="coerce")
    # o TSE marca local sem coordenada com -1 (latitude perto de zero é Macapá, no equador: fica)
    lat, lon = pd.to_numeric(d.NR_LATITUDE, errors="coerce"), pd.to_numeric(d.NR_LONGITUDE, errors="coerce")
    sem = (lat == -1) | (lon == -1)
    d["NR_LATITUDE"], d["NR_LONGITUDE"] = lat.mask(sem), lon.mask(sem)
    return (d.groupby(["NR_ZONA", "NR_LOCAL_VOTACAO"], as_index=False)
            .agg(nome_2022=("NM_LOCAL_VOTACAO", "first"), bairro=("NM_BAIRRO", "first"),
                 lat=("NR_LATITUDE", "first"), lon=("NR_LONGITUDE", "first"), eleitores_2022=("QT_ELEITOR_SECAO", "sum")))


def locais(uf, cd, anos, rotulo=""):
    """Os locais de cada ano com votos, bairro e coordenada (zona + número; sem par, o nome normalizado)."""
    coord = coordenadas(uf, cd)
    coord["chave_nome"] = coord.nome_2022.map(normalizar)
    saidas = []
    for ano in anos:
        g = votos_por_local(ano, uf, cd)
        g = g.merge(coord, on=["NR_ZONA", "NR_LOCAL_VOTACAO"], how="left")
        sem = g.lat.isna()
        if sem.any():
            # par pelo nome: só nomes únicos no cadastro de 2022 (nome repetido não decide o lugar)
            unicos = coord[coord.lat.notna()].drop_duplicates("chave_nome", keep=False).set_index("chave_nome")
            chaves = g.loc[sem, "NM_LOCAL_VOTACAO"].map(normalizar)
            achou = chaves.isin(unicos.index)
            for col in ("bairro", "lat", "lon", "eleitores_2022", "nome_2022"):
                g.loc[achou[achou].index, col] = chaves[achou].map(unicos[col])
        print(f"{rotulo}{ano}: {len(g)} locais · {int(g.validos.sum()):,} válidos · sem coordenada: "
              f"{int(g.lat.isna().sum())}")
        saidas.append(g)
    return pd.concat(saidas).drop(columns=["chave_nome"])


def _uma_cidade(args, anos):
    uf = args[args.index("--uf") + 1] if "--uf" in args else "MG"
    cd = int(args[args.index("--cd") + 1]) if "--cd" in args else 43710
    nome = args[args.index("--nome") + 1] if "--nome" in args else "contagem"
    destino = RAIZ / "dados" / "saida" / f"locais_{nome}.csv"
    locais(uf, cd, anos).to_csv(destino, index=False)
    print(f"gravado {destino}")


def _t20(anos):
    cidades = [(uf, cd) for uf, cd, _ibge, _nome in CIDADES_T20]
    baixar_locais(cidades)
    for ano in anos:
        baixar_secoes(ano, cidades)
    partes = []
    for uf, cd, ibge, nome in CIDADES_T20:
        tse = pd.read_csv(_cache_locais(uf, cd), dtype=str, usecols=["NM_MUNICIPIO"], nrows=1).NM_MUNICIPIO.iloc[0]
        if normalizar(tse) != normalizar(nome):
            raise SystemExit(f"{uf}/{cd}: o TSE chama de {tse!r}, a lista diz {nome!r}")
        t = locais(uf, cd, anos, rotulo=f"{nome} ({uf}) ")
        t.insert(0, "cd_ibge", ibge)
        t.insert(0, "cd_tse", cd)
        t.insert(0, "uf", uf)
        partes.append(t)
    destino = TSE / "locais_t20.csv"
    pd.concat(partes).to_csv(destino, index=False)
    print(f"gravado {destino}")


if __name__ == "__main__":
    args = sys.argv[1:]
    anos = [int(a) for a in args if a.isdigit() and len(a) == 4] or ANOS
    if "--t20" in args:
        _t20(anos)
    else:
        _uma_cidade(args, anos)
