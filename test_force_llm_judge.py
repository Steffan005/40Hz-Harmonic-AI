#!/usr/bin/env python3
"""
Force LLM judge activation by crafting edge cases with low entropy/length.
"""

import json
from heuristics import HeuristicValidator
from evaluator_v2 import EvaluatorV2

def test_heuristic_scores():
    """Test what heuristic scores various outputs get."""

    validator = HeuristicValidator()
    evaluator = EvaluatorV2()

    print("="*70)
    print("TESTING HEURISTIC SCORES TO FIND AMBIGUOUS ZONE")
    print("="*70)
    print()

    test_cases = [
        ("Too short", "x = 1", "Very short code"),
        ("Low entropy", "aaaaaaaaaaaaaaaaaaaaa", "Repetitive text"),
        ("Borderline length", "def f(x): return x", "Minimal function"),
        ("No docstring", "def calc(a,b,c,d,e):\n  return a+b+c+d+e", "Undocumented code"),
        ("Vague", "The system works by processing inputs.", "Vague explanation"),
        ("Incomplete", "def foo():\n  # TODO: implement", "Incomplete implementation"),
    ]

    for name, output, description in test_cases:
        hresult = validator.validate(output)
        hscore = hresult["score"]

        print(f"Test: {name}")
        print(f"  Output: {output[:50]}...")
        print(f"  Heuristic Score: {hscore:.3f}")
        print(f"  Details: {json.dumps(hresult['details'], indent=4)}")

        # Predict routing
        tau_low = evaluator.tau_low
        tau_high = evaluator.tau_high

        if hscore < tau_low:
            routing = "heuristic_reject"
        elif hscore > tau_high:
            routing = "heuristic_accept"
        else:
            routing = "🎯 LLM_JUDGE"

        print(f"  Predicted Routing: {routing}")
        print()

    print("="*70)
    print("NOW TESTING LIVE EVALUATOR WITH AMBIGUOUS CASES")
    print("="*70)
    print()

    # Test case 1: Low entropy
    goal1 = "Repeat a pattern 20 times"
    output1 = "a" * 25  # Low entropy, meets min length
    result1 = evaluator.evaluate(goal1, output1)
    print(f"Test 1 - Low Entropy:")
    print(f"  Routing: {result1['routing_path']}")
    print(f"  Score: {result1['quality_score']:.1f}")
    print()

    # Test case 2: Just at minimum length
    goal2 = "Write minimal code"
    output2 = "x=1;y=2;print(x+y)"  # Exactly 19 chars
    result2 = evaluator.evaluate(goal2, output2)
    print(f"Test 2 - Minimal Length:")
    print(f"  Routing: {result2['routing_path']}")
    print(f"  Score: {result2['quality_score']:.1f}")
    print()

    # Test case 3: Borderline entropy
    goal3 = "Generate test data"
    output3 = "test test test test test test test data"  # Repetitive
    result3 = evaluator.evaluate(goal3, output3)
    print(f"Test 3 - Borderline Entropy:")
    print(f"  Routing: {result3['routing_path']}")
    print(f"  Score: {result3['quality_score']:.1f}")
    print()

    # Print stats
    stats = evaluator.get_stats()
    print("="*70)
    print(f"LLM Judge Activations: {stats['llm_judge_calls']}")
    print(f"Heuristic Routing: {stats['heuristic_routing_rate']:.1%}")
    print("="*70)

    if stats['llm_judge_calls'] > 0:
        print("🎉 SUCCESS: LLM judge activated!")
    else:
        print("⚠️  Heuristics too strong - need weaker test cases")


if __name__ == "__main__":
    test_heuristic_scores()
