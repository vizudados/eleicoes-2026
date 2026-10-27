"""Inspeção somente leitura das entradas do Brief F."""
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extrair_tse import ArquivoRemoto, BLOCO

RAIZ = Path(__file__).resolve().parents[1]


def local():
    for nome in ("municipio_ano", "municipio_2turno", "comparecimento_ano", "abstencao_perfil",
                 "abstencao_faixa_municipio", "pt_historico_brasil", "pt_historico_uf", "t20_locais"):
        d = pd.read_csv(RAIZ / f"dados/pbi/{nome}.csv")
        print(nome, len(d), list(d), flush=True)
        print(d.head(2).to_string(index=False))
    for ano in (2006, 2010, 2014, 2018, 2022, 2026):
        for nome in ("presidente", "detalhe"):
            d = pd.read_csv(RAIZ / f"dados/bruto/tse/{nome}_{ano}_BR.csv", sep=";", encoding="latin1")
            print(ano, nome, "colunas", list(d), flush=True)
            print(d.groupby(["NR_TURNO", "SG_UF"]).size().groupby(level=0).agg(["sum", "count"]).to_string())
            if ano == 2010:
                print(d[d.SG_UF.eq("VT")].head(2).to_string(index=False))
        print("---", flush=True)


def remoto():
    urls = [
        "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_comparecimento_abstencao/perfil_comparecimento_abstencao_2026.zip",
        "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip",
        "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2022_BR.zip",
    ]
    for url in urls:
        print("URL", url, flush=True)
        try:
            remoto = ArquivoRemoto(url)
            with zipfile.ZipFile(io.BufferedReader(remoto, buffer_size=BLOCO)) as z:
                print("ZIP", remoto.tamanho, [(i.filename, i.file_size, str(i.date_time)) for i in z.infolist()], flush=True)
                nomes = [n for n in z.namelist() if n.upper().endswith("_AC.CSV")] or [n for n in z.namelist() if n.lower().endswith(".csv")][:1]
                for nome in nomes:
                    with z.open(nome) as arq:
                        d = pd.read_csv(arq, encoding="latin1", sep=";", nrows=4)
                    print(d.to_string(index=False), flush=True)
        except Exception as exc:
            print(type(exc).__name__, str(exc), flush=True)


def chaves():
    from brief_f_2turno import mapear_transito, DETALHE
    for ano in (2006, 2010, 2014, 2018, 2022, 2026):
        v = pd.read_csv(RAIZ / f"dados/bruto/tse/presidente_{ano}_BR.csv", sep=";", encoding="latin1")
        d = pd.read_csv(RAIZ / f"dados/bruto/tse/detalhe_{ano}_BR.csv", sep=";", encoding="latin1")
        campo = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in v else "QT_VOTOS_NOMINAIS"
        v["votos"] = v[campo]
        d = d.rename(columns=DETALHE)
        v, d = mapear_transito(v, ano, "votos"), mapear_transito(d, ano, "detalhe")
        keys = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO"]
        vm = v.groupby(keys, as_index=False).agg(votos=("votos", "sum"), nome=("NM_MUNICIPIO", "first"))
        dm = d.groupby(keys, as_index=False)[list(DETALHE.values())].sum()
        m = vm.merge(dm, how="outer", on=keys, indicator=True)
        print(ano, m[m._merge.ne("both")].to_string(index=False), flush=True)


def api():
    cfg = json.loads((RAIZ / "dados/bruto/tse/2t2026/config.json").read_text(encoding="utf-8"))
    abr = next(a for a in cfg["abr"] if a["cd"].upper() == "RJ")
    print("CONFIG", next(m for m in abr["mu"] if int(m["cd"]) == 60011))
    b = json.loads((RAIZ / "dados/bruto/tse/2t2026/rj/60011.json").read_text(encoding="utf-8"))
    print("CHAVES MUNICÍPIO", list(b))
    print("SEÇÕES", b.get("s"))
    raiz = "https://resultados.tse.jus.br/oficial/ele2026/6258/"
    for caminho in ["dados/rj/rj60011-z0004-c0001-e006258-u.json", "dados/rj/rj60011-c0001-e006258-z0004-u.json",
                    "config/rj/rj60011-zona.json", "config/rj/rj60011-secoes.json"]:
        url = raiz + caminho
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                texto = r.read(2000).decode("utf-8")
                print(r.status, url, texto[:1500], flush=True)
        except urllib.error.HTTPError as exc:
            print(exc.code, url, flush=True)


if __name__ == "__main__":
    if "--api" in sys.argv:
        api()
    elif "--chaves" in sys.argv:
        chaves()
    elif "--remoto" in sys.argv:
        remoto()
    else:
        local()
