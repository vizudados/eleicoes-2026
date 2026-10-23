"""Coletor da apuração em tempo real (TSE, API pública de divulgação de resultados).

Lê o arquivo de presidente do Brasil e das 27 UFs (`<ciclo>/<eleição>/dados/<uf>/<uf>-c0001-e<eleição>-u.json`),
normaliza e grava em `dados/apuracao/`:
- `ultimo.json`    o retrato atual (Brasil + UFs), com o status da apuração;
- `ufs.csv`        uma linha por UF (e uma "BR"), pronta para o Power BI;
- `historico.csv`  uma linha por atualização do TSE (só acrescenta quando a hora de totalização muda), para a curva
                   de "como a apuração andou" ao longo da noite.
É o que o GitHub Actions roda (`.github/workflows/apuracao.yml`). Sem dependências fora da biblioteca padrão.

Uso:
  python -I apuracao/coletar.py                         # 2º turno de 2026 (eleição 6258), uma coleta
  python -I apuracao/coletar.py --eleicao 6257          # 1º turno (ensaio com o resultado final)
  python -I apuracao/coletar.py --repetir 4 --intervalo 60   # 4 coletas, uma por minuto
"""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://resultados.tse.jus.br/oficial/{ciclo}/{eleicao}/dados/{uf}/{uf}-c0001-e{eleicao:06d}-u.json"
UFS = ["br", "ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr",
       "rj", "rn", "ro", "rr", "rs", "sc", "se", "sp", "to", "zz"]
BRASILIA = timezone(timedelta(hours=-3))
CAMPOS_UF = ["uf", "atualizado_tse", "secoes_pct", "eleitorado", "comparecimento", "abstencao", "abstencao_pct",
             "brancos", "nulos", "validos", "lula_votos", "lula_pct", "flavio_votos", "flavio_pct", "lider", "diferenca_votos",
             "secoes_total", "secoes_totalizadas", "eleitorado_apurado"]
# Seções e eleitorado das seções totalizadas vêm em número absoluto para que a soma de várias UFs (uma região, o filtro do
# painel) dê o percentual certo; o pst e o pa do TSE só valem para a UF em que foram calculados.
CAMPOS_HISTORICO = ["coletado_em", "atualizado_tse", "secoes_pct", "lula_votos", "lula_pct", "flavio_votos", "flavio_pct",
                    "brancos", "nulos", "abstencao", "validos", "secoes_totalizadas", "secoes_total"]


def numero(txt):
    """'47,03' → 47.03; '' → None."""
    if txt in (None, ""):
        return None
    return float(str(txt).replace(".", "").replace(",", ".")) if "," in str(txt) else float(txt)


