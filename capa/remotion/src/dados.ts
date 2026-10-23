// Dados preparados por scripts/preparar_dados.py e scripts/preparar_arte.py (em public/dados).
import capa from '../public/dados/capa.json';
import ceu from '../public/dados/ceu.json';
import horizonte from '../public/dados/horizonte.json';
import {T} from './tempo';

export type Estrela = (typeof capa.estrelas)[number];

export const CENTRO = {x: 960, y: 583};
/** Bandeira oficial: 4200 × 2940 unidades (M = 210); na tela, 760 × 532 px. */
export const ESC_BANDEIRA = 760 / 4200;
/** Raio externo da estrela (unidades da bandeira) por grandeza: 0,30M · 0,25M · 0,20M · 0,14M · 0,10M de diâmetro. */
export const RAIO_GRANDEZA = [0, 31.5, 26.25, 21, 15, 10.5];
/** Raio da estrela pousada no mapa, em px. */
export const RAIO_MAPA = [0, 6.4, 5.4, 4.6, 3.9, 3.4];

export const DADOS = capa;
export const CEU = ceu as Record<string, {largura: number; altura: number}>;
export const HORIZONTE = horizonte;

/** Partida de cada estrela: da esquerda para a direita da bandeira. */
const ordemVoo = [...capa.estrelas.keys()].sort((a, b) => capa.estrelas[a].x - capa.estrelas[b].x);
export const PARTIDA: number[] = new Array(capa.estrelas.length);
ordemVoo.forEach((i, k) => {
  PARTIDA[i] = T.voo[0] + (k / (ordemVoo.length - 1)) * (T.voo[1] - T.voo[0]);
});
export const CHEGADA: Record<string, number> = {};
capa.estrelas.forEach((e, i) => {
  CHEGADA[e.uf] = PARTIDA[i] + T.vooDur;
});

/** Surgimento no céu: da 1ª à 5ª grandeza, de cima para baixo dentro da grandeza. */
const ordemSurge = [...capa.estrelas.keys()].sort(
  (a, b) => capa.estrelas[a].g - capa.estrelas[b].g || capa.estrelas[a].y - capa.estrelas[b].y,
);
export const SURGE: number[] = new Array(capa.estrelas.length);
ordemSurge.forEach((i, k) => {
  SURGE[i] = T.estrelas[0] + (k / (ordemSurge.length - 1)) * (T.estrelas[1] - T.estrelas[0]);
});

/** Polígono de estrela de 5 pontas (ponta para cima), raio externo r. */
export const estrelaPath = (r: number) => {
  const pts: string[] = [];
  for (let k = 0; k < 10; k++) {
    const raio = k % 2 === 0 ? r : r * 0.382;
    const ang = -Math.PI / 2 + (k * Math.PI) / 5;
    pts.push(`${(raio * Math.cos(ang)).toFixed(2)},${(raio * Math.sin(ang)).toFixed(2)}`);
  }
  return `M${pts.join('L')}Z`;
};
