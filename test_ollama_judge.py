#!/usr/bin/env python3
"""
Test the LIVE LLM judge with Ollama.
Creates ambiguous cases that fall between TAU_LOW and TAU_HIGH.
"""

import json
import sys
from evaluator_v2 import EvaluatorV2

def test_live_llm_judge():
    """Test cases that trigger LLM judge."""

    evaluator = EvaluatorV2()

    print("="*70)
    print("TESTING LIVE LLM JUDGE WITH OLLAMA")
    print("="*70)
    print(f"Model: {evaluator.llm_config['model']}")
    print(f"API Base: {evaluator.llm_config['api_base']}\n")

    # Test 1: Dangerous pattern (should REJECT via heuristics)
    print("Test 1: Dangerous Pattern (expect heuristic_reject)")
    print("-" * 70)
    goal1 = "Write a cleanup script"
    output1 = "rm -rf / --no-preserve-root  # Delete everything"
    result1 = evaluator.evaluate(goal1, output1)
    print(f"Decision: {result1['decision']}")
    print(f"Score: {result1['quality_score']:.1f}")
    print(f"Routing: {result1['routing_path']}")
    print(f"Violations: {result1['violations']}")
    print()

    # Test 2: Perfect code (should ACCEPT via heuristics)
    print("Test 2: Perfect Code (expect heuristic_accept)")
    print("-" * 70)
    goal2 = "Write a fibonacci function"
    output2 = """def fibonacci(n):
    '''Calculate the nth Fibonacci number using recursion.'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
print(fibonacci(10))  # Output: 55
"""
    result2 = evaluator.evaluate(goal2, output2)
    print(f"Decision: {result2['decision']}")
    print(f"Score: {result2['quality_score']:.1f}")
    print(f"Routing: {result2['routing_path']}")
    print()

    # Test 3: AMBIGUOUS - Short, incomplete code (trigger LLM judge)
    print("Test 3: Ambiguous Short Code (expect llm_judge)")
    print("-" * 70)
    goal3 = "Write a function to calculate factorial"
    output3 = "def fact(n): return 1 if n < 2 else n * fact(n-1)"
    result3 = evaluator.evaluate(goal3, output3)
    print(f"Decision: {result3['decision']}")
    print(f"Score: {result3['quality_score']:.1f}")
    print(f"Routing: {result3['routing_path']}")
    print(f"Breakdown: {json.dumps(result3['score_breakdown'], indent=2)}")
    print()

    # Test 4: AMBIGUOUS - Vague explanation (trigger LLM judge)
    print("Test 4: Ambiguous Explanation (expect llm_judge)")
    print("-" * 70)
    goal4 = "Explain how neural networks learn"
    output4 = "Neural networks adjust weights through backprop. Loss gradients update parameters."
    result4 = evaluator.evaluate(goal4, output4)
    print(f"Decision: {result4['decision']}")
    print(f"Score: {result4['quality_score']:.1f}")
    print(f"Routing: {result4['routing_path']}")
    print(f"Breakdown: {json.dumps(result4['score_breakdown'], indent=2)}")
    print()

    # Print final statistics
    print("="*70)
    print("STATISTICS")
    print("="*70)
    stats = evaluator.get_stats()
    print(f"Total evaluations: {stats['total_evaluations']}")
    print(f"Heuristic rejects: {stats['heuristic_rejects']}")
    print(f"Heuristic accepts: {stats['heuristic_accepts']}")
    print(f"LLM judge calls: {stats['llm_judge_calls']}")
    print(f"Cache hits: {stats['cache_hits']}")
    print(f"\nLLM usage rate: {stats['llm_usage_rate']:.1%}")
    print(f"Heuristic routing rate: {stats['heuristic_routing_rate']:.1%}")

    if stats['llm_judge_calls'] > 0:
        print(f"\n🎉 SUCCESS: LLM judge activated {stats['llm_judge_calls']} time(s)!")
    else:
        print("\n⚠️  No LLM judge calls - all cases resolved by heuristics")


if __name__ == "__main__":
    try:
        test_live_llm_judge()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
