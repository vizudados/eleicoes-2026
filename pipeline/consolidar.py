"""Consolida o 1º turno de presidente por município (2006–2026) e cruza com o IBGE.

Lê `dados/bruto/tse/presidente_<ano>_BR.csv` e `dados/bruto/ibge/*.json`; grava em `dados/saida/`:
- `votos_municipio.csv`  um registro por município × ano: válidos, PT, adversário principal, demais
- `nacional.csv`         totais do país por ano e candidato (inclui o exterior)
- `municipios.csv`       cadastro: código TSE, código IBGE, nome, UF, região, população e renda do Censo 2022
- `depara_pendente.csv`  códigos do TSE sem par no IBGE (deve ficar vazio ou só com o exterior)

"Adversário principal" é o candidato mais votado no país fora o PT, em cada ano.

Uso: python -I -X utf8 pipeline/consolidar.py
"""
import json
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
TSE = RAIZ / "dados" / "bruto" / "tse"
IBGE = RAIZ / "dados" / "bruto" / "ibge"
SAIDA = RAIZ / "dados" / "saida"
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]

# Nomes que o TSE grafa diferente do IBGE (UF, nome normalizado do TSE) -> nome normalizado do IBGE.
GRAFIAS = {
    "GO|BOMJESUS": "GO|BOMJESUSDEGOIAS",  # Bom Jesus -> Bom Jesus de Goiás
    "MG|BARAODEMONTEALTO": "MG|BARAODOMONTEALTO",  # Barão De Monte Alto -> Barão do Monte Alto
    "MG|DONAEUSEBIA": "MG|DONAEUZEBIA",  # Dona Eusébia -> Dona Euzébia
    "MG|SAOTHOMEDASLETRAS": "MG|SAOTOMEDASLETRAS",  # São Thomé Das Letras -> São Tomé das Letras
    "MT|SANTOANTONIODOLEVERGER": "MT|SANTOANTONIODELEVERGER",  # Santo Antônio Do Leverger -> Santo Antônio de Leverger
    "PA|ELDORADODOSCARAJAS": "PA|ELDORADODOCARAJAS",  # Eldorado Dos Carajás -> Eldorado do Carajás
    "PR|MUNHOZDEMELLO": "PR|MUNHOZDEMELO",  # Munhoz De Mello -> Munhoz de Melo
    "RN|BOASAUDE": "RN|JANUARIOCICCO",  # Boa Saúde -> Januário Cicco
    "RO|ESPIGAODOOESTE": "RO|ESPIGAODOESTE",  # Espigão Do Oeste -> Espigão D'Oeste
    "RO|ALVORADADOOESTE": "RO|ALVORADADOESTE",  # Alvorada Do Oeste -> Alvorada D'Oeste
    "RR|SAOLUIZ": "RR|SAOLUIZDOANAUA",  # São Luiz -> São Luiz do Anauá
    "SE|AMPARODESAOFRANCISCO": "SE|AMPARODOSAOFRANCISCO",  # Amparo De São Francisco -> Amparo do São Francisco
    "SP|SAOLUISDOPARAITINGA": "SP|SAOLUIZDOPARAITINGA",  # São Luís Do Paraitinga -> São Luiz do Paraitinga
}


def normalizar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return "".join(c for c in sem_acento.upper() if c.isalnum())


def ler_tse(ano):
    df = pd.read_csv(TSE / f"presidente_{ano}_BR.csv", sep=";", encoding="latin1", dtype=str)
    col = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in df else "QT_VOTOS_NOMINAIS"
    df = df[df["NR_TURNO"] == "1"].copy()
    df["votos"] = df[col].astype(int)
    df["CD_MUNICIPIO"] = df["CD_MUNICIPIO"].astype(int)
    df["ano"] = ano
    return df[["ano", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_CANDIDATO", "NM_URNA_CANDIDATO",
               "SG_PARTIDO", "votos"]]


def ler_detalhe(ano):
    df = pd.read_csv(TSE / f"detalhe_{ano}_BR.csv", sep=";", encoding="latin1", dtype=str)
    df = df[df["NR_TURNO"] == "1"].copy()
    nulos = "QT_TOTAL_VOTOS_NULOS" if "QT_TOTAL_VOTOS_NULOS" in df else "QT_VOTOS_NULOS"
    saida = pd.DataFrame({"ano": ano, "SG_UF": df["SG_UF"], "CD_MUNICIPIO": df["CD_MUNICIPIO"].astype(int)})
    for destino, origem in (("aptos", "QT_APTOS"), ("comparecimento", "QT_COMPARECIMENTO"),
                            ("abstencoes", "QT_ABSTENCOES"), ("brancos", "QT_VOTOS_BRANCOS"), ("nulos", nulos)):
        saida[destino] = pd.to_numeric(df[origem], errors="coerce").fillna(0).astype("int64")
    return saida


