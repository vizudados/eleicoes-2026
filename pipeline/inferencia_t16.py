"""Entrada reprodutível da análise T16 reiniciada em 27/10/2026."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('inferencia_t16_v2',Path(__file__).with_name('inferencia_t16_v2.py'))
modulo=importlib.util.module_from_spec(spec);spec.loader.exec_module(modulo)
if __name__=='__main__':modulo.main()
