"""Abstenção por município × faixa de idade (1º turno, 2014–2026), para a tela 07 · Quem falta (código T25).

Lê os membros por UF (`perfil_comparecimento_abstencao_<ano>_<UF>.csv`, inclusive ZZ, o exterior) de
`perfil_comparecimento_abstencao_<ano>.zip` do TSE em fluxo (HTTP Range + leitura por blocos, como
`extrair_perfil_abstencao.py` faz com o `_BRASIL`), sem gravar o arquivo bruto (3 GB descomprimidos por ano). Filtra o
1º turno, soma aptos, comparecimento e abstenção por município (código TSE → IBGE pelo cadastro
`dados/saida/municipios.csv`) e faixa de idade, agrupada nas sete faixas das telas 06 e 07 (16 e 17 anos, 18 a 24, 25
a 34, 35 a 44, 45 a 59, 60 a 69, 70 ou mais). A idade que o TSE não sabe ("Inválido") fica numa oitava linha,
"idade não informada" (ordem 9), para a soma bater; a tela não a mostra.

Os zips de 2018 e 2022 não trazem o membro do DF nem o do exterior (ZZ): essas duas UFs saem do `_BRASIL`, lido inteiro
em fluxo nesses anos, e a leitura serve também de conferência UF a UF (cada membro próprio contra a mesma UF no
`_BRASIL`).

Saída: `dados/saida/abstencao_municipio_faixa.csv` (ano, uf, cd_tse, cd_ibge, faixa, faixa_ordem, aptos,
comparecimento, abstencao). O exterior sai com uf = ZZ, o código TSE da cidade e cd_ibge vazio.

Conferência (impressa no fim): por ano, a soma de todos os membros contra o `_BRASIL` (dados/saida/abstencao_perfil.csv,
gravado por extrair_perfil_abstencao.py) e a soma dos municípios (sem o ZZ) contra 'Município ano'
(dados/pbi/municipio_ano.csv, que vem do detalhe da votação). Antes de 2014 o TSE não publica esta base.

Uso: python -I -X utf8 pipeline/extrair_abstencao_municipio.py [ano ...] [--conferir]
     (--conferir só refaz a conferência sobre o CSV já gravado, sem baixar nada)
"""
import io
import sys
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extrair_tse import BLOCO, ArquivoRemoto  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "dados" / "saida" / "abstencao_municipio_faixa.csv"
CADASTRO = RAIZ / "dados" / "saida" / "municipios.csv"
PERFIL_BRASIL = RAIZ / "dados" / "saida" / "abstencao_perfil.csv"
MUNICIPIO_ANO = RAIZ / "dados" / "pbi" / "municipio_ano.csv"
URL = ("https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_comparecimento_abstencao/"
       "perfil_comparecimento_abstencao_{ano}.zip")
ANOS = [2014, 2018, 2022, 2026]
# faixa do TSE (DS_FAIXA_ETARIA) -> (faixa da tela, ordem); as mesmas faixas da tela 06 (desenho_t06.FAIXAS)
FAIXAS = [
    ("16 e 17 anos", ["16 anos", "17 anos"]),
    ("18 a 24 anos", ["18 anos", "19 anos", "20 anos", "21 a 24 anos"]),
    ("25 a 34 anos", ["25 a 29 anos", "30 a 34 anos"]),
    ("35 a 44 anos", ["35 a 39 anos", "40 a 44 anos"]),
    ("45 a 59 anos", ["45 a 49 anos", "50 a 54 anos", "55 a 59 anos"]),
    ("60 a 69 anos", ["60 a 64 anos", "65 a 69 anos"]),
    ("70 anos ou mais", ["70 a 74 anos", "75 a 79 anos", "80 a 84 anos", "85 a 89 anos", "90 a 94 anos",
                         "95 a 99 anos", "100 anos ou mais"]),
]
SEM_IDADE = ("idade não informada", 9)
DA_CATEGORIA = {cat: (faixa, i + 1) for i, (faixa, cats) in enumerate(FAIXAS) for cat in cats}
COLUNAS = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "DS_FAIXA_ETARIA", "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]
SOMAS = ["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]


def membro_uf(nome):
    """Sigla da UF do membro (`…_<ano>_<UF>.csv`) ou None para o _BRASIL, o leiame e o que não for CSV."""
    if not nome.lower().endswith(".csv"):
        return None
    uf = nome.rsplit("_", 1)[-1][:-4].upper()
    return uf if len(uf) == 2 else None


CHAVE = ["SG_UF", "CD_MUNICIPIO", "DS_FAIXA_ETARIA"]
TIPOS = {"NR_TURNO": "int16", "SG_UF": str, "CD_MUNICIPIO": str, "DS_FAIXA_ETARIA": str, "QT_APTOS": "int64",
         "QT_COMPARECIMENTO": "int64", "QT_ABSTENCAO": "int64"}
# as 27 UFs e o exterior: o membro que faltar no zip (2018 e 2022 não trazem DF nem ZZ) sai do _BRASIL
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ",
       "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"]


