// Prova com o SVG real e as caixas que geram a T23. Não produz bitmap ou imagem por IA.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const caixasHtml = require('./caixas_encerramento.cjs');
const carregar = require('./carregar_encerramento.cjs');
const sobrepoe = (a, b) => a[0] < b[0] + b[2] && a[0] + a[2] > b[0] && a[1] < b[1] + b[3] && a[1] + a[3] > b[1];
const rectArea = r => [r.x, r.y, r.largura, r.altura];
const esc = t => String(t).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');

function contato(p, rect) {
  const x = Math.max(rect[0], Math.min(rect[0] + rect[2], p.x));
  const y = Math.max(rect[1], Math.min(rect[1] + rect[3], p.y));
  return (p.x - x) ** 2 + (p.y - y) ** 2 < (p.r + (p.traco || 0) / 2) ** 2;
}

function provar(runtime, gravar = true) {
  const {roteiro, dados, geometria, svg, raiz} = runtime;
  const caixas = caixasHtml(roteiro);
  const contatos = [], atrasos = [];
  let pontosConferidos = 0;
  for (let f = 0; f < roteiro.segundos * roteiro.fps; f++) {
    const t = f / roteiro.fps;
    // União do deslocamento de 14 px durante a entrada: prova conservadora.
    const visiveis = caixas.filter(c => t >= c.inicio).map(c => ({...c,
      rect: [c.rect[0], c.rect[1], c.rect[2], c.rect[3] + (c.anima && t < c.inicio + roteiro.entrada ? 14 : 0)]}));
    for (const p of geometria.circulosNoTempo(t)) {
      if (p.opacidade <= 0.02) continue;
      pontosConferidos++;
      for (const c of visiveis) if (contato(p, c.rect)) contatos.push({quadro: f, ponto: p.classe + p.id, caixa: c.nome});
    }
    // Para qualquer atraso do vídeo, o recorte CSS não intersecta texto visível.
    const recorte = rectArea(t < roteiro.fecharRecorte ? roteiro.recorteInicial : roteiro.areaGrafica);
    for (const c of visiveis) if (sobrepoe(recorte, c.rect)) atrasos.push({quadro: f, caixa: c.nome});
  }
  const final = Array.from(geometria.circulosNoTempo(roteiro.parado));
  const contatosFinal = [];
  for (const p of final) for (const c of caixas) if (contato(p, c.rect)) contatosFinal.push({ponto: p.classe + p.id, caixa: c.nome});
  const fontes = ['src/encerramento/roteiro.json', 'src/encerramento/Encerramento.tsx',
    'src/encerramento/geometria.ts', 'public/dados/encerramento.json', '../../pbi/scripts/paginas/t23_encerramento.py',
    'scripts/caixas_encerramento.cjs', 'scripts/provar_encerramento.cjs'];
  const fontesSha256 = Object.fromEntries(fontes.map(f => [f, crypto.createHash('sha256').update(fs.readFileSync(path.join(raiz, f))).digest('hex')]));
  const resultado = {quadros: 450, caixas: caixas.length, pontosConferidos, fontesSha256,
    assentos: dados.lotes.length, cunha: dados.lotes.filter(l => l.diferenca).length,
    contatos, contatosFinal, contatosComRecorteCss: atrasos,
    fonteCaixas: 'src/encerramento/roteiro.json, a mesma fonte de _caixa() e GRUPOS da T23'};
  if (gravar) {
    const destino = path.join(raiz, '../../pbi/qa/encerramento/rodada3');
    fs.mkdirSync(destino, {recursive: true});
    const sobreposicao = caixas.map(c => '<g><rect x="' + c.rect[0] + '" y="' + c.rect[1] + '" width="' + c.rect[2]
      + '" height="' + c.rect[3] + '" fill="none" stroke="#CBBDA2" stroke-width="0.8" stroke-dasharray="4 4"/>'
      + '<text x="' + c.rect[0] + '" y="' + (c.rect[1] - 4) + '" fill="#CBBDA2" font-size="11">' + esc(c.nome) + '</text></g>').join('');
    fs.writeFileSync(path.join(destino, 'final-com-caixas.svg'), svg(roteiro.parado).replace('</svg>', '<g data-prova="caixas-html">' + sobreposicao + '</g></svg>'));
    fs.writeFileSync(path.join(destino, 'sobreposicoes.json'), JSON.stringify(resultado, null, 2) + '\n');
  }
  return resultado;
}

module.exports = {provar, contato};
if (require.main === module) {
  const r = provar(carregar());
  console.log('Prova da T23: ' + r.assentos + ' assentos, ' + r.cunha + ' na cunha; ' + r.pontosConferidos + ' marcas conferidas.');
  console.log('Contatos na animação/final/recorte CSS: ' + r.contatos.length + '/' + r.contatosFinal.length + '/' + r.contatosComRecorteCss.length);
  if (r.contatos.length || r.contatosFinal.length || r.contatosComRecorteCss.length) process.exitCode = 1;
}
