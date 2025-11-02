"""
Economist Office - Unity Quantum City

Domain: Economist
Manager: EconomistManager
Specialists: EconomistAnalyst, EconomistRiskAssessor, EconomistAdvisor, EconomistComplianceChecker

Generated: 2025-10-16T10:57:02.672804
"""

from .agents.manager import EconomistManager
from .agents.economistanalyst import EconomistAnalyst
from .agents.economistriskassessor import EconomistRiskAssessor
from .agents.economistadvisor import EconomistAdvisor
from .agents.economistcompliancechecker import EconomistComplianceChecker

__all__ = [
    'EconomistManager',
    'EconomistAnalyst', 'EconomistRiskAssessor', 'EconomistAdvisor', 'EconomistComplianceChecker'
]

__version__ = '0.1.0'
