"""Pesquisa reproduzível das publicações TSE e recorte de seções do Brief F.

Uso: python -I -X utf8 pipeline/brief_f_publicacoes.py [--somente-cache] [--cache-novo nome]
Grava apenas arquivos novos no cache brief_f e saídas com prefixo brief_f/t20.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extrair_secoes import CIDADES_T20
from extrair_tse import BLOCO
from exportar_2turno import gravar_csv, gravar_json

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / "dados/bruto/tse/brief_f"
SAIDA = RAIZ / "dados/saida/2turno"
BASE = "https://cdn.tse.jus.br/estatistica/sead/odsele/"


def obter(url, nome, somente_cache, limite=800_000_000):
    destino = CACHE / nome
    if destino.exists():
        return destino
    if somente_cache:
        raise FileNotFoundError(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    pedido = urllib.request.Request(url, headers={"User-Agent": "VizuDados-BriefF/1.0"})
    with urllib.request.urlopen(pedido, timeout=60) as r, destino.with_suffix(destino.suffix + ".parcial").open("wb") as f:
        total = 0
        while pedaco := r.read(BLOCO):
            total += len(pedaco)
            if total > limite:
                raise ValueError("Download excedeu o limite declarado")
            f.write(pedaco)
    destino.with_suffix(destino.suffix + ".parcial").replace(destino)
    return destino


def secao(ano, arquivo):
    cidades = {(uf, int(cd)): (ibge, nome) for uf, cd, ibge, nome in CIDADES_T20}
    contagem, partes, total_linhas = Counter(), [], 0
    with zipfile.ZipFile(arquivo) as z:
        nome = next(n for n in z.namelist() if n.upper().endswith("_BR.CSV"))
        with z.open(nome) as f:
            colunas = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_CARGO",
                       "NR_VOTAVEL", "QT_VOTOS", "NR_LOCAL_VOTACAO"]
            for b in pd.read_csv(f, sep=";", encoding="latin1", usecols=colunas, chunksize=400_000):
                contagem.update({int(k): int(v) for k, v in b.NR_TURNO.value_counts().items()})
                total_linhas += len(b)
                alvo = pd.MultiIndex.from_arrays([b.SG_UF, b.CD_MUNICIPIO]).isin(cidades)
                p = b[alvo & b.NR_TURNO.eq(2) & b.CD_CARGO.eq(1)]
                if not p.empty:
                    partes.append(p)
                if total_linhas % 2_000_000 == 0:
                    print(f"Seções {ano}: {total_linhas:,} linhas lidas", flush=True)
    if partes:
        d = pd.concat(partes, ignore_index=True)
        chaves = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_VOTAVEL"]
        if d.duplicated(chaves).any():
            raise ValueError("Seção/candidato duplicado no recorte")
        d = d.rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "cd_tse", "NR_ZONA": "zona",
                              "NR_SECAO": "secao", "NR_VOTAVEL": "numero", "QT_VOTOS": "votos",
                              "NR_LOCAL_VOTACAO": "local"})
        d["cd_ibge"] = [cidades[(uf, cd)][0] for uf, cd in zip(d.uf, d.cd_tse)]
        d["ano"], d["turno"] = ano, 2
        d = d[["ano", "turno", "uf", "cd_tse", "cd_ibge", "zona", "secao", "local", "numero", "votos"]]
        d = d.sort_values(["uf", "cd_ibge", "zona", "secao", "numero"])
        gravar_csv(d, SAIDA / f"t20_secoes_2turno_{ano}.csv")
        for num, campo in [(13, "pt"), (22, "adv"), (95, "brancos"), (96, "nulos")]:
            d[campo] = d.votos.where(d.numero.eq(num), 0)
        d["validos"] = d.votos.where(d.numero.isin([13, 22]), 0)
        if not d.numero.isin([13, 22, 95, 96]).all():
            raise ValueError("Número de votável inesperado no segundo turno")
        zonas = d.groupby(["ano", "turno", "uf", "cd_tse", "cd_ibge", "zona"], as_index=False).agg(
            pt=("pt", "sum"), adv=("adv", "sum"), validos=("validos", "sum"),
            brancos=("brancos", "sum"), nulos=("nulos", "sum"), secoes=("secao", "nunique"), locais=("local", "nunique"))
        zonas["cidade"] = [cidades[(uf, cd)][1] + f" ({uf})" for uf, cd in zip(zonas.uf, zonas.cd_tse)]
        gravar_csv(zonas, SAIDA / f"t20_zonas_2turno_{ano}.csv")
        # Dois controles: município publicado e soma direta do bruto munzona por zona.
        publicado = pd.read_csv(RAIZ / "dados/pbi/municipio_2turno.csv")
        publicado = publicado[publicado.ano.eq(ano)].set_index("cd_ibge")
        raw = pd.read_csv(RAIZ / f"dados/bruto/tse/presidente_{ano}_BR.csv", sep=";", encoding="latin1")
        raw = raw[raw.NR_TURNO.eq(2) & raw.CD_CARGO.eq(1)]
        provas = []
        for (uf, cd, ibge), g in zonas.groupby(["uf", "cd_tse", "cd_ibge"]):
            for campo in ["pt", "adv", "validos", "brancos", "nulos"]:
                obtido, esperado = int(g[campo].sum()), int(publicado.loc[int(ibge), campo])
                provas.append({"ano": ano, "nivel": "cidade", "uf": uf, "cd_ibge": ibge, "zona": "",
                               "campo": campo, "obtido": obtido, "esperado": esperado, "diferenca": obtido - esperado})
            for r in g.itertuples():
                b = raw[raw.SG_UF.eq(uf) & raw.CD_MUNICIPIO.eq(cd) & raw.NR_ZONA.eq(r.zona)]
                for campo, num in [("pt", 13), ("adv", 22)]:
                    esperado = int(b.loc[b.NR_CANDIDATO.eq(num), "QT_VOTOS_NOMINAIS_VALIDOS"].sum())
                    obtido = int(getattr(r, campo))
                    provas.append({"ano": ano, "nivel": "zona", "uf": uf, "cd_ibge": ibge, "zona": r.zona,
                                   "campo": campo, "obtido": obtido, "esperado": esperado, "diferenca": obtido - esperado})
        p = pd.DataFrame(provas)
        gravar_csv(p, SAIDA / f"brief_f_prova_zonas_{ano}.csv")
        if p.diferenca.ne(0).any() or zonas.cd_ibge.nunique() != 34:
            raise ValueError("Recorte das zonas não passou pela prova")
        print(f"Seções {ano}: {len(d):,} linhas; {len(zonas)} zonas; {len(p)} provas sem diferença", flush=True)
    return {"linhas_por_turno": dict(sorted(contagem.items())), "linhas_2turno_34_cidades": sum(map(len, partes))}


def perfil(arquivo):
    turnos, datas, partes_perfil, partes_municipio = Counter(), Counter(), [], []
    with zipfile.ZipFile(arquivo) as z:
        nome = next(n for n in z.namelist() if n.upper().endswith("_BRASIL.CSV"))
        with z.open(nome) as f:
            cols = ["DT_GERACAO", "NR_TURNO", "SG_UF", "CD_MUNICIPIO", "DS_FAIXA_ETARIA", "DS_GENERO",
                    "DS_GRAU_INSTRUCAO", "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]
            total = 0
            for b in pd.read_csv(f, sep=";", encoding="latin1", usecols=cols, chunksize=500_000):
                turnos.update({int(k): int(v) for k, v in b.NR_TURNO.value_counts().items()})
                datas.update({str(k): int(v) for k, v in b.DT_GERACAO.value_counts().items()})
                b = b[b.NR_TURNO.eq(2)]
                campos = ["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]
                if not b.empty:
                    for dim, col in [("faixa_etaria", "DS_FAIXA_ETARIA"), ("genero", "DS_GENERO"), ("escolaridade", "DS_GRAU_INSTRUCAO")]:
                        p = b.groupby(col, as_index=False)[campos].sum().rename(columns={col: "categoria"})
                        p["dimensao"] = dim
                        partes_perfil.append(p)
                    partes_municipio.append(b.groupby(["SG_UF", "CD_MUNICIPIO", "DS_FAIXA_ETARIA"], as_index=False)[campos].sum())
                total += 500_000
                if total % 2_000_000 == 0:
                    print(f"Perfil 2026: até {total:,} linhas lidas", flush=True)
    # Se a publicação passar a conter o 2º turno, exige validação adicional antes de exportar perfis.
    if partes_perfil:
        raise RuntimeError("Perfil do segundo turno agora disponível: implementar a conferência municipal antes de publicar")
    return {"linhas_por_turno": dict(sorted(turnos.items())), "datas_geracao": dict(datas), "perfil_2turno_disponivel": False}


def main():
    global CACHE
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--somente-cache", action="store_true")
    p.add_argument("--cache-novo", help="Nome de pasta inédita em dados/bruto/tse para uma nova consulta ao servidor")
    args = p.parse_args()
    if args.cache_novo:
        if not re.fullmatch(r"brief_f_[a-z0-9_-]+", args.cache_novo):
            p.error("--cache-novo deve começar por brief_f_ e conter apenas a-z, 0-9, _ e -")
        CACHE = CACHE.parent / args.cache_novo
        if CACHE.exists():
            p.error("--cache-novo exige uma pasta que ainda não existe")
    pesquisa = {"executado_utc": datetime.now(timezone.utc).isoformat(),
                "modo": "releitura do cache" if args.somente_cache else "download somente se ausente",
                "cache": CACHE.relative_to(RAIZ).as_posix(), "arquivos": [], "catalogos": []}
    for slug in ["comparecimento-e-abstencao-2026", "resultados-2026", "resultados-2026-boletim-de-urna"]:
        url = "https://dadosabertos.tse.jus.br/api/3/action/package_show?id=" + slug
        try:
            arq = obter(url, slug + ".json", args.somente_cache, 10_000_000)
            obj = json.loads(arq.read_text(encoding="utf-8"))["result"]
            recursos = [{k: r.get(k) for k in ["name", "url", "last_modified", "created"]} for r in obj["resources"]]
            pesquisa["catalogos"].append({"url": url, "arquivo": str(arq.relative_to(RAIZ)),
                                         "metadata_modified": obj.get("metadata_modified"), "recursos": recursos})
            print(slug, [(r["name"], r["url"]) for r in recursos if "segundo" in (r["name"] or "").lower()], flush=True)
        except (urllib.error.HTTPError, json.JSONDecodeError, KeyError) as exc:
            pesquisa["catalogos"].append({"url": url, "erro": str(exc)})
    for tipo, ano in [("perfil_comparecimento_abstencao", 2026), ("votacao_secao", 2026), ("votacao_secao", 2022)]:
        nome = f"{tipo}_{ano}" + ("_BR" if tipo == "votacao_secao" else "") + ".zip"
        url = BASE + tipo + "/" + nome
        print("Lendo", nome, flush=True)
        arquivo = obter(url, nome, args.somente_cache)
        with zipfile.ZipFile(arquivo) as z:
            membros = [{"nome": i.filename, "bytes": i.file_size, "data_zip": list(i.date_time)} for i in z.infolist()]
        resumo = secao(ano, arquivo) if tipo == "votacao_secao" else perfil(arquivo)
        with arquivo.open("rb") as fonte:
            sha256 = hashlib.file_digest(fonte, "sha256").hexdigest()
        pesquisa["arquivos"].append({"url": url, "arquivo": arquivo.relative_to(RAIZ).as_posix(),
                                    "sha256": sha256,
                                    "bytes": arquivo.stat().st_size, "membros": membros, **resumo})
        gravar_json(pesquisa, SAIDA / "brief_f_publicacoes.json")
    print("Pesquisa concluída", flush=True)


if __name__ == "__main__":
    main()
