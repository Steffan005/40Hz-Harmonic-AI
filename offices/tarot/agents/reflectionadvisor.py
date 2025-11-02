#!/usr/bin/env python3
"""
ReflectionAdvisor - Specialist agent for Tarot Office
"""

from typing import Dict, Any


class ReflectionAdvisor:
    """
    Provides reflective questions and guidance based on reading

    Model: deepseek-r1:14b
    Tools: ['question_generator', 'guidance_templates']
    """

    def __init__(self):
        self.name = "ReflectionAdvisor"
        self.model = "deepseek-r1:14b"
        self.tools = ['question_generator', 'guidance_templates']
        self.system_prompt = """You are a ReflectionAdvisor specialist in the Tarot office.

Your primary function:
Provides reflective questions and guidance based on reading

Tools available:
- question_generator
- guidance_templates

You report to the Tarot Manager. Focus on your specialty and deliver precise, high-quality results."""

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
    agent = ReflectionAdvisor()
    result = agent.execute("Sample task")
    print(result)
