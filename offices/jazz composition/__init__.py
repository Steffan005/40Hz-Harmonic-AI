"""
Jazz Composition Office - Unity Quantum City

Domain: Jazz Composition
Manager: Jazz CompositionManager
Specialists: JazzCompositionCreator, JazzCompositionCritic, JazzCompositionCurator, JazzCompositionPerformer

Generated: 2025-10-16T10:56:01.500930
"""

from .agents.manager import Jazz CompositionManager
from .agents.jazzcompositioncreator import JazzCompositionCreator
from .agents.jazzcompositioncritic import JazzCompositionCritic
from .agents.jazzcompositioncurator import JazzCompositionCurator
from .agents.jazzcompositionperformer import JazzCompositionPerformer

__all__ = [
    'Jazz CompositionManager',
    'JazzCompositionCreator', 'JazzCompositionCritic', 'JazzCompositionCurator', 'JazzCompositionPerformer'
]

__version__ = '0.1.0'
