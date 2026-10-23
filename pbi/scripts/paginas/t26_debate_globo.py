# -*- coding: utf-8 -*-
"""20 · Debate na Globo — o último debate mudou alguma coisa? (código T26; dono: agente da T26)

Pedido do Alisson em 23/10/2026, dia do debate: uma página por debate do 2º turno, pronta antes dos números. A da Band
(18/10) é a 08 · Debate (T07); esta é a da Globo (23/10, 21h20). Desenho próprio, sem repetir o formato da T07 nem o do
documentário: em vez de "o número da noite + o palco + o gráfico", uma ficha da noite, o palco com os dois púlpitos e
uma fita do tempo com os cinco números que vão chegar, cada um com o seu lugar marcado até chegar.

  T26_Ficha_Html     a ficha: o selo da situação (marcado, no ar, realizado, adiado, cancelado), a hora, onde passa,
                     mediação e checagem, a manchete (o que já dá para dizer) e as regras em blocos
  T26_Palco_Html     os dois púlpitos em traço (grão 'T26 Debate Globo'[Chave], só as linhas de presença): nome, púlpito
                     na cor do candidato (tracejado e vazio se ele faltar ou se o debate cair) e a situação; o palco, a
                     mesa da mediação e as luzes ficam no bodyTemplate. Dossiê ttT26Presenca (histórico e fonte)
  T26_Noite_Html     o fundo da faixa de baixo: o título e a fita do tempo, do início do debate à eleição de domingo
  T26_Noite_Cartoes  os cinco cartões (grão 'T26 Debate Globo'[Cartão]): buscas, audiência, transmissão na internet,
                     redes e pesquisas, pendurados na fita na ordem em que chegam; o número (contador) ou o lugar dele
                     tracejado com "aguardando", a fonte e a régua da Band (18/10) na mesma medida. Dossiê ttT26Cartao

Sem filtro cruzado: nada na tela muda com clique. O realce no hover é o da casa (CSS_REALCE: o púlpito ou o cartão sob
o mouse fica, os outros apagam). Contas e desenho: pbi/scripts/desenho_t26.py.
"""
from __future__ import annotations

import estilo
import pagina_lib
import pbip_lib as lib
from pbip_lib import Visual
from paginas import _campanha as cp

P = "T26"
CSS = "Estilo · CSS"
C = estilo.COR
Z = lib.CAMADAS["conteudo"]

FICHA = (150, 140, 880, 340)
PALCO = (1060, 140, 710, 330)
NOITE = (150, 490, 1620, 510)

CSS_FICHA = (
    f".t26f .selo{{position:absolute;left:2px;top:2px;width:170px;height:46px;display:flex;align-items:center;"
    f"justify-content:center;transform:rotate(-3deg);background:url({cp.img('arte/limpos/dossie/carimbo-retangular-tinta.png', 340)}) "
    "center/100% 100% no-repeat}"
    ".t26f .selo span{font-size:15px;font-weight:700;letter-spacing:.22em;color:var(--tinta);padding-left:.22em}"
    ".t26f .dia{position:absolute;left:196px;top:6px;white-space:nowrap}"
    ".t26f .situ{position:absolute;left:196px;top:26px;white-space:nowrap}"
    ".t26f .hora{position:absolute;left:0;top:58px}"
    ".t26f .hora .num{font-size:88px;letter-spacing:-.045em}"
    ".t26f .riscado{color:var(--cinza);text-decoration:line-through;text-decoration-thickness:5px}"
    ".t26f .onde{position:absolute;left:300px;top:66px;width:580px}"
    ".t26f .onde .txt{font-size:17px;line-height:1.4}"
    ".t26f .onde b{font-weight:600;color:var(--tinta)}"
    ".t26f .onde .nota{margin-top:4px}"
    ".t26f .man{position:absolute;left:0;top:156px;width:870px;font-size:23px}"
    ".t26f .regras{position:absolute;left:0;top:246px;width:880px;display:flex;gap:10px}"
    f".t26f .bl{{width:var(--bl);border-top:2px solid {C['tinta']};padding-top:6px}}"
    ".t26f .bl .bt{font-size:15px;line-height:1.25;margin-top:3px;color:var(--tinta);min-height:38px}"
    ".t26f .bl .bm{font-size:15px;color:var(--grafite);margin-top:2px;white-space:nowrap}"
    ".t26f .bl .bm b{font-weight:700;color:var(--tinta)}"
)


