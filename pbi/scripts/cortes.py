#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cortes — acha texto cortado nas telas: tinta do glifo fora do visual ou de uma caixa que recorta.

O HTML Content recorta tudo o que passa da caixa do visual. Um número grande com top negativo ou line-height curto
perde o alto dos dígitos (o '711' da tela 12 saiu sem o topo do 1). A caixa do texto não basta para achar isso: ela
inclui o respiro da fonte. Aqui a tinta é medida de verdade: para cada nó de texto visível, a métrica da fonte no
canvas (actualBoundingBoxAscent/Descent, com o letter-spacing do elemento) dá onde o glifo começa e termina em
relação à linha de base, e a linha de base sai do retângulo do texto. A tinta é comparada com a janela do visual e
com cada ancestral que recorta (overflow diferente de visible).

Cada tela é montada pela previa (mesma árvore do visual, iframe do tamanho do visual, animações no estado final), no
estado normal e com a leitura aberta, e medida no Edge headless.

    python -X utf8 pbi/scripts/cortes.py                 # todas as telas, com e sem leitura
    python -X utf8 pbi/scripts/cortes.py T11 T13         # só essas
    python -X utf8 pbi/scripts/cortes.py --sem-leitura   # só o estado normal

Saída: uma linha por corte (tela, visual, lado, px, trecho) e pbi/qa/cortes/cortes.json. Código 1 se houver corte.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
PAGINAS = PBI / "pbip" / "Eleicoes.Report" / "definition" / "pages"
MARCADORES = PBI / "pbip" / "Eleicoes.Report" / "definition" / "bookmarks"
SAIDA = PBI / "qa" / "cortes"
FOLGA = 1.0  # px de tolerância (antisserrilhado)

MEDIR = r"""async () => {
  await document.fonts.ready;
  const cv = document.createElement('canvas').getContext('2d');
  const W = innerWidth, H = innerHeight, achados = [];
  const visivel = el => {
    for (let a = el; a; a = a.parentElement) {
      const c = getComputedStyle(a);
      if (c.display === 'none' || c.visibility === 'hidden' || parseFloat(c.opacity) === 0) return false;
    }
    return true;
  };
  // só recorta o ancestral por onde passa a cadeia de blocos de contenção: um filho absoluto escapa dos ancestrais
  // estáticos até o primeiro posicionado (ou com transform); html e body ficam com a janela do visual
  const recortes = el => {
    const caixas = [{x0: 0, y0: 0, x1: W, y1: H, quem: 'visual', ret: false}];
    let pula = null;
    for (let a = el; a && a !== document.body && a !== document.documentElement; a = a.parentElement) {
      const c = getComputedStyle(a);
      if (pula) {
        const contem = c.transform !== 'none' || c.filter !== 'none' || (pula === 'absolute' && c.position !== 'static');
        if (!contem) continue;
        pula = null;
      }
      const clipa = c.overflowX !== 'visible' || c.overflowY !== 'visible';
      if (c.position === 'absolute' || c.position === 'fixed') pula = c.position;
      if (clipa) {
        const r = a.getBoundingClientRect();
        const bl = parseFloat(c.borderLeftWidth), bt = parseFloat(c.borderTopWidth);
        caixas.push({x0: r.left + bl, y0: r.top + bt, x1: r.left + bl + a.clientWidth, y1: r.top + bt + a.clientHeight,
                     quem: a.tagName.toLowerCase() + (a.className ? '.' + String(a.className).split(' ')[0] : ''),
                     ret: getComputedStyle(el).textOverflow === 'ellipsis' || c.textOverflow === 'ellipsis',
                     sox: c.overflowX === 'visible', soy: c.overflowY === 'visible'});
      }
    }
    return caixas;
  };
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const t = n.textContent.replace(/\s+/g, ' ').trim();
    const el = n.parentElement;
    if (!t || !el || ['SCRIPT', 'STYLE', 'TITLE'].includes(el.tagName) || !visivel(el)) continue;
    const g = document.createRange(); g.selectNodeContents(n);
    const rs = Array.from(g.getClientRects()).filter(q => q.width > 0.5 && q.height > 0.5);
    if (!rs.length) continue;
    const cs = getComputedStyle(el);
    cv.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    try { cv.letterSpacing = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing; } catch (e) {}
    const m = cv.measureText(t);
    const alt = m.fontBoundingBoxAscent + m.fontBoundingBoxDescent;
    if (!alt) continue;
    const k = rs[0].height / alt;                       // escala de transform dos ancestrais
    const topo = rs[0].top + (m.fontBoundingBoxAscent - m.actualBoundingBoxAscent) * k;
    const ult = rs[rs.length - 1];
    const base = ult.top + (m.fontBoundingBoxAscent + m.actualBoundingBoxDescent) * k;
    let esq = null, dir = null;
    // texto girado (nota à mão com rotate): a métrica do canvas não vale; a caixa girada contém a tinta, então ela é
    // a medida (pode sobrar 1 ou 2 px de respiro da fonte, nunca faltar)
    let girado = false;
    for (let a = el; a && a !== document.body; a = a.parentElement) {
      const tr = getComputedStyle(a).transform;
      if (tr && tr !== 'none') { const v = tr.match(/matrix\(([^)]+)\)/); if (v) { const p = v[1].split(',').map(Number); if (Math.abs(p[1]) > 1e-3 || Math.abs(p[2]) > 1e-3) { girado = true; break; } } }
    }
    let topoT = topo, baseT = base;
    if (girado) {
      topoT = Math.min(...rs.map(q => q.top)); baseT = Math.max(...rs.map(q => q.bottom));
      esq = Math.min(...rs.map(q => q.left)); dir = Math.max(...rs.map(q => q.right));
    } else if (rs.length === 1) {                       // horizontal só em linha única (a quebra já cabe na largura)
      esq = rs[0].left - Math.max(0, m.actualBoundingBoxLeft) * k;
      dir = rs[0].left + m.actualBoundingBoxRight * k;
    }
    const x0t = esq !== null ? esq : Math.min(...rs.map(q => q.left)), x1t = dir !== null ? dir : Math.max(...rs.map(q => q.right));
    for (const c of recortes(el)) {
      // inteiro fora da caixa = escondido de propósito (linhas da lista além da altura do visual): não é corte
      if (baseT <= c.y0 || topoT >= c.y1 || x1t <= c.x0 || x0t >= c.x1) continue;
      const lados = [];
      if (!c.soy && topoT < c.y0 - %FOLGA%) lados.push(['topo', c.y0 - topoT]);
      if (!c.soy && baseT > c.y1 + %FOLGA%) lados.push(['base', baseT - c.y1]);
      if (!c.ret && !c.sox && esq !== null && esq < c.x0 - %FOLGA%) lados.push(['esquerda', c.x0 - esq]);
      if (!c.ret && !c.sox && dir !== null && dir > c.x1 + %FOLGA%) lados.push(['direita', dir - c.x1]);
      for (const [lado, px] of lados)
        achados.push({lado, px: Math.round(px * 10) / 10, quem: c.quem, fonte: cs.fontSize,
                      texto: t.slice(0, 40), classe: el.className ? String(el.className) : el.tagName.toLowerCase()});
    }
  }
  return achados;
}""".replace("%FOLGA%", str(FOLGA))


