// Testes da geometria real do Remotion e do contrato com a T23, sem Chromium.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {test} = require('node:test');
const carregar = require('./carregar_encerramento.cjs');
const {provar} = require('./provar_encerramento.cjs');
const runtime = carregar();
const {dados, roteiro, geometria, svg, raiz, FPS_ENCERRAMENTO, QUADROS_ENCERRAMENTO} = runtime;
const h = roteiro.hemiciclo;
const ordenados = [...dados.lotes].sort((a, b) => a.ordemAngular - b.ordemAngular);
const cunha = ordenados.filter(l => l.diferenca);
const perto = (a, b, eps = 0.000003) => Math.abs(a - b) < eps;

test('cada voto é conservado por origem, lote e candidatura, incluindo exterior e frações', () => {
  const origens = dados.origens.map(() => ({lula: 0, flavio: 0}));
  const lotes = dados.lotes.map(() => 0);
  dados.fragmentos.forEach(([o, d, votos]) => {
    assert.ok(Number.isSafeInteger(votos) && votos > 0 && votos <= dados.unidade);
    origens[o][dados.lotes[d].candidato] += votos;
    lotes[d] += votos;
  });
  dados.origens.forEach((o, i) => {
    assert.equal(origens[i].lula, o.lula, o.id);
    assert.equal(origens[i].flavio, o.flavio, o.id);
  });
  dados.lotes.forEach((l, i) => {
    assert.equal(lotes[i], l.votos);
    assert.ok(perto((l.r / h.raioPonto) ** 2, l.votos / dados.unidade));
  });
  assert.deepEqual(dados.totais, {lula: 64256232, flavio: 59826041});
  assert.equal(dados.diferenca, 4430191);
  for (const candidato of ['lula', 'flavio']) {
    assert.equal(dados.lotes.filter(l => l.candidato === candidato).reduce((s, l) => s + l.votos, 0), dados.totais[candidato]);
  }
  assert.equal(dados.lotes.filter(l => l.votos === 50000).length, 2480);
  assert.deepEqual(dados.lotes.filter(l => l.votos < 50000).map(l => l.votos).sort((a, b) => a - b), [26041, 26041, 30191]);
});

test('2.483 assentos: arcos completos, equidistantes e sem corredor ou coluna central', () => {
  assert.equal(dados.lotes.length, 2483);
  assert.ok(!('corredor' in h));
  assert.equal(new Set(dados.lotes.map(l => l.fila)).size, 36);
  for (let fila = 0; fila < h.fileiras; fila++) {
    const pontos = ordenados.filter(l => l.fila === fila);
    if (fila === 0) {
      assert.equal(pontos.length, 1);
      assert.equal(pontos[0].x, h.x);
      assert.equal(pontos[0].y, h.base);
      continue;
    }
    assert.ok(pontos.length > 1);
    assert.ok(perto(pontos[0].angulo, 0));
    assert.ok(perto(pontos.at(-1).angulo, Math.PI));
    const passo = Math.PI / (pontos.length - 1);
    pontos.forEach((p, j) => {
      assert.ok(perto(p.angulo, passo * j, 1e-12), 'Vão angular na fileira ' + fila);
      assert.ok(perto(Math.hypot(p.x - h.x, p.y - h.base), h.raioInterno + fila * (h.raioExterno - h.raioInterno) / (h.fileiras - 1)));
    });
    const juntoDoEixo = pontos.reduce((a, b) => Math.abs(a.angulo - Math.PI / 2) < Math.abs(b.angulo - Math.PI / 2) ? a : b);
    assert.ok(Math.abs(juntoDoEixo.angulo - Math.PI / 2) <= passo / 2 + 1e-12);
  }
});

test('as candidaturas ocupam por ângulo global, sem blocos artificiais por fileira', () => {
  assert.deepEqual(ordenados.map(l => l.ordemAngular), Array.from({length: 2483}, (_, i) => i));
  for (let i = 1; i < ordenados.length; i++) assert.ok(ordenados[i].angulo >= ordenados[i - 1].angulo - 1e-12);
  ordenados.forEach((l, i) => assert.equal(l.candidato, i < 1286 ? 'lula' : 'flavio'));
  assert.equal(ordenados.filter(l => l.candidato === 'flavio').length, 1197);
  assert.equal(ordenados.filter(l => l.candidato === 'lula').length, 1286);
});

test('a cunha é exatamente a fatia simétrica de 89 assentos, com área e votos simétricos', () => {
  assert.equal(cunha.length, 89);
  assert.deepEqual(cunha.map(l => l.ordemAngular), Array.from({length: 89}, (_, i) => 1197 + i));
  assert.equal(cunha.reduce((s, l) => s + l.votos, 0), 4430191);
  assert.equal(cunha.filter(l => l.x < h.x).length, 44);
  assert.equal(cunha.filter(l => l.x > h.x).length, 44);
  assert.equal(cunha.filter(l => l.x === h.x).length, 1);
  cunha.forEach(l => {
    const espelho = ordenados[2482 - l.ordemAngular];
    assert.ok(espelho.diferenca);
    assert.ok(perto(l.x + espelho.x, 2 * h.x));
    assert.equal(l.y, espelho.y);
    assert.equal(l.votos, espelho.votos);
    assert.equal(l.r, espelho.r);
  });
  assert.equal(ordenados[1241].votos, 30191);
  const metade = dados.lotes.filter(l => l.x < h.x).reduce((s, l) => s + l.votos, 0) + ordenados[1241].votos / 2;
  assert.equal(metade, (dados.totais.lula + dados.totais.flavio) / 2);
  for (let i = 0; i < 1197; i++) {
    assert.ok(perto(ordenados[i].x + ordenados[2482 - i].x, 1920));
    assert.equal(ordenados[i].y, ordenados[2482 - i].y);
    assert.equal(ordenados[i].votos, ordenados[2482 - i].votos);
  }
});

