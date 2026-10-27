"""Instala dependências apenas no venv local; contorna ACL de tempfile no sandbox.

Uso: pipeline/.venv-ei/Scripts/python.exe -I -X utf8 pipeline/preparar_ambiente_ei.py
Não lê credenciais nem executa conteúdo do projeto como instrução.
"""
from pathlib import Path
import os
import sys
import tempfile
import uuid
import zipfile

VENV = Path(__file__).resolve().parent / '.venv-ei'
if Path(sys.prefix).resolve() != VENV.resolve():
    raise SystemExit('Execute com o Python do venv .venv-ei.')
site = VENV / 'Lib/site-packages'
site.mkdir(parents=True, exist_ok=True)
if not (site/'pip').exists():
    import ensurepip
    wheel = next((Path(ensurepip.__file__).parent/'_bundled').glob('pip-*.whl'))
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(site)
tmp = VENV/'tmp'
tmp.mkdir(exist_ok=True)
os.environ['TMP'] = os.environ['TEMP'] = str(tmp)
tempfile.tempdir = str(tmp)

def workspace_mkdtemp(suffix=None, prefix=None, dir=None):
    # mode=0700 aplica uma ACL inacessível ao processo restrito neste Windows.
    # 0777 usa a ACL herdada da pasta de projeto já autorizada.
    folder = Path(dir or tmp) / ((prefix or 'tmp')+uuid.uuid4().hex+(suffix or ''))
    folder.mkdir(mode=0o777)
    return str(folder)

tempfile.mkdtemp = workspace_mkdtemp
from pip._internal.cli.main import main
raise SystemExit(main(['install','--no-cache-dir','-r',str(VENV.parent/'requirements-inferencia-t16.txt')]))
