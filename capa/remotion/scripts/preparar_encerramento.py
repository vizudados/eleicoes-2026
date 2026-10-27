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


def assentos(quantidade, extras, h):
    """Pares espelhados e 89 posições à esquerda do eixo, no corredor central.

    O eixo compara duas parcelas iguais; não é um corte de 50% dos válidos.
    """
    raios = [h['raioInterno'] + i * (h['raioExterno'] - h['raioInterno']) / (h['fileiras'] - 1)
             for i in range(h['fileiras'])]
    angulos = [math.acos(h['corredor'] / r) for r in raios]
    quantidades = repartir(quantidade, [r * a for r, a in zip(raios, angulos)])
    comuns = []
    for fila, (raio, angulo, n) in enumerate(zip(raios, angulos, quantidades)):
        for j in range(n):
            theta = (j + 0.5) * angulo / n
            comuns.append((raio * math.cos(theta), h['base'] - raio * math.sin(theta), fila))
    # Duas ou três colunas, com intervalo maior que o diâmetro dos pontos.
    por_fila = [extras // len(raios)] * len(raios)
    for fila in range(len(raios) - (extras % len(raios)), len(raios)):
        por_fila[fila] += 1
    excedentes = []
    for fila, (raio, n) in enumerate(zip(raios, por_fila)):
        for j in range(n):
            dx = 6 + j * 8.5
            excedentes.append((-dx, h['base'] - math.sqrt(raio * raio - dx * dx), fila))
    return comuns, excedentes


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
    origens_fora = {r['id']: r for r in roteiro['origensForaMapa']}
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
            x, y = origens_fora[cod]['x'], origens_fora[cod]['y']
        origens.append({'id': cod, 'x': round(x, 3), 'y': round(y, 3), 'mapa': geografia,
                        'lula': r['pt'], 'flavio': r['adv']})

    # O trecho comum permanece espelhado. Os 89 excedentes de Lula atravessam o
    # eixo para a esquerda e chegam depois de todos os pares comuns.
    comum = min(totais.values())
    lotes, fragmentos = [], []
    h = roteiro['hemiciclo']
    n_comuns = math.ceil(comum / UNIDADE)
    n_extras = math.ceil(abs(totais['lula'] - totais['flavio']) / UNIDADE)
    assentos_comuns, assentos_extras = assentos(n_comuns, n_extras, h)
    for candidato in ('flavio', 'lula'):
        pesos = [UNIDADE] * (comum // UNIDADE)
        if comum % UNIDADE:
            pesos.append(comum % UNIDADE)
        extra = totais[candidato] - comum
        if extra:
            pesos.extend([UNIDADE] * (extra // UNIDADE))
            if extra % UNIDADE:
                pesos.append(extra % UNIDADE)
        primeiros = len(lotes)
        for i, votos in enumerate(pesos):
            diferenca = i >= n_comuns
            if diferenca:
                dx, y, fila = assentos_extras[i - n_comuns]
                x = h['x'] + dx
            else:
                dx, y, fila = assentos_comuns[i]
                x = h['x'] + (-dx if candidato == 'flavio' else dx)
            # Mesma semente/tempo no par; sem prioridade para uma candidatura.
            acaso = ((i * 73 + 19) % 997) / 996
            janela = roteiro['partidasDiferenca'] if diferenca else roteiro['partidas']
            inicio = janela[0] + acaso * (janela[1] - janela[0])
            duracao = roteiro['vooDiferenca'] if diferenca else roteiro['voo']
            lotes.append({'candidato': candidato, 'votos': votos, 'x': round(x, 6), 'y': round(y, 6),
                          'r': round(h['raioPonto'] * math.sqrt(votos / UNIDADE), 6), 'fila': fila,
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
            'contorno': capa['contorno']['d1'], 'divisas': [d['d'] for d in capa['divisas']],
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
