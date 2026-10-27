"""Atualiza apenas o ponto de entrada próprio para o reinício autorizado."""
from pathlib import Path
p=Path(__file__).with_name('inferencia_t16.py')
p.write_text('''"""Entrada reprodutível da análise T16 reiniciada em 27/10/2026."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('inferencia_t16_v2',Path(__file__).with_name('inferencia_t16_v2.py'))
modulo=importlib.util.module_from_spec(spec);spec.loader.exec_module(modulo)
if __name__=='__main__':modulo.main()
''',encoding='utf-8')
