"""História do PT: contas, desenho e dois specs Vega 6. Não escreve PBIP nem consulta o motor."""
from __future__ import annotations

import json
from pathlib import Path
import desenho_t21 as T21
import estilo
from validar_dax_gerado import problemas

PBI = Path(__file__).resolve().parents[1]
ANOS = [1989, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022, 2026]
MAPA_W, MAPA_H = 810, 700
PASSO, TRANSICAO, ENTRADA = 1900, 650, 1800
REGUA_X = [104 + i * 74 for i in range(10)]
MAPA_NUMEROS = {
    'ano': {'x': 610, 'y': 96, 's': 48}, 'pt': {'x': 610, 'y': 210, 's': 70},
    'turno': {'x': 610, 'y': 128, 's': 17}, 'adv': {'x': 710, 'y': 309, 's': 15},
    'outros': {'x': 677, 'y': 334, 's': 15},
}
GRAFICO_W, GRAFICO_H = 750, 510
GRAFICO_X, GRAFICO_DIREITA, GRAFICO_ALTURA = 44, 18, 190
GRAFICO_TOPOS = [20, 280]
GRAFICO_MAXIMO = 70000000
GRAFICO_MARCAS = [0, 20000000, 40000000, 60000000]


def corpo_mapa_rotulos():
    """Textos fixos em HTML/Sora, atrás do canvas; valores que mudam no play são glifos no Vega."""
    css = (".labels29{color:var(--grafite)}.labels29 .lb{position:absolute;font-size:15px;line-height:22px;white-space:nowrap}"
           ".labels29 .ano{position:absolute;top:675px;width:68px;text-align:center;font-size:14px;line-height:18px;color:var(--tinta)}")
    labels = [(623, 110, 'º turno', 17), (610, 226, 'de 27 estados', 17),
              (610, 250, 'com o PT à frente', 15), (610, 295, 'Adversário:', 15), (610, 320, 'Outros:', 15),
              (610, 371, '1994 e 1998:', 15), (610, 394, 'decisão no 1º turno', 15),
              (610, 438, '1998 · CE: Ciro (PPS)', 14),
              (10, 584, 'Cor: vencedor · intensidade: vantagem sobre o 2º colocado', 14),
              (10, 608, 'PT: vermelho · adversário nacional: azul · outros: marrom', 14)]
    partes = [f"<div class='lb' style='left:{x}px;top:{y}px;font-size:{s}px'>{txt}</div>" for x, y, txt, s in labels]
    partes += [f"<div class='ano' style='left:{x-34}px'>{ano}</div>" for x, ano in zip(REGUA_X, ANOS)]
    return f"<style>{css}</style><div class='tela labels29'>{''.join(partes)}</div>{{{{content}}}}"


def corpo_grafico_rotulos():
    """Eixos e títulos na Sora embutida do HTML; geometria única compartilhada com as escalas Vega."""
    css = (".eixos29{color:var(--grafite)}.eixos29 .lbl{position:absolute;font-size:13px;line-height:18px;white-space:nowrap}"
           ".eixos29 .turno{position:absolute;font-size:14px;line-height:18px;font-weight:650}")
    partes = []
    for turno, topo in enumerate(GRAFICO_TOPOS, 1):
        partes.append(f"<div class='turno' style='left:{GRAFICO_X}px;top:{topo-20}px'>{turno}º TURNO</div>")
        for v in GRAFICO_MARCAS:
            y = topo + GRAFICO_ALTURA * (1 - v / GRAFICO_MAXIMO)
            partes.append(f"<div class='lbl' style='left:0;top:{y-9:.3f}px;width:36px;text-align:right'>{v//1000000} mi</div>")
        for ano in ANOS:
            x = GRAFICO_X + (GRAFICO_W-GRAFICO_X-GRAFICO_DIREITA) * (ano-ANOS[0]) / (ANOS[-1]-ANOS[0])
            partes.append(f"<div class='lbl' style='left:{x-25:.3f}px;top:{topo+GRAFICO_ALTURA+7}px;width:50px;text-align:center'>{ano}</div>")
    return f"<style>{css}</style><div class='tela eixos29'>{''.join(partes)}</div>{{{{content}}}}"


def gravar(nome, expr, desc, fmt='texto', conta=False):
    erros = problemas(expr, comentario_inline=True)
    if erros:
        raise ValueError(nome + ': ' + '; '.join(erros))
    sub = 'Contas' if conta else 'Desenho'
    p = PBI / 'dax/T29 História do PT' / sub / ('T29 · ' + nome + '.dax')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f'/*\n@pasta: T29 História do PT\\{sub}\n@formato: {fmt}\n@descricao: {desc}\n'
                 '@oraculo: dados/saida/pt_historico; PT-HISTORICO-METODO.md\n'
                 '@gerado: pbi/scripts/desenho_t29.py\n*/\n' + expr.strip() + '\n', encoding='utf-8')


