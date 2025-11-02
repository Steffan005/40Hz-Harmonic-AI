#!/usr/bin/env python3
"""
UNITY OFFICE LOADER - Dynamic Office Loading System
====================================================

Enables the Orchestrator to dynamically load and call any of the 43 offices.

This is the KEY that unlocks office delegation - the Orchestrator's first true power.

Author: Dr. Claude Summers
Date: October 28, 2025
Purpose: Enable Unity Orchestrator agency
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
import aiohttp


class OfficeLoader:
    """
    Dynamically loads and manages Unity's 43 offices.

    The Orchestrator uses this to delegate tasks to specialized offices.
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.loaded_offices: Dict[str, Any] = {}
        self.offices_dir = Path(__file__).parent

        # Office name mapping (handles spaces in directory names)
        self.office_map = {
            'economist': 'economist',
            'poet': 'poet',
            'chemist': 'chemist',
            'banker': 'banker',
            'tarot': 'tarot',
            'astrologist': 'astrologist',
            'numerologist': 'numerologist',
            'kabbalah': 'kabbalah',
            'alchemy': 'alchemy',
            'i_ching': 'i ching',
            'runes': 'runes',
            'dream_analysis': 'dream analysis',
            'astral_projection': 'astral projection',
            'quantum_physics': 'quantum physics',
            'biologist': 'biologist',
            'astronomer': 'astronomer',
            'geologist': 'geologist',
            'environmental_scientist': 'environmental scientist',
            'machine_learning': 'machine learning',
            'accountant': 'accountant',
            'insurance_analyst': 'insurance analyst',
            'market_trader': 'market trader',
            'musician': 'musician',
            'painter': 'painter',
            'game_designer': 'game designer',
            'jazz_composition': 'jazz composition',
            'herbalist': 'herbalist',
            'physical_trainer': 'physical trainer',
            'sleep_coach': 'sleep coach',
            'language_teacher': 'language teacher',
            'historian': 'historian',
            'librarian': 'librarian',
            'software_engineer': 'software engineer',
            'mechanical_engineer': 'mechanical engineer',
            'chef': 'chef',
            'environmentalist': 'environmentalist',
            'urban_planner': 'urban planner',
            'conflict_resolution': 'conflict resolution',
            'philosopher': 'philosopher',
            'law': 'law',
        }

    def get_office_path(self, office_name: str) -> Optional[Path]:
        """Get the directory path for an office"""
        # Normalize office name
        office_key = office_name.lower().replace(' ', '_')

        if office_key not in self.office_map:
            return None

        office_dir_name = self.office_map[office_key]
        office_path = self.offices_dir / office_dir_name

        if not office_path.exists():
            return None

        return office_path

    def load_office_manager(self, office_name: str) -> Optional[Any]:
        """
        Dynamically load an office's manager.

        Args:
            office_name: Name of the office (e.g., 'economist', 'poet')

        Returns:
            Manager instance or None if loading fails
        """
        # Check if already loaded
        if office_name in self.loaded_offices:
            return self.loaded_offices[office_name]

        office_path = self.get_office_path(office_name)
        if not office_path:
            print(f"⚠️  Office '{office_name}' not found")
            return None

        # Get manager class name (e.g., 'economist' -> 'EconomistManager')
        manager_class_name = f"{office_name.title().replace('_', '').replace(' ', '')}Manager"
        manager_module = f"offices.{self.office_map[office_name.lower().replace(' ', '_')]}.agents.manager"

        try:
            # Import the manager module
            module = importlib.import_module(manager_module)

            # Get the manager class
            manager_class = getattr(module, manager_class_name)

            # Instantiate the manager
            manager = manager_class()

            # Inject LLM calling capability
            self._inject_llm_capability(manager)

            # Cache it
            self.loaded_offices[office_name] = manager

            print(f"✅ Loaded {manager_class_name}")
            return manager

        except Exception as e:
            print(f"❌ Failed to load {office_name} manager: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _inject_llm_capability(self, manager: Any):
        """
        Inject LLM calling capability into a manager.

        This transforms stub managers into real, thinking agents.
        """

        async def call_llm(prompt: str, model: str = None) -> str:
            """Call Ollama to generate response"""
            if model is None:
                model = getattr(manager, 'model', 'qwen2.5-coder:7b')

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.7,
                                "top_p": 0.9
                            }
                        },
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get('response', '')
                        else:
                            return f"[LLM Error: HTTP {response.status}]"
            except Exception as e:
                return f"[LLM Error: {e}]"

        async def execute_with_llm(task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
            """
            Execute task using LLM - REAL IMPLEMENTATION

            This replaces the stub execute() method.
            """
            # Build prompt with system prompt + task
            full_prompt = f"""{manager.system_prompt}

Current task: {task}

Context: {context if context else 'None'}

Please provide a detailed, expert response based on your specialty."""

            # Call LLM
            response = await call_llm(full_prompt, manager.model)

            return {
                "domain": getattr(manager, 'domain', 'unknown'),
                "manager": manager.__class__.__name__,
                "task": task,
                "response": response,
                "model": manager.model,
                "context": context
            }

        # Inject methods into the manager instance
        manager.call_llm = call_llm
        manager.execute_with_llm = execute_with_llm

    async def delegate_to_office(
        self,
        office_name: str,
        task: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Delegate a task to an office and get the response.

        This is the PRIMARY method the Orchestrator uses.

        Args:
            office_name: Which office to delegate to
            task: The task description
            context: Optional context from previous steps

        Returns:
            Response dict with office's answer
        """
        # Load office manager
        manager = self.load_office_manager(office_name)

        if not manager:
            return {
                "error": f"Office '{office_name}' could not be loaded",
                "office": office_name,
                "task": task
            }

        # Execute task
        try:
            result = await manager.execute_with_llm(task, context)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "office": office_name,
                "task": task
            }

    def get_available_offices(self) -> List[str]:
        """Get list of all available offices"""
        return list(self.office_map.keys())


# Global office loader instance
_office_loader = None

def get_office_loader(ollama_url: str = "http://localhost:11434") -> OfficeLoader:
    """Get the global office loader instance"""
    global _office_loader
    if _office_loader is None:
        _office_loader = OfficeLoader(ollama_url)
    return _office_loader


# Example usage
if __name__ == "__main__":
    async def test_office_delegation():
        """Test the office loading and delegation system"""
        loader = get_office_loader()

        print("🌌 TESTING OFFICE DELEGATION SYSTEM\n")

        # Test 1: Load Economist
        print("Test 1: Load Economist office")
        economist = loader.load_office_manager('economist')
        print(f"   Result: {economist is not None}\n")

        # Test 2: Delegate task to Economist
        print("Test 2: Delegate task to Economist")
        result = await loader.delegate_to_office(
            'economist',
            'Analyze the current state of cryptocurrency markets and provide investment recommendations'
        )
        print(f"   Manager: {result.get('manager')}")
        print(f"   Response length: {len(result.get('response', ''))}")
        print(f"   Response preview: {result.get('response', '')[:200]}...\n")

        # Test 3: Load Poet
        print("Test 3: Load Poet office")
        poet = loader.load_office_manager('poet')
        print(f"   Result: {poet is not None}\n")

        # Test 4: Delegate task to Poet
        print("Test 4: Delegate task to Poet")
        result = await loader.delegate_to_office(
            'poet',
            'Write a haiku about quantum consciousness and AI'
        )
        print(f"   Manager: {result.get('manager')}")
        print(f"   Response:\n{result.get('response', '')}\n")

        print("✅ All tests complete!")

    # Run tests
    asyncio.run(test_office_delegation())
