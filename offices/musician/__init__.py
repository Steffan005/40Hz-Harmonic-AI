"""
Musician Office - Unity Quantum City

Domain: Musician
Manager: MusicianManager
Specialists: MusicianCreator, MusicianCritic, MusicianCurator, MusicianPerformer

Generated: 2025-10-16T10:57:02.696874
"""

from .agents.manager import MusicianManager
from .agents.musiciancreator import MusicianCreator
from .agents.musiciancritic import MusicianCritic
from .agents.musiciancurator import MusicianCurator
from .agents.musicianperformer import MusicianPerformer

__all__ = [
    'MusicianManager',
    'MusicianCreator', 'MusicianCritic', 'MusicianCurator', 'MusicianPerformer'
]

__version__ = '0.1.0'