def conta(nome, expr, desc, fmt='#,0'):
    gravar(nome, expr, desc, fmt, True)


def escape(expr):
    return f'''SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( {expr}, "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" ), """", "&quot;" ), "'", "&#39;" )'''


def medidas():
    for n, c in [('PT votos', 'VotosPT'), ('adversário votos', 'VotosAdversario'), ('válidos', 'Validos'),
                 ('aptos', 'Aptos'), ('comparecimento', 'Comparecimento')]:
        conta(n, f"SUM ( 'PT histórico Brasil'[{c}] )", 'Resultado nacional do ano e turno em contexto, com exterior; não acumular eleições.')
    for n, v in [('PT %', 'PT votos'), ('adversário %', 'adversário votos')]:
        conta(n, f'DIVIDE ( [T29 · {v}], [T29 · válidos] )', 'Fatia dos válidos no ano e turno.', '0.00%')
    for n, c in [('candidato PT', 'Candidato PT'), ('adversário', 'Adversário')]:
        conta(n, f"SELECTEDVALUE ( 'PT histórico Brasil'[{c}] )", 'Identidade nacional da candidatura do turno.', 'texto')
    for n, col in [('mapa · PT votos', 'VotosPT'), ('mapa · adversário votos', 'VotosAdversario'),
                   ('mapa · válidos', 'Validos'), ('mapa · vantagem votos', 'Vantagem vencedor')]:
        conta(n, f"SUM ( 'PT histórico mapa'[{col}] )", 'Resultado da UF no turno decisivo; vencedor efetivo entre todos os candidatos.')
    conta('mapa · margem', 'DIVIDE ( [T29 · mapa · vantagem votos], [T29 · mapa · válidos] )',
          'Vantagem real do vencedor sobre o segundo colocado, sobre os válidos. Mesma escala para todos os partidos.', '0.00%')
    for n, c in [('mapa · grupo', 'Grupo vencedor'), ('mapa · vencedor', 'Vencedor'),
                 ('mapa · partido vencedor', 'Partido vencedor'), ('mapa · candidato PT', 'Candidato PT'),
                 ('mapa · adversário', 'Adversário')]:
        conta(n, f"SELECTEDVALUE ( 'PT histórico mapa'[{c}] )", 'Identidade da candidatura no turno decisivo da UF.', 'texto')
    for nome, col in [('PT', 'VotosPT'), ('adversário', 'VotosAdversario')]:
        for turno in [1, 2]:
            conta(f'estado · {nome} {turno}º', f'''VAR _ano = SELECTEDVALUE ( 'PT histórico mapa'[Ano] )
RETURN CALCULATE ( SUM ( 'PT histórico UF'[{col}] ),
    'PT histórico UF'[Ano] = _ano, 'PT histórico UF'[Turno] = {turno} )''',
                  'Série estadual completa do dossiê. Ano vem da linha decisiva; turno ausente permanece BLANK, nunca zero.')
    conta('mapa · turno', "MAX ( 'PT histórico mapa'[Turno] )", 'Segundo turno quando houve; 1994 e 1998 no primeiro.', '0')
    for grupo, nome in [('PT', 'PT'), ('Adversário', 'adversário'), ('Outros', 'outros')]:
        conta(f'mapa · estados {nome}', f'''COALESCE ( CALCULATE ( COUNTROWS ( 'PT histórico mapa' ),
    REMOVEFILTERS ( 'UF' ), 'PT histórico mapa'[UF] <> "ZZ", 'PT histórico mapa'[Grupo vencedor] = "{grupo}" ), 0 )''',
              'Quantidade de UFs, entre 27, com cada vencedor no ano; exterior excluído, tooltip de UF não altera o país.')
    for nome, base, ano, turno in [('recorde', 'PT votos', 2026, 2), ('recorde anterior', 'PT votos', 2022, 2),
                                  ('fatia 2002', 'PT %', 2002, 2), ('fatia 2026', 'PT %', 2026, 2),
                                  ('aptos 1989', 'aptos', 1989, 1), ('aptos 2026', 'aptos', 2026, 1)]:
        conta(nome, f'''CALCULATE ( [T29 · {base}], REMOVEFILTERS ( 'PT histórico Brasil' ),
    'PT histórico Brasil'[Ano] = {ano}, 'PT histórico Brasil'[Turno] = {turno} )''',
              'Referência nacional fixa, com exterior; recorde por candidatura em um único turno.',
              '0.00%' if nome.startswith('fatia') else '#,0')
    conta('acima do recorde anterior', '[T29 · recorde] - [T29 · recorde anterior]', 'Diferença nominal entre os segundos turnos de 2026 e 2022.')
    gravar('Resposta · HTML', '''"<div class='tela h29'><div class='man sobe'><span class='num'>"
    & FORMAT ( [T29 · recorde], "#,0" ) & "</span> votos: o recorde presidencial</div>"
    & "<div class='txt sobe d2'>Lula teve a maior votação de uma candidatura em um turno de eleição presidencial direta no Brasil. "
    & "<b>" & FORMAT ( [T29 · acima do recorde anterior], "#,0" ) & " votos</b> acima da marca dele em 2022.</div></div>"''',
           'Manchete responde à pergunta; recorde em contagem, sem atribuir crescimento contínuo ou causalidade.')
    gravar('Resposta · ALT', '''"Lula recebeu " & FORMAT ( [T29 · recorde], "#,0" )
    & " votos, recorde de uma candidatura em um turno presidencial direto; "
    & FORMAT ( [T29 · acima do recorde anterior], "#,0" ) & " acima de 2022. Recorde em votos não significa recorde percentual."''', 'Manchete acessível.')
    gravar('Contexto · HTML', '''"<div class='tela contexto29'><div>Recorde em votos, não em fatia: <b>"
    & FORMAT ( [T29 · fatia 2002], "0.00%" ) & "</b> dos válidos em 2002 × <b>"
    & FORMAT ( [T29 · fatia 2026], "0.00%" ) & "</b> em 2026.</div><div>O eleitorado também cresceu: <b>"
    & FORMAT ( [T29 · aptos 1989] / 1e6, "0.0" ) & " mi</b> em 1989 → <b>"
    & FORMAT ( [T29 · aptos 2026] / 1e6, "0.0" ) & " mi</b> em 2026.</div></div>"''', 'Válidos e eleitorado: denominadores explícitos da comparação histórica.')
    gravar('Contexto · ALT', '''"PT: " & FORMAT ( [T29 · fatia 2002], "0.00%" ) & " dos válidos em 2002 e "
    & FORMAT ( [T29 · fatia 2026], "0.00%" ) & " em 2026. Eleitorado: "
    & FORMAT ( [T29 · aptos 1989] / 1e6, "0.0" ) & " milhões em 1989 e "
    & FORMAT ( [T29 · aptos 2026] / 1e6, "0.0" ) & " milhões em 2026."''', 'Denominadores acessíveis.')
    gravar('Mapa · série', '''VAR _anos = ADDCOLUMNS ( VALUES ( 'PT histórico mapa'[Ano] ),
    "@grupo", [T29 · mapa · grupo], "@m", [T29 · mapa · margem], "@t", [T29 · mapa · turno] )
RETURN CONCATENATEX ( _anos,
    'PT histórico mapa'[Ano] & "|" & [@grupo] & "|" & FORMAT ( [@m], "0.00000000", "en-US" ) & "|" & [@t],
    ";", 'PT histórico mapa'[Ano], ASC )''', 'Campo de desenho do Deneb: valores observados de cada UF, uma linha original por UF.')
    gravar('Mapa · quadros', '''VAR _anos = ADDCOLUMNS ( VALUES ( 'PT histórico mapa'[Ano] ),
    "@pt", [T29 · mapa · estados PT], "@adv", [T29 · mapa · estados adversário], "@outros", [T29 · mapa · estados outros],
    "@t", [T29 · mapa · turno] )
RETURN CONCATENATEX ( _anos,
    'PT histórico mapa'[Ano] & "|" & [@t] & "|" & [@pt] & "|" & [@adv] & "|" & [@outros],
    ";", 'PT histórico mapa'[Ano], ASC )''', 'Contadores calculados no DAX, nunca agregados pelo Vega.')
    gravar('Mapa · ALT', '"Dez mapas estaduais de 1989 a 2026, no turno decisivo. Play automático, pausa e anos clicáveis. Cor = vencedor real; intensidade = vantagem sobre o segundo colocado. Em 1998, Ciro venceu o Ceará. Passe numa UF para ler sua série."', 'Mapa animado acessível, estado estático em 2026.')
    gravar('Gráfico · ALT', '"Votos do PT e do principal adversário em cada eleição, em dois painéis com a mesma escala. Não houve segundo turno em 1994 ou 1998; a linha é interrompida. A queda de 2014 para 2018 permanece visível. Lula bate o recorde em 2026."', 'Série com os turnos separados e lacunas preservadas.')
    tooltip_medidas()


