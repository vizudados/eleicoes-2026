"""Baixa do IBGE o que o mockup cruza com o voto: municípios, população e renda do Censo 2022 e as malhas.

Saídas em `dados/bruto/ibge/`:
- `municipios.json`     localidades (código IBGE de 7 dígitos, nome, UF, região)
- `populacao_2022.json` SIDRA 4709 · v93 · população residente, Censo 2022
- `renda_2022.json`     SIDRA 10295 · v13431 · rendimento nominal médio mensal domiciliar per capita, Censo 2022
- `malha_municipios.json` e `malha_uf.json`  TopoJSON da API de malhas v3 (qualidade intermediária)

Uso: python -I pipeline/extrair_ibge.py
"""
import gzip
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "dados" / "bruto" / "ibge"

FONTES = {
    "municipios.json": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
    "populacao_2022.json": "https://apisidra.ibge.gov.br/values/t/4709/n6/all/v/93/p/2022",
    "renda_2022.json": "https://apisidra.ibge.gov.br/values/t/10295/n6/all/v/13431/p/2022/c2/6794/c86/95251/c58/95253",
    "malha_municipios.json": "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
                             "?intrarregiao=municipio&qualidade=intermediaria&formato=application/json",
    "malha_uf.json": "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
                     "?intrarregiao=UF&qualidade=intermediaria&formato=application/json",
}


def baixar(url):
    pedido = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    with urllib.request.urlopen(pedido, timeout=300) as r:
        corpo = r.read()
    return gzip.decompress(corpo) if corpo[:2] == b"\x1f\x8b" else corpo


if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, url in FONTES.items():
        corpo = baixar(url)
        (SAIDA / nome).write_bytes(corpo)
        print(f"{nome}: {len(corpo):,} bytes")
