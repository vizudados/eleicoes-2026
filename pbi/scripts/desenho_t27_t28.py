"""Gera as contas, os desenhos e os specs das duas telas finais, sem alterar o PBIP ou o motor.

Mesma gramática, mesmas contas para os dois candidatos. T27 fecha a identidade observada dos ganhos;
não estima de qual grupo veio o voto individual de Lula ou Flávio.
"""
from __future__ import annotations
import json
from pathlib import Path
from validar_dax_gerado import problemas

PBI = Path(__file__).resolve().parents[1]


def gravar(pasta, nome, expressao, descricao, formato='texto', conta=False):
    erros=problemas(expressao,comentario_inline=True)
    if erros:
        raise ValueError(f'{nome}: ' + '; '.join(erros))
    tipo = 'Contas' if conta else 'Desenho'
    p = PBI / 'dax' / pasta / tipo / (nome + '.dax')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f'/*\n@pasta: {pasta}\\{tipo}\n@formato: {formato}\n@descricao: {descricao}\n'
                 '@oraculo: dados/saida/2turno/comparacao_municipios.csv; dados/pbi/municipio_ano.csv; municipio_2turno.csv\n'
                 '@gerado: pbi/scripts/desenho_t27_t28.py\n*/\n'
                 + expressao.strip() + '\n', encoding='utf-8')


def conta(p, nome, expr, desc, fmt='#,0'):
    gravar(f'{p} ' + ('De onde vieram' if p == 'T27' else 'Onde Flávio perdeu'), f'{p} · {nome}', expr, desc, fmt, True)


def desenho(p, nome, expr, desc):
    gravar(f'{p} ' + ('De onde vieram' if p == 'T27' else 'Onde Flávio perdeu'), f'{p} · {nome}', expr, desc)


def ref(p, nome):
    return f'[{p} · {nome}]'


def compacto(valor, assinado=False):
    """Só formatação: milhões, milhares ou unidades, sem esconder uma variação pequena como 0,00 mi."""
    texto=(f'SWITCH ( TRUE (), ABS ( {valor} ) >= 1e6, FORMAT ( ABS ( {valor} ) / 1e6, "0.00" ) & " mi", '
           f'ABS ( {valor} ) >= 1000, FORMAT ( ABS ( {valor} ) / 1000, "0.0" ) & " mil", '
           f'FORMAT ( ABS ( {valor} ), "#,0" ) )')
    return (f'IF ( {valor} > 0, "+", IF ( {valor} < 0, "−", "" ) ) & ({texto})') if assinado else texto


