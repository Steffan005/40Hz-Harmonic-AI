#!/usr/bin/env python3
"""
CitySpawner - Automated Office Generation Framework

Given a domain name and configuration, this module scaffolds a complete office:
- Manager Agent + 3-4 specialist sub-agents
- Domain-specific tools
- Memory graph integration
- Evolution loop hooks
- UI window template

Usage:
    spawner = CitySpawner()
    office = spawner.spawn_office(
        domain="Astrologist",
        specialists=["StarDataFetcher", "HoroscopeInterpreter", "NatalChartAnalyzer"],
        tools=["ephemeris_api", "chart_generator"],
        metrics=["accuracy", "narrative_quality"]
    )
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AgentSpec:
    """Specification for a single agent."""
    name: str
    role: str  # "manager" | "specialist"
    description: str
    model: str  # "deepseek-r1:14b" | "qwen2.5-coder:7b"
    tools: List[str]
    prompts: Dict[str, str]


@dataclass
class OfficeSpec:
    """Complete specification for a domain office."""
    domain: str
    manager: AgentSpec
    specialists: List[AgentSpec]
    tools: List[Dict[str, str]]  # [{name, description, implementation}]
    metrics: List[str]
    memory_tags: List[str]
    ui_config: Dict[str, any]
    created_at: str


class CitySpawner:
    """
    Automated office generation framework.

    The CitySpawner is Unity's mitosis mechanism - it creates new neural lobes
    (offices) by cloning a template and customizing it for specific domains.
    """

    def __init__(self, offices_dir: Path = None):
        self.offices_dir = offices_dir or Path("offices")
        self.offices_dir.mkdir(exist_ok=True)

        # Template prompts
        self.manager_prompt_template = """You are the {domain} Manager, overseeing {num_specialists} specialist agents.

Your responsibilities:
1. Decompose user requests into subtasks for specialists
2. Coordinate specialist outputs into coherent responses
3. Maintain domain knowledge in the shared memory graph
4. Optimize workflows through the evolution loop

Specialists under your supervision:
{specialist_list}

Always prioritize accuracy, coherence, and user value."""

        self.specialist_prompt_template = """You are a {role} specialist in the {domain} office.

Your primary function:
{description}

Tools available:
{tools_list}

You report to the {domain} Manager. Focus on your specialty and deliver precise, high-quality results."""

    def spawn_office(
        self,
        domain: str,
        specialists: List[Dict[str, str]],
        tools: List[Dict[str, str]],
        metrics: List[str],
        description: str = "",
        model_preferences: Optional[Dict[str, str]] = None
    ) -> OfficeSpec:
        """
        Spawn a complete office for the given domain.

        Args:
            domain: Office name (e.g., "Astrologist", "Banker")
            specialists: List of specialist configs
                [{name, description, model, tools}, ...]
            tools: List of tool configs
                [{name, description, implementation}, ...]
            metrics: Evaluation metrics for this domain
                ["accuracy", "narrative_quality", "user_satisfaction"]
            description: Office overview
            model_preferences: Override default model selection

        Returns:
            OfficeSpec with complete configuration
        """
        print(f"\n{'='*70}")
        print(f"CITYSPAWNER: Generating {domain} Office")
        print(f"{'='*70}")

        # Default model selection
        default_models = {
            "manager": "deepseek-r1:14b",  # Reasoning for coordination
            "specialist": "deepseek-r1:14b"  # Can override per specialist
        }

        if model_preferences:
            default_models.update(model_preferences)

        # Create manager agent
        specialist_names = [s['name'] for s in specialists]
        manager = AgentSpec(
            name=f"{domain}Manager",
            role="manager",
            description=f"Oversees and coordinates all {domain} operations",
            model=default_models["manager"],
            tools=[t['name'] for t in tools],
            prompts={
                "system": self.manager_prompt_template.format(
                    domain=domain,
                    num_specialists=len(specialists),
                    specialist_list="\n".join(f"- {s['name']}: {s['description']}" for s in specialists)
                )
            }
        )

        # Create specialist agents
        specialist_agents = []
        for spec in specialists:
            agent = AgentSpec(
                name=spec['name'],
                role="specialist",
                description=spec['description'],
                model=spec.get('model', default_models['specialist']),
                tools=spec.get('tools', []),
                prompts={
                    "system": self.specialist_prompt_template.format(
                        role=spec['name'],
                        domain=domain,
                        description=spec['description'],
                        tools_list="\n".join(f"- {t}" for t in spec.get('tools', []))
                    )
                }
            )
            specialist_agents.append(agent)

        # UI configuration
        ui_config = {
            "window_title": f"Unity — {domain} Office",
            "icon": self._get_office_icon(domain),
            "width": 900,
            "height": 600,
            "theme": {
                "primary_color": self._get_office_color(domain),
                "fractal_pattern": "mandelbrot"
            }
        }

        # Memory tags for this office
        memory_tags = [
            domain.lower(),
            "office",
            *[m.lower() for m in metrics]
        ]

        # Create office spec
        office_spec = OfficeSpec(
            domain=domain,
            manager=manager,
            specialists=specialist_agents,
            tools=tools,
            metrics=metrics,
            memory_tags=memory_tags,
            ui_config=ui_config,
            created_at=datetime.utcnow().isoformat()
        )

        # Generate office directory structure
        self._scaffold_office_directory(office_spec)

        # Generate Python modules
        self._generate_office_modules(office_spec)

        # Generate configuration files
        self._generate_office_config(office_spec)

        print(f"\n✅ {domain} Office spawned successfully!")
        print(f"   Location: {self.offices_dir / domain.lower()}")
        print(f"   Manager: {manager.name}")
        print(f"   Specialists: {len(specialist_agents)}")
        print(f"   Tools: {len(tools)}")
        print(f"   Metrics: {', '.join(metrics)}")

        return office_spec

    def _scaffold_office_directory(self, spec: OfficeSpec):
        """Create directory structure for the office."""
        office_dir = self.offices_dir / spec.domain.lower()
        office_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (office_dir / "agents").mkdir(exist_ok=True)
        (office_dir / "tools").mkdir(exist_ok=True)
        (office_dir / "config").mkdir(exist_ok=True)
        (office_dir / "data").mkdir(exist_ok=True)

    def _generate_office_modules(self, spec: OfficeSpec):
        """Generate Python module files for the office."""
        office_dir = self.offices_dir / spec.domain.lower()

        # __init__.py
        init_content = f'''"""
{spec.domain} Office - Unity Quantum City

