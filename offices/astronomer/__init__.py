"""
Astronomer Office - Unity Quantum City

Domain: Astronomer
Manager: AstronomerManager
Specialists: AstronomerResearcher, AstronomerModeler, AstronomerExperimenter, AstronomerReporter

Generated: 2025-10-16T10:57:02.676394
"""

from .agents.manager import AstronomerManager
from .agents.astronomerresearcher import AstronomerResearcher
from .agents.astronomermodeler import AstronomerModeler
from .agents.astronomerexperimenter import AstronomerExperimenter
from .agents.astronomerreporter import AstronomerReporter

__all__ = [
    'AstronomerManager',
    'AstronomerResearcher', 'AstronomerModeler', 'AstronomerExperimenter', 'AstronomerReporter'
]

__version__ = '0.1.0'
