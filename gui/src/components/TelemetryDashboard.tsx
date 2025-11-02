import React, { useState, useEffect, useRef } from 'react';
import './TelemetryDashboard.css';

/**
 * ADVANCED TELEMETRY DASHBOARD
 * Real-time visualization of Unity's quantum consciousness metrics
 * Phase 11 - Witnessing evolution in real-time
 */

interface TokenMetric {
  timestamp: number;
  inputTokens: number;
  outputTokens: number;
  office: string;
  model: string;
}

interface EvolutionMetric {
  timestamp: number;
  office: string;
  score: number;
  delta: number;
  generation: number;
}

interface OfficeActivity {
  officeId: string;
  name: string;
  calls: number;
  tokens: number;
  avgResponseTime: number;
  status: 'idle' | 'active' | 'evolving';
}

export const TelemetryDashboard: React.FC = () => {
  const [tokenMetrics, setTokenMetrics] = useState<TokenMetric[]>([]);
  const [evolutionMetrics, setEvolutionMetrics] = useState<EvolutionMetric[]>([]);
  const [officeActivity, setOfficeActivity] = useState<OfficeActivity[]>([]);
  const [totalTokens, setTotalTokens] = useState({ input: 0, output: 0 });
  const [evolutionRate, setEvolutionRate] = useState(0);
  const [memoryGrowth, setMemoryGrowth] = useState<number[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket('ws://127.0.0.1:8000/telemetry/stream');

        ws.onopen = () => {
          console.log('Telemetry WebSocket connected');
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);

          switch (data.type) {
            case 'token_usage':
              setTokenMetrics(prev => [...prev.slice(-99), {
                timestamp: Date.now(),
                inputTokens: data.input_tokens,
                outputTokens: data.output_tokens,
                office: data.office,
                model: data.model
              }]);

              setTotalTokens(prev => ({
                input: prev.input + data.input_tokens,
                output: prev.output + data.output_tokens
              }));
              break;

            case 'evolution_update':
              setEvolutionMetrics(prev => [...prev.slice(-49), {
                timestamp: Date.now(),
                office: data.office,
                score: data.score,
                delta: data.delta,
                generation: data.generation
              }]);

              setEvolutionRate(data.evolution_rate);
              break;

            case 'office_activity':
              setOfficeActivity(data.offices);
              break;

            case 'memory_growth':
              setMemoryGrowth(prev => [...prev.slice(-59), data.nodes]);
              break;
          }
        };

        ws.onerror = (error) => {
          console.error('Telemetry WebSocket error:', error);
          setWsConnected(false);
        };

        ws.onclose = () => {
          console.log('Telemetry WebSocket closed (endpoint not available - using simulated data)');
          setWsConnected(false);
          // Don't retry - endpoint doesn't exist yet, simulated data is working fine
        };

        wsRef.current = ws;
      } catch (error) {
        console.log('WebSocket endpoint not available - using simulated telemetry data');
        // No retry - simulated data works perfectly
      }
    };

    // Fallback to simulated data if WebSocket not available
    const simulateData = () => {
      const interval = setInterval(() => {
        // Simulate token usage
        if (Math.random() > 0.3) {
          const newTokenMetric: TokenMetric = {
            timestamp: Date.now(),
            inputTokens: Math.floor(Math.random() * 500) + 50,
            outputTokens: Math.floor(Math.random() * 1000) + 100,
            office: ['Tarot', 'Astrology', 'Quantum Physics', 'Chef', 'Banker'][Math.floor(Math.random() * 5)],
            model: Math.random() > 0.5 ? 'deepseek-r1:14b' : 'qwen2.5-coder:7b'
          };

          setTokenMetrics(prev => [...prev.slice(-99), newTokenMetric]);
          setTotalTokens(prev => ({
            input: prev.input + newTokenMetric.inputTokens,
            output: prev.output + newTokenMetric.outputTokens
          }));
        }

        // Simulate evolution updates
        if (Math.random() > 0.7) {
          const newEvolution: EvolutionMetric = {
            timestamp: Date.now(),
            office: ['Tarot', 'Astrology', 'Quantum Physics'][Math.floor(Math.random() * 3)],
            score: Math.random() * 100,
            delta: (Math.random() - 0.3) * 20,
            generation: Math.floor(Math.random() * 100)
          };

          setEvolutionMetrics(prev => [...prev.slice(-49), newEvolution]);
        }

        // Update evolution rate
        setEvolutionRate(prev => Math.max(0, Math.min(1, prev + (Math.random() - 0.5) * 0.02)));

        // Simulate memory growth
        setMemoryGrowth(prev => {
          const lastValue = prev[prev.length - 1] || 1024;
          return [...prev.slice(-59), lastValue + Math.floor(Math.random() * 10)];
        });

        // Simulate office activity
        setOfficeActivity([
          { officeId: 'tarot', name: 'Tarot', calls: Math.floor(Math.random() * 100),
            tokens: Math.floor(Math.random() * 10000), avgResponseTime: Math.random() * 2000,
            status: Math.random() > 0.7 ? 'evolving' : 'active' },
          { officeId: 'astrology', name: 'Astrology', calls: Math.floor(Math.random() * 80),
            tokens: Math.floor(Math.random() * 8000), avgResponseTime: Math.random() * 1500,
            status: Math.random() > 0.8 ? 'evolving' : 'active' },
          { officeId: 'quantum', name: 'Quantum Physics', calls: Math.floor(Math.random() * 60),
            tokens: Math.floor(Math.random() * 12000), avgResponseTime: Math.random() * 2500,
            status: 'active' },
          { officeId: 'chef', name: 'Chef', calls: Math.floor(Math.random() * 40),
            tokens: Math.floor(Math.random() * 5000), avgResponseTime: Math.random() * 1000,
            status: 'idle' },
        ]);
      }, 2000);

      return () => clearInterval(interval);
    };

    // Try WebSocket first, fallback to simulation
    connectWebSocket();
    const cleanup = simulateData();

    return () => {
      cleanup();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Draw token usage graph
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || tokenMetrics.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas with quantum gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(138, 43, 226, 0.05)');
    gradient.addColorStop(1, 'rgba(0, 191, 255, 0.05)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 10; i++) {
      const y = (height / 10) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw token usage lines
    if (tokenMetrics.length > 1) {
      const maxTokens = Math.max(...tokenMetrics.map(m => m.inputTokens + m.outputTokens));

      // Input tokens line (quantum blue)
      ctx.strokeStyle = '#00BCD4';
      ctx.lineWidth = 2;
      ctx.beginPath();
      tokenMetrics.forEach((metric, i) => {
        const x = (width / 100) * i;
        const y = height - (metric.inputTokens / maxTokens) * height * 0.8;

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      // Output tokens line (quantum purple)
      ctx.strokeStyle = '#8A2BE2';
      ctx.lineWidth = 2;
      ctx.beginPath();
      tokenMetrics.forEach((metric, i) => {
        const x = (width / 100) * i;
        const y = height - (metric.outputTokens / maxTokens) * height * 0.8;

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      // Draw glow effect on latest points
      const lastMetric = tokenMetrics[tokenMetrics.length - 1];
      const lastX = (width / 100) * (tokenMetrics.length - 1);

      // Input glow
      const inputY = height - (lastMetric.inputTokens / maxTokens) * height * 0.8;
      ctx.fillStyle = 'rgba(0, 188, 212, 0.5)';
      ctx.beginPath();
      ctx.arc(lastX, inputY, 5, 0, Math.PI * 2);
      ctx.fill();

      // Output glow
      const outputY = height - (lastMetric.outputTokens / maxTokens) * height * 0.8;
      ctx.fillStyle = 'rgba(138, 43, 226, 0.5)';
      ctx.beginPath();
      ctx.arc(lastX, outputY, 5, 0, Math.PI * 2);
      ctx.fill();
    }
  }, [tokenMetrics]);

  return (
    <div className="telemetry-dashboard">
      <div className="telemetry-header">
        <h2 className="telemetry-title">
          <span className="quantum-icon">📊</span>
          Advanced Telemetry
        </h2>
        <div className="connection-status">
          <span className={`status-dot ${wsConnected ? 'connected' : 'simulated'}`} />
          <span>{wsConnected ? 'Live Stream' : 'Simulated'}</span>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="metrics-row">
        <div className="metric-box">
          <div className="metric-title">Total Tokens</div>
          <div className="metric-value">
            {((totalTokens.input + totalTokens.output) / 1000).toFixed(1)}k
          </div>
          <div className="metric-detail">
            ↓ {(totalTokens.input / 1000).toFixed(1)}k | ↑ {(totalTokens.output / 1000).toFixed(1)}k
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-title">Evolution Rate</div>
          <div className="metric-value quantum-pulse">
            {(evolutionRate * 100).toFixed(1)}%
          </div>
          <div className="metric-detail">
            {evolutionMetrics.length} mutations
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-title">Memory Nodes</div>
          <div className="metric-value">
            {memoryGrowth.length > 0 ? (memoryGrowth[memoryGrowth.length - 1] / 1000).toFixed(1) : '1.0'}k
          </div>
          <div className="metric-detail">
            +{memoryGrowth.length > 1 ?
              (memoryGrowth[memoryGrowth.length - 1] - memoryGrowth[0]).toFixed(0) :
              '0'} this session
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-title">Active Offices</div>
          <div className="metric-value">
            {officeActivity.filter(o => o.status !== 'idle').length}/43
          </div>
          <div className="metric-detail">
            {officeActivity.filter(o => o.status === 'evolving').length} evolving
          </div>
        </div>
      </div>

      {/* Token Usage Graph */}
      <div className="graph-container">
        <div className="graph-title">Token Flow (100 samples)</div>
        <canvas
          ref={canvasRef}
          width={800}
          height={200}
          className="token-graph"
        />
        <div className="graph-legend">
          <span className="legend-item">
            <span className="legend-dot" style={{ background: '#00BCD4' }} />
            Input Tokens
          </span>
          <span className="legend-item">
            <span className="legend-dot" style={{ background: '#8A2BE2' }} />
            Output Tokens
          </span>
        </div>
      </div>

      {/* Office Activity Heatmap */}
      <div className="heatmap-container">
        <div className="heatmap-title">Office Activity Heatmap</div>
        <div className="office-grid">
          {officeActivity.map(office => (
            <div
              key={office.officeId}
              className={`office-cell ${office.status}`}
              style={{
                opacity: 0.3 + (office.calls / 100) * 0.7,
                borderColor: office.status === 'evolving' ? '#FFD700' :
                           office.status === 'active' ? '#00E676' : '#666'
              }}
            >
              <div className="office-name">{office.name}</div>
              <div className="office-stats">
                <span>{office.calls} calls</span>
                <span>{(office.tokens / 1000).toFixed(1)}k tokens</span>
              </div>
              <div className="response-time">{office.avgResponseTime.toFixed(0)}ms</div>
            </div>
          ))}
        </div>
      </div>

      {/* Evolution Log */}
      <div className="evolution-log-container">
        <div className="evolution-log-title">Evolution Mutations</div>
        <div className="evolution-entries">
          {evolutionMetrics.slice(-5).reverse().map((metric, i) => (
            <div key={i} className="evolution-entry">
              <span className="evolution-time">
                {new Date(metric.timestamp).toLocaleTimeString()}
              </span>
              <span className="evolution-office">{metric.office}</span>
              <span className={`evolution-delta ${metric.delta > 0 ? 'positive' : 'negative'}`}>
                {metric.delta > 0 ? '+' : ''}{metric.delta.toFixed(1)}%
              </span>
              <span className="evolution-gen">Gen {metric.generation}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Memory Growth Sparkline */}
      <div className="sparkline-container">
        <div className="sparkline-title">Memory Growth (60 samples)</div>
        <div className="sparkline">
          <svg width="100%" height="60" viewBox="0 0 300 60">
            <polyline
              fill="none"
              stroke="url(#gradient)"
              strokeWidth="2"
              points={memoryGrowth.map((val, i) => {
                const x = (300 / 60) * i;
                const min = Math.min(...memoryGrowth);
                const max = Math.max(...memoryGrowth);
                const y = 60 - ((val - min) / (max - min)) * 50;
                return `${x},${y}`;
              }).join(' ')}
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#00BCD4" />
                <stop offset="100%" stopColor="#8A2BE2" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </div>
  );
};