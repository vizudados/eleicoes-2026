"""Confere as contas da apuração (pbi/dax/T18 Apuração) no motor do Desktop contra os arquivos do coletor.

Rode com pPastaApuracao apontando para a pasta que se quer conferir (scripts/parametro.ps1): no ensaio do 1º turno, o
oráculo é o próprio TSE (percentuais e totais publicados em ufs.csv). Confere o Brasil, cada UF e uma região inteira
(a soma de várias UFs, que só bate se as contas forem razão de somas).

    python -X utf8 pbi/scripts/conferir_apuracao.py dados/apuracao/ensaio-1turno
"""
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dax import consultar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
REGIAO = {"Sudeste": ["ES", "MG", "RJ", "SP"], "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]}


def num(x):
    return float(x) if x not in ("", None) else 0.0


def main():
    pasta = RAIZ / (sys.argv[1] if len(sys.argv) > 1 else "dados/apuracao/ensaio-1turno")
    linhas = {r["uf"]: r for r in csv.DictReader(open(pasta / "ufs.csv", encoding="utf-8"))}
    erros = 0

    def bate(rotulo, obtido, esperado, tol=0.0):
        nonlocal erros
        ok = (obtido == esperado) if isinstance(esperado, str) else abs((obtido or 0) - esperado) <= tol
        if not ok:
            erros += 1
            print(f"DIFERE {rotulo}: motor {obtido!r} × arquivo {esperado!r}")
        return ok

    medidas = ["Apuração · Lula votos", "Apuração · Flávio votos", "Apuração · Lula %", "Apuração · Flávio %",
               "Apuração · abstenção %", "Apuração · seções %", "Apuração · diferença", "Apuração · brancos",
               "Apuração · nulos", "Apuração · líder", "Apuração · válidos", "Apuração · escopo"]
    cols = ", ".join(f'"{m}", [{m}]' for m in medidas)
    br = consultar(f"EVALUATE ROW ( {cols} )")[0]
    v = {k.strip("[]"): x for k, x in br.items()}
    b = linhas["BR"]
    bate("BR Lula votos", v["Apuração · Lula votos"], num(b["lula_votos"]))
    bate("BR Flávio votos", v["Apuração · Flávio votos"], num(b["flavio_votos"]))
    bate("BR Lula %", round(v["Apuração · Lula %"] * 100, 2), num(b["lula_pct"]), 0.005)
    bate("BR Flávio %", round(v["Apuração · Flávio %"] * 100, 2), num(b["flavio_pct"]), 0.005)
    bate("BR abstenção %", round(v["Apuração · abstenção %"] * 100, 2), num(b["abstencao_pct"]), 0.005)
    bate("BR seções %", round(v["Apuração · seções %"] * 100, 2), num(b["secoes_pct"]), 0.005)
    bate("BR diferença", v["Apuração · diferença"], num(b["diferenca_votos"]))
    bate("BR brancos", v["Apuração · brancos"], num(b["brancos"]))
    bate("BR nulos", v["Apuração · nulos"], num(b["nulos"]))
    bate("BR líder", v["Apuração · líder"], b["lider"])
    bate("BR escopo", v["Apuração · escopo"], "Brasil")
    print(f"Brasil: Lula {v['Apuração · Lula votos']:,.0f} ({v['Apuração · Lula %']:.4%}) × Flávio "
          f"{v['Apuração · Flávio votos']:,.0f} ({v['Apuração · Flávio %']:.4%}) · líder {v['Apuração · líder']}")

    por_uf = consultar(
        "EVALUATE SUMMARIZECOLUMNS ( 'UF'[UF], \"l\", [Apuração · Lula %], \"f\", [Apuração · Flávio %], "
        "\"a\", [Apuração · abstenção %], \"s\", [Apuração · seções %], \"d\", [Apuração · líder], "
        "\"e\", [Apuração · escopo] )")
    n = 0
    for r in por_uf:
        uf = r["UF[UF]"]
        e = linhas[uf]
        n += 1
        bate(f"{uf} Lula %", round(r["[l]"] * 100, 2), num(e["lula_pct"]), 0.005)
        bate(f"{uf} Flávio %", round(r["[f]"] * 100, 2), num(e["flavio_pct"]), 0.005)
        bate(f"{uf} abstenção %", round(r["[a]"] * 100, 2), num(e["abstencao_pct"]), 0.005)
        bate(f"{uf} seções %", round(r["[s]"] * 100, 2), num(e["secoes_pct"]), 0.005)
        bate(f"{uf} líder", r["[d]"], e["lider"])
    print(f"{n} UFs conferidas (com o exterior)")

    for regiao, ufs in REGIAO.items():
        lula = sum(num(linhas[u]["lula_votos"]) for u in ufs)
        val = sum(num(linhas[u]["validos"]) for u in ufs)
        r = consultar(f"EVALUATE ROW ( \"l\", CALCULATE ( [Apuração · Lula %], 'UF'[Região] = \"{regiao}\" ), "
                      f"\"e\", CALCULATE ( [Apuração · escopo], 'UF'[Região] = \"{regiao}\" ), "
                      f"\"n\", CALCULATE ( [Apuração · UFs com Lula à frente], 'UF'[Região] = \"{regiao}\" ) )")[0]
        bate(f"{regiao} Lula %", round(r["[l]"], 6), round(lula / val, 6), 1e-6)
        bate(f"{regiao} escopo", r["[e]"], f"{len(ufs)} UFs")
        esperado = sum(1 for u in ufs if linhas[u]["lider"] == "Lula")
        bate(f"{regiao} UFs com Lula à frente", r["[n]"], esperado)
        print(f"{regiao}: Lula {r['[l]']:.4%} · {r['[e]']} · Lula à frente em {r['[n]']}")
    tot = consultar("EVALUATE ROW ( \"l\", [Apuração · UFs com Lula à frente], \"f\", [Apuração · UFs com Flávio à frente] )")[0]
    lula_ufs = sum(1 for u, e in linhas.items() if u not in ("BR", "ZZ") and e["lider"] == "Lula")
    flavio_ufs = sum(1 for u, e in linhas.items() if u not in ("BR", "ZZ") and e["lider"] == "Flávio")
    bate("UFs Lula", tot["[l]"], lula_ufs)
    bate("UFs Flávio", tot["[f]"], flavio_ufs)
    print(f"UFs: Lula à frente em {tot['[l]']}, Flávio em {tot['[f]']}")
    print("OK: todas as contas batem com o arquivo" if not erros else f"{erros} diferença(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
