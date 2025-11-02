"""
Unity Office Templates and Registration System
Provides reusable templates for all 43 Unity offices with specialized capabilities
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from memory_graph import SharedMemoryGraph, MemoryGraphConfig, ConsentLevel
from message_protocol import MessageRouter, OfficeMessageHandler, MessageType
from langgraph_integration import UnityStateManager
from crewai_integration import UnityAgentFactory, UnityRole


class OfficeStatus(str, Enum):
    """Office operational status"""
    INITIALIZING = "initializing"
    ONLINE = "online"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class OfficeCategory(str, Enum):
    """Categories of Unity offices"""
    CORE = "core"  # Orchestrator, Memory, Security
    FINANCIAL = "financial"  # Trading, Crypto, Banking, etc.
    LEGAL = "legal"  # Legal, Compliance, Contracts, IP
    LIFESTYLE = "lifestyle"  # Travel, Restaurant, Events, Shopping
    HEALTH = "health"  # Physical, Nutrition, Sleep, Psychology, Medical
    CREATIVE = "creative"  # Content, Video, Graphics, Music
    TECHNICAL = "technical"  # DevOps, Data, Security, Cloud
    EDUCATION = "education"  # Research, Education, Language, Skills
    SPIRITUAL = "spiritual"  # Tarot, Astrology, Meditation, Life Coach
    HOME = "home"  # Kitchen, Home Automation, Maintenance
    SPECIAL = "special"  # Quantum, Emergency


@dataclass
class OfficeCapabilities:
    """Capabilities and features of an office"""
    can_delegate: bool = True
    can_access_memory: bool = True
    can_collaborate: bool = True
    can_execute_code: bool = False
    can_access_external_apis: bool = False
    can_handle_sensitive_data: bool = False
    requires_authentication: bool = False
    max_concurrent_tasks: int = 10
    supported_message_types: Set[MessageType] = field(default_factory=set)
    specialized_tools: List[str] = field(default_factory=list)


class OfficeTemplate(ABC):
    """Base template for all Unity offices"""

    def __init__(
        self,
        office_id: str,
        office_type: str,
        category: OfficeCategory,
        capabilities: OfficeCapabilities
    ):
        self.office_id = office_id
        self.office_type = office_type
        self.category = category
        self.capabilities = capabilities
        self.status = OfficeStatus.INITIALIZING

        # Core components
        self.memory_graph: Optional[SharedMemoryGraph] = None
        self.message_handler: Optional[OfficeMessageHandler] = None
        self.state_manager: Optional[UnityStateManager] = None
        self.agent_factory: Optional[UnityAgentFactory] = None

        # Office state
        self.active_tasks: Dict[str, Any] = {}
        self.connected_offices: Set[str] = set()
        self.metrics: Dict[str, Any] = {}

    async def initialize(self, config: Dict[str, Any]):
        """Initialize the office with all components"""

        # Initialize memory graph
        memory_config = MemoryGraphConfig(**config.get("memory", {}))
        self.memory_graph = SharedMemoryGraph(memory_config)
        await self.memory_graph.initialize()

        # Initialize message handler
        router = config.get("message_router")
        if router:
            self.message_handler = OfficeMessageHandler(
                self.office_id,
                self.office_type,
                router
            )
            await self.message_handler.initialize()

        # Initialize state manager
        self.state_manager = UnityStateManager()
        self.state_manager.create_office_graph(self.office_id, self.office_type)

        # Initialize agent factory
        self.agent_factory = UnityAgentFactory(config.get("llm", {}))

        # Office-specific initialization
        await self._initialize_office()

        self.status = OfficeStatus.ONLINE
        print(f"✅ Office {self.office_id} ({self.office_type}) initialized")

    @abstractmethod
    async def _initialize_office(self):
        """Office-specific initialization - override in subclass"""
        pass

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - must be implemented by each office"""
        pass

    async def shutdown(self):
        """Gracefully shutdown the office"""
        self.status = OfficeStatus.OFFLINE

        # Close memory graph
        if self.memory_graph:
            await self.memory_graph.close()

        # Additional cleanup
        await self._cleanup_office()

    async def _cleanup_office(self):
        """Office-specific cleanup - override if needed"""
        pass


# CORE OFFICE TEMPLATES

