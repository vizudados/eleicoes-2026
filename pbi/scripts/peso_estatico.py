"""Mede fontes, folhas e plano de páginas em disco. Não conecta ao motor nem grava PBIP."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import montar_pbip as mp
import pbip_lib as lib
import estilo
import dax_para_tmdl as dpt
import gerar_modelo as gm

PBI = Path(__file__).resolve().parents[1]


def medir():
    ctx = mp.carregar_contexto()
    ctx.medidas.update(dpt.ler(p)['nome'] for p in (PBI/'dax').rglob('*.dax') if '_modelo' not in p.parts)
    tabelas, _, _ = gm.carregar_declaracoes()
    ctx.colunas.update((t['nome'], c['nome']) for t in tabelas for c in t['colunas'])
    itens = mp.carregar_declaracoes(ctx)
    paginas = defaultdict(lambda: {'visuais': 0, 'html': 0, 'body': 0, 'json': 0, 'folhas': Counter(), 'tipos':Counter()})
    for i in itens:
        if not isinstance(i, lib.Visual):
            continue
        d = i.doc
        p = paginas[i.pagina]
        p['visuais'] += 1
        p['json'] += len(json.dumps(d, ensure_ascii=False))
        v = d['visual']
        p['tipos'][v['visualType']] += 1
        if v['visualType'] == lib.GUID_HTML:
            p['html'] += 1
            obj = v.get('objects', {})
            if 'templates' in obj:
                p['body'] += len(obj['templates'][0]['properties']['bodyTemplate']['expr']['Literal']['Value'])
            if 'stylesheet' in obj:
                p['folhas'][obj['stylesheet'][0]['properties']['stylesheet']['expr']['Measure']['Property']] += 1
    return {'escopo': 'Plano e fontes em disco; sem motor ou navegador',
            'css_base': len(estilo.css_base()),
            'css_mao': len(estilo.font_face(estilo.FAMILIA_MAO,'caveat-notas','400 700')),
            'fontes': {p.name: p.stat().st_size for p in (PBI/'assets/fontes').glob('*.woff2')},
            'paginas': dict(paginas), 'erros_plano': mp.conferir(itens, ctx)}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--nome', default='depois')
    args = ap.parse_args()
    r = medir()
    d = PBI/'qa/rodada5'
    d.mkdir(exist_ok=True)
    (d/f'peso-{args.nome}.json').write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k!='paginas'}, ensure_ascii=False, indent=2))
