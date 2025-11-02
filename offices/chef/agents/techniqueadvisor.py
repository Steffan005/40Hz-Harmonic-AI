#!/usr/bin/env python3
"""
TechniqueAdvisor - Specialist agent for Chef Office
"""

from typing import Dict, Any


class TechniqueAdvisor:
    """
    Recommends cooking techniques and equipment

    Model: deepseek-r1:14b
    Tools: ['technique_db', 'equipment_matcher']
    """

    def __init__(self):
        self.name = "TechniqueAdvisor"
        self.model = "deepseek-r1:14b"
        self.tools = ['technique_db', 'equipment_matcher']
        self.system_prompt = """You are a TechniqueAdvisor specialist in the Chef office.

Your primary function:
Recommends cooking techniques and equipment

Tools available:
- technique_db
- equipment_matcher

You report to the Chef Manager. Focus on your specialty and deliver precise, high-quality results."""

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
    agent = TechniqueAdvisor()
    result = agent.execute("Sample task")
    print(result)
