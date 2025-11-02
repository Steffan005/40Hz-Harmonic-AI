#!/usr/bin/env python3
"""
Bandit Controller for selecting optimization strategies (arms).
Uses UCB1 with novelty penalty to encourage diverse mutations.
"""
from __future__ import annotations  # Defer type hint evaluation for np.ndarray

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Make sentence_transformers optional - use simple hash-based embeddings if not available
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    np = None  # Will use simple hash-based approach


class BanditController:
    """
    Multi-Armed Bandit (UCB1) for selecting optimization strategies.

    Arms:
        - textgrad: Gradient-based prompt optimization
        - aflow_stub: Workflow topology search (Monte Carlo Tree Search)
        - mipro_stub: Bayesian instruction tuning
        - random_jitter: Random perturbation baseline

    Reward: Δ(metric_main) from evaluator
    Novelty penalty: Cosine distance < 0.2 → penalize by 0.5
    """

    ARMS = ["textgrad", "aflow_stub", "mipro_stub", "random_jitter"]

    def __init__(
        self,
        beta: float = 1.0,
        novelty_threshold: float = 0.2,
        state_path: str = "./state/bandit.jsonl"
    ):
        self.beta = beta  # UCB1 exploration coefficient
        self.novelty_threshold = novelty_threshold
        self.state_path = Path(state_path)

        # Arm statistics
        self.arm_counts = {arm: 0 for arm in self.ARMS}
        self.arm_rewards = {arm: 0.0 for arm in self.ARMS}
        self.total_pulls = 0

        # History for novelty detection
        self.history_embeddings = []  # List of (arm, embedding, score)
        self.embedding_model = None  # Lazy load

        # Load persisted state
        self._load_state()

    def select_arm(self, current_embedding: Optional[np.ndarray] = None) -> str:
        """
        Select arm using UCB1 policy with novelty consideration.

        Args:
            current_embedding: Embedding of current workflow (for novelty check)

        Returns:
            arm_name: Selected strategy
        """
        self.total_pulls += 1

        # First: Ensure all arms pulled at least once
        unplayed_arms = [arm for arm, count in self.arm_counts.items() if count == 0]
        if unplayed_arms:
            return unplayed_arms[0]

        # Compute UCB1 scores
        ucb_scores = {}
        for arm in self.ARMS:
            avg_reward = self.arm_rewards[arm] / max(self.arm_counts[arm], 1)
            exploration_term = self.beta * math.sqrt(
                2 * math.log(self.total_pulls) / max(self.arm_counts[arm], 1)
            )
            ucb_scores[arm] = avg_reward + exploration_term

        # Apply novelty penalty
        if current_embedding is not None and len(self.history_embeddings) > 0:
            for arm in self.ARMS:
                # Check similarity to recent outputs from this arm
                arm_history = [
                    (emb, score) for a, emb, score in self.history_embeddings[-10:]
                    if a == arm
                ]

                if arm_history:
                    # Compute cosine similarity to most recent
                    most_recent_emb = arm_history[-1][0]
                    similarity = self._cosine_similarity(current_embedding, most_recent_emb)

                    # Penalize if too similar (low novelty)
                    if similarity > (1 - self.novelty_threshold):  # Similarity > 0.8
                        ucb_scores[arm] *= 0.5  # 50% penalty

        # Select arm with highest UCB score
        selected_arm = max(ucb_scores.items(), key=lambda x: x[1])[0]
        return selected_arm

    def update(
        self,
        arm: str,
        reward: float,
        embedding: Optional[np.ndarray] = None
    ):
        """
        Update arm statistics after observing reward.

        Args:
            arm: Selected arm
            reward: Observed reward (Δscore from evaluator)
            embedding: Output embedding for novelty tracking
        """
        self.arm_counts[arm] += 1
        self.arm_rewards[arm] += reward

        # Store embedding for novelty detection
        if embedding is not None:
            self.history_embeddings.append((arm, embedding, reward))

            # Keep last 50 entries
            if len(self.history_embeddings) > 50:
                self.history_embeddings = self.history_embeddings[-50:]

        # Persist state
        self._save_state(arm, reward)

    def get_stats(self) -> Dict:
        """Return bandit statistics."""
        stats = {
            "total_pulls": self.total_pulls,
            "arm_counts": self.arm_counts.copy(),
            "arm_rewards": self.arm_rewards.copy(),
            "arm_avg_rewards": {
                arm: self.arm_rewards[arm] / max(self.arm_counts[arm], 1)
                for arm in self.ARMS
            }
        }
        return stats

    def compute_novelty(self, embedding: np.ndarray) -> float:
        """
        Compute novelty score for given embedding.

        Returns:
            novelty: Minimum cosine distance to history (0-1, higher = more novel)
        """
        if len(self.history_embeddings) == 0:
            return 1.0  # Fully novel if no history

        # Compute distance to all historical embeddings
        distances = [
            1 - self._cosine_similarity(embedding, hist_emb)
            for _, hist_emb, _ in self.history_embeddings
        ]

        # Return minimum distance (most similar historical output)
        return min(distances) if distances else 1.0

    def _cosine_similarity(self, a, b) -> float:
        """Compute cosine similarity between two vectors (works with lists or numpy arrays)."""
        if SENTENCE_TRANSFORMERS_AVAILABLE and np is not None:
            # Use numpy if available (faster)
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
        else:
            # Simple Python fallback
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def get_embedding(self, text: str):
        """
        Generate embedding for text using sentence-transformers.
        Falls back to simple hash-based embedding if sentence-transformers not available.
        Lazy loads model on first use.
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            # Simple fallback: use hash-based pseudo-embedding
            import hashlib
            hash_bytes = hashlib.sha256(text.encode()).digest()
            # Convert to list of floats (normalized to [0, 1])
            embedding = [b / 255.0 for b in hash_bytes[:32]]  # 32-dim vector
            return embedding

        if self.embedding_model is None:
            print("Loading sentence-transformer model (first use)...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding

    def _load_state(self):
        """Load persisted bandit state from disk."""
        if not self.state_path.exists():
            return

        with open(self.state_path, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    arm = entry["arm"]
                    reward = entry["reward"]

                    self.arm_counts[arm] = entry.get("arm_count", 0)
                    self.arm_rewards[arm] = entry.get("arm_total_reward", 0)
                    self.total_pulls = entry.get("total_pulls", 0)

        print(f"Loaded bandit state: {self.arm_counts}")

    def _save_state(self, arm: str, reward: float):
        """Persist bandit state to disk (append-only log)."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": time.time(),
            "arm": arm,
            "reward": reward,
            "arm_count": self.arm_counts[arm],
            "arm_total_reward": self.arm_rewards[arm],
            "total_pulls": self.total_pulls
        }

        with open(self.state_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


# Example usage
if __name__ == "__main__":
    bandit = BanditController()

    print("="*60)
    print("BANDIT CONTROLLER TEST")
    print("="*60)

    # Simulate 20 arm selections with rewards
    for gen in range(20):
        # Generate dummy embedding for novelty test
        dummy_text = f"Generated output for generation {gen}"
        embedding = bandit.get_embedding(dummy_text)

        # Select arm
        arm = bandit.select_arm(current_embedding=embedding)

        # Simulate reward (random for demo)
        import random
        reward = random.uniform(-5, 10)  # Δscore

        # Update bandit
        bandit.update(arm, reward, embedding)

        # Compute novelty
        novelty = bandit.compute_novelty(embedding)

        print(f"Gen {gen+1:02d}: Arm={arm:15s} Reward={reward:+6.2f} Novelty={novelty:.3f}")

    # Print final statistics
    print("\n" + "="*60)
    print("BANDIT STATISTICS:")
    print(json.dumps(bandit.get_stats(), indent=2))
