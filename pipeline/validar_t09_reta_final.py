"""Provas locais da T09; não conecta ao Desktop nem altera o modelo.

Caminho A: pandas sobre o levantamento pos_2turno.csv, com pivot.
Caminho B: pandas sobre os CSVs efetivamente lidos pelo Power BI, com seleção
por estudo/métrica/janela; confere também a reexportação dos brutos em memória.
Emite consultas DAX e comandos de prévia para a main executar após o refresh.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

from exportar_pbi import copiar

RAIZ = Path(__file__).resolve().parents[1]
QA = RAIZ / "pbi/qa/p3/t09"
CANDIDATOS = ["Lula", "Flávio Bolsonaro"]
COLUNAS = ["estudo", "metrica", "periodo_inicio", "periodo_fim", "candidato", "unidade"]


def par(df: pd.DataFrame) -> dict[str, float]:
    assert len(df) == 2 and not df.candidato.duplicated().any(), df.to_string()
    assert set(df.candidato) == set(CANDIDATOS) and df.valor.notna().all()
    return df.set_index("candidato").valor.astype(float).to_dict()


def escolher(df: pd.DataFrame, estudo: str, metrica: str, inicio: str, fim: str) -> dict:
    return par(df.loc[
        df.estudo.eq(estudo) & df.metrica.eq(metrica)
        & df.periodo_inicio.eq(inicio) & df.periodo_fim.eq(fim)
    ])


def janela_periodo(df: pd.DataFrame, inicio: str, fim: str) -> dict | None:
    """Mesma política declarada pela tela, implementada em pandas por grupo."""
    df = df[df.periodo_inicio.ge(inicio) & df.periodo_fim.le(fim) & df.valor.notna()]
    opcoes = []
    for chave, grupo in df.groupby(COLUNAS[:-2] + ["unidade"]):
        grupo = grupo[grupo.candidato.isin(CANDIDATOS)]
        if set(grupo.candidato) == set(CANDIDATOS):
            duracao = (pd.Timestamp(chave[3]) - pd.Timestamp(chave[2])).days
            opcoes.append((duracao, chave[2], chave, grupo))
    if not opcoes:
        return None
    _, _, chave, grupo = sorted(opcoes, key=lambda x: (x[0], x[1]), reverse=True)[0]
    return {"estudo": chave[0], "metrica": chave[1], "inicio": chave[2], "fim": chave[3], "valores": par(grupo)}


def referencias_motor() -> None:
    # Somente leitura dos geradores; nenhuma consulta ao motor aqui.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(RAIZ / "pbi/scripts"))
    import previa

    contas = ["herói · Lula", "herói · Flávio", "herói · vezes", "herói · diferença IPD",
              "período · IPD · Lula", "período · IPD · Flávio", "período · IPD · dia"]
    nomes = {"T09 · " + c for c in contas}
    nomes |= {"T09 · " + c for c in ["lado · ganho", "lado · Meta", "reta final · anúncios"]}
    define = previa.bloco_define(nomes)
    pares = ",\n        ".join(f'"{c}", [T09 · {c}]' for c in contas)
    q = define + "EVALUATE UNION (\n    ROW (\"Ordem\", 0,\n        " + pares + "),\n"
    q += "    SUMMARIZECOLUMNS ( 'Período'[Ordem],\n        " + pares + ")\n)\nORDER BY [Ordem]\n"
    q += "\nEVALUATE SUMMARIZECOLUMNS ( Monitoramento[Candidato],\n"
    q += '    "ganho 24/10", [T09 · lado · ganho], "Meta 18–24/10", [T09 · lado · Meta],\n'
    q += '    "anúncios 18–24/10", [T09 · reta final · anúncios] )\n'
    (QA / "prova_contas.dax").write_text(q, encoding="utf-8")
    # Prova HTML/ALT no grão de cada visual, para detectar erro do parser e LEN.
    desenhos = sorted((RAIZ / "pbi/dax/T09 Redes/Desenho").glob("*.dax"))
    nomes = {p.stem for p in desenhos}
    q = previa.bloco_define(nomes)
    resultados = []
    for ordem in range(5):
        filtro = "" if ordem == 0 else f", TREATAS ( {{ {ordem} }}, 'Período'[Ordem] )"
        for p in desenhos:
            n = p.stem
            if any(x in n for x in ["Balões", "Tooltip conversa"]):
                grao = "Monitoramento[Candidato]"
            elif any(x in n for x in ["Linhas", "Tooltip lado"]):
                grao = "Seguidores[Candidato]"
            elif any(x in n for x in ["Popularidade pontos", "Tooltip IPD"]):
                grao = "Monitoramento[Início]"
            else:
                grao = None
            corpo = f"LEN ( [{n}] )"
            if grao:
                corpo = f'MAXX ( SUMMARIZECOLUMNS ( {grao}, "@n", {corpo} ), [@n] )'
            resultados.append(f'ROW ( "Período", {ordem}, "Medida", "{n}", "LEN", CALCULATE ( {corpo}{filtro} ) )')
    q += "EVALUATE UNION (\n    " + ",\n    ".join(resultados) + "\n)\n"
    (QA / "prova_html.dax").write_text(q, encoding="utf-8")


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    original = copiar(RAIZ / "dados/bruto/digital/pos_2turno.csv")
    fonte = original[original.valor.notna() & original.observacao.str.startswith("CONFIRMADO |")]
    # A: pivot do levantamento original, sem usar o exportador específico.
    a = fonte.pivot(index=["metrica", "periodo_inicio", "periodo_fim"], columns="candidato", values="valor")
    assert a.notna().all().all() and a.shape == (7, 2)
    m = pd.read_csv(RAIZ / "dados/pbi/monitoramento.csv")
    # B: cada linha confirmada tem exatamente um valor persistido; só a Bites
    # usa o rótulo histórico equivalente (mesmas cinco redes, em outra ordem).
    alias = "interações nos perfis oficiais (X, YouTube, TikTok, Instagram, Facebook), de segunda a sábado"
    for _, row in fonte.iterrows():
        metrica = alias if row.estudo == "Bites (agência de dados)" else row.metrica
        b = escolher(m, row.estudo, metrica, row.periodo_inicio, row.periodo_fim)
        assert b[row.candidato] == row.valor
    assert original.loc[original.valor.isna()].shape[0] == 46
    assert m.loc[m.periodo_inicio.ge("2026-10-25")].empty, "Não há dado pós-eleição no levantamento."
    resultados = []
    for (metrica, inicio, fim), linha in a.iterrows():
        valores = {c: float(linha[c]) for c in CANDIDATOS}
        resultados.append({"metrica": metrica, "inicio": inicio, "fim": fim, "valores": valores})
    # Valida números publicados e razões sem usar as medidas DAX como oráculo.
    bites = a.loc[(fonte.iloc[0].metrica, "2026-10-19", "2026-10-24")]
    assert list(bites[CANDIDATOS]) == [92000000, 24600000]
    razao_final = float(bites["Lula"] / bites["Flávio Bolsonaro"])
    assert math.isclose(razao_final, 3.739837398373984)
    for dia, valores in [("2026-10-22", [81.1, 77.0]), ("2026-10-24", [82.7, 76.2])]:
        assert list(a.loc[("IPD", dia, dia), CANDIDATOS]) == valores
    assert not m.duplicated(COLUNAS).any()
    # CSVs existentes: prefixo byte a byte, cabeçalhos e reexportação equivalentes.
    preservacao = []
    for nome, n_novas in [("monitoramento", 10), ("seguidores", 2), ("anuncios", 2)]:
        bruto = copiar(RAIZ / f"dados/bruto/digital/{nome}.csv")
        atual = pd.read_csv(RAIZ / f"dados/pbi/{nome}.csv")
        pd.testing.assert_frame_equal(bruto, atual, check_dtype=False)
        for pasta in ["dados/bruto/digital", "dados/pbi"]:
            caminho = RAIZ / pasta / f"{nome}.csv"
            antes = QA / "antes" / pasta / f"{nome}.csv"
            assert caminho.read_bytes().startswith(antes.read_bytes())
            sep = ";" if pasta.endswith("digital") else ","
            assert len(pd.read_csv(caminho, sep=sep)) - len(pd.read_csv(antes, sep=sep)) == n_novas
            preservacao.append({"arquivo": caminho.relative_to(RAIZ).as_posix(), "linhas_novas": n_novas,
                                "prefixo_sha256": hashlib.sha256(antes.read_bytes()).hexdigest()})
    estoque = pd.read_csv(RAIZ / "dados/pbi/seguidores.csv")
    assert estoque.loc[estoque.data.eq("2026-10-24"), "seguidores"].isna().all()
    # Confere também o gasto na tabela própria (não só em Monitoramento).
    ads = pd.read_csv(RAIZ / "dados/pbi/anuncios.csv")
    semana = ads[ads.periodo.eq("2026-10-18 a 2026-10-24 (7 dias)")]
    assert sorted(semana.valor_reais.tolist()) == [3071478, 9415354]
    assert semana.plataforma.eq("Meta (Facebook/Instagram)").all()
    interacoes = m[m.estudo.str.contains("Bites") & m.metrica.str.contains("interações")]
    seguidores = m[m.metrica.str.contains("seguidores ganhos") & ~m.metrica.str.contains(" - ") & m.unidade.eq("seguidores")]
    ipd = m[m.metrica.isin(["IPD", "IPD (patamar máximo)"])]
    cobertura = []
    # Datas lidas do módulo por AST; não importa gerar_modelo nem executa modelo.
    modulo = ast.parse((RAIZ / "pbi/modelo/periodo.py").read_text(encoding="utf-8-sig"))
    periodos = next(ast.literal_eval(n.value) for n in modulo.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "PERIODOS" for t in n.targets))
    for ordem, _, nome, inicio, fim, _, _, _ in periodos:
        inicio, fim = pd.Timestamp(*inicio).isoformat()[:10], pd.Timestamp(*fim).isoformat()[:10]
        p = ipd[ipd.periodo_inicio.ge(inicio) & ipd.periodo_inicio.le(fim)]
        ultimo = max(d for d, g in p.groupby("periodo_inicio") if set(g.candidato) == set(CANDIDATOS))
        interacao = janela_periodo(interacoes, inicio, fim)
        ganho = janela_periodo(seguidores, inicio, fim)
        corte = {"ordem": ordem, "nome": nome, "inicio": inicio, "fim": fim,
                 "interacoes": interacao, "ganho": ganho, "ipd_dia": ultimo,
                 "ipd": par(p[p.periodo_inicio.eq(ultimo)])}
        if ordem in [3, 4]:
            assert interacao is None
        if ordem == 3:
            assert ganho is None and ultimo == "2026-10-22"
        if ordem == 4:
            assert ganho["valores"] == {"Lula": 221000.0, "Flávio Bolsonaro": 161000.0}
            assert ultimo == "2026-10-24"
        corte["meta"] = None
        if ordem == 2:
            dia = ads[ads.periodo.eq("2026-10-19 (1 dia)") & ads.candidato_ou_partido.str.contains("rótulo da campanha")]
            corte["meta"] = dict(zip(dia.candidato_ou_partido, dia.valor_reais))
        cobertura.append(corte)
    # Estrutura DAX sem motor: parser local, referências e variáveis declaradas.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(RAIZ / "pbi/scripts"))
    from validar_dax_gerado import problemas
    todas = {p.stem for p in (RAIZ / "pbi/dax").rglob("*.dax")}
    for p in (RAIZ / "pbi/dax/T09 Redes").rglob("*.dax"):
        texto = p.read_text(encoding="utf-8-sig")
        assert not problemas(texto), (p, problemas(texto))
        assert not [r for r in re.findall(r"\[(T09 · [^\]]+)\]", texto) if r not in todas], p
        codigo = re.sub(r'/\*.*?\*/|--[^\n]*|"(?:""|[^"])*"', "", texto, flags=re.S)
        declaradas = set(re.findall(r"\bVAR\s+(_\w+)", codigo, flags=re.I))
        usadas = set(re.findall(r"\b_\w+", codigo))
        assert usadas <= declaradas, (p, usadas - declaradas)
    # T08 e T17 compartilham só Período; continuam independentes dos três CSVs.
    for prefixo in ["T08", "T17"]:
        for p in (RAIZ / "pbi/dax").glob(prefixo + "*/*/*.dax"):
            s = p.read_text(encoding="utf-8-sig")
            assert not any(t in s for t in ["Monitoramento[", "Seguidores[", "'Anúncios'["]), p
    referencias_motor()
    saida = {"caminho_A": "pandas/pivot do levantamento pos_2turno.csv",
             "caminho_B": "pandas/seleção dos CSVs PBI + reexportação bruta em memória",
             "valores_confirmados": 14, "valores_divergentes": 0, "razao_bites_reta_final": razao_final,
             "medicoes": resultados, "periodos": cobertura, "preservacao": preservacao,
             "motor_DAX": "Não executado: sandbox sem autenticação; consultas geradas para a main."}
    (QA / "prova_pandas.json").write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("14 valores por dois caminhos: 0 divergências; 19/10 e Bites deduplicados.")
    print("CSV: 10/2/2 linhas novas, prefixos intactos; estoque 24/10 vazio, ganho em Monitoramento.")
    for p in cobertura:
        print(p["nome"], "· IPD", p["ipd_dia"], p["ipd"], "· Bites", p["interacoes"], "· ganhos", p["ganho"])
    print("Estrutura/referências DAX e independência T08/T17: OK. Motor/render pendentes da main.")


if __name__ == "__main__":
    main()
