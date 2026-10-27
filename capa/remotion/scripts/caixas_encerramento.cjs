// São as fontes que a própria T23 usa: _caixa() e GRUPOS vêm deste mesmo JSON.
module.exports = roteiro => {
  const caixas = Object.entries(roteiro.textos).map(([nome, rect]) => ({nome, rect,
    inicio: roteiro.html[nome.startsWith('resultado') ? 'resultado' : nome === 'fontes' ? 'fecho' : nome], anima: true}));
  for (const [titulo, x, y, w, h, itens] of roteiro.grupos) {
    caixas.push({nome: titulo, rect: [x, y, w, roteiro.alturaCabecalhoGrupo], inicio: roteiro.html.achados, anima: true});
    itens.forEach(([cod], i) => caixas.push({nome: 'achado ' + cod, rect: [x, y + 30 + i * h, w, h],
      inicio: roteiro.html.achados, anima: true}));
  }
  for (const [nome, rect] of Object.entries(roteiro.casca)) caixas.push({nome, rect, inicio: 0, anima: false});
  return caixas;
};