def tooltip_medidas():
    # Só leituras por item; sem mudança de contexto ou conta escondida no desenho.
    gravar('Estado · HTML', f'''VAR _nome = {escape("SELECTEDVALUE ( 'UF'[Nome], \"Estado\" )")}
VAR _anos = ADDCOLUMNS ( VALUES ( 'PT histórico mapa'[Ano] ),
    "@pt1", [T29 · estado · PT 1º], "@pt2", [T29 · estado · PT 2º],
    "@adv1", [T29 · estado · adversário 1º], "@adv2", [T29 · estado · adversário 2º],
    "@partido", [T29 · mapa · partido vencedor], "@t", [T29 · mapa · turno] )
VAR _linhas = CONCATENATEX ( _anos,
    "<tr><td>" & 'PT histórico mapa'[Ano] & " · " & [@t] & "º</td><td>" & FORMAT ( [@pt1] / 1e6, "0.00" ) & " / "
    & IF ( ISBLANK ( [@pt2] ), "—", FORMAT ( [@pt2] / 1e6, "0.00" ) )
    & "</td><td>" & FORMAT ( [@adv1] / 1e6, "0.00" ) & " / "
    & IF ( ISBLANK ( [@adv2] ), "—", FORMAT ( [@adv2] / 1e6, "0.00" ) )
    & "</td><td>" & {escape('[@partido]')} & "</td></tr>",
    "", 'PT histórico mapa'[Ano], ASC )
RETURN "<div class='tela dossier29'><div class='fita'></div><div class='rot'>DOSSIÊ · HISTÓRIA DO ESTADO</div>"
    & "<h2>" & _nome & "</h2><p>Votos em milhões · 1º / 2º turno. Traço: não houve 2º turno.</p>"
    & "<table><thead><tr><th>Ano · decisão</th><th class='lula'>PT · 1º / 2º</th><th class='flavio'>Adv. · 1º / 2º</th><th>Venceu</th></tr></thead>"
    & "<tbody>" & _linhas & "</tbody></table><p>PT: Lula; Dilma em 2010/2014; Haddad em 2018.</p>"
    & "<p>Adversário é o mais votado fora do PT no país; o vencedor da UF pode ser outro. Em 1998, Ceará: Ciro (PPS).</p>"
    & "<div class='mao'>cada estado tem sua história</div>"
    & "<small>Fontes: TSE · versões históricas descritas no i da página.</small></div>"''', 'Dossiê estadual da série, sem presumir que o principal adversário venceu toda UF não petista.')
    gravar('Estado · ALT', '"Dossiê do estado: votos do PT e do principal adversário nacional nos dois turnos de cada eleição, e partido vencedor no turno decisivo. Em 1994 e 1998 não houve segundo turno. Valores em milhões; versões históricas no i."', 'Série estadual acessível.')
    gravar('Eleição · HTML', f'''VAR _ano = SELECTEDVALUE ( 'PT histórico Brasil'[Ano] )
VAR _turno = SELECTEDVALUE ( 'PT histórico Brasil'[Turno] )
VAR _pt = {escape('[T29 · candidato PT]')}
VAR _adv = {escape('[T29 · adversário]')}
RETURN "<div class='tela dossier29'><div class='fita'></div><div class='rot'>DOSSIÊ · ELEIÇÃO PRESIDENCIAL</div>"
    & "<h2>" & _ano & " · " & _turno & "º turno</h2><p>Brasil, com exterior · comparação no mesmo turno.</p>"
    & "<div class='par'><b class='lula'>" & _pt & " · PT</b><strong>" & FORMAT ( [T29 · PT votos], "#,0" )
    & " votos</strong><span>" & FORMAT ( [T29 · PT %], "0.00%" ) & " dos válidos</span></div>"
    & "<div class='par'><b class='flavio'>" & _adv & "</b><strong>" & FORMAT ( [T29 · adversário votos], "#,0" )
    & " votos</strong><span>" & FORMAT ( [T29 · adversário %], "0.00%" ) & " dos válidos</span></div>"
    & "<p>" & FORMAT ( [T29 · aptos], "#,0" ) & " eleitores aptos; " & FORMAT ( [T29 · comparecimento], "#,0" )
    & " compareceram.</p><small>Fontes: TSE · versões históricas descritas no i.</small></div>"''', 'Os mesmos votos e percentuais para as duas candidaturas, mais participação.')
    gravar('Eleição · ALT', '''"Eleição " & SELECTEDVALUE ( 'PT histórico Brasil'[Ano] ) & ", "
    & SELECTEDVALUE ( 'PT histórico Brasil'[Turno] ) & "º turno. " & [T29 · candidato PT] & ": "
    & FORMAT ( [T29 · PT votos], "#,0" ) & " votos; " & [T29 · adversário] & ": "
    & FORMAT ( [T29 · adversário votos], "#,0" ) & " votos. Dossiê com válidos e participação."''', 'Dossiê nacional acessível.')


