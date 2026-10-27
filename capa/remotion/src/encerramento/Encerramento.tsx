// Da zona eleitoral ao resultado: cada fragmento conserva votos de uma origem.
// Somente SVG. Sem imagens, bandeira, estrelas, horizonte, áudio ou acasos no tempo.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import dados from '../../public/dados/encerramento.json';
import roteiro from './roteiro.json';
import {progresso, suave, mistura, posicaoFragmento} from './geometria';

export const FPS_ENCERRAMENTO = roteiro.fps;
export const QUADROS_ENCERRAMENTO = roteiro.segundos * roteiro.fps;
export const COR = {tinta: '#1C1915', creme: '#E5DBC8', areia: '#CBBDA2', flavio: '#8FA8CF', lula: '#D9877B'};
const cor = (c: string) => c === 'lula' ? COR.lula : COR.flavio;

/** Função pura: o mesmo quadro produz o mesmo SVG, mesmo ao buscar para trás. */
export const DesenhoEncerramento: React.FC<{t: number}> = ({t: recebido}) => {
  const t = Math.min(recebido, roteiro.parado);
  const mapa = roteiro.mapa;
  const mapaOpacidade = 1 - suave(progresso(t, ...roteiro.someMapa as [number, number]));
  const desenha = suave(progresso(t, ...roteiro.contorno as [number, number]));
  const destaca = suave(progresso(t, ...roteiro.diferenca as [number, number]));
  const area = roteiro.areaGrafica;
  const pontos: React.ReactNode[] = [];
  const chegadas: React.ReactNode[] = [];

  if (t < roteiro.partidasDiferenca[1] + roteiro.vooDiferenca) {
    dados.fragmentos.forEach(([origemIndice, destinoIndice, votos], i) => {
      const origem = dados.origens[origemIndice];
      const lote = dados.lotes[destinoIndice];
      const entra = suave(progresso(t, 1.7, 2.5));
      const entrega = progresso(t, lote.partida + lote.duracao - 0.35, lote.partida + lote.duracao);
      if (entra === 0 || entrega === 1) return;
      const {x, y} = posicaoFragmento(origem, lote, t);
      pontos.push(<circle key={i} cx={x} cy={y} r={roteiro.hemiciclo.raioPonto * Math.sqrt(votos / dados.unidade)}
        fill={cor(lote.candidato)} opacity={0.76 * entra * (1 - entrega)} />);
    });
  }
  dados.lotes.forEach((lote, i) => {
    const entrega = suave(progresso(t, lote.partida + lote.duracao - 0.35, lote.partida + lote.duracao));
    if (entrega === 0) return;
    const opacidade = lote.diferenca ? mistura(0.82, 1, destaca) : mistura(0.82, 0.74, destaca);
    chegadas.push(<circle key={i} data-lote={i} cx={lote.x} cy={lote.y} r={lote.r}
      fill={cor(lote.candidato)} opacity={opacidade * entrega} />);
    // Os excedentes acendem na própria cor e ficam fixos, à esquerda do eixo.
    if (lote.diferenca && destaca > 0) {
      chegadas.push(<circle key={`d${i}`} data-diferenca={i} cx={lote.x} cy={lote.y} r={lote.r + 0.65}
        fill="none" stroke={cor(lote.candidato)} strokeWidth={0.7} opacity={0.65 * destaca} />);
    }
  });

  return <svg width={1920} height={1080} viewBox="0 0 1920 1080" aria-hidden="true">
    <rect width={1920} height={1080} fill={COR.tinta} />
    <defs><clipPath id="t23-area-livre"><rect x={area.x} y={area.y} width={area.largura} height={area.altura} /></clipPath></defs>
    <g clipPath="url(#t23-area-livre)">
    {mapaOpacidade > 0 && <g opacity={mapaOpacidade}>
      <g transform={`translate(${mapa.x} ${mapa.y}) scale(${mapa.escala}) translate(-960 -583)`}
        fill="none" stroke={COR.areia} strokeLinecap="round" strokeLinejoin="round">
        <path d={dados.contorno} strokeWidth={1.8} pathLength={1} strokeDasharray="1 2"
          strokeDashoffset={1 - desenha} opacity={0.65} />
        <g opacity={0.2 * suave(progresso(t, 0.9, 2.0))} strokeWidth={1}>
          {dados.divisas.map((d, i) => <path key={i} d={d} />)}
        </g>
      </g>
      {dados.origens.map((origem, i) => {
        const ordem = ((i * 37) % 5573) / 5572;
        const a = suave(progresso(t, roteiro.municipios[0] + ordem * 0.65, roteiro.municipios[1]));
        return <circle key={origem.id} cx={origem.x} cy={origem.y} r={origem.mapa ? 0.8 : 2.2}
          fill={COR.areia} opacity={0.5 * a} />;
      })}
    </g>}
    <g data-camada="fragmentos">{pontos}</g>
    <path data-eixo="comparacao" d="M960,194 Q959.6,335 960,480" fill="none" stroke={COR.areia}
      strokeWidth={0.85} strokeDasharray="3 5" opacity={0.48 * suave(progresso(t, 7.4, 8.0))} />
    <g data-camada="resultado">{chegadas}</g>
    </g>
  </svg>;
};

export const Encerramento: React.FC = () => <AbsoluteFill style={{backgroundColor: COR.tinta}}>
  <DesenhoEncerramento t={useCurrentFrame() / FPS_ENCERRAMENTO} />
</AbsoluteFill>;
