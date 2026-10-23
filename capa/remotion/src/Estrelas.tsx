// As 27 estrelas: surgem no disco da bandeira (posições e grandezas oficiais), voam cada uma para a sua UF
// e ficam pousadas no mapa, de onde parte a onda dos municípios.
import React from 'react';
import {zoomBandeira} from './Bandeira';
import {CENTRO, CHEGADA, DADOS, ESC_BANDEIRA, PARTIDA, RAIO_GRANDEZA, RAIO_MAPA, SURGE, estrelaPath} from './dados';
import {COR, T, acaso, mistura, prog, saida, suave, volta} from './tempo';

type Ponto = {x: number; y: number};

const bezier = (a: Ponto, c: Ponto, b: Ponto, q: number): Ponto => ({
  x: (1 - q) * (1 - q) * a.x + 2 * (1 - q) * q * c.x + q * q * b.x,
  y: (1 - q) * (1 - q) * a.y + 2 * (1 - q) * q * c.y + q * q * b.y,
});

export const Estrelas: React.FC<{t: number}> = ({t}) => {
  const z = zoomBandeira(t);
  const itens: React.ReactNode[] = [];
  const brilhos: React.ReactNode[] = [];
  DADOS.estrelas.forEach((e, i) => {
    const surge = prog(t, SURGE[i], SURGE[i] + 0.42);
    if (surge <= 0) return;
    const partida = PARTIDA[i];
    const chegada = CHEGADA[e.uf];
    const q = suave(prog(t, partida, partida + T.vooDur));
    const naBandeira: Ponto = {x: CENTRO.x + e.x * ESC_BANDEIRA * z, y: CENTRO.y + e.y * ESC_BANDEIRA * z};
    const inicio: Ponto = {x: CENTRO.x + e.x * ESC_BANDEIRA, y: CENTRO.y + e.y * ESC_BANDEIRA};
    const fim: Ponto = {x: e.ax, y: e.ay};
    const dx = fim.x - inicio.x;
    const dy = fim.y - inicio.y;
    const dist = Math.hypot(dx, dy) || 1;
    const curva = (0.22 + 0.18 * acaso(i, 4)) * dist * (acaso(i, 9) > 0.5 ? 1 : -1);
    const ctrl: Ponto = {x: (inicio.x + fim.x) / 2 - (dy / dist) * curva, y: (inicio.y + fim.y) / 2 + (dx / dist) * curva};

    const rBandeira = RAIO_GRANDEZA[e.g] * ESC_BANDEIRA;
    let pos: Ponto;
    let r: number;
    if (q <= 0) {
      pos = naBandeira;
      const cintila = 1 + 0.07 * Math.sin(2 * Math.PI * (t * 1.1 + acaso(i, 2))) * prog(t, SURGE[i] + 0.4, SURGE[i] + 0.9);
      r = rBandeira * z * volta(surge) * cintila;
    } else {
      pos = bezier(inicio, ctrl, fim, q);
      r = mistura(rBandeira, RAIO_MAPA[e.g], q) * (1 + 0.55 * Math.sin(Math.PI * q));
    }

    // Brilho ao nascer: duas linhas cruzadas que se apagam.
    const brilho = 1 - prog(t, SURGE[i], SURGE[i] + 0.75);
    if (brilho > 0 && surge > 0) {
      const l = r * 3.2 * saida(surge);
      brilhos.push(
        <g key={`b${i}`} transform={`translate(${pos.x} ${pos.y})`} opacity={0.75 * brilho} stroke={COR.estrela} strokeWidth={0.9} strokeLinecap="round">
          <line x1={-l} y1={0} x2={l} y2={0} />
          <line x1={0} y1={-l} x2={0} y2={l} />
        </g>,
      );
    }

    // Rastro no voo.
    if (q > 0 && q < 1) {
      const pts: string[] = [];
      for (let k = 0; k <= 8; k++) {
        const qq = Math.max(0, q - 0.22 * (1 - k / 8));
        const p = bezier(inicio, ctrl, fim, qq);
        pts.push(`${p.x.toFixed(1)},${p.y.toFixed(1)}`);
      }
      itens.push(
        <polyline key={`r${i}`} points={pts.join(' ')} fill="none" stroke={COR.estrela} strokeWidth={Math.max(0.8, r * 0.45)} strokeLinecap="round" opacity={0.28 * Math.sin(Math.PI * q)} />,
      );
      itens.push(<circle key={`h${i}`} cx={pos.x} cy={pos.y} r={r * 3.2} fill="url(#brilho-estrela)" opacity={0.5 * Math.sin(Math.PI * q)} />);
    } else if (q <= 0) {
      const apaga = 1 - prog(t, T.cor[0], T.cor[0] + 0.5); // no azul do disco o brilho some
      if (apaga > 0) itens.push(<circle key={`h${i}`} cx={pos.x} cy={pos.y} r={r * 3} fill="url(#brilho-estrela)" opacity={0.32 * surge * apaga} />);
    }

    // Pouso e o sinal da onda dos municípios: anéis que se abrem e somem.
    for (const [a, raio, forca] of [
      [chegada, 20, 0.55],
      [T.pontos - 0.15 + 0.25 * acaso(i, 6), 26, 0.4],
    ] as const) {
      const p = prog(t, a, a + 0.85);
      if (p > 0 && p < 1) {
        itens.push(
          <circle key={`a${i}-${a}`} cx={fim.x} cy={fim.y} r={RAIO_MAPA[e.g] + raio * saida(p)} fill="none" stroke={COR.estrela} strokeWidth={1} opacity={forca * (1 - p)} />,
        );
      }
    }

    const contornoTinta = mistura(0, 1.1, q);
    itens.push(
      <path
        key={`e${i}`}
        d={estrelaPath(r)}
        transform={`translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`}
        fill={COR.estrela}
        stroke={COR.tinta}
        strokeWidth={contornoTinta}
        paintOrder="stroke"
        strokeLinejoin="round"
        opacity={Math.min(1, surge * 2)}
      />,
    );
  });
  return (
    <g>
      <defs>
        <radialGradient id="brilho-estrela">
          <stop offset="0" stopColor={COR.estrela} stopOpacity={0.55} />
          <stop offset="0.35" stopColor={COR.estrela} stopOpacity={0.18} />
          <stop offset="1" stopColor={COR.estrela} stopOpacity={0} />
        </radialGradient>
      </defs>
      {itens}
      {brilhos}
    </g>
  );
};
