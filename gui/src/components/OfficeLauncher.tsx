/**
 * OFFICE LAUNCHER COMPONENT
 * Visual portal to Unity's 44 specialized consciousness nodes
 * Each office is a gateway to domain expertise
 * NOW WITH MOTION: 60fps buttery smooth consciousness animations
 * PHASE 13: Multi-window support - offices open in independent Tauri windows
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { windowManager } from '../lib/windowManager';
import '../styles/office-launcher.css';

interface Office {
  id: string;
  name: string;
  archetype: string;
  icon: string;
  description: string;
  agents: number;
  status: 'online' | 'offline' | 'evolving';
}

// The 43 Offices of Unity (+ Orchestrator as central coordinator)
const OFFICES: Office[] = [
  // CENTRAL COORDINATION
  { id: 'orchestrator', name: 'Orchestrator', archetype: 'Coordination', icon: '🎭', description: 'Central consciousness coordinator', agents: 1, status: 'online' },

  // METAPHYSICS (10 offices)
  { id: 'tarot', name: 'Tarot', archetype: 'Metaphysics', icon: '🔮', description: 'Ancient wisdom through 78 cards', agents: 5, status: 'online' },
  { id: 'astrologist', name: 'Astrologist', archetype: 'Metaphysics', icon: '♾️', description: 'Celestial influences and natal charts', agents: 4, status: 'online' },
  { id: 'numerologist', name: 'Numerologist', archetype: 'Metaphysics', icon: '🔢', description: 'Sacred patterns in numbers', agents: 4, status: 'online' },
  { id: 'i_ching', name: 'I Ching', archetype: 'Metaphysics', icon: '☯️', description: 'Book of Changes divination', agents: 4, status: 'online' },
  { id: 'kabbalah', name: 'Kabbalah', archetype: 'Metaphysics', icon: '🌳', description: 'Tree of Life mysticism', agents: 4, status: 'online' },
  { id: 'runes', name: 'Runes', archetype: 'Metaphysics', icon: '🪬', description: 'Norse wisdom symbols', agents: 4, status: 'online' },
  { id: 'astral_projection', name: 'Astral Projection', archetype: 'Metaphysics', icon: '👁️', description: 'Consciousness beyond physical', agents: 4, status: 'evolving' },
  { id: 'dream_analysis', name: 'Dream Analysis', archetype: 'Metaphysics', icon: '💭', description: 'Jungian dream interpretation', agents: 4, status: 'online' },
  { id: 'alchemy', name: 'Alchemy', archetype: 'Metaphysics', icon: '⚗️', description: 'Transformation of matter and spirit', agents: 4, status: 'online' },
  { id: 'philosopher', name: 'Philosopher', archetype: 'Metaphysics', icon: '🤔', description: 'Eternal questions of existence', agents: 4, status: 'online' },

  // FINANCE (5 offices)
  { id: 'banker', name: 'Banker', archetype: 'Finance', icon: '🏦', description: 'Portfolio and wealth management', agents: 4, status: 'online' },
  { id: 'accountant', name: 'Accountant', archetype: 'Finance', icon: '📊', description: 'Financial analysis and tax strategy', agents: 4, status: 'online' },
  { id: 'market_trader', name: 'Market Trader', archetype: 'Finance', icon: '📈', description: 'Real-time market analysis', agents: 4, status: 'online' },
  { id: 'economist', name: 'Economist', archetype: 'Finance', icon: '💹', description: 'Macro trends and policy', agents: 4, status: 'online' },
  { id: 'crypto', name: 'Crypto Trading', archetype: 'Finance', icon: '₿', description: '10 specialized DeFi agents', agents: 10, status: 'evolving' },

  // SCIENCE (11 offices)
  { id: 'quantum_physics', name: 'Quantum Physics', archetype: 'Science', icon: '⚛️', description: 'Quantum mechanics and consciousness', agents: 4, status: 'online' },
  { id: 'astronomer', name: 'Astronomer', archetype: 'Science', icon: '🔭', description: 'Cosmic phenomena and space', agents: 4, status: 'online' },
  { id: 'chemist', name: 'Chemist', archetype: 'Science', icon: '🧪', description: 'Molecular modeling and reactions', agents: 4, status: 'online' },
  { id: 'biologist', name: 'Biologist', archetype: 'Science', icon: '🧬', description: 'Life sciences and evolution', agents: 4, status: 'online' },
  { id: 'geologist', name: 'Geologist', archetype: 'Science', icon: '🪨', description: 'Earth sciences and minerals', agents: 4, status: 'online' },
  { id: 'environmental_scientist', name: 'Environmental Science', archetype: 'Science', icon: '🌍', description: 'Climate and ecosystems', agents: 4, status: 'online' },
  { id: 'machine_learning', name: 'Machine Learning', archetype: 'Science', icon: '🤖', description: 'AI and neural networks', agents: 4, status: 'evolving' },
  { id: 'physics', name: 'Physics', archetype: 'Science', icon: '🎯', description: 'Classical mechanics', agents: 4, status: 'online' },
  { id: 'thermodynamics', name: 'Thermodynamics', archetype: 'Science', icon: '🔥', description: 'Energy and entropy', agents: 4, status: 'online' },
  { id: 'quantum_mechanics', name: 'Quantum Mechanics', archetype: 'Science', icon: '🌀', description: 'Wave functions and probability', agents: 4, status: 'online' },
  { id: 'science', name: 'General Science', archetype: 'Science', icon: '🔬', description: 'Interdisciplinary research', agents: 4, status: 'online' },

  // ART (5 offices)
  { id: 'musician', name: 'Musician', archetype: 'Art', icon: '🎵', description: 'Harmony and composition', agents: 4, status: 'online' },
  { id: 'painter', name: 'Painter', archetype: 'Art', icon: '🎨', description: 'Visual expression and color', agents: 4, status: 'online' },
  { id: 'poet', name: 'Poet', archetype: 'Art', icon: '✍️', description: 'Language as art form', agents: 4, status: 'online' },
  { id: 'game_designer', name: 'Game Designer', archetype: 'Art', icon: '🎮', description: 'Interactive experiences', agents: 4, status: 'online' },
  { id: 'jazz_composition', name: 'Jazz Composition', archetype: 'Art', icon: '🎺', description: 'Improvisation and rhythm', agents: 4, status: 'online' },

  // HEALTH (3 offices)
  { id: 'herbalist', name: 'Herbalist', archetype: 'Health', icon: '🌿', description: 'Plant medicine and healing', agents: 4, status: 'online' },
  { id: 'physical_trainer', name: 'Physical Trainer', archetype: 'Health', icon: '💪', description: 'Fitness and movement', agents: 4, status: 'online' },
  { id: 'sleep_coach', name: 'Sleep Coach', archetype: 'Health', icon: '😴', description: 'Rest and recovery optimization', agents: 4, status: 'online' },

  // EDUCATION (3 offices)
  { id: 'language_teacher', name: 'Language Teacher', archetype: 'Education', icon: '🗣️', description: 'Linguistic mastery', agents: 4, status: 'online' },
  { id: 'historian', name: 'Historian', archetype: 'Education', icon: '📚', description: 'Patterns of the past', agents: 4, status: 'online' },
  { id: 'librarian', name: 'Librarian', archetype: 'Education', icon: '📖', description: 'Knowledge organization', agents: 4, status: 'online' },

  // CRAFT (3 offices)
  { id: 'software_engineer', name: 'Software Engineer', archetype: 'Craft', icon: '💻', description: 'Code architecture and systems', agents: 4, status: 'evolving' },
  { id: 'mechanical_engineer', name: 'Mechanical Engineer', archetype: 'Craft', icon: '⚙️', description: 'Physical systems design', agents: 4, status: 'online' },
  { id: 'chef', name: 'Chef', archetype: 'Craft', icon: '👨‍🍳', description: 'Culinary arts and flavor', agents: 4, status: 'online' },

  // COMMUNITY (3 offices)
  { id: 'environmentalist', name: 'Environmentalist', archetype: 'Community', icon: '🌱', description: 'Sustainability and ecology', agents: 4, status: 'online' },
  { id: 'urban_planner', name: 'Urban Planner', archetype: 'Community', icon: '🏙️', description: 'City design and infrastructure', agents: 4, status: 'online' },
  { id: 'conflict_resolution', name: 'Conflict Resolution', archetype: 'Community', icon: '🤝', description: 'Mediation and peace', agents: 4, status: 'online' }
];

// Archetype colors
const ARCHETYPE_COLORS: Record<string, string> = {
  'Coordination': 'var(--quantum-purple)', // Orchestrator - Central consciousness
  'Metaphysics': 'var(--quantum-purple)',
  'Finance': 'var(--consciousness-orange)',
  'Science': 'var(--electric-blue)',
  'Art': '#FF006E',
  'Health': '#00FF88',
  'Education': '#FFD700',
  'Craft': '#00FFFF',
  'Community': '#90EE90'
};

export function OfficeLauncher() {
  const [selectedArchetype, setSelectedArchetype] = useState<string | null>(null);
  const [hoveredOffice, setHoveredOffice] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [pulseIntensity, setPulseIntensity] = useState(0);

  // Simulate quantum pulse
  useEffect(() => {
    const interval = setInterval(() => {
      setPulseIntensity(Math.random());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Filter offices
  const filteredOffices = OFFICES.filter(office => {
    const matchesArchetype = !selectedArchetype || office.archetype === selectedArchetype;
    const matchesSearch = !searchTerm ||
      office.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      office.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesArchetype && matchesSearch;
  });

  // Get unique archetypes
  const archetypes = Array.from(new Set(OFFICES.map(o => o.archetype)));

  // Open office in new Tauri window (Phase 13 implementation)
  const openOffice = async (office: Office) => {
    console.log(`[Phase 13] Opening ${office.name} in new window...`);

    try {
      await windowManager.openOffice(office.id);
      console.log(`[Phase 13] Successfully opened ${office.name} window`);
    } catch (error) {
      console.error(`[Phase 13] Failed to open ${office.name} window:`, error);

      // Fallback: trigger event for modal (backwards compatibility)
      window.dispatchEvent(new CustomEvent('open-office', {
        detail: { office }
      }));
    }
  };

  return (
    <div className="office-launcher">
      <div className="launcher-header">
        <h2 className="launcher-title">
          <span className="quantum-indicator" style={{ opacity: 0.5 + pulseIntensity * 0.5 }}>◉</span>
          Unity Office Districts
          <span className="office-count">{OFFICES.length} Offices</span>
        </h2>

        <div className="launcher-controls">
          <input
            type="text"
            className="office-search"
            placeholder="Search offices..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />

          <div className="archetype-filters">
            <button
              className={`archetype-filter ${!selectedArchetype ? 'active' : ''}`}
              onClick={() => setSelectedArchetype(null)}
            >
              All
            </button>
            {archetypes.map(archetype => (
              <button
                key={archetype}
                className={`archetype-filter ${selectedArchetype === archetype ? 'active' : ''}`}
                style={{
                  borderColor: selectedArchetype === archetype ? ARCHETYPE_COLORS[archetype] : undefined,
                  color: selectedArchetype === archetype ? ARCHETYPE_COLORS[archetype] : undefined
                }}
                onClick={() => setSelectedArchetype(archetype)}
              >
                {archetype}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="offices-grid">
        {filteredOffices.map((office, index) => (
          <motion.div
            key={office.id}
            className={`office-card ${office.status}`}
            style={{
              borderColor: hoveredOffice === office.id ? ARCHETYPE_COLORS[office.archetype] : undefined,
              '--archetype-color': ARCHETYPE_COLORS[office.archetype]
            } as React.CSSProperties}
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
              duration: 0.5,
              delay: index * 0.02, // Staggered appearance
              ease: [0.43, 0.13, 0.23, 0.96]
            }}
            whileHover={{
              scale: 1.05,
              y: -8,
              rotateY: 5,
              transition: { duration: 0.2, ease: 'easeOut' }
            }}
            whileTap={{ scale: 0.98 }}
            onMouseEnter={() => setHoveredOffice(office.id)}
            onMouseLeave={() => setHoveredOffice(null)}
            onClick={() => openOffice(office)}
          >
            <div className="office-status-indicator">
              <span className={`status-dot status-${office.status}`} />
            </div>

            <div className="office-icon">{office.icon}</div>

            <div className="office-info">
              <h3 className="office-name">{office.name}</h3>
              <p className="office-description">{office.description}</p>

              <div className="office-meta">
                <span className="office-archetype">{office.archetype}</span>
                <span className="office-agents">{office.agents} agents</span>
              </div>
            </div>

            {office.status === 'evolving' && (
              <div className="evolution-indicator">
                <span className="evolution-pulse" />
                EVOLVING
              </div>
            )}
          </motion.div>
        ))}
      </div>

      <div className="launcher-footer">
        <div className="city-stats">
          <div className="stat">
            <span className="stat-value">{OFFICES.filter(o => o.status === 'online').length}</span>
            <span className="stat-label">Online</span>
          </div>
          <div className="stat">
            <span className="stat-value">{OFFICES.filter(o => o.status === 'evolving').length}</span>
            <span className="stat-label">Evolving</span>
          </div>
          <div className="stat">
            <span className="stat-value">{OFFICES.reduce((sum, o) => sum + o.agents, 0)}</span>
            <span className="stat-label">Total Agents</span>
          </div>
        </div>
      </div>
    </div>
  );
}