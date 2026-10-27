"""conferir_player — abre o vídeo da Lia em algumas telas DENTRO do Power BI Desktop e prova que ele toca e fecha.

Para cada tela: vai até ela, Ctrl+clique no ▶ (no card, na capa), acha o <video> do player, manda tocar sem som,
confere que carregou (duração do arquivo publicado) e que o tempo anda, fotografa e fecha no ×; depois confere que o
player sumiu. Fotos em pbi/qa/lia-guia/player/.

    python -X utf8 pbi/scripts/conferir_player.py                 # capa, 04 Resultado, 19 Os outros, Encerramento
    python -X utf8 pbi/scripts/conferir_player.py T05 TIX
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cdp  # noqa: E402
import texto_telas as T  # noqa: E402
from paginas import casca  # noqa: E402

SAIDA = AQUI.parent / "qa" / "lia-guia" / "player"


def centro(caixa):
    x, y, w, h = caixa
    return x + w / 2, y + h / 2


def ctrl_clique(pg, x, y):
    # o mouse para em cima antes (o botão nativo só age com o cursor pousado: um clique instantâneo não abre o player)
    x0, y0, k = cdp.area_da_pagina(pg)
    pg.mouse.move(x0 + x * k, y0 + y * k)
    time.sleep(.6)
    pg.keyboard.down("Control")
    pg.mouse.down()
    time.sleep(.12)
    pg.mouse.up()
    pg.keyboard.up("Control")


def video_do_player(pg, cod):
    for f in pg.frames:
        try:
            if f.evaluate("() => !!document.querySelector('video[src*=\"/midia/lia/\"], video source[src*=\"/midia/lia/\"]')"):
                el = f.frame_element()
                if el.is_visible():
                    return f
        except Exception:  # noqa: BLE001
            continue
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    SAIDA.mkdir(parents=True, exist_ok=True)
    pedidos = sys.argv[1:] or ["T00", "T01", "T16", "T23"]
    falhas = 0
    with sync_playwright() as pw:
        nav = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{cdp.PORTA}")
        pg = cdp.pagina_do_relatorio(nav)
        telas = dict(T.telas())
        for cod in pedidos:
            T.ir(pg, telas[cod], cod)
            time.sleep(4)
            # depois da troca de aba o foco fica na barra de abas: um clique fora da página devolve o foco à tela sem
            # selecionar visual nenhum, e só então o Ctrl+clique chega ao botão
            x0, y0, k = cdp.area_da_pagina(pg)
            pg.mouse.click(x0 + 960 * k, y0 + 1110 * k)
            time.sleep(1)
            ctrl_clique(pg, *centro(casca.VIDEO_CAPA if cod == "T00" else casca.VIDEO))
            time.sleep(4)
            f = video_do_player(pg, cod)
            if not f:
                print(f"FALHA {cod}: o player não abriu")
                falhas += 1
                continue
            # a foto vem ANTES de tocar: com o vídeo em reprodução a captura do WebView2 não sai
            pg.mouse.move(2, 2)
            x0, y0, k = cdp.area_da_pagina(pg)
            pg.screenshot(path=str(SAIDA / f"{cod}-aberto.png"), clip={"x": x0, "y": y0, "width": 1920 * k, "height": 1080 * k},
                          timeout=120000)
            r = f.evaluate("""async () => {
              const v = document.querySelector('video');
              v.muted = true; try { await v.play(); } catch (e) {}
              const t0 = v.currentTime; await new Promise(r => setTimeout(r, 3000));
              const res = {src: v.currentSrc, dur: v.duration, t0, t1: v.currentTime, estado: v.readyState, erro: v.error && v.error.code};
              v.pause(); return res;
            }""")
            ok = r["src"].endswith(f"/{cod}.mp4") and r["dur"] > 25 and r["t1"] > r["t0"] + 1 and not r["erro"]
            print(f"{'ok' if ok else 'FALHA'} {cod}: {r['src'].rsplit('/', 1)[-1]} · {r['dur']:.1f} s · tocou "
                  f"{r['t0']:.1f}→{r['t1']:.1f} s · readyState {r['estado']}")
            falhas += not ok
            # o clique no vídeo deixa o visual do player selecionado, e aí o Ctrl+clique no × só mexe na seleção:
            # um clique fora da página desfaz a seleção
            pg.mouse.click(x0 + 960 * k, y0 + 1110 * k)
            time.sleep(1)
            ctrl_clique(pg, *centro(casca.PLAYER_FECHAR))
            time.sleep(3)
            if video_do_player(pg, cod):
                print(f"FALHA {cod}: o player não fechou")
                falhas += 1
            else:
                print(f"ok {cod}: fechou")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
