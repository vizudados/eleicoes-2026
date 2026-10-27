"""Exporta a inferência aprovada da T16 para a tabela desconectada do painel.

CSV de origem: UTF-8 BOM, ponto e vírgula, vírgula decimal. CSV do modelo:
UTF-8, vírgula, ponto decimal (fxCsv/en-US). Não ajusta modelos nem publica.
As somas e razões usam as amostras pareadas: nunca somam limites marginais.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "dados/saida/2turno/inferencia_t16"
SAIDA = RAIZ / "dados/pbi/t16_urna.csv"
QA = RAIZ / "pbi/qa/p4"
DESTINOS = ["Lula", "Flávio", "Branco ou nulo", "Não votou"]
RESIDUAL = "Branco, nulo ou não votou"


def ler(nome):
    return pd.read_csv(ENTRADA / nome, sep=";", decimal=",")


def resumo(amostras, base):
    media = float(np.mean(amostras))
    inferior, superior = np.quantile(amostras, [.025, .975])
    return dict(media=media / base * 100, inferior=inferior / base * 100,
                superior=superior / base * 100, votos=media,
                inferior_votos=inferior, superior_votos=superior, base=base)


def exportar():
    diagnostico = json.loads((ENTRADA / "diagnostico_bayes_slice_principal_seis.json").read_text(encoding="utf-8-sig"))
    if not diagnostico["convergiu"] or diagnostico["rhat_max"] >= 1.01:
        raise ValueError("Amostragem bayesiana não aprovada")
    if min(diagnostico["ess_bulk_min"], diagnostico["ess_tail_min"]) <= 400:
        raise ValueError("Amostragem sem ESS suficiente")
    linhas = []
    fontes = ["diagnostico_bayes_slice_principal_seis.json", "base_municipal.csv",
              "confronto_pesquisas_resumo.csv", "outros_e_comparecimento.csv"]
    for execucao, metodo in [("bayes_slice_principal_seis", "Bayes"),
                             ("restrito_principal_seis", "Restrito")]:
        fontes += [execucao + ".csv", "amostras_" + execucao + ".npz"]
        tabela = ler(execucao + ".csv").query("area == 'Brasil'")
        with np.load(ENTRADA / ("amostras_" + execucao + ".npz"), allow_pickle=False) as z:
            fluxos, nomes = z["fluxos"].copy(), z["nomes"].tolist()
        if fluxos.shape[1:] != (6, 4) or not np.isfinite(fluxos).all() or fluxos.min() < -1e-5:
            raise ValueError("Amostras incompatíveis com a especificação de seis origens")
        for i, origem in enumerate(nomes):
            origem_csv = tabela[tabela.origem.eq(origem)].set_index("destino")
            base = int(origem_csv.base_origem_votos.iloc[0])
            np.testing.assert_allclose(fluxos[:, i].sum(axis=1), base, rtol=0, atol=.01)
            for j, destino in enumerate(DESTINOS):
                r = origem_csv.loc[destino]
                calc = resumo(fluxos[:, i, j], base)
                # Caminho 1: CSV publicado. Caminho 2: amostras pareadas originais.
                for campo, coluna in [("media", "media_pct"), ("inferior", "inferior_95_pct"),
                                       ("superior", "superior_95_pct"), ("votos", "media_votos")]:
                    # CSV restrito conserva duas casas em votos (até 0,005 de arredondamento).
                    np.testing.assert_allclose(calc[campo], r[coluna], rtol=0,
                                               atol=.01 if campo == "votos" else .002)
                linhas.append(dict(serie="Fluxo", origem=origem, destino=destino, metodo=metodo,
                                   tipo_intervalo=r.tipo_intervalo, **calc))
            linhas.append(dict(serie="Fluxo", origem=origem, destino=RESIDUAL, metodo=metodo,
                               tipo_intervalo=origem_csv.tipo_intervalo.iloc[0],
                               **resumo(fluxos[:, i, 2:].sum(axis=1), base)))
            if origem == "Não votou":
                votantes = fluxos[:, i, :3].sum(axis=1)
                for j, destino in enumerate(DESTINOS[:3]):
                    # Condicionamento ANTES dos quantis, incluindo branco/nulo no denominador.
                    taxa = fluxos[:, i, j] / votantes * 100
                    inferior, superior = np.quantile(taxa, [.025, .975])
                    linhas.append(dict(serie="Entre quem foi votar", origem=origem, destino=destino,
                                       metodo=metodo, media=taxa.mean(), inferior=inferior, superior=superior,
                                       votos=fluxos[:, i, j].mean(), base=votantes.mean(),
                                       inferior_votos=np.quantile(fluxos[:, i, j], .025),
                                       superior_votos=np.quantile(fluxos[:, i, j], .975),
                                       tipo_intervalo=origem_csv.tipo_intervalo.iloc[0]))
    pesquisas = ler("confronto_pesquisas_resumo.csv")
    pesquisas = pesquisas[pesquisas.origem.isin(["Cury + Renan + Caiado", "Não votou"])]
    for r in pesquisas.itertuples():
        linhas.append(dict(serie="Pesquisa", origem=r.origem, destino=r.destino, metodo="Pesquisa",
                           media=r.media_pesquisas_pct, inferior=r.minimo_instituto_pct,
                           superior=r.maximo_instituto_pct, base=r.institutos,
                           tipo_intervalo="mínimo e máximo entre institutos; não é IC"))
    base = ler("base_municipal.csv")
    if base.cd_ibge.duplicated().any():
        raise ValueError("Município repetido")
    resumo_comp = ler("outros_e_comparecimento.csv")
    saldo = resumo_comp[(resumo_comp.execucao == "bayes_slice_principal_seis") &
                        (resumo_comp.medida == "Saldo de comparecimento modelado")].iloc[0]
    metadados = [("Unidades eleitorais", len(base), len(base), len(base)),
                 ("R-hat máximo", diagnostico["rhat_max"], diagnostico["rhat_max"], diagnostico["rhat_max"]),
                 ("Saldo observado", (base.comparecimento_2 - base.comparecimento_1).sum(), None, None),
                 ("Saldo modelado", saldo.media_votos, saldo.inferior_95_votos, saldo.superior_95_votos)]
    for nome, media, inferior, superior in metadados:
        linhas.append(dict(serie="Diagnóstico", origem="Brasil", destino=nome, metodo="Diagnóstico",
                           media=media, inferior=inferior, superior=superior,
                           tipo_intervalo="credibilidade_modelo_95" if nome == "Saldo modelado" else "observado ou diagnóstico"))
    saida = pd.DataFrame(linhas)
    if saida.duplicated(["serie", "origem", "destino", "metodo"]).any():
        raise ValueError("Chave repetida")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    saida.to_csv(SAIDA, index=False, encoding="utf-8", float_format="%.10f", lineterminator="\n")
    QA.mkdir(parents=True, exist_ok=True)
    manifesto = {"saida": str(SAIDA.relative_to(RAIZ)), "linhas": len(saida),
                 "fontes_sha256": {f: hashlib.sha256((ENTRADA / f).read_bytes()).hexdigest() for f in fontes},
                 "saida_sha256": hashlib.sha256(SAIDA.read_bytes()).hexdigest(),
                 "nota": "NPZ locais só para somas/condicionamento antes dos quantis; o modelo lê somente o CSV."}
    (QA / "t16_manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"T16: {len(saida)} linhas exportadas; CSV e amostras conferidos em todas as 48 células nacionais.")


if __name__ == "__main__":
    exportar()
