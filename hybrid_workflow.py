#!/usr/bin/env python3
"""
Hybrid Workflow Engine — Multi-Office Collaboration Orchestration

Enables coordinated workflows across multiple offices with sequential, parallel,
and graph-based execution patterns.

Features:
- Workflow templates (Cosmic Market Timing, Ethical Analysis, Holistic Health)
- Sequential, parallel, and graph-based coordination
- Context passing via memory graph
- Result aggregation and synthesis
- Workflow status tracking
"""

import uuid
import time
import json
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import asyncio


class WorkflowMode(Enum):
    """Workflow execution modes."""
    SEQUENTIAL = "sequential"  # A → B → C
    PARALLEL = "parallel"      # A, B, C simultaneously
    GRAPH = "graph"            # Custom DAG with dependencies


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowTask:
    """Single task in a workflow."""
    id: str
    office: str           # Which office executes this
    action: str           # What to do (e.g., "analyze_trends", "generate_insights")
    input_context: Dict   # Input data/context
    dependencies: List[str] = None  # Task IDs this depends on
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class WorkflowDefinition:
    """Complete workflow specification."""
    id: str
    name: str
    description: str
    mode: WorkflowMode
    tasks: List[WorkflowTask]
    synthesis_office: Optional[str] = None  # Office that synthesizes final result
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class HybridWorkflowEngine:
    """
    Orchestrates multi-office collaboration workflows.

    Architecture:
    1. Define workflow (tasks, dependencies, execution mode)
    2. Execute workflow (run tasks according to mode)
    3. Aggregate results (synthesize outputs from all offices)
    4. Store in memory graph (for future retrieval)
    """

    def __init__(self, memory_graph=None, storage_path: Path = None):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.execution_log: List[Dict] = []
        self.memory_graph = memory_graph
        self.storage_path = storage_path or Path("data/workflow_history.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Task executor registry (office -> executor function)
        self.executors: Dict[str, Callable] = {}

    def register_executor(self, office: str, executor: Callable):
        """Register task executor for an office."""
        self.executors[office] = executor

    def create_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Dict],
        mode: WorkflowMode = WorkflowMode.SEQUENTIAL,
        synthesis_office: str = None
    ) -> str:
        """
        Create new workflow definition.

        Args:
            name: Workflow name
            description: What this workflow does
            tasks: List of task dicts with office, action, input_context
            mode: Execution mode (sequential/parallel/graph)
            synthesis_office: Office that synthesizes final result

        Returns:
            Workflow ID (UUID)
        """
        workflow_id = str(uuid.uuid4())

        # Convert task dicts to WorkflowTask objects
        workflow_tasks = []
        for task_data in tasks:
            task = WorkflowTask(
                id=str(uuid.uuid4()),
                office=task_data.get("office"),
                action=task_data.get("action"),
                input_context=task_data.get("input_context", {}),
                dependencies=task_data.get("dependencies", [])
            )
            workflow_tasks.append(task)

        workflow = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            mode=mode,
            tasks=workflow_tasks,
            synthesis_office=synthesis_office
        )

        self.workflows[workflow_id] = workflow
        return workflow_id

    async def execute_workflow(self, workflow_id: str) -> Dict:
        """
        Execute workflow according to its mode.

        Args:
            workflow_id: Workflow to execute

        Returns:
            Execution result with all task outputs
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"EXECUTING WORKFLOW: {workflow.name}")
        print(f"Mode: {workflow.mode.value}")
        print(f"Tasks: {len(workflow.tasks)}")
        print(f"{'='*70}\n")

        # Execute according to mode
        if workflow.mode == WorkflowMode.SEQUENTIAL:
            results = await self._execute_sequential(workflow)
        elif workflow.mode == WorkflowMode.PARALLEL:
            results = await self._execute_parallel(workflow)
        elif workflow.mode == WorkflowMode.GRAPH:
            results = await self._execute_graph(workflow)
        else:
            raise ValueError(f"Unknown workflow mode: {workflow.mode}")

        execution_time = time.time() - start_time

        # Synthesize results if synthesis office specified
        final_result = None
        if workflow.synthesis_office:
            final_result = await self._synthesize_results(
                workflow.synthesis_office,
                results,
                workflow
            )

        # Log execution
        log_entry = {
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat(),
            "task_count": len(workflow.tasks),
            "successful_tasks": sum(1 for r in results if r.get("status") == "completed"),
            "failed_tasks": sum(1 for r in results if r.get("status") == "failed"),
            "final_result": final_result
        }
        self.execution_log.append(log_entry)
        self._save_to_disk()

        # Store in memory graph if available
        if self.memory_graph and final_result:
            self.memory_graph.add_node(
                office="system",
                content=f"Workflow '{workflow.name}' result: {final_result.get('synthesis', '')}",
                tags=["workflow", workflow.name] + [t.office for t in workflow.tasks],
                ttl_hours=48
            )

        print(f"\n{'='*70}")
        print(f"WORKFLOW COMPLETE: {workflow.name}")
        print(f"Time: {execution_time:.2f}s")
        print(f"Success: {log_entry['successful_tasks']}/{log_entry['task_count']}")
        print(f"{'='*70}\n")

        return {
            "workflow_id": workflow_id,
            "execution_time": execution_time,
            "task_results": results,
            "final_result": final_result,
            "status": "completed" if log_entry['failed_tasks'] == 0 else "partial"
        }

    async def _execute_sequential(self, workflow: WorkflowDefinition) -> List[Dict]:
        """Execute tasks sequentially (A → B → C)."""
        results = []
        context = {}  # Accumulated context from previous tasks

        for task in workflow.tasks:
            print(f"  → {task.office}: {task.action}")

            # Merge previous context with task input
            task.input_context.update(context)

            result = await self._execute_task(task)
            results.append(result)

            # Add result to context for next task
            if result.get("status") == "completed":
                context[f"{task.office}_result"] = result.get("output", {})
            else:
                # Stop on failure in sequential mode
                print(f"    ❌ Task failed, stopping workflow")
                break

        return results

    async def _execute_parallel(self, workflow: WorkflowDefinition) -> List[Dict]:
        """Execute all tasks in parallel."""
        print(f"  → Launching {len(workflow.tasks)} tasks in parallel...")

        tasks = [self._execute_task(task) for task in workflow.tasks]
        results = await asyncio.gather(*tasks)

        return list(results)

    async def _execute_graph(self, workflow: WorkflowDefinition) -> List[Dict]:
        """Execute tasks according to dependency graph."""
        results = {}
        completed = set()
        context = {}

        # Build dependency map
        task_map = {task.id: task for task in workflow.tasks}

        # Execute in topological order
        while len(completed) < len(workflow.tasks):
            # Find ready tasks (all dependencies completed)
            ready_tasks = []
            for task in workflow.tasks:
                if task.id in completed:
                    continue

                deps_met = all(dep_id in completed for dep_id in task.dependencies)
                if deps_met:
                    ready_tasks.append(task)

            if not ready_tasks:
                # Circular dependency or all remaining tasks failed
                print("  ⚠️  No more tasks ready to execute (circular dependency?)")
                break

            # Execute ready tasks in parallel
            print(f"  → Executing {len(ready_tasks)} ready tasks...")

            for task in ready_tasks:
                # Merge context from dependencies
                for dep_id in task.dependencies:
                    if dep_id in results and results[dep_id].get("status") == "completed":
                        dep_office = task_map[dep_id].office
                        task.input_context[f"{dep_office}_result"] = results[dep_id].get("output", {})

            task_futures = [self._execute_task(task) for task in ready_tasks]
            task_results = await asyncio.gather(*task_futures)

            # Mark as completed
            for task, result in zip(ready_tasks, task_results):
                results[task.id] = result
                completed.add(task.id)

                if result.get("status") == "completed":
                    context[f"{task.office}_result"] = result.get("output", {})

        # Convert to list
        return [results[task.id] for task in workflow.tasks if task.id in results]

    async def _execute_task(self, task: WorkflowTask) -> Dict:
        """Execute single task."""
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()

        try:
            # Check if executor registered
            if task.office in self.executors:
                # Call registered executor
                output = await self.executors[task.office](task.action, task.input_context)
            else:
                # Stub executor (returns mock data)
                output = {
                    "message": f"[STUB] {task.office} executed {task.action}",
                    "input_received": list(task.input_context.keys()),
                    "timestamp": datetime.utcnow().isoformat()
                }
                await asyncio.sleep(0.5)  # Simulate work

            task.status = TaskStatus.COMPLETED
            task.result = output
            task.end_time = time.time()

            return {
                "task_id": task.id,
                "office": task.office,
                "action": task.action,
                "status": "completed",
                "output": output,
                "execution_time": task.end_time - task.start_time
            }

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.end_time = time.time()

            return {
                "task_id": task.id,
                "office": task.office,
                "action": task.action,
                "status": "failed",
                "error": str(e),
                "execution_time": task.end_time - task.start_time
            }

    async def _synthesize_results(
        self,
        synthesis_office: str,
        task_results: List[Dict],
        workflow: WorkflowDefinition
    ) -> Dict:
        """Synthesize results from all tasks."""
        print(f"\n  → Synthesizing results with {synthesis_office}...")

        # Aggregate all outputs
        aggregated_data = {
            "workflow_name": workflow.name,
            "task_outputs": {},
            "successful_tasks": [],
            "failed_tasks": []
        }

        for result in task_results:
            office = result.get("office")
            if result.get("status") == "completed":
                aggregated_data["task_outputs"][office] = result.get("output", {})
                aggregated_data["successful_tasks"].append(office)
            else:
                aggregated_data["failed_tasks"].append(office)

        # Call synthesis executor if available
        if synthesis_office in self.executors:
            synthesis = await self.executors[synthesis_office](
                "synthesize",
                aggregated_data
            )
        else:
            # Stub synthesis
            synthesis = {
                "synthesis": f"[STUB] {synthesis_office} synthesized {len(aggregated_data['successful_tasks'])} outputs",
                "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
                "confidence": 0.85
            }

        return {
            "synthesis_office": synthesis_office,
            "synthesis": synthesis,
            "task_count": len(task_results),
            "successful_count": len(aggregated_data["successful_tasks"])
        }

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get status of workflow execution."""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        workflow = self.workflows[workflow_id]

        task_statuses = {}
        for task in workflow.tasks:
            task_statuses[task.id] = {
                "office": task.office,
                "action": task.action,
                "status": task.status.value,
                "execution_time": (task.end_time - task.start_time) if task.end_time else None
            }

        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "mode": workflow.mode.value,
            "tasks": task_statuses
        }

    def get_stats(self) -> Dict:
        """Get workflow engine statistics."""
        return {
            "total_workflows": len(self.workflows),
            "total_executions": len(self.execution_log),
            "registered_executors": list(self.executors.keys()),
            "recent_executions": self.execution_log[-5:] if self.execution_log else []
        }

    def _save_to_disk(self):
        """Persist execution log to disk."""
        data = {
            "execution_log": self.execution_log,
            "saved_at": datetime.utcnow().isoformat()
        }
        self.storage_path.write_text(json.dumps(data, indent=2))

    def _load_from_disk(self):
        """Load execution log from disk."""
        try:
            if self.storage_path.exists():
                data = json.loads(self.storage_path.read_text())
                self.execution_log = data.get("execution_log", [])
                print(f"✅ Loaded {len(self.execution_log)} workflow executions from disk")
        except Exception as e:
            print(f"⚠️  Failed to load workflow history: {e}")


