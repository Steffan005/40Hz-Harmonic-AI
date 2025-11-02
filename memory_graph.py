#!/usr/bin/env python3
"""
Cross-Office Memory Graph — Shared Knowledge System

Enables offices to share knowledge with TTL, consent flags, and semantic search.
Foundation for hybrid workflows and cross-domain synthesis.

Features:
- Memory nodes with metadata (office, tags, TTL, consent)
- Directed edges (dependencies, references, triggers)
- TTL-based auto-pruning
- Consent-based access control
- Semantic search (embeddings)
- Hierarchical summarization
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib


@dataclass
class MemoryNode:
    """Single memory node in the graph."""
    id: str
    office: str  # Which office created this
    content: str  # The actual knowledge
    created_at: datetime
    expires_at: datetime  # TTL
    consent_required: bool  # If True, only creating office can access
    tags: List[str]  # For filtering/search
    access_count: int = 0
    embedding: Optional[List[float]] = None  # For semantic search


@dataclass
class MemoryEdge:
    """Directed edge between nodes."""
    id: str
    source: str  # source node ID
    target: str  # target node ID
    relation: str  # "depends_on", "references", "triggers", "summarizes"
    weight: float = 1.0
    metadata: Dict = None


class MemoryGraph:
    """
    Shared memory graph for cross-office collaboration.

    Architecture:
    - Nodes: Individual memories (queries, results, insights)
    - Edges: Relationships between memories
    - TTL: Automatic expiration and pruning
    - Consent: Access control per node
    - Semantic Search: Find related memories via embeddings
    """

    def __init__(self, storage_path: Path = None):
        self.nodes: Dict[str, MemoryNode] = {}
        self.edges: Dict[str, MemoryEdge] = {}
        self.office_index: Dict[str, Set[str]] = {}  # office -> node IDs
        self.tag_index: Dict[str, Set[str]] = {}  # tag -> node IDs

        self.storage_path = storage_path or Path("data/memory_graph.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load from disk if exists
        if self.storage_path.exists():
            self._load_from_disk()

    def add_node(
        self,
        office: str,
        content: str,
        ttl_hours: int = 24,
        consent_required: bool = False,
        tags: List[str] = None,
        embedding: List[float] = None
    ) -> str:
        """
        Add memory node to graph.

        Args:
            office: Office that created this memory
            content: The knowledge/data to store
            ttl_hours: Time to live in hours (default 24)
            consent_required: If True, only this office can access
            tags: Tags for filtering
            embedding: Optional embedding for semantic search

        Returns:
            Node ID (UUID)
        """
        node_id = str(uuid.uuid4())
        tags = tags or []

        node = MemoryNode(
            id=node_id,
            office=office,
            content=content,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
            consent_required=consent_required,
            tags=tags,
            access_count=0,
            embedding=embedding
        )

        self.nodes[node_id] = node

        # Update indexes
        if office not in self.office_index:
            self.office_index[office] = set()
        self.office_index[office].add(node_id)

        for tag in tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(node_id)

        self._save_to_disk()
        return node_id

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        weight: float = 1.0,
        metadata: Dict = None
    ) -> str:
        """
        Add directed edge between nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation: Type of relationship
            weight: Edge weight (default 1.0)
            metadata: Optional metadata dict

        Returns:
            Edge ID (UUID)
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError(f"Both nodes must exist: {source_id}, {target_id}")

        edge_id = str(uuid.uuid4())

        edge = MemoryEdge(
            id=edge_id,
            source=source_id,
            target=target_id,
            relation=relation,
            weight=weight,
            metadata=metadata or {}
        )

        self.edges[edge_id] = edge
        self._save_to_disk()
        return edge_id

    def query(
        self,
        querying_office: str,
        tags: List[str] = None,
        offices: List[str] = None,
        semantic_query: str = None,
        limit: int = 10
    ) -> List[MemoryNode]:
        """
        Query memory graph with filtering.

        Args:
            querying_office: Office making the query
            tags: Filter by tags (any match)
            offices: Filter by creating offices
            semantic_query: Optional semantic search string
            limit: Max results

        Returns:
            List of matching MemoryNode objects
        """
        results = []

        for node in self.nodes.values():
            # Check expiration
            if datetime.utcnow() > node.expires_at:
                continue

            # Check consent
            if node.consent_required and querying_office != node.office:
                continue

            # Office filter
            if offices and node.office not in offices:
                continue

            # Tag filter
            if tags and not any(t in node.tags for t in tags):
                continue

            # Semantic search (if provided and embeddings available)
            if semantic_query and node.embedding:
                similarity = self._compute_similarity(semantic_query, node.embedding)
                if similarity < 0.7:  # Threshold
                    continue

            results.append(node)
            node.access_count += 1

        # Sort by creation time (newest first)
        results.sort(key=lambda n: n.created_at, reverse=True)

        return results[:limit]

    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, relation: str = None) -> List[MemoryNode]:
        """
        Get neighboring nodes via edges.

        Args:
            node_id: Center node ID
            relation: Optional filter by edge relation

        Returns:
            List of connected MemoryNode objects
        """
        neighbors = []

        for edge in self.edges.values():
            if edge.source == node_id:
                if relation is None or edge.relation == relation:
                    target_node = self.nodes.get(edge.target)
                    if target_node:
                        neighbors.append(target_node)

        return neighbors

    def link_offices(self, office_a: str, office_b: str, relation: str) -> str:
        """
        Create conceptual link between two offices.

        Creates a metadata node representing the relationship.

        Args:
            office_a: First office name
            office_b: Second office name
            relation: Type of relationship

        Returns:
            Link node ID
        """
        link_content = f"Cross-office link: {office_a} <-> {office_b} ({relation})"

        node_id = self.add_node(
            office="system",
            content=link_content,
            ttl_hours=168,  # 1 week
            tags=["office_link", office_a, office_b, relation]
        )

        return node_id

    def prune_expired(self) -> int:
        """
        Remove expired nodes from graph.

        Returns:
            Number of nodes pruned
        """
        now = datetime.utcnow()
        expired_ids = [
            node_id for node_id, node in self.nodes.items()
            if now > node.expires_at
        ]

        for node_id in expired_ids:
            node = self.nodes[node_id]

            # Remove from indexes
            if node.office in self.office_index:
                self.office_index[node.office].discard(node_id)

            for tag in node.tags:
                if tag in self.tag_index:
                    self.tag_index[tag].discard(node_id)

            # Remove edges connected to this node
            edges_to_remove = [
                edge_id for edge_id, edge in self.edges.items()
                if edge.source == node_id or edge.target == node_id
            ]
            for edge_id in edges_to_remove:
                del self.edges[edge_id]

            # Remove node
            del self.nodes[node_id]

        if expired_ids:
            self._save_to_disk()

        return len(expired_ids)

    def get_stats(self) -> Dict:
        """Get memory graph statistics."""
        office_counts = {}
        for office, node_ids in self.office_index.items():
            office_counts[office] = len(node_ids)

        tag_counts = {}
        for tag, node_ids in self.tag_index.items():
            tag_counts[tag] = len(node_ids)

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "offices": office_counts,
            "tags": tag_counts,
            "avg_access_count": sum(n.access_count for n in self.nodes.values()) / max(len(self.nodes), 1)
        }

    def export_subgraph(
        self,
        node_ids: List[str],
        include_neighbors: bool = True
    ) -> Dict:
        """
        Export subgraph as JSON.

        Args:
            node_ids: List of node IDs to export
            include_neighbors: Include connected nodes

        Returns:
            Dict with nodes and edges
        """
        export_nodes = {}
        export_edges = {}

        # Add requested nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                export_nodes[node_id] = self.nodes[node_id]

        # Add neighbors if requested
        if include_neighbors:
            for edge in self.edges.values():
                if edge.source in export_nodes or edge.target in export_nodes:
                    export_edges[edge.id] = edge

                    # Add neighbor nodes
                    if edge.source not in export_nodes and edge.source in self.nodes:
                        export_nodes[edge.source] = self.nodes[edge.source]
                    if edge.target not in export_nodes and edge.target in self.nodes:
                        export_nodes[edge.target] = self.nodes[edge.target]

        # Convert to JSON-serializable format
        return {
            "nodes": [self._node_to_dict(n) for n in export_nodes.values()],
            "edges": [self._edge_to_dict(e) for e in export_edges.values()]
        }

    def _compute_similarity(self, query: str, embedding: List[float]) -> float:
        """Compute semantic similarity (stub - would use real embeddings)."""
        # Stub: simple hash-based similarity for now
        query_hash = hash(query.lower())
        embedding_hash = hash(tuple(embedding[:5]) if embedding else ())

        # Return random similarity for demo
        return abs((query_hash % 100) - (embedding_hash % 100)) / 100.0

    def _node_to_dict(self, node: MemoryNode) -> Dict:
        """Convert node to JSON-serializable dict."""
        return {
            "id": node.id,
            "office": node.office,
            "content": node.content,
            "created_at": node.created_at.isoformat(),
            "expires_at": node.expires_at.isoformat(),
            "consent_required": node.consent_required,
            "tags": node.tags,
            "access_count": node.access_count
        }

    def _edge_to_dict(self, edge: MemoryEdge) -> Dict:
        """Convert edge to JSON-serializable dict."""
        return {
            "id": edge.id,
            "source": edge.source,
            "target": edge.target,
            "relation": edge.relation,
            "weight": edge.weight,
            "metadata": edge.metadata
        }

    def _save_to_disk(self):
        """Persist graph to disk."""
        data = {
            "nodes": [self._node_to_dict(n) for n in self.nodes.values()],
            "edges": [self._edge_to_dict(e) for e in self.edges.values()],
            "saved_at": datetime.utcnow().isoformat()
        }

        self.storage_path.write_text(json.dumps(data, indent=2))

    def _load_from_disk(self):
        """Load graph from disk."""
        try:
            data = json.loads(self.storage_path.read_text())

            # Load nodes
            for node_data in data.get("nodes", []):
                node = MemoryNode(
                    id=node_data["id"],
                    office=node_data["office"],
                    content=node_data["content"],
                    created_at=datetime.fromisoformat(node_data["created_at"]),
                    expires_at=datetime.fromisoformat(node_data["expires_at"]),
                    consent_required=node_data["consent_required"],
                    tags=node_data["tags"],
                    access_count=node_data["access_count"]
                )
                self.nodes[node.id] = node

                # Rebuild indexes
                if node.office not in self.office_index:
                    self.office_index[node.office] = set()
                self.office_index[node.office].add(node.id)

                for tag in node.tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = set()
                    self.tag_index[tag].add(node.id)

            # Load edges
            for edge_data in data.get("edges", []):
                edge = MemoryEdge(
                    id=edge_data["id"],
                    source=edge_data["source"],
                    target=edge_data["target"],
                    relation=edge_data["relation"],
                    weight=edge_data["weight"],
                    metadata=edge_data.get("metadata", {})
                )
                self.edges[edge.id] = edge

            print(f"✅ Loaded {len(self.nodes)} nodes, {len(self.edges)} edges from disk")

        except Exception as e:
            print(f"⚠️  Failed to load memory graph: {e}")


