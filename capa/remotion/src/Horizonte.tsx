// O horizonte de Norte a Sul (Amazônia → sertão → Pelourinho → Congresso → Pão de Açúcar → São Paulo →
// araucárias → pampa): um desenho só, revelado da esquerda para a direita pela ponta da caneta.
// A máscara usa o mapa de ordem (public/img/horizonte-ordem.png): cada pixel aparece quando a frente passa por ele.
import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';
import {HORIZONTE} from './dados';
import {COR, T, acaso, clamp01, hexRgb, mistura, prog, saida} from './tempo';

const H = HORIZONTE;
const NITIDEZ = 36; // largura da frente de revelação ≈ 1/36 da faixa (≈ 45 px)

const carregar = (src: string) =>
  new Promise<HTMLImageElement>((ok, erro) => {
    const img = new Image();
    img.onload = () => ok(img);
    img.onerror = erro;
    img.src = src;
  });

const pixels = (img: HTMLImageElement) => {
  const c = document.createElement('canvas');
  c.width = img.width;
  c.height = img.height;
  const ctx = c.getContext('2d', {willReadFrequently: true})!;
  ctx.drawImage(img, 0, 0);
  return ctx.getImageData(0, 0, img.width, img.height).data;
};

/** Frente da caneta (0 → 1,08) no tempo t. */
export const frenteHorizonte = (t: number) => mistura(-0.06, 1.08, prog(t, T.horizonte[0], T.horizonte[1]));

export const Horizonte: React.FC<{t: number}> = ({t}) => {
  const ref = useRef<HTMLCanvasElement>(null);
  const [dados, setDados] = useState<{alfa: Uint8ClampedArray; ordem: Uint8ClampedArray} | null>(null);
  const [espera] = useState(() => delayRender('horizonte'));

  useEffect(() => {
    Promise.all([carregar(staticFile('img/horizonte.png')), carregar(staticFile('img/horizonte-ordem.png'))]).then(
      ([a, o]) => {
        const pa = pixels(a);
        const po = pixels(o);
        const n = H.largura * H.altura;
        const alfa = new Uint8ClampedArray(n);
        const ordem = new Uint8ClampedArray(n);
        for (let i = 0; i < n; i++) {
          alfa[i] = pa[i * 4 + 3];
          ordem[i] = po[i * 4];
        }
        setDados({alfa, ordem});
      },
    );
  }, []);

  const frente = frenteHorizonte(t);
  useLayoutEffect(() => {
    if (!dados || !ref.current) return;
    const ctx = ref.current.getContext('2d')!;
    const img = ctx.createImageData(H.largura, H.altura);
    const [r, g, b] = hexRgb(COR.creme);
    const d = img.data;
    const k = NITIDEZ;
    for (let i = 0; i < dados.alfa.length; i++) {
      const a = dados.alfa[i];
      if (a === 0) continue;
      const m = clamp01(k * (frente - dados.ordem[i] / 255));
      if (m === 0) continue;
      d[i * 4] = r;
      d[i * 4 + 1] = g;
      d[i * 4 + 2] = b;
      d[i * 4 + 3] = a * m;
    }
    ctx.putImageData(img, 0, 0);
  }, [dados, frente]);

  useEffect(() => {
    if (dados) continueRender(espera);
  }, [dados, espera]);

  return (
    <canvas
      ref={ref}
      width={H.largura}
      height={H.altura}
      style={{position: 'absolute', left: H.x, top: H.y, width: H.largura, height: H.altura}}
    />
  );
};

/** Ponta da caneta do horizonte e brilhos da água (rio, baía, espelho d'água). */
export const HorizonteVivo: React.FC<{t: number}> = ({t}) => {
  const frente = frenteHorizonte(t);
  const partes: React.ReactNode[] = [];
  const chao = H.y + H.chao;
  // A ponta anda na frente visível junto ao chão (ordem_chao: quando a tinta de cada coluna aparece).
  const alvo = frente - 0.5 / NITIDEZ;
  let coluna = 0;
  while (coluna < H.ordem_chao.length - 1 && H.ordem_chao[coluna + 1] <= alvo) coluna++;
  const xn = clamp01((coluna * 4) / (H.largura - 1));
  if (frente > -0.02 && frente < 1.04) {
    const xl = xn * (H.largura - 1);
    const topo = H.y + H.perfil[Math.min(H.perfil.length - 1, Math.round(xl / 4))];
    const sobe = 0.5 + 0.5 * Math.sin(2 * Math.PI * (t * 2.3));
    const y = mistura(chao - 2, topo + 6, sobe * 0.85);
    const forca = Math.min(1, (frente + 0.02) * 10, (1.04 - frente) * 10);
    partes.push(
      <g key="ponta" opacity={forca}>
        <circle cx={H.x + xl} cy={y} r={8} fill={COR.estrela} opacity={0.14} />
        <circle cx={H.x + xl} cy={y} r={2.2} fill={COR.estrela} />
      </g>,
    );
  }
  // Brilho da água: traços curtos que vão e voltam, depois que a caneta passou.
  const aguas = [
    {x0: 150, x1: 262, y0: 968, y1: 985, n: 9},
    {x0: 958, x1: 1175, y0: 966, y1: 986, n: 14},
    {x0: 828, x1: 905, y0: 978, y1: 986, n: 5},
  ];
  const calma = 1 - prog(t, T.calmo - 0.8, T.calmo + 0.6);
  aguas.forEach((a, j) => {
    for (let k = 0; k < a.n; k++) {
      const s = j * 100 + k;
      const x = mistura(a.x0, a.x1, acaso(s, 3));
      const y = mistura(a.y0, a.y1, acaso(s, 5));
      const revelado = clamp01((frente - H.ordem_chao[Math.min(H.ordem_chao.length - 1, Math.round((x - H.x) / 4))]) * 10);
      if (revelado <= 0) continue;
      const fase = Math.sin(2 * Math.PI * (t * (0.35 + 0.3 * acaso(s, 8)) + acaso(s, 9)));
      const op = revelado * (0.22 + 0.2 * fase) * mistura(0.35, 1, calma);
      const l = 3 + 6 * acaso(s, 11);
      const dx = 2.5 * fase * calma;
      partes.push(
        <line key={`a${s}`} x1={x - l + dx} y1={y} x2={x + l + dx} y2={y} stroke={COR.creme} strokeWidth={0.8} strokeLinecap="round" opacity={op} />,
      );
    }
  });
  return <g>{partes}</g>;
};

export const revelado = (t: number, xFrame: number) => {
  const k = Math.max(0, Math.min(H.ordem_chao.length - 1, Math.round((xFrame - H.x) / 4)));
  return saida(clamp01((frenteHorizonte(t) - H.ordem_chao[k]) * 5));
};
