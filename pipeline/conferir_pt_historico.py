"""Segunda conferência da série histórica, sem importar o exportador/pandas.

Uso: python -I -X utf8 pipeline/conferir_pt_historico.py
1989 é relido dos ZIP; 1994, das células HTML por regex independente;
1998–2026/1, linha a linha dos CSV; 2026/2, dos JSON estaduais do TSE.
"""
import csv
import hashlib
import html
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "dados/bruto/tse/historico_pt"
SAIDA = RAIZ / "dados/saida/pt_historico"
ANOS = [1989, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]
SOMAS = ["votos_pt", "votos_adv", "validos", "comparecimento", "aptos"]
COLUNAS = ["ano", "turno", "uf", "candidato_pt", "votos_pt", "adversario", "partido_adversario", "votos_adv", "validos", "comparecimento", "aptos"]
UFS = "AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO ZZ".split()
VT = dict(zip(range(99901, 99928), "SP MG RJ RS BA PR CE PE SC GO MA PB PA ES PI RN AL MT MS DF SE AM RO AC AP RR TO".split()))


def csv_linhas(caminho, sep=",", encoding="utf-8"):
    with caminho.open(encoding=encoding, newline="") as f:
        yield from csv.DictReader(f, delimiter=sep)


def numero(s):
    return int(s.strip().replace(".", ""))


def linhas_html(caminho):
    texto = caminho.read_text(encoding="utf-8")
    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", texto, re.I | re.S):
        celulas = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)
        yield [" ".join(html.unescape(re.sub("<[^>]+>", " ", c)).split()) for c in celulas]


