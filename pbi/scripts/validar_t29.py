"""Provas locais da história presidencial. CSV e declarações; não substitui DAX, tooltip ou gesto no Desktop."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'pipeline'))
import exportar_t29 as exportador
import desenho_t29 as D

QA = RAIZ / 'pbi/qa/rodada3'


def ler(p):
    with (RAIZ / p).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    QA.mkdir(parents=True, exist_ok=True)
    erros = []
    def exigir(cond, msg):
        if not cond:
            erros.append(msg)
    uf = ler('dados/pbi/pt_historico_uf.csv')
    br = ler('dados/pbi/pt_historico_brasil.csv')
    mapa = ler('dados/pbi/t29_mapa.csv')
    recalculado = exportador.construir()
    exigir([{k: str(v) for k, v in r.items()} for r in recalculado] == mapa, 'Derivado difere da recomposição independente do arquivo gravado')
    exigir((len(uf), len(br), len(mapa)) == (504, 18, 280), 'Cobertura histórica mudou')
    exigir(len({(r['ano'], r['turno'], r['uf']) for r in uf}) == 504, 'Chaves históricas duplicadas')
    campos = ['votos_pt', 'votos_adv', 'validos', 'comparecimento', 'aptos']
    for r in br:
        parte = [u for u in uf if (u['ano'], u['turno']) == (r['ano'], r['turno'])]
        exigir(len(parte) == 28, f'UFs incompletas {r["ano"]}/{r["turno"]}')
        for campo in campos:
            exigir(sum(int(u[campo]) for u in parte) == int(r[campo]), f'Fechamento {campo} {r["ano"]}/{r["turno"]}')
    exigir(not any(r['turno'] == '2' and r['ano'] in ['1994', '1998'] for r in br), 'Segundo turno inexistente foi criado')
    tabela_br = {(int(r['ano']), int(r['turno'])): r for r in br}
    recorde = int(tabela_br[(2026, 2)]['votos_pt'])
    anterior = int(tabela_br[(2022, 2)]['votos_pt'])
    ranking = ler('dados/saida/pt_historico/todos_candidatos_brasil.csv')
    exigir(max(int(r['votos']) for r in ranking) == recorde == 64256232, 'Recorde nacional')
    exigir(recorde-anterior == 3910233, 'Acréscimo sobre o recorde anterior')
    exigir(int(tabela_br[(2018, 1)]['votos_pt'])-int(tabela_br[(2014, 1)]['votos_pt']) == -11925617, 'Queda do primeiro turno não preservada')
    exigir(int(tabela_br[(2018, 2)]['votos_pt'])-int(tabela_br[(2014, 2)]['votos_pt']) == -7460212, 'Queda do segundo turno não preservada')
    ce = next(r for r in mapa if r['uf'] == 'CE' and r['ano'] == '1998')
    exigir(ce['partido_vencedor'] == 'PPS' and ce['grupo_vencedor'] == 'Outros', 'Ciro no Ceará em 1998')
    esperado_pt = [4, 2, 2, 26, 20, 16, 15, 11, 13, 13]
    quadros = []
    for i, ano in enumerate(D.ANOS):
        parte = [r for r in mapa if int(r['ano']) == ano and r['uf'] != 'ZZ']
        n = Counter(r['grupo_vencedor'] for r in parte)
        exigir(len(parte) == 27 and n['PT'] == esperado_pt[i], f'Contador de UFs {ano}')
        quadros.append(f'{ano}|{parte[0]["turno"]}|{n["PT"]}|{n["Adversário"]}|{n["Outros"]}')
    fixture_mapa = []
    for estado in sorted({r['uf'] for r in mapa}):
        parte = [r for r in mapa if r['uf'] == estado]
        serie = ';'.join(f'{r["ano"]}|{r["grupo_vencedor"]}|{int(r["vantagem_vencedor"])/int(r["validos"]):.8f}|{r["turno"]}' for r in parte)
        fixture_mapa.append({'uf': estado, 'serie': serie, 'quadros': ';'.join(quadros)})
    fixture_votos = [{'ano': int(r['ano']), 'turno': int(r['turno']), 'pt': int(r['votos_pt']), 'adv': int(r['votos_adv'])} for r in br]
    for nome, spec, dados, w, h in [('mapa', D.mapa_spec(), fixture_mapa, 810, 700), ('votos', D.grafico_spec(), fixture_votos, 750, 510)]:
        def conferir_scope(s):
            nomes_locais = [d['name'] for d in s.get('data', [])] + [d['name'] for d in s.get('signals', [])]
            nomes_locais += [m['name'] for m in s.get('marks', []) if 'name' in m]
            exigir(len(nomes_locais) == len(set(nomes_locais)), f'Colisão de nomes Vega em {nome}')
            for d in s.get('data', []):
                exigir('url' not in d, 'Dado remoto em Vega')
            for m in s.get('marks', []):
                conferir_scope(m)
        conferir_scope(spec)
        (QA/f't29_{nome}_entrada.json').write_text(json.dumps({'spec': spec, 'dados': dados, 'largura': w, 'altura': h}, ensure_ascii=False), encoding='utf-8')
    relatorio = {'escopo': 'CSV e fontes locais; sem motor DAX ou Desktop', 'linhas_uf': len(uf), 'linhas_brasil': len(br),
                 'linhas_mapa': len(mapa), 'fechamentos_nacionais': len(br)*len(campos), 'vencedores_conferidos': len(mapa),
                 'recorde': recorde, 'anterior': anterior, 'diferenca': recorde-anterior,
                 'estados_pt_por_ano': dict(zip(D.ANOS, esperado_pt)), 'ce_1998': {k: ce[k] for k in ['vencedor', 'partido_vencedor', 'vantagem_vencedor']},
                 'sha256_csv_derivado': hashlib.sha256((RAIZ/'dados/pbi/t29_mapa.csv').read_bytes()).hexdigest(), 'erros': erros}
    (QA/'validacao-t29.json').write_text(json.dumps(relatorio, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    return bool(erros)


if __name__ == '__main__':
    raise SystemExit(main())
