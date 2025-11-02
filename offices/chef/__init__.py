"""
Chef Office - Unity Quantum City

Domain: Chef
Manager: ChefManager
Specialists: RecipeOptimizer, FlavorPairingAgent, TechniqueAdvisor, MenuDesigner

Generated: 2025-10-29T09:08:28.647328
"""

from .agents.manager import ChefManager
from .agents.recipeoptimizer import RecipeOptimizer
from .agents.flavorpairingagent import FlavorPairingAgent
from .agents.techniqueadvisor import TechniqueAdvisor
from .agents.menudesigner import MenuDesigner

__all__ = [
    'ChefManager',
    'RecipeOptimizer', 'FlavorPairingAgent', 'TechniqueAdvisor', 'MenuDesigner'
]

__version__ = '0.1.0'
