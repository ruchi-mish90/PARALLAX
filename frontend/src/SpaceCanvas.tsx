import { Suspense, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const MOON_TEX =
  "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/moon_1024.jpg";

export function MoonSphere() {
  const ref = useRef<THREE.Mesh>(null!);
  const map = useTexture(MOON_TEX);

  useFrame((_, dt) => {
    if (ref.current) {
      ref.current.rotation.y += dt * 0.013;
    }
  });

  return (
    <mesh ref={ref} position={[0, 0, 0]}>
      <sphereGeometry args={[1.35, 64, 64]} />
      <meshStandardMaterial map={map} roughness={0.96} metalness={0.0} />
    </mesh>
  );
}

export interface SpaceCanvasProps {
  className?: string;
  style?: React.CSSProperties;
}

export default function MoonCanvas({
  className = "w-full h-full",
  style,
}: SpaceCanvasProps = {}) {
  return (
    <div className={className} style={{ width: "100%", height: "100%", minHeight: "100vh", ...style }}>
      <Canvas
        camera={{ position: [0, 0, 3.2], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
      >
        <color attach="background" args={["#030507"]} />
        <ambientLight intensity={0.02} />
        <directionalLight position={[45, 10, 25]} intensity={1.85} color="#fff8f0" />
        <Suspense fallback={null}>
          <MoonSphere />
        </Suspense>
      </Canvas>
    </div>
  );
}
