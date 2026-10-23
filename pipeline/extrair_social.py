"""Indicadores sociais por município para a tela "quem vota em quem" (pedido do Alisson, 23/10/2026: renda per capita,
escolaridade, Bolsa Família e IDH dos lugares).

Lê os brutos de `dados/bruto/social/` (baixados à parte, grandes, fora do git; ver FONTES.md lá) e o cadastro
`dados/saida/municipios.csv` (código TSE ↔ IBGE, população e renda do Censo 2022). Grava
`dados/saida/social_municipio.csv`, uma linha por município:

- eleitores, escol_medio: eleitorado de 2026 (perfil do eleitorado do TSE, julho de 2026) e a fatia com pelo menos o
  ensino médio completo (médio completo, superior incompleto ou completo) entre os que informaram a escolaridade;
- bf_familias, domicilios, bf_100dom: famílias pagas pelo Bolsa Família na folha de agosto de 2026 (Portal da
  Transparência; cada família conta uma vez, pelo NIS do responsável), domicílios particulares ocupados do Censo 2022
  e as famílias para cada 100 domicílios (uma casa pode ter mais de uma família: é uma aproximação, dita na tela);
- idhm: IDH municipal de 2010 (Atlas do Desenvolvimento Humano, pelo Ipeadata), o último medido por município.

Do arquivo do Bolsa Família só saem contagens por município; nenhum nome, NIS ou CPF é gravado.

    python -I -X utf8 pipeline/extrair_social.py
"""

import io
import json
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "dados" / "bruto" / "social"
SAIDA = RAIZ / "dados" / "saida"
PERFIL = BRUTO / "tse" / "perfil_eleitorado_2026.zip"
BOLSA = BRUTO / "bf" / "202608_NovoBolsaFamilia.zip"
COMPETENCIA = "202608"
MEDIO_OU_MAIS = {"ENSINO MÉDIO COMPLETO", "SUPERIOR INCOMPLETO", "SUPERIOR COMPLETO"}
# Nomes que o Portal da Transparência grafa diferente do IBGE (UF|nome normalizado do Portal -> do IBGE), do relatório
# de pendências deste script (folha de agosto de 2026); cada par conferido no cadastro do IBGE.
GRAFIAS_BF = {
    "BA|MUQUEMDESAOFRANCISCO": "BA|MUQUEMDOSAOFRANCISCO", "BA|SANTATERESINHA": "BA|SANTATEREZINHA",
    "CE|ITAPAGE": "CE|ITAPAJE", "MG|BARAODEMONTEALTO": "MG|BARAODOMONTEALTO", "MG|BRASOPOLIS": "MG|BRAZOPOLIS",
    "MG|DONAEUSEBIA": "MG|DONAEUZEBIA", "MG|SAOTHOMEDASLETRAS": "MG|SAOTOMEDASLETRAS", "MT|POXOREO": "MT|POXOREU",
    "MT|SANTOANTONIODOLEVERGER": "MT|SANTOANTONIODELEVERGER", "PA|ELDORADODOSCARAJAS": "PA|ELDORADODOCARAJAS",
    "PA|SANTAISABELDOPARA": "PA|SANTAIZABELDOPARA", "PB|SAODOMINGOSDEPOMBAL": "PB|SAODOMINGOS",
    "PB|SERIDO": "PB|SAOVICENTEDOSERIDO", "PE|BELEMDESAOFRANCISCO": "PE|BELEMDOSAOFRANCISCO",
    "PE|IGUARACI": "PE|IGUARACY", "PE|LAGOADOITAENGA": "PE|LAGOADEITAENGA",
    "PE|DISTRITOESTADUALDEFERNANDODENORONHA": "PE|FERNANDODENORONHA", "RJ|PARATI": "RJ|PARATY",
    "RJ|TRAJANODEMORAIS": "RJ|TRAJANODEMORAES", "RN|ACU": "RN|ASSU", "RN|ARES": "RN|AREZ",
    "RN|CAMPOGRANDEEXAUGUSTOSEVERO": "RN|CAMPOGRANDE", "RN|SERRACAIADAEXPRESIDENTEJUSCELINO": "RN|SERRACAIADA",
    "RR|SAOLUIZ": "RR|SAOLUIZDOANAUA", "SE|AMPARODESAOFRANCISCO": "SE|AMPARODOSAOFRANCISCO",
    "SE|GRACHOCARDOSO": "SE|GRACCHOCARDOSO", "SP|FLORINIA": "SP|FLORINEA",
    "SP|SAOLUISDOPARAITINGA": "SP|SAOLUIZDOPARAITINGA", "TO|FORTALEZADOTABOCAO": "TO|TABOCAO",
    "TO|COUTODEMAGALHAES": "TO|COUTOMAGALHAES", "TO|SAOVALERIODANATIVIDADE": "TO|SAOVALERIO",
}


