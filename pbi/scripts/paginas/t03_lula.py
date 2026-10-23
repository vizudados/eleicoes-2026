# -*- coding: utf-8 -*-
"""T03 · Onde estão os votos de Lula? (dono: agente das telas 01–06). Mesmo gerador da outra tela de votos
(neutralidade): tudo em pbi/scripts/desenho_t03_t05.py, o lado é parâmetro. Filtro de UF da casca."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desenho_t03_t05 import declarar_votos  # noqa: E402


def declarar(ctx):
    return declarar_votos("T03")
