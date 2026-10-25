/* Apuração ao vivo · a cópia da tela 25 do painel "Eleições 2026 · o voto de perto" para o site.
 *
 * O navegador lê a API pública do TSE a cada minuto (27 UFs e o exterior) e o Brasil é a soma deles, a mesma regra do
 * coletor (apuracao/coletar.py): o arquivo nacional chega depois dos estaduais. A curva da noite junta o histórico que o
 * coletor grava no GitHub com as atualizações que esta página viu. O desenho repete as medidas HTML da T18
 * (pbi/dax/T18 Apuração/Desenho), com o mesmo CSS e as mesmas fontes, extraídos da prévia por montar.py.
 *
 * ?eleicao=6257 mostra o 1º turno (ensaio, com o resultado final).
 */
(function () {
  'use strict';

  const PARAMS = new URLSearchParams(location.search);
  const ELEICAO = Number(PARAMS.get('eleicao') || 6258);
  const TSE = 'https://resultados.tse.jus.br/oficial/ele2026/' + ELEICAO + '/dados/';
  const PASTA_HIST = ELEICAO === 6258 ? 'dados/apuracao' : 'dados/apuracao/ensaio-1turno';
  const HISTORICO = 'https://raw.githubusercontent.com/vizudados/eleicoes-2026/main/' + PASTA_HIST + '/historico.csv';
  const INTERVALO = 60 * 1000;
  const FECHAMENTO = Date.UTC(2026, 9, 25, 20, 0, 0); // 17h de 25/10 em Brasília

  // UF: nome, "em" (o recorte na frase) e a casa no mapa de quadrados (coluna, linha), as mesmas da T18
  const UF = {
    AC: ['Acre', 'no Acre', 0, 2], AL: ['Alagoas', 'em Alagoas', 5, 3], AM: ['Amazonas', 'no Amazonas', 1, 1],
    AP: ['Amapá', 'no Amapá', 3, 0], BA: ['Bahia', 'na Bahia', 3, 3], CE: ['Ceará', 'no Ceará', 4, 1],
    DF: ['Distrito Federal', 'no Distrito Federal', 2, 4], ES: ['Espírito Santo', 'no Espírito Santo', 4, 4],
    GO: ['Goiás', 'em Goiás', 2, 3], MA: ['Maranhão', 'no Maranhão', 3, 1], MG: ['Minas Gerais', 'em Minas Gerais', 3, 4],
    MS: ['Mato Grosso do Sul', 'em Mato Grosso do Sul', 1, 4], MT: ['Mato Grosso', 'em Mato Grosso', 1, 3],
    PA: ['Pará', 'no Pará', 2, 1], PB: ['Paraíba', 'na Paraíba', 5, 2], PE: ['Pernambuco', 'em Pernambuco', 4, 2],
    PI: ['Piauí', 'no Piauí', 3, 2], PR: ['Paraná', 'no Paraná', 1, 5], RJ: ['Rio de Janeiro', 'no Rio de Janeiro', 3, 5],
    RN: ['Rio Grande do Norte', 'no Rio Grande do Norte', 5, 1], RO: ['Rondônia', 'em Rondônia', 1, 2],
    RR: ['Roraima', 'em Roraima', 1, 0], RS: ['Rio Grande do Sul', 'no Rio Grande do Sul', 1, 7],
    SC: ['Santa Catarina', 'em Santa Catarina', 1, 6], SE: ['Sergipe', 'em Sergipe', 4, 3],
    SP: ['São Paulo', 'em São Paulo', 2, 5], TO: ['Tocantins', 'no Tocantins', 2, 2], ZZ: ['Exterior', 'no exterior', 5, 0]
  };
  const SIGLAS = Object.keys(UF);

  // ---------- formatação (o FORMAT do DAX em pt-BR) ----------
  const inteiro = (n) => Math.round(n).toLocaleString('pt-BR');
  const dec = (x, c) => x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c });
  const en = (x, c) => x.toFixed(c);
  const esc = (s) => String(s).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  // número que conta até o valor novo a cada atualização (k = chave para lembrar o valor anterior)
  const an = (k, v, d, s) => "<span data-k='" + k + "' data-n='" + v + "' data-d='" + d + "' data-s='" + (s || '') + "'>" +
    (d ? dec(v, d) : inteiro(v)) + (s || '') + '</span>';
  const anAttr = (k, v, d, s) => " data-k='" + k + "' data-n='" + v + "' data-d='" + d + "' data-s='" + (s || '') + "'";
  const num = (t) => (t === undefined || t === null || t === '' ? 0 : Number(String(t).replace(',', '.')));
  const quando = (dt, ht) => (dt && ht ? dt + ' ' + ht.slice(0, 5) : '');
  const paraData = (txt) => { // 'dd/mm/aaaa hh:mm[:ss]' → Date (Brasília)
    const m = /^(\d\d)\/(\d\d)\/(\d{4}) (\d\d):(\d\d)(?::(\d\d))?/.exec(txt || '');
    return m ? new Date(Date.UTC(+m[3], +m[2] - 1, +m[1], +m[4] + 3, +m[5], +(m[6] || 0))) : null;
  };
  const agoraBrasilia = () => new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
  }).format(new Date()).replace(',', '');

  // ---------- dados ----------
  function lerUF(b) {
    const s = b.s, e = b.e, v = b.v;
    const c = {};
    let eleito = '';
    for (const agr of b.carg[0].agr) for (const par of agr.par) for (const k of par.cand) {
      c[+k.n] = +k.vap || 0;
      if (k.e === 's' && /^eleito/i.test(k.st || '')) eleito = +k.n === 13 ? 'Lula' : +k.n === 22 ? 'Flávio' : '';
    }
    return {
      tse: quando(b.dt, b.ht), turno: +b.t, tf: b.tf === 's', eleito,
      eleitorado: +e.te || 0, comparecimento: +e.c || 0, abstencao: +e.a || 0, brancos: +v.vb || 0, nulos: +v.tvn || 0,
      validos: +v.vv || 0, lula: c[13] || 0, flavio: c[22] || 0, secoes: +s.ts || 0, totalizadas: +s.st || 0
    };
  }

  function somar(lista) {
    const r = { eleitorado: 0, comparecimento: 0, abstencao: 0, brancos: 0, nulos: 0, validos: 0, lula: 0, flavio: 0,
      secoes: 0, totalizadas: 0, tse: '' };
    let maior = null;
    for (const u of lista) {
      for (const k of ['eleitorado', 'comparecimento', 'abstencao', 'brancos', 'nulos', 'validos', 'lula', 'flavio', 'secoes', 'totalizadas']) r[k] += u[k];
      const d = paraData(u.tse);
      if (d && (!maior || d > maior)) { maior = d; r.tse = u.tse; }
    }
    return r;
  }

  async function baixar(uf) {
    const sigla = uf.toLowerCase();
    const r = await fetch(TSE + sigla + '/' + sigla + '-c0001-e' + String(ELEICAO).padStart(6, '0') + '-u.json');
    if (!r.ok) throw new Error(uf + ' ' + r.status);
    return lerUF(await r.json());
  }

  const estado = { ufs: {}, br: null, turno: ELEICAO === 6257 ? 1 : 2, coleta: '', historico: new Map(), escopo: 'BR',
    modo: 'quadrados', primeira: true, t1: {}, caminhos: null, vistos: {}, marcas: {}, nCurva: 0 };

  async function atualizar() {
    const pedidos = SIGLAS.map((uf) => baixar(uf).then((d) => [uf, d]).catch(() => null));
    pedidos.push(baixar('BR').then((d) => ['BR', d]).catch(() => null));
    const lidos = (await Promise.all(pedidos)).filter(Boolean);
    if (!lidos.length) return false;
    const ufs = {};
    let brTse = null;
    for (const [uf, d] of lidos) if (uf === 'BR') brTse = d; else ufs[uf] = d;
    // vale o mais adiantado, a soma das UFs e do exterior ou o arquivo nacional: o que tiver mais seções totalizadas (na
    // noite do 2º turno o nacional chegou antes dos estaduais); com alguma UF fora desta leitura, a soma ficaria curta e
    // vale o nacional (a mesma regra do coletor)
    const completo = SIGLAS.every((uf) => ufs[uf]);
    if (!completo && !brTse) return false;
    const soma = completo ? somar(SIGLAS.map((uf) => ufs[uf])) : null;
    const br = soma && (!brTse || soma.totalizadas >= brTse.totalizadas) ? soma : brTse;
    br.eleito = brTse ? brTse.eleito : '';
    br.turno = brTse ? brTse.turno : estado.turno;
    estado.ufs = Object.assign(estado.ufs, ufs);
    estado.br = br;
    estado.turno = br.turno;
    estado.coleta = agoraBrasilia();
    if (br.tse && br.validos > 0) estado.historico.set(br.tse, { tse: br.tse, lula: br.lula, flavio: br.flavio, validos: br.validos });
    return true;
  }

  async function lerHistorico() {
    try {
      const r = await fetch(HISTORICO);
      if (!r.ok) return;
      const linhas = (await r.text()).trim().split(/\r?\n/);
      const cab = linhas.shift().split(',');
      const i = (n) => cab.indexOf(n);
      for (const l of linhas) {
        const c = l.split(',');
        const tse = c[i('atualizado_tse')].slice(0, 16);
        const validos = num(c[i('validos')]);
        if (tse && validos > 0 && !estado.historico.has(tse)) {
          estado.historico.set(tse, { tse, lula: num(c[i('lula_votos')]), flavio: num(c[i('flavio_votos')]), validos });
        }
      }
    } catch (e) { /* sem histórico, a curva usa só o que a página viu */ }
  }

  // ---------- contas do recorte (Brasil ou uma UF) ----------
  function recorte() {
    const uf = estado.escopo;
    const d = uf === 'BR' ? estado.br : estado.ufs[uf];
    if (!d) return null;
    const lider = d.lula > d.flavio ? 'Lula' : d.flavio > d.lula ? 'Flávio' : '—';
    return Object.assign({}, d, {
      lider,
      lulaP: d.validos ? d.lula / d.validos : 0, flavioP: d.validos ? d.flavio / d.validos : 0,
      secoesP: d.secoes ? d.totalizadas / d.secoes : 0,
      abstP: d.comparecimento + d.abstencao ? d.abstencao / (d.comparecimento + d.abstencao) : 0,
      dif: Math.abs(d.lula - d.flavio)
    });
  }

  function fase() {
    const br = estado.br;
    if (!br || br.totalizadas === 0) return 'aguardando';
    const pct = br.totalizadas / br.secoes;
    if (br.eleito) return pct < 1 ? 'definido' : 'encerrada';
    return pct >= 1 ? 'encerrada' : 'apurando';
  }

  // ---------- desenho: T18 · Placar · HTML ----------
  function htmlPlacar() {
    const r = recorte();
    if (!r) return '';
    const f = fase();
    const aguarda = f === 'aguardando';
    const noBrasil = estado.escopo === 'BR';
    const nome = noBrasil ? 'Brasil' : UF[estado.escopo][0];
    const em = noBrasil ? '' : UF[estado.escopo][1];
    const onde = noBrasil ? '' : ' ' + em;
    const lulaTxt = aguarda ? '—' : an('lp', r.lulaP * 100, 2, '%');
    const flavioTxt = aguarda ? '—' : an('fp', r.flavioP * 100, 2, '%');
    const votos = (k, n) => (aguarda ? 'aguardando a 1ª parcial' : an(k, n, 0, n === 1 ? ' voto' : ' votos'));
    const secoesTxt = an('sf', r.secoesP * 100, 2, '%');
    const difTxt = an('dif', r.dif, 0, '');
    const blocoLula = "<div class='cand sobe d2'><div class='rot lula-esc'>LULA · PT · 13</div><div class='num pct lula'>" + lulaTxt +
      "</div><div class='txt votos'>" + votos('lv', r.lula) + '</div></div>';
    const blocoFlavio = "<div class='cand sobe d3'><div class='rot flavio-esc'>FLÁVIO BOLSONARO · PL · 22</div><div class='num pct flavio'>" +
      flavioTxt + "</div><div class='txt votos'>" + votos('fv', r.flavio) + '</div></div>';
    const par = r.lider === 'Flávio' ? blocoFlavio + blocoLula : blocoLula + blocoFlavio;
    const selo = estado.turno === 1 ? "<div class='selo entra d6'>ENSAIO · 1º TURNO</div>"
      : f === 'definido' ? "<div class='selo entra d6'>MATEMATICAMENTE DEFINIDO</div>"
        : f === 'encerrada' ? "<div class='selo entra d6'>APURAÇÃO ENCERRADA</div>" : '';
    const liderBR = estado.br.lula > estado.br.flavio ? 'Lula' : estado.br.flavio > estado.br.lula ? 'Flávio' : '—';
    let frase;
    if (aguarda) frase = 'As urnas fecham às 17h de domingo, 25/10.';
    else if (!noBrasil && f === 'definido') {
      frase = liderBR + ' está matematicamente eleito no Brasil; ' + em + ', ' +
        (r.lider === '—' ? 'empate exato' : r.lider + ' está à frente por ' + difTxt + ' votos') + '.';
    } else if (r.lider === '—') frase = 'Empate exato' + onde + ' com ' + secoesTxt + ' das seções apuradas.';
    else if (f === 'apurando') frase = r.lider + ' está à frente' + onde + ' por ' + difTxt + ' votos, com ' + secoesTxt + ' das seções apuradas.';
    else if (f === 'definido') frase = r.lider + ' está matematicamente eleito: a diferença de ' + difTxt + ' votos já não pode ser revertida.';
    else frase = r.lider + ' lidera' + onde + ' · apuração encerrada · diferença de ' + difTxt + ' votos';
    const relogio = aguarda
      ? "<div class='relogio sobe d4'><span class='rot'>FALTAM</span><span class='num' id='t18rel'>" + esc(contagem()) + '</span></div>' +
        "<div class='txt sobe d5'>" + inteiro(r.eleitorado) + ' eleitores podem votar' + (noBrasil ? '' : ' ' + em) + '.</div>'
      : '';
    const barra = "<div class='secoes sobe d5'><div class='rot'>SEÇÕES APURADAS" + (noBrasil ? '' : ' · ' + nome.toUpperCase()) +
      "</div><div class='trilho'><div class='enche barra-x' data-w='" + en(r.secoesP * 100, 3) + "' data-wk='sw' style='width:" +
      en(r.secoesP * 100, 3) + "%'></div><span class='num'>" + an('sb', r.secoesP * 100, 2, '%') + "</span></div><div class='nota'>Abstenção " + dec(r.abstP * 100, 2) + '% · brancos ' + inteiro(r.brancos) +
      ' · nulos ' + inteiro(r.nulos) + '</div></div>';
    const tse = r.tse;
    const topo = "<div class='rot topo entra'>" + (tse ? 'ATUALIZADO PELO TSE · ' + tse : 'AGUARDANDO A PRIMEIRA DIVULGAÇÃO DO TSE') +
      ' · COLETADO EM ' + (estado.coleta || '—') + (noBrasil || selo ? '' : ' · ' + nome.toUpperCase()) + '</div>';
    const marca = aguarda || r.lider === '—' ? '' : "<span class='visto'>✓</span>";
    // no celular, as mesmas peças em coluna (t18m), na largura da tela e sem escala
    if (MODO_CEL) {
      return "<div class='t18m'>" + topo + selo + "<div class='par'>" + par + '</div>' +
        "<div class='man frase sobe d4'>" + marca + '<span>' + frase + '</span></div>' + relogio + (aguarda ? '' : barra) + '</div>';
    }
    return "<div class='tela t18p'>" + topo + "<div class='par'>" + par + selo + '</div>' +
      "<div class='man frase sobe d4'>" + marca + '<span>' + frase + '</span></div>' + relogio + (aguarda ? '' : barra) + '</div>';
  }

  const CSS_CELULAR = '<style>.t18m{padding:2px 0 10px 0}.t18m .topo{font-size:10.5px;line-height:1.6;letter-spacing:.1em;margin-bottom:12px}' +
    '.t18m .par{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start}' +
    '.t18m .cand .rot{font-size:10.5px;letter-spacing:.08em;line-height:1.35}' +
    '.t18m .cand .pct{font-size:36px;margin:6px 0 4px 0}.t18m .cand .votos{font-size:13px;color:var(--grafite)}' +
    '.t18m .selo{display:inline-block;transform:rotate(-3deg);border:2px solid #1C1915;outline:1px solid #1C1915;' +
    'outline-offset:3px;padding:5px 9px;font-weight:700;font-size:10.5px;letter-spacing:.12em;margin:2px 0 14px 4px}' +
    '.t18m .frase{display:flex;align-items:flex-start;gap:8px;margin:16px 0 10px 0;font-size:16px;line-height:1.35}' +
    '.t18m .visto{font-family:var(--mao);font-size:26px;line-height:1;margin-top:-4px}' +
    '.t18m .relogio{display:flex;align-items:baseline;gap:10px;margin:6px 0 4px 0}.t18m .relogio .num{font-size:28px}' +
    '.t18m .relogio + .txt{font-size:14px}' +
    '.t18m .secoes{margin-top:6px}.t18m .secoes .rot{font-size:10.5px}' +
    '.t18m .trilho{position:relative;height:24px;background:#E5DBC8;margin:6px 0 8px 0;overflow:hidden}' +
    '.t18m .enche{height:100%;background:#1C1915}' +
    '.t18m .trilho .num{position:absolute;left:8px;top:4px;font-size:14px;color:#F1EBDF;mix-blend-mode:difference}' +
    '.t18m .secoes .nota{font-size:12.5px;color:var(--grafite)}</style>';

  function contagem() {
    const d = FECHAMENTO - Date.now();
    if (d <= 0) return 'as urnas já fecharam';
    const D = Math.floor(d / 864e5), h = Math.floor((d % 864e5) / 36e5), m = Math.floor((d % 36e5) / 6e4), s = Math.floor((d % 6e4) / 1e3);
    return (D ? D + (D === 1 ? ' dia, ' : ' dias, ') : '') + h + ' h ' + (m < 10 ? '0' : '') + m + ' min ' + (s < 10 ? '0' : '') + s + ' s';
  }

  // ---------- desenho: T18 · Curva · HTML ----------
  function htmlCurva() {
    const pts = [...estado.historico.values()].map((p) => Object.assign({ d: paraData(p.tse) }, p)).filter((p) => p.d)
      .sort((a, b) => a.d - b.d);
    const n = pts.length;
    const min = 0.40, max = 0.60;
    const y = (v) => 20 + (1 - (Math.min(Math.max(v, min), max) - min) / (max - min)) * 230;
    let base = null;
    // 17h (Brasília) do dia da primeira atualização, como T18 · noite · 17h; antes disso o ponto fica no começo do eixo
    if (n) { base = new Date(pts[0].d.getTime() - 3 * 36e5); base.setUTCHours(17 + 3, 0, 0, 0); }
    const xs = pts.map((p) => {
      const l = p.lula / p.validos, f = p.flavio / p.validos;
      const x = 70 + Math.min(Math.max((p.d - base) / 36e5, 0), 7) / 7 * 770;
      return { x, l, f, yl: y(l), yf: y(f) };
    });
    let grade = '';
    for (const v of [0.40, 0.45, 0.50, 0.55, 0.60]) {
      const yy = y(v);
      grade += "<line x1='70' x2='840' y1='" + en(yy, 1) + "' y2='" + en(yy, 1) + "' class='g" + (v === 0.5 ? ' meio' : '') +
        "'/><text x='58' y='" + en(yy + 5, 1) + "' class='ex' text-anchor='end'>" + Math.round(v * 100) + '%</text>';
    }
    let horas = '';
    for (let h = 17; h <= 24; h++) horas += "<text x='" + en(70 + (h - 17) / 7 * 770, 1) + "' y='282' class='ex' text-anchor='middle'>" + (h === 24 ? '0h' : h + 'h') + '</text>';
    let series = '', rotulos = '', vazio = '';
    const novo = !estado.primeira && n > estado.nCurva;
    estado.nCurva = n;
    if (n >= 2) {
      const linha = (k) => xs.map((p) => en(p.x, 1) + ',' + en(p[k], 1)).join(' ');
      const re = novo ? ' redesenha' : '';
      series = "<polyline points='" + linha('yf') + "' class='lf traco" + re + "' pathLength='1' fill='none'/>" +
        "<polyline points='" + linha('yl') + "' class='ll traco" + re + "' pathLength='1' fill='none'/>";
    }
    if (n >= 1) {
      const u = xs[n - 1];
      const esq = u.x < 455;
      const xt = en(esq ? u.x + 14 : u.x - 14, 1), anc = esq ? 'start' : 'end';
      const bc = novo ? ' brota-novo' : '';
      rotulos = "<circle cx='" + en(u.x, 1) + "' cy='" + en(u.yf, 1) + "' r='6' class='pf brota d8" + bc + "'/>" +
        "<circle cx='" + en(u.x, 1) + "' cy='" + en(u.yl, 1) + "' r='6' class='pl brota d8" + bc + "'/>" +
        "<text x='" + xt + "' y='" + en(u.yf + (u.f >= u.l ? -14 : 26), 1) + "' text-anchor='" + anc + "' class='rf entra d9'>Flávio <tspan" +
        anAttr('cf', u.f * 100, 2, '%') + '>' + dec(u.f * 100, 2) + '%</tspan></text>' +
        "<text x='" + xt + "' y='" + en(u.yl + (u.l > u.f ? -14 : 26), 1) + "' text-anchor='" + anc + "' class='rl entra d9'>Lula <tspan" +
        anAttr('cl', u.l * 100, 2, '%') + '>' + dec(u.l * 100, 2) + '%</tspan></text>';
    } else vazio = "<text x='455' y='96' text-anchor='middle' class='vz'>a curva começa às 17h</text>";
    return "<div class='tela t18c'><div class='rot entra'>A CURVA DA NOITE · % DOS VÁLIDOS A CADA ATUALIZAÇÃO DO TSE · BRASIL</div>" +
      "<svg viewBox='0 0 900 290' width='900' height='290'>" + grade + horas + series + rotulos + vazio + '</svg></div>';
  }

  // ---------- desenho: T18 · Mapa · HTML (quadrados) e o mapa do Brasil ----------
  function liderUF(uf) {
    const d = estado.ufs[uf];
    if (!d) return { classe: 'qz', pct: null, secoes: 0 };
    const l = d.lula > d.flavio ? 'Lula' : d.flavio > d.lula ? 'Flávio' : '—';
    const pct = l === 'Lula' ? d.lula / d.validos : l === 'Flávio' ? d.flavio / d.validos : null;
    return { classe: l === 'Lula' ? 'ql' : l === 'Flávio' ? 'qf' : 'qz', pct, secoes: d.secoes ? d.totalizadas / d.secoes : 0 };
  }

  // o quadrado (ou o estado no mapa) pulsa quando o líder ou a porcentagem muda numa atualização
  function mudou(uf, q) {
    const marca = q.classe + (q.pct === null ? '' : q.pct.toFixed(4));
    const antes = estado.marcas[uf];
    estado.marcas[uf] = marca;
    return !estado.primeira && antes !== undefined && antes !== marca;
  }

  function htmlQuadrados() {
    let h = '';
    for (const uf of SIGLAS) {
      const [, , col, lin] = UF[uf];
      const q = liderUF(uf);
      const sel = estado.escopo === uf ? ';outline:3px solid var(--tinta);outline-offset:3px' : '';
      h += "<div class='tela mq'><div data-uf='" + uf + "' class='q " + q.classe + (uf === 'ZZ' ? ' ex' : '') + ' brota d' + (lin + 1) +
        (mudou(uf, q) ? ' pulsa' : '') + "' style='left:" + (22 + col * 104) + 'px;top:' + (52 + lin * 92) + 'px' + sel + "'>" +
        '<b>' + (uf === 'ZZ' ? 'EX' : uf) + '</b><i' + anAttr('qs' + uf, q.secoes * 100, 0, '%') + '>' + Math.round(q.secoes * 100) + '%</i>' +
        (q.pct === null ? '<span>—</span>' : '<span' + anAttr('qp' + uf, q.pct * 100, 1, '%') + '>' + dec(q.pct * 100, 1) + '%</span>') +
        '</div></div>';
    }
    return h;
  }

  const COR = { ql: '#D9877B', qf: '#8FA8CF', qz: '#E5DBC8' };
  const TINTA = { ql: '#8E2620', qf: '#1D3C6E', qz: '#48423A' };
  function htmlMapa() {
    const cam = estado.caminhos;
    if (!cam) return htmlQuadrados();
    // o Brasil na área dos quadrados (22..638 × 52..780), com o EX no mesmo canto
    let paths = '', rot = '';
    for (const uf of SIGLAS) {
      if (uf === 'ZZ') continue;
      const q = liderUF(uf);
      const sel = estado.escopo === uf;
      paths += "<path data-uf='" + uf + "' d='" + cam.caminhos[uf] + "' fill='" + COR[q.classe] + "' stroke='" + (sel ? '#1C1915' : '#F1EBDF') +
        "' stroke-width='" + (sel ? 4 : 1.6) + "' class='uf" + (mudou(uf, q) ? ' pulsa' : '') + "'/>";
      const c = cam.centros[uf];
      if (c) {
        const pequeno = ['DF', 'SE', 'AL', 'PB', 'RN', 'ES', 'RJ'].includes(uf);
        rot += "<text x='" + en(c[0], 1) + "' y='" + en(c[1], 1) + "' text-anchor='middle' class='mr" + (pequeno ? ' p' : '') + "'>" + uf +
          (pequeno ? '' : "<tspan x='" + en(c[0], 1) + "' dy='22' fill='" + TINTA[q.classe] + "' class='mp'" +
            (q.pct === null ? '' : anAttr('gp' + uf, q.pct * 100, 1, '%')) + '>' +
            (q.pct === null ? '—' : dec(q.pct * 100, 1) + '%') + '</tspan>') + '</text>';
      }
    }
    const ex = liderUF('ZZ');
    mudou('ZZ', ex);
    const sel = estado.escopo === 'ZZ' ? " style='left:542px;top:52px;outline:3px solid var(--tinta);outline-offset:3px'" : " style='left:542px;top:52px'";
    return "<style>.geo .uf{cursor:pointer;transition:opacity .18s}.geo:has(.uf:hover) .uf:not(:hover){opacity:.55}" +
      ".geo .mr{font-family:var(--fonte);font-size:21px;font-weight:700;fill:#1C1915;pointer-events:none}.geo .mr.p{font-size:15px}" +
      ".geo .mp{font-size:19px;font-weight:700}</style>" +
      "<div class='tela mq'><svg class='geo' viewBox='" + cam.viewBox + "' style='position:absolute;left:0;top:44px;width:640px;height:740px;pointer-events:auto'>" +
      paths + rot + '</svg>' +
      "<div data-uf='ZZ' class='q " + ex.classe + " ex'" + sel + '><b>EX</b><i>' + Math.round(ex.secoes * 100) + '%</i><span>' +
      (ex.pct === null ? '—' : dec(ex.pct * 100, 1) + '%') + '</span></div></div>';
  }

  // ---------- desenho: T18 · Tooltip UF · HTML ----------
  function htmlTooltip(uf) {
    const d = estado.ufs[uf];
    if (!d) return '';
    const nome = UF[uf][0].toUpperCase();
    if (!(d.validos > 0)) {
      const t1 = estado.t1[uf];
      return "<div class='tela tt18'><div class='fita'></div><div class='rot'>" + nome + '</div>' +
        "<div class='linha'><span class='num'>" + an('tte', d.eleitorado, 0, '') + "</span><span class='rot'>ELEITORES</span></div>" +
        "<div class='txt'>A apuração começa às 17h de domingo, 25/10: " + an('tts', d.secoes, 0, '') + ' seções a contar.</div>' +
        (t1 ? "<div class='nota'>No 1º turno: Lula " + dec(t1.lula * 100, 1) + '% × Flávio ' + dec(t1.flavio * 100, 1) + '% dos válidos.</div>' : '') +
        "<div class='mao'>ainda sem votos</div></div>";
    }
    const l = d.lula / d.validos, f = d.flavio / d.validos;
    const lider = d.lula > d.flavio ? 'Lula' : d.flavio > d.lula ? 'Flávio' : '—';
    const abst = d.comparecimento + d.abstencao ? d.abstencao / (d.comparecimento + d.abstencao) : 0;
    return "<div class='tela tt18'><div class='fita'></div><div class='rot'>" + nome + '</div>' +
      "<div class='linha'><span class='lula num'>" + an('ttl', l * 100, 2, '%') + "</span><span class='rot'>LULA</span></div>" +
      "<div class='barra'><i class='bl barra-x' style='width:" + en(l * 100, 3) + "%'></i><i class='bf barra-x-dir' style='width:" + en(f * 100, 3) +
      "%'></i></div>" +
      "<div class='linha'><span class='flavio num'>" + an('ttf', f * 100, 2, '%') + "</span><span class='rot'>FLÁVIO</span></div>" +
      "<div class='txt'>" + an('ttlv', d.lula, 0, '') + ' × ' + an('ttfv', d.flavio, 0, '') + ' votos · diferença de ' +
      an('ttd', Math.abs(d.lula - d.flavio), 0, '') + '</div>' +
      "<div class='nota'>" + dec((d.secoes ? d.totalizadas / d.secoes : 0) * 100, 2) + '% das seções · abstenção ' + dec(abst * 100, 2) + '%' +
      (d.tse ? ' · atualizado às ' + d.tse.slice(11, 16) : '') + '</div>' +
      (lider !== '—' ? "<div class='mao " + (lider === 'Lula' ? 'lula-esc' : 'flavio-esc') + "'>" + lider + ' na frente</div>' : '') + '</div>';
  }

  // ---------- palco: os visuais em iframes do tamanho do Power BI, com o mesmo CSS ----------
  let PECAS = null;
  const quadros = {};

  // cada visual num iframe; no celular, o resultado, o mapa e a curva vão para as vagas da coluna (o iframe não muda de
  // lugar depois de criado: movido, ele recarregaria vazio)
  const VAGA = { placar: 'v-placar', mapa: 'v-mapa', curva: 'v-curva' };
  function quadro(id, css) {
    const f = document.createElement('iframe');
    f.title = id;
    f.setAttribute('scrolling', 'no');
    f.srcdoc = '<!doctype html><html><head><meta charset="utf-8"><base href="' + document.baseURI + '"><link rel="stylesheet" href="base.css?v=20261025-1730">' +
      css + '<style id="congela"></style></head><body><div id="c"></div></body></html>';
    (MODO_CEL && VAGA[id] ? document.getElementById(VAGA[id]) : document.getElementById('palco')).appendChild(f);
    quadros[id] = f;
    estilizar(id);
    return new Promise((ok) => f.addEventListener('load', () => ok(f), { once: true }));
  }

  function pintar(id, html) {
    const f = quadros[id];
    if (!f) return;
    const doc = f.contentDocument;
    // depois da primeira pintura, as entradas animadas não se repetem a cada minuto
    if (!estado.primeira && id !== 'tooltip') doc.getElementById('congela').textContent = CONGELA;
    doc.getElementById('c').innerHTML = html;
    animar(doc, id === 'tooltip');
  }

  // depois da primeira pintura, as entradas não se repetem a cada minuto; ficam as animações de atualização
  const CONGELA = '.sobe,.entra,.brota,.barra-x,.barra-x-dir,.traco,.traco-rapido,.cor,.esmaece,.mq .q{animation:none!important}' +
    '.redesenha{animation:eTraco 1.1s cubic-bezier(.45,.05,.3,1) both!important}' +
    '.brota-novo{animation:eEscala .6s cubic-bezier(.2,.9,.3,1.3) both!important}' +
    '.mq .q.pulsa{animation:qPulsa 1.4s ease-out both!important}.geo .uf.pulsa{animation:gPulsa 1.4s ease-out both!important}' +
    '@keyframes qPulsa{0%{box-shadow:0 0 0 0 rgba(28,25,21,.55);transform:scale(1.06)}100%{box-shadow:0 0 0 16px rgba(28,25,21,0);transform:scale(1)}}' +
    '@keyframes gPulsa{0%{opacity:.35}100%{opacity:1}}';

  // os números contam do valor anterior até o novo (do zero na primeira vez e no dossiê); as barras crescem do antigo
  function animar(doc, doZero) {
    const vistos = estado.vistos;
    const dur = 950, t0 = performance.now();
    const itens = [];
    doc.querySelectorAll('[data-k]').forEach((el) => {
      const k = el.getAttribute('data-k'), para = +el.getAttribute('data-n');
      const de = doZero || vistos[k] === undefined ? 0 : vistos[k];
      if (!doZero) vistos[k] = para;
      if (de !== para) itens.push([el, de, para, +el.getAttribute('data-d'), el.getAttribute('data-s') || '']);
    });
    doc.querySelectorAll('[data-w]').forEach((el) => {
      const k = el.getAttribute('data-wk'), para = +el.getAttribute('data-w');
      const de = vistos[k] === undefined ? para : vistos[k];
      vistos[k] = para;
      if (de === para) return;
      el.style.transition = 'none';
      el.style.width = de + '%';
      void el.offsetWidth;
      el.style.transition = 'width .95s cubic-bezier(.2,.7,.2,1)';
      el.style.width = para + '%';
    });
    if (!itens.length) return;
    const passo = (agora) => {
      // o carimbo do quadro pode vir antes de t0: sem o piso, a conta começaria negativa
      const x = Math.max(0, Math.min(1, (agora - t0) / dur)), e = 1 - Math.pow(1 - x, 3);
      for (const [el, de, para, d, s] of itens) {
        const v = de + (para - de) * e;
        el.textContent = (d ? dec(v, d) : inteiro(v)) + s;
      }
      if (x < 1) requestAnimationFrame(passo);
    };
    requestAnimationFrame(passo);
    // garantia: sem quadros de animação (aba em segundo plano, economia de energia), o número final aparece do mesmo jeito
    setTimeout(() => {
      for (const [el, , para, d, s] of itens) el.textContent = (d ? dec(para, d) : inteiro(para)) + s;
    }, dur + 200);
  }

  function desenhar() {
    pintar('placar', htmlPlacar());
    pintar('curva', htmlCurva());
    pintar('mapa', PECAS.mapa_fixo + (estado.modo === 'mapa' ? htmlMapa() : htmlQuadrados()));
    ligarMapa();
    rotuloFiltro();
    if (MODO_CEL) alturaPlacar();
    estado.primeira = false;
  }

  // ---------- celular: os blocos em coluna (resultado, mapa, curva), cada um na largura da tela ----------
  const GEO = { casca: [0, 0, 1920, 1080, 10], placar: [150, 140, 900, 470, 300], curva: [150, 640, 900, 340, 301],
    mapa: [1110, 140, 660, 860, 302], tooltip: [520, 300, 580, 460, 400] };
  const largura = () => document.documentElement.clientWidth || window.innerWidth || 0;
  const celular = () => largura() < 1000;
  let MODO_CEL = false; // decidido em iniciar(), quando a janela (ou o iframe do site) já tem largura

  function alturaPlacar() {
    const f = quadros.placar;
    const c = f.contentDocument && f.contentDocument.getElementById('c');
    if (c) f.style.height = Math.ceil(c.scrollHeight + 8) + 'px';
  }

  function estilizar(id) {
    const f = quadros[id];
    const [x, y, w, h, z] = GEO[id];
    if (!MODO_CEL || !VAGA[id]) {
      f.style.cssText = 'position:absolute;border:0;left:' + x + 'px;top:' + y + 'px;width:' + w + 'px;height:' + h + 'px;z-index:' + z +
        ';background:transparent' + (id === 'tooltip' || (MODO_CEL && id === 'casca') ? ';display:none;pointer-events:none' : '');
      return;
    }
    // no celular: o resultado na largura da tela, sem escala; o mapa e a curva escalados para caber nela
    const vaga = document.getElementById(VAGA[id]);
    const W = vaga.clientWidth;
    if (id === 'placar') {
      f.style.cssText = 'position:static;display:block;border:0;background:transparent;width:' + W + 'px;height:' + (f.style.height || '420px');
      return;
    }
    const s = W / w;
    f.style.cssText = 'position:absolute;left:0;top:0;border:0;background:transparent;transform-origin:0 0;width:' + w + 'px;height:' + h +
      'px;transform:scale(' + s + ')';
    vaga.style.height = h * s + 'px';
  }

  function arrumar() {
    if (!MODO_CEL) { ajustar(); return; }
    document.getElementById('v-modo').appendChild(document.getElementById('modo'));
    for (const id of Object.keys(VAGA)) estilizar(id);
    alturaPlacar();
  }

  // ---------- interação: clique no estado filtra o resultado; dossiê no mouse ----------
  function ligarMapa() {
    const doc = quadros.mapa.contentDocument;
    doc.querySelectorAll('[data-uf]').forEach((el) => {
      const uf = el.getAttribute('data-uf');
      el.addEventListener('click', () => escolher(estado.escopo === uf ? 'BR' : uf));
      el.addEventListener('mouseenter', () => mostrarTooltip(uf, el));
      el.addEventListener('mouseleave', esconderTooltip);
    });
  }

  function mostrarTooltip(uf, el) {
    const tt = quadros.tooltip;
    if (MODO_CEL) return;
    const html = htmlTooltip(uf);
    if (!tt || !html) return;
    pintar('tooltip', html);
    // o dossiê abre à esquerda do mapa, na altura do estado (coordenadas do palco de 1920 × 1080)
    const r = el.getBoundingClientRect();
    tt.style.left = (1110 - 590) + 'px';
    tt.style.top = Math.min(Math.max(140 + r.top - 60, 110), 1080 - 470) + 'px';
    tt.style.display = 'block';
  }
  function esconderTooltip() { if (quadros.tooltip) quadros.tooltip.style.display = 'none'; }

  function escolher(uf) {
    estado.escopo = uf;
    document.getElementById('filtro-sel').value = uf;
    document.getElementById('filtro-cel').value = uf;
    desenhar();
  }

  function rotuloFiltro() {
    const nome = estado.escopo === 'BR' ? 'Todo o Brasil' : UF[estado.escopo][0];
    for (const el of document.querySelectorAll('#filtro .rotulo, #cel .rotulo-cel')) el.textContent = nome;
  }

  // ---------- montagem ----------
  // a tela cabe inteira na janela (largura e altura), centrada: no quadro 16:9 do site enche tudo, sem barra de rolagem
  function ajustar() {
    const W = document.documentElement.clientWidth, H = window.innerHeight;
    const s = Math.min(W / 1920, H / 1080);
    document.getElementById('palco').style.transform = 'translate(' + Math.max(0, (W - 1920 * s) / 2) + 'px,0) scale(' + s + ')';
    document.getElementById('quadro').style.height = Math.floor(1080 * s) + 'px';
  }

  async function centros(cam) {
    // o centro de cada estado, medido no próprio desenho (para os rótulos do mapa)
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', cam.viewBox);
    svg.style.cssText = 'position:absolute;left:-9999px;width:1000px;height:1000px';
    document.body.appendChild(svg);
    const c = {};
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const [uf, d] of Object.entries(cam.caminhos)) {
      const p = document.createElementNS(ns, 'path');
      p.setAttribute('d', d);
      svg.appendChild(p);
      const b = p.getBBox();
      c[uf] = [b.x + b.width / 2, b.y + b.height / 2];
      x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height);
    }
    // o quadro do desenho justo no Brasil, para o mapa ocupar a área dos quadrados
    cam.viewBox = [x0 - 8, y0 - 8, x1 - x0 + 16, y1 - y0 + 16].map((v) => v.toFixed(1)).join(' ');
    // o centro da caixa de Goiás cai em cima do Distrito Federal
    if (c.GO) c.GO[1] -= 18;
    svg.remove();
    cam.centros = c;
    return cam;
  }

  async function iniciar() {
    // num iframe que ainda está sendo montado, a largura pode vir zerada: espera ela existir
    for (let i = 0; i < 120 && largura() === 0; i++) await new Promise((ok) => requestAnimationFrame(ok));
    MODO_CEL = celular();
    PECAS = await (await fetch('pecas.json')).json();
    estado.t1 = await (await fetch('primeiro_turno.json')).json();
    const palco = document.getElementById('palco');
    // a casca (cabeçalho, urna, rodapé) e o filtro do alto, como no painel
    document.body.classList.toggle('celular', MODO_CEL);
    await Promise.all([
      // a casca é fixa: sem a animação de entrada, que num quadro escondido ficaria parada no começo
      MODO_CEL ? null : quadro('casca', '<style>*{animation:none!important}</style>')
        .then((f) => { f.contentDocument.getElementById('c').innerHTML = PECAS.casca; }),
      quadro('placar', PECAS.placar_css + CSS_CELULAR),
      // no celular, curva e mapa saem escalados: os textos pequenos crescem para continuar legíveis
      quadro('curva', PECAS.curva_css + (MODO_CEL ? '<style>.t18c .rot{font-size:18px;letter-spacing:.06em}.t18c .ex{font-size:26px}' +
        '.t18c .rl,.t18c .rf{font-size:34px}</style>' : '')),
      quadro('mapa', PECAS.mapa_css + (MODO_CEL ? '<style>.mapa-fixo .rot{font-size:15px;letter-spacing:.08em}' +
        '.mapa-fixo .leg{font-size:19px;gap:16px}.mapa-fixo .leg i{width:18px;height:18px}.mapa-fixo .dica{font-size:26px}</style>' : '')),
      MODO_CEL ? null : quadro('tooltip', '<style>' + TT_CSS + '</style>')
    ]);
    const filtro = document.getElementById('filtro');
    filtro.insertAdjacentHTML('afterbegin', PECAS.filtro.replace('>Todo o Brasil<', " class='rotulo'>Todo o Brasil<"));
    const opcoes = "<option value='BR'>Todo o Brasil</option>" +
      SIGLAS.filter((u) => u !== 'ZZ').sort((a, b) => UF[a][0].localeCompare(UF[b][0], 'pt-BR'))
        .map((u) => "<option value='" + u + "'>" + UF[u][0] + '</option>').join('') + "<option value='ZZ'>Exterior</option>";
    for (const id of ['filtro-sel', 'filtro-cel']) {
      const sel = document.getElementById(id);
      sel.innerHTML = opcoes;
      sel.addEventListener('change', () => escolher(sel.value));
    }
    document.querySelectorAll('#modo button').forEach((b) => b.addEventListener('click', async () => {
      // o desenho do Brasil (28 kB) só vem na primeira vez que alguém pede o mapa
      if (b.dataset.modo === 'mapa' && !estado.caminhos) {
        estado.caminhos = await centros(await (await fetch('uf_caminhos.json')).json());
      }
      estado.modo = b.dataset.modo;
      document.querySelectorAll('#modo button').forEach((x) => x.classList.toggle('on', x === b));
      desenhar();
    }));
    await lerHistorico();
    await atualizar();
    arrumar();
    desenhar();
    // ?dossie=BA abre o dossiê de um estado ao carregar (para conferir o desenho sem passar o mouse)
    const dossie = PARAMS.get('dossie');
    if (dossie && UF[dossie]) {
      const el = quadros.mapa.contentDocument.querySelector("[data-uf='" + dossie + "']");
      if (el) setTimeout(() => mostrarTooltip(dossie, el), 1500);
    }
    // de computador para celular (ou o contrário) a página se monta de novo; no mesmo modo, só reescala
    addEventListener('resize', () => { if (celular() !== MODO_CEL) location.reload(); else arrumar(); });
    setInterval(async () => { if (await atualizar()) desenhar(); }, INTERVALO);
    setInterval(lerHistorico, 5 * INTERVALO);
    setInterval(() => {
      const el = quadros.placar && quadros.placar.contentDocument.getElementById('t18rel');
      if (el) el.textContent = contagem();
    }, 1000);
    palco.classList.add('pronto');
  }

  const TT_CSS = ".tt18{background:#FBF8F2;border:1.5px solid #CBBDA2;padding:34px 34px 26px 34px;box-shadow:0 14px 34px rgba(28,25,21,.2)}" +
    ".tt18 .fita{position:absolute;left:200px;top:-12px;width:150px;height:30px;background:#CBBDA2;opacity:.7;transform:rotate(-3deg)}" +
    ".tt18 .rot{margin-bottom:14px;font-size:16px}.tt18 .linha{display:flex;align-items:baseline;gap:14px}.tt18 .linha .num{font-size:48px}" +
    ".tt18 .linha .rot{font-size:15px}.tt18 .barra{display:flex;height:16px;margin:10px 0 14px 0;background:#E5DBC8}" +
    ".tt18 .barra .bl{background:#B8322A}.tt18 .barra .bf{background:#2B5797;margin-left:auto}" +
    ".tt18 .txt{font-size:19px;margin-top:16px;color:var(--tinta)}.tt18 .nota{margin-top:8px;font-size:15px}" +
    ".tt18 .mao{position:absolute;right:28px;top:24px;transform:rotate(-4deg);font-size:32px}" +
    ".tela.tt18{inset:auto;left:14px;right:14px;top:14px;animation:ttEntra .38s cubic-bezier(.2,.8,.2,1) both}" +
    "@keyframes ttEntra{from{opacity:0;transform:translateY(12px) scale(.96)}}" +
    ".tt18 .barra .bl,.tt18 .barra .bf{animation-delay:.12s!important}";

  iniciar();
})();
