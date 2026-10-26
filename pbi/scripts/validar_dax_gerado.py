"""Checagem estrutural de emissão DAX; não substitui o parser do Analysis Services.

Detecta RETURN sem VAR no escopo, delimitadores/literais abertos e comentário que corta linha de código.
Uso: python -X utf8 pbi/scripts/validar_dax_gerado.py [--autoteste]
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path


def problemas(expressao: str, *, comentario_inline=False) -> list[str]:
    erros=[]
    grupos=[]
    variaveis={0:False}
    i=0
    codigo_na_linha=False
    while i<len(expressao):
        c=expressao[i]
        if c in '\r\n':
            codigo_na_linha=False;i+=1;continue
        if c.isspace():i+=1;continue
        if expressao.startswith('--',i) or expressao.startswith('//',i):
            if comentario_inline and codigo_na_linha:
                erros.append('Comentário no fim de linha de código; mover para linha própria.')
            fim=expressao.find('\n',i)
            i=len(expressao) if fim<0 else fim
            continue
        if expressao.startswith('/*',i):
            fim=expressao.find('*/',i+2)
            if fim<0:erros.append('Comentário de bloco não fechado.');break
            i=fim+2;continue
        codigo_na_linha=True
        if c in ('"',"'",'['):
            fecha=']' if c=='[' else c
            inicio=i;i+=1
            while i<len(expressao):
                if expressao[i]==fecha:
                    if i+1<len(expressao) and expressao[i+1]==fecha:i+=2;continue
                    i+=1;break
                i+=1
            else:erros.append(f'Literal ou referência não fechada na posição {inicio}.')
            continue
        if c in '({':
            grupos.append(c);variaveis[len(grupos)]=False;i+=1;continue
        if c in ')}':
            esperado='(' if c==')' else '{'
            if not grupos or grupos[-1]!=esperado:erros.append(f'Delimitador {c} sem abertura na posição {i}.')
            else:
                variaveis.pop(len(grupos),None);grupos.pop()
            i+=1;continue
        if c==',':
            variaveis[len(grupos)]=False;i+=1;continue
        m=re.match(r'[A-Za-z_][A-Za-z_0-9]*',expressao[i:])
        if m:
            palavra=m.group().upper();nivel=len(grupos)
            if palavra=='VAR':variaveis[nivel]=True
            if palavra=='RETURN' and not variaveis.get(nivel,False):
                erros.append(f'RETURN sem VAR no escopo, posição {i}.')
            i+=len(m.group());continue
        i+=1
    if grupos:erros.append('Delimitador de expressão não fechado.')
    return list(dict.fromkeys(erros))


def autoteste():
    casos=[
        ('RETURN "quebrado"',False),
        ('/* cabeçalho */\n-- início\nRETURN "quebrado"',False),
        ('VAR _html = "<div>ok</div>"\nRETURN _html',True),
        ('VAR _t = { 1, 2 }\nRETURN COUNTROWS ( _t )',True),
        ('IF ( TRUE (), VAR _x = 1 RETURN _x, 0 )',True),
        ('IF ( TRUE (), RETURN 1, 0 )',False),
        ('"RETURN -- /* texto */"',True),
        ('"<svg data-v=""--"">{ x }</svg>"',True),
        ('VAR _x = 1 -- & expressão cortada\nRETURN _x',False),
        ('VAR _x = "sem fechamento',False),
    ]
    for texto,valido in casos:
        assert (not problemas(texto,comentario_inline=True))==valido, texto
    print(f'Autoteste: {len(casos)} casos passaram.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--autoteste',action='store_true')
    args=ap.parse_args()
    if args.autoteste:autoteste()
    raiz=Path(__file__).resolve().parents[1]/'dax'
    achados=[];n=0
    # Toda a árvore é lida: uma raiz RETURN inválida pode derrubar qualquer DEFINE que a inclua.
    for p in raiz.rglob('*.dax'):
        if '_modelo' in p.parts:continue
        n+=1
        texto=p.read_text(encoding='utf-8')
        for erro in problemas(texto):achados.append(f'{p.relative_to(raiz)}: {erro}')
    for erro in achados:print('ERRO',erro)
    print(f'{n} medidas verificadas · {len(achados)} erro(s) estrutural(is). Não é prova do motor DAX.')
    return int(bool(achados))


if __name__=='__main__':
    raise SystemExit(main())
