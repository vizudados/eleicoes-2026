"""Encerramento dos dois turnos. Reutiliza as contas nacionais da capa e a geometria da própria página."""
from pathlib import Path
import roteiro
from paginas.t23_encerramento import GRUPOS
from validar_dax_gerado import problemas

PASTA = Path(__file__).resolve().parents[1] / 'dax/T23 Encerramento'


def gravar(nome, expr, desc, fmt='texto', conta=False):
    erros = problemas(expr, comentario_inline=True)
    if erros:
        raise ValueError('; '.join(erros))
    sub = 'Contas' if conta else 'Desenho'
    (PASTA / sub).mkdir(parents=True, exist_ok=True)
    (PASTA / sub / f'T23 · {nome}.dax').write_text(
        f'/*\n@pasta: T23 Encerramento\\{sub}\n@formato: {fmt}\n@descricao: {desc}\n'
        '@oraculo: TSE nacional 2026 com exterior; dados/pbi/pt_historico_brasil.csv\n'
        '@gerado: pbi/scripts/desenho_t23.py\n*/\n'+expr.strip()+'\n', encoding='utf-8')


def main():
    for turno in [1, 2]:
        for nome, coluna in [('comparecimento', 'Comparecimento'), ('aptos', 'Aptos')]:
            if turno == 2 and nome == 'aptos':
                continue
            gravar(f'{nome} {turno}º turno', f'''CALCULATE ( SUM ( 'PT histórico Brasil'[{coluna}] ),
    REMOVEFILTERS ( 'PT histórico Brasil' ),
    'PT histórico Brasil'[Ano] = 2026, 'PT histórico Brasil'[Turno] = {turno} )''',
                'Total nacional do turno com exterior; mesma cobertura nos dois turnos.', '#,0', True)
        if turno == 1:
            expr = '''VAR _aptos = [T23 · aptos 1º turno]
RETURN IF ( _aptos > 0, 1 - DIVIDE ( [T23 · comparecimento 1º turno], _aptos ) )'''
            descricao = 'Abstenção nacional do primeiro turno antes do arredondamento; um menos comparecimento sobre aptos.'
        else:
            expr = "CALCULATE ( [Apuração · abstenção %], REMOVEFILTERS ( 'UF' ) )"
            descricao = 'Taxa final nacional do TSE, mesma conta da T18: abstenção sobre comparecimento mais abstenção nas seções instaladas, com exterior.'
        gravar(f'abstenção {turno}º turno', expr, descricao, '0.00%', True)
    gravar('comparecimento a mais', '[T23 · comparecimento 2º turno] - [T23 · comparecimento 1º turno]',
        'Variação líquida do comparecimento nacional entre turnos, com exterior; não identifica os mesmos eleitores.', '#,0', True)
    gravar('diferença final', 'ABS ( [T00 · 2º turno · Lula votos] - [T00 · 2º turno · Flávio votos] )',
        'Diferença final entre as duas candidaturas, votos nacionais com exterior.', '#,0', True)
    blocos = ['[T23 · Resumo · HTML]']
    for cand, pos, cls in [('Flávio', 'esq', 'flavio'), ('Lula', 'dir', 'lula')]:
        nome = 'FLÁVIO BOLSONARO · PL' if cand == 'Flávio' else 'LULA · PT'
        selo = "<span class='selo-eleito' aria-label='Lula eleito'>eleito</span>" if cand == 'Lula' else ''
        blocos.append(f'''"<div class='bl {pos} sobe d3'><div class='rot'>{nome}</div><div class='rot etapa'>2º TURNO · RESULTADO FINAL</div>"
    & "<div class='num v {cls}-c'>" & FORMAT ( [T00 · 2º turno · {cand} votos] / 1e6, "0.00" )
    & " mi</div><div class='p'>" & FORMAT ( [T00 · 2º turno · {cand} %], "0.00%" ) & " dos válidos</div>"
    & "<div class='primeiro'>1º turno · <span class='num'>" & FORMAT ( [T00 · {cand} votos] / 1e6, "0.00" )
    & " mi</span> · " & FORMAT ( [T00 · {cand} %], "0.00%" ) & "</div>{selo}</div>"''')
    textos = {
        'T10': '''FORMAT ( [T10 · institutos · Lula à frente], "0" ) & " de " & FORMAT ( [T10 · institutos], "0" )
            & " institutos davam Lula à frente; a urna deu Flávio."''',
        'T01': '''"Flávio terminou o 1º turno com " & FORMAT ( [T06 · diferença Flávio Lula] / 1e6, "0.00" ) & " mi de votos de vantagem."''',
        'T06': '''"A ausência foi " & FORMAT ( [T06 · vezes a diferença em 2026], "0" ) & " vezes a diferença entre os dois no 1º turno."''',
        # O clique leva à tela 09, que abre em "Pós Eleições 2026" (o 2º turno): o achado conta o mesmo recorte, fixo,
        # para não depender do padrão do filtro (26/10/2026: dizia "1º turno" com o número do 2º, 278; no 1º foram 711).
        'T11': '''FORMAT ( CALCULATE ( [T11 · viraram], 'Momento eleição'[Momento] = "Pós Eleições 2026" ), "#,0" )
            & " municípios trocaram Lula por Flávio do 2º turno de 2022 para o de 2026."''',
        'T13': '''"Nas cidades pequenas e de renda mais alta, Lula perdeu mais terreno no 1º turno."''',
        'T19': '''FORMAT ( [T00 · municípios no mapa], "#,0" ) & " municípios para explorar o voto."''',
        'T17': '''"Flávio liderava " & FORMAT ( [T17 · depois · Flávio à frente], "0" ) & " de "
            & FORMAT ( [T17 · depois · pesquisas], "0" ) & " pesquisas; a urna deu Lula."''',
        'T18': '''"Lula foi eleito por " & FORMAT ( [Apuração · diferença], "#,0" )
            & " votos; voltou à frente às " & SUBSTITUTE ( FORMAT ( [T18 · noite · Lula retomou a frente], "HH:mm" ), ":", "h" ) & "."''',
        'T27': '''"Entre os turnos, Lula ganhou " & FORMAT ( [T23 · Lula ganhou entre turnos] / 1e6, "0.00" )
            & " mi de votos; Flávio, " & FORMAT ( [T23 · Flávio ganhou entre turnos] / 1e6, "0.00" ) & " mi."''',
        'T28': '''FORMAT ( [T23 · municípios Flávio para Lula], "#,0" ) & " municípios trocaram Flávio por Lula; Minas foi o único estado a virar."''',
        'T29': '''"Lula chegou ao recorde de " & FORMAT ( [T29 · recorde] / 1e6, "0.00" ) & " mi de votos, "
            & FORMAT ( [T29 · acima do recorde anterior] / 1e6, "0.00" ) & " mi acima de 2022."''',
    }
    for titulo, x, y, w, h, itens in GRUPOS:
        blocos.append(f'''"<div class='grupo' style='left:{x}px;top:{y}px;width:{w}px'>{titulo}</div>"''')
        for i, (cod, _) in enumerate(itens):
            blocos.append(f'''"<div class='linha sobe' style='left:{x}px;top:{y+30+i*h}px;width:{w}px;height:{h}px'>"
    & "<b>{roteiro.numero(cod)}</b><span>" & ({textos[cod]}) & "</span></div>"''')
    gravar('Achados · HTML', 'VAR _html = ' + '\n    & '.join(blocos) + '\nRETURN _html',
           'Resultado espelhado dos dois turnos e onze achados/atalhos distribuídos nos cinco atos.')
    gravar('Resumo · HTML', '''"<div class='tela resumo-final'><div class='rot sobe d4'>DIFERENÇA FINAL</div>"
    & "<div class='num diferenca sobe d5'>" & FORMAT ( [T23 · diferença final], "#,0" ) & "</div>"
    & "<div class='de'>votos entre Lula e Flávio</div><div class='risco-fecho'></div>"
    & "<div class='abst'>Abstenção · 1º → 2º turno: <b class='num'>" & FORMAT ( [T23 · abstenção 1º turno], "0.00%" )
    & "</b> → <b class='num'>" & FORMAT ( [T23 · abstenção 2º turno], "0.00%" ) & "</b></div>"
    & "<div class='comparecimento'><b class='num'>" & FORMAT ( [T23 · comparecimento a mais], "#,0" )
    & "</b> a mais votaram no 2º turno</div></div>"''', 'Fecho numérico central: diferença final e participação, com contador automático.')
    gravar('Resumo · ALT', '''"Diferença final: " & FORMAT ( [T23 · diferença final], "#,0" ) & " votos. Abstenção de "
    & FORMAT ( [T23 · abstenção 1º turno], "0.00%" ) & " para " & FORMAT ( [T23 · abstenção 2º turno], "0.00%" )
    & " entre os turnos; " & FORMAT ( [T23 · comparecimento a mais], "#,0" ) & " pessoas a mais compareceram, incluindo exterior."''', 'Resumo acessível da diferença e da participação.')
    gravar('Achados · ALT', '''"Encerramento. 2º turno: Lula "
    & FORMAT ( [T00 · 2º turno · Lula %], "0.00%" ) & "; Flávio "
    & FORMAT ( [T00 · 2º turno · Flávio %], "0.00%" )
    & ". Diferença: " & FORMAT ( [T23 · diferença final], "#,0" ) & " votos. Abstenção "
    & FORMAT ( [T23 · abstenção 1º turno], "0.00%" ) & " → " & FORMAT ( [T23 · abstenção 2º turno], "0.00%" )
    & "; " & FORMAT ( [T23 · comparecimento a mais], "#,0" ) & " presenças a mais. Achados dos cinco atos levam à origem."''',
           'Encerramento acessível, resultados e navegação.')
    print('T23: encerramento dos dois turnos e achados por ato gerados; PBIP preservado.')


if __name__ == '__main__':
    main()
