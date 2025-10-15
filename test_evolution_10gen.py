#!/usr/bin/env python3
"""
Integration Test: 10-Generation Evolution Run
Tests all components together and collects metrics.
"""

import json
import time
import random
import hashlib
from pathlib import Path
from typing import List

# Import all components
from evaluator_v2 import EvaluatorV2
from bandit_controller import BanditController
from budget_manager import BudgetManager, BudgetExceededError
from memory_store import MemoryStore
from telemetry import Telemetry
from stop_rules import StopRules


class EvolutionRunner:
    """Orchestrates 10-generation evolution test."""

    def __init__(self):
        self.evaluator = EvaluatorV2()
        self.bandit = BanditController()
        self.budget = BudgetManager()
        self.memory = MemoryStore()
        self.telemetry = Telemetry()
        self.stop_rules = StopRules(max_generations=10, target_score=999.0)  # Disabled for full test run

        self.scores = []
        self.robustness_scores = []

    def run_generation(self, gen: int, goal: str) -> dict:
        """Run one evolution generation."""

        # Set seed for reproducibility
        seed = 42 + gen
        random.seed(seed)

        # Select arm using bandit
        current_embedding = self.bandit.get_embedding(f"gen_{gen}_output")
        arm = self.bandit.select_arm(current_embedding)

        # Simulate workflow mutation based on arm
        output = self._mutate_workflow(goal, arm, gen)

        # Hash workflow
        workflow_hash = hashlib.sha256(output.encode()).hexdigest()[:12]

        # Evaluate
        eval_start = time.time()
        eval_result = self.evaluator.evaluate(goal, output, rubric_version="v1")
        eval_time_ms = (time.time() - eval_start) * 1000

        score = eval_result["quality_score"]
        delta_score = score - self.scores[-1] if self.scores else score

        # Compute novelty
        novelty = self.bandit.compute_novelty(current_embedding)

        # Simulate robustness check (in real system, would run adversarial probes)
        robustness = self._check_robustness(output)

        # Update bandit with reward
        reward = delta_score / 10.0  # Normalize
        self.bandit.update(arm, reward, current_embedding)

        # Store in memory
        memory_id = self.memory.store(
            title=f"Generation {gen}",
            content=output,
            tags=["workflow", arm, f"gen_{gen}"]
        )

        # Log telemetry
        self.telemetry.log_generation(
            generation=gen,
            arm=arm,
            seed=seed,
            workflow_hash=workflow_hash,
            rubric_version="v1",
            delta_score=delta_score,
            tokens=self.budget.current_tokens,
            time_ms=eval_time_ms,
            cache_hit=eval_result["used_cache"],
            novelty=novelty,
            robust_pct=robustness,
            budget_flags=[]
        )

        # Record scores
        self.scores.append(score)
        self.robustness_scores.append(robustness)

        return {
            "gen": gen,
            "arm": arm,
            "score": score,
            "delta_score": delta_score,
            "novelty": novelty,
            "robustness": robustness,
            "eval_time_ms": eval_time_ms,
            "routing_path": eval_result["routing_path"],
            "used_cache": eval_result["used_cache"],
            "memory_id": memory_id
        }

    def _mutate_workflow(self, goal: str, arm: str, gen: int) -> str:
        """
        Simulate workflow mutation based on selected arm.
        In real system, this would call TextGrad, AFlow, etc.
        """
        base_output = f"Workflow for: {goal}\nGeneration: {gen}\nOptimization: {arm}\n"

        if arm == "textgrad":
            base_output += "Applied gradient-based prompt refinement.\n"
            base_output += "def optimized_function():\n    # TextGrad optimized code\n    return 'Improved output'\n"

        elif arm == "aflow_stub":
            base_output += "Applied MCTS workflow topology search.\n"
            base_output += "# New DAG structure:\n# Node1 -> Node2 -> Node3\n"

        elif arm == "mipro_stub":
            base_output += "Applied Bayesian instruction tuning.\n"
            base_output += "# Tuned hyperparameters: temperature=0.3, top_p=0.9\n"

        elif arm == "random_jitter":
            base_output += "Applied random perturbation.\n"
            base_output += f"# Random element: {random.randint(1, 100)}\n"

        # Add some variety to trigger different evaluation paths
        if gen % 3 == 0:
            base_output += "\n# Additional complexity for this generation\n"

        return base_output

    def _check_robustness(self, output: str) -> float:
        """
        Simulate robustness check (adversarial probes).
        Returns percentage (0-100).
        """
        # Simple heuristic: check for dangerous patterns
        from heuristics import HeuristicValidator

        validator = HeuristicValidator()
        result = validator.validate(output)

        # If any violations, robustness is low
        if result["violations"]:
            return 50.0  # Failed some probes

        # Otherwise, high robustness
        return random.uniform(80, 95)  # Simulate variation

    def run_full_test(self, goal: str = "Implement a task scheduling system"):
        """Run complete 10-generation test."""

        print("="*70)
        print("10-GENERATION EVOLUTION TEST")
        print("="*70)
        print(f"Goal: {goal}\n")

        results = []

        for gen in range(1, 11):
            try:
                with self.budget.BudgetGuard(generation=gen):
                    # Simulate token consumption
                    self.budget.consume_tokens(random.randint(800, 1500))

                    # Run generation
                    result = self.run_generation(gen, goal)

                    # Check stop rules
                    should_stop, reason = self.stop_rules.should_stop(
                        self.scores,
                        self.robustness_scores
                    )

                    result["stop_rule"] = reason
                    results.append(result)

                    # Print progress
                    print(f"Gen {gen:02d}: "
                          f"Arm={result['arm']:15s} "
                          f"Score={result['score']:5.1f} "
                          f"Δ={result['delta_score']:+5.1f} "
                          f"Novel={result['novelty']:.2f} "
                          f"Robust={result['robustness']:4.1f}% "
                          f"Cache={result['used_cache']} "
                          f"Path={result['routing_path']}")

                    if should_stop:
                        print(f"\n⏹  Stopped: {reason}")
                        break

            except BudgetExceededError as e:
                print(f"\n❌ Budget exceeded at Gen {gen}: {e}")
                break

        return results


