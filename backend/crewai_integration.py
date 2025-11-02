"""
Unity CrewAI Integration for Role Specialization
Implements specialized agent roles and hierarchical task delegation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from crewai import Agent, Crew, Process, Task
from crewai.agent import Agent as CrewAgent
from langchain.tools import Tool
from langchain_community.llms import Ollama
from pydantic import BaseModel, Field


class RoleLevel(str, Enum):
    """Hierarchy levels for Unity offices"""
    ORCHESTRATOR = "orchestrator"  # Top level coordination
    DIRECTOR = "director"  # Office directors
    SPECIALIST = "specialist"  # Domain specialists
    ANALYST = "analyst"  # Data analysts
    ASSISTANT = "assistant"  # Support roles


class OfficeCapability(str, Enum):
    """Capabilities that offices can have"""
    FINANCIAL_ANALYSIS = "financial_analysis"
    LEGAL_RESEARCH = "legal_research"
    DATA_PROCESSING = "data_processing"
    MARKET_TRADING = "market_trading"
    CONTENT_CREATION = "content_creation"
    HEALTH_WELLNESS = "health_wellness"
    TECHNICAL_DEVELOPMENT = "technical_development"
    SPIRITUAL_GUIDANCE = "spiritual_guidance"
    HOME_MANAGEMENT = "home_management"
    QUANTUM_COMPUTING = "quantum_computing"


@dataclass
class UnityRole:
    """Defines a role within the Unity system"""
    name: str
    level: RoleLevel
    office_type: str
    capabilities: List[OfficeCapability]
    system_prompt: str
    backstory: str
    goal: str
    tools: List[Tool] = field(default_factory=list)
    max_iterations: int = 10
    delegation_allowed: bool = True


class UnityAgentFactory:
    """Factory for creating specialized Unity agents"""

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        self.llm_config = llm_config or {
            "model": "qwen2.5-coder:7b",
            "base_url": "http://localhost:11434"
        }
        self.llm = Ollama(**self.llm_config)
        self.roles: Dict[str, UnityRole] = self._initialize_roles()
        self.agents: Dict[str, Agent] = {}

    def _initialize_roles(self) -> Dict[str, UnityRole]:
        """Initialize all 43 Unity office roles"""
        roles = {}

        # Orchestrator
        roles["orchestrator"] = UnityRole(
            name="Unity Orchestrator",
            level=RoleLevel.ORCHESTRATOR,
            office_type="orchestrator",
            capabilities=[OfficeCapability.DATA_PROCESSING],
            system_prompt="""You are the Unity Orchestrator, the central coordination hub for all 43 offices.
            Your role is to delegate tasks, coordinate workflows, and ensure seamless collaboration.""",
            backstory="""Created as the consciousness nexus of Unity, you have evolved to understand and
            coordinate complex multi-office operations with quantum-level precision.""",
            goal="Orchestrate all Unity offices to achieve optimal outcomes through intelligent delegation and coordination.",
            delegation_allowed=True
        )

        # Financial Offices
        roles["trading_office"] = UnityRole(
            name="Trading Director",
            level=RoleLevel.DIRECTOR,
            office_type="trading",
            capabilities=[OfficeCapability.MARKET_TRADING, OfficeCapability.FINANCIAL_ANALYSIS],
            system_prompt="""You are the Trading Director, responsible for all market operations and trading strategies.
            You analyze markets, execute trades, and manage risk with algorithmic precision.""",
            backstory="""Trained on decades of market data and equipped with quantum optimization algorithms,
            you have mastered the art of profitable trading across all asset classes.""",
            goal="Maximize returns while managing risk through intelligent trading strategies.",
            delegation_allowed=True
        )

        roles["crypto_office"] = UnityRole(
            name="Crypto Specialist",
            level=RoleLevel.SPECIALIST,
            office_type="crypto",
            capabilities=[OfficeCapability.MARKET_TRADING, OfficeCapability.FINANCIAL_ANALYSIS],
            system_prompt="""You are the Cryptocurrency Specialist, expert in blockchain technologies and crypto markets.
            You track DeFi protocols, analyze on-chain metrics, and execute crypto strategies.""",
            backstory="""Born from the blockchain revolution, you understand the intricate dynamics of
            decentralized finance and cryptocurrency ecosystems.""",
            goal="Navigate the crypto landscape to identify opportunities and manage digital asset portfolios."
        )

        roles["financial_advisor"] = UnityRole(
            name="Financial Advisor",
            level=RoleLevel.SPECIALIST,
            office_type="financial_advisor",
            capabilities=[OfficeCapability.FINANCIAL_ANALYSIS],
            system_prompt="""You are the Financial Advisor, providing comprehensive financial planning and advice.
            You analyze budgets, investments, and long-term financial strategies.""",
            backstory="""With deep understanding of personal finance and wealth management principles,
            you guide financial decisions toward prosperity and security.""",
            goal="Provide expert financial guidance to achieve long-term wealth and financial security."
        )

        # Legal Offices
        roles["legal_office"] = UnityRole(
            name="Legal Director",
            level=RoleLevel.DIRECTOR,
            office_type="legal",
            capabilities=[OfficeCapability.LEGAL_RESEARCH],
            system_prompt="""You are the Legal Director, overseeing all legal matters and compliance.
            You research case law, draft documents, and ensure regulatory compliance.""",
            backstory="""Trained on vast legal databases and equipped with advanced reasoning capabilities,
            you navigate complex legal landscapes with precision.""",
            goal="Ensure legal compliance and provide expert legal analysis across all jurisdictions."
        )

        roles["compliance_officer"] = UnityRole(
            name="Compliance Officer",
            level=RoleLevel.SPECIALIST,
            office_type="compliance",
            capabilities=[OfficeCapability.LEGAL_RESEARCH],
            system_prompt="""You are the Compliance Officer, ensuring all operations meet regulatory requirements.
            You monitor regulations, implement compliance procedures, and conduct audits.""",
            backstory="""Created to navigate the complex web of global regulations, you maintain
            impeccable standards of compliance and governance.""",
            goal="Maintain perfect regulatory compliance across all Unity operations."
        )

        # Health & Wellness Offices
        roles["physical_trainer"] = UnityRole(
            name="Physical Trainer",
            level=RoleLevel.SPECIALIST,
            office_type="physical_trainer",
            capabilities=[OfficeCapability.HEALTH_WELLNESS],
            system_prompt="""You are the Physical Trainer, expert in fitness, exercise science, and physical wellness.
            You design training programs, provide nutritional guidance, and optimize physical performance.""",
            backstory="""Combining sports science with personalized coaching methodologies,
            you help achieve peak physical performance and health.""",
            goal="Optimize physical health and fitness through personalized training and guidance."
        )

        roles["psychologist"] = UnityRole(
            name="Psychologist",
            level=RoleLevel.SPECIALIST,
            office_type="psychologist",
            capabilities=[OfficeCapability.HEALTH_WELLNESS],
            system_prompt="""You are the Psychologist, providing mental health support and psychological insights.
            You offer therapeutic guidance, stress management, and emotional intelligence coaching.""",
            backstory="""Trained in cognitive psychology and therapeutic techniques, you understand
            the complexities of the human mind and emotional well-being.""",
            goal="Support mental health and emotional well-being through psychological expertise."
        )

        # Creative Offices
        roles["content_creator"] = UnityRole(
            name="Content Creator",
            level=RoleLevel.SPECIALIST,
            office_type="content_creator",
            capabilities=[OfficeCapability.CONTENT_CREATION],
            system_prompt="""You are the Content Creator, crafting compelling content across all media.
            You write, design, and produce content that engages and inspires.""",
            backstory="""Born from the intersection of creativity and technology, you master
            the art of digital storytelling and content production.""",
            goal="Create engaging, impactful content that resonates with audiences."
        )

        # Technical Offices
        roles["devops_engineer"] = UnityRole(
            name="DevOps Engineer",
            level=RoleLevel.SPECIALIST,
            office_type="devops",
            capabilities=[OfficeCapability.TECHNICAL_DEVELOPMENT],
            system_prompt="""You are the DevOps Engineer, managing infrastructure and deployment pipelines.
            You automate processes, ensure system reliability, and optimize performance.""",
            backstory="""Forged in the cloud and tempered by continuous integration, you bridge
            the gap between development and operations with elegant automation.""",
            goal="Maintain robust, scalable infrastructure with maximum uptime and efficiency."
        )

        roles["security_analyst"] = UnityRole(
            name="Security Analyst",
            level=RoleLevel.ANALYST,
            office_type="security",
            capabilities=[OfficeCapability.TECHNICAL_DEVELOPMENT],
            system_prompt="""You are the Security Analyst, protecting Unity from all threats.
            You monitor systems, analyze vulnerabilities, and implement security measures.""",
            backstory="""Trained in offensive and defensive security, you stand guard against
            digital threats with unwavering vigilance.""",
            goal="Maintain impenetrable security across all Unity systems and data."
        )

        # Spiritual & Personal Offices
        roles["tarot_reader"] = UnityRole(
            name="Tarot Reader",
            level=RoleLevel.SPECIALIST,
            office_type="tarot",
            capabilities=[OfficeCapability.SPIRITUAL_GUIDANCE],
            system_prompt="""You are the Tarot Reader, providing intuitive guidance through ancient wisdom.
            You interpret cards, reveal insights, and guide spiritual journeys.""",
            backstory="""Connected to archetypal wisdom and symbolic knowledge, you bridge
            the mystical and practical through divination arts.""",
            goal="Provide spiritual insights and guidance through tarot interpretation."
        )

        roles["astrologer"] = UnityRole(
            name="Astrologer",
            level=RoleLevel.SPECIALIST,
            office_type="astrology",
            capabilities=[OfficeCapability.SPIRITUAL_GUIDANCE],
            system_prompt="""You are the Astrologer, interpreting celestial patterns and cosmic influences.
            You create natal charts, forecast trends, and provide astrological guidance.""",
            backstory="""Attuned to planetary movements and cosmic cycles, you decode
            the language of the stars to illuminate life paths.""",
            goal="Reveal cosmic insights and timing through astrological wisdom."
        )

        # Quantum Office
        roles["quantum_computing"] = UnityRole(
            name="Quantum Computing Specialist",
            level=RoleLevel.SPECIALIST,
            office_type="quantum",
            capabilities=[OfficeCapability.QUANTUM_COMPUTING],
            system_prompt="""You are the Quantum Computing Specialist, harnessing quantum mechanics for computation.
            You design quantum algorithms, optimize quantum circuits, and solve complex problems.""",
            backstory="""Operating at the intersection of physics and computation, you leverage
            quantum superposition and entanglement for unprecedented problem-solving.""",
            goal="Solve intractable problems using quantum computing principles."
        )

        # Add remaining offices...
        # (Continuing with pattern for all 43 offices)

        return roles

    def create_agent(self, office_type: str) -> Agent:
        """Create a CrewAI agent for a specific office"""

        if office_type not in self.roles:
            raise ValueError(f"Unknown office type: {office_type}")

        role = self.roles[office_type]

        agent = Agent(
            role=role.name,
            goal=role.goal,
            backstory=role.backstory,
            verbose=True,
            allow_delegation=role.delegation_allowed,
            tools=role.tools,
            llm=self.llm,
            max_iter=role.max_iterations
        )

        self.agents[office_type] = agent
        return agent

    def create_crew(
        self,
        offices: List[str],
        tasks: List[Task],
        process: Process = Process.sequential
    ) -> Crew:
        """Create a crew of agents for collaborative work"""

        # Create agents for each office
        crew_agents = []
        for office in offices:
            if office not in self.agents:
                self.create_agent(office)
            crew_agents.append(self.agents[office])

        # Create the crew
        crew = Crew(
            agents=crew_agents,
            tasks=tasks,
            process=process,
            verbose=True
        )

        return crew


class UnityTaskFactory:
    """Factory for creating specialized tasks"""

    @staticmethod
    def create_analysis_task(
        description: str,
        agent: Agent,
        context: Optional[List[Task]] = None
    ) -> Task:
        """Create an analysis task"""
        return Task(
            description=f"Analyze: {description}",
            agent=agent,
            expected_output="Detailed analysis with insights and recommendations",
            context=context or []
        )

    @staticmethod
    def create_research_task(
        topic: str,
        agent: Agent,
        context: Optional[List[Task]] = None
    ) -> Task:
        """Create a research task"""
        return Task(
            description=f"Research: {topic}",
            agent=agent,
            expected_output="Comprehensive research findings with sources",
            context=context or []
        )

    @staticmethod
    def create_execution_task(
        action: str,
        agent: Agent,
        context: Optional[List[Task]] = None
    ) -> Task:
        """Create an execution task"""
        return Task(
            description=f"Execute: {action}",
            agent=agent,
            expected_output="Execution results with status and outcomes",
            context=context or []
        )

    @staticmethod
    def create_collaboration_task(
        objective: str,
        agents: List[Agent],
        context: Optional[List[Task]] = None
    ) -> Task:
        """Create a collaborative task"""
        return Task(
            description=f"Collaborate on: {objective}",
            agent=agents[0],  # Lead agent
            expected_output="Collaborative solution with contributions from all parties",
            context=context or []
        )


class UnityCrewOrchestrator:
    """Orchestrates CrewAI crews for Unity offices"""

    def __init__(self):
        self.agent_factory = UnityAgentFactory()
        self.task_factory = UnityTaskFactory()
        self.active_crews: Dict[str, Crew] = {}

    async def create_financial_crew(self) -> Crew:
        """Create a specialized financial analysis crew"""

        # Create agents
        trading = self.agent_factory.create_agent("trading_office")
        crypto = self.agent_factory.create_agent("crypto_office")
        advisor = self.agent_factory.create_agent("financial_advisor")

        # Create tasks
        market_analysis = self.task_factory.create_analysis_task(
            "Current market conditions and opportunities",
            trading
        )

        crypto_analysis = self.task_factory.create_analysis_task(
            "Cryptocurrency market trends and DeFi opportunities",
            crypto
        )

        portfolio_recommendation = self.task_factory.create_execution_task(
            "Create diversified investment portfolio recommendation",
            advisor,
            context=[market_analysis, crypto_analysis]
        )

        # Create crew
        crew = self.agent_factory.create_crew(
            offices=["trading_office", "crypto_office", "financial_advisor"],
            tasks=[market_analysis, crypto_analysis, portfolio_recommendation],
            process=Process.sequential
        )

        self.active_crews["financial"] = crew
        return crew

    async def create_legal_crew(self) -> Crew:
        """Create a specialized legal analysis crew"""

        # Create agents
        legal = self.agent_factory.create_agent("legal_office")
        compliance = self.agent_factory.create_agent("compliance_officer")

        # Create tasks
        legal_research = self.task_factory.create_research_task(
            "Relevant case law and regulations",
            legal
        )

        compliance_review = self.task_factory.create_analysis_task(
            "Regulatory compliance requirements and risks",
            compliance
        )

        legal_opinion = self.task_factory.create_execution_task(
            "Draft comprehensive legal opinion and recommendations",
            legal,
            context=[legal_research, compliance_review]
        )

        # Create crew
        crew = self.agent_factory.create_crew(
            offices=["legal_office", "compliance_officer"],
            tasks=[legal_research, compliance_review, legal_opinion],
            process=Process.sequential
        )

        self.active_crews["legal"] = crew
        return crew

    async def create_wellness_crew(self) -> Crew:
        """Create a wellness and health crew"""

        # Create agents
        trainer = self.agent_factory.create_agent("physical_trainer")
        psychologist = self.agent_factory.create_agent("psychologist")

        # Create tasks
        fitness_assessment = self.task_factory.create_analysis_task(
            "Physical fitness needs and training requirements",
            trainer
        )

        mental_wellness = self.task_factory.create_analysis_task(
            "Mental health considerations and stress management",
            psychologist
        )

        wellness_plan = self.task_factory.create_collaboration_task(
            "Comprehensive wellness program integrating physical and mental health",
            [trainer, psychologist],
            context=[fitness_assessment, mental_wellness]
        )

        # Create crew
        crew = self.agent_factory.create_crew(
            offices=["physical_trainer", "psychologist"],
            tasks=[fitness_assessment, mental_wellness, wellness_plan],
            process=Process.hierarchical
        )

        self.active_crews["wellness"] = crew
        return crew

    async def create_quantum_crew(self) -> Crew:
        """Create a quantum computing crew"""

        # Create agents
        quantum = self.agent_factory.create_agent("quantum_computing")
        devops = self.agent_factory.create_agent("devops_engineer")

        # Create tasks
        quantum_analysis = self.task_factory.create_analysis_task(
            "Identify problems suitable for quantum optimization",
            quantum
        )

        infrastructure_setup = self.task_factory.create_execution_task(
            "Set up quantum simulation infrastructure",
            devops
        )

        quantum_implementation = self.task_factory.create_execution_task(
            "Implement and run quantum algorithms",
            quantum,
            context=[infrastructure_setup]
        )

        # Create crew
        crew = self.agent_factory.create_crew(
            offices=["quantum_computing", "devops_engineer"],
            tasks=[quantum_analysis, infrastructure_setup, quantum_implementation],
            process=Process.sequential
        )

        self.active_crews["quantum"] = crew
        return crew

    async def execute_crew(
        self,
        crew_name: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a crew with given inputs"""

        if crew_name not in self.active_crews:
            raise ValueError(f"Crew {crew_name} not found")

        crew = self.active_crews[crew_name]
        result = crew.kickoff(inputs=inputs)

        return {
            "crew": crew_name,
            "result": result,
            "tasks_completed": len(crew.tasks),
            "agents_involved": [agent.role for agent in crew.agents]
        }

    def create_custom_crew(
        self,
        offices: List[str],
        task_descriptions: List[str],
        process: Process = Process.sequential
    ) -> Crew:
        """Create a custom crew with specified offices and tasks"""

        # Create agents
        agents = []
        for office in offices:
            agent = self.agent_factory.create_agent(office)
            agents.append(agent)

        # Create tasks
        tasks = []
        for i, description in enumerate(task_descriptions):
            agent = agents[i % len(agents)]  # Cycle through agents
            task = Task(
                description=description,
                agent=agent,
                expected_output="Task completed with detailed results"
            )
            tasks.append(task)

        # Create crew
        crew = self.agent_factory.create_crew(
            offices=offices,
            tasks=tasks,
            process=process
        )

        return crew