def normalizar(nome):
    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    return "".join(c for c in sem_acento.upper() if c.isalnum())


def escolaridade(cad):
    partes = []
    with zipfile.ZipFile(PERFIL) as z:
        for nome in z.namelist():
            # só os 27 arquivos das UFs: o _BRASIL repete todos e o _ZZ é o exterior
            uf = nome.upper().removesuffix(".CSV").rsplit("_", 1)[-1]
            if not nome.lower().endswith(".csv") or len(uf) != 2 or uf == "ZZ":
                continue
            with z.open(nome) as bruto:
                leitor = pd.read_csv(io.TextIOWrapper(bruto, encoding="latin1"), sep=";", dtype=str,
                                     usecols=["CD_MUNICIPIO", "DS_GRAU_ESCOLARIDADE", "QT_ELEITORES"],
                                     chunksize=1_000_000)
                for bloco in leitor:
                    bloco["QT_ELEITORES"] = bloco["QT_ELEITORES"].astype(int)
                    partes.append(bloco.groupby(["CD_MUNICIPIO", "DS_GRAU_ESCOLARIDADE"], as_index=False)
                                  ["QT_ELEITORES"].sum())
    e = pd.concat(partes).groupby(["CD_MUNICIPIO", "DS_GRAU_ESCOLARIDADE"], as_index=False)["QT_ELEITORES"].sum()
    e["cd_tse"] = e["CD_MUNICIPIO"].astype(int)
    tot = e.groupby("cd_tse")["QT_ELEITORES"].sum().rename("eleitores")
    inf = e[e.DS_GRAU_ESCOLARIDADE != "NÃO INFORMADO"].groupby("cd_tse")["QT_ELEITORES"].sum().rename("informaram")
    med = e[e.DS_GRAU_ESCOLARIDADE.isin(MEDIO_OU_MAIS)].groupby("cd_tse")["QT_ELEITORES"].sum().rename("medio")
    r = pd.concat([tot, inf, med], axis=1).fillna(0).reset_index()
    r["escol_medio"] = r.medio / r.informaram
    print(f"escolaridade: {len(r)} municípios do TSE, {int(r.eleitores.sum()):,} eleitores; categorias: "
          + ", ".join(sorted(e.DS_GRAU_ESCOLARIDADE.unique())))
    r = r.merge(cad[["cd_tse", "cd_ibge"]], on="cd_tse", how="inner")
    return r[["cd_ibge", "eleitores", "escol_medio"]]


