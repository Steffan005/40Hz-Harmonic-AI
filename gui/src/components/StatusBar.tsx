// StatusBar Component - Displays real-time telemetry
import { useEffect, useState } from 'react';
import { api, TelemetryMetrics } from '../lib/api';
import '../styles/status-bar.css';

export function StatusBar() {
  const [metrics, setMetrics] = useState<TelemetryMetrics>({
    tokens_per_sec: 0,
    delta_score: 0,
    cache_hit_rate: 0,
    robust_pct: 0,
    memory_use_mb: 0,
    module_status: {},
  });

  const [isLoading, setIsLoading] = useState(false);

  // Poll telemetry every 5 seconds (reduced from 1s for performance)
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        setIsLoading(true);
        const latest = await api.getTelemetryMetrics();
        setMetrics(latest);
      } catch (err) {
        console.error('Failed to fetch telemetry:', err);
      } finally {
        setIsLoading(false);
      }
    }, 5000); // 5 seconds instead of 1

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-bar-horizontal">
      <div className="status-metric-compact">
        <span className="metric-icon">⚡</span>
        <span className="metric-text">{metrics.tokens_per_sec.toFixed(1)} tok/s</span>
      </div>

      <div className="status-metric-compact">
        <span className="metric-icon">📈</span>
        <span className="metric-text" style={{ color: metrics.delta_score >= 0 ? '#00E676' : '#FF1744' }}>
          {metrics.delta_score >= 0 ? '+' : ''}{metrics.delta_score.toFixed(1)}
        </span>
      </div>

      <div className="status-metric-compact">
        <span className="metric-icon">💾</span>
        <span className="metric-text">{(metrics.cache_hit_rate * 100).toFixed(0)}%</span>
      </div>

      <div className="status-metric-compact">
        <span className="metric-icon">🎯</span>
        <span className="metric-text">{metrics.robust_pct.toFixed(0)}%</span>
      </div>

      <div className="status-metric-compact">
        <span className="metric-icon">🧠</span>
        <span className="metric-text">{metrics.memory_use_mb.toFixed(0)}MB</span>
      </div>

      {isLoading && <div className="spinner-tiny" />}
    </div>
  );
}
