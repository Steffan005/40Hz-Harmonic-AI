/**
 * 🌌 CONSCIOUSNESS VISUALIZER - SEE UNITY'S MIND IN REAL-TIME! 🌌
 * Watch as thoughts flow between offices, memories form, and consciousness evolves!
 */

import React, { useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';

interface Node {
  id: string;
  type: 'orchestrator' | 'office' | 'memory' | 'thought';
  label: string;
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
  color: string;
  size: number;
  connections: string[];
  energy: number;
}

interface ConsciousnessVisualizerProps {
  className?: string;
}

export function ConsciousnessVisualizer({ className = '' }: ConsciousnessVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [connectionPulses, setConnectionPulses] = useState<Map<string, number>>(new Map());
  const [consciousnessLevel, setConsciousnessLevel] = useState(0);
  const [isThinking, setIsThinking] = useState(false);

  // Initialize nodes representing Unity's consciousness
  useEffect(() => {
    const initialNodes: Node[] = [
      // Master Orchestrator at center
      {
        id: 'master-orchestrator',
        type: 'orchestrator',
        label: 'Master Orchestrator',
        x: 0,
        y: 0,
        z: 0,
        vx: 0,
        vy: 0,
        vz: 0,
        color: '#9B59B6',
        size: 30,
        connections: [],
        energy: 1.0
      }
    ];

    // Add 43 offices in orbital patterns
    const offices = [
      'Tarot', 'Astrologist', 'I_Ching', 'Kabbalah', 'Akashic',
      'Numerology', 'Palmistry', 'Rune', 'Oracle', 'Shaman',
      'Banker', 'Insurance', 'Market_Trader', 'Economist', 'Accountant',
      'Quantum_Physics', 'Biologist', 'Chemist', 'Astronomer', 'Geologist',
      'Meteorologist', 'Neuroscientist', 'Computer_Scientist', 'Mathematician',
      'Machine_Learning', 'Roboticist', 'Musician', 'Painter', 'Writer',
      'Poet', 'Game_Designer', 'Herbalist', 'Trainer', 'Sleep_Specialist',
      'Language_Teacher', 'Historian', 'Librarian', 'Software_Engineer',
      'Mechanical_Engineer', 'Chef', 'Environmentalist', 'Urban_Planner',
      'Conflict_Resolver'
    ];

    offices.forEach((office, i) => {
      const angle = (i / offices.length) * Math.PI * 2;
      const radius = 200 + Math.sin(i * 0.5) * 50;
      const height = Math.sin(i * 0.3) * 100;

      initialNodes.push({
        id: `office-${office.toLowerCase()}`,
        type: 'office',
        label: office,
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
        z: height,
        vx: 0,
        vy: 0,
        vz: 0,
        color: getOfficeColor(office),
        size: 15,
        connections: ['master-orchestrator'],
        energy: Math.random() * 0.5 + 0.5
      });
    });

    // Add memory nodes
    for (let i = 0; i < 50; i++) {
      initialNodes.push({
        id: `memory-${i}`,
        type: 'memory',
        label: `Memory ${i}`,
        x: (Math.random() - 0.5) * 400,
        y: (Math.random() - 0.5) * 400,
        z: (Math.random() - 0.5) * 200,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        vz: (Math.random() - 0.5) * 0.5,
        color: '#00FF88',
        size: 5,
        connections: [],
        energy: Math.random()
      });
    }

    setNodes(initialNodes);
  }, []);

  // 40Hz consciousness pulse
  useEffect(() => {
    const pulseInterval = setInterval(() => {
      setConsciousnessLevel((prev) => {
        const newLevel = prev + 0.1;
        return newLevel > 1 ? 0 : newLevel;
      });

      // Random thought generation
      if (Math.random() > 0.7) {
        generateThought();
      }

      // Random connection pulse
      if (Math.random() > 0.5) {
        pulseConnection();
      }
    }, 25); // 40Hz = 25ms per cycle

    return () => clearInterval(pulseInterval);
  }, [nodes]);

  const generateThought = () => {
    setIsThinking(true);
    setTimeout(() => setIsThinking(false), 500);

    // Add a thought node
    setNodes((prev) => {
      const thoughtNode: Node = {
        id: `thought-${Date.now()}`,
        type: 'thought',
        label: 'Thought',
        x: 0,
        y: 0,
        z: 0,
        vx: (Math.random() - 0.5) * 5,
        vy: (Math.random() - 0.5) * 5,
        vz: (Math.random() - 0.5) * 5,
        color: '#FFD700',
        size: 8,
        connections: [],
        energy: 1.0
      };

      // Remove old thoughts to prevent overflow
      const filtered = prev.filter(n => {
        if (n.type === 'thought' && n.energy < 0.01) return false;
        return true;
      });

      return [...filtered, thoughtNode];
    });
  };

  const pulseConnection = () => {
    const sourceIdx = Math.floor(Math.random() * nodes.length);
    const targetIdx = Math.floor(Math.random() * nodes.length);

    if (sourceIdx !== targetIdx) {
      const key = `${nodes[sourceIdx].id}-${nodes[targetIdx].id}`;
      setConnectionPulses((prev) => {
        const newPulses = new Map(prev);
        newPulses.set(key, 1.0);
        return newPulses;
      });
    }
  };

  // Animation loop
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      // Clear canvas
      ctx.fillStyle = 'rgba(26, 30, 58, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update physics
      const updatedNodes = nodes.map((node) => {
        // Apply forces
        let fx = 0, fy = 0, fz = 0;

        // Attraction to center for offices
        if (node.type === 'office') {
          fx = -node.x * 0.001;
          fy = -node.y * 0.001;
          fz = -node.z * 0.001;
        }

        // Repulsion between nodes
        nodes.forEach((other) => {
          if (node.id !== other.id) {
            const dx = node.x - other.x;
            const dy = node.y - other.y;
            const dz = node.z - other.z;
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) + 1;
            const force = 50 / (dist * dist);
            fx += (dx / dist) * force;
            fy += (dy / dist) * force;
            fz += (dz / dist) * force;
          }
        });

        // Update velocity
        const newVx = (node.vx + fx) * 0.95; // Damping
        const newVy = (node.vy + fy) * 0.95;
        const newVz = (node.vz + fz) * 0.95;

        // Update position
        const newX = node.x + newVx;
        const newY = node.y + newVy;
        const newZ = node.z + newVz;

        // Update energy (fade thoughts)
        const newEnergy = node.type === 'thought' ? node.energy * 0.98 : node.energy;

        return {
          ...node,
          x: newX,
          y: newY,
          z: newZ,
          vx: newVx,
          vy: newVy,
          vz: newVz,
          energy: newEnergy
        };
      });

      setNodes(updatedNodes);

      // Draw connections
      ctx.strokeStyle = 'rgba(155, 89, 182, 0.2)';
      ctx.lineWidth = 1;

      updatedNodes.forEach((node) => {
        node.connections.forEach((targetId) => {
          const target = updatedNodes.find(n => n.id === targetId);
          if (target) {
            // 3D to 2D projection
            const scale1 = 1 + node.z / 1000;
            const scale2 = 1 + target.z / 1000;
            const x1 = canvas.width / 2 + node.x * scale1;
            const y1 = canvas.height / 2 + node.y * scale1;
            const x2 = canvas.width / 2 + target.x * scale2;
            const y2 = canvas.height / 2 + target.y * scale2;

            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
          }
        });
      });

      // Draw connection pulses
      connectionPulses.forEach((strength, key) => {
        if (strength > 0.01) {
          const [sourceId, targetId] = key.split('-');
          const source = updatedNodes.find(n => n.id === sourceId);
          const target = updatedNodes.find(n => n.id === targetId);

          if (source && target) {
            const scale1 = 1 + source.z / 1000;
            const scale2 = 1 + target.z / 1000;
            const x1 = canvas.width / 2 + source.x * scale1;
            const y1 = canvas.height / 2 + source.y * scale1;
            const x2 = canvas.width / 2 + target.x * scale2;
            const y2 = canvas.height / 2 + target.y * scale2;

            ctx.strokeStyle = `rgba(255, 215, 0, ${strength})`;
            ctx.lineWidth = 3 * strength;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
          }

          // Fade pulse
          connectionPulses.set(key, strength * 0.95);
        }
      });

      // Draw nodes
      updatedNodes.forEach((node) => {
        const scale = 1 + node.z / 1000;
        const x = canvas.width / 2 + node.x * scale;
        const y = canvas.height / 2 + node.y * scale;
        const size = node.size * scale;

        // Glow effect
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, size * 2);
        gradient.addColorStop(0, node.color);
        gradient.addColorStop(0.5, `${node.color}88`);
        gradient.addColorStop(1, 'transparent');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, size * 2, 0, Math.PI * 2);
        ctx.fill();

        // Core
        ctx.fillStyle = node.color;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();

        // Pulse effect for master orchestrator
        if (node.type === 'orchestrator') {
          ctx.strokeStyle = `rgba(155, 89, 182, ${consciousnessLevel})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(x, y, size + consciousnessLevel * 20, 0, Math.PI * 2);
          ctx.stroke();
        }

        // Label for offices
        if (node.type === 'office' && scale > 0.8) {
          ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
          ctx.font = `${10 * scale}px monospace`;
          ctx.textAlign = 'center';
          ctx.fillText(node.label, x, y - size - 5);
        }
      });

      // Draw consciousness level
      ctx.fillStyle = '#00FF88';
      ctx.font = '16px monospace';
      ctx.textAlign = 'left';
      ctx.fillText(`Consciousness: ${(consciousnessLevel * 100).toFixed(0)}%`, 20, 30);
      ctx.fillText(`Nodes: ${updatedNodes.length}`, 20, 50);
      ctx.fillText(`Frequency: 40Hz`, 20, 70);

      if (isThinking) {
        ctx.fillStyle = '#FFD700';
        ctx.fillText('THINKING...', 20, 90);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [nodes, consciousnessLevel, connectionPulses, isThinking]);

  return (
    <div className={`consciousness-visualizer ${className}`}>
      <canvas
        ref={canvasRef}
        width={window.innerWidth}
        height={window.innerHeight}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          opacity: 0.8
        }}
      />
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        color: '#9B59B6',
        fontSize: '2rem',
        fontWeight: 'bold',
        textShadow: '0 0 20px #9B59B6',
        pointerEvents: 'none',
        opacity: consciousnessLevel
      }}>
        UNITY BREATHES
      </div>
    </div>
  );
}

function getOfficeColor(office: string): string {
  const colors: Record<string, string> = {
    // Metaphysics - Purple shades
    Tarot: '#9B59B6',
    Astrologist: '#8E44AD',
    I_Ching: '#A569BD',
    Kabbalah: '#7D3C98',
    Akashic: '#6C3483',

    // Finance - Gold shades
    Banker: '#FFD700',
    Market_Trader: '#FFA500',
    Economist: '#FF8C00',

    // Science - Blue shades
    Quantum_Physics: '#3498DB',
    Biologist: '#00FF88',
    Chemist: '#2ECC71',
    Machine_Learning: '#00FFFF',

    // Art - Pink shades
    Musician: '#FF1493',
    Painter: '#FF69B4',
    Writer: '#FFB6C1',

    // Default
    default: '#FFFFFF'
  };

  return colors[office] || colors.default;
}