def contas(p):
    for cand, col in [('Lula', 'VotosPT'), ('Flávio', 'VotosAdversario')]:
        for turno, tabela in [('1º', 'Município ano'), ('2º', 'Município segundo turno')]:
            conta(p, f'{cand} {turno}', f'''CALCULATE ( SUM ( '{tabela}'[{col}] ),
    REMOVEFILTERS ( 'Ano' ), '{tabela}'[Ano] = 2026 )''',
                  f'Votos de {cand} em 2026, {turno} turno, sem exterior; respeita Município e UF.')
        conta(p, f'ganho {cand}', f'{ref(p, cand+" 2º")} - {ref(p, cand+" 1º")}',
              f'Saldo em votos de {cand}: segundo menos primeiro turno, sem exterior.')
    for nome, coluna in [('comparecimento', 'Comparecimento'), ('abstenções', 'Abstencoes'),
                          ('brancos', 'Brancos'), ('nulos', 'Nulos')]:
        for turno, tabela in [('1º', 'Município ano'), ('2º', 'Município segundo turno')]:
            conta(p, f'{nome} {turno}', f'''CALCULATE ( SUM ( '{tabela}'[{coluna}] ),
    REMOVEFILTERS ( 'Ano' ), '{tabela}'[Ano] = 2026 )''', f'{nome}, {turno} turno, recorte municipal de 2026.')
        conta(p, f'saldo {nome}', f'{ref(p, nome+" 2º")} - {ref(p, nome+" 1º")}',
              f'Variação agregada de {nome}; não identifica quem voltou ou deixou de votar.')
    conta(p, 'vantagem Lula 1º', f'{ref(p,"Lula 1º")} - {ref(p,"Flávio 1º")}', 'Lula menos Flávio, votos no primeiro turno.')
    conta(p, 'vantagem Lula 2º', f'{ref(p,"Lula 2º")} - {ref(p,"Flávio 2º")}', 'Lula menos Flávio, votos no segundo turno.')
    conta(p, 'mudança de vantagem', f'{ref(p,"ganho Lula")} - {ref(p,"ganho Flávio")}',
          'Redução da vantagem de Flávio: ganho de Lula menos ganho de Flávio, em votos; sinal negativo favorece Flávio.')
    for nome, teste in [
        ('virou para Lula', f'{ref(p,"Flávio 1º")} > {ref(p,"Lula 1º")} && {ref(p,"Lula 2º")} > {ref(p,"Flávio 2º")}'),
        ('virou para Flávio', f'{ref(p,"Lula 1º")} > {ref(p,"Flávio 1º")} && {ref(p,"Flávio 2º")} > {ref(p,"Lula 2º")}')]:
        conta(p, nome, f'IF ( {teste}, 1, 0 )', 'Indicador de virada estrita; empate não conta como vitória.')
        conta(p, nome+' · municípios', f"SUMX ( VALUES ( 'Município'[CodIBGE] ), {ref(p,nome)} )", 'Municípios com virada estrita, no recorte.')
        conta(p, nome+' · UFs', f'''SUMX (
    FILTER ( VALUES ( 'UF'[UF] ), 'UF'[UF] <> "ZZ" ),
    VAR _uf = 'UF'[UF]
    RETURN CALCULATE ( {ref(p,nome)}, REMOVEFILTERS ( 'Município' ), 'UF'[UF] = _uf ) )''',
              'UFs inteiras com virada estrita. Reaplica a UF após limpar Município, cuja tabela expandida também contém UF.')
    conta(p, 'Jair 2022', '''VAR _n = CALCULATE ( COUNTROWS ( 'Município segundo turno' ),
    REMOVEFILTERS ( 'Ano' ), 'Município segundo turno'[Ano] = 2022 )
RETURN IF ( _n > 0, CALCULATE ( SUM ( 'Município segundo turno'[VotosAdversario] ),
    REMOVEFILTERS ( 'Ano' ), 'Município segundo turno'[Ano] = 2022 ) )''', 'Votos de Jair no segundo turno de 2022; município sem base permanece BLANK.')
    conta(p, 'Lula 2022', '''VAR _n = CALCULATE ( COUNTROWS ( 'Município segundo turno' ),
    REMOVEFILTERS ( 'Ano' ), 'Município segundo turno'[Ano] = 2022 )
RETURN IF ( _n > 0, CALCULATE ( SUM ( 'Município segundo turno'[VotosPT] ),
    REMOVEFILTERS ( 'Ano' ), 'Município segundo turno'[Ano] = 2022 ) )''', 'Votos de Lula no segundo turno de 2022, mesma regra de ausência usada para Jair.')
    conta(p, 'saldo Lula contra 2022', f'IF ( NOT ISBLANK ( {ref(p,"Lula 2022")} ), {ref(p,"Lula 2º")} - {ref(p,"Lula 2022")} )', 'Lula 2026 menos Lula 2022, ambos no segundo turno.')
    conta(p, 'saldo Flávio contra 2022', f'IF ( NOT ISBLANK ( {ref(p,"Jair 2022")} ), {ref(p,"Flávio 2º")} - {ref(p,"Jair 2022")} )', 'Flávio 2026 menos Jair 2022, mesma conta em votos da comparação de Lula.')
    conta(p, 'abaixo de Jair · indicador', f'IF ( NOT ISBLANK ( {ref(p,"Jair 2022")} ) && {ref(p,"Flávio 2º")} < {ref(p,"Jair 2022")}, 1, 0 )',
          '1 se Flávio teve menos votos que Jair em 2022; mesma conta absoluta por município.')
    conta(p, 'abaixo de Jair · municípios', f"SUMX ( VALUES ( 'Município'[CodIBGE] ), {ref(p,'abaixo de Jair · indicador')} )", 'Municípios em que Flávio ficou abaixo de Jair, comparáveis.')
    conta(p, 'perda para Jair', f'IF ( NOT ISBLANK ( {ref(p,"Jair 2022")} ), {ref(p,"Jair 2022")} - {ref(p,"Flávio 2º")} )',
          'Jair 2022 menos Flávio 2026, ambos segundo turno; só para contexto comparável. Não é efeito causal.')
    conta(p, 'perda positiva para Jair', f'IF ( {ref(p,"perda para Jair")} > 0, {ref(p,"perda para Jair")} )',
          'Somente municípios em que Flávio ficou abaixo de Jair, em votos; vazio nos demais.')
    conta(p, 'municípios sem 2022', f"COUNTROWS ( FILTER ( VALUES ( 'Município'[CodIBGE] ), ISBLANK ( {ref(p,'Jair 2022')} ) ) )", 'Municípios sem segundo turno de 2022; nunca converter ausência em zero.')
    conta(p, 'território alterado', '''IF ( SELECTEDVALUE ( 'Município'[CodIBGE] )
    IN { "5101837", "5107925", "5106240", "5106307", "5108502" }, 1, 0 )''',
          'Ressalva territorial em MT: Boa Esperança do Norte, Sorriso, Nova Ubiratã, Paranatinga e Vera; sem reconstrução em área constante.')
    conta(p, 'mapa · valor', ref(p,'ganho Lula' if p == 'T27' else 'mudança de vantagem'),
          'Saldo em votos mostrado no mapa e no ranking; sinal preservado.')
    conta(p, 'mapa · tamanho', f'ABS ( {ref(p,"mapa · valor")} )', 'Magnitude absoluta, só para dimensionar a marca.')
    conta(p, 'fluxo · escala', f'MAX ( ABS ( {ref(p,"ganho Lula")} ), ABS ( {ref(p,"ganho Flávio")} ) )', 'Máximo absoluto dos ganhos, geometria dos traços.')
    conta(p, 'estado virou · mudança', f'IF ( {ref(p,"virou para Lula")} = 1, {ref(p,"mudança de vantagem")} )',
          'Mudança em votos somente onde houve virada estrita para Lula; vazio nos demais estados.')
    if p == 'T27':
        conta(p,'demais no 1º turno', '''CALCULATE ( SUM ( 'Município ano'[VotosDemais] ),
    REMOVEFILTERS ( 'Ano' ), 'Município ano'[Ano] = 2026 )''', 'Votos observados dos demais candidatos no primeiro turno, sem exterior.')
        conta(p,'queda de brancos e nulos', f'-{ref(p,"saldo brancos")} - {ref(p,"saldo nulos")}',
              'Brancos e nulos do primeiro menos segundo turno; negativo significa aumento dos inválidos.')
        conta(p,'ganhos da dupla', f'{ref(p,"ganho Lula")} + {ref(p,"ganho Flávio")}', 'Soma dos ganhos observados de Lula e Flávio entre turnos.')
        conta(p,'identidade · soma das parcelas', f'{ref(p,"demais no 1º turno")} + {ref(p,"saldo comparecimento")} + {ref(p,"queda de brancos e nulos")}',
              'Demais no primeiro turno + variação de comparecimento + queda de inválidos; identidade de saldos.')
        conta(p,'identidade · resíduo', f'{ref(p,"ganhos da dupla")} - {ref(p,"identidade · soma das parcelas")}',
              'Controle de QA: deve ser zero em qualquer recorte municipal. Não é mostrado como KPI.')
        for cand in ['Lula','Flávio']:
            conta(p,f'parcela {cand} nos ganhos', f'''VAR _l = {ref(p,'ganho Lula')}
VAR _f = {ref(p,'ganho Flávio')}
VAR _total = {ref(p,'ganhos da dupla')}
RETURN IF ( _l >= 0 && _f >= 0 && _total > 0, DIVIDE ( {ref(p,'ganho '+cand)}, _total ) )''',
                  'Parcela do aumento conjunto; só é interpretada como distribuição de ganhos quando ambos não perdem votos.', '0.00%')
        conta(p,'Lula em cada dez ganhos', f'''VAR _p = {ref(p,'parcela Lula nos ganhos')}
RETURN IF ( NOT ISBLANK ( _p ), 10 * _p )''', 'De cada dez votos ganhos pela dupla, quantos foram ganhos líquidos de Lula.', '0.0')