def corpo_palco() -> str:
    """O palco fixo (piso, luzes, a mesa da mediação) atrás dos dois púlpitos que a medida desenha."""
    t, a, g = C["tinta"], C["areia"], C["grafite"]
    palco = (
        "<svg class='palco' width='710' height='330' viewBox='0 0 710 330'>"
        f"<g fill='none' stroke='{a}' stroke-width='1.2' stroke-dasharray='2 7' stroke-linecap='round'>"
        "<path d='M138 64 L96 212 M162 64 L204 212'/><path d='M548 64 L506 212 M572 64 L614 212'/></g>"
        f"<path class='traco' pathLength='1' d='M8 214 C 200 204, 510 204, 702 214' fill='none' stroke='{g}' "
        "stroke-width='1.8' stroke-linecap='round' filter='url(#rbu)'/>"
        f"<path class='traco' pathLength='1' d='M40 228 C 220 220, 490 220, 670 228' fill='none' stroke='{a}' "
        "stroke-width='1.4' stroke-linecap='round' filter='url(#rbu)' style='animation-delay:.3s'/>"
        f"<g class='entra d4' fill='{C['papel']}' stroke='{t}' stroke-width='2' stroke-linejoin='round' "
        "filter='url(#rbu)'><path d='M300 172 L410 172 L404 208 L306 208 Z'/><path d='M318 186 L392 186' fill='none'/>"
        "<path d='M355 172 L355 158 C 355 152, 360 149, 366 149' fill='none' stroke-linecap='round'/></g>"
        "</svg>"
    )
    css = (
        ".palco{position:fixed;left:0;top:0;pointer-events:none}"
        ".pmed{position:fixed;left:255px;width:200px;top:124px;text-align:center;pointer-events:none}"
        f".pdica{{position:fixed;left:255px;width:200px;top:276px;text-align:center;font-family:var(--mao);"
        f"font-size:26px;color:{C['grafite']};transform:rotate(-2deg);pointer-events:none}}"
        ".t26p{pointer-events:none}"
        ".t26p .pu{position:absolute;top:0;width:260px;height:262px;text-align:center;pointer-events:auto;cursor:help}"
        ".t26p .nm{height:58px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}"
        ".t26p .nm span{font-size:24px;font-weight:700;letter-spacing:-.01em;line-height:1.1}"
        ".t26p .nm small{margin-top:3px}"
        ".t26p .pul{display:block;margin:4px auto 0}"
        ".t26p .pul path{fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}"
        f".t26p .ok.l .pul path,.t26p .duvida.l .pul path{{stroke:{C['vermelho']}}}"
        f".t26p .ok.f .pul path,.t26p .duvida.f .pul path{{stroke:{C['azul']}}}"
        ".t26p .ok.l .pul .tampo,.t26p .ok.l .pul .corpo{fill:rgba(217,135,123,.22)}"
        ".t26p .ok.f .pul .tampo,.t26p .ok.f .pul .corpo{fill:rgba(143,168,207,.26)}"
        # o púlpito se desenha (traço); com dúvida, tracejado longo; vazio (ausente ou sem debate), tracejado curto e cinza
        ".t26p .ok .pul path{stroke-dasharray:1;stroke-dashoffset:0;animation:eTraco 1.6s cubic-bezier(.45,.05,.3,1) both}"
        ".t26p .duvida .pul path{stroke-dasharray:.07 .04}"
        f".t26p .vazio .pul path{{stroke:{C['cinza']};stroke-dasharray:.035 .035;stroke-width:2}}"
        ".t26p .vazio .nm span{color:var(--cinza)}"
        ".t26p .st{margin-top:24px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:16px;"
        "font-weight:600;color:var(--tinta)}"
        f".t26p .st .ok{{display:block;width:24px;height:24px;background:url({cp.img('arte/limpos/dossie/visto-tinta.png', 48)}) "
        "center/contain no-repeat}"
        f".t26p .st .qq{{font-style:normal;width:22px;height:22px;border-radius:50%;border:1.6px solid {C['grafite']};"
        "font-size:14px;line-height:19px}"
        f".t26p .st .xx path{{stroke:{C['grafite']};stroke-width:2.6;stroke-linecap:round;fill:none}}"
        ".t26p .vazio .st{color:var(--grafite)}"
    )
    return (f"<style>{css}</style>{cp.defs_rabisco()}{palco}"
            "<div class='pmed rot entra d5'>MEDIAÇÃO</div><div class='pdica entra d10'>passe o mouse</div>"
            "{{content}}")


