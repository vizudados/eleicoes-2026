from pathlib import Path
from datetime import datetime,timezone
import json
p=Path(__file__).resolve().parents[1]/'dados/saida/2turno/inferencia_t16'
for c in ['sem_capitais','ate_50mil_habitantes']:
    o={'utc':datetime.now(timezone.utc).isoformat(),'cenario':c,'efeito_uf':True,'grupos':'seis','convergiu':False,
       'status':'interrompida_para_usar_desenho_regional_viavel_no_prazo','amostras_posteriores_concluidas':0,
       'motivo':'A versão regional sem desvio UF será confrontada com sua própria base completa. Esta tentativa ainda estava em aquecimento e não fornece resultados.'}
    (p/f'diagnostico_bayes_{c}_seis.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (p/f'bayes_{c}_seis.log').open('a',encoding='utf-8') as f:f.write(json.dumps(o,ensure_ascii=False)+'\n')
