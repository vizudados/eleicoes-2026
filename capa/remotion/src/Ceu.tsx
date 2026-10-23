// Céu noturno: estrelas fracas de fundo (fora do título, das setas e dos blocos de números, que ficam calmos),
// e, no fim, nuvens e aves em traço creme sobre o horizonte.
import React from 'react';
import {Img, staticFile} from 'remotion';
import {CEU, DADOS} from './dados';
import {revelado} from './Horizonte';
import {T, acaso, mistura, prog, saida} from './tempo';

export const CeuDeFundo: React.FC<{t: number}> = ({t}) => {
  const entra = mistura(0.45, 1, saida(prog(t, 0, 1.4)));
  const vivo = 1 - prog(t, T.calmo - 1.2, T.calmo);
  return (
    <g>
      {DADOS.ceu.map((s, i) => {
        const pisca = s.f > 0.72 ? 1 - 0.45 * vivo * (0.5 + 0.5 * Math.sin(2 * Math.PI * (t * (0.25 + 0.3 * s.f) + s.f * 9))) : 1;
        return <circle key={i} cx={s.x} cy={s.y} r={s.r * 1.15} fill="#F1EBDF" opacity={Math.min(0.75, s.a * 1.9) * entra * pisca} />;
      })}
    </g>
  );
};

type Peca = {nome: string; x: number; y: number; deriva: number; opacidade: number};
const NUVENS: Peca[] = [
  {nome: 'nuvem-1', x: 250, y: 800, deriva: 16, opacidade: 0.6},
  {nome: 'fiapo-1', x: 382, y: 838, deriva: 22, opacidade: 0.38},
  {nome: 'nuvem-3', x: 622, y: 805, deriva: 12, opacidade: 0.55},
  {nome: 'nuvem-4', x: 1302, y: 814, deriva: 14, opacidade: 0.55},
  {nome: 'fiapo-3', x: 1478, y: 836, deriva: 20, opacidade: 0.36},
  {nome: 'nuvem-2', x: 1662, y: 796, deriva: 12, opacidade: 0.6},
];

const peca = (nome: string, x: number, y: number, opacidade: number, extra?: React.CSSProperties) => {
  const c = CEU[nome];
  return (
    <Img
      key={nome}
      src={staticFile(`img/${nome}.png`)}
      style={{
        position: 'absolute',
        left: x - c.largura / 2,
        top: y - c.altura / 2,
        width: c.largura,
        height: c.altura,
        opacity: opacidade,
        ...extra,
      }}
    />
  );
};

export const CeuDoHorizonte: React.FC<{t: number}> = ({t}) => {
  if (t < T.horizonte[0]) return null;
  const deriva = saida(prog(t, T.horizonte[0], T.calmo + 0.4));
  const itens: React.ReactNode[] = NUVENS.map((n) => {
    const op = n.opacidade * revelado(t, n.x);
    return op > 0.001 ? peca(n.nome, n.x + n.deriva * deriva, n.y, op) : null;
  });
  // Garça: atravessa devagar da Amazônia para o centro e pousa o voo no ar (quadro final).
  const g = saida(prog(t, 12.0, T.calmo));
  if (g > 0) {
    const x = mistura(150, 532, g);
    const y = mistura(842, 792, g) + 3 * Math.sin(2 * Math.PI * t * 0.5) * (1 - g);
    itens.push(peca('garca', x, y, 0.82 * Math.min(1, g * 6)));
  }
  // Bando ao longe, chegando pela direita.
  const b = saida(prog(t, 12.6, T.calmo));
  if (b > 0) {
    itens.push(peca('bando', mistura(1905, 1548, b), mistura(806, 800, b) + 2 * Math.sin(2 * Math.PI * (t * 0.6 + acaso(3))) * (1 - b), 0.7 * Math.min(1, b * 5)));
  }
  return <>{itens}</>;
};