def corpo_noite() -> str:
    css = (
        ".t26n .cab{position:absolute;left:0;top:0;width:1400px}"
        ".t26n .cab .txt{margin-top:4px}"
        ".t26n .ini{position:absolute;left:0;top:48px;white-space:nowrap}"
        ".t26n .fimr{position:absolute;right:58px;top:48px;white-space:nowrap}"
        ".t26n .fita{position:absolute;left:0;top:60px}"
        f".t26n .fita path{{fill:none;stroke:{C['tinta']};stroke-width:2.2;stroke-linecap:round}}"
        f".t26n .fita circle{{fill:{C['tinta']}}}"
        f".t26n .urna{{position:absolute;right:0;top:46px;width:52px;height:44px;background:url({cp.icone('urna', 104)}) "
        "center/contain no-repeat}"
    )
    return f"<style>{css}</style>{cp.defs_rabisco()}{{{{content}}}}"


ICONES = {"buscas": "lupa", "audiencia": "tv-debate", "streaming": "celular", "redes": "megafone", "pesquisas": "barras"}


def corpo_cartoes() -> str:
    t = C["tinta"]
    icones = "".join(f".t26c .ic-{k}{{background-image:url({cp.icone(v, 80)})}}" for k, v in ICONES.items())
    css = (
        ".t26c{pointer-events:none}"
        f".t26c .cx{{position:absolute;top:88px;width:300px;height:418px;display:flex;flex-direction:column;"
        f"padding:12px 16px 12px 16px;background:{C['branco']};box-shadow:inset 0 0 0 1px {C['areia']};"
        "pointer-events:auto;cursor:help;animation:uSobe .7s cubic-bezier(.2,.7,.2,1) both}"
        f".t26c .tk{{position:absolute;left:149px;top:-16px;width:2px;height:16px;background:{t}}}"
        f".t26c .tk::before{{content:'';position:absolute;left:-5px;top:-6px;width:12px;height:12px;border-radius:50%;"
        f"background:{C['papel']};box-shadow:inset 0 0 0 2.4px {t}}}"
        f".t26c .publicado .tk::before,.t26c .consolidado .tk::before{{background:{t}}}"
        f".t26c .previa .tk::before,.t26c .parcial .tk::before{{background:linear-gradient(90deg,{t} 50%,{C['papel']} 50%)}}"
        ".t26c .ic{position:absolute;right:12px;top:10px;width:42px;height:42px;background:center/contain no-repeat;"
        "opacity:.85}"
        + icones +
        ".t26c .qd{padding-right:46px;min-height:50px}"
        ".t26c .qd .qt{font-size:15px;line-height:1.3;color:var(--grafite);margin-top:2px}"
        ".t26c .ti{margin-top:8px;font-size:20px;font-weight:600;letter-spacing:-.01em;line-height:1.2}"
        ".t26c .me{margin-top:4px;font-size:15px;line-height:1.3;color:var(--grafite)}"
        ".t26c .vz{position:relative;margin-top:10px;height:100px;flex:none}"
        ".t26c .mold{position:absolute;left:0;top:0}"
        f".t26c .mold path{{fill:none;stroke:{C['cinza']};stroke-width:1.6;stroke-dasharray:7 6;stroke-linecap:round}}"
        ".t26c .vz .mao{position:absolute;left:0;right:0;top:32px;text-align:center;font-size:30px;color:var(--grafite)}"
        ".t26c .vz.um{display:flex;align-items:baseline;gap:8px;padding-top:24px}"
        ".t26c .vz.um .num{font-size:64px;letter-spacing:-.04em;white-space:nowrap;flex:none}"
        ".t26c .vz.um .un{font-size:17px;color:var(--grafite);line-height:1.2}"
        ".t26c .vz .tag{position:absolute;left:0;top:0;font-size:13px;font-weight:600;letter-spacing:.14em;color:var(--cinza)}"
        ".t26c .vz.nd .ndt{padding-top:30px;font-size:20px;font-weight:600;color:var(--cinza)}"
        ".t26c .vz.par{display:flex;gap:12px}"
        ".t26c .lado{position:relative;width:128px;height:100px}"
        ".t26c .lado .rot{position:relative;padding-top:10px}"
        ".t26c .lado.vazio .rot{padding-left:12px}"
        ".t26c .lado .ndt{padding:30px 0 0 12px;font-size:17px;font-weight:600;color:var(--cinza)}"
        ".t26c .lado .mao{top:42px;font-size:26px}"
        ".t26c .lado .nl{margin-top:12px;white-space:nowrap}"
        ".t26c .lado .nl .num{font-size:46px;letter-spacing:-.04em}"
        ".t26c .lado .nl small{font-size:17px;font-weight:600;color:var(--grafite);margin-left:2px}"
        ".t26c .np{margin-top:6px;font-size:13px;line-height:1.35;color:var(--grafite)}"
        ".t26c .fo{margin-top:8px;font-size:13px;line-height:1.35;color:var(--cinza)}"
        f".t26c .ref{{margin-top:auto;border-top:1.5px solid {C['areia']};padding-top:8px}}"
        ".t26c .ref .rq{letter-spacing:0;text-transform:none;font-weight:400;color:var(--grafite)}"
        ".t26c .ref .rv{display:flex;gap:16px;margin-top:6px;font-size:15px;font-weight:600;white-space:nowrap}"
        ".t26c .ref .rv .num{font-size:21px;margin-left:3px}"
        ".t26c .br{display:flex;align-items:center;gap:8px;height:26px;margin-top:2px}"
        ".t26c .br .bn{width:42px;font-size:13px;color:var(--grafite)}"
        ".t26c .br i{display:block;height:12px}"
        f".t26c .br .g{{background:{t}}}.t26c .br .b{{background:{C['areia']}}}"
        f".t26c .br .oca{{width:140px;box-shadow:inset 0 0 0 1px {C['cinza']};background:repeating-linear-gradient(90deg,"
        "transparent 0 6px,rgba(107,99,87,.22) 6px 8px)}"
        ".t26c .br b.num{font-size:20px;white-space:nowrap}"
    )
    return f"<style>{css}</style>{{{{content}}}}"


