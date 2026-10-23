"""cdp — teste de gesto DENTRO do Power BI Desktop do projeto, pelo protocolo de depuração do WebView2 dele.

Abra o Desktop com a porta própria do projeto (desktop.ps1 -Acao abrir -Reabrir -Cdp 9347; L124: a prova confere que a
porta é deste Desktop). O script conecta (Playwright connect_over_cdp), acha a página do relatório, navega pelas abas,
clica como o leitor (Ctrl+clique nos botões nativos, que no modo de edição só agem com Ctrl; clique simples dentro dos
visuais HTML), lê o texto que cada visual desenhou e fotografa a tela. Nada é salvo: o Desktop fecha sem salvar (L104).

    python -X utf8 pbi/scripts/cdp.py roteiro pbi/qa/gestos/roteiro.json     # executa um roteiro de passos
    python -X utf8 pbi/scripts/cdp.py foto T18 pbi/qa/gestos/T18.png

Passos do roteiro (lista JSON): {"ir": "18 Apuração"} · {"clicar_botao": [x, y]} (coordenada da página 1920×1080, com
Ctrl) · {"clicar_html": ".mq .q", "texto": "MG"} (primeiro elemento com o seletor e o texto, dentro de qualquer quadro) ·
{"ler": ".t18p"} (texto do primeiro quadro que tem o seletor) · {"esperar": 2} · {"foto": "arquivo.png"} ·
{"conferir": ".t18p", "contem": "MINAS GERAIS"} (falha se o texto não contiver).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PORTA = 9347


def pagina_do_relatorio(nav):
    melhor = None
    for ctx in nav.contexts:
        for pg in ctx.pages:
            if len(pg.frames) > 1 and (melhor is None or len(pg.frames) > len(melhor.frames)):
                melhor = pg
    if melhor is None:
        raise SystemExit("nenhuma página com visuais no WebView2 (o relatório está aberto?)")
    return melhor


_AREA = {}


def area_da_pagina(pg):
    """Caixa (x, y, escala) da página 1920×1080 na tela, pelo quadro da casca (que ocupa a página inteira). A geometria
    não muda entre páginas: a primeira medida vale para o roteiro todo; enquanto não há, tenta por até 30 s."""
    if "a" in _AREA:
        return _AREA["a"]
    fim = time.time() + 30
    while time.time() < fim:
        a = _medir_area(pg)
        if a:
            _AREA["a"] = a
            return a
        time.sleep(1)
    raise SystemExit("não achei a casca na página aberta")


def _medir_area(pg):
    for f in pg.frames:
        try:
            if f.query_selector(".cs.tela") or f.query_selector(".cp.tela") or f.query_selector(".fx.tela"):
                el = f.frame_element()
                b = el.bounding_box()
                if b and b["width"] > 500:
                    return b["x"], b["y"], b["width"] / 1920
        except Exception:  # noqa: BLE001
            continue
    return None


def quadro_com(pg, seletor, texto=None):
    for f in pg.frames:
        try:
            for el in f.query_selector_all(seletor):
                b = el.bounding_box()                    # quadros de páginas anteriores ficam ocultos no DOM
                if not b or b["width"] < 2 or not f.frame_element().is_visible():
                    continue
                if texto is None or texto in (el.inner_text() or ""):
                    return f, el
        except Exception:  # noqa: BLE001
            continue
    return None, None


def executar(pg, passos, pasta: Path) -> int:
    falhas = 0
    for i, p in enumerate(passos, 1):
        if "ir" in p:
            pg.get_by_text(p["ir"], exact=True).first.click()
            time.sleep(p.get("espera", 6))
            print(f"{i:02d} ir {p['ir']}")
        elif "clicar_botao" in p:
            x0, y0, k = area_da_pagina(pg)
            x, y = p["clicar_botao"]
            pg.keyboard.down("Control")
            pg.mouse.click(x0 + x * k, y0 + y * k)
            pg.keyboard.up("Control")
            time.sleep(p.get("espera", 5))
            print(f"{i:02d} ctrl+clique em ({x}, {y})")
        elif "clicar_html" in p:
            f, el = quadro_com(pg, p["clicar_html"], p.get("texto"))
            if not el:
                print(f"{i:02d} FALHA: não achei {p['clicar_html']} {p.get('texto', '')}")
                falhas += 1
                continue
            el.click()
            time.sleep(p.get("espera", 4))
            print(f"{i:02d} clique em {p['clicar_html']} {p.get('texto', '')}")
        elif "pairar_html" in p:
            f, el = quadro_com(pg, p["pairar_html"], p.get("texto"))
            if el:
                el.hover()
                time.sleep(p.get("espera", 3))
            print(f"{i:02d} mouse sobre {p['pairar_html']} {p.get('texto', '')}: {'ok' if el else 'FALHA'}")
            falhas += 0 if el else 1
        elif "ler" in p:
            f, el = quadro_com(pg, p["ler"])
            print(f"{i:02d} {p['ler']}: " + ((el.inner_text() or "").replace("\n", " · ")[:400] if el else "(não achei)"))
        elif "conferir" in p:
            txt, ok, fim = "", False, time.time() + p.get("ate", 15)
            while time.time() < fim and not ok:          # a página pode estar trocando: tenta por até 15 s
                try:
                    f, el = quadro_com(pg, p["conferir"])
                    txt = (el.inner_text() or "") if el else ""
                except Exception:  # noqa: BLE001
                    txt = ""
                ok = p["contem"] in txt
                if not ok:
                    time.sleep(1)
            falhas += 0 if ok else 1
            print(f"{i:02d} {'ok   ' if ok else 'FALHA'} {p['conferir']} contém {p['contem']!r}"
                  + ("" if ok else f" — leu: {txt.replace(chr(10), ' · ')[:200]!r}"))
        elif "esperar" in p:
            time.sleep(p["esperar"])
        elif "foto" in p:
            x0, y0, k = area_da_pagina(pg)
            destino = pasta / p["foto"]
            destino.parent.mkdir(parents=True, exist_ok=True)
            for tentativa in (1, 2):
                try:
                    pg.screenshot(path=str(destino), clip={"x": x0, "y": y0, "width": 1920 * k, "height": 1080 * k},
                                  timeout=90000)
                    print(f"{i:02d} foto {destino}")
                    break
                except Exception as e:  # noqa: BLE001 (página pesada ainda desenhando: tenta de novo, depois segue)
                    if tentativa == 2:
                        print(f"{i:02d} FALHA foto {destino}: {str(e)[:80]}")
                        falhas += 1
                    time.sleep(5)
        elif "tecla" in p:
            pg.keyboard.press(p["tecla"])
            time.sleep(p.get("espera", 2))
    return falhas


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    modo = sys.argv[1]
    with sync_playwright() as pw:
        nav = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORTA}")
        pg = pagina_do_relatorio(nav)
        if modo == "roteiro":
            arq = Path(sys.argv[2])
            passos = json.loads(arq.read_text(encoding="utf-8"))
            falhas = executar(pg, passos, arq.parent)
            print(f"{len(passos)} passos · {falhas} falha(s)")
            return 1 if falhas else 0
        if modo == "foto":
            from roteiro import POR_CODIGO  # noqa: PLC0415
            t = POR_CODIGO[sys.argv[2]]
            return executar(pg, [{"ir": t.titulo_pagina}, {"foto": Path(sys.argv[3]).name}], Path(sys.argv[3]).parent)
    return 2


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
