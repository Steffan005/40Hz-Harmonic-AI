"""
Unity Shared Memory Graph with TTL and Consent Management
Implements a distributed memory system with time-to-live and consent flags
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import chromadb
import lancedb
import numpy as np
import redis.asyncio as redis
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memory nodes in the system"""
    KNOWLEDGE = "knowledge"
    EXPERIENCE = "experience"
    SKILL = "skill"
    RELATIONSHIP = "relationship"
    DECISION = "decision"
    STRATEGY = "strategy"
    EMOTION = "emotion"
    CONTEXT = "context"


class ConsentLevel(str, Enum):
    """Memory sharing consent levels"""
    PRIVATE = "private"  # Only accessible to originating office
    RESTRICTED = "restricted"  # Requires explicit permission
    SHARED = "shared"  # Available to all offices with consent
    PUBLIC = "public"  # Freely accessible to all offices


@dataclass
class MemoryNode:
    """Represents a single memory node in the graph"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: MemoryType = MemoryType.KNOWLEDGE
    title: str = ""
    content: str = ""
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    office_id: str = ""
    consent_level: ConsentLevel = ConsentLevel.RESTRICTED
    ttl_seconds: int = 3600  # Default 1 hour
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    connections: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)


class MemoryGraphConfig(BaseModel):
    """Configuration for the memory graph system"""
    chroma_path: str = "./chroma_db"
    lance_path: str = "./lance_db"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    default_ttl: int = 3600
    max_connections: int = 100
    embedding_model: str = "all-MiniLM-L6-v2"
    cleanup_interval: int = 60  # Cleanup expired memories every minute


class SharedMemoryGraph:
    """
    Distributed memory graph with TTL and consent management
    Uses Chroma for vector storage, LanceDB for persistence, Redis for pub/sub
    """

    def __init__(self, config: MemoryGraphConfig):
        self.config = config
        self.nodes: Dict[str, MemoryNode] = {}
        self.office_permissions: Dict[str, Set[str]] = {}
        self.chroma_client = None
        self.lance_db = None
        self.redis_client = None
        self.collection = None
        self.cleanup_task = None
        self._initialized = False

    async def initialize(self):
        """Initialize all backend connections"""
        if self._initialized:
            return

        # Initialize Chroma
        self.chroma_client = chromadb.PersistentClient(path=self.config.chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="unity_memories",
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize LanceDB
        self.lance_db = lancedb.connect(self.config.lance_path)

        # Create table if not exists
        if "memories" not in self.lance_db.table_names():
            self.lance_table = self.lance_db.create_table(
                "memories",
                data=[{
                    "id": "init",
                    "vector": np.zeros(384).tolist(),  # MiniLM embedding size
                    "title": "",
                    "content": "",
                    "metadata": {}
                }]
            )
        else:
            self.lance_table = self.lance_db.open_table("memories")

        # Initialize Redis
        self.redis_client = await redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            decode_responses=True
        )

        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_memories())

        self._initialized = True
        print(f"✅ Shared Memory Graph initialized")

    async def create_memory(
        self,
        office_id: str,
        title: str,
        content: str,
        memory_type: MemoryType = MemoryType.KNOWLEDGE,
        consent_level: ConsentLevel = ConsentLevel.RESTRICTED,
        ttl_seconds: Optional[int] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> MemoryNode:
        """Create a new memory node with consent and TTL"""

        # Create memory node
        node = MemoryNode(
            type=memory_type,
            title=title,
            content=content,
            office_id=office_id,
            consent_level=consent_level,
            ttl_seconds=ttl_seconds or self.config.default_ttl,
            tags=tags or [],
            metadata=metadata or {}
        )

        # Generate embedding
        node.embedding = await self._generate_embedding(content)

        # Store in memory
        self.nodes[node.id] = node

        # Store in Chroma
        self.collection.add(
            ids=[node.id],
            embeddings=[node.embedding.tolist()],
            metadatas=[{
                "office_id": office_id,
                "type": memory_type.value,
                "consent_level": consent_level.value,
                "created_at": node.created_at,
                "ttl_seconds": node.ttl_seconds
            }],
            documents=[content]
        )

        # Store in LanceDB for persistence
        await self._persist_to_lance(node)

        # Publish creation event
        await self._publish_event("memory_created", {
            "id": node.id,
            "office_id": office_id,
            "type": memory_type.value,
            "consent_level": consent_level.value
        })

        return node

    async def get_memory(
        self,
        memory_id: str,
        requesting_office: str
    ) -> Optional[MemoryNode]:
        """Get a memory node with consent checking"""

        node = self.nodes.get(memory_id)
        if not node:
            # Try to load from persistent storage
            node = await self._load_from_lance(memory_id)
            if not node:
                return None

        # Check if memory has expired
        if self._is_expired(node):
            await self.delete_memory(memory_id)
            return None

        # Check consent
        if not self._has_access(node, requesting_office):
            return None

        # Update access metadata
        node.accessed_at = time.time()
        node.access_count += 1

        return node

    async def search_memories(
        self,
        query: str,
        requesting_office: str,
        limit: int = 10,
        memory_type: Optional[MemoryType] = None,
        min_consent: ConsentLevel = ConsentLevel.PUBLIC
    ) -> List[MemoryNode]:
        """Search memories with consent filtering"""

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=limit * 2,  # Get more to filter by consent
            where={"type": memory_type.value} if memory_type else None
        )

        # Filter by consent and build memory nodes
        memories = []
        for idx, memory_id in enumerate(results['ids'][0]):
            node = await self.get_memory(memory_id, requesting_office)
            if node and self._meets_consent_requirement(node, min_consent):
                memories.append(node)
                if len(memories) >= limit:
                    break

        return memories

    async def connect_memories(
        self,
        memory_id1: str,
        memory_id2: str,
        requesting_office: str
    ) -> bool:
        """Create a connection between two memories"""

        # Get both memories with consent check
        node1 = await self.get_memory(memory_id1, requesting_office)
        node2 = await self.get_memory(memory_id2, requesting_office)

        if not node1 or not node2:
            return False

        # Check if requesting office can modify
        if node1.office_id != requesting_office and node2.office_id != requesting_office:
            return False

        # Create bidirectional connection
        node1.connections.add(memory_id2)
        node2.connections.add(memory_id1)

        # Publish connection event
        await self._publish_event("memories_connected", {
            "memory_id1": memory_id1,
            "memory_id2": memory_id2,
            "office_id": requesting_office
        })

        return True

    async def update_consent(
        self,
        memory_id: str,
        new_consent: ConsentLevel,
        requesting_office: str
    ) -> bool:
        """Update consent level for a memory"""

        node = self.nodes.get(memory_id)
        if not node:
            return False

        # Only the owning office can change consent
        if node.office_id != requesting_office:
            return False

        old_consent = node.consent_level
        node.consent_level = new_consent

        # Update in Chroma
        self.collection.update(
            ids=[memory_id],
            metadatas=[{"consent_level": new_consent.value}]
        )

        # Publish consent change event
        await self._publish_event("consent_updated", {
            "memory_id": memory_id,
            "old_consent": old_consent.value,
            "new_consent": new_consent.value,
            "office_id": requesting_office
        })

        return True

    async def update_ttl(
        self,
        memory_id: str,
        new_ttl: int,
        requesting_office: str
    ) -> bool:
        """Update TTL for a memory"""

        node = self.nodes.get(memory_id)
        if not node:
            return False

        # Only the owning office can change TTL
        if node.office_id != requesting_office:
            return False

        node.ttl_seconds = new_ttl

        # Update in Chroma
        self.collection.update(
            ids=[memory_id],
            metadatas=[{"ttl_seconds": new_ttl}]
        )

        return True

    async def delete_memory(
        self,
        memory_id: str,
        force: bool = False
    ) -> bool:
        """Delete a memory from the graph"""

        if memory_id not in self.nodes and not force:
            return False

        # Remove from all stores
        self.nodes.pop(memory_id, None)
        self.collection.delete(ids=[memory_id])

        # Publish deletion event
        await self._publish_event("memory_deleted", {
            "memory_id": memory_id
        })

        return True

    async def grant_office_access(
        self,
        granting_office: str,
        receiving_office: str,
        memory_ids: List[str]
    ) -> int:
        """Grant another office access to specific memories"""

        granted_count = 0
        for memory_id in memory_ids:
            node = self.nodes.get(memory_id)
            if node and node.office_id == granting_office:
                # Add to permissions
                if receiving_office not in self.office_permissions:
                    self.office_permissions[receiving_office] = set()
                self.office_permissions[receiving_office].add(memory_id)
                granted_count += 1

        # Publish permission grant event
        await self._publish_event("access_granted", {
            "granting_office": granting_office,
            "receiving_office": receiving_office,
            "memory_count": granted_count
        })

        return granted_count

    async def get_office_memories(
        self,
        office_id: str,
        include_shared: bool = True
    ) -> List[MemoryNode]:
        """Get all memories for a specific office"""

        memories = []
        for node in self.nodes.values():
            if node.office_id == office_id:
                memories.append(node)
            elif include_shared and self._has_access(node, office_id):
                memories.append(node)

        return memories

    async def get_memory_graph(
        self,
        center_memory_id: str,
        depth: int = 2,
        requesting_office: str = None
    ) -> Dict[str, Any]:
        """Get a subgraph centered on a memory"""

        visited = set()
        graph = {
            "nodes": [],
            "edges": []
        }

        async def traverse(memory_id: str, current_depth: int):
            if current_depth > depth or memory_id in visited:
                return

            visited.add(memory_id)
            node = await self.get_memory(memory_id, requesting_office)

            if not node:
                return

            # Add node to graph
            graph["nodes"].append({
                "id": node.id,
                "title": node.title,
                "type": node.type.value,
                "office_id": node.office_id,
                "consent_level": node.consent_level.value
            })

            # Traverse connections
            for connected_id in node.connections:
                graph["edges"].append({
                    "source": memory_id,
                    "target": connected_id
                })
                await traverse(connected_id, current_depth + 1)

        await traverse(center_memory_id, 0)
        return graph

    # Internal helper methods

    def _is_expired(self, node: MemoryNode) -> bool:
        """Check if a memory has expired"""
        age = time.time() - node.created_at
        return age > node.ttl_seconds

    def _has_access(self, node: MemoryNode, requesting_office: str) -> bool:
        """Check if an office has access to a memory"""
        # Owner always has access
        if node.office_id == requesting_office:
            return True

        # Check consent level
        if node.consent_level == ConsentLevel.PUBLIC:
            return True
        elif node.consent_level == ConsentLevel.SHARED:
            return True
        elif node.consent_level == ConsentLevel.RESTRICTED:
            # Check explicit permissions
            return node.id in self.office_permissions.get(requesting_office, set())
        else:  # PRIVATE
            return False

    def _meets_consent_requirement(
        self,
        node: MemoryNode,
        min_consent: ConsentLevel
    ) -> bool:
        """Check if a memory meets minimum consent requirement"""
        consent_hierarchy = {
            ConsentLevel.PUBLIC: 0,
            ConsentLevel.SHARED: 1,
            ConsentLevel.RESTRICTED: 2,
            ConsentLevel.PRIVATE: 3
        }
        return consent_hierarchy[node.consent_level] <= consent_hierarchy[min_consent]

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        # TODO: Implement actual embedding generation
        # For now, return random embedding
        return np.random.randn(384)

    async def _persist_to_lance(self, node: MemoryNode):
        """Persist memory to LanceDB"""
        data = {
            "id": node.id,
            "vector": node.embedding.tolist() if node.embedding is not None else [],
            "title": node.title,
            "content": node.content,
            "metadata": json.dumps({
                "office_id": node.office_id,
                "type": node.type.value,
                "consent_level": node.consent_level.value,
                "ttl_seconds": node.ttl_seconds,
                "created_at": node.created_at,
                "tags": node.tags
            })
        }
        # Append to LanceDB table
        self.lance_table.add([data])

    async def _load_from_lance(self, memory_id: str) -> Optional[MemoryNode]:
        """Load memory from LanceDB"""
        try:
            result = self.lance_table.search().where(f"id = '{memory_id}'").limit(1).to_list()
            if result:
                data = result[0]
                metadata = json.loads(data["metadata"])
                node = MemoryNode(
                    id=data["id"],
                    title=data["title"],
                    content=data["content"],
                    type=MemoryType(metadata["type"]),
                    office_id=metadata["office_id"],
                    consent_level=ConsentLevel(metadata["consent_level"]),
                    ttl_seconds=metadata["ttl_seconds"],
                    created_at=metadata["created_at"],
                    tags=metadata.get("tags", []),
                    embedding=np.array(data["vector"])
                )
                self.nodes[memory_id] = node
                return node
        except Exception as e:
            print(f"Error loading memory from Lance: {e}")
        return None

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to Redis pub/sub"""
        if self.redis_client:
            channel = f"unity:memory:{event_type}"
            message = json.dumps({
                "event_type": event_type,
                "timestamp": time.time(),
                "data": data
            })
            await self.redis_client.publish(channel, message)

    async def _cleanup_expired_memories(self):
        """Background task to clean up expired memories"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)

                expired_ids = []
                for memory_id, node in list(self.nodes.items()):
                    if self._is_expired(node):
                        expired_ids.append(memory_id)

                for memory_id in expired_ids:
                    await self.delete_memory(memory_id, force=True)

                if expired_ids:
                    print(f"🗑️ Cleaned up {len(expired_ids)} expired memories")

            except Exception as e:
                print(f"Error in cleanup task: {e}")

    async def close(self):
        """Clean up connections"""
        if self.cleanup_task:
            self.cleanup_task.cancel()

        if self.redis_client:
            await self.redis_client.close()


# Federation manager for multi-office memory coordination
class MemoryFederation:
    """Manages memory federation across all Unity offices"""

    def __init__(self):
        self.memory_graphs: Dict[str, SharedMemoryGraph] = {}
        self.office_registry: Dict[str, Dict[str, Any]] = {}

    async def register_office(
        self,
        office_id: str,
        office_type: str,
        capabilities: List[str],
        memory_config: Optional[MemoryGraphConfig] = None
    ):
        """Register a new office in the federation"""

        # Create dedicated memory graph for office
        config = memory_config or MemoryGraphConfig()
        memory_graph = SharedMemoryGraph(config)
        await memory_graph.initialize()

        self.memory_graphs[office_id] = memory_graph
        self.office_registry[office_id] = {
            "type": office_type,
            "capabilities": capabilities,
            "registered_at": time.time()
        }

        print(f"📝 Office registered: {office_id} ({office_type})")

    async def federated_search(
        self,
        query: str,
        requesting_office: str,
        target_offices: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Tuple[str, MemoryNode]]:
        """Search across multiple office memory graphs"""

        results = []
        offices_to_search = target_offices or list(self.memory_graphs.keys())

        # Search each office's memory graph
        tasks = []
        for office_id in offices_to_search:
            if office_id in self.memory_graphs:
                graph = self.memory_graphs[office_id]
                tasks.append(graph.search_memories(
                    query,
                    requesting_office,
                    limit=limit
                ))

        # Gather results
        office_results = await asyncio.gather(*tasks)

        # Combine and rank results
        for office_id, memories in zip(offices_to_search, office_results):
            for memory in memories:
                results.append((office_id, memory))

        # Sort by relevance (simplified - could use embedding similarity)
        results.sort(key=lambda x: x[1].access_count, reverse=True)

        return results[:limit]

    async def cross_office_memory_share(
        self,
        source_office: str,
        target_office: str,
        memory_id: str,
        consent_level: ConsentLevel = ConsentLevel.SHARED
    ) -> bool:
        """Share a memory from one office to another"""

        if source_office not in self.memory_graphs or target_office not in self.memory_graphs:
            return False

        source_graph = self.memory_graphs[source_office]
        target_graph = self.memory_graphs[target_office]

        # Get the memory from source
        memory = await source_graph.get_memory(memory_id, source_office)
        if not memory:
            return False

        # Create a copy in target office with appropriate consent
        await target_graph.create_memory(
            office_id=target_office,
            title=f"[Shared from {source_office}] {memory.title}",
            content=memory.content,
            memory_type=memory.type,
            consent_level=consent_level,
            ttl_seconds=memory.ttl_seconds,
            tags=memory.tags + [f"shared_from:{source_office}"],
            metadata={
                **memory.metadata,
                "original_office": source_office,
                "original_memory_id": memory_id
            }
        )

        return True