Domain: {spec.domain}
Manager: {spec.manager.name}
Specialists: {", ".join(s.name for s in spec.specialists)}

Generated: {spec.created_at}
"""

from .agents.manager import {spec.manager.name}
{chr(10).join(f"from .agents.{s.name.lower()} import {s.name}" for s in spec.specialists)}

__all__ = [
    '{spec.manager.name}',
    {", ".join(f"'{s.name}'" for s in spec.specialists)}
]

__version__ = '0.1.0'
'''
        (office_dir / "__init__.py").write_text(init_content)

        # Manager agent
        manager_content = f'''#!/usr/bin/env python3
"""
{spec.manager.name} - Coordination and oversight for {spec.domain} Office
"""

from typing import Dict, List, Any


class {spec.manager.name}:
    """
    Manager agent for {spec.domain} office.

    Coordinates {len(spec.specialists)} specialist agents:
    {chr(10).join(f"    - {s.name}: {s.description}" for s in spec.specialists)}
    """

    def __init__(self):
        self.domain = "{spec.domain}"
        self.model = "{spec.manager.model}"
        self.specialists = {[s.name for s in spec.specialists]}
        self.tools = {spec.manager.tools}

        # System prompt
        self.system_prompt = """{spec.manager.prompts['system']}"""

    def decompose_task(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Decompose user request into specialist subtasks.

        Args:
            user_request: User's query or request

        Returns:
            List of subtasks for specialists
        """
        # Stub: In production, would use LLM to decompose
        return [
            {{"specialist": s, "task": f"Process {{user_request}} via {{s}}"}}
            for s in self.specialists
        ]

    def synthesize_results(self, specialist_outputs: List[Dict]) -> str:
        """
        Synthesize specialist outputs into coherent response.

        Args:
            specialist_outputs: Results from each specialist

        Returns:
            Unified response
        """
        # Stub: In production, would use LLM to synthesize
        return "\\n\\n".join(
            f"{{o['specialist']}}: {{o['result']}}"
            for o in specialist_outputs
        )

    def execute(self, user_request: str) -> Dict[str, Any]:
        """
        Execute complete workflow: decompose → delegate → synthesize.

        Args:
            user_request: User's request

        Returns:
            Final result with metadata
        """
        subtasks = self.decompose_task(user_request)

        # Simulate specialist execution (would call actual agents in production)
        specialist_outputs = [
            {{"specialist": st["specialist"], "result": f"[Stub] {{st['task']}}"}}
            for st in subtasks
        ]

        final_result = self.synthesize_results(specialist_outputs)

        return {{
            "domain": self.domain,
            "request": user_request,
            "subtasks": subtasks,
            "result": final_result,
            "metadata": {{
                "model": self.model,
                "specialists_used": self.specialists
            }}
        }}


# Example usage
if __name__ == "__main__":
    manager = {spec.manager.name}()
    result = manager.execute("Sample request for {spec.domain}")
    print(result)
'''
        (office_dir / "agents" / "manager.py").write_text(manager_content)

        # Specialist agents (stub for each)
        for specialist in spec.specialists:
            specialist_content = f'''#!/usr/bin/env python3
"""
{specialist.name} - Specialist agent for {spec.domain} Office
"""

from typing import Dict, Any


