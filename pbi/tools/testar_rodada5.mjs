// Runtime Vega e ciclo do contador, sem Power BI. Fixtures geradas por validar_rodada5.py.
import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import * as vega from 'vega';
const raiz=new URL('../qa/rodada5/',import.meta.url);
let clock=100000,visivel=true,estatico=true;
vega.expressionFunction('now',()=>clock);
vega.expressionFunction('windowSize',()=>estatico?[0,0]:[1920,1080]);
vega.expressionFunction('containerSize',()=>visivel?[1620,1080]:[0,0]);
for(const n of ['pbiCrossFilterApply','pbiCrossFilterClear'])vega.expressionFunction(n,()=>null);
function criar(nome){
  const f=JSON.parse(readFileSync(new URL(nome+'-mapa.json',raiz),'utf8')),s=f.spec;
  s.width=f.largura;s.height=f.altura;s.signals??=[];
  s.signals.push({name:'pbiContainerWidth',value:f.largura},{name:'pbiContainerHeight',value:f.altura});
  s.data.find(d=>d.name==='dataset').values=f.dados.map((r,i)=>({...r,__row__:i,__selected__:'neutral'}));
  return new vega.View(vega.parse(s),{renderer:'none'});
}
for(const [p,esperado] of [['T27',5570],['T28',212]]){
  const v=criar(p);await v.runAsync();
  assert.equal(v.data('locais').length,esperado);
  assert(v.data('locais').every(r=>r.uf&&Number.isInteger(r.__row__)));
  const svg=await v.toSVG();assert(!/<text\b/.test(svg));
  writeFileSync(new URL(p+'-mapa-local.svg',raiz),svg);
  v.finalize();
}
const t21=criar('T21');await t21.runAsync();
assert.equal(t21.data('anos').length,6);
assert.equal(t21.signal('txtCont'),'2.663');
assert.equal(t21.data('dataset').filter(r=>r.anos!=null).length,1);
writeFileSync(new URL('T21-mapa-local.svg',raiz),await t21.toSVG());
t21.finalize();

estatico=false;const oculto=criar('T28');await oculto.runAsync();
visivel=false;clock+=1000;await new Promise(r=>setTimeout(r,45));
assert.equal(oculto.signal('t'),0,'contêiner oculto não avança relógio');
visivel=true;await new Promise(r=>setTimeout(r,45));assert(oculto.signal('t')>0);
clock+=5000;await new Promise(r=>setTimeout(r,45));assert.equal(oculto.signal('t'),2400);
clock+=5000;await new Promise(r=>setTimeout(r,45));assert.equal(oculto.signal('t'),2400);
oculto.finalize();

const script=readFileSync(new URL('../scripts/movimento.js',import.meta.url),'utf8');
function contador(reduzido=false){
  const quadros=new Map(),eventos={};let id=0,io;
  const pai={nodeType:1,closest:()=>null};
  const texto={nodeValue:'1.000',parentNode:pai};
  const body={getElementsByTagName:()=>[],querySelector:()=>null};
  const d={hidden:false,body,documentElement:{},getElementById:()=>body,
    addEventListener:(n,f)=>eventos[n]=f,createTreeWalker:()=>{let usado=false;return{nextNode:()=>usado?null:(usado=true,texto)}}};
  const w={matchMedia:()=>({matches:reduzido}),requestAnimationFrame:f=>{quadros.set(++id,f);return id},
    cancelAnimationFrame:n=>quadros.delete(n),getComputedStyle:()=>({fontSize:'24',animationName:'none'}),
    IntersectionObserver:class{constructor(f){io=f}observe(){}}};
  vm.runInNewContext(script,{window:w,document:d,HTMLElement:class{}});
  const passo=t=>{const fs=[...quadros.values()];quadros.clear();for(const f of fs)f(t)};
  return{quadros,texto,d,eventos,passo,io:()=>io};
}
const c=contador();assert.equal(c.quadros.size,1);
c.d.hidden=true;c.eventos.visibilitychange();assert.equal(c.quadros.size,0);
c.d.hidden=false;c.eventos.visibilitychange();assert.equal(c.quadros.size,1);
c.passo(0);assert.equal(c.texto.nodeValue,'0');c.passo(16);
c.io()([{isIntersecting:false}]);assert.equal(c.quadros.size,0);
c.io()([{isIntersecting:true}]);c.passo(1016);
assert.equal(c.texto.nodeValue,'1.000');assert.equal(c.quadros.size,0,'contador não deixa RAF ativo no fim');
const r=contador(true);assert.equal(r.quadros.size,0);assert.equal(r.texto.nodeValue,'1.000');
const resultado={escopo:'Runtime local, sem Desktop',mapas:{T27:5570,T28:212},ufDerivada:true,rowPreservado:true,
  quadroT21Repeticoes:1,contadorT21:2663,relogioPausaOculto:true,relogioParaNoFim:true,
  contadorPausaOculto:true,contadorFilaFinal:0,movimentoReduzido:true};
writeFileSync(new URL('runtime-local.json',raiz),JSON.stringify(resultado,null,2)+'\n');
console.log(JSON.stringify(resultado,null,2));
