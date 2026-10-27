"""Verificação independente do Brief F com csv.DictReader e inteiros Python.

Uso: python -I -X utf8 pipeline/brief_f_validar.py
Reconstrói cada célula municipal sem pandas/pivot/merge, confere as três
abrangências nacionais e valida a soma seção → zona de 2022.
"""
import ast
import csv
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "dados/saida/2turno"
CAMPOS = ["pt", "adv", "demais", "validos", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"]
DET = {"aptos": "QT_APTOS", "comparecimento": "QT_COMPARECIMENTO", "abstencoes": "QT_ABSTENCOES",
       "brancos": "QT_VOTOS_BRANCOS", "nulos": "QT_TOTAL_VOTOS_NULOS", "validos": "QT_TOTAL_VOTOS_VALIDOS"}


def ler(caminho, bruto=False):
    with (RAIZ / caminho).open(encoding="latin1" if bruto else "utf-8-sig", newline="") as f:
        yield from csv.DictReader(f, delimiter=";" if bruto else ",")


def chave_nome(nome):
    texto = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().upper()
    return "".join(c for c in texto if c.isalnum())


def gravar(linhas, nome):
    with (SAIDA / nome).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def conferir(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)


def main():
    cad = list(ler("dados/pbi/municipio.csv"))
    mapa = {(r["uf"], int(r["cd_tse"])): int(r["cd_ibge"]) for r in cad}
    ibge_uf = {int(r["cd_ibge"]): r["uf"] for r in cad}
    # Lê apenas a constante declarada, sem importar/executar o extrator.
    arvore = ast.parse((RAIZ / "pipeline/extrair_secoes.py").read_text(encoding="utf-8"))
    cidades = next(ast.literal_eval(n.value) for n in arvore.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "CIDADES_T20" for t in n.targets))
    capitais = {chave_nome(nome): (uf, int(cd)) for uf, cd, _, nome in cidades[:27]}
    reconstruido, vt, nacional = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for ano in (2006, 2010, 2014, 2018, 2022, 2026):
        for tipo in ("presidente", "detalhe"):
            for r in ler(f"dados/bruto/tse/{tipo}_{ano}_BR.csv", bruto=True):
                if int(r["CD_CARGO"]) != 1:
                    continue
                turno, uf, cd = int(r["NR_TURNO"]), r["SG_UF"], int(r["CD_MUNICIPIO"])
                transito = uf == "VT"
                if transito:
                    uf, cd = capitais[chave_nome(r["NM_MUNICIPIO"])]
                if tipo == "presidente":
                    num = int(r["NR_CANDIDATO"])
                    adv = 17 if ano == 2018 else 45 if ano <= 2014 else 22
                    papel = "pt" if num == 13 else "adv" if num == adv else "demais"
                    valores = {papel: int(r.get("QT_VOTOS_NOMINAIS_VALIDOS", r["QT_VOTOS_NOMINAIS"]))}
                else:
                    valores = {c: int(r[col]) for c, col in DET.items()}
                nacional[(ano, turno, "com_exterior")].update(valores)
                nacional[(ano, turno, "exterior" if uf == "ZZ" else "sem_exterior")].update(valores)
                if uf != "ZZ":
                    ibge = mapa[(uf, cd)]
                    reconstruido[(ano, turno, ibge)].update(valores)
                    if transito:
                        vt[(ano, turno, ibge)].update(valores)
        print(f"Verificação independente: {ano}", flush=True)
    config = json.loads((RAIZ / "dados/bruto/tse/2t2026/config.json").read_text(encoding="utf-8"))
    for abr in config["abr"]:
        uf = abr["cd"].upper()
        for mun in abr["mu"]:
            p = RAIZ / f"dados/bruto/tse/2t2026/{uf.lower()}/{str(mun['cd']).zfill(5)}.json"
            r = json.loads(p.read_text(encoding="utf-8"))
            candidatos = {int(c["n"]): int(c["vap"]) for ca in r["carg"] if int(ca["cd"]) == 1
                          for agr in ca["agr"] for par in agr["par"] for c in par["cand"]}
            valores = {"pt": candidatos[13], "adv": candidatos[22], "demais": 0, "validos": int(r["v"]["vv"]),
                       "aptos": int(r["e"]["te"]), "comparecimento": int(r["e"]["c"]), "abstencoes": int(r["e"]["a"]),
                       "brancos": int(r["v"]["vb"]), "nulos": int(r["v"]["tvn"])}
            nacional[(2026, 2, "com_exterior")].update(valores)
            nacional[(2026, 2, "exterior" if uf == "ZZ" else "sem_exterior")].update(valores)
            if uf != "ZZ":
                reconstruido[(2026, 2, int(mun["cdi"]))].update(valores)
    contagem, reconciliacao = Counter(), defaultdict(Counter)
    for turno, caminho in [(1, "dados/pbi/municipio_ano.csv"), (2, "dados/saida/2turno/municipio_2turno_completo.csv")]:
        vistas = set()
        for r in ler(caminho):
            ano, ibge = int(r["ano"]), int(r["cd_ibge"])
            chave = (ano, turno, ibge)
            conferir(chave not in vistas, f"Chave duplicada: {chave}")
            vistas.add(chave)
            for c in CAMPOS:
                publicado, transito = int(r[c]), vt[chave][c]
                obtido = publicado + (transito if turno == 1 else 0)
                esperado = reconstruido[chave][c]
                conferir(obtido == esperado, f"Célula {chave}/{c}: {obtido} != {esperado}")
                contagem[f"celulas_municipais_turno_{turno}"] += 1
                if turno == 1:
                    a = reconciliacao[(ano, ibge_uf[ibge], c)]
                    a["total_existente"] += publicado
                    a["transito_omitido"] += transito
                    a["total_reconstruido"] += esperado
        conferir(vistas == {k for k in reconstruido if k[1] == turno}, f"Cobertura de municípios difere no turno {turno}")
    for r in ler("dados/saida/2turno/comparecimento_turno.csv"):
        chave = (int(r["ano"]), int(r["turno"]), r["abrangencia"])
        for c in ("aptos", "comparecimento", "abstencoes", "brancos", "nulos"):
            conferir(int(r[c]) == nacional[chave][c], f"Comparecimento {chave}/{c}")
            contagem["celulas_comparecimento"] += 1
    linhas = []
    for (ano, uf, c), a in sorted(reconciliacao.items()):
        linhas.append({"ano": ano, "uf": uf, "campo": c, **dict(a),
                       "diferenca_sem_reconciliar": a["total_existente"] - a["total_reconstruido"],
                       "diferenca_reconciliada": a["total_existente"] + a["transito_omitido"] - a["total_reconstruido"]})
    gravar(linhas, "brief_f_primeiro_turno_reconciliacao.csv")
    zonas, secoes, locais = defaultdict(Counter), defaultdict(set), defaultdict(set)
    for r in ler("dados/saida/2turno/t20_secoes_2turno_2022.csv"):
        chave = (r["uf"], r["cd_ibge"], r["zona"])
        num, votos = int(r["numero"]), int(r["votos"])
        campo = {13: "pt", 22: "adv", 95: "brancos", 96: "nulos"}[num]
        zonas[chave][campo] += votos
        if num in (13, 22):
            zonas[chave]["validos"] += votos
        secoes[chave].add(r["secao"])
        locais[chave].add(r["local"])
        contagem["linhas_secao_2022"] += 1
    for r in ler("dados/saida/2turno/t20_zonas_2turno_2022.csv"):
        chave = (r["uf"], r["cd_ibge"], r["zona"])
        for c in ("pt", "adv", "validos", "brancos", "nulos"):
            conferir(int(r[c]) == zonas[chave][c], f"Zona {chave}/{c}")
            contagem["celulas_zona_2022"] += 1
        conferir(int(r["secoes"]) == len(secoes[chave]), "Contagem de seções")
        conferir(int(r["locais"]) == len(locais[chave]), "Contagem de locais")
    # Controle adicional por zona dos campos do detalhe de 2022.
    detalhe_zona = defaultdict(Counter)
    for r in ler("dados/bruto/tse/detalhe_2022_BR.csv", bruto=True):
        if int(r["NR_TURNO"]) != 2 or int(r["CD_CARGO"]) != 1 or r["SG_UF"] == "ZZ":
            continue
        ibge = mapa[(r["SG_UF"], int(r["CD_MUNICIPIO"]))]
        chave = (r["SG_UF"], str(ibge), r["NR_ZONA"])
        if chave in zonas:
            detalhe_zona[chave].update({c: int(r[col]) for c, col in DET.items()})
    for chave in zonas:
        for c in ["validos", "brancos", "nulos"]:
            conferir(zonas[chave][c] == detalhe_zona[chave][c], f"Detalhe 2022 {chave}/{c}")
            contagem["celulas_zona_2022_detalhe"] += 1
        zonas[chave].update({c: detalhe_zona[chave][c] for c in ["aptos", "comparecimento", "abstencoes"]})
    # API por zona de 2026: decodificação independente da normalização do exportador.
    zonas26 = {}
    for r in ler("dados/saida/2turno/brief_f_fontes_zonas_2026.csv"):
        caminho = RAIZ / r["arquivo"]
        conferir(hashlib.sha256(caminho.read_bytes()).hexdigest() == r["sha256"], "Hash da zona 2026")
        b = json.loads(caminho.read_text(encoding="utf-8"))
        conferir(b["tf"] == "s" and int(b["t"]) == 2 and int(b["ele"]) == 6258, "Zona não final")
        cand = {int(c["n"]): int(c["vap"]) for cargo in b["carg"] if int(cargo["cd"]) == 1
                for agr in cargo["agr"] for par in agr["par"] for c in par["cand"]}
        chave = (r["uf"], r["cd_ibge"], r["zona"])
        zonas26[chave] = {"pt": cand[13], "adv": cand[22], "demais": 0, "validos": int(b["v"]["vv"]),
                          "aptos": int(b["e"]["te"]), "comparecimento": int(b["e"]["c"]), "abstencoes": int(b["e"]["a"]),
                          "brancos": int(b["v"]["vb"]), "nulos": int(b["v"]["tvn"]), "secoes": int(b["s"]["ts"])}
        contagem["hashes_zonas_2026"] += 1
    for r in ler("dados/saida/2turno/t20_zonas_2turno_2026.csv"):
        chave = (r["uf"], r["cd_ibge"], r["zona"])
        for c in CAMPOS + ["secoes"]:
            conferir(int(r[c]) == zonas26[chave][c], f"Zona 2026 {chave}/{c}")
            contagem["celulas_zona_2026"] += 1
    for r in ler("dados/saida/2turno/t20_zonas_2turno_2022_2026.csv"):
        chave = (r["uf"], r["cd_ibge"], r["zona"])
        esperado = zonas26[chave] if int(r["ano"]) == 2026 else zonas[chave]
        for c in CAMPOS:
            conferir(int(r[c]) == esperado[c], f"Tabela combinada zonas {r['ano']}/{chave}/{c}")
            contagem["celulas_zonas_combinadas"] += 1
    original = (RAIZ / "dados/pbi/municipio_2turno.csv").read_bytes().splitlines(keepends=True)
    combinado = (SAIDA / "municipio_2turno_completo.csv").read_bytes().splitlines(keepends=True)
    conferir(combinado[-len(original) + 1:] == original[1:], "Bytes originais diferentes")
    # Confere que as entradas auditadas continuam idênticas ao manifesto.
    for r in ler("dados/saida/2turno/brief_f_entradas_sha256.csv"):
        conferir(hashlib.sha256((RAIZ / r["arquivo"]).read_bytes()).hexdigest() == r["sha256"], "Entrada alterada: " + r["arquivo"])
        contagem["hashes_entrada_conferidos"] += 1
    resultado = {"metodo": "csv.DictReader, Counter e inteiros Python; reextração independente sem pandas",
                 "contagens": dict(contagem), "diferencas": 0, "bytes_2022_2026_preservados": True}
    (SAIDA / "brief_f_validacao_independente.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
