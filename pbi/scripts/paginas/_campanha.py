# -*- coding: utf-8 -*-
"""_campanha — peças comuns às telas da campanha e do epílogo do mesmo dono (T07 Debate, T08 Buscas, T09 Redes,
T10 Pesquisas, T16 Os outros, T17 2º turno). O "_" no nome tira o módulo da montagem (não declara nada sozinho).

- img(caminho, largura): arte em traço (PNG transparente de arte/limpos) reduzida e embutida como WebP (base64), para
  o bodyTemplate (texto fixo, fora do limite das medidas). WebP com alfa: ~40 % do PNG.
- CSS_DOSSIE: o cartão "dossiê" das páginas de tooltip (papel, fita no topo, ícone em traço no canto, nota à mão).
  Ocupa a página inteira, cantos retos (L078); tudo entra com .sobe/.entra em cascata curta (L079).
- dossie(icone): bodyTemplate do tooltip com a fita e o ícone fixos e o {{content}} da medida.
"""
from __future__ import annotations

import base64
import io
from functools import lru_cache

import estilo

C = estilo.COR


@lru_cache(maxsize=None)
def img(caminho: str, largura: int, qualidade: int = 82) -> str:
    """Arte de arte/limpos (ou outro caminho relativo à raiz) como data URI WebP com `largura` px."""
    from PIL import Image
    im = Image.open(estilo.RAIZ / caminho).convert("RGBA")
    altura = round(im.height * largura / im.width)
    im = im.resize((largura, altura), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "WEBP", quality=qualidade, method=6)
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode("ascii")


def defs_rabisco(ident: str = "rbu", escala: float = 1.8, frequencia: float = 0.03, semente: int = 11) -> str:
    """<svg> vazio com o filtro de traço tremido em coordenadas do usuário: o do estilo (objectBoundingBox) zera a
    região numa linha reta horizontal ou vertical (caixa de altura 0) e a linha some. Use filter='url(#rbu)'."""
    return (f"<svg width='0' height='0' style='position:absolute'><defs><filter id='{ident}' filterUnits='userSpaceOnUse' "
            f"x='-200' y='-200' width='4000' height='2400'><feTurbulence type='fractalNoise' baseFrequency='{frequencia}' "
            f"numOctaves='2' seed='{semente}' result='r'/><feDisplacementMap in='SourceGraphic' in2='r' scale='{escala}' "
            f"xChannelSelector='R' yChannelSelector='G'/></filter></defs></svg>")


def icone(nome: str, largura: int, cor: str = "tinta") -> str:
    return img(f"arte/limpos/icones/{nome}-{cor}.png", largura)


CSS_DOSSIE = (
    f".dos{{position:fixed;inset:0;background:{C['papel']};box-shadow:inset 0 0 0 1.5px {C['areia']};"
    "padding:40px 30px 18px 30px;overflow:hidden}"
    ".dos .fita{position:absolute;left:calc(50% - 60px);top:-14px;width:120px;opacity:.5;transform:rotate(-3deg)}"
    ".dos .ico{position:absolute;right:22px;top:18px;width:46px;opacity:.85}"
    ".dos .sob{font-size:13px;letter-spacing:.14em;padding-right:60px}"
    ".dos .tt{font-size:22px;font-weight:600;line-height:1.2;margin:6px 0 10px 0;padding-right:56px}"
    ".dos .txt{font-size:15px;line-height:1.42;color:var(--tinta)}"
    ".dos .nota{font-size:13px;margin-top:8px}"
    f".dos .mao{{position:absolute;right:26px;bottom:14px;font-size:26px;color:{C['vermelho_escuro']};"
    "transform:rotate(-3deg);white-space:nowrap}"
    f".dos .mao.az{{color:{C['azul_escuro']}}}.dos .mao.ti{{color:{C['tinta']}}}"
    ".dos .par{display:flex;gap:28px;align-items:baseline;margin:4px 0 8px 0}"
    ".dos .par .num{font-size:34px}"
    ".dos .par small{display:block;font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase}"
    f".dos hr{{border:0;border-top:1px solid {C['areia']};margin:10px 0}}"
)


def dossie(icone_nome: str, css_extra: str = "") -> str:
    """bodyTemplate do tooltip dossiê: CSS comum + da tela, a fita e o ícone em traço fixos e o conteúdo da medida."""
    return (f"<style>{CSS_DOSSIE}{css_extra}</style><div class='dos'>"
            f"<img class='fita entra' alt='' src='{img('arte/limpos/dossie/fita-tinta.png', 120)}'/>"
            f"<img class='ico entra d2' alt='' src='{icone(icone_nome, 46)}'/>{{{{content}}}}</div>")
