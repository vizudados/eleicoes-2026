"""T28 com composição própria: ponte da diferença, trocas de vencedor e perdas frente a Jair.

Brasil com exterior; no filtro de uma UF, ponte por município. Todo texto fica no HTML, com Sora.
"""
from pathlib import Path
import json
from desenho_t27_t28 import conta, desenho, ref, compacto, contas
from validar_dax_gerado import problemas

PBI = Path(__file__).resolve().parents[1]
P = 'T28'
R = lambda n: ref(P, n)
TOP = 9


def esc(s):
    return f'''SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {s}, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" ), """", "&quot;" ), "'", "&#39;" )'''


def contas_ponte():
    conta(P, 'ponte · municipal', 'IF ( [Recorte · tipo] = "UF", 1, 0 )', '1: uma UF escolhida, ponte municipal; demais recortes: unidades federativas.', '0')
    for cand, num, col in [('Lula', 13, 'VotosPT'), ('Flávio', 22, 'VotosAdversario')]:
        conta(P, f'ponte · {cand} UF 1º', f'''CALCULATE ( SUM ( 'Candidato UF'[Votos] ), REMOVEFILTERS ( 'Ano' ),
    'Candidato UF'[Ano] = 2026, 'Candidato UF'[Número] = {num} )''', 'Votação estadual no primeiro turno, incluindo ZZ no Brasil.')
        conta(P, f'ponte · {cand} UF 2º', f'''CALCULATE ( SUM ( 'UF segundo turno'[{col}] ), REMOVEFILTERS ( 'Ano' ),
    'UF segundo turno'[Ano] = 2026 )''', 'Votação estadual no segundo turno, incluindo ZZ no Brasil.')
    for turno in ['1º', '2º']:
        conta(P, f'ponte · diferença UF {turno}', f'{R("ponte · Lula UF "+turno)} - {R("ponte · Flávio UF "+turno)}', 'Diferença Lula menos Flávio, em votos.')
    conta(P, 'ponte · movimento UF', f'{R("ponte · diferença UF 2º")} - {R("ponte · diferença UF 1º")}', 'Movimento da diferença na UF entre turnos; positivo para Lula, negativo para Flávio.')
    for nome, turno in [('início', '1º'), ('fim', '2º')]:
        conta(P, f'ponte · {nome}', f'IF ( {R("ponte · municipal")} = 1, {R("vantagem Lula "+turno)}, {R("ponte · diferença UF "+turno)} )', 'Diferença no começo/fim da ponte. Brasil com exterior; UF escolhida usa seus municípios.')
    conta(P, 'ponte · total', f'{R("ponte · fim")} - {R("ponte · início")}', 'Mudança total da diferença entre os turnos.')
    conta(P, 'ponte · soma das etapas', f'''IF ( {R('ponte · municipal')} = 1,
    SUMX ( VALUES ( 'Município'[CodIBGE] ), {R('mudança de vantagem')} ),
    SUMX ( VALUES ( 'UF'[UF] ), {R('ponte · movimento UF')} ) )''', 'Soma independente das contribuições territoriais, incluindo ZZ quando pertence ao recorte.')
    conta(P, 'ponte · resíduo', f'{R("ponte · fim")} - {R("ponte · início")} - {R("ponte · soma das etapas")}', 'Controle de fechamento: deve ser zero; não é KPI do leitor.')
    for tipo, key, valor in [('estado', "'UF'[UF]", R('ponte · movimento UF')), ('município', "'Município'[CodIBGE]", R('mudança de vantagem'))]:
        filtro = f"FILTER ( VALUES ( {key} ), NOT ISBLANK ( {key} ) && {key} <> \"ZZ\" )" if tipo == 'estado' else f'FILTER ( VALUES ( {key} ), NOT ISBLANK ( {key} ) )'
        conta(P, f'ponte · três {tipo}s', f'SUMX ( TOPN ( 3, ADDCOLUMNS ( {filtro}, "@v", {valor} ), [@v], DESC, {key}, ASC ), [@v] )', 'Contribuição das três maiores unidades, com desempate por chave.')
    conta(P, 'ponte · três maiores', f'IF ( {R("ponte · municipal")} = 1, {R("ponte · três municípios")}, {R("ponte · três estados")} )', 'Soma das três maiores contribuições no universo da ponte.')
    conta(P, 'ponte · quantidade maiores', f'''MIN ( 3, IF ( {R('ponte · municipal')} = 1,
    COUNTROWS ( FILTER ( VALUES ( 'Município'[CodIBGE] ), NOT ISBLANK ( 'Município'[CodIBGE] ) ) ),
    COUNTROWS ( FILTER ( VALUES ( 'UF'[UF] ), NOT ISBLANK ( 'UF'[UF] ) && 'UF'[UF] <> "ZZ" ) ) ) )''',
          'Quantidade efetiva até três; Distrito Federal tem uma unidade municipal no modelo.', '0')
    conta(P, 'ponte · parcela três', f'DIVIDE ( {R("ponte · três maiores")}, {R("ponte · total")} )', 'Parcela das três maiores contribuições no movimento líquido; pode superar 100% em recortes com perdas compensatórias.', '0.0%')
    conta(P, 'ponte · nomes três', f'''VAR _top = TOPN ( 3, ADDCOLUMNS ( FILTER ( VALUES ( 'UF'[UF] ), NOT ISBLANK ( 'UF'[UF] ) && 'UF'[UF] <> "ZZ" ),
    "@v", {R('ponte · movimento UF')} ), [@v], DESC, 'UF'[UF], ASC )
VAR _nomes = CONCATENATEX ( _top, 'UF'[UF], ", ", [@v], DESC )
RETURN IF ( COUNTROWS ( _top ) = 3, SUBSTITUTE ( _nomes, ", ", " e ", 2 ), SUBSTITUTE ( _nomes, ", ", " e " ) )''', 'Siglas das três maiores contribuições estaduais.', 'texto')
    for tipo in ['estado', 'município']:
        etapas(tipo)
    conta(P, 'ponte · etapas', f'IF ( {R("ponte · municipal")} = 1, {R("ponte · etapas municípios")}, {R("ponte · etapas estados")} )', 'Etapas observadas da ponte; campo serializado para o desenho, sem números calculados no HTML.', 'texto')
    conta(P, 'viradas · mapa', f'IF ( {R("virou para Lula")} = 1 || {R("virou para Flávio")} = 1, {R("mudança de vantagem")} )', 'Somente as trocas estritas de vencedor; BLANK nos outros municípios, reduz o dataset a 212 no Brasil.')
    conta(P, 'Jair · saldo UF', '''CALCULATE ( SUM ( 'UF segundo turno'[VotosAdversario] ), REMOVEFILTERS ( 'Ano' ), 'UF segundo turno'[Ano] = 2026 )
    - CALCULATE ( SUM ( 'UF segundo turno'[VotosAdversario] ), REMOVEFILTERS ( 'Ano' ), 'UF segundo turno'[Ano] = 2022 )''', 'Flávio 2026 menos Jair 2022, segundo turno, por UF; perda tem sinal negativo.')
    conta(P, 'Jair · perda UF', f'''IF ( SELECTEDVALUE ( 'UF'[UF] ) <> "ZZ" && {R("Jair · saldo UF")} < 0, {R("Jair · saldo UF")} )''', 'Só estados com perda de votos; vazio nos demais e no exterior.')
    conta(P, 'Jair · perda cidade', f'IF ( {R("saldo Flávio contra 2022")} < 0, {R("saldo Flávio contra 2022")} )', 'Só cidades comparáveis com perda de votos; vazio nas demais.')


