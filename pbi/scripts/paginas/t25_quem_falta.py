# -*- coding: utf-8 -*-
"""T25 · Quem falta — quem mais falta às urnas, e onde? (a 07 na ordem do roteiro, logo depois da 06 · Ausência; dono:
agente das telas 06 e 07). Declarações em pbi/scripts/desenho_t25.py (declarar_quem_falta), junto do gerador das
medidas e do spec do mapa. Filtro de UF da casca.

Filtro cruzado entre três peças (pedido do Alisson, 23/10/2026): o clique num ano muda o mapa e as idades; o clique numa
faixa de idade muda o mapa e os anos; o clique num município muda os anos e as idades. A manchete acompanha tudo.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desenho_t25 import declarar_quem_falta  # noqa: E402


def declarar(ctx):
    return declarar_quem_falta()
