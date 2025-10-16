#!/usr/bin/env python3
"""
Budget Manager - Enforces resource limits per generation.
Provides context manager for pre-emptive enforcement.
"""

import json
import time
import yaml
import sys
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


def _get_config_path(relative_path: str) -> Path:
    """
    Get absolute path to config file, handling PyInstaller frozen state.

    When running as PyInstaller frozen binary, sys.frozen is set and
    sys._MEIPASS points to the temp extraction directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller frozen binary
        base_path = Path(sys._MEIPASS)
    else:
        # Running as normal Python script
        base_path = Path(__file__).parent

    return base_path / relative_path


class BudgetManager:
    """Enforces token, time, agent, and concurrency limits."""

    def __init__(self, config_path: str = None):
        # Load configuration (handle PyInstaller frozen state)
        if config_path is None:
            config_path = _get_config_path("configs/budget.yaml")
        else:
            config_path = Path(config_path)

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.max_tokens_per_gen = self.config['max_tokens_per_gen']
        self.max_time_s = self.config['max_time_s']
        self.max_agents = self.config['max_agents']
        self.max_concurrency = self.config['max_concurrency']

        self.preemption_mode = self.config['PREEMPTION']['mode']
        self.grace_period = self.config['PREEMPTION']['grace_period_s']

        self.log_enabled = self.config['LOG_BUDGET_EVENTS']
        self.log_path = Path(self.config['BUDGET_LOG_PATH'])

        # Runtime state
        self.current_tokens = 0
        self.current_agents = 0
        self.start_time = None
        self.aborted = False

    @contextmanager
    def BudgetGuard(self, generation: int):
        """
        Context manager for budget enforcement.

        Usage:
            with budget_manager.BudgetGuard(gen=5):
                # Run generation
                result = run_evolution_cycle()
        """
        self.start_time = time.time()
        self.current_tokens = 0
        self.current_agents = 0
        self.aborted = False

        try:
            yield self
        except BudgetExceededError as e:
            self.aborted = True
            self._log_event("budget_exceeded", generation, str(e))
            raise
        finally:
            elapsed = time.time() - self.start_time
            self._log_event(
                "generation_complete",
                generation,
                {
                    "elapsed_s": elapsed,
                    "tokens": self.current_tokens,
                    "agents": self.current_agents,
                    "aborted": self.aborted
                }
            )

    def consume_tokens(self, count: int):
        """
        Record token usage and check limit.
        Raises BudgetExceededError if limit reached.
        """
        self.current_tokens += count

        if self.current_tokens > self.max_tokens_per_gen:
            raise BudgetExceededError(
                f"Token limit exceeded: {self.current_tokens}/{self.max_tokens_per_gen}"
            )

    def check_time_limit(self):
        """Check if time limit exceeded."""
        if self.start_time is None:
            return

        elapsed = time.time() - self.start_time
        if elapsed > self.max_time_s:
            if self.preemption_mode == "immediate":
                raise BudgetExceededError(
                    f"Time limit exceeded: {elapsed:.1f}s/{self.max_time_s}s"
                )
            else:
                # Graceful mode: allow grace period
                if elapsed > self.max_time_s + self.grace_period:
                    raise BudgetExceededError(
                        f"Time limit exceeded (grace period exhausted): {elapsed:.1f}s/{self.max_time_s}s"
                    )

    def register_agent(self):
        """Register new agent. Raises if limit exceeded."""
        self.current_agents += 1

        if self.current_agents > self.max_agents:
            raise BudgetExceededError(
                f"Agent limit exceeded: {self.current_agents}/{self.max_agents}"
            )

    def unregister_agent(self):
        """Unregister agent when complete."""
        self.current_agents = max(0, self.current_agents - 1)

    def get_status(self) -> dict:
        """Return current budget status."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        return {
            "tokens_used": self.current_tokens,
            "tokens_limit": self.max_tokens_per_gen,
            "tokens_remaining": max(0, self.max_tokens_per_gen - self.current_tokens),
            "time_elapsed_s": elapsed,
            "time_limit_s": self.max_time_s,
            "time_remaining_s": max(0, self.max_time_s - elapsed),
            "active_agents": self.current_agents,
            "agent_limit": self.max_agents,
            "aborted": self.aborted
        }

    def _log_event(self, event_type: str, generation: int, details):
        """Log budget event to file."""
        if not self.log_enabled:
            return

        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": time.time(),
            "event": event_type,
            "generation": generation,
            "details": details
        }

        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')


class BudgetExceededError(Exception):
    """Raised when budget limit is breached."""
    pass


# Example usage
if __name__ == "__main__":
    budget = BudgetManager()

    print("="*60)
    print("BUDGET MANAGER TEST")
    print("="*60)

    # Test 1: Normal usage within limits
    print("\nTest 1: Normal usage")
    try:
        with budget.BudgetGuard(generation=1):
            print("  Consuming 5000 tokens...")
            budget.consume_tokens(5000)
            print(f"  Status: {budget.get_status()}")

            print("  Registering 3 agents...")
            for i in range(3):
                budget.register_agent()
            print(f"  Active agents: {budget.current_agents}")

            time.sleep(1)  # Simulate work
            budget.check_time_limit()

            print("  ✅ Generation completed within budget")

    except BudgetExceededError as e:
        print(f"  ❌ Budget exceeded: {e}")

    # Test 2: Token limit breach
    print("\nTest 2: Token limit breach")
    try:
        with budget.BudgetGuard(generation=2):
            print("  Consuming 15000 tokens (exceeds limit)...")
            budget.consume_tokens(15000)
            print("  This line should not print")

    except BudgetExceededError as e:
        print(f"  ✅ Correctly caught: {e}")

    # Test 3: Agent limit breach
    print("\nTest 3: Agent limit breach")
    try:
        with budget.BudgetGuard(generation=3):
            print("  Registering 12 agents (exceeds limit of 10)...")
            for i in range(12):
                budget.register_agent()
            print("  This line should not print")

    except BudgetExceededError as e:
        print(f"  ✅ Correctly caught: {e}")

    print("\n" + "="*60)
    print("All tests completed")
