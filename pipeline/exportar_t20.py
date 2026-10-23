"""Exporta dados/pbi/t20_locais.csv: os 112 locais de votação de Contagem (MG) no 1º turno de 2026, um por linha, com
os votos de 2026 e os de 2022 e 2018 do mesmo local (zona + número), para a tela 20 · Escola. Dono: tela 20.

Por que um arquivo próprio: em dados/pbi/local_contagem.csv o cruzamento com as posições do mapa casa só por zona e
número, e o local 1350 da zona 91 tem dois nomes em 2026 (Centro Social Urbano e Instituto Educacional Aquarela): as
linhas desse número saem em dobro nos três anos. Aqui o 2026 casa com a posição por zona, número e nome (como o
pipeline/montar_dados_mockup.py, o oráculo), e 2022 e 2018 entram pela soma das seções do mesmo zona + número.

Colunas: id (1…112), local (nome legível; repetido ganha o número), nome_tse, bairro, endereco, zona, numero, secoes,
pt_2026, adv_2026, validos_2026, pt_2022, adv_2022, validos_2022, pt_2018, adv_2018, validos_2018 (vazio quando o local
não existia), px, py (posição no mapa da tela, % da largura e da altura de docs/midia/mapas/escolas-contagem.png).

Entradas: dados/saida/locais_contagem.csv e dados/saida/escolas_posicao.csv.
Uso: python -I -X utf8 pipeline/exportar_t20.py
"""
import re
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "dados" / "saida"
DESTINO = RAIZ / "dados" / "pbi" / "t20_locais.csv"
SIGLAS = {"CAIC", "CEDETEM", "SENAI", "CEFET", "CEMAR", "CEMEI", "CEI", "CSU", "CEC", "NEEC", "FUNEC", "PUC", "SESI",
          "JK", "UMEI", "EM", "EE", "II", "III", "IV", "VC-03"}
MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "d'agua"}
ABREVIA = {"EST.": "Est.", "PROF.": "Prof.", "PROFª": "Profª", "DR": "Dr.", "ESP.": "Esp.", "CONJ.": "Conj.",
           "E.": "E.", "M.": "M.", "A.": "A.", "NSTITUTO": "Instituto"}


def titulo(texto) -> str:
    """Nome do TSE (maiúsculas) → nome legível: siglas ficam, conectivos em minúscula, resto com inicial maiúscula."""
    if not isinstance(texto, str) or not texto.strip():
        return ""
    palavras = re.sub(r"\s+", " ", texto.strip()).split(" ")
    saida = []
    for i, p in enumerate(palavras):
        nucleo = p.strip("()")
        if nucleo in ABREVIA:
            q = p.replace(nucleo, ABREVIA[nucleo])
        elif nucleo in SIGLAS or re.search(r"\d", nucleo) or "/" in nucleo:
            q = p
        elif i > 0 and p.lower() in MINUSCULAS:
            q = p.lower()
        else:
            # inicial maiúscula em cada parte separada por hífen, parêntese ou apóstrofo
            q = re.sub(r"(^|[-(/'])([^\W\d_])", lambda m: m.group(1) + m.group(2).upper(), p.lower())
            q = re.sub(r"-(i{1,3}|iv)\b", lambda m: "-" + m.group(1).upper(), q)
        saida.append(q)
    return " ".join(saida).replace("d'agua", "d'Água").replace("D'agua", "d'Água")


def main():
    loc = pd.read_csv(SAIDA / "locais_contagem.csv")
    pos = pd.read_csv(SAIDA / "escolas_posicao.csv")
    chave = ["NR_ZONA", "NR_LOCAL_VOTACAO"]
    antes = (loc[loc.ano < 2026].groupby(["ano"] + chave)[["pt", "adv", "validos"]].sum().unstack("ano"))
    antes.columns = [f"{c}_{a}" for c, a in antes.columns]
    a26 = loc[loc.ano == 2026].rename(columns={"pt": "pt_2026", "adv": "adv_2026", "validos": "validos_2026"})
    a26 = a26.merge(antes, left_on=chave, right_index=True, how="left")
    a26 = a26.merge(pos[chave + ["NM_LOCAL_VOTACAO", "px", "py"]], on=chave + ["NM_LOCAL_VOTACAO"], how="left")
    if len(a26) != (loc.ano == 2026).sum():
        raise SystemExit("o cruzamento com as posições duplicou linhas")
    a26 = a26.sort_values(chave + ["NM_LOCAL_VOTACAO"]).reset_index(drop=True)
    a26["local"] = a26.NM_LOCAL_VOTACAO.map(titulo)
    repetidos = a26.local.duplicated(keep=False)
    a26.loc[repetidos, "local"] = a26.loc[repetidos].apply(lambda r: f"{r.local} (local {r.NR_LOCAL_VOTACAO})", axis=1)
    a26["bairro"] = a26.bairro.map(titulo)
    a26["endereco"] = a26.DS_LOCAL_VOTACAO_ENDERECO.map(titulo)
    a26["id"] = range(1, len(a26) + 1)
    saida = a26.rename(columns={"NM_LOCAL_VOTACAO": "nome_tse", "NR_ZONA": "zona", "NR_LOCAL_VOTACAO": "numero"})[
        ["id", "local", "nome_tse", "bairro", "endereco", "zona", "numero", "secoes", "pt_2026", "adv_2026",
         "validos_2026", "pt_2022", "adv_2022", "validos_2022", "pt_2018", "adv_2018", "validos_2018", "px", "py"]]
    for c in ("pt_2022", "adv_2022", "validos_2022", "pt_2018", "adv_2018", "validos_2018"):
        saida[c] = saida[c].astype("Int64")
    saida["px"] = saida.px.round(2)
    saida["py"] = saida.py.round(2)
    saida.to_csv(DESTINO, index=False, encoding="utf-8", lineterminator="\n")
    m26 = (saida.pt_2026 - saida.adv_2026) / saida.validos_2026
    m22 = (saida.pt_2022 - saida.adv_2022) / saida.validos_2022
    print(f"t20_locais.csv · {len(saida)} locais · Lula à frente em 2026: {(m26 > 0).sum()} · em 2022 (mesmo local): "
          f"{(m22 > 0).sum()} · viraram: {((m22 > 0) & (m26 < 0)).sum()} · sem posição: {saida.px.isna().sum()}")


if __name__ == "__main__":
    main()