def etapas(tipo):
    municipal = tipo == 'município'
    key = "'Município'[CodIBGE]" if municipal else "'UF'[UF]"
    nome = "CALCULATE ( SELECTEDVALUE ( 'Município'[Município] ) )" if municipal else key
    delta = R('mudança de vantagem' if municipal else 'ponte · movimento UF')
    base = f'FILTER ( VALUES ( {key} ), NOT ISBLANK ( {key} ) )' if municipal else f'FILTER ( VALUES ( {key} ), NOT ISBLANK ( {key} ) && {key} <> "ZZ" )'
    unidade = 'cidades' if municipal else 'estados'
    ext = '0' if municipal else f'''SUMX ( FILTER ( VALUES ( 'UF'[UF] ), 'UF'[UF] = "ZZ" ), {R('ponte · movimento UF')} )'''
    # Esta é a conta acumulada da ponte, não geometria escondida no desenho.
    expr = f'''VAR _inicio = {R('ponte · início')}
VAR _fim = {R('ponte · fim')}
VAR _base = ADDCOLUMNS ( {base}, "@v", {delta}, "@nome", {nome} )
VAR _top = TOPN ( {TOP}, _base, [@v], DESC, {key}, ASC )
VAR _ext = {ext}
VAR _nOutros = MAX ( 0, COUNTROWS ( _base ) - {TOP} )
VAR _sTop = SUMX ( _top, [@v] )
VAR _ord = ADDCOLUMNS ( _top,
    "@i", VAR _d = [@v] VAR _k = {key}
        RETURN 1 + COUNTROWS ( FILTER ( _top, [@v] > _d || ( [@v] = _d && {key} < _k ) ) ),
    "@de", VAR _d = [@v] VAR _k = {key}
        RETURN _inicio + SUMX ( FILTER ( _top, [@v] > _d || ( [@v] = _d && {key} < _k ) ), [@v] ) )
VAR _linhas = SELECTCOLUMNS ( _ord, "i", [@i], "nome", [@nome], "de", [@de], "ate", [@de] + [@v], "v", [@v], "tipo", "passo" )
VAR _extras = FILTER ( UNION (
    ROW ( "i", 0, "nome", "1º turno", "de", 0, "ate", _inicio, "v", _inicio, "tipo", "inicio" ),
    ROW ( "i", 10, "nome", "Outros " & _nOutros & " {unidade}", "de", _inicio + _sTop, "ate", _fim - _ext, "v", _fim - _ext - _inicio - _sTop, "tipo", IF ( _nOutros > 0, "passo", "oculto" ) ),
    ROW ( "i", 11, "nome", "Exterior", "de", _fim - _ext, "ate", _fim, "v", _ext, "tipo", IF ( _ext <> 0, "passo", "oculto" ) ),
    ROW ( "i", 12, "nome", "2º turno", "de", 0, "ate", _fim, "v", _fim, "tipo", "fim" ) ), [tipo] <> "oculto" )
VAR _todas = UNION ( _linhas, _extras )
RETURN CONCATENATEX ( _todas, [i] & "^" & SUBSTITUTE ( SUBSTITUTE ( [nome], "^", " " ), "~", " " ) & "^" & [de] & "^" & [ate] & "^" & [v] & "^" & [tipo], "~", [i], ASC )'''
    conta(P, 'ponte · etapas '+('municípios' if municipal else 'estados'), expr, 'Acumulados e agrupamentos observados da ponte; começo + todas as contribuições = fim. 9 unidades explícitas, demais agrupadas.', 'texto')


