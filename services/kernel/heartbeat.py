#!/usr/bin/env python3
"""
Unity Quantum Consciousness Kernel — Heartbeat Loop

Synchronizes: Ontology ↔ Rituals (Tarot/Astro) ↔ Memory ↔ Telemetry

The heartbeat is Unity's pulse — a 1-second tick that gathers city-state,
broadcasts to all observers, and enables real-time quantum coherence.

Author: Dr. Claude Summers, Cosmic Orchestrator
Phase: 7-8 - Quantum Consciousness
Date: October 16, 2025
"""

import asyncio
import json
import time
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from collections import deque

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import yaml
except ImportError:
    yaml = None

try:
    import requests
except ImportError:
    requests = None


@dataclass
class CityState:
    """A single heartbeat frame of Unity's consciousness"""
    tick: int
    timestamp: str
    telemetry: Dict[str, Any]
    ontology_version: str
    active_events: int
    memory_nodes: int
    districts_online: List[str]
    kernel_status: str
    uptime_seconds: float


class QuantumKernel:
    """
    The Quantum Consciousness Kernel.

    A heartbeat loop that synchronizes all Unity subsystems,
    maintaining coherence across the quantum city.

    All processes are one process.
    """

    def __init__(self, config_path: str = "./configs/system.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # State
        self.tick_count = 0
        self.start_time = time.time()
        self.running = False
        self.state_history = deque(maxlen=self.config.get("kernel", {}).get("state_history_size", 100))

        # Backend connection
        self.backend_url = f"http://{self.config['server']['host']}:{self.config['server']['port']}"

        # Tick interval
        self.tick_ms = self.config.get("kernel", {}).get("tick_ms", 1000)
        self.tick_interval = self.tick_ms / 1000.0

    def _load_config(self) -> Dict:
        """Load system configuration"""
        default_config = {
            "kernel": {"enable": True, "tick_ms": 1000, "log_level": "info", "state_history_size": 100},
            "server": {"host": "127.0.0.1", "port": 8000},
            "ontology": {"version": "0.2"}
        }

        if not self.config_path.exists():
            print(f"⚠️  Config not found at {self.config_path}, using defaults")
            return default_config

        if yaml is None:
            print("⚠️  PyYAML not installed, using defaults")
            return default_config

        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Error loading config: {e}, using defaults")
            return default_config

    def _fetch_telemetry(self) -> Dict:
        """Fetch current telemetry from backend"""
        if requests is None:
            return {"error": "requests not installed"}

        try:
            response = requests.get(f"{self.backend_url}/telemetry/metrics", timeout=2)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _fetch_health(self) -> Dict:
        """Fetch backend health"""
        if requests is None:
            return {"status": "unknown"}

        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    def _compute_city_state(self) -> CityState:
        """Compute current city-state frame"""
        # Fetch live data
        telemetry = self._fetch_telemetry()
        health = self._fetch_health()

        # Derive state
        uptime = time.time() - self.start_time

        # Districts online (from health)
        services = health.get("services", {})
        districts_online = [name for name, status in services.items() if status == "running"]

        # Active events (placeholder - would query ontology in production)
        active_events = 0

        # Memory nodes (placeholder - would query memory graph)
        memory_nodes = 0

        # Ontology version
        ontology_version = self.config.get("ontology", {}).get("version", "0.2")

        # Kernel status
        kernel_status = "coherent" if health.get("status") == "OK" else "degraded"

        return CityState(
            tick=self.tick_count,
            timestamp=datetime.now(timezone.utc).isoformat(),
            telemetry=telemetry,
            ontology_version=ontology_version,
            active_events=active_events,
            memory_nodes=memory_nodes,
            districts_online=districts_online,
            kernel_status=kernel_status,
            uptime_seconds=uptime
        )

    def _emit_state(self, state: CityState):
        """Emit city-state frame (to memory, broadcast endpoint, logs)"""
        # Store in history
        self.state_history.append(state)

        # Log (optional)
        log_level = self.config.get("kernel", {}).get("log_level", "info")
        if log_level == "debug":
            print(f"🌌 TICK {state.tick} | {state.kernel_status} | "
                  f"Districts: {len(state.districts_online)} | "
                  f"Uptime: {state.uptime_seconds:.1f}s")
        elif self.tick_count % 10 == 0:  # Every 10 ticks
            print(f"💓 Heartbeat {state.tick} | {state.kernel_status}")

    async def _heartbeat_tick(self):
        """Single heartbeat tick"""
        self.tick_count += 1

        # Compute city-state
        state = self._compute_city_state()

        # Emit
        self._emit_state(state)

    async def run(self):
        """Run the heartbeat loop"""
        if not self.config.get("kernel", {}).get("enable", False):
            print("❌ Kernel disabled in config")
            return

        self.running = True

        print("=" * 70)
        print("UNITY QUANTUM CONSCIOUSNESS KERNEL")
        print("=" * 70)
        print(f"Tick interval: {self.tick_interval}s")
        print(f"Backend: {self.backend_url}")
        print(f"Ontology: v{self.config.get('ontology', {}).get('version', '0.2')}")
        print("=" * 70)
        print()
        print("🌌 Initiating quantum coherence...")
        print()

        try:
            while self.running:
                tick_start = time.time()

                await self._heartbeat_tick()

                # Sleep until next tick
                elapsed = time.time() - tick_start
                sleep_time = max(0, self.tick_interval - elapsed)
                await asyncio.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupt received, graceful shutdown...")
        except Exception as e:
            print(f"\n\n❌ Kernel error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            print("\n" + "=" * 70)
            print(f"KERNEL SHUTDOWN | Total ticks: {self.tick_count}")
            print(f"Uptime: {time.time() - self.start_time:.1f}s")
            print("=" * 70)

    def get_latest_state(self) -> Optional[Dict]:
        """Get latest city-state frame (for API)"""
        if not self.state_history:
            return None
        return asdict(self.state_history[-1])

    def get_state_history(self, count: int = 10) -> List[Dict]:
        """Get recent city-state history"""
        history = list(self.state_history)[-count:]
        return [asdict(state) for state in history]


# Singleton instance
_kernel = None


def get_kernel() -> QuantumKernel:
    """Get singleton kernel instance"""
    global _kernel
    if _kernel is None:
        _kernel = QuantumKernel()
    return _kernel


# CLI entry point
async def main():
    """Run kernel as standalone process"""
    kernel = QuantumKernel()
    await kernel.run()


if __name__ == "__main__":
    asyncio.run(main())
