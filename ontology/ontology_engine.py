#!/usr/bin/env python3
"""
Unity Ontology Engine

Load, query, and reason over Unity's domain ontology.

Usage:
    from ontology.ontology_engine import OntologyEngine

    engine = OntologyEngine()
    concepts = engine.find_cross_domain_concept("cycles")
    office = engine.get_office("tarot")

Author: Dr. Claude Summers, Cosmic Orchestrator
Phase: 6 - Ontology & Ritual Engines
Date: October 16, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Entity:
    """Generic entity from ontology"""
    id: str
    type: str
    properties: Dict[str, Any]

    def get(self, key: str, default=None):
        """Get property value"""
        return self.properties.get(key, default)


@dataclass
class Relationship:
    """Relationship between entities"""
    type: str
    source: str
    target: str
    properties: Dict[str, Any] = field(default_factory=dict)


class OntologyEngine:
    """
    Engine for loading and querying Unity's domain ontology.

    Features:
    - Load YAML ontology
    - Query entities by ID or type
    - Find cross-domain concept mappings
    - Calculate semantic similarity
    - Suggest collaborations based on relationships
    """

    def __init__(self, ontology_path: Optional[str] = None):
        if ontology_path is None:
            # Default path relative to this file
            base_path = Path(__file__).parent
            ontology_path = base_path / "unity_ontology.yaml"

        self.ontology_path = Path(ontology_path)
        self.ontology = {}
        self.entities = {}
        self.relationships = []

        # Load ontology if it exists
        if self.ontology_path.exists():
            self.load()

    def load(self):
        """Load ontology from YAML"""
        with open(self.ontology_path, 'r') as f:
            self.ontology = yaml.safe_load(f)

        # Index entities
        self._index_entities()

        print(f"✅ Loaded ontology v{self.ontology.get('version')}")
        print(f"   Entities: {len(self.entities)}")
        print(f"   Concepts: {len(self.ontology.get('concept_mappings', {}))}")

    def _index_entities(self):
        """Index all entities from ontology"""
        entity_types = self.ontology.get('entities', {})

        for entity_type, schema in entity_types.items():
            examples = schema.get('examples', [])
            for example in examples:
                entity_id = example.get('id')
                if entity_id:
                    self.entities[entity_id] = Entity(
                        id=entity_id,
                        type=entity_type,
                        properties=example
                    )

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a given type"""
        return [e for e in self.entities.values() if e.type == entity_type]

    def get_district(self, district_id: str) -> Optional[Entity]:
        """Get district by ID"""
        return self.get_entity(district_id)

    def get_office(self, office_id: str) -> Optional[Entity]:
        """Get office (Building) by ID"""
        return self.get_entity(office_id)

    def get_offices_in_district(self, district_id: str) -> List[Entity]:
        """Get all offices in a district"""
        district = self.get_district(district_id)
        if not district:
            return []

        office_ids = district.get('offices', [])
        offices = []
        for office_id in office_ids:
            office = self.get_office(office_id)
            if office:
                offices.append(office)

        return offices

    def find_cross_domain_concept(self, concept: str) -> Optional[Dict]:
        """
        Find cross-domain mapping for a concept.

        Args:
            concept: Concept name (e.g., "cycles", "balance")

        Returns:
            Dict with concept description and instances across domains
        """
        mappings = self.ontology.get('concept_mappings', {})
        return mappings.get(concept)

    def get_all_concepts(self) -> List[str]:
        """Get list of all cross-domain concepts"""
        return list(self.ontology.get('concept_mappings', {}).keys())

    def find_related_offices(self, office_id: str, relation_type: Optional[str] = None) -> List[Dict]:
        """
        Find offices related to given office.

        Args:
            office_id: Office ID
            relation_type: Filter by relation type (optional)

        Returns:
            List of dicts with {office_id, relation_type, properties}
        """
        office = self.get_office(office_id)
        if not office:
            return []

        relationships = office.get('relationships', [])

        if relation_type:
            relationships = [r for r in relationships if r.get('type') == relation_type]

        return relationships

    def suggest_collaboration(self, offices: List[str]) -> Dict:
        """
        Suggest collaboration patterns based on office relationships.

        Args:
            offices: List of office IDs

        Returns:
            Dict with suggested mode, shared concepts, and rationale
        """
        # Get all offices
        office_entities = [self.get_office(oid) for oid in offices]
        office_entities = [o for o in office_entities if o]  # Filter None

        if not office_entities:
            return {"error": "No valid offices found"}

        # Find shared knowledge domains
        all_domains = []
        for office in office_entities:
            domains = office.get('knowledge_domains', [])
            all_domains.extend(domains)

        # Count domain occurrences
        domain_counts = {}
        for domain in all_domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        # Shared domains (appear in 2+ offices)
        shared_domains = [d for d, count in domain_counts.items() if count >= 2]

        # Suggest mode based on relationships
        has_relationships = any(office.get('relationships') for office in office_entities)

        if len(offices) == 2 and has_relationships:
            mode = "sequential"
            rationale = "Two offices with existing relationships work well sequentially"
        elif len(offices) >= 3:
            mode = "parallel"
            rationale = "Multiple offices can provide parallel perspectives"
        else:
            mode = "graph"
            rationale = "Custom graph-based workflow recommended"

        return {
            "mode": mode,
            "shared_concepts": shared_domains,
            "rationale": rationale,
            "participants": offices
        }

    def semantic_similarity(self, concept1: str, concept2: str) -> float:
        """
        Calculate semantic similarity between two concepts.

        Currently uses simple keyword overlap. Future: embedding-based.

        Returns:
            Similarity score [0.0, 1.0]
        """
        # Get concept mappings
        mapping1 = self.find_cross_domain_concept(concept1)
        mapping2 = self.find_cross_domain_concept(concept2)

        if not mapping1 or not mapping2:
            return 0.0

        # Extract keywords from instances
        keywords1 = set()
        for instance in mapping1.get('instances', []):
            keywords1.add(instance.get('term', '').lower())

        keywords2 = set()
        for instance in mapping2.get('instances', []):
            keywords2.add(instance.get('term', '').lower())

        # Jaccard similarity
        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        return intersection / union if union > 0 else 0.0

    def get_concept_for_domain(self, concept: str, domain: str) -> Optional[Dict]:
        """
        Get domain-specific instance of a cross-domain concept.

        Args:
            concept: Concept name (e.g., "cycles")
            domain: Domain/office name (e.g., "astrology")

        Returns:
            Instance dict or None
        """
        mapping = self.find_cross_domain_concept(concept)
        if not mapping:
            return None

        for instance in mapping.get('instances', []):
            if instance.get('domain') == domain:
                return instance

        return None

    def export_office_summary(self, office_id: str) -> Dict:
        """
        Export comprehensive summary of an office.

        Returns:
            Dict with all office info including relationships and concepts
        """
        office = self.get_office(office_id)
        if not office:
            return {"error": f"Office '{office_id}' not found"}

        # Get district
        district_id = office.get('district')
        district = self.get_district(district_id)

        # Get related offices
        relationships = self.find_related_offices(office_id)

        # Find concepts this office uses
        knowledge_domains = office.get('knowledge_domains', [])

        # Find cross-domain concepts related to these domains
        relevant_concepts = []
        for concept_name, concept_data in self.ontology.get('concept_mappings', {}).items():
            for instance in concept_data.get('instances', []):
                if instance.get('domain') == office_id:
                    relevant_concepts.append({
                        'concept': concept_name,
                        'term': instance.get('term'),
                        'example': instance.get('example')
                    })

        return {
            'office_id': office_id,
            'name': office.get('name'),
            'district': district.get('name') if district else None,
            'specialization': office.get('specialization'),
            'tools': office.get('tools', []),
            'knowledge_domains': knowledge_domains,
            'relationships': relationships,
            'cross_domain_concepts': relevant_concepts
        }

    def stats(self) -> Dict:
        """Get ontology statistics"""
        return {
            'version': self.ontology.get('version'),
            'entities': {
                entity_type: len(self.get_entities_by_type(entity_type))
                for entity_type in self.ontology.get('entities', {}).keys()
            },
            'concepts': len(self.ontology.get('concept_mappings', {})),
            'relationships': len(self.ontology.get('relationships', {}))
        }


