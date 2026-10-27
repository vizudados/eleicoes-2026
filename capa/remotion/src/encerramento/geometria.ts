// A composição e a prova de colisão leem exatamente estas primitivas.
import dados from '../../public/dados/encerramento.json';
import roteiro from './roteiro.json';

export const progresso = (t: number, a: number, b: number) => Math.max(0, Math.min(1, (t - a) / (b - a)));
export const suave = (v: number) => v * v * (3 - 2 * v);
export const mistura = (a: number, b: number, v: number) => a + (b - a) * v;

export const posicaoFragmento = (
  origem: {x: number; y: number; mapa: boolean},
  lote: {x: number; y: number; candidato: string; partida: number; duracao: number},
  t: number,
) => {
  const p = suave(progresso(t, lote.partida, lote.partida + lote.duracao));
  if (!origem.mapa) {
    const q = 1 - p;
    return {
      x: q ** 3 * origem.x + 3 * q * q * p * 1750 + 3 * q * p * p * (lote.x + 120) + p ** 3 * lote.x,
      y: q ** 3 * origem.y + 3 * q * q * p * origem.y + 3 * q * p * p * (lote.y + 100) + p ** 3 * lote.y,
    };
  }
  return {
    x: mistura(origem.x, lote.x, p) + (lote.candidato === 'flavio' ? -60 : 60) * p * (1 - p),
    y: mistura(origem.y, lote.y, p) - 40 * p * (1 - p),
  };
};

export type Circulo = {
  x: number; y: number; r: number; opacidade: number; id: number | string;
  classe: 'municipio' | 'fragmento' | 'lote' | 'diferenca'; candidato?: string; traco?: number;
};

export const opacidadeMapa = (t: number) => 1 - suave(progresso(t, roteiro.someMapa[0], roteiro.someMapa[1]));
export const destaque = (t: number) => suave(progresso(t, roteiro.diferenca[0], roteiro.diferenca[1]));
export const opacidadeFio = (t: number) => 0.26 * suave(progresso(t, roteiro.exterior.inicio, roteiro.exterior.inicio + 0.5))
  * (1 - suave(progresso(t, 8.0, 8.7)));

export function* circulosNoTempo(recebido: number): Generator<Circulo> {
  const t = Math.min(recebido, roteiro.parado);
  const mapa = opacidadeMapa(t);
  if (mapa > 0) {
    for (let i = 0; i < dados.origens.length; i++) {
      const o = dados.origens[i];
      if (!o.mapa) continue; // Exterior não vira ponto solto na abertura.
      const ordem = ((i * 37) % 5573) / 5572;
      const a = suave(progresso(t, roteiro.municipios[0] + ordem * 0.65, roteiro.municipios[1]));
      if (a > 0) yield {x: o.x, y: o.y, r: 0.85, opacidade: 0.55 * a * mapa, id: o.id, classe: 'municipio'};
    }
  }
  if (t >= 1.7 && t < roteiro.partidasDiferenca[1] + roteiro.vooDiferenca) {
    for (let i = 0; i < dados.fragmentos.length; i++) {
      const [o, d, votos] = dados.fragmentos[i];
      const origem = dados.origens[o], lote = dados.lotes[d];
      if (!origem.mapa && t <= lote.partida) continue;
      const entrega = progresso(t, lote.partida + lote.duracao - 0.35, lote.partida + lote.duracao);
      if (entrega === 1) continue;
      const entra = origem.mapa ? suave(progresso(t, 1.7, 2.5)) : suave(progresso(t, lote.partida, lote.partida + 0.25));
      const p = posicaoFragmento(origem, lote, t);
      yield {...p, r: roteiro.hemiciclo.raioPonto * Math.sqrt(votos / dados.unidade), opacidade: 0.76 * entra * (1 - entrega),
        id: i, classe: 'fragmento', candidato: lote.candidato};
    }
  }
  const realce = destaque(t);
  for (let i = 0; i < dados.lotes.length; i++) {
    const l = dados.lotes[i];
    const entrega = suave(progresso(t, l.partida + l.duracao - 0.35, l.partida + l.duracao));
    if (entrega === 0) continue;
    yield {x: l.x, y: l.y, r: l.r, opacidade: (l.diferenca ? mistura(0.82, 1, realce) : mistura(0.82, 0.64, realce)) * entrega,
      id: i, classe: 'lote', candidato: l.candidato};
    if (l.diferenca && realce > 0) yield {x: l.x, y: l.y, r: l.r + 0.35, traco: 0.55,
      opacidade: 0.72 * realce, id: i, classe: 'diferenca', candidato: l.candidato};
  }
}
