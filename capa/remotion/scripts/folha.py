"""Folha de contato dos quadros de revisão: python scripts/folha.py saida.png q000 q030 ... (largura 960 cada)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
pasta = Path(__file__).resolve().parent.parent / 'out' / 'quadros'
saida, nomes = sys.argv[1], sys.argv[2:]
esc = float(nomes.pop(0)[2:]) if nomes and nomes[0].startswith('x=') else 0.5
ims = [Image.open(pasta / f'{n}.png').convert('RGB') for n in nomes]
w, h = int(1920 * esc), int(1080 * esc)
col = 2 if len(ims) > 1 else 1
lin = (len(ims) + col - 1) // col
folha = Image.new('RGB', (w * col, h * lin), 'black')
for i, (n, im) in enumerate(zip(nomes, ims)):
    r = im.resize((w, h), Image.LANCZOS)
    ImageDraw.Draw(r).text((8, 6), n, fill=(255, 80, 80))
    folha.paste(r, ((i % col) * w, (i // col) * h))
folha.save(saida)
