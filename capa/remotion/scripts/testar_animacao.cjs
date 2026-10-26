// Confere o SVG real do mapa sem Chromium. Compila em out/testes-2t, sem mudar os fontes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {test} = require('node:test');
const ts = require('typescript');
const React = require('react');
const {renderToStaticMarkup} = require('react-dom/server');

const raiz = path.resolve(__dirname, '..');
// API local do TypeScript, sem processo filho (spawn é restrito no sandbox).
const config = ts.readConfigFile(path.join(raiz, 'tsconfig.json'), ts.sys.readFile);
if (config.error) throw new Error(ts.flattenDiagnosticMessageText(config.error.messageText, '\n'));
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, raiz, {noEmit: false,
  module: ts.ModuleKind.CommonJS, moduleResolution: ts.ModuleResolutionKind.Node10,
  outDir: path.join(raiz, 'out/testes-2t')});
const programa = ts.createProgram(parsed.fileNames, parsed.options);
const emitido = programa.emit();
const erros = [...parsed.errors, ...ts.getPreEmitDiagnostics(programa), ...emitido.diagnostics];
if (erros.length) throw new Error(ts.formatDiagnosticsWithColorAndContext(erros, {
  getCanonicalFileName: (p) => p, getCurrentDirectory: () => raiz, getNewLine: () => '\n'}));
const {Mapa} = require('../out/testes-2t/src/Mapa.js');
const {T, FPS, QUADROS, hexRgb} = require('../out/testes-2t/src/tempo.js');
const {inicioCor1, iniciosCor2, brilhoTroca} = require('../out/testes-2t/src/municipios.js');
const m = require('../public/dados/capa.json').municipios;
const cor1 = m.d.map((d, i) => inicioCor1(d, m.u[i]));
const cor2 = iniciosCor2(cor1);
const svg = (t) => renderToStaticMarkup(React.createElement('svg', null, React.createElement(Mapa, {t})));
const circulos = (s) => [...s.matchAll(/<circle cx="([^"]+)" cy="([^"]+)" r="([^"]+)" fill="(rgb\([^)]+\))" opacity="([^"]+)"/g)];
const corRgb = (hex) => `rgb(${hexRgb(hex).join(',')})`;

test('o 1º turno está completo em 12,4 s e permanece igual até 13,2 s', () => {
  const a = svg(372 / FPS);
  assert.equal(a, svg(T.segundoTurno[0]));
  const c = circulos(a);
  assert.equal(c.length, 5570);
  c.forEach((p, i) => assert.equal(p[4], corRgb(m.cor[i])));
  assert.ok(!a.includes('data-municipio='));
  assert.ok(Math.max(...cor1) + T.corDur <= 12.4);
});

test('a segunda onda começa em 13,2 s, termina em 16,7 s e mantém a ordem espacial', () => {
  assert.equal(Math.min(...cor2), 13.2);
  assert.equal(Math.max(...cor2) + T.corDur, 16.7);
  const ordem = cor1.map((_, i) => i).sort((a, b) => cor1[a] - cor1[b]);
  for (let k = 1; k < ordem.length; k++) assert.ok(cor2[ordem[k - 1]] <= cor2[ordem[k]]);
  const meio = circulos(svg(14.966666666666667));
  assert.ok(meio.some((p, i) => p[4] === corRgb(m.cor[i]) && m.cor[i] !== m.cor2[i]));
  assert.ok(meio.some((p, i) => p[4] === corRgb(m.cor2[i]) && m.cor[i] !== m.cor2[i]));
  assert.ok(meio.some((p, i) => p[4] !== corRgb(m.cor[i]) && p[4] !== corRgb(m.cor2[i])));
});

test('todos os pontos terminam na cor do 2º turno, com posição e raio preservados', () => {
  const antes = circulos(svg(12.4));
  const fim = svg(T.segundoTurno[1]);
  const depois = circulos(fim);
  assert.equal(depois.length, 5570);
  depois.forEach((p, i) => {
    assert.deepEqual(p.slice(1, 4), antes[i].slice(1, 4));
    assert.equal(p[4], corRgb(m.cor2[i]));
    assert.equal(p[5], '1');
  });
  assert.ok(!fim.includes('data-municipio='));
  assert.equal(fim, svg(18));
  assert.equal(fim, svg((QUADROS - 1) / FPS));
});

test('só as 212 trocas recebem brilho e os dois sentidos têm a mesma curva', () => {
  m.troca.forEach((troca, i) => {
    const centro = cor2[i] + T.corDur / 2;
    assert.equal(brilhoTroca(centro, cor2[i], troca) > 0, troca !== 0);
    assert.equal(brilhoTroca(cor2[i], cor2[i], troca), 0);
    assert.equal(brilhoTroca(cor2[i] + T.corDur, cor2[i], troca), 0);
  });
  for (let q = 0; q <= 60; q++) {
    assert.equal(brilhoTroca(13 + q / 100, 13, 1), brilhoTroca(13 + q / 100, 13, -1));
  }
  for (const direcao of [1, -1]) {
    const i = m.troca.indexOf(direcao);
    const s = svg(cor2[i] + T.corDur / 2);
    assert.ok(s.includes(`data-municipio="${m.cd_ibge[i]}"`));
    assert.ok(s.includes('clip-path="url(#limite-viradas)"'));
  }
  assert.equal(m.troca.filter(Boolean).length, 212);
});

test('há 90 quadros de assentamento e o codificador espera a mesma duração', () => {
  assert.equal(QUADROS, 630);
  assert.equal(QUADROS - T.assenta * FPS, 90);
  const ps = fs.readFileSync(path.join(raiz, 'scripts/codificar.ps1'), 'utf8');
  assert.ok(ps.includes(`$quadros = ${QUADROS}`));
  assert.ok(ps.includes('capa-2t.mp4'));
  assert.ok(ps.includes('capa-2t.webm'));
  assert.ok(ps.includes('capa-2t-final.jpg'));
  assert.ok(ps.includes('capa-2t-inicio.jpg'));
});
