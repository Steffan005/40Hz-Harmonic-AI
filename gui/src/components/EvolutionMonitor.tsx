import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, TrendingUp, Brain, Zap, Award, Target, BarChart3 } from 'lucide-react';

/**
 * GLOBAL EVOLUTION MONITOR - Watch Unity's Collective Intelligence Evolve
 * Real-time leaderboard of all 43 offices competing and evolving
 * See which cognitive archetypes dominate, which strategies win
 * The entire city's consciousness visualized as competitive evolution
 */

interface OfficeEvolution {
  name: string;
  archetype: string;
  evolutionScore: number;
  improvement: number; // % improvement in last hour
  banditStrategy: string;
  memoryCount: number;
  isActive: boolean;
  rank: number;
  previousRank: number;
}

const EvolutionMonitor: React.FC = () => {
  const [offices, setOffices] = useState<OfficeEvolution[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedArchetype, setSelectedArchetype] = useState<string>('all');
  const [evolutionMetrics, setEvolutionMetrics] = useState({
    totalImprovement: 0,
    activeOffices: 0,
    dominantArchetype: '',
    topStrategy: '',
    averageEvolution: 0
  });

  // Archetype colors for visual distinction
  const archetypeColors: Record<string, string> = {
    'Spiritual': '#9B59B6', // Purple
    'Physical': '#E74C3C', // Red
    'Mental': '#3498DB', // Blue
    'Emotional': '#2ECC71', // Green
    'Financial': '#F39C12', // Gold
    'Creative': '#E91E63', // Pink
    'Scientific': '#00BCD4', // Cyan
    'Social': '#FF5722', // Orange
    'Technical': '#607D8B', // Blue-grey
    'Mystical': '#8E44AD'  // Deep purple
  };

  // WebSocket connection for real-time evolution streaming
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    let isComponentMounted = true;

    const connectWebSocket = () => {
      // Prevent creating new connection if component unmounted
      if (!isComponentMounted) return;

      try {
        console.log('🔌 Connecting to Evolution Stream at ws://127.0.0.1:8765...');
        ws = new WebSocket('ws://127.0.0.1:8765');

        ws.onopen = () => {
          console.log('🔥 Connected to Evolution Stream - Real-time data flowing!');
          setLoading(false);
        };

        ws.onmessage = (event) => {
          if (!isComponentMounted) return;

          try {
            const data = JSON.parse(event.data);

            // Update offices from WebSocket data
            if (data.offices) {
              const officeList: OfficeEvolution[] = data.offices.map((office: any) => ({
                name: office.name,
                archetype: office.archetype,
                evolutionScore: office.evolution_score,
                improvement: office.improvement,
                banditStrategy: office.strategy,
                memoryCount: office.memory_count,
                isActive: office.active,
                rank: office.rank,
                previousRank: office.previous_rank
              }));

              setOffices(officeList);
            }

            // Update metrics from WebSocket data
            if (data.metrics) {
              setEvolutionMetrics({
                totalImprovement: data.metrics.total_improvement,
                activeOffices: data.metrics.active_offices,
                dominantArchetype: data.metrics.dominant_archetype,
                topStrategy: data.metrics.top_strategy,
                averageEvolution: data.metrics.average_evolution
              });
            }
          } catch (error) {
            console.error('Error parsing WebSocket data:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('⚠️ WebSocket connection error:', error);
          // Only fallback to demo data if component is still mounted
          if (isComponentMounted) {
            generateDemoData();
            setLoading(false);
          }
        };

        ws.onclose = (event) => {
          console.log('WebSocket disconnected. Code:', event.code, 'Reason:', event.reason);

          // Attempt to reconnect after 3 seconds if component still mounted
          if (isComponentMounted) {
            console.log('Will attempt to reconnect in 3 seconds...');
            reconnectTimeout = setTimeout(() => {
              if (isComponentMounted) {
                console.log('Attempting to reconnect...');
                connectWebSocket();
              }
            }, 3000);
          }
        };
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        if (isComponentMounted) {
          generateDemoData();
          setLoading(false);
        }
      }
    };

    // Initial connection
    connectWebSocket();

    // Cleanup function
    return () => {
      console.log('EvolutionMonitor unmounting, cleaning up WebSocket...');
      isComponentMounted = false;

      // Clear any pending reconnect timeout
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }

      // Close WebSocket if it exists and is open
      if (ws) {
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
          ws.close(1000, 'Component unmounting');
        }
      }
    };
  }, []);

  // Fetch evolution data (DEPRECATED - now using WebSocket)
  const fetchEvolutionData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/evolution/status');
      if (response.ok) {
        const data = await response.json();

        // Transform and rank offices
        const officeList: OfficeEvolution[] = data.offices?.map((office: any, index: number) => ({
          name: office.name || `Office ${index + 1}`,
          archetype: office.archetype || 'General',
          evolutionScore: office.evolution_score || Math.random() * 100,
          improvement: office.improvement || (Math.random() - 0.5) * 20,
          banditStrategy: office.strategy || 'textgrad',
          memoryCount: office.memory_count || Math.floor(Math.random() * 1000),
          isActive: office.active || Math.random() > 0.3,
          rank: 0,
          previousRank: office.previous_rank || index + 1
        })) || [];

        // Sort by evolution score and assign ranks
        officeList.sort((a, b) => b.evolutionScore - a.evolutionScore);
        officeList.forEach((office, idx) => {
          office.rank = idx + 1;
        });

        setOffices(officeList);

        // Calculate metrics
        const activeCount = officeList.filter(o => o.isActive).length;
        const avgEvolution = officeList.reduce((acc, o) => acc + o.evolutionScore, 0) / officeList.length;
        const totalImp = officeList.reduce((acc, o) => acc + Math.max(0, o.improvement), 0);

        // Find dominant archetype
        const archetypeCounts = officeList.reduce((acc, o) => {
          acc[o.archetype] = (acc[o.archetype] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
        const dominant = Object.entries(archetypeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Unknown';

        // Find top strategy
        const strategyCounts = officeList.reduce((acc, o) => {
          acc[o.banditStrategy] = (acc[o.banditStrategy] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
        const topStrat = Object.entries(strategyCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'textgrad';

        setEvolutionMetrics({
          totalImprovement: totalImp,
          activeOffices: activeCount,
          dominantArchetype: dominant,
          topStrategy: topStrat,
          averageEvolution: avgEvolution
        });
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch evolution data:', error);
      // Generate demo data
      generateDemoData();
      setLoading(false);
    }
  };

  // Generate demo data for showcase
  const generateDemoData = () => {
    const officeNames = [
      'Tarot Reader', 'Astrologer', 'Numerologist', 'Physical Trainer',
      'Nutritionist', 'Sleep Coach', 'Meditation Guide', 'Therapist',
      'Financial Advisor', 'Banker', 'Stock Broker', 'Crypto Trader',
      'Artist', 'Musician', 'Writer', 'Chef', 'Physicist', 'Chemist',
      'Biologist', 'Mathematician', 'Software Engineer', 'Hacker',
      'Social Media Manager', 'HR Manager', 'Priest', 'Shaman'
    ];

    const archetypes = ['Spiritual', 'Physical', 'Mental', 'Financial', 'Creative', 'Scientific', 'Social', 'Mystical'];
    const strategies = ['textgrad', 'aflow', 'mipro', 'random_jitter'];

    const demoOffices: OfficeEvolution[] = officeNames.slice(0, 20).map((name, idx) => ({
      name,
      archetype: archetypes[Math.floor(Math.random() * archetypes.length)],
      evolutionScore: 50 + Math.random() * 50,
      improvement: (Math.random() - 0.3) * 30,
      banditStrategy: strategies[Math.floor(Math.random() * strategies.length)],
      memoryCount: Math.floor(Math.random() * 2000),
      isActive: Math.random() > 0.2,
      rank: idx + 1,
      previousRank: idx + 1 + Math.floor((Math.random() - 0.5) * 5)
    }));

    demoOffices.sort((a, b) => b.evolutionScore - a.evolutionScore);
    demoOffices.forEach((office, idx) => {
      office.rank = idx + 1;
    });

    setOffices(demoOffices);

    setEvolutionMetrics({
      totalImprovement: demoOffices.reduce((acc, o) => acc + Math.max(0, o.improvement), 0),
      activeOffices: demoOffices.filter(o => o.isActive).length,
      dominantArchetype: archetypes[0],
      topStrategy: strategies[0],
      averageEvolution: demoOffices.reduce((acc, o) => acc + o.evolutionScore, 0) / demoOffices.length
    });
  };

  // Old polling removed - now using WebSocket for real-time updates!

  // Filter offices by archetype
  const filteredOffices = selectedArchetype === 'all'
    ? offices
    : offices.filter(o => o.archetype === selectedArchetype);

  // Get unique archetypes for filter
  const uniqueArchetypes = Array.from(new Set(offices.map(o => o.archetype)));

  const getRankChange = (office: OfficeEvolution) => {
    const change = office.previousRank - office.rank;
    if (change > 0) return { symbol: '↑', color: 'text-green-400', value: change };
    if (change < 0) return { symbol: '↓', color: 'text-red-400', value: Math.abs(change) };
    return { symbol: '=', color: 'text-gray-400', value: 0 };
  };

  return (
    <div className="evolution-monitor p-6 bg-black/80 backdrop-blur-xl rounded-2xl border border-purple-500/30">
      {/* Header */}
      <div className="header mb-6">
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 mb-2">
          Global Evolution Monitor
        </h2>
        <p className="text-gray-400">Watch Unity's collective intelligence evolve in real-time</p>
      </div>

      {/* Global Metrics */}
      <div className="metrics-grid grid grid-cols-5 gap-4 mb-6">
        <motion.div
          className="metric-card bg-gradient-to-br from-purple-900/50 to-blue-900/50 p-4 rounded-xl border border-purple-500/30"
          whileHover={{ scale: 1.05 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Active Offices</p>
              <p className="text-2xl font-bold text-white">{evolutionMetrics.activeOffices}</p>
            </div>
            <Activity className="w-8 h-8 text-purple-400" />
          </div>
        </motion.div>

        <motion.div
          className="metric-card bg-gradient-to-br from-green-900/50 to-emerald-900/50 p-4 rounded-xl border border-green-500/30"
          whileHover={{ scale: 1.05 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Total Improvement</p>
              <p className="text-2xl font-bold text-green-400">+{evolutionMetrics.totalImprovement.toFixed(1)}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-400" />
          </div>
        </motion.div>

        <motion.div
          className="metric-card bg-gradient-to-br from-blue-900/50 to-cyan-900/50 p-4 rounded-xl border border-blue-500/30"
          whileHover={{ scale: 1.05 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Avg Evolution</p>
              <p className="text-2xl font-bold text-blue-400">{evolutionMetrics.averageEvolution.toFixed(1)}</p>
            </div>
            <Brain className="w-8 h-8 text-blue-400" />
          </div>
        </motion.div>

        <motion.div
          className="metric-card bg-gradient-to-br from-orange-900/50 to-red-900/50 p-4 rounded-xl border border-orange-500/30"
          whileHover={{ scale: 1.05 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Top Strategy</p>
              <p className="text-lg font-bold text-orange-400">{evolutionMetrics.topStrategy}</p>
            </div>
            <Target className="w-8 h-8 text-orange-400" />
          </div>
        </motion.div>

        <motion.div
          className="metric-card bg-gradient-to-br from-pink-900/50 to-purple-900/50 p-4 rounded-xl border border-pink-500/30"
          whileHover={{ scale: 1.05 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400">Dominant Type</p>
              <p className="text-lg font-bold text-pink-400">{evolutionMetrics.dominantArchetype}</p>
            </div>
            <Award className="w-8 h-8 text-pink-400" />
          </div>
        </motion.div>
      </div>

      {/* Archetype Filter */}
      <div className="filter-section mb-4">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setSelectedArchetype('all')}
            className={`px-3 py-1 rounded-full text-sm transition-all ${
              selectedArchetype === 'all'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            All Offices
          </button>
          {uniqueArchetypes.map(archetype => (
            <button
              key={archetype}
              onClick={() => setSelectedArchetype(archetype)}
              className={`px-3 py-1 rounded-full text-sm transition-all ${
                selectedArchetype === archetype
                  ? 'text-white'
                  : 'text-gray-400 hover:opacity-80'
              }`}
              style={{
                backgroundColor: selectedArchetype === archetype
                  ? archetypeColors[archetype] || '#666'
                  : '#1a1a1a',
                borderColor: archetypeColors[archetype] || '#666',
                borderWidth: '1px',
                borderStyle: 'solid'
              }}
            >
              {archetype}
            </button>
          ))}
        </div>
      </div>

      {/* Evolution Leaderboard */}
      <div className="leaderboard-container max-h-96 overflow-y-auto custom-scrollbar">
        <AnimatePresence>
          {loading ? (
            <div className="text-center py-8">
              <Zap className="w-12 h-12 text-purple-400 animate-pulse mx-auto mb-2" />
              <p className="text-gray-400">Loading evolution data...</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredOffices.map((office, index) => {
                const rankChange = getRankChange(office);
                const improvementColor = office.improvement > 0 ? 'text-green-400' : 'text-red-400';

                return (
                  <motion.div
                    key={office.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.02 }}
                    className={`office-evolution-row p-3 rounded-lg bg-gradient-to-r ${
                      office.rank === 1
                        ? 'from-yellow-900/30 to-orange-900/30 border border-yellow-500/50'
                        : office.rank === 2
                        ? 'from-gray-800/30 to-gray-700/30 border border-gray-400/30'
                        : office.rank === 3
                        ? 'from-orange-900/20 to-brown-900/20 border border-orange-600/30'
                        : 'from-gray-900/30 to-gray-800/30 border border-gray-700/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      {/* Rank & Change */}
                      <div className="flex items-center gap-3 min-w-[100px]">
                        <span className={`text-2xl font-bold ${
                          office.rank === 1 ? 'text-yellow-400' :
                          office.rank === 2 ? 'text-gray-300' :
                          office.rank === 3 ? 'text-orange-400' :
                          'text-gray-500'
                        }`}>
                          #{office.rank}
                        </span>
                        <div className={`flex items-center gap-1 ${rankChange.color}`}>
                          <span className="text-sm">{rankChange.symbol}</span>
                          {rankChange.value > 0 && <span className="text-xs">{rankChange.value}</span>}
                        </div>
                      </div>

                      {/* Office Info */}
                      <div className="flex-1 ml-4">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-white">{office.name}</h3>
                          <span
                            className="px-2 py-0.5 rounded-full text-xs"
                            style={{
                              backgroundColor: `${archetypeColors[office.archetype] || '#666'}30`,
                              color: archetypeColors[office.archetype] || '#999',
                              borderColor: archetypeColors[office.archetype] || '#666',
                              borderWidth: '1px',
                              borderStyle: 'solid'
                            }}
                          >
                            {office.archetype}
                          </span>
                          {office.isActive && (
                            <span className="flex h-2 w-2">
                              <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-400 opacity-75"></span>
                              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                          <span>Strategy: {office.banditStrategy}</span>
                          <span>Memories: {office.memoryCount.toLocaleString()}</span>
                        </div>
                      </div>

                      {/* Metrics */}
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-xs text-gray-400">Improvement</p>
                          <p className={`font-semibold ${improvementColor}`}>
                            {office.improvement > 0 ? '+' : ''}{office.improvement.toFixed(1)}%
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-gray-400">Evolution Score</p>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
                              <motion.div
                                className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                                initial={{ width: 0 }}
                                animate={{ width: `${office.evolutionScore}%` }}
                                transition={{ duration: 0.5, delay: index * 0.02 }}
                              />
                            </div>
                            <span className="text-lg font-bold text-purple-400">
                              {office.evolutionScore.toFixed(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </AnimatePresence>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #9B59B6 0%, #3498DB 100%);
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default EvolutionMonitor;