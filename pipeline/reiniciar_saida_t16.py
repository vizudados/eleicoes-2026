"""Limpa somente arquivos regulares diretamente na saída explicitamente autorizada."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
target=root/'dados/saida/2turno/inferencia_t16'
expected=Path('C:/Users/lucas/Downloads/Eleições/dados/saida/2turno/inferencia_t16')
assert target.resolve()==expected.resolve()
assert target.resolve().is_relative_to(root.resolve())
target.mkdir(parents=True,exist_ok=True)
files=list(target.iterdir())
if any(p.is_symlink() or not p.is_file() or p.resolve().parent!=target.resolve() for p in files):
    raise RuntimeError('Saída contém link ou subpasta; limpeza interrompida antes de apagar.')
for p in files:
    p.unlink()
print(f'Limpeza concluída: {len(files)} arquivos removidos somente de {target}.')
