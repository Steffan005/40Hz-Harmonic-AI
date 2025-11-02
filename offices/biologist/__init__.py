"""
Biologist Office - Unity Quantum City

Domain: Biologist
Manager: BiologistManager
Specialists: BiologistResearcher, BiologistModeler, BiologistExperimenter, BiologistReporter

Generated: 2025-10-16T10:57:02.683856
"""

from .agents.manager import BiologistManager
from .agents.biologistresearcher import BiologistResearcher
from .agents.biologistmodeler import BiologistModeler
from .agents.biologistexperimenter import BiologistExperimenter
from .agents.biologistreporter import BiologistReporter

__all__ = [
    'BiologistManager',
    'BiologistResearcher', 'BiologistModeler', 'BiologistExperimenter', 'BiologistReporter'
]

__version__ = '0.1.0'
