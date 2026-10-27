// SVG real e geometria pura. A entrada do HTML é verificada em CSS, sem DOM com JavaScript.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {test} = require('node:test');
const ts = require('typescript');
const React = require('react');
const {renderToStaticMarkup} = require('react-dom/server');
const raiz = path.resolve(__dirname, '..');
const dados = require('../public/dados/encerramento.json');
const roteiro = require('../src/encerramento/roteiro.json');
const config = ts.readConfigFile(path.join(raiz, 'tsconfig.json'), ts.sys.readFile);
if (config.error) throw new Error(ts.flattenDiagnosticMessageText(config.error.messageText, '\n'));
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, raiz, {noEmit: false,
  module: ts.ModuleKind.CommonJS, moduleResolution: ts.ModuleResolutionKind.Node10,
  outDir: path.join(raiz, 'out/testes-encerramento')});
const programa = ts.createProgram(parsed.fileNames, parsed.options);
const emitido = programa.emit();
const erros = [...parsed.errors, ...ts.getPreEmitDiagnostics(programa), ...emitido.diagnostics];
if (erros.length) throw new Error(ts.formatDiagnosticsWithColorAndContext(erros, {
  getCanonicalFileName: (p) => p, getCurrentDirectory: () => raiz, getNewLine: () => '\n'}));
const {DesenhoEncerramento, FPS_ENCERRAMENTO, QUADROS_ENCERRAMENTO} = require('../out/testes-encerramento/src/encerramento/Encerramento.js');
const {posicaoFragmento} = require('../out/testes-encerramento/src/encerramento/geometria.js');
const svg = (t) => renderToStaticMarkup(React.createElement(DesenhoEncerramento, {t}));
const h = roteiro.hemiciclo;
const area = roteiro.areaGrafica;
const comuns = dados.lotes.filter(l => !l.diferenca);
const extras = dados.lotes.filter(l => l.diferenca);

test('cada voto é conservado por origem, candidatura e lote, incluindo frações', () => {
  const porOrigem = dados.origens.map(() => ({lula: 0, flavio: 0}));
  const porLote = dados.lotes.map(() => 0);
  for (const [origem, destino, votos] of dados.fragmentos) {
    assert.ok(Number.isSafeInteger(votos) && votos > 0 && votos <= dados.unidade);
    porOrigem[origem][dados.lotes[destino].candidato] += votos;
    porLote[destino] += votos;
  }
  dados.origens.forEach((o, i) => {
    assert.equal(porOrigem[i].lula, o.lula, o.id);
    assert.equal(porOrigem[i].flavio, o.flavio, o.id);
  });
  dados.lotes.forEach((l, i) => assert.equal(porLote[i], l.votos));
  assert.deepEqual(dados.totais, {lula: 64256232, flavio: 59826041});
  for (const candidato of ['lula', 'flavio']) {
    assert.equal(dados.lotes.filter(l => l.candidato === candidato).reduce((s, l) => s + l.votos, 0), dados.totais[candidato]);
  }
  assert.equal(dados.diferenca, 4430191);
});

test('todas as origens permanecem: malha, município sem coordenada e exterior', () => {
  assert.equal(dados.origens.length, 5572);
  assert.equal(dados.origens.filter(o => o.mapa).length, 5570);
  assert.deepEqual(dados.origens.filter(o => !o.mapa).map(o => o.id), ['5101837', 'ZZ']);
  assert.deepEqual(dados.exterior, {lula: 200154, flavio: 171497});
  assert.ok(roteiro.mapa.escala / 0.51 > 1.25);
  dados.origens.forEach(o => {
    assert.ok(o.x >= area.x && o.x <= area.x + area.largura);
    assert.ok(o.y >= area.y && o.y <= area.y + area.altura);
  });
});

test('hemiciclo grande: 33 fileiras, raio de 280 px e pares exatamente espelhados', () => {
  const a = comuns.filter(l => l.candidato === 'flavio');
  const b = comuns.filter(l => l.candidato === 'lula');
  assert.equal(a.length, 1197);
  assert.equal(b.length, 1197);
  assert.equal(h.raioExterno, 280);
  assert.equal(new Set(a.map(l => l.fila)).size, 33);
  a.forEach((l, i) => {
    assert.ok(Math.abs(l.x + b[i].x - 1920) < 0.000002);
    for (const k of ['votos', 'y', 'r', 'partida', 'duracao', 'fila']) assert.equal(l[k], b[i][k]);
    assert.ok(l.x < h.x && b[i].x > h.x);
  });
  dados.lotes.forEach(l => {
    const raio = Math.hypot(l.x - h.x, l.y - h.base);
    assert.ok(raio >= h.raioInterno - 0.000002 && raio <= h.raioExterno + 0.000002);
    assert.ok(Math.abs((l.r / h.raioPonto) ** 2 - l.votos / dados.unidade) < 0.000002);
  });
});

