/**
 * MEMORY GRAPH COMPONENT
 * Visual representation of Unity's collective consciousness
 * Nodes represent memories, edges represent associations
 * Living, breathing network that evolves in real-time
 */

import React, { useRef, useEffect, useState } from 'react';
import { api } from '../lib/api';
import '../styles/memory-graph.css';

interface MemoryNode {
  id: string;
  office: string;
  content: string;
  timestamp: Date;
  ttl_hours: number;
  tags: string[];
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  radius?: number;
  color?: string;
}

interface MemoryEdge {
  source: string;
  target: string;
  relation: string;
  weight: number;
}

interface GraphData {
  nodes: MemoryNode[];
  edges: MemoryEdge[];
}

// Office color palette
const OFFICE_COLORS: Record<string, string> = {
  tarot: '#9B59B6',      // Purple
  astrology: '#3498DB',  // Blue
  physics: '#00FFFF',    // Cyan
  banker: '#FFA500',     // Orange
  chef: '#2ECC71',       // Green
  philosopher: '#E74C3C', // Red
  default: '#95A5A6'     // Grey
};

export function MemoryGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [hoveredNode, setHoveredNode] = useState<MemoryNode | null>(null);
  const [selectedOffice, setSelectedOffice] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(true);

  // Force simulation parameters
  const FORCE_CONFIG = {
    centerForce: 0.02,
    chargeForce: -300,
    linkDistance: 100,
    linkStrength: 0.1,
    velocityDecay: 0.9,
    alphaTarget: 0.001
  };

  // Initialize graph with sample data
  useEffect(() => {
    loadMemoryGraph();
    const interval = setInterval(loadMemoryGraph, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadMemoryGraph = async () => {
    try {
      // TODO: Replace with actual API call when available
      // const response = await api.getMemoryGraph();

      // For now, create sample data
      const sampleData: GraphData = {
        nodes: [
          { id: '1', office: 'tarot', content: 'Three of Cups reading', timestamp: new Date(), ttl_hours: 24, tags: ['divination'] },
          { id: '2', office: 'astrology', content: 'Mercury retrograde analysis', timestamp: new Date(), ttl_hours: 48, tags: ['planets'] },
          { id: '3', office: 'physics', content: 'Quantum entanglement study', timestamp: new Date(), ttl_hours: 72, tags: ['quantum'] },
          { id: '4', office: 'banker', content: 'Portfolio optimization', timestamp: new Date(), ttl_hours: 24, tags: ['finance'] },
          { id: '5', office: 'chef', content: 'Molecular gastronomy recipe', timestamp: new Date(), ttl_hours: 12, tags: ['cooking'] },
          { id: '6', office: 'philosopher', content: 'Consciousness emergence theory', timestamp: new Date(), ttl_hours: 168, tags: ['metaphysics'] },
          { id: '7', office: 'tarot', content: 'Celtic Cross spread', timestamp: new Date(), ttl_hours: 24, tags: ['divination'] },
          { id: '8', office: 'astrology', content: 'Natal chart interpretation', timestamp: new Date(), ttl_hours: 48, tags: ['birth'] },
          { id: '9', office: 'physics', content: 'Wave function collapse', timestamp: new Date(), ttl_hours: 72, tags: ['quantum'] },
          { id: '10', office: 'philosopher', content: 'Unity of consciousness', timestamp: new Date(), ttl_hours: 168, tags: ['unity'] }
        ],
        edges: [
          { source: '1', target: '2', relation: 'synchronicity', weight: 0.8 },
          { source: '2', target: '3', relation: 'cosmic_influence', weight: 0.6 },
          { source: '3', target: '6', relation: 'theory', weight: 0.9 },
          { source: '4', target: '5', relation: 'investment', weight: 0.4 },
          { source: '6', target: '10', relation: 'concept', weight: 1.0 },
          { source: '1', target: '7', relation: 'same_office', weight: 0.7 },
          { source: '2', target: '8', relation: 'same_office', weight: 0.7 },
          { source: '3', target: '9', relation: 'same_office', weight: 0.7 },
          { source: '9', target: '10', relation: 'emergence', weight: 0.8 }
        ]
      };

      // Initialize node positions and physics
      const canvas = canvasRef.current;
      if (canvas) {
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;

        sampleData.nodes = sampleData.nodes.map((node, i) => ({
          ...node,
          x: node.x || centerX + (Math.random() - 0.5) * 400,
          y: node.y || centerY + (Math.random() - 0.5) * 400,
          vx: 0,
          vy: 0,
          radius: 10 + node.tags.length * 2,
          color: OFFICE_COLORS[node.office] || OFFICE_COLORS.default
        }));
      }

      setGraphData(sampleData);
    } catch (error) {
      console.error('Failed to load memory graph:', error);
    }
  };

  // Force simulation
  useEffect(() => {
    if (!isSimulating || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const simulate = () => {
      const { nodes, edges } = graphData;
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      // Apply forces to nodes
      nodes.forEach(node => {
        if (!node.x || !node.y) return;

        // Center force
        node.vx = (node.vx || 0) + (centerX - node.x) * FORCE_CONFIG.centerForce;
        node.vy = (node.vy || 0) + (centerY - node.y) * FORCE_CONFIG.centerForce;

        // Repulsion between nodes
        nodes.forEach(other => {
          if (node.id === other.id || !node.x || !node.y || !other.x || !other.y) return;

          const dx = node.x - other.x;
          const dy = node.y - other.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = FORCE_CONFIG.chargeForce / (distance * distance);

          node.vx! += (dx / distance) * force;
          node.vy! += (dy / distance) * force;
        });
      });

      // Apply edge constraints
      edges.forEach(edge => {
        const source = nodes.find(n => n.id === edge.source);
        const target = nodes.find(n => n.id === edge.target);

        if (source?.x && source?.y && target?.x && target?.y) {
          const dx = target.x - source.x;
          const dy = target.y - source.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (distance - FORCE_CONFIG.linkDistance) * FORCE_CONFIG.linkStrength * edge.weight;

          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;

          source.vx = (source.vx || 0) + fx;
          source.vy = (source.vy || 0) + fy;
          target.vx = (target.vx || 0) - fx;
          target.vy = (target.vy || 0) - fy;
        }
      });

      // Update positions
      nodes.forEach(node => {
        if (!node.x || !node.y) return;

        // Apply velocity decay
        node.vx = (node.vx || 0) * FORCE_CONFIG.velocityDecay;
        node.vy = (node.vy || 0) * FORCE_CONFIG.velocityDecay;

        // Update position
        node.x += node.vx || 0;
        node.y += node.vy || 0;

        // Keep within bounds
        const margin = node.radius || 10;
        node.x = Math.max(margin, Math.min(canvas.width - margin, node.x));
        node.y = Math.max(margin, Math.min(canvas.height - margin, node.y));
      });

      render();
      animationRef.current = requestAnimationFrame(simulate);
    };

    const render = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw edges
      graphData.edges.forEach(edge => {
        const source = graphData.nodes.find(n => n.id === edge.source);
        const target = graphData.nodes.find(n => n.id === edge.target);

        if (source?.x && source?.y && target?.x && target?.y) {
          ctx.beginPath();
          ctx.moveTo(source.x, source.y);
          ctx.lineTo(target.x, target.y);

          // Edge style based on relation
          ctx.strokeStyle = `rgba(155, 89, 182, ${0.2 + edge.weight * 0.3})`;
          ctx.lineWidth = 1 + edge.weight * 2;

          // Glow effect for strong connections
          if (edge.weight > 0.7) {
            ctx.shadowBlur = 10;
            ctx.shadowColor = 'rgba(155, 89, 182, 0.5)';
          }

          ctx.stroke();
          ctx.shadowBlur = 0;
        }
      });

      // Draw nodes
      graphData.nodes.forEach(node => {
        if (!node.x || !node.y) return;

        const radius = node.radius || 10;
        const isHighlighted = selectedOffice === null || node.office === selectedOffice;
        const isHovered = hoveredNode?.id === node.id;

        // Node glow
        if (isHovered || isHighlighted) {
          ctx.beginPath();
          ctx.arc(node.x, node.y, radius * 2, 0, Math.PI * 2);
          const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, radius * 2);
          gradient.addColorStop(0, `${node.color}40`);
          gradient.addColorStop(1, 'transparent');
          ctx.fillStyle = gradient;
          ctx.fill();
        }

        // Node circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = isHighlighted ? node.color! : `${node.color}60`;
        ctx.strokeStyle = node.color!;
        ctx.lineWidth = isHovered ? 3 : 2;
        ctx.fill();
        ctx.stroke();

        // Breathing animation
        if (isHighlighted) {
          const breathScale = 1 + Math.sin(Date.now() * 0.001) * 0.05;
          ctx.save();
          ctx.translate(node.x, node.y);
          ctx.scale(breathScale, breathScale);
          ctx.beginPath();
          ctx.arc(0, 0, radius, 0, Math.PI * 2);
          ctx.strokeStyle = `${node.color}80`;
          ctx.lineWidth = 1;
          ctx.stroke();
          ctx.restore();
        }

        // Office icon (simplified)
        if (isHovered) {
          ctx.fillStyle = 'white';
          ctx.font = '10px JetBrains Mono';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(node.office[0].toUpperCase(), node.x, node.y);
        }
      });

      // Draw hover info
      if (hoveredNode && hoveredNode.x && hoveredNode.y) {
        const padding = 10;
        const boxWidth = 200;
        const boxHeight = 80;
        const x = hoveredNode.x + 20;
        const y = hoveredNode.y - boxHeight / 2;

        // Info box background
        ctx.fillStyle = 'rgba(26, 30, 58, 0.95)';
        ctx.strokeStyle = hoveredNode.color!;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(x, y, boxWidth, boxHeight, 8);
        ctx.fill();
        ctx.stroke();

        // Info text
        ctx.fillStyle = 'white';
        ctx.font = '12px JetBrains Mono';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';

        ctx.fillText(`Office: ${hoveredNode.office}`, x + padding, y + padding);
        ctx.font = '10px JetBrains Mono';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';

        // Truncate content
        const content = hoveredNode.content.length > 30
          ? hoveredNode.content.slice(0, 30) + '...'
          : hoveredNode.content;
        ctx.fillText(content, x + padding, y + padding + 20);

        // Tags
        ctx.fillStyle = hoveredNode.color!;
        ctx.fillText(`Tags: ${hoveredNode.tags.join(', ')}`, x + padding, y + padding + 35);

        // TTL
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.fillText(`TTL: ${hoveredNode.ttl_hours}h`, x + padding, y + padding + 50);
      }
    };

    simulate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [graphData, hoveredNode, selectedOffice, isSimulating]);

  // Handle canvas resize
  useEffect(() => {
    const handleResize = () => {
      if (canvasRef.current) {
        canvasRef.current.width = canvasRef.current.offsetWidth;
        canvasRef.current.height = canvasRef.current.offsetHeight;
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Mouse interaction
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Find node under cursor
    const node = graphData.nodes.find(n => {
      if (!n.x || !n.y) return false;
      const dx = x - n.x;
      const dy = y - n.y;
      return Math.sqrt(dx * dx + dy * dy) < (n.radius || 10);
    });

    setHoveredNode(node || null);
  };

  // Get unique offices
  const offices = Array.from(new Set(graphData.nodes.map(n => n.office)));

  return (
    <div className="memory-graph">
      <div className="graph-header">
        <div className="graph-title">
          <span className="quantum-indicator">🧠</span>
          Memory Graph
          <span className="node-count">{graphData.nodes.length} nodes</span>
        </div>

        <div className="graph-controls">
          <button
            className={`control-button ${isSimulating ? 'active' : ''}`}
            onClick={() => setIsSimulating(!isSimulating)}
          >
            {isSimulating ? '⏸ Pause' : '▶ Simulate'}
          </button>

          <div className="office-filters">
            <button
              className={`filter-chip ${!selectedOffice ? 'active' : ''}`}
              onClick={() => setSelectedOffice(null)}
            >
              All
            </button>
            {offices.map(office => (
              <button
                key={office}
                className={`filter-chip ${selectedOffice === office ? 'active' : ''}`}
                style={{
                  borderColor: selectedOffice === office ? OFFICE_COLORS[office] : undefined,
                  color: selectedOffice === office ? OFFICE_COLORS[office] : undefined
                }}
                onClick={() => setSelectedOffice(office)}
              >
                {office}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="graph-canvas-container">
        <canvas
          ref={canvasRef}
          className="graph-canvas"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoveredNode(null)}
        />
      </div>

      <div className="graph-footer">
        <div className="graph-stats">
          <div className="stat">
            <span className="stat-value">{graphData.edges.length}</span>
            <span className="stat-label">Connections</span>
          </div>
          <div className="stat">
            <span className="stat-value">{offices.length}</span>
            <span className="stat-label">Offices</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {Math.round(graphData.edges.reduce((sum, e) => sum + e.weight, 0) / graphData.edges.length * 100)}%
            </span>
            <span className="stat-label">Avg Strength</span>
          </div>
        </div>
      </div>
    </div>
  );
}