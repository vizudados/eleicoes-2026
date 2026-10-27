"""Prepara somente o Encerramento: votos exatos, origens e lotes de até 50 mil votos.

Cada fragmento tem uma origem real e um destino; a soma dos fragmentos preserva
todos os votos de cada município e do exterior. Não sorteia nem estima votos.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

PROJETO = Path(__file__).resolve().parents[1]
RAIZ = PROJETO.parents[1]
SAIDA = PROJETO / 'public/dados/encerramento.json'
ROTEIRO = PROJETO / 'src/encerramento/roteiro.json'
UNIDADE = 50_000
ESPERADO = {'lula': 64_256_232, 'flavio': 59_826_041}


def ler_csv(nome):
    with (RAIZ / 'dados/pbi' / nome).open(encoding='utf-8-sig', newline='') as arq:
        linhas = [r for r in csv.DictReader(arq) if r['ano'] == '2026']
    for r in linhas:
        for c in ('pt', 'adv', 'validos'):
            r[c] = int(r[c])
        if min(r['pt'], r['adv']) < 0 or r['pt'] + r['adv'] != r['validos']:
            raise ValueError(f'Votos inválidos em {nome}: {r}')
    return linhas


def repartir(total, pesos):
    """Quantidades inteiras pela maior sobra; a soma fica exata e a ordem é fixa."""
    quotas = [total * p / sum(pesos) for p in pesos]
    partes = [math.floor(q) for q in quotas]
    ordem = sorted(range(len(pesos)), key=lambda i: (-(quotas[i] - partes[i]), i))
    for i in ordem[:total - sum(partes)]:
        partes[i] += 1
    return partes


def assentos(quantidade, h):
    """Arcos completos e equidistantes, ordenados pelo ângulo entre todas as filas.

    Há um único assento no eixo; os demais formam pares geométricos exatos.
    A ordem dos empates angulares também é espelhada.
    """
    raios = [h['raioInterno'] + i * (h['raioExterno'] - h['raioInterno']) / (h['fileiras'] - 1)
             for i in range(h['fileiras'])]
    pares = repartir(quantidade // 2, raios)
    fila_central = 0  # Arco degenerado no centro da base: fecha o semicírculo sem entalhe.
    direita = []
    for fila, (raio, n_pares) in enumerate(zip(raios, pares)):
        n = 2 * n_pares + int(fila == fila_central)
        for j in range(n_pares):
            theta = math.pi * j / (n - 1)
            direita.append({'x': h['x'] + raio * math.cos(theta),
                            'y': h['base'] - raio * math.sin(theta), 'fila': fila, 'angulo': theta})
    direita.sort(key=lambda a: (a['angulo'], a['fila']))
    centro = {'x': h['x'], 'y': h['base'] - raios[fila_central], 'fila': fila_central, 'angulo': math.pi / 2}
    esquerda = [dict(a, x=2 * h['x'] - a['x'], angulo=math.pi - a['angulo']) for a in reversed(direita)]
    return direita + [centro] + esquerda


def preparar():
    roteiro = json.loads(ROTEIRO.read_text(encoding='utf-8'))
    capa = json.loads((PROJETO / 'public/dados/capa.json').read_text(encoding='utf-8'))
    mun, ufs = ler_csv('municipio_2turno.csv'), ler_csv('uf_2turno.csv')
    if len(mun) != 5571 or len({r['cd_ibge'] for r in mun}) != len(mun):
        raise ValueError('Esperados 5.571 municípios únicos em 2026.')
    if len(ufs) != 28 or len({r['uf'] for r in ufs}) != 28:
        raise ValueError('Esperadas 27 UFs e exterior, sem duplicação.')
    exterior, = [r for r in ufs if r['uf'] == 'ZZ']
    totais = {c: sum(r[col] for r in ufs) for c, col in [('lula', 'pt'), ('flavio', 'adv')]}
    if totais != ESPERADO:
        raise ValueError(f'Total nacional inesperado: {totais}')
    for c, col in [('lula', 'pt'), ('flavio', 'adv')]:
        if sum(r[col] for r in mun) + exterior[col] != totais[c]:
            raise ValueError(f'Municípios + exterior não fecham: {c}')

    cm = capa['municipios']
    centros = {cod: (x, y) for cod, x, y in zip(cm['cd_ibge'], cm['x'], cm['y'])}
    sem_coordenada = set(r['cd_ibge'] for r in mun) - centros.keys()
    if sem_coordenada != {'5101837'}:
        raise ValueError(f'Cobertura geográfica inesperada: {sem_coordenada}')
    boa = roteiro['boaEsperanca']
    # Aproximação expressamente autorizada: média dos centroides dos municípios
    # de origem. Nenhuma coordenada fictícia fora do mapa é criada.
    centros[boa['codigo']] = tuple(sum(centros[c][i] for c in boa['municipiosOrigem']) / 2 for i in (0, 1))
    mapa = roteiro['mapa']
    origens = []
    for r in sorted(mun, key=lambda r: r['cd_ibge']) + [dict(exterior, cd_ibge='ZZ')]:
        cod = r['cd_ibge']
        geografia = cod in centros
        if geografia:
            x, y = centros[cod]
            x = mapa['x'] + (x - 960) * mapa['escala']
            y = mapa['y'] + (y - 583) * mapa['escala']
        else:
            x, y = roteiro['exterior']['x'], roteiro['exterior']['y']
        origens.append({'id': cod, 'x': round(x, 3), 'y': round(y, 3), 'mapa': geografia,
                        'lula': r['pt'], 'flavio': r['adv']})

    # Fronteiras angulares globais: Flávio entra da esquerda e Lula da direita.
    # A fatia entre uma fronteira e seu espelho contém 44 pares + centro.
    comum = min(totais.values())
    lotes, fragmentos = [], []
    h = roteiro['hemiciclo']
    n_comuns = math.ceil(comum / UNIDADE)
    n_extras = math.ceil(abs(totais['lula'] - totais['flavio']) / UNIDADE)
    n_total = 2 * n_comuns + n_extras
    lugares = assentos(n_total, h)
    for candidato in ('flavio', 'lula'):
        pesos = [UNIDADE] * (comum // UNIDADE)
        if comum % UNIDADE:
            pesos.append(comum % UNIDADE)
        extra = totais[candidato] - comum
        if extra:
            pesos.extend([UNIDADE] * n_extras)
            # A fração da cunha fica no único assento central, preservando a
            # simetria tanto das posições quanto das áreas dos 44 pares.
            pesos[n_comuns + n_extras // 2] = extra - UNIDADE * (n_extras - 1)
        primeiros = len(lotes)
        for i, votos in enumerate(pesos):
            diferenca = i >= n_comuns
            if diferenca:
                ordem = i
            else:
                ordem = n_total - 1 - i if candidato == 'flavio' else i
            lugar = lugares[ordem]
            # Mesma semente/tempo no par; sem prioridade para uma candidatura.
            acaso = ((i * 73 + 19) % 997) / 996
            janela = roteiro['partidasDiferenca'] if diferenca else roteiro['partidas']
            inicio = janela[0] + acaso * (janela[1] - janela[0])
            duracao = roteiro['vooDiferenca'] if diferenca else roteiro['voo']
            lotes.append({'candidato': candidato, 'votos': votos, 'x': round(lugar['x'], 6), 'y': round(lugar['y'], 6),
                          'r': round(h['raioPonto'] * math.sqrt(votos / UNIDADE), 6), 'fila': lugar['fila'],
                          'angulo': lugar['angulo'], 'ordemAngular': ordem,
                          'partida': inicio, 'duracao': duracao, 'diferenca': diferenca})
        # Interseção dos intervalos cumulativos origem × lote: conserva cada voto
        # municipal, incluindo os pequenos municípios e as frações de lote.
        destino, livre = primeiros, pesos[0]
        for indice, origem in enumerate(origens):
            restante = origem[candidato]
            while restante:
                votos = min(restante, livre)
                fragmentos.append([indice, destino, votos])
                restante -= votos
                livre -= votos
                if livre == 0:
                    destino += 1
                    if destino < primeiros + len(pesos):
                        livre = lotes[destino]['votos']

    arquivos = ['dados/pbi/municipio_2turno.csv', 'dados/pbi/uf_2turno.csv',
                'capa/remotion/public/dados/capa.json', 'capa/remotion/src/encerramento/roteiro.json']
    return {'unidade': UNIDADE, 'totais': totais, 'diferenca': abs(totais['lula'] - totais['flavio']),
            'municipais': {c: sum(r[c] for r in origens if r['id'] != 'ZZ') for c in totais},
            'exterior': {c: exterior[col] for c, col in [('lula', 'pt'), ('flavio', 'adv')]},
            'fontesSha256': {n: hashlib.sha256((RAIZ / n).read_bytes()).hexdigest() for n in arquivos},
            'boaEsperanca': dict(boa, centroNaProjecaoDaCapa=list(centros[boa['codigo']])),
            'contorno': capa['contorno']['d1'], 'ilhas': [d['d'] for d in capa['ilhas']],
            'divisas': [d['d'] for d in capa['divisas']],
            'origens': origens, 'lotes': lotes, 'fragmentos': fragmentos}


def main():
    dados = preparar()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f'Encerramento: {len(dados["origens"])} origens, {len(dados["lotes"])} lotes, '
          f'{len(dados["fragmentos"])} fragmentos; Lula {dados["totais"]["lula"]:,}, '
          f'Flávio {dados["totais"]["flavio"]:,}, diferença {dados["diferenca"]:,}.')


if __name__ == '__main__':
    main()