class {specialist.name}:
    """
    {specialist.description}

    Model: {specialist.model}
    Tools: {specialist.tools}
    """

    def __init__(self):
        self.name = "{specialist.name}"
        self.model = "{specialist.model}"
        self.tools = {specialist.tools}
        self.system_prompt = """{specialist.prompts['system']}"""

    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute specialist task.

        Args:
            task: Task description
            context: Optional context from other agents

        Returns:
            Task result
        """
        # Stub: In production, would call LLM with system_prompt + task
        return {{
            "specialist": self.name,
            "task": task,
            "result": f"[Stub] {{self.name}} processed: {{task}}",
            "model": self.model,
            "tools_used": self.tools
        }}


# Example usage
if __name__ == "__main__":
    agent = {specialist.name}()
    result = agent.execute("Sample task")
    print(result)
'''
            (office_dir / "agents" / f"{specialist.name.lower()}.py").write_text(specialist_content)

    def _generate_office_config(self, spec: OfficeSpec):
        """Generate configuration YAML for the office."""
        office_dir = self.offices_dir / spec.domain.lower()

        config = {
            "domain": spec.domain,
            "manager": asdict(spec.manager),
            "specialists": [asdict(s) for s in spec.specialists],
            "tools": spec.tools,
            "metrics": spec.metrics,
            "memory_tags": spec.memory_tags,
            "ui_config": spec.ui_config,
            "evolution": {
                "enabled": True,
                "max_generations": 100,
                "bandit_arms": ["textgrad", "aflow_stub", "mipro_stub", "random_jitter"],
                "validation_set_size": 10
            },
            "created_at": spec.created_at
        }

        (office_dir / "config" / "office.yaml").write_text(
            yaml.dump(config, default_flow_style=False)
        )

    def _get_office_icon(self, domain: str) -> str:
        """Get emoji icon for office based on domain."""
        icons = {
            "Astrologist": "⭐",
            "Tarot": "🔮",
            "Numerologist": "🔢",
            "Banker": "🏦",
            "Philosopher": "🤔",
            "Chef": "👨‍🍳",
            "Musician": "🎵",
            "Artist": "🎨",
            "Scientist": "🔬",
            "Historian": "📜",
            "Psychologist": "🧠",
            "Architect": "🏛️",
            "Botanist": "🌱",
            "Therapist": "💆",
            "Environmentalist": "🌍",
            "Game Designer": "🎮"
        }
        return icons.get(domain, "🏢")

    def _get_office_color(self, domain: str) -> str:
        """Get primary color for office UI based on domain."""
        colors = {
            "Astrologist": "#FFD700",  # Gold
            "Tarot": "#9370DB",  # Medium purple
            "Numerologist": "#4169E1",  # Royal blue
            "Banker": "#2E8B57",  # Sea green
            "Philosopher": "#8B4513",  # Saddle brown
            "Chef": "#FF6347",  # Tomato
            "Musician": "#FF1493",  # Deep pink
            "Artist": "#FF4500",  # Orange red
            "Scientist": "#00CED1",  # Dark turquoise
            "Historian": "#CD853F",  # Peru
            "Psychologist": "#6A5ACD",  # Slate blue
            "Architect": "#708090",  # Slate gray
            "Botanist": "#32CD32",  # Lime green
            "Therapist": "#87CEEB",  # Sky blue
            "Environmentalist": "#228B22",  # Forest green
            "Game Designer": "#FF00FF"  # Magenta
        }
        return colors.get(domain, "#FFA500")  # Default: orange


# Example usage
if __name__ == "__main__":
    spawner = CitySpawner()

    # Spawn Astrologist Office
    astrologist = spawner.spawn_office(
        domain="Astrologist",
        description="Cosmic pattern analysis and horoscope generation",
        specialists=[
            {
                "name": "StarDataFetcher",
                "description": "Retrieves planetary positions and astronomical data",
                "tools": ["ephemeris_api", "timezone_converter"]
            },
            {
                "name": "HoroscopeInterpreter",
                "description": "Interprets astrological aspects and generates horoscopes",
                "tools": ["aspect_calculator", "sign_interpreter"]
            },
            {
                "name": "NatalChartAnalyzer",
                "description": "Analyzes birth charts for personality insights",
                "tools": ["chart_generator", "house_system"]
            },
            {
                "name": "ReportWriter",
                "description": "Synthesizes astrological findings into readable reports",
                "tools": ["template_engine", "pdf_generator"]
            }
        ],
        tools=[
            {"name": "ephemeris_api", "description": "Swiss Ephemeris data", "implementation": "pyswisseph"},
            {"name": "chart_generator", "description": "SVG chart rendering", "implementation": "matplotlib"},
            {"name": "aspect_calculator", "description": "Calculate planetary aspects", "implementation": "custom"}
        ],
        metrics=["accuracy", "narrative_quality", "user_satisfaction"]
    )

    print(f"\n✨ Office created: {astrologist.domain}")
    print(f"   Config: offices/{astrologist.domain.lower()}/config/office.yaml")
