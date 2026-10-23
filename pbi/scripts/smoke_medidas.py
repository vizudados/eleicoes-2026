# -*- coding: utf-8 -*-
"""smoke_medidas — avalia no motor do Desktop aberto cada medida de desenho (HTML/CSS/JS) em três contextos: sem
filtro, com uma UF (Minas Gerais, que mudou de lado), com a UF menor (Roraima) e com um município (Contagem/MG). Reprova
erro do motor e texto acima de 32.760 caracteres (L048, por precaução). L039: erro de motor para tudo.

**VAZIO não é erro.** O visual com granularidade (a tira da T06, a escada da T03, os alvos do filtro cruzado) só tem
texto dentro de uma linha do grão; num contexto total ele é vazio mesmo. O que prova esses visuais é a prévia
(`previa.py`) e a foto do Desktop.

    python -X utf8 pbi/scripts/smoke_medidas.py [prefixo]      # ex.: "T06 ·"
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import dax  # noqa: E402

DAX_DIR = AQUI.parent / "dax"
# medidas de linha: (padrão do nome, coluna da granularidade) — as telas que desenham uma linha por item.
GRAOS: list[tuple[str, str]] = []
# contextos de prova: sem filtro, a UF que mudou de lado, a menor UF e um município
FILTROS = ["", 'TREATAS ( { "Minas Gerais" }, UF[Nome] )', 'TREATAS ( { "Roraima" }, UF[Nome] )',
           "TREATAS ( { \"Contagem (MG)\" }, 'Município'[Rótulo] )"]


def nomes(prefixo: str) -> list[str]:
    out = []
    for p in sorted(DAX_DIR.rglob("*.dax")):
        if "_modelo" in p.parts:
            continue
        t = p.read_text(encoding="utf-8")
        mm = re.search(r"@nome:\s*(.+)", t)
        nome = mm.group(1).strip() if mm else p.stem
        if re.search(r"· (HTML|CSS|JS)\b", nome) and nome.startswith(prefixo):
            out.append(nome)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    prefixo = sys.argv[1] if len(sys.argv) > 1 else ""
    erros = 0
    for nome in nomes(prefixo):
        ref = "[" + nome.replace("]", "]]") + "]"
        grao = next((g for p, g in GRAOS if re.search(p, nome)), None)
        for f in FILTROS:
            filtro = f", {f}" if f else ""
            if grao:
                q = (f"EVALUATE ADDCOLUMNS ( SUMMARIZECOLUMNS ( {grao}{filtro}, \"@h\", {ref} ), "
                     f"\"@n\", LEN ( [@h] ) )")
            else:
                q = f"EVALUATE ROW ( \"@n\", CALCULATE ( LEN ( {ref} ){filtro} ) )"
            try:
                r = dax.consultar(q)
            except dax.ErroDax as e:
                erros += 1
                print(f"ERRO  {nome} [{f or 'sem filtro'}]: {str(e)[:300]}")
                continue
            ns = [x.get("[@n]") or 0 for x in r]
            mx = max(ns) if ns else 0
            # sem grupo de cálculo no modelo, o teto de 32.760 (L048) não vale; o CSS com a Barlow embutida tem ~50 mil
            teto = 1_000_000 if "· CSS" in nome else 32_760
            flag = "ok " if mx and mx < teto else "VAZIO" if not mx else "GRANDE"
            if flag != "ok ":
                erros += 1 if flag == "GRANDE" else 0
            print(f"{flag} {nome} [{f or 'sem filtro'}]: {len(ns)} linha(s), maior {mx} caracteres")
    print(f"\n{erros} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