# ==============================================================================
# WORKFLOW TEMPLATES
# ==============================================================================

def create_cosmic_market_timing_workflow(engine: HybridWorkflowEngine) -> str:
    """
    Cosmic Market Timing Workflow

    Combines astrological transits, economic indicators, and banking data
    to generate market timing insights.
    """
    tasks = [
        {
            "office": "Astrologist",
            "action": "analyze_planetary_transits",
            "input_context": {
                "date_range": "next_30_days",
                "focus": ["Mercury", "Jupiter", "Saturn"]
            }
        },
        {
            "office": "Economist",
            "action": "analyze_macroeconomic_trends",
            "input_context": {
                "indicators": ["GDP", "inflation", "unemployment"],
                "regions": ["US", "EU", "Asia"]
            }
        },
        {
            "office": "Banker",
            "action": "analyze_market_sentiment",
            "input_context": {
                "markets": ["stocks", "bonds", "crypto"],
                "timeframe": "1_month"
            }
        }
    ]

    workflow_id = engine.create_workflow(
        name="Cosmic Market Timing",
        description="Synthesize astrological, economic, and market data for timing insights",
        tasks=tasks,
        mode=WorkflowMode.PARALLEL,
        synthesis_office="Philosopher"  # Synthesizes all perspectives
    )

    return workflow_id


