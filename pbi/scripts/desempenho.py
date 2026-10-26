"""desempenho — teste de otimização das 24 telas (pedido do Alisson, 23/10/2026: "rode um teste de otimização, é claro,
será necessário por conta que são muitas páginas").

Duas medidas, sobre o projeto integrado e aberto no Desktop:
  1. motor: a consulta que cada visual de dado faz (HTML Content: o conteúdo, com a granularidade quando há; Deneb: o
     dataset; folha de estilo uma vez), cronometrada a frio (cache limpo) e a quente, com linhas e caracteres
     devolvidos (desempenho.ps1, uma conexão só);
  2. peso: por página, quantos visuais, quantos com dado, tamanho do bodyTemplate e do JSON dos visuais.
Relatório em pbi/qa/desempenho/relatorio.md (+ .json). Limites: consulta fria ≤ 800 ms (atenção) / 2.000 ms
(reprova); texto devolvido ≤ 32.000 caracteres por valor (L048); página ≤ 12 visuais de dado.

    python -X utf8 pbi/scripts/desempenho.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import montar_pbip as mp  # noqa: E402
import pbip_lib as lib  # noqa: E402
from previa import coluna_de, medida_de, ref_coluna, ref_medida  # noqa: E402

PBI = AQUI.parent
SAIDA = PBI / "qa" / "desempenho"
ATENCAO, REPROVA = 800, 2000


def consultas(itens) -> tuple[list[dict], dict]:
    lista, peso = [], defaultdict(lambda: {"visuais": 0, "com_dado": 0, "corpo": 0, "json": 0})
    estilos = set()
    for i in itens:
        if not isinstance(i, lib.Visual):
            continue
        d = i.doc
        p = peso[i.pagina]
        p["visuais"] += 1
        p["json"] += len(json.dumps(d, ensure_ascii=False))
        v = d["visual"]
        tipo = v["visualType"]
        est = v.get("query", {}).get("queryState", {})
        chave = f"{i.pagina}/{d['name']}"
        if tipo == lib.GUID_HTML:
            obj = v.get("objects", {})
            if "templates" in obj:
                p["corpo"] += len(obj["templates"][0]["properties"]["bodyTemplate"]["expr"]["Literal"]["Value"])
            if "stylesheet" in obj:
                estilos.add(obj["stylesheet"][0]["properties"]["stylesheet"]["expr"]["Measure"]["Property"])
            conteudo = medida_de(est["content"]["projections"][0])
            if conteudo in ("Casca · vazio",):
                continue
            p["com_dado"] += 1
            gran = coluna_de(est["sampling"]["projections"][0]) if "sampling" in est else None
            if gran:
                q = f'EVALUATE SUMMARIZECOLUMNS ( {ref_coluna(*gran)}, "c", {ref_medida(conteudo)} )'
            else:
                q = f'EVALUATE ROW ( "c", {ref_medida(conteudo)} )'
            lista.append({"chave": chave, "consulta": q})
        elif tipo == lib.GUID_DENEB:
            p["com_dado"] += 1
            cols, meds = [], []
            for pr in est.get("dataset", {}).get("projections", []):
                c = coluna_de(pr)
                if c:
                    cols.append(ref_coluna(*c))
                else:
                    m = medida_de(pr)
                    meds.append(f'"{m}", {ref_medida(m)}')
            q = "EVALUATE SUMMARIZECOLUMNS ( " + ", ".join(cols + meds) + " )"
            lista.append({"chave": chave, "consulta": q})
        elif tipo == lib.GUID_VIZUFILTER or tipo in ("slicer", "advancedSlicerVisual", "tableEx", "pivotTable"):
            p["com_dado"] += 1
    for e in sorted(estilos):
        lista.append({"chave": f"_estilo/{e}", "consulta": f'EVALUATE ROW ( "c", {ref_medida(e)} )'})
    return lista, peso


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    SAIDA.mkdir(parents=True, exist_ok=True)
    ctx = mp.carregar_contexto()
    itens = mp.carregar_declaracoes(ctx)
    lista, peso = consultas(itens)
    ent = SAIDA / "consultas.json"
    ent.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
    sai = SAIDA / "tempos.json"
    r = subprocess.run(["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(AQUI / "desempenho.ps1"),
                        "-Entrada", str(ent), "-Saida", str(sai)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600)
    if r.returncode != 0 or not sai.exists():
        print(r.stdout, r.stderr)
        return 2
    tempos = json.loads(sai.read_text(encoding="utf-8-sig"))
    if isinstance(tempos, dict):
        tempos = [tempos]
    linhas = ["# Teste de desempenho · painel Eleições 2026", "",
              f"{len(tempos)} consultas (uma por visual de dado + folhas de estilo), frio = cache do motor limpo.", "",
              "Caracteres contam somente campos de texto; números e metadados do DataView não entram. Não é o payload integral do navegador.", "",
              "| Visual | frio (ms) | quente (ms) | linhas | caracteres | situação |", "|---|---:|---:|---:|---:|---|"]
    ruins = 0
    for t in sorted(tempos, key=lambda t: -(t.get("frio") or 0)):
        if t.get("erro"):
            sit, ruins = "ERRO: " + t["erro"][:120], ruins + 1
        elif t["frio"] > REPROVA:
            sit, ruins = "reprova", ruins + 1
        elif t["frio"] > ATENCAO:
            sit = "atenção"
        else:
            sit = "ok"
        if t.get("caracteres") and t["caracteres"] > 32000 * max(1, t.get("linhas") or 1):
            sit += " · texto longo"
        linhas.append(f"| {t['chave']} | {t.get('frio')} | {t.get('quente')} | {t.get('linhas')} | "
                      f"{t.get('caracteres')} | {sit} |")
    linhas += ["", "## Peso por página", "", "| Página | visuais | com dado | bodyTemplate (car.) | JSON dos visuais (car.) |",
               "|---|---:|---:|---:|---:|"]
    for pag in sorted(peso):
        p = peso[pag]
        aviso = " ⚠" if p["com_dado"] > 12 else ""
        linhas.append(f"| {pag}{aviso} | {p['visuais']} | {p['com_dado']} | {p['corpo']:,} | {p['json']:,} |")
    total_frio = sum(t.get("frio") or 0 for t in tempos)
    linhas += ["", f"Soma a frio: {total_frio / 1000:.1f} s · consultas com problema: {ruins}"]
    (SAIDA / "relatorio.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas[-3:]))
    print(f"relatório: {SAIDA / 'relatorio.md'}")
    return 1 if ruins else 0


if __name__ == "__main__":
    sys.exit(main())
