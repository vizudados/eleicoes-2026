# -*- coding: utf-8 -*-
"""pbip_lib — construtores PBIR do painel Eleições 2026 (kit da casa, Vizu Dados,
adaptado em 23/10/2026).

A biblioteca NÃO grava nada: os construtores devolvem o conteúdo (dict) de page.json / visual.json / bookmark, e o
montar_pbip.py consolida, confere e grava (backup datado + manifesto do que ele gerencia).

Particularidades do kit:
  - HTML Content e Deneb entram como visuais PRIVADOS Standalone 2.0.0.0 (GUID próprio, pacote em CustomVisuals/), não
    pelos GUIDs públicos do AppSource;
  - HTML Content 2.0 grava compatibility.legacyRendering = false (sem o marcador, com o papel content preenchido, o
    visual liga o modo legado sozinho e grava true; o JS da casa é escrito para o DOM novo, achando a raiz por
    document.currentScript) e contentFormatting.renderMode = 'rebuild' (o 'reconcile' não refaz a animação de entrada).
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

AQUI = Path(__file__).resolve().parent                     # pbi/scripts
RAIZ = AQUI.parent                                         # pbi/
PBIP_DIR = RAIZ / "pbip"
NOME_PROJETO = "Eleicoes"
PASTA_REPORT = "Eleicoes.Report"
PASTA_MODELO = "Eleicoes.SemanticModel"
LARGURA, ALTURA = 1920, 1080

_ESQ = "https://developer.microsoft.com/json-schemas/fabric/"
ESQUEMA = {
    "pagina": _ESQ + "item/report/definition/page/2.1.0/schema.json",
    "paginas": _ESQ + "item/report/definition/pagesMetadata/1.1.0/schema.json",
    "visual": _ESQ + "item/report/definition/visualContainer/2.9.0/schema.json",
    "visual_deneb": _ESQ + "item/report/definition/visualContainer/2.12.0/schema.json",
    "bookmark": _ESQ + "item/report/definition/bookmark/2.1.0/schema.json",
    "bookmarks": _ESQ + "item/report/definition/bookmarksMetadata/1.0.0/schema.json",
    "report": _ESQ + "item/report/definition/report/3.3.0/schema.json",
}

# Visuais privados (handoff §12.1 e §7): GUID, versão do package.json, arquivo e SHA-256 conferidos
PACOTES = {
    "html": {"guid": "STANDALONEhtmlContent443BE3AD55E043BF878BED274D3A6855", "versao": "2.0.0.0",
             "arquivo": "visuais/HTML-Content-Standalone.2.0.0.pbiviz",
             "sha256": "1f67297aa8b9e6debe2fb033e6a57f50c3c7cb669175476d760b3421af3e0248", "tamanho": 147347},
    "deneb": {"guid": "STANDALONEdeneb7E15AEF80B9E4D4F8E12924291ECE89A", "versao": "2.0.0.20260908#0dfe02de",
              "arquivo": "visuais/deneb.standalone.2.0.0.0.pbiviz",
              "sha256": "5d4c0ef87b2c29f6888b21423da5547e8b2552bec4778d45a7309e70783ccc5d", "tamanho": 1955983},
    # VizuFilter 2.13.0.0 (23/10/2026): a 2.12.1.0 da casa + o modo régua (cartão "regua": botão arrastável sobre uma
    # coluna numérica, tela 24 · Simulador) + a Sora do painel embutida (família "Sora Vizu", como na 2.12.2.0). Com
    # regua.ativo desligado desenha e grava o mesmo que a 2.12. Fonte fora do repositório (pbi/visuais_src/, ignorado).
    "vizufilter": {"guid": "smartFilterFixed9B35E14F08BD474496777B2253A30D3A", "versao": "2.13.0.0",
                   "arquivo": "visuais/vizufilter/smartFilterFixed9B35E14F08BD474496777B2253A30D3A.2.13.0.0.pbiviz",
                   "sha256": "bde3a8800b76b57474ee732a61a128cfb5db1c8c504db30ff1c8a8323949d9eb", "tamanho": 1094613},
}
GUID_HTML = PACOTES["html"]["guid"]
GUID_DENEB = PACOTES["deneb"]["guid"]
GUID_VIZUFILTER = PACOTES["vizufilter"]["guid"]
DENEB = {"vega": "6.4.0", "desenvolvedor": "2.0.0.0"}
TABELA_MEDIDAS = "_Medidas"

# camadas z (tabOrder segue a leitura: trilho, cabeçalho, conteúdo). O "?" e a leitura ficam abaixo do drawer; o drawer
# em 5000+; a navegação acima do drawer (o trilho segue clicável com o painel aberto), como no kit da casa. O tour guiado
# (véu + card + controles) fica por cima de tudo: 7000 (HTML) e os botões dele logo acima.
CAMADAS = {"conteudo": 300, "acao": 1020, "leitura": 4000, "drawer": 5000, "navegacao": 5500, "tour": 7000}
TOOLTIP_LARGURA_MINIMA = 400

RE_NOME = re.compile(r"^[A-Za-z0-9_-]+$")
# T00 Capa … T23 Encerramento, T24 Quem vota, T25 Quem falta e T26 Debate na Globo (entram no meio do roteiro) · TIX
# (sumário) · TT (tooltip)
RE_NOME_VISUAL = re.compile(r"^(T(?:[01][0-9]|2[0-6])|TT|TIX)_[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9]+$")
RE_TOOLTIP = re.compile(r"^ttT(?:[01][0-9]|2[0-6])[A-Z][A-Za-z0-9]*$")
RE_ALIAS = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
RE_RECURSO = re.compile(r"^[A-Za-z0-9_.-]+\.(svg|png|jpg|jpeg|json)$")
RE_BOOKMARK = re.compile(r"^(?:T(?:[01][0-9]|2[0-6])|TIX)_[A-Z0-9]+(?:_[A-Z0-9]+)*_\d{2}$")
RE_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
MAX_NOME_VISUAL = 50
MAX_ALT = 250
_NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://vizudados.com.br/eleicoes-2026/painel")


class ErroDeclaracao(ValueError):
    """Declaração inválida: o montador para antes de gravar qualquer arquivo."""


def id_estavel(chave: str) -> str:
    return str(uuid.uuid5(_NS, chave))


# ----------------------------------------------------------------------------------------------------------------
# Literais e expressões PBIR
# ----------------------------------------------------------------------------------------------------------------
def _numero(valor) -> str:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"número esperado, veio {valor!r}")
    if isinstance(valor, float):
        if not math.isfinite(valor):
            raise ValueError(f"número não finito: {valor!r}")
        if valor.is_integer():
            return str(int(valor))
        return format(valor, ".6f").rstrip("0").rstrip(".")
    return str(valor)


def lit(valor) -> dict:
    """Literal PBIR: bool → true/false · número → <n>D · texto → '<texto>' (aspa simples dobrada)."""
    if isinstance(valor, bool):
        v = "true" if valor else "false"
    elif isinstance(valor, (int, float)):
        v = _numero(valor) + "D"
    elif isinstance(valor, str):
        v = "'" + valor.replace("'", "''") + "'"
    else:
        raise TypeError(f"literal não suportado: {valor!r}")
    return {"expr": {"Literal": {"Value": v}}}


def literal_filtro(valor) -> str:
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, int):
        return str(valor) + "L"
    if isinstance(valor, float):
        return _numero(valor) + "D"
    if isinstance(valor, str):
        return "'" + valor.replace("'", "''") + "'"
    raise TypeError(f"valor de filtro não suportado: {valor!r}")


def cor(hex_: str) -> dict:
    if not isinstance(hex_, str) or not RE_HEX.match(hex_):
        raise ErroDeclaracao(f"cor inválida {hex_!r}: use #RRGGBB")
    return {"solid": {"color": lit(hex_.upper())}}


def campo_coluna_expr(tabela: str, coluna: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": coluna}}


def campo_medida_expr(nome: str, tabela: str = TABELA_MEDIDAS) -> dict:
    return {"Measure": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": nome}}


def expr_medida(nome: str, tabela: str = TABELA_MEDIDAS) -> dict:
    return {"expr": campo_medida_expr(nome, tabela)}


def expr_recurso(nome: str) -> dict:
    return {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": nome}}}


def proj_coluna(tabela: str, coluna: str, *, alias: str | None = None, rotulo: str | None = None,
                ativa: bool | None = None) -> dict:
    p = {"field": campo_coluna_expr(tabela, coluna), "queryRef": f"{tabela}.{coluna}", "nativeQueryRef": alias or coluna}
    if ativa is not None:
        p["active"] = ativa
    if rotulo is not None:
        p["displayName"] = rotulo
    return p


def proj_medida(nome: str, *, tabela: str = TABELA_MEDIDAS, alias: str | None = None, rotulo: str | None = None) -> dict:
    p = {"field": campo_medida_expr(nome, tabela), "queryRef": f"{tabela}.{nome}", "nativeQueryRef": alias or nome}
    if rotulo is not None:
        p["displayName"] = rotulo
    return p


@dataclass(frozen=True)
class RefMedida:
    """Marca "esta propriedade vem de uma medida" (alt text dinâmico, folha de estilo)."""
    nome: str
    tabela: str = TABELA_MEDIDAS


def medida(nome: str, tabela: str = TABELA_MEDIDAS) -> RefMedida:
    return RefMedida(nome, tabela)


def ordem_coluna(tabela: str, coluna: str, direcao: str = "Ascending") -> tuple:
    if direcao not in ("Ascending", "Descending"):
        raise ErroDeclaracao(f"direção {direcao!r}")
    return (campo_coluna_expr(tabela, coluna), direcao)


def ordem_medida(nome: str, direcao: str = "Ascending", tabela: str = TABELA_MEDIDAS) -> tuple:
    if direcao not in ("Ascending", "Descending"):
        raise ErroDeclaracao(f"direção {direcao!r}")
    return (campo_medida_expr(nome, tabela), direcao)


# ----------------------------------------------------------------------------------------------------------------
# Contêiner comum (moldura desligada; title.text = name nomeia o objeto no painel Seleção — L031)
# ----------------------------------------------------------------------------------------------------------------
def checar_nome_visual(nome: str) -> None:
    if not isinstance(nome, str) or not RE_NOME.match(nome):
        raise ErroDeclaracao(f"nome de visual {nome!r}: só letras ASCII, dígitos, _ e -")
    if len(nome) > MAX_NOME_VISUAL:
        raise ErroDeclaracao(f"nome de visual {nome!r} tem {len(nome)} caracteres (máximo {MAX_NOME_VISUAL}, L031)")
    if not RE_NOME_VISUAL.match(nome):
        raise ErroDeclaracao(f"nome de visual {nome!r} fora de <TELA>_<Bloco>_<Papel> (ex. T1_Res_Venda)")


def _checar_geometria(nome, x, y, w, h, largura=LARGURA, altura=ALTURA) -> None:
    for rot, v in (("x", x), ("y", y), ("largura", w), ("altura", h)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ErroDeclaracao(f"{nome}: {rot} {v!r} não é número")
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > largura + 0.5 or y + h > altura + 0.5:
        raise ErroDeclaracao(f"{nome}: geometria inválida ({x}, {y}, {w}×{h}) para a página {largura}×{altura}")


def _alt(alt, nome: str) -> dict:
    if isinstance(alt, RefMedida):
        return expr_medida(alt.nome, alt.tabela)
    if not isinstance(alt, str) or not alt.strip():
        raise ErroDeclaracao(f"{nome}: alt obrigatório (texto até {MAX_ALT} caracteres ou medida('… · ALT'))")
    if len(alt) > MAX_ALT:
        raise ErroDeclaracao(f"{nome}: alt com {len(alt)} caracteres (máximo {MAX_ALT})")
    return lit(alt)


def _desligado() -> list:
    return [{"properties": {"show": lit(False)}}]


def _container(nome: str, alt, tooltip_pagina: str | None = None) -> dict:
    if tooltip_pagina is None:
        dica = _desligado()
    else:
        if not RE_TOOLTIP.match(tooltip_pagina or ""):
            raise ErroDeclaracao(f"{nome}: página de tooltip {tooltip_pagina!r} fora do padrão tt<TELA><Assunto>")
        dica = [{"properties": {"show": lit(True), "type": lit("Canvas"), "section": lit(tooltip_pagina)}}]
    return {
        "background": _desligado(), "border": _desligado(), "dropShadow": _desligado(),
        "title": [{"properties": {"show": lit(False), "text": lit(nome)}}],
        "visualHeader": _desligado(), "visualTooltip": dica,
        "padding": [{"properties": {"top": lit(0), "bottom": lit(0), "left": lit(0), "right": lit(0)}}],
        "general": [{"properties": {"altText": _alt(alt, nome)}}],
    }


def _visual(nome, x, y, w, h, *, z: int, tab: int | None, tipo: str, alt, query: dict | None = None,
            objetos: dict | None = None, tooltip_pagina: str | None = None, cruzar_filtro: bool | None = None,
            filtros: dict | None = None, oculto: bool = False, pagina_wh: tuple = (LARGURA, ALTURA)) -> dict:
    checar_nome_visual(nome)
    _checar_geometria(nome, x, y, w, h, *pagina_wh)
    v: dict[str, Any] = {"visualType": tipo}
    if query:
        v["query"] = query
    if objetos:
        v["objects"] = objetos
    v["visualContainerObjects"] = _container(nome, alt, tooltip_pagina)
    if cruzar_filtro is not None:
        v["drillFilterOtherVisuals"] = cruzar_filtro
    doc: dict[str, Any] = {"$schema": ESQUEMA["visual"], "name": nome,
                           "position": {"x": x, "y": y, "z": z, "height": h, "width": w,
                                        "tabOrder": z if tab is None else tab},
                           "visual": v}
    if filtros:
        doc["filterConfig"] = filtros
    if oculto:
        doc["isHidden"] = True
    return doc


# ----------------------------------------------------------------------------------------------------------------
# actionButton transparente (o desenho está no papel de parede; o botão só recebe o clique)
# ----------------------------------------------------------------------------------------------------------------
ACOES = ("PageNavigation", "Bookmark", "ClearAllSlicers")
_ESTADOS_BOTAO = ("default", "hover", "press", "selected", "disabled")


def acao_navegar(pagina: str) -> tuple:
    return ("PageNavigation", pagina)


def acao_navegar_medida(medida: str) -> tuple:
    """Navegação com destino condicional (fx): a medida devolve o nome de exibição da página de destino."""
    return ("PageNavigation", ("medida", medida))


def acao_bookmark(nome: str) -> tuple:
    return ("Bookmark", nome)


def acao_limpar_filtros() -> tuple:
    return ("ClearAllSlicers", None)


def _por_estado(props, especial: dict | None = None) -> list:
    # a entrada SEM seletor vem primeiro: sem ela o botão desenha o rótulo padrão mesmo com show=false por estado
    saida = [{"properties": props()}]
    for s in _ESTADOS_BOTAO:
        p = props()
        if especial and s in especial:
            p.update(especial[s])
        saida.append({"properties": p, "selector": {"id": s}})
    return saida


def visual_botao(nome: str, x, y, w, h, acao: tuple | None, *, dica: str, alt: str | None = None,
                 z: int = CAMADAS["acao"], tab: int | None = None, oculto: bool = False,
                 realce: str | None = None, raio: int = 0, pagina_wh: tuple = (LARGURA, ALTURA),
                 realce_transp: tuple = (88, 80), realce_ligado: bool = False,
                 imagens: dict | None = None, fundo: tuple | None = None) -> dict:
    """actionButton transparente sobre um desenho do papel de parede. `realce` = cor #RRGGBB do preenchimento só no
    hover/press (retorno visual do clique; raio em px), com a transparência (hover, press) de `realce_transp`.
    `realce_ligado` liga o preenchimento na base (show=true, transparência 100): no Power BI o "mostrar preenchimento"
    vale para todos os estados, e com ele desligado o Service pinta a cor do hover com opacidade 0 (medido no Service em
    16/10/2026, fill-opacity 0 sob o mouse). Sem ele, o realce não aparece.
    `imagens` = {estado: recurso registrado (PNG)}, pintado sobre a cor `realce` opaca nesses estados ("default",
    "hover", "press"): o botão desenha o próprio rótulo em cada estado (botões da capa, botoes_capa.py).
    `fundo` = (cor #RRGGBB, transparência 0–100) pintado em todos os estados: o botão é também um véu (a visão de sócio
    da T1G esmaece os outros quadros com ele, e o clique no véu volta à visão da empresa; 17/10/2026).
    `acao` = acao_navegar | acao_bookmark | acao_limpar_filtros."""
    if acao is not None and (not isinstance(acao, tuple) or len(acao) != 2 or acao[0] not in ACOES):
        raise ErroDeclaracao(f"{nome}: ação {acao!r}")
    condicional = acao is not None and isinstance(acao[1], tuple) and acao[1][0] == "medida"
    if acao is not None and acao[0] in ("PageNavigation", "Bookmark") and not condicional and not (
            isinstance(acao[1], str) and RE_NOME.match(acao[1])):
        raise ErroDeclaracao(f"{nome}: destino {acao[1]!r} inválido para {acao[0]}")
    if not isinstance(dica, str) or not dica.strip():
        raise ErroDeclaracao(f"{nome}: dica obrigatória")
    especial = None
    if imagens:
        if not realce or not set(imagens) <= set(_ESTADOS_BOTAO):
            raise ErroDeclaracao(f"{nome}: imagens pedem a cor de fundo em `realce` e estados de {_ESTADOS_BOTAO}")
        especial = {e: {"show": lit(True), "fillColor": cor(realce), "transparency": lit(0),
                        "image": {"image": {"name": lit(a), "url": expr_recurso(a), "scaling": lit("Fit")}}}
                    for e, a in imagens.items()}
        realce_ligado = True
    elif realce:
        especial = {"hover": {"show": lit(True), "fillColor": cor(realce), "transparency": lit(realce_transp[0])},
                    "press": {"show": lit(True), "fillColor": cor(realce), "transparency": lit(realce_transp[1])}}
    if fundo:
        if imagens or realce or not RE_HEX.match(fundo[0]) or not 0 <= fundo[1] <= 100:
            raise ErroDeclaracao(f"{nome}: fundo {fundo!r} (cor #RRGGBB e transparência 0–100, sem realce nem imagens)")
        base_fill = {"show": lit(True), "fillColor": cor(fundo[0]), "transparency": lit(fundo[1])}
    else:
        base_fill = {"show": lit(bool(realce) and realce_ligado), "transparency": lit(100)}
    objetos = {
        "fill": _por_estado(lambda: dict(base_fill), especial),
        "outline": _por_estado(lambda: {"show": lit(False), "transparency": lit(100), "weight": lit(0)}),
        "icon": _por_estado(lambda: {"show": lit(False)}),
        "text": _por_estado(lambda: {"show": lit(False), "text": lit("")}),
    }
    if raio:
        objetos["shape"] = [{"properties": {"tileShape": lit("rectangleRounded"), "roundEdge": lit(raio)}}]
    doc = _visual(nome, x, y, w, h, z=z, tab=tab, tipo="actionButton", alt=alt or dica, objetos=objetos,
                  oculto=oculto, pagina_wh=pagina_wh)
    if acao is None:
        doc["visual"]["visualContainerObjects"]["visualLink"] = [{"properties": {"show": lit(False)}}]
        return doc
    props = {"show": lit(True), "type": lit(acao[0]), "tooltip": lit(dica), "suppressDefaultTooltip": lit(True)}
    if acao[0] == "PageNavigation":
        props["navigationSection"] = expr_medida(acao[1][1]) if condicional else lit(acao[1])
    elif acao[0] == "Bookmark":
        props["bookmark"] = lit(acao[1])
    doc["visual"]["visualContainerObjects"]["visualLink"] = [{"properties": props}]
    return doc


def visual_imagem(nome: str, x, y, w, h, recurso: str, *, alt: str, z: int = CAMADAS["conteudo"],
                  tab: int | None = None, oculto: bool = False) -> dict:
    if not RE_RECURSO.match(recurso):
        raise ErroDeclaracao(f"{nome}: recurso {recurso!r} fora do padrão (ASCII, sem espaço)")
    objetos = {"general": [{"properties": {"imageUrl": expr_recurso(recurso)}}],
               "imageScaling": [{"properties": {"imageScalingType": lit("Fit")}}]}
    return _visual(nome, x, y, w, h, z=z, tab=tab, tipo="image", alt=alt, objetos=objetos, oculto=oculto)


# ----------------------------------------------------------------------------------------------------------------
# VizuFilter (smartFilterFixed) — propriedades conferidas contra as capabilities do pacote (padrão da casa)
# ----------------------------------------------------------------------------------------------------------------
CHAVES_SINCRONIA = ("groupName", "fieldChanges", "filterChanges")   # VisualSyncGroup (visualConfiguration 2.3.0)


def grupo_sincronia(nome: str, *, campos: bool = True, filtros: bool = True) -> dict:
    """syncGroup de segmentação entre páginas (`visual.syncGroup`): as segmentações do mesmo grupo projetam o MESMO
    campo, um só (com mais de um campo o Desktop desliga a sincronia)."""
    if not isinstance(nome, str) or not RE_NOME.match(nome):
        raise ErroDeclaracao(f"grupo de sincronia {nome!r}: nome ASCII sem espaço")
    return {"groupName": nome, "fieldChanges": bool(campos), "filterChanges": bool(filtros)}


def _valor_por_tipo(objeto: str, prop: str, valor, tipo: dict, nome: str):
    """Codifica o valor pelo tipo declarado na capability (bool, numeric, fontSize, text, enumeration, cor)."""
    onde = f"{nome}: {objeto}.{prop}"
    if "bool" in tipo:
        if not isinstance(valor, bool):
            raise ErroDeclaracao(f"{onde} espera bool, veio {valor!r}")
        return lit(valor)
    if "numeric" in tipo or "integer" in tipo or tipo.get("formatting", {}).get("fontSize"):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ErroDeclaracao(f"{onde} espera número, veio {valor!r}")
        return lit(valor)
    if "text" in tipo:
        if not isinstance(valor, str):
            raise ErroDeclaracao(f"{onde} espera texto, veio {valor!r}")
        return lit(valor)
    if "enumeration" in tipo:
        validos = [e["value"] for e in tipo["enumeration"]]
        if valor not in validos:
            raise ErroDeclaracao(f"{onde} = {valor!r}; valores válidos: {validos}")
        return lit(valor)
    if tipo.get("fill", {}).get("solid", {}).get("color"):
        return cor(valor)
    raise ErroDeclaracao(f"{onde}: tipo {tipo} não é gravado por este construtor")


def _objeto_vizufilter(objeto: str, valores: dict, cap: dict, nome: str) -> list:
    props_cap = cap["objetos"].get(objeto)
    if props_cap is None:
        raise ErroDeclaracao(f"{nome}: objeto {objeto!r} não existe no VizuFilter {PACOTES['vizufilter']['versao']}")
    props = {}
    for prop, valor in valores.items():
        if prop not in props_cap:
            raise ErroDeclaracao(f"{nome}: {objeto}.{prop} não existe no VizuFilter "
                                 f"{PACOTES['vizufilter']['versao']} (existem: {sorted(props_cap)})")
        props[prop] = _valor_por_tipo(objeto, prop, valor, props_cap[prop].get("type", {}), nome)
    return [{"properties": props}]


def filtro_visual_categorico(nome: str, tabela: str, coluna: str, valores) -> dict:
    """filterConfig de visual: coluna IN valores (ex.: recortar o seletor às categorias de uma tela)."""
    valores = list(valores)
    if not valores:
        raise ErroDeclaracao(f"filtro {nome}: sem valores")
    return {"filters": [{
        "name": nome, "field": campo_coluna_expr(tabela, coluna), "type": "Categorical",
        "filter": {"Version": 2, "From": [{"Name": "t", "Entity": tabela, "Type": 0}],
                   "Where": [{"Condition": {"In": {
                       "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": coluna}}],
                       "Values": [[{"Literal": {"Value": literal_filtro(v)}}] for v in valores]}}}]}}]}


def filtro_visual_topn(nome: str, tabela: str, coluna: str, medida: str, n: int,
                       tabela_medida: str = TABELA_MEDIDAS) -> dict:
    """filterConfig de visual: Top N de `coluna` pela `medida` (decrescente), no formato que o Desktop grava (subconsulta
    com Top e OrderBy). O Top N é recalculado no contexto da página (segmentações e drawer)."""
    if n < 1:
        raise ErroDeclaracao(f"filtro {nome}: N = {n}")
    col = {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": coluna}}
    sub = {"Version": 2,
           "From": [{"Name": "d", "Entity": tabela, "Type": 0}, {"Name": "m", "Entity": tabela_medida, "Type": 0}],
           "Select": [dict(col, Name="field")],
           "OrderBy": [{"Direction": 2, "Expression": {"Measure": {
               "Expression": {"SourceRef": {"Source": "m"}}, "Property": medida}}}],
           "Top": int(n)}
    return {"filters": [{
        "name": nome, "field": campo_coluna_expr(tabela, coluna), "type": "TopN",
        "filter": {"Version": 2,
                   "From": [{"Name": "subquery", "Expression": {"Subquery": {"Query": sub}}, "Type": 2},
                            {"Name": "d", "Entity": tabela, "Type": 0}],
                   "Where": [{"Condition": {"In": {"Expressions": [col],
                                                   "Table": {"SourceRef": {"Source": "subquery"}}}}}]}}]}


# ----------------------------------------------------------------------------------------------------------------
# Segmentações nativas (receita da casa, D60/D68: "suspensa com cara de gatilho"; pedido do dono em 01/10 noite:
# filtros separados por categoria, com as personalizações do Power BI). A suspensa nativa abre a lista POR CIMA da
# página (visual personalizado não passa da própria caixa), por isso os campos do drawer são nativos.
# ----------------------------------------------------------------------------------------------------------------
FONTE_SEGMENTACAO = "'''Segoe UI'', wf_segoe-ui_normal, helvetica, arial, sans-serif'"


def _lit_int(n: int) -> dict:
    return {"expr": {"Literal": {"Value": f"{int(n)}L"}}}


def segmentacao(nome: str, x, y, w, h, *, tabela: str, coluna: str, rotulo: str, alt: str, grupo: str,
                modo: str = "Dropdown", unica: bool = False, pesquisa: bool = False, tokens: dict,
                corpo_pt: float = 13.5, padding_itens: int = 8, raio: int = 12, seta_visivel: bool = True,
                cabecalho: dict | None = None, z: int = CAMADAS["drawer"], tab: int | None = None,
                oculto: bool = False) -> dict:
    """Segmentação clássica (`slicer`) num campo só, sincronizada por `grupo` entre as páginas. `modo` = Dropdown
    (suspensa) ou Basic (lista). `tokens` = cores: fundo, texto, borda, seta, marca e (com pesquisa) pesquisa_fundo e
    pesquisa_borda. `seta_visivel=False` deixa a seta nativa transparente (a seta é a do desenho embaixo). `cabecalho`
    = {"texto": cor, "pt": tamanho} liga o cabeçalho com o rótulo do campo; sem ele o cabeçalho fica desligado."""
    if modo not in ("Dropdown", "Basic"):
        raise ErroDeclaracao(f"{nome}: modo {modo!r}")
    t = tokens
    itens = {"fontFamily": {"expr": {"Literal": {"Value": FONTE_SEGMENTACAO}}}, "textSize": lit(corpo_pt),
             "fontColor": cor(t["texto"]), "background": cor(t["fundo"]), "outlineStyle": lit(0),
             "padding": lit(padding_itens)}
    if cabecalho:
        cab = [{"properties": {"show": lit(True), "fontColor": cor(cabecalho["texto"]), "textSize": lit(cabecalho["pt"]),
                               "fontFamily": {"expr": {"Literal": {"Value": FONTE_SEGMENTACAO}}},
                               "outlineStyle": lit(0)}}]
    else:
        cab = [{"properties": {"show": lit(False)}}]
    objetos = {
        "data": [{"properties": {"mode": lit(modo)}}],
        "header": cab,
        # clássica: strictSingleSelect = "Seleção única"; singleSelect = "Seleção múltipla com CTRL" (desligado: caixas)
        "selection": [{"properties": {"strictSingleSelect": lit(unica), "singleSelect": lit(False),
                                      "selectAllCheckboxEnabled": lit(False)}}],
        "items": [{"properties": itens}],
        "selectionIcon": [{"properties": {"color": cor(t["marca"])}}],
        "general": [{"properties": {"responsive": lit(True),
                                    **({"selfFilterEnabled": lit(True)} if pesquisa else {})}}],
    }
    if modo == "Dropdown":
        objetos["dropdown"] = [{"properties": {
            "borderColor": cor(t["borda"]), "borderRadius": _lit_int(raio), "iconColor": cor(t["seta"]),
            "iconTransparency": lit(0 if seta_visivel else 100), "accentBarColor": cor(t["borda"]),
            "accentBarTransparency": lit(100)}}]
    if pesquisa:
        objetos["searchBox"] = [{"properties": {"background": cor(t["pesquisa_fundo"]),
                                                "borderColor": cor(t["pesquisa_borda"]), "outlineStyle": lit(4)}}]
    doc = _visual(nome, x, y, w, h, z=z, tab=tab, tipo="slicer", alt=alt,
                  query={"queryState": {"Values": {"projections": [
                      proj_coluna(tabela, coluna, rotulo=rotulo, ativa=True)]}}},
                  objetos=objetos, cruzar_filtro=True, oculto=oculto)
    doc["visual"]["visualContainerObjects"]["padding"] = [
        {"properties": {k: lit(2) for k in ("top", "bottom", "left", "right")}}]
    v = {}
    for k, val in doc["visual"].items():
        if k == "drillFilterOtherVisuals":
            v["syncGroup"] = grupo_sincronia(grupo)
        v[k] = val
    doc["visual"] = v
    return doc


_ESTADOS_SEG_BOTOES = ("default", "interaction:hover", "interaction:press", "selection:selected")


def segmentacao_botoes(nome: str, x, y, w, h, *, tabela: str, coluna: str, padrao, grupo: str,
                       linhas: int, colunas: int, cores: dict | None, alt: str, z: int, tab: int | None = None,
                       oculto: bool = False, raio: int = 8, corpo_pt: float = 10.5, forcar: bool = False,
                       espaco: int | None = None, fundo: dict | None = None, invisivel: bool = False,
                       marcado_semibold: bool = False) -> dict:
    """Segmentação de botões (advancedSlicerVisual), seleção única, syncGroup `grupo` (receita da casa).
    `cores` = fundo, fundo_hover, fundo_marcado, texto, texto_marcado. `padrao` = valor marcado de início.
    `forcar` = "Forçar seleção" (sem seleção, o 1º item fica marcado). `espaco` = px entre os botões. `fundo` =
    {"cor", "raio", "padding"}: trilho do seletor no contêiner do visual (fundo + borda arredondada). `invisivel` = camada
    de clique sem desenho (receita 7: o estado é desenhado por HTML embaixo). `marcado_semibold` = texto marcado em
    Segoe UI Semibold (600) em vez de negrito (700)."""
    def por_estado(props: dict) -> list:
        return [{"properties": p, "selector": {"id": e}} for e, p in props.items()]

    c = cores or {"fundo": "#FFFFFF", "fundo_hover": "#FFFFFF", "fundo_marcado": "#FFFFFF", "texto": "#FFFFFF",
                  "texto_marcado": "#FFFFFF"}
    layout = {"rowCount": _lit_int(linhas), "columnCount": _lit_int(colunas)}
    if espaco is not None:
        layout["cellPadding"] = _lit_int(espaco)
    objetos = {
        "layout": [{"properties": layout}],
        "shapeCustomRectangle": [{"properties": {"tileShape": lit("rectangleRoundedByPixel"),
                                                 "rectangleRoundedCurve": _lit_int(raio)},
                                  "selector": {"id": "default"}}],
        "fillCustom": por_estado({
            "default": {"show": lit(True), "fillColor": cor(c["fundo"]), "transparency": lit(0)},
            "interaction:hover": {"fillColor": cor(c["fundo_hover"]), "transparency": lit(0)},
            "interaction:press": {"fillColor": cor(c["fundo_hover"]), "transparency": lit(0)},
            "selection:selected": {"fillColor": cor(c["fundo_marcado"]), "transparency": lit(0)}}),
        "outline": por_estado({e: {"show": lit(False)} for e in _ESTADOS_SEG_BOTOES}),
        "accentBar": por_estado({e: {"show": lit(False)} for e in _ESTADOS_SEG_BOTOES}),
        "selectionIcon": [{"properties": {"show": lit(False)}}],
        "label": por_estado({e: {"show": lit(False)} for e in _ESTADOS_SEG_BOTOES}),
        "value": por_estado({
            "default": {"show": lit(True), "fontSize": lit(corpo_pt), "fontFamily": lit("Segoe UI"),
                        "fontColor": cor(c["texto"]), "horizontalAlignment": lit("center"),
                        "verticalAlignment": lit("middle")},
            "selection:selected": {"bold": lit(True), "fontColor": cor(c["texto_marcado"])}}),
        "selection": [{"properties": {"singleSelect": lit(True), "strictSingleSelect": lit(bool(forcar)),
                                      "selectAllCheckboxEnabled": lit(False)}}],
    }
    # margem interna mínima: com a margem padrão o texto desce e é cortado em botões baixos (36 px; T3, 03/10)
    # (objetos por estado: só valem com seletor; a entrada sem seletor é ignorada pelo botão)
    margem = {"paddingSelection": lit("Custom"), "leftMargin": _lit_int(4), "rightMargin": _lit_int(4),
              "topMargin": _lit_int(0), "bottomMargin": _lit_int(0)}
    objetos["padding"] = por_estado({e: dict(margem) for e in _ESTADOS_SEG_BOTOES})
    objetos["spacing"] = por_estado({e: {"verticalSpacing": _lit_int(0)} for e in _ESTADOS_SEG_BOTOES})
    if marcado_semibold:
        objetos["value"][-1]["properties"] = {"bold": lit(False), "fontColor": cor(c["texto_marcado"]),
                                              "fontFamily": lit("Segoe UI Semibold")}
    if invisivel:
        # nada pintado em estado nenhum: o desenho embaixo mostra o valor; o botão só recebe o clique
        objetos["fillCustom"] = por_estado({e: {"show": lit(False)} for e in _ESTADOS_SEG_BOTOES})
        objetos["value"] = [{"properties": {"show": lit(False), "transparency": lit(100), "fontSize": lit(8)}}] +             por_estado({e: {"show": lit(False), "transparency": lit(100), "fontSize": lit(8)} for e in _ESTADOS_SEG_BOTOES})
        objetos["shadowCustom"] = por_estado({e: {"show": lit(False)} for e in _ESTADOS_SEG_BOTOES})
        objetos["glowCustom"] = por_estado({e: {"show": lit(False)} for e in _ESTADOS_SEG_BOTOES})
    if padrao is not None:
        objetos["general"] = [{"properties": {"filter": {"filter": {
            "Version": 2, "From": [{"Name": "x", "Entity": tabela, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "x"}}, "Property": coluna}}],
                "Values": [[{"Literal": {"Value": literal_filtro(padrao)}}]]}}}]}}}}]
    doc = _visual(nome, x, y, w, h, z=z, tab=tab, tipo="advancedSlicerVisual", alt=alt,
                  query={"queryState": {"Values": {"projections": [proj_coluna(tabela, coluna, ativa=True)]}}},
                  objetos=objetos, cruzar_filtro=True, oculto=oculto)
    if fundo:
        vco = doc["visual"]["visualContainerObjects"]
        vco["background"] = [{"properties": {"show": lit(True), "color": cor(fundo["cor"]), "transparency": lit(0)}}]
        vco["border"] = [{"properties": {"show": lit(True), "color": cor(fundo["cor"]),
                                         "radius": lit(fundo.get("raio", 0))}}]
        pad = fundo.get("padding", 0)
        vco["padding"] = [{"properties": {k: lit(pad) for k in ("top", "bottom", "left", "right")}}]
    v = {}
    for k, val in doc["visual"].items():
        if k == "drillFilterOtherVisuals":
            v["syncGroup"] = grupo_sincronia(grupo)
        v[k] = val
    doc["visual"] = v
    return doc


def visual_vizufilter(nome: str, x, y, w, h, *, categoria: tuple, geral: dict, layout: dict, estilo: dict, alt,
                      z: int = CAMADAS["drawer"], tab: int | None = None, oculto: bool = False,
                      sincronia: dict | None = None, filtros: dict | None = None,
                      medidas: dict | None = None, extras: dict | None = None, regua: dict | None = None) -> dict:
    """VizuFilter num campo só (`categoria` = (tabela, coluna, rótulo); no modo caminho, dFiltro[Caminho]). `geral`,
    `layout` e `estilo` vão aos objetos general/layout/style, conferidos propriedade a propriedade e enum a enum contra
    as capabilities do pacote em PACOTES (objeto vazio = não gravado). `sincronia` = grupo_sincronia(...) grava
    `visual.syncGroup`. `regua` (2.13.0.0) = o cartão Régua (objeto regua: ativo, valorPadrao, cores, diâmetro…), o modo
    do botão arrastável sobre uma coluna numérica."""
    cap = capacidades("vizufilter")
    if "category" not in cap["papeis"]:
        raise ErroDeclaracao(f"{nome}: papel category ausente no VizuFilter")
    tabela, coluna, rotulo = categoria
    estado = {"category": {"projections": [proj_coluna(tabela, coluna, rotulo=rotulo, ativa=True)]}}
    # 2.10: papéis de medida opcionais (itemMarker, itemLabel, itemSort): {papel: nome da medida}
    for papel, medida in (medidas or {}).items():
        if papel not in cap["papeis"]:
            raise ErroDeclaracao(f"{nome}: papel {papel!r} ausente no VizuFilter {PACOTES['vizufilter']['versao']}")
        estado[papel] = {"projections": [proj_medida(medida)]}
    objetos = {objeto: _objeto_vizufilter(objeto, valores, cap, nome)
               for objeto, valores in (("general", geral), ("layout", layout), ("style", estilo)) if valores}
    if extras:
        objetos["itemExtras"] = _objeto_vizufilter("itemExtras", extras, cap, nome)
    if regua:
        objetos["regua"] = _objeto_vizufilter("regua", regua, cap, nome)
    doc = _visual(nome, x, y, w, h, z=z, tab=tab, tipo=GUID_VIZUFILTER, alt=alt, query={"queryState": estado},
                  objetos=objetos, cruzar_filtro=True, filtros=filtros, oculto=oculto)
    if sincronia is not None:
        if set(sincronia) != set(CHAVES_SINCRONIA):
            raise ErroDeclaracao(f"{nome}: sincronia {sincronia!r} — use grupo_sincronia()")
        v = {}
        for k, val in doc["visual"].items():
            if k == "drillFilterOtherVisuals":
                v["syncGroup"] = sincronia
            v[k] = val
        v.setdefault("syncGroup", sincronia)
        doc["visual"] = v
    return doc


# ----------------------------------------------------------------------------------------------------------------
# HTML Content Standalone 2.0
# ----------------------------------------------------------------------------------------------------------------
# Kit de movimento (pedido do Alisson, 20/10/2026: "números sem animação de contador, barras e linhas sem racing …
# precisamos deixar mais smooth as animações"): movimento.js, no fim do bodyTemplate de cada visual de conteúdo. Na
# entrada (1,5 s depois da 1ª renderização) os números de 20 px ou mais (sem ano, data nem ordinal) contam do zero e as barras usam o crescimento do
# CSS; nas renderizações seguintes (filtro, clique) os números contam do valor anterior, as barras deslizam do tamanho
# anterior (scale → 1, 0,7 s) e as entradas por opacidade não piscam de novo. O texto final é sempre o do DAX; sem JS,
# com erro ou com movimento reduzido, nada muda. Fora: alvos de clique, leituras, cabeçalho, casca e dicas.
# Tooltips (TT_…, pedido do Alisson, 23/10/2026: "animação dos elementos dos tooltips"): cada ponto sob o mouse é uma
# entrada — os filhos do cartão sobem em cascata curta (CSS_ENTRADA_TT, especificidade zero: quem já tem animação
# própria fica com a sua), as barras crescem de novo e os números contam do valor do ponto anterior (do zero no 1º).
RE_SEM_MOVIMENTO = re.compile(r"(_Alvos|_Leitura|Cab_Pergunta|_Casca_|_Dica\d|_Onde_Obras|_Abas$|^tt)")
CSS_ENTRADA_TT = (
    "@keyframes ttSobe{from{opacity:0;transform:translateY(10px)}}"
    ":where(.htmlViewerEntry>*>*){animation:ttSobe .42s cubic-bezier(.2,.7,.2,1) both}"
    + "".join(f":where(.htmlViewerEntry>*>:nth-child({i})){{animation-delay:{(i - 1) * 45}ms}}" for i in range(2, 15))
    + ":where(.htmlViewerEntry>*>:nth-child(n+15)){animation-delay:630ms}"
)
# Realce no hover (preferência do Alisson, 23/10/2026: "passar o mouse no elemento e ele fica destacado, em gráficos a
# barra em destaque se acende mais e as outras se apagam"): em todo visual com grão, a entrada sob o mouse fica inteira
# e as outras apagam (transição curta). Só opacidade: quem pega o mouse continua sendo o que cada visual declara (raiz
# sem ponteiro e alvos com ponteiro, L114). Devolver o ponteiro aos filhos da raiz foi testado e quebrou: contêineres e
# SVGs do tamanho do visual passaram a pegar o mouse e a última entrada roubava o clique e o tooltip das outras.
# Fora: os alvos transparentes sobre o desenho de outro visual (o realce deles é o anel que eles mesmos desenham).
RE_SEM_REALCE = re.compile(r"(Alvo|Alvos|_Mapa_Exterior|_Casca_|_Filtro_|_Botoes)")
CSS_REALCE = (
    ".htmlViewerEntry{transition:opacity .18s ease}"
    "#htmlContent:has(.htmlViewerEntry:hover) .htmlViewerEntry:not(:hover){opacity:.42}"
)
_SCRIPT_MOVIMENTO: str | None = None


def script_movimento(tooltip: bool = False) -> str:
    """O movimento.js numa tag; `tooltip` liga o modo de tooltip (window.__mvTT antes do kit)."""
    global _SCRIPT_MOVIMENTO
    if _SCRIPT_MOVIMENTO is None:
        js = "".join(l.strip() for l in (AQUI / "movimento.js").read_text(encoding="utf-8").splitlines())
        if "</script" in js.lower() or "//" in js.replace("://", ""):
            raise ErroDeclaracao("movimento.js: </script> ou comentário de linha (as linhas são juntadas)")
        _SCRIPT_MOVIMENTO = js
    return "<script>" + ("window.__mvTT=1;" if tooltip else "") + _SCRIPT_MOVIMENTO + "</script>"


def visual_html(nome: str, x, y, w, h, medida_conteudo: str, *, alt, z: int = CAMADAS["conteudo"],
                tab: int | None = None, granularidade: tuple | None = None, tooltips: Iterable[str] = (),
                filtro_cruzado: bool = False, transparencia_nao_selecionados: bool | None = None,
                tooltip_pagina: str | None = None, folha_de_estilo: str | None = None,
                ordenacao: Iterable[tuple] = (), oculto: bool = False, tabela: str = TABELA_MEDIDAS,
                sem_dados: str | None = " ", pagina_wh: tuple = (LARGURA, ALTURA), filtros: dict | None = None,
                modelo_corpo: str | None = None, movimento: bool | None = None,
                realce: bool | None = None) -> dict:
    """HTML Content Standalone 2.0 (`STANDALONEhtmlContent…6855`). Papel `content` = UMA medida HTML; `granularidade` =
    (tabela, coluna) no papel `sampling` (rótulo "Context" no 2.0). Sem granularidade o visual não cruza filtro nem abre
    tooltip de página (L011). Grava legacyRendering = false e renderMode = rebuild (ver docstring do módulo). Altura
    dentro do HTML: 100vh/100vw ou position:fixed, nunca height:100% (L037)."""
    tooltips = list(tooltips)
    ordenacao = list(ordenacao)
    if not isinstance(medida_conteudo, str) or not medida_conteudo.strip():
        raise ErroDeclaracao(f"{nome}: medida HTML obrigatória (papel content)")
    if (filtro_cruzado or tooltip_pagina) and not granularidade:
        raise ErroDeclaracao(f"{nome}: filtro cruzado / tooltip de página exigem granularidade (papel sampling)")
    estado: dict[str, Any] = {"content": {"projections": [proj_medida(medida_conteudo, tabela=tabela)]}}
    if granularidade:
        tab_g, col_g = granularidade
        estado["sampling"] = {"projections": [proj_coluna(tab_g, col_g)]}
    if tooltips:
        estado["tooltips"] = {"projections": [proj_medida(m, tabela=tabela) for m in tooltips]}
    query: dict[str, Any] = {"queryState": estado}
    if ordenacao:
        query["sortDefinition"] = {"sort": [{"field": f, "direction": d} for f, d in ordenacao]}
    formato = {"renderMode": lit("rebuild")}
    if sem_dados is not None:
        formato["noDataMessage"] = lit(sem_dados)
    objetos: dict[str, Any] = {"contentFormatting": [{"properties": formato}],
                               "compatibility": [{"properties": {"legacyRendering": lit(False)}}]}
    if filtro_cruzado:
        props = {"enabled": lit(True)}
        if transparencia_nao_selecionados is not None:
            props["useTransparency"] = lit(bool(transparencia_nao_selecionados))
        objetos["crossFilter"] = [{"properties": props}]
    if folha_de_estilo:
        objetos["stylesheet"] = [{"properties": {"stylesheet": expr_medida(folha_de_estilo, tabela)}}]
    # o kit de movimento (movimento.js, 20/10/2026): entra no fim do bodyTemplate, uma vez por visual; por padrão em
    # todo visual de conteúdo, fora das camadas de clique, leituras, cabeçalhos, casca e tooltips (movimento=None)
    if movimento is None:
        movimento = not RE_SEM_MOVIMENTO.search(nome)
    tooltip = nome.startswith("TT_")
    if realce is None:
        realce = bool(granularidade) and not RE_SEM_REALCE.search(nome)
    if realce:
        modelo_corpo = f"<style>{CSS_REALCE}</style>" + (modelo_corpo if modelo_corpo is not None else "{{content}}")
    if movimento:
        modelo_corpo = (modelo_corpo if modelo_corpo is not None else "{{content}}") + script_movimento(tooltip)
        if tooltip:
            modelo_corpo = f"<style>{CSS_ENTRADA_TT}</style>" + modelo_corpo
    if modelo_corpo is not None:
        # templates.bodyTemplate do 2.0: texto fixo do visual com {{content}} no lugar da medida (fora do limite de
        # 32.760 caracteres das medidas de texto, L048)
        if "{{content}}" not in modelo_corpo:
            raise ErroDeclaracao(f"{nome}: modelo_corpo sem o marcador {{{{content}}}}")
        objetos["templates"] = [{"properties": {"bodyTemplate": lit(modelo_corpo)}}]
    return _visual(nome, x, y, w, h, z=z, tab=tab, tipo=GUID_HTML, alt=alt, query=query, objetos=objetos,
                   tooltip_pagina=tooltip_pagina, cruzar_filtro=True if filtro_cruzado else None, oculto=oculto,
                   pagina_wh=pagina_wh, filtros=filtros)


# ----------------------------------------------------------------------------------------------------------------
# Deneb Standalone 2.0 (Vega puro — L026)
# ----------------------------------------------------------------------------------------------------------------
def campo_coluna(alias: str, tabela: str, coluna: str) -> tuple:
    return ("coluna", alias, tabela, coluna)


def campo_medida(alias: str, nome: str, tabela: str = TABELA_MEDIDAS) -> tuple:
    return ("medida", alias, tabela, nome)


def checar_spec_vega(texto: str, nome: str) -> dict:
    try:
        spec = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ErroDeclaracao(f"{nome}: spec Vega não é JSON válido ({e})") from None
    esquema = str(spec.get("$schema", ""))
    if "vega-lite" in esquema or not esquema.startswith("https://vega.github.io/schema/vega/v"):
        raise ErroDeclaracao(f"{nome}: $schema {esquema!r} — a casa usa Vega puro (L026)")
    dados = spec.get("data", []) or []
    for d in dados:
        if isinstance(d, dict) and "url" in d:
            raise ErroDeclaracao(f"{nome}: data '{d.get('name')}' com url — só o dataset interno do Deneb")
    if not any(isinstance(d, dict) and d.get("name") == "dataset" for d in dados):
        raise ErroDeclaracao(f"{nome}: spec sem data 'dataset' (o Deneb injeta os campos nesse nome)")
    return spec


def _texto_spec(spec, nome: str) -> str:
    if isinstance(spec, dict):
        texto = json.dumps(spec, ensure_ascii=False, indent=2)
    else:
        p = Path(spec)
        if not p.is_absolute():
            p = RAIZ / p
        if not p.is_file():
            raise ErroDeclaracao(f"{nome}: spec {p} não existe")
        texto = p.read_text(encoding="utf-8-sig").strip()
    checar_spec_vega(texto, nome)
    return texto


def visual_deneb(nome: str, x, y, w, h, spec, campos: Iterable[tuple], *, alt, z: int = CAMADAS["conteudo"],
                 tab: int | None = None, tooltips: bool = True, selecao: bool = False, max_selecao: int = 50,
                 menu_contexto: bool | None = None, tooltip_pagina: str | None = None, renderizacao: str = "svg",
                 oculto: bool = False, modo_selecao: str = "simple", pagina_wh: tuple = (LARGURA, ALTURA)) -> dict:
    """Deneb Standalone com provider Vega. `spec` = caminho relativo a pbi/ ou dict. `campos` = campo_coluna/campo_medida
    na ordem do papel dataset. `tooltip_pagina` liga a página de tooltip (o datum precisa manter __row__)."""
    texto = _texto_spec(spec, nome)
    projecoes, vistos, suporte = [], set(), {}
    for c in campos:
        if not (isinstance(c, tuple) and len(c) == 4 and c[0] in ("coluna", "medida")):
            raise ErroDeclaracao(f"{nome}: campo {c!r}")
        tipo, alias, tabela, campo = c
        if not RE_ALIAS.match(alias) or alias in vistos:
            raise ErroDeclaracao(f"{nome}: alias {alias!r} inválido ou repetido")
        vistos.add(alias)
        if tipo == "coluna":
            projecoes.append(proj_coluna(tabela, campo, alias=alias, rotulo=alias))
        else:
            projecoes.append(proj_medida(campo, tabela=tabela, alias=alias, rotulo=alias))
        suporte[alias] = {"highlight": False, "highlightStatus": False, "highlightComparator": False,
                          "format": tipo == "medida", "formatted": tipo == "medida", "names": False}
    if not projecoes:
        raise ErroDeclaracao(f"{nome}: Deneb sem campos")
    vega: dict[str, Any] = {
        "jsonSpec": lit(texto), "jsonConfig": lit("{}"), "provider": lit("vega"), "version": lit(DENEB["vega"]),
        "renderMode": lit(renderizacao), "enableTooltips": lit(bool(tooltips)),
    }
    if menu_contexto is not None:
        vega["enableContextMenu"] = lit(bool(menu_contexto))
    vega["enableSelection"] = lit(bool(selecao))
    vega["selectionMode"] = lit(modo_selecao)
    vega["selectionMaxDataPoints"] = lit(max_selecao)
    objetos = {
        "vega": [{"properties": vega}],
        "stateManagement": [{"properties": {"viewportHeight": lit(h), "viewportWidth": lit(w),
            "supportFieldConfiguration": lit(json.dumps(suporte, ensure_ascii=False, separators=(",", ":"))),
            "denebMetaVersion": lit("2"), "consolidateFieldParameters": lit(False)}}],
        "developer": [{"properties": {"version": lit(DENEB["desenvolvedor"])}}],
    }
    visual = _visual(nome, x, y, w, h, z=z, tab=tab, tipo=GUID_DENEB, alt=alt,
                     query={"queryState": {"dataset": {"projections": projecoes}}}, objetos=objetos,
                     tooltip_pagina=tooltip_pagina, cruzar_filtro=True if selecao else None, oculto=oculto,
                     pagina_wh=pagina_wh)
    visual["$schema"] = ESQUEMA["visual_deneb"]
    return visual


# ----------------------------------------------------------------------------------------------------------------
# Bookmarks e páginas
# ----------------------------------------------------------------------------------------------------------------
def bookmark_exibicao(nome: str, pagina: str, visibilidade: dict, *, titulo: str | None = None) -> dict:
    """Bookmark só de exibição (applyOnlyToTargetVisuals + suppressData + suppressActiveSection): alterna a
    visibilidade de {visual: True (mostra) | False (oculta)} sem tocar filtro, página ou dado."""
    if not RE_BOOKMARK.match(nome) or not nome.startswith(pagina + "_"):
        raise ErroDeclaracao(f"bookmark {nome!r}: padrão <TELA>_<ASSUNTO>_<NN> da própria página ({pagina})")
    if not visibilidade:
        raise ErroDeclaracao(f"bookmark {nome!r} sem alvos")
    for v, mostra in visibilidade.items():
        checar_nome_visual(v)
        if not isinstance(mostra, bool):
            raise ErroDeclaracao(f"bookmark {nome!r}: {v} → {mostra!r}")
    vis = dict(sorted(visibilidade.items()))
    return {"$schema": ESQUEMA["bookmark"], "name": nome, "displayName": titulo or nome,
            "options": {"applyOnlyToTargetVisuals": True, "targetVisualNames": list(vis), "suppressActiveSection": True,
                        "suppressData": True},
            "explorationState": {"version": "1.0", "activeSection": pagina, "sections": {pagina: {"visualContainers": {
                v: {"singleVisual": {} if m else {"display": {"mode": "hidden"}}} for v, m in vis.items()}}}}}


def bookmark_chegada(nome: str, pagina: str, visibilidade: dict, *, titulo: str) -> dict:
    """Marcador de chegada (L095): Página atual + Exibição, sem Dados (applyOnlyToTargetVisuals + suppressData). Leva à
    `pagina` e deixa {visual: True (mostra) | False (oculta)}, sem tocar em filtro nem dado. Toda navegação entre
    páginas passa por um destes: a página de destino chega sempre no estado declarado (gaveta aberta ou fechada),
    nunca no que a sessão deixou nela."""
    if not RE_BOOKMARK.match(nome) or not nome.startswith(pagina + "_"):
        raise ErroDeclaracao(f"bookmark {nome!r}: padrão <TELA>_<ASSUNTO>_<NN> da página de destino ({pagina})")
    if not visibilidade:
        raise ErroDeclaracao(f"bookmark {nome!r} sem alvos")
    for v, mostra in visibilidade.items():
        checar_nome_visual(v)
        if not isinstance(mostra, bool):
            raise ErroDeclaracao(f"bookmark {nome!r}: {v} → {mostra!r}")
    vis = dict(sorted(visibilidade.items()))
    return {"$schema": ESQUEMA["bookmark"], "name": nome, "displayName": titulo,
            "options": {"applyOnlyToTargetVisuals": True, "targetVisualNames": list(vis), "suppressData": True},
            "explorationState": {"version": "1.0", "activeSection": pagina, "sections": {pagina: {"visualContainers": {
                v: {"singleVisual": {} if m else {"display": {"mode": "hidden"}}} for v, m in vis.items()}}}}}


def filtro_in(tabela: str, coluna: str, valores) -> dict:
    """Filtro 'coluna IN valores' no formato que a segmentação grava em general.filter (e o bookmark em merge)."""
    return {"Version": 2, "From": [{"Name": "x", "Entity": tabela, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "x"}}, "Property": coluna}}],
                "Values": [[{"Literal": {"Value": literal_filtro(v)}}] for v in valores]}}}]}


def bookmark_selecao(nome: str, pagina: str, segmentacao: tuple, mostrar: Iterable[str], *, titulo: str,
                     tipo_segmentacao: str = "advancedSlicerVisual") -> dict:
    """Bookmark de Dados + Página atual + Exibição, aplicado só aos visuais-alvo: leva à `pagina`, marca na
    segmentação oculta `segmentacao` = (visual, tabela, coluna, valor) e deixa visíveis os visuais de `mostrar` (a gaveta
    segue aberta na página nova). Os outros filtros (empreendimento, mês) não são tocados."""
    if not RE_BOOKMARK.match(nome):
        raise ErroDeclaracao(f"bookmark {nome!r} fora do padrão")
    visual, tabela, coluna, valor = segmentacao
    checar_nome_visual(visual)
    mostrar = sorted(set(mostrar))
    for v in mostrar:
        checar_nome_visual(v)
    conteudo = {visual: {"singleVisual": {"visualType": tipo_segmentacao, "objects": {"merge": {"general": [
        {"properties": {"filter": {"filter": filtro_in(tabela, coluna, [valor])}}}]}}, "display": {"mode": "hidden"}}}}
    for v in mostrar:
        conteudo[v] = {"singleVisual": {}}
    return {"$schema": ESQUEMA["bookmark"], "name": nome, "displayName": titulo,
            "options": {"applyOnlyToTargetVisuals": True, "targetVisualNames": sorted(conteudo)},
            "explorationState": {"version": "1.0", "activeSection": pagina,
                                 "sections": {pagina: {"visualContainers": dict(sorted(conteudo.items()))}}}}


def pagina_relatorio(nome: str, titulo: str, fundo_cor: str, papel_de_parede: str) -> dict:
    """Página 1920×1080 FitToPage; fundo = papel de parede registrado (Fit) sobre a cor da página; outspace idem."""
    fundo = {"color": cor(fundo_cor), "transparency": lit(0),
             "image": {"image": {"name": lit(papel_de_parede), "url": expr_recurso(papel_de_parede),
                                 "scaling": lit("Fit")}}}
    return {"$schema": ESQUEMA["pagina"], "name": nome, "displayName": titulo, "displayOption": "FitToPage",
            "width": LARGURA, "height": ALTURA,
            "objects": {"background": [{"properties": fundo}],
                        "outspace": [{"properties": {"color": cor(fundo_cor), "transparency": lit(0)}}]}}


def pagina_tooltip(nome: str, titulo: str, *, altura: int, largura: int, cor_fundo: str = "#FFFFFF") -> dict:
    """Página de tooltip (Tooltip, HiddenInViewMode, ActualSize, pageBinding Tooltip, fundo branco). Nome tt<TELA>…"""
    if not RE_TOOLTIP.match(nome or ""):
        raise ErroDeclaracao(f"página de tooltip {nome!r} fora do padrão tt<TELA><Assunto>")
    if largura < TOOLTIP_LARGURA_MINIMA:
        raise ErroDeclaracao(f"{nome}: largura {largura} < {TOOLTIP_LARGURA_MINIMA}")
    fundo = [{"properties": {"color": cor(cor_fundo), "transparency": lit(0)}}]
    return {"$schema": ESQUEMA["pagina"], "name": nome, "displayName": titulo, "displayOption": "ActualSize",
            "width": largura, "height": altura, "type": "Tooltip", "visibility": "HiddenInViewMode",
            "pageBinding": {"name": nome, "type": "Tooltip", "parameters": []},
            "objects": {"background": fundo, "outspace": [{"properties": {"color": cor(cor_fundo), "transparency": lit(0)}}]}}


# ----------------------------------------------------------------------------------------------------------------
# Pacotes de visual privado (CustomVisuals/<GUID>/)
# ----------------------------------------------------------------------------------------------------------------
def arquivos_pacote(chave: str) -> dict[str, bytes]:
    """{caminho relativo a CustomVisuals/<GUID>: bytes} do .pbiviz, conferido: tamanho, SHA-256, entradas, GUID,
    versão e ausência de externalJS."""
    cfg = PACOTES[chave]
    arq = RAIZ / cfg["arquivo"]
    if not arq.is_file():
        raise ErroDeclaracao(f"pacote {chave}: {arq} não existe")
    blob = arq.read_bytes()
    if len(blob) != cfg["tamanho"]:
        raise ErroDeclaracao(f"pacote {chave}: tamanho {len(blob)} ≠ {cfg['tamanho']}")
    sha = hashlib.sha256(blob).hexdigest()
    if sha != cfg["sha256"]:
        raise ErroDeclaracao(f"pacote {chave}: SHA-256 {sha} ≠ {cfg['sha256']}")
    saida: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in sorted(z.namelist()):
            if n.endswith("/"):
                continue
            if n.startswith("/") or ".." in Path(n).parts:
                raise ErroDeclaracao(f"pacote {chave}: entrada suspeita {n!r}")
            saida[n] = z.read(n)
    guid = cfg["guid"]
    esperado = {"package.json", f"resources/{guid}.pbiviz.json"}
    if set(saida) != esperado:
        raise ErroDeclaracao(f"pacote {chave}: entradas {sorted(saida)} ≠ {sorted(esperado)}")
    pacote = json.loads(saida["package.json"].decode("utf-8-sig"))
    if pacote.get("visual", {}).get("guid") != guid or pacote.get("version") != cfg["versao"]:
        raise ErroDeclaracao(f"pacote {chave}: {pacote.get('visual', {}).get('guid')} {pacote.get('version')}")
    recurso = json.loads(saida[f"resources/{guid}.pbiviz.json"].decode("utf-8-sig"))
    if recurso.get("externalJS"):
        raise ErroDeclaracao(f"pacote {chave}: externalJS (dependência remota) — recusado")
    return saida


def capacidades(chave: str) -> dict:
    guid = PACOTES[chave]["guid"]
    d = json.loads(arquivos_pacote(chave)[f"resources/{guid}.pbiviz.json"].decode("utf-8-sig"))
    cap = d["capabilities"]
    return {"papeis": {r["name"]: r.get("kind") for r in cap.get("dataRoles", [])},
            "objetos": {o: v.get("properties", {}) for o, v in cap.get("objects", {}).items()}}


def serializar(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

# ----------------------------------------------------------------------------------------------------------------
# Declarações (o montar_pbip consolida; os módulos de pbi/scripts/paginas devolvem listas destas)
# ----------------------------------------------------------------------------------------------------------------
@dataclass
class Pagina:
    doc: dict
    ordem: int = 100


@dataclass
class Visual:
    pagina: str
    doc: dict


@dataclass
class Bookmark:
    doc: dict
    grupo: tuple | None = None          # (nome, displayName) do grupo em bookmarks.json


@dataclass
class Recurso:
    nome: str                          # nome registrado (ASCII), usado em expr_recurso
    origem: Path                       # arquivo no projeto


TIPOS_INTERACAO = ("Default", "DataFilter", "HighlightFilter", "NoFilter")


@dataclass
class Interacao:
    """Exceção à interação padrão de uma página (page.json → visualInteractions). Direcional: a seleção feita em
    `origem` deixa de chegar a `alvo` (NoFilter) ou chega com outro tipo. Declare só as exceções (19/10/2026, crítica B
    I1: sem isto, o clique nas fachadas da T02, nas tiras da T06 e na lista da T09 filtrava também o VizuFilter, os
    rótulos e as tiras ocultas)."""
    pagina: str
    origem: str                        # nome do visual que emite a seleção
    alvo: str                          # nome do visual que recebe (ou não) o filtro
    tipo: str = "NoFilter"