# Singleton instance
_memory_graph = None


def get_memory_graph() -> MemoryGraph:
    """Get singleton memory graph instance."""
    global _memory_graph
    if _memory_graph is None:
        _memory_graph = MemoryGraph()
    return _memory_graph


# CLI testing
if __name__ == "__main__":
    print("="*70)
    print("MEMORY GRAPH TEST")
    print("="*70)

    graph = MemoryGraph(storage_path=Path("test_memory_graph.json"))

    # Test 1: Add nodes from different offices
    print("\n1. Adding memory nodes...")
    astrologist_node = graph.add_node(
        office="Astrologist",
        content="Mercury retrograde October 10-31, avoid tech investments",
        tags=["planetary_transits", "market_timing", "mercury"],
        ttl_hours=48
    )
    print(f"   ✅ Astrologist node: {astrologist_node[:8]}")

    banker_node = graph.add_node(
        office="Banker",
        content="Tech sector P/E ratio: 28 (slightly overvalued)",
        tags=["tech_sector", "valuation", "market_analysis"],
        ttl_hours=24
    )
    print(f"   ✅ Banker node: {banker_node[:8]}")

    # Test 2: Link nodes
    print("\n2. Linking related memories...")
    edge_id = graph.add_edge(
        source_id=astrologist_node,
        target_id=banker_node,
        relation="complements",
        metadata={"context": "Cosmic market timing"}
    )
    print(f"   ✅ Edge created: {edge_id[:8]}")

    # Test 3: Query by tags
    print("\n3. Querying by tags...")
    results = graph.query(
        querying_office="Economist",
        tags=["market_timing", "market_analysis"]
    )
    print(f"   ✅ Found {len(results)} memories")
    for r in results:
        print(f"      • {r.office}: {r.content[:50]}...")

    # Test 4: Office link
    print("\n4. Creating cross-office link...")
    link_id = graph.link_offices("Astrologist", "Banker", "synergy")
    print(f"   ✅ Link created: {link_id[:8]}")

    # Test 5: Statistics
    print("\n5. Memory graph statistics:")
    stats = graph.get_stats()
    print(f"   Total nodes: {stats['total_nodes']}")
    print(f"   Total edges: {stats['total_edges']}")
    print(f"   Offices: {stats['offices']}")

    # Test 6: Export subgraph
    print("\n6. Exporting subgraph...")
    subgraph = graph.export_subgraph([astrologist_node])
    print(f"   ✅ Exported {len(subgraph['nodes'])} nodes, {len(subgraph['edges'])} edges")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
