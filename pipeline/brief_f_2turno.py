"""Brief F: segundo turno 2006–2026, comparecimento e inventário DAX.

Uso: python -I -X utf8 pipeline/brief_f_2turno.py
Somente leitura nas entradas; escreve exclusivamente em dados/saida/2turno.
Não executa os entrypoints dos exportadores existentes.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from consolidar import normalizar
from exportar_2turno import COLUNAS, gravar_csv, gravar_json, normalizar as normalizar_api
from extrair_secoes import CIDADES_T20

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "dados/saida/2turno"
ANOS = (2006, 2010, 2014, 2018, 2022, 2026)
ESQUEMA = ["ano", "cd_ibge", *COLUNAS]
DETALHE = {"QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "QT_ABSTENCOES": "abstencoes",
           "QT_VOTOS_BRANCOS": "brancos", "QT_TOTAL_VOTOS_NULOS": "nulos", "QT_TOTAL_VOTOS_VALIDOS": "validos"}
HISTORICO = {"pt": "votos_pt", "adv": "votos_adv", "validos": "validos", "comparecimento": "comparecimento", "aptos": "aptos"}
PROVAS, TRANSITO, RESIDUOS, SEM_VOTACAO = [], [], [], []
ENTRADAS = set()


def entrada(caminho):
    p = RAIZ / caminho
    ENTRADAS.add(p)
    return p


def csv_pbi(nome):
    return pd.read_csv(entrada(f"dados/pbi/{nome}.csv"))


def prova(ano, turno, teste, local, campo, obtido, esperado):
    obtido, esperado = int(obtido), int(esperado)
    PROVAS.append({"ano": ano, "turno": turno, "teste": teste, "local": local, "campo": campo,
                   "obtido": obtido, "esperado": esperado, "diferenca": obtido - esperado})


def mapear_transito(d, ano, tipo):
    """VT/2010 é o lugar de votação, identificado pelo nome da capital no próprio TSE."""
    vt = d.SG_UF.eq("VT")
    if not vt.any():
        return d
    if ano != 2010:
        raise ValueError("VT inesperado fora de 2010")
    capitais = {normalizar(nome): (uf, cd) for uf, cd, _, nome in CIDADES_T20[:27]}
    for (turno, cd, nome), g in d[vt].groupby(["NR_TURNO", "CD_MUNICIPIO", "NM_MUNICIPIO"]):
        uf, destino = capitais[normalizar(nome)]
        campos = ["votos"] if tipo == "votos" else list(DETALHE.values())
        TRANSITO.append({"ano": ano, "turno": turno, "tipo": tipo, "cd_tse_original": cd,
                         "nome": nome, "uf_destino": uf, "cd_tse_destino": destino,
                         **{c: int(g[c].sum()) for c in campos}})
    destinos = d.loc[vt, "NM_MUNICIPIO"].map(normalizar).map(capitais)
    if destinos.isna().any():
        raise ValueError("Capital VT não encontrada")
    d.loc[vt, "SG_UF"] = destinos.map(lambda x: x[0])
    d.loc[vt, "CD_MUNICIPIO"] = destinos.map(lambda x: x[1])
    return d


def carregar(ano, cadastro):
    v = pd.read_csv(entrada(f"dados/bruto/tse/presidente_{ano}_BR.csv"), sep=";", encoding="latin1")
    d = pd.read_csv(entrada(f"dados/bruto/tse/detalhe_{ano}_BR.csv"), sep=";", encoding="latin1")
    v, d = v[v.CD_CARGO.eq(1)].copy(), d[d.CD_CARGO.eq(1)].copy()
    campo = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in v else "QT_VOTOS_NOMINAIS"
    v["votos"] = v[campo].astype("int64")
    d = d.rename(columns=DETALHE)
    v, d = mapear_transito(v, ano, "votos"), mapear_transito(d, ano, "detalhe")
    chaves = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO"]
    # O adversário do segundo turno é também o principal adversário nacional no primeiro.
    adversario = 17 if ano == 2018 else 45 if ano <= 2014 else 22
    v["papel"] = v.NR_CANDIDATO.map({13: "pt", adversario: "adv"}).fillna("demais")
    votos = v.pivot_table(index=chaves, columns="papel", values="votos", aggfunc="sum", fill_value=0).reset_index()
    if "demais" not in votos:
        votos["demais"] = 0
    det = d.groupby(chaves, as_index=False)[list(DETALHE.values())].sum()
    m = votos.merge(det, on=chaves, how="outer", validate="one_to_one", indicator=True)
    # Algumas cidades do exterior têm aptos, mas nenhuma seção instalada/voto;
    # estão apenas no detalhe. Conserva os aptos e atribui zero só aos votos ausentes.
    sem_votos = m._merge.eq("right_only") & m.SG_UF.eq("ZZ") & m.validos.eq(0) & m.comparecimento.eq(0)
    for r in m.loc[sem_votos].itertuples():
        SEM_VOTACAO.append({"ano": ano, "turno": r.NR_TURNO, "uf": r.SG_UF,
                            "cd_tse": r.CD_MUNICIPIO, "aptos": r.aptos})
    if not (m._merge.eq("both") | sem_votos).all():
        raise ValueError(f"Chaves de votos e detalhe diferentes em {ano}")
    m.loc[sem_votos, ["pt", "adv", "demais"]] = 0
    m[["pt", "adv", "demais"]] = m[["pt", "adv", "demais"]].astype("int64")
    m = m.drop(columns="_merge").rename(columns={"NR_TURNO": "turno", "SG_UF": "uf", "CD_MUNICIPIO": "cd_tse"})
    m["ano"] = ano
    m = m.merge(cadastro[["uf", "cd_tse", "cd_ibge"]], on=["uf", "cd_tse"], how="left", validate="many_to_one")
    if m.loc[m.uf.ne("ZZ"), "cd_ibge"].isna().any():
        raise ValueError("Município sem IBGE: " + str(m[m.cd_ibge.isna() & m.uf.ne("ZZ")].to_dict("records")))
    for turno, g in m.groupby("turno"):
        for uf, h in g.groupby("uf"):
            a = v[v.NR_TURNO.eq(turno) & v.SG_UF.eq(uf)]
            b = d[d.NR_TURNO.eq(turno) & d.SG_UF.eq(uf)]
            for papel in ("pt", "adv", "demais"):
                prova(ano, turno, "soma direta votos x municípios", uf, papel, h[papel].sum(), sum(map(int, a.loc[a.papel.eq(papel), "votos"])))
            prova(ano, turno, "votos candidatos x detalhe", uf, "validos", h[["pt", "adv", "demais"]].to_numpy().sum(), h.validos.sum())
            for campo in DETALHE.values():
                prova(ano, turno, "soma direta detalhe x municípios", uf, campo, h[campo].sum(), sum(map(int, b[campo])))
    # Resíduos são da fonte; não substituir aptos nem abstenções para forçar identidades.
    for r in d.itertuples():
        saldo = int(r.aptos - r.comparecimento - r.abstencoes)
        saldo_votos = int(r.comparecimento - r.validos - r.brancos - r.nulos)
        if saldo or saldo_votos:
            RESIDUOS.append({"ano": ano, "turno": r.NR_TURNO, "uf": r.SG_UF, "cd_tse": r.CD_MUNICIPIO,
                             "zona": r.NR_ZONA, "aptos_menos_comparecimento_abstencoes": saldo,
                             "comparecimento_menos_validos_brancos_nulos": saldo_votos,
                             "eleitores_secoes_nao_instaladas": r.QT_ELEITORES_SECOES_NAO_INSTALADAS,
                             "votos_anulados": r.QT_TOTAL_VOTOS_ANULADOS,
                             "votos_anulados_subjudice": r.QT_TOTAL_VOTOS_ANUL_SUBJUD,
                             "votos_anulados_separados": r.QT_VOTOS_ANULADOS_APU_SEP})
    return m


def carregar_api(cadastro):
    config = json.loads(entrada("dados/bruto/tse/2t2026/config.json").read_text(encoding="utf-8"))
    linhas = []
    for abr in config["abr"]:
        uf = abr["cd"].upper()
        for mun in abr["mu"]:
            p = entrada(f"dados/bruto/tse/2t2026/{uf.lower()}/{str(mun['cd']).zfill(5)}.json")
            bruto = json.loads(p.read_text(encoding="utf-8"))
            if int(bruto["ele"]) != 6258 or str(bruto["tf"]) != "s" or int(bruto["cdabr"]) != int(mun["cd"]):
                raise ValueError("Cache de 2026 não final ou município incorreto")
            linhas.append({"ano": 2026, "turno": 2, "uf": uf, "cd_tse": int(mun["cd"]),
                           "cd_ibge": int(mun["cdi"]) if uf != "ZZ" else None, **normalizar_api(bruto)})
    m = pd.DataFrame(linhas)
    if m.duplicated(["uf", "cd_tse"]).any() or m.loc[m.uf.ne("ZZ"), "cd_ibge"].duplicated().any():
        raise ValueError("Chaves duplicadas no cache API")
    if set(m.loc[m.uf.ne("ZZ"), "cd_ibge"].astype(int)) != set(cadastro.cd_ibge):
        raise ValueError("Cobertura 2026 difere do cadastro")
    for uf in sorted(set(m.uf) | {"BR"}):
        bruto = json.loads(entrada(f"dados/bruto/tse/2t2026/totais/{uf.lower()}.json").read_text(encoding="utf-8"))
        if int(bruto["ele"]) != 6258 or str(bruto["tf"]) != "s":
            raise ValueError("Totalização não final")
        esperado = normalizar_api(bruto)
        g = m if uf == "BR" else m[m.uf.eq(uf)]
        for campo in COLUNAS:
            prova(2026, 2, "municípios x API total final", uf, campo, g[campo].sum(), esperado[campo])
    return m


def inventario():
    linhas = []
    tabela = "'Município segundo turno'"
    for p in sorted((RAIZ / "pbi/dax").rglob("*.dax")):
        texto = p.read_text(encoding="utf-8-sig")
        sem_comentario = re.sub(r"/\*.*?\*/|//[^\n]*|--[^\n]*", "", texto, flags=re.S)
        if tabela not in sem_comentario:
            continue
        ENTRADAS.add(p)
        filtros = re.findall(re.escape(tabela) + r"\[Ano\]\s*=\s*([A-Za-z_][\w]*|\d{4})", sem_comentario)
        linhas.append({"medida": p.stem, "arquivo": p.relative_to(RAIZ).as_posix(),
                       "filtra_ano_explicitamente": bool(filtros), "valores_ano": "; ".join(dict.fromkeys(filtros)),
                       "filtros_ano": len(filtros), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    df = pd.DataFrame(linhas)
    gravar_csv(df, SAIDA / "brief_f_inventario_medidas.csv")
    md = ["# Inventário somente leitura — Município segundo turno", "",
          "Busca direta em todos os .dax de pbi/dax, retirados comentários. A presença do filtro foi revisada no CALCULATE de cada leitura.", "",
          "| Medida | Filtra Ano explicitamente | Valor | Arquivo |", "|---|---|---|---|"]
    md += [f"| {r.medida} | {'Sim' if r.filtra_ano_explicitamente else 'NÃO'} | {r.valores_ano} | `{r.arquivo}` |" for r in df.itertuples()]
    (SAIDA / "brief_f_inventario_medidas.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return df


def main():
    cadastro = csv_pbi("municipio")
    existentes = csv_pbi("municipio_2turno")
    antes = entrada("dados/pbi/municipio_2turno.csv").read_bytes()
    partes = []
    for ano in ANOS:
        partes.append(carregar(ano, cadastro))
        print(f"{ano}: brutos conferidos", flush=True)
    partes.append(carregar_api(cadastro))
    m = pd.concat(partes, ignore_index=True)
    if m.duplicated(["ano", "turno", "uf", "cd_tse"]).any():
        raise ValueError("Município/ano/turno duplicado")
    uf_hist, br_hist = csv_pbi("pt_historico_uf"), csv_pbi("pt_historico_brasil")
    for (ano, turno), g in m.groupby(["ano", "turno"]):
        exterior = g[g.uf.eq("ZZ")]
        for campo, col in HISTORICO.items():
            ref_br = br_hist[br_hist.ano.eq(ano) & br_hist.turno.eq(turno)][col].item()
            prova(ano, turno, "Brasil com exterior x histórico", "BR", campo, g[campo].sum(), ref_br)
            prova(ano, turno, "Brasil sem exterior x histórico menos ZZ", "BR", campo,
                  g.loc[g.uf.ne("ZZ"), campo].sum(), ref_br - exterior[campo].sum())
        for uf, h in g.groupby("uf"):
            ref = uf_hist[uf_hist.ano.eq(ano) & uf_hist.turno.eq(turno) & uf_hist.uf.eq(uf)]
            if len(ref) != 1:
                raise ValueError(f"Referência histórica ausente: {ano}/{turno}/{uf}")
            for campo, col in HISTORICO.items():
                prova(ano, turno, "UF x histórico", uf, campo, h[campo].sum(), ref[col].item())
    # As linhas correntes permanecem byte a byte; primeiro comparar cada célula com a reextração.
    novos = m[m.turno.eq(2) & m.uf.ne("ZZ")].copy()
    novos["cd_ibge"] = novos.cd_ibge.astype("int64")
    correntes = novos[novos.ano.isin([2022, 2026])][ESQUEMA].sort_values(["ano", "cd_ibge"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(correntes.astype("int64"), existentes.sort_values(["ano", "cd_ibge"]).reset_index(drop=True).astype("int64"))
    antigos = novos[novos.ano.le(2018)][ESQUEMA].astype("int64").sort_values(["ano", "cd_ibge"])
    # Comparecimento: com exterior, sem exterior (inclui trânsito interno), e apenas exterior.
    comp = []
    referencia_comp = csv_pbi("comparecimento_ano").set_index("ano")
    for (ano, turno), g in m.groupby(["ano", "turno"]):
        for abrangencia, h in [("com_exterior", g), ("sem_exterior", g[g.uf.ne("ZZ")]), ("exterior", g[g.uf.eq("ZZ")])]:
            r = {"ano": ano, "turno": turno, "abrangencia": abrangencia,
                 **{c: int(h[c].sum()) for c in ["aptos", "comparecimento", "abstencoes", "brancos", "nulos"]}}
            comp.append(r)
            if turno == 1 and abrangencia == "com_exterior":
                for c in ["aptos", "comparecimento", "abstencoes", "brancos", "nulos"]:
                    prova(ano, turno, "comparecimento 1º x comparecimento_ano com exterior", "BR", c, r[c], referencia_comp.loc[ano, c])
    provas = pd.DataFrame(PROVAS)
    gravar_csv(provas, SAIDA / "brief_f_prova_totais.csv")
    if provas.diferenca.ne(0).any():
        print(provas[provas.diferenca.ne(0)].to_string(index=False))
        raise ValueError("Há diferenças nos totais; saídas municipais não publicadas")
    gravar_csv(antigos, SAIDA / "municipio_2turno_2006_2018.csv")
    # Concatena os bytes originais após as linhas novas, sem reserializar 2022/2026.
    novas_linhas = (SAIDA / "municipio_2turno_2006_2018.csv").read_bytes().splitlines(keepends=True)
    linhas_originais = antes.splitlines(keepends=True)
    combinado = b"".join([linhas_originais[0], *novas_linhas[1:], *linhas_originais[1:]])
    (SAIDA / "municipio_2turno_completo.csv").write_bytes(combinado)
    if combinado.splitlines(keepends=True)[len(antigos) + 1:] != linhas_originais[1:]:
        raise ValueError("Bytes das linhas originais foram alterados")
    gravar_csv(pd.DataFrame(comp), SAIDA / "comparecimento_turno.csv")
    gravar_csv(pd.DataFrame(TRANSITO), SAIDA / "brief_f_voto_transito_2010.csv")
    gravar_csv(pd.DataFrame(RESIDUOS), SAIDA / "brief_f_residuos_fonte.csv")
    gravar_csv(pd.DataFrame(SEM_VOTACAO), SAIDA / "brief_f_exterior_sem_votacao.csv")
    inventario_df = inventario()
    resumo = m[m.uf.ne("ZZ")].groupby(["ano", "turno"], as_index=False).agg(
        municipios=("cd_ibge", "size"), pt=("pt", "sum"), adv=("adv", "sum"), validos=("validos", "sum"),
        aptos=("aptos", "sum"), comparecimento=("comparecimento", "sum"))
    gravar_csv(resumo, SAIDA / "brief_f_resumo_totais.csv")
    manifesto = [{"arquivo": p.relative_to(RAIZ).as_posix(), "bytes": p.stat().st_size,
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(ENTRADAS)]
    gravar_csv(pd.DataFrame(manifesto), SAIDA / "brief_f_entradas_sha256.csv")
    gravar_json({"municipios_antigos": len(antigos), "municipios_completo": len(antigos) + len(existentes),
                 "linhas_comparecimento": len(comp), "provas": len(provas), "diferencas": int(provas.diferenca.ne(0).sum()),
                 "medidas": len(inventario_df), "medidas_sem_ano": int((~inventario_df.filtra_ano_explicitamente).sum()),
                 "linhas_2022_2026_identicas_byte_a_byte": True,
                 "sha256_municipio_2turno_original": hashlib.sha256(antes).hexdigest(),
                 "abrangencia_comparecimento_ano": "com exterior e com VT/2010"}, SAIDA / "brief_f_resumo.json")
    print(resumo.to_string(index=False))
    print(f"Concluído: {len(provas)} provas, nenhuma diferença; {len(inventario_df)} medidas", flush=True)


if __name__ == "__main__":
    main()
