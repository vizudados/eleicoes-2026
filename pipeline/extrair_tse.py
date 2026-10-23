"""Extrai do TSE os arquivos de presidente (membro `_BR`), de 2006 a 2026, sem baixar o zip inteiro.

Os zips do TSE trazem todos os cargos (centenas de MB). Este script lê o zip remoto por pedaços (HTTP Range): baixa
só o diretório central e o membro `_BR` (presidente). Bases:
- `votacao` (padrão): `votacao_candidato_munzona_<ano>.zip` -> `dados/bruto/tse/presidente_<ano>_BR.csv`
- `detalhe`: `detalhe_votacao_munzona_<ano>.zip` (aptos, comparecimento, abstenção, brancos, nulos)
  -> `dados/bruto/tse/detalhe_<ano>_BR.csv`

Uso: python -I pipeline/extrair_tse.py [--listar] [--base detalhe] [ano ...]
"""
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "dados" / "bruto" / "tse"
BASES = {"votacao": ("votacao_candidato_munzona", "presidente"), "detalhe": ("detalhe_votacao_munzona", "detalhe")}
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/{pasta}/{pasta}_{ano}.zip"
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]
BLOCO = 4 * 1024 * 1024


class ArquivoRemoto(io.RawIOBase):
    """Arquivo somente leitura sobre HTTP Range, com cache de um bloco."""

    def __init__(self, url):
        self.url = url
        self.pos = 0
        pedido = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(pedido, timeout=60) as r:
            self.tamanho = int(r.headers["Content-Length"])
        self.cache_ini, self.cache = -1, b""
        self.baixado = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, deslocamento, origem=0):
        base = {0: 0, 1: self.pos, 2: self.tamanho}[origem]
        self.pos = max(0, base + deslocamento)
        return self.pos

    def _buscar(self, ini):
        fim = min(self.tamanho, ini + BLOCO) - 1
        pedido = urllib.request.Request(self.url, headers={"Range": f"bytes={ini}-{fim}"})
        with urllib.request.urlopen(pedido, timeout=120) as r:
            self.cache = r.read()
        self.cache_ini = ini
        self.baixado += len(self.cache)

    def readinto(self, destino):
        if self.pos >= self.tamanho:
            return 0
        if not (self.cache_ini <= self.pos < self.cache_ini + len(self.cache)):
            self._buscar(self.pos)
        ini = self.pos - self.cache_ini
        pedaco = self.cache[ini:ini + len(destino)]
        destino[:len(pedaco)] = pedaco
        self.pos += len(pedaco)
        return len(pedaco)


def membro_br(nomes):
    candidatos = [n for n in nomes if n.upper().endswith("_BR.CSV")]
    if len(candidatos) != 1:
        raise SystemExit(f"esperava um membro _BR.csv, achei {candidatos}")
    return candidatos[0]


def extrair(ano, listar=False, base="votacao"):
    pasta, prefixo = BASES[base]
    remoto = ArquivoRemoto(URL.format(pasta=pasta, ano=ano))
    with zipfile.ZipFile(io.BufferedReader(remoto, buffer_size=BLOCO)) as z:
        if listar:
            for info in z.infolist():
                print(f"{ano}  {info.file_size:>12,}  {info.compress_size:>12,}  {info.filename}")
            return
        nome = membro_br(z.namelist())
        destino = SAIDA / f"{prefixo}_{ano}_BR.csv"
        SAIDA.mkdir(parents=True, exist_ok=True)
        with z.open(nome) as origem, open(destino, "wb") as saida:
            while pedaco := origem.read(BLOCO):
                saida.write(pedaco)
    print(f"{ano}: {nome} -> {destino.name} ({destino.stat().st_size:,} bytes; baixados {remoto.baixado:,} de {remoto.tamanho:,})")


if __name__ == "__main__":
    args = sys.argv[1:]
    listar = "--listar" in args
    base = args[args.index("--base") + 1] if "--base" in args else "votacao"
    anos = [int(a) for a in args if a.isdigit()] or ANOS
    for ano in anos:
        extrair(ano, listar, base)
