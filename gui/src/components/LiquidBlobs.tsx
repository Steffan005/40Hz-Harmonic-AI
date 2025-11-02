/**
 * LIQUID CONSCIOUSNESS BLOBS
 * Gesture-responsive morphing blobs that follow the user's consciousness
 * 2025 cutting-edge: Glassmorphism + Liquid + Gesture-responsive
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface BlobPosition {
  x: number;
  y: number;
  scale: number;
  rotation: number;
}

export function LiquidBlobs() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [blobs, setBlobs] = useState<BlobPosition[]>([
    { x: 20, y: 20, scale: 1, rotation: 0 },
    { x: 80, y: 30, scale: 1.2, rotation: 45 },
    { x: 50, y: 70, scale: 0.9, rotation: 90 },
    { x: 15, y: 60, scale: 1.1, rotation: 135 },
    { x: 75, y: 80, scale: 1, rotation: 180 }
  ]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Animate blobs to follow mouse subtly
  useEffect(() => {
    setBlobs(prev => prev.map((blob, i) => ({
      ...blob,
      x: blob.x + (mousePos.x - blob.x) * 0.01 * (i + 1),
      y: blob.y + (mousePos.y - blob.y) * 0.01 * (i + 1),
      rotation: blob.rotation + 0.1
    })));
  }, [mousePos]);

  return (
    <div className="liquid-blobs">
      {blobs.map((blob, i) => (
        <motion.div
          key={i}
          className="blob"
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: 0.15,
            scale: blob.scale,
            x: `${blob.x}vw`,
            y: `${blob.y}vh`,
            rotate: blob.rotation
          }}
          transition={{
            duration: 20 + i * 5,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
          style={{
            position: 'absolute',
            width: `${300 + i * 100}px`,
            height: `${300 + i * 100}px`,
            background: `radial-gradient(circle,
              ${i % 3 === 0 ? '#9B59B6' : i % 3 === 1 ? '#3498DB' : '#FFA500'},
              transparent 70%)`,
            filter: 'blur(80px)',
            borderRadius: '40% 60% 70% 30% / 40% 50% 60% 50%',
            pointerEvents: 'none',
            zIndex: 0
          }}
        />
      ))}
    </div>
  );
}
