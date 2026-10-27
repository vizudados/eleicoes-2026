"""texto_telas — o texto que cada tela mostra DENTRO do Power BI Desktop do projeto (cada visual HTML, na ordem da página),
para os roteiros dos vídeos da Lia citarem só o que está na tela (27/10/2026: "as telas precisam ser 100% fiéis").

Usa o protocolo de depuração do Desktop (cdp.py, porta 9347). Para cada tela visível: vai até ela, espera assentar, lê o
texto de cada quadro HTML (com a posição na página 1920×1080) e grava pbi/qa/lia-guia/texto/<código>[-pre].json. Nas telas
com o filtro Pré/Pós, lê também o Pré e volta ao Pós no fim.

    python -X utf8 pbi/scripts/texto_telas.py              # todas as telas, no modo em que o painel está (o Pós)
    python -X utf8 pbi/scripts/cdp.py roteiro pbi/qa/lia-guia/pre.json     # troca o filtro para o Pré
    python -X utf8 pbi/scripts/texto_telas.py --so-pre     # as telas com o filtro, no Pré
    python -X utf8 pbi/scripts/cdp.py roteiro pbi/qa/lia-guia/pos.json     # volta ao Pós
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cdp  # noqa: E402
import momento_eleicao as M  # noqa: E402

PBI = AQUI.parent
SAIDA = PBI / "qa" / "lia-guia" / "texto"
PAGINAS = PBI / "pbip" / "Eleicoes.Report" / "definition" / "pages"
LENTAS = {"T00", "T22", "T29", "T19", "T21", "T27", "T23", "T16"}


def telas():
    ordem = json.loads((PAGINAS / "pages.json").read_text(encoding="utf-8"))["pageOrder"]
    saida = []
    for p in ordem:
        d = json.loads((PAGINAS / p / "page.json").read_text(encoding="utf-8"))
        if d.get("visibility") != "HiddenInViewMode":
            saida.append((p, d["displayName"]))
    return saida


def ler(pg) -> list[dict]:
    x0, y0, k = cdp.area_da_pagina(pg)
    blocos = []
    for f in pg.frames:
        try:
            el = f.frame_element()
            if not el.is_visible():
                continue
            b = el.bounding_box()
            if not b or b["width"] < 8:
                continue
            texto = (f.evaluate("() => document.body ? document.body.innerText : ''") or "").strip()
            if not texto:
                continue
            blocos.append({"x": round((b["x"] - x0) / k), "y": round((b["y"] - y0) / k),
                           "w": round(b["width"] / k), "h": round(b["height"] / k), "texto": texto})
        except Exception:  # noqa: BLE001
            continue
    blocos.sort(key=lambda b: (b["y"], b["x"]))
    return blocos


def ler_estavel(pg) -> list[dict]:
    """Lê até o texto parar de mudar: os contadores (movimento.js) contam a cada renderização do visual."""
    anterior = None
    for _ in range(15):
        atual = ler(pg)
        if atual == anterior:
            return atual
        anterior = atual
        time.sleep(2.5)
    print("  aviso: o texto não assentou em 37 s")
    return anterior


def ir(pg, nome, codigo):
    pg.mouse.move(2, 2)
    pg.get_by_text(nome, exact=True).first.click()
    time.sleep(25 if codigo in LENTAS else 12)
    pg.mouse.move(2, 2)
    time.sleep(1)


def escolher(pg, valor):
    x0, y0, k = cdp.area_da_pagina(pg)
    for tentativa in range(4):
        pg.keyboard.down("Control")
        pg.mouse.click(x0 + 1100 * k, y0 + 84 * k)
        pg.keyboard.up("Control")
        time.sleep(5 + 2 * tentativa)
        f, el = cdp.quadro_com(pg, ".sff-option", valor)
        if el is not None:
            cdp._clique_escalado(pg, f, el)
            time.sleep(6)
            return
        pg.mouse.move(2, 2)
        time.sleep(2)
    raise SystemExit(f"não achei a opção {valor}")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    SAIDA.mkdir(parents=True, exist_ok=True)
    lista = telas()
    with sync_playwright() as pw:
        nav = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{cdp.PORTA}")
        pg = cdp.pagina_do_relatorio(nav)
        so_pre = "--so-pre" in sys.argv     # o filtro já está no Pré (trocado pelo cdp.py roteiro, que acerta o clique)
        for cod, nome in ([] if so_pre else lista):
            ir(pg, nome, cod)
            (SAIDA / f"{cod}.json").write_text(json.dumps({"codigo": cod, "pagina": nome, "modo": "Pós",
                                                             "blocos": ler_estavel(pg)}, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
            print("ok", cod)
        resultado = dict(lista)["T01"]
        if not so_pre:
            return 0
        for cod, nome in lista:
            if cod in M.TELAS:
                ir(pg, nome, cod)
                (SAIDA / f"{cod}-pre.json").write_text(json.dumps({"codigo": cod, "pagina": nome, "modo": "Pré",
                                                                     "blocos": ler_estavel(pg)}, ensure_ascii=False, indent=1),
                                                          encoding="utf-8")
                print("ok", cod, "pré")
    return 0


if __name__ == "__main__":
    sys.exit(main())
