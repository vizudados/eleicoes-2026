"""Corpus e detecção de escrita à mão. Sem navegador, rede ou dependência de fonte instalada."""
from functools import lru_cache
import html
from pathlib import Path
import re
import string

PBI = Path(__file__).resolve().parents[1]
RAIZ = PBI.parent
PORTUGUES = 'áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ'


@lru_cache(maxsize=1)
def corpus():
    # Inclui os nomes dinâmicos dos CSV, não apenas o texto constante das telas.
    ps = list((PBI/'dax').rglob('*.dax')) + list((PBI/'scripts').glob('*.py'))
    ps += list((PBI/'scripts/paginas').glob('*.py')) + list((PBI/'scripts/leituras').glob('*.json'))
    ps += list((RAIZ/'dados/pbi').glob('*.csv'))
    base = set(string.ascii_letters + string.digits + string.punctuation + ' ' + PORTUGUES)
    sor = set(base)
    mao = set(string.ascii_letters + string.digits + ' .,;:!?%+−–—()ºª/×' + PORTUGUES)
    fontes = []
    for p in ps:
        if p.parent.name == '_Estilo' or p.name == 'fontes_painel.py':
            continue
        t = p.read_text(encoding='utf-8-sig')
        t = re.sub(r'data:[^\s\"\']{300,}', '', t)
        sor.update(html.unescape(t))
        # Notas literais, inclusive dentro de strings DAX/Python. O alfabeto latino/português acima cobre
        # as notas dinâmicas (municípios e candidatos), sem reter o bloco Latin-1 inteiro.
        for m in re.finditer(r'class=[\"\'][^\"\']*\bmao\b[^\"\']*[\"\'][^>]*>(.{0,500}?)</', t, re.S):
            mao.update(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))))
        fontes.append(str(p.relative_to(RAIZ)))
    return {'sora': ''.join(sorted(sor)), 'caveat': ''.join(sorted(mao)), 'arquivos_lidos': fontes}


@lru_cache(maxsize=1)
def medidas():
    r = {}
    for p in (PBI/'dax').rglob('*.dax'):
        t = p.read_text(encoding='utf-8')
        nome = re.search(r'@nome:\s*([^\r\n]+)', t)
        r[nome.group(1).strip() if nome else p.stem] = t.split('*/',1)[-1]
    return r


@lru_cache(maxsize=512)
def texto_medida(nome):
    mapa = medidas()
    vistos = set()
    def abrir(n):
        if n in vistos or n not in mapa or n.startswith('Estilo ·'):
            return ''
        vistos.add(n)
        t = mapa[n]
        return t + '\n' + '\n'.join(abrir(x) for x in re.findall(r'\[([^\]]+)\]', t) if x in mapa)
    return abrir(nome)


def usa_mao(nome, corpo=''):
    t = (corpo or '') + '\n' + texto_medida(nome)
    t = re.sub(r'data:[A-Za-z0-9/+.-]+;base64,[A-Za-z0-9+/=]+','',t)
    t = t.replace('""','"')  # aspas de atributo dentro de literais DAX
    # Uma regra .mao não significa que o elemento existe: ignora CSS sem uso no corpo compartilhado.
    classes_mao = {'mao'}
    css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>',t,flags=re.S|re.I))
    for seletor, regras in re.findall(r'([^{}]+)\{([^{}]+)\}', css):
        if re.search(r'font(?:-family)?\s*:[^;]*var\(--mao\)', regras):
            for trecho in seletor.split(','):
                cs = re.findall(r'\.([\w-]+)', trecho)
                if cs:
                    classes_mao.add(cs[-1])
    markup = re.sub(r'<style[^>]*>.*?</style>|<script[^>]*>.*?</script>', '', t, flags=re.S|re.I)
    for cs in re.findall(r'class=[\"\']([^\"\']+)[\"\']', markup):
        if classes_mao.intersection(cs.split()):
            return True
    return bool(re.search(r'style=[\"\'][^\"\']*font(?:-family)?\s*:[^;]*var\(--mao\)', markup))