class OrchestratorOffice(OfficeTemplate):
    """Template for the Orchestrator office"""

    def __init__(self, office_id: str = "orchestrator_main"):
        super().__init__(
            office_id=office_id,
            office_type="orchestrator",
            category=OfficeCategory.CORE,
            capabilities=OfficeCapabilities(
                can_delegate=True,
                can_access_memory=True,
                can_collaborate=True,
                can_execute_code=False,
                max_concurrent_tasks=100,
                supported_message_types={
                    MessageType.REQUEST,
                    MessageType.WORKFLOW,
                    MessageType.BROADCAST
                }
            )
        )
        self.workflow_queue: List[Dict[str, Any]] = []
        self.office_registry: Dict[str, Dict[str, Any]] = {}

    async def _initialize_office(self):
        """Initialize orchestrator-specific components"""
        # Set up workflow management
        self.state_manager.create_workflow_graph()

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process orchestration tasks"""
        task_type = task.get("type")

        if task_type == "delegate":
            return await self._delegate_task(task)
        elif task_type == "workflow":
            return await self._execute_workflow(task)
        elif task_type == "coordinate":
            return await self._coordinate_offices(task)
        else:
            return {"error": "Unknown task type"}

    async def _delegate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to appropriate office"""
        target_office = task.get("target_office")
        if not target_office:
            # Determine best office for task
            target_office = await self._select_office_for_task(task)

        # Send task to office
        if self.message_handler:
            response = await self.message_handler.router.send_request(
                self.office_id,
                target_office,
                "process_task",
                task
            )
            return {"delegated_to": target_office, "response": response}

        return {"error": "Message handler not initialized"}

    async def _execute_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multi-office workflow"""
        workflow_id = task.get("workflow_id")
        offices = task.get("offices", [])

        result = await self.state_manager.run_workflow(
            workflow_id,
            offices,
            task.get("description", ""),
            task.get("context", {})
        )

        return {"workflow_id": workflow_id, "result": result}

    async def _coordinate_offices(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple offices"""
        offices = task.get("offices", [])
        coordination_type = task.get("coordination_type")

        # Broadcast coordination request
        if self.message_handler:
            await self.message_handler.router.broadcast_notification(
                self.office_id,
                "coordination_request",
                {"type": coordination_type, "offices": offices}
            )

        return {"coordinated_offices": offices}

    async def _select_office_for_task(self, task: Dict[str, Any]) -> str:
        """Select best office for a given task"""
        # Simple heuristic - can be enhanced with ML
        task_keywords = str(task).lower()

        if "trade" in task_keywords or "market" in task_keywords:
            return "trading_office"
        elif "legal" in task_keywords or "law" in task_keywords:
            return "legal_office"
        elif "health" in task_keywords or "medical" in task_keywords:
            return "medical_advisor"
        else:
            return "general_office"


# FINANCIAL OFFICE TEMPLATES

