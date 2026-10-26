// Roteiro em segundos (30 fps, 21 s = 630 quadros) e funções de tempo.
export const FPS = 30;
export const SEGUNDOS = 21;
export const QUADROS = SEGUNDOS * FPS;

export const T = {
  // Ato 1 · o céu da bandeira
  estrelas: [0.25, 1.45] as const, // as 27 estrelas surgem, da 1ª à 5ª grandeza
  circulo: [1.1, 1.9] as const,
  faixa: [1.55, 2.25] as const,
  lema: [1.8, 2.75] as const, // ORDEM E PROGRESSO, letra a letra
  zoom: [1.75, 2.72] as const, // do disco à bandeira inteira
  losango: [2.72, 3.4] as const,
  retangulo: [2.92, 3.66] as const,
  cor: [3.1, 4.1] as const, // verde, amarelo, azul e branco esmaecidos
  // Ato 2 · cada estrela voa para a sua UF
  voo: [4.55, 5.75] as const, // janela de partida (da esquerda para a direita da bandeira)
  vooDur: 1.4,
  fantasma: [4.5, 5.5] as const, // a bandeira recua para um fantasma
  someFantasma: [6.75, 7.9] as const,
  contorno: [5.0, 7.45] as const,
  contorno2: [5.25, 7.75] as const,
  divisaDur: 0.95,
  // Ato 3 · os 5.570 municípios
  pontos: 8.0,
  velOnda: 70, // px/s, da estrela da UF para fora
  acende: 0.45,
  corAtraso: 1.25,
  corDur: 1.05,
  // Segunda onda: mesma ordem espacial do 1º turno, mesma duração de esmaecimento por ponto.
  segundoTurno: [13.2, 16.7] as const,
  brilhoTrocaDur: 0.6, // pulso creme igual nos dois sentidos, centrado no meio da transição local
  // Ato 4 · o horizonte de Norte a Sul
  horizonte: [11.0, 15.7] as const,
  // Ato 5 · assenta
  calmo: 16.6,
  assenta: 18.0, // o tempo de TODAS as camadas congela aqui; 3 s finais realmente parados
};

export const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x);
export const prog = (t: number, a: number, b: number) => clamp01((t - a) / (b - a));
export const suave = (x: number) => {
  const v = clamp01(x);
  return v < 0.5 ? 4 * v * v * v : 1 - Math.pow(-2 * v + 2, 3) / 2;
};
export const leve = (x: number) => {
  const v = clamp01(x);
  return v * v * (3 - 2 * v);
};
export const saida = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
export const volta = (x: number) => {
  // ease-out com leve passada (back)
  const v = clamp01(x) - 1;
  const c = 1.9;
  return 1 + (c + 1) * v * v * v + c * v * v;
};
export const mistura = (a: number, b: number, f: number) => a + (b - a) * f;

/** Acaso determinístico (mesma semente, mesmo quadro). */
export const acaso = (i: number, semente = 1) => {
  const x = Math.sin(i * 127.1 + semente * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

export const hexRgb = (h: string): [number, number, number] => [
  parseInt(h.slice(1, 3), 16),
  parseInt(h.slice(3, 5), 16),
  parseInt(h.slice(5, 7), 16),
];
export const rgb = (a: [number, number, number], b: [number, number, number], f: number) =>
  `rgb(${Math.round(mistura(a[0], b[0], f))},${Math.round(mistura(a[1], b[1], f))},${Math.round(mistura(a[2], b[2], f))})`;

export const COR = {
  tinta: '#1C1915',
  papel: '#F1EBDF',
  creme: '#E5DBC8',
  areia: '#CBBDA2',
  estrela: '#F6F0E3',
  // Bandeira com as cores esmaecidas, conversando com o bege da casa.
  verde: '#5E7C59',
  amarelo: '#CDAC5E',
  azul: '#34477A',
  branco: '#ECE5D6',
};