def mapa_spec():
    c = estilo.COR
    sx = '(width / 810)'
    anos_x = REGUA_X
    # Contornos em rabisco e comprimentos reaproveitados da T21; os dados históricos vêm do motor.
    caminhos = T21.ufs()
    signals = [
        {'name': 'estatico', 'init': '!(windowSize()[0] > 0)'},
        {'name': 'reduceMotion', 'value': False, 'description': 'A main pode fixar true para exportação sem movimento.'},
        {'name': 't0', 'init': 'now()'},
        {'name': 'anosLista', 'value': ANOS},
        {'name': 'temQuadros', 'update': "length(data('quadros')) == 10"},
        {'name': 'estado', 'init': 'estatico || reduceMotion ? {de:9,para:9,t0:0,tocando:false,iniciado:true} : {de:0,para:0,t0:0,tocando:false,iniciado:false}',
         'on': [
             {'events': '@marcaPlay:click, @marcaIcone:click', 'update':
              'estado.tocando ? {de:estado.para,para:estado.para,t0:0,tocando:false,iniciado:true} : '
              '{de:estado.para,para:estado.para == 9 ? 0 : estado.para,t0:now(),tocando:true,iniciado:true}'},
             {'events': '@marcaAno:click, @marcaAnoAlvo:click', 'update':
              '{de:estado.para,para:datum.i,t0:now(),tocando:false,iniciado:true}'},
             {'events': 'timer{16}', 'update': '!estatico && !reduceMotion && temQuadros && !estado.iniciado ? '
              '{de:0,para:0,t0:now(),tocando:true,iniciado:true} : '
              f'(!estatico && !reduceMotion && estado.tocando && now()-estado.t0 >= {PASSO} ? '
              '(estado.para < 9 ? {de:estado.para,para:estado.para+1,t0:now(),tocando:estado.para+1 < 9,iniciado:true} : '
              '{de:9,para:9,t0:estado.t0,tocando:false,iniciado:true}) : estado)'}]},
        {'name': 'agora', 'init': 'now()', 'on': [{'events': 'timer{16}', 'update':
            f'estatico || reduceMotion ? agora : (estado.tocando || now()-estado.t0 < {TRANSICAO+100} || '
            f'now()-t0 < {ENTRADA+100} ? now() : agora)'}]},
        {'name': 'entrada', 'update': f'estatico || reduceMotion ? 1 : clamp((agora-t0)/{ENTRADA},0,1)'},
        {'name': 'prog', 'update': f'estatico || reduceMotion || estado.t0 == 0 ? 1 : clamp((agora-estado.t0)/{TRANSICAO},0,1)'},
        {'name': 'e', 'update': 'prog*prog*(3-2*prog)'},
        {'name': 'anoAtual', 'update': 'anosLista[estado.para]'},
        {'name': 'sobre', 'value': None, 'on': [{'events': '@marcaUF:mouseover', 'update': 'datum.uf'},
                                              {'events': '@marcaUF:mouseout', 'update': 'null'}]},
        {'name': 'cfg', 'value': MAPA_NUMEROS},
        {'name': 'glifos', 'value': T21.glifos()},
        {'name': 'txtAno', 'update': "''+anoAtual"},
        {'name': 'txtPt', 'update': "length(data('quadros')) == 10 ? ''+round(data('quadros')[estado.de].pt + (data('quadros')[estado.para].pt-data('quadros')[estado.de].pt)*e) : ''"},
        {'name': 'txtTurno', 'update': "length(data('quadros')) == 10 ? ''+data('quadros')[estado.para].turno : ''"},
        *[{'name': nome, 'update': f"length(data('quadros')) == 10 ? ''+round(data('quadros')[estado.de].{campo} + (data('quadros')[estado.para].{campo}-data('quadros')[estado.de].{campo})*e) : ''"}
          for nome, campo in [('txtAdv', 'adv'), ('txtOutros', 'outros')]],
    ]
    data = [
        {'name': 'dataset'},
        {'name': 'quadros', 'source': 'dataset', 'transform': [
            {'type': 'aggregate', 'groupby': ['quadros']},
            {'type': 'formula', 'as': 'partes', 'expr': "split(datum.quadros,';')"},
            {'type': 'flatten', 'fields': ['partes'], 'as': ['parte']},
            *[{'type': 'formula', 'as': field, 'expr': f"toNumber(split(datum.parte,'|')[{i}])"}
              for i, field in enumerate(['ano', 'turno', 'pt', 'adv', 'outros'])],
            {'type': 'collect', 'sort': {'field': 'ano'}},
            {'type': 'window', 'ops': ['row_number'], 'as': ['ordem']},
            {'type': 'formula', 'as': 'i', 'expr': 'datum.ordem-1'}]},
        {'name': 'geometria', 'values': caminhos},
        {'name': 'ufsDados', 'source': 'dataset', 'transform': [
            {'type': 'formula', 'as': 'partes', 'expr': "split(datum.serie,';')"},
            {'type': 'formula', 'as': 'atual', 'expr': "split(datum.partes[estado.para],'|')"},
            {'type': 'formula', 'as': 'anterior', 'expr': "split(datum.partes[estado.de],'|')"},
            {'type': 'lookup', 'from': 'geometria', 'key': 'uf', 'fields': ['uf'], 'values': ['r', 'l'], 'as': ['path', 'comp']},
            {'type': 'filter', 'expr': 'isValid(datum.path)'},
            {'type': 'formula', 'as': 'corAtual', 'expr': "datum.atual[1] == 'PT' ? scale('corPT',toNumber(datum.atual[2])) : (datum.atual[1] == 'Adversário' ? scale('corAdv',toNumber(datum.atual[2])) : scale('corOutros',toNumber(datum.atual[2])))"},
            {'type': 'formula', 'as': 'corAnterior', 'expr': "datum.anterior[1] == 'PT' ? scale('corPT',toNumber(datum.anterior[2])) : (datum.anterior[1] == 'Adversário' ? scale('corAdv',toNumber(datum.anterior[2])) : scale('corOutros',toNumber(datum.anterior[2])))"}]},
        {'name': 'algarismos', 'values': [{'k': k, 'i': i} for k in MAPA_NUMEROS for i in range(4)], 'transform': [
            {'type': 'formula', 'as': 'txt', 'expr': "datum.k == 'ano' ? txtAno : (datum.k == 'pt' ? txtPt : (datum.k == 'turno' ? txtTurno : (datum.k == 'adv' ? txtAdv : txtOutros)))"},
            {'type': 'filter', 'expr': 'datum.i < length(datum.txt)'},
            {'type': 'formula', 'as': 'ch', 'expr': 'substring(datum.txt,datum.i,datum.i+1)'},
            {'type': 'formula', 'as': 'w', 'expr': 'glifos[datum.ch].w'},
            {'type': 'window', 'groupby': ['k'], 'sort': {'field': 'i'}, 'ops': ['sum'], 'fields': ['w'], 'as': ['cum']},
            {'type': 'formula', 'as': 'x0', 'expr': 'datum.cum-datum.w'}]},
    ]
    marks = [
        {'type': 'path', 'name': 'marcaUF', 'from': {'data': 'ufsDados'}, 'encode': {'update': {
            'path': {'field': 'path'}, 'x': {'signal': f'10*{sx}'}, 'y': {'signal': f'8*{sx}'},
            'scaleX': {'signal': f'.57*{sx}'}, 'scaleY': {'signal': f'.57*{sx}'},
            'fill': {'field': 'corAtual'}, 'fillOpacity': {'signal': "(sobre && sobre != datum.uf ? .40 : .94)*clamp(entrada*2-.4,0,1)*e"},
            'stroke': {'value': c['grafite']}, 'strokeWidth': {'signal': 'sobre == datum.uf ? 2 : .8'},
            'strokeDash': {'signal': '[datum.comp*.57+4,datum.comp*.57+4]'},
            'strokeDashOffset': {'signal': '(datum.comp*.57+4)*(1-entrada)'}, 'cursor': {'value': 'help'}}}},
        # A cor anterior persiste por baixo da nova: esmaecimento de uma eleição para a outra, sem piscar em branco.
        {'type': 'path', 'name': 'marcaCorAnterior', 'interactive': False, 'from': {'data': 'ufsDados'},
         'encode': {'update': {'path': {'field': 'path'}, 'x': {'signal': f'10*{sx}'}, 'y': {'signal': f'8*{sx}'},
             'scaleX': {'signal': f'.57*{sx}'}, 'scaleY': {'signal': f'.57*{sx}'}, 'fill': {'field': 'corAnterior'},
             'opacity': {'signal': "(1-e)*clamp(entrada*2-.4,0,1)*(sobre && sobre != datum.uf ? .4 : 1)"}}}},
        {'type': 'path', 'from': {'data': 'algarismos'}, 'interactive': False, 'encode': {'update': {
            'path': {'signal': 'glifos[datum.ch].d'},
            'x': {'signal': f'(cfg[datum.k].x+datum.x0*cfg[datum.k].s/1000)*{sx}'},
            'y': {'signal': f'cfg[datum.k].y*{sx}'},
            'scaleX': {'signal': f'cfg[datum.k].s/1000*{sx}'}, 'scaleY': {'signal': f'-cfg[datum.k].s/1000*{sx}'},
            'fill': {'value': c['tinta']}}}},
        {'type': 'rule', 'interactive': False, 'encode': {'update': {
            'x': {'signal': f'104*{sx}'}, 'x2': {'signal': f'770*{sx}'}, 'y': {'signal': f'663*{sx}'}, 'stroke': {'value': c['areia']}}}},
        {'type': 'rect', 'name': 'marcaAnoAlvo', 'from': {'data': 'quadros'}, 'encode': {'update': {
            'xc': {'signal': f'{anos_x}[datum.i]*{sx}'}, 'width': {'signal': f'66*{sx}'},
            'y': {'signal': f'640*{sx}'}, 'height': {'signal': f'58*{sx}'}, 'fill': {'value': 'transparent'}, 'cursor': {'value': 'pointer'}}}},
        {'type': 'symbol', 'name': 'marcaAno', 'from': {'data': 'quadros'}, 'encode': {'update': {
            'x': {'signal': f'{anos_x}[datum.i]*{sx}'}, 'y': {'signal': f'655*{sx}'},
            'size': {'signal': f'(datum.i == estado.para ? 280 : 110)*{sx}*{sx}'},
            'fill': {'signal': f"datum.i == estado.para ? '{c['tinta']}' : '{c['papel']}'"},
            'stroke': {'value': c['tinta']}, 'cursor': {'value': 'pointer'}}}},
        {'type': 'symbol', 'name': 'marcaPlay', 'encode': {'update': {
            'x': {'signal': f'30*{sx}'}, 'y': {'signal': f'660*{sx}'}, 'size': {'signal': f'2500*{sx}*{sx}'},
            'fill': {'value': c['tinta']}, 'cursor': {'value': 'pointer'}}}},
        {'type': 'path', 'name': 'marcaIcone', 'encode': {'update': {
            'x': {'signal': f'30*{sx}'}, 'y': {'signal': f'660*{sx}'}, 'scaleX': {'signal': sx}, 'scaleY': {'signal': sx},
            'path': {'signal': "estado.tocando ? 'M-8,-10L-3,-10L-3,10L-8,10Z M3,-10L8,-10L8,10L3,10Z' : 'M-6,-11L11,0L-6,11Z'"},
            'fill': {'value': c['papel']}, 'cursor': {'value': 'pointer'}}}},
    ]
    return {'$schema': 'https://vega.github.io/schema/vega/v6.json',
            'description': 'T29: 27 UFs, vencedor efetivo, dez eleições. Autoplay finito, pausa e régua; __row__ original preservado para dossiê UF.',
            'width': {'signal': 'pbiContainerWidth'}, 'height': {'signal': 'pbiContainerHeight'}, 'padding': 0,
            'autosize': {'type': 'none', 'contains': 'padding'}, 'background': None,
            'signals': signals, 'data': data, 'scales': [
                {'name': n, 'type': 'linear', 'domain': [0, .60], 'range': [c[meio], c[fim]], 'clamp': True}
                for n, meio, fim in [('corPT', 'rosa', 'vermelho'), ('corAdv', 'azul_claro', 'azul'),
                                    ('corOutros', 'areia', 'marrom')]], 'marks': marks}


