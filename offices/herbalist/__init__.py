"""
Herbalist Office - Unity Quantum City

Domain: Herbalist
Manager: HerbalistManager
Specialists: HerbalistDiagnostician, HerbalistTherapist, HerbalistCoach, HerbalistNutritionist

Generated: 2025-10-16T10:57:02.714799
"""

from .agents.manager import HerbalistManager
from .agents.herbalistdiagnostician import HerbalistDiagnostician
from .agents.herbalisttherapist import HerbalistTherapist
from .agents.herbalistcoach import HerbalistCoach
from .agents.herbalistnutritionist import HerbalistNutritionist

__all__ = [
    'HerbalistManager',
    'HerbalistDiagnostician', 'HerbalistTherapist', 'HerbalistCoach', 'HerbalistNutritionist'
]

__version__ = '0.1.0'