CSS_TT_CARTAO = (
    ".dos .lis .li{margin:2px 0;font-size:15px;line-height:1.38}"
    ".dos .lst{margin:4px 0 6px 0}"
    ".dos .ps{display:grid;grid-template-columns:1fr 52px 52px;font-size:13px;line-height:1.55;color:var(--grafite)}"
    ".dos .ps b{text-align:right;font-weight:700}"
    ".dos .ps.dep span{font-weight:600;color:var(--tinta)}"
)
CSS_TT_PRESENCA = ".dos .lis .li{margin:2px 0;font-size:15px;line-height:1.38}"


def declarar(ctx):
    return [
        Visual(P, lib.visual_html("T26_Ficha_Html", *FICHA, "T26 · Ficha · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=f"<style>{CSS_FICHA}</style>{{{{content}}}}",
                                  alt=lib.medida("T26 · Ficha · ALT"), z=Z, tab=100)),
        Visual(P, lib.visual_html("T26_Palco_Html", *PALCO, "T26 · Palco · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_palco(), granularidade=("T26 Debate Globo", "Chave"),
                                  tooltip_pagina="ttT26Presenca", alt=lib.medida("T26 · Palco · ALT"), z=Z + 1,
                                  tab=110)),
        Visual(P, lib.visual_html("T26_Noite_Html", *NOITE, "T26 · Noite · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_noite(), alt=lib.medida("T26 · Noite · ALT"), z=Z + 2, tab=120)),
        Visual(P, lib.visual_html("T26_Noite_Cartoes", *NOITE, "T26 · Cartões · HTML", folha_de_estilo=CSS,
                                  modelo_corpo=corpo_cartoes(), granularidade=("T26 Debate Globo", "Cartão"),
                                  tooltip_pagina="ttT26Cartao", alt=lib.medida("T26 · Cartões · ALT"), z=Z + 3,
                                  tab=130)),
        *pagina_lib.tooltip("ttT26Presenca", "Debate na Globo · presença", 480, 400, "T26 · Tooltip presença · HTML",
                            ordem=300, folha_de_estilo=CSS, modelo_corpo=cp.dossie("microfone", CSS_TT_PRESENCA)),
        *pagina_lib.tooltip("ttT26Cartao", "Debate na Globo · número da noite", 520, 530, "T26 · Tooltip cartão · HTML",
                            ordem=301, folha_de_estilo=CSS, modelo_corpo=cp.dossie("tv-debate", CSS_TT_CARTAO)),
    ]
