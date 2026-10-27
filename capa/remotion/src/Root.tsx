import React from 'react';
import {Composition} from 'remotion';
import {Capa} from './Capa';
import {FPS, QUADROS} from './tempo';
import {Encerramento, FPS_ENCERRAMENTO, QUADROS_ENCERRAMENTO} from './encerramento/Encerramento';

export const Root: React.FC = () => (
  <>
    <Composition id="Capa" component={Capa} durationInFrames={QUADROS} fps={FPS} width={1920} height={1080} />
    <Composition id="Encerramento" component={Encerramento} durationInFrames={QUADROS_ENCERRAMENTO}
      fps={FPS_ENCERRAMENTO} width={1920} height={1080} />
  </>
);
