"""Inspeção e coleta de formatos antigos do TSE, sem alterar arquivos existentes.

Uso: python -I -X utf8 pipeline/inspecionar_pt_historico.py
Auxiliar de pesquisa: extrai os TXT de UF de 1989 e filtra presidente do membro
BRASIL de 1998, que contém todos os cargos. Fontes públicas, cache retomável.
"""
import csv
import argparse
import importlib.util
import io
import json
import time
import urllib.request
import zipfile
from pathlib import Path
from html.parser import HTMLParser

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "dados/bruto/tse/historico_pt"


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--paginas", action="store_true")
    args = parser.parse_args()
    if args.paginas:
        class Pagina(HTMLParser):
            def handle_starttag(self, tag, attrs):
                a = dict(attrs)
                if tag in {"iframe", "object", "embed"}:
                    print(tag, a)
                if tag == "a" and any(t in a.get("href", "").lower() for t in [".pdf", "hotsite", "ords", "powerbi"]):
                    print("recurso", a.get("href"))
        urls = ["https://www.tse.jus.br/eleicoes/eleicoes-anteriores/eleicoes-1994/resultados-das-eleicoes-1994/brasil/resultados-das-eleicoes-1994-brasil",
                "https://www.tse.jus.br/eleicoes/eleicoes-anteriores/eleicoes-1994/resultados-das-eleicoes-1994/minas-gerais",
                "https://www.tse.jus.br/eleicoes/eleicoes-anteriores/eleicoes-1989/resultados"]
        for i, url in enumerate(urls):
            destino = CACHE / f"pagina_inspecao_{i}.html"
            if not destino.exists():
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=45) as r:
                    destino.write_bytes(r.read())
            html = destino.read_text(encoding="utf-8")
            print("URL", url)
            Pagina().feed(html)
            inicio = html.find('id="content-core"')
            if inicio >= 0:
                print(html[inicio:inicio+6500])
        return
    for tipo in ["votacao_candidato_uf", "detalhe_votacao_uf"]:
        url = f"https://cdn.tse.jus.br/estatistica/sead/odsele/{tipo}/{tipo}_1989.zip"
        destino = CACHE / f"{tipo}_1989.zip"
        if not destino.exists():
            for tentativa in range(4):
                try:
                    with urllib.request.urlopen(url, timeout=60) as r:
                        corpo = r.read(20_000_001)
                    if len(corpo) > 20_000_000:
                        raise ValueError("ZIP de 1989 excedeu o limite de 20 MB")
                    with zipfile.ZipFile(io.BytesIO(corpo)) as z:
                        z.testzip()
                    destino.write_bytes(corpo)
                    break
                except OSError:
                    if tentativa == 3:
                        raise
                    time.sleep(2 ** (tentativa + 1))
        with zipfile.ZipFile(destino) as z:
            print(tipo, [(i.filename, i.file_size) for i in z.infolist()], flush=True)
            for info in z.infolist():
                if info.filename.lower().endswith((".txt", ".csv", ".pdf")):
                    nome = Path(info.filename).name
                    saida = CACHE / "1989" / nome
                    if not saida.exists():
                        saida.parent.mkdir(parents=True, exist_ok=True)
                        saida.write_bytes(z.read(info))
                    if info.filename.lower().endswith((".txt", ".csv")):
                        print(z.read(info).decode("latin1")[:2200], flush=True)
    destino = RAIZ / "dados/bruto/tse/presidente_1998_BR.csv"
    if not destino.exists():
        spec = importlib.util.spec_from_file_location("extrair_tse_existente", RAIZ / "pipeline/extrair_tse.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        url = mod.URL.format(pasta="votacao_candidato_munzona", ano=1998)
        remoto = mod.ArquivoRemoto(url)
        with zipfile.ZipFile(io.BufferedReader(remoto, buffer_size=mod.BLOCO)) as z:
            nome = "votacao_candidato_munzona_1998_BRASIL.csv"
            with z.open(nome) as entrada:
                leitor = csv.DictReader(io.TextIOWrapper(entrada, encoding="latin1", newline=""), delimiter=";")
                print("1998 colunas", leitor.fieldnames, flush=True)
                temp = destino.with_suffix(".csv.tmp")
                quantidade = 0
                with temp.open("w", encoding="latin1", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=leitor.fieldnames, delimiter=";", quoting=csv.QUOTE_ALL)
                    w.writeheader()
                    for r in leitor:
                        if r["CD_CARGO"] == "1":
                            w.writerow(r)
                            quantidade += 1
                temp.replace(destino)
        print("1998 presidente", quantidade, "linhas; bytes HTTP", remoto.baixado, flush=True)
        (CACHE / "fonte_1998.json").write_text(json.dumps({"url": url, "membro": nome,
                "filtro": "CD_CARGO=1", "linhas": quantidade, "bytes_http": remoto.baixado}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
