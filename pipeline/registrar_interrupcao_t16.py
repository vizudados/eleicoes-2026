"""Registra a tentativa de oito origens sem promover amostras de aquecimento."""
from pathlib import Path
import json
from datetime import datetime,timezone
p=Path(__file__).resolve().parents[1]/'dados/saida/2turno/inferencia_t16'
o={'utc':datetime.now(timezone.utc).isoformat(),'convergiu':False,'status':'interrompida_por_viabilidade_no_prazo_de_90_minutos',
   'cenario':'principal','grupos':'oito','efeito_uf':True,'cadeias':4,'aquecimento_planejado':1000,'amostras_planejadas_por_cadeia':2000,
   'ultima_iteracao_aproximada':300,'amostras_posteriores_concluidas':0,
   'motivo':'Ritmo observado não permitiria concluir e validar dentro do prazo. Apenas aquecimento; não há matriz utilizável nem diagnóstico de convergência concluído.'}
(p/'diagnostico_bayes_principal_oito.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (p/'bayes_principal_oito.log').open('a',encoding='utf-8') as f:f.write(json.dumps(o,ensure_ascii=False)+'\n')