# Singleton instance
_engine = None

def get_ontology_engine() -> OntologyEngine:
    """Get singleton ontology engine"""
    global _engine
    if _engine is None:
        _engine = OntologyEngine()
    return _engine


# CLI for testing
if __name__ == "__main__":
    engine = OntologyEngine()

    print("\n" + "=" * 70)
    print("UNITY ONTOLOGY ENGINE - TEST")
    print("=" * 70)

    # Stats
    print("\n📊 Statistics:")
    stats = engine.stats()
    print(f"   Version: {stats['version']}")
    for entity_type, count in stats['entities'].items():
        print(f"   {entity_type}: {count}")
    print(f"   Concepts: {stats['concepts']}")
    print(f"   Relationships: {stats['relationships']}")

    # Test: Get office
    print("\n🏢 Office: Tarot")
    tarot = engine.get_office('tarot')
    if tarot:
        print(f"   Name: {tarot.get('name')}")
        print(f"   District: {tarot.get('district')}")
        print(f"   Tools: {', '.join(tarot.get('tools', []))}")

    # Test: Cross-domain concept
    print("\n🔗 Cross-Domain Concept: 'cycles'")
    cycles = engine.find_cross_domain_concept('cycles')
    if cycles:
        print(f"   Description: {cycles['description']}")
        for instance in cycles['instances']:
            print(f"   - {instance['domain']}: {instance['term']}")

    # Test: Collaboration suggestion
    print("\n🤝 Collaboration Suggestion: [tarot, astrology, economist]")
    suggestion = engine.suggest_collaboration(['tarot', 'astrology', 'economist'])
    print(f"   Mode: {suggestion['mode']}")
    print(f"   Rationale: {suggestion['rationale']}")
    print(f"   Shared concepts: {', '.join(suggestion['shared_concepts'])}")

    # Test: Office summary
    print("\n📋 Office Summary: Economist")
    summary = engine.export_office_summary('economist')
    if 'error' not in summary:
        print(f"   Name: {summary['name']}")
        print(f"   District: {summary['district']}")
        print(f"   Knowledge domains: {len(summary['knowledge_domains'])}")
        print(f"   Relationships: {len(summary['relationships'])}")

    print("\n" + "=" * 70)
    print("✅ Ontology engine operational")
    print("=" * 70)
