"""Exporta dados/pbi/t19_lado.csv: de que lado cada município ficou em 2022 e em 2026 (a segmentação "Virou?" da tela
19 · Explorador). Dono: tela 19.

Um município por linha (os 5.571 do IBGE), com o lado de cada eleição pela margem do PT (votos do PT − votos do
adversário principal): "Virou para Flávio" (Lula à frente em 2022, Flávio em 2026), "Lula nas duas", "Bolsonaro nas duas"
(Jair em 2022, Flávio em 2026) e "Empate ou cidade nova" (empate exato num dos anos ou município sem 2022). A conta é a
mesma das medidas da tela (margem > 0 = PT à frente); o CSV só guarda o rótulo, para a segmentação ter uma coluna.

Entradas: dados/pbi/municipio.csv e dados/pbi/municipio_ano.csv (pipeline/exportar_pbi.py).
Uso: python -I -X utf8 pipeline/exportar_t19.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PBI = RAIZ / "dados" / "pbi"
ROTULOS = [("Virou para Flávio", 1), ("Lula nas duas", 2), ("Bolsonaro nas duas", 3), ("Empate ou cidade nova", 4)]


def lado(pt, adv):
    if pd.isna(pt) or pd.isna(adv):
        return None
    return "L" if pt > adv else ("A" if pt < adv else "E")


def rotulo(l22, l26):
    if l22 == "L" and l26 == "A":
        return "Virou para Flávio"
    if l22 == "A" and l26 == "L":
        return "Virou para Lula"
    if l22 == "L" and l26 == "L":
        return "Lula nas duas"
    if l22 == "A" and l26 == "A":
        return "Bolsonaro nas duas"
    return "Empate ou cidade nova"


def main():
    mun = pd.read_csv(PBI / "municipio.csv", dtype={"cd_ibge": str})
    ano = pd.read_csv(PBI / "municipio_ano.csv", dtype={"cd_ibge": str})
    largo = ano[ano.ano.isin([2022, 2026])].pivot_table(index="cd_ibge", columns="ano", values=["pt", "adv"],
                                                         aggfunc="sum")
    largo.columns = [f"{c}{a}" for c, a in largo.columns]
    d = mun[["cd_ibge"]].set_index("cd_ibge").join(largo)
    d["lado"] = [rotulo(lado(a, b), lado(c, e)) for a, b, c, e in zip(d.pt2022, d.adv2022, d.pt2026, d.adv2026)]
    ordem = dict(ROTULOS)
    ordem["Virou para Lula"] = 0
    d["lado_ordem"] = d.lado.map(ordem)
    saida = d.reset_index()[["cd_ibge", "lado", "lado_ordem"]]
    saida.to_csv(PBI / "t19_lado.csv", index=False, encoding="utf-8", lineterminator="\n")
    print(f"t19_lado.csv · {len(saida)} linhas")
    print(saida.lado.value_counts().to_string())


if __name__ == "__main__":
    main()
