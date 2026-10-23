"""Monta `mockup/data/eleicoes.json`: tudo o que as telas do mockup mostram, já calculado e formatado em pt-BR.

A tela não calcula: formata. Cada tela leva a pergunta, a manchete (a resposta, com o número-chave) e a próxima
pergunta; cada número vem com o valor bruto ao lado do texto. As frases saem daqui — nada escrito à mão no Figma.

Entradas: `dados/saida/{votos_municipio,municipios,nacional}.csv` (pipeline/consolidar.py) e, quando existir,
`dados/bruto/pesquisas/*.csv` (levantamento de pesquisas).
Uso: python -I -X utf8 pipeline/montar_dados_mockup.py
"""
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
SAIDA_DADOS = RAIZ / "dados" / "saida"
PESQUISAS = RAIZ / "dados" / "bruto" / "pesquisas"
DESTINO = RAIZ / "mockup" / "data" / "eleicoes.json"
ANOS = [2006, 2010, 2014, 2018, 2022, 2026]
CIDADE_GUIA = ("Contagem", "MG")
PORTES = [(0, 10_000, "até 10 mil"), (10_000, 50_000, "10 a 50 mil"), (50_000, 200_000, "50 a 200 mil"),
          (200_000, 1_000_000, "200 mil a 1 milhão"), (1_000_000, 10**9, "mais de 1 milhão")]
QUINTIS = ["mais pobres", "2º quinto", "3º quinto", "4º quinto", "mais ricas"]
# Grade de quadrados das UFs (coluna, linha): cada UF numa célula, na posição aproximada do mapa.
GRADE_UF = {"RR": (1, 0), "AP": (3, 0), "EX": (5, 0),
            "AM": (1, 1), "PA": (2, 1), "MA": (3, 1), "CE": (4, 1), "RN": (5, 1),
            "AC": (0, 2), "RO": (1, 2), "TO": (2, 2), "PI": (3, 2), "PE": (4, 2), "PB": (5, 2),
            "MT": (1, 3), "GO": (2, 3), "BA": (3, 3), "SE": (4, 3), "AL": (5, 3),
            "MS": (1, 4), "DF": (2, 4), "MG": (3, 4), "ES": (4, 4),
            "PR": (1, 5), "SP": (2, 5), "RJ": (3, 5), "SC": (1, 6), "RS": (1, 7)}
NOME_UF = {"AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
           "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
           "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
           "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
           "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
           "SE": "Sergipe", "TO": "Tocantins", "EX": "Exterior"}
REGIAO_UF = {"Norte": "AC AP AM PA RO RR TO", "Nordeste": "AL BA CE MA PB PE PI RN SE",
             "Centro-Oeste": "DF GO MT MS", "Sudeste": "ES MG RJ SP", "Sul": "PR RS SC"}
REGIAO_UF = {uf: r for r, ufs in REGIAO_UF.items() for uf in ufs.split()}


# ---------- formatação pt-BR ----------
def milhar(n):
    return f"{int(round(n)):,}".replace(",", ".")


