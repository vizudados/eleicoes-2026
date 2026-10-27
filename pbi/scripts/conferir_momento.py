"""conferir_momento — quais visuais de telas SEM o filtro Pré/Pós usam medida que depende dele (27/10/2026: o Encerramento
herdou o Pós em achados que falam do 1º turno). Uma tela sem o filtro sempre vê o padrão (Pós); se o texto dela fala do
1º turno, a medida tem de fixar o recorte com CALCULATE ( …, 'Momento eleição'[Momento] = "Pré Eleições 2026" ).

    python -X utf8 pbi/scripts/conferir_momento.py

Lista, por tela, o visual, a medida que ele pede e o caminho até [Eleição · pós]. Não abre o Desktop.
"""
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import momento_eleicao as M  # noqa: E402

PBIP = AQUI.parent / 'pbip'
TMDL = PBIP / 'Eleicoes.SemanticModel/definition/tables/_Medidas.tmdl'
PAGINAS = PBIP / 'Eleicoes.Report/definition/pages'


def medidas():
    texto = TMDL.read_text(encoding='utf-8').replace('\r\n', '\n')
    saida, atual, buf = {}, None, []
    for ln in texto.split('\n'):
        m = re.match(r"^\tmeasure\s+('(?:[^']|'')+'|[^\s=]+)\s*=?(.*)$", ln)
        if m:
            if atual:
                saida[atual] = '\n'.join(buf)
            atual = m.group(1).strip("'").replace("''", "'")
            buf = [m.group(2)]
        elif atual is not None:
            if re.match(r'^\t[a-z]', ln):
                saida[atual] = '\n'.join(buf)
                atual, buf = None, []
            else:
                buf.append(ln)
    if atual:
        saida[atual] = '\n'.join(buf)
    return saida


def main():
    exprs = medidas()
    # uma referência com o recorte fixado (CALCULATE ( [X], 'Momento eleição'[Momento] = "…" )) não depende da escolha
    fixa = re.compile(r"CALCULATE\s*\(\s*\[[^\]]+\]\s*,\s*'Momento eleição'\[Momento\]\s*=\s*\"[^\"]+\"\s*\)")
    deps = {n: {d for d in re.findall(r'\[([^\]]+)\]', re.sub(r'"(?:[^"]|"")*"', '', fixa.sub('', e)))
                if d in exprs and d != n}
            for n, e in exprs.items()}
    raiz = 'Eleição · pós'
    caminho = {raiz: [raiz]}
    mudou = True
    while mudou:
        mudou = False
        for n, ds in deps.items():
            if n in caminho:
                continue
            for d in ds:
                if d in caminho:
                    caminho[n] = [n] + caminho[d]
                    mudou = True
                    break
    # telas sem o filtro; uma tooltip (ttT22…) herda o filtro da tela de origem (os 3 caracteres depois de "tt")
    achados = 0
    for pag in sorted(PAGINAS.iterdir()):
        dona = pag.name[2:5] if pag.name.startswith('tt') else pag.name
        if not pag.is_dir() or dona in M.TELAS:
            continue
        for vj in sorted(pag.glob('visuals/*/visual.json')):
            usados = set(re.findall(r'"Property":\s*"([^"]+)"', vj.read_text(encoding='utf-8')))
            for u in sorted(usados):
                if u in caminho:
                    achados += 1
                    print(f'{pag.name} · {vj.parent.name} · [{u}] ← ' + ' ← '.join(caminho[u][1:4]) +
                          (' …' if len(caminho[u]) > 4 else ''))
    print(f'{achados} visual(is) de tela sem filtro dependem do Pré/Pós')


if __name__ == '__main__':
    main()
