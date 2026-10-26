"""Enriquece o mapa decisivo com vencedor e segundo colocado reais; não altera as fontes históricas."""
from collections import defaultdict
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / 'dados/saida/pt_historico'
SAIDA = RAIZ / 'dados/pbi/t29_mapa.csv'


def linhas(nome):
    with (ORIGEM / nome).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def construir():
    grupos = defaultdict(list)
    for r in linhas('todos_candidatos_uf.csv'):
        grupos[(r['ano'], r['turno'], r['uf'])].append(r)
    saida = []
    for r in linhas('mapa_turno_decisivo.csv'):
        ranking = sorted(grupos[(r['ano'], r['turno'], r['uf'])], key=lambda x: (-int(x['votos']), x['numero']))
        primeiro, segundo = ranking[:2]
        assert int(primeiro['votos']) == int(r['votos_vencedor'])
        assert primeiro['partido'] == r['partido_vencedor']
        saida.append({**{k: r[k] for k in ['ano', 'turno', 'uf', 'candidato_pt', 'votos_pt', 'adversario',
                                          'partido_adversario', 'votos_adv', 'validos', 'comparecimento', 'aptos']},
                      'vencedor': primeiro['nome'], 'partido_vencedor': primeiro['partido'],
                      'votos_vencedor': primeiro['votos'], 'segundo': segundo['nome'],
                      'votos_segundo': segundo['votos'],
                      'vantagem_vencedor': int(primeiro['votos']) - int(segundo['votos']),
                      'grupo_vencedor': 'PT' if primeiro['partido'] == 'PT' else
                          ('Adversário' if primeiro['partido'] == r['partido_adversario'] else 'Outros')})
    assert len(saida) == 280
    return saida


def main():
    dados = construir()
    with SAIDA.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(dados[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(dados)
    print(f'T29: {len(dados)} linhas decisivas, 27 UFs + ZZ por eleição; vencedor real e vantagem sobre o segundo.')


if __name__ == '__main__':
    main()
