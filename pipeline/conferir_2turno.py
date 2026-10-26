"""Segunda conferência, independente dos scripts de exportação e análise.

Usa apenas csv/json e inteiros da biblioteca padrão para refazer a agregação.
Uso: python -I -X utf8 pipeline/conferir_2turno.py
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "dados/saida/2turno"
CAMPOS = "pt adv demais validos aptos comparecimento abstencoes brancos nulos".split()
checagens = Counter()


def ler(nome, sep=",", encoding="utf-8"):
    with open(RAIZ / nome, encoding=encoding, newline="") as f:
        return list(csv.DictReader(f, delimiter=sep))


def conferir(esperado, obtido, contexto):
    for campo in CAMPOS:
        if int(esperado[campo]) != int(obtido[campo]):
            raise AssertionError(f"{contexto}: {campo}: {esperado[campo]} != {obtido[campo]}")
        checagens["contagens_iguais"] += 1


def resolver_sistema(matriz, vetor):
    """Eliminação gaussiana com pivoteamento, só para as 2–4 variáveis do teste."""
    m = [list(linha) + [valor] for linha, valor in zip(matriz, vetor)]
    n = len(m)
    for i in range(n):
        melhor = max(range(i, n), key=lambda j: abs(m[j][i]))
        m[i], m[melhor] = m[melhor], m[i]
        assert abs(m[i][i]) > 1e-12, "Regressão singular"
        divisor = m[i][i]
        m[i] = [x / divisor for x in m[i]]
        for j in range(n):
            if j != i:
                mult = m[j][i]
                m[j] = [a - mult * b for a, b in zip(m[j], m[i])]
    return [r[-1] for r in m]


def main():
    cadastro = ler("dados/pbi/municipio.csv")
    depara = {(r["uf"], int(r["cd_tse"])): int(r["cd_ibge"]) for r in cadastro}
    exp_m = ler("dados/pbi/municipio_2turno.csv")
    exp_u = ler("dados/pbi/uf_2turno.csv")
    assert list(exp_m[0]) == ["ano", "cd_ibge"] + CAMPOS
    assert list(exp_u[0]) == ["ano", "uf"] + CAMPOS
    em = {(int(r["ano"]), int(r["cd_ibge"])): r for r in exp_m}
    eu = {(int(r["ano"]), r["uf"]): r for r in exp_u}
    assert len(em) == len(exp_m) and len(eu) == len(exp_u)
    config = json.loads((RAIZ / "dados/bruto/tse/2t2026/config.json").read_text(encoding="utf-8"))
    u26 = defaultdict(Counter)
    nao_instalados = Counter()
    for abr in config["abr"]:
        uf = abr["cd"].upper()
        for m in abr["mu"]:
            b = json.loads((RAIZ / "dados/bruto/tse/2t2026" / uf.lower() / f"{int(m['cd']):05d}.json").read_text(encoding="utf-8"))
            cands = [c for cargo in b["carg"] if int(cargo["cd"]) == 1 for agr in cargo["agr"] for par in agr["par"] for c in par["cand"]]
            votos = {int(c["n"]): int(c["vap"]) for c in cands}
            r = {"pt": votos[13], "adv": votos[22], "demais": 0, "validos": int(b["v"]["vv"]),
                 "aptos": int(b["e"]["te"]), "comparecimento": int(b["e"]["c"]), "abstencoes": int(b["e"]["a"]),
                 "brancos": int(b["v"]["vb"]), "nulos": int(b["v"]["tvn"])}
            u26[uf].update(r)
            nao_instalados[uf] += int(b["e"]["esni"])
            if uf != "ZZ":
                conferir(r, em[(2026, int(m["cdi"]))], f"2026 {uf}/{m['cd']}")
                checagens["municipios_2026"] += 1
    for uf, total in u26.items():
        conferir(total, eu[(2026, uf)], "2026/" + uf)
    # 2022: leitura linha a linha, sem pivot ou groupby, incluindo voto em trânsito.
    m22 = defaultdict(Counter)
    for r in ler("dados/bruto/tse/presidente_2022_BR.csv", ";", "latin1"):
        if r["NR_TURNO"] != "2" or r["CD_CARGO"] != "1":
            continue
        chave = (r["SG_UF"], int(r["CD_MUNICIPIO"]))
        campo = {"13": "pt", "22": "adv"}[r["NR_CANDIDATO"]]
        m22[chave][campo] += int(r["QT_VOTOS_NOMINAIS_VALIDOS"])
    mapa = {"aptos": "QT_APTOS", "comparecimento": "QT_COMPARECIMENTO", "abstencoes": "QT_ABSTENCOES",
            "brancos": "QT_VOTOS_BRANCOS", "nulos": "QT_TOTAL_VOTOS_NULOS", "validos": "QT_TOTAL_VOTOS_VALIDOS"}
    nao_inst22 = 0
    for r in ler("dados/bruto/tse/detalhe_2022_BR.csv", ";", "latin1"):
        if r["NR_TURNO"] != "2" or r["CD_CARGO"] != "1":
            continue
        chave = (r["SG_UF"], int(r["CD_MUNICIPIO"]))
        for campo, origem in mapa.items():
            m22[chave][campo] += int(r[origem])
        nao_inst22 += int(r["QT_ELEITORES_SECOES_NAO_INSTALADAS"])
    u22 = defaultdict(Counter)
    for (uf, cd), valor in m22.items():
        u22[uf].update(valor)
        if uf != "ZZ":
            conferir(valor, em[(2022, depara[(uf, cd)])], f"2022 {uf}/{cd}")
            checagens["municipios_2022"] += 1
    for uf, valor in u22.items():
        conferir(valor, eu[(2022, uf)], "2022/" + uf)
    total26, total22 = Counter(), Counter()
    for v in u26.values():
        total26.update(v)
    for v in u22.values():
        total22.update(v)
    ultimo = json.loads((RAIZ / "dados/apuracao/ultimo.json").read_text(encoding="utf-8"))["brasil"]
    ref = {"pt": ultimo["lula_votos"], "adv": ultimo["flavio_votos"], "demais": 0, "validos": ultimo["validos"],
           "aptos": ultimo["eleitorado"], "comparecimento": ultimo["comparecimento"], "abstencoes": ultimo["abstencao"],
           "brancos": ultimo["brancos"], "nulos": ultimo["nulos"]}
    conferir(ref, total26, "Brasil/ultimo.json")
    for total, nao_inst in [(total26, sum(nao_instalados.values())), (total22, nao_inst22)]:
        assert total["aptos"] - total["comparecimento"] - total["abstencoes"] == nao_inst
    # Recalcula as comparações de cada município e o agrupamento regional do 1º ao 2º.
    m1 = {int(r["cd_ibge"]): r for r in ler("dados/pbi/municipio_ano.csv") if r["ano"] == "2026"}
    comp = ler("dados/saida/2turno/comparacao_municipios.csv")
    viradas = Counter()
    crescimentos = {c: defaultdict(Counter) for c in ["regiao", "porte", "quinto"]}
    for r in comp:
        cod = int(r["cd_ibge"])
        a, b = m1[cod], em[(2026, cod)]
        for campo in CAMPOS:
            assert int(r["delta_" + campo]) == int(b[campo]) - int(a[campo])
            checagens["deltas_iguais"] += 1
        assert int(r["delta_saldo_pt"]) == int(b["pt"]) - int(b["adv"]) - int(a["pt"]) + int(a["adv"])
        viradas[(r["vencedor_1t"], r["vencedor_2t"])] += 1
        for cat in crescimentos:
            for campo in ["pt", "adv", "comparecimento"]:
                crescimentos[cat][r[cat]][campo] += int(b[campo]) - int(a[campo])
    for cat, grupos in crescimentos.items():
        for r in ler(f"dados/saida/2turno/crescimento_{cat}.csv"):
            for campo in ["pt", "adv", "comparecimento"]:
                assert int(r["delta_" + campo]) == grupos[r[cat]][campo]
                checagens["agrupamentos_iguais"] += 1
    h = ler("dados/apuracao/historico.csv")
    primeiro_flavio = next(r for r in h if int(r["flavio_votos"]) > int(r["lula_votos"]))
    indice_flavio = h.index(primeiro_flavio)
    primeiro_lula = next(r for r in h[indice_flavio + 1:] if int(r["lula_votos"]) > int(r["flavio_votos"]))
    garantia = {}
    for modo in ["retrospectivo", "conservador"]:
        for r in h:
            restantes = total26["validos"] - int(r["validos"]) if modo == "retrospectivo" else total26["aptos"] - sum(int(r[c]) for c in ["abstencao", "brancos", "nulos", "validos"])
            if int(r["lula_votos"]) - int(r["flavio_votos"]) > restantes:
                garantia[modo] = r["atualizado_tse"]
                break
    marcos = {r["marco"]: r for r in ler("dados/saida/2turno/apuracao_marcos.csv")}
    assert marcos["lideranca_flávio"]["atualizado_tse"] == primeiro_flavio["atualizado_tse"]
    assert marcos["lideranca_lula"]["atualizado_tse"] == primeiro_lula["atualizado_tse"]
    for modo, hora in garantia.items():
        assert marcos["garantia_" + modo]["atualizado_tse"] == hora
    # Conta pesquisas novamente, tratando vazios como ausências.
    polls = ler("dados/pbi/pesquisa.csv")
    contagem_pesquisas = {}
    for turno, limite in [(1, "2026-10-04"), (2, "2026-10-25")]:
        linhas = [r for r in polls if r["cenario"] == f"{turno}º turno" and r["tipo"] == "validos" and r["divulgacao"] < limite and (not r["campo_fim"] or r["campo_fim"] < limite)]
        q = Counter()
        for r in linhas:
            q["linhas"] += 1
            if not r["lula"] or not r["flavio"]:
                q["sem_valores"] += 1
            else:
                l, f = float(r["lula"]), float(r["flavio"])
                q["lula_frente" if l > f else "flavio_frente" if f > l else "empates"] += 1
                q["pares_numericos"] += 1
        ref = next(r for r in ler("dados/saida/2turno/pesquisas_placar.csv") if r["turno"] == str(turno) and r["recorte"] == "todo_o_arquivo")
        for campo, valor in q.items():
            assert int(float(ref[campo])) == valor
        contagem_pesquisas[turno] = dict(q)
        direcoes = []
        for r in linhas:
            base = r
            if not r["lula"] or not r["flavio"]:
                base = next(t for t in polls if t["cenario"] == r["cenario"] and t["tipo"] == "totais" and t["instituto"] == r["instituto"] and t["registro_tse"] == r["registro_tse"])
            l, f = Decimal(base["lula"]), Decimal(base["flavio"])
            direcoes.append((r, "Lula" if l > f else "Flávio" if f > l else "Empate"))
        ultimas = {}
        for r, lider in sorted(direcoes, key=lambda z: (z[0]["divulgacao"], z[0]["campo_fim"], int(z[0]["id"]))):
            ultimas[r["instituto"]] = (r, lider)
        publicadas = ler(f"dados/saida/2turno/pesquisas_{turno}t_direcao_todas.csv")
        esperado = {int(r["id_validos"]): r["lider"] for r in publicadas}
        assert all(esperado[int(r["id"])] == lider for r, lider in direcoes)
        publicadas = {r["instituto"]: r for r in ler(f"dados/saida/2turno/pesquisas_{turno}t_direcao_ultimas.csv")}
        assert all(publicadas[instituto]["lider"] == lider for instituto, (_, lider) in ultimas.items())
        checagens["direcoes_pesquisas"] += len(direcoes) + len(ultimas)
        if turno == 2:
            numericas = [r for r, _ in ultimas.values() if r["lula"] and r["flavio"]]
            media_lula = sum(Decimal(r["lula"]) for r in numericas) / len(numericas)
            media_flavio = sum(Decimal(r["flavio"]) for r in numericas) / len(numericas)
            assert media_lula == Decimal("49.2") and media_flavio == Decimal("50.8")
            erros = ler("dados/saida/2turno/pesquisas_2t_ultimas.csv")
            urna_lula = 100 * Decimal(total26["pt"]) / total26["validos"]
            urna_flavio = 100 - urna_lula
            for r in erros:
                if not r["lula"] or not r["flavio"]:
                    continue
                erro_l = Decimal(r["lula"]) - urna_lula
                erro_f = Decimal(r["flavio"]) - urna_flavio
                assert abs(Decimal(r["lula_erro_pp"]) - erro_l) < Decimal("0.000000001")
                assert abs(Decimal(r["flavio_erro_pp"]) - erro_f) < Decimal("0.000000001")
                checagens["erros_pesquisas"] += 2
    # Reestima os três modelos por equações normais e eliminação gaussiana.
    modelos = ler("dados/saida/2turno/regressao_ecologica.csv")
    for nome, termos in [("principal", ["constante", "demais", "comparecimento"]),
                         ("com_invalidos", ["constante", "demais", "comparecimento", "invalidos"]),
                         ("sem_constante", ["demais", "comparecimento"])]:
        w, x = [], []
        for r in comp:
            peso = int(r["aptos_1t"])
            xs = {"constante": 1.0, "demais": int(r["demais_1t"]) / peso,
                  "comparecimento": int(r["delta_comparecimento"]) / peso,
                  "invalidos": int(r["delta_invalidos"]) / peso}
            w.append(peso)
            x.append([xs[t] for t in termos])
        matriz = [[math.fsum(p * linha[i] * linha[j] for p, linha in zip(w, x)) for j in range(len(termos))] for i in range(len(termos))]
        for candidato, campo in [("Lula", "delta_pt"), ("Flávio", "delta_adv")]:
            # X' W y, com y=ganho/peso: o peso cancela neste produto.
            vetor = [math.fsum(linha[i] * int(r[campo]) for linha, r in zip(x, comp)) for i in range(len(termos))]
            betas = resolver_sistema(matriz, vetor)
            for termo, coef in zip(termos, betas):
                publicado = next(r for r in modelos if r["modelo"] == nome and r["candidato"] == candidato and r["termo"] == termo)
                assert abs(coef - float(publicado["coeficiente"])) < 1e-8
                checagens["coeficientes_regressao"] += 1
    fatos = ler("dados/bruto/domingo/fatos.csv")
    assert list(fatos[0]) == ["data_hora", "fato", "fonte", "url", "confirmacao"]
    for r in fatos:
        assert None not in r and all(r.values())
        assert datetime.fromisoformat(r["data_hora"]).tzinfo is not None
        assert r["url"].startswith("https://")
        if r["confirmacao"] == "confirmado em 2 fontes ou mais":
            assert len({o["url"] for o in fatos if o["fato"] == r["fato"]}) >= 2
        else:
            assert r["confirmacao"] == "uma fonte"
    checagens["registros_documentais_validos"] = len(fatos)
    for r in ler("dados/saida/2turno/hashes_analise.csv"):
        assert hashlib.sha256((RAIZ / r["arquivo"]).read_bytes()).hexdigest() == r["sha256"]
    saida = {"status": "PASSOU", "checagens": dict(checagens), "totais_2022": dict(total22), "totais_2026": dict(total26),
             "eleitores_secoes_nao_instaladas_2022": nao_inst22, "eleitores_secoes_nao_instaladas_2026": sum(nao_instalados.values()),
             "uf_nao_instaladas_2026": dict(nao_instalados), "garantia": garantia, "pesquisas": contagem_pesquisas,
             "viradas": {" → ".join(k): v for k, v in viradas.items()},
             "metodo": "Biblioteca padrão, somas inteiras linha a linha, sem importar exportador/analisador e sem pandas/numpy"}
    (SAIDA / "validacao_independente.json").write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(saida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
