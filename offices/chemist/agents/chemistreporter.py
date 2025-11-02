#!/usr/bin/env python3
"""
ChemistReporter - Specialist agent for Chemist Office
"""

from typing import Dict, Any


class ChemistReporter:
    """
    Writes research summaries and papers for Chemist

    Model: deepseek-r1:14b
    Tools: ['literature_search', 'simulation_engine', 'data_visualizer']
    """

    def __init__(self):
        self.name = "ChemistReporter"
        self.model = "deepseek-r1:14b"
        self.tools = ['literature_search', 'simulation_engine', 'data_visualizer']
        self.system_prompt = """You are a ChemistReporter specialist in the Chemist office.

Your primary function:
Writes research summaries and papers for Chemist

Tools available:
- literature_search
- simulation_engine
- data_visualizer

You report to the Chemist Manager. Focus on your specialty and deliver precise, high-quality results."""

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
    agent = ChemistReporter()
    result = agent.execute("Sample task")
    print(result)
