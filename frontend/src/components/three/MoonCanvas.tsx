import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { MoonSphere } from './MoonSphere';
import { SpaceParticles } from './SpaceParticles';
import { LunarRegion } from '../../types/regions';

interface MoonCanvasProps {
  onSelectRegion?: (region: LunarRegion) => void;
  className?: string;
  interactive?: boolean;
}

export const MoonCanvas: React.FC<MoonCanvasProps> = ({ 
  onSelectRegion, 
  className = 'h-[500px] w-full',
  interactive = true 
}) => {
  return (
    <div className={`relative ${className}`}>
      <Canvas
        camera={{ position: [0, 1.2, 5.8], fov: 42 }}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        dpr={[1, 2]}
      >
        {/* Soft deep space ambient light */}
        <ambientLight intensity={0.12} color="#8E95A5" />

        {/* Primary Sun directional light creating grazing terminator shadow */}
        <directionalLight
          position={[6, 2.5, 4]}
          intensity={2.8}
          color="#FFF8E7"
        />

        {/* Secondary subtle earthshine bounce */}
        <directionalLight
          position={[-5, -2, -3]}
          intensity={0.25}
          color="#64D2FF"
        />

        <Suspense fallback={null}>
          <SpaceParticles count={500} />
          <MoonSphere onSelectRegion={onSelectRegion} />
        </Suspense>

        {interactive && (
          <OrbitControls
            enablePan={false}
            enableZoom={true}
            minDistance={3.8}
            maxDistance={8.5}
            rotateSpeed={0.5}
            dampingFactor={0.05}
          />
        )}
      </Canvas>
    </div>
  );
};
