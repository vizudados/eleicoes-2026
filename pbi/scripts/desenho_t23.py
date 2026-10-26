"""Encerramento dos dois turnos. Reutiliza as contas nacionais da capa e a geometria da própria página."""
from pathlib import Path
import roteiro
from paginas.t23_encerramento import GRUPOS
from validar_dax_gerado import problemas

PASTA = Path(__file__).resolve().parents[1] / 'dax/T23 Encerramento/Desenho'


def gravar(nome, expr, desc):
    erros = problemas(expr, comentario_inline=True)
    if erros:
        raise ValueError('; '.join(erros))
    (PASTA / f'T23 · {nome}.dax').write_text(
        f'/*\n@pasta: T23 Encerramento\\Desenho\n@formato: texto\n@descricao: {desc}\n'
        '@gerado: pbi/scripts/desenho_t23.py\n*/\n'+expr.strip()+'\n', encoding='utf-8')


def main():
    blocos = []
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
        'T11': '''FORMAT ( [T11 · viraram], "#,0" ) & " municípios trocaram Lula por Flávio de 2022 para o 1º turno de 2026."''',
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
    gravar('Achados · ALT', '''"Da zona eleitoral ao resultado. 2º turno: Lula "
    & FORMAT ( [T00 · 2º turno · Lula %], "0.00%" ) & "; Flávio "
    & FORMAT ( [T00 · 2º turno · Flávio %], "0.00%" )
    & ". Primeiro turno menor, resultado final maior. Achados dos cinco atos levam às telas de origem, inclusive à história do PT e ao recorde de votos."''',
           'Encerramento acessível, resultados e navegação.')
    print('T23: encerramento dos dois turnos e achados por ato gerados; PBIP preservado.')


if __name__ == '__main__':
    main()
