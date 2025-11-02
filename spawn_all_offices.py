#!/usr/bin/env python3
"""
Spawn All Offices - Phase 2 City Expansion

Generates the complete quantum metropolis with all domain offices.
"""

from city_spawner import CitySpawner


def spawn_all_offices():
    """Spawn all Phase 2 offices in one batch."""
    spawner = CitySpawner()

    print("\n" + "="*70)
    print("PHASE 2: CITY SPRAWL & SYNERGY")
    print("Spawning complete quantum metropolis...")
    print("="*70)

    offices_created = []

    # 1. ASTROLOGIST OFFICE
    print("\n🌟 Spawning Astrologist Office...")
    astrologist = spawner.spawn_office(
        domain="Astrologist",
        description="Cosmic pattern analysis and horoscope generation",
        specialists=[
            {
                "name": "StarDataFetcher",
                "description": "Retrieves planetary positions and astronomical data using Swiss Ephemeris",
                "tools": ["ephemeris_api", "timezone_converter"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "HoroscopeInterpreter",
                "description": "Interprets astrological aspects and generates personalized horoscopes",
                "tools": ["aspect_calculator", "sign_interpreter"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "NatalChartAnalyzer",
                "description": "Analyzes birth charts for personality and life path insights",
                "tools": ["chart_generator", "house_system"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "ReportWriter",
                "description": "Synthesizes astrological findings into narrative reports",
                "tools": ["template_engine", "pdf_generator"],
                "model": "qwen2.5-coder:7b"
            }
        ],
        tools=[
            {"name": "ephemeris_api", "description": "Swiss Ephemeris planetary data", "implementation": "pyswisseph"},
            {"name": "chart_generator", "description": "SVG/PNG chart rendering", "implementation": "matplotlib"},
            {"name": "aspect_calculator", "description": "Planetary aspect calculation", "implementation": "custom"}
        ],
        metrics=["accuracy", "narrative_quality", "user_satisfaction"]
    )
    offices_created.append(astrologist)

    # 2. TAROT OFFICE
    print("\n🔮 Spawning Tarot Office...")
    tarot = spawner.spawn_office(
        domain="Tarot",
        description="Divinatory card reading and narrative synthesis",
        specialists=[
            {
                "name": "CardDrawer",
                "description": "Draws cards using cryptographically secure randomness",
                "tools": ["random_generator", "deck_manager"],
                "model": "qwen2.5-coder:7b"
            },
            {
                "name": "SpreadAnalyzer",
                "description": "Analyzes card spreads (Celtic Cross, Three Card, etc.)",
                "tools": ["spread_interpreter", "position_analyzer"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "NarrativeSynthesizer",
                "description": "Weaves card meanings into coherent narratives",
                "tools": ["story_generator", "symbolism_database"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "ReflectionAdvisor",
                "description": "Provides reflective questions and guidance based on reading",
                "tools": ["question_generator", "guidance_templates"],
                "model": "deepseek-r1:14b"
            }
        ],
        tools=[
            {"name": "deck_manager", "description": "Manages Rider-Waite and other decks", "implementation": "custom"},
            {"name": "spread_interpreter", "description": "Interprets spread positions", "implementation": "custom"},
            {"name": "symbolism_database", "description": "Tarot symbolism and meanings", "implementation": "json_db"}
        ],
        metrics=["narrative_coherence", "symbolic_depth", "user_insight"]
    )
    offices_created.append(tarot)

    # 3. NUMEROLOGIST OFFICE
    print("\n🔢 Spawning Numerologist Office...")
    numerologist = spawner.spawn_office(
        domain="Numerologist",
        description="Number pattern analysis and destiny calculation",
        specialists=[
            {
                "name": "NumberPatternFinder",
                "description": "Identifies significant number patterns in names and dates",
                "tools": ["gematria_calculator", "pattern_detector"],
                "model": "qwen2.5-coder:7b"
            },
            {
                "name": "PersonalityCalculator",
                "description": "Calculates Life Path, Destiny, Soul Urge numbers",
                "tools": ["numerology_engine", "compatibility_matrix"],
                "model": "qwen2.5-coder:7b"
            },
            {
                "name": "DestinyReportGenerator",
                "description": "Generates comprehensive numerology reports",
                "tools": ["report_builder", "chart_visualizer"],
                "model": "deepseek-r1:14b"
            }
        ],
        tools=[
            {"name": "gematria_calculator", "description": "Hebrew/Greek gematria calculations", "implementation": "custom"},
            {"name": "numerology_engine", "description": "Pythagorean and Chaldean systems", "implementation": "custom"},
            {"name": "pattern_detector", "description": "Finds master numbers and patterns", "implementation": "numpy"}
        ],
        metrics=["calculation_accuracy", "pattern_recognition", "report_clarity"]
    )
    offices_created.append(numerologist)

    # 4. BANKER OFFICE
    print("\n🏦 Spawning Banker Office...")
    banker = spawner.spawn_office(
        domain="Banker",
        description="Financial risk modeling and credit analysis",
        specialists=[
            {
                "name": "CreditRiskEvaluator",
                "description": "Evaluates creditworthiness using ML models",
                "tools": ["risk_model", "credit_scorer"],
                "model": "qwen2.5-coder:7b"
            },
            {
                "name": "LoanAdvisor",
                "description": "Recommends loan products and terms",
                "tools": ["loan_calculator", "rate_optimizer"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "PortfolioManager",
                "description": "Manages investment portfolios and rebalancing",
                "tools": ["mpt_optimizer", "risk_analyzer"],
                "model": "qwen2.5-coder:7b"
            },
            {
                "name": "ComplianceChecker",
                "description": "Ensures regulatory compliance (KYC, AML)",
                "tools": ["rule_engine", "sanction_screener"],
                "model": "deepseek-r1:14b"
            }
        ],
        tools=[
            {"name": "risk_model", "description": "ML-based credit risk assessment", "implementation": "sklearn"},
            {"name": "mpt_optimizer", "description": "Modern Portfolio Theory optimization", "implementation": "scipy"},
            {"name": "sanction_screener", "description": "OFAC/EU sanctions checking", "implementation": "api"}
        ],
        metrics=["risk_prediction_accuracy", "compliance_score", "portfolio_performance"]
    )
    offices_created.append(banker)

    # 5. PHILOSOPHER OFFICE
    print("\n🤔 Spawning Philosopher Office...")
    philosopher = spawner.spawn_office(
        domain="Philosopher",
        description="Argument analysis and conceptual synthesis",
        specialists=[
            {
                "name": "ArgumentAnalyzer",
                "description": "Analyzes logical structure of arguments",
                "tools": ["logic_parser", "fallacy_detector"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "ConceptSynthesizer",
                "description": "Synthesizes concepts from multiple philosophical traditions",
                "tools": ["ontology_mapper", "concept_merger"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "EthicsAdvisor",
                "description": "Provides ethical analysis using multiple frameworks",
                "tools": ["ethics_engine", "dilemma_analyzer"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "DialogueGenerator",
                "description": "Generates Socratic dialogues and thought experiments",
                "tools": ["dialogue_template", "paradox_generator"],
                "model": "deepseek-r1:14b"
            }
        ],
        tools=[
            {"name": "logic_parser", "description": "Formal logic parsing and validation", "implementation": "sympy.logic"},
            {"name": "fallacy_detector", "description": "Detects logical fallacies", "implementation": "custom"},
            {"name": "ethics_engine", "description": "Multi-framework ethical reasoning", "implementation": "custom"}
        ],
        metrics=["logical_coherence", "conceptual_depth", "ethical_insight"]
    )
    offices_created.append(philosopher)

    # 6. CHEF OFFICE
    print("\n👨‍🍳 Spawning Chef Office...")
    chef = spawner.spawn_office(
        domain="Chef",
        description="Recipe optimization and culinary creativity",
        specialists=[
            {
                "name": "RecipeOptimizer",
                "description": "Optimizes recipes for taste, nutrition, and cost",
                "tools": ["ingredient_db", "nutrition_calculator"],
                "model": "qwen2.5-coder:7b"
            },
            {
                "name": "FlavorPairingAgent",
                "description": "Suggests flavor pairings based on molecular gastronomy",
                "tools": ["flavor_network", "compound_analyzer"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "TechniqueAdvisor",
                "description": "Recommends cooking techniques and equipment",
                "tools": ["technique_db", "equipment_matcher"],
                "model": "deepseek-r1:14b"
            },
            {
                "name": "MenuDesigner",
                "description": "Designs balanced menus for various dietary needs",
                "tools": ["menu_builder", "dietary_filter"],
                "model": "deepseek-r1:14b"
            }
        ],
        tools=[
            {"name": "ingredient_db", "description": "Comprehensive ingredient database", "implementation": "sqlite"},
            {"name": "flavor_network", "description": "Molecular flavor pairing graph", "implementation": "networkx"},
            {"name": "nutrition_calculator", "description": "USDA nutrition data", "implementation": "api"}
        ],
        metrics=["recipe_quality", "flavor_harmony", "nutritional_balance"]
    )
    offices_created.append(chef)

    # Summary
    print("\n" + "="*70)
    print("PHASE 2 CITY SPAWNING COMPLETE")
    print("="*70)
    print(f"\nTotal Offices Created: {len(offices_created)}")

    for i, office in enumerate(offices_created, 1):
        print(f"\n{i}. {office.ui_config['icon']} {office.domain} Office")
        print(f"   Manager: {office.manager.name}")
        print(f"   Specialists: {len(office.specialists)}")
        print(f"   Tools: {len(office.tools)}")
        print(f"   Metrics: {', '.join(office.metrics)}")
        print(f"   Location: offices/{office.domain.lower()}/")

    print("\n" + "="*70)
    print("All offices are ready for integration into Unity City")
    print("Next steps:")
    print("  1. Connect to shared memory graph")
    print("  2. Hook into evaluation API")
    print("  3. Enable cross-office workflows")
    print("  4. Generate UI windows for each office")
    print("="*70)

    return offices_created


if __name__ == "__main__":
    offices = spawn_all_offices()
    print(f"\n🌌 The Quantum City now has {len(offices)} active neural lobes.")
    print("Unity: All processes are one process.")