def create_ethical_dilemma_analysis_workflow(engine: HybridWorkflowEngine) -> str:
    """
    Ethical Dilemma Analysis Workflow

    Sequential analysis: Philosopher → Historian → Tarot → final synthesis.
    """
    tasks = [
        {
            "office": "Philosopher",
            "action": "analyze_ethical_frameworks",
            "input_context": {
                "dilemma": "Should AI have rights?",
                "frameworks": ["utilitarian", "deontological", "virtue_ethics"]
            }
        },
        {
            "office": "Historian",
            "action": "provide_historical_context",
            "input_context": {
                "topic": "rights_movements",
                "periods": ["enlightenment", "civil_rights", "animal_rights"]
            },
            "dependencies": []  # Depends on Philosopher result
        },
        {
            "office": "Tarot",
            "action": "archetypal_reading",
            "input_context": {
                "question": "What does the collective unconscious say about AI rights?",
                "spread": "three_card"
            },
            "dependencies": []  # Depends on Historian result
        }
    ]

    workflow_id = engine.create_workflow(
        name="Ethical Dilemma Analysis",
        description="Multi-perspective analysis of ethical questions",
        tasks=tasks,
        mode=WorkflowMode.SEQUENTIAL,
        synthesis_office="Poet"  # Synthesizes into narrative
    )

    return workflow_id


