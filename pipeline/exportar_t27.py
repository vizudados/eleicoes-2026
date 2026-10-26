"""Exporta os componentes da estimativa ecológica do agente de dados para a T27.

Lê somente dados/saida/2turno. Não refaz a regressão nem estima transições individuais.
O restante é definido por identidade: ganho observado - componente demais - componente comparecimento.
Assim as três parcelas fecham com o ganho em qualquer UF/porte, inclusive com parcelas negativas.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def exportar():
    origem = RAIZ / 'dados/saida/2turno'
    with (origem / 'regressao_ecologica.csv').open(encoding='utf-8-sig', newline='') as f:
        coeficientes = [r for r in csv.DictReader(f) if r['modelo'] == 'principal']
    coef = {}
    for r in coeficientes:
        chave = r['candidato'], r['termo']
        if chave in coef:
            raise ValueError(f'Coeficiente repetido: {chave}')
        coef[chave] = float(r['coeficiente'])
    campos = ['cd_ibge', 'lula_demais', 'lula_comparecimento', 'lula_resto',
              'flavio_demais', 'flavio_comparecimento', 'flavio_resto']
    linhas, vistos = [], set()
    with (origem / 'comparacao_municipios.csv').open(encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            cod = str(int(r['cd_ibge']))
            if cod in vistos:
                raise ValueError(f'Município repetido: {cod}')
            vistos.add(cod)
            item = {'cd_ibge': cod}
            for cand, prefixo, ganho in [('Lula', 'lula', 'delta_pt'), ('Flávio', 'flavio', 'delta_adv')]:
                outros = float(r['demais_1t']) * coef[cand, 'demais']
                presenca = float(r['delta_comparecimento']) * coef[cand, 'comparecimento']
                resto = float(r[ganho]) - outros - presenca
                if not all(math.isfinite(v) for v in (outros, presenca, resto)):
                    raise ValueError(f'Parcela inválida: {cod}')
                item.update({f'{prefixo}_demais': format(outros, '.12g'),
                             f'{prefixo}_comparecimento': format(presenca, '.12g'),
                             f'{prefixo}_resto': format(resto, '.12g')})
                if abs(sum(float(item[f'{prefixo}_{p}']) for p in ['demais', 'comparecimento', 'resto'])
                       - float(r[ganho])) > 0.001:
                    raise ValueError(f'Decomposição não fecha: {cod}, {cand}')
            linhas.append(item)
    if len(linhas) != 5571:
        raise ValueError(f'Esperados 5.571 municípios; recebidos {len(linhas)}')
    destino = RAIZ / 'dados/pbi/t27_fluxo.csv'
    with destino.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(linhas, key=lambda r: r['cd_ibge']))
    print(f'{destino.relative_to(RAIZ)}: {len(linhas)} municípios; parcelas fecham para ambos os candidatos.')


if __name__ == '__main__':
    exportar()