def _blocos(z, nome):
    """Blocos do 1º turno de um membro do zip, lido em fluxo."""
    with z.open(nome) as bruto:
        for bloco in pd.read_csv(io.TextIOWrapper(bruto, encoding="latin1"), sep=";", usecols=COLUNAS, dtype=TIPOS,
                                 chunksize=1_000_000):
            bloco = bloco[bloco.NR_TURNO == 1].copy()
            bloco["SG_UF"] = bloco.SG_UF.str.strip().str.upper()
            yield bloco


def agregar(ano):
    """Soma do 1º turno por (UF, município TSE, faixa do TSE), lendo os membros por UF do zip remoto em fluxo. Se o zip
    não traz o membro de alguma UF (2018 e 2022: DF e ZZ), essa UF sai do _BRASIL, que então é lido inteiro e também
    serve de conferência: a soma de cada UF com membro próprio contra a mesma UF no _BRASIL. Devolve (soma, conferência
    por UF ou None)."""
    inicio = time.time()
    remoto = ArquivoRemoto(URL.format(ano=ano))
    partes, por_uf = [], {}
    with zipfile.ZipFile(io.BufferedReader(remoto, buffer_size=BLOCO)) as z:
        nomes = z.namelist()
        membros = sorted((membro_uf(n), n) for n in nomes if membro_uf(n))
        for uf, nome in membros:
            tot = None
            for bloco in _blocos(z, nome):
                partes.append(bloco.groupby(CHAVE, as_index=False)[SOMAS].sum())
                s = bloco[SOMAS].sum()
                tot = s if tot is None else tot + s
            por_uf[uf] = tot
        faltam = sorted(set(UFS) - {uf for uf, _n in membros})
        conferencia = None
        if faltam:
            brasil = next(n for n in nomes if n.upper().endswith("_BRASIL.CSV"))
            acum = []
            for bloco in _blocos(z, brasil):
                acum.append(bloco.groupby("SG_UF")[SOMAS].sum())
                partes.append(bloco[bloco.SG_UF.isin(faltam)].groupby(CHAVE, as_index=False)[SOMAS].sum())
            no_brasil = pd.concat(acum).groupby(level=0).sum()
            proprios = pd.DataFrame(por_uf).T
            conferencia = proprios.join(no_brasil, rsuffix="_BRASIL")
            conferencia.insert(0, "ano", ano)
    soma = pd.concat(partes).groupby(CHAVE, as_index=False)[SOMAS].sum()
    soma.insert(0, "ano", ano)
    extra = f" · {', '.join(faltam)} lidos do _BRASIL" if faltam else ""
    print(f"{ano}: {len(membros)} membros por UF{extra} · baixados {remoto.baixado / 1e6:,.0f} MB de "
          f"{remoto.tamanho / 1e6:,.0f} MB · aptos {soma.QT_APTOS.sum():,} · {time.time() - inicio:,.0f} s", flush=True)
    return soma, conferencia


def montar(bruto):
    """Bruto do TSE (por faixa fina) -> as sete faixas da tela + idade não informada, com o código IBGE."""
    cad = pd.read_csv(CADASTRO, dtype={"cd_ibge": str})
    ibge = dict(zip(cad.cd_tse.astype(int), cad.cd_ibge))
    d = bruto.copy()
    d["DS_FAIXA_ETARIA"] = d.DS_FAIXA_ETARIA.str.strip()
    desconhecidas = sorted(set(d.DS_FAIXA_ETARIA) - set(DA_CATEGORIA) - {"Inválido"})
    if desconhecidas:
        raise SystemExit(f"faixas do TSE fora do mapa: {desconhecidas}")
    par = d.DS_FAIXA_ETARIA.map(lambda c: DA_CATEGORIA.get(c, SEM_IDADE))
    d["faixa"] = par.str[0]
    d["faixa_ordem"] = par.str[1].astype(int)
    d["cd_tse"] = d.CD_MUNICIPIO.astype(int)
    d["uf"] = d.SG_UF.str.strip().str.upper()
    d["cd_ibge"] = d.cd_tse.map(ibge)
    d.loc[d.uf == "ZZ", "cd_ibge"] = None
    sem = d[(d.uf != "ZZ") & d.cd_ibge.isna()][["ano", "uf", "cd_tse"]].drop_duplicates()
    if len(sem):
        raise SystemExit(f"{len(sem)} município(s) do perfil sem código IBGE no cadastro: {sem.head(20).values.tolist()}")
    d = d.groupby(["ano", "uf", "cd_tse", "cd_ibge", "faixa", "faixa_ordem"], as_index=False, dropna=False)[SOMAS].sum()
    d.columns = ["ano", "uf", "cd_tse", "cd_ibge", "faixa", "faixa_ordem", "aptos", "comparecimento", "abstencao"]
    return d.sort_values(["ano", "uf", "cd_tse", "faixa_ordem"]).reset_index(drop=True)