def baixar(url, tentativas=3):
    pedido = urllib.request.Request(url, headers={"User-Agent": "VizuDados-Apuracao/1.0 (+https://vizudados.com.br)"})
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(pedido, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if i == tentativas - 1:
                return None
            time.sleep(2 * (i + 1))


def candidatos(bruto):
    saida = []
    for agr in bruto["carg"][0]["agr"]:
        for par in agr["par"]:
            for c in par["cand"]:
                saida.append({"numero": int(c["n"]), "nome": c["nmu"].title(), "partido": par["sg"],
                              "votos": int(c["vap"] or 0), "pct": numero(c["pvap"]) or 0.0,
                              "eleito": c.get("e") == "s", "situacao": c.get("st", "")})
    return sorted(saida, key=lambda c: -c["votos"])


def resumo(bruto, uf):
    s, e, v = bruto["s"], bruto["e"], bruto["v"]
    cands = candidatos(bruto)
    por_numero = {c["numero"]: c for c in cands}
    lula, flavio = por_numero.get(13, {}), por_numero.get(22, {})
    hora = f"{bruto.get('dt', '')} {bruto.get('ht', '')}".strip()
    return {
        "uf": uf.upper(), "atualizado_tse": hora, "secoes_pct": numero(s.get("pst")) or 0.0,
        "eleitorado": int(e.get("te") or 0), "comparecimento": int(e.get("c") or 0), "abstencao": int(e.get("a") or 0),
        "abstencao_pct": numero(e.get("pa")) or 0.0, "brancos": int(v.get("vb") or 0), "nulos": int(v.get("tvn") or 0),
        "validos": int(v.get("vv") or 0),
        "lula_votos": lula.get("votos", 0), "lula_pct": lula.get("pct", 0.0),
        "flavio_votos": flavio.get("votos", 0), "flavio_pct": flavio.get("pct", 0.0),
        "lider": ("Lula" if lula.get("votos", 0) > flavio.get("votos", 0) else
                  "Flávio" if flavio.get("votos", 0) > lula.get("votos", 0) else "—"),
        "diferenca_votos": abs(lula.get("votos", 0) - flavio.get("votos", 0)),
        "secoes_total": int(s.get("ts") or 0), "secoes_totalizadas": int(s.get("st") or 0),
        "eleitorado_apurado": int(e.get("est") or 0),
        "candidatos": cands, "totalizacao_final": bruto.get("tf") == "s",
    }


def status(br):
    if br["secoes_pct"] == 0:
        return "aguardando"
    if any(c["eleito"] and c["situacao"].lower().startswith("eleito") for c in br["candidatos"]):
        return "definido" if br["secoes_pct"] < 100 else "encerrada"
    return "encerrada" if br["secoes_pct"] >= 100 else "apurando"


CONFIG_MUN = "https://resultados.tse.jus.br/oficial/{ciclo}/{eleicao}/config/mun-e{eleicao:06d}-cm.json"
BASE_MUN = "https://resultados.tse.jus.br/oficial/{ciclo}/{eleicao}/dados/zz/zz{cd}-c0001-e{eleicao:06d}-u.json"
CAMPOS_EXT = ["cd", "cidade", "pais", "continente", "atualizado_tse", "secoes_pct", "secoes_total", "secoes_totalizadas",
              "validos", "lula_votos", "flavio_votos"]


def coletar_exterior(ciclo, eleicao, pasta):
    """As 186 cidades do exterior, uma por arquivo da API, ligadas ao país (o TSE não publica o país; a tabela é
    dados/bruto/exterior/cidade_pais.csv). Grava exterior.csv; o painel agrega por país no tooltip do exterior."""
    config = baixar(CONFIG_MUN.format(ciclo=ciclo, eleicao=eleicao))
    if not config:
        print("exterior: sem a lista de cidades do TSE; exterior.csv mantido", file=sys.stderr)
        return
    cidades = next((a["mu"] for a in config["abr"] if a["cd"].lower() == "zz"), [])
    mapa = {}
    with open(RAIZ / "dados" / "bruto" / "exterior" / "cidade_pais.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            mapa[r["cd_tse"]] = mapa[r["cidade"]] = (r["pais"], r["continente"])
    urls = [BASE_MUN.format(ciclo=ciclo, eleicao=eleicao, cd=m["cd"]) for m in cidades]
    with ThreadPoolExecutor(12) as ex:
        brutos = list(ex.map(baixar, urls))
    linhas = []
    for m, b in zip(cidades, brutos):
        if not b:
            continue
        s_, v = b["s"], b["v"]
        por_numero = {c["numero"]: c for c in candidatos(b)}
        pais, continente = mapa.get(m["cd"]) or mapa.get(m["nm"]) or ("?", "?")
        linhas.append({"cd": m["cd"], "cidade": m["nm"].title(), "pais": pais, "continente": continente,
                       "atualizado_tse": f"{b.get('dt', '')} {b.get('ht', '')}".strip(),
                       "secoes_pct": numero(s_.get("pst")) or 0.0, "secoes_total": int(s_.get("ts") or 0),
                       "secoes_totalizadas": int(s_.get("st") or 0), "validos": int(v.get("vv") or 0),
                       "lula_votos": por_numero.get(13, {}).get("votos", 0),
                       "flavio_votos": por_numero.get(22, {}).get("votos", 0)})
    with open(pasta / "exterior.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_EXT)
        w.writeheader()
        w.writerows(sorted(linhas, key=lambda l: (l["pais"], l["cidade"])))
    print(f"exterior: {len(linhas)} de {len(cidades)} cidades")


def coletar(ciclo, eleicao, pasta):
    urls = {uf: BASE.format(ciclo=ciclo, eleicao=eleicao, uf=uf) for uf in UFS}
    with ThreadPoolExecutor(8) as ex:
        brutos = dict(zip(urls, ex.map(baixar, urls.values())))
    if not brutos.get("br"):
        print("falha ao baixar o arquivo do Brasil; nada gravado", file=sys.stderr)
        return False
    linhas = [resumo(b, uf) for uf, b in brutos.items() if b]
    br = next(l for l in linhas if l["uf"] == "BR")
    agora = datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M:%S")
    retrato = {"eleicao": eleicao, "turno": int(brutos["br"]["t"]), "coletado_em": agora,
               "atualizado_tse": br["atualizado_tse"], "status": status(br), "brasil": br,
               "ufs": [l for l in linhas if l["uf"] != "BR"],
               "fonte": "TSE · resultados.tse.jus.br (API pública de divulgação)",
               "faltaram": sorted(uf.upper() for uf, b in brutos.items() if not b)}
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "ultimo.json").write_text(json.dumps(retrato, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(pasta / "ufs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_UF, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)
    # O histórico existe desde a primeira coleta (só o cabeçalho enquanto o TSE não divulga), para o Power BI nunca
    # pedir um arquivo que ainda não está no repositório; ganha uma linha a cada nova hora de totalização.
    historico = pasta / "historico.csv"
    ultima_hora = ""
    if historico.exists():
        with open(historico, encoding="utf-8") as f:
            ultimas = list(csv.DictReader(f))
            ultima_hora = ultimas[-1]["atualizado_tse"] if ultimas else ""
    else:
        with open(historico, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CAMPOS_HISTORICO)
    if br["atualizado_tse"] and br["atualizado_tse"] != ultima_hora:
        with open(historico, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CAMPOS_HISTORICO, extrasaction="ignore").writerow({**br, "coletado_em": agora})
    coletar_exterior(ciclo, eleicao, pasta)
    print(f"{agora} · eleição {eleicao} · {retrato['status']} · {br['secoes_pct']}% das seções · "
          f"Lula {br['lula_pct']}% × Flávio {br['flavio_pct']}% · UFs: {len(retrato['ufs'])} · faltaram: {retrato['faltaram']}")
    return True


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--ciclo", default="ele2026")
    a.add_argument("--eleicao", type=int, default=6258)
    a.add_argument("--saida", default=str(RAIZ / "dados" / "apuracao"))
    a.add_argument("--repetir", type=int, default=1)
    a.add_argument("--intervalo", type=int, default=60)
    args = a.parse_args()
    for i in range(args.repetir):
        coletar(args.ciclo, args.eleicao, Path(args.saida))
        if i + 1 < args.repetir:
            time.sleep(args.intervalo)
