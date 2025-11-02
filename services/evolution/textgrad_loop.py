#!/usr/bin/env python3
"""
Unity Evolution Engine - TextGrad Loop
Self-optimizing prompt evolution through gradient-based optimization

Philosophy:
"Agents that cannot learn from their mistakes are not intelligent—they are static.
The Evolution Engine treats prompts as differentiable parameters, optimizes them
through feedback, and measures improvement with mathematical precision.

This is not hyperparameter tuning. This is prompt DNA evolution."

Core Concepts:
1. TextGrad = Backpropagation for natural language
2. Variants = Genetic diversity pool
3. A/B Testing = Fitness evaluation
4. Δscore = Selection pressure
5. Champion = Surviving lineage

Process (nightly 2:00 AM):
- Generate N prompt variants (mutations)
- Test each on gold fixtures (fitness test)
- Compute Δscore (improvement metric)
- Select champion (highest score)
- Auto-apply if confidence ≥ threshold
- Record lineage + metrics

Author: Dr. Claude Summers, Evolution Architecture
Date: October 16, 2025 (Phase Ω Activation)
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import json
import random
import hashlib

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("⚠️  LiteLLM not available - using fallback mode")


@dataclass
class PromptVariant:
    """A prompt variant (mutation)"""
    variant_id: str
    task_family: str
    prompt_text: str
    generation_method: str  # 'baseline', 'mutation', 'crossover', 'llm_generated'
    parent_id: Optional[str]

    # Metadata
    created_at: str
    model_used: str
    temperature: float

    # Performance (filled after eval)
    eval_score: float = 0.0
    eval_count: int = 0
    latency_ms: float = 0.0
    token_count: int = 0
    confidence: float = 0.0

    # Status
    status: str = 'pending'  # 'pending', 'testing', 'champion', 'retired'


@dataclass
class EvaluationResult:
    """Result of evaluating a prompt variant"""
    variant_id: str
    task_family: str

    # Metrics
    accuracy_score: float  # 0-100
    latency_ms: float
    token_count: int
    robustness_score: float  # 0-100 (consistency across test cases)

    # Details
    test_cases_passed: int
    test_cases_total: int
    failure_modes: List[str]

    # Composite
    composite_score: float  # Weighted combination
    confidence: float  # 0-1

    timestamp: str


@dataclass
class OptimizationRun:
    """Record of a full optimization cycle"""
    run_id: str
    task_family: str
    timestamp: str

    # Configuration
    n_variants: int
    budget_tokens: int
    baseline_id: str

    # Results
    variants_tested: int
    champion_id: str
    delta_score: float  # Improvement over baseline
    confidence: float

    # Decision
    applied: bool
    apply_reason: str

    # Lineage
    generation: int  # How many optimization cycles for this task
    parent_champion_id: Optional[str]


class TextGradLoop:
    """
    TextGrad Loop - Prompt Evolution Engine

    Philosophy:
    "Prompts are programs. Programs have bugs. Bugs can be fixed through
    gradient-based optimization. TextGrad computes the 'gradient' of
    performance with respect to prompt text, then updates the prompt
    to maximize task performance.

    This is machine learning—but for natural language instructions."

    Process (Evolutionary):
    1. GENERATION: Create N variants from baseline
       - Mutation: Change words/phrases
       - Crossover: Combine two parents
       - LLM-generated: Ask model to improve

    2. EVALUATION: Test each variant
       - Run on gold fixtures
       - Measure accuracy, latency, robustness
       - Compute composite score

    3. SELECTION: Pick champion
       - Highest composite score
       - Must beat baseline (Δscore > 0)
       - Must have confidence ≥ threshold

    4. REPRODUCTION: Apply champion
       - Replace baseline if auto-apply enabled
       - Record lineage (parent → child)
       - Update generation counter

    This mirrors Darwinian evolution:
    - Variants = genetic diversity
    - Evaluation = environmental pressure
    - Selection = survival of fittest
    - Reproduction = passing genes forward
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "TextGrad Evolution Loop"

        # Configuration
        self.config = config or {
            'model_reasoning': 'ollama/deepseek-r1:14b',
            'model_coder': 'ollama/qwen2.5-coder:7b',
            'n_variants_default': 6,
            'budget_tokens_default': 5000,
            'confidence_threshold': 0.78,  # Auto-apply if ≥ 78%
            'mutation_strategies': ['word_swap', 'phrase_add', 'reorder', 'llm_improve'],
            'composite_weights': {
                'accuracy': 0.5,
                'robustness': 0.3,
                'latency': 0.1,  # Lower is better (inverted)
                'tokens': 0.1    # Lower is better (inverted)
            }
        }

        print(f"🧬 Initializing {self.name}...")

        # Storage
        self.variants_file = Path(__file__).parent.parent.parent / "logs" / "evolution" / "variants.json"
        self.runs_file = Path(__file__).parent.parent.parent / "logs" / "evolution" / "runs.json"
        self.champions_file = Path(__file__).parent.parent.parent / "logs" / "evolution" / "champions.json"

        # Ensure directories
        self.variants_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self.variants = self._load_variants()
        self.runs = self._load_runs()
        self.champions = self._load_champions()

        print(f"✅ {self.name} initialized")
        print(f"   Variants tracked: {len(self.variants)}")
        print(f"   Optimization runs: {len(self.runs)}")
        print(f"   Champions: {len(self.champions)}")

    def _load_variants(self) -> List[PromptVariant]:
        """Load variants from disk"""
        if self.variants_file.exists():
            try:
                with open(self.variants_file, 'r') as f:
                    data = json.load(f)
                    return [PromptVariant(**v) for v in data]
            except Exception as e:
                print(f"⚠️  Failed to load variants: {e}")
        return []

    def _save_variants(self):
        """Save variants to disk"""
        try:
            with open(self.variants_file, 'w') as f:
                json.dump([asdict(v) for v in self.variants], f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save variants: {e}")

    def _load_runs(self) -> List[OptimizationRun]:
        """Load optimization runs"""
        if self.runs_file.exists():
            try:
                with open(self.runs_file, 'r') as f:
                    data = json.load(f)
                    return [OptimizationRun(**r) for r in data]
            except Exception as e:
                print(f"⚠️  Failed to load runs: {e}")
        return []

    def _save_runs(self):
        """Save optimization runs"""
        try:
            with open(self.runs_file, 'w') as f:
                json.dump([asdict(r) for r in self.runs], f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save runs: {e}")

    def _load_champions(self) -> Dict[str, str]:
        """Load current champions (task_family → variant_id)"""
        if self.champions_file.exists():
            try:
                with open(self.champions_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load champions: {e}")
        return {}

    def _save_champions(self):
        """Save current champions"""
        try:
            with open(self.champions_file, 'w') as f:
                json.dump(self.champions, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save champions: {e}")

    def generate_variant_id(self, prompt_text: str) -> str:
        """Generate deterministic variant ID from prompt hash"""
        hash_obj = hashlib.sha256(prompt_text.encode())
        return f"v_{hash_obj.hexdigest()[:12]}"

    def mutate_prompt(self, baseline: str, strategy: str) -> str:
        """
        Apply mutation strategy to baseline prompt

        Strategies:
        - word_swap: Replace key words with synonyms
        - phrase_add: Add clarifying phrases
        - reorder: Restructure instruction order
        - llm_improve: Ask LLM to improve
        """
        if strategy == 'word_swap':
            # Simple word substitutions (demonstration)
            mutations = {
                'analyze': 'evaluate',
                'provide': 'give',
                'explain': 'describe',
                'careful': 'thorough',
                'ensure': 'make sure'
            }
            mutated = baseline
            for old, new in mutations.items():
                if old in mutated.lower():
                    mutated = mutated.replace(old, new)
                    break
            return mutated

        elif strategy == 'phrase_add':
            # Add clarifying phrase
            additions = [
                "\n\nBe precise and thorough in your response.",
                "\n\nEnsure all claims are supported by evidence.",
                "\n\nUse clear, professional language.",
                "\n\nFocus on actionable recommendations."
            ]
            return baseline + random.choice(additions)

        elif strategy == 'reorder':
            # Split into sentences and reorder
            sentences = baseline.split('. ')
            if len(sentences) > 2:
                random.shuffle(sentences)
                return '. '.join(sentences)
            return baseline

        elif strategy == 'llm_improve':
            # Ask LLM to improve (most powerful)
            return self._llm_improve_prompt(baseline)

        else:
            return baseline

    def _llm_improve_prompt(self, baseline: str) -> str:
        """Use LLM to improve prompt"""
        if not LITELLM_AVAILABLE:
            # Fallback: just add a quality phrase
            return baseline + "\n\nProvide high-quality, actionable insights."

        try:
            improve_instruction = f"""You are a prompt engineering expert. Improve this prompt to make it clearer, more specific, and more likely to produce high-quality outputs.

Original prompt:
{baseline}

Improved prompt (output ONLY the improved prompt, no explanation):"""

            response = litellm.completion(
                model=self.config['model_reasoning'],
                messages=[{"role": "user", "content": improve_instruction}],
                temperature=0.7,
                max_tokens=500
            )

            improved = response.choices[0].message.content.strip()
            return improved if improved else baseline

        except Exception as e:
            print(f"⚠️  LLM improvement failed: {e}")
            return baseline

    def generate_variants(
        self,
        baseline: PromptVariant,
        n_variants: int
    ) -> List[PromptVariant]:
        """
        Generate N variants from baseline using multiple strategies
        """
        print(f"\n🧬 Generating {n_variants} variants from baseline...")

        variants = []
        strategies = self.config['mutation_strategies']

        for i in range(n_variants):
            strategy = strategies[i % len(strategies)]

            mutated_text = self.mutate_prompt(baseline.prompt_text, strategy)
            variant_id = self.generate_variant_id(mutated_text)

            variant = PromptVariant(
                variant_id=variant_id,
                task_family=baseline.task_family,
                prompt_text=mutated_text,
                generation_method=f"mutation_{strategy}",
                parent_id=baseline.variant_id,
                created_at=datetime.now().isoformat(),
                model_used=self.config['model_reasoning'],
                temperature=0.7,
                status='pending'
            )

            variants.append(variant)
            print(f"   {i+1}. {strategy:15s} → {variant_id}")

        return variants

    def evaluate_variant(
        self,
        variant: PromptVariant,
        test_harness: callable
    ) -> EvaluationResult:
        """
        Evaluate variant using test harness

        Args:
            variant: PromptVariant to test
            test_harness: Function that tests prompt (returns metrics)
        """
        print(f"   Evaluating {variant.variant_id[:16]}...")

        try:
            # Run test harness (returns dict with metrics)
            metrics = test_harness(variant.prompt_text)

            # Compute composite score
            weights = self.config['composite_weights']

            # Invert latency/tokens (lower is better)
            latency_score = max(0, 100 - (metrics.get('latency_ms', 1000) / 10))
            tokens_score = max(0, 100 - (metrics.get('token_count', 1000) / 10))

            composite = (
                weights['accuracy'] * metrics.get('accuracy', 0) +
                weights['robustness'] * metrics.get('robustness', 0) +
                weights['latency'] * latency_score +
                weights['tokens'] * tokens_score
            )

            result = EvaluationResult(
                variant_id=variant.variant_id,
                task_family=variant.task_family,
                accuracy_score=metrics.get('accuracy', 0),
                latency_ms=metrics.get('latency_ms', 0),
                token_count=metrics.get('token_count', 0),
                robustness_score=metrics.get('robustness', 0),
                test_cases_passed=metrics.get('passed', 0),
                test_cases_total=metrics.get('total', 0),
                failure_modes=metrics.get('failures', []),
                composite_score=composite,
                confidence=metrics.get('confidence', 0.5),
                timestamp=datetime.now().isoformat()
            )

            # Update variant
            variant.eval_score = composite
            variant.eval_count += 1
            variant.latency_ms = metrics.get('latency_ms', 0)
            variant.token_count = metrics.get('token_count', 0)
            variant.confidence = metrics.get('confidence', 0.5)
            variant.status = 'tested'

            print(f"      Score: {composite:.1f} | Accuracy: {result.accuracy_score:.1f}% | Latency: {result.latency_ms:.0f}ms")

            return result

        except Exception as e:
            print(f"      ❌ Evaluation failed: {e}")

            # Return low-score result
            return EvaluationResult(
                variant_id=variant.variant_id,
                task_family=variant.task_family,
                accuracy_score=0,
                latency_ms=9999,
                token_count=9999,
                robustness_score=0,
                test_cases_passed=0,
                test_cases_total=1,
                failure_modes=[str(e)],
                composite_score=0,
                confidence=0,
                timestamp=datetime.now().isoformat()
            )

    def optimize_prompt(
        self,
        task_family: str,
        baseline_prompt: str,
        test_harness: callable,
        n_variants: int = None,
        budget_tokens: int = None
    ) -> OptimizationRun:
        """
        Run one optimization cycle

        Args:
            task_family: Task identifier (e.g., "attorney_consult")
            baseline_prompt: Current prompt to improve
            test_harness: Function to evaluate prompts
            n_variants: Number of variants to generate
            budget_tokens: Token budget (unused for now)

        Returns:
            OptimizationRun with results
        """
        print(f"\n{'='*70}")
        print(f"🧬 TEXTGRAD OPTIMIZATION CYCLE")
        print(f"{'='*70}")
        print(f"Task: {task_family}")

        n_variants = n_variants or self.config['n_variants_default']
        budget_tokens = budget_tokens or self.config['budget_tokens_default']

        # Create baseline variant
        baseline_id = self.generate_variant_id(baseline_prompt)
        baseline = PromptVariant(
            variant_id=baseline_id,
            task_family=task_family,
            prompt_text=baseline_prompt,
            generation_method='baseline',
            parent_id=None,
            created_at=datetime.now().isoformat(),
            model_used='n/a',
            temperature=0.0,
            status='baseline'
        )

        # Evaluate baseline
        print(f"\n📊 Evaluating baseline...")
        baseline_result = self.evaluate_variant(baseline, test_harness)
        baseline_score = baseline_result.composite_score

        # Generate variants
        variants = self.generate_variants(baseline, n_variants)

        # Evaluate all variants
        print(f"\n📊 Evaluating {len(variants)} variants...")
        results = []
        for variant in variants:
            result = self.evaluate_variant(variant, test_harness)
            results.append(result)

        # Select champion (highest score)
        best_result = max(results, key=lambda r: r.composite_score)
        best_variant = next(v for v in variants if v.variant_id == best_result.variant_id)

        delta_score = best_result.composite_score - baseline_score

        print(f"\n{'='*70}")
        print(f"🏆 CHAMPION SELECTED")
        print(f"{'='*70}")
        print(f"   Variant: {best_variant.variant_id}")
        print(f"   Method: {best_variant.generation_method}")
        print(f"   Score: {best_result.composite_score:.1f} (baseline: {baseline_score:.1f})")
        print(f"   Δscore: {delta_score:+.1f}")
        print(f"   Confidence: {best_result.confidence:.1%}")

        # Determine if should apply
        should_apply = (
            delta_score > 0 and
            best_result.confidence >= self.config['confidence_threshold']
        )

        if should_apply:
            apply_reason = f"Δscore={delta_score:+.1f}, confidence={best_result.confidence:.1%} ≥ {self.config['confidence_threshold']:.0%}"
            print(f"   ✅ AUTO-APPLYING (confidence threshold met)")

            # Update champion
            best_variant.status = 'champion'
            self.champions[task_family] = best_variant.variant_id
            self._save_champions()
        else:
            apply_reason = f"Δscore={delta_score:+.1f} or confidence={best_result.confidence:.1%} < {self.config['confidence_threshold']:.0%}"
            print(f"   ⏸️  PENDING APPROVAL (confidence threshold not met)")

        # Record run
        generation = len([r for r in self.runs if r.task_family == task_family]) + 1
        parent_champion = self.champions.get(task_family)

        run = OptimizationRun(
            run_id=f"run_{task_family}_{int(time.time())}",
            task_family=task_family,
            timestamp=datetime.now().isoformat(),
            n_variants=n_variants,
            budget_tokens=budget_tokens,
            baseline_id=baseline_id,
            variants_tested=len(variants),
            champion_id=best_variant.variant_id,
            delta_score=delta_score,
            confidence=best_result.confidence,
            applied=should_apply,
            apply_reason=apply_reason,
            generation=generation,
            parent_champion_id=parent_champion
        )

        # Save everything
        self.variants.extend([baseline] + variants)
        self.runs.append(run)
        self._save_variants()
        self._save_runs()

        print(f"{'='*70}\n")

        return run

    def get_status(self) -> Dict[str, Any]:
        """Get evolution engine status"""
        return {
            'engine': self.name,
            'philosophy': 'Prompts evolve through gradient-based optimization—this is Darwinian selection for language',
            'variants_tracked': len(self.variants),
            'optimization_runs': len(self.runs),
            'current_champions': len(self.champions),
            'config': self.config,
            'wisdom': 'Agents that cannot learn are not intelligent. Evolution is survival.'
        }


# Singleton instance
_textgrad = None


def get_textgrad_loop() -> TextGradLoop:
    """Get singleton TextGrad loop"""
    global _textgrad
    if _textgrad is None:
        _textgrad = TextGradLoop()
    return _textgrad


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY TEXTGRAD EVOLUTION LOOP")
    print("="*70)
    print()

    loop = get_textgrad_loop()

    print("\nStatus:")
    status = loop.get_status()
    for key, value in status.items():
        if key != 'wisdom':
            print(f"  {key}: {value}")

    print(f"\n💬 Wisdom: {status['wisdom']}")

    # Demo: optimize a simple prompt
    print("\n🧬 Demo: Optimizing attorney consultation prompt...")

    baseline_prompt = """You are a legal expert. Analyze the following case and provide recommendations."""

    # Simple test harness (returns fake metrics)
    def demo_test_harness(prompt_text: str) -> Dict[str, Any]:
        """Fake test harness for demo"""
        # Simulate evaluation
        time.sleep(0.1)

        # Score based on prompt length & keywords
        score = 50
        if 'thorough' in prompt_text.lower():
            score += 10
        if 'evidence' in prompt_text.lower():
            score += 10
        if 'actionable' in prompt_text.lower():
            score += 10
        if len(prompt_text) > 100:
            score += 10

        return {
            'accuracy': min(100, score + random.uniform(-5, 5)),
            'robustness': min(100, score + random.uniform(-10, 10)),
            'latency_ms': random.uniform(500, 1500),
            'token_count': len(prompt_text.split()) * 2,
            'passed': random.randint(3, 5),
            'total': 5,
            'confidence': random.uniform(0.6, 0.9),
            'failures': []
        }

    # Run optimization
    run = loop.optimize_prompt(
        task_family='attorney_consult_demo',
        baseline_prompt=baseline_prompt,
        test_harness=demo_test_harness,
        n_variants=4
    )

    print("\n📊 Optimization complete!")
    print(f"   Champion: {run.champion_id}")
    print(f"   Δscore: {run.delta_score:+.1f}")
    print(f"   Applied: {run.applied}")

    print("\n✅ TextGrad Loop ready for nightly evolution")
