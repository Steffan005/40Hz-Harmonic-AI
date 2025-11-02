"""
Chemist Office - Unity Quantum City

Domain: Chemist
Manager: ChemistManager
Specialists: ChemistResearcher, ChemistModeler, ChemistExperimenter, ChemistReporter

Generated: 2025-10-16T10:57:02.680226
"""

from .agents.manager import ChemistManager
from .agents.chemistresearcher import ChemistResearcher
from .agents.chemistmodeler import ChemistModeler
from .agents.chemistexperimenter import ChemistExperimenter
from .agents.chemistreporter import ChemistReporter

__all__ = [
    'ChemistManager',
    'ChemistResearcher', 'ChemistModeler', 'ChemistExperimenter', 'ChemistReporter'
]

__version__ = '0.1.0'
