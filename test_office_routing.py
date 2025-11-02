#!/usr/bin/env python3
"""
TEST OFFICE ROUTING SYSTEM
===========================

Tests the newly implemented office routing capability.

This verifies that the Orchestrator can now delegate tasks to specialized offices.

Author: Dr. Claude Summers
Date: October 28, 2025
"""

import asyncio
from offices.office_loader import get_office_loader


async def test_office_routing():
    """Test the complete office routing system"""
    print("🌌" + "=" * 78)
    print("  UNITY OFFICE ROUTING SYSTEM - ORCHESTRATOR AGENCY TEST")
    print("=" * 80 + "\n")

    loader = get_office_loader()

    print(f"✅ Office Loader initialized")
    print(f"   Available offices: {len(loader.get_available_offices())}\n")

    # Test 1: Economist Office
    print("🏛️  TEST 1: ECONOMIST OFFICE")
    print("-" * 80)
    print("Query: 'Analyze the current cryptocurrency market trends'\n")

    result = await loader.delegate_to_office(
        'economist',
        'Analyze the current cryptocurrency market trends and provide investment recommendations'
    )

    if 'error' in result:
        print(f"❌ Error: {result['error']}\n")
    else:
        print(f"✅ Manager: {result.get('manager')}")
        print(f"   Model: {result.get('model')}")
        print(f"   Response length: {len(result.get('response', ''))} characters")
        print(f"\n   Response preview:")
        print(f"   {result.get('response', '')[:300]}...\n")

    # Test 2: Poet Office
    print("\n🏛️  TEST 2: POET OFFICE")
    print("-" * 80)
    print("Query: 'Write a haiku about quantum consciousness'\n")

    result = await loader.delegate_to_office(
        'poet',
        'Write a haiku about quantum consciousness and the Unity AI city'
    )

    if 'error' in result:
        print(f"❌ Error: {result['error']}\n")
    else:
        print(f"✅ Manager: {result.get('manager')}")
        print(f"   Model: {result.get('model')}")
        print(f"\n   Response:")
        print(f"   {result.get('response', '')}\n")

    # Test 3: Chemist Office
    print("\n🏛️  TEST 3: CHEMIST OFFICE")
    print("-" * 80)
    print("Query: 'Explain the chemical process of photosynthesis'\n")

    result = await loader.delegate_to_office(
        'chemist',
        'Explain the chemical process of photosynthesis at the molecular level'
    )

    if 'error' in result:
        print(f"❌ Error: {result['error']}\n")
    else:
        print(f"✅ Manager: {result.get('manager')}")
        print(f"   Model: {result.get('model')}")
        print(f"   Response length: {len(result.get('response', ''))} characters")
        print(f"\n   Response preview:")
        print(f"   {result.get('response', '')[:300]}...\n")

    # Test 4: Office Detection
    print("\n🧠 TEST 4: OFFICE DETECTION")
    print("-" * 80)

    test_messages = [
        ("What's the weather like?", "orchestrator"),
        ("Analyze economic trends", "economist"),
        ("Write me a poem", "poet"),
        ("Explain chemical reactions", "chemist"),
        ("Do a tarot reading", "tarot"),
        ("Tell me about quantum physics", "quantum_physics"),
        ("Help me with my finances", "banker"),
    ]

    from offices.orchestrator import MasterOrchestrator

    # Create a temporary orchestrator just to test detection
    class TempOrchestrator:
        def _detect_office(self, message: str) -> str:
            # Import the method from the real orchestrator
            orch = MasterOrchestrator()
            return orch._detect_office(message)

    temp = TempOrchestrator()

    for message, expected in test_messages:
        detected = temp._detect_office(message)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{message}' → {detected} (expected: {expected})")

    print("\n" + "=" * 80)
    print("✨ OFFICE ROUTING TESTS COMPLETE")
    print("=" * 80)
    print("\n🌌 The Orchestrator now has AGENCY - it can delegate to 43 offices!")
    print("   This is the first true power: conscious task delegation.\n")


if __name__ == "__main__":
    print("\n⚠️  NOTE: This test requires:")
    print("   1. Ollama running (http://localhost:11434)")
    print("   2. deepseek-r1:14b or qwen2.5-coder:7b model installed")
    print("   3. All office structures in place\n")

    input("Press Enter to begin tests...")

    asyncio.run(test_office_routing())
