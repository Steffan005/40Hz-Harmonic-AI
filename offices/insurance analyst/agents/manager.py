#!/usr/bin/env python3
"""
Insurance AnalystManager - Coordination and oversight for Insurance Analyst Office
"""

from typing import Dict, List, Any


class Insurance AnalystManager:
    """
    Manager agent for Insurance Analyst office.

    Coordinates 4 specialist agents:
        - InsuranceAnalystAnalyst: Analyzes market data and financial statements for Insurance Analyst
    - InsuranceAnalystRiskAssessor: Evaluates and quantifies risks for Insurance Analyst
    - InsuranceAnalystAdvisor: Recommends investment strategies for Insurance Analyst
    - InsuranceAnalystComplianceChecker: Ensures regulatory compliance for Insurance Analyst
    """

    def __init__(self):
        self.domain = "Insurance Analyst"
        self.model = "deepseek-r1:14b"
        self.specialists = ['InsuranceAnalystAnalyst', 'InsuranceAnalystRiskAssessor', 'InsuranceAnalystAdvisor', 'InsuranceAnalystComplianceChecker']
        self.tools = ['market_data_api', 'risk_model', 'compliance_engine']

        # System prompt
        self.system_prompt = """You are the Insurance Analyst Manager, overseeing 4 specialist agents.

Your responsibilities:
1. Decompose user requests into subtasks for specialists
2. Coordinate specialist outputs into coherent responses
3. Maintain domain knowledge in the shared memory graph
4. Optimize workflows through the evolution loop

Specialists under your supervision:
- InsuranceAnalystAnalyst: Analyzes market data and financial statements for Insurance Analyst
- InsuranceAnalystRiskAssessor: Evaluates and quantifies risks for Insurance Analyst
- InsuranceAnalystAdvisor: Recommends investment strategies for Insurance Analyst
- InsuranceAnalystComplianceChecker: Ensures regulatory compliance for Insurance Analyst

Always prioritize accuracy, coherence, and user value."""

    def decompose_task(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Decompose user request into specialist subtasks.

        Args:
            user_request: User's query or request

        Returns:
            List of subtasks for specialists
        """
        # Stub: In production, would use LLM to decompose
        return [
            {"specialist": s, "task": f"Process {user_request} via {s}"}
            for s in self.specialists
        ]

    def synthesize_results(self, specialist_outputs: List[Dict]) -> str:
        """
        Synthesize specialist outputs into coherent response.

        Args:
            specialist_outputs: Results from each specialist

        Returns:
            Unified response
        """
        # Stub: In production, would use LLM to synthesize
        return "\n\n".join(
            f"{o['specialist']}: {o['result']}"
            for o in specialist_outputs
        )

    def execute(self, user_request: str) -> Dict[str, Any]:
        """
        Execute complete workflow: decompose → delegate → synthesize.

        Args:
            user_request: User's request

        Returns:
            Final result with metadata
        """
        subtasks = self.decompose_task(user_request)

        # Simulate specialist execution (would call actual agents in production)
        specialist_outputs = [
            {"specialist": st["specialist"], "result": f"[Stub] {st['task']}"}
            for st in subtasks
        ]

        final_result = self.synthesize_results(specialist_outputs)

        return {
            "domain": self.domain,
            "request": user_request,
            "subtasks": subtasks,
            "result": final_result,
            "metadata": {
                "model": self.model,
                "specialists_used": self.specialists
            }
        }


# Example usage
if __name__ == "__main__":
    manager = Insurance AnalystManager()
    result = manager.execute("Sample request for Insurance Analyst")
    print(result)
