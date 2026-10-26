// Tempos dos pontos, separados do SVG para conferir a onda e o brilho sem Chromium.
import {T, prog} from './tempo';

export const inicioCor1 = (distancia: number, acaso: number) => {
  const on = T.pontos + distancia / T.velOnda + 0.35 * acaso;
  return on + T.corAtraso + 0.4 * ((acaso * 7.3) % 1);
};

export const iniciosCor2 = (primeiroTurno: number[]) => {
  const minimo = Math.min(...primeiroTurno);
  const intervalo = Math.max(...primeiroTurno) - minimo;
  const janela = T.segundoTurno[1] - T.segundoTurno[0] - T.corDur;
  return primeiroTurno.map((t) => T.segundoTurno[0] + (intervalo > 0 ? (t - minimo) / intervalo : 0) * janela);
};

export const brilhoTroca = (t: number, inicio: number, troca: number) => {
  if (troca === 0) return 0;
  const centro = inicio + T.corDur / 2;
  const a = centro - T.brilhoTrocaDur / 2;
  const b = centro + T.brilhoTrocaDur / 2;
  if (t <= a || t >= b) return 0;
  return Math.sin(Math.PI * prog(t, a, b)) ** 2;
};
