// Da zona eleitoral ao resultado. Somente desenho em SVG, sem texto ou imagens.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import dados from '../../public/dados/encerramento.json';
import roteiro from './roteiro.json';
import {circulosNoTempo, opacidadeMapa, opacidadeFio, progresso, suave} from './geometria';

export const FPS_ENCERRAMENTO = roteiro.fps;
export const QUADROS_ENCERRAMENTO = roteiro.segundos * roteiro.fps;
export const COR = {tinta: '#1C1915', areia: '#CBBDA2', flavio: '#8FA8CF', lula: '#D9877B'};
const cor = (c?: string) => c === 'lula' ? COR.lula : c === 'flavio' ? COR.flavio : COR.areia;

/** Mesmo tempo e mesmos dados produzem o mesmo quadro, inclusive ao buscar para trás. */
export const DesenhoEncerramento: React.FC<{t: number}> = ({t: recebido}) => {
  const t = Math.min(recebido, roteiro.parado);
  const mapa = roteiro.mapa;
  const opacidade = opacidadeMapa(t);
  const desenha = suave(progresso(t, roteiro.contorno[0], roteiro.contorno[1]));
  return <svg width={1920} height={1080} viewBox="0 0 1920 1080" aria-hidden="true">
    <rect width={1920} height={1080} fill={COR.tinta} />
    {opacidade > 0 && <g opacity={opacidade}
      transform={'translate(' + mapa.x + ' ' + mapa.y + ') scale(' + mapa.escala + ') translate(-960 -583)'}
      fill="none" stroke={COR.areia} strokeLinecap="round" strokeLinejoin="round">
      <path d={dados.contorno} strokeWidth={1.5} pathLength={1} strokeDasharray="1 2"
        strokeDashoffset={1 - desenha} opacity={0.65} />
      {dados.ilhas.map((d, i) => <path key={i} d={d} strokeWidth={1.1} opacity={0.6 * desenha} />)}
      <g opacity={0.2 * suave(progresso(t, 0.9, 2.0))} strokeWidth={0.8}>
        {dados.divisas.map((d, i) => <path key={i} d={d} />)}
      </g>
    </g>}
    <path data-fio="exterior" d="M1920,650 C1720,650 1480,590 1290,440" fill="none"
      stroke={COR.areia} strokeWidth={0.8} opacity={opacidadeFio(t)} />
    <path data-eixo="50-por-cento" d="M960,183 L960,470" fill="none" stroke={COR.areia}
      strokeWidth={0.85} strokeDasharray="3 5" opacity={0.48 * suave(progresso(t, 7.4, 8.0))} />
    <g data-camada="pontos">{Array.from(circulosNoTempo(t), (p) =>
      <circle key={p.classe + p.id} cx={p.x} cy={p.y} r={p.r} opacity={p.opacidade}
        fill={p.traco ? 'none' : cor(p.candidato)} stroke={p.traco ? cor(p.candidato) : undefined} strokeWidth={p.traco}
        data-origem={p.classe === 'municipio' ? p.id : undefined}
        data-fragmento={p.classe === 'fragmento' ? p.id : undefined}
        data-lote={p.classe === 'lote' ? p.id : undefined}
        data-diferenca={p.classe === 'diferenca' ? p.id : undefined} />
    )}</g>
  </svg>;
};

export const Encerramento: React.FC = () => <AbsoluteFill style={{backgroundColor: COR.tinta}}>
  <DesenhoEncerramento t={useCurrentFrame() / FPS_ENCERRAMENTO} />
</AbsoluteFill>;
