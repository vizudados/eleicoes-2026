# -*- coding: utf-8 -*-
"""desenho_t01_t06_comum — peças comuns dos geradores das telas 01 a 06 (dono: agente das telas 01–06).

Os geradores (desenho_t01.py, desenho_t02_t04.py, desenho_t03_t05.py, desenho_t06.py) escrevem um arquivo .dax por
medida em pbi/dax/<TNN Nome>/{Contas,Desenho}/ e apagam os .dax que deixaram de existir nessas pastas (só nelas).

Ajudantes de texto DAX que se repetem no desenho (só formatam valor já lido, nunca calculam):
  num_humano(v)   56104503 → "56,10 mi" · 123456 → "123,5 mil" · 950 → "950"
  pct(v)          0.4516 → "45,2%"
  pp(v)           -3.27 → "−3,3" (pontos percentuais com sinal tipográfico)
  esc(v)          escapa & < > " ' para HTML
  css(v)          número para CSS/SVG em en-US ("0.0##", L106)
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PBI = AQUI.parent
RAIZ = PBI.parent
DAX = PBI / "dax"
sys.path.insert(0, str(AQUI))

URL_MIDIA = "https://vizudados.github.io/eleicoes-2026/midia"


class Gravador:
    """Grava as medidas de uma tela e, no fim, apaga os .dax órfãos da pasta da tela."""

    def __init__(self, pasta_tela: str):
        self.pasta_tela = pasta_tela            # ex.: "T01 Placar"
        self.raiz = DAX / pasta_tela
        self.gravados: set[Path] = set()

    def medida(self, nome: str, tipo: str, descricao: str, expressao: str, formato: str = "texto",
               oraculo: str | None = None) -> Path:
        """tipo = "Contas" ou "Desenho"."""
        if not nome.startswith(self.pasta_tela[:3] + " · "):
            raise ValueError(f"{nome}: toda medida da tela começa por '{self.pasta_tela[:3]} · '")
        if "\t" in expressao:
            raise ValueError(f"{nome}: tab na expressão")
        if expressao.strip("\n")[:1].isspace():
            raise ValueError(f"{nome}: a 1ª linha da expressão não pode ser recuada (quebra o TMDL)")
        destino = self.raiz / tipo / f"{nome}.dax"
        destino.parent.mkdir(parents=True, exist_ok=True)
        cab = [f"@pasta: {self.pasta_tela}\\{tipo}", f"@formato: {formato}", f"@descricao: {descricao}"]
        if oraculo:
            cab.append(f"@oraculo: {oraculo}")
        texto = "/*\n" + "\n".join(cab) + "\n*/\n" + expressao.strip("\n") + "\n"
        if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
            destino.write_text(texto, encoding="utf-8", newline="\n")
        self.gravados.add(destino.resolve())
        return destino

    def conta(self, nome, descricao, expressao, formato="#,0", oraculo=None):
        return self.medida(nome, "Contas", descricao, expressao, formato, oraculo)

    def desenho(self, nome, descricao, expressao):
        return self.medida(nome, "Desenho", descricao, expressao, "texto")

    def limpar(self) -> list[Path]:
        apagados = []
        if self.raiz.is_dir():
            for p in self.raiz.rglob("*.dax"):
                if p.resolve() not in self.gravados:
                    p.unlink()
                    apagados.append(p)
        return apagados

    def resumo(self) -> str:
        return f"{self.pasta_tela}: {len(self.gravados)} medidas"


# ---------------------------------------------------------------------------------------------------- texto DAX
def num_humano(v: str) -> str:
    """Expressão DAX: número de votos/pessoas para o leitor (mi com 2 casas, mil com 1, inteiro abaixo de mil)."""
    return (f'SWITCH ( TRUE (), ABS ( {v} ) >= 1000000, FORMAT ( {v} / 1000000, "0.00" ) & " mi", '
            f'ABS ( {v} ) >= 1000, FORMAT ( {v} / 1000, "0.0" ) & " mil", FORMAT ( {v}, "#,0" ) )')


def num_humano1(v: str) -> str:
    """Como num_humano, com uma casa nos milhões (33.469.244 → "33,5 mi"), para totais de pessoas."""
    return (f'SWITCH ( TRUE (), ABS ( {v} ) >= 1000000, FORMAT ( {v} / 1000000, "0.0" ) & " mi", '
            f'ABS ( {v} ) >= 1000, FORMAT ( {v} / 1000, "0.0" ) & " mil", FORMAT ( {v}, "#,0" ) )')


def num_humano_sinal(v: str) -> str:
    """Como num_humano, com + ou − (sinal tipográfico)."""
    return f'IF ( {v} < 0, "−", "+" ) & {num_humano(f"ABS ( {v} )")}'


def pct(v: str, casas: int = 1) -> str:
    fmt = "0." + "0" * casas + "%" if casas else "0%"
    return f'FORMAT ( {v}, "{fmt}" )'


def pp(v: str) -> str:
    """Pontos percentuais com sinal (+3,3 / −3,3 / 0,0)."""
    return f'FORMAT ( {v}, "+0.0;−0.0;0.0" )'


def inteiro(v: str) -> str:
    return f'FORMAT ( {v}, "#,0" )'


def esc(v: str) -> str:
    return (f'SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {v}, "&", "&amp;" ), "<", "&lt;" ), '
            f'">", "&gt;" ), """", "&quot;" ), "\'", "&#39;" )')


