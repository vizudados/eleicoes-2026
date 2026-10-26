"""Análises reproduzíveis para o painel e o vídeo do 2º turno de 2026.

Uso: python -I -X utf8 pipeline/analisar_2turno.py
Todos os percentuais são calculados sobre somas; nenhuma média municipal de
percentuais é apresentada como resultado de uma região. Modelos são agregados.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student

RAIZ = Path(__file__).resolve().parents[1]
PBI = RAIZ / "dados/pbi"
SAIDA = RAIZ / "dados/saida/2turno"
CONTAS = ["pt", "adv", "demais", "validos", "aptos", "comparecimento", "abstencoes", "brancos", "nulos"]
CATALOGO = []
FONTE_MUN = "dados/pbi/municipio_ano.csv (2026, 1º turno); dados/pbi/municipio_2turno.csv (2022 e 2026, 2º turno); dados/pbi/municipio.csv"
FONTE_UF = "dados/saida/2turno/uf_1turno_2026.csv; dados/pbi/uf_2turno.csv; dados/pbi/municipio.csv:uf,regiao"
ALERTA_ECO = "Estimativa ecológica entre municípios. Associação agregada, sem identificar transferência individual nem efeito causal do comparecimento. Coeficientes não limitados a 0–100%."


def salvar(df, nome, origem, campos, metodo):
    caminho = SAIDA / nome
    df = df.copy()
    df["arquivo_origem"], df["campo_origem"], df["metodo"] = origem, campos, metodo
    df.to_csv(caminho, index=False, encoding="utf-8", lineterminator="\n", float_format="%.12g")
    CATALOGO.append({"arquivo": caminho.relative_to(RAIZ).as_posix(), "linhas": len(df), "arquivo_origem": origem,
                     "campo_origem": campos, "metodo": metodo})
    return df


def indicadores(df):
    d = df.copy()
    d["pt_pct"] = 100 * d.pt / d.validos
    d["adv_pct"] = 100 * d.adv / d.validos
    d["saldo_pt"] = d.pt - d.adv
    d["diferenca_absoluta"] = d.saldo_pt.abs()
    d["margem_pt_pp"] = 100 * d.saldo_pt / d.validos
    d["abstencao_pct"] = 100 * d.abstencoes / (d.comparecimento + d.abstencoes)
    d["abstencao_sobre_aptos_pct"] = 100 * d.abstencoes / d.aptos
    d["vencedor"] = np.select([d.pt.gt(d.adv), d.adv.gt(d.pt)], ["Lula", "Adversário"], default="Empate")
    return d


def primeiro_turno_uf():
    v = pd.read_csv(RAIZ / "dados/bruto/tse/presidente_2026_BR.csv", sep=";", encoding="latin1")
    v = v[v.NR_TURNO.eq(1) & v.CD_CARGO.eq(1)].copy()
    v["papel"] = v.NR_CANDIDATO.map({13: "pt", 22: "adv"}).fillna("demais")
    wide = v.pivot_table(index="SG_UF", columns="papel", values="QT_VOTOS_NOMINAIS_VALIDOS", aggfunc="sum").reset_index().rename(columns={"SG_UF": "uf"})
    d = pd.read_csv(RAIZ / "dados/bruto/tse/detalhe_2026_BR.csv", sep=";", encoding="latin1")
    d = d[d.NR_TURNO.eq(1) & d.CD_CARGO.eq(1)]
    mapa = {"QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento", "QT_ABSTENCOES": "abstencoes",
            "QT_VOTOS_BRANCOS": "brancos", "QT_TOTAL_VOTOS_NULOS": "nulos", "QT_TOTAL_VOTOS_VALIDOS": "validos"}
    det = d.groupby("SG_UF", as_index=False)[list(mapa)].sum().rename(columns={"SG_UF": "uf", **mapa})
    uf = wide.merge(det, on="uf", validate="one_to_one")
    if not (uf.pt + uf.adv + uf.demais).eq(uf.validos).all():
        raise ValueError("Candidatos e detalhe não fecham no primeiro turno")
    oficial = pd.read_csv(PBI / "candidato_ano.csv").query("ano == 2026")
    for numero, campo in [(13, "pt"), (22, "adv")]:
        assert int(uf[campo].sum()) == int(oficial.loc[oficial.numero.eq(numero), "votos"].iloc[0])
    assert int(uf.validos.sum()) == int(oficial.validos.iloc[0])
    uf["ano"], uf["turno"] = 2026, 1
    salvar(uf, "uf_1turno_2026.csv", "dados/bruto/tse/presidente_2026_BR.csv; dados/bruto/tse/detalhe_2026_BR.csv",
           "NR_TURNO=1; CD_CARGO=1; NR_CANDIDATO=13/22/outros; QT_VOTOS_NOMINAIS_VALIDOS; QT_APTOS; QT_COMPARECIMENTO; QT_ABSTENCOES; QT_VOTOS_BRANCOS; QT_TOTAL_VOTOS_NULOS; QT_TOTAL_VOTOS_VALIDOS",
           "Soma por SG_UF; inclui ZZ; conferido com candidato_ano.csv")
    return uf, oficial


def comparar(base1, base2, chaves):
    a = base1[chaves + CONTAS].rename(columns={c: c + "_1t" for c in CONTAS})
    b = base2[chaves + CONTAS].rename(columns={c: c + "_2t" for c in CONTAS})
    d = a.merge(b, on=chaves, validate="one_to_one")
    for c in CONTAS:
        d["delta_" + c] = d[c + "_2t"] - d[c + "_1t"]
    for sufixo in ["1t", "2t"]:
        d["saldo_pt_" + sufixo] = d["pt_" + sufixo] - d["adv_" + sufixo]
        d["pt_pct_" + sufixo] = 100 * d["pt_" + sufixo] / d["validos_" + sufixo]
        d["adv_pct_" + sufixo] = 100 * d["adv_" + sufixo] / d["validos_" + sufixo]
        d["abstencao_pct_" + sufixo] = 100 * d["abstencoes_" + sufixo] / (d["abstencoes_" + sufixo] + d["comparecimento_" + sufixo])
        d["vencedor_" + sufixo] = np.select([d["saldo_pt_" + sufixo].gt(0), d["saldo_pt_" + sufixo].lt(0)], ["Lula", "Flávio"], default="Empate")
    d["delta_saldo_pt"] = d.saldo_pt_2t - d.saldo_pt_1t
    d["perda_vantagem_flavio"] = d.delta_saldo_pt
    d["perda_vantagem_lula"] = -d.delta_saldo_pt
    d["delta_abstencao_pp"] = d.abstencao_pct_2t - d.abstencao_pct_1t
    d["delta_invalidos"] = d.delta_brancos + d.delta_nulos
    d["mudou_vencedor"] = d.vencedor_1t.ne(d.vencedor_2t)
    # Identidade contábil; não atribui o voto de uma pessoa a nenhum grupo.
    assert (d.delta_pt + d.delta_adv).eq(d.demais_1t + d.delta_comparecimento - d.delta_invalidos).all()
    return d


def agregado(municipios, coluna):
    contas = [c + s for c in CONTAS for s in ["_1t", "_2t"]]
    d = municipios.groupby(coluna, dropna=False, as_index=False)[contas].sum()
    a = d[[coluna] + [c + "_1t" for c in CONTAS]].rename(columns={c + "_1t": c for c in CONTAS})
    b = d[[coluna] + [c + "_2t" for c in CONTAS]].rename(columns={c + "_2t": c for c in CONTAS})
    z = comparar(a, b, [coluna])
    z["municipios"] = municipios.groupby(coluna, dropna=False).size().reindex(z[coluna]).to_numpy()
    return z


def correlacao(x, y, w):
    x, y, w = np.asarray(x, float), np.asarray(y, float), np.asarray(w, float)
    x, y = x - np.average(x, weights=w), y - np.average(y, weights=w)
    den = np.sqrt(np.sum(w * x * x) * np.sum(w * y * y))
    return float(np.sum(w * x * y) / den) if den else float("nan")


def regressao(mun):
    linhas, predicoes, robustez = [], [], []
    n = len(mun)
    peso = mun.aptos_1t.to_numpy(float)
    specs = {"principal": ["constante", "demais", "comparecimento"],
             "com_invalidos": ["constante", "demais", "comparecimento", "invalidos"],
             "sem_constante": ["demais", "comparecimento"]}
    for especificacao, nomes in specs.items():
        xs = {"constante": np.ones(n), "demais": mun.demais_1t / peso,
              "comparecimento": mun.delta_comparecimento / peso, "invalidos": mun.delta_invalidos / peso}
        x = np.column_stack([xs[c] for c in nomes])
        raiz = np.sqrt(peso)
        xw = x * raiz[:, None]
        inv = np.linalg.inv(xw.T @ xw)
        for candidato, campo in [("Lula", "delta_pt"), ("Flávio", "delta_adv")]:
            y = mun[campo].to_numpy(float) / peso
            beta, _, rank, _ = np.linalg.lstsq(xw, y * raiz, rcond=None)
            residuo = y - x @ beta
            # Erro padrão agrupado nas 27 UFs, com correção de amostra finita.
            grupos = mun.uf.unique()
            meat = np.zeros((len(nomes), len(nomes)))
            for uf in grupos:
                mascara = mun.uf.eq(uf).to_numpy()
                score = x[mascara].T @ (peso[mascara] * residuo[mascara])
                meat += np.outer(score, score)
            cov = inv @ meat @ inv * len(grupos) / (len(grupos) - 1) * (n - 1) / (n - len(nomes))
            se = np.sqrt(np.maximum(np.diag(cov), 0))
            critico = student.ppf(.975, len(grupos) - 1)
            r2 = 1 - np.sum(peso * residuo ** 2) / np.sum(peso * (y - np.average(y, weights=peso)) ** 2)
            for i, termo in enumerate(nomes):
                linhas.append({"modelo": especificacao, "candidato": candidato, "termo": termo, "coeficiente": beta[i],
                               "erro_padrao_uf": se[i], "ic95_inferior": beta[i] - critico * se[i],
                               "ic95_superior": beta[i] + critico * se[i], "n_municipios": n, "n_ufs": len(grupos),
                               "r2_ponderado": r2, "condicao_matriz": np.linalg.cond(xw), "posto": rank, "aviso": ALERTA_ECO})
            if especificacao == "principal":
                for i, termo in enumerate(nomes):
                    robustez.append({"candidato": candidato, "componente": termo,
                                     "soma_votos_modelados": float(np.sum(peso * x[:, i] * beta[i])), "aviso": ALERTA_ECO})
                predicoes.append(pd.DataFrame({"cd_ibge": mun.cd_ibge, "candidato": candidato,
                                               "ganho_observado": mun[campo], "ganho_estimado": peso * (x @ beta),
                                               "residuo_votos": peso * residuo}))
        # Sensibilidade: retirar uma UF por vez sem transformar dispersão em causalidade.
        if especificacao == "principal":
            for excluida in sorted(mun.uf.unique()):
                mask = mun.uf.ne(excluida).to_numpy()
                for candidato, campo in [("Lula", "delta_pt"), ("Flávio", "delta_adv")]:
                    y = mun[campo].to_numpy(float) / peso
                    b = np.linalg.lstsq(xw[mask], (y * raiz)[mask], rcond=None)[0]
                    for termo, valor in zip(nomes, b):
                        linhas.append({"modelo": "sem_uf_" + excluida, "candidato": candidato, "termo": termo,
                                       "coeficiente": valor, "n_municipios": int(mask.sum()), "n_ufs": 26, "aviso": ALERTA_ECO})
    salvar(pd.DataFrame(linhas), "regressao_ecologica.csv", FONTE_MUN,
           "delta_pt/aptos_1t ou delta_adv/aptos_1t ~ 1 + demais_1t/aptos_1t + delta_comparecimento/aptos_1t; peso=aptos_1t",
           "Mínimos quadrados ponderados; IC95 por UF, t(26); sensibilidades com inválidos, sem intercepto e sem cada UF; Brasil sem exterior")
    salvar(pd.DataFrame(robustez), "decomposicao_modelo.csv", FONTE_MUN, "X * beta * aptos_1t", ALERTA_ECO)
    salvar(pd.concat(predicoes), "regressao_predicoes.csv", FONTE_MUN, "delta_pt,delta_adv,aptos,demais,comparecimento", ALERTA_ECO)
    return pd.DataFrame(linhas)


def pesquisas(resultado1, resultado2):
    p = pd.read_csv(PBI / "pesquisa.csv")
    if p.duplicated(["cenario", "instituto", "registro_tse", "tipo"]).any():
        raise ValueError("Pesquisas duplicadas: revisar unidade de contagem")
    resumos = []
    for turno, limite, resultado in [(1, "2026-10-04", resultado1), (2, "2026-10-25", resultado2)]:
        recorte = p[p.cenario.eq(f"{turno}º turno") & p.divulgacao.lt(limite)
                    & (p.campo_fim.isna() | p.campo_fim.lt(limite))].copy()
        validos = recorte[recorte.tipo.eq("validos")].copy()
        validos["par_numerico"] = validos[["lula", "flavio"]].notna().all(axis=1)
        validos["lider"] = np.select([validos.lula.gt(validos.flavio), validos.flavio.gt(validos.lula)], ["Lula", "Flávio"], default="Empate")
        validos.loc[~validos.par_numerico, "lider"] = "Sem valores"
        salvar(validos, f"pesquisas_{turno}t_inventario.csv", "dados/pbi/pesquisa.csv",
               "cenario,tipo,divulgacao,campo_fim,instituto,registro_tse,lula,flavio,fonte_url",
               f"Todas as linhas tipo=validos publicadas antes de {limite}; campo_fim ausente não exclui publicação datada; ausências de votos não são empate nem zero")
        direcao_todas = []
        for _, r in validos.iterrows():
            base, l, f = "validos", r.lula, r.flavio
            if pd.isna(l) or pd.isna(f):
                totais = recorte[recorte.tipo.eq("totais") & recorte.instituto.eq(r.instituto) & recorte.registro_tse.eq(r.registro_tse)]
                if len(totais) == 1:
                    base, l, f = "totais (somente direção)", totais.lula.iloc[0], totais.flavio.iloc[0]
            direcao_todas.append({"id_validos": r.id, "instituto": r.instituto, "divulgacao": r.divulgacao,
                                  "registro_tse": r.registro_tse, "base_usada": base, "lula": l, "flavio": f,
                                  "lider": "Sem valores" if pd.isna(l) or pd.isna(f) else "Lula" if l > f else "Flávio" if f > l else "Empate"})
        dt = pd.DataFrame(direcao_todas)
        salvar(dt, f"pesquisas_{turno}t_direcao_todas.csv", "dados/pbi/pesquisa.csv", "validos; se vazio, totais da mesma rodada",
               "Só direção; não usa totais para média ou erros em pontos; cada rodada contada uma vez")
        for janela, mascara in [("direcao_todas_validos_ou_totais", pd.Series(True, index=dt.index)),
                                ("direcao_apos_1t_validos_ou_totais", dt.divulgacao.gt("2026-10-04"))]:
            q = dt[mascara]
            resumos.append({"turno": turno, "recorte": janela, "linhas": len(q),
                            "lula_frente": int(q.lider.eq("Lula").sum()), "flavio_frente": int(q.lider.eq("Flávio").sum()),
                            "empates": int(q.lider.eq("Empate").sum()), "sem_valores": int(q.lider.eq("Sem valores").sum())})
        for janela, mascara in [("todo_o_arquivo", pd.Series(True, index=validos.index)),
                                ("apos_primeiro_turno", validos.divulgacao.gt("2026-10-04"))]:
            q = validos[mascara]
            resumos.append({"turno": turno, "recorte": janela, "linhas": len(q), "pares_numericos": int(q.par_numerico.sum()),
                            "lula_frente": int(q.lula.gt(q.flavio).sum()), "flavio_frente": int(q.flavio.gt(q.lula).sum()),
                            "empates": int(q.lula.eq(q.flavio).sum()), "sem_valores": int((~q.par_numerico).sum())})
        # Última rodada de cada instituto, inclusive ausências; nenhuma rodada antiga é promovida silenciosamente.
        ultimas = validos.sort_values(["divulgacao", "campo_fim", "id"]).groupby("instituto").tail(1).copy()
        for cand, campo in [("lula", "pt"), ("flavio", "adv")]:
            real = 100 * resultado[campo] / resultado["validos"]
            ultimas[cand + "_urna_pct"] = real
            ultimas[cand + "_erro_pp"] = ultimas[cand] - real
            ultimas[cand + "_erro_absoluto_pp"] = ultimas[cand + "_erro_pp"].abs()
            ultimas[cand + "_dentro_margem_divulgada"] = ultimas[cand + "_erro_absoluto_pp"].le(ultimas.margem_pp).where(ultimas.par_numerico)
        ultimas["erro_medio_absoluto_dupla_pp"] = ultimas[["lula_erro_absoluto_pp", "flavio_erro_absoluto_pp"]].mean(axis=1)
        ultimas["erro_vantagem_lula_pp"] = (ultimas.lula - ultimas.flavio) - 100 * (resultado["pt"] - resultado["adv"]) / resultado["validos"]
        salvar(ultimas.sort_values("erro_medio_absoluto_dupla_pp"), f"pesquisas_{turno}t_ultimas.csv", "dados/pbi/pesquisa.csv; " + FONTE_UF,
               "tipo=validos; ultima divulgacao/campo_fim/id por instituto; erro=pesquisa-urna",
               "Erro assinado e absoluto dos dois candidatos; intervalo divulgado é referência descritiva, não teste da pesquisa contra a urna")
        numericas = ultimas[ultimas.par_numerico]
        medias = {"turno": turno, "recorte": "ultima_por_instituto_validos_publicados", "institutos": len(ultimas),
                  "pares_numericos": len(numericas), "lula_frente": int(numericas.lula.gt(numericas.flavio).sum()),
                  "flavio_frente": int(numericas.flavio.gt(numericas.lula).sum()), "empates": int(numericas.lula.eq(numericas.flavio).sum()),
                  "sem_valores": int((~ultimas.par_numerico).sum()), "media_lula": numericas.lula.mean(), "media_flavio": numericas.flavio.mean(),
                  "erro_media_lula_pp": numericas.lula.mean() - 100 * resultado["pt"] / resultado["validos"]}
        resumos.append(medias)
        # Espelho da manchete: direção da dupla na última rodada, com válidos ou totais declarados.
        direcao = []
        for _, r in ultimas.iterrows():
            base, l, f = "validos", r.lula, r.flavio
            if pd.isna(l) or pd.isna(f):
                t = recorte[recorte.tipo.eq("totais") & recorte.instituto.eq(r.instituto) & recorte.registro_tse.eq(r.registro_tse)]
                if len(t) == 1:
                    base, l, f = "totais (somente direção, sem converter em válidos)", t.lula.iloc[0], t.flavio.iloc[0]
            direcao.append({"instituto": r.instituto, "divulgacao": r.divulgacao, "registro_tse": r.registro_tse,
                            "base_usada": base, "lula": l, "flavio": f, "lider": "Sem valores" if pd.isna(l) or pd.isna(f) else "Lula" if l > f else "Flávio" if f > l else "Empate"})
        direcao = pd.DataFrame(direcao)
        salvar(direcao, f"pesquisas_{turno}t_direcao_ultimas.csv", "dados/pbi/pesquisa.csv", "validos; se vazio, totais da mesma rodada",
               "Conta a direção da dupla; não mistura bases para médias ou erros em pontos")
        resumos.append({"turno": turno, "recorte": "direcao_ultima_validos_ou_totais", "institutos": len(direcao),
                        "lula_frente": int(direcao.lider.eq("Lula").sum()), "flavio_frente": int(direcao.lider.eq("Flávio").sum()),
                        "empates": int(direcao.lider.eq("Empate").sum()), "sem_valores": int(direcao.lider.eq("Sem valores").sum())})
    salvar(pd.DataFrame(resumos), "pesquisas_placar.csv", "dados/pbi/pesquisa.csv; " + FONTE_UF,
           "cenario,tipo,lula,flavio,divulgacao,campo_fim,registro_tse", "Uma rodada por instituto/registro; sem duplicar totais e válidos; média simples, peso igual por instituto; universos separados")
    transf = pd.read_csv(PBI / "transferencia.csv")
    transf = transf[transf.divulgacao.gt("2026-10-04") & transf.divulgacao.lt("2026-10-25")].copy()
    transf["ultima_data_instituto"] = transf.groupby("instituto").divulgacao.transform("max")
    transf = transf[transf.divulgacao.eq(transf.ultima_data_instituto)].copy()
    transf["lula_entre_dupla_pct"] = 100 * transf.lula / (transf.lula + transf.flavio)
    transf["flavio_entre_dupla_pct"] = 100 * transf.flavio / (transf.lula + transf.flavio)
    salvar(transf, "transferencia_ultimas.csv", "dados/pbi/transferencia.csv", "instituto,divulgacao,campo_inicio,campo_fim,segmento_1turno,lula,flavio,branco_nulo_nao_vota,nao_sabe,n_segmento,base,observacao,fonte_url",
           "Última onda após 04/10 por instituto; mantém base e tamanho do segmento ausente; intenção declarada não é fluxo observado; entre_dupla exclui outras respostas")
    return pd.DataFrame(resumos), transf


def noite(aptos, validos_final):
    h = pd.read_csv(RAIZ / "dados/apuracao/historico.csv")
    h["linha_origem"] = np.arange(2, len(h) + 2)
    h["dt_coleta"] = pd.to_datetime(h.coletado_em, format="%d/%m/%Y %H:%M:%S")
    h["dt_tse"] = pd.to_datetime(h.atualizado_tse, format="%d/%m/%Y %H:%M:%S")
    h = h.sort_values(["dt_coleta", "linha_origem"])
    if (h.validos.diff().dropna() < 0).any() or (h.secoes_totalizadas.diff().dropna() < 0).any():
        raise ValueError("Revisão decrescente no histórico: exige auditoria antes de limpar")
    assert h.lula_votos.add(h.flavio_votos).eq(h.validos).all()
    h["recuo_relogio_tse"] = h.dt_tse.diff().lt(pd.Timedelta(0))
    h["diferenca_lula_votos"] = h.lula_votos - h.flavio_votos
    h["lula_pct_calculado"] = 100 * h.lula_votos / h.validos
    h["flavio_pct_calculado"] = 100 * h.flavio_votos / h.validos
    h["secoes_pct_calculado"] = 100 * h.secoes_totalizadas / h.secoes_total
    h["lider"] = np.select([h.diferenca_lula_votos.gt(0), h.diferenca_lula_votos.lt(0)], ["Lula", "Flávio"], default="Empate")
    h["validos_restantes_final_conhecido"] = validos_final - h.validos
    # Limite conservador disponível sem conhecer de antemão o comparecimento final.
    h["limite_votos_restantes_eleitorado"] = aptos - h.abstencao - h.brancos - h.nulos - h.validos
    for sufixo, coluna in [("retrospectivo", "validos_restantes_final_conhecido"), ("conservador", "limite_votos_restantes_eleitorado")]:
        r = h[coluna]
        h["flavio_precisaria_votos_" + sufixo] = np.floor((r + h.diferenca_lula_votos) / 2).astype("int64") + 1
        h["flavio_precisaria_pct_" + sufixo] = 100 * h["flavio_precisaria_votos_" + sufixo] / r.where(r.gt(0))
        h["lula_garantido_" + sufixo] = h.diferenca_lula_votos.gt(r)
    estados = ["lula_votos", "flavio_votos", "brancos", "nulos", "abstencao", "validos", "secoes_totalizadas", "secoes_total"]
    h["estado_repetido"] = h.duplicated(estados)
    salvar(h, "apuracao_auditoria.csv", "dados/apuracao/historico.csv; dados/apuracao/ultimo.json", ",".join(estados) + ",atualizado_tse,coletado_em; brasil.eleitorado",
           "Preserva todas as linhas na ordem de coleta; identifica repetição e recuo do relógio do TSE")
    limpa = h[~h.estado_repetido].copy()
    salvar(limpa, "apuracao_serie.csv", "dados/apuracao/historico.csv; dados/apuracao/ultimo.json", "linha_origem,atualizado_tse,coletado_em,secoes_totalizadas,secoes_total,lula_votos,flavio_votos,validos,abstencao,brancos,nulos",
           "Remove somente estados numéricos idênticos; não reordena pelo relógio TSE que recua; percentuais recalculados, valores publicados preservados; garantia retrospectiva conhece válidos finais, conservadora usa teto de eleitorado ainda não contabilizado")
    limpa["hora_tse"] = limpa.dt_tse.dt.strftime("%Y-%m-%d %H:00")
    hora = limpa.groupby("hora_tse", sort=True).tail(1)
    salvar(hora, "apuracao_hora.csv", "dados/saida/2turno/apuracao_serie.csv", "atualizado_tse,secoes_pct,lula_pct_calculado,flavio_pct_calculado,diferenca_lula_votos",
           "Último estado observado em cada hora informada pelo TSE; mantém data/hora exata da parcial; horas sem atualização não recebem interpolação")
    eventos = []
    def evento(nome, linha, observacao):
        eventos.append({"marco": nome, **linha.drop(labels=["hora_tse"], errors="ignore").to_dict(), "observacao_marco": observacao})
    evento("primeira_parcial", limpa.iloc[0], "Primeira linha coletada; 5 seções arredondam para 0,00%, não ausência de votos")
    for lider in ["Flávio", "Lula"]:
        mascara = limpa.lider.eq(lider) & limpa.lider.shift().ne(lider)
        candidatas = limpa[mascara]
        if lider == "Lula":
            candidatas = candidatas[candidatas.dt_coleta.gt(limpa[limpa.lider.eq("Flávio")].dt_coleta.min())]
        if len(candidatas):
            evento("lideranca_" + lider.lower(), candidatas.iloc[0], "Primeira parcial observada após a troca de liderança; não determina o segundo exato ocorrido entre coletas")
    for tipo in ["retrospectivo", "conservador"]:
        evento("garantia_" + tipo, limpa[limpa["lula_garantido_" + tipo]].iloc[0],
               "Vantagem > votos restantes. Para vencer, Flávio precisaria floor((restantes+vantagem)/2)+1 dos restantes. " + ("Usa válidos finais conhecidos depois da apuração." if tipo == "retrospectivo" else "Trata todo eleitor ainda não contabilizado como possível voto válido; não usa o comparecimento futuro."))
    evento("100_porcento_secoes", limpa[limpa.secoes_totalizadas.eq(limpa.secoes_total)].iloc[0], "100% por contagem inteira; 100,00% arredondado pode aparecer antes")
    evento("ultima_atualizacao", h.iloc[-1], "Pode haver nova hora de geração sem mudança dos votos")
    salvar(pd.DataFrame(eventos), "apuracao_marcos.csv", "dados/apuracao/historico.csv; dados/apuracao/ultimo.json", "atualizado_tse,coletado_em,lula_votos,flavio_votos,validos,secoes_totalizadas,secoes_total,abstencao,brancos,nulos",
           "Horário do TSE e da coleta separados; garantia é conta própria, não horário oficial de proclamação")
    return pd.DataFrame(eventos)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    cad = pd.read_csv(PBI / "municipio.csv")
    m1 = pd.read_csv(PBI / "municipio_ano.csv").query("ano == 2026")
    m2 = pd.read_csv(PBI / "municipio_2turno.csv")
    uf2 = pd.read_csv(PBI / "uf_2turno.csv")
    uf1, oficial1 = primeiro_turno_uf()
    regiao = cad[["uf", "regiao"]].drop_duplicates()
    regiao = pd.concat([regiao, pd.DataFrame([{"uf": "ZZ", "regiao": "Exterior"}])], ignore_index=True)
    m = comparar(m1, m2.query("ano == 2026"), ["cd_ibge"]).merge(cad, on="cd_ibge", validate="one_to_one")
    m[["porte", "quinto"]] = m[["porte", "quinto"]].fillna("Sem classificação no cadastro")
    assert len(m) == len(m1) == len(m2.query("ano == 2026"))
    u = comparar(uf1, uf2.query("ano == 2026"), ["uf"]).merge(regiao, on="uf", validate="one_to_one")
    # Prova do 1º turno municipal contra o bruto munzona por UF, em todos os campos.
    provas = []
    for uf, grupo in m.groupby("uf"):
        origem = uf1.set_index("uf").loc[uf]
        for c in CONTAS:
            esperado, obtido = int(origem[c]), int(grupo[c + "_1t"].sum())
            provas.append({"uf": uf, "campo": c, "obtido_municipal": obtido, "esperado_bruto": esperado,
                           "diferenca": obtido - esperado, "bate": obtido == esperado})
    salvar(pd.DataFrame(provas), "prova_primeiro_turno.csv", FONTE_MUN + "; dados/bruto/tse/*_2026_BR.csv", ",".join(CONTAS), "Soma municipal por UF contra brutos de votação e detalhe; exterior fora da base municipal")
    assert all(p["bate"] for p in provas)
    nacionais = uf2.groupby("ano", as_index=False)[CONTAS].sum()
    n = indicadores(nacionais)
    n["adversario"] = n.ano.map({2022: "Jair Bolsonaro", 2026: "Flávio Bolsonaro"})
    n["abstencao_pct_publicada_tse"] = n.ano.map({2022: 20.59, 2026: 19.22})
    n["nota_abstencao"] = "2022: a notícia oficial informa 20,59%, mas suas próprias contagens resultam em 20,581571...% (20,58%); a conta é mantida, sem ajustar números. 2026: 19,22% publicado coincide com o arredondamento."
    n["abstencao_brancos_nulos"] = n.abstencoes + n.brancos + n.nulos
    n["nao_validos_sobre_diferenca"] = n.abstencao_brancos_nulos / n.diferenca_absoluta
    salvar(n, "resultado_nacional.csv", "dados/pbi/uf_2turno.csv", ",".join(CONTAS), "Brasil com ZZ; percentuais exatos calculados; abstenção sobre presença+abstenção; comparar contingentes não identifica voto potencial")
    resultado2 = nacionais.set_index("ano").loc[2026].to_dict()
    resultado1 = uf1[CONTAS].sum().to_dict()
    dif = pd.DataFrame([{"campo": c, "valor_2022": int(nacionais.set_index("ano").loc[2022, c]),
                         "valor_2026": int(resultado2[c]), "delta": int(resultado2[c] - nacionais.set_index("ano").loc[2022, c])} for c in CONTAS])
    salvar(dif, "comparacao_nacional_2022.csv", "dados/pbi/uf_2turno.csv", ",".join(CONTAS), "Segundo turno de 2026 menos segundo turno de 2022; candidatos adversários diferentes")
    por_ano = n.set_index("ano")
    percentuais = pd.DataFrame([{"indicador": c, "valor_2022": por_ano.loc[2022, c], "valor_2026": por_ano.loc[2026, c],
                                 "delta_pontos_percentuais": por_ano.loc[2026, c] - por_ano.loc[2022, c]}
                                for c in ["pt_pct", "adv_pct", "margem_pt_pp", "abstencao_pct"]])
    salvar(percentuais, "comparacao_percentuais_2022.csv", "dados/pbi/uf_2turno.csv", "pt,adv,validos,comparecimento,abstencoes",
           "Brasil com ZZ; diferença calculada antes do arredondamento; percentual candidato sobre válidos; abstenção sobre presença+abstenção")
    r = uf2.merge(regiao, on="uf", validate="many_to_one")
    salvar(indicadores(r), "resultado_uf.csv", "dados/pbi/uf_2turno.csv; dados/pbi/municipio.csv", ",".join(CONTAS) + ",uf,regiao", "Percentuais por UF e ano; ZZ separado de UFs")
    salvar(indicadores(r.groupby(["ano", "regiao"], as_index=False)[CONTAS].sum()), "resultado_regiao.csv", "dados/pbi/uf_2turno.csv; dados/pbi/municipio.csv", ",".join(CONTAS) + ",uf,regiao", "Somar votos antes de calcular percentuais; exterior em categoria própria")
    vencedores = indicadores(r)
    salvar(vencedores.groupby(["ano", "regiao", "vencedor"], as_index=False).agg(quantidade=("uf", "size")), "vitorias_uf.csv", "dados/pbi/uf_2turno.csv", "pt,adv,uf", "Conta 27 UFs; ZZ aparece somente em Exterior; vencedor Adversário é Jair em 2022 e Flávio em 2026")
    for candidato, coluna in [("flavio", "perda_vantagem_flavio"), ("lula", "perda_vantagem_lula")]:
        m["posicao_perda_vantagem_" + candidato] = m[coluna].rank(method="min", ascending=False).astype(int)
        u["posicao_perda_vantagem_" + candidato] = u[coluna].rank(method="min", ascending=False).astype(int)
    salvar(m.sort_values("perda_vantagem_flavio", ascending=False), "comparacao_municipios.csv", FONTE_MUN, ",".join(CONTAS) + ",populacao,renda_pc,porte,quinto", "2026: 2º menos 1º turno; perda de vantagem de Flávio = ganho de Lula menos ganho de Flávio, em votos; não implica queda absoluta de votos de Flávio; posições simétricas para Lula e Flávio, empate recebe menor posição")
    salvar(u.sort_values("perda_vantagem_flavio", ascending=False), "comparacao_ufs.csv", FONTE_UF, ",".join(CONTAS), "2026: 2º menos 1º turno; ZZ incluído e identificado")
    for coluna in ["regiao", "porte", "quinto"]:
        salvar(agregado(m, coluna), f"crescimento_{coluna}.csv", FONTE_MUN, ",".join(CONTAS) + "," + coluna,
               "Municípios sem exterior; categorias e renda per capita/população do cadastro, Censo 2022; ganho não identifica origem individual dos votos")
    salvar(m[m.mudou_vencedor], "viradas_municipios.csv", FONTE_MUN, "pt,adv,cd_ibge", "Todas as mudanças em ambos os sentidos; empate separado")
    salvar(u[u.mudou_vencedor], "viradas_ufs.csv", FONTE_UF, "pt,adv,uf", "Todas as mudanças em ambos os sentidos; ZZ identificado")
    comp22 = m2.query("ano == 2026").merge(m2.query("ano == 2022"), on="cd_ibge", how="outer", suffixes=("_2026", "_2022"), validate="one_to_one", indicator=True).merge(cad, on="cd_ibge", validate="one_to_one")
    comp22["comparavel"] = comp22._merge.eq("both")
    for c in CONTAS:
        comp22["delta_" + c] = comp22[c + "_2026"] - comp22[c + "_2022"]
    comp22["perda_votos_flavio_vs_jair"] = -comp22.delta_adv
    comp22["perda_votos_lula_vs_lula"] = -comp22.delta_pt
    for candidato, coluna in [("flavio", "perda_votos_flavio_vs_jair"), ("lula", "perda_votos_lula_vs_lula")]:
        comp22["posicao_perda_votos_" + candidato] = comp22[coluna].rank(method="min", ascending=False).astype("Int64")
    comp22["ressalva_territorial"] = np.where(comp22.uf.eq("MT") & comp22.nome.isin(["Sorriso", "Nova Ubiratã", "Vera", "Paranatinga", "Boa Esperança do Norte"]),
        "Criação de Boa Esperança do Norte e revisão territorial/populacional. Mesmo código não assegura área constante; queda não deve ser atribuída só ao voto. Ver METODO.md e fonte IBGE.", "Código coincidente não é auditoria de fronteira constante")
    for ano in [2022, 2026]:
        comp22[f"adv_pct_{ano}"] = 100 * comp22[f"adv_{ano}"] / comp22[f"validos_{ano}"]
        comp22[f"pt_pct_{ano}"] = 100 * comp22[f"pt_{ano}"] / comp22[f"validos_{ano}"]
        comp22[f"abstencao_pct_{ano}"] = 100 * comp22[f"abstencoes_{ano}"] / (comp22[f"abstencoes_{ano}"] + comp22[f"comparecimento_{ano}"])
    for conta in ["pt", "adv", "abstencao"]:
        comp22["delta_" + conta + "_pp"] = comp22[f"{conta}_pct_2026"] - comp22[f"{conta}_pct_2022"]
    salvar(comp22.sort_values("perda_votos_flavio_vs_jair", ascending=False), "municipios_2026_vs_2022.csv", FONTE_MUN,
           ",".join(CONTAS) + ",cd_ibge", "Comparação de segundo turno; ausentes em 2022 ficam vazios, nunca zero; população e limites municipais podem mudar")
    cuf = uf2.query("ano == 2026").merge(uf2.query("ano == 2022"), on="uf", suffixes=("_2026", "_2022"), validate="one_to_one")
    for c in CONTAS:
        cuf["delta_" + c] = cuf[c + "_2026"] - cuf[c + "_2022"]
    for ano in [2022, 2026]:
        cuf[f"adv_pct_{ano}"] = 100 * cuf[f"adv_{ano}"] / cuf[f"validos_{ano}"]
        cuf[f"pt_pct_{ano}"] = 100 * cuf[f"pt_{ano}"] / cuf[f"validos_{ano}"]
    for conta in ["pt", "adv"]:
        cuf["delta_" + conta + "_pp"] = cuf[f"{conta}_pct_2026"] - cuf[f"{conta}_pct_2022"]
    cuf["perda_votos_flavio_vs_jair"] = -cuf.delta_adv
    cuf["perda_votos_lula_vs_lula"] = -cuf.delta_pt
    for candidato, coluna in [("flavio", "perda_votos_flavio_vs_jair"), ("lula", "perda_votos_lula_vs_lula")]:
        cuf["posicao_perda_votos_" + candidato] = cuf[coluna].rank(method="min", ascending=False).astype(int)
    salvar(cuf.sort_values("perda_votos_flavio_vs_jair", ascending=False), "ufs_2026_vs_2022.csv", "dados/pbi/uf_2turno.csv", ",".join(CONTAS), "Comparação de segundos turnos por UF, inclusive ZZ; ordenar perdas absolutas dos dois candidatos")
    grandes = m.sort_values(["populacao", "cd_ibge"], ascending=[False, True]).copy()
    grandes["ordem_populacao"] = range(1, len(grandes) + 1)
    salvar(grandes.head(100), "grandes_cidades.csv", FONTE_MUN, "populacao,pt,adv,validos,comparecimento", "100 maiores populações do cadastro Censo 2022; posição determinística pelo código em empate; sem exterior")
    por_porte = m.assign(grupo_grandes=np.select([m.populacao.ge(500000), m.populacao.lt(500000)],
                                                ["500 mil ou mais", "Menos de 500 mil"], default="Sem população no cadastro"))
    salvar(agregado(por_porte, "grupo_grandes"), "peso_grandes_cidades.csv", FONTE_MUN, "populacao,pt,adv,validos,comparecimento", "Corte explícito de população do Censo 2022, não eleitorado")
    ab = u.copy()
    ab22 = indicadores(uf2.query("ano == 2022"))[["uf", "abstencoes", "abstencao_pct", "comparecimento", "aptos"]]
    ab = ab.merge(ab22.rename(columns={c: c + "_2022_2t" for c in ab22.columns if c != "uf"}), on="uf", validate="one_to_one")
    ab["delta_abstencao_2022_pp"] = ab.abstencao_pct_2t - ab.abstencao_pct_2022_2t
    ab["delta_abstencoes_2022"] = ab.abstencoes_2t - ab.abstencoes_2022_2t
    salvar(ab.sort_values("delta_abstencao_pp"), "abstencao_ufs.csv", FONTE_UF, "aptos,comparecimento,abstencoes,pt,adv,validos", "2026 2º x 1º e 2022 2º; taxa sobre comparecimento+abstenções; taxa sobre aptos também consta nos resultados nacionais")
    m["grupo_comparecimento"] = np.select([m.delta_comparecimento.gt(0), m.delta_comparecimento.lt(0)], ["Aumentou", "Diminuiu"], default="Igual")
    m["grupo_voto_presenca"] = m.vencedor_1t + " no 1º turno / presença " + m.grupo_comparecimento.str.lower()
    salvar(agregado(m, "grupo_voto_presenca"), "comparecimento_voto_1turno.csv", FONTE_MUN, "pt,adv,validos,comparecimento,abstencoes", "Associação por vencedor municipal do 1º turno e sentido da mudança de presença; não identifica quem voltou ou deixou de votar")
    corrs = []
    for cand, coluna in [("Lula", "pt_pct_1t"), ("Flávio", "adv_pct_1t")]:
        corrs.append({"candidato": cand, "correlacao_ponderada": correlacao(m[coluna], m.delta_abstencao_pp, m.aptos_1t), "municipios": len(m)})
    salvar(pd.DataFrame(corrs), "abstencao_correlacao.csv", FONTE_MUN, "pt/validos ou adv/validos no 1º turno; delta_abstencao_pp; peso=aptos_1t", "Correlação de Pearson ponderada pelo eleitorado; relação municipal sem inferência causal")
    modelos = regressao(m)
    placar, transf = pesquisas(resultado1, resultado2)
    modelos_demais = modelos[modelos.modelo.eq("principal") & modelos.termo.eq("demais")]
    confronto = []
    for _, pesquisa in transf[transf.segmento_1turno.eq("agregado_3via")].iterrows():
        for candidato, campo in [("Lula", "lula"), ("Flávio", "flavio")]:
            modelo = modelos_demais[modelos_demais.candidato.eq(candidato)].iloc[0]
            confronto.append({"instituto": pesquisa.instituto, "divulgacao": pesquisa.divulgacao,
                               "segmento": "agregado_3via", "candidato": candidato, "pesquisa_pct_base_total": pesquisa[campo],
                               "coeficiente_ecologico_vezes_100": 100 * modelo.coeficiente,
                               "ic95_ecologico_inferior_vezes_100": 100 * modelo.ic95_inferior,
                               "ic95_ecologico_superior_vezes_100": 100 * modelo.ic95_superior,
                               "diferenca_descritiva_pontos": 100 * modelo.coeficiente - pesquisa[campo],
                               "n_segmento": pesquisa.n_segmento, "fonte_url_pesquisa": pesquisa.fonte_url,
                               "aviso": "Medidas diferentes: intenção individual declarada versus coeficiente de associação municipal. Não é erro da pesquisa nem taxa observada de transferência. " + ALERTA_ECO})
    salvar(pd.DataFrame(confronto), "transferencia_pesquisa_vs_ecologia.csv", "dados/pbi/transferencia.csv; dados/saida/2turno/regressao_ecologica.csv",
           "segmento_1turno=agregado_3via; lula,flavio; modelo=principal,termo=demais,coeficiente",
           "Somente segmento agregado publicado; sem sintetizar segmentos de cobertura ou bases diferentes. Coeficiente x100 é escala comparável em pontos, não probabilidade individual")
    marcos = noite(int(resultado2["aptos"]), int(resultado2["validos"]))
    # Conserva o timestamp final das UFs; não o interpreta como instante em que concluíram 100%.
    atual = pd.read_csv(RAIZ / "dados/apuracao/ufs.csv")
    salvar(atual[atual.uf.ne("BR")][["uf", "atualizado_tse", "secoes_total", "secoes_totalizadas"]], "horarios_finais_ufs.csv",
           "dados/apuracao/ufs.csv", "uf,atualizado_tse,secoes_total,secoes_totalizadas",
           "Retrato final, sem histórico por UF. Horas locais de geração não provam ordem de conclusão e não explicam a troca de liderança")
    salvar(pd.DataFrame(CATALOGO), "catalogo.csv", "pipeline/analisar_2turno.py", "arquivo,arquivo_origem,campo_origem,metodo", "Dicionário das saídas e fórmulas de origem")
    insumos = [PBI / n for n in ["municipio.csv", "municipio_ano.csv", "municipio_2turno.csv", "uf_2turno.csv", "pesquisa.csv", "transferencia.csv", "candidato_ano.csv"]]
    insumos += [RAIZ / "dados/apuracao" / n for n in ["ultimo.json", "ufs.csv", "historico.csv"]]
    insumos += [RAIZ / "dados/bruto/tse" / nome for nome in ["presidente_2022_BR.csv", "detalhe_2022_BR.csv", "presidente_2026_BR.csv", "detalhe_2026_BR.csv"]]
    pd.DataFrame([{"arquivo": p.relative_to(RAIZ).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in insumos]).to_csv(SAIDA / "hashes_analise.csv", index=False)
    resumo = {"municipios_2026": len(m), "municipios_comparaveis_2022": int(comp22.comparavel.sum()),
              "municipios_sem_base_2022": comp22[~comp22.comparavel][["cd_ibge", "nome", "uf"]].to_dict("records"),
              "viradas_municipais": m.groupby(["vencedor_1t", "vencedor_2t"]).size().to_dict(),
              "saldo_brasil_1t": int(resultado1["pt"] - resultado1["adv"]),
              "saldo_brasil_2t": int(resultado2["pt"] - resultado2["adv"]),
              "ganho_lula_brasil": int(resultado2["pt"] - resultado1["pt"]),
              "ganho_flavio_brasil": int(resultado2["adv"] - resultado1["adv"])}
    resumo["viradas_municipais"] = {" → ".join(k): int(v) for k, v in resumo["viradas_municipais"].items()}
    (SAIDA / "analise_resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print("Análises concluídas; consulte catalogo.csv e os avisos de método em cada saída.")


if __name__ == "__main__":
    main()
