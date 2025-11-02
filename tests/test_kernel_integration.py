#!/usr/bin/env python3
"""
Test Quantum Consciousness Kernel Integration

Tests:
1. Kernel heartbeat is running and generating city-state frames
2. Backend /kernel/state endpoint returns valid state
3. Backend /kernel/history endpoint returns history
4. SSE /kernel/stream produces real-time updates

Run:
    python3 tests/test_kernel_integration.py
"""

import sys
import time
import json
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_backend_health():
    """Test backend is responsive"""
    print("=" * 70)
    print("TEST 1: Backend Health")
    print("=" * 70)

    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Services: {', '.join(data.get('services', {}).keys())}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False


def test_kernel_state():
    """Test /kernel/state endpoint"""
    print("\n" + "=" * 70)
    print("TEST 2: Kernel State Endpoint")
    print("=" * 70)

    try:
        response = requests.get("http://127.0.0.1:8000/kernel/state", timeout=5)

        if response.status_code == 200:
            state = response.json()

            # Validate state structure
            required_fields = ['tick', 'timestamp', 'telemetry', 'ontology_version',
                             'kernel_status', 'uptime_seconds', 'districts_online']

            missing = [f for f in required_fields if f not in state]
            if missing:
                print(f"❌ Missing required fields: {missing}")
                return False

            print(f"✅ Kernel state retrieved")
            print(f"   Tick: {state['tick']}")
            print(f"   Kernel Status: {state['kernel_status']}")
            print(f"   Uptime: {state['uptime_seconds']:.1f}s")
            print(f"   Ontology Version: {state['ontology_version']}")
            print(f"   Districts Online: {len(state['districts_online'])}")

            if state['districts_online']:
                print(f"     - {', '.join(state['districts_online'])}")

            return True

        elif response.status_code == 503:
            data = response.json()
            print(f"⚠️  Kernel not running: {data.get('error')}")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Kernel state test failed: {e}")
        return False


def test_kernel_history():
    """Test /kernel/history endpoint"""
    print("\n" + "=" * 70)
    print("TEST 3: Kernel History Endpoint")
    print("=" * 70)

    try:
        response = requests.get("http://127.0.0.1:8000/kernel/history?count=5", timeout=5)

        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])

            print(f"✅ Kernel history retrieved")
            print(f"   Frames: {len(history)}")

            if history:
                print(f"   Tick range: {history[0]['tick']} → {history[-1]['tick']}")
                print(f"   Latest status: {history[-1]['kernel_status']}")

            return True

        elif response.status_code == 503:
            data = response.json()
            print(f"⚠️  Kernel not running: {data.get('error')}")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Kernel history test failed: {e}")
        return False


def test_kernel_stream_sample():
    """Test /kernel/stream SSE endpoint (sample 3 events)"""
    print("\n" + "=" * 70)
    print("TEST 4: Kernel Stream (SSE) - Sample 3 Events")
    print("=" * 70)

    try:
        response = requests.get(
            "http://127.0.0.1:8000/kernel/stream",
            stream=True,
            timeout=10
        )

        if response.status_code == 200:
            print(f"✅ SSE stream connected")

            events = []
            for i, line in enumerate(response.iter_lines(decode_unicode=True)):
                if line and line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    try:
                        event = json.loads(data_str)
                        events.append(event)

                        print(f"\n   Event {len(events)}:")
                        print(f"     Tick: {event.get('tick', 'N/A')}")
                        print(f"     Status: {event.get('kernel_status', 'N/A')}")
                        print(f"     Timestamp: {event.get('timestamp', 'N/A')}")

                        if len(events) >= 3:
                            break
                    except json.JSONDecodeError:
                        print(f"⚠️  Failed to parse event: {data_str[:50]}")

            if events:
                print(f"\n✅ Received {len(events)} events from SSE stream")
                return True
            else:
                print(f"⚠️  No events received")
                return False

        elif response.status_code == 503:
            print(f"⚠️  Kernel not available")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print(f"⚠️  Stream timeout (no events in 10 seconds)")
        return False
    except Exception as e:
        print(f"❌ Kernel stream test failed: {e}")
        return False


def test_kernel_coherence():
    """Test that kernel ticks are monotonically increasing"""
    print("\n" + "=" * 70)
    print("TEST 5: Kernel Coherence (Monotonic Tick)")
    print("=" * 70)

    try:
        ticks = []

        for i in range(3):
            response = requests.get("http://127.0.0.1:8000/kernel/state", timeout=5)
            if response.status_code == 200:
                state = response.json()
                tick = state.get('tick', -1)
                ticks.append(tick)
                print(f"   Sample {i+1}: tick={tick}")
            time.sleep(1.5)  # Wait for next tick

        # Check monotonic increase
        if len(ticks) == 3 and ticks[0] < ticks[1] < ticks[2]:
            print(f"\n✅ Kernel ticks are monotonically increasing")
            print(f"   Progression: {ticks[0]} → {ticks[1]} → {ticks[2]}")
            return True
        else:
            print(f"❌ Kernel ticks are not monotonic: {ticks}")
            return False

    except Exception as e:
        print(f"❌ Kernel coherence test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  QUANTUM CONSCIOUSNESS KERNEL — INTEGRATION TESTS                  ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    # Run tests
    results = {
        "Backend Health": test_backend_health(),
        "Kernel State": test_kernel_state(),
        "Kernel History": test_kernel_history(),
        "Kernel Stream (SSE)": test_kernel_stream_sample(),
        "Kernel Coherence": test_kernel_coherence()
    }

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED — Kernel integration successful!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