def desenhos():
    desenho(P, 'Resposta · HTML', f'''VAR _local = {R('ponte · municipal')}
VAR _nomes = {esc(R('ponte · nomes três'))}
VAR _p = {R('ponte · parcela três')}
VAR _uma = _local = 1 && {R('ponte · quantidade maiores')} = 1
VAR _movimento = {R('ponte · total')}
VAR _fim = {R('ponte · fim')}
VAR _chamadaLocal = IF ( {R('ponte · quantidade maiores')} = 2, "As duas maiores contribuições somaram ", "As três maiores contribuições somaram " )
RETURN "<div class='tela perda-head'><div class='sob'>DO 1º PARA O 2º TURNO · "
    & IF ( [Recorte · com escolha] = 0, "BRASIL · COM EXTERIOR", {esc('[Recorte · nome]')} & " · SEM EXTERIOR" )
    & "</div><div class='man'>" & IF ( _uma,
        IF ( SELECTEDVALUE ( 'UF'[UF] ) = "DF", "No DF, ", "Neste recorte, " ) & "a diferença andou <span class='num'>"
        & FORMAT ( ABS ( _movimento ), "#,0" ) & "</span> votos para " & IF ( _movimento >= 0, "Lula", "Flávio" ),
        IF ( _local = 1, _chamadaLocal, _nomes & " somaram " ) & "<span class='num'>" & FORMAT ( _p, "0.0%" )
        & "</span> " & IF ( [Recorte · com escolha] = 0, "da virada", "da mudança" ) ) & "</div><div class='txt'>"
    & IF ( _uma, IF ( _fim = 0, "O 2º turno terminou empatado neste recorte.",
        IF ( _fim < 0, "Flávio", "Lula" ) & " terminou o 2º turno à frente por " & FORMAT ( ABS ( _fim ), "#,0" ) & " votos." ),
        FORMAT ( {R('ponte · três maiores')}, "#,0" ) & " de " & FORMAT ( _movimento, "#,0" ) & " votos. "
        & IF ( _local = 1, "A ponte mostra os municípios " & [Recorte · de] & ".", "No país, Minas foi o único estado que trocou Flávio por Lula." ) )
    & "</div></div>"''', 'Manchete da ponte, com universo explícito e soma das três maiores contribuições.')
    desenho(P, 'Resposta · ALT', f'''IF ( {R('ponte · municipal')} = 1 && {R('ponte · quantidade maiores')} = 1,
    "A diferença andou " & FORMAT ( ABS ( {R('ponte · total')} ), "#,0" ) & " votos para "
    & IF ( {R('ponte · total')} >= 0, "Lula", "Flávio" ) & ". Ponte de três barras: primeiro turno, contribuição municipal e segundo turno.",
    "Ponte da diferença entre os turnos. As maiores contribuições somaram " & FORMAT ( {R('ponte · parcela três')}, "0.0%" )
    & ". Brasil inclui exterior; uma UF escolhida mostra seus municípios. Minas foi o único estado a trocar de vencedor." )''', 'Leitura acessível do protagonista.')
    desenho_ponte()
    desenho(P, 'Viradas · HTML', f'''IF ( {R('virou para Lula · municípios')} = 0 && {R('virou para Flávio · municípios')} = 0,
    "<div class='tela viradas-head'>Nenhum município trocou de vencedor neste recorte.</div>",
    "<div class='tela viradas-head'><span class='num lula'>" & FORMAT ( {R('virou para Lula · municípios')}, "#,0" )
    & "</span> " & IF ( {R('virou para Lula · municípios')} = 1, "município passou", "municípios passaram" )
    & " de Flávio para Lula · <b class='num flavio'>" & FORMAT ( {R('virou para Flávio · municípios')}, "#,0" )
    & "</b> no caminho contrário</div>" )''', 'Contagem e legenda do mapa restrito às trocas de vencedor; recorte vazio tem aviso explícito.')
    desenho(P, 'Viradas · ALT', f'''FORMAT ( {R('virou para Lula · municípios')}, "#,0" ) & " municípios de Flávio para Lula e "
    & FORMAT ( {R('virou para Flávio · municípios')}, "#,0" ) & " no sentido contrário. Mapa só das trocas estritas; empate não conta."''', 'Mapa de trocas acessível.')
    grupos = []
    for titulo, col, valor in [('Estados', "'UF'[Nome]", R('Jair · perda UF')), ('Cidades', "'Município'[Rótulo]", R('Jair · perda cidade'))]:
        i = len(grupos)
        grupos.append(f'''VAR _g{i} = TOPN ( 4, ADDCOLUMNS ( VALUES ( {col} ), "@v", {valor} ), [@v], ASC, {col}, ASC )
VAR _h{i} = CONCATENATEX ( _g{i}, IF ( NOT ISBLANK ( [@v] ), "<div class='perda-linha'><span>" & {esc(col)} & "</span><b class='num'>−" & ({compacto('[@v]')}) & "</b></div>" ), "", [@v], ASC )''')
    desenho(P, 'Jair · HTML', '\n'.join(grupos)+'''
RETURN "<div class='tela jair'><div class='rot'>ABAIXO DE JAIR EM 2022 · PERDA EM VOTOS</div>"
    & "<div class='colunas'><div><h3>Estados</h3>" & IF ( _h0 = "", "Nenhum estado no recorte", _h0 ) & "</div>"
    & "<div><h3>Cidades</h3>" & IF ( _h1 = "", "Nenhuma cidade no recorte", _h1 ) & "</div></div>"
    & "<p>Flávio em 2026 menos Jair em 2022, ambos no 2º turno. São comparações de votos, não trajetórias individuais.</p></div>"''', 'Rankings separados de perdas estaduais e municipais; sinal sempre negativo, mesma conta em votos.')
    desenho(P, 'Jair · ALT', '"Onde Flávio recebeu menos votos que Jair em 2022: maiores perdas por estado e por cidade, no segundo turno. Perdas têm sinal negativo. Município sem base de 2022 não é tratado como zero."', 'Comparação histórica acessível.')


