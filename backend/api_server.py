#!/usr/bin/env python3
"""
EvoAgentX Backend API Server
Exposes REST endpoints for GUI to call evaluation, mutation, bandit, memory, telemetry
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluator_v2 import EvaluatorV2
from bandit_controller import BanditController
from budget_manager import BudgetManager, BudgetExceededError
from memory_store import MemoryStore
from telemetry import Telemetry

app = Flask(__name__)
CORS(app)  # Enable CORS for Tauri

# Initialize all modules
evaluator = EvaluatorV2()
bandit = BanditController()
budget = BudgetManager()
memory = MemoryStore()
telemetry = Telemetry()

# Global state
current_generation = 0
latest_metrics = {
    "tokens_per_sec": 0.0,
    "delta_score": 0.0,
    "cache_hit_rate": 0.0,
    "robust_pct": 0.0,
    "memory_use_mb": 0.0,
    "module_status": {
        "evaluator": "healthy",
        "bandit": "healthy",
        "budget": "healthy",
        "memory": "healthy",
        "telemetry": "healthy"
    }
}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "OK",
        "timestamp": time.time(),
        "services": {
            "evaluator": "running",
            "bandit": "running",
            "memory": "running",
            "telemetry": "running"
        }
    })


@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Evaluate workflow output"""
    global current_generation, latest_metrics

    try:
        data = request.json
        goal = data.get('goal', '')
        output = data.get('output', '')
        rubric_version = data.get('rubric_version', 'v1')

        # Evaluate
        start_time = time.time()
        result = evaluator.evaluate(goal, output, rubric_version)
        eval_time_ms = (time.time() - start_time) * 1000

        # Compute delta score (simple: compare to 0 if first run)
        delta_score = result['quality_score'] - latest_metrics['delta_score']

        # Estimate robustness (from heuristics or fixed for now)
        robust_pct = 85.0 if not result.get('violations') else 50.0

        # Update metrics
        stats = evaluator.get_stats()
        latest_metrics['cache_hit_rate'] = stats.get('cache_hit_rate', 0.0)
        latest_metrics['delta_score'] = result['quality_score']
        latest_metrics['robust_pct'] = robust_pct

        # Log telemetry
        current_generation += 1
        telemetry.log_generation(
            generation=current_generation,
            arm="manual",
            seed=int(time.time()),
            workflow_hash="manual_eval",
            rubric_version=rubric_version,
            delta_score=delta_score,
            tokens=budget.current_tokens,
            time_ms=eval_time_ms,
            cache_hit=result.get('used_cache', False),
            novelty=0.0,
            robust_pct=robust_pct,
            budget_flags=[]
        )

        return jsonify({
            "quality_score": result['quality_score'],
            "delta_score": delta_score,
            "robust_pct": robust_pct,
            "cache_hit": result.get('used_cache', False),
            "time_ms": eval_time_ms,
            "routing_path": result.get('routing_path', 'unknown'),
            "violations": result.get('violations', [])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/mutate', methods=['POST'])
def mutate():
    """Mutate workflow using selected arm"""
    global current_generation, latest_metrics

    try:
        data = request.json
        goal = data.get('goal', '')
        current_workflow = data.get('current_workflow', '')
        arm_override = data.get('arm')  # "auto" or specific arm

        # Select arm
        if arm_override and arm_override != "auto":
            arm = arm_override
        else:
            # Use bandit to select
            embedding = bandit.get_embedding(f"gen_{current_generation}_workflow")
            arm = bandit.select_arm(embedding)

        # Simulate mutation (in real system, would call TextGrad/AFlow)
        variant_id = f"variant_{current_generation}_{int(time.time())}"
        mutated_workflow = f"{current_workflow}\n# Mutation by {arm}\n"

        # Compute novelty
        embedding = bandit.get_embedding(mutated_workflow)
        novelty = bandit.compute_novelty(embedding)

        # Update bandit (with dummy reward for now)
        reward = 0.5  # Would normally be delta_score/10.0
        bandit.update(arm, reward, embedding)

        # Delta score (simulated)
        delta_score = 2.5

        latest_metrics['delta_score'] = delta_score

        return jsonify({
            "variant_id": variant_id,
            "arm": arm,
            "delta_score": delta_score,
            "novelty": novelty,
            "workflow": mutated_workflow
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/bandit/status', methods=['GET'])
def bandit_status():
    """Get bandit controller status"""
    try:
        stats = bandit.get_stats()
        return jsonify({
            "arm_counts": stats['arm_counts'],
            "arm_rewards": stats['arm_rewards'],
            "total_pulls": stats['total_pulls']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/bandit/policy', methods=['PATCH'])
def update_bandit_policy():
    """Update bandit policy (e.g., UCB beta)"""
    try:
        data = request.json
        ucb_beta = data.get('ucb_beta')

        if ucb_beta is not None:
            bandit.beta = ucb_beta

        return jsonify({"status": "updated", "ucb_beta": bandit.beta})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/memory/snapshot', methods=['POST'])
def memory_snapshot():
    """Create memory snapshot"""
    try:
        data = request.json
        title = data.get('title', 'Snapshot')
        content = data.get('content', '')

        memory_id = memory.store(title, content, tags=["snapshot"])

        # Get TOC entry
        toc = memory.get_toc(limit=1)
        entry = toc[-1] if toc else None

        return jsonify({
            "id": memory_id,
            "title": entry.get('title') if entry else title,
            "note": entry.get('note') if entry else content[:100],
            "timestamp": time.time()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/workflow/dag', methods=['GET'])
def workflow_dag():
    """Get workflow DAG structure (stub for now)"""
    try:
        # Return a sample fractal DAG
        dag = {
            "nodes": [
                {"id": "eval1", "node_type": "evaluator", "label": "Evaluator", "position": {"x": 100, "y": 100}},
                {"id": "mutate1", "node_type": "mutator", "label": "TextGrad", "position": {"x": 300, "y": 100}},
                {"id": "mutate2", "node_type": "mutator", "label": "AFlow", "position": {"x": 300, "y": 200}},
                {"id": "bandit1", "node_type": "bandit", "label": "Bandit", "position": {"x": 500, "y": 150}},
                {"id": "memory1", "node_type": "memory", "label": "Memory", "position": {"x": 500, "y": 250}},
            ],
            "edges": [
                {"from": "eval1", "to": "mutate1", "label": "score"},
                {"from": "eval1", "to": "mutate2", "label": "score"},
                {"from": "mutate1", "to": "bandit1", "label": "variant"},
                {"from": "mutate2", "to": "bandit1", "label": "variant"},
                {"from": "bandit1", "to": "memory1", "label": "selected"},
            ]
        }

        return jsonify(dag)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/telemetry/metrics', methods=['GET'])
def telemetry_metrics():
    """Get current telemetry metrics"""
    try:
        # Update tokens/sec estimate
        if budget.current_tokens > 0 and budget.start_time:
            elapsed = time.time() - budget.start_time
            latest_metrics['tokens_per_sec'] = budget.current_tokens / max(elapsed, 1.0)

        # Memory usage (MB)
        import psutil
        process = psutil.Process()
        latest_metrics['memory_use_mb'] = process.memory_info().rss / 1024 / 1024

        return jsonify(latest_metrics)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("="*70)
    print("EVOAGENTX BACKEND API SERVER")
    print("="*70)
    print("Starting on http://127.0.0.1:8000")
    print()
    print("Endpoints:")
    print("  GET  /health")
    print("  POST /evaluate")
    print("  POST /mutate")
    print("  GET  /bandit/status")
    print("  PATCH /bandit/policy")
    print("  POST /memory/snapshot")
    print("  GET  /workflow/dag")
    print("  GET  /telemetry/metrics")
    print("="*70)
    print()

    app.run(host='127.0.0.1', port=8000, debug=False)