def cadastro_ibge():
    locais = json.loads((IBGE / "municipios.json").read_text(encoding="utf-8"))
    linhas = []
    for m in locais:
        uf = (m.get("microrregiao") or {}).get("mesorregiao", {}).get("UF") or \
             m["regiao-imediata"]["regiao-intermediaria"]["UF"]
        linhas.append({"cd_ibge": str(m["id"]), "nome": m["nome"], "uf": uf["sigla"],
                       "regiao": uf["regiao"]["nome"]})
    cad = pd.DataFrame(linhas)

    def sidra(arquivo, campo):
        tabela = json.loads((IBGE / arquivo).read_text(encoding="utf-8"))[1:]
        return pd.DataFrame({"cd_ibge": [t["D1C"] for t in tabela],
                             campo: [float(t["V"]) if t["V"] not in ("-", "...", "X") else None for t in tabela]})

    cad = cad.merge(sidra("populacao_2022.json", "populacao"), on="cd_ibge", how="left")
    cad = cad.merge(sidra("renda_2022.json", "renda_pc"), on="cd_ibge", how="left")
    cad["chave"] = cad["uf"] + "|" + cad["nome"].map(normalizar)
    return cad


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    bruto = pd.concat([ler_tse(a) for a in ANOS], ignore_index=True)

    # Totais nacionais por candidato (com o exterior, como o TSE divulga).
    nacional = (bruto.groupby(["ano", "NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO"], as_index=False)["votos"]
                .sum().sort_values(["ano", "votos"], ascending=[True, False]))
    nacional["validos_ano"] = nacional.groupby("ano")["votos"].transform("sum")
    nacional["pct"] = nacional["votos"] / nacional["validos_ano"]
    nacional.to_csv(SAIDA / "nacional.csv", index=False)

    adversario = (nacional[nacional["SG_PARTIDO"] != "PT"].groupby("ano").head(1)
                  .set_index("ano")[["NR_CANDIDATO", "NM_URNA_CANDIDATO"]])
    pt = nacional[nacional["SG_PARTIDO"] == "PT"].set_index("ano")[["NR_CANDIDATO", "NM_URNA_CANDIDATO"]]

    # Fora do recorte municipal: exterior (ZZ) e voto em trânsito de 2010 (VT), que contam só no total do país.
    mun = bruto[~bruto["SG_UF"].isin(["ZZ", "VT"])].copy()
    mun["papel"] = "demais"
    for ano in ANOS:
        no_ano = mun["ano"] == ano
        mun.loc[no_ano & (mun["NR_CANDIDATO"] == pt.loc[ano, "NR_CANDIDATO"]), "papel"] = "pt"
        mun.loc[no_ano & (mun["NR_CANDIDATO"] == adversario.loc[ano, "NR_CANDIDATO"]), "papel"] = "adv"
    votos = (mun.pivot_table(index=["ano", "SG_UF", "CD_MUNICIPIO"], columns="papel", values="votos",
                             aggfunc="sum", fill_value=0).reset_index())
    votos["validos"] = votos[["pt", "adv", "demais"]].sum(axis=1)

    # De-para TSE -> IBGE pelo nome mais recente de cada código do TSE.
    nomes = (mun.sort_values("ano").groupby(["SG_UF", "CD_MUNICIPIO"], as_index=False).last()
             [["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"]])
    nomes["chave"] = nomes["SG_UF"] + "|" + nomes["NM_MUNICIPIO"].map(normalizar)
    nomes["chave"] = nomes["chave"].map(lambda c: GRAFIAS.get(c, c))
    cad = cadastro_ibge()
    depara = nomes.merge(cad, on="chave", how="left")
    pendente = depara[depara["cd_ibge"].isna()]
    pendente.to_csv(SAIDA / "depara_pendente.csv", index=False)

    depara = depara.dropna(subset=["cd_ibge"])
    depara = depara.rename(columns={"SG_UF": "uf_tse", "CD_MUNICIPIO": "cd_tse"})
    depara[["cd_tse", "cd_ibge", "nome", "uf", "regiao", "populacao", "renda_pc"]].to_csv(
        SAIDA / "municipios.csv", index=False)

    votos = votos.merge(depara[["cd_tse", "cd_ibge"]], left_on="CD_MUNICIPIO", right_on="cd_tse", how="left")
    votos = votos.rename(columns={"SG_UF": "uf"}).drop(columns=["CD_MUNICIPIO"])
    votos.to_csv(SAIDA / "votos_municipio.csv", index=False)

    # Comparecimento (detalhe da votação): aptos, comparecimento, abstenção, brancos e nulos do 1º turno.
    comp = pd.concat([ler_detalhe(a) for a in ANOS], ignore_index=True)
    comp.groupby("ano", as_index=False)[["aptos", "comparecimento", "abstencoes", "brancos", "nulos"]].sum().to_csv(
        SAIDA / "comparecimento_nacional.csv", index=False)
    comp_mun = comp[~comp["SG_UF"].isin(["ZZ", "VT"])]
    comp_mun = (comp_mun.groupby(["ano", "SG_UF", "CD_MUNICIPIO"], as_index=False)
                [["aptos", "comparecimento", "abstencoes", "brancos", "nulos"]].sum())
    comp_mun = comp_mun.merge(depara[["cd_tse", "cd_ibge"]], left_on="CD_MUNICIPIO", right_on="cd_tse", how="left")
    comp_mun = comp_mun.rename(columns={"SG_UF": "uf"}).drop(columns=["CD_MUNICIPIO"])
    comp_mun.to_csv(SAIDA / "comparecimento_municipio.csv", index=False)
    print(f"comparecimento: {len(comp_mun):,} linhas município × ano · sem IBGE: {comp_mun.cd_ibge.isna().sum()}")

    print(f"municípios no TSE: {len(nomes):,} · com par no IBGE: {len(depara):,} · pendentes: {len(pendente)}")
    print(f"IBGE sem par no TSE: {len(set(cad['cd_ibge']) - set(depara['cd_ibge'])):,}")
    print(pendente[["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"]].to_string(index=False))


if __name__ == "__main__":
    main()
