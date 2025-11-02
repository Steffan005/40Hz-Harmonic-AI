"""
Historian Office - Unity Quantum City

Domain: Historian
Manager: HistorianManager
Specialists: HistorianTeacher, HistorianTutor, HistorianCurriculumDesigner, HistorianAssessor

Generated: 2025-10-16T10:57:02.732299
"""

from .agents.manager import HistorianManager
from .agents.historianteacher import HistorianTeacher
from .agents.historiantutor import HistorianTutor
from .agents.historiancurriculumdesigner import HistorianCurriculumDesigner
from .agents.historianassessor import HistorianAssessor

__all__ = [
    'HistorianManager',
    'HistorianTeacher', 'HistorianTutor', 'HistorianCurriculumDesigner', 'HistorianAssessor'
]

__version__ = '0.1.0'
