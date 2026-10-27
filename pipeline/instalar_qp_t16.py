"""Instala o resolvedor QP somente no venv autorizado."""
import os,sys,tempfile,uuid
from pathlib import Path
v=Path(__file__).parent/'.venv-ei'
assert Path(sys.prefix).resolve()==v.resolve()
tmp=v/'tmp';tmp.mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(tmp);tempfile.tempdir=str(tmp)
def mkdtemp(suffix=None,prefix=None,dir=None):
    p=Path(dir or tmp)/((prefix or 'tmp')+uuid.uuid4().hex+(suffix or ''));p.mkdir(mode=0o777);return str(p)
tempfile.mkdtemp=mkdtemp
from pip._internal.cli.main import main
raise SystemExit(main(['install','--no-cache-dir','osqp']))
