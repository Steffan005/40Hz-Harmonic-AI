#!/usr/bin/env python3
"""
Model Preloader — Eliminate 9.7s First-Call Latency

Preloads all configured LLMs on backend startup to ensure instant first response.
Critical for production UX.
"""

import asyncio
import time
from typing import List, Dict
import litellm
from datetime import datetime


class ModelPreloader:
    """Preload LLMs into Ollama memory on backend startup."""

    def __init__(self, models: List[str] = None):
        self.models = models or [
            "deepseek-r1:14b",
            "qwen2.5-coder:7b"
        ]
        self.preload_status = {}
        self.total_preload_time = 0

    async def preload_single_model(self, model: str) -> Dict:
        """Preload single model with timing."""
        start_time = time.time()

        try:
            # Minimal inference to trigger model load
            response = await litellm.acompletion(
                model=f"ollama/{model}",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                temperature=0
            )

            load_time = time.time() - start_time

            result = {
                "model": model,
                "status": "loaded",
                "load_time": round(load_time, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "response_received": bool(response)
            }

            print(f"✅ {model} preloaded in {load_time:.2f}s")
            return result

        except Exception as e:
            load_time = time.time() - start_time

            result = {
                "model": model,
                "status": "failed",
                "load_time": round(load_time, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

            print(f"❌ {model} failed to preload: {e}")
            return result

    async def preload_all_models(self) -> Dict:
        """Preload all configured models concurrently."""
        print("\n" + "="*70)
        print("MODEL PRELOADER: Loading all LLMs into memory...")
        print("="*70)

        start_time = time.time()

        # Preload models in parallel
        tasks = [self.preload_single_model(model) for model in self.models]
        results = await asyncio.gather(*tasks)

        self.total_preload_time = time.time() - start_time

        # Build status dict
        for result in results:
            self.preload_status[result["model"]] = result

        # Summary
        successful = sum(1 for r in results if r["status"] == "loaded")
        failed = sum(1 for r in results if r["status"] == "failed")

        print("\n" + "="*70)
        print(f"PRELOAD COMPLETE: {successful}/{len(self.models)} models loaded")
        print(f"Total time: {self.total_preload_time:.2f}s")
        print("="*70 + "\n")

        return {
            "total_models": len(self.models),
            "successful": successful,
            "failed": failed,
            "total_time": round(self.total_preload_time, 2),
            "models": self.preload_status
        }

    def get_status(self) -> Dict:
        """Get current preload status."""
        return {
            "preloaded": bool(self.preload_status),
            "total_time": self.total_preload_time,
            "models": self.preload_status
        }


# Singleton instance
_preloader = None


def get_preloader() -> ModelPreloader:
    """Get singleton preloader instance."""
    global _preloader
    if _preloader is None:
        _preloader = ModelPreloader()
    return _preloader


async def preload_models_on_startup():
    """Main entry point for backend startup."""
    preloader = get_preloader()
    return await preloader.preload_all_models()


# CLI testing
if __name__ == "__main__":
    async def test_preload():
        preloader = ModelPreloader()
        result = await preloader.preload_all_models()

        print("\nPreload Status:")
        print(f"  Total models: {result['total_models']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Total time: {result['total_time']}s")

        for model, status in result['models'].items():
            print(f"\n  {model}:")
            print(f"    Status: {status['status']}")
            print(f"    Load time: {status['load_time']}s")

    asyncio.run(test_preload())
