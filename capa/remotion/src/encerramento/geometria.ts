// Geometria pura, compartilhada pelo SVG e pela varredura de colisões dos testes.
export const progresso = (t: number, a: number, b: number) => Math.max(0, Math.min(1, (t - a) / (b - a)));
export const suave = (v: number) => v * v * (3 - 2 * v);
export const mistura = (a: number, b: number, v: number) => a + (b - a) * v;
export const posicaoFragmento = (
  origem: {x: number; y: number},
  lote: {x: number; y: number; candidato: string; partida: number; duracao: number},
  t: number,
) => {
  const p = suave(progresso(t, lote.partida, lote.partida + lote.duracao));
  return {
    x: mistura(origem.x, lote.x, p) + (lote.candidato === 'flavio' ? -76 : 76) * p * (1 - p),
    y: mistura(origem.y, lote.y, p) + 36 * p * (1 - p),
  };
};
