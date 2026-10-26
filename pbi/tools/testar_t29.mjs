// Prova local do runtime Vega instalado. Não é prova do motor DAX nem de tooltip do Power BI.
import {readFileSync, writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import * as vega from 'vega';

const raiz = new URL('../qa/rodada3/', import.meta.url);
let relogio = 100000;
vega.expressionFunction('now', () => relogio);
vega.expressionFunction('windowSize', () => [1920, 1080]);
function criar(nome, estatico = false) {
  const entrada = JSON.parse(readFileSync(new URL(`t29_${nome}_entrada.json`, raiz), 'utf8'));
  const s = entrada.spec;
  function semFonteInstalada(scope) {
    for (const m of scope.marks ?? []) {
      assert.notEqual(m.type, 'text', 'texto do visual precisa estar no HTML ou em caminhos de glifos');
      semFonteInstalada(m);
    }
    for (const a of scope.axes ?? []) assert.equal(a.labels, false, 'eixos devem ter rótulos no HTML');
  }
  semFonteInstalada(s);
  s.width = entrada.largura; s.height = entrada.altura;
  s.signals ??= [];
  for (const [name, value] of [['pbiContainerWidth', s.width], ['pbiContainerHeight', s.height]]) s.signals.push({name, value});
  if (nome === 'mapa' && estatico) s.signals.find(g => g.name === 'estatico').init = 'true';
  s.data.find(d => d.name === 'dataset').values = entrada.dados.map((r,i) => ({...r,__row__:i,__selected__:'neutral'}));
  return new vega.View(vega.parse(s), {renderer:'none'});
}
const pausa = () => new Promise(resolve => setTimeout(resolve, 45));
const estatico = criar('mapa', true);
await estatico.runAsync();
assert.equal(estatico.signal('anoAtual'), 2026);
assert.equal(estatico.signal('txtPt'), '13');
assert.equal(estatico.signal('txtTurno'), '2');
assert.equal(estatico.signal('txtAdv'), '14');
assert.equal(estatico.signal('txtOutros'), '0');
assert.equal(estatico.data('ufsDados').length, 27);
assert(estatico.data('ufsDados').every(r => Number.isInteger(r.__row__)));
assert(!/<text\b/.test(await estatico.toSVG()), 'mapa não pode emitir texto nativo que dependa de fonte instalada');
estatico.signal('estado', {de:2,para:2,t0:0,tocando:false,iniciado:true});
await estatico.runAsync();
assert.equal(estatico.signal('txtTurno'), '1');
assert.equal(estatico.signal('txtAdv'), '24');
assert.equal(estatico.signal('txtOutros'), '1');
assert.deepEqual([...new Set(estatico.data('algarismos').map(r => r.k))].sort(), ['adv','ano','outros','pt','turno']);
estatico.finalize();

const mapa = criar('mapa');
await mapa.runAsync();
await pausa();
assert.equal(mapa.signal('estado').tocando, true, 'autoplay deve iniciar quando os dez quadros chegam');
assert.equal(mapa.signal('anoAtual'), 1989);
const percorridos = [1989];
for (let i=1; i<10; i++) {
  relogio += 2000;
  await pausa();
  await mapa.runAsync();
  percorridos.push(mapa.signal('anoAtual'));
}
assert.deepEqual(percorridos, [1989,1994,1998,2002,2006,2010,2014,2018,2022,2026]);
assert.equal(mapa.signal('estado').tocando, false);
relogio += 1000;
await pausa();
const agoraFinal = mapa.signal('agora');
relogio += 3000;
await pausa();
assert.equal(mapa.signal('agora'), agoraFinal, 'o relógio precisa parar no fim');
// Reenvio incremental do dataset não pode reiniciar a história.
mapa.change('dataset', vega.changeset().modify(() => true, '__selected__', 'neutral'));
await mapa.runAsync();
assert.equal(mapa.signal('anoAtual'), 2026);
mapa.signal('estado', {de:9,para:2,t0:relogio,tocando:false,iniciado:true});
await mapa.runAsync();
const ce = mapa.data('ufsDados').find(r => r.uf === 'CE');
assert.equal(ce.atual[1], 'Outros');
mapa.finalize();

const votos = criar('votos');
await votos.runAsync();
const curvas = votos.data('curvas');
assert.equal(curvas.filter(r => r.votos == null && r.turno === 2).length, 4, 'duas lacunas para cada lado');
assert(curvas.filter(r => r.votos != null).every(r => Number.isInteger(r.__row__)), 'pontos devem manter a linha original para tooltip');
assert(!/<text\b/.test(await votos.toSVG()), 'gráfico não pode emitir texto nativo que dependa de fonte instalada');
votos.finalize();
const resultado = {escopo:'Runtime Vega local, sem Power BI', anos:percorridos, estatico2026:true,
  ufs:27, autoplay:true, relogio_parou:true, incremental_preservou_ano:true, ce1998:'Outros',
  lacunasSegundoTurno:4, rowTooltipPreservado:true, textosNativosVega:0, contadoresEmGlifos:5};
writeFileSync(new URL('validacao-vega.json', raiz), JSON.stringify(resultado,null,2)+'\n');
console.log(JSON.stringify(resultado,null,2));
