// Renderiza quadros avulsos para revisão: node scripts/quadros.mjs 0 60 120 ... (saída em out/quadros/)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const quadros = process.argv.slice(2).map(Number);
const serveUrl = await bundle({entryPoint: path.join(raiz, 'src/index.ts'), publicDir: path.join(raiz, 'public')});
const composition = await selectComposition({serveUrl, id: 'Capa'});
for (const frame of quadros) {
  const t0 = Date.now();
  const output = path.join(raiz, 'out', 'quadros', `q${String(frame).padStart(3, '0')}.png`);
  await renderStill({composition, serveUrl, output, frame, imageFormat: 'png'});
  console.log(`quadro ${frame} · ${Date.now() - t0} ms`);
}
