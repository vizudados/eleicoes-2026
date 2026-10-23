// render_vega.mjs — desenha um spec Vega do Deneb fora do Power BI, para a prévia (pbi/scripts/previa.py).
// Entrada: um JSON { spec, dados, largura, altura } (dados = linhas do dataset, como o Deneb injeta em "dataset").
// Saída: SVG. Uso: node render_vega.mjs entrada.json saida.svg
// Imita o Deneb no que importa para a foto: o data "dataset" recebe as linhas (com __row__ e __selected__ neutro),
// width/height = tamanho do visual, e as funções de expressão do Deneb existem (pbiFormat devolve o valor em texto;
// pbiCrossFilterApply e afins não fazem nada). Animação: o spec deve ter estado final estático (L019); a prévia
// desenha o quadro inicial do runtime sem timer.
import { readFileSync, writeFileSync } from "node:fs";
import * as vega from "vega";

const [entrada, saida] = process.argv.slice(2);
if (!entrada || !saida) {
  console.error("uso: node render_vega.mjs entrada.json saida.svg");
  process.exit(2);
}
const { spec, dados, largura, altura } = JSON.parse(readFileSync(entrada, "utf8"));

const nada = () => null;
for (const [nome, fn] of Object.entries({
  pbiFormat: (v) => (v == null ? "" : String(v)),
  pbiFormatAutoUnit: (v) => (v == null ? "" : String(v)),
  pbiCrossFilterApply: nada,
  pbiCrossFilterClear: nada,
  pbiCrossHighlightApply: nada,
  pbiColor: () => "#0B0B0C",
  pbiContainsText: (a, b) => String(a ?? "").toLowerCase().includes(String(b ?? "").toLowerCase()),
})) {
  try { vega.expressionFunction(nome, fn); } catch { /* já registrada */ }
}

const linhas = (dados || []).map((r, i) => ({ ...r, __row__: i, __selected__: "neutral" }));
const s = JSON.parse(JSON.stringify(spec));
s.width = largura;
s.height = altura;
s.autosize = s.autosize || { type: "fit", contains: "padding" };
s.data = (s.data || []).map((d) => (d.name === "dataset" ? { ...d, values: linhas } : d));
s.signals = (s.signals || []).map((g) =>
  g.name === "pbiContainerWidth" ? { ...g, value: largura } : g.name === "pbiContainerHeight" ? { ...g, value: altura } : g);
if (!s.signals.find((g) => g.name === "pbiContainerWidth")) s.signals.push({ name: "pbiContainerWidth", value: largura });
if (!s.signals.find((g) => g.name === "pbiContainerHeight")) s.signals.push({ name: "pbiContainerHeight", value: altura });

try {
  const view = new vega.View(vega.parse(s), { renderer: "none" });
  await view.runAsync();
  const svg = await view.toSVG();
  writeFileSync(saida, svg, "utf8");
  console.log(`ok ${saida} (${linhas.length} linhas)`);
  // spec com evento `timer` (entrada animada) cria um setInterval na View: finaliza e sai para o node não ficar vivo
  view.finalize();
  process.exit(0);
} catch (e) {
  console.error("ERRO vega:", e && e.message ? e.message : e);
  process.exit(1);
}
