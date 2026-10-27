"""T20: lê o segundo turno nas seções oficiais de 2018 das 34 cidades.

HTTP Range + descompressão em fluxo: nenhum ZIP é extraído no disco. Só as linhas
das cidades/cargo/turno autorizados são conservadas em pbi/qa/p2/fase2/secoes2018.
O CSV novo só é gravado após as provas por município e por zona passarem.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import struct
import urllib.request
import zipfile
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
QA = RAIZ / "pbi/qa/p2/fase2"
CACHE = QA / "secoes2018"
DESTINO = RAIZ / "dados/pbi/t20_zonas_2turno_2018.csv"
COLS = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_CARGO", "NR_VOTAVEL", "QT_VOTOS"]


class Remoto(io.RawIOBase):
    def __init__(self, url):
        self.url, self.pos = url, 0
        with self.abrir(0, 0) as r:
            self.tamanho = int(r.headers["Content-Range"].split("/")[-1])

    def abrir(self, ini, fim):
        r = urllib.request.urlopen(urllib.request.Request(self.url, headers={
            "User-Agent": "Mozilla/5.0", "Range": f"bytes={ini}-{fim}"}), timeout=90)
        if r.status != 206 or not r.headers.get("Content-Range", "").startswith(f"bytes {ini}-"):
            r.close()
            raise RuntimeError("Faixa HTTP não atendida: " + self.url)
        return r

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = offset + (self.pos if whence == 1 else self.tamanho if whence == 2 else 0)
        return self.pos

    def read(self, n=-1):
        n = self.tamanho-self.pos if n < 0 else min(n, self.tamanho-self.pos)
        if n <= 0:
            return b""
        with self.abrir(self.pos, self.pos+n-1) as r:
            b = r.read(n)
        self.pos += len(b)
        return b


class ComHash:
    def __init__(self, resposta):
        self.resposta, self.sha, self.n = resposta, hashlib.sha256(), 0

    def read(self, n=-1):
        b = self.resposta.read(n)
        self.sha.update(b)
        self.n += len(b)
        return b

    def seekable(self):
        return False


def coletar(uf, codigos):
    arquivo, manifesto = CACHE/f"{uf}.csv", CACHE/f"{uf}.json"
    if arquivo.exists() and manifesto.exists():
        info = json.loads(manifesto.read_text(encoding="utf-8"))
        if info["csv_sha256"] == hashlib.sha256(arquivo.read_bytes()).hexdigest():
            print(uf, "cache conferido", info["linhas_selecionadas"], flush=True)
            return info
    url = f"https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2018_{uf}.zip"
    remoto = Remoto(url)
    with zipfile.ZipFile(remoto) as z:
        item = z.getinfo(f"votacao_secao_2018_{uf}.csv")
    remoto.seek(item.header_offset)
    local = remoto.read(30)
    assert local[:4] == b"PK\x03\x04" and item.compress_type == zipfile.ZIP_DEFLATED
    tam_nome, tam_extra = struct.unpack_from("<HH", local, 26)
    inicio = item.header_offset+30+tam_nome+tam_extra
    vistos, selecionados, cab_escrito = 0, 0, False
    CACHE.mkdir(parents=True, exist_ok=True)
    with remoto.abrir(inicio, inicio+item.compress_size-1) as r, arquivo.open("w", encoding="utf-8", newline="") as out:
        stream = ComHash(r)
        with zipfile.ZipExtFile(stream, "r", item) as membro, io.TextIOWrapper(membro, encoding="latin1", newline="") as txt:
            cab = next(csv.reader([txt.readline()], delimiter=";"))
            cols = COLS + (["NR_LOCAL_VOTACAO"] if "NR_LOCAL_VOTACAO" in cab else [])
            tipos = {c: (str if c == "SG_UF" else "int64") for c in cols}
            for t in pd.read_csv(txt, sep=";", names=cab, usecols=cols, dtype=tipos, chunksize=150_000):
                vistos += len(t)
                parte = t[(t.NR_TURNO == 2) & (t.CD_CARGO == 1) & t.CD_MUNICIPIO.isin(codigos)
                          & t.SG_UF.ne("ZZ")]
                assert set(parte.NR_VOTAVEL.unique()) <= {13, 17, 95, 96}
                if len(parte):
                    parte.to_csv(out, index=False, header=not cab_escrito, lineterminator="\n")
                    cab_escrito = True
                    selecionados += len(parte)
                if vistos % 3_000_000 == 0:
                    print(uf, "lidas", vistos, "selecionadas", selecionados, flush=True)
        assert stream.n == item.compress_size
        info = dict(uf=uf, url=url, membro=item.filename, crc32=item.CRC,
                    comprimido=item.compress_size, descomprimido=item.file_size,
                    comprimido_sha256=stream.sha.hexdigest(), linhas_lidas=vistos,
                    linhas_selecionadas=selecionados)
    assert selecionados > 0
    # O arquivo precisa estar fechado: a última escrita do TextIO pode estar no buffer.
    info["csv_sha256"] = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    manifesto.write_text(json.dumps(info, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(uf, "concluído", vistos, selecionados, flush=True)
    return info


def consolidar(cidades):
    registros = []
    independente = defaultdict(Counter)
    for uf in sorted(cidades.uf.unique()):
        arquivo = CACHE/f"{uf}.csv"
        t = pd.read_csv(arquivo)
        assert t.NR_TURNO.eq(2).all() and t.CD_CARGO.eq(1).all()
        g = t.groupby(["CD_MUNICIPIO", "NR_ZONA", "NR_VOTAVEL"]).QT_VOTOS.sum().unstack(fill_value=0)
        for col in (13, 17, 95, 96):
            if col not in g:
                g[col] = 0
        zona = pd.DataFrame(dict(pt=g[13], adv=g[17], brancos=g[95], nulos=g[96]))
        zona["validos"] = zona.pt+zona.adv
        zona["secoes"] = t.groupby(["CD_MUNICIPIO", "NR_ZONA"]).NR_SECAO.nunique()
        zona["locais"] = (t.groupby(["CD_MUNICIPIO", "NR_ZONA"]).NR_LOCAL_VOTACAO.nunique()
                            if "NR_LOCAL_VOTACAO" in t else pd.NA)
        registros.append(zona.reset_index())
        # Segundo caminho: nenhuma agregação pandas ou função de normalização.
        with arquivo.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                assert r["NR_TURNO"] == "2" and r["CD_CARGO"] == "1"
                independente[(int(r["CD_MUNICIPIO"]), int(r["NR_ZONA"]))][int(r["NR_VOTAVEL"])] += int(r["QT_VOTOS"])
    z = pd.concat(registros, ignore_index=True)
    for r in z.itertuples():
        esperado = independente[(r.CD_MUNICIPIO, r.NR_ZONA)]
        assert (r.pt, r.adv, r.brancos, r.nulos) == tuple(esperado[k] for k in (13, 17, 95, 96))
    detalhe = pd.read_csv(RAIZ/"dados/bruto/tse/detalhe_2018_BR.csv", sep=";", encoding="latin1")
    detalhe = detalhe[(detalhe.NR_TURNO == 2) & (detalhe.CD_CARGO == 1) & detalhe.CD_MUNICIPIO.isin(cidades.cod_tse)]
    campos = {"QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "QT_ABSTENCOES": "abstencoes",
              "QT_VOTOS_BRANCOS": "brancos_det", "QT_TOTAL_VOTOS_NULOS": "nulos_det", "QT_VOTOS_NOMINAIS_VALIDOS": "validos_det"}
    d = detalhe.groupby(["CD_MUNICIPIO", "NR_ZONA"])[list(campos)].sum().rename(columns=campos).reset_index()
    z = z.merge(d, on=["CD_MUNICIPIO", "NR_ZONA"], how="outer", validate="one_to_one", indicator=True)
    assert z._merge.eq("both").all()
    for col in ("brancos", "nulos", "validos"):
        assert z[col].eq(z[col+"_det"]).all(), col
    z = z.merge(cidades[["cod_tse", "cod_ibge", "cidade", "uf"]], left_on="CD_MUNICIPIO", right_on="cod_tse", validate="many_to_one")
    z = z.rename(columns={"cod_ibge": "cd_ibge", "NR_ZONA": "zona", "cod_tse": "cd_tse"})
    z["ano"], z["turno"], z["demais"] = 2018, 2, 0
    locais = pd.read_csv(RAIZ/"dados/pbi/t20_locais.csv", dtype={"cod_ibge": str})
    z["cd_ibge"] = z.cd_ibge.astype(str)
    z = z.merge(locais[["cod_ibge", "zona", "id"]], left_on=["cd_ibge", "zona"], right_on=["cod_ibge", "zona"], how="left", validate="one_to_one")
    z["id"] = z.id.astype("Int64")
    z["fonte"] = "TSE votação por seção 2018/2 + detalhe munzona; pipeline/coletar_p2_zonas_2018.py"
    modelo = pd.read_csv(RAIZ/"dados/pbi/t20_zonas_turno.csv", nrows=0).columns
    z = z[list(modelo)].sort_values(["cd_ibge", "zona"]).reset_index(drop=True)
    municipal = pd.read_csv(RAIZ/"dados/pbi/municipio_2turno.csv", dtype={"cd_ibge": str})
    municipal = municipal[municipal.ano == 2018].set_index("cd_ibge")
    provas = []
    for cod, g in z.groupby("cd_ibge"):
        for col in ("pt", "adv", "validos", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"):
            soma, esperado = int(g[col].sum()), int(municipal.loc[cod, col])
            provas.append(dict(cd_ibge=cod, campo=col, obtido=soma, esperado=esperado, diferenca=soma-esperado))
    p = pd.DataFrame(provas)
    assert p.diferenca.eq(0).all()
    votos = pd.read_csv(RAIZ/"dados/bruto/tse/presidente_2018_BR.csv", sep=";", encoding="latin1",
                        usecols=["NR_TURNO", "CD_CARGO", "CD_MUNICIPIO", "NR_ZONA", "NR_CANDIDATO", "QT_VOTOS_NOMINAIS_VALIDOS"])
    votos = votos[(votos.NR_TURNO == 2) & (votos.CD_CARGO == 1)].groupby(["CD_MUNICIPIO", "NR_ZONA", "NR_CANDIDATO"]).QT_VOTOS_NOMINAIS_VALIDOS.sum()
    tse_por_cod = dict(zip(cidades.cod_ibge.astype(str), cidades.cod_tse))
    for r in z.itertuples():
        for numero, valor in ((13, r.pt), (17, r.adv)):
            assert int(valor) == int(votos.loc[(tse_por_cod[r.cd_ibge], r.zona, numero)])
    p.to_csv(QA/"prova2018_municipios.csv", index=False, lineterminator="\n")
    z.to_csv(DESTINO, index=False, lineterminator="\n")
    return z, len(provas)


def main():
    QA.mkdir(parents=True, exist_ok=True)
    cidades = pd.read_csv(RAIZ/"dados/pbi/t20_cidades.csv")
    # Presidente está no arquivo BR; os arquivos por UF trazem os cargos estaduais.
    fonte = coletar("BR", set(cidades.cod_tse))
    selecionadas = pd.read_csv(CACHE/"BR.csv")
    assert set(selecionadas.SG_UF) == set(cidades.uf)
    for uf, t in selecionadas.groupby("SG_UF"):
        assert set(t.CD_MUNICIPIO) == set(cidades[cidades.uf == uf].cod_tse)
        t.to_csv(CACHE/f"{uf}.csv", index=False, lineterminator="\n")
    z, provas = consolidar(cidades)
    resumo = dict(status="APROVADO", cidades=z.cd_ibge.nunique(), zonas=len(z),
                  provas_municipais=provas, zonas_sem_id=int(z.id.isna().sum()),
                  campos_conferidos_por_zona=["pt", "adv", "validos", "brancos", "nulos"],
                  arquivo=str(DESTINO.relative_to(RAIZ)),
                  sha256=hashlib.sha256(DESTINO.read_bytes()).hexdigest(), fontes=[fonte])
    (QA/"coleta2018_resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("APROVADO", len(z), "zonas", z.cd_ibge.nunique(), "cidades", provas, "provas municipais", flush=True)


if __name__ == "__main__":
    main()
