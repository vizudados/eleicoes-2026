"""Conferência P2: pandas (junção/agrupamento) e caminho independente com csv/inteiros."""
from collections import defaultdict, Counter
import csv
import hashlib
import json
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
QA = RAIZ / "pbi/qa/p2"


def ler(nome):
    with (RAIZ / nome).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validar():
    QA.mkdir(parents=True, exist_ok=True)
    cmp = pd.read_csv(RAIZ / "dados/pbi/comparecimento_turno.csv")
    original = pd.read_csv(RAIZ / "dados/saida/2turno/comparecimento_turno.csv")
    pd.testing.assert_frame_equal(cmp, original)
    pre = pd.read_csv(RAIZ / "dados/pbi/comparecimento_ano.csv").set_index("ano")
    campos = ["aptos", "comparecimento", "abstencoes", "brancos", "nulos"]
    pd.testing.assert_frame_equal(cmp.query("turno==1 and abrangencia=='com_exterior'").set_index("ano")[campos],
                                  pre[campos], check_dtype=False)
    nac = cmp.query("ano==2026 and turno==2 and abrangencia=='com_exterior'").iloc[0]
    hist = pd.read_csv(RAIZ / "dados/pbi/pt_historico_brasil.csv")
    h26 = hist.query("ano==2026 and turno==2").iloc[0]
    dif = int(h26.votos_pt - h26.votos_adv)
    # Segundo caminho nacional, sem pandas ou reutilização de agregação.
    nc = next(r for r in ler("dados/pbi/comparecimento_turno.csv")
              if (r["ano"], r["turno"], r["abrangencia"]) == ("2026", "2", "com_exterior"))
    hc = next(r for r in ler("dados/pbi/pt_historico_brasil.csv") if (r["ano"], r["turno"]) == ("2026", "2"))
    assert int(nac.abstencoes) == int(nc["abstencoes"]) == 30_509_005
    assert dif == int(hc["votos_pt"])-int(hc["votos_adv"]) == 4_430_191
    assert int(nac.brancos+nac.nulos+nac.abstencoes) == sum(int(nc[k]) for k in ("brancos", "nulos", "abstencoes"))
    for ano, g in cmp.groupby("ano"):
        for turno, t in g.groupby("turno"):
            partes = t.set_index("abrangencia")
            assert (partes.loc["com_exterior", campos] == partes.loc["sem_exterior", campos]+partes.loc["exterior", campos]).all()
    social = pd.read_csv(RAIZ / "dados/pbi/municipio_social.csv", dtype={"cd_ibge": str})
    agregados = []
    grupos = defaultdict(list)
    for r in ler("dados/pbi/municipio_social.csv"):
        grupos[(r["lente"], int(r["degrau"]))].append(r["cd_ibge"])
    for modo, arquivo in (("Pré", "dados/pbi/municipio_ano.csv"),
                          ("Pós", "dados/saida/2turno/municipio_2turno_completo.csv")):
        dados = pd.read_csv(RAIZ / arquivo, dtype={"cd_ibge": str})
        dados = dados[dados.ano.isin([2022, 2026])]
        junto = social.merge(dados, on="cd_ibge", validate="many_to_many")
        soma = junto.groupby(["lente", "degrau", "ano"])[["pt", "adv", "validos", "aptos"]].sum()
        # Caminho independente: índice simples e soma inteira dos municípios do degrau.
        indice = {(int(r["ano"]), r["cd_ibge"]): r for r in ler(arquivo) if r["ano"] in ("2022", "2026")}
        for (lente, degrau, ano), r in soma.iterrows():
            rr = {c: sum(int(indice[(ano, cod)][c]) for cod in grupos[(lente, degrau)] if (ano, cod) in indice)
                  for c in ("pt", "adv", "validos", "aptos")}
            assert all(int(r[c]) == rr[c] for c in rr), (modo, lente, degrau, ano)
            agregados.append(dict(modo=modo, lente=lente, degrau=int(degrau), ano=int(ano), **rr,
                                  lula_pct=100*rr["pt"]/rr["validos"], flavio_pct=100*rr["adv"]/rr["validos"]))
    pd.DataFrame(agregados).to_csv(QA / "t24_quintos_conferidos.csv", index=False, lineterminator="\n")
    zonas = pd.read_csv(RAIZ / "dados/pbi/t20_zonas_turno.csv", dtype={"cd_ibge": str})
    origem_z = pd.read_csv(RAIZ / "dados/saida/2turno/t20_zonas_2turno_2022_2026.csv", dtype={"cd_ibge": str})
    pd.testing.assert_frame_equal(zonas[zonas.ano.isin([2022, 2026])][origem_z.columns], origem_z, check_dtype=False)
    m2 = pd.read_csv(RAIZ / "dados/saida/2turno/municipio_2turno_completo.csv", dtype={"cd_ibge": str}).set_index(["ano", "cd_ibge"])
    zc = defaultdict(lambda: Counter())
    for r in ler("dados/pbi/t20_zonas_turno.csv"):
        chave = (int(r["ano"]), r["cd_ibge"])
        for c in ("pt", "adv", "validos", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"):
            zc[chave][c] += int(r[c])
        zc[chave]["zonas"] += 1
        zc[chave]["lula"] += int(int(r["pt"]) > int(r["adv"]))
    zres = []
    for (ano, cod), g in zonas.groupby(["ano", "cd_ibge"]):
        rr = zc[(ano, cod)]
        for c in ("pt", "adv", "validos", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"):
            assert int(g[c].sum()) == rr[c] == int(m2.loc[(ano, cod), c]), (ano, cod, c)
        assert int((g.pt > g.adv).sum()) == rr["lula"]
        zres.append(dict(ano=int(ano), cd_ibge=cod, cidade=g.cidade.iloc[0], **rr))
    pd.DataFrame(zres).to_csv(QA / "t20_cidades_conferidas.csv", index=False, lineterminator="\n")
    # Ordem, viradas e histórico incompleto por zona: o mesmo cálculo por dois caminhos.
    z22 = zonas[zonas.ano == 2022].set_index(["cd_ibge", "zona"])
    z26 = zonas[zonas.ano == 2026].copy()
    z26["margem26"] = (z26.pt-z26.adv)/z26.validos
    z26 = z26.join(((z22.pt-z22.adv)/z22.validos).rename("margem22"), on=["cd_ibge", "zona"])
    z26["variacao"] = z26.margem26-z26.margem22
    z26["posicao"] = z26.sort_values(["variacao", "id"], na_position="last").groupby("cd_ibge").cumcount()+1
    zi = {(r["ano"], r["cd_ibge"], r["zona"]): r for r in ler("dados/pbi/t20_zonas_turno.csv")}
    for cod, g in z26.groupby("cd_ibge"):
        calc = []
        for r in g.itertuples():
            anterior = zi.get(("2022", cod, str(r.zona)))
            v = (r.pt-r.adv)/r.validos-(int(anterior["pt"])-int(anterior["adv"]))/int(anterior["validos"]) if anterior else None
            calc.append((v is None, v or 0, int(r.id), r.zona))
        ordem = [x[3] for x in sorted(calc)]
        assert ordem == g.sort_values("posicao").zona.tolist()
    z26.to_csv(QA / "t20_ordem_zonas_conferida.csv", index=False, lineterminator="\n")
    pesquisa = pd.read_csv(RAIZ / "dados/pbi/perfil_pesquisa_2turno.csv")
    assert len(pesquisa) == 8
    total = pesquisa[pesquisa.lente == "Todos"].set_index("candidato")
    assert total.loc["Lula", "percentual"] == 47 and total.loc["Flávio", "percentual"] == 48
    assert total.fatia.eq(1).all() and total.base_ponderada.eq(4050).all()
    assert pesquisa.groupby("categoria").fatia.nunique().eq(1).all()
    esperado = {"até 2 SM": (53, 41, 1911), "mais de 2 a 5 SM": (41, 55, 1438), "mais de 5 SM": (39, 57, 546)}
    for cat, (lu, fl, base) in esperado.items():
        g = pesquisa[pesquisa.categoria == cat]
        assert int(g[g.candidato == "Lula"].percentual.iloc[0]) == lu
        assert int(g[g.candidato == "Flávio"].percentual.iloc[0]) == fl
        assert abs(g.fatia.iloc[0]-base/4050) < 1e-12
    turnos2018 = Counter()
    for p in (RAIZ / "dados/bruto/tse").glob("secoes_2018_*.csv"):
        turnos2018.update(pd.read_csv(p, usecols=["NR_TURNO"]).NR_TURNO.value_counts().to_dict())
    assert set(turnos2018) == {1}
    # Mapa/ano: nacional com exterior versus municipal sem exterior em todos os segundos turnos.
    fatos = pd.read_csv(RAIZ / "dados/saida/2turno/municipio_2turno_completo.csv")
    # Confere também o arquivo efetivamente lido pelo modelo, que já contém os seis anos.
    pd.testing.assert_frame_equal(pd.read_csv(RAIZ / "dados/pbi/municipio_2turno.csv"), fatos)
    for ano, g in fatos.groupby("ano"):
        row = cmp.query("ano==@ano and turno==2 and abrangencia=='sem_exterior'").iloc[0]
        assert all(int(g[c].sum()) == int(row[c]) for c in campos)
    idade = pd.read_csv(RAIZ / "dados/pbi/abstencao_faixa_municipio.csv")
    idade_soma = idade.groupby(["ano", "faixa_ordem"])[["aptos", "abstencoes"]].sum()
    idade_contagem = defaultdict(Counter)
    for r in ler("dados/pbi/abstencao_faixa_municipio.csv"):
        k = (int(r["ano"]), int(r["faixa_ordem"]))
        for c in ("aptos", "abstencoes"):
            idade_contagem[k][c] += int(r[c])
    for k, r in idade_soma.iterrows():
        assert all(int(r[c]) == idade_contagem[k][c] for c in ("aptos", "abstencoes"))
    idade_soma.assign(taxa_pct=100*idade_soma.abstencoes/idade_soma.aptos).to_csv(
        QA/"t25_idade_primeiro_turno_conferida.csv", lineterminator="\n")
    hashes = json.loads((QA / "hashes_preservados.json").read_text(encoding="utf-8"))
    alterados = [p for p, h in hashes.items() if hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() != h]
    # A main integrou outras telas entre as fases; proteger os insumos deste P2,
    # não congelar arquivos de campanha pertencentes a outras frentes.
    insumos_p2 = {"municipio_2turno.csv", "municipio_ano.csv", "municipio_social.csv", "municipio.csv",
                  "t20_locais.csv", "t20_cidades.csv", "comparecimento_ano.csv", "abstencao_faixa_municipio.csv"}
    assert not [p for p in alterados if Path(p).name in insumos_p2], alterados
    resumo = dict(status="APROVADO", comparacoes_quintos=len(agregados), zonas_por_ano=zonas.ano.value_counts().to_dict(),
                  nacional_2026_segundo={**{k:int(nac[k]) for k in campos}, "diferenca":dif,
                                        "taxa_pct":100*nac.abstencoes/nac.aptos, "vezes":nac.abstencoes/dif,
                                        "nao_escolheram":int(nac.abstencoes+nac.brancos+nac.nulos)},
                  cache_2018_turnos=dict(turnos2018), insumos_p2_preexistentes_alterados=[],
                  outros_arquivos_alterados_desde_fase1=alterados)
    (QA / "conferencia_independente.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    validar()