test('os 89 excedentes atravessam o eixo para a esquerda e chegam por último', () => {
  assert.equal(extras.length, 89);
  assert.equal(extras.reduce((s, l) => s + l.votos, 0), 4430191);
  extras.forEach(l => assert.ok(l.candidato === 'lula' && l.x + l.r < h.x));
  const fimComuns = Math.max(...comuns.map(l => l.partida + l.duracao));
  const inicioEntregasExtras = Math.min(...extras.map(l => l.partida + l.duracao - 0.35));
  const fimExtras = Math.max(...extras.map(l => l.partida + l.duracao));
  assert.ok(inicioEntregasExtras > fimComuns);
  assert.ok(roteiro.html.resultado >= fimExtras + 0.19);
  assert.equal(roteiro.html.diferenca, roteiro.diferenca[0]);
  assert.ok(roteiro.html.achados > roteiro.html.participacao + roteiro.entrada);
});

test('pontos finais não encostam, incluindo os contornos dos excedentes', () => {
  const grade = new Map();
  for (const lote of dados.lotes) {
    const raio = lote.r + (lote.diferenca ? 1 : 0);
    const gx = Math.floor(lote.x / 8), gy = Math.floor(lote.y / 8);
    for (let x = gx - 1; x <= gx + 1; x++) for (let y = gy - 1; y <= gy + 1; y++) {
      for (const outro of grade.get(x + ',' + y) || []) {
        const minimo = raio + outro.raio + 0.65;
        assert.ok(Math.hypot(lote.x - outro.x, lote.y - outro.y) > minimo, 'Assentos encostados');
      }
    }
    const chave = gx + ',' + gy;
    if (!grade.has(chave)) grade.set(chave, []);
    grade.get(chave).push({...lote, raio});
  }
});

test('todos os voos ficam na área livre, varrendo cada quadro e cada fragmento', () => {
  // Independe da carga: nenhuma caixa de texto cruza o retângulo gráfico.
  for (const [nome, [x, y, w, a]] of Object.entries(roteiro.textos)) {
    assert.ok(x + w <= area.x || x >= area.x + area.largura || y + a <= area.y || y >= area.y + area.altura, nome);
  }
  let conferidos = 0;
  for (let f = 0; f < 270; f++) {
    const t = f / 30;
    for (const [o, d, votos] of dados.fragmentos) {
      const lote = dados.lotes[d];
      if (t < 1.7 || t > lote.partida + lote.duracao) continue;
      const p = posicaoFragmento(dados.origens[o], lote, t);
      const r = h.raioPonto * Math.sqrt(votos / dados.unidade);
      assert.ok(p.x - r >= area.x && p.x + r <= area.x + area.largura, 'Voo fora da largura: ' + f);
      assert.ok(p.y - r >= area.y && p.y + r <= area.y + area.altura, 'Voo fora da altura: ' + f);
      conferidos++;
    }
  }
  assert.ok(conferidos > 1000000);
});

test('SVG contém hemiciclo completo e realce, sem imagens, texto ou faixa antiga', () => {
  const fim = svg(roteiro.html.resultado);
  assert.equal([...fim.matchAll(/data-lote=/g)].length, 2483);
  assert.ok(fim.includes('data-camada="fragmentos"></g>'));
  assert.ok(fim.includes('clip-path="url(#t23-area-livre)"'));
  assert.ok(fim.includes('data-eixo="comparacao"'));
  assert.ok(!/<image|<text|<script|NaN/.test(fim));
  const realce = svg(roteiro.diferenca[1]);
  assert.equal([...realce.matchAll(/data-diferenca=/g)].length, 89);
  assert.equal([...realce.matchAll(/opacity="0.74"/g)].length, 2394);
  assert.equal([...realce.matchAll(/fill="#D9877B" opacity="1"/g)].length, 89);
});

test('90 quadros finais são idênticos; codificador usa sequência exclusiva da rodada 2', () => {
  assert.equal(FPS_ENCERRAMENTO, 30);
  assert.equal(QUADROS_ENCERRAMENTO, 450);
  const final = svg(12);
  for (let f = 360; f < 450; f++) assert.equal(svg(f / 30), final, 'quadro ' + f);
  assert.notEqual(svg(3), svg(4));
  const ps = fs.readFileSync(path.join(raiz, 'scripts/codificar_encerramento.ps1'), 'utf8');
  assert.ok(ps.includes('$quadros = 450'));
  assert.ok(ps.includes('element-360.png'));
  assert.ok(ps.includes('out\\seq-encerramento-r2'));
});

const saida = path.join(raiz, '../../pbi/qa/encerramento/rodada2');
fs.mkdirSync(saida, {recursive: true});
for (const f of [0, 60, 90, 150, 216, 240, 261, 267, 285, 303, 327, 360, 449]) {
  fs.writeFileSync(path.join(saida, 'quadro-' + String(f).padStart(3, '0') + '.svg'), svg(f / 30));
}
