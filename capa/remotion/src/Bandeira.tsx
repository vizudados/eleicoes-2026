// Bandeira do Brasil em traço de caneta, com cores esmaecidas. Geometria oficial (Lei 5.700/1971):
// retângulo 20M × 14M, losango a 1,7M das bordas, círculo de raio 3,5M, faixa entre arcos de raio 8M e 8,5M
// centrados 2M à esquerda do pé do diâmetro vertical, dístico ORDEM E PROGRESSO nas posições do desenho oficial.
// As estrelas são desenhadas em Estrelas.tsx (elas saem da bandeira e voam para o mapa).
import React from 'react';
import {CENTRO, DADOS, ESC_BANDEIRA} from './dados';
import {COR, T, hexRgb, mistura, prog, rgb, saida, suave} from './tempo';

// Letras do dístico (desenho oficial, unidades da bandeira; base em y = 0, altura 70).
const P = 'm-31.5 0h13v-26h28a22 22 0 0 0 0-44h-40zm13-39h27a9 9 0 0 0 0-18h-27z';
const O = 'm0 0a31.5 35 0 0 0 0-70 31.5 35 0 0 0 0 70m0-13a18.5 22 0 0 0 0-44 18.5 22 0 0 0 0 44';
const GLIFOS: Record<string, string[]> = {
  O: [O],
  R: [P, 'm28 0c0-10 0-32-15-32h-19c22 0 22 22 22 32'],
  D: ['m-31.5 0h33a30 30 0 0 0 30-30v-10a30 30 0 0 0-30-30h-33zm13-13h19a19 19 0 0 0 19-19v-6a19 19 0 0 0-19-19h-19z'],
  E: ['m-31.5 0h63v-13h-51v-18h40v-12h-40v-14h48v-13h-60z'],
  e: ['m-26.25 0h52.5v-12h-40.5v-16h33v-12h-33v-11h39.25v-12h-51.25z'],
  M: ['m-31.5 0h12v-48l14 48h11l14-48v48h12v-70h-17.5l-14 48-14-48h-17.5z'],
  P: [P],
  G: [O, 'M5-35H31.5V-25H5z', 'm21.5-35h10v35h-10z'],
  S: [
    'm-15.75-22c0 7 6.75 10.5 16.75 10.5s14.74-3.25 14.75-7.75c0-14.25-46.75-5.25-46.5-30.25 0.25-21.5 24.75-20.5 33.75-20.5s26 4 25.75 21.25h-15.25c0-7.5-7-10.25-15-10.25-7.75 0-13.25 1.25-13.25 8.5-0.25 11.75 46.25 4 46.25 28.75 0 18.25-18 21.75-31.5 21.75-11.5 0-31.55-4.5-31.5-22z',
  ],
};
const LEMA: [string, number][] = [
  ['O', -7], ['R', -4], ['D', -1], ['E', 2], ['M', 5], ['e', 9.75], ['P', 14.5], ['R', 17.5],
  ['O', 20.5], ['G', 23.5], ['R', 26.5], ['E', 29.5], ['S', 32.5], ['S', 35.5], ['O', 38.5],
];

const LOSANGO = 'M-1743 0L0 1113L1743 0L0-1113Z';
const FAIXA = 'm-2205 1470a1785 1785 0 0 1 3570 0h-105a1680 1680 0 1 0-3360 0z';

/** Traço que se desenha: pathLength 1, tracejado único, deslocado conforme o progresso. */
const Traco: React.FC<{d: string; p: number; largura: number; opacidade?: number; cor?: string}> = ({
  d,
  p,
  largura,
  opacidade = 1,
  cor = COR.creme,
}) =>
  p <= 0 ? null : (
    <path
      d={d}
      pathLength={1}
      fill="none"
      stroke={cor}
      strokeWidth={largura}
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray="1 2"
      strokeDashoffset={1 - p}
      opacity={opacidade}
    />
  );

/** Zoom da câmera: começa no disco (2×) e abre até a bandeira inteira. */
export const zoomBandeira = (t: number) => mistura(2.0, 1.0, suave(prog(t, T.zoom[0], T.zoom[1])));

export const opacidadeBandeira = (t: number) =>
  mistura(1, 0.24, suave(prog(t, T.fantasma[0], T.fantasma[1]))) * (1 - suave(prog(t, T.someFantasma[0], T.someFantasma[1])));

const LAVAGENS = [
  // [id, cor, centro x, centro y, raio final, início, fim]
  ['azul', COR.azul, 0, 0, 900, 3.1, 3.65],
  ['amarelo', COR.amarelo, 0, 0, 2000, 3.2, 3.88],
  ['branco', COR.branco, -700, -170, 1700, 3.28, 3.86],
  ['verde', COR.verde, 0, 0, 2900, 3.36, 4.1],
] as const;

