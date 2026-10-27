"""Executa testes independentes em sequência, sem editar o painel."""
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
script=root/'pipeline/inferencia_t16.py'
for c in ['sem_capitais','ate_50mil_habitantes','demais_separados','sem_nao_votou','base_aptos_2turno']:
    subprocess.run([sys.executable,'-I','-X','utf8',str(script),'--etapa','restrito','--cenario',c,'--bootstrap','500'],check=True,cwd=root)
