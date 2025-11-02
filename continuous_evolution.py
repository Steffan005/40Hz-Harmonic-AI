#!/usr/bin/env python3
"""
Continuous Evolution Loop - The City's Heartbeat

Runs the evaluate → mutate → bandit cycle continuously on a validation set,
logging all proposals to changes.md for human approval before filesystem writes.

This is the self-improvement engine of the quantum city.
"""

import time
import json
import random
import argparse
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from evaluator_v2 import EvaluatorV2
from bandit_controller import BanditController
from budget_manager import BudgetManager, BudgetExceededError
from memory_store import MemoryStore
from telemetry import Telemetry
from diff_proposal_manager import DiffProposalManager


class ContinuousEvolutionEngine:
    """
    The quantum city's self-improvement heartbeat.

    Continuously generates workflow variants, evaluates them,
    and proposes improvements via the conscious veto system (changes.md).
    """

    def __init__(
        self,
        max_generations: int = 100,
        validation_set_size: int = 10,
        auto_apply: bool = False
    ):
        self.max_generations = max_generations
        self.validation_set_size = validation_set_size
        self.auto_apply = auto_apply

        # Initialize modules
        self.evaluator = EvaluatorV2()
        self.bandit = BanditController()
        self.budget = BudgetManager()
        self.memory = MemoryStore()
        self.telemetry = Telemetry()
        self.diff_manager = DiffProposalManager()

        # State
        self.generation = 0
        self.best_score = 0.0
        self.best_workflow = None
        self.improvement_history = []

        # Validation set (simple math problems for demo)
        self.validation_set = self._create_validation_set()

    def _create_validation_set(self) -> List[Dict]:
        """
        Create a small validation set of test cases.

        In production, this would be real user tasks or benchmarks.
        For demo, using simple math problems.
        """
        problems = [
            {"goal": "Calculate 2 + 2", "expected": "4"},
            {"goal": "Calculate 10 * 5", "expected": "50"},
            {"goal": "Calculate 100 / 4", "expected": "25"},
            {"goal": "Calculate 7 - 3", "expected": "4"},
            {"goal": "Calculate square root of 16", "expected": "4"},
            {"goal": "Calculate 2^8", "expected": "256"},
            {"goal": "Calculate factorial of 5", "expected": "120"},
            {"goal": "Calculate GCD of 12 and 8", "expected": "4"},
            {"goal": "Calculate LCM of 4 and 6", "expected": "12"},
            {"goal": "Calculate sum of first 10 integers", "expected": "55"},
        ]

        return problems[:self.validation_set_size]

    def run_generation(self) -> Dict:
        """
        Run one generation of the evolution loop.

        Returns:
            Generation results dict
        """
        self.generation += 1
        print(f"\n{'='*70}")
        print(f"GENERATION {self.generation}/{self.max_generations}")
        print(f"{'='*70}")

        # Select arm using bandit
        embedding = self.bandit.get_embedding(f"gen_{self.generation}")
        arm = self.bandit.select_arm(embedding)
        print(f"Bandit selected: {arm}")

        # Generate workflow variant
        workflow_variant = self._generate_variant(arm)
        print(f"Generated variant: {len(workflow_variant)} chars")

        # Evaluate on validation set
        total_score = 0.0
        scores = []

        for i, test_case in enumerate(self.validation_set):
            score = self._evaluate_workflow(workflow_variant, test_case)
            scores.append(score)
            total_score += score

        avg_score = total_score / len(self.validation_set)
        delta_score = avg_score - self.best_score

        print(f"Average score: {avg_score:.2f} (Δ: {delta_score:+.2f})")

        # Compute novelty
        novelty = self.bandit.compute_novelty(embedding)
        print(f"Novelty: {novelty:.3f}")

        # Update bandit
        normalized_reward = max(0.0, min(1.0, avg_score / 100.0))
        self.bandit.update(arm, normalized_reward, embedding)

        # If improvement, create diff proposal
        if delta_score > 0:
            print(f"✨ IMPROVEMENT DETECTED: +{delta_score:.2f}")
            self.best_score = avg_score
            self.best_workflow = workflow_variant

            # Create diff proposal
            proposal_id = self.diff_manager.propose_change(
                variant_id=f"variant_{self.generation}",
                arm=arm,
                predicted_delta=delta_score,
                file_path="workflow_best.py",
                old_content=self.best_workflow or "",
                new_content=workflow_variant,
                rationale=f"{arm} mutation improved average score from {avg_score - delta_score:.2f} to {avg_score:.2f}"
            )

            print(f"📝 Diff proposal created: {proposal_id}")
            print(f"   Review in changes.md and mark [APPLY] to execute")

            self.improvement_history.append({
                "generation": self.generation,
                "arm": arm,
                "delta_score": delta_score,
                "avg_score": avg_score,
                "proposal_id": proposal_id
            })

        # Log telemetry
        self.telemetry.log_generation(
            generation=self.generation,
            arm=arm,
            seed=random.randint(1, 10000),
            workflow_hash=f"variant_{self.generation}",
            rubric_version="v1",
            delta_score=delta_score,
            tokens=len(workflow_variant.split()),
            time_ms=0.0,  # Would measure in production
            cache_hit=False,
            novelty=novelty,
            robust_pct=avg_score,
            budget_flags=[]
        )

        return {
            "generation": self.generation,
            "arm": arm,
            "avg_score": avg_score,
            "delta_score": delta_score,
            "novelty": novelty,
            "best_score": self.best_score
        }

    def _generate_variant(self, arm: str) -> str:
        """
        Generate workflow variant using specified arm.

        Args:
            arm: Mutation strategy (textgrad, aflow, mipro, random_jitter)

        Returns:
            Workflow variant as string
        """
        # Stub implementation - in production would call actual TextGrad/AFlow
        base_workflow = self.best_workflow or "def solve(problem):\n    return eval(problem)\n"

        variants = {
            "textgrad": f"{base_workflow}\n# TextGrad: Added gradient-based optimization\n",
            "aflow_stub": f"{base_workflow}\n# AFlow: Added automated workflow composition\n",
            "mipro_stub": f"{base_workflow}\n# MIPRO: Added multi-turn prompting\n",
            "random_jitter": f"{base_workflow}\n# Random: Added exploration jitter\n"
        }

        return variants.get(arm, base_workflow)

    def _evaluate_workflow(self, workflow: str, test_case: Dict) -> float:
        """
        Evaluate workflow on a single test case.

        Args:
            workflow: Workflow code
            test_case: Test case dict with 'goal' and 'expected'

        Returns:
            Quality score (0-100)
        """
        # Stub evaluation - in production would actually execute workflow
        # For now, return random score weighted by generation
        base_score = 70.0 + (self.generation * 0.5)  # Gradual improvement
        noise = random.uniform(-5.0, 5.0)
        return min(100.0, max(0.0, base_score + noise))

    def run(self):
        """Run the continuous evolution loop."""
        print("="*70)
        print("CONTINUOUS EVOLUTION ENGINE - STARTING")
        print("="*70)
        print(f"Max generations: {self.max_generations}")
        print(f"Validation set size: {self.validation_set_size}")
        print(f"Auto-apply: {self.auto_apply}")
        print()

        start_time = time.time()

        try:
            for gen in range(self.max_generations):
                result = self.run_generation()

                # Budget checking happens via BudgetGuard context manager
                # For now, we run without budget enforcement in continuous mode

                # Execute approved changes periodically
                if (gen + 1) % 10 == 0:
                    print("\n📋 Checking for approved changes...")
                    executed = self.diff_manager.execute_approved_changes()
                    if executed:
                        print(f"✅ Executed {len(executed)} approved changes")

                # Brief pause
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n⏸️  Evolution paused by user")

        elapsed = time.time() - start_time

        # Final report
        print("\n" + "="*70)
        print("EVOLUTION COMPLETE")
        print("="*70)
        print(f"Generations completed: {self.generation}")
        print(f"Time elapsed: {elapsed:.1f}s")
        print(f"Best score achieved: {self.best_score:.2f}")
        print(f"Improvements found: {len(self.improvement_history)}")
        print()

        # Bandit statistics
        stats = self.bandit.get_stats()
        print("Bandit Arm Statistics:")
        for arm, count in stats['arm_counts'].items():
            reward = stats['arm_rewards'].get(arm, 0.0)
            avg_reward = reward / max(count, 1)
            print(f"  {arm:15s}: {count:3d} pulls, {avg_reward:.3f} avg reward")
        print()

        # Diff proposal statistics
        diff_stats = self.diff_manager.get_stats()
        print("Diff Proposal Statistics:")
        print(f"  Total proposals: {diff_stats['total_proposals']}")
        print(f"  Applied: {diff_stats['applied']}")
        print(f"  Rejected: {diff_stats['rejected']}")
        print(f"  Deferred: {diff_stats['deferred']}")
        print(f"  Pending: {diff_stats['pending']}")
        print(f"  Acceptance rate: {diff_stats['acceptance_rate']:.1f}%")
        print()

        print("Evolution logs: logs/evolution.jsonl")
        print("Diff proposals: changes.md")
        print("\n🌌 Unity: All processes are one process 🌌\n")


def main():
    parser = argparse.ArgumentParser(description="Continuous Evolution Engine")
    parser.add_argument("--generations", type=int, default=100, help="Max generations")
    parser.add_argument("--validation-size", type=int, default=10, help="Validation set size")
    parser.add_argument("--auto-apply", action="store_true", help="Auto-apply all improvements (DANGEROUS)")

    args = parser.parse_args()

    engine = ContinuousEvolutionEngine(
        max_generations=args.generations,
        validation_set_size=args.validation_size,
        auto_apply=args.auto_apply
    )

    engine.run()


if __name__ == "__main__":
    main()