def dec(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def menos(txt):
    return txt.replace("-", "−")


def mi(n, casas=1):
    return f"{dec(n / 1e6, casas)} mi"


def mi_sinal(n, casas=2):
    return menos(("+" if n > 0 else "") + mi(n, casas))


def pct(x, casas=1):
    return f"{dec(100 * x, casas)}%"


def pp(x, casas=1, sinal=True):
    v = 100 * x
    txt = (("+" if v > 0 else "") if sinal else "") + dec(v, casas)
    return menos(txt) + " p.p."


def margem_txt(m):
    """Margem PT − adversário, em p.p., dita pelo lado que vence."""
    v = 100 * m
    return menos(("+" if v > 0 else "") + dec(v, 1)) + " p.p."


# ---------- leitura ----------
def carregar():
    votos = pd.read_csv(SAIDA_DADOS / "votos_municipio.csv", dtype={"cd_ibge": str})
    muns = pd.read_csv(SAIDA_DADOS / "municipios.csv", dtype={"cd_ibge": str})
    nac = pd.read_csv(SAIDA_DADOS / "nacional.csv")
    return votos, muns, nac


def candidato(nac, ano, partido=None, posicao=None):
    linhas = nac[nac.ano == ano].sort_values("votos", ascending=False)
    if partido:
        linhas = linhas[linhas.SG_PARTIDO == partido]
    linha = linhas.iloc[posicao or 0]
    return {"nome": linha.NM_URNA_CANDIDATO.title(), "partido": linha.SG_PARTIDO, "numero": int(linha.NR_CANDIDATO),
            "votos": int(linha.votos), "pct": float(linha.pct)}


NOMES_CURTOS = {"LULA": "Lula", "FLAVIO BOLSONARO": "Flávio Bolsonaro", "JAIR BOLSONARO": "Jair Bolsonaro",
                "GERALDO ALCKMIN": "Geraldo Alckmin", "JOSÉ SERRA": "José Serra", "AÉCIO NEVES": "Aécio Neves",
                "DILMA": "Dilma Rousseff", "FERNANDO HADDAD": "Fernando Haddad",
                "ESCRITOR AUGUSTO CURY": "Augusto Cury", "RENAN SANTOS": "Renan Santos"}


def nome(n):
    return NOMES_CURTOS.get(n.upper(), n.title())


# ---------- telas ----------
def base_municipal(votos, muns):
    largo = votos.pivot_table(index="cd_ibge", columns="ano", values=["pt", "adv", "demais", "validos"], aggfunc="sum")
    largo.columns = [f"{c}{a}" for c, a in largo.columns]
    d = largo.join(muns.set_index("cd_ibge")[["nome", "uf", "regiao", "populacao", "renda_pc"]])
    for a in ANOS:
        d[f"marg{a}"] = (d[f"pt{a}"] - d[f"adv{a}"]) / d[f"validos{a}"]
        d[f"ptp{a}"] = d[f"pt{a}"] / d[f"validos{a}"]
        d[f"advp{a}"] = d[f"adv{a}"] / d[f"validos{a}"]
    d["dmarg"] = d.marg2026 - d.marg2022
    d["dpt"] = d.pt2026 - d.pt2022
    d["dadv"] = d.adv2026 - d.adv2022
    d["virou"] = (d.marg2022 > 0) & (d.marg2026 < 0)
    d["voltou"] = (d.marg2022 < 0) & (d.marg2026 > 0)
    d["porte"] = pd.cut(d.populacao, [p[0] for p in PORTES] + [PORTES[-1][1]], labels=[p[2] for p in PORTES],
                        right=False)
    d["quinto"] = pd.qcut(d.renda_pc, 5, labels=QUINTIS)
    return d


def margem_agregada(g, a):
    return (g[f"pt{a}"].sum() - g[f"adv{a}"].sum()) / g[f"validos{a}"].sum()


def tela_placar(nac):
    c26 = nac[nac.ano == 2026].sort_values("votos", ascending=False)
    validos = int(c26.validos_ano.iloc[0])
    lista = [{"nome": nome(r.NM_URNA_CANDIDATO), "partido": r.SG_PARTIDO, "votos": int(r.votos),
              "votos_txt": mi(r.votos, 2) if r.votos >= 1e6 else milhar(r.votos), "pct": float(r.pct),
              "pct_txt": pct(r.pct)} for r in c26.itertuples()]
    flavio, lula = candidato(nac, 2026, "PL"), candidato(nac, 2026, "PT")
    bolso22, lula22 = candidato(nac, 2022, "PL"), candidato(nac, 2022, "PT")
    dif = flavio["votos"] - lula["votos"]
    principais = lista[:4]
    demais = lista[4:]
    return {
        "tela": 1, "nome": "Placar", "pergunta": "Quem venceu o 1º turno, e por quanto?",
        "manchete": f"Flávio terminou {mi(dif, 2)} de votos à frente de Lula",
        "proxima_pergunta": "As pesquisas viram isso chegando?",
        "validos": validos, "validos_txt": milhar(validos),
        "candidatos": principais,
        "demais": {"qtd": len(demais), "votos": int(sum(c["votos"] for c in demais)),
                   "pct": float(sum(c["pct"] for c in demais)),
                   "pct_txt": pct(sum(c["pct"] for c in demais)),
                   "nomes": [c["nome"] for c in demais]},
        "diferenca": {"votos": dif, "votos_txt": milhar(dif), "pp": flavio["pct"] - lula["pct"],
                      "pp_txt": pp(flavio["pct"] - lula["pct"], sinal=False)},
        "de_2022_para_2026": [
            {"lado": "PT", "de": {"nome": "Lula", "ano": 2022, "votos": lula22["votos"], "votos_txt": mi(lula22["votos"], 2),
                                  "pct_txt": pct(lula22["pct"])},
             "para": {"nome": "Lula", "ano": 2026, "votos": lula["votos"], "votos_txt": mi(lula["votos"], 2),
                      "pct_txt": pct(lula["pct"])},
             "variacao": lula["votos"] - lula22["votos"], "variacao_txt": mi_sinal(lula["votos"] - lula22["votos"])},
            {"lado": "PL", "de": {"nome": "Jair Bolsonaro", "ano": 2022, "votos": bolso22["votos"],
                                  "votos_txt": mi(bolso22["votos"], 2), "pct_txt": pct(bolso22["pct"])},
             "para": {"nome": "Flávio Bolsonaro", "ano": 2026, "votos": flavio["votos"],
                      "votos_txt": mi(flavio["votos"], 2), "pct_txt": pct(flavio["pct"])},
             "variacao": flavio["votos"] - bolso22["votos"], "variacao_txt": mi_sinal(flavio["votos"] - bolso22["votos"])},
        ],
        "nota": "Votos válidos do 1º turno, com o exterior. TSE, arquivo de 22/10/2026.",
    }


def tela_virada(d):
    viraram = d[d.virou].sort_values("populacao", ascending=False)
    lula22, lula26 = int((d.marg2022 > 0).sum()), int((d.marg2026 > 0).sum())
    lista = [{"municipio": r.nome, "uf": r.uf, "populacao": int(r.populacao), "populacao_txt": milhar(r.populacao),
              "lula22_txt": pct(r.ptp2022), "flavio26_txt": pct(r.advp2026), "margem22_txt": margem_txt(r.marg2022),
              "margem26_txt": margem_txt(r.marg2026)} for r in viraram.head(10).itertuples()]
    por_regiao = viraram.groupby("regiao").size().sort_values(ascending=False)
    return {
        "tela": 3, "nome": "Virada", "pergunta": "Onde os votos mudaram de lado?",
        "manchete": f"{len(viraram)} municípios trocaram Lula por Flávio; nenhum fez o caminho inverso",
        "proxima_pergunta": "Como cada estado se moveu?",
        "viraram": int(len(viraram)), "voltaram": int(d.voltou.sum()),
        "lula_venceu": {"2022": lula22, "2026": lula26, "2022_txt": milhar(lula22), "2026_txt": milhar(lula26)},
        "flavio_venceu_2026": int((d.marg2026 < 0).sum()), "flavio_venceu_2026_txt": milhar((d.marg2026 < 0).sum()),
        "municipios": int(len(d)), "municipios_txt": milhar(len(d)),
        "pt_perdeu_votos_em": int((d.dpt < 0).sum()), "pt_perdeu_votos_em_txt": milhar((d.dpt < 0).sum()),
        "pl_ganhou_votos_em": int((d.dadv > 0).sum()), "pl_ganhou_votos_em_txt": milhar((d.dadv > 0).sum()),
        "variacao_votos": {"lula": int(d.dpt.sum()), "lula_txt": mi_sinal(d.dpt.sum()),
                           "pl": int(d.dadv.sum()), "pl_txt": mi_sinal(d.dadv.sum()),
                           "nota": "soma dos municípios, sem o exterior"},
        "viraram_por_regiao": [{"regiao": r, "qtd": int(n)} for r, n in por_regiao.items()],
        "maiores_que_viraram": lista,
        "mapas": {"vencedor_e_virada": "arte/mapas/virada.png", "bolhas_lula": "arte/mapas/bolhas-lula.png",
                  "bolhas_pl": "arte/mapas/bolhas-pl.png"},
    }


def tela_estados(d, nac):
    linhas = []
    for uf, g in d.groupby("uf"):
        m22, m26 = margem_agregada(g, 2022), margem_agregada(g, 2026)
        linhas.append({"uf": uf, "nome": NOME_UF[uf], "regiao": REGIAO_UF[uf], "m22": m22, "m26": m26,
                       "pt26": g.pt2026.sum() / g.validos2026.sum(), "adv26": g.adv2026.sum() / g.validos2026.sum(),
                       "validos26": int(g.validos2026.sum()), "viraram": int(g.virou.sum()), "municipios": int(len(g))})
    # Exterior = nacional − municípios (2022 e 2026 não têm voto em trânsito no arquivo).
    ext = {}
    for a in (2022, 2026):
        n = nac[nac.ano == a]
        pt_n = n[n.SG_PARTIDO == "PT"].votos.sum()
        adv_n = n[n.SG_PARTIDO != "PT"].sort_values("votos", ascending=False).votos.iloc[0]
        val_n = n.votos.sum()
        ext[a] = (pt_n - d[f"pt{a}"].sum(), adv_n - d[f"adv{a}"].sum(), val_n - d[f"validos{a}"].sum())
    linhas.append({"uf": "EX", "nome": "Exterior", "regiao": "Exterior",
                   "m22": (ext[2022][0] - ext[2022][1]) / ext[2022][2], "m26": (ext[2026][0] - ext[2026][1]) / ext[2026][2],
                   "pt26": ext[2026][0] / ext[2026][2], "adv26": ext[2026][1] / ext[2026][2],
                   "validos26": int(ext[2026][2]), "viraram": 0, "municipios": 0})
    for l in linhas:
        l["dm"] = l["m26"] - l["m22"]
        l["col"], l["linha"] = GRADE_UF[l["uf"]]
    linhas.sort(key=lambda l: l["dm"])
    ufs = [{"uf": l["uf"], "nome": l["nome"], "regiao": l["regiao"], "grade": {"col": l["col"], "linha": l["linha"]},
            "margem22": l["m22"], "margem26": l["m26"], "variacao": l["dm"],
            "margem22_txt": margem_txt(l["m22"]), "margem26_txt": margem_txt(l["m26"]), "variacao_txt": pp(l["dm"]),
            "vencedor22": "Lula" if l["m22"] > 0 else "Bolsonaro", "vencedor26": "Lula" if l["m26"] > 0 else "Flávio",
            "lula26_txt": pct(l["pt26"]), "flavio26_txt": pct(l["adv26"]), "validos26_txt": milhar(l["validos26"]),
            "municipios_que_viraram": l["viraram"], "municipios": l["municipios"]} for l in linhas]
    regioes = []
    for r, g in d.groupby("regiao"):
        m22, m26 = margem_agregada(g, 2022), margem_agregada(g, 2026)
        regioes.append({"regiao": r, "margem22": m22, "margem26": m26, "variacao": m26 - m22,
                        "margem22_txt": margem_txt(m22), "margem26_txt": margem_txt(m26), "variacao_txt": pp(m26 - m22)})
    regioes.sort(key=lambda x: x["variacao"])
    so_ufs = [u for u in ufs if u["uf"] != "EX"]
    caiu_em_todas = all(u["variacao"] < 0 for u in so_ufs)
    mudaram = [u for u in so_ufs if u["vencedor22"] == "Lula" and u["vencedor26"] == "Flávio"]
    caiu = [u for u in so_ufs if u["variacao"] < 0]
    excecoes = [u for u in so_ufs if u["variacao"] >= 0]
    nomes_mudaram = " e ".join(u["nome"] for u in sorted(mudaram, key=lambda u: u["nome"]))
    manchete = f"Lula perdeu margem em {len(caiu)} das {len(so_ufs)} unidades; {nomes_mudaram} mudaram de lado"
    return {"tela": 4, "nome": "Estados", "pergunta": "Como cada estado se moveu?", "manchete": manchete,
            "excecoes": [{"uf": u["uf"], "nome": u["nome"], "variacao_txt": u["variacao_txt"]} for u in excecoes],
            "proxima_pergunta": "Em que tipo de cidade Lula perdeu mais?",
            "lula_perdeu_margem_em_todas": caiu_em_todas,
            "estados_que_mudaram_de_lado": [{"uf": u["uf"], "nome": u["nome"]} for u in mudaram],
            "ufs": ufs, "regioes": regioes,
            "nota": "Margem = (Lula − adversário) ÷ votos válidos; positivo, Lula à frente. Variação 2022 → 2026."}


def tela_perfil(d):
    celulas, linhas_txt = [], []
    limites = d.groupby("quinto", observed=True).renda_pc.agg(["min", "max"])
    for porte in [p[2] for p in PORTES]:
        for q in QUINTIS:
            g = d[(d.porte == porte) & (d.quinto == q)]
            if len(g) == 0:
                celulas.append({"porte": porte, "quinto": q, "municipios": 0, "variacao": None, "variacao_txt": "—"})
                continue
            v = margem_agregada(g, 2026) - margem_agregada(g, 2022)
            exemplos = g.sort_values("populacao", ascending=False).head(3)
            celulas.append({"porte": porte, "quinto": q, "municipios": int(len(g)), "variacao": v,
                            "variacao_txt": pp(v), "margem26_txt": margem_txt(margem_agregada(g, 2026)),
                            "exemplos": [f"{r.nome} ({r.uf})" for r in exemplos.itertuples()]})
    validas = [c for c in celulas if c["variacao"] is not None and c["municipios"] >= 10]
    pior = min(validas, key=lambda c: c["variacao"])
    melhor = max(validas, key=lambda c: c["variacao"])
    por_porte = [{"porte": p[2], "variacao_txt": pp(margem_agregada(d[d.porte == p[2]], 2026)
                                                    - margem_agregada(d[d.porte == p[2]], 2022)),
                  "municipios": int((d.porte == p[2]).sum())} for p in PORTES]
    por_quinto = [{"quinto": q, "variacao_txt": pp(margem_agregada(d[d.quinto == q], 2026)
                                                  - margem_agregada(d[d.quinto == q], 2022)),
                   "renda_txt": f"R$ {milhar(limites.loc[q, 'min'])} a R$ {milhar(limites.loc[q, 'max'])}"}
                  for q in QUINTIS]
    return {"tela": 5, "nome": "Perfil", "pergunta": "Em que tipo de cidade Lula perdeu mais?",
            "manchete": f"Nas cidades {pior['porte']} e {pior['quinto']}, a margem de Lula caiu {pp(pior['variacao'], sinal=False).replace('−', '')}"
                        .replace("cidades até 10 mil", "cidades de até 10 mil habitantes")
                        .replace("e mais ricas", "e de renda mais alta"),
            "proxima_pergunta": "Como o PT chegou até aqui?",
            "celulas": celulas, "linhas": por_porte, "colunas": por_quinto,
            "maior_queda": {"porte": pior["porte"], "quinto": pior["quinto"], "variacao_txt": pior["variacao_txt"],
                            "municipios": pior["municipios"]},
            "menor_queda": {"porte": melhor["porte"], "quinto": melhor["quinto"], "variacao_txt": melhor["variacao_txt"],
                            "municipios": melhor["municipios"]},
            "regua": "Porte: população do Censo 2022. Renda: rendimento domiciliar per capita médio do Censo 2022, "
                     "em quintos de municípios (cada coluna tem 1.114 cidades). Célula: variação da margem de Lula "
                     "sobre o adversário, 2022 → 2026, somando os votos das cidades da célula.",
            "nota": "— = não há município nessa combinação."}


def tela_serie(nac, d):
    anos = []
    for a in ANOS:
        pt_c = candidato(nac, a, "PT")
        adv_c = nac[(nac.ano == a) & (nac.SG_PARTIDO != "PT")].sort_values("votos", ascending=False).iloc[0]
        anos.append({"ano": a, "pt": {"nome": nome(pt_c["nome"]), "pct": pt_c["pct"], "pct_txt": pct(pt_c["pct"])},
                     "adversario": {"nome": nome(adv_c.NM_URNA_CANDIDATO), "partido": adv_c.SG_PARTIDO,
                                    "pct": float(adv_c.pct), "pct_txt": pct(adv_c.pct)},
                     "pt_na_frente": pt_c["pct"] > adv_c.pct})
    regioes = []
    for r, g in d.groupby("regiao"):
        regioes.append({"regiao": r, "serie": [{"ano": a, "pt_pct": float(g[f"pt{a}"].sum() / g[f"validos{a}"].sum()),
                                                "pt_pct_txt": pct(g[f"pt{a}"].sum() / g[f"validos{a}"].sum()),
                                                "adv_pct": float(g[f"adv{a}"].sum() / g[f"validos{a}"].sum()),
                                                "adv_pct_txt": pct(g[f"adv{a}"].sum() / g[f"validos{a}"].sum())}
                                               for a in ANOS]})
    atras = [x["ano"] for x in anos if not x["pt_na_frente"]]
    return {"tela": 6, "nome": "Série", "pergunta": "Como o PT chegou até aqui, de 2006 a 2026?",
            "manchete": f"Pela {len(atras)}ª vez em seis eleições, o PT termina o 1º turno em segundo lugar",
            "proxima_pergunta": "E na minha cidade?",
            "anos": anos, "pt_atras_em": atras, "regioes": regioes,
            "nota": "% dos votos válidos no 1º turno. Adversário = o mais votado fora do PT em cada ano."}


def ficha_cidade(d, nome_cidade, uf):
    r = d[(d.nome == nome_cidade) & (d.uf == uf)].iloc[0]
    pares = d[(d.porte == r.porte) & (d.quinto == r.quinto)]
    var_cel = margem_agregada(pares, 2026) - margem_agregada(pares, 2022)
    posicao = int((pares.dmarg < r.dmarg).sum()) + 1
    serie = [{"ano": a, "pt_pct": float(r[f"ptp{a}"]), "pt_pct_txt": pct(r[f"ptp{a}"]),
              "adv_pct": float(r[f"advp{a}"]), "adv_pct_txt": pct(r[f"advp{a}"]),
              "margem": float(r[f"marg{a}"]), "margem_txt": margem_txt(r[f"marg{a}"])} for a in ANOS]
    vence26 = "Lula" if r.marg2026 > 0 else "Flávio"
    pct_venc = r.ptp2026 if r.marg2026 > 0 else r.advp2026
    return {"municipio": r.nome, "uf": r.uf, "regiao": r.regiao, "populacao": int(r.populacao),
            "populacao_txt": milhar(r.populacao), "renda_pc_txt": f"R$ {milhar(r.renda_pc)}",
            "porte": r.porte, "quinto": r.quinto,
            "manchete": f"Em {r.nome}, {vence26} venceu com {pct(pct_venc)}; a margem de Lula caiu {pp(r.dmarg, sinal=False).replace('−', '')} desde 2022"
                        if r.dmarg < 0 else f"Em {r.nome}, {vence26} venceu com {pct(pct_venc)}; a margem de Lula subiu {pp(r.dmarg)} desde 2022",
            "serie": serie,
            "votos": {"lula22": int(r.pt2022), "lula26": int(r.pt2026), "pl22": int(r.adv2022), "pl26": int(r.adv2026),
                      "lula22_txt": milhar(r.pt2022), "lula26_txt": milhar(r.pt2026),
                      "pl22_txt": milhar(r.adv2022), "pl26_txt": milhar(r.adv2026),
                      "variacao_lula_txt": menos(f"{'+' if r.dpt > 0 else ''}{milhar(r.dpt)}"),
                      "variacao_pl_txt": menos(f"{'+' if r.dadv > 0 else ''}{milhar(r.dadv)}")},
            "margem22_txt": margem_txt(r.marg2022), "margem26_txt": margem_txt(r.marg2026), "variacao_txt": pp(r.dmarg),
            "virou": bool(r.virou),
            "entre_parecidas": {"grupo": f"cidades de {r.porte} de habitantes e renda no {r.quinto}"
                                .replace("mil de habitantes", "mil habitantes")
                                .replace("renda no mais pobres", "renda entre as mais pobres")
                                .replace("renda no mais ricas", "renda entre as mais ricas"),
                                "municipios": int(len(pares)), "variacao_grupo_txt": pp(var_cel),
                                "posicao": posicao, "posicao_txt": f"{posicao}ª maior queda de {len(pares)}"}}


def tela_cidade(d):
    guia = ficha_cidade(d, *CIDADE_GUIA)
    outras = [ficha_cidade(d, n, u) for n, u in [("São Paulo", "SP"), ("Salvador", "BA"), ("Chapecó", "SC")]]
    return {"tela": 7, "nome": "Minha cidade", "pergunta": "Como votou a minha cidade?",
            "manchete": guia["manchete"], "proxima_pergunta": "O que os números dizem, afinal?",
            "cidade_guia": guia, "outras_cidades": outras,
            "busca_exemplo": {"digitado": "Cont", "sugestoes": [f"{r.nome} ({r.uf})" for r in
                                                                 d[d.nome.str.startswith("Cont")].sort_values(
                                                                     "populacao", ascending=False).head(5).itertuples()]}}


def data_txt(iso):
    return f"{iso[8:10]}/{iso[5:7]}"


def tela_pesquisas(nac):
    """Antes: a última pesquisa de 1º turno de cada instituto contra o resultado. Agora: o 2º turno, pesquisa a pesquisa.

    Diferença = Flávio − Lula em pontos (positivo, Flávio à frente). Nas últimas pesquisas do 1º turno vale a base que o
    instituto divulgou (válidos quando houve; senão, totais). No 2º turno, a série usa votos totais (todas as pesquisas
    divulgam) e a média usa válidos e totais em separado.
    """
    p1 = pd.read_csv(PESQUISAS / "pesquisas_1turno.csv", sep=";")
    p2 = pd.read_csv(PESQUISAS / "pesquisas_2turno.csv", sep=";")
    flavio, lula = candidato(nac, 2026, "PL"), candidato(nac, 2026, "PT")
    res_dif = 100 * (flavio["pct"] - lula["pct"])

    # Antes: última divulgação de cada instituto (com o par Lula × Flávio publicado).
    ultimas = []
    for inst, g in p1.groupby("instituto"):
        g = g.dropna(subset=["lula", "flavio"])
        if g.empty:
            continue
        ult = g[g.divulgacao == g.divulgacao.max()]
        base = "validos" if (ult.tipo == "validos").any() else "totais"
        r = ult[ult.tipo == base].iloc[0]
        dif = float(r.flavio - r.lula)
        ultimas.append({"instituto": inst, "divulgacao": r.divulgacao, "divulgacao_txt": data_txt(r.divulgacao),
                        "base": "válidos" if base == "validos" else "totais", "lula": float(r.lula), "flavio": float(r.flavio),
                        "lula_txt": pct(r.lula / 100), "flavio_txt": pct(r.flavio / 100),
                        "diferenca": dif, "diferenca_txt": menos(f"{'+' if dif > 0 else ''}{dec(dif)}"),
                        "na_frente": "Flávio" if dif > 0 else ("Lula" if dif < 0 else "empate"),
                        "erro_vs_resultado": dif - res_dif if base == "validos" else None,
                        "erro_vs_resultado_txt": menos(f"{'+' if dif - res_dif > 0 else ''}{dec(dif - res_dif)}")
                        if base == "validos" else "—",
                        "registro_tse": r.registro_tse})
    ultimas.sort(key=lambda u: u["diferenca"])
    lula_frente = [u for u in ultimas if u["na_frente"] == "Lula"]
    com_validos = [u for u in ultimas if u["base"] == "válidos"]
    media_validos_lula = float(np.mean([u["lula"] for u in com_validos]))
    media_validos_flavio = float(np.mean([u["flavio"] for u in com_validos]))
    erro_medio = float(np.mean([u["erro_vs_resultado"] for u in com_validos]))

    # 2º turno: série pesquisa a pesquisa (totais) e médias depois do 1º turno.
    t2 = p2[p2.tipo == "totais"].dropna(subset=["lula", "flavio"]).copy()
    t2["dif"] = t2.flavio - t2.lula
    t2 = t2.sort_values("divulgacao")
    serie = [{"instituto": r.instituto, "divulgacao": r.divulgacao, "divulgacao_txt": data_txt(r.divulgacao),
              "momento": r.momento, "lula": float(r.lula), "flavio": float(r.flavio), "diferenca": float(r.dif),
              "diferenca_txt": menos(f"{'+' if r.dif > 0 else ''}{dec(r.dif)}"),
              "observacao": r.observacao if isinstance(r.observacao, str) else ""} for r in t2.itertuples()]
    # Média móvel de 10 dias por fase (não atravessa o dia da eleição); só dias com 3+ pesquisas na janela.
    media_movel = []
    for momento, g in t2.groupby("momento"):
        datas = pd.to_datetime(g.divulgacao)
        for dia in pd.date_range(datas.min(), datas.max()):
            janela = g[(datas > dia - pd.Timedelta(days=10)) & (datas <= dia)]
            if len(janela) >= 3:
                media_movel.append({"data": dia.strftime("%Y-%m-%d"), "momento": momento,
                                    "diferenca": round(float(janela.dif.mean()), 2), "pesquisas": int(len(janela))})
    antes, depois = t2[t2.momento == "antes_1turno"], t2[t2.momento == "apos_1turno"]
    # Válidos depois do 1º turno; fora a Veritá retirada do ar (campo antes da eleição), como no FONTES.md.
    v2 = p2[(p2.tipo == "validos") & (p2.momento == "apos_1turno")].dropna(subset=["lula", "flavio"])
    retirada = v2.observacao.fillna("").str.contains("retirad", case=False)
    v2 = v2[~retirada]
    depois_ok = depois[~depois.observacao.fillna("").str.contains("retirad", case=False)]
    medias = {"validos": {"lula": float(v2.lula.mean()), "flavio": float(v2.flavio.mean()), "pesquisas": int(len(v2))},
              "totais": {"lula": float(depois_ok.lula.mean()), "flavio": float(depois_ok.flavio.mean()),
                         "pesquisas": int(len(depois_ok))}}
    for m in medias.values():
        m["lula_txt"], m["flavio_txt"] = pct(m["lula"] / 100), pct(m["flavio"] / 100)
    contagem_antes = {"pesquisas": int(len(antes)), "lula_frente": int((antes.dif < 0).sum()),
                      "flavio_frente": int((antes.dif > 0).sum()), "empate": int((antes.dif == 0).sum())}
    contagem_depois = {"pesquisas": int(len(depois_ok)), "lula_frente": int((depois_ok.dif < 0).sum()),
                       "flavio_frente": int((depois_ok.dif > 0).sum()), "empate": int((depois_ok.dif == 0).sum())}
    manchete = (f"Na véspera, {len(lula_frente)} de {len(ultimas)} institutos davam Lula à frente; "
                f"a urna deu Flávio por {dec(res_dif)} ponto")
    return {
        "tela": 2, "nome": "Pesquisas", "pergunta": "O que as pesquisas diziam antes do 1º turno, e o que dizem agora?",
        "manchete": manchete,
        "manchete_agora": f"Desde 05/10, Flávio lidera {contagem_depois['flavio_frente']} de "
                          f"{contagem_depois['pesquisas']} pesquisas do 2º turno",
        "proxima_pergunta": "Onde os votos mudaram de lado?",
        "antes": {
            "titulo": "A última pesquisa de cada instituto antes do 1º turno",
            "resultado": {"flavio": round(100 * flavio["pct"], 2), "lula": round(100 * lula["pct"], 2),
                          "diferenca": round(res_dif, 2), "diferenca_txt": menos(f"+{dec(res_dif)}"),
                          "texto": f"Urna: Flávio {pct(flavio['pct'])} × Lula {pct(lula['pct'])} (válidos)"},
            "institutos": ultimas,
            "lula_frente": len(lula_frente), "flavio_frente": len(ultimas) - len(lula_frente), "total": len(ultimas),
            "com_validos": len(com_validos),
            "media_validos": {"lula": media_validos_lula, "flavio": media_validos_flavio,
                              "lula_txt": pct(media_validos_lula / 100), "flavio_txt": pct(media_validos_flavio / 100),
                              "institutos": len(com_validos)},
            "erro_medio_diferenca": erro_medio,
            "erro_medio_txt": f"{dec(abs(erro_medio))} pontos a favor de Lula" if erro_medio < 0
                              else f"{dec(erro_medio)} pontos a favor de Flávio",
            "nota": "Diferença = Flávio − Lula, em pontos. Válidos quando o instituto divulgou; senão, votos totais "
                    "(o erro contra a urna só se mede nos válidos)."},
        "segundo_turno": {
            "titulo": "Lula × Flávio no 2º turno, pesquisa a pesquisa",
            "serie": serie, "media_movel": media_movel,
            "antes": contagem_antes, "depois": contagem_depois, "medias_depois": medias,
            "dia_da_eleicao": "2026-10-04", "segundo_turno": "2026-10-25",
            "nota": "Votos totais; diferença = Flávio − Lula. Antes de 04/10, o 2º turno era simulado nas pesquisas do "
                    "1º turno. Média móvel de 10 dias (3 pesquisas ou mais), sem atravessar o dia da eleição."},
        "fontes": "Institutos com registro no TSE; números conferidos em relatório do instituto ou do contratante "
                  "(levantamento de 22/10/2026, dados/bruto/pesquisas/FONTES.md).",
    }


CANDIDATOS = {
    "pt": {"nome": "Lula", "nome_completo": "Luiz Inácio Lula da Silva", "partido": "PT", "numero": 13, "cor": "vermelho",
           "adversario": "Flávio", "anterior": "Lula", "retrato": "retrato-lula", "cena": "comicio-lula",
           "credito_foto": "Retrato em traço a partir da foto oficial (Ricardo Stuckert/Palácio do Planalto, CC BY 2.0)"},
    "adv": {"nome": "Flávio", "nome_completo": "Flávio Bolsonaro", "partido": "PL", "numero": 22, "cor": "azul",
            "adversario": "Lula", "anterior": "Jair Bolsonaro", "retrato": "retrato-flavio", "cena": "comicio-flavio",
            "credito_foto": "Retrato em traço a partir da foto oficial (Agência Senado)"},
}


def tela_candidato(d, nac, lado):
    """Página do candidato: os mesmos blocos e as mesmas contas para os dois, só muda o lado."""
    c = CANDIDATOS[lado]
    outro = "adv" if lado == "pt" else "pt"
    atual = candidato(nac, 2026, c["partido"])
    antes = candidato(nac, 2022, c["partido"])
    validos = int(nac[nac.ano == 2026].votos.sum())
    posicao = int((nac[nac.ano == 2026].votos > atual["votos"]).sum()) + 1
    frente = d[f"{lado}2026"] > d[f"{outro}2026"]
    eleitores_frente = d.loc[frente, "validos2026"].sum() / d.validos2026.sum()
    regioes = []
    total_muni = d[f"{lado}2026"].sum()
    for r, g in d.groupby("regiao"):
        regioes.append({"regiao": r, "pct": float(g[f"{lado}2026"].sum() / g.validos2026.sum()),
                        "pct_txt": pct(g[f"{lado}2026"].sum() / g.validos2026.sum()),
                        "parte_dos_votos": float(g[f"{lado}2026"].sum() / total_muni),
                        "parte_dos_votos_txt": pct(g[f"{lado}2026"].sum() / total_muni, 0),
                        "votos_txt": mi(g[f"{lado}2026"].sum(), 2)})
    regioes.sort(key=lambda r: -r["parte_dos_votos"])
    por_uf = (d.groupby("uf")[[f"{lado}2026", "validos2026"]].sum()
              .assign(p=lambda x: x[f"{lado}2026"] / x.validos2026).sort_values("p", ascending=False))
    ufs_top = [{"uf": u, "nome": NOME_UF[u], "pct_txt": pct(r.p)} for u, r in por_uf.head(5).iterrows()]
    uf_fraca = por_uf.index[-1]
    grandes = d[d.populacao >= 100_000].assign(p=lambda x: x[f"{lado}2026"] / x.validos2026)
    cidades_votos = [{"municipio": r.nome, "uf": r.uf, "votos_txt": milhar(r[f"{lado}2026"]),
                      "pct_txt": pct(r[f"{lado}2026"] / r.validos2026)}
                     for _, r in d.sort_values(f"{lado}2026", ascending=False).head(5).iterrows()]
    cidades_fortes = [{"municipio": r.nome, "uf": r.uf, "pct_txt": pct(r.p), "populacao_txt": milhar(r.populacao)}
                      for _, r in grandes.sort_values("p", ascending=False).head(3).iterrows()]
    m_regiao = {r: margem_agregada(g, 2026) for r, g in d.groupby("regiao")}
    base_forte = max(m_regiao, key=lambda r: m_regiao[r] if lado == "pt" else -m_regiao[r])
    dif_votos = atual["votos"] - antes["votos"]
    principal = regioes[0]
    verbo = "venceu" if posicao == 1 else "ficou à frente"
    manchete = (f"{c['nome']} teve {pct(atual['pct'])} e {verbo} em {milhar(frente.sum())} municípios; "
                f"o {principal['regiao']} deu {principal['parte_dos_votos_txt']} dos seus votos")
    return {
        "nome": c["nome"], "pergunta": f"Onde estão os votos de {c['nome']}?", "manchete": manchete,
        "candidato": {k: c[k] for k in ("nome", "nome_completo", "partido", "numero", "cor")},
        "votos": atual["votos"], "votos_txt": mi(atual["votos"], 2), "votos_cheio_txt": milhar(atual["votos"]),
        "pct": atual["pct"], "pct_txt": pct(atual["pct"]), "posicao_txt": f"{posicao}º lugar",
        "comparacao_2022": {"candidato_2022": c["anterior"], "votos_2022_txt": mi(antes["votos"], 2),
                            "pct_2022_txt": pct(antes["pct"]), "variacao_votos_txt": mi_sinal(dif_votos),
                            "variacao_pp_txt": pp(atual["pct"] - antes["pct"]),
                            "nota": f"Em 2022 o candidato do {c['partido']} foi {c['anterior']}."},
        "municipios_a_frente": int(frente.sum()), "municipios_a_frente_txt": milhar(frente.sum()),
        "eleitores_nesses_municipios_txt": pct(eleitores_frente, 0),
        "municipios_total_txt": milhar(len(d)),
        "regioes": regioes, "ufs_mais_fortes": ufs_top,
        "uf_mais_fraca": {"uf": uf_fraca, "nome": NOME_UF[uf_fraca], "pct_txt": pct(por_uf.p.iloc[-1])},
        "cidades_que_mais_deram_votos": cidades_votos, "cidades_grandes_mais_fortes": cidades_fortes,
        "base_mais_forte": {"regiao": base_forte, "margem_txt": margem_txt(m_regiao[base_forte])
                            if lado == "pt" else margem_txt(-m_regiao[base_forte]).replace("+", "+")},
        "arte": {"retrato": c["retrato"], "cena": c["cena"],
                 "cena_legenda": f"A cena ao fundo é do {base_forte}, onde {c['nome']} teve a maior margem."},
        "credito_foto": c["credito_foto"],
        "nota": "Municípios à frente: mais votos que o adversário principal no município. Regiões: soma dos municípios "
                "(sem o exterior).",
    }


FAIXAS = [("16 e 17 anos", ["16 anos", "17 anos"]), ("18 a 24", ["18 anos", "19 anos", "20 anos", "21 a 24 anos"]),
          ("25 a 34", ["25 a 29 anos", "30 a 34 anos"]), ("35 a 44", ["35 a 39 anos", "40 a 44 anos"]),
          ("45 a 59", ["45 a 49 anos", "50 a 54 anos", "55 a 59 anos"]), ("60 a 69", ["60 a 64 anos", "65 a 69 anos"]),
          ("70 ou mais", ["70 a 74 anos", "75 a 79 anos", "80 a 84 anos", "85 a 89 anos", "90 a 94 anos",
                          "95 a 99 anos", "100 anos ou mais"])]


def tela_ausencia(muns, diferenca_votos):
    nac = pd.read_csv(SAIDA_DADOS / "comparecimento_nacional.csv")
    comp = pd.read_csv(SAIDA_DADOS / "comparecimento_municipio.csv", dtype={"cd_ibge": str})
    comp = comp.merge(muns[["cd_ibge", "regiao"]], on="cd_ibge", how="left")
    perfil = pd.read_csv(SAIDA_DADOS / "abstencao_perfil.csv")
    serie = []
    for r in nac.itertuples():
        bn = r.brancos + r.nulos
        ninguem = r.abstencoes + bn
        serie.append({"ano": int(r.ano), "aptos_txt": mi(r.aptos), "abstencoes": int(r.abstencoes),
                      "abstencoes_txt": mi(r.abstencoes), "abstencao_pct": r.abstencoes / r.aptos,
                      "abstencao_pct_txt": pct(r.abstencoes / r.aptos),
                      "brancos_nulos_txt": mi(bn), "brancos_nulos_pct_txt": pct(bn / r.comparecimento),
                      "nao_escolheram": int(ninguem), "nao_escolheram_txt": mi(ninguem),
                      "nao_escolheram_pct_txt": pct(ninguem / r.aptos)})
    s0, s1 = serie[0], serie[-1]
    vezes = s1["abstencoes"] / diferenca_votos
    regioes = []
    for reg, g in comp.dropna(subset=["regiao"]).groupby("regiao"):
        a06 = g[g.ano == 2006]; a26 = g[g.ano == 2026]
        p06, p26 = a06.abstencoes.sum() / a06.aptos.sum(), a26.abstencoes.sum() / a26.aptos.sum()
        regioes.append({"regiao": reg, "pct2006_txt": pct(p06), "pct2026_txt": pct(p26), "variacao_txt": pp(p26 - p06),
                        "pct2006": p06, "pct2026": p26})
    regioes.sort(key=lambda r: -(r["pct2026"] - r["pct2006"]))
    idade = []
    fe = perfil[perfil.dimensao == "faixa_etaria"]
    for rotulo, cats in FAIXAS:
        linha = {"faixa": rotulo}
        for ano in (2014, 2026):
            g = fe[(fe.ano == ano) & fe.categoria.isin(cats)]
            linha[f"pct{ano}"] = float(g.abstencao.sum() / g.aptos.sum())
            linha[f"pct{ano}_txt"] = pct(linha[f"pct{ano}"])
        linha["variacao_txt"] = pp(linha["pct2026"] - linha["pct2014"])
        linha["aptos2026_txt"] = mi(fe[(fe.ano == 2026) & fe.categoria.isin(cats)].aptos.sum())
        idade.append(linha)
    jovens = next(i for i in idade if i["faixa"] == "18 a 24")
    return {
        "nome": "Ausência", "pergunta": "Quantos brasileiros não escolheram ninguém?",
        "manchete": f"{s1['abstencoes_txt'].replace(' mi', ' milhões')} não foram votar: "
                    f"{dec(vezes, 0)} vezes a diferença entre Flávio e Lula",
        "serie": serie,
        "abstencao_2006_txt": s0["abstencao_pct_txt"], "abstencao_2026_txt": s1["abstencao_pct_txt"],
        "nao_escolheram_2026_txt": s1["nao_escolheram_txt"], "nao_escolheram_2026_pct_txt": s1["nao_escolheram_pct_txt"],
        "vezes_a_diferenca": round(vezes, 1),
        "regioes": regioes, "idade": idade,
        "achado_idade": f"De 2014 a 2026, a abstenção dos eleitores de 18 a 24 anos foi de {jovens['pct2014_txt']} para "
                        f"{jovens['pct2026_txt']}; acima dos 70, caiu",
        "mapa": "abstencao-2026",
        "escala_mapa": "10% (creme) · 17% (areia) · 25% (grafite) · 32% ou mais (tinta)",
        "nota": "1º turno, presidente. Abstenção = aptos que não compareceram; 'não escolheram ninguém' = abstenção + "
                "brancos + nulos. Perfil por idade: TSE publica desde 2014. Voto facultativo aos 16, 17 e 70+ anos.",
    }


COLUNAS_EXPLORADOR = ["Município", "Porte", "Renda per capita", "Lula 2026", "Flávio 2026", "Margem 2006–2026",
                      "Variação 2022→26", "Abstenção 2026", "Virou?"]


def linha_explorador(r, abst):
    serie = [round(100 * r[f"marg{a}"], 1) for a in ANOS]
    return {"municipio": r["nome"], "uf": r["uf"], "porte": str(r["porte"]), "quinto": str(r["quinto"]),
            "renda_txt": f"R$ {milhar(r['renda_pc'])}", "populacao_txt": milhar(r["populacao"]),
            "lula26_txt": pct(r["ptp2026"]), "flavio26_txt": pct(r["advp2026"]),
            "margem_serie": serie, "margem26_txt": margem_txt(r["marg2026"]), "variacao_txt": pp(r["dmarg"]),
            "variacao": round(100 * r["dmarg"], 2), "abstencao26_txt": pct(abst) if abst == abst else "—",
            "virou": bool(r["virou"]), "validos26": int(r["validos2026"])}


def tela_explorador(d):
    comp = pd.read_csv(SAIDA_DADOS / "comparecimento_municipio.csv", dtype={"cd_ibge": str})
    c26 = comp[comp.ano == 2026].groupby("cd_ibge")[["abstencoes", "aptos"]].sum()
    d = d.join((c26.abstencoes / c26.aptos).rename("abst26"))
    padrao = d.sort_values("validos2026", ascending=False).head(12)
    # Estado "laço na dispersão": renda no quinto mais alto, 20 mil habitantes ou mais e queda maior que 15 p.p.
    laco = d[(d.quinto == "mais ricas") & (d.populacao >= 20_000) & (d.dmarg <= -0.15)].sort_values("dmarg")
    return {
        "nome": "Explorador", "pergunta": "Onde está a minha pergunta? Explore os 5.571 municípios",
        "manchete": "Cada linha é um município: filtre, selecione na dispersão e clique para abrir a cidade",
        "colunas": COLUNAS_EXPLORADOR,
        "padrao": {"recorte_txt": "Todo o Brasil · 5.571 municípios · ordem: mais votos válidos",
                   "linhas": [linha_explorador(r, r.abst26) for _, r in padrao.iterrows()]},
        "selecao_laco": {"recorte_txt": f"Seleção na dispersão: renda entre as mais ricas, 20 mil hab. ou mais e queda "
                                        f"maior que 15 p.p. · {len(laco)} municípios",
                         "qtd": int(len(laco)), "linhas": [linha_explorador(r, r.abst26) for _, r in laco.head(12).iterrows()],
                         "uf_mais_frequente": laco.uf.value_counts().index[0] if len(laco) else "—"},
        "segmentacoes": ["Região", "UF", "Porte", "Renda (quinto)", "Virou?", "Busca por nome"],
        "dispersao": {"x": "renda domiciliar per capita (R$, escala log)", "y": "variação da margem de Lula 2022→2026 (p.p.)",
                      "tamanho": "votos válidos 2026", "cor": "margem 2026",
                      "arte": "explorador-dispersao", "arte_selecao": "explorador-dispersao-selecao"},
        "interacoes": ["laço na dispersão filtra matriz e mapa", "clique na linha acende o município no mapa e na "
                       "dispersão", "clique direito → Ver a cidade (detalhamento para a tela Minha cidade)",
                       "passar o mouse → tooltip de página com a série de 20 anos"],
        "nota": "Margem = (Lula/PT − adversário) ÷ válidos. Renda e população: Censo 2022. Município novo de 2025 "
                "(Boa Esperança do Norte · MT) sem dado do Censo.",
    }


def tela_movimento(d, nac):
    anos = []
    for a in ANOS:
        pt_c = candidato(nac, a, "PT")
        adv_c = nac[(nac.ano == a) & (nac.SG_PARTIDO != "PT")].sort_values("votos", ascending=False).iloc[0]
        por_uf = []
        for uf, g in d.groupby("uf"):
            por_uf.append({"uf": uf, "margem": round(100 * margem_agregada(g, a), 1),
                           "margem_txt": margem_txt(margem_agregada(g, a))})
        por_uf.sort(key=lambda x: -x["margem"])
        anos.append({"ano": a, "pt": nome(pt_c["nome"]), "adversario": nome(adv_c.NM_URNA_CANDIDATO),
                     "margem_nacional_txt": margem_txt(pt_c["pct"] - adv_c.pct),
                     "municipios_pt_frente": int((d[f"marg{a}"] > 0).sum()),
                     "ranking_uf": por_uf, "mapa": f"movimento-{a}"})
    return {"nome": "20 anos", "pergunta": "Como o mapa mudou em 20 anos?",
            "manchete": f"De {milhar(anos[0]['municipios_pt_frente'])} para {milhar(anos[-1]['municipios_pt_frente'])} "
                        f"municípios com o PT à frente, de 2006 a 2026",
            "anos": anos,
            "parametros_de_campo": {"metrica": ["Margem PT × adversário", "% PT", "% adversário", "Abstenção",
                                               "Brancos e nulos"],
                                    "ano": ANOS, "dimensao": ["Município (mapa)", "UF (ranking)", "Região"]},
            "play": "botão de play anima 2006 → 2026 (1,5 s por eleição); o ranking de UFs reordena junto",
            "nota": "Mapa: municípios pela margem de cada ano, mesma escala (−60 a +60 p.p.)."}


def tela_simulador():
    bruto = pd.read_csv(RAIZ / "dados" / "bruto" / "tse" / "presidente_2026_BR.csv", sep=";", encoding="latin1",
                        dtype=str)
    bruto = bruto[bruto.NR_TURNO == "1"]
    bruto["votos"] = bruto.QT_VOTOS_NOMINAIS_VALIDOS.astype(int)
    grupos = {"22": "Flávio", "13": "Lula", "70": "Cury", "14": "Renan"}
    bruto["grupo"] = bruto.NR_CANDIDATO.map(grupos).fillna("Demais")
    caiado = bruto[bruto.NM_URNA_CANDIDATO.str.contains("CAIADO", case=False)]
    if not caiado.empty:
        bruto.loc[caiado.index, "grupo"] = "Caiado"
    por_uf = bruto.pivot_table(index="SG_UF", columns="grupo", values="votos", aggfunc="sum", fill_value=0)
    tot = por_uf.sum()
    outros = ["Cury", "Renan", "Caiado", "Demais"]
    O, F, L = tot[outros].sum(), tot["Flávio"], tot["Lula"]
    empate = (F - L + O) / (2 * O)

    def cenario(fracao_lula, fracao_flavio, rotulo):
        lula = por_uf["Lula"] + sum(por_uf[c] * fracao_lula for c in outros)
        flav = por_uf["Flávio"] + sum(por_uf[c] * fracao_flavio for c in outros)
        val = lula + flav
        ufs = [{"uf": u, "lula_txt": pct(lula[u] / val[u]), "flavio_txt": pct(flav[u] / val[u]),
                "frente": "Lula" if lula[u] > flav[u] else "Flávio"} for u in por_uf.index]
        return {"rotulo": rotulo, "parametros": {c: {"lula": fracao_lula, "flavio": fracao_flavio,
                                                     "nao_vota": round(1 - fracao_lula - fracao_flavio, 2)}
                                                 for c in outros},
                "lula_txt": pct(lula.sum() / val.sum()), "flavio_txt": pct(flav.sum() / val.sum()),
                "ufs_lula": sum(u["frente"] == "Lula" for u in ufs), "ufs_flavio": sum(u["frente"] == "Flávio" for u in ufs),
                "ufs": ufs}

    return {
        "nome": "Simulador", "pergunta": "E se os eleitores dos outros candidatos escolherem?",
        "manchete": f"Para empatar, Lula precisaria de {pct(empate, 0)} dos {mi(O, 2)} de votos dos outros candidatos",
        "aviso": "Simulação, não previsão: você decide para onde vão os votos; o painel só faz a conta.",
        "votos_outros": {c: {"votos_txt": mi(tot[c], 2), "pct_txt": pct(tot[c] / tot.sum())} for c in outros},
        "total_outros_txt": mi(O, 2), "diferenca_txt": milhar(F - L),
        "empate_fracao_lula": round(empate, 4),
        "cenarios": [cenario(0.5, 0.5, "Ponto de partida: metade para cada um"),
                     cenario(0.0, 0.0, "Só os votos de Lula e de Flávio")],
        "controles": ["um controle deslizante por candidato: % para Lula · % para Flávio · resto não vota",
                      "comparecimento: −5 a +5 p.p. (aplicado igual aos dois)"],
        "nota": "Base: votos válidos do 1º turno de 2026 por UF (com o exterior). Em 'Demais' entram os outros 7 "
                "candidatos.",
    }


def tela_escola():
    """Do país à escola: votação de presidente por local de votação em Contagem (2018, 2022, 2026)."""
    loc = pd.read_csv(SAIDA_DADOS / "locais_contagem.csv")
    pos = pd.read_csv(SAIDA_DADOS / "escolas_posicao.csv")
    loc["m"] = (loc.pt - loc.adv) / loc.validos
    # Anos anteriores por zona + número; em 2026 o TSE repete um número para dois lugares (zona 91, local 1350), então
    # a margem de 2026 é a da própria linha e a posição no mapa casa também pelo nome.
    antes = (loc[loc.ano < 2026].groupby(["ano", "NR_ZONA", "NR_LOCAL_VOTACAO"])[["pt", "adv", "validos"]].sum()
             .assign(m=lambda x: (x.pt - x.adv) / x.validos).m.unstack("ano").rename(columns=lambda c: f"m{c}"))
    a26 = loc[loc.ano == 2026].merge(antes, left_on=["NR_ZONA", "NR_LOCAL_VOTACAO"], right_index=True, how="left")
    a26 = a26.merge(pos[["NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO", "px", "py"]],
                    on=["NR_ZONA", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO"], how="left")
    a26["m2026"] = a26.m
    a26["dm"] = a26.m2026 - a26.m2022
    lula22 = int((loc[loc.ano == 2022].m > 0).sum())
    lula26 = int((a26.m2026 > 0).sum())
    viraram = a26[(a26.m2022 > 0) & (a26.m2026 < 0)]

    def ficha(r):
        serie = [{"ano": a, "margem_txt": margem_txt(r[f"m{a}"]) if r[f"m{a}"] == r[f"m{a}"] else "—"}
                 for a in (2018, 2022, 2026)]
        return {"local": str(r.NM_LOCAL_VOTACAO).title(), "bairro": str(r.bairro).title() if r.bairro == r.bairro else "—",
                "endereco": str(r.DS_LOCAL_VOTACAO_ENDERECO).title(), "secoes": int(r.secoes),
                "validos_txt": milhar(r.validos), "lula_txt": pct(r.pt / r.validos), "flavio_txt": pct(r.adv / r.validos),
                "margem26_txt": margem_txt(r.m2026), "variacao_txt": pp(r.dm) if r.dm == r.dm else "—", "serie": serie,
                "virou": bool(r.m2022 > 0 > r.m2026), "pos_mapa_pct": {"x": round(r.px, 1), "y": round(r.py, 1)}
                if r.px == r.px else None}

    nova = a26[a26.bairro.fillna("").str.contains("NOVA CONTAGEM", case=False)]
    nova_t = loc[loc.bairro.fillna("").str.contains("NOVA CONTAGEM", case=False)].groupby("ano")[["pt", "adv", "validos"]].sum()
    nova_serie = [{"ano": int(a), "margem_txt": margem_txt((r.pt - r.adv) / r.validos)} for a, r in nova_t.iterrows()]
    maiores_quedas = a26.dropna(subset=["dm"]).sort_values("dm").head(5)
    return {
        "nome": "Escola", "pergunta": "Como votou cada escola de Contagem?",
        "manchete": f"Lula ficou à frente em {lula26} dos {len(a26)} locais de votação de Contagem; em 2022, eram {lula22}",
        "municipio": "Contagem (MG)", "locais_2026": int(len(a26)),
        "lula_frente_2022": lula22, "lula_frente_2026": lula26, "locais_que_viraram": int(len(viraram)),
        "nova_contagem": {"locais": int(len(nova)), "serie": nova_serie,
                          "texto": "Nova Contagem, onde o documentário começa: a margem de Lula foi de "
                                   f"{nova_serie[1]['margem_txt']} em 2022 a {nova_serie[2]['margem_txt']} em 2026"
                          if len(nova_serie) == 3 else ""},
        "maiores_quedas": [ficha(r) for _, r in maiores_quedas.iterrows()],
        "exemplo_tooltip": ficha(nova.sort_values("validos", ascending=False).iloc[0]) if len(nova) else None,
        "mapa": "escolas-contagem",
        "nota": "Votos de presidente por local de votação (soma das seções), 1º turno; coordenadas do cadastro de locais do "
                "TSE de 2022. Margem = (Lula/PT − adversário) ÷ válidos. Locais de 2018 e 2022 cruzados por zona e número.",
    }


DEBATE = RAIZ / "dados" / "bruto" / "debate"


def tela_debate():
    """Os dois debates da Band: 23/08 (Lula e Flávio faltaram; Cury subiu e caiu) e 18/10 (o único frente a frente)."""
    bruto = json.loads((DEBATE / "debate_band.json").read_text(encoding="utf-8"))
    d1, d2 = bruto["debate_1turno_2026_08_23"], bruto["debate_2turno_2026_10_18"]
    p1 = d1["pesquisas_antes_depois"]["primeiro_turno_votos_totais"]
    cury_antes, cury_depois = p1["antes"]["cury"], p1["depois"]["cury"]
    p1t = pd.read_csv(PESQUISAS / "pesquisas_1turno.csv", sep=";")
    cury = p1t[(p1t.tipo == "totais")].dropna(subset=["cury"]).sort_values("divulgacao")
    serie_cury = [{"instituto": r.instituto, "divulgacao": r.divulgacao, "divulgacao_txt": data_txt(r.divulgacao),
                   "cury": float(r.cury)} for r in cury.itertuples()]
    trends = d1["repercussao_digital"]["google_trends_coletado"]["diario_16ago_06set"]
    tv2 = d2["audiencia"]["tv"][0]
    ad2 = d2["pesquisas_antes_depois"] if "pesquisas_antes_depois" in d2 else {}
    debates = pd.read_csv(DEBATE / "debates.csv", sep=";").fillna("")
    linha_tempo = []
    for r in debates.itertuples():
        obs = str(r.observacao)
        abre = obs.upper()
        status = ("cancelado" if abre.startswith("CANCELADO") else
                  "não realizado" if abre.startswith("NÃO REALIZADO") else
                  "realizado (fonte única)" if "FONTE ÚNICA" in abre else "realizado")
        linha_tempo.append({"data": r.data, "data_txt": data_txt(r.data), "turno": int(r.turno), "emissora": r.emissora,
                            "participantes": r.participantes, "ausentes": r.ausentes, "status": status,
                            "audiencia_gsp": r.audiencia_pontos_gsp, "observacao": obs[:200]})
    q2 = d2["quem_venceu"]["pesquisas_qualitativas"][0]
    return {
        "nome": "Debate", "pergunta": "O que mudou depois do debate na Band?",
        "manchete": f"Sem Lula e Flávio no 1º debate, Cury foi de {dec(cury_antes['media'])}% a {dec(cury_depois['media'])}% "
                    f"nas pesquisas; terminou com 2,9%",
        "primeiro_turno": {
            "data_txt": "23/08", "participantes": ["Ronaldo Caiado", "Renan Santos", "Augusto Cury"],
            "ausentes": ["Lula", "Flávio Bolsonaro", "Romeu Zema"],
            "palco": "púlpitos dos ausentes mantidos vazios no estúdio, por regra acertada com as campanhas",
            "cury_antes_txt": f"{dec(cury_antes['media'])}%", "cury_antes_n": cury_antes["n"],
            "cury_depois_txt": f"{dec(cury_depois['media'])}%", "cury_depois_n": cury_depois["n"],
            "cury_urna_txt": "2,9%", "serie_cury": serie_cury,
            "marcos": [{"data": "2026-08-23", "rotulo": "debate da Band"},
                       {"data": "2026-08-28", "rotulo": "começa o horário eleitoral"},
                       {"data": "2026-08-29", "rotulo": "sabatina de Cury no Jornal Nacional"},
                       {"data": "2026-10-04", "rotulo": "urna: 2,89% dos válidos"}],
            "ressalva": "A alta coincide com o debate, o início do horário eleitoral (28/08) e a sabatina de Cury no JN "
                        "(29/08); coincidência no tempo não prova causa.",
            "audiencia_txt": "cerca de 2 pontos na Grande SP (prévia; fontes divergem entre 1,9 e 2,2)",
            "trends_diario": trends,
            "citacao": {"quem": "Augusto Cury", "trecho": "Lula tinha que estar aqui para responder sobre o caos que "
                                                           "está a educação"}},
        "segundo_turno": {
            "data_txt": "18/10", "titulo": "O único frente a frente da campanha",
            "audiencia_txt": f"{dec(tv2['valor_pontos'], 0)} pontos", "pico_txt": f"{dec(tv2['pico_pontos'])} de pico",
            "share_txt": f"{tv2['share_pct']}% de share", "pessoas_txt": f"{tv2['pessoas']} de pessoas na Grande SP",
            "audiencia_nota": "Kantar IBOPE, Grande SP, divulgado pela Band; a maior audiência de debate em 20 anos, "
                              "segundo a emissora",
            "youtube_pico_txt": "5,39 mi de aparelhos ao mesmo tempo no YouTube (Poder360)",
            "pesquisas_txt": "Lula 45,6% → 46,0%; Flávio 48,0% → 48,0% (19 pesquisas antes, 5 depois; dentro da margem)",
            "pesquisas_nota": "Janela 'depois' de só 4 dias; 10 pesquisas com campo atravessando 18/10 ficaram fora.",
            "citacoes": [{"quem": "Lula", "trecho": "Eu desafio você. Amanhã abrimos a nossa conta bancária"},
                         {"quem": "Flávio Bolsonaro", "trecho": "Aqui é o Flávio, não é o Jair."}],
            "qualitativa": {"instituto": q2["instituto"], "metodo": q2["metodo"], "flavio": 82, "lula": 79,
                            "leitura": "Quaest (30 grupos de eleitores): nota 82 para Flávio e 79 para Lula; sem virada"}},
        "linha_do_tempo": linha_tempo,
        "debates_realizados": sum(x["status"].startswith("realizado") for x in linha_tempo),
        "debates_cancelados": sum(not x["status"].startswith("realizado") for x in linha_tempo),
        "artes": {"palco_vazio": "debate-palco", "frente_a_frente": "debate-frente", "icone": "tv-debate"},
        "nota": "Pesquisas: votos totais, média simples por janela (antes: campo encerrado até 22/08; depois: de 24/08 a "
                "06/09). Audiência e repercussão: fontes no levantamento (dados/bruto/debate/FONTES.md).",
    }


def tela_quem_e(lado):
    """Primeira página do candidato: retrato, comício e trajetória (os números ficam na página seguinte)."""
    c = CANDIDATOS[lado]
    trajetoria = RAIZ / "dados" / "bruto" / "trajetoria" / "trajetoria.json"
    marcos = []
    if trajetoria.exists():
        chave = "lula" if lado == "pt" else "flavio"
        marcos = json.loads(trajetoria.read_text(encoding="utf-8")).get(chave, [])
    return {"nome": f"{c['nome']} · quem é", "pergunta": f"Quem é {c['nome_completo']}?",
            "manchete": "(aguardando o levantamento da trajetória)" if not marcos else "",
            "pendente": not marcos, "candidato": {k: c[k] for k in ("nome", "nome_completo", "partido", "numero", "cor")},
            "marcos": marcos, "arte": {"retrato": c["retrato"], "cena": c["cena"]}, "credito_foto": c["credito_foto"]}


def tela_apuracao():
    """Contagem e resultado ao vivo: lê o retrato que o coletor (apuracao/coletar.py) grava a cada coleta."""
    pasta = RAIZ / "dados" / "apuracao"
    ao_vivo = json.loads((pasta / "ultimo.json").read_text(encoding="utf-8"))
    ensaio = json.loads((pasta / "ensaio-1turno" / "ultimo.json").read_text(encoding="utf-8"))

    def estado(r):
        b = r["brasil"]
        return {"status": r["status"], "atualizado_tse": r["atualizado_tse"], "coletado_em": r["coletado_em"],
                "secoes_pct_txt": f"{dec(b['secoes_pct'], 2)}%", "lula_txt": f"{dec(b['lula_pct'], 2)}%",
                "flavio_txt": f"{dec(b['flavio_pct'], 2)}%", "lula_votos_txt": milhar(b["lula_votos"]),
                "flavio_votos_txt": milhar(b["flavio_votos"]), "diferenca_txt": milhar(b["diferenca_votos"]),
                "lider": b["lider"], "abstencao_pct_txt": f"{dec(b['abstencao_pct'], 2)}%",
                "brancos_txt": milhar(b["brancos"]), "nulos_txt": milhar(b["nulos"]),
                "ufs": [{"uf": u["uf"], "secoes_pct": u["secoes_pct"], "lider": u["lider"],
                         "lula_pct_txt": f"{dec(u['lula_pct'])}%", "flavio_pct_txt": f"{dec(u['flavio_pct'])}%"}
                        for u in r["ufs"]]}

    return {"nome": "Apuração", "pergunta": "Quem está na frente na apuração do 2º turno?",
            "manchete": "A apuração do 2º turno começa às 17h de 25/10; esta tela se atualiza sozinha",
            "ao_vivo": estado(ao_vivo), "ensaio_1turno": estado(ensaio),
            "estados_da_tela": {"aguardando": "antes das 17h: relógio até o fechamento das urnas, zeros e o eleitorado",
                                "apurando": "placar, % de seções totalizadas, mapa de UFs pela liderança, curva da noite",
                                "definido": "o TSE marca o eleito antes de 100%: selo 'matematicamente definido'",
                                "encerrada": "100% das seções: resultado final"},
            "historico": "dados/apuracao/historico.csv (uma linha por atualização do TSE, para a curva da noite)",
            "fonte": ao_vivo["fonte"],
            "nota": "Atualização: o coletor roda no GitHub Actions a cada poucos minutos e grava os arquivos no "
                    "repositório; o Power BI lê esses arquivos e é atualizado pela API ao fim de cada coleta."}


# Filtro do topo só onde ele muda a leitura da tela (pedido do Alisson, 23/10/2026).
FILTRO_POR_TELA = {"Placar": "UF", "Lula": "UF", "Flávio": "UF", "Ausência": "UF e município", "Virada": "UF",
                   "Perfil": "UF", "Série": "UF", "Minha cidade": "município", "Escola": "município (Contagem)",
                   "Apuração": "UF"}


def pendente(nome, pergunta, pasta):
    return {"nome": nome, "pergunta": pergunta, "pendente": True,
            "manchete": f"(aguardando o levantamento em dados/bruto/{pasta})"}


def main():
    votos, muns, nac = carregar()
    d = base_municipal(votos, muns)
    placar = tela_placar(nac)
    virada = tela_virada(d)
    estados = tela_estados(d, nac)
    perfil = tela_perfil(d)
    serie = tela_serie(nac, d)
    cidade = tela_cidade(d)
    pesquisas = tela_pesquisas(nac)
    segundo = pesquisas.pop("segundo_turno")
    pesquisas["nome"], pesquisas["pergunta"] = "Pesquisas", "O que as pesquisas diziam antes da urna?"
    agora = {"nome": "2º turno", "pergunta": "E agora, o que as pesquisas dizem do 2º turno?",
             "manchete": pesquisas.pop("manchete_agora"), **segundo, "fontes": pesquisas["fontes"]}
    lula_pg, flavio_pg = tela_candidato(d, nac, "pt"), tela_candidato(d, nac, "adv")
    ausencia = tela_ausencia(muns, placar["diferenca"]["votos"])
    debate = tela_debate()
    buscas = pendente("Buscas", "O que o Brasil perguntou ao Google?", "digital")
    redes = pendente("Redes", "Quem dominou as redes?", "digital")
    flavio, lula = placar["candidatos"][0], placar["candidatos"][1]
    capa = {"nome": "Capa", "pergunta": "Afinal, qual Brasil foi às urnas no 1º turno?",
            "titulo": "O que os números dizem.",
            "sobretitulo": "ELEIÇÕES 2026 · 1º TURNO PRESIDENCIAL",
            "linhas": [f"Flávio Bolsonaro {flavio['votos_txt']} · {flavio['pct_txt']} dos válidos",
                       f"Lula {lula['votos_txt']} · {lula['pct_txt']}",
                       f"{virada['viraram']} municípios mudaram de lado · {virada['municipios_txt']} no mapa"],
            "legenda_mapa": "CADA PONTO É UM MUNICÍPIO",
            "legenda_mapa_sub": "cor pela margem de 2026: vermelho, Lula à frente; azul, Flávio à frente",
            "manchete": f"Flávio {flavio['pct_txt']} × Lula {lula['pct_txt']}: {virada['viraram']} municípios mudaram de lado",
            "mapa": "arte/mapas/capa-pontos.png"}
    encerramento = {"nome": "Encerramento", "pergunta": "O que os números dizem, afinal?",
                    "titulo": "O que os números dizem.",
                    "fontes": ["TSE · votação, comparecimento e perfil do eleitor, 1º turno de 2006 a 2026 (arquivos de "
                               "22/10/2026)",
                               "IBGE · Censo 2022: população e rendimento domiciliar per capita; malha municipal",
                               "Institutos de pesquisa com registro no TSE (levantamento de 22/10/2026)",
                               "Fotos oficiais: Palácio do Planalto (CC BY 2.0) e Agência Senado"],
                    "assinatura": "Vizu Dados · vizudados.com.br"}
    # A história em atos; a ordem define o número da tela e a próxima pergunta de cada uma.
    atos = [("Abertura", [capa]),
            ("I · O resultado", [placar, tela_quem_e("pt"), lula_pg, tela_quem_e("adv"), flavio_pg, ausencia]),
            ("II · A campanha", [debate, buscas, redes, pesquisas]),
            ("III · O mapa", [virada, estados, perfil, serie]),
            ("Epílogo", [cidade, pendente("Os outros", "Para onde vão os votos dos outros candidatos?", "transferencia"),
                         agora, tela_apuracao()]),
            ("IV · Explore você mesmo", [tela_explorador(d), tela_escola(),
                                         tela_movimento(d, nac), tela_simulador()]),
            ("Fim", [encerramento])]
    paginas = []
    for ato, telas in atos:
        for p in telas:
            p["ato"] = ato
            paginas.append(p)
    for i, p in enumerate(paginas):
        p["tela"] = i
        p["filtro"] = FILTRO_POR_TELA.get(p["nome"])
        p.pop("proxima_pergunta", None)
        if i + 1 < len(paginas):
            p["proxima_pergunta"] = paginas[i + 1]["pergunta"]
    encerramento["achados"] = [{"ato": p["ato"], "tela": p["tela"], "frase": p["manchete"]} for p in paginas
                               if p["nome"] in ("Placar", "Ausência", "Pesquisas", "Virada", "Perfil", "Série", "2º turno")]
    extremos = {"maior_numero": placar["validos_txt"],
                "municipio_mais_longo": max(d.nome, key=len) + " (" + d.loc[d.nome.map(len).idxmax(), "uf"] + ")",
                "uf_mais_longa": "Rio Grande do Norte"}
    saida = {
        "meta": {"titulo": "Eleições 2026 · o que os números dizem", "gerado_em": datetime.now().isoformat(timespec="seconds"),
                 "data_base": "TSE · 22/10/2026", "rodape": "Fonte: TSE e IBGE · resultado de 22/10/2026",
                 "aviso_dados": "Dados reais: TSE (1º turno de 2006 a 2026) e IBGE (Censo 2022). Nada ilustrativo.",
                 "recorte": "Margem = (Lula ou candidato do PT − adversário principal) ÷ votos válidos, em p.p.; "
                            "adversário principal = o mais votado fora do PT no ano.",
                 "extremos": extremos,
                 "paginas": [{"tela": p["tela"], "ato": p["ato"], "nome": p["nome"], "pergunta": p["pergunta"], "filtro": p["filtro"],
                              "pendente": p.get("pendente", False)} for p in paginas]},
        "paginas": paginas,
    }
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(json.dumps(saida, ensure_ascii=False, indent=1, default=lambda o: o.item()
                                  if isinstance(o, np.generic) else str(o)), encoding="utf-8")
    for p in paginas:
        print(f"{p['tela']:02d} {p['nome']:<13} {p.get('manchete', '')}")


if __name__ == "__main__":
    main()