def css(v: str) -> str:
    return f'FORMAT ( {v}, "0.0##", "en-US" )'


def plural(n: str, um: str, varios: str) -> str:
    return f'IF ( {n} = 1, "{um}", "{varios}" )'


def bloco(linhas: list[str], recuo: int = 4) -> str:
    return "\n".join(" " * recuo + l if l else "" for l in linhas)


# Macros do texto DAX escrito nos geradores: @MI(x)@, @MIS(x)@, @PCT(x)@, @PCT0(x)@, @PP(x)@, @INT(x)@, @ESC(x)@,
# @CSS(x)@ viram as expressões acima (o argumento pode ter parênteses aninhados).
_MACROS = {"MI": num_humano, "MI1": num_humano1, "MIS": num_humano_sinal, "PCT": pct, "PCT0": lambda v: pct(v, 0), "PP": pp,
           "INT": inteiro, "ESC": esc, "CSS": css}


def expandir(texto: str) -> str:
    saida, i = [], 0
    while True:
        j = texto.find("@", i)
        if j < 0:
            saida.append(texto[i:])
            return "".join(saida)
        k = texto.find("(", j)
        nome = texto[j + 1:k] if k > j else ""
        if k < 0 or nome not in _MACROS:
            saida.append(texto[i:j + 1])
            i = j + 1
            continue
        nivel, m = 0, k
        while m < len(texto):
            if texto[m] == "(":
                nivel += 1
            elif texto[m] == ")":
                nivel -= 1
                if nivel == 0:
                    break
            m += 1
        if m + 1 >= len(texto) or texto[m + 1] != "@":
            raise ValueError(f"macro @{nome}( sem fecho ')@' perto de: {texto[j:j + 60]!r}")
        arg = expandir(texto[k + 1:m])
        saida.append(texto[i:j])
        saida.append(_MACROS[nome](arg.strip()))
        i = m + 2


def dax(texto: str) -> str:
    """Tira a indentação comum do bloco (textwrap.dedent) e expande as macros."""
    import textwrap
    saida = expandir(textwrap.dedent(texto).strip("\n"))
    if saida[:1].isspace():           # a 1ª linha recuada quebra o TMDL gerado (main, 23/10/2026 02:10)
        raise ValueError(f"expressão com a 1ª linha recuada: {saida[:60]!r}")
    return saida
