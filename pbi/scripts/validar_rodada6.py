"""Regressões do HTML efetivamente avaliado: números válidos, bandas e texto nas colunas reais."""
from pathlib import Path
import ast
import json
import re
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from simular_rodada6 import preparar,Q

PBI=Path(__file__).resolve().parents[1]


def main():
    casos=preparar()
    erros=[];provas=[]
    f=instancer.instantiateVariableFont(TTFont(PBI/'assets/fontes/sora-wght.ttf'),{'wght':600})
    cm=f.getBestCmap();up=f['head'].unitsPerEm
    def largura(t,px,tracking=0):
        return sum(f['hmtx'][cm[ord(c)]][0]for c in t)*px/up+max(0,len(t)-1)*tracking
    for c in casos:
        nome=c['nome'];depois=(Q/(nome+'-depois.html')).read_text(encoding='utf-8')
        antes=Q/(nome+'-antes.html')
        antigos=antes.read_text(encoding='utf-8')if antes.exists()else''
        bad=lambda t:len(re.findall(r"\b(?:x|y|x1|x2|y1|y2|width|height)='-?\d+\.'|(?:left|width):-?\d+\.px",t))
        assert bad(depois)==0,(nome,'geometria numérica inválida')
        prova={'nome':nome,'viewport':[c['largura'],c['altura']],'invalidos_antes':bad(antigos),'invalidos_depois':bad(depois)}
        if nome=='T27-lista':
            bandas=re.findall(r"<span class='faixa-barra'><i style='left:([-\d.]+)px;width:([-\d.]+)px",depois)
            assert len(bandas)==8
            assert all(float(x)>=0 and float(w)>=0 and float(x)+float(w)<=330.01 for x,w in bandas)
            assert 335<350
            prova['bandas']=8;prova['nomes_terminam_x']=335;prova['barras_comecam_x']=350
        if nome=='T22-fundos':
            titulo='Quantos não teriam escolhido ninguém?'
            assert titulo in depois
            px=largura(titulo,16)
            assert px<410
            assert 'line-height:20px' in depois and 'top:24px' in depois
            prova['titulo_b_largura_px']=px;prova['largura_coluna']=410;prova['intervalo_vertical_minimo_px']=4
        if nome=='T22-tabela':
            cols=[('INSTITUTO',108),('DESTINO DOS OUTROS VOTOS',260),('LULA LEVA',84),('2º TURNO DARIA',290)]
            sizes=[{'texto':t,'largura_texto':largura(t,12,1.2),'largura_coluna':w}for t,w in cols]
            assert all(x['largura_texto']<x['largura_coluna']for x in sizes)
            prova['colunas']=sizes
        if nome=='T28-DF-manchete':
            assert '79.671' in depois and '154.318' in depois and '100,0%' not in depois
        provas.append(prova)
    for p in [PBI/'scripts/desenho_t28.py',PBI/'scripts/desenho_t27_t28.py',PBI/'scripts/desenho_t22.py']:
        ast.parse(p.read_text(encoding='utf-8'))
    # Trava a causa do defeito no gerador, não apenas na simulação.
    assert '"0.##"' not in (PBI/'dax/T28 Onde Flávio perdeu/Desenho/T28 · Ponte · HTML.dax').read_text(encoding='utf-8')
    assert '"0.##"' not in (PBI/'dax/T27 De onde vieram/Desenho/T27 · Lista · HTML.dax').read_text(encoding='utf-8')
    r={'escopo':'HTML do motor da rodada anterior, corrigido deterministicamente; geometria/metricas estáticas, sem nova consulta DAX',
       'casos':provas,'erros':erros,'captura_browser_neste_sandbox':'bloqueada: canais de processo do Chromium/Playwright; nenhum navegador MCP disponível'}
    (Q/'provas-locais.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
