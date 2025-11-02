// EvoAgentX API Client
// Communicates with Tauri backend via IPC

import { invoke } from '@tauri-apps/api/tauri';

// Check if running in Tauri or browser
const isTauri = () => {
  return typeof window !== 'undefined' && '__TAURI__' in window;
};

export interface DiagnosticsResult {
  status: string;
  checks: Record<string, CheckResult>;
  timestamp: number;
}

export interface CheckResult {
  passed: boolean;
  message: string;
  severity: string;
}

export interface EvaluateRequest {
  goal: string;
  output: string;
  rubric_version: string;
}

export interface EvaluateResponse {
  quality_score: number;
  delta_score: number;
  robust_pct: number;
  cache_hit: boolean;
  time_ms: number;
  routing_path: string;
  violations: string[];
}

export interface MutateRequest {
  goal: string;
  current_workflow: string;
  arm?: string;
}

export interface MutateResponse {
  variant_id: string;
  arm: string;
  delta_score: number;
  novelty: number;
  workflow: string;
}

export interface BanditStatus {
  arm_counts: Record<string, number>;
  arm_rewards: Record<string, number>;
  total_pulls: number;
}

export interface MemorySnapshot {
  id: string;
  title: string;
  note: string;
  timestamp: number;
}

export interface WorkflowDAG {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface WorkflowNode {
  id: string;
  node_type: string;
  label: string;
  position: { x: number; y: number };
}

export interface WorkflowEdge {
  from: string;
  to: string;
  label?: string;
}

export interface TelemetryMetrics {
  tokens_per_sec: number;
  delta_score: number;
  cache_hit_rate: number;
  robust_pct: number;
  memory_use_mb: number;
  module_status: Record<string, string>;
}

export const api = {
  async runDiagnostics(): Promise<DiagnosticsResult> {
    return invoke<DiagnosticsResult>('run_diagnostics');
  },

  async isPreflightPassed(): Promise<boolean> {
    if (!isTauri()) {
      // In browser mode, assume preflight passed
      return Promise.resolve(true);
    }
    return invoke<boolean>('is_preflight_passed');
  },

  async evaluate(request: EvaluateRequest): Promise<EvaluateResponse> {
    return invoke<EvaluateResponse>('evaluate', { request });
  },

  async mutateWorkflow(request: MutateRequest): Promise<MutateResponse> {
    return invoke<MutateResponse>('mutate_workflow', { request });
  },

  async getBanditStatus(): Promise<BanditStatus> {
    return invoke<BanditStatus>('get_bandit_status');
  },

  async createMemorySnapshot(title: string, content: string): Promise<MemorySnapshot> {
    return invoke<MemorySnapshot>('create_memory_snapshot', { title, content });
  },

  async getWorkflowDAG(): Promise<WorkflowDAG> {
    return invoke<WorkflowDAG>('get_workflow_dag');
  },

  async getTelemetryMetrics(): Promise<TelemetryMetrics> {
    if (!isTauri()) {
      // In browser mode, return simulated metrics
      return Promise.resolve({
        tokens_per_sec: 0,
        delta_score: 2.5,
        cache_hit_rate: 0.5,
        robust_pct: 0.85,
        memory_use_mb: 33,
        module_status: {
          orchestrator: 'online',
          evolution: 'online',
          telemetry: 'online'
        }
      });
    }
    return invoke<TelemetryMetrics>('get_telemetry_metrics');
  },
};
