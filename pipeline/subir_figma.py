"""Envia PNGs para as URLs de upload do Figma (MCP upload_assets) e grava os imageHash em `arte/hashes.json`.

Uso: python -I -X utf8 pipeline/subir_figma.py <pagina_id> <arquivo1>=<uuid1> <arquivo2>=<uuid2> ...
O uuid é o trecho de `.../mcp/upload/<uuid>/submit` devolvido pelo upload_assets; o nome do hash é o do arquivo sem .png.
"""
import concurrent.futures as cf
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
HASHES = RAIZ / "arte" / "hashes.json"


def enviar(pagina, arquivo, uid):
    url = f"https://mcp.figma.com/mcp/upload/{uid}/submit?scaleMode=FILL&currentPageId={quote(pagina)}"
    r = subprocess.run(["curl", "-sS", "-X", "POST", "-F", f"file=@{arquivo};type=image/png", url],
                       capture_output=True, text=True)
    try:
        return Path(arquivo).stem, json.loads(r.stdout).get("imageHash")
    except json.JSONDecodeError:
        return Path(arquivo).stem, None


if __name__ == "__main__":
    pagina, pares = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
    with cf.ThreadPoolExecutor(8) as ex:
        res = dict(ex.map(lambda p: enviar(pagina, *p), pares))
    hashes = json.loads(HASHES.read_text(encoding="utf-8"))
    hashes.update({k: v for k, v in res.items() if v})
    HASHES.write_text(json.dumps(hashes, indent=1, ensure_ascii=False), encoding="utf-8")
    falhas = [k for k, v in res.items() if not v]
    print(f"{len(res) - len(falhas)} enviados · falhas: {falhas}")
