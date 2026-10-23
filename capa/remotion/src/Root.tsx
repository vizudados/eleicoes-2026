import React from 'react';
import {Composition} from 'remotion';
import {Capa} from './Capa';
import {FPS, QUADROS} from './tempo';

export const Root: React.FC = () => (
  <Composition id="Capa" component={Capa} durationInFrames={QUADROS} fps={FPS} width={1920} height={1080} />
);
