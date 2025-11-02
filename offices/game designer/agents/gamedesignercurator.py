#!/usr/bin/env python3
"""
GameDesignerCurator - Specialist agent for Game Designer Office
"""

from typing import Dict, Any


class GameDesignerCurator:
    """
    Selects and organizes collections for Game Designer

    Model: deepseek-r1:14b
    Tools: ['generation_engine', 'style_analyzer', 'gallery_manager']
    """

    def __init__(self):
        self.name = "GameDesignerCurator"
        self.model = "deepseek-r1:14b"
        self.tools = ['generation_engine', 'style_analyzer', 'gallery_manager']
        self.system_prompt = """You are a GameDesignerCurator specialist in the Game Designer office.

Your primary function:
Selects and organizes collections for Game Designer

Tools available:
- generation_engine
- style_analyzer
- gallery_manager

You report to the Game Designer Manager. Focus on your specialty and deliver precise, high-quality results."""

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
    agent = GameDesignerCurator()
    result = agent.execute("Sample task")
    print(result)
