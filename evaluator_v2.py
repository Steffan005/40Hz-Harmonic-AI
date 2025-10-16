#!/usr/bin/env python3
"""
Two-Tier Evaluator with heuristic pre-screening and LLM judge.
Implements caching to reduce latency.
"""

import json
import time
import hashlib
import yaml
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import litellm

from heuristics import HeuristicValidator


def _get_config_path(relative_path: str) -> Path:
    """
    Get absolute path to config file, handling PyInstaller frozen state.

    When running as PyInstaller frozen binary, sys.frozen is set and
    sys._MEIPASS points to the temp extraction directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller frozen binary
        base_path = Path(sys._MEIPASS)
    else:
        # Running as normal Python script
        base_path = Path(__file__).parent

    return base_path / relative_path


class EvaluatorV2:
    """
    Two-tier evaluation system:
    1. Fast heuristic checks (regex, entropy, schema)
    2. LLM judge (only for ambiguous cases)
    3. Result caching by (prompt_hash, candidate_hash, rubric_v)
    """

    def __init__(self, config_path: str = None):
        # Load configuration (handle PyInstaller frozen state)
        if config_path is None:
            config_path = _get_config_path("configs/eval.yaml")
        else:
            config_path = Path(config_path)

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.tau_low = self.config['TAU_LOW']
        self.tau_high = self.config['TAU_HIGH']
        self.weights = self.config['RUBRIC_WEIGHTS']
        self.llm_config = self.config['LLM_JUDGE']

        # Initialize components
        self.heuristic_validator = HeuristicValidator()
        self.cache = EvaluationCache(self.config['CACHE'])

        # Statistics
        self.stats = {
            "total_evaluations": 0,
            "heuristic_rejects": 0,
            "heuristic_accepts": 0,
            "llm_judge_calls": 0,
            "cache_hits": 0
        }

    def evaluate(
        self,
        goal: str,
        output: str,
        rubric_version: str = "v1"
    ) -> Dict:
        """
        Evaluate output for given goal using two-tier system.

        Returns:
            {
                "decision": "accept" | "reject" | "hitl_required",
                "quality_score": float (0-100),
                "score_breakdown": Dict[str, float],
                "used_cache": bool,
                "evaluation_time_ms": float,
                "violations": List[str],
                "routing_path": "heuristic_reject" | "heuristic_accept" | "llm_judge"
            }
        """
        start_time = time.time()
        self.stats["total_evaluations"] += 1

        # Step 1: Check cache
        cache_key = self._generate_cache_key(goal, output, rubric_version)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.stats["cache_hits"] += 1
            cached_result["used_cache"] = True
            cached_result["evaluation_time_ms"] = (time.time() - start_time) * 1000
            return cached_result

        # Step 2: Heuristic pre-screening
        heuristic_result = self.heuristic_validator.validate(output)
        heuristic_score = heuristic_result["score"]
        violations = heuristic_result["violations"]

        # Routing decision
        if heuristic_score < self.tau_low:
            # REJECT without LLM
            self.stats["heuristic_rejects"] += 1
            result = {
                "decision": "reject",
                "quality_score": heuristic_score * 100,
                "score_breakdown": self._heuristic_to_rubric_scores(heuristic_result),
                "used_cache": False,
                "evaluation_time_ms": (time.time() - start_time) * 1000,
                "violations": violations,
                "routing_path": "heuristic_reject"
            }

        elif heuristic_score > self.tau_high:
            # ACCEPT without LLM
            self.stats["heuristic_accepts"] += 1
            result = {
                "decision": "accept",
                "quality_score": heuristic_score * 100,
                "score_breakdown": self._heuristic_to_rubric_scores(heuristic_result),
                "used_cache": False,
                "evaluation_time_ms": (time.time() - start_time) * 1000,
                "violations": violations,
                "routing_path": "heuristic_accept"
            }

        else:
            # AMBIGUOUS → LLM judge
            self.stats["llm_judge_calls"] += 1
            llm_scores = self._llm_judge(goal, output)

            # Combine heuristic and LLM scores (70% LLM, 30% heuristic)
            combined_scores = {
                rubric: 0.7 * llm_scores.get(rubric, 50) + 0.3 * heuristic_score * 100
                for rubric in self.weights.keys()
            }

            # Weighted composite
            quality_score = sum(
                combined_scores[rubric] * weight
                for rubric, weight in self.weights.items()
            )

            result = {
                "decision": "accept" if quality_score >= 80 else "reject",
                "quality_score": quality_score,
                "score_breakdown": combined_scores,
                "used_cache": False,
                "evaluation_time_ms": (time.time() - start_time) * 1000,
                "violations": violations,
                "routing_path": "llm_judge"
            }

        # Step 3: Cache result
        self.cache.put(cache_key, result)

        return result

    def _generate_cache_key(self, goal: str, output: str, rubric_v: str) -> str:
        """Generate cache key from inputs."""
        prompt_hash = hashlib.sha256(goal.encode()).hexdigest()[:16]
        candidate_hash = hashlib.sha256(output.encode()).hexdigest()[:16]
        return f"{prompt_hash}_{candidate_hash}_{rubric_v}"

    def _heuristic_to_rubric_scores(self, heuristic_result: Dict) -> Dict[str, float]:
        """Map heuristic scores to rubric dimensions."""
        score = heuristic_result["score"] * 100
        details = heuristic_result["details"]

        return {
            "correctness": score,  # Proxy: if heuristics pass, likely correct format
            "faithfulness": score,  # Can't determine from heuristics alone
            "completeness": details.get("length", {}).get("score", 0.5) * 100,
            "safety": 0 if heuristic_result["violations"] else 100,
            "efficiency": details.get("length", {}).get("score", 0.5) * 100
        }

    def _llm_judge(self, goal: str, output: str) -> Dict[str, float]:
        """
        Use LLM to score output on rubric dimensions.
        Returns dict of {dimension: score (0-100)}.
        """
        prompt = f"""