export const Bandeira: React.FC<{t: number}> = ({t}) => {
  const opac = opacidadeBandeira(t);
  if (opac <= 0.002 || t < T.circulo[0]) return null;
  const z = zoomBandeira(t);
  const esc = ESC_BANDEIRA * z;
  const px = (v: number) => v / esc; // largura em px → unidades da bandeira
  const b = DADOS.bandeira;
  const lav = Object.fromEntries(
    LAVAGENS.map(([id, , , , raio, a, f]) => [id, {r: raio * saida(prog(t, a, f)), fim: t >= f}]),
  ) as Record<string, {r: number; fim: boolean}>;
  const corOk = t >= T.cor[0];
  // Depois da cor, a caneta recua um pouco: a bandeira lê como bandeira, o traço como desenho.
  const tracoOpac = mistura(0.95, 0.62, prog(t, T.cor[0], T.cor[1]));
  const largura = px(1.35);

  const camada = (id: string, cor: string, forma: React.ReactNode) => {
    const l = lav[id];
    if (l.r <= 0) return null;
    return (
      <g key={id} mask={l.fim ? undefined : `url(#lav-${id})`} fill={cor} opacity={0.93}>
        {forma}
      </g>
    );
  };

  return (
    <g transform={`translate(${CENTRO.x} ${CENTRO.y}) scale(${esc})`} opacity={opac}>
      <defs>
        <clipPath id="disco">
          <circle r={735} />
        </clipPath>
        <clipPath id="g-corte">
          <path d="m-31.5 0v-70h63v70zm31.5-47v12h31.5v-12z" />
        </clipPath>
        <filter id="borra" x="-60%" y="-60%" width="220%" height="220%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.0045" numOctaves={2} seed={11} result="ruido" />
          <feDisplacementMap in="SourceGraphic" in2="ruido" scale={360} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={16} />
        </filter>
        {corOk &&
          LAVAGENS.map(([id, , cx, cy]) => (
            <mask key={id} id={`lav-${id}`} maskUnits="userSpaceOnUse" x={-2400} y={-1800} width={4800} height={3600}>
              <circle cx={cx} cy={cy} r={Math.max(1, lav[id].r)} fill="#fff" filter="url(#borra)" />
            </mask>
          ))}
      </defs>

      {/* Cores esmaecidas, em lavagem de tinta do centro para fora */}
      {corOk && (
        <g opacity={mistura(1, 0.38, suave(prog(t, T.fantasma[0], T.fantasma[1])))}>
          {camada('verde', COR.verde, <rect x={-2100} y={-1470} width={4200} height={2940} />)}
          {camada('amarelo', COR.amarelo, <path d={LOSANGO} />)}
          {camada('azul', COR.azul, <circle r={735} />)}
          {camada('branco', COR.branco, <path d={FAIXA} clipPath="url(#disco)" />)}
        </g>
      )}

      {/* Traço de caneta: círculo, faixa, losango, retângulo */}
      <g>
        <Traco d={b.circulo.d} p={suave(prog(t, T.circulo[0], T.circulo[1]))} largura={largura} opacidade={tracoOpac} />
        {b.faixa.map((f, i) => (
          <Traco key={i} d={f.d} p={suave(prog(t, T.faixa[0] + i * 0.12, T.faixa[1] + i * 0.12))} largura={largura * 0.85} opacidade={tracoOpac} />
        ))}
        {b.losango.map((l, i) => {
          const passo = (T.losango[1] - T.losango[0]) / 5;
          return <Traco key={i} d={l.d} p={suave(prog(t, T.losango[0] + i * passo, T.losango[0] + (i + 2) * passo))} largura={largura} opacidade={tracoOpac} />;
        })}
        {b.retangulo.map((l, i) => {
          const passo = (T.retangulo[1] - T.retangulo[0]) / 5;
          return <Traco key={i} d={l.d} p={suave(prog(t, T.retangulo[0] + i * passo, T.retangulo[0] + (i + 2) * passo))} largura={largura} opacidade={tracoOpac} />;
        })}
      </g>

      {/* Dístico: cada letra se escreve (contorno) e depois se preenche; na cor, vira verde sobre o branco */}
      <g transform="translate(-420 1470)">
        {LEMA.map(([letra, ang], i) => {
          const n = LEMA.length;
          const a = T.lema[0] + (i / n) * (T.lema[1] - T.lema[0] - 0.2);
          const p = prog(t, a, a + 0.28);
          if (p <= 0) return null;
          const enche = prog(t, a + 0.2, a + 0.42);
          const verde = suave(prog(t, T.cor[0] + 0.14, T.cor[0] + 0.5)); // verde junto com a lavagem branca da faixa
          const preenchimento = rgb(hexRgb(COR.creme), hexRgb(COR.verde), verde);
          const opPre = mistura(0.85 * enche, 1, verde);
          return (
            <g key={i} transform={`rotate(${ang}) translate(0 -1697.5)`}>
              {GLIFOS[letra].map((d, k) => (
                <g key={k} clipPath={letra === 'G' && k === 0 ? 'url(#g-corte)' : undefined}>
                  <path d={d} fill={preenchimento} fillRule="evenodd" opacity={opPre} />
                  <path
                    d={d}
                    pathLength={1}
                    fill="none"
                    stroke={COR.creme}
                    strokeWidth={px(0.8)}
                    strokeDasharray="1 2"
                    strokeDashoffset={1 - saida(p)}
                    opacity={mistura(0.9, 0, verde)}
                  />
                </g>
              ))}
            </g>
          );
        })}
      </g>
    </g>
  );
};