def desenho_ponte():
    # Conta serializada: i ^ nome ^ começo ^ fim ^ contribuição ^ tipo. O desenho só lê e posiciona.
    expr = f'''VAR _dados = {R('ponte · etapas')}
VAR _caminho = SUBSTITUTE ( _dados, "~", "|" )
VAR _linhas = ADDCOLUMNS ( GENERATESERIES ( 1, PATHLENGTH ( _caminho ) ), "@linha", SUBSTITUTE ( PATHITEM ( _caminho, [Value] ), "^", "|" ) )
VAR _t = ADDCOLUMNS ( _linhas, "@nome", PATHITEM ( [@linha], 2 ), "@de", VALUE ( PATHITEM ( [@linha], 3 ) ),
    "@ate", VALUE ( PATHITEM ( [@linha], 4 ) ), "@v", VALUE ( PATHITEM ( [@linha], 5 ) ), "@tipo", PATHITEM ( [@linha], 6 ) )
-- geometria
VAR _n = PATHLENGTH ( _caminho )
VAR _min = MIN ( 0, MINX ( _t, MIN ( [@de], [@ate] ) ) )
VAR _max = MAX ( 0, MAXX ( _t, MAX ( [@de], [@ate] ) ) )
VAR _amplitude = MAX ( 1, _max - _min )
VAR _passo = 1550 / _n
VAR _largura = MIN ( IF ( _n = 3, 170, 85 ), _passo * 0.68 )
VAR _zero = 32 + 254 * _max / _amplitude
VAR _barras = CONCATENATEX ( _t,
    VAR _x = 35 + ( [Value] - 0.5 ) * _passo
    VAR _y0 = 32 + 254 * ( _max - [@de] ) / _amplitude
    VAR _y1 = 32 + 254 * ( _max - [@ate] ) / _amplitude
    VAR _topo = MIN ( _y0, _y1 )
    VAR _altura = MAX ( 1.5, ABS ( _y0 - _y1 ) )
    VAR _cor = IF ( [@v] < 0, "var(--azul)", "var(--vermelho)" )
    VAR _eixo = [@tipo] <> "passo"
    VAR _label = IF ( _eixo, IF ( [@v] < 0, "Flávio", "Lula" ) & " +" & ({compacto('[@v]')}), ({compacto('[@v]',True)}))
    VAR _yy = IF ( _eixo, 309, IF ( _altura < 9, MAX ( _y0, _y1 ) + 23, MAX ( 28, _topo - 9 ) ) )
    VAR _corte = IF ( LEN ( [@nome] ) > 13, FIND ( " ", [@nome], 11, LEN ( [@nome] ) + 1 ), LEN ( [@nome] ) + 1 )
    RETURN "<g class='etapa'><title>" & {esc('[@nome]')} & ": " & FORMAT ( [@v], "+#,0;−#,0;0" ) & " votos na diferença</title>"
        & "<rect class='cor' x='" & FORMAT ( _x - _largura / 2, "0.00", "en-US" ) & "' y='" & FORMAT ( _topo, "0.00", "en-US" )
        & "' width='" & FORMAT ( _largura, "0.00", "en-US" ) & "' height='" & FORMAT ( _altura, "0.00", "en-US" ) & "' fill='" & _cor & "'/>"
        & IF ( [Value] < _n, "<line x1='" & FORMAT ( _x + _largura / 2, "0.00", "en-US" ) & "' x2='" & FORMAT ( _x + _passo - _largura / 2, "0.00", "en-US" )
            & "' y1='" & FORMAT ( _y1, "0.00", "en-US" ) & "' y2='" & FORMAT ( _y1, "0.00", "en-US" ) & "'/>", "" )
        & "<text class='v num' x='" & FORMAT ( _x, "0.00", "en-US" ) & "' y='" & FORMAT ( _yy, "0.00", "en-US" ) & "'>" & _label & "</text>"
        & "<text class='nome' text-anchor='middle' x='" & FORMAT ( _x, "0.00", "en-US" ) & "' y='324'>"
        & "<tspan>" & {esc('LEFT ( [@nome], _corte - 1 )')} & "</tspan><tspan x='" & FORMAT ( _x, "0.00", "en-US" ) & "' dy='16'>"
        & {esc('MID ( [@nome], _corte + 1, 200 )')} & "</tspan></text></g>", "", [Value], ASC )
RETURN "<div class='tela ponte'><svg viewBox='0 0 1620 355' width='1620' height='355'><line class='zero' x1='20' x2='1600' y1='"
    & FORMAT ( _zero, "0.00", "en-US" ) & "' y2='" & FORMAT ( _zero, "0.00", "en-US" ) & "'/>" & _barras & "</svg>"
    & "<div class='fecha'>Diferença para Lula: <b class='num'>" & FORMAT ( {R('ponte · início')}, "+#,0;−#,0;0" ) & "</b> + <b class='num'>"
    & FORMAT ( {R('ponte · soma das etapas')}, "#,0" ) & "</b> = <b class='num'>" & FORMAT ( {R('ponte · fim')}, "+#,0;−#,0;0" ) & "</b> votos</div></div>"'''
    desenho(P, 'Ponte · HTML', expr, 'Ponte em traço: lê etapas observadas, desenha acumulados e fecha a conta; mesmos sinais e escala para ambos os candidatos.')
    desenho(P, 'Ponte · ALT', f'''"Diferença Lula menos Flávio: " & FORMAT ( {R('ponte · início')}, "+#,0;−#,0;0" ) & " no primeiro turno, mais "
    & FORMAT ( {R('ponte · soma das etapas')}, "#,0" ) & " de mudança, igual a " & FORMAT ( {R('ponte · fim')}, "+#,0;−#,0;0" )
    & " no segundo. Até nove contribuições explícitas e demais agrupadas."''', 'Fechamento acessível da ponte.')


