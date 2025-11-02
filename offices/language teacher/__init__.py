"""
Language Teacher Office - Unity Quantum City

Domain: Language Teacher
Manager: Language TeacherManager
Specialists: LanguageTeacherTeacher, LanguageTeacherTutor, LanguageTeacherCurriculumDesigner, LanguageTeacherAssessor

Generated: 2025-10-16T10:57:02.728443
"""

from .agents.manager import Language TeacherManager
from .agents.languageteacherteacher import LanguageTeacherTeacher
from .agents.languageteachertutor import LanguageTeacherTutor
from .agents.languageteachercurriculumdesigner import LanguageTeacherCurriculumDesigner
from .agents.languageteacherassessor import LanguageTeacherAssessor

__all__ = [
    'Language TeacherManager',
    'LanguageTeacherTeacher', 'LanguageTeacherTutor', 'LanguageTeacherCurriculumDesigner', 'LanguageTeacherAssessor'
]

__version__ = '0.1.0'
