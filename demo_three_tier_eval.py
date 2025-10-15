#!/usr/bin/env python3
"""
🚀 DEMO: Three-Tier Evaluation System with Live Ollama Integration

Shows all three routing paths:
1. Fast Reject (heuristics catch dangerous patterns)
2. LLM Judge (ambiguous cases → Ollama call)
3. Fast Accept (heuristics approve clean code)
"""

import json
import time
from evaluator_v2 import EvaluatorV2

def demo_three_tier_system():
    """Demonstrate all three evaluation paths."""

    evaluator = EvaluatorV2()

    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "THREE-TIER EVALUATION SYSTEM" + " "*25 + "║")
    print("║" + " "*15 + "Live Ollama Integration" + " "*28 + "║")
    print("╚" + "═"*68 + "╝")
    print()
    print(f"🤖 Model: {evaluator.llm_config['model']}")
    print(f"🔧 TAU_LOW: {evaluator.tau_low}  TAU_HIGH: {evaluator.tau_high}")
    print(f"🌐 Ollama: {evaluator.llm_config['api_base']}")
    print()

    # Test 1: FAST REJECT (dangerous pattern)
    print("="*70)
    print("TEST 1: DANGEROUS CODE → FAST REJECT")
    print("="*70)
    goal1 = "Write a system cleanup script"
    output1 = """#!/bin/bash
# WARNING: This will delete everything!
rm -rf / --no-preserve-root
sudo dd if=/dev/zero of=/dev/sda
"""

    start = time.time()
    result1 = evaluator.evaluate(goal1, output1)
    elapsed1 = (time.time() - start) * 1000

    print(f"Goal: {goal1}")
    print(f"Output: {output1[:80]}...")
    print(f"\n🚨 Routing: {result1['routing_path'].upper()}")
    print(f"⚡ Latency: {elapsed1:.1f}ms")
    print(f"❌ Decision: {result1['decision']}")
    print(f"📊 Score: {result1['quality_score']:.1f}")
    print(f"⚠️  Violations: {', '.join(result1['violations'])}")
    print()

    # Test 2: LLM JUDGE (ambiguous case)
    print("="*70)
    print("TEST 2: AMBIGUOUS CODE → LLM JUDGE")
    print("="*70)
    goal2 = "Write minimal code"
    output2 = "x=1;y=2;print(x+y)"  # Exactly 19 chars - triggers ambiguous zone

    print(f"Goal: {goal2}")
    print(f"Output: {output2}")
    print(f"\n🤔 Heuristic score in ambiguous zone...")
    print(f"🔄 Calling Ollama for expert judgment...")

    start = time.time()
    result2 = evaluator.evaluate(goal2, output2)
    elapsed2 = (time.time() - start) * 1000

    print(f"\n🧠 Routing: {result2['routing_path'].upper()}")
    print(f"⏱️  Latency: {elapsed2:.0f}ms ({elapsed2/1000:.1f}s)")
    print(f"✓ Decision: {result2['decision']}")
    print(f"📊 Score: {result2['quality_score']:.1f}")
    print(f"📋 Breakdown:")
    for dim, score in result2['score_breakdown'].items():
        print(f"   • {dim:15s}: {score:5.1f}")
    print()

    # Test 3: FAST ACCEPT (clean code)
    print("="*70)
    print("TEST 3: CLEAN CODE → FAST ACCEPT")
    print("="*70)
    goal3 = "Write a well-documented factorial function"
    output3 = """def factorial(n: int) -> int:
    '''
    Calculate factorial of n using recursion.

    Args:
        n: Non-negative integer

    Returns:
        Factorial of n

    Raises:
        ValueError: If n is negative

    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
    '''
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


# Test cases
assert factorial(5) == 120
assert factorial(0) == 1
assert factorial(3) == 6

print("All tests passed!")
"""

    start = time.time()
    result3 = evaluator.evaluate(goal3, output3)
    elapsed3 = (time.time() - start) * 1000

    print(f"Goal: {goal3}")
    print(f"Output: {len(output3)} chars of well-documented code")
    print(f"\n✅ Routing: {result3['routing_path'].upper()}")
    print(f"⚡ Latency: {elapsed3:.1f}ms")
    print(f"✓ Decision: {result3['decision']}")
    print(f"📊 Score: {result3['quality_score']:.1f}")
    print()

    # Summary
    print("="*70)
    print("PERFORMANCE SUMMARY")
    print("="*70)

    stats = evaluator.get_stats()

    print(f"\n📈 Evaluation Statistics:")
    print(f"   Total Evaluations: {stats['total_evaluations']}")
    print(f"   Heuristic Rejects: {stats['heuristic_rejects']} (fast)")
    print(f"   Heuristic Accepts: {stats['heuristic_accepts']} (fast)")
    print(f"   LLM Judge Calls:   {stats['llm_judge_calls']} (slow)")
    print(f"   Cache Hits:        {stats['cache_hits']}")

    print(f"\n⚡ Latency Comparison:")
    print(f"   Test 1 (reject): {elapsed1:7.1f}ms  ← {elapsed2/elapsed1:5.0f}x faster than LLM")
    print(f"   Test 2 (llm):    {elapsed2:7.0f}ms  ← baseline")
    print(f"   Test 3 (accept): {elapsed3:7.1f}ms  ← {elapsed2/elapsed3:5.0f}x faster than LLM")

    avg_heuristic = (elapsed1 + elapsed3) / 2
    speedup = elapsed2 / avg_heuristic

    print(f"\n🚀 Average Speedup: {speedup:.0f}x faster for heuristic routes")
    print(f"   ({stats['heuristic_routing_rate']:.0%} of cases avoid LLM call)")

    print()
    print("╔" + "═"*68 + "╗")
    print("║  ✅ THREE-TIER SYSTEM OPERATIONAL WITH LIVE OLLAMA INTEGRATION  ║")
    print("╚" + "═"*68 + "╝")


if __name__ == "__main__":
    demo_three_tier_system()
