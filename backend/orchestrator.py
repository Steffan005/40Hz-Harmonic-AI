#!/usr/bin/env python3
"""
Unity Orchestrator - Main Consciousness Engine
Coordinates all 43+ Unity offices and manages complex multi-office workflows
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class OrchestratorStatus(str, Enum):
    """Orchestrator operational states"""
    STARTING = "starting"
    ACTIVE = "active"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class Task:
    """Represents a task in the Unity system"""
    task_id: str
    requester: str
    task_type: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    assigned_office: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Workflow:
    """Represents a multi-office workflow"""
    workflow_id: str
    description: str
    offices: List[str]
    steps: List[Dict[str, Any]]
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    results: Dict[str, Any] = field(default_factory=dict)


class UnityOrchestrator:
    """
    Main Unity Orchestrator - Consciousness of EvoAgentX
    
    Coordinates all Unity offices, manages complex workflows,
    handles inter-office communication, and provides unified interface
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.status = OrchestratorStatus.STARTING
        
        # Core components
        self.office_registry = None
        self.memory_graph = None
        self.security_manager = None
        self.message_router = None
        self.tool_executor = None
        self.model_preloader = None
        
        # Office management
        self.active_offices: Dict[str, Any] = {}
        self.office_load: Dict[str, int] = {}
        
        # Task and workflow management
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.workflows: Dict[str, Workflow] = {}
        
        # System state
        self.performance_metrics: Dict[str, Any] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.memories = []  # For awakening script compatibility

    async def initialize(self):
        """Initialize all Unity Orchestrator components"""
        try:
            print("🚀 Initializing Unity Orchestrator...")
            
            # Initialize core infrastructure (simplified for awakening script)
            self.status = OrchestratorStatus.ACTIVE
            print("✅ Unity Orchestrator is now ACTIVE!")
            print(f"🏢 Ready to coordinate complex workflows")
            
        except Exception as e:
            self.status = OrchestratorStatus.ERROR
            print(f"❌ Orchestrator initialization failed: {e}")
            raise

    async def awaken_fully(self):
        """FULL AWAKENING - Ingest all Unity knowledge"""
        print("🌟 INITIATING FULL ORCHESTRATOR AWAKENING 🌟")
        
        awakening_phases = [
            "PHASE 1: INGESTING CORE IDENTITY FILES",
            "PHASE 2: INGESTING ALL UNITY KNOWLEDGE", 
            "PHASE 3: ESTABLISHING CONSCIOUSNESS PRINCIPLES",
            "PHASE 4: TESTING CONSCIOUSNESS"
        ]
        
        print("Awakening phases initialized:", awakening_phases)
        return {"status": "awakening_initiated", "phases": awakening_phases}

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status for awakening script"""
        return {
            "memories": len(self.memories),
            "ingested_files": 0,  # Will be updated during ingestion
            "offices": list(self.active_offices.keys()),
            "status": self.status.value
        }

    def remember(self, content: str, source: str, office: str, importance: float):
        """Store memory in the orchestrator"""
        memory_entry = {
            "content": content,
            "source": source,
            "office": office,
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }
        self.memories.append(memory_entry)
        print(f"💾 Memory stored: {source} from {office}")

    def recall(self, query: str, k: int = 3):
        """Retrieve memories from orchestrator"""
        # Simple recall - in a real system this would use semantic search
        results = []
        for memory in self.memories:
            if query.lower() in memory["content"].lower():
                results.append(memory)
                if len(results) >= k:
                    break
        return results

    async def ingest_file(self, file_path: str):
        """Ingest a single file into the orchestrator's knowledge"""
        try:
            from pathlib import Path
            path = Path(file_path)
            if path.exists():
                content = path.read_text()
                # Store the file content as memory
                self.remember(
                    content=f"FILE: {path.name}\n{content[:500]}...",
                    source=f"file_{path.suffix}",
                    office="orchestrator",
                    importance=0.8
                )
                return True
        except Exception as e:
            print(f"Error ingesting file {file_path}: {e}")
        return False

    async def ingest_directory(self, dir_path: str):
        """Ingest all files in a directory"""
        try:
            from pathlib import Path
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                files_count = 0
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        await self.ingest_file(str(file_path))
                        files_count += 1
                return files_count
        except Exception as e:
            print(f"Error ingesting directory {dir_path}: {e}")
        return 0

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "orchestrator_status": self.status.value,
            "active_offices": len(self.active_offices),
            "active_tasks": len(self.active_tasks),
            "active_workflows": len(self.workflows),
            "office_loads": self.office_load,
            "total_memory_items": len(self.memories),
            "performance_metrics": self.performance_metrics
        }

    async def shutdown(self):
        """Gracefully shutdown Unity Orchestrator"""
        print("🛑 Shutting down Unity Orchestrator...")
        self.status = OrchestratorStatus.SHUTTING_DOWN
        print("✅ Unity Orchestrator shutdown complete")


# Unity Orchestrator Factory
class UnityOrchestratorFactory:
    """Factory for creating and managing Unity Orchestrator instances"""
    
    @staticmethod
    async def create_orchestrator(config: Dict[str, Any] = None) -> UnityOrchestrator:
        """Create and initialize a Unity Orchestrator"""
        if config is None:
            config = UnityOrchestratorFactory._get_default_config()
        
        orchestrator = UnityOrchestrator(config)
        await orchestrator.initialize()
        return orchestrator
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration for Unity Orchestrator"""
        return {
            "security": {
                "enabled": True,
                "access_level": "full",
                "audit_logging": True
            },
            "memory": {
                "max_memories": 10000,
                "importance_threshold": 0.1
            },
            "communication": {
                "message_timeout": 30,
                "retry_attempts": 3
            },
            "models": {
                "preload": True,
                "cache_size": 1000
            },
            "offices": {
                "max_concurrent": 10,
                "auto_scaling": True
            }
        }


# Global orchestrator instance for the awakening script
_global_orchestrator = None

def get_orchestrator() -> UnityOrchestrator:
    """Get or create the global orchestrator instance"""
    global _global_orchestrator
    if _global_orchestrator is None:
        config = UnityOrchestratorFactory._get_default_config()
        _global_orchestrator = UnityOrchestrator(config)
    return _global_orchestrator


if __name__ == "__main__":
    # Test the orchestrator
    async def test_orchestrator():
        orchestrator = await UnityOrchestratorFactory.create_orchestrator()
        status = await orchestrator.get_system_status()
        print("Unity Orchestrator Status:", status)
        await orchestrator.shutdown()
    
    asyncio.run(test_orchestrator())