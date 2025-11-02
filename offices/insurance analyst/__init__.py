"""
Insurance Analyst Office - Unity Quantum City

Domain: Insurance Analyst
Manager: Insurance AnalystManager
Specialists: InsuranceAnalystAnalyst, InsuranceAnalystRiskAssessor, InsuranceAnalystAdvisor, InsuranceAnalystComplianceChecker

Generated: 2025-10-16T10:57:02.665084
"""

from .agents.manager import Insurance AnalystManager
from .agents.insuranceanalystanalyst import InsuranceAnalystAnalyst
from .agents.insuranceanalystriskassessor import InsuranceAnalystRiskAssessor
from .agents.insuranceanalystadvisor import InsuranceAnalystAdvisor
from .agents.insuranceanalystcompliancechecker import InsuranceAnalystComplianceChecker

__all__ = [
    'Insurance AnalystManager',
    'InsuranceAnalystAnalyst', 'InsuranceAnalystRiskAssessor', 'InsuranceAnalystAdvisor', 'InsuranceAnalystComplianceChecker'
]

__version__ = '0.1.0'
