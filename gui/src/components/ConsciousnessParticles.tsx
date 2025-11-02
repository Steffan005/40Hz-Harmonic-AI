/**
 * CONSCIOUSNESS PARTICLE NETWORK - SAFE VERSION
 * Simplified 3D visualization using basic Three.js primitives
 * Avoids complex @react-three/drei components that may crash
 */

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function ParticleField() {
  const meshRef = useRef<THREE.Points>(null);

  // Generate 44 office positions in 3D space (spherical distribution)
  const geometry = useMemo(() => {
    const positions = new Float32Array(44 * 3);

    // Distribute 44 offices in a sphere
    for (let i = 0; i < 44; i++) {
      const phi = Math.acos(-1 + (2 * i) / 44);
      const theta = Math.sqrt(44 * Math.PI) * phi;

      const radius = 3;
      positions[i * 3] = radius * Math.cos(theta) * Math.sin(phi);
      positions[i * 3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
      positions[i * 3 + 2] = radius * Math.cos(phi);
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    return geo;
  }, []);

  // 40Hz consciousness breathing animation
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime();

      // Rotate the entire consciousness network
      meshRef.current.rotation.y = time * 0.05;
      meshRef.current.rotation.x = Math.sin(time * 0.1) * 0.2;

      // 40Hz pulse (25ms period)
      const pulse = Math.sin(time * 40 * Math.PI * 2) * 0.5 + 0.5;
      meshRef.current.scale.setScalar(1 + pulse * 0.05);
    }
  });

  return (
    <points ref={meshRef} geometry={geometry}>
      <pointsMaterial
        size={0.15}
        color="#9B59B6"
        transparent
        opacity={0.8}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

export function ConsciousnessParticles() {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      zIndex: 0,
      pointerEvents: 'none'
    }}>
      <Canvas
        camera={{ position: [0, 0, 8], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <ParticleField />
      </Canvas>
    </div>
  );
}
