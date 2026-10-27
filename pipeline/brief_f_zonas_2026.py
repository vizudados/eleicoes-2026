"""Segundo turno de 2026 nas 34 cidades: resultados finais por zona da API TSE.

Uso: python -I -X utf8 pipeline/brief_f_zonas_2026.py [--somente-cache]
Reaproveita normalização e coleta retomável do exportador existente. Não escreve
em dados/pbi. A soma de cada cidade deve fechar nos nove campos municipais.
"""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exportar_2turno import API, COLUNAS, baixar_json, gravar_csv, gravar_json, normalizar
from extrair_secoes import CIDADES_T20

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "dados/bruto/tse/brief_f_zonas_2026"
SAIDA = RAIZ / "dados/saida/2turno"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--somente-cache", action="store_true")
    args = p.parse_args()
    config = json.loads((RAIZ / "dados/bruto/tse/2t2026/config.json").read_text(encoding="utf-8"))
    por_codigo = {(a["cd"].upper(), int(m["cd"])): m for a in config["abr"] for m in a["mu"]}
    tarefas = []
    for uf, cd, ibge, nome in CIDADES_T20:
        m = por_codigo[(uf, cd)]
        if int(m["cdi"]) != int(ibge):
            raise ValueError("Código IBGE difere do cadastro oficial")
        for zona in sorted(m["z"]):
            zona = str(zona).zfill(4)
            tarefas.append({"uf": uf, "cd_tse": cd, "cd_ibge": int(ibge), "cidade": nome + f" ({uf})",
                            "zona": int(zona), "url": f"{API}/dados/{uf.lower()}/{uf.lower()}{cd:05d}-z{zona}-c0001-e006258-u.json",
                            "cache": CACHE / uf.lower() / f"{cd:05d}_{zona}.json"})
    def coletar(t):
        b = baixar_json(t["url"], t["cache"], args.somente_cache)
        if int(b["ele"]) != 6258 or str(b["tf"]) != "s" or b["tpabr"] != "zona" or int(b["cdabr"]) != t["zona"]:
            raise ValueError("Resposta não final ou de outra zona: " + t["url"])
        if int(b["s"]["st"]) != int(b["s"]["ts"]):
            raise ValueError("Há seções não totalizadas: " + t["url"])
        linha = {"ano": 2026, "turno": 2, **{k: t[k] for k in ["uf", "cd_tse", "cd_ibge", "cidade", "zona"]},
                 **normalizar(b), "secoes": int(b["s"]["ts"]), "secoes_totalizadas": int(b["s"]["st"])}
        fonte = {k: t[k] for k in ["uf", "cd_tse", "cd_ibge", "zona", "url"]}
        fonte.update({"arquivo": t["cache"].relative_to(RAIZ).as_posix(),
                      "sha256": hashlib.sha256(t["cache"].read_bytes()).hexdigest(),
                      "atualizado_tse": b["dt"] + " " + b["ht"]})
        return linha, fonte
    with ThreadPoolExecutor(max_workers=8) as executor:
        resultados = list(executor.map(coletar, tarefas))
    zonas = pd.DataFrame([linha for linha, _ in resultados]).sort_values(["uf", "cd_ibge", "zona"])
    if zonas.duplicated(["cd_ibge", "zona"]).any():
        raise ValueError("Zona duplicada")
    municipio = pd.read_csv(RAIZ / "dados/pbi/municipio_2turno.csv")
    municipio = municipio[municipio.ano.eq(2026)].set_index("cd_ibge")
    provas = []
    for ibge, g in zonas.groupby("cd_ibge"):
        for c in COLUNAS:
            obtido, esperado = int(g[c].sum()), int(municipio.loc[ibge, c])
            provas.append({"ano": 2026, "nivel": "zonas API x município publicado", "cd_ibge": ibge,
                           "campo": c, "obtido": obtido, "esperado": esperado, "diferenca": obtido - esperado})
        # Outro controle: JSON municipal original, sem passar pelo CSV do painel.
        uf, cd = g.uf.iloc[0], int(g.cd_tse.iloc[0])
        bruto = json.loads((RAIZ / f"dados/bruto/tse/2t2026/{uf.lower()}/{cd:05d}.json").read_text(encoding="utf-8"))
        esperado_api = normalizar(bruto)
        for c in COLUNAS:
            obtido, esperado = int(g[c].sum()), esperado_api[c]
            provas.append({"ano": 2026, "nivel": "zonas API x município API", "cd_ibge": ibge,
                           "campo": c, "obtido": obtido, "esperado": esperado, "diferenca": obtido - esperado})
    provas = pd.DataFrame(provas)
    gravar_csv(provas, SAIDA / "brief_f_prova_zonas_2026.csv")
    if provas.diferenca.ne(0).any() or zonas.cd_ibge.nunique() != 34:
        raise ValueError("Totais por zona divergentes")
    atual = pd.read_csv(RAIZ / "dados/pbi/t20_locais.csv")
    if set(zip(atual.cod_ibge, atual.zona)) != set(zip(zonas.cd_ibge, zonas.zona)):
        raise ValueError("Zonas 2026 diferem das chaves da tela atual")
    gravar_csv(zonas, SAIDA / "t20_zonas_2turno_2026.csv")
    gravar_csv(pd.DataFrame([fonte for _, fonte in resultados]), SAIDA / "brief_f_fontes_zonas_2026.csv")
    # Prepara também uma tabela longa para o filtro, conservando a malha de cada ano.
    z22 = pd.read_csv(SAIDA / "t20_zonas_2turno_2022.csv")
    det22 = pd.read_csv(RAIZ / "dados/bruto/tse/detalhe_2022_BR.csv", sep=";", encoding="latin1")
    det22 = det22[det22.NR_TURNO.eq(2) & det22.CD_CARGO.eq(1)]
    det22 = det22.groupby(["SG_UF", "CD_MUNICIPIO", "NR_ZONA"], as_index=False).agg(
        aptos=("QT_APTOS", "sum"), comparecimento=("QT_COMPARECIMENTO", "sum"), abstencoes=("QT_ABSTENCOES", "sum"))
    det22 = det22.rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "cd_tse", "NR_ZONA": "zona"})
    z22 = z22.merge(det22, on=["uf", "cd_tse", "zona"], how="left", validate="one_to_one")
    if z22[["aptos", "comparecimento", "abstencoes"]].isna().any().any():
        raise ValueError("Zona 2022 sem detalhe")
    z22["demais"] = 0
    z26 = zonas.copy()
    # Quantidade de locais não consta do resultado unificado por zona: desconhecido em 2026.
    z26["locais"] = pd.NA
    z22["fonte"] = "TSE votação por seção + detalhe munzona"
    z26["fonte"] = "TSE resultado final por município e zona (API eleição 6258)"
    campos = ["ano", "turno", "uf", "cd_tse", "cd_ibge", "cidade", "zona", *COLUNAS, "secoes", "locais", "fonte"]
    combinado = pd.concat([z22[campos], z26[campos]], ignore_index=True).sort_values(["ano", "uf", "cd_ibge", "zona"])
    combinado["locais"] = combinado.locais.astype("Int64")
    gravar_csv(combinado, SAIDA / "t20_zonas_2turno_2022_2026.csv")
    gravar_json({"zonas_2026": len(zonas), "cidades": int(zonas.cd_ibge.nunique()), "provas": len(provas),
                 "diferencas": 0, "zonas_combinadas": len(combinado), "secoes_2026": int(zonas.secoes.sum()),
                 "locais_2026": "não informado pela API; vazio, sem reutilizar o número do primeiro turno"},
                SAIDA / "brief_f_resumo_zonas_2026.json")
    print(f"2026: {len(zonas)} zonas; {len(provas)} provas com diferença zero; combinado {len(combinado)} linhas", flush=True)


if __name__ == "__main__":
    main()
