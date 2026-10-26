"""Coleta retomável e exportação auditada do segundo turno presidencial.

Uso: python -I -X utf8 pipeline/exportar_2turno.py [--workers 8] [--somente-cache]
Não modifica os CSV de entrada nem o coletor da apuração. Falha antes de publicar
os dois CSV do painel se qualquer total geográfico divergir.
"""
import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "dados/bruto/tse/2t2026"
SAIDA = RAIZ / "dados/saida/2turno"
COLUNAS = ["pt", "adv", "demais", "validos", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"]
ORIGEM = {"pt": "lula_votos", "adv": "flavio_votos", "validos": "validos", "aptos": "eleitorado",
          "comparecimento": "comparecimento", "abstencoes": "abstencao", "brancos": "brancos", "nulos": "nulos"}
API = "https://resultados.tse.jus.br/oficial/ele2026/6258"
URL_CONFIG = API + "/config/mun-e006258-cm.json"
URL_2022 = "https://www.tse.jus.br/comunicacao/noticias/2022/Outubro/100-das-secoes-totalizadas-confira-como-ficou-o-quadro-eleitoral-apos-o-2o-turno/"
UFS = set("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO ZZ".split())


def gravar_csv(df, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temp = caminho.with_suffix(caminho.suffix + ".tmp")
    df.to_csv(temp, index=False, encoding="utf-8", lineterminator="\n", float_format="%.12g")
    temp.replace(caminho)


def gravar_json(obj, caminho):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temp = caminho.with_suffix(caminho.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(caminho)


def baixar_json(url, destino, somente_cache=False):
    """Até seis tentativas; no máximo oito chamadas simultâneas no executor."""
    if destino.exists():
        return json.loads(destino.read_text(encoding="utf-8"))
    if somente_cache:
        raise FileNotFoundError(f"Cache ausente: {destino.relative_to(RAIZ)}")
    for tentativa in range(6):
        try:
            pedido = urllib.request.Request(url, headers={"User-Agent": "VizuDados-EstudoEleitoral/1.0"})
            with urllib.request.urlopen(pedido, timeout=45) as resposta:
                corpo = resposta.read(4_000_001)
            if len(corpo) > 4_000_000:
                raise ValueError("Resposta JSON excedeu 4 MB")
            objeto = json.loads(corpo.decode("utf-8"))
            # Preserva os bytes da fonte, inclusive espaços e codificação.
            destino.parent.mkdir(parents=True, exist_ok=True)
            temp = destino.with_suffix(".json.tmp")
            temp.write_bytes(corpo)
            temp.replace(destino)
            time.sleep(0.05)
            return objeto
        except urllib.error.HTTPError as erro:
            if erro.code not in {408, 425, 429, 500, 502, 503, 504} or tentativa == 5:
                raise
            espera = max(2 ** (tentativa + 1), int(erro.headers.get("Retry-After", "0")))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if tentativa == 5:
                raise
            espera = 2 ** (tentativa + 1)
        time.sleep(min(120, espera) + random.random())
    raise RuntimeError("Tentativas esgotadas")


def normalizar(bruto):
    if int(bruto["t"]) != 2:
        raise ValueError("A fonte não é do segundo turno")
    candidatos = {}
    for cargo in bruto["carg"]:
        if int(cargo["cd"]) != 1:
            continue
        for agr in cargo["agr"]:
            for partido in agr["par"]:
                for candidato in partido["cand"]:
                    numero = int(candidato["n"])
                    if numero in candidatos:
                        raise ValueError("Candidato duplicado")
                    candidatos[numero] = int(candidato["vap"])
    if set(candidatos) != {13, 22}:
        raise ValueError(f"Candidatos inesperados: {candidatos}")
    e, v = bruto["e"], bruto["v"]
    return {"pt": candidatos[13], "adv": candidatos[22], "demais": 0,
            "validos": int(v["vv"]), "aptos": int(e["te"]), "comparecimento": int(e["c"]),
            "abstencoes": int(e["a"]), "brancos": int(v["vb"]), "nulos": int(v["tvn"])}


def referencia_2022():
    """Oráculo público congelado, conferido na notícia oficial em 26/10/2026.

    O endpoint antigo /545/dados retorna 404 e o HTML via urllib retorna 403.
    A notícia foi lida com a ferramenta web, parágrafos de participação e de
    Presidência (31/10/2022 00:35, atualização 08/07/2026 00:49). Estes são
    valores de controle, jamais usados para completar ou redistribuir votos.
    """
    totais = {"aptos": 156454011, "comparecimento": 124252796, "abstencoes": 32200558,
              "brancos": 1769678, "nulos": 3930765, "validos": 118552353,
              "pt": 60345999, "adv": 58206354, "demais": 0}
    gravar_json({"url": URL_2022, "consulta": "2026-10-26", "metodo": "Transcrição dos oito totais da notícia oficial, conferida via ferramenta web; oráculo congelado no script",
                 "totais": totais}, SAIDA / "referencia_nacional_2022.json")
    return totais


def prova(linhas, ano, nivel, local, campo, obtido, esperado, fonte):
    linhas.append({"ano": ano, "nivel": nivel, "local": local, "campo": campo,
                   "obtido": int(obtido), "esperado": int(esperado), "diferenca": int(obtido) - int(esperado),
                   "bate": int(obtido) == int(esperado), "fonte": fonte})


def ler_2022():
    tabelas = {}
    for nome, base in [("presidente", "votacao"), ("detalhe", "detalhe")]:
        caminho = RAIZ / f"dados/bruto/tse/{nome}_2022_BR.csv"
        df = pd.read_csv(caminho, sep=";", encoding="latin1") if caminho.exists() else pd.DataFrame()
        if df.empty or not df.NR_TURNO.eq(2).any():
            subprocess.run([sys.executable, "-I", "-X", "utf8", str(RAIZ / "pipeline/extrair_tse.py"),
                            "--base", base, "2022"], check=True, cwd=RAIZ)
            df = pd.read_csv(caminho, sep=";", encoding="latin1")
        tabelas[nome] = df[df.NR_TURNO.eq(2) & df.CD_CARGO.eq(1)].copy()
    votos, detalhe = tabelas["presidente"], tabelas["detalhe"]
    chaves = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "ST_VOTO_EM_TRANSITO"]
    if detalhe.duplicated(chaves).any() or votos.duplicated(chaves + ["NR_CANDIDATO"]).any():
        raise ValueError("Chave duplicada nos brutos de 2022")
    if set(votos.NR_CANDIDATO) != {13, 22}:
        raise ValueError("Candidatos inesperados no bruto de 2022")
    votos["papel"] = votos.NR_CANDIDATO.map({13: "pt", 22: "adv"})
    chaves = ["SG_UF", "CD_MUNICIPIO"]
    wide = votos.pivot_table(index=chaves, columns="papel", values="QT_VOTOS_NOMINAIS_VALIDOS", aggfunc="sum").reset_index()
    mapa = {"QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "QT_ABSTENCOES": "abstencoes",
            "QT_VOTOS_BRANCOS": "brancos", "QT_TOTAL_VOTOS_NULOS": "nulos", "QT_TOTAL_VOTOS_VALIDOS": "validos"}
    det = detalhe.groupby(chaves, as_index=False)[list(mapa)].sum().rename(columns=mapa)
    df = wide.merge(det, on=chaves, validate="one_to_one", how="outer", indicator=True)
    if not df._merge.eq("both").all():
        raise ValueError("Municípios de votação e detalhe diferentes em 2022")
    df = df.drop(columns="_merge").rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "cd_tse"})
    df["demais"], df["ano"] = 0, 2022
    cadastro = pd.read_csv(RAIZ / "dados/pbi/municipio.csv", usecols=["cd_tse", "cd_ibge", "uf"])
    nacional = df.groupby(["ano", "uf"], as_index=False)[COLUNAS].sum()
    municipios = df[df.uf.ne("ZZ")].merge(cadastro, on=["cd_tse", "uf"], how="left", validate="one_to_one")
    if municipios.cd_ibge.isna().any():
        raise ValueError("Código TSE de 2022 sem código IBGE: " + str(municipios[municipios.cd_ibge.isna()].to_dict("records")))
    municipios["cd_ibge"] = municipios.cd_ibge.astype("int64")
    return municipios, nacional, tabelas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8, choices=range(1, 9))
    parser.add_argument("--somente-cache", action="store_true")
    args = parser.parse_args()
    config = baixar_json(URL_CONFIG, CACHE / "config.json", args.somente_cache)
    entradas = []
    for abr in config["abr"]:
        uf = abr["cd"].upper()
        if uf not in UFS:
            raise ValueError(f"UF inesperada: {uf}")
        for mun in abr["mu"]:
            cd = str(mun["cd"]).zfill(5)
            if not cd.isdigit():
                raise ValueError("Código TSE inválido")
            entradas.append({"uf": uf, "cd_tse": int(cd), "cd_ibge": int(mun["cdi"]) if uf != "ZZ" else None,
                             "nome": mun["nm"], "url": f"{API}/dados/{uf.lower()}/{uf.lower()}{cd}-c0001-e006258-u.json",
                             "cache": CACHE / uf.lower() / f"{cd}.json"})
    if len({(e["uf"], e["cd_tse"]) for e in entradas}) != len(entradas):
        raise ValueError("Município duplicado na configuração")
    tarefas = entradas + [{"uf": uf, "url": f"{API}/dados/{uf.lower()}/{uf.lower()}-c0001-e006258-u.json",
                           "cache": CACHE / "totais" / f"{uf.lower()}.json"} for uf in sorted(UFS | {"BR"})]
    erros = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futuros = {executor.submit(baixar_json, e["url"], e["cache"], args.somente_cache): e for e in tarefas}
        for numero, futuro in enumerate(as_completed(futuros), 1):
            e = futuros[futuro]
            try:
                e["bruto"] = futuro.result()
            except Exception as erro:
                erros.append({"url": e["url"], "erro": str(erro)})
            if numero % 500 == 0 or numero == len(tarefas):
                print(f"Coleta: {numero}/{len(tarefas)}; falhas: {len(erros)}", flush=True)
    gravar_json(erros, CACHE / "falhas.json")
    if erros:
        raise RuntimeError(f"{len(erros)} arquivos ausentes; consulte o cache/falhas.json e reexecute")
    linhas, manifesto = [], []
    for e in tarefas:
        b = e["bruto"]
        if int(b["ele"]) != 6258 or str(b.get("tf")) != "s":
            raise ValueError(f"Fonte não final da eleição 6258: {e['url']}")
        manifesto.append({"uf": e["uf"], "cd_tse": e.get("cd_tse", ""), "url": e["url"],
                          "arquivo": e["cache"].relative_to(RAIZ).as_posix(),
                          "sha256": hashlib.sha256(e["cache"].read_bytes()).hexdigest(),
                          "atualizado_tse": f"{b['dt']} {b['ht']}"})
        if "cd_tse" in e:
            if int(b["cdabr"]) != e["cd_tse"]:
                raise ValueError("Resposta de outro município")
            linhas.append({"ano": 2026, "uf": e["uf"], "cd_tse": e["cd_tse"], "cd_ibge": e["cd_ibge"],
                           "nome": e["nome"], **normalizar(b)})
    todos = pd.DataFrame(linhas)
    uf26 = todos.groupby(["ano", "uf"], as_index=False)[COLUNAS].sum()
    mun26 = todos[todos.uf.ne("ZZ")].copy()
    mun26["cd_ibge"] = mun26.cd_ibge.astype("int64")
    if mun26.cd_ibge.duplicated().any():
        raise ValueError("IBGE duplicado em 2026")
    cadastro = pd.read_csv(RAIZ / "dados/pbi/municipio.csv")
    if set(mun26.cd_ibge) != set(cadastro.cd_ibge):
        raise ValueError("A cobertura municipal difere do cadastro do painel")
    referencia = pd.read_csv(RAIZ / "dados/apuracao/ufs.csv").set_index("uf")
    ultimo = json.loads((RAIZ / "dados/apuracao/ultimo.json").read_text(encoding="utf-8"))
    provas = []
    for _, r in uf26.iterrows():
        api_uf = normalizar(next(e["bruto"] for e in tarefas if e["uf"] == r.uf and "cd_tse" not in e))
        for campo, origem in ORIGEM.items():
            prova(provas, 2026, "UF municípios x repositório", r.uf, campo, r[campo], referencia.loc[r.uf, origem], "dados/apuracao/ufs.csv:" + origem)
            prova(provas, 2026, "UF municípios x API", r.uf, campo, r[campo], api_uf[campo], next(e["url"] for e in tarefas if e["uf"] == r.uf and "cd_tse" not in e))
    api_br = normalizar(next(e["bruto"] for e in tarefas if e["uf"] == "BR"))
    for campo, origem in ORIGEM.items():
        total = uf26[campo].sum()
        prova(provas, 2026, "Brasil UFs x ultimo", "BR", campo, total, ultimo["brasil"][origem], "dados/apuracao/ultimo.json:brasil." + origem)
        prova(provas, 2026, "Brasil UFs x API", "BR", campo, total, api_br[campo], f"{API}/dados/br/br-c0001-e006258-u.json")
        prova(provas, 2026, "Brasil UFs x linha BR", "BR", campo, total, referencia.loc["BR", origem], "dados/apuracao/ufs.csv:BR." + origem)
    mun22, uf22, raws22 = ler_2022()
    api22 = referencia_2022()
    for campo in COLUNAS:
        prova(provas, 2022, "Brasil CSV x notícia TSE", "BR", campo, uf22[campo].sum(), api22[campo], URL_2022)
    # Caminho independente: somas diretas dos CSV longos, antes do pivot/join/agregação municipal.
    for num, campo in [(13, "pt"), (22, "adv")]:
        direto = sum(int(v) for v in raws22["presidente"].loc[lambda x: x.NR_CANDIDATO.eq(num), "QT_VOTOS_NOMINAIS_VALIDOS"])
        prova(provas, 2022, "Brasil soma direta x exportação", "BR", campo, uf22[campo].sum(), direto, "dados/bruto/tse/presidente_2022_BR.csv:QT_VOTOS_NOMINAIS_VALIDOS")
    for origem, campo in [("QT_APTOS", "aptos"), ("QT_COMPARECIMENTO", "comparecimento"), ("QT_ABSTENCOES", "abstencoes"),
                          ("QT_VOTOS_BRANCOS", "brancos"), ("QT_TOTAL_VOTOS_NULOS", "nulos"), ("QT_TOTAL_VOTOS_VALIDOS", "validos")]:
        prova(provas, 2022, "Brasil soma direta x exportação", "BR", campo, uf22[campo].sum(), sum(map(int, raws22["detalhe"][origem])), "dados/bruto/tse/detalhe_2022_BR.csv:" + origem)
    tabela_provas = pd.DataFrame(provas)
    gravar_csv(tabela_provas, SAIDA / "prova_totais.csv")
    manifesto.append({"uf": "", "cd_tse": "", "url": URL_CONFIG,
                      "arquivo": (CACHE / "config.json").relative_to(RAIZ).as_posix(),
                      "sha256": hashlib.sha256((CACHE / "config.json").read_bytes()).hexdigest(),
                      "atualizado_tse": f"{config.get('dg', '')} {config.get('hg', '')}".strip()})
    gravar_csv(pd.DataFrame(manifesto).sort_values(["uf", "cd_tse"], key=lambda s: s.astype(str)), SAIDA / "fontes_coleta.csv")
    gravar_csv(pd.DataFrame([{"arquivo": f"dados/bruto/tse/{prefixo}_2022_BR.csv",
                              "url": f"https://cdn.tse.jus.br/estatistica/sead/odsele/{pasta}/{pasta}_2022.zip",
                              "sha256": hashlib.sha256((RAIZ / f"dados/bruto/tse/{prefixo}_2022_BR.csv").read_bytes()).hexdigest(),
                              "filtro": "NR_TURNO=2; CD_CARGO=1; membro com sufixo _BR.csv"}
                             for prefixo, pasta in [("presidente", "votacao_candidato_munzona"), ("detalhe", "detalhe_votacao_munzona")]]),
               SAIDA / "fontes_brutos_2022.csv")
    if not tabela_provas.bate.all():
        print(tabela_provas[~tabela_provas.bate].to_string(index=False))
        raise ValueError("Totais divergentes: os CSV do painel não foram gravados")
    municipios = pd.concat([mun22, mun26], ignore_index=True)
    ufs = pd.concat([uf22, uf26], ignore_index=True)
    if municipios.duplicated(["ano", "cd_ibge"]).any() or ufs.duplicated(["ano", "uf"]).any():
        raise ValueError("Chave duplicada no resultado")
    for tabela in [municipios, ufs]:
        if (tabela[COLUNAS] < 0).any().any() or not tabela.pt.add(tabela.adv).eq(tabela.validos).all():
            raise ValueError("Contagens inválidas")
        if not tabela.validos.add(tabela.brancos).add(tabela.nulos).eq(tabela.comparecimento).all():
            raise ValueError("Votos não fecham com comparecimento")
    # O eleitorado não precisa ser presença + abstenção: as fontes têm resíduos,
    # registrados por município e por UF, sem redistribuir ou completar valores.
    residuos = pd.concat([municipios.assign(nivel="município", local=municipios.cd_ibge.astype(str)),
                          ufs.assign(nivel="UF", local=ufs.uf)], ignore_index=True)
    residuos["aptos_menos_presenca_abstencao"] = residuos.aptos - residuos.comparecimento - residuos.abstencoes
    gravar_csv(residuos[["ano", "nivel", "local", "aptos", "comparecimento", "abstencoes", "aptos_menos_presenca_abstencao"]], SAIDA / "residuos_eleitorado.csv")
    gravar_csv(todos[todos.uf.eq("ZZ")].drop(columns="cd_ibge"), SAIDA / "exterior_2turno_2026.csv")
    gravar_csv(municipios[["ano", "cd_ibge"] + COLUNAS].astype("int64").sort_values(["ano", "cd_ibge"]), RAIZ / "dados/pbi/municipio_2turno.csv")
    gravar_csv(ufs[["ano", "uf"] + COLUNAS].sort_values(["ano", "uf"]), RAIZ / "dados/pbi/uf_2turno.csv")
    resumo = {"provas": len(provas), "todas_batem": True, "municipios_por_ano": municipios.groupby("ano").size().to_dict(),
              "ufs_por_ano": ufs.groupby("ano").size().to_dict(), "exterior_cidades_2026": int(todos.uf.eq("ZZ").sum()),
              "totais": ufs.groupby("ano")[COLUNAS].sum().reset_index().to_dict("records"),
              "comando": "python -I -X utf8 pipeline/exportar_2turno.py"}
    gravar_json(resumo, SAIDA / "exportacao_resumo.json")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
