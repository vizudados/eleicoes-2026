"""Abstenção por perfil do eleitor (1º turno, 2014–2026): faixa etária, gênero e escolaridade.

Lê o membro `_BRASIL` de `perfil_comparecimento_abstencao_<ano>.zip` do TSE em fluxo (HTTP Range + leitura por
blocos), filtra o 1º turno e soma aptos, comparecimento e abstenção por perfil, sem gravar o arquivo bruto (3 GB
descomprimido). Antes de 2014 o TSE não publica esta base.
Saída: `dados/saida/abstencao_perfil.csv` (ano, dimensão, categoria, aptos, comparecimento, abstenção).

Uso: python -I -X utf8 pipeline/extrair_perfil_abstencao.py [ano ...]
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extrair_tse import BLOCO, ArquivoRemoto  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "dados" / "saida" / "abstencao_perfil.csv"
URL = ("https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_comparecimento_abstencao/"
       "perfil_comparecimento_abstencao_{ano}.zip")
ANOS = [2014, 2018, 2022, 2026]
# O nome da coluna de escolaridade mudou ao longo dos anos; vale a primeira que existir.
DIMENSOES = {"faixa_etaria": ["DS_FAIXA_ETARIA"], "genero": ["DS_GENERO"],
             "escolaridade": ["DS_GRAU_INSTRUCAO", "DS_GRAU_ESCOLARIDADE"]}


def agregar(ano):
    remoto = ArquivoRemoto(URL.format(ano=ano))
    with zipfile.ZipFile(io.BufferedReader(remoto, buffer_size=BLOCO)) as z:
        nome = next(n for n in z.namelist() if n.upper().endswith("_BRASIL.CSV"))
        with z.open(nome) as bruto:
            leitor = pd.read_csv(io.TextIOWrapper(bruto, encoding="latin1"), sep=";", dtype=str, chunksize=500_000)
            partes = []
            for bloco in leitor:
                bloco = bloco[bloco["NR_TURNO"] == "1"]
                qt_abst = "QT_ABSTENCAO" if "QT_ABSTENCAO" in bloco else "QT_ABSTENCOES"
                for c in ("QT_APTOS", "QT_COMPARECIMENTO", qt_abst):
                    bloco[c] = pd.to_numeric(bloco[c], errors="coerce").fillna(0)
                for dim, opcoes in DIMENSOES.items():
                    col = next(c for c in opcoes if c in bloco)
                    g = bloco.groupby(col)[["QT_APTOS", "QT_COMPARECIMENTO", qt_abst]].sum().reset_index()
                    g.columns = ["categoria", "aptos", "comparecimento", "abstencao"]
                    g["dimensao"] = dim
                    partes.append(g)
    soma = pd.concat(partes).groupby(["dimensao", "categoria"], as_index=False).sum()
    soma.insert(0, "ano", ano)
    soma["pct_abstencao"] = soma.abstencao / soma.aptos
    print(f"{ano}: {nome} · baixados {remoto.baixado / 1e6:,.0f} MB · aptos {soma[soma.dimensao == 'genero'].aptos.sum():,.0f}")
    return soma


if __name__ == "__main__":
    anos = [int(a) for a in sys.argv[1:] if a.isdigit()] or ANOS
    novos = pd.concat([agregar(a) for a in anos])
    if SAIDA.exists():
        antigos = pd.read_csv(SAIDA)
        novos = pd.concat([antigos[~antigos.ano.isin(anos)], novos])
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    novos.sort_values(["ano", "dimensao", "categoria"]).to_csv(SAIDA, index=False)
    print(f"gravado {SAIDA}")