def bolsa_familia(cad):
    """Famílias pagas na competência: NIS do responsável distintos por município (UF + código SIAFI)."""
    pares, nomes, linhas = [], [], 0
    with zipfile.ZipFile(BOLSA) as z:
        nome = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(nome) as bruto:
            leitor = pd.read_csv(io.TextIOWrapper(bruto, encoding="latin1"), sep=";", dtype=str,
                                 usecols=["MÊS COMPETÊNCIA", "UF", "CÓDIGO MUNICÍPIO SIAFI", "NOME MUNICÍPIO",
                                          "NIS FAVORECIDO"], chunksize=2_000_000)
            for bloco in leitor:
                linhas += len(bloco)
                bloco = bloco[bloco["MÊS COMPETÊNCIA"] == COMPETENCIA]
                chave = (bloco["UF"] + "|" + bloco["CÓDIGO MUNICÍPIO SIAFI"]).astype("category")
                # o NIS (11 dígitos) vira inteiro só para contar famílias distintas; não sai daqui
                nis = pd.to_numeric(bloco["NIS FAVORECIDO"], errors="coerce").astype("Int64")
                pares.append(pd.DataFrame({"chave_siafi": chave.astype(str), "nis": nis}).drop_duplicates())
                nomes.append(pd.DataFrame({"chave_siafi": chave.astype(str), "nome_portal": bloco["NOME MUNICÍPIO"]})
                             .drop_duplicates("chave_siafi"))
    todos = pd.concat(pares, ignore_index=True).drop_duplicates()
    sem_nis = int(todos.nis.isna().sum())
    b = todos.groupby("chave_siafi", as_index=False).size().rename(columns={"size": "bf_familias"})
    b = b.merge(pd.concat(nomes).drop_duplicates("chave_siafi"), on="chave_siafi", how="left")
    b["uf"] = b.chave_siafi.str.split("|").str[0]
    del todos, pares
    print(f"bolsa família: {linhas:,} linhas no arquivo, {int(b.bf_familias.sum()):,} famílias em {len(b)} municípios"
          f" ({sem_nis} linha(s) sem NIS)")
    b["chave"] = b.uf + "|" + b.nome_portal.map(normalizar)
    b["chave"] = b.chave.map(lambda c: GRAFIAS_BF.get(c, c))
    c = cad.assign(chave=cad.uf + "|" + cad.nome.map(normalizar))
    r = b.merge(c[["chave", "cd_ibge"]], on="chave", how="left")
    pend = r[r.cd_ibge.isna()]
    if len(pend):
        print(f"bolsa família: {len(pend)} município(s) do Portal sem par no IBGE:")
        print(pend[["uf", "nome_portal", "bf_familias"]].to_string(index=False))
    dup = r.dropna(subset=["cd_ibge"]).cd_ibge.duplicated(keep=False)
    if dup.any():
        print("bolsa família: códigos IBGE repetidos:", r.dropna(subset=["cd_ibge"])[dup].to_string(index=False))
    return r.dropna(subset=["cd_ibge"])[["cd_ibge", "bf_familias"]], pend


def domicilios():
    d = json.loads((BRUTO / "domicilios_2022.json").read_text(encoding="utf-8"))[1:]
    return pd.DataFrame({"cd_ibge": [x["D1C"] for x in d], "domicilios": [int(x["V"]) for x in d]})


def idhm():
    v = json.loads((BRUTO / "idhm_ipea.json").read_text(encoding="utf-8"))["value"]
    m = [x for x in v if x["NIVNOME"] == "Municípios" and x["VALDATA"].startswith("2010")]
    return pd.DataFrame({"cd_ibge": [x["TERCODIGO"] for x in m], "idhm": [x["VALVALOR"] for x in m]})


def main():
    cad = pd.read_csv(SAIDA / "municipios.csv", dtype={"cd_ibge": str})
    cad["cd_tse"] = cad.cd_tse.astype(int)
    esc = escolaridade(cad)
    bf, pend = bolsa_familia(cad)
    r = (cad[["cd_ibge", "nome", "uf", "populacao", "renda_pc"]]
         .merge(esc, on="cd_ibge", how="left")
         .merge(bf, on="cd_ibge", how="left")
         .merge(domicilios(), on="cd_ibge", how="left")
         .merge(idhm(), on="cd_ibge", how="left"))
    r["bf_100dom"] = 100 * r.bf_familias / r.domicilios
    for col, rot in (("escol_medio", "escolaridade"), ("bf_familias", "Bolsa Família"), ("domicilios", "domicílios"),
                     ("idhm", "IDHM 2010"), ("renda_pc", "renda")):
        faltam = r[r[col].isna()]
        if len(faltam):
            print(f"sem {rot}: {len(faltam)} — " + ", ".join((faltam.nome + "/" + faltam.uf).head(12)))
    r.sort_values("cd_ibge").to_csv(SAIDA / "social_municipio.csv", index=False, float_format="%.6g")
    print(f"gravado {SAIDA / 'social_municipio.csv'}: {len(r)} municípios")
    return 1 if len(pend) else 0


if __name__ == "__main__":
    sys.exit(main())