def desenhos(p):
    r=lambda x:ref(p,x)
    l,f,v=r('ganho Lula'),r('ganho Flávio'),r('mudança de vantagem')
    nl,nf,nv=compacto(l),compacto(f),compacto(v)
    hl=f'({nl}) & IF ( ABS ( {l} ) >= 1e6, " de votos", IF ( ABS ( {l} ) = 1, " voto", " votos" ) )'
    hf=f'({nf}) & IF ( ABS ( {f} ) >= 1e6, " de votos", IF ( ABS ( {f} ) = 1, " voto", " votos" ) )'
    if p=='T27':
        numero=f'IF ( NOT ISBLANK ( {r("Lula em cada dez ganhos")} ), FORMAT ( {r("Lula em cada dez ganhos")}, "0.0" ), ({nl}) )'
        frase=f'''IF ( NOT ISBLANK ( {r('Lula em cada dez ganhos')} ),
    "De cada 10 votos que a dupla ganhou, " & FORMAT ( {r('Lula em cada dez ganhos')}, "0.0" ) & " foram para Lula",
    "Lula " & IF ( {l} >= 0, "ganhou ", "perdeu " ) & ({hl}) & " entre os turnos" )'''
        apoio=f'''IF ( NOT ISBLANK ( {r('parcela Lula nos ganhos')} ),
    "Lula ficou com " & FORMAT ( {r('parcela Lula nos ganhos')}, "0.00%" ) & " do aumento; Flávio, "
        & FORMAT ( {r('parcela Flávio nos ganhos')}, "0.00%" ) & ". A conta dos volumes observados fecha abaixo.",
    "Flávio " & IF ( {f} >= 0, "ganhou ", "perdeu " ) & ({hf}) & ". A conta abaixo mostra o saldo conjunto dos dois." )'''
    else:
        numero=nv
        frase=f'"A vantagem de Flávio " & IF ( {v} >= 0, "diminuiu ", "aumentou " ) & ({nv}) & IF ( ABS ( {v} ) >= 1e6, " de votos", IF ( ABS ( {v} ) = 1, " voto", " votos" ) )'
        apoio=f'"Lula " & IF ( {l} >= 0, "ganhou ", "perdeu " ) & ({hl}) & "; Flávio " & IF ( {f} >= 0, "ganhou ", "perdeu " ) & ({hf}) & ". Perder vantagem não significa perder votos em termos absolutos."'
    desenho(p,'Resposta · HTML',f'''-- 1 · Leituras e 2 · Textos
VAR _frase = {frase}
VAR _apoio = {apoio}
VAR _numero = {numero}
VAR _titulo = SUBSTITUTE ( _frase, _numero, "<b class='num hero'>" & _numero & "</b>" )
-- 4 · Marcação
RETURN "<div class='tela st-res'><div class='sob'>DO 1º PARA O 2º TURNO · " & UPPER ( [Recorte · nome] )
    & " · SEM EXTERIOR</div><div class='man sobe'>" & _titulo & "</div><div class='txt sobe d2'>" & _apoio & "</div></div>"''','Manchete responde à pergunta com contas do recorte.')
    desenho(p,'Resposta · ALT',f'''{frase} & ". " & {apoio}''','Resposta acessível do recorte; valores em milhões.')
    linhas=[]
    for i,(cand,cls) in enumerate([('Lula','lula'),('Flávio','flavio')]):
        y=40+i*100
        linhas.append(f'''"<div class='candidato {cls}-esc' style='top:{y-20}px'>{cand}</div>"
    & "<div class='origem num' style='top:{y}px'>" & FORMAT ( {r(cand+' 1º')}, "#,0" ) & "</div>"
    & "<div class='destino num {cls}' style='top:{y}px'>" & FORMAT ( {r(cand+' 2º')}, "#,0" ) & "</div>"
    & "<svg class='ponte' style='top:{y+12}px' width='300' height='45'>"
    & "<path d='M5 24 C70 8, 170 40, 286 20' pathLength='1' class='traco' fill='none' stroke='var(--{'vermelho' if cls=='lula' else 'azul'})' stroke-width='"
    -- geometria
    & FORMAT ( 3 + 11 * DIVIDE ( ABS ( {r('ganho '+cand)} ), {r('fluxo · escala')}, 0 ), "0.0", "en-US" )
    & "' stroke-linecap='round' filter='url(#rb)'/></svg>"
    & "<div class='saldo num {cls}-esc' style='top:{y+54}px'>" & FORMAT ( {r('ganho '+cand)}, "+#,0;-#,0;0" ) & IF ( ABS ( {r('ganho '+cand)} ) = 1, " voto", " votos" ) & "</div>"''')
    if p=='T27':
        tabela='''"<div class='conta-observada'><div class='rot'>A SOMA DOS GANHOS · VOTOS OBSERVADOS</div>"'''
        for medida,label in [
            ('demais no 1º turno','"Demais candidatos no 1º turno"'),
            ('saldo comparecimento',f'IF ( {r("saldo comparecimento")} >= 0, "Comparecimento a mais", "Comparecimento a menos" )'),
            ('queda de brancos e nulos',f'IF ( {r("queda de brancos e nulos")} >= 0, "Brancos e nulos a menos", "Brancos e nulos a mais" )')]:
            tabela+=f'''\n    & "<div class='parcela'><span>" & ({label}) & "</span><b class='num'>" & FORMAT ( {r(medida)}, "+#,0;-#,0;0" ) & "</b></div>"'''
        tabela+=f'''\n    & "<div class='parcela total'><span>" & IF ( {r('ganhos da dupla')} >= 0, "Ganho total da dupla", "Saldo total da dupla" )
    & "</span><b class='num'>= " & FORMAT ( {r('ganhos da dupla')}, "+#,0;-#,0;0" ) & "</b></div>"
    & "<div class='nota'>a urna não mostra quem trocou de candidato.</div></div>"'''
    else:
        tabela=f'''"<div class='resumo-viradas'><div class='rot'>ONDE O VENCEDOR MUDOU · MUNICÍPIOS · VITÓRIA ESTRITA</div>"
    & "<div class='viradas'><div><b class='num lula-esc'>" & FORMAT ( {r('virou para Lula · municípios')}, "#,0" )
    & "</b><span>Flávio → Lula</span></div><div><b class='num flavio-esc'>" & FORMAT ( {r('virou para Flávio · municípios')}, "#,0" )
    & "</b><span>Lula → Flávio</span></div><div><b class='num'>" & FORMAT ( {r('abaixo de Jair · municípios')}, "#,0" )
    & "</b><span>Flávio abaixo de Jair em 2022</span></div></div>"
    & "<div class='nota'>Empates não contam como virada. A comparação com Jair usa apenas municípios com base nos dois anos.</div></div>"'''
    participacao='' if p=='T27' else f'''\n    & "<div class='participacao'>Saldo de comparecimento: <b>" & FORMAT ( {r('saldo comparecimento')}, "+#,0;-#,0;0" )
    & "</b> · abstenções: <b>" & FORMAT ( {r('saldo abstenções')}, "+#,0;-#,0;0" ) & "</b></div>"'''
    desenho(p,'Fluxo · HTML', '''-- 1 · Leituras e 3 · Geometria: espessura proporcional ao ganho absoluto
-- 4 · Marcação
VAR _html = "<div class='tela st-fluxo'><div class='rot antes'>1º TURNO</div><div class='rot depois'>2º TURNO</div>"
    & '''+'\n    & '.join(linhas)+participacao+ '\n    & '+tabela+'\n    & "</div>"\nRETURN _html', 'Fluxo em traço, mesmos volumes observados para os dois candidatos; não afirma transferência individual.')
    desenho(p,'Fluxo · ALT', f'''"Votos entre turnos: Lula " & FORMAT ( {r('Lula 1º')}, "#,0" ) & " para " & FORMAT ( {r('Lula 2º')}, "#,0" )
    & "; Flávio " & FORMAT ( {r('Flávio 1º')}, "#,0" ) & " para " & FORMAT ( {r('Flávio 2º')}, "#,0" ) & ". Sem exterior; origens individuais não observadas."''','Leitura acessível dos dois fluxos.')
    # As listas vêm de medidas; só a geometria e a marcação permanecem no desenho.
    if p=='T27':
        grupos=[('Região',"'UF'[Região]"),('Porte',"'Município'[Porte]")]
    else:
        grupos=[('Estados · mudança em votos',"'UF'[Nome]"),('Abaixo de Jair · perda em votos',"'Município'[Rótulo]")]
    partes=[]
    for j,(label,col) in enumerate(grupos):
        valor=r('ganho Lula' if p=='T27' else 'mudança de vantagem')
        if p=='T28' and j==1:
            valor=r('perda positiva para Jair')
        lista=f'ADDCOLUMNS ( VALUES ( {col} ), "@v", {valor} )'
        partes.append(f'''VAR _g{j} = TOPN ( 2, {lista}, [@v], DESC, {col}, ASC )
VAR _t{j} = CONCATENATEX ( _g{j},
    IF ( NOT ISBLANK ( [@v] ), "<div><span>" & SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {col}, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" ), """", "&quot;" ), "'", "&#39;" )
    & "</span><b>" & ({compacto('[@v]',True)}) & "</b></div>" ), "", [@v], DESC )''')
    extra=''
    if p=='T28':
        partes.append(f'''VAR _viradas = TOPN ( 2, ADDCOLUMNS ( VALUES ( 'UF'[Nome] ), "@v", {r('estado virou · mudança')} ), [@v], DESC, 'UF'[Nome], ASC )
VAR _ufVirada = CONCATENATEX ( _viradas, IF ( NOT ISBLANK ( [@v] ), 'UF'[Nome] & " " ), "" )''')
        extra=' & "<div class=\'nota\'>Virada para Lula: " & IF ( _ufVirada = "", "nenhum estado", _ufVirada ) & "</div>"'
    desenho(p,'Apoios · HTML','\n'.join(partes)+f'''
RETURN "<div class='tela st-apoios'><div><div class='rot'>{grupos[0][0]}</div>" & _t0
    {extra} & "</div><div><div class='rot'>{grupos[1][0]}</div>" & IF ( _t1 = "", "<div>Nenhum no recorte</div>", _t1 ) & "</div></div>"''', 'Regiões e portes na T27; estados e viradas na T28, com os mesmos saldos em votos.')
    desenho(p,'Apoios · ALT','"Apoios por território e porte; saldos em votos, sem exterior. No filtro do alto, escolha uma UF ou região para explorar."','Contexto acessível dos apoios.')
    desenho(p,'Município · HTML',f'''-- 1 · Leituras
VAR _nome = SELECTEDVALUE ( 'Município'[Rótulo], "Municípios do recorte" )
VAR _esc = SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( _nome, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" ), """", "&quot;" ), "'", "&#39;" )
-- 4 · Marcação
RETURN "<div class='tela st-tt'><div class='fita'></div><div class='tit'>" & _esc
    & "</div><div class='rot'>DO 1º PARA O 2º TURNO · VOTOS</div><div class='duo'><div class='lula-esc'>Lula <b class='num'>"
    & FORMAT ( {r('ganho Lula')}, "+#,0;-#,0;0" ) & "</b></div><div class='flavio-esc'>Flávio <b class='num'>"
    & FORMAT ( {r('ganho Flávio')}, "+#,0;-#,0;0" ) & "</b></div></div><div class='txt'>O saldo de Lula menos Flávio passou de "
    & FORMAT ( {r('vantagem Lula 1º')}, "+#,0;-#,0;0" ) & " para " & FORMAT ( {r('vantagem Lula 2º')}, "+#,0;-#,0;0" )
    & IF ( ABS ( {r('vantagem Lula 2º')} ) = 1, " voto.", " votos." ) & "</div><div class='txt'>Comparecimento: " & FORMAT ( {r('saldo comparecimento')}, "+#,0;-#,0;0" )
    & "; abstenções: " & FORMAT ( {r('saldo abstenções')}, "+#,0;-#,0;0" ) & "; brancos: " & FORMAT ( {r('saldo brancos')}, "+#,0;-#,0;0" )
    & "; nulos: " & FORMAT ( {r('saldo nulos')}, "+#,0;-#,0;0" ) & ".</div><div class='txt'>"
    & IF ( ISBLANK ( {r('Jair 2022')} ), "Sem base de 2022; comparação com Jair indisponível.",
        "Frente ao 2º turno de 2022: Lula " & FORMAT ( {r('saldo Lula contra 2022')}, "+#,0;-#,0;0" ) & IF ( ABS ( {r('saldo Lula contra 2022')} ) = 1, " voto; Flávio ", " votos; Flávio " )
        & FORMAT ( {r('saldo Flávio contra 2022')}, "+#,0;-#,0;0" ) & IF ( ABS ( {r('saldo Flávio contra 2022')} ) = 1, " voto frente a Jair.", " votos frente a Jair." ) )
    & IF ( {r('território alterado')} = 1, " Limites territoriais mudaram em MT; a comparação não foi reconstruída em área constante.", "" )
    & "</div><div class='mao'>saldo não é trajetória</div></div>"''','Dossiê municipal acrescenta comparecimento, abstenção, inválidos e Jair 2022.')
    desenho(p,'Município · ALT',f'''SELECTEDVALUE ( 'Município'[Rótulo], "Recorte" ) & ": saldo de comparecimento " & FORMAT ( {r('saldo comparecimento')}, "+#,0;-#,0;0" )
    & "; saldo de abstenções " & FORMAT ( {r('saldo abstenções')}, "+#,0;-#,0;0" ) & ". A comparação de 2022 exige município presente nos dois anos."''','Alternativa acessível do dossiê.')


