#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ponte Python para o motor local do Power BI Desktop do painel Eleições 2026 (consultas DAX/DMV, somente leitura).

Adaptado do kit da casa (Vizu Dados).

Chama ``dax.ps1`` (ADOMD.NET no pwsh 7) com a consulta num arquivo temporário e lê o
resultado em JSON tipado. Nada passa pelo stdout do pwsh: o console do Windows usa cp850
e quebra os acentos que vêm do modelo.

Como módulo::

    from dax import consultar, ErroDax
    linhas = consultar('EVALUATE ROW ( "x", 1 )')        # -> [{'[x]': 1}]
    try:
        consultar(texto)
    except ErroDax as e:
        print(e)            # mensagem do motor + trecho da consulta com a posição (linha, coluna)

Como linha de comando::

    python dax.py --arquivo consulta.dax --saida x.tsv
    python dax.py --consulta "EVALUATE ROW ( \\"x\\", 1 )" --saida x.json
    python dax.py --arquivo consulta.dax                  (imprime as primeiras linhas)

A porta vem de ``--porta`` ou de ``qa/porta.txt`` (gravado por ``desktop.ps1``). Valores
voltam tipados: número, texto, booleano, None (BLANK) e data como texto ISO sem fuso
(``2026-09-01T00:00:00``). Nomes de coluna saem como o ADOMD devolve: ``dMaquina[Local]`` para
coluna e ``[Nome]`` para expressão nomeada.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DAX_PS1 = os.path.join(AQUI, 'dax.ps1')
PWSH = os.environ.get('BEV_PWSH', 'pwsh')

_POSICAO = re.compile(r'\((\d+),\s*(\d+)\)')