def telas() -> list[str]:
    return sorted(p.name for p in PAGINAS.iterdir() if p.is_dir() and not p.name.startswith("tt"))


def montar(pagina: str, marcador: str | None) -> Path | None:
    nome = pagina + (f"-{marcador}" if marcador else "")
    png = SAIDA / f"{nome}.png"
    cmd = [sys.executable, "-X", "utf8", str(AQUI / "previa.py"), pagina, "--saida", str(png)]
    if marcador:
        cmd += ["--marcador", marcador]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    html = png.with_suffix(".html")
    if not html.exists():
        print(f"{nome}: a prévia não montou ({(r.stdout + r.stderr).strip()[-160:]})")
        return None
    return html


def medir(nav, html: Path) -> list[dict]:
    # movimento reduzido, como na foto da prévia: o kit de movimento mostra o número final sem contar
    pg = nav.new_page(viewport={"width": 1920, "height": 1080}, reduced_motion="reduce")
    pg.goto(html.as_uri(), wait_until="load")
    pg.wait_for_timeout(1500)
    achados = []
    for f in pg.frames[1:]:
        try:
            visual = f.frame_element().get_attribute("title") or "?"
            for a in f.evaluate(MEDIR):
                achados.append({"visual": visual, **a})
        except Exception as e:  # noqa: BLE001 (quadro que caiu no meio: segue)
            achados.append({"visual": "?", "lado": "erro", "px": 0, "texto": str(e)[:80]})
    pg.close()
    return achados


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("paginas", nargs="*")
    ap.add_argument("--sem-leitura", action="store_true")
    a = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    casos = []
    for p in a.paginas or telas():
        casos.append((p, None))
        if not a.sem_leitura and (MARCADORES / f"{p}_LEITURA_ABRE_01.bookmark.json").exists():
            casos.append((p, f"{p}_LEITURA_ABRE_01"))
    tudo = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(channel="msedge")
        for p, m in casos:
            html = montar(p, m)
            if not html:
                continue
            for c in medir(nav, html):
                c["tela"] = p + (" (leitura)" if m else "")
                tudo.append(c)
                print(f"{c['tela']:<16} {c['visual']:<34} {c['lado']:<8} {c['px']:>5} px  {c.get('fonte', ''):>6}  "
                      f"{c.get('classe', '')[:18]:<18} «{c['texto']}» ({c.get('quem', '')})")
        nav.close()
    (SAIDA / "cortes.json").write_text(json.dumps(tudo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(casos)} estados · {len(tudo)} corte(s)")
    return 1 if tudo else 0


if __name__ == "__main__":
    sys.exit(main())
