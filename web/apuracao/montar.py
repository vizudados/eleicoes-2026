"""Monta a cópia da tela 25 · Apuração do painel para o site (web/apuracao/), a partir da prévia da T18.

A prévia (pbi/scripts/previa.py T18) desenha a página igual ao Power BI: papel, casca, fontes e o CSS de cada visual.
Daqui saem as fontes (fontes/*.woff2), o CSS comum (base.css), a casca sem setas e o CSS de cada bloco (pecas.json).
O desenho dinâmico (resultado, curva e mapa) é o apuracao.js, que repete as medidas HTML da T18 em JavaScript.
Também grava o 1º turno por UF (primeiro_turno.json), para o dossiê de cada estado.

    python -I -X utf8 web/apuracao/montar.py
"""
import base64
import html
import json
import re
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
PREVIA = RAIZ / "pbi" / "qa" / "previa" / "T18.html"
FONTES = {"Sora Eleicoes": "sora-eleicoes", "Caveat Eleicoes": "caveat-eleicoes", "Sora Vizu": "sora-vizu"}

pagina = PREVIA.read_text(encoding="utf-8")
iframes = {m.group(1): html.unescape(m.group(2))
           for m in re.finditer(r'<iframe title="([^"]+)" style="[^"]+" srcdoc="([^"]*)"', pagina)}


def salvar_fonte(familia, peso, dados, n=[0]):
    nome = FONTES.get(familia) or f"sora-setas-{len([1 for _ in (AQUI / 'fontes').glob('sora-setas-*')]) + 1}"
    arq = AQUI / "fontes" / f"{nome}.woff2"
    arq.write_bytes(base64.b64decode(dados.split(",", 1)[1]))
    return f"fontes/{nome}.woff2"


def fontes_para_arquivo(css):
    def troca(m):
        familia, resto, dados = m.group(1), m.group(2), m.group(3)
        url = salvar_fonte(familia, None, dados)
        return f"@font-face{{font-family:'{familia}';{resto}src:url({url})"
    return re.sub(r"@font-face\{font-family:'([^']+)';(.*?)src:url\((data:[^)]+)\)", troca, css, flags=re.S)


for f in (AQUI / "fontes").glob("*.woff2"):
    f.unlink()
# CSS comum: o <head> de um visual dinâmico, sem o congelamento de animação da prévia
cab = iframes["T18_Placar_Html"].split("</head>", 1)[0]
estilos = "".join(re.findall(r"<style(?: id=\"[^\"]+\")?>(.*?)</style>", cab, flags=re.S)[:-1])
(AQUI / "base.css").write_text(fontes_para_arquivo(estilos), encoding="utf-8")
# a fonte do gatilho do filtro (página principal da prévia)
m = re.search(r"@font-face\{font-family:'Sora Vizu';.*?src:url\((data:[^)]+)\)", pagina, flags=re.S)
salvar_fonte("Sora Vizu", None, m.group(1))


def corpo(nome):
    b = iframes[nome].split("</head>", 1)[1]
    return b.split('<div id="htmlContent">', 1)[1].rsplit('<div class="htmlViewerEntry"> </div>', 1)[0]


def primeiro_estilo(txt):
    return re.match(r"(?:<style>.*?</style>)*", txt, flags=re.S).group(0)


pecas = {}
casca = corpo("T18_Casca_Fundo")
casca = casca.replace("Fonte: TSE · API pública de divulgação dos resultados, coletada a cada minuto",
                      "Fonte: TSE · API pública de divulgação dos resultados, consultada a cada minuto · "
                      "Brasil = soma das UFs e do exterior")
pecas["casca"] = casca.replace("</style>", ".cs .seta,.cs .info{display:none}</style>", 1)
for chave, nome in [("placar", "T18_Placar_Html"), ("curva", "T18_Curva_Html"), ("mapa", "T18_Mapa_Html")]:
    pecas[chave + "_css"] = primeiro_estilo(corpo(nome))
mapa = corpo("T18_Mapa_Html")
pecas["mapa_fixo"] = re.search(r"<div class='mapa-fixo'>.*?</div></div>", mapa, flags=re.S).group(0)
filtro = re.search(r'<div title="T18_Casca_Filtro" style="[^"]+">(.*?)</div></div>', pagina, flags=re.S)
pecas["filtro"] = filtro.group(1) + "</div>"
(AQUI / "pecas.json").write_text(json.dumps(pecas, ensure_ascii=False, indent=1), encoding="utf-8")

# 1º turno por UF (válidos), para o dossiê do estado antes dos votos do 2º
URL = "https://resultados.tse.jus.br/oficial/ele2026/6257/dados/{uf}/{uf}-c0001-e006257-u.json"
UFS = ["ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj",
       "rn", "ro", "rr", "rs", "sc", "se", "sp", "to", "zz"]
t1 = {}
for uf in UFS:
    d = json.loads(urllib.request.urlopen(urllib.request.Request(URL.format(uf=uf), headers={"User-Agent": "VizuDados"})).read())
    vv = int(d["v"]["vv"])
    c = {int(x["n"]): int(x["vap"]) for a in d["carg"][0]["agr"] for p in a["par"] for x in p["cand"]}
    t1[uf.upper()] = {"lula": round(c.get(13, 0) / vv, 4), "flavio": round(c.get(22, 0) / vv, 4)}
(AQUI / "primeiro_turno.json").write_text(json.dumps(t1), encoding="utf-8")
print("ok ·", ", ".join(sorted(p.name for p in (AQUI / "fontes").iterdir())), "· pecas:", list(pecas))
