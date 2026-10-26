"""Contrato único do Antes/Depois: seleção, posição, sincronia e leitura de fontes.

O filtro fica em (952,60), 314×208, sempre atrás do conteúdo; o filtro já existente fica em (1282,60).
As medidas não trocam o grão, preservando UF, município, sort e tooltip.
"""
from __future__ import annotations
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

PRE = 'Pré Eleições 2026'
POS = 'Pós Eleições 2026'
CAIXA = (952, 60, 314, 208)
GRUPO = 'Eleicoes2026Momento'
TELAS = {'T02', 'T04', 'T03', 'T05', 'T01', 'T11', 'T12', 'T13'}


def fonte(t):
    if t.codigo in {'T01', 'T03', 'T05', 'T11', 'T12', 'T13'}:
        return 'Fontes: TSE e IBGE · 1º turno (04/10) e 2º turno (25/10/2026)'
    if t.codigo in {'T02', 'T04'}:
        return t.fonte.replace(' · fotos', ' · 2º turno de 25/10/2026 · fotos')
    return t.fonte


def segundo(expressao_pre: str, expressao_pos: str) -> str:
    return f'IF ( [Eleição · pós] = 1, {expressao_pos}, {expressao_pre} )'


def municipal_2022_2026(expr: str) -> str:
    """Somente fatos com ano explícito 2022/2026. Séries históricas nunca viram séries incompletas."""
    import re
    fonte = "'Município ano'"
    if fonte in expr and re.search(r"'Município ano'\[Ano\]\s*=\s*(?:2022|2026)\b", expr):
        return segundo(expr, expr.replace(fonte, "'Município segundo turno'"))
    return expr


def soma_municipal(coluna: str, ano: int = 2026) -> str:
    def soma(t):
        return f"CALCULATE ( SUM ( '{t}'[{coluna}] ), '{t}'[Ano] = {ano} )"
    return segundo(soma('Município ano'), soma('Município segundo turno'))


def soma_uf(coluna: str, ano: int = 2026, *, remover_uf=False) -> str:
    extra = "REMOVEFILTERS ( 'UF' ), " if remover_uf else ''
    return f"CALCULATE ( SUM ( 'UF segundo turno'[{coluna}] ), {extra}'UF segundo turno'[Ano] = {ano} )"


def filtro(t):
    import pbip_lib as lib
    from paginas import casca
    geral = dict(mode='dropdown', singleSelect=True, singleSelectAllowAll=False, sortAscending=True,
                 startOpen=False, alwaysOpen=False, showSearch=False, showSelectAll=False, showReset=False,
                 showSelectedCount=False, showSelectedValue=True, selectedValueOnly=True, syncSelectionWithHost=True,
                 triggerMode='value', triggerLabel='Eleição 2026', placeholderText=POS,
                 defaultSelection='value', defaultValue=POS, pathMode=False)
    return lib.Visual(t.codigo, lib.visual_vizufilter(
        f'{t.codigo}_Filtro_Momento', *CAIXA, categoria=('Momento eleição', 'Momento', 'Eleição 2026'),
        geral=geral, layout=casca.layout_filtro(CAIXA), estilo=casca._estilo_filtro(t),
        sincronia=lib.grupo_sincronia(GRUPO), medidas={'itemSort': 'Eleição · ordem'},
        alt=lib.medida('Eleição · Filtro · ALT'), z=lib.CAMADAS['filtro'], tab=3))


def gerar_medidas():
    from desenho_t01_t06_comum import PBI
    pasta = PBI / 'dax/_Momento eleição'
    contas = {
        'Eleição · pós': ('0', 'Sem seleção, ou seleção múltipla, assume Pós.',
                         f'INT ( SELECTEDVALUE ( \'Momento eleição\'[Momento], "{POS}" ) <> "{PRE}" )'),
        'Eleição · turno': ('0', 'Turno correspondente à escolha.', 'IF ( [Eleição · pós] = 1, 2, 1 )'),
        'Eleição · ordem': ('0', 'Ordem do item do filtro.', "SELECTEDVALUE ( 'Momento eleição'[Ordem] )"),
        'Eleição · Filtro · ALT': ('texto', 'Texto acessível da escolha e seu efeito.',
            f'IF ( [Eleição · pós] = 1, "{POS}: resultado do segundo turno de 25/10/2026.", '
            f'"{PRE}: primeiro turno e trajetória até a disputa do segundo turno." )'),
        'Eleição · Exterior · HTML': ('texto', 'Exterior no mesmo turno da tela; Pós usa totalização final por país.',
            'IF ( [Eleição · pós] = 1, [Exterior · ao vivo · HTML], [Exterior · 1º turno · HTML] )'),
        'Eleição · Exterior · ALT': ('texto', 'Texto acessível do exterior no turno escolhido.',
            'IF ( [Eleição · pós] = 1, [Exterior · ao vivo · ALT], [Exterior · 1º turno · ALT] )'),
    }
    for nome, (fmt, desc, expr) in contas.items():
        sub = 'Desenho' if nome.endswith((' · HTML', ' · ALT')) else 'Contas'
        arq = pasta / sub / (nome + '.dax')
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(f'/*\n@pasta: _Momento eleição\\{sub}\n@formato: {fmt}\n@descricao: {desc}\n*/\n{expr}\n', encoding='utf-8')


if __name__ == '__main__':
    gerar_medidas()
