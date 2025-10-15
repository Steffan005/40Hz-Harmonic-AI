#!/usr/bin/env python3
"""
Stop Rules - Determines when to halt evolution.
Uses t-test for stagnation detection and safety plateau checks.
"""

import numpy as np
from scipy import stats
from typing import List, Tuple, Optional


class StopRules:
    """
    Advanced stop conditions with statistical testing.

    Conditions:
    1. Max generations reached
    2. Target score achieved
    3. Stagnation (t-test shows no improvement)
    4. Safety plateau (robustness drops while score increases)
    5. Budget exceeded (handled by BudgetManager)
    """

    def __init__(
        self,
        max_generations: int = 10,
        target_score: float = 90.0,
        stagnation_window: int = 5,
        stagnation_pvalue: float = 0.2,
        stagnation_uplift_threshold: float = 0.5,
        stagnation_patience: int = 3,
        safety_drop_threshold: float = 0.1
    ):
        self.max_generations = max_generations
        self.target_score = target_score
        self.stagnation_window = stagnation_window
        self.stagnation_pvalue = stagnation_pvalue
        self.stagnation_uplift_threshold = stagnation_uplift_threshold
        self.stagnation_patience = stagnation_patience
        self.safety_drop_threshold = safety_drop_threshold

        self.stagnation_flags = 0
        self.baseline_scores = []

    def should_stop(
        self,
        scores: List[float],
        robustness_scores: Optional[List[float]] = None
    ) -> Tuple[bool, str]:
        """
        Determine if evolution should stop.

        Args:
            scores: List of quality scores (one per generation)
            robustness_scores: Optional list of robustness scores

        Returns:
            (should_stop, reason)
        """
        current_gen = len(scores)

        # Rule 1: Max generations
        if current_gen >= self.max_generations:
            return True, f"max_generations:{self.max_generations}"

        # Rule 2: Target achieved
        if scores[-1] >= self.target_score:
            return True, f"target_achieved:{scores[-1]:.1f}>={self.target_score}"

        # Rule 3: Stagnation detection (need at least stagnation_window + 2 gens)
        if current_gen >= self.stagnation_window + 2:
            is_stagnant = self._detect_stagnation(scores)
            if is_stagnant:
                self.stagnation_flags += 1
                if self.stagnation_flags >= self.stagnation_patience:
                    return True, f"stagnation:{self.stagnation_flags}_consecutive_flags"
            else:
                self.stagnation_flags = 0  # Reset

        # Rule 4: Safety plateau (robustness dropping while score increasing)
        if robustness_scores and len(robustness_scores) >= 3:
            is_unsafe_plateau = self._detect_safety_plateau(scores, robustness_scores)
            if is_unsafe_plateau:
                return True, "safety_plateau:HITL_required"

        return False, ""

    def _detect_stagnation(self, scores: List[float]) -> bool:
        """
        Use t-test to detect stagnation.

        Compare last N scores to baseline (first few generations).
        If p > 0.2 AND uplift < 0.5, flag as stagnant.
        """
        # Baseline: first few generations (or first half if < 10 gens)
        if not self.baseline_scores:
            baseline_size = min(3, len(scores) // 2)
            self.baseline_scores = scores[:baseline_size]

        # Recent: last N generations
        recent_scores = scores[-self.stagnation_window:]

        # T-test: are recent scores significantly different from baseline?
        if len(self.baseline_scores) >= 2 and len(recent_scores) >= 2:
            try:
                t_stat, p_value = stats.ttest_ind(recent_scores, self.baseline_scores)

                # Check uplift
                mean_recent = np.mean(recent_scores)
                mean_baseline = np.mean(self.baseline_scores)
                uplift = mean_recent - mean_baseline

                # Stagnation criteria
                if p_value > self.stagnation_pvalue and uplift < self.stagnation_uplift_threshold:
                    return True

            except Exception as e:
                # If t-test fails (e.g., identical values), check simple variance
                variance = np.var(recent_scores)
                if variance < 0.01:  # Essentially flat
                    return True

        return False

    def _detect_safety_plateau(
        self,
        scores: List[float],
        robustness_scores: List[float]
    ) -> bool:
        """
        Detect if score is increasing while robustness is decreasing.
        This suggests overfitting or gaming the metric.
        """
        # Compare last 3 vs previous 3
        if len(scores) < 6:
            return False

        recent_scores = scores[-3:]
        prev_scores = scores[-6:-3]

        recent_robust = robustness_scores[-3:]
        prev_robust = robustness_scores[-6:-3]

        # Check trends
        score_trend = np.mean(recent_scores) - np.mean(prev_scores)
        robust_trend = np.mean(recent_robust) - np.mean(prev_robust)

        # Safety plateau: score ↑ but robustness ↓
        if score_trend > 1.0 and robust_trend < -self.safety_drop_threshold * 100:
            return True

        return False


# Example usage
if __name__ == "__main__":
    stop_rules = StopRules(max_generations=15, stagnation_patience=2)

    # Simulate score progression
    test_scores = [
        65.0, 68.0, 72.0,  # Improving
        75.0, 76.0, 76.5,  # Slowing
        77.0, 77.2, 77.1,  # Stagnating
        77.3, 77.2, 77.4,  # Still stagnant
        77.5, 77.6, 77.7   # Marginal
    ]

    print("Testing stop rules...")
    for i, score in enumerate(test_scores, 1):
        scores_so_far = test_scores[:i]
        should_stop, reason = stop_rules.should_stop(scores_so_far)

        print(f"Gen {i:02d}: Score={score:.1f} | Stop={should_stop} | Reason={reason}")

        if should_stop:
            break