def specs(p):
    # Contornos simplificados em coordenadas do mapa da casa; desenho geográfico fixo, sem dados remotos.
    # Usa a geometria já normalizada e provada pela tela 03; os dados e as marcas recebem nomes distintos.
    base=json.loads((PBI/'spec/t03_mapa.json').read_text(encoding='utf-8'))
    ufs=next(d['values'] for d in base['data'] if d['name']=='ufs')
    s={
        '$schema':'https://vega.github.io/schema/vega/v6.json',
        'description':f'{p}: saldo municipal em votos. Tamanho é magnitude. ' + ('Vermelho: crescimento de Lula; azul: queda de Lula. ' if p=='T27' else 'Vermelho: mudança de vantagem para Lula; azul: para Flávio. ') + 'Contorno em traço, cor por esmaecer e seleção com linhagem municipal.',
        'width':{'signal':'pbiContainerWidth'},'height':{'signal':'pbiContainerHeight'},
        'padding':0,'autosize':{'type':'none','contains':'padding'},'background':None,
        'signals':[
            {'name':'estatico','init':'!(windowSize()[0] > 0)'},
            {'name':'fim','value':2400},
            {'name':'chave','update':"join(pluck(data('dataset'),'cod'), ',') + '|' + join(pluck(data('ufsAtivas'), 'uf'), ',')"},
            {'name':'t0','init':'now()','on':[{'events':{'signal':'chave'},'update':'now()'}]},
            {'name':'t','init':'estatico ? fim : 0','on':[{'events':{'signal':'chave'},'update':'estatico ? fim : 0'}, {'events':{'type':'timer','throttle':16},'update':'estatico || t >= fim ? fim : min(now()-t0,fim)'}]},
            {'name':'quadro','update':"length(data('limites')) ? data('limites')[0] : {x0:0,y0:0,x1:1000,y1:1000}"},
            {'name':'k','update':'min((width-30)/max(quadro.x1-quadro.x0,60),(height-30)/max(quadro.y1-quadro.y0,60))'},
            {'name':'ox','update':'width/2-(quadro.x0+quadro.x1)/2*k'},
            {'name':'oy','update':'height/2-(quadro.y0+quadro.y1)/2*k'},
            {'name':'maior','update':"length(data('extremos')) ? max(data('extremos')[0].v,1) : 1"},
            {'name':'clique','value':None,'on':[
                {'events':{'source':'scope','type':'mouseup','markname':'marcaMunicipios'},'update':"pbiCrossFilterApply(event)"},
                {'events':{'source':'view','type':'mouseup','filter':["!event.item || event.item.mark.name != 'marcaMunicipios'"]},'update':'pbiCrossFilterClear()'}]}
        ],
        'data':[
            {'name':'dataset'},
            {'name':'ufsAtivas','source':'dataset','transform':[{'type':'aggregate','groupby':['uf']}]},
            {'name':'contornos','values':ufs},
            {'name':'contornosAtivos','source':'contornos','transform':[{'type':'filter','expr':"indata('ufsAtivas','uf',datum.uf)"}]},
            {'name':'limites','source':'contornosAtivos','transform':[{'type':'aggregate','fields':['x0','y0','x1','y1'],'ops':['min','min','max','max'],'as':['x0','y0','x1','y1']}]},
            {'name':'locais','source':'dataset','transform':[{'type':'filter','expr':'isValid(datum.x) && isValid(datum.y) && isValid(datum.val)'}, {'type':'collect','sort':{'field':'tam','order':'descending'}}]},
            {'name':'extremos','source':'locais','transform':[{'type':'aggregate','fields':['tam'],'ops':['max'],'as':['v']}]}
        ],
        'marks':[
            {'name':'marcaCorUF','type':'path','from':{'data':'contornosAtivos'},'interactive':False,'encode':{'update':{
                'path':{'field':'d'},'x':{'signal':'ox'},'y':{'signal':'oy'},'scaleX':{'signal':'k'},'scaleY':{'signal':'k'},
                'fill':{'value':'#E5DBC8'},'fillOpacity':{'signal':'0.3*clamp((t-450)/1000,0,1)'},
                'stroke':{'value':'#48423A'},'strokeWidth':{'value':1},
                'strokeDash':{'signal':'t>=fim ? [] : [datum.ld*k+4,datum.ld*k+4]'},
                'strokeDashOffset':{'signal':'(datum.ld*k+4)*(1-clamp(t/1100,0,1))'}}}},
            {'name':'marcaMunicipios','type':'symbol','from':{'data':'locais'},'encode':{'update':{
                'x':{'signal':'ox+datum.x*k'},'y':{'signal':'oy+datum.y*k'},
                'size':{'signal':'12+210*sqrt(datum.tam/maior)'},
                'fill':{'signal':"datum.val > 0 ? '#B8322A' : datum.val < 0 ? '#31699B' : '#BBAD91'"},
                'fillOpacity':{'signal':"(datum.__selected__=='off' ? 0.2 : 0.8)*clamp((t-600)/1200,0,1)"},
                'stroke':{'signal':"datum.__selected__=='on' ? '#1C1915' : '#F1EBDF'"},
                'strokeWidth':{'signal':"datum.__selected__=='on' ? 2 : 0.4"},'tooltip':{'signal':'datum'},'cursor':{'value':'pointer'}},
                'hover':{'stroke':{'value':'#1C1915'},'strokeWidth':{'value':2},'fillOpacity':{'value':1}}}}
        ]}
    (PBI/f'spec/{p.lower()}_mapa.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lista={
        '$schema':'https://vega.github.io/schema/vega/v6.json','width':{'signal':'pbiContainerWidth'},'height':{'signal':'pbiContainerHeight'},
        'padding':0,'autosize':{'type':'none','contains':'padding'},'background':None,
        'signals':[
            {'name':'hoverCod','value':None,'on':[{'events':'@marcaAlvos:mouseover','update':'datum.cod'}, {'events':'@marcaAlvos:mouseout','update':'null'}]},
            {'name':'clique','value':None,'on':[{'events':{'source':'scope','type':'mouseup','markname':'marcaAlvos'},'update':'pbiCrossFilterApply(event)'},{'events':{'source':'view','type':'mouseup','filter':["!event.item || event.item.mark.name != 'marcaAlvos'"]},'update':'pbiCrossFilterClear()'}]},
        ],
        'data':[{'name':'dataset'}, {'name':'linhas','source':'dataset','transform':[
            {'type':'filter','expr':'isValid(datum.val)'},
            {'type':'window','sort':{'field':['val','cod'],'order':['descending','ascending']},'ops':['row_number'],'as':['pos']},
            {'type':'filter','expr':'datum.pos<=8'}]}],
        'scales':[{'name':'x','type':'linear','domain':{'data':'linhas','field':'val'},'range':[350,680],'zero':True,'nice':True}],
        'marks':[
            {'name':'marcaBarras','type':'rect','from':{'data':'linhas'},'interactive':False,'encode':{'update':{
                'x':{'signal':"min(scale('x',datum.val),scale('x',0))"},'x2':{'signal':"max(scale('x',datum.val),scale('x',0))"},
                'y':{'signal':'30+(datum.pos-1)*29+7'},'height':{'value':14},'cornerRadius':{'value':4},
                'fill':{'signal':"datum.val>=0 ? '#B8322A' : '#31699B'"},
                'opacity':{'signal':"(hoverCod != null && hoverCod != datum.cod) || datum.__selected__=='off' ? 0.25 : 0.85"}}}},
            {'name':'marcaNomes','type':'text','from':{'data':'linhas'},'interactive':False,'encode':{'update':{
                'x':{'value':0},'y':{'signal':'30+(datum.pos-1)*29+16'},'text':{'field':'rotulo'},'limit':{'value':335},
                'font':{'value':'Sora Vizu'},'fontSize':{'value':17},'fill':{'value':'#1C1915'},
                'opacity':{'signal':"(hoverCod != null && hoverCod != datum.cod) || datum.__selected__=='off' ? 0.4 : 1"}}}},
            {'name':'marcaValores','type':'text','from':{'data':'linhas'},'interactive':False,'encode':{'update':{
                'x':{'signal':'width-5'},'y':{'signal':'30+(datum.pos-1)*29+16'},'align':{'value':'right'},
                'text':{'field':'valorTexto'},'font':{'value':'Sora Vizu'},'fontSize':{'value':18},'fontWeight':{'value':600},'fill':{'value':'#1C1915'},
                'opacity':{'signal':"(hoverCod != null && hoverCod != datum.cod) || datum.__selected__=='off' ? 0.4 : 1"}}}},
            {'name':'marcaAlvos','type':'rect','from':{'data':'linhas'},'encode':{'update':{
                'x':{'value':0},'width':{'signal':'width'},'y':{'signal':'30+(datum.pos-1)*29'},'height':{'value':28},
                'fill':{'value':'#1C1915'},'fillOpacity':{'value':0},'tooltip':{'signal':'datum'},'cursor':{'value':'pointer'}},
                'hover':{'fillOpacity':{'value':0.06}}}}
        ]}
    (PBI/f'spec/{p.lower()}_lista.json').write_text(json.dumps(lista,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    desenho(p,'valor formatado',f'FORMAT ( {ref(p,"mapa · valor")}, "+#,0;-#,0;0" )','Rótulo da lista, formatado pelo DAX; Vega só posiciona.')


def main():
    for p in ['T27','T28']:
        contas(p)
        desenhos(p)
        specs(p)
    print('T27 e T28: contas, desenhos e specs gerados; nenhum PBIP ou motor alterado.')


if __name__=='__main__':
    main()
