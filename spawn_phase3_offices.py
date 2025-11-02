#!/usr/bin/env python3
"""
Phase 3: Infinite City Expansion - Initial Office Wave

Spawns 20+ offices across all 8 archetypes to demonstrate the scalability
of Unity's domain-agnostic architecture.

Archetypes:
- Metaphysics: Esoteric and symbolic domains
- Finance: Economic and market analysis
- Science: Research and empirical investigation
- Art: Creative expression and aesthetics
- Health: Wellness and medical domains
- Education: Knowledge transmission
- Craft: Practical construction and optimization
- Community: Social cohesion and mediation
"""

from domain_spawning_engine import DomainSpawningEngine


def spawn_phase3_offices():
    """Spawn the Phase 3 initial office wave."""
    engine = DomainSpawningEngine()

    print("\n" + "="*70)
    print("PHASE 3: INFINITE CITY EXPANSION")
    print("Spawning 20+ offices across all archetypes...")
    print("="*70)

    # Batch configuration for Phase 3 offices
    phase3_configs = [
        # ========== METAPHYSICS (5 offices) ==========
        {
            "domain": "Astral Projection",
            "archetype": "Metaphysics",
            "custom_metrics": ["astral_coherence", "journey_depth", "symbolic_richness"]
        },
        {
            "domain": "I Ching",
            "archetype": "Metaphysics",
            "custom_metrics": ["hexagram_accuracy", "interpretation_depth", "guidance_quality"]
        },
        {
            "domain": "Alchemy",
            "archetype": "Metaphysics",
            "custom_metrics": ["transmutation_coherence", "symbolic_depth", "spiritual_insight"]
        },
        {
            "domain": "Kabbalah",
            "archetype": "Metaphysics",
            "custom_metrics": ["tree_of_life_accuracy", "gematria_coherence", "mystical_depth"]
        },
        {
            "domain": "Runes",
            "archetype": "Metaphysics",
            "custom_metrics": ["rune_interpretation", "casting_accuracy", "divinatory_insight"]
        },

        # ========== FINANCE (4 offices) ==========
        {
            "domain": "Accountant",
            "archetype": "Finance",
            "custom_metrics": ["accuracy", "compliance_rate", "audit_quality"]
        },
        {
            "domain": "Insurance Analyst",
            "archetype": "Finance",
            "custom_metrics": ["risk_assessment_accuracy", "premium_optimization", "claim_prediction"]
        },
        {
            "domain": "Market Trader",
            "archetype": "Finance",
            "custom_metrics": ["trade_accuracy", "risk_adjusted_return", "market_timing"]
        },
        {
            "domain": "Economist",
            "archetype": "Finance",
            "custom_metrics": ["forecast_accuracy", "policy_impact_analysis", "model_quality"]
        },

        # ========== SCIENCE (5 offices) ==========
        {
            "domain": "Astronomer",
            "archetype": "Science",
            "custom_metrics": ["observation_accuracy", "model_quality", "discovery_rate"]
        },
        {
            "domain": "Chemist",
            "archetype": "Science",
            "custom_metrics": ["synthesis_success", "reaction_prediction", "safety_compliance"]
        },
        {
            "domain": "Biologist",
            "archetype": "Science",
            "custom_metrics": ["hypothesis_quality", "experimental_design", "reproducibility"]
        },
        {
            "domain": "Geologist",
            "archetype": "Science",
            "custom_metrics": ["mineral_identification", "formation_analysis", "prediction_accuracy"]
        },
        {
            "domain": "Environmental Scientist",
            "archetype": "Science",
            "custom_metrics": ["ecosystem_modeling", "impact_assessment", "sustainability_score"]
        },

        # ========== ART (4 offices) ==========
        {
            "domain": "Musician",
            "archetype": "Art",
            "custom_metrics": ["harmonic_quality", "emotional_resonance", "technical_mastery"]
        },
        {
            "domain": "Painter",
            "archetype": "Art",
            "custom_metrics": ["composition_quality", "color_harmony", "emotional_impact"]
        },
        {
            "domain": "Poet",
            "archetype": "Art",
            "custom_metrics": ["linguistic_creativity", "metaphor_depth", "emotional_resonance"]
        },
        {
            "domain": "Game Designer",
            "archetype": "Art",
            "custom_metrics": ["gameplay_balance", "narrative_quality", "player_engagement"]
        },

        # ========== HEALTH (3 offices) ==========
        {
            "domain": "Herbalist",
            "archetype": "Health",
            "custom_metrics": ["remedy_effectiveness", "safety_compliance", "patient_satisfaction"]
        },
        {
            "domain": "Physical Trainer",
            "archetype": "Health",
            "custom_metrics": ["program_effectiveness", "injury_prevention", "client_progress"]
        },
        {
            "domain": "Sleep Coach",
            "archetype": "Health",
            "custom_metrics": ["sleep_quality_improvement", "protocol_adherence", "client_satisfaction"]
        },

        # ========== EDUCATION (3 offices) ==========
        {
            "domain": "Language Teacher",
            "archetype": "Education",
            "custom_metrics": ["fluency_gain", "retention_rate", "engagement_score"]
        },
        {
            "domain": "Historian",
            "archetype": "Education",
            "custom_metrics": ["accuracy", "source_quality", "narrative_coherence"]
        },
        {
            "domain": "Librarian",
            "archetype": "Education",
            "custom_metrics": ["cataloging_accuracy", "retrieval_efficiency", "curation_quality"]
        },

        # ========== CRAFT (2 offices) ==========
        {
            "domain": "Software Engineer",
            "archetype": "Craft",
            "custom_metrics": ["code_quality", "test_coverage", "performance_optimization"]
        },
        {
            "domain": "Mechanical Engineer",
            "archetype": "Craft",
            "custom_metrics": ["design_efficiency", "structural_integrity", "manufacturability"]
        },

        # ========== COMMUNITY (2 offices) ==========
        {
            "domain": "Environmentalist",
            "archetype": "Community",
            "custom_metrics": ["conservation_impact", "community_engagement", "sustainability_score"]
        },
        {
            "domain": "Urban Planner",
            "archetype": "Community",
            "custom_metrics": ["livability_score", "sustainability", "community_satisfaction"]
        }
    ]

    print(f"\nTotal offices to spawn: {len(phase3_configs)}")
    print("\nArchetype distribution:")
    archetype_counts = {}
    for cfg in phase3_configs:
        arch = cfg["archetype"]
        archetype_counts[arch] = archetype_counts.get(arch, 0) + 1

    for arch, count in sorted(archetype_counts.items()):
        print(f"  {arch}: {count} offices")

    print("\n" + "="*70)
    print("SPAWNING OFFICES...")
    print("="*70)

    # Batch spawn all offices
    spawned = engine.batch_spawn(phase3_configs)

    print("\n" + "="*70)
    print("PHASE 3 INITIAL WAVE COMPLETE")
    print("="*70)

    print(f"\n✅ Total offices spawned: {len(spawned)}")

    # Group by archetype
    by_archetype = {}
    for office in spawned:
        # Infer archetype from config
        matching_cfg = next(c for c in phase3_configs if c["domain"] == office.domain)
        arch = matching_cfg["archetype"]

        if arch not in by_archetype:
            by_archetype[arch] = []
        by_archetype[arch].append(office)

    print("\nOffices by archetype:")
    for arch, offices in sorted(by_archetype.items()):
        print(f"\n{arch.upper()} ({len(offices)} offices):")
        for office in offices:
            print(f"  {office.ui_config['icon']} {office.domain}")
            print(f"     Manager: {office.manager.name}")
            print(f"     Specialists: {len(office.specialists)}")
            print(f"     Metrics: {', '.join(office.metrics)}")

    # Statistics
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)

    total_specialists = sum(len(o.specialists) for o in spawned)
    total_tools = sum(len(o.tools) for o in spawned)
    total_metrics = sum(len(o.metrics) for o in spawned)

    print(f"Total Offices:       {len(spawned)}")
    print(f"Total Managers:      {len(spawned)}")
    print(f"Total Specialists:   {total_specialists}")
    print(f"Total Tools:         {total_tools}")
    print(f"Total Metrics:       {total_metrics}")
    print(f"Total Agents:        {len(spawned) + total_specialists} (managers + specialists)")

    # Model distribution
    deepseek_count = 0
    qwen_count = 0
    for office in spawned:
        if office.manager.model == "deepseek-r1:14b":
            deepseek_count += 1
        for specialist in office.specialists:
            if specialist.model == "deepseek-r1:14b":
                deepseek_count += 1
            else:
                qwen_count += 1

    print(f"\nModel Distribution:")
    print(f"  DeepSeek-R1:14B (reasoning):  {deepseek_count} agents")
    print(f"  Qwen-2.5-coder:7B (code):     {qwen_count} agents")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Run evolution loops for each office with domain-specific metrics")
    print("2. Build cross-domain memory graph for knowledge sharing")
    print("3. Create Global Evolution Monitor dashboard")
    print("4. Implement hybrid workflows (cross-office collaboration)")
    print("5. Generate UI windows for all offices")
    print("6. Integrate research materials via Research Agents")
    print("="*70)

    print("\n🌌 The Quantum City now has {} active neural lobes.".format(len(spawned)))
    print("Unity: All processes are one process.")

    return spawned


if __name__ == "__main__":
    spawned_offices = spawn_phase3_offices()

    # Save manifest
    import json
    from pathlib import Path

    manifest = {
        "phase": 3,
        "total_offices": len(spawned_offices),
        "domains": [o.domain for o in spawned_offices],
        "created_at": spawned_offices[0].created_at if spawned_offices else None
    }

    Path("phase3_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("\n📋 Manifest saved to phase3_manifest.json")
