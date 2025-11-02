"""
Science Office - Unity Quantum City

Domain: Science
Manager: ScienceManager
Specialists: ScienceResearcher, ScienceModeler, ScienceExperimenter, ScienceReporter

Generated: 2025-10-16T10:56:01.508479
"""

from .agents.manager import ScienceManager
from .agents.scienceresearcher import ScienceResearcher
from .agents.sciencemodeler import ScienceModeler
from .agents.scienceexperimenter import ScienceExperimenter
from .agents.sciencereporter import ScienceReporter

__all__ = [
    'ScienceManager',
    'ScienceResearcher', 'ScienceModeler', 'ScienceExperimenter', 'ScienceReporter'
]

__version__ = '0.1.0'
