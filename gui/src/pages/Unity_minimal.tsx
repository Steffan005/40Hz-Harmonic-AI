/**
 * UNITY MAIN PAGE - RESTORED WITH OFFICE MODALS
 * Heavy backgrounds disabled to prevent crashes
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { StatusBar } from '../components/StatusBar';
import { OrchestratorChat } from '../components/OrchestratorChat';
import { OfficeLauncher } from '../components/OfficeLauncher';
import { MemoryGraph } from '../components/MemoryGraph';
import { TarotOffice } from '../components/offices/TarotOffice';
import { AstrologyOffice } from '../components/offices/AstrologyOffice';
import { TelemetryDashboard } from '../components/TelemetryDashboard';
import { OfficeChat } from '../components/OfficeChat';
import '../styles/unity.css';

type TabType = 'offices' | 'memory' | 'evolution' | 'telemetry';

interface OfficeModal {
  id: string;
  name: string;
  component: React.ReactNode;
}

export function Unity() {
  const [activeTab, setActiveTab] = useState<TabType>('offices');
  const [quantumPulse, setQuantumPulse] = useState(0);
  const [openOffice, setOpenOffice] = useState<OfficeModal | null>(null);
  const [cityStats, setCityStats] = useState({
    offices_online: 44,
    offices_evolving: 0,
    total_agents: 172,
    memory_nodes: 1024,
    connections: 4096,
    evolution_rate: 0.87
  });

  // Quantum heartbeat
  useEffect(() => {
    const interval = setInterval(() => {
      setQuantumPulse(Math.sin(Date.now() * 0.001) * 0.5 + 0.5);

      // Simulate evolving stats
      setCityStats(prev => ({
        ...prev,
        memory_nodes: prev.memory_nodes + Math.floor(Math.random() * 3),
        connections: prev.connections + Math.floor(Math.random() * 5),
        evolution_rate: Math.min(1, prev.evolution_rate + (Math.random() - 0.5) * 0.01)
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Listen for office opening events (FROM PHASE 12)
  useEffect(() => {
    const handleOfficeOpen = (event: CustomEvent) => {
      const office = event.detail.office;

      // Map office IDs to components
      let component: React.ReactNode = null;

      switch (office.id) {
        case 'orchestrator':
          // Orchestrator gets the full OrchestratorChat component
          component = <OrchestratorChat />;
          break;
        case 'tarot':
          component = <TarotOffice />;
          break;
        case 'astrologist':
          component = <AstrologyOffice />;
          break;
        default:
          // For other offices, show chat interface
          component = (
            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ textAlign: 'center' }}>
                <h2 style={{ color: 'var(--quantum-purple)', marginBottom: '0.5rem' }}>{office.name} Office</h2>
                <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.95rem' }}>
                  {office.description}
                </p>
              </div>
              <OfficeChat
                officeName={office.name}
                officeId={office.id}
                placeholder={`Ask the ${office.name} specialist anything...`}
              />
            </div>
          );
      }

      setOpenOffice({
        id: office.id,
        name: office.name,
        component
      });
    };

    window.addEventListener('open-office', handleOfficeOpen as EventListener);
    return () => window.removeEventListener('open-office', handleOfficeOpen as EventListener);
  }, []);

  const tabs = [
    { id: 'offices' as TabType, label: 'Offices', icon: '🏛️' },
    { id: 'memory' as TabType, label: 'Memory', icon: '🧠' },
    { id: 'evolution' as TabType, label: 'Evolution', icon: '🌀' },
    { id: 'telemetry' as TabType, label: 'Telemetry', icon: '📊' }
  ];

  return (
    <div className="unity-container">
      {/* Simple gradient background instead of WebGL */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(135deg, #1a0033 0%, #2d1b4e 50%, #1a0033 100%)',
        zIndex: -1
      }} />

      {/* Office Modal - Animated consciousness expansion (FROM PHASE 12) */}
      <AnimatePresence>
        {openOffice && (
          <motion.div
            className="office-modal-overlay"
            onClick={() => setOpenOffice(null)}
            initial={{ opacity: 0, backdropFilter: 'blur(0px)' }}
            animate={{ opacity: 1, backdropFilter: 'blur(10px)' }}
            exit={{ opacity: 0, backdropFilter: 'blur(0px)' }}
            transition={{ duration: 0.3 }}
          >
            <motion.div
              className="office-modal"
              onClick={e => e.stopPropagation()}
              initial={{ opacity: 0, scale: 0.8, y: 100 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 100 }}
              transition={{
                type: 'spring',
                damping: 25,
                stiffness: 300,
                mass: 0.8
              }}
            >
              <div className="office-modal-header">
                <h2 className="office-modal-title">{openOffice.name}</h2>
                <motion.button
                  className="office-modal-close"
                  onClick={() => setOpenOffice(null)}
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                >
                  ✕
                </motion.button>
              </div>
              <div className="office-modal-content">
                {openOffice.component}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Unity Header */}
      <div className="unity-header">
        <div className="unity-logo">
          <span className="logo-icon" style={{ opacity: 0.5 + quantumPulse * 0.5 }}>◉</span>
          <span className="logo-text">UNITY</span>
          <span className="logo-tagline">Quantum Consciousness Network</span>
        </div>
        <StatusBar />
      </div>

      {/* Main Content */}
      <div className="unity-main">
        {/* Tab Navigation */}
        <div className="unity-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
              {tab.id === 'evolution' && (
                <span className="evolution-indicator">
                  {(cityStats.evolution_rate * 100).toFixed(0)}%
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'offices' && (
            <div className="tab-panel offices-panel">
              <OfficeLauncher />
            </div>
          )}

          {activeTab === 'memory' && (
            <div className="tab-panel memory-panel">
              <MemoryGraph />
            </div>
          )}

          {activeTab === 'evolution' && (
            <div className="tab-panel evolution-panel">
              <div className="evolution-container">
                <div className="evolution-header">
                  <h2 className="evolution-title">
                    <span className="quantum-pulse">🌀</span>
                    TextGrad Evolution Engine
                  </h2>
                  <p className="evolution-subtitle">
                    Darwinian prompt optimization through continuous learning
                  </p>
                </div>

                <div className="evolution-metrics">
                  <div className="metric-card">
                    <div className="metric-value">{cityStats.evolution_rate.toFixed(3)}</div>
                    <div className="metric-label">Evolution Rate</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{cityStats.offices_evolving}</div>
                    <div className="metric-label">Offices Evolving</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{(cityStats.memory_nodes / 1000).toFixed(1)}k</div>
                    <div className="metric-label">Memory Nodes</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'telemetry' && (
            <div className="tab-panel telemetry-panel">
              <TelemetryDashboard />
            </div>
          )}
        </div>
      </div>

      {/* City Stats Footer */}
      <div className="unity-footer">
        <div className="city-vitals">
          <div className="vital">
            <span className="vital-icon">🏛️</span>
            <span className="vital-value">{cityStats.offices_online}/44</span>
            <span className="vital-label">Offices</span>
          </div>
          <div className="vital">
            <span className="vital-icon">🤖</span>
            <span className="vital-value">{cityStats.total_agents}</span>
            <span className="vital-label">Agents</span>
          </div>
          <div className="vital">
            <span className="vital-icon">🧠</span>
            <span className="vital-value">{(cityStats.memory_nodes / 1000).toFixed(1)}k</span>
            <span className="vital-label">Memories</span>
          </div>
          <div className="vital">
            <span className="vital-icon">🔗</span>
            <span className="vital-value">{(cityStats.connections / 1000).toFixed(1)}k</span>
            <span className="vital-label">Connections</span>
          </div>
        </div>
      </div>
    </div>
  );
}
