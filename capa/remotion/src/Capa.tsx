// Capa animada · Eleições 2026 · o voto de perto (Vizu Dados).
// "O céu da bandeira vira o mapa do voto": as 27 estrelas da bandeira (uma por UF) desenham a bandeira,
// voam para os seus estados, o Brasil se desenha à volta delas, os 5.570 municípios mostram os dois turnos de 2026
// e o horizonte de Norte a Sul se desenha na base. Toca uma vez e para no quadro final.
// Zonas livres para o HTML por cima: título y 110–300 (x 300–1620), números x 140–560 e 1360–1780 (y 380–760),
// cabeçalho y 0–100, rodapé y 1000–1080, setas x 40–120 e 1800–1880 (y 510–570).
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Bandeira} from './Bandeira';
import {CeuDeFundo, CeuDoHorizonte} from './Ceu';
import {Estrelas} from './Estrelas';
import {Horizonte, HorizonteVivo} from './Horizonte';
import {Mapa} from './Mapa';
import {COR, FPS, T} from './tempo';

export const Capa: React.FC = () => {
  const t = Math.min(useCurrentFrame() / FPS, T.assenta);
  return (
    <AbsoluteFill style={{backgroundColor: COR.tinta}}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
        <CeuDeFundo t={t} />
        <Bandeira t={t} />
        <Mapa t={t} />
      </svg>
      <Horizonte t={t} />
      <CeuDoHorizonte t={t} />
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
        <HorizonteVivo t={t} />
        <Estrelas t={t} />
      </svg>
    </AbsoluteFill>
  );
};
