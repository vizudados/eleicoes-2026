"""capturar_telas — a foto fiel de cada tela, tirada DENTRO do Power BI Desktop do projeto, e a caixa de cada pedaço de
texto que ela mostra, para os vídeos da Lia por tela (27/10/2026: "as telas precisam ser 100% fiéis").

Para cada tela visível: vai até ela, espera o texto assentar (os contadores do movimento.js), tira o mouse da página e
fotografa só a página (pbi/qa/lia-guia/telas/<código>.png, na resolução do Desktop); grava em <código>.caixas.json cada nó
de texto dos visuais HTML com a caixa na página 1920×1080 (x, y, w, h), já com a escala que o Power BI aplica ao visual.

    python -X utf8 pbi/scripts/capturar_telas.py            # todas as telas, no modo em que o painel está (o Pós)
    python -X utf8 pbi/scripts/capturar_telas.py T01 T23    # só algumas
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
import texto_telas as T  # noqa: E402

SAIDA = AQUI.parent / "qa" / "lia-guia" / "telas"

# Cada nó de texto visível do documento do visual, com o retângulo de cada linha (um nó pode quebrar em várias).
_JS_NOS = """() => {
  const saida = [];
  const andar = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = andar.nextNode())) {
    const t = n.textContent.replace(/\\s+/g, ' ').trim();
    if (!t) continue;
    const el = n.parentElement;
    if (!el) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    for (const q of r.getClientRects()) {
      if (q.width < 1 || q.height < 1) continue;
      saida.push({t, x: q.left, y: q.top, w: q.width, h: q.height, tam: parseFloat(cs.fontSize)});
    }
  }
  return {nos: saida, largura: window.innerWidth};
}"""


def caixas(pg) -> list[dict]:
    x0, y0, k = cdp.area_da_pagina(pg)
    todas = []
    for f in pg.frames:
        try:
            el = f.frame_element()
            if not el.is_visible():
                continue
            b = el.bounding_box()
            if not b or b["width"] < 8:
                continue
            r = f.evaluate(_JS_NOS)
            if not r["nos"]:
                continue
            esc = b["width"] / r["largura"]           # o Power BI encolhe o visual: px do documento → px da tela
            for q in r["nos"]:
                todas.append({"t": q["t"], "tam": round(q["tam"], 1),
                              "x": round((b["x"] + q["x"] * esc - x0) / k, 1),
                              "y": round((b["y"] + q["y"] * esc - y0) / k, 1),
                              "w": round(q["w"] * esc / k, 1), "h": round(q["h"] * esc / k, 1)})
        except Exception:  # noqa: BLE001
            continue
    return todas


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    SAIDA.mkdir(parents=True, exist_ok=True)
    so = set(sys.argv[1:])
    with sync_playwright() as pw:
        nav = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{cdp.PORTA}")
        pg = cdp.pagina_do_relatorio(nav)
        for cod, nome in T.telas():
            if so and cod not in so:
                continue
            T.ir(pg, nome, cod)
            T.ler_estavel(pg)                          # espera os contadores assentarem
            pg.keyboard.press("Escape")
            pg.mouse.move(2, 2)
            time.sleep(1.5)
            x0, y0, k = cdp.area_da_pagina(pg)
            pg.screenshot(path=str(SAIDA / f"{cod}.png"), clip={"x": x0, "y": y0, "width": 1920 * k, "height": 1080 * k},
                          timeout=90000)
            (SAIDA / f"{cod}.caixas.json").write_text(json.dumps({"codigo": cod, "pagina": nome, "escala": k,
                                                                    "nos": caixas(pg)}, ensure_ascii=False, indent=0),
                                                         encoding="utf-8")
            print("ok", cod)
    return 0


if __name__ == "__main__":
    sys.exit(main())
