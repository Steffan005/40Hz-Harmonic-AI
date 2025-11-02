import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Brain, Lightbulb, TrendingUp, AlertCircle, Sparkles } from 'lucide-react';

/**
 * KNOWLEDGE HEATMAP - Cross-Office Knowledge Matrix
 * Interactive heatmap showing knowledge contribution across all domains
 * X-axis: 43 offices | Y-axis: Knowledge domains
 * Color intensity = contribution level
 * See knowledge clusters and gaps across the entire cognitive ecosystem
 */

interface KnowledgeCell {
  office: string;
  domain: string;
  intensity: number; // 0-100 contribution level
  memories: number;
  lastUpdated: Date;
}

interface DomainStats {
  domain: string;
  totalContribution: number;
  topContributor: string;
  coverage: number; // % of offices contributing
}

const KnowledgeHeatmap: React.FC = () => {
  const [heatmapData, setHeatmapData] = useState<KnowledgeCell[][]>([]);
  const [domainStats, setDomainStats] = useState<DomainStats[]>([]);
  const [selectedCell, setSelectedCell] = useState<KnowledgeCell | null>(null);
  const [hoveredCell, setHoveredCell] = useState<{ x: number; y: number } | null>(null);
  const [viewMode, setViewMode] = useState<'intensity' | 'memories' | 'recency'>('intensity');

  // All 43 offices
  const offices = [
    'Tarot Reader', 'Astrologer', 'Numerologist', 'Crystal Healer', 'Shaman',
    'Physical Trainer', 'Nutritionist', 'Sleep Coach', 'Meditation Guide', 'Yoga Instructor',
    'Therapist', 'Life Coach', 'Relationship Counselor', 'Social Worker', 'HR Manager',
    'Financial Advisor', 'Banker', 'Stock Broker', 'Crypto Trader', 'Accountant',
    'Artist', 'Musician', 'Writer', 'Chef', 'Fashion Designer',
    'Physicist', 'Chemist', 'Biologist', 'Mathematician', 'Data Scientist',
    'Software Engineer', 'Hacker', 'Network Admin', 'Database Admin', 'DevOps Engineer',
    'Priest', 'Rabbi', 'Imam', 'Buddhist Monk', 'Philosopher',
    'Detective', 'Lawyer', 'Judge'
  ];

  // Knowledge domains
  const domains = [
    'Spirituality', 'Health & Wellness', 'Psychology', 'Finance', 'Arts & Creativity',
    'Sciences', 'Technology', 'Philosophy', 'Law & Ethics', 'Social Dynamics',
    'Prediction & Divination', 'Energy Work', 'Consciousness', 'Systems Thinking',
    'Pattern Recognition', 'Risk Assessment', 'Innovation', 'Communication'
  ];

  // Generate heatmap data
  const generateHeatmapData = () => {
    const data: KnowledgeCell[][] = [];

    domains.forEach(domain => {
      const row: KnowledgeCell[] = [];
      offices.forEach(office => {
        // Generate intensity based on domain-office affinity
        let intensity = Math.random() * 30; // Base random contribution

        // Add affinity bonuses for matching domains
        if (domain === 'Spirituality' && ['Tarot Reader', 'Astrologer', 'Shaman', 'Priest'].includes(office)) {
          intensity += 50 + Math.random() * 20;
        }
        if (domain === 'Finance' && ['Financial Advisor', 'Banker', 'Stock Broker', 'Crypto Trader'].includes(office)) {
          intensity += 50 + Math.random() * 20;
        }
        if (domain === 'Technology' && ['Software Engineer', 'Hacker', 'Data Scientist'].includes(office)) {
          intensity += 50 + Math.random() * 20;
        }
        if (domain === 'Health & Wellness' && ['Physical Trainer', 'Nutritionist', 'Yoga Instructor'].includes(office)) {
          intensity += 50 + Math.random() * 20;
        }
        if (domain === 'Arts & Creativity' && ['Artist', 'Musician', 'Writer', 'Chef'].includes(office)) {
          intensity += 50 + Math.random() * 20;
        }
        if (domain === 'Sciences' && ['Physicist', 'Chemist', 'Biologist', 'Mathematician'].includes(office)) {
          intensity += 50 + Math.random() * 20;
        }
        if (domain === 'Psychology' && ['Therapist', 'Life Coach', 'Relationship Counselor'].includes(office)) {
          intensity += 50 + Math.random() * 20;
        }

        intensity = Math.min(100, intensity);

        row.push({
          office,
          domain,
          intensity,
          memories: Math.floor(intensity * (5 + Math.random() * 10)),
          lastUpdated: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000) // Last 7 days
        });
      });
      data.push(row);
    });

    setHeatmapData(data);

    // Calculate domain statistics
    const stats: DomainStats[] = domains.map((domain, domainIdx) => {
      const domainRow = data[domainIdx];
      const totalContribution = domainRow.reduce((sum, cell) => sum + cell.intensity, 0);
      const contributingOffices = domainRow.filter(cell => cell.intensity > 20).length;
      const topContributor = domainRow.reduce((max, cell) =>
        cell.intensity > max.intensity ? cell : max
      ).office;

      return {
        domain,
        totalContribution: totalContribution / offices.length,
        topContributor,
        coverage: (contributingOffices / offices.length) * 100
      };
    });

    setDomainStats(stats);
  };

  useEffect(() => {
    generateHeatmapData();
    // Update every 10 seconds for live effect
    const interval = setInterval(() => {
      // Simulate some cells updating
      setHeatmapData(prev => {
        const newData = [...prev];
        for (let i = 0; i < 5; i++) {
          const y = Math.floor(Math.random() * domains.length);
          const x = Math.floor(Math.random() * offices.length);
          if (newData[y] && newData[y][x]) {
            newData[y][x] = {
              ...newData[y][x],
              intensity: Math.min(100, newData[y][x].intensity + (Math.random() - 0.3) * 10),
              lastUpdated: new Date()
            };
          }
        }
        return newData;
      });
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // Get color for intensity
  const getIntensityColor = (intensity: number, mode: string) => {
    if (mode === 'intensity') {
      // Purple to blue gradient based on intensity
      const r = Math.floor(155 - intensity * 0.55);
      const g = Math.floor(89 - intensity * 0.39);
      const b = Math.floor(182 + intensity * 0.37);
      return `rgb(${r}, ${g}, ${b})`;
    } else if (mode === 'memories') {
      // Green gradient for memory count
      const memories = hoveredCell && heatmapData[hoveredCell.y]?.[hoveredCell.x]?.memories || 0;
      const normalizedMemories = Math.min(100, memories / 10);
      const r = Math.floor(46 - normalizedMemories * 0.2);
      const g = Math.floor(204 - normalizedMemories * 0.5);
      const b = Math.floor(113 - normalizedMemories * 0.7);
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      // Recency - red for old, blue for new
      const cell = hoveredCell && heatmapData[hoveredCell.y]?.[hoveredCell.x];
      if (cell) {
        const hoursSinceUpdate = (Date.now() - cell.lastUpdated.getTime()) / (1000 * 60 * 60);
        const recency = Math.max(0, 100 - hoursSinceUpdate * 2);
        const r = Math.floor(231 - recency * 1.8);
        const g = Math.floor(76 + recency * 1.0);
        const b = Math.floor(60 + recency * 1.6);
        return `rgb(${r}, ${g}, ${b})`;
      }
      return 'rgb(50, 50, 50)';
    }
  };

  const getCellOpacity = (cell: KnowledgeCell) => {
    if (viewMode === 'intensity') return 0.3 + (cell.intensity / 100) * 0.7;
    if (viewMode === 'memories') return 0.3 + Math.min(1, cell.memories / 100) * 0.7;
    const hoursSinceUpdate = (Date.now() - cell.lastUpdated.getTime()) / (1000 * 60 * 60);
    return 0.3 + Math.max(0, 1 - hoursSinceUpdate / 168) * 0.7; // 168 hours = 1 week
  };

  return (
    <div className="knowledge-heatmap p-6 bg-black/80 backdrop-blur-xl rounded-2xl border border-purple-500/30">
      {/* Header */}
      <div className="header mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
              Knowledge Heatmap Matrix
            </h2>
            <p className="text-gray-400 mt-1">Cross-office knowledge contribution across all domains</p>
          </div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-yellow-400 animate-pulse" />
            <span className="text-sm text-gray-400">
              {offices.length} Offices × {domains.length} Domains
            </span>
          </div>
        </div>

        {/* View Mode Selector */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={() => setViewMode('intensity')}
            className={`px-4 py-2 rounded-lg transition-all ${
              viewMode === 'intensity'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <Brain className="w-4 h-4 inline mr-2" />
            Intensity
          </button>
          <button
            onClick={() => setViewMode('memories')}
            className={`px-4 py-2 rounded-lg transition-all ${
              viewMode === 'memories'
                ? 'bg-green-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <Lightbulb className="w-4 h-4 inline mr-2" />
            Memory Count
          </button>
          <button
            onClick={() => setViewMode('recency')}
            className={`px-4 py-2 rounded-lg transition-all ${
              viewMode === 'recency'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            <TrendingUp className="w-4 h-4 inline mr-2" />
            Recency
          </button>
        </div>
      </div>

      {/* Domain Statistics */}
      <div className="domain-stats mb-4 grid grid-cols-4 gap-3">
        {domainStats.slice(0, 4).map((stat, idx) => (
          <motion.div
            key={stat.domain}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="stat-card bg-gradient-to-br from-purple-900/30 to-blue-900/30 p-3 rounded-lg border border-purple-500/20"
          >
            <p className="text-xs text-gray-400 mb-1">{stat.domain}</p>
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold text-purple-400">
                {stat.totalContribution.toFixed(1)}%
              </span>
              <span className="text-xs text-gray-500">
                {stat.coverage.toFixed(0)}% coverage
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Top: {stat.topContributor.split(' ')[0]}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Heatmap Container */}
      <div className="heatmap-container relative overflow-auto max-h-[600px] custom-scrollbar">
        <div className="heatmap-wrapper inline-block min-w-full">
          {/* Office Labels (X-axis) */}
          <div className="offices-header flex ml-32">
            {offices.map((office, idx) => (
              <div
                key={office}
                className="office-label text-xs text-gray-400 transform rotate-45 origin-left"
                style={{
                  minWidth: '20px',
                  maxWidth: '20px',
                  height: '80px',
                  writingMode: 'vertical-rl',
                  textOrientation: 'mixed'
                }}
              >
                {office}
              </div>
            ))}
          </div>

          {/* Heatmap Grid */}
          <div className="heatmap-grid">
            {heatmapData.map((row, y) => (
              <div key={y} className="heatmap-row flex items-center">
                {/* Domain Label (Y-axis) */}
                <div className="domain-label text-xs text-gray-400 w-32 pr-2 text-right">
                  {domains[y]}
                </div>

                {/* Cells */}
                {row.map((cell, x) => (
                  <motion.div
                    key={`${x}-${y}`}
                    className="heatmap-cell relative"
                    style={{
                      width: '20px',
                      height: '20px',
                      backgroundColor: getIntensityColor(cell.intensity, viewMode),
                      opacity: getCellOpacity(cell),
                      border: hoveredCell?.x === x && hoveredCell?.y === y
                        ? '2px solid #fff'
                        : '1px solid rgba(0,0,0,0.3)',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={() => setHoveredCell({ x, y })}
                    onMouseLeave={() => setHoveredCell(null)}
                    onClick={() => setSelectedCell(cell)}
                    whileHover={{ scale: 1.5, zIndex: 10 }}
                    transition={{ duration: 0.2 }}
                  >
                    {/* Pulse effect for recent updates */}
                    {(Date.now() - cell.lastUpdated.getTime()) < 10000 && (
                      <span className="absolute inset-0 animate-ping bg-white opacity-30 rounded-sm"></span>
                    )}
                  </motion.div>
                ))}

                {/* Row total */}
                <div className="row-total ml-2 text-xs text-gray-500">
                  {row.reduce((sum, cell) => sum + cell.intensity, 0).toFixed(0)}
                </div>
              </div>
            ))}
          </div>

          {/* Column totals */}
          <div className="column-totals flex ml-32 mt-2">
            {offices.map((_, x) => {
              const columnTotal = heatmapData.reduce((sum, row) =>
                sum + (row[x]?.intensity || 0), 0
              );
              return (
                <div
                  key={x}
                  className="text-xs text-gray-500 text-center"
                  style={{ minWidth: '20px', maxWidth: '20px' }}
                >
                  {columnTotal.toFixed(0)}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Selected Cell Details */}
      {selectedCell && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="cell-details mt-4 p-4 bg-gradient-to-br from-purple-900/50 to-blue-900/50 rounded-lg border border-purple-500/30"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">
                {selectedCell.office} → {selectedCell.domain}
              </h3>
              <div className="flex gap-4 mt-2 text-sm">
                <span className="text-purple-400">
                  Intensity: {selectedCell.intensity.toFixed(1)}%
                </span>
                <span className="text-green-400">
                  Memories: {selectedCell.memories}
                </span>
                <span className="text-blue-400">
                  Updated: {new Date(selectedCell.lastUpdated).toLocaleString()}
                </span>
              </div>
            </div>
            <button
              onClick={() => setSelectedCell(null)}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
        </motion.div>
      )}

      {/* Legend */}
      <div className="legend mt-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-400">Low Contribution</span>
          <div className="gradient-bar h-4 w-32 rounded" style={{
            background: `linear-gradient(90deg,
              ${getIntensityColor(0, viewMode)} 0%,
              ${getIntensityColor(50, viewMode)} 50%,
              ${getIntensityColor(100, viewMode)} 100%)`
          }} />
          <span className="text-xs text-gray-400">High Contribution</span>
        </div>
        <div className="text-xs text-gray-500 flex items-center gap-2">
          <AlertCircle className="w-3 h-3" />
          Click cells for details • Hover to highlight
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #9B59B6 0%, #3498DB 100%);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-corner {
          background: rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  );
};

export default KnowledgeHeatmap;