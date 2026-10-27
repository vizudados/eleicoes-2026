// Compila pelos pacotes locais, sem Chromium ou processos filhos.
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const React = require('react');
const {renderToStaticMarkup} = require('react-dom/server');

module.exports = () => {
  const raiz = path.resolve(__dirname, '..');
  const config = ts.readConfigFile(path.join(raiz, 'tsconfig.json'), ts.sys.readFile);
  if (config.error) throw new Error(ts.flattenDiagnosticMessageText(config.error.messageText, '\n'));
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, raiz, {noEmit: false,
    module: ts.ModuleKind.CommonJS, moduleResolution: ts.ModuleResolutionKind.Node10,
    outDir: path.join(raiz, 'out/testes-encerramento')});
  const programa = ts.createProgram(parsed.fileNames, parsed.options);
  const emitido = programa.emit();
  const erros = [...parsed.errors, ...ts.getPreEmitDiagnostics(programa), ...emitido.diagnostics];
  if (erros.length) throw new Error(ts.formatDiagnosticsWithColorAndContext(erros, {
    getCanonicalFileName: p => p, getCurrentDirectory: () => raiz, getNewLine: () => '\n'}));
  const composicao = require('../out/testes-encerramento/src/encerramento/Encerramento.js');
  return {raiz, ...composicao,
    dados: JSON.parse(fs.readFileSync(path.join(raiz, 'public/dados/encerramento.json'), 'utf8')),
    roteiro: JSON.parse(fs.readFileSync(path.join(raiz, 'src/encerramento/roteiro.json'), 'utf8')),
    geometria: require('../out/testes-encerramento/src/encerramento/geometria.js'),
    svg: t => renderToStaticMarkup(React.createElement(composicao.DesenhoEncerramento, {t}))};
};