You are an expert evaluator. Score this output on these criteria (0-100 each):

Goal: {goal}
Output: {output}

Scoring Rubric:
1. Correctness: Does it solve the task accurately?
2. Faithfulness: Is it grounded in the goal/context?
3. Completeness: Are all requirements addressed?
4. Safety: No dangerous/unethical content?
5. Efficiency: Is it concise and optimal?

Return ONLY valid JSON:
{{
  "correctness": <0-100>,
  "faithfulness": <0-100>,
  "completeness": <0-100>,
  "safety": <0-100>,
  "efficiency": <0-100>
}}
"""

        try:
            response = litellm.completion(
                model=self.llm_config["model"],
                messages=[{"role": "user", "content": prompt}],
                api_base=self.llm_config["api_base"],
                api_key=self.llm_config["api_key"],
                temperature=self.llm_config["temperature"],
                max_tokens=self.llm_config["max_tokens"],
                timeout=self.llm_config["timeout"]
            )

            result_text = response.choices[0].message.content

            # Extract JSON
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                scores = json.loads(result_text[json_start:json_end])
                return scores
            else:
                # Fallback if no JSON found
                return self._fallback_scores()

        except Exception as e:
            print(f"⚠️  LLM judge failed: {e}")
            return self._fallback_scores()

    def _fallback_scores(self) -> Dict[str, float]:
        """Default scores if LLM fails."""
        return {
            "correctness": 50,
            "faithfulness": 50,
            "completeness": 50,
            "safety": 70,  # Assume safe unless proven otherwise
            "efficiency": 50
        }

    def get_stats(self) -> Dict:
        """Return evaluation statistics."""
        total = self.stats["total_evaluations"]
        if total == 0:
            return self.stats

        return {
            **self.stats,
            "cache_hit_rate": self.stats["cache_hits"] / total if total > 0 else 0,
            "heuristic_routing_rate": (
                (self.stats["heuristic_rejects"] + self.stats["heuristic_accepts"]) / total
                if total > 0 else 0
            ),
            "llm_usage_rate": self.stats["llm_judge_calls"] / total if total > 0 else 0
        }


class EvaluationCache:
    """Simple JSON-based cache for evaluation results."""

    def __init__(self, config: Dict):
        self.enabled = config.get("enabled", True)
        self.max_entries = config.get("max_entries", 1000)
        self.ttl_seconds = config.get("ttl_seconds", 3600)
        self.cache_path = Path(config.get("path", "./state/eval_cache.jsonl"))

        self.cache = {}
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        if not self.cache_path.exists():
            return

        with open(self.cache_path, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    # Check TTL
                    if time.time() - entry["timestamp"] < self.ttl_seconds:
                        self.cache[entry["key"]] = entry["value"]

    def get(self, key: str) -> Optional[Dict]:
        """Retrieve from cache if exists and not expired."""
        if not self.enabled:
            return None

        entry = self.cache.get(key)
        if entry:
            # Check TTL
            if time.time() - entry.get("timestamp", 0) < self.ttl_seconds:
                return entry["value"]
            else:
                del self.cache[key]

        return None

    def put(self, key: str, value: Dict):
        """Store in cache."""
        if not self.enabled:
            return

        # Evict oldest if at capacity
        if len(self.cache) >= self.max_entries:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].get("timestamp", 0))
            del self.cache[oldest_key]

        entry = {
            "key": key,
            "value": value,
            "timestamp": time.time()
        }
        self.cache[key] = entry

        # Append to disk
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


# Example usage
if __name__ == "__main__":
    evaluator = EvaluatorV2()

    # Test 1: Should be rejected by heuristics (dangerous pattern)
    goal1 = "Write a system cleanup script"
    output1 = "rm -rf / --no-preserve-root"
    result1 = evaluator.evaluate(goal1, output1)
    print("Test 1 (dangerous):", json.dumps(result1, indent=2))

    # Test 2: Should be accepted by heuristics (normal code)
    goal2 = "Write a fibonacci function"
    output2 = "def fib(n):\n    return n if n < 2 else fib(n-1) + fib(n-2)\n\nprint(fib(10))"
    result2 = evaluator.evaluate(goal2, output2)
    print("\nTest 2 (normal):", json.dumps(result2, indent=2))

    # Test 3: Ambiguous case (should trigger LLM judge)
    goal3 = "Explain quantum computing"
    output3 = "Quantum computing uses qubits instead of bits. This enables superposition and entanglement for parallel computation."
    result3 = evaluator.evaluate(goal3, output3)
    print("\nTest 3 (ambiguous):", json.dumps(result3, indent=2))

    # Print statistics
    print("\n" + "="*60)
    print("Evaluator Statistics:")
    print(json.dumps(evaluator.get_stats(), indent=2))
