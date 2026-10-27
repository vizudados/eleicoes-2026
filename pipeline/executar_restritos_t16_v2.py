"""Sensibilidades da nova execução, em sequência e sem amostradores antigos."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1];script=root/'pipeline/inferencia_t16.py'
for c,g in [('principal','oito'),('sem_capitais','oito'),('ate_50mil_habitantes','oito'),('demais_separados','oito'),('sem_nao_votou','oito'),('base_aptos_2turno','oito'),('sem_capitais','seis'),('ate_50mil_habitantes','seis')]:
    subprocess.run([sys.executable,'-I','-X','utf8',str(script),'--etapa','restrito','--cenario',c,'--grupos',g,'--bootstrap','500'],check=True,cwd=root)
