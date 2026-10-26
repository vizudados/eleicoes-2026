# -*- coding: utf-8 -*-
"""T04 · Flávio · quem é (dono: agente das telas 01–06). Mesma geometria e mesmo gerador da outra tela "quem é"
(neutralidade): tudo em pbi/scripts/desenho_t02_t04.py, o lado é parâmetro. Antes/Depois pela casca."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desenho_t02_t04 import declarar_quem_e  # noqa: E402


def declarar(ctx):
    return declarar_quem_e("T04")
