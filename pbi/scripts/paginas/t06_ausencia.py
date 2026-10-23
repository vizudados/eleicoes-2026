# -*- coding: utf-8 -*-
"""T06 · Ausência — quantos brasileiros não escolheram ninguém? (dono: agente das telas 06 e 07). Declarações em
pbi/scripts/desenho_t06.py (declarar_ausencia), junto do gerador das medidas. Filtro de UF da casca. O mapa e as idades
que estavam aqui viraram a tela seguinte, 07 · Quem falta (código T25), com filtro cruzado entre as peças."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desenho_t06 import declarar_ausencia  # noqa: E402


def declarar(ctx):
    return declarar_ausencia()
