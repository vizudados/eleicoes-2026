"""conferir_campos — auditoria estática do PBIP (26/10/2026, depois do erro "Column 'T27 · valor formatado' cannot be
found" no Service): todo campo que o relatório pede existe no modelo? E toda medida citada dentro de outra existe?

    python -X utf8 pbi/scripts/conferir_campos.py            # padrão: pbi/pbip
    python -X utf8 pbi/scripts/conferir_campos.py <pasta do pbip>

Não abre o Desktop. Ignora colunas virtuais ([@x], nomes criados com "x" na própria medida e Value1… das tabelas
literais). Código de saída 1 quando há problema.
"""
import json, re, sys, glob, os
from pathlib import Path
raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'pbip'
modelo = raiz / 'Eleicoes.SemanticModel/definition/tables'
rel = raiz / 'Eleicoes.Report/definition'

def nome(s):
    s = s.strip()
    if s.startswith("'") and s.endswith("'"):
        s = s[1:-1].replace("''", "'")
    return s

tabelas = {}   # tabela -> {campos}
medidas_expr = {}  # (tabela, medida) -> expressão
for f in sorted(modelo.glob('*.tmdl')):
    linhas = f.read_text(encoding='utf-8').splitlines()
    tab = None; atual = None; buf = []
    for ln in linhas:
        m = re.match(r"^table\s+(.+?)\s*$", ln)
        if m: tab = nome(m.group(1)); tabelas.setdefault(tab, set()); continue
        m = re.match(r"^\t(measure|column)\s+('(?:[^']|'')+'|[^\s=]+)\s*(=\s*(.*))?$", ln)
        if m and tab:
            if atual: medidas_expr[atual] = '\n'.join(buf)
            atual = None; buf = []
            n = nome(m.group(2)); tabelas[tab].add(n)
            if m.group(1) == 'measure':
                atual = (tab, n); buf = [m.group(4) or '']
            continue
        m = re.match(r"^\t(hierarchy|partition|annotation)\b", ln)
        if m:
            if atual: medidas_expr[atual] = '\n'.join(buf)
            atual = None; buf = []; continue
        if atual is not None:
            if re.match(r"^\t\t(formatString|displayFolder|lineageTag|annotation|description|dataCategory|isHidden|formatStringDefinition|changedProperty)\b", ln):
                medidas_expr[atual] = '\n'.join(buf); atual = None; buf = []
            else:
                buf.append(ln)
    if atual: medidas_expr[atual] = '\n'.join(buf)

todos_campos = set()
for t, cs in tabelas.items():
    for c in cs: todos_campos.add((t, c))
medidas = {c for (t, c) in medidas_expr}

problemas = []
def varrer(obj, onde):
    if isinstance(obj, dict):
        if 'Property' in obj and 'Expression' in obj and isinstance(obj['Expression'], dict):
            src = obj['Expression'].get('SourceRef', {})
            ent = src.get('Entity')
            if ent is not None:
                if ent not in tabelas:
                    problemas.append((onde, f'tabela inexistente: {ent}[{obj["Property"]}]'))
                elif obj['Property'] not in tabelas[ent]:
                    problemas.append((onde, f'campo inexistente: {ent}[{obj["Property"]}]'))
        for v in obj.values(): varrer(v, onde)
    elif isinstance(obj, list):
        for v in obj: varrer(v, onde)

# Fontes com alias (From: Name/Entity, SourceRef: Source)
def varrer_alias(obj, onde, alias=None):
    if isinstance(obj, dict):
        if 'From' in obj and isinstance(obj['From'], list):
            alias = {f.get('Name'): f.get('Entity') for f in obj['From'] if isinstance(f, dict)}
        if 'Property' in obj and isinstance(obj.get('Expression'), dict):
            src = obj['Expression'].get('SourceRef', {})
            if 'Source' in src and alias:
                ent = alias.get(src['Source'])
                if ent and (ent not in tabelas or obj['Property'] not in tabelas[ent]):
                    problemas.append((onde, f'campo inexistente (alias): {ent}[{obj["Property"]}]'))
        for v in obj.values(): varrer_alias(v, onde, alias)
    elif isinstance(obj, list):
        for v in obj: varrer_alias(v, onde, alias)

n = 0
for f in sorted(rel.rglob('*.json')):
    try: d = json.loads(f.read_text(encoding='utf-8'))
    except Exception as e: problemas.append((str(f), f'json inválido {e}')); continue
    onde = str(f.relative_to(rel))
    varrer(d, onde); varrer_alias(d, onde); n += 1

# medidas que citam medidas inexistentes ([Nome] sem tabela antes)
cit = 0
for (t, m), expr in medidas_expr.items():
    literais = set(x.replace('""','"') for x in re.findall(r'"((?:[^"]|"")*)"', expr))
    limpo = re.sub(r'"(?:[^"]|"")*"', '""', expr)          # tira strings
    limpo = re.sub(r'//[^\n]*|--[^\n]*', '', limpo)
    limpo = re.sub(r'/\*.*?\*/', '', limpo, flags=re.S)
    for q in re.finditer(r"('(?:[^']|'')+'|\b[A-Za-z_][\w ]*)?\[([^\]]+)\]", limpo):
        tabq, campo = q.group(1), q.group(2)
        cit += 1
        if campo in literais or campo.startswith('@') or re.fullmatch(r'Value\d+', campo): continue
        if tabq:
            tq = nome(tabq.strip())
            if tq in tabelas and campo not in tabelas[tq]:
                problemas.append((f'medida {t}[{m}]', f'cita {tq}[{campo}] inexistente'))
        else:
            if campo not in medidas and not any(campo in cs for cs in tabelas.values()):
                # pode ser coluna de variável de tabela (VAR t = ...; t[col]) — tratado acima; aqui [x] solto
                problemas.append((f'medida {t}[{m}]', f'cita [{campo}] que não existe como medida nem coluna'))

print(f'{len(tabelas)} tabelas, {len(medidas)} medidas, {n} arquivos do relatório, {cit} citações em medidas')
vistos = set()
for onde, p in problemas:
    if (onde, p) in vistos: continue
    vistos.add((onde, p)); print(onde, '->', p)
print('problemas:', len(vistos))
sys.exit(1 if vistos else 0)