def main():
    votos = defaultdict(Counter)
    partidos = {}
    detalhe = defaultdict(Counter)
    total_campos = 0
    for tipo in ["votacao_candidato_uf", "detalhe_votacao_uf"]:
        with zipfile.ZipFile(CACHE / f"{tipo}_1989.zip") as z:
            nome = next(n for n in z.namelist() if n.lower().endswith(".txt"))
            with z.open(nome) as f:
                for r in csv.reader(io.TextIOWrapper(f, encoding="latin1", newline=""), delimiter=";"):
                    if not r:
                        continue
                    chave = (1989, int(r[3]), r[5])
                    if tipo.startswith("votacao"):
                        votos[chave][int(r[8])] += int(r[25])
                        partidos[(1989, int(r[8]))] = r[20]
                    else:
                        detalhe[chave]["aptos"] += int(r[9])
                        detalhe[chave]["comparecimento"] += int(r[10])
    for uf in UFS:
        caminho = CACHE / "1994" / f"{uf}_presidente.html"
        chave = (1994, 1, uf)
        for r in linhas_html(caminho):
            if len(r) >= 3 and re.match(r"^\d+\s", r[0]):
                cand = int(r[0].split()[0])
                votos[chave][cand] += numero(r[2])
                partidos[(1994, cand)] = r[1]
            if len(r) >= 3 and r[0].startswith("Total de votos apurados"):
                detalhe[chave]["comparecimento"] = numero(r[1])
                detalhe[chave]["aptos"] = numero(re.search(r"de\s+([\d.]+)\s+eleitores", r[2])[1])
            if len(r) >= 2 and r[0].startswith("Total de votos válidos"):
                detalhe[chave]["validos"] = numero(r[1])
    for ano in ANOS[2:]:
        origem = RAIZ / f"dados/bruto/tse/presidente_{ano}_BR.csv"
        for r in csv_linhas(origem, ";", "latin1"):
            if r["CD_CARGO"] != "1":
                continue
            uf = VT[int(r["CD_MUNICIPIO"])] if r["SG_UF"] == "VT" else r["SG_UF"]
            chave = (ano, int(r["NR_TURNO"]), uf)
            cand = int(r["NR_CANDIDATO"])
            campo = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in r else "QT_VOTOS_NOMINAIS"
            votos[chave][cand] += int(r[campo])
            partidos[(ano, cand)] = r["SG_PARTIDO"]
        for r in csv_linhas(RAIZ / f"dados/bruto/tse/detalhe_{ano}_BR.csv", ";", "latin1"):
            if r["CD_CARGO"] != "1":
                continue
            uf = VT[int(r["CD_MUNICIPIO"])] if r["SG_UF"] == "VT" else r["SG_UF"]
            chave = (ano, int(r["NR_TURNO"]), uf)
            for campo, origem in [("aptos", "QT_APTOS"), ("comparecimento", "QT_COMPARECIMENTO"), ("validos", "QT_TOTAL_VOTOS_VALIDOS")]:
                detalhe[chave][campo] += int(r[origem])
    for uf in UFS:
        bruto = json.loads((RAIZ / "dados/bruto/tse/2t2026/totais" / (uf.lower() + ".json")).read_text(encoding="utf-8"))
        chave = (2026, 2, uf)
        for agr in bruto["carg"][0]["agr"]:
            for par in agr["par"]:
                for c in par["cand"]:
                    votos[chave][int(c["n"])] = int(c["vap"])
                    partidos[(2026, int(c["n"]))] = par["sg"]
        detalhe[chave] = Counter({"aptos": int(bruto["e"]["te"]), "comparecimento": int(bruto["e"]["c"]), "validos": int(bruto["v"]["vv"])})
    for chave in votos:
        if chave[0] == 1989:
            detalhe[chave]["validos"] = sum(votos[chave].values())
        assert sum(votos[chave].values()) == detalhe[chave]["validos"], chave
    candidatos_nacionais = defaultdict(Counter)
    for (ano, turno, uf), contagem in votos.items():
        candidatos_nacionais[(ano, turno)].update(contagem)
    exportadas = list(csv_linhas(RAIZ / "dados/pbi/pt_historico_uf.csv"))
    assert len(exportadas) == 504 and list(exportadas[0]) == COLUNAS
    totais = defaultdict(Counter)
    lideres = {}
    for r in exportadas:
        ano, turno, uf = int(r["ano"]), int(r["turno"]), r["uf"]
        chave = ano, turno, uf
        n = candidatos_nacionais[(ano, turno)]
        pt = max((c for c in n if partidos[(ano, c)] == "PT"), key=n.get)
        adv = max((c for c in n if partidos[(ano, c)] != "PT"), key=n.get)
        esperado = {"votos_pt": votos[chave][pt], "votos_adv": votos[chave][adv], **detalhe[chave]}
        for campo in SOMAS:
            assert int(r[campo]) == esperado[campo], (chave, campo, r[campo], esperado[campo])
            totais[(ano, turno)][campo] += int(r[campo])
            total_campos += 1
        assert r["partido_adversario"] == partidos[(ano, adv)]
        vencedor = max(votos[chave], key=votos[chave].get)
        lideres[chave] = partidos[(ano, vencedor)]
    br = list(csv_linhas(RAIZ / "dados/pbi/pt_historico_brasil.csv"))
    assert len(br) == 18 and list(br[0]) == COLUNAS
    for r in br:
        chave = int(r["ano"]), int(r["turno"])
        assert r["uf"] == "BR"
        for campo in SOMAS:
            assert int(r[campo]) == totais[chave][campo]
            total_campos += 1
    pub_candidatos = {(int(r["ano"]), int(r["turno"]), int(r["numero"])): int(r["votos"]) for r in csv_linhas(SAIDA / "todos_candidatos_brasil.csv")}
    for (ano, turno), contagem in candidatos_nacionais.items():
        for numero_cand, valor in contagem.items():
            assert pub_candidatos[(ano, turno, numero_cand)] == valor
    assert max(pub_candidatos, key=pub_candidatos.get) == (2026, 2, 13)
    assert max(v for (a, t, c), v in pub_candidatos.items() if a < 2026) == 60345999
    assert pub_candidatos[(2026, 2, 13)] - 60345999 == 3910233
    for r in csv_linhas(SAIDA / "nacional_percentuais.csv"):
        for lado in ["pt", "adv"]:
            for den in ["validos", "aptos"]:
                exato = 100 * Decimal(r["votos_" + lado]) / Decimal(r[den])
                assert abs(Decimal(r[f"{lado}_pct_{den}"]) - exato) < Decimal("0.000000001")
                total_campos += 1
    for r in csv_linhas(SAIDA / "geografia_todos_turnos.csv"):
        assert r["partido_vencedor"] == lideres[(int(r["ano"]), int(r["turno"]), r["uf"])]
    decisivo = {ano: max(t for a, t in candidatos_nacionais if a == ano) for ano in ANOS}
    mudancas = {}
    for uf in UFS[:-1]:
        lados = [lideres[(ano, decisivo[ano], uf)] == "PT" for ano in ANOS]
        mudancas[uf] = sum(a != b for a, b in zip(lados, lados[1:]))
    for r in csv_linhas(SAIDA / "ranking_mudancas_uf.csv"):
        assert int(r["mudancas_pt_nao_pt"]) == mudancas[r["uf"]]
    for r in csv_linhas(SAIDA / "crescimento_mesmo_turno.csv"):
        if not r["ano_anterior"]:
            continue
        ano, turno, anterior = int(r["ano"]), int(r["turno"]), int(float(r["ano_anterior"]))
        assert int(float(r["intervalo_anos"])) == ano - anterior
        for campo in SOMAS:
            esperado = totais[(ano, turno)][campo] - totais[(anterior, turno)][campo]
            assert int(float(r["delta_" + campo])) == esperado
            total_campos += 1
    for r in csv_linhas(SAIDA / "vitorias_ufs_por_eleicao.csv"):
        ano, turno = int(r["ano"]), int(r["turno"])
        n = candidatos_nacionais[(ano, turno)]
        adv = max((c for c in n if partidos[(ano, c)] != "PT"), key=n.get)
        c_pt = sum(lideres[(ano, turno, uf)] == "PT" for uf in UFS[:-1])
        c_adv = sum(lideres[(ano, turno, uf)] == partidos[(ano, adv)] for uf in UFS[:-1])
        assert int(r["ufs_pt"]) == c_pt and int(r["ufs_adversario"]) == c_adv
        assert int(r["ufs_outros"]) == 27 - c_pt - c_adv
    limites = list(csv_linhas(SAIDA / "limites_candidatos_antes_1989.csv"))
    assert len(limites) == 15 and max(int(r["votos"]) for r in limites) == 5636623
    for r in csv_linhas(SAIDA / "comparacao_publicacoes.csv"):
        assert int(r["diferenca"]) == int(r["valor_serie_mesma_cobertura"]) - int(r["valor_publicacao"])
        assert (r["bate"] == "True") == (int(r["diferenca"]) == 0)
    for r in csv_linhas(SAIDA / "fontes.csv"):
        assert hashlib.sha256((RAIZ / r["arquivo"]).read_bytes()).hexdigest() == r["sha256"]
    resumo = {"status": "PASSOU", "campos_conferidos": total_campos, "linhas_uf": len(exportadas), "linhas_brasil": len(br),
              "candidaturas_turnos_conferidas": len(pub_candidatos), "recorde": 64256232, "recorde_anterior": 60345999,
              "diferenca_recorde": 3910233, "mais_mudancas": {uf: n for uf, n in mudancas.items() if n == max(mudancas.values())},
              "metodo": "ZIP original de 1989, parser HTML independente de 1994, CSV linha a linha e mapa por código VT de 2010, JSON de UFs para 2026/2; sem pandas e sem importar o exportador",
              "divergencias_entre_publicacoes": sum(r["bate"] == "False" for r in csv_linhas(SAIDA / "comparacao_publicacoes.csv")),
              "campos_nominais_divergentes_no_detalhe_1989": sum(int(r["diferenca_candidatos_detalhe"]) != 0 for r in csv_linhas(SAIDA / "controle_validos_1989.csv")),
              "ressalva": "Confirma a transcrição e as contas das fontes adotadas. Não elimina as divergências entre publicações oficiais registradas em comparacao_publicacoes.csv"}
    (SAIDA / "validacao_independente.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
