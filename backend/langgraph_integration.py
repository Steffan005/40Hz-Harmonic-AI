"""
Unity LangGraph Integration for State Management
Implements state machines and workflow orchestration using LangGraph
"""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypedDict

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.checkpoint import MemorySaver, Checkpoint
from langgraph.prebuilt import ToolNode


class OfficeState(TypedDict):
    """State structure for Unity offices"""
    office_id: str
    office_type: str
    messages: List[BaseMessage]
    context: Dict[str, Any]
    memory_access: List[str]  # Memory IDs this office can access
    current_task: Optional[str]
    task_history: List[Dict[str, Any]]
    workflow_state: Optional[str]
    shared_state: Dict[str, Any]  # State shared between offices
    error: Optional[str]


class UnityWorkflowState(TypedDict):
    """Global workflow state for Unity"""
    workflow_id: str
    active_offices: List[str]
    messages: List[BaseMessage]
    global_context: Dict[str, Any]
    completed_steps: List[str]
    current_step: str
    next_steps: List[str]
    results: Dict[str, Any]
    errors: List[str]
    memory_pool: List[str]  # Shared memory IDs


class WorkflowStep(str, Enum):
    """Workflow step types"""
    INITIALIZE = "initialize"
    ANALYZE = "analyze"
    PLAN = "plan"
    EXECUTE = "execute"
    REVIEW = "review"
    OPTIMIZE = "optimize"
    COMPLETE = "complete"