class ErroDax(Exception):
    """Falha ao consultar o motor. ``mensagem`` é o texto do motor, sem tradução."""

    def __init__(self, mensagem, etapa='consulta', detalhes=None, consulta=None,
                 linha=None, coluna=None, codigo=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.etapa = etapa
        self.detalhes = detalhes or []
        self.consulta = consulta
        self.linha = linha
        self.coluna = coluna
        self.codigo = codigo

    def mensagem_curta(self):
        """A mensagem do motor sem o eco da consulta inteira (o erro de sintaxe repete o texto todo)."""
        msg = self.mensagem or ''
        if self.consulta and len(self.consulta) > 80:
            for alvo in (self.consulta, self.consulta.rstrip('\n')):
                msg = msg.replace(alvo, '<consulta>')
        return msg

    def __str__(self):
        cab = f'[{self.etapa}] {self.mensagem_curta()}'
        if self.consulta and self.linha:
            return cab + '\n' + trecho(self.consulta, self.linha, self.coluna)
        return cab


def trecho(texto, linha, coluna=None, contexto=2):
    """Linhas ao redor de (linha, coluna), numeradas a partir de 1, com um circunflexo na coluna."""
    linhas = texto.splitlines()
    if not linhas or not linha or linha < 1:
        return ''
    ini = max(1, linha - contexto)
    fim = min(len(linhas), linha + contexto)
    saida = []
    for n in range(ini, fim + 1):
        saida.append(f'{n:>5} | {linhas[n - 1]}')
        if n == linha and coluna and coluna >= 1:
            saida.append('      | ' + ' ' * (coluna - 1) + '^')
    return '\n'.join(saida)


def _posicao(mensagem, detalhes):
    for d in detalhes or []:
        if d.get('linha'):
            return int(d['linha']), (int(d['coluna']) if d.get('coluna') else None)
    m = _POSICAO.search(mensagem or '')
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def ler_porta():
    caminho = os.path.join(RAIZ, 'qa', 'porta.txt')
    try:
        with open(caminho, encoding='utf-8', errors='replace') as fh:
            m = re.search(r'\d+', fh.read())
        return int(m.group(0)) if m else None
    except OSError:
        return None


def executar(dax, porta=None, timeout=300):
    """Roda a consulta e devolve o JSON bruto de dax.ps1 (``resultados`` = lista de conjuntos)."""
    if not dax or not dax.strip():
        raise ErroDax('consulta vazia', etapa='uso')
    fd_q, arq_q = tempfile.mkstemp(prefix='eleicoes_q_', suffix='.dax')
    fd_o, arq_o = tempfile.mkstemp(prefix='eleicoes_r_', suffix='.json')
    os.close(fd_o)
    try:
        with os.fdopen(fd_q, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(dax)
        os.unlink(arq_o)   # dax.ps1 só grava se chegar ao motor; ausência = falhou antes
        cmd = [PWSH, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', DAX_PS1,
               '-QueryFile', arq_q, '-Out', arq_o, '-Timeout', str(int(timeout))]
        if porta:
            cmd += ['-Port', str(int(porta))]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=timeout + 90)
        except FileNotFoundError:
            raise ErroDax(f'pwsh não encontrado ({PWSH}); defina BEV_PWSH', etapa='ambiente')
        except subprocess.TimeoutExpired:
            raise ErroDax(f'dax.ps1 não respondeu em {timeout + 90} s', etapa='tempo', consulta=dax)
        saida = (r.stdout or b'').decode('utf-8', 'replace').strip()
        if not os.path.exists(arq_o):
            etapa = {1: 'uso', 3: 'porta'}.get(r.returncode, 'ambiente')
            erro = (r.stderr or b'').decode('utf-8', 'replace').strip()
            raise ErroDax(saida or erro or f'dax.ps1 saiu com {r.returncode}', etapa=etapa,
                          consulta=dax, codigo=r.returncode)
        with open(arq_o, encoding='utf-8') as fh:
            res = json.load(fh)
    finally:
        for p in (arq_q, arq_o):
            try:
                os.unlink(p)
            except OSError:
                pass
    if not res.get('ok'):
        linha, coluna = _posicao(res.get('erro'), res.get('detalhes'))
        raise ErroDax(res.get('erro') or 'erro sem mensagem', etapa=res.get('etapa', 'consulta'),
                      detalhes=res.get('detalhes'), consulta=dax, linha=linha, coluna=coluna,
                      codigo=r.returncode)
    return res


def _como_dicts(conjunto):
    cols = conjunto['colunas']
    return [dict(zip(cols, linha)) for linha in conjunto['linhas']]


def _consultar_service(dax):
    """VIZU_DAX=service (17/10/2026, sessão na nuvem, sem o Desktop): a consulta vai ao modelo publicado no workspace pela
    API executeQueries (fabric_api.consultar). Mesmo formato de saída do motor local."""
    sys.path.insert(0, AQUI)
    import fabric_api
    try:
        return fabric_api.consultar(dax)
    except RuntimeError as e:
        raise ErroDax(str(e), consulta=dax) from None


def consultar(dax, porta=None, timeout=300):
    """Primeiro conjunto de resultados como lista de dicionários {coluna: valor}."""
    if os.environ.get('VIZU_DAX') == 'service':
        return _consultar_service(dax)
    res = executar(dax, porta=porta, timeout=timeout)
    conjuntos = res.get('resultados') or []
    return _como_dicts(conjuntos[0]) if conjuntos else []


def consultar_tudo(dax, porta=None, timeout=300):
    """Todos os conjuntos (um por EVALUATE), cada um como lista de dicionários."""
    res = executar(dax, porta=porta, timeout=timeout)
    return [_como_dicts(c) for c in res.get('resultados') or []]


def _tsv(valor):
    if valor is None:
        return ''
    if isinstance(valor, bool):
        return 'true' if valor else 'false'
    s = str(valor)
    return s.replace('\\', '\\\\').replace('\t', '\\t').replace('\r', '\\r').replace('\n', '\\n')


def gravar(res, caminho, consulta=None):
    """Grava o resultado de ``executar`` em .tsv (escapado, reversível) ou .json (linhas como dicts)."""
    pasta = os.path.dirname(os.path.abspath(caminho))
    os.makedirs(pasta, exist_ok=True)
    conjuntos = res.get('resultados') or []
    if caminho.lower().endswith('.json'):
        doc = {'porta': res.get('porta'), 'ms': res.get('ms'), 'consulta': consulta}
        if conjuntos:
            doc.update(colunas=conjuntos[0]['colunas'], tipos=conjuntos[0]['tipos'],
                       linhas=_como_dicts(conjuntos[0]))
            if len(conjuntos) > 1:
                doc['extras'] = [{'colunas': c['colunas'], 'tipos': c['tipos'], 'linhas': _como_dicts(c)}
                                 for c in conjuntos[1:]]
        with open(caminho, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
    else:
        with open(caminho, 'w', encoding='utf-8', newline='\n') as fh:
            for n, c in enumerate(conjuntos, 1):
                if n > 1:
                    fh.write(f'#resultado {n}\n')
                fh.write('\t'.join(_tsv(x) for x in c['colunas']) + '\n')
                for linha in c['linhas']:
                    fh.write('\t'.join(_tsv(x) for x in linha) + '\n')


def _resumo(valor, largura=90):
    if valor is None:
        return '(BLANK)'
    s = str(valor).replace('\n', ' ')
    return s if len(s) <= largura else s[:largura] + f'... ({len(s)} chars)'


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description='Consulta DAX/DMV no motor local do Desktop (somente leitura).')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--arquivo', help='arquivo UTF-8 com a consulta (DEFINE/EVALUATE ou DMV)')
    g.add_argument('--consulta', help='texto da consulta')
    ap.add_argument('--saida', help='grava o resultado em .tsv ou .json')
    ap.add_argument('--porta', type=int, help='porta do msmdsrv (padrão: qa/porta.txt)')
    ap.add_argument('--timeout', type=int, default=300, help='segundos (padrão 300)')
    ap.add_argument('--linhas', type=int, default=20, help='quantas linhas imprimir sem --saida')
    a = ap.parse_args(argv)

    if a.arquivo:
        with open(a.arquivo, encoding='utf-8-sig') as fh:
            texto = fh.read()
    else:
        texto = a.consulta
    try:
        res = executar(texto, porta=a.porta, timeout=a.timeout)
    except ErroDax as e:
        print(f'ERRO {e}', file=sys.stdout)
        return 2 if e.etapa == 'consulta' else 3
    conjuntos = res.get('resultados') or []
    formas = ', '.join(f"{len(c['linhas'])}x{len(c['colunas'])}" for c in conjuntos)
    print(f"ok porta={res.get('porta')} ms={res.get('ms')} resultados={len(conjuntos)} ({formas})")
    if a.saida:
        gravar(res, a.saida, consulta=texto)
        print(f'gravado: {a.saida}')
    else:
        for c in conjuntos:
            print(' | '.join(c['colunas']))
            for linha in c['linhas'][:a.linhas]:
                print(' | '.join(_resumo(v) for v in linha))
            if len(c['linhas']) > a.linhas:
                print(f"... mais {len(c['linhas']) - a.linhas} linha(s)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
