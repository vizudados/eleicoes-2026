"""Exporta somente os três CSVs novos do brief P2; não opera o Desktop.

As fontes conferidas do brief F permanecem intactas. Não há perfil por idade
do segundo turno. A coleta presidencial de 2018 é feita por coletar_p2_zonas_2018.py.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "dados/pbi"
QA = RAIZ / "pbi/qa/p2"


def exportar():
    comparecimento = pd.read_csv(RAIZ / "dados/saida/2turno/comparecimento_turno.csv")
    assert len(comparecimento) == 36
    assert not comparecimento.duplicated(["ano", "turno", "abrangencia"]).any()
    zonas = pd.read_csv(RAIZ / "dados/saida/2turno/t20_zonas_2turno_2022_2026.csv",
                        dtype={"cd_ibge": str})
    locais = pd.read_csv(SAIDA / "t20_locais.csv", dtype={"cod_ibge": str})
    zonas = zonas.merge(locais[["cod_ibge", "zona", "id"]],
                        left_on=["cd_ibge", "zona"], right_on=["cod_ibge", "zona"],
                        how="left", validate="many_to_one")
    assert len(zonas) == 639
    assert zonas.loc[zonas.ano == 2026, "id"].notna().all()
    assert not zonas.duplicated(["ano", "cd_ibge", "zona"]).any()
    zonas = zonas.drop(columns="cod_ibge")
    # Zona histórica fora do desenho atual conserva seus votos e entra na contagem de 2022.
    zonas["id"] = zonas.id.astype("Int64")
    historico = pd.read_csv(SAIDA / "t20_zonas_2turno_2018.csv", dtype={"cd_ibge": str, "id": "Int64"})
    assert historico.ano.eq(2018).all() and historico.turno.eq(2).all()
    assert list(historico.columns) == list(zonas.columns)
    zonas = pd.concat([zonas, historico], ignore_index=True)
    assert not zonas.duplicated(["ano", "cd_ibge", "zona"]).any()
    pesquisa = pd.read_csv(RAIZ / "dados/bruto/pesquisas/datafolha_2turno_renda.csv", sep=";")
    ordem = {"até 2 SM": 1, "mais de 2 a 5 SM": 2, "mais de 5 SM": 3}
    perfil = pesquisa.assign(
        turno=2, lente="Renda", categoria_ordem=pesquisa.categoria.map(ordem),
        campo="23–24/10/2026 · BR-09540/2026",
        fatia=pesquisa.base_ponderada / pesquisa.amostra_total)
    perfil = perfil[["instituto", "divulgacao", "campo", "turno", "candidato", "lente", "categoria",
                     "categoria_ordem", "percentual", "fatia", "base_ponderada", "amostra_total", "fonte_url"]]
    assert len(perfil) == 6 and perfil.categoria_ordem.notna().all()
    assert not perfil.duplicated(["candidato", "categoria"]).any()
    # PDF oficial, p. 27 (impressa 8/17), pergunta 2 estimulada, coluna Total.
    # Campo 23–24/10, BR-09540/2026: base total, não votos válidos.
    # SHA-256 do PDF: 41f91c3495dc96da9e51e130fcd74b8078e7c4a31d4bda894b400b847b70c1d0.
    totais = []
    for candidato, percentual in (("Lula", 47), ("Flávio", 48)):
        r = perfil[perfil.candidato == candidato].iloc[0].to_dict()
        r.update(lente="Todos", categoria="todos os eleitores", categoria_ordem=4,
                 percentual=percentual, fatia=1.0, base_ponderada=4050)
        totais.append(r)
    perfil = pd.concat([perfil, pd.DataFrame(totais)], ignore_index=True)
    arquivos = {"comparecimento_turno.csv": comparecimento,
                "t20_zonas_turno.csv": zonas, "perfil_pesquisa_2turno.csv": perfil}
    QA.mkdir(parents=True, exist_ok=True)
    manifesto = []
    for nome, tabela in arquivos.items():
        destino = SAIDA / nome
        tabela.to_csv(destino, index=False, encoding="utf-8", lineterminator="\n")
        manifesto.append({"arquivo": f"dados/pbi/{nome}", "linhas": len(tabela),
                          "sha256": hashlib.sha256(destino.read_bytes()).hexdigest()})
    (QA / "arquivos_dados.json").write_text(json.dumps(manifesto, indent=2, ensure_ascii=False)+"\n",
                                             encoding="utf-8")
    print(json.dumps(manifesto, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    exportar()