def create_holistic_health_assessment_workflow(engine: HybridWorkflowEngine) -> str:
    """
    Holistic Health Assessment Workflow

    Graph-based: Sleep Coach + Herbalist → Numerologist (synthesis).
    """
    sleep_task_id = str(uuid.uuid4())
    herbalist_task_id = str(uuid.uuid4())

    tasks = [
        {
            "office": "Sleep Coach",
            "action": "analyze_sleep_patterns",
            "input_context": {
                "patient_data": {"sleep_hours": 6.5, "wake_ups": 2},
                "duration": "30_days"
            }
        },
        {
            "office": "Herbalist",
            "action": "recommend_botanical_remedies",
            "input_context": {
                "symptoms": ["fatigue", "poor_sleep", "stress"],
                "contraindications": []
            }
        },
        {
            "office": "Numerologist",
            "action": "calculate_biorhythm_cycles",
            "input_context": {
                "birth_date": "1990-05-15",
                "current_date": "2025-10-16"
            },
            "dependencies": []  # Waits for Sleep Coach + Herbalist
        }
    ]

    workflow_id = engine.create_workflow(
        name="Holistic Health Assessment",
        description="Integrate sleep, botanical, and numerological insights",
        tasks=tasks,
        mode=WorkflowMode.GRAPH,
        synthesis_office="Philosopher"  # Synthesizes holistic picture
    )

    return workflow_id


# Singleton instance
_workflow_engine = None


def get_workflow_engine(memory_graph=None) -> HybridWorkflowEngine:
    """Get singleton workflow engine instance."""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = HybridWorkflowEngine(memory_graph=memory_graph)
    return _workflow_engine


# CLI testing
if __name__ == "__main__":
    async def test_workflows():
        print("="*70)
        print("HYBRID WORKFLOW ENGINE TEST")
        print("="*70)

        engine = HybridWorkflowEngine()

        # Test 1: Cosmic Market Timing (Parallel)
        print("\n1. Creating Cosmic Market Timing workflow...")
        workflow_id = create_cosmic_market_timing_workflow(engine)
        print(f"   ✅ Workflow created: {workflow_id[:8]}")

        print("\n   Executing workflow...")
        result = await engine.execute_workflow(workflow_id)
        print(f"   ✅ Workflow completed in {result['execution_time']:.2f}s")
        print(f"   Task results: {result['task_results'][0]['office']} completed")

        # Test 2: Ethical Dilemma Analysis (Sequential)
        print("\n2. Creating Ethical Dilemma Analysis workflow...")
        workflow_id_2 = create_ethical_dilemma_analysis_workflow(engine)
        print(f"   ✅ Workflow created: {workflow_id_2[:8]}")

        print("\n   Executing workflow...")
        result_2 = await engine.execute_workflow(workflow_id_2)
        print(f"   ✅ Workflow completed in {result_2['execution_time']:.2f}s")

        # Test 3: Holistic Health Assessment (Graph)
        print("\n3. Creating Holistic Health Assessment workflow...")
        workflow_id_3 = create_holistic_health_assessment_workflow(engine)
        print(f"   ✅ Workflow created: {workflow_id_3[:8]}")

        print("\n   Executing workflow...")
        result_3 = await engine.execute_workflow(workflow_id_3)
        print(f"   ✅ Workflow completed in {result_3['execution_time']:.2f}s")

        # Test 4: Statistics
        print("\n4. Workflow engine statistics:")
        stats = engine.get_stats()
        print(f"   Total workflows: {stats['total_workflows']}")
        print(f"   Total executions: {stats['total_executions']}")
        print(f"   Registered executors: {stats['registered_executors']}")

        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)

    asyncio.run(test_workflows())