def grafico_spec():
    c = estilo.COR
    # Anos numéricos no eixo: o intervalo 1989–1994 continua com cinco anos.
    linhas = []
    for turno in [1, 2]:
        data_nome = f'painel{turno}'
        linhas.append({'name': data_nome, 'source': 'curvas', 'transform': [{'type': 'filter', 'expr': f'datum.turno == {turno}'}]})
    groups = []
    for turno in [1, 2]:
        ytop = GRAFICO_TOPOS[turno-1]
        groups.append({'type': 'group', 'name': f'grupoTurno{turno}', 'encode': {'update': {
            'x': {'value': GRAFICO_X}, 'y': {'value': ytop}, 'width': {'signal': f'width-{GRAFICO_X+GRAFICO_DIREITA}'}, 'height': {'value': GRAFICO_ALTURA}}},
            'signals': [{'name': 'width', 'update': f'pbiContainerWidth-{GRAFICO_X+GRAFICO_DIREITA}'}, {'name': 'height', 'value': GRAFICO_ALTURA}],
            'scales': [{'name': 'x', 'type': 'linear', 'domain': [1989, 2026], 'range': [0, {'signal': 'width'}], 'zero': False},
                       {'name': 'y', 'type': 'linear', 'domain': [0, GRAFICO_MAXIMO], 'range': [{'signal': 'height'}, 0], 'zero': True}],
            'axes': [{'orient': 'left', 'scale': 'y', 'values': GRAFICO_MARCAS,
                      'grid': True, 'domain': False, 'ticks': False, 'labels': False, 'gridColor': c['areia']},
                     {'orient': 'bottom', 'scale': 'x', 'values': ANOS, 'domainColor': c['areia'],
                      'tickSize': 3, 'labels': False}],
            'marks': [
                {'type': 'group', 'from': {'facet': {'name': f'serie{turno}', 'data': f'painel{turno}', 'groupby': 'lado'}},
                 'marks': [{'type': 'line', 'interactive': False, 'from': {'data': f'serie{turno}'}, 'sort': {'field': 'datum.ano'},
                            'encode': {'update': {'x': {'scale': 'x', 'field': 'ano'}, 'y': {'scale': 'y', 'field': 'votos'},
                                'defined': {'signal': 'isValid(datum.votos)'}, 'stroke': {'signal': f"datum.lado == 'pt' ? '{c['vermelho']}' : '{c['azul']}'"},
                                'strokeWidth': {'value': 2.5},
                                'opacity': {'signal': '!sobreLado || sobreLado == datum.lado ? 1 : .4'}}}},
                           {'type': 'symbol', 'name': f'marcaVoto{turno}', 'from': {'data': f'serie{turno}'},
                            'encode': {'update': {'x': {'scale': 'x', 'field': 'ano'}, 'y': {'scale': 'y', 'field': 'votos'},
                                'opacity': {'signal': 'isValid(datum.votos) ? (!sobreLado || sobreLado == datum.lado ? 1 : .4) : 0'}, 'size': {'value': 70},
                                'fill': {'signal': f"datum.lado == 'pt' ? '{c['vermelho']}' : '{c['azul']}'"},
                                'stroke': {'value': c['papel']}, 'strokeWidth': {'value': 1},
                                'tooltip': {'signal': "datum.ano+' · '+datum.turno+'º turno'"}}}}]},
            ]})
    return {'$schema': 'https://vega.github.io/schema/vega/v6.json', 'description':
            'T29: PT e principal adversário nacional, dois painéis e mesma escala de votos. Segundo turno interrompido em 1994/1998, sem inventar resultado.',
            'width': {'signal': 'pbiContainerWidth'}, 'height': {'signal': 'pbiContainerHeight'}, 'padding': 0,
            'autosize': {'type': 'none', 'contains': 'padding'}, 'background': None,
            'signals': [{'name': 'sobreLado', 'value': None, 'on': [
                {'events': '@marcaVoto1:mouseover, @marcaVoto2:mouseover', 'update': 'datum.lado'},
                {'events': '@marcaVoto1:mouseout, @marcaVoto2:mouseout', 'update': 'null'}]}],
            'data': [{'name': 'dataset'},
                     {'name': 'ausencias', 'values': [{'ano': a, 'turno': 2, 'pt': None, 'adv': None} for a in [1994, 1998]]},
                     {'name': 'curvas', 'source': ['dataset', 'ausencias'], 'transform': [
                         {'type': 'fold', 'fields': ['pt', 'adv'], 'as': ['lado', 'votos']},
                         {'type': 'collect', 'sort': {'field': ['turno', 'lado', 'ano']}}]}, *linhas],
            'marks': groups}


def main():
    medidas()
    for nome, spec in [('mapa', mapa_spec()), ('votos', grafico_spec())]:
        p = PBI / f'spec/t29_{nome}.json'
        p.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('T29: contas, desenhos e specs gerados. Modelo e Desktop preservados.')


if __name__ == '__main__':
    main()
