#!/usr/bin/env python3
"""
Telemetry - Logs evolution metrics to JSONL.
Records seeds, versions, and all key metrics per generation.
"""

import json
import time
import hashlib
import platform
from pathlib import Path
from typing import Dict, Optional, List
import sys


class Telemetry:
    """Structured logging of evolution runs."""

    def __init__(self, log_path: str = "./logs/evolution.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self.run_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]
        self.versions = self._capture_versions()

    def log_generation(
        self,
        generation: int,
        arm: str,
        seed: int,
        workflow_hash: str,
        rubric_version: str,
        delta_score: float,
        tokens: int,
        time_ms: float,
        cache_hit: bool,
        novelty: float,
        robust_pct: Optional[float] = None,
        budget_flags: List[str] = None
    ):
        """
        Log metrics for one generation to JSONL.

        Args:
            generation: Generation number
            arm: Selected optimization strategy
            seed: Random seed used
            workflow_hash: Hash of workflow structure
            rubric_version: Evaluation rubric version
            delta_score: Change in score from previous generation
            tokens: Total tokens consumed
            time_ms: Execution time in milliseconds
            cache_hit: Whether evaluator used cache
            novelty: Novelty score (0-1)
            robust_pct: Robustness percentage (0-100)
            budget_flags: List of budget violations
        """
        entry = {
            "run_id": self.run_id,
            "ts": time.time(),
            "gen": generation,
            "arm": arm,
            "seed": seed,
            "workflow_hash": workflow_hash,
            "rubric_v": rubric_version,
            "Δscore": delta_score,
            "tokens": tokens,
            "time_ms": time_ms,
            "cache_hit": cache_hit,
            "novelty": novelty,
            "robust_pct": robust_pct or 0.0,
            "budget_flags": budget_flags or [],
            "versions": self.versions
        }

        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def _capture_versions(self) -> Dict:
        """Capture tool/library versions for reproducibility."""
        versions = {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        }

        # Try to get package versions
        try:
            import litellm
            versions["litellm"] = getattr(litellm, "__version__", "unknown")
        except:
            pass

        try:
            import evoagentx
            versions["evoagentx"] = getattr(evoagentx, "__version__", "unknown")
        except:
            pass

        try:
            from sentence_transformers import __version__ as st_version
            versions["sentence_transformers"] = st_version
        except:
            pass

        return versions


# Example
if __name__ == "__main__":
    telemetry = Telemetry()

    # Log 3 test generations
    for gen in range(3):
        telemetry.log_generation(
            generation=gen + 1,
            arm="textgrad",
            seed=42 + gen,
            workflow_hash=f"hash_{gen}",
            rubric_version="v1",
            delta_score=gen * 2.5,
            tokens=1500,
            time_ms=2340.5,
            cache_hit=gen % 2 == 0,
            novelty=0.7,
            robust_pct=85.3,
            budget_flags=[]
        )

    print(f"✅ Logged 3 generations to {telemetry.log_path}")
    print(f"Run ID: {telemetry.run_id}")
    print(f"Versions: {json.dumps(telemetry.versions, indent=2)}")
