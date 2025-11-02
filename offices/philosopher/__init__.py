"""
Philosopher Office - Unity Quantum City

Domain: Philosopher
Manager: PhilosopherManager
Specialists: ArgumentAnalyzer, ConceptSynthesizer, EthicsAdvisor, DialogueGenerator

Generated: 2025-10-29T09:08:28.642340
"""

from .agents.manager import PhilosopherManager
from .agents.argumentanalyzer import ArgumentAnalyzer
from .agents.conceptsynthesizer import ConceptSynthesizer
from .agents.ethicsadvisor import EthicsAdvisor
from .agents.dialoguegenerator import DialogueGenerator

__all__ = [
    'PhilosopherManager',
    'ArgumentAnalyzer', 'ConceptSynthesizer', 'EthicsAdvisor', 'DialogueGenerator'
]

__version__ = '0.1.0'
