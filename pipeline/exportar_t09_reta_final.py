"""Integra somente os achados confirmados do Brief H, sem regravar linhas antigas.

Usa a mesma leitura e serialização de exportar_pbi.copiar/gravar. O modo de
acréscimo preserva os bytes existentes e pode ser repetido sem duplicar linhas.
Ganhos de seguidores ficam em Monitoramento; Seguidores recebe apenas a lacuna
explícita do estoque de 24/10, nunca o ganho diário como se fosse um total.

    python -X utf8 pipeline/exportar_t09_reta_final.py
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

from exportar_pbi import copiar

RAIZ = Path(__file__).resolve().parents[1]
BRUTO = RAIZ / "dados/bruto/digital"
PBI = RAIZ / "dados/pbi"
CHAVE_MON = ["estudo", "periodo_inicio", "periodo_fim", "metrica", "candidato", "unidade"]
METRICA_BITES = "interações nos perfis oficiais (X, Instagram, Facebook, TikTok, YouTube)"
ALIAS_BITES = "interações nos perfis oficiais (X, YouTube, TikTok, Instagram, Facebook), de segunda a sábado"


def novas_linhas(atual: pd.DataFrame, novas: pd.DataFrame, chave: list[str]) -> pd.DataFrame:
    """Recusa conflito de valor; uma reconfirmação da mesma chave não é adição."""
    existentes = atual.fillna("").astype(str)
    if "metrica" in existentes:
        # Mesma janela, redes e fornecedor, apenas em ordem diferente no rótulo
        # original. Não duplicar a medição que já estava na base.
        existentes["metrica"] = existentes["metrica"].replace({ALIAS_BITES: METRICA_BITES})
    linhas = []
    for _, row in novas.iterrows():
        mascara = pd.Series(True, index=existentes.index)
        for coluna in chave:
            mascara &= existentes[coluna].eq(str(row[coluna]))
        if mascara.any():
            valor = "valor" if "valor" in atual else "valor_reais" if "valor_reais" in atual else "seguidores"
            a = pd.to_numeric(atual.loc[mascara, valor], errors="coerce")
            b = pd.to_numeric(pd.Series([row[valor]]), errors="coerce").iloc[0]
            if not (a.isna().all() and pd.isna(b)) and not a.eq(b).all():
                raise ValueError(f"Conflito de valor: {tuple(row[c] for c in chave)}")
        else:
            linhas.append(row)
    return pd.DataFrame(linhas, columns=atual.columns)


def acrescentar(path: Path, novas: pd.DataFrame, sep: str) -> None:
    if novas.empty:
        print(f"{path.relative_to(RAIZ)}: sem linhas novas")
        return
    antes = path.read_bytes()
    if antes and not antes.endswith(b"\n"):
        raise ValueError(f"Arquivo sem quebra final: {path}")
    # Mesmos parâmetros de exportar_pbi.gravar; apenas header=False na cauda.
    cauda = novas.to_csv(index=False, header=False, sep=sep, lineterminator="\n").encode("utf-8")
    with path.open("ab") as arq:
        arq.write(cauda)
    assert path.read_bytes() == antes + cauda
    print(f"{path.relative_to(RAIZ)}: +{len(novas)} linhas")


def integrar() -> None:
    fonte = copiar(BRUTO / "pos_2turno.csv")
    confirmados = fonte[fonte["valor"].notna() & fonte["observacao"].str.startswith("CONFIRMADO |")].copy()
    assert len(confirmados) == 14, "O levantamento de entrada mudou: revisar antes de integrar."
    assert not confirmados.duplicated(CHAVE_MON).any()
    anuncios = copiar(BRUTO / "anuncios.csv")
    gastos = confirmados[confirmados["unidade"].eq("BRL")]
    linhas_ads = []
    for _, row in gastos.iterrows():
        # Reutiliza a identidade da página oficial já lida pela T09.
        identidade = anuncios.loc[
            anuncios["plataforma"].eq("Meta (Facebook/Instagram)")
            & anuncios["candidato_ou_partido"].str.startswith(row["candidato"] + " (página"),
            "candidato_ou_partido",
        ].iloc[0]
        numero = confirmados.loc[
            confirmados["candidato"].eq(row["candidato"]) & confirmados["unidade"].eq("anúncios"), "valor"
        ].item()
        linhas_ads.append(dict(zip(anuncios.columns, [
            identidade, "Meta (Facebook/Instagram)", "2026-10-18 a 2026-10-24 (7 dias)",
            row["valor"], row["fonte_url"], row["observacao"] + f" | {int(numero)} anúncios",
        ])))
    # O schema de Seguidores é estoque. A lacuna fica vazia, seguindo a convenção
    # dos registros anteriores; os valores de GANHO permanecem em Monitoramento.
    ganhos = confirmados[confirmados["unidade"].eq("seguidores")]
    linhas_seg = [{
        "candidato": r["candidato"], "plataforma": "Instagram", "data": r["periodo_fim"],
        "seguidores": float("nan"), "fonte_url": r["fonte_url"],
        "observacao": "EM BRANCO: total de seguidores em 24/10 não publicado neste levantamento; "
                      "a Quaest publicou somente o ganho diário, registrado separadamente em monitoramento.csv. "
                      + r["observacao"],
    } for _, r in ganhos.iterrows()]
    lotes = [
        ("monitoramento", confirmados, CHAVE_MON),
        ("anuncios", pd.DataFrame(linhas_ads, columns=anuncios.columns),
         ["candidato_ou_partido", "plataforma", "periodo"]),
        ("seguidores", pd.DataFrame(linhas_seg), ["candidato", "plataforma", "data"]),
    ]
    # Valida todos os destinos antes da primeira escrita.
    planos = []
    for nome, novas, chave in lotes:
        bruto = BRUTO / f"{nome}.csv"
        cauda_bruto = novas_linhas(copiar(bruto), novas, chave)
        # Round-trip pelo mesmo parser do exportador comum, sem rodar o main global.
        buffer = io.StringIO(cauda_bruto.to_csv(index=False, sep=";"))
        cauda_pbi = pd.read_csv(buffer, sep=";")
        destino = PBI / f"{nome}.csv"
        planos.append((bruto, cauda_bruto, ";"))
        planos.append((destino, novas_linhas(copiar(destino, sep=","), cauda_pbi, chave), ","))
    for path, novas, sep in planos:
        acrescentar(path, novas, sep)


if __name__ == "__main__":
    integrar()
