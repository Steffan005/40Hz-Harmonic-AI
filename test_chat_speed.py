#!/usr/bin/env python3
"""Test Orchestrator chat speed with cloud LLM"""

import asyncio
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "offices"))

async def test_chat_speed():
    from orchestrator import get_orchestrator

    orchestrator = get_orchestrator()

    print("\n" + "="*70)
    print("⚡ TESTING CLOUD LLM SPEED")
    print("="*70)
    print(f"Cloud enabled: {orchestrator.cloud_enabled}")
    print(f"Model: {orchestrator.cloud_model}")

    message = "Say hello in exactly 3 words"
    print(f"\nSending: '{message}'")

    start_time = time.time()
    print("⏱️  Starting timer...")

    response = ""
    async for chunk in orchestrator.chat(message, stream=False):
        response += chunk

    elapsed = time.time() - start_time

    print(f"\n📝 Response: {response}")
    print(f"⏱️  Time taken: {elapsed:.2f} seconds")

    if elapsed < 10:
        print("✅ FAST RESPONSE - Cloud LLM is working!")
    else:
        print("🐌 SLOW RESPONSE - Using local model")

    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_chat_speed())