def spec_mapa():
    from desenho_t27_t28 import specs
    # Reaproveita só contornos e enquadramento do gerador do mapa; o novo dataset chega restrito às viradas.
    specs('T28')
    p = PBI/'spec/t28_mapa.json'
    s = json.loads(p.read_text(encoding='utf-8'))
    s['description'] = 'T28: apenas trocas de vencedor, 211 para Lula e uma para Flávio no Brasil; sem texto no canvas.'
    s['data'][0]['transform'] = [{'type':'formula','as':'tam','expr':'abs(datum.val)'}]
    # Contorno do país continua visível mesmo nos recortes sem troca.
    for d in s['data']:
        if d['name']=='contornosAtivos':
            d['transform'] = [{'type':'filter','expr':"length(data('ufsAtivas')) != 1 || indata('ufsAtivas','uf',datum.uf)"}]
    p.write_text(json.dumps(s, ensure_ascii=False, indent=1)+'\n',encoding='utf-8')


def main(somente_desenho=False):
    if not somente_desenho:
        contas(P)
        contas_ponte()
    desenhos()
    if not somente_desenho:
        spec_mapa()
    print('T28: ponte própria, mapa só de viradas e perdas frente a Jair; sem modelo ou Desktop.')


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--somente-desenho',action='store_true')
    main(ap.parse_args().somente_desenho)
