# -*- coding: utf-8 -*-
"""21 · 20 anos — como o mapa mudou em 20 anos? (dono: tela 21)

De 3.103 para 2.663 municípios com o PT à frente, de 2006 a 2026.

  T21_Fundo_Html   fundo (atrás do Deneb, mesma caixa e mesma geometria): manchete, rótulos dos contadores, régua dos
                   anos com quem disputou cada eleição, a nota "aperte o play" e a legenda de cor
  T21_Mapa_Deneb   Deneb (Vega 6, canvas): os 5.571 municípios pela margem do PT no ano; o contorno das UFs se desenha
                   e os pontos esmaecem do norte para o sul; o play anda de 2006 a 2026 (1,75 s por eleição, a cor
                   desliza entre os anos, o relógio para no fim, L123); a régua dos anos é clicável; as barras e os
                   contadores (ano, municípios com o PT à frente, margem nacional) contam a cada passo, com os glifos
                   da Sora. Hover: o dossiê do município da tela 19 (ttT19Municipio)

Medidas em pbi/dax/T21 20 anos (desenho gerado por pbi/scripts/desenho_t21.py); spec em pbi/spec/t21_mapa.json.
"""
from __future__ import annotations

import desenho_t21 as D
import desenho_t19 as D19
import pbip_lib as lib
import pagina_lib
import roteiro
from pbip_lib import Visual

P = "T21"
CSS = "Estilo · CSS"
Z = lib.CAMADAS["conteudo"]
CAIXA = (150, 140, D.W, D.H)


def _mapa() -> dict:
    campos = [lib.campo_coluna("cod", "Município", "CodIBGE"), lib.campo_medida("x", "T21 · mapa · x inteiro"),
              lib.campo_medida("y", "T21 · mapa · y inteiro")]
    campos += [lib.campo_medida(f"m{a % 100:02d}", f"T21 · mapa · margem {a} inteira") for a in D.ANOS]
    campos.append(lib.campo_medida("anos", "T21 · Mapa · anos para o Deneb"))
    doc = lib.visual_deneb("T21_Mapa_Deneb", *CAIXA, "spec/t21_mapa.json", campos,
                           alt=lib.medida("T21 · Mapa · ALT"), z=Z + 1, tab=110, tooltip_pagina="ttT21Municipio",
                           renderizacao="canvas")
    # L123: a vista não é recompilada quando o dado chega de novo (o relógio e o ano em tela não voltam ao começo)
    doc["visual"]["objects"]["dataLimit"] = [{"properties": {"enableIncrementalDataUpdates": lib.lit(True)}}]
    return doc


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T21_Fundo_Html", *CAIXA, "T21 · Fundo · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=D.corpo_fundo(), alt=lib.medida("T21 · Fundo · ALT"), z=Z, tab=100)),
        Visual(P, _mapa()),
        *pagina_lib.tooltip("ttT21Municipio", "20 anos · município", 460, 350, "T21 · Dossiê · HTML",
                            ordem=100 + int(roteiro.numero(P)) * 10,
                            folha_de_estilo=CSS, modelo_corpo=D19.corpo_dossie()),
    ]
