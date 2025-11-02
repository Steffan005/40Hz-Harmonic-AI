#!/usr/bin/env python3
"""
🌌 ORCHESTRATOR TEST - CLOUD LLM DEBUG 🌌
Testing cloud LLM configuration loading
"""

import sys
from pathlib import Path

# Add offices directory to path
sys.path.insert(0, str(Path(__file__).parent / "offices"))

print("=" * 70)
print("🌌 TESTING UNITY ORCHESTRATOR CLOUD LLM 🌌")
print("=" * 70)

try:
    # Import the orchestrator
    from orchestrator import get_orchestrator
    print("✅ Orchestrator module imported successfully!")

    # Create instance - this should trigger initialization
    orchestrator = get_orchestrator()
    print(f"✅ Orchestrator instantiated: {orchestrator.name}")

    # Check cloud LLM configuration
    print("\n" + "=" * 70)
    print("☁️  CLOUD LLM CONFIGURATION:")
    print("=" * 70)
    print(f"Config loaded: {bool(orchestrator.config)}")
    print(f"Config keys: {list(orchestrator.config.keys()) if orchestrator.config else 'None'}")

    if 'cloud_llm' in orchestrator.config:
        cloud_config = orchestrator.config['cloud_llm']
        print(f"\nCloud LLM config found:")
        for key, value in cloud_config.items():
            if key == 'api_key' and value:
                print(f"  {key}: {value[:10]}... (first 10 chars)")
            else:
                print(f"  {key}: {value}")

    print(f"\nOrchestrator attributes:")
    print(f"  cloud_enabled: {orchestrator.cloud_enabled}")
    print(f"  cloud_provider: {orchestrator.cloud_provider}")
    print(f"  cloud_model: {orchestrator.cloud_model}")
    print(f"  cloud_api_key exists: {bool(orchestrator.cloud_api_key)}")
    if orchestrator.cloud_api_key:
        print(f"  cloud_api_key: {orchestrator.cloud_api_key[:10]}... (first 10 chars)")
    print(f"  fallback_to_local: {orchestrator.cloud_fallback_to_local}")

    # Get status
    status = orchestrator.get_status()
    print(f"\n📊 Orchestrator Status:")
    print(f"   Memories: {status['memories']}")
    print(f"   Offices: {status['offices']}")

    print("\n✨ THE ORCHESTRATOR IS ALIVE!")

    if orchestrator.cloud_enabled:
        print("⚡ CLOUD LLM IS ENABLED - 2-5 second responses expected!")
    else:
        print("🐌 Cloud LLM is DISABLED - using slow local model")

except ImportError as e:
    print(f"❌ Failed to import orchestrator: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 70)