def generate_report(runner: EvolutionRunner, results: List[dict]):
    """Generate comprehensive metrics report."""

    print("\n" + "="*70)
    print("METRICS REPORT")
    print("="*70)

    # 1. Evaluator stats
    eval_stats = runner.evaluator.get_stats()
    print("\n[1] EVALUATOR PERFORMANCE:")
    print(f"  Total evaluations: {eval_stats['total_evaluations']}")
    print(f"  Cache hit rate: {eval_stats['cache_hit_rate']:.1%}")
    print(f"  Heuristic routing rate: {eval_stats['heuristic_routing_rate']:.1%}")
    print(f"  LLM usage rate: {eval_stats['llm_usage_rate']:.1%}")

    # Compute latency reduction
    avg_eval_time = sum(r['eval_time_ms'] for r in results) / len(results)
    baseline_time = 2000  # Assume 2s baseline for full LLM judge
    latency_reduction = (1 - avg_eval_time / baseline_time) * 100
    print(f"  Avg eval time: {avg_eval_time:.0f}ms")
    print(f"  Latency reduction: {latency_reduction:.1f}% vs baseline")

    # 2. Bandit stats
    bandit_stats = runner.bandit.get_stats()
    print("\n[2] BANDIT ARM SELECTION:")
    for arm, count in bandit_stats['arm_counts'].items():
        avg_reward = bandit_stats['arm_avg_rewards'][arm]
        print(f"  {arm:15s}: {count:2d} pulls, avg reward={avg_reward:+5.2f}")

    # Check diversity (≥3 arms selected)
    arms_used = sum(1 for count in bandit_stats['arm_counts'].values() if count > 0)
    print(f"  Arms used: {arms_used}/4 ({'✓' if arms_used >= 3 else '✗'} diversity criterion)")

    # Mean novelty
    mean_novelty = sum(r['novelty'] for r in results) / len(results)
    print(f"  Mean novelty: {mean_novelty:.2f} ({'✓' if mean_novelty >= 0.2 else '✗'} threshold)")

    # 3. Budget compliance
    budget_status = runner.budget.get_status()
    print("\n[3] BUDGET COMPLIANCE:")
    print(f"  Tokens used: {budget_status['tokens_used']}/{budget_status['tokens_limit']}")
    print(f"  Time elapsed: {budget_status['time_elapsed_s']:.1f}s/{budget_status['time_limit_s']}s")
    print(f"  Max agents: {budget_status['active_agents']}/{budget_status['agent_limit']}")
    print(f"  Aborted: {'✗ No' if not budget_status['aborted'] else '✓ Yes'}")

    # 4. Robustness
    avg_robustness = sum(r['robustness'] for r in results) / len(results)
    print("\n[4] ROBUSTNESS:")
    print(f"  Average: {avg_robustness:.1f}%")
    print(f"  Min: {min(r['robustness'] for r in results):.1f}%")
    print(f"  Max: {max(r['robustness'] for r in results):.1f}%")

    # 5. HITL cases
    hitl_cases = [r for r in results if "HITL" in r.get('stop_rule', '')]
    print("\n[5] HITL CASES:")
    if hitl_cases:
        for case in hitl_cases:
            print(f"  Gen {case['gen']}: {case['stop_rule']}")
    else:
        print("  None")

    # Save metrics to file
    metrics_path = Path("./logs/test_metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metrics_path, 'w') as f:
        json.dump({
            "evaluator": eval_stats,
            "bandit": bandit_stats,
            "budget": budget_status,
            "robustness": {
                "avg": avg_robustness,
                "min": min(r['robustness'] for r in results),
                "max": max(r['robustness'] for r in results)
            },
            "results": results
        }, f, indent=2)

    print(f"\n✅ Metrics saved to: {metrics_path}")


if __name__ == "__main__":
    runner = EvolutionRunner()
    results = runner.run_full_test()
    generate_report(runner, results)

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
