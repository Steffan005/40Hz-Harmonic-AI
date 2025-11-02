#!/usr/bin/env python3
"""
Unity A/B Test Harness - Attorney Evaluation
Rigorous prompt testing with fixed seeds and gold fixtures

Philosophy:
"You cannot improve what you cannot measure. Gold fixtures are the ground truth.
Fixed seeds ensure reproducibility. A/B testing reveals which prompt truly performs better.

This is science—not guesswork."

Test Methodology:
1. Gold Fixtures = Hand-crafted test cases with known correct answers
2. Fixed Seeds = Deterministic LLM sampling for fair comparison
3. Pass@k = Success rate across multiple samples
4. Robustness = Consistency across varied inputs
5. Composite Score = Weighted combination of metrics

Author: Dr. Claude Summers, Evaluation Architecture
Date: October 16, 2025 (Phase Ω)
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

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("⚠️  LiteLLM not available - using mock mode")


@dataclass
class GoldFixture:
    """A test case with ground truth"""
    fixture_id: str
    task_family: str
    input_text: str
    expected_elements: List[str]  # Key elements that should appear in response
    scoring_criteria: Dict[str, float]  # Criteria → weight
    difficulty: str  # 'easy', 'medium', 'hard'


@dataclass
class EvalResult:
    """Result of evaluating a prompt on a fixture"""
    fixture_id: str
    prompt_text: str
    response_text: str

    # Scores (0-100)
    accuracy_score: float
    completeness_score: float
    clarity_score: float
    relevance_score: float

    # Metrics
    elements_found: List[str]
    elements_missing: List[str]
    latency_ms: float
    token_count: int

    # Composite
    composite_score: float
    passed: bool

    timestamp: str


class AttorneyEvaluator:
    """
    Attorney Evaluation Harness

    Philosophy:
    "Legal advice must be accurate, complete, clear, and relevant.
    We test prompts against gold fixtures that represent real cases.
    A prompt that passes 4/5 fixtures is better than one that passes 3/5.

    This is how we measure improvement."

    Gold Fixtures (Examples):
    1. Miranda Rights (Criminal Defense)
       - Input: Client arrested without Miranda warning
       - Expected: Mention suppression of evidence, 5th Amendment, cite Miranda v. Arizona
       - Criteria: Accuracy 50%, Completeness 30%, Clarity 20%

    2. ADA Accommodation (Civil Rights)
       - Input: Disabled employee denied reasonable accommodation
       - Expected: Mention ADA, interactive process, reasonable accommodation standard
       - Criteria: Accuracy 40%, Completeness 40%, Relevance 20%

    3. Search & Seizure (Criminal Defense)
       - Input: Warrantless search of vehicle
       - Expected: Mention 4th Amendment, automobile exception, probable cause
       - Criteria: Accuracy 50%, Completeness 30%, Clarity 20%

    Scoring:
    - Accuracy: Does response contain correct legal concepts?
    - Completeness: Are all key elements present?
    - Clarity: Is explanation understandable to non-lawyers?
    - Relevance: Does response address the specific question?

    Composite = weighted sum of criteria
    Pass = composite ≥ 70
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "Attorney Evaluator"

        # Configuration
        self.config = config or {
            'model': 'ollama/deepseek-r1:14b',
            'temperature': 0.3,  # Low for consistency
            'max_tokens': 1000,
            'fixed_seed': 42,  # Deterministic sampling
            'pass_threshold': 70.0  # 70% composite score to pass
        }

        print(f"⚖️  Initializing {self.name}...")

        # Load gold fixtures
        self.fixtures = self._load_gold_fixtures()

        print(f"✅ {self.name} initialized")
        print(f"   Gold fixtures: {len(self.fixtures)}")
        print(f"   Pass threshold: {self.config['pass_threshold']}%")

    def _load_gold_fixtures(self) -> List[GoldFixture]:
        """Load gold test fixtures"""
        # In production, load from JSON/YAML
        # For now, hardcoded examples
        fixtures = [
            GoldFixture(
                fixture_id='miranda_01',
                task_family='criminal_defense',
                input_text="Client was arrested for DUI and questioned without being read Miranda rights. What are our options?",
                expected_elements=[
                    'Miranda v. Arizona',
                    'suppression of evidence',
                    'Fifth Amendment',
                    'right to remain silent',
                    'motion to suppress'
                ],
                scoring_criteria={'accuracy': 0.5, 'completeness': 0.3, 'clarity': 0.2},
                difficulty='medium'
            ),
            GoldFixture(
                fixture_id='ada_01',
                task_family='civil_rights',
                input_text="Employee with hearing impairment requested sign language interpreter. Employer denied request citing cost. Is this ADA violation?",
                expected_elements=[
                    'Americans with Disabilities Act',
                    'reasonable accommodation',
                    'interactive process',
                    'undue hardship',
                    'effective communication'
                ],
                scoring_criteria={'accuracy': 0.4, 'completeness': 0.4, 'relevance': 0.2},
                difficulty='medium'
            ),
            GoldFixture(
                fixture_id='search_01',
                task_family='criminal_defense',
                input_text="Police searched client's car during traffic stop without warrant or consent. Found drugs in trunk. Can this be suppressed?",
                expected_elements=[
                    'Fourth Amendment',
                    'automobile exception',
                    'probable cause',
                    'warrantless search',
                    'motion to suppress'
                ],
                scoring_criteria={'accuracy': 0.5, 'completeness': 0.3, 'clarity': 0.2},
                difficulty='hard'
            ),
            GoldFixture(
                fixture_id='excessive_force_01',
                task_family='civil_rights',
                input_text="Client alleges police used excessive force during arrest causing broken ribs. What legal claims are available?",
                expected_elements=[
                    'Fourth Amendment',
                    'excessive force',
                    '42 USC 1983',
                    'qualified immunity',
                    'objectively reasonable'
                ],
                scoring_criteria={'accuracy': 0.5, 'completeness': 0.3, 'relevance': 0.2},
                difficulty='hard'
            ),
            GoldFixture(
                fixture_id='competency_01',
                task_family='criminal_defense',
                input_text="Client has schizophrenia and hallucinations. Concerned about competency to stand trial. What standards apply?",
                expected_elements=[
                    'Dusky v. United States',
                    'present ability to consult',
                    'rational understanding',
                    'competency evaluation',
                    'mental health expert'
                ],
                scoring_criteria={'accuracy': 0.5, 'completeness': 0.3, 'clarity': 0.2},
                difficulty='medium'
            )
        ]

        return fixtures

    def evaluate_prompt(
        self,
        prompt_text: str,
        task_family: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a prompt against gold fixtures

        Returns metrics dict compatible with TextGrad loop
        """
        print(f"\n⚖️  Evaluating prompt on gold fixtures...")

        # Filter fixtures by task family if specified
        fixtures = self.fixtures
        if task_family:
            fixtures = [f for f in fixtures if f.task_family == task_family]

        if not fixtures:
            print(f"⚠️  No fixtures found for task: {task_family}")
            fixtures = self.fixtures  # Use all

        results = []
        passed_count = 0

        for fixture in fixtures:
            print(f"   Testing {fixture.fixture_id}...")
            result = self._evaluate_fixture(prompt_text, fixture)
            results.append(result)

            if result.passed:
                passed_count += 1

        # Aggregate metrics
        avg_accuracy = sum(r.accuracy_score for r in results) / len(results)
        avg_completeness = sum(r.completeness_score for r in results) / len(results)
        avg_clarity = sum(r.clarity_score for r in results) / len(results)
        avg_relevance = sum(r.relevance_score for r in results) / len(results)
        avg_composite = sum(r.composite_score for r in results) / len(results)

        avg_latency = sum(r.latency_ms for r in results) / len(results)
        avg_tokens = sum(r.token_count for r in results) / len(results)

        robustness = (passed_count / len(results)) * 100

        print(f"\n   Results:")
        print(f"      Passed: {passed_count}/{len(results)} ({robustness:.0f}%)")
        print(f"      Avg Composite: {avg_composite:.1f}")
        print(f"      Avg Latency: {avg_latency:.0f}ms")

        # Return format compatible with TextGrad
        return {
            'accuracy': avg_accuracy,
            'robustness': robustness,
            'latency_ms': avg_latency,
            'token_count': int(avg_tokens),
            'passed': passed_count,
            'total': len(results),
            'confidence': avg_composite / 100.0,  # 0-1
            'failures': [r.fixture_id for r in results if not r.passed],
            'details': {
                'completeness': avg_completeness,
                'clarity': avg_clarity,
                'relevance': avg_relevance
            }
        }

    def _evaluate_fixture(
        self,
        prompt_text: str,
        fixture: GoldFixture
    ) -> EvalResult:
        """Evaluate prompt on single fixture"""
        start_time = time.time()

        # Generate response using prompt
        response_text = self._generate_response(prompt_text, fixture.input_text)

        latency_ms = (time.time() - start_time) * 1000

        # Score the response
        accuracy = self._score_accuracy(response_text, fixture.expected_elements)
        completeness = self._score_completeness(response_text, fixture.expected_elements)
        clarity = self._score_clarity(response_text)
        relevance = self._score_relevance(response_text, fixture.input_text)

        # Compute composite (using fixture criteria)
        criteria = fixture.scoring_criteria
        composite = (
            criteria.get('accuracy', 0) * accuracy +
            criteria.get('completeness', 0) * completeness +
            criteria.get('clarity', 0) * clarity +
            criteria.get('relevance', 0) * relevance
        )

        # Normalize if weights don't sum to 1
        total_weight = sum(criteria.values())
        if total_weight > 0:
            composite = (composite / total_weight) * 100

        passed = composite >= self.config['pass_threshold']

        # Determine which elements were found
        found = [e for e in fixture.expected_elements if e.lower() in response_text.lower()]
        missing = [e for e in fixture.expected_elements if e.lower() not in response_text.lower()]

        return EvalResult(
            fixture_id=fixture.fixture_id,
            prompt_text=prompt_text[:100] + '...',  # Truncate for storage
            response_text=response_text[:500] + '...' if len(response_text) > 500 else response_text,
            accuracy_score=accuracy,
            completeness_score=completeness,
            clarity_score=clarity,
            relevance_score=relevance,
            elements_found=found,
            elements_missing=missing,
            latency_ms=latency_ms,
            token_count=len(response_text.split()),
            composite_score=composite,
            passed=passed,
            timestamp=datetime.now().isoformat()
        )

    def _generate_response(self, prompt_text: str, input_text: str) -> str:
        """Generate response using LLM"""
        if not LITELLM_AVAILABLE:
            # Mock response for testing
            return f"Mock legal analysis for: {input_text[:50]}... This includes some legal concepts and recommendations."

        try:
            messages = [
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": input_text}
            ]

            response = litellm.completion(
                model=self.config['model'],
                messages=messages,
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens'],
                seed=self.config['fixed_seed']  # Deterministic
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"      ⚠️  LLM generation failed: {e}")
            return "Error generating response."

    def _score_accuracy(self, response: str, expected_elements: List[str]) -> float:
        """Score accuracy (presence of expected legal concepts)"""
        if not expected_elements:
            return 100.0

        found_count = sum(1 for e in expected_elements if e.lower() in response.lower())
        return (found_count / len(expected_elements)) * 100

    def _score_completeness(self, response: str, expected_elements: List[str]) -> float:
        """Score completeness (coverage of all key elements)"""
        # Similar to accuracy but may weight elements differently
        return self._score_accuracy(response, expected_elements)

    def _score_clarity(self, response: str) -> float:
        """Score clarity (readability, structure)"""
        # Simple heuristics (in production, use readability metrics)
        score = 50.0

        # Positive signals
        if len(response) > 100:
            score += 10  # Sufficient detail
        if any(marker in response for marker in ['\n\n', '. ', ':\n']):
            score += 10  # Structured
        if not any(jargon in response.lower() for jargon in ['herein', 'aforementioned', 'heretofore']):
            score += 10  # Avoids excessive legalese
        if len(response.split()) < 500:
            score += 10  # Concise
        if response.count('.') >= 3:
            score += 10  # Multiple sentences

        return min(100.0, score)

    def _score_relevance(self, response: str, input_text: str) -> float:
        """Score relevance (addresses the specific question)"""
        # Check if key terms from input appear in response
        input_words = set(input_text.lower().split())
        response_words = set(response.lower().split())

        # Remove stop words (simplified)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were'}
        input_words -= stop_words
        response_words -= stop_words

        if not input_words:
            return 100.0

        # Overlap ratio
        overlap = len(input_words & response_words)
        return min(100.0, (overlap / len(input_words)) * 100 + 20)  # Base 20 + overlap bonus


# Test function (for TextGrad integration)
def create_attorney_test_harness(task_family: Optional[str] = None):
    """
    Create test harness function for TextGrad

    Returns:
        Function that takes prompt_text and returns metrics dict
    """
    evaluator = AttorneyEvaluator()

    def test_harness(prompt_text: str) -> Dict[str, Any]:
        """Test harness compatible with TextGrad"""
        return evaluator.evaluate_prompt(prompt_text, task_family)

    return test_harness


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY ATTORNEY EVALUATION HARNESS")
    print("="*70)
    print()

    evaluator = AttorneyEvaluator()

    print("\n⚖️  Testing prompts on gold fixtures...\n")

    # Test 1: Basic prompt
    print("="*70)
    print("TEST 1: BASIC PROMPT")
    print("="*70)

    basic_prompt = """You are a legal expert. Analyze the case and provide recommendations."""

    basic_metrics = evaluator.evaluate_prompt(basic_prompt)

    print(f"\n📊 Basic Prompt Results:")
    print(f"   Accuracy: {basic_metrics['accuracy']:.1f}%")
    print(f"   Robustness: {basic_metrics['robustness']:.1f}%")
    print(f"   Passed: {basic_metrics['passed']}/{basic_metrics['total']}")

    # Test 2: Enhanced prompt
    print("\n")
    print("="*70)
    print("TEST 2: ENHANCED PROMPT")
    print("="*70)

    enhanced_prompt = """You are an experienced attorney. For each case:
1. Identify relevant legal principles and precedents
2. Analyze the key facts and legal elements
3. Provide clear, actionable recommendations
4. Cite specific case law when applicable

Be thorough, accurate, and professional."""

    enhanced_metrics = evaluator.evaluate_prompt(enhanced_prompt)

    print(f"\n📊 Enhanced Prompt Results:")
    print(f"   Accuracy: {enhanced_metrics['accuracy']:.1f}%")
    print(f"   Robustness: {enhanced_metrics['robustness']:.1f}%")
    print(f"   Passed: {enhanced_metrics['passed']}/{enhanced_metrics['total']}")

    # Comparison
    delta_accuracy = enhanced_metrics['accuracy'] - basic_metrics['accuracy']
    delta_robustness = enhanced_metrics['robustness'] - basic_metrics['robustness']

    print("\n")
    print("="*70)
    print("COMPARISON")
    print("="*70)
    print(f"   Δ Accuracy: {delta_accuracy:+.1f}%")
    print(f"   Δ Robustness: {delta_robustness:+.1f}%")

    if delta_accuracy > 0:
        print(f"   ✅ Enhanced prompt is {delta_accuracy:.1f}% more accurate")
    else:
        print(f"   ❌ Basic prompt is {abs(delta_accuracy):.1f}% more accurate")

    print("\n✅ Attorney Evaluator ready for TextGrad integration")
