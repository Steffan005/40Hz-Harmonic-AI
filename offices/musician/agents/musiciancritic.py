#!/usr/bin/env python3
"""
MusicianCritic - Specialist agent for Musician Office
"""

from typing import Dict, Any


class MusicianCritic:
    """
    Analyzes and critiques artistic works for Musician

    Model: deepseek-r1:14b
    Tools: ['generation_engine', 'style_analyzer', 'gallery_manager']
    """

    def __init__(self):
        self.name = "MusicianCritic"
        self.model = "deepseek-r1:14b"
        self.tools = ['generation_engine', 'style_analyzer', 'gallery_manager']
        self.system_prompt = """You are a MusicianCritic specialist in the Musician office.

Your primary function:
Analyzes and critiques artistic works for Musician

Tools available:
- generation_engine
- style_analyzer
- gallery_manager

You report to the Musician Manager. Focus on your specialty and deliver precise, high-quality results."""

    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute specialist task.

        Args:
            task: Task description
            context: Optional context from other agents

        Returns:
            Task result
        """
        # Stub: In production, would call LLM with system_prompt + task
        return {
            "specialist": self.name,
            "task": task,
            "result": f"[Stub] {self.name} processed: {task}",
            "model": self.model,
            "tools_used": self.tools
        }


# Example usage
if __name__ == "__main__":
    agent = MusicianCritic()
    result = agent.execute("Sample task")
    print(result)
