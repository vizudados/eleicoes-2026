"""Consulta pública e evidência de licença; não usa credenciais nem geradores externos."""
from __future__ import annotations
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'pbi/qa/quem-e/fontes'
UA = {'User-Agent': 'VizuDados-Eleicoes/1.0 (public photo license audit)'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as f:
        return f.read()


def api(**params):
    return json.loads(get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(
        {'action': 'query', 'format': 'json', **params})))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    terms = ['Lula 25.10.2026', '"Flávio Bolsonaro" 2026 -logo',
             '"Flávio Bolsonaro" "2026-10"', '"Flávio Bolsonaro" "2026-09"']
    for i, term in enumerate(terms):
        d = api(generator='search', gsrsearch=term, gsrnamespace=6, gsrlimit=30,
                prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=1600)
        (OUT / f'commons-busca-{i}.json').write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        for p in d.get('query', {}).get('pages', {}).values():
            z = p['imageinfo'][0]; m = z.get('extmetadata', {})
            print(p['title'], {k: m.get(k, {}).get('value') for k in ['DateTimeOriginal', 'LicenseShortName']})


def baixar_escolhidas():
    ref = ROOT / 'arte/ref/historicas'
    for nome, title in [
        ('lula-2026-reeleicao', 'File:25.10.2026 - Lula é reeleito Presidente do Brasil - 55612564286.jpg'),
        ('flavio-2026-registro-recente', 'File:23.10.2026 - Debate na Globo - 55608517678.jpg'),
    ]:
        d = api(titles=title, prop='imageinfo|revisions', iiprop='url|size|extmetadata', iiurlwidth=1600,
                rvprop='content', rvslots='main')
        p = next(iter(d['query']['pages'].values()))
        ii = p['imageinfo'][0]
        assert ii['extmetadata']['LicenseShortName']['value'] == 'CC BY-SA 4.0'
        (OUT / (nome + '-metadados.json')).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
        target = ref / (nome + '.jpg')
        target.write_bytes(get(ii.get('thumburl', ii['url'])))
        print(nome, ii['descriptionurl'], ii['extmetadata']['LicenseShortName']['value'])


def conferir_video_flavio():
    """Rodada 2: guarda metadados, template e revisão pública antes de baixar o vídeo."""
    title = 'File:Flávio Bolsonaro cita ministro ao aventar possibilidade de anulação do resultado das eleições.webm'
    OUT.mkdir(parents=True, exist_ok=True)
    d = api(titles=title, prop='imageinfo|revisions', iiprop='url|size|extmetadata',
            rvprop='content|timestamp|ids', rvslots='main')
    p = next(iter(d['query']['pages'].values()))
    ii = p['imageinfo'][0]
    wiki = p['revisions'][0]['slots']['main']['*']
    assert 'Attribution-TVSenadoBr' in wiki, 'Template de atribuição não confirmado'
    assert 'LicenseReview' in wiki, 'Revisão de licença não confirmada'
    (OUT / 'flavio-2026-pos-video-metadados.json').write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    t = api(titles='Template:Attribution-TVSenadoBr', prop='revisions', rvprop='content|timestamp|ids', rvslots='main')
    (OUT / 'tv-senado-template-atribuicao.json').write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'pagina':ii['descriptionurl'], 'url':ii['url'], 'meta':ii['extmetadata'], 'wikitext':wiki}, ensure_ascii=False, indent=2))
    print('TEMPLATE', next(iter(t['query']['pages'].values()))['revisions'][0]['slots']['main']['*'])
    tr = api(titles='Template:Attribution-TVSenadoBr/en|Template:Attribution-TVSenadoBr/pt',
             prop='revisions', rvprop='content|timestamp|ids', rvslots='main')
    (OUT / 'tv-senado-template-texto.json').write_text(json.dumps(tr, ensure_ascii=False, indent=2), encoding='utf-8')
    for page in tr['query']['pages'].values():
        print(page['title'], page.get('revisions', [{}])[0].get('slots', {}).get('main', {}).get('*', 'não encontrada'))


if __name__ == '__main__':
    import sys
    if '--flavio-video' in sys.argv:
        conferir_video_flavio()
    elif '--baixar' in sys.argv:
        baixar_escolhidas()
    else:
        main()