class TradingOffice(OfficeTemplate):
    """Template for Trading office"""

    def __init__(self, office_id: str = "trading_001"):
        super().__init__(
            office_id=office_id,
            office_type="trading",
            category=OfficeCategory.FINANCIAL,
            capabilities=OfficeCapabilities(
                can_access_external_apis=True,
                can_handle_sensitive_data=True,
                requires_authentication=True,
                specialized_tools=["quantconnect", "alpaca", "binance"]
            )
        )
        self.active_positions: Dict[str, Any] = {}
        self.market_data: Dict[str, Any] = {}
        self.strategies: List[str] = []

    async def _initialize_office(self):
        """Initialize trading-specific components"""
        # Load trading strategies
        self.strategies = ["momentum", "mean_reversion", "arbitrage"]

        # Connect to market data feeds (mock)
        self.market_data = {
            "SPY": {"price": 450.0, "volume": 1000000},
            "BTC": {"price": 50000.0, "volume": 10000}
        }

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process trading tasks"""
        task_type = task.get("type")

        if task_type == "analyze_market":
            return await self._analyze_market(task)
        elif task_type == "execute_trade":
            return await self._execute_trade(task)
        elif task_type == "backtest_strategy":
            return await self._backtest_strategy(task)
        else:
            return {"error": "Unknown trading task"}

    async def _analyze_market(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions"""
        symbol = task.get("symbol", "SPY")
        analysis = {
            "symbol": symbol,
            "current_price": self.market_data.get(symbol, {}).get("price"),
            "trend": "bullish",
            "volatility": "moderate",
            "recommendation": "buy"
        }
        return analysis

    async def _execute_trade(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade"""
        trade = {
            "symbol": task.get("symbol"),
            "action": task.get("action"),
            "quantity": task.get("quantity"),
            "price": self.market_data.get(task.get("symbol"), {}).get("price"),
            "status": "executed"
        }

        # Update positions
        self.active_positions[trade["symbol"]] = trade

        return trade

    async def _backtest_strategy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Backtest a trading strategy"""
        strategy = task.get("strategy", "momentum")
        return {
            "strategy": strategy,
            "returns": 0.15,
            "sharpe_ratio": 1.5,
            "max_drawdown": -0.10
        }


# LEGAL OFFICE TEMPLATES

class LegalOffice(OfficeTemplate):
    """Template for Legal office"""

    def __init__(self, office_id: str = "legal_001"):
        super().__init__(
            office_id=office_id,
            office_type="legal",
            category=OfficeCategory.LEGAL,
            capabilities=OfficeCapabilities(
                can_access_external_apis=True,
                can_handle_sensitive_data=True,
                specialized_tools=["pacer", "courtlistener", "lexisnexis"]
            )
        )
        self.case_database: Dict[str, Any] = {}
        self.regulations: Dict[str, Any] = {}

    async def _initialize_office(self):
        """Initialize legal-specific components"""
        # Load legal databases (mock)
        self.regulations = {
            "GDPR": "General Data Protection Regulation",
            "SOX": "Sarbanes-Oxley Act",
            "HIPAA": "Health Insurance Portability and Accountability Act"
        }

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process legal tasks"""
        task_type = task.get("type")

        if task_type == "legal_research":
            return await self._legal_research(task)
        elif task_type == "contract_review":
            return await self._contract_review(task)
        elif task_type == "compliance_check":
            return await self._compliance_check(task)
        else:
            return {"error": "Unknown legal task"}

    async def _legal_research(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct legal research"""
        topic = task.get("topic")
        return {
            "topic": topic,
            "relevant_cases": ["Case A v. B", "Case C v. D"],
            "statutes": ["Section 101", "Section 202"],
            "analysis": "Legal analysis summary"
        }

    async def _contract_review(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review a contract"""
        return {
            "contract_id": task.get("contract_id"),
            "issues_found": ["Clause 3.1 needs clarification"],
            "risk_level": "medium",
            "recommendations": ["Add termination clause"]
        }

    async def _compliance_check(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance"""
        regulations = task.get("regulations", ["GDPR"])
        return {
            "regulations_checked": regulations,
            "compliance_status": "partial",
            "actions_required": ["Update privacy policy"]
        }


# HEALTH OFFICE TEMPLATES

class PhysicalTrainerOffice(OfficeTemplate):
    """Template for Physical Trainer office"""

    def __init__(self, office_id: str = "trainer_001"):
        super().__init__(
            office_id=office_id,
            office_type="physical_trainer",
            category=OfficeCategory.HEALTH,
            capabilities=OfficeCapabilities(
                specialized_tools=["fitness_tracker", "nutrition_calculator"]
            )
        )
        self.training_programs: Dict[str, Any] = {}
        self.client_progress: Dict[str, Any] = {}

    async def _initialize_office(self):
        """Initialize trainer-specific components"""
        self.training_programs = {
            "strength": "5x5 Stronglifts",
            "cardio": "HIIT Program",
            "flexibility": "Yoga Flow"
        }

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process training tasks"""
        task_type = task.get("type")

        if task_type == "create_workout":
            return await self._create_workout(task)
        elif task_type == "track_progress":
            return await self._track_progress(task)
        elif task_type == "nutrition_plan":
            return await self._nutrition_plan(task)
        else:
            return {"error": "Unknown training task"}

    async def _create_workout(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workout plan"""
        goal = task.get("goal", "general_fitness")
        return {
            "workout_plan": {
                "monday": "Upper body strength",
                "wednesday": "Cardio HIIT",
                "friday": "Lower body strength"
            },
            "duration": "4 weeks",
            "intensity": "moderate"
        }

    async def _track_progress(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Track fitness progress"""
        client_id = task.get("client_id")
        return {
            "client_id": client_id,
            "weight_change": -2.5,
            "strength_gain": 10,
            "endurance_improvement": 15
        }

    async def _nutrition_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create nutrition plan"""
        calories = task.get("daily_calories", 2000)
        return {
            "daily_calories": calories,
            "macros": {
                "protein": calories * 0.3 / 4,
                "carbs": calories * 0.4 / 4,
                "fats": calories * 0.3 / 9
            },
            "meal_timing": ["8am", "12pm", "3pm", "6pm", "8pm"]
        }


# SPIRITUAL OFFICE TEMPLATES

class TarotReaderOffice(OfficeTemplate):
    """Template for Tarot Reader office"""

    def __init__(self, office_id: str = "tarot_001"):
        super().__init__(
            office_id=office_id,
            office_type="tarot_reader",
            category=OfficeCategory.SPIRITUAL,
            capabilities=OfficeCapabilities(
                specialized_tools=["tarot_deck", "spread_interpreter"]
            )
        )
        self.tarot_deck: List[str] = []
        self.spreads: Dict[str, Any] = {}

    async def _initialize_office(self):
        """Initialize tarot-specific components"""
        # Initialize tarot deck
        self.tarot_deck = [
            "The Fool", "The Magician", "The High Priestess",
            "The Empress", "The Emperor", "The Hierophant",
            "The Lovers", "The Chariot", "Strength",
            "The Hermit", "Wheel of Fortune", "Justice"
            # ... (full 78 card deck)
        ]

        self.spreads = {
            "three_card": ["Past", "Present", "Future"],
            "celtic_cross": ["Situation", "Challenge", "Past", "Future",
                           "Above", "Below", "Advice", "Influences",
                           "Hopes", "Outcome"]
        }

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process tarot reading tasks"""
        task_type = task.get("type")

        if task_type == "reading":
            return await self._perform_reading(task)
        elif task_type == "interpret_card":
            return await self._interpret_card(task)
        else:
            return {"error": "Unknown tarot task"}

    async def _perform_reading(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a tarot reading"""
        spread_type = task.get("spread", "three_card")
        question = task.get("question", "General guidance")

        import random
        cards = random.sample(self.tarot_deck, len(self.spreads[spread_type]))

        reading = {
            "question": question,
            "spread": spread_type,
            "cards": {}
        }

        for position, card in zip(self.spreads[spread_type], cards):
            reading["cards"][position] = {
                "card": card,
                "interpretation": f"The {card} in {position} suggests..."
            }

        return reading

    async def _interpret_card(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret a specific card"""
        card = task.get("card", "The Fool")
        return {
            "card": card,
            "upright_meaning": "New beginnings, innocence, spontaneity",
            "reversed_meaning": "Recklessness, risk-taking, foolishness",
            "advice": "Embrace new opportunities with open mind"
        }


# QUANTUM OFFICE TEMPLATE

class QuantumOffice(OfficeTemplate):
    """Template for Quantum Computing office"""

    def __init__(self, office_id: str = "quantum_001"):
        super().__init__(
            office_id=office_id,
            office_type="quantum_computing",
            category=OfficeCategory.SPECIAL,
            capabilities=OfficeCapabilities(
                can_execute_code=True,
                specialized_tools=["qiskit", "cirq", "quantum_simulator"]
            )
        )
        self.quantum_circuits: Dict[str, Any] = {}
        self.optimization_problems: Dict[str, Any] = {}

    async def _initialize_office(self):
        """Initialize quantum-specific components"""
        self.optimization_problems = {
            "portfolio": "Portfolio optimization using QAOA",
            "routing": "Vehicle routing using VQE",
            "scheduling": "Job scheduling using quantum annealing"
        }

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process quantum computing tasks"""
        task_type = task.get("type")

        if task_type == "optimize":
            return await self._quantum_optimize(task)
        elif task_type == "simulate":
            return await self._quantum_simulate(task)
        else:
            return {"error": "Unknown quantum task"}

    async def _quantum_optimize(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run quantum optimization"""
        problem_type = task.get("problem", "portfolio")
        return {
            "problem": problem_type,
            "optimal_solution": [0.3, 0.4, 0.3],  # Mock result
            "quantum_advantage": 1.5,
            "qubits_used": 8
        }

    async def _quantum_simulate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate quantum circuit"""
        circuit_depth = task.get("depth", 10)
        return {
            "circuit_depth": circuit_depth,
            "measurement_results": {"00": 512, "11": 512},
            "entanglement_entropy": 0.693
        }


# OFFICE REGISTRY AND FACTORY

class OfficeRegistry:
    """Central registry for all Unity offices"""

    def __init__(self):
        self.templates: Dict[str, type] = {
            # Core
            "orchestrator": OrchestratorOffice,

            # Financial
            "trading": TradingOffice,

            # Legal
            "legal": LegalOffice,

            # Health
            "physical_trainer": PhysicalTrainerOffice,

            # Spiritual
            "tarot_reader": TarotReaderOffice,

            # Quantum
            "quantum_computing": QuantumOffice,

            # Add all 43 office templates here...
        }

        self.active_offices: Dict[str, OfficeTemplate] = {}

    async def create_office(
        self,
        office_type: str,
        office_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> OfficeTemplate:
        """Create and register a new office"""

        if office_type not in self.templates:
            raise ValueError(f"Unknown office type: {office_type}")

        # Get template class
        template_class = self.templates[office_type]

        # Create office instance
        if office_id:
            office = template_class(office_id)
        else:
            office = template_class()

        # Initialize office
        await office.initialize(config or {})

        # Register office
        self.active_offices[office.office_id] = office

        return office

    async def get_office(self, office_id: str) -> Optional[OfficeTemplate]:
        """Get an active office by ID"""
        return self.active_offices.get(office_id)

    async def list_offices(self) -> List[Dict[str, Any]]:
        """List all active offices"""
        return [
            {
                "id": office.office_id,
                "type": office.office_type,
                "category": office.category.value,
                "status": office.status.value
            }
            for office in self.active_offices.values()
        ]

    async def shutdown_office(self, office_id: str):
        """Shutdown and unregister an office"""
        if office_id in self.active_offices:
            office = self.active_offices[office_id]
            await office.shutdown()
            del self.active_offices[office_id]

    async def shutdown_all(self):
        """Shutdown all offices"""
        for office_id in list(self.active_offices.keys()):
            await self.shutdown_office(office_id)