def conferir(d):
    """Imprime a conferência por ano: todos os membros × _BRASIL e municípios × 'Município ano'."""
    ok = True
    brasil = pd.read_csv(PERFIL_BRASIL)
    brasil = brasil[brasil.dimensao == "faixa_etaria"].groupby("ano")[["aptos", "comparecimento", "abstencao"]].sum()
    mun_ano = pd.read_csv(MUNICIPIO_ANO, dtype={"cd_ibge": str}).groupby("ano")[["aptos", "abstencoes"]].sum()
    print("\nConferência (1º turno)")
    print(f"{'ano':>4}  {'aptos UFs+ZZ':>13} {'_BRASIL':>13} {'dif':>6}  {'abst UFs+ZZ':>12} {'_BRASIL':>12} {'dif':>6}"
          f"  {'aptos munic.':>13} {'Munic. ano':>13} {'dif':>8}  {'abst munic.':>12} {'Munic. ano':>12} {'dif':>8}"
          f"  {'municípios':>10}")
    for ano, g in d.groupby("ano"):
        mun = g[g.uf != "ZZ"]
        a_t, s_t = int(g.aptos.sum()), int(g.abstencao.sum())
        a_b, s_b = (int(brasil.loc[ano, "aptos"]), int(brasil.loc[ano, "abstencao"])) if ano in brasil.index else (0, 0)
        a_m, s_m = int(mun.aptos.sum()), int(mun.abstencao.sum())
        a_r, s_r = (int(mun_ano.loc[ano, "aptos"]), int(mun_ano.loc[ano, "abstencoes"])) if ano in mun_ano.index \
            else (0, 0)
        ok &= a_t == a_b and s_t == s_b
        print(f"{ano:>4}  {a_t:>13,} {a_b:>13,} {a_t - a_b:>6,}  {s_t:>12,} {s_b:>12,} {s_t - s_b:>6,}"
              f"  {a_m:>13,} {a_r:>13,} {a_m - a_r:>8,}  {s_m:>12,} {s_r:>12,} {s_m - s_r:>8,}"
              f"  {mun.cd_ibge.nunique():>10,}")
    print("membros por UF = _BRASIL:", "sim" if ok else "NÃO")
    return ok


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--conferir" in args:
        sys.exit(0 if conferir(pd.read_csv(SAIDA, dtype={"cd_ibge": str})) else 1)
    anos = [int(a) for a in args if a.isdigit()] or ANOS
    with ProcessPoolExecutor(max_workers=min(4, len(anos))) as ex:
        resultados = list(ex.map(agregar, anos))
    novos = montar(pd.concat([r[0] for r in resultados]))
    for _soma, conf in resultados:
        if conf is None:
            continue
        ano = int(conf.ano.iloc[0])
        iguais = ((conf.QT_APTOS == conf.QT_APTOS_BRASIL) & (conf.QT_ABSTENCAO == conf.QT_ABSTENCAO_BRASIL)).sum()
        print(f"{ano}: UFs com membro próprio iguais à mesma UF no _BRASIL (aptos e abstenção): {iguais} de {len(conf)}")
        dif = conf[(conf.QT_APTOS != conf.QT_APTOS_BRASIL) | (conf.QT_ABSTENCAO != conf.QT_ABSTENCAO_BRASIL)]
        if len(dif):
            print(dif.to_string())
    if SAIDA.exists():
        antigos = pd.read_csv(SAIDA, dtype={"cd_ibge": str})
        novos = pd.concat([antigos[~antigos.ano.isin(anos)], novos])
    novos = novos.sort_values(["ano", "uf", "cd_tse", "faixa_ordem"])
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    novos.to_csv(SAIDA, index=False, lineterminator="\n")
    print(f"gravado {SAIDA} · {len(novos):,} linhas")
    sys.exit(0 if conferir(novos) else 1)
