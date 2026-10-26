"""Valida dados, identidades e declarações pós-eleição sem alterar o PBIP ou consultar o Desktop.

Não substitui previa.py, smoke_medidas.py, gestos e salvamento pela main.
"""
from __future__ import annotations
import ast
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode=True
PBI=Path(__file__).resolve().parents[1]
RAIZ=PBI.parent
sys.path.insert(0,str(PBI/'scripts'))
import dax_para_tmdl as dpt
import gerar_modelo as gm
import montar_pbip as mp
from validar_dax_gerado import problemas


def ler(nome):
    with (RAIZ/nome).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def main():
    erros=[]
    def exigir(ok,msg):
        if not ok:erros.append(msg)
    municipios=ler('dados/pbi/municipio_2turno.csv')
    ufs=ler('dados/pbi/uf_2turno.csv')
    cmp=ler('dados/saida/2turno/comparacao_municipios.csv')
    exigir(len({(r['ano'],r['cd_ibge']) for r in municipios})==len(municipios),'Chave municipal repetida')
    exigir(len({(r['ano'],r['uf']) for r in ufs})==56,'Chave UF/ano inválida')
    primeiro={r['cd_ibge']:r for r in ler('dados/pbi/municipio_ano.csv') if r['ano']=='2026'}
    identidades=[]
    for ano,n in [('2022',5570),('2026',5571)]:
        rs=[r for r in municipios if r['ano']==ano]
        exigir(len(rs)==n,f'Cobertura municipal {ano}')
        for r in rs:
            exigir(int(r['validos'])==int(r['pt'])+int(r['adv']),f'Válidos {r["cd_ibge"]}/{ano}')
            exigir(int(r['comparecimento'])==int(r['validos'])+int(r['brancos'])+int(r['nulos']),
                   f'Comparecimento {r["cd_ibge"]}/{ano}')
            if ano=='2026':
                a=primeiro[r['cd_ibge']]
                ganho_lula=int(r['pt'])-int(a['pt'])
                ganho_flavio=int(r['adv'])-int(a['adv'])
                outros=int(a['demais'])
                presenca=int(r['comparecimento'])-int(a['comparecimento'])
                queda=int(a['brancos'])+int(a['nulos'])-int(r['brancos'])-int(r['nulos'])
                exigir(ganho_lula+ganho_flavio==outros+presenca+queda,f'Identidade observada não fecha em {r["cd_ibge"]}')
                identidades.append({'cd_ibge':r['cd_ibge'],'ganho_lula':ganho_lula,'ganho_flavio':ganho_flavio,
                                    'demais':outros,'comparecimento':presenca,'queda_invalidos':queda})
    soma={k:sum(r[k] for r in identidades) for k in ['ganho_lula','ganho_flavio','demais','comparecimento','queda_invalidos']}
    soma['ganhos_dupla']=soma['ganho_lula']+soma['ganho_flavio']
    soma['lula_em_dez']=10*soma['ganho_lula']/soma['ganhos_dupla']
    soma['lula_parcela']=soma['ganho_lula']/soma['ganhos_dupla']
    exigir([soma[k] for k in ['demais','comparecimento','queda_invalidos','ganhos_dupla']]==[9287152,2920562,1820154,14027868],
           'Parcelas nacionais da identidade municipal diferem do controle')
    final=[r for r in ufs if r['ano']=='2026']
    esperado={'pt':64256232,'adv':59826041,'validos':124082273,'abstencoes':30509005,
              'brancos':1430496,'nulos':2723305,'comparecimento':128236074}
    oficial={k:sum(int(r[k]) for r in final) for k in esperado}
    exigir(oficial==esperado,'Total nacional difere do TSE final de 25/10/2026, 23h26')
    locais={k:sum(int(r[k]) for r in cmp) for k in ['pt_1t','pt_2t','adv_1t','adv_2t','delta_pt','delta_adv',
                'perda_vantagem_flavio','delta_comparecimento','delta_abstencoes']}
    viradas={cand:sum(r['vencedor_1t']==antes and r['vencedor_2t']==depois for r in cmp)
             for cand,antes,depois in [('para_lula','Flávio','Lula'),('para_flavio','Lula','Flávio')]}
    exigir(viradas=={'para_lula':211,'para_flavio':1},'Contagem de viradas estritas difere')
    historico=ler('dados/apuracao/historico.csv')
    from datetime import datetime
    hora=lambda r:datetime.strptime(r['atualizado_tse'],'%d/%m/%Y %H:%M:%S')
    h=sorted(historico,key=hora)
    f=next(r for r in h if int(r['flavio_votos'])>int(r['lula_votos']))
    l=next(r for r in h if hora(r)>hora(f) and int(r['lula_votos'])>int(r['flavio_votos']))
    exigir(f['atualizado_tse']=='25/10/2026 19:45:23','Marco de Flávio difere')
    exigir(l['atualizado_tse']=='25/10/2026 20:24:14','Primeiro registro de retorno de Lula difere')
    exigir(all(int(r['lula_votos'])>int(r['flavio_votos']) for r in h if hora(r)>=hora(l)),
           'Lula não conservou a liderança depois do marco identificado')
    mgs=[r for r in ler('dados/saida/2turno/comparacao_ufs.csv') if r['uf']=='MG'][0]
    exigir(int(mgs['saldo_pt_2t'])==109313,'Resultado de MG difere')
    exigir(int(mgs['perda_vantagem_flavio'])==697925,'Mudança de vantagem em MG difere')
    pesquisas=ler('dados/pbi/pesquisa.csv')
    rodadas=[]
    sem_momento=[]
    for r in pesquisas:
        if r['cenario']!='2º turno' or r['tipo']!='totais' or not r['lula'] or not r['flavio']:
            continue
        momento=r['momento']
        if momento not in {'antes_1turno','apos_1turno'}:
            sem_momento.append(r['id'])
            momento=('apos_1turno' if r['campo_fim']>='2026-10-04' else 'antes_1turno') if r['campo_fim'] else None
        if momento=='apos_1turno':rodadas.append(r)
    pesquisa_apos={'rodadas':len(rodadas),
                   'flavio_frente':sum(float(r['flavio'])>float(r['lula']) for r in rodadas),
                   'lula_frente':sum(float(r['lula'])>float(r['flavio']) for r in rodadas),
                   'empates':sum(float(r['lula'])==float(r['flavio']) for r in rodadas),
                   'ids_com_momento_ausente':sem_momento}
    exigir(pesquisa_apos['rodadas']==50 and pesquisa_apos['flavio_frente']==44,
           'Rodadas de votos totais após o primeiro turno diferem do CSV revisado')
    # Importa declarações, não executa os geradores nem grava o modelo.
    tabelas,relacoes,_=gm.carregar_declaracoes()
    exigir('T27 Estimativa' not in {t['nome'] for t in tabelas},'Tabela de regressão ainda declarada')
    meds=[dpt.ler(p) for p in (PBI/'dax').rglob('*.dax') if '_modelo' not in p.parts]
    for m in meds:
        if m['nome'].startswith(('T27 ·','T28 ·','T00 ·','T23 ·','T18 ·')):
            corpo='\n'.join(m['linhas'])
            erros.extend(m['nome']+': '+e for e in problemas(corpo))
            exigir('T27 Estimativa' not in corpo and 't27_fluxo.csv' not in corpo,'Referência de regressão restante: '+m['nome'])
    exigir(not any(m['nome'].startswith('T27 · estimativa ') for m in meds),'Medidas de regressão restantes')
    ctx=mp.carregar_contexto()
    ctx.medidas.update(m['nome'] for m in meds)
    ctx.colunas.update((t['nome'],c['nome']) for t in tabelas for c in t['colunas'])
    itens=mp.carregar_declaracoes(ctx)
    erros.extend(mp.conferir(itens,ctx))
    plano=mp.plano(itens)
    erros.extend(mp.conferir_caminhos(plano))
    for p in (PBI/'scripts/paginas').glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    for p in (PBI/'spec').glob('t2[78]_*.json'):
        s=json.loads(p.read_text(encoding='utf-8'));nomes=[]
        def marcas(ms):
            for m in ms:
                if m.get('name'):nomes.append(m['name'])
                marcas(m.get('marks',[]))
        nomes.extend(d['name'] for d in s.get('data',[]));nomes.extend(d['name'] for d in s.get('signals',[]));marcas(s.get('marks',[]))
        exigir(len(nomes)==len(set(nomes)),f'Nomes Vega repetidos: {p.name}')
        exigir(not any('url' in d for d in s.get('data',[])),f'Dado remoto em Vega: {p.name}')
    sem_mapa=[r['rotulo'] for r in cmp if not r['x'] or not r['y']]
    relatorio={'escopo':'Validação local de dados e declarações; não é prova do motor DAX',
               'oficial_2026_com_exterior':oficial,'municipal_sem_exterior':locais,'viradas_estritas':viradas,
               'primeiro_registro_flavio':f['atualizado_tse'],'primeiro_registro_retorno_lula':l['atualizado_tse'],
               'municipios_sem_posicao_no_mapa':sem_mapa,'medidas_em_disco':len(meds),'relacoes_declaradas':len(relacoes),
               'identidade_observada_sem_exterior':soma,'identidades_municipais_conferidas':len(identidades),
               'pesquisas_2t_votos_totais_apos_1t':pesquisa_apos,
               'arquivos_no_plano':len(plano),'erros':erros}
    destino=PBI/'qa/previa/validacao-pos-eleicao.json';destino.parent.mkdir(parents=True,exist_ok=True)
    destino.write_text(json.dumps(relatorio,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(relatorio,ensure_ascii=False,indent=2))
    return int(bool(erros))


if __name__=='__main__':
    raise SystemExit(main())
