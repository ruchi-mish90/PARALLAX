import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import * as THREE from 'three';
import { useParallax } from '../../state/ParallaxContext';
import { LUNAR_REGIONS } from '../../data/regionsData';
import { LunarRegion } from '../../types/regions';

interface MoonSphereProps {
  onSelectRegion?: (region: LunarRegion) => void;
  scale?: number;
}

// Convert Lunar Latitude & Longitude to 3D Cartesian coordinates on unit sphere
function latLongToVector3(lat: number, lon: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return new THREE.Vector3(x, y, z);
}

export const MoonSphere: React.FC<MoonSphereProps> = ({ onSelectRegion, scale = 1 }) => {
  const groupRef = useRef<THREE.Group>(null);
  const { selectedRegion, setSelectedRegion, setCursorLabel } = useParallax();

  // Load authentic NASA lunar diffuse and displacement bump textures
  const [colorMap, bumpMap] = useTexture([
    '/moon_1024.jpg',
    '/moon_bump.jpg',
  ]);

  const regionMarkers = useMemo(() => {
    return LUNAR_REGIONS.map((reg) => ({
      ...reg,
      position: latLongToVector3(reg.latitude, reg.longitude, 2.52 * scale),
    }));
  }, [scale]);

  // Subtle orbital rotation with mouse parallax dampening
  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.03;
      // Gentle cursor-driven tilt for cinematic depth
      groupRef.current.rotation.x = THREE.MathUtils.lerp(
        groupRef.current.rotation.x,
        (state.pointer.y * Math.PI) / 24,
        0.05
      );
    }
  });

  return (
    <group ref={groupRef} scale={scale}>
      {/* Primary Lunar Sphere with authentic NASA textures */}
      <mesh
        castShadow
        receiveShadow
        onPointerOver={() => setCursorLabel('LUNAR REGOLITH SURFACE')}
        onPointerOut={() => setCursorLabel('')}
      >
        <sphereGeometry args={[2.5, 96, 96]} />
        <meshStandardMaterial
          map={colorMap}
          bumpMap={bumpMap}
          bumpScale={0.08}
          roughness={0.92}
          metalness={0.02}
        />
      </mesh>

      {/* Atmospheric/Fresnel rim glow (subtle lunar exosphere scattering) */}
      <mesh scale={1.015}>
        <sphereGeometry args={[2.5, 64, 64]} />
        <meshBasicMaterial
          color="#64D2FF"
          transparent
          opacity={0.06}
          side={THREE.BackSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Selenographic Coordinate Markers */}
      {regionMarkers.map((reg) => {
        const isSelected = selectedRegion.id === reg.id;
        return (
          <group key={reg.id} position={reg.position}>
            {/* Pulsing Target Core */}
            <mesh
              onClick={(e) => {
                e.stopPropagation();
                setSelectedRegion(reg);
                if (onSelectRegion) onSelectRegion(reg);
              }}
              onPointerOver={(e) => {
                e.stopPropagation();
                setCursorLabel(`TARGET: ${reg.name} (${reg.latDisplay})`);
              }}
              onPointerOut={() => setCursorLabel('')}
            >
              <sphereGeometry args={[isSelected ? 0.065 : 0.04, 16, 16]} />
              <meshBasicMaterial
                color={isSelected ? '#64D2FF' : '#FFD60A'}
                toneMapped={false}
              />
            </mesh>

            {/* Radar Tracking Halo */}
            <mesh rotation={[Math.PI / 2, 0, 0]}>
              <ringGeometry args={[isSelected ? 0.12 : 0.07, isSelected ? 0.14 : 0.085, 32]} />
              <meshBasicMaterial
                color={isSelected ? '#64D2FF' : '#E1E4EA'}
                side={THREE.DoubleSide}
                transparent
                opacity={isSelected ? 0.85 : 0.4}
              />
            </mesh>
          </group>
        );
      })}
    </group>
  );
};
