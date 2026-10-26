// O mapa do voto: contorno do Brasil e divisas das UFs em traço de caneta; 5.570 municípios que acendem como
// estrelas pequenas, em ondas a partir da estrela de cada UF; depois mostram as margens dos dois turnos de 2026.
import React, {useMemo} from 'react';
import {CHEGADA, DADOS} from './dados';
import {brilhoTroca, inicioCor1, iniciosCor2} from './municipios';
import {COR, T, hexRgb, leve, mistura, prog, rgb, saida, suave} from './tempo';

const Traco: React.FC<{d: string; p: number; largura: number; opacidade: number}> = ({d, p, largura, opacidade}) =>
  p <= 0 ? null : (
    <path
      d={d}
      pathLength={1}
      fill="none"
      stroke={COR.creme}
      strokeWidth={largura}
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray="1 2"
      strokeDashoffset={1 - p}
      opacity={opacidade}
    />
  );

const BRANCO_QUENTE = hexRgb('#FFF6E4');
const CREME = hexRgb(COR.creme);

export const Mapa: React.FC<{t: number}> = ({t}) => {
  const m = DADOS.municipios;
  const pontos = useMemo(
    () => {
      const cores1 = m.d.map((d, i) => inicioCor1(d, m.u[i]));
      const cores2 = iniciosCor2(cores1);
      return m.x.map((x, i) => {
        const on = T.pontos + m.d[i] / T.velOnda + 0.35 * m.u[i];
        return {
          x,
          y: m.y[i],
          r: m.r[i],
          on,
          cor: cores1[i],
          cor2: cores2[i],
          primeiro: hexRgb(m.cor[i]),
          segundo: hexRgb(m.cor2[i]),
          troca: m.troca[i],
          faisca: m.r[i] > 1.9,
        };
      });
    },
    [m],
  );

  // Contorno: uma linha só, do extremo norte, no sentido horário; um segundo passe mais leve, atrasado.
  const c = DADOS.contorno;
  const pc = leve(prog(t, T.contorno[0], T.contorno[1]));
  const pc2 = leve(prog(t, T.contorno2[0], T.contorno2[1]));
  const amostras = c.amostras;
  const n = amostras.length / 2;
  let ponta: React.ReactNode = null;
  if (pc > 0 && pc < 1) {
    const k = Math.min(n - 1, Math.floor(pc * (n - 1)));
    const x = amostras[2 * k];
    const y = amostras[2 * k + 1];
    const forca = Math.min(1, pc * 12, (1 - pc) * 12);
    ponta = (
      <g opacity={forca}>
        <circle cx={x} cy={y} r={7} fill={COR.estrela} opacity={0.16} />
        <circle cx={x} cy={y} r={2.1} fill={COR.estrela} />
      </g>
    );
  }

  const divisas = DADOS.divisas.map((dv, i) => {
    const a = Math.max(...dv.ufs.map((u) => CHEGADA[u] ?? T.contorno[0])) - 0.15;
    const p = suave(prog(t, a, a + T.divisaDur));
    return <Traco key={i} d={dv.d} p={p} largura={0.95} opacidade={0.42} />;
  });

  const ilhas = DADOS.ilhas.map((il, i) => (
    <Traco key={i} d={il.d} p={suave(prog(t, T.contorno[1] - 0.6 + i * 0.05, T.contorno[1] - 0.1 + i * 0.05))} largura={0.9} opacidade={0.8} />
  ));

  const circulos: React.ReactNode[] = [];
  const faiscas: React.ReactNode[] = [];
  const viradas: React.ReactNode[] = [];
  if (t >= T.pontos) {
    for (let i = 0; i < pontos.length; i++) {
      const p = pontos[i];
      if (t < p.on) continue;
      const a = prog(t, p.on, p.on + T.acende);
      const r = p.r * mistura(2.3, 1, saida(a));
      const corP = prog(t, p.cor, p.cor + T.corDur);
      const cor2P = prog(t, p.cor2, p.cor2 + T.corDur);
      const cor = cor2P > 0
        ? rgb(p.primeiro, p.segundo, suave(cor2P))
        : corP > 0 ? rgb(CREME, p.primeiro, suave(corP)) : rgb(BRANCO_QUENTE, CREME, a);
      circulos.push(<circle key={i} cx={p.x} cy={p.y} r={r.toFixed(2)} fill={cor} opacity={Math.min(1, a * 3)} />);
      const brilho = brilhoTroca(t, p.cor2, p.troca);
      if (brilho > 0) {
        // Halo finito, sem blur, preso à área do mapa. Não move nem redimensiona o ponto.
        viradas.push(
          <g key={`v${i}`} data-municipio={m.cd_ibge[i]} opacity={brilho}>
            <circle cx={p.x} cy={p.y} r={6.5} fill="url(#brilho-virada)" />
            <circle cx={p.x} cy={p.y} r={p.r + 1.2} fill="none" stroke={COR.estrela} strokeWidth={0.75} opacity={0.8} />
          </g>,
        );
      }
      if (p.faisca && a < 1) {
        const l = (3 + p.r * 2.2) * Math.sin(Math.PI * a);
        faiscas.push(
          <g key={`f${i}`} stroke="#FFF6E4" strokeWidth={0.8} strokeLinecap="round" opacity={0.7 * (1 - a)}>
            <line x1={p.x - l} y1={p.y} x2={p.x + l} y2={p.y} />
            <line x1={p.x} y1={p.y - l} x2={p.x} y2={p.y + l} />
          </g>,
        );
      }
    }
  }

  return (
    <g>
      <defs>
        <radialGradient id="brilho-virada">
          <stop offset="0" stopColor={COR.estrela} stopOpacity={0.85} />
          <stop offset="0.4" stopColor={COR.estrela} stopOpacity={0.4} />
          <stop offset="1" stopColor={COR.estrela} stopOpacity={0} />
        </radialGradient>
        <clipPath id="limite-viradas"><rect x={688} y={303} width={544} height={560} /></clipPath>
      </defs>
      {divisas}
      <Traco d={c.d2} p={pc2} largura={0.9} opacidade={0.32} />
      <Traco d={c.d1} p={pc} largura={1.45} opacidade={0.92} />
      {ilhas}
      {ponta}
      <g>{circulos}</g>
      <g>{faiscas}</g>
      <g clipPath="url(#limite-viradas)">{viradas}</g>
    </g>
  );
};
