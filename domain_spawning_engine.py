#!/usr/bin/env python3
"""
DomainSpawningEngine - Infinite City Expansion Meta-Engine

This is the self-replication mechanism of Unity. Given:
- A domain name (e.g., "Quantum Physics")
- An archetype category (e.g., "Science")
- Optional customization

The engine generates:
- Complete office structure (manager + specialists)
- Domain-appropriate tools
- Evaluation metrics
- Memory graph integration
- UI window configuration
- Evolution loop hooks

Archetypes define the "cognitive style" of the office:
- Metaphysics: Interpreter, Oracle, Synthesizer, Advisor
- Finance: Analyst, Risk Assessor, Advisor, Compliance
- Science: Researcher, Modeler, Experimenter, Reporter
- Art: Creator, Critic, Curator, Performer
- Health: Diagnostician, Therapist, Coach, Nutritionist
- Education: Teacher, Tutor, Curriculum Designer, Assessor
- Craft: Designer, Builder, Optimizer, Tester
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from city_spawner import CitySpawner, OfficeSpec


# Archetype Templates
ARCHETYPE_TEMPLATES = {
    "Metaphysics": {
        "specialist_roles": [
            {"name": "Interpreter", "desc": "Interprets symbolic patterns and meanings"},
            {"name": "Oracle", "desc": "Provides divinations and predictions"},
            {"name": "Synthesizer", "desc": "Weaves insights into coherent narratives"},
            {"name": "Advisor", "desc": "Offers guidance and reflective questions"}
        ],
        "tools": ["symbolism_db", "pattern_detector", "narrative_generator"],
        "metrics": ["symbolic_depth", "narrative_coherence", "insight_quality"],
        "model_preference": "deepseek-r1:14b"  # Reasoning-heavy
    },
    "Finance": {
        "specialist_roles": [
            {"name": "Analyst", "desc": "Analyzes market data and financial statements"},
            {"name": "RiskAssessor", "desc": "Evaluates and quantifies risks"},
            {"name": "Advisor", "desc": "Recommends investment strategies"},
            {"name": "ComplianceChecker", "desc": "Ensures regulatory compliance"}
        ],
        "tools": ["market_data_api", "risk_model", "compliance_engine"],
        "metrics": ["prediction_accuracy", "risk_score", "compliance_rate"],
        "model_preference": "qwen2.5-coder:7b"  # Calculation-heavy
    },
    "Science": {
        "specialist_roles": [
            {"name": "Researcher", "desc": "Conducts literature review and hypothesis generation"},
            {"name": "Modeler", "desc": "Builds computational or mathematical models"},
            {"name": "Experimenter", "desc": "Designs and simulates experiments"},
            {"name": "Reporter", "desc": "Writes research summaries and papers"}
        ],
        "tools": ["literature_search", "simulation_engine", "data_visualizer"],
        "metrics": ["hypothesis_quality", "model_accuracy", "reproducibility"],
        "model_preference": "deepseek-r1:14b"  # Reasoning + modeling
    },
    "Art": {
        "specialist_roles": [
            {"name": "Creator", "desc": "Generates original artistic content"},
            {"name": "Critic", "desc": "Analyzes and critiques artistic works"},
            {"name": "Curator", "desc": "Selects and organizes collections"},
            {"name": "Performer", "desc": "Presents or performs works"}
        ],
        "tools": ["generation_engine", "style_analyzer", "gallery_manager"],
        "metrics": ["originality", "aesthetic_quality", "emotional_impact"],
        "model_preference": "deepseek-r1:14b"  # Creative reasoning
    },
    "Health": {
        "specialist_roles": [
            {"name": "Diagnostician", "desc": "Identifies health issues and root causes"},
            {"name": "Therapist", "desc": "Provides therapeutic interventions"},
            {"name": "Coach", "desc": "Motivates and tracks progress"},
            {"name": "Nutritionist", "desc": "Designs nutrition and wellness plans"}
        ],
        "tools": ["symptom_analyzer", "treatment_db", "wellness_tracker"],
        "metrics": ["diagnostic_accuracy", "treatment_efficacy", "patient_satisfaction"],
        "model_preference": "deepseek-r1:14b"  # Medical reasoning
    },
    "Education": {
        "specialist_roles": [
            {"name": "Teacher", "desc": "Explains concepts and facilitates learning"},
            {"name": "Tutor", "desc": "Provides personalized instruction"},
            {"name": "CurriculumDesigner", "desc": "Designs learning pathways"},
            {"name": "Assessor", "desc": "Evaluates student understanding"}
        ],
        "tools": ["concept_explainer", "quiz_generator", "progress_tracker"],
        "metrics": ["learning_gain", "engagement", "mastery_level"],
        "model_preference": "deepseek-r1:14b"  # Pedagogical reasoning
    },
    "Craft": {
        "specialist_roles": [
            {"name": "Designer", "desc": "Designs functional and aesthetic solutions"},
            {"name": "Builder", "desc": "Implements and constructs designs"},
            {"name": "Optimizer", "desc": "Improves efficiency and performance"},
            {"name": "Tester", "desc": "Validates quality and usability"}
        ],
        "tools": ["design_tool", "build_system", "optimization_engine"],
        "metrics": ["functionality", "efficiency", "quality"],
        "model_preference": "qwen2.5-coder:7b"  # Implementation-heavy
    },
    "Community": {
        "specialist_roles": [
            {"name": "Counselor", "desc": "Provides emotional and social support"},
            {"name": "Mediator", "desc": "Resolves conflicts and facilitates dialogue"},
            {"name": "Organizer", "desc": "Coordinates community activities"},
            {"name": "Advocate", "desc": "Champions causes and represents interests"}
        ],
        "tools": ["counseling_framework", "conflict_resolver", "event_planner"],
        "metrics": ["satisfaction", "resolution_rate", "community_health"],
        "model_preference": "deepseek-r1:14b"  # Social reasoning
    }
}


@dataclass
class DomainTemplate:
    """Template for spawning a domain-specific office."""
    domain: str
    archetype: str
    specialists: List[Dict[str, str]]
    tools: List[str]
    metrics: List[str]
    model_preference: str
    custom_config: Optional[Dict[str, Any]] = None


class DomainSpawningEngine:
    """
    Meta-engine for infinite city expansion.

    Generates offices based on archetype templates + domain specifics.
    """

    def __init__(self, spawner: Optional[CitySpawner] = None):
        self.spawner = spawner or CitySpawner()
        self.archetypes = ARCHETYPE_TEMPLATES
        self.spawned_offices: List[OfficeSpec] = []

    def spawn_from_archetype(
        self,
        domain: str,
        archetype: str,
        custom_specialists: Optional[List[Dict]] = None,
        custom_tools: Optional[List[str]] = None,
        custom_metrics: Optional[List[str]] = None
    ) -> OfficeSpec:
        """
        Spawn office from archetype template.

        Args:
            domain: Domain name (e.g., "Quantum Physics")
            archetype: Archetype category (e.g., "Science")
            custom_specialists: Override specialist roles
            custom_tools: Additional tools
            custom_metrics: Additional metrics

        Returns:
            OfficeSpec for spawned office
        """
        if archetype not in self.archetypes:
            raise ValueError(f"Unknown archetype: {archetype}. Available: {list(self.archetypes.keys())}")

        template = self.archetypes[archetype]

        # Build specialists list
        specialists = custom_specialists if custom_specialists else []
        if not specialists:
            for role in template["specialist_roles"]:
                specialist_name = f"{domain.replace(' ', '')}{role['name']}"
                specialists.append({
                    "name": specialist_name,
                    "description": f"{role['desc']} for {domain}",
                    "model": template["model_preference"],
                    "tools": custom_tools or template["tools"]
                })

        # Build tools list
        tools = []
        tool_names = custom_tools if custom_tools else template["tools"]
        for tool_name in tool_names:
            tools.append({
                "name": tool_name,
                "description": f"{tool_name.replace('_', ' ').title()} for {domain}",
                "implementation": "custom"
            })

        # Build metrics
        metrics = custom_metrics if custom_metrics else template["metrics"]

        # Spawn office using CitySpawner
        office_spec = self.spawner.spawn_office(
            domain=domain,
            description=f"{archetype} office for {domain}",
            specialists=specialists,
            tools=tools,
            metrics=metrics
        )

        self.spawned_offices.append(office_spec)
        return office_spec

    def spawn_from_config(self, config: Dict[str, Any]) -> OfficeSpec:
        """
        Spawn office from JSON/YAML config.

        Config format:
        {
            "domain": "Quantum Physics",
            "archetype": "Science",
            "custom_specialists": [...],  # Optional
            "custom_tools": [...],         # Optional
            "custom_metrics": [...]        # Optional
        }
        """
        return self.spawn_from_archetype(
            domain=config["domain"],
            archetype=config["archetype"],
            custom_specialists=config.get("custom_specialists"),
            custom_tools=config.get("custom_tools"),
            custom_metrics=config.get("custom_metrics")
        )

    def batch_spawn(self, configs: List[Dict[str, Any]]) -> List[OfficeSpec]:
        """Spawn multiple offices from config list."""
        return [self.spawn_from_config(cfg) for cfg in configs]

    def spawn_hierarchical(
        self,
        hierarchy: Dict[str, Any],
        parent_domain: str = ""
    ) -> List[OfficeSpec]:
        """
        Spawn offices hierarchically.

        hierarchy = {
            "Science": {
                "archetype": "Science",
                "children": {
                    "Physics": {
                        "archetype": "Science",
                        "children": {
                            "Quantum Mechanics": {"archetype": "Science"},
                            "Classical Mechanics": {"archetype": "Science"}
                        }
                    },
                    "Biology": {"archetype": "Science"}
                }
            }
        }
        """
        spawned = []

        for domain, spec in hierarchy.items():
            full_domain = f"{parent_domain} {domain}".strip()

            # Spawn this level
            office = self.spawn_from_archetype(
                domain=full_domain,
                archetype=spec["archetype"]
            )
            spawned.append(office)

            # Recurse into children
            if "children" in spec:
                spawned.extend(
                    self.spawn_hierarchical(spec["children"], parent_domain=full_domain)
                )

        return spawned

    def get_stats(self) -> Dict[str, Any]:
        """Get spawning statistics."""
        archetype_counts = {}
        for office in self.spawned_offices:
            # Infer archetype from office config
            archetype = "Unknown"
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

        return {
            "total_offices": len(self.spawned_offices),
            "archetype_distribution": archetype_counts,
            "domains": [o.domain for o in self.spawned_offices]
        }


# Example usage and testing
if __name__ == "__main__":
    engine = DomainSpawningEngine()

    print("="*70)
    print("DOMAIN SPAWNING ENGINE - INFINITE CITY EXPANSION")
    print("="*70)

    # Test 1: Spawn from archetype
    print("\n1. Spawning Quantum Physics (Science archetype)...")
    quantum = engine.spawn_from_archetype("Quantum Physics", "Science")
    print(f"   ✅ {quantum.domain} spawned with {len(quantum.specialists)} specialists")

    # Test 2: Spawn from config
    print("\n2. Spawning from JSON config...")
    config = {
        "domain": "Dream Analysis",
        "archetype": "Metaphysics",
        "custom_metrics": ["dream_interpretation_depth", "symbolism_coherence"]
    }
    dream = engine.spawn_from_config(config)
    print(f"   ✅ {dream.domain} spawned")

    # Test 3: Batch spawn
    print("\n3. Batch spawning multiple offices...")
    batch_configs = [
        {"domain": "Machine Learning", "archetype": "Science"},
        {"domain": "Jazz Composition", "archetype": "Art"},
        {"domain": "Conflict Resolution", "archetype": "Community"}
    ]
    batch = engine.batch_spawn(batch_configs)
    print(f"   ✅ Spawned {len(batch)} offices")

    # Test 4: Hierarchical spawn
    print("\n4. Hierarchical spawning (Science → Physics → subfields)...")
    hierarchy = {
        "Science": {
            "archetype": "Science",
            "children": {
                "Physics": {
                    "archetype": "Science",
                    "children": {
                        "Quantum Mechanics": {"archetype": "Science"},
                        "Thermodynamics": {"archetype": "Science"}
                    }
                }
            }
        }
    }
    hierarchical = engine.spawn_hierarchical(hierarchy)
    print(f"   ✅ Spawned {len(hierarchical)} offices hierarchically")

    # Stats
    print("\n" + "="*70)
    print("SPAWNING COMPLETE")
    print("="*70)
    stats = engine.get_stats()
    print(f"Total Offices: {stats['total_offices']}")
    print(f"Domains: {', '.join(stats['domains'])}")
    print("\n🌌 Unity: All processes are one process")