test('o mapa inicial tem 620 px, centrado; não há ponto externo ou rótulo solto', () => {
  assert.equal(roteiro.mapa.altura, 620);
  assert.equal(roteiro.mapa.x, 960);
  assert.equal(roteiro.mapa.y, 560);
  assert.ok(perto(roteiro.mapa.escala * 560, 620));
  const mapa = dados.origens.filter(o => o.mapa);
  assert.equal(mapa.length, 5571);
  assert.equal(dados.origens.filter(o => !o.mapa).length, 1);
  const capa = require('../public/dados/capa.json').municipios;
  const indices = new Map(capa.cd_ibge.map((id, i) => [id, i]));
  for (const o of mapa) {
    let x, y;
    if (o.id === '5101837') {
      x = roteiro.boaEsperanca.municipiosOrigem.reduce((s, id) => s + capa.x[indices.get(id)], 0) / 2;
      y = roteiro.boaEsperanca.municipiosOrigem.reduce((s, id) => s + capa.y[indices.get(id)], 0) / 2;
    } else { x = capa.x[indices.get(o.id)]; y = capa.y[indices.get(o.id)]; }
    assert.ok(perto(o.x, 960 + (x - 960) * roteiro.mapa.escala, 0.00051), o.id);
    assert.ok(perto(o.y, 560 + (y - 583) * roteiro.mapa.escala, 0.00051), o.id);
  }
  const abertura = Array.from(geometria.circulosNoTempo(2));
  assert.equal(abertura.filter(p => p.classe === 'municipio').length, 5571);
  for (const p of abertura.filter(p => p.classe === 'fragmento')) {
    const origem = dados.origens[dados.fragmentos[p.id][0]];
    assert.ok(origem.mapa);
    assert.equal(p.x, origem.x);
    assert.equal(p.y, origem.y);
  }
  assert.ok(!svg(2).includes('data-origem="ZZ"'));
  assert.ok(!/<text|<image|<script/.test(svg(2)));
  assert.ok(!svg(2).includes('Boa Esperança do Norte'));
  assert.equal(geometria.opacidadeFio(2), 0);
  assert.ok(geometria.opacidadeFio(4) > 0);
});

test('a cunha chega por último; números e realce entram depois da entrega', () => {
  const comuns = dados.lotes.filter(l => !l.diferenca);
  assert.ok(Math.min(...cunha.map(l => l.partida + l.duracao - 0.35)) > Math.max(...comuns.map(l => l.partida + l.duracao)));
  assert.ok(roteiro.html.resultado >= Math.max(...cunha.map(l => l.partida + l.duracao)) + 0.19);
  assert.equal(roteiro.html.diferenca, roteiro.diferenca[0]);
  assert.ok(roteiro.fecharRecorte < roteiro.html.resultado);
});

test('os pontos finais não encostam, mesmo com o contorno fino da cunha', () => {
  const grade = new Map();
  for (const l of dados.lotes) {
    const r = l.r + (l.diferenca ? 0.35 + 0.55 / 2 : 0);
    const gx = Math.floor(l.x / 8), gy = Math.floor(l.y / 8);
    for (let x = gx - 1; x <= gx + 1; x++) for (let y = gy - 1; y <= gy + 1; y++) {
      for (const outro of grade.get(x + ',' + y) || []) assert.ok(Math.hypot(l.x - outro.x, l.y - outro.y) > r + outro.r + 0.3);
    }
    const chave = gx + ',' + gy;
    if (!grade.has(chave)) grade.set(chave, []);
    grade.get(chave).push({...l, r});
  }
});

test('o SVG real termina com 2.483 pontos e 89 contornos, sem texto no vídeo', () => {
  const final = svg(12);
  assert.equal([...final.matchAll(/data-lote=/g)].length, 2483);
  assert.equal([...final.matchAll(/data-diferenca=/g)].length, 89);
  assert.ok(final.includes('data-eixo="50-por-cento"'));
  assert.ok(!/<text|<image|<script|NaN/.test(final));
  assert.equal([...final.matchAll(/opacity="0.64"/g)].length, 2394);
});

test('o quadro final é calmo: 90 SVGs idênticos e sequência exclusiva da rodada 3', () => {
  assert.equal(FPS_ENCERRAMENTO, 30);
  assert.equal(QUADROS_ENCERRAMENTO, 450);
  const final = svg(12);
  for (let f = 360; f < 450; f++) assert.equal(svg(f / 30), final);
  assert.notEqual(svg(3), svg(4));
  const ps = fs.readFileSync(path.join(raiz, 'scripts/codificar_encerramento.ps1'), 'utf8');
  assert.ok(ps.includes('out\\seq-encerramento-r3'));
  assert.ok(ps.includes('element-360.png'));
});

test('a prova usa o SVG real e as mesmas caixas da T23: zero sobreposição em 450 quadros', () => {
  const resultado = provar(runtime);
  assert.ok(resultado.pontosConferidos > 3000000);
  assert.deepEqual(resultado.contatos, []);
  assert.deepEqual(resultado.contatosFinal, []);
  assert.deepEqual(resultado.contatosComRecorteCss, []);
});

const saida = path.join(raiz, '../../pbi/qa/encerramento/rodada3');
fs.mkdirSync(saida, {recursive: true});
for (const f of [0, 60, 90, 150, 216, 240, 261, 267, 285, 303, 327, 360, 449]) {
  fs.writeFileSync(path.join(saida, 'quadro-' + String(f).padStart(3, '0') + '.svg'), svg(f / 30));
}
