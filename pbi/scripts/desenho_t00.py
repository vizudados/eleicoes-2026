"""Capa dos dois turnos: contas e desenho, sem gravar o PBIP ou consultar o Desktop."""
from pathlib import Path
from validar_dax_gerado import problemas

PASTA=Path(__file__).resolve().parents[1]/'dax/T00 Capa'


def gravar(nome,expr,desc,formato='texto',conta=False):
    erros=problemas(expr,comentario_inline=True)
    if erros:raise ValueError(nome+': '+'; '.join(erros))
    sub='Contas' if conta else 'Desenho'
    p=PASTA/sub/(nome+'.dax');p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(f'/*\n@pasta: T00 Capa\\{sub}\n@formato: {formato}\n@descricao: {desc}\n'
                 '@oraculo: TSE nacional com exterior; UF segundo turno 2026; viradas municipais sem exterior\n'
                 '@gerado: pbi/scripts/desenho_t00.py\n*/\n'+expr.strip()+'\n',encoding='utf-8')


def main():
    for cand,col in [('Lula','VotosPT'),('Flávio','VotosAdversario'),('válidos','Validos')]:
        nome=f'T00 · 2º turno · {cand}' + ('' if cand=='válidos' else ' votos')
        gravar(nome,f'''CALCULATE ( SUM ( 'UF segundo turno'[{col}] ),
    REMOVEFILTERS ( 'UF' ), REMOVEFILTERS ( 'Ano' ), REMOVEFILTERS ( 'UF segundo turno' ),
    'UF segundo turno'[Ano] = 2026 )''','Resultado nacional final do segundo turno, com exterior; independe do filtro de UF.','#,0',True)
    for cand in ['Lula','Flávio']:
        gravar(f'T00 · 2º turno · {cand} %',f'DIVIDE ( [T00 · 2º turno · {cand} votos], [T00 · 2º turno · válidos] )',
               'Percentual final nacional dos votos válidos do segundo turno.','0.00%',True)
    for sentido in ['Lula','Flávio']:
        nome='Flávio para Lula' if sentido=='Lula' else 'Lula para Flávio'
        gravar(f'T00 · entre turnos · {nome}',f'''CALCULATE ( [T28 · virou para {sentido} · municípios],
    REMOVEFILTERS ( 'UF' ), REMOVEFILTERS ( 'Município' ), REMOVEFILTERS ( 'Ano' ) )''',
               'Municípios que trocaram de vencedor entre os turnos de 2026, sem empates ou exterior.','#,0',True)
    blocos=[]
    for cand,pos,cls in [('Flávio','esq','flavio'),('Lula','dir','lula')]:
        nome='FLÁVIO BOLSONARO · PL' if cand=='Flávio' else 'LULA · PT'
        # 27/10/2026: Lula já era presidente; a palavra certa é reeleito (pedido do dono, "tem que mudar isso em tudo")
        selo="<span class='selo-eleito' aria-label='Lula reeleito'>reeleito</span>" if cand=='Lula' else ''
        blocos.append(f'''"<div class='bl {pos} sobe d6'><div class='rot'>{nome}</div><div class='rot etapa'>2º TURNO · RESULTADO FINAL</div>"
    & "<div class='num v {cls}-c'>" & FORMAT ( [T00 · 2º turno · {cand} votos] / 1e6, "0.00" )
    & " mi</div><div class='p'>" & FORMAT ( [T00 · 2º turno · {cand} %], "0.00%" ) & " dos válidos</div>"
    & "<div class='primeiro'>1º turno · <span class='num'>" & FORMAT ( [T00 · {cand} votos] / 1e6, "0.00" )
    & " mi</span> · " & FORMAT ( [T00 · {cand} %], "0.00%" ) & "</div>{selo}</div>"''')
    expr='''VAR _paraLula = [T00 · entre turnos · Flávio para Lula]
VAR _paraFlavio = [T00 · entre turnos · Lula para Flávio]
VAR _n = [T00 · municípios no mapa]
VAR _html = '''+'\n    & '.join(blocos)+'''
    & "<div class='pe-esq sobe d10'><span class='vir'><span class='num'>" & FORMAT ( _paraLula, "#,0" )
    & "</span><span class='risco'></span></span> " & IF ( _paraLula = 1, "município trocou", "municípios trocaram" )
    & " Flávio por Lula<br/>entre os turnos · <span class='num'>" & FORMAT ( _paraFlavio, "#,0" )
    & "</span> " & IF ( _paraFlavio = 1, "fez", "fizeram" ) & " o caminho contrário</div>"
    & "<div class='pe-dir sobe d11'><span class='num'>" & FORMAT ( _n, "#,0" )
    & "</span> municípios, um ponto cada</div>"
RETURN _html'''
    gravar('T00 · Capa · HTML',expr,'Capa com segundo turno em destaque, primeiro turno menor e viradas estritas entre turnos; mesmos blocos para os dois.')
    gravar('T00 · Capa · ALT','''"Eleições 2026. 2º: Lula " & FORMAT ( [T00 · 2º turno · Lula votos] / 1e6, "0.00" )
    & " mi, " & FORMAT ( [T00 · 2º turno · Lula %], "0.00%" ) & " (reeleito); Flávio "
    & FORMAT ( [T00 · 2º turno · Flávio votos] / 1e6, "0.00" ) & " mi, " & FORMAT ( [T00 · 2º turno · Flávio %], "0.00%" )
    & ". 1º: Lula " & FORMAT ( [T00 · Lula votos] / 1e6, "0.00" ) & " mi, " & FORMAT ( [T00 · Lula %], "0.00%" )
    & "; Flávio " & FORMAT ( [T00 · Flávio votos] / 1e6, "0.00" ) & " mi, " & FORMAT ( [T00 · Flávio %], "0.00%" ) & ". "
    & FORMAT ( [T00 · entre turnos · Flávio para Lula], "#,0" ) & " municípios Flávio → Lula; "
    & FORMAT ( [T00 · entre turnos · Lula para Flávio], "#,0" ) & " no sentido contrário entre turnos."''','Leitura acessível da capa, com os dois resultados e viradas entre turnos.')
    print('Capa: sete contas novas e dois desenhos gerados; PBIP e motor preservados.')


if __name__=='__main__':
    main()