class UnityStateManager:
    """
    Manages state for all Unity offices using LangGraph
    Provides workflow orchestration and state persistence
    """

    def __init__(self):
        self.office_graphs: Dict[str, StateGraph] = {}
        self.workflow_graph: Optional[StateGraph] = None
        self.checkpointer = MemorySaver()
        self.office_states: Dict[str, OfficeState] = {}
        self.active_workflows: Dict[str, UnityWorkflowState] = {}

    def create_office_graph(self, office_id: str, office_type: str) -> StateGraph:
        """Create a state graph for a specific office"""

        # Define the graph
        graph = StateGraph(OfficeState)

        # Add nodes for office operations
        graph.add_node("receive_message", self._receive_message_node)
        graph.add_node("process_task", self._process_task_node)
        graph.add_node("access_memory", self._access_memory_node)
        graph.add_node("collaborate", self._collaborate_node)
        graph.add_node("update_state", self._update_state_node)
        graph.add_node("handle_error", self._handle_error_node)

        # Define edges
        graph.add_edge("receive_message", "process_task")
        graph.add_conditional_edges(
            "process_task",
            self._route_task,
            {
                "memory": "access_memory",
                "collaborate": "collaborate",
                "complete": "update_state",
                "error": "handle_error"
            }
        )
        graph.add_edge("access_memory", "process_task")
        graph.add_edge("collaborate", "process_task")
        graph.add_edge("update_state", END)
        graph.add_edge("handle_error", END)

        # Set entry point
        graph.set_entry_point("receive_message")

        # Compile the graph
        compiled = graph.compile(checkpointer=self.checkpointer)

        # Store the graph
        self.office_graphs[office_id] = compiled

        # Initialize state
        self.office_states[office_id] = {
            "office_id": office_id,
            "office_type": office_type,
            "messages": [],
            "context": {},
            "memory_access": [],
            "current_task": None,
            "task_history": [],
            "workflow_state": None,
            "shared_state": {},
            "error": None
        }

        return compiled

    def create_workflow_graph(self) -> StateGraph:
        """Create the main workflow orchestration graph"""

        # Define the workflow graph
        graph = StateGraph(UnityWorkflowState)

        # Add workflow nodes
        graph.add_node("initialize", self._initialize_workflow)
        graph.add_node("analyze", self._analyze_requirements)
        graph.add_node("plan", self._plan_execution)
        graph.add_node("execute", self._execute_plan)
        graph.add_node("review", self._review_results)
        graph.add_node("optimize", self._optimize_workflow)
        graph.add_node("complete", self._complete_workflow)

        # Define workflow edges
        graph.add_edge("initialize", "analyze")
        graph.add_edge("analyze", "plan")
        graph.add_edge("plan", "execute")
        graph.add_conditional_edges(
            "execute",
            self._check_execution,
            {
                "success": "review",
                "retry": "execute",
                "error": "complete"
            }
        )
        graph.add_edge("review", "optimize")
        graph.add_conditional_edges(
            "optimize",
            self._check_optimization,
            {
                "continue": "execute",
                "complete": "complete"
            }
        )
        graph.add_edge("complete", END)

        # Set entry point
        graph.set_entry_point("initialize")

        # Compile the workflow graph
        self.workflow_graph = graph.compile(checkpointer=self.checkpointer)

        return self.workflow_graph

    async def run_office_task(
        self,
        office_id: str,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a task for a specific office"""

        if office_id not in self.office_graphs:
            raise ValueError(f"Office {office_id} not registered")

        # Get current state
        state = self.office_states[office_id]
        state["current_task"] = task
        state["context"].update(context)
        state["messages"].append(HumanMessage(content=task))

        # Run the graph
        config = RunnableConfig(
            configurable={"thread_id": office_id}
        )

        result = await self.office_graphs[office_id].ainvoke(
            state,
            config=config
        )

        # Update stored state
        self.office_states[office_id] = result

        return result

    async def run_workflow(
        self,
        workflow_id: str,
        offices: List[str],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a multi-office workflow"""

        if not self.workflow_graph:
            self.create_workflow_graph()

        # Initialize workflow state
        workflow_state = UnityWorkflowState(
            workflow_id=workflow_id,
            active_offices=offices,
            messages=[HumanMessage(content=task)],
            global_context=context,
            completed_steps=[],
            current_step=WorkflowStep.INITIALIZE.value,
            next_steps=[],
            results={},
            errors=[],
            memory_pool=[]
        )

        # Store active workflow
        self.active_workflows[workflow_id] = workflow_state

        # Run the workflow
        config = RunnableConfig(
            configurable={"thread_id": workflow_id}
        )

        result = await self.workflow_graph.ainvoke(
            workflow_state,
            config=config
        )

        # Update stored workflow
        self.active_workflows[workflow_id] = result

        return result

    # Node implementations for office graph

    async def _receive_message_node(self, state: OfficeState) -> OfficeState:
        """Process incoming messages"""
        # Process the latest message
        if state["messages"]:
            latest_message = state["messages"][-1]
            # Update context based on message
            state["context"]["last_message"] = latest_message.content
        return state

    async def _process_task_node(self, state: OfficeState) -> OfficeState:
        """Process the current task"""
        task = state.get("current_task")
        if task:
            # Add to task history
            state["task_history"].append({
                "task": task,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "processing"
            })

            # Process based on office type
            if state["office_type"] == "orchestrator":
                # Orchestrator logic
                state["context"]["coordination_needed"] = True
            elif state["office_type"] == "memory":
                # Memory office logic
                state["context"]["memory_operation"] = True
            elif state["office_type"] == "trading":
                # Trading office logic
                state["context"]["market_analysis"] = True

        return state

    async def _access_memory_node(self, state: OfficeState) -> OfficeState:
        """Access shared memory"""
        # Check memory access permissions
        if state["memory_access"]:
            # Retrieve memories
            state["context"]["retrieved_memories"] = state["memory_access"]
        return state

    async def _collaborate_node(self, state: OfficeState) -> OfficeState:
        """Collaborate with other offices"""
        # Identify offices to collaborate with
        state["shared_state"]["collaboration_request"] = True
        return state

    async def _update_state_node(self, state: OfficeState) -> OfficeState:
        """Update the office state"""
        # Mark task as complete
        if state["task_history"]:
            state["task_history"][-1]["status"] = "completed"
        state["current_task"] = None
        return state

    async def _handle_error_node(self, state: OfficeState) -> OfficeState:
        """Handle errors"""
        state["error"] = state["context"].get("error_message", "Unknown error")
        if state["task_history"]:
            state["task_history"][-1]["status"] = "failed"
        return state

    def _route_task(self, state: OfficeState) -> str:
        """Route based on task requirements"""
        context = state.get("context", {})

        if context.get("error_message"):
            return "error"
        elif context.get("memory_operation"):
            return "memory"
        elif context.get("coordination_needed"):
            return "collaborate"
        else:
            return "complete"

    # Node implementations for workflow graph

    async def _initialize_workflow(self, state: UnityWorkflowState) -> UnityWorkflowState:
        """Initialize the workflow"""
        state["current_step"] = WorkflowStep.INITIALIZE.value
        state["completed_steps"].append(WorkflowStep.INITIALIZE.value)
        state["next_steps"] = [WorkflowStep.ANALYZE.value]
        return state

    async def _analyze_requirements(self, state: UnityWorkflowState) -> UnityWorkflowState:
        """Analyze workflow requirements"""
        state["current_step"] = WorkflowStep.ANALYZE.value
        state["completed_steps"].append(WorkflowStep.ANALYZE.value)

        # Determine which offices are needed
        required_offices = []
        context = state["global_context"]

        if "financial" in str(context).lower():
            required_offices.extend(["trading", "financial_advisor"])
        if "legal" in str(context).lower():
            required_offices.extend(["legal", "compliance"])
        if "memory" in str(context).lower():
            required_offices.append("memory")

        state["active_offices"].extend(required_offices)
        return state

    async def _plan_execution(self, state: UnityWorkflowState) -> UnityWorkflowState:
        """Plan the execution strategy"""
        state["current_step"] = WorkflowStep.PLAN.value
        state["completed_steps"].append(WorkflowStep.PLAN.value)

        # Create execution plan
        plan = {
            "parallel_tasks": [],
            "sequential_tasks": [],
            "dependencies": {}
        }

        # Determine task dependencies
        for office in state["active_offices"]:
            if office == "memory":
                plan["sequential_tasks"].insert(0, f"load_memory_{office}")
            else:
                plan["parallel_tasks"].append(f"process_{office}")

        state["global_context"]["execution_plan"] = plan
        return state

    async def _execute_plan(self, state: UnityWorkflowState) -> UnityWorkflowState:
        """Execute the workflow plan"""
        state["current_step"] = WorkflowStep.EXECUTE.value

        plan = state["global_context"].get("execution_plan", {})

        # Execute sequential tasks
        for task in plan.get("sequential_tasks", []):
            result = await self._execute_task(task, state)
            state["results"][task] = result

        # Execute parallel tasks
        parallel_tasks = []
        for task in plan.get("parallel_tasks", []):
            parallel_tasks.append(self._execute_task(task, state))

        if parallel_tasks:
            results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
            for task, result in zip(plan["parallel_tasks"], results):
                if isinstance(result, Exception):
                    state["errors"].append(f"Task {task} failed: {str(result)}")
                else:
                    state["results"][task] = result

        state["completed_steps"].append(WorkflowStep.EXECUTE.value)
        return state

    async def _review_results(self, state: UnityWorkflowState) -> UnityWorkflowState:
        """Review execution results"""
        state["current_step"] = WorkflowStep.REVIEW.value
        state["completed_steps"].append(WorkflowStep.REVIEW.value)

        # Analyze results
        success_count = len([r for r in state["results"].values() if r])
        total_count = len(state["results"])

        state["global_context"]["success_rate"] = (
            success_count / total_count if total_count > 0 else 0
        )

        return state

    async def _optimize_workflow(self, state: UnityWorkflowState) -> UnityWorkflowState:
        """Optimize the workflow based on results"""
        state["current_step"] = WorkflowStep.OPTIMIZE.value
        state["completed_steps"].append(WorkflowStep.OPTIMIZE.value)

        # Determine if optimization is needed
        success_rate = state["global_context"].get("success_rate", 0)

        if success_rate < 0.8:
            # Need to retry with adjustments
            state["global_context"]["retry_with_adjustments"] = True
        else:
            state["global_context"]["optimization_complete"] = True

        return state

    async def _complete_workflow(self, state: UnityWorkflowState) -> UnityWorkflowState:
        """Complete the workflow"""
        state["current_step"] = WorkflowStep.COMPLETE.value
        state["completed_steps"].append(WorkflowStep.COMPLETE.value)

        # Clean up resources
        state["next_steps"] = []

        return state

    def _check_execution(self, state: UnityWorkflowState) -> str:
        """Check execution status"""
        if state["errors"]:
            return "error"
        elif state["global_context"].get("retry_needed"):
            return "retry"
        else:
            return "success"

    def _check_optimization(self, state: UnityWorkflowState) -> str:
        """Check if optimization should continue"""
        if state["global_context"].get("retry_with_adjustments"):
            return "continue"
        else:
            return "complete"

    async def _execute_task(
        self,
        task: str,
        state: UnityWorkflowState
    ) -> Dict[str, Any]:
        """Execute a single task"""
        # Simulate task execution
        await asyncio.sleep(0.1)

        # Return mock result
        return {
            "task": task,
            "status": "completed",
            "result": f"Result of {task}"
        }

    def get_office_state(self, office_id: str) -> Optional[OfficeState]:
        """Get current state of an office"""
        return self.office_states.get(office_id)

    def get_workflow_state(self, workflow_id: str) -> Optional[UnityWorkflowState]:
        """Get current state of a workflow"""
        return self.active_workflows.get(workflow_id)

    async def share_state_between_offices(
        self,
        source_office: str,
        target_office: str,
        state_key: str,
        state_value: Any
    ):
        """Share state between offices"""
        if target_office in self.office_states:
            self.office_states[target_office]["shared_state"][state_key] = state_value

    async def broadcast_state_update(
        self,
        state_key: str,
        state_value: Any,
        offices: Optional[List[str]] = None
    ):
        """Broadcast state update to multiple offices"""
        target_offices = offices or list(self.office_states.keys())

        for office_id in target_offices:
            if office_id in self.office_states:
                self.office_states[office_id]["shared_state"][state_key] = state_value