"""Resume apenas as medições estáticas da rodada 5; tempos reais ficam com desempenho.py na main."""
import json
from pathlib import Path

Q=Path(__file__).resolve().parents[1]/'qa/rodada5'


def main():
    a=json.loads((Q/'peso-antes.json').read_text(encoding='utf-8'))
    b=json.loads((Q/'peso-depois.json').read_text(encoding='utf-8'))
    r=json.loads((Q/'provas-locais.json').read_text(encoding='utf-8'))
    fmt=lambda n:f'{n:,}'.replace(',','.')
    linhas=['# Peso estático · rodada 5','','Sem nova consulta ao motor ou medição de renderização do navegador.',
        'JSON de dados é simulado pelos mesmos CSV e aliases, sem metadados do SDK; caracteres contam campos de texto.','',
        '| Item | Antes | Depois |','|---|---:|---:|',
        f"| CSS comum, caracteres | {fmt(a['css_base'])} | {fmt(b['css_base'])} |",
        f"| CSS para notas, composição completa | {fmt(a['css_base'])} | {fmt(b['css_base']+b['css_mao'])} |"]
    for nome,f in r['fontes'].items():linhas.append(f"| {nome}, WOFF2 bytes | {fmt(f['bytes_antes'])} | {fmt(f['bytes_depois'])} |")
    for nome,p in r['payloads_estimados'].items():
        linhas.append(f"| {nome}, linhas | {fmt(p['antes_linhas'])} | {fmt(p['depois_linhas'])} |")
        linhas.append(f"| {nome}, caracteres de texto | {fmt(p['antes_texto'])} | {fmt(p['depois_texto'])} |")
        linhas.append(f"| {nome}, JSON estimado, bytes | {fmt(p['antes_json_bytes'])} | {fmt(p['depois_json_bytes'])} |")
    c=r.get('T19_cache',{})
    if c:linhas.append(f"| T19, texto da consulta (cache + rótulos) | {fmt(c['consulta_texto_antes'])} | {fmt(c['consulta_texto_depois'])} |")
    linhas+=['','| Página | Visuais antes → depois | JSON de declaração antes → depois (car.) |','|---|---:|---:|']
    for p in ['T03','T05','T11','T19','T21','T22','T23','T25','T27','T28','TIX']:
        x,y=a['paginas'][p],b['paginas'][p]
        linhas.append(f"| {p} | {x['visuais']} → {y['visuais']} | {fmt(x['json'])} → {fmt(y['json'])} |")
    antes=sum(sum(p['folhas'].values())*a['css_base']for p in a['paginas'].values())
    depois=sum(p['folhas'].get('Estilo · CSS',0)*b['css_base']+p['folhas'].get('Estilo · CSS com mão',0)*(b['css_base']+b['css_mao'])for p in b['paginas'].values())
    linhas+=['',f'Soma teórica de folhas por instância declarada: {fmt(antes)} → {fmt(depois)} caracteres ({(1-depois/antes)*100:.2f}% a menos).',
        'Isso soma uma visita a todos os visuais/tooltips; não é tráfego observado nem memória simultânea.',
        '', 'Na T19 já existia Top 16 no PBIR. O benchmark anterior não aplicava o filtro visual; o guard da medida agora limita também a consulta bruta. O ganho no navegador deve ser medido separadamente.',
        '', 'Colunas __format/__formatted não referenciadas deixaram de ser emitidas pelo Deneb. Esse ganho adicional no DataView não está contado no JSON simulado acima.']
    (Q/'resumo.md').write_text('\n'.join(linhas)+'\n',encoding='utf-8')
    print('\n'.join(linhas))


if __name__=='__main__':main()
