"""
Unity Inter-Office Message Passing Protocol
Implements pub/sub messaging with Redis for office communication
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel, Field


class MessagePriority(str, Enum):
    """Message priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class MessageType(str, Enum):
    """Types of inter-office messages"""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    WORKFLOW = "workflow"
    MEMORY_SHARE = "memory_share"


@dataclass
class Message:
    """Inter-office message structure"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: MessageType = MessageType.REQUEST
    priority: MessagePriority = MessagePriority.NORMAL
    sender_office: str = ""
    target_office: Optional[str] = None  # None for broadcasts
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None  # For request/response pairing
    timestamp: float = field(default_factory=time.time)
    ttl_seconds: int = 300  # Message expiry (5 minutes default)
    require_ack: bool = False
    retry_count: int = 0
    max_retries: int = 3


class MessageProtocolConfig(BaseModel):
    """Configuration for the message protocol"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    max_queue_size: int = 1000
    default_timeout: int = 30
    heartbeat_interval: int = 10
    max_retries: int = 3


class MessageRouter:
    """
    Central message router for Unity inter-office communication
    Handles pub/sub, request/response, and broadcast patterns
    """

    def __init__(self, config: MessageProtocolConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.office_handlers: Dict[str, Dict[MessageType, Callable]] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.office_queues: Dict[str, asyncio.Queue] = {}
        self.subscriptions: Dict[str, List[str]] = {}
        self.listener_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self._running = False

    async def initialize(self):
        """Initialize Redis connections and start listeners"""
        # Create Redis connection
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            decode_responses=True
        )

        # Create pub/sub connection
        self.pubsub = self.redis_client.pubsub()

        # Subscribe to system channels
        await self.pubsub.subscribe(
            "unity:system:broadcast",
            "unity:system:heartbeat"
        )

        # Start listener task
        self.listener_task = asyncio.create_task(self._listen_for_messages())

        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        self._running = True
        print(f"✅ Message Router initialized")

    async def register_office(
        self,
        office_id: str,
        office_type: str,
        handlers: Optional[Dict[MessageType, Callable]] = None
    ):
        """Register an office with the message router"""

        # Create office queue
        self.office_queues[office_id] = asyncio.Queue(
            maxsize=self.config.max_queue_size
        )

        # Register handlers
        if handlers:
            self.office_handlers[office_id] = handlers

        # Subscribe to office-specific channel
        channel = f"unity:office:{office_id}"
        await self.pubsub.subscribe(channel)

        # Track subscription
        if office_id not in self.subscriptions:
            self.subscriptions[office_id] = []
        self.subscriptions[office_id].append(channel)

        # Announce office online
        await self.broadcast_notification(
            sender_office="system",
            event_type="office_online",
            data={
                "office_id": office_id,
                "office_type": office_type,
                "timestamp": time.time()
            }
        )

        print(f"📮 Office registered: {office_id} ({office_type})")

    async def unregister_office(self, office_id: str):
        """Unregister an office from the message router"""

        # Unsubscribe from channels
        if office_id in self.subscriptions:
            for channel in self.subscriptions[office_id]:
                await self.pubsub.unsubscribe(channel)
            del self.subscriptions[office_id]

        # Remove queue
        if office_id in self.office_queues:
            del self.office_queues[office_id]

        # Remove handlers
        if office_id in self.office_handlers:
            del self.office_handlers[office_id]

        # Announce office offline
        await self.broadcast_notification(
            sender_office="system",
            event_type="office_offline",
            data={"office_id": office_id}
        )

    async def send_message(
        self,
        message: Message,
        wait_for_response: bool = False,
        timeout: Optional[int] = None
    ) -> Optional[Message]:
        """Send a message to a specific office or broadcast"""

        # Add to metrics
        await self._track_message(message)

        # Determine channel
        if message.target_office:
            channel = f"unity:office:{message.target_office}"
        else:
            channel = "unity:system:broadcast"

        # Serialize message
        message_data = self._serialize_message(message)

        # If waiting for response, create future
        response_future = None
        if wait_for_response and message.type == MessageType.REQUEST:
            response_future = asyncio.Future()
            self.pending_responses[message.id] = response_future

        # Publish message
        await self.redis_client.publish(channel, message_data)

        # Wait for response if requested
        if response_future:
            try:
                timeout = timeout or self.config.default_timeout
                response = await asyncio.wait_for(
                    response_future,
                    timeout=timeout
                )
                return response
            except asyncio.TimeoutError:
                del self.pending_responses[message.id]
                if message.retry_count < message.max_retries:
                    # Retry the message
                    message.retry_count += 1
                    return await self.send_message(
                        message,
                        wait_for_response,
                        timeout
                    )
                else:
                    raise TimeoutError(f"No response received for message {message.id}")
            finally:
                if message.id in self.pending_responses:
                    del self.pending_responses[message.id]

        return None

    async def send_request(
        self,
        sender_office: str,
        target_office: str,
        action: str,
        params: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        timeout: Optional[int] = None
    ) -> Optional[Message]:
        """Send a request and wait for response"""

        message = Message(
            type=MessageType.REQUEST,
            priority=priority,
            sender_office=sender_office,
            target_office=target_office,
            payload={
                "action": action,
                "params": params
            },
            require_ack=True
        )

        return await self.send_message(
            message,
            wait_for_response=True,
            timeout=timeout
        )

    async def send_response(
        self,
        request_message: Message,
        response_data: Dict[str, Any],
        success: bool = True
    ):
        """Send a response to a request"""

        response = Message(
            type=MessageType.RESPONSE if success else MessageType.ERROR,
            priority=request_message.priority,
            sender_office=request_message.target_office,
            target_office=request_message.sender_office,
            correlation_id=request_message.id,
            payload=response_data
        )

        await self.send_message(response)

    async def broadcast_notification(
        self,
        sender_office: str,
        event_type: str,
        data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ):
        """Broadcast a notification to all offices"""

        message = Message(
            type=MessageType.BROADCAST,
            priority=priority,
            sender_office=sender_office,
            payload={
                "event_type": event_type,
                "data": data
            }
        )

        await self.send_message(message)

    async def create_workflow(
        self,
        workflow_id: str,
        steps: List[Dict[str, Any]],
        initiating_office: str
    ) -> str:
        """Create a multi-office workflow"""

        workflow_message = Message(
            type=MessageType.WORKFLOW,
            priority=MessagePriority.HIGH,
            sender_office=initiating_office,
            payload={
                "workflow_id": workflow_id,
                "steps": steps,
                "current_step": 0,
                "status": "initiated"
            }
        )

        # Store workflow in Redis
        workflow_key = f"unity:workflow:{workflow_id}"
        await self.redis_client.setex(
            workflow_key,
            3600,  # 1 hour TTL
            json.dumps(workflow_message.payload)
        )

        # Notify first office in workflow
        if steps:
            first_step = steps[0]
            target_office = first_step.get("office")
            if target_office:
                workflow_message.target_office = target_office
                await self.send_message(workflow_message)

        return workflow_id

    async def advance_workflow(
        self,
        workflow_id: str,
        step_result: Dict[str, Any]
    ):
        """Advance a workflow to the next step"""

        workflow_key = f"unity:workflow:{workflow_id}"
        workflow_data = await self.redis_client.get(workflow_key)

        if not workflow_data:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = json.loads(workflow_data)
        current_step = workflow["current_step"]
        steps = workflow["steps"]

        # Record step result
        steps[current_step]["result"] = step_result
        steps[current_step]["completed_at"] = time.time()

        # Move to next step
        next_step = current_step + 1

        if next_step < len(steps):
            workflow["current_step"] = next_step
            workflow["status"] = "in_progress"

            # Update workflow in Redis
            await self.redis_client.setex(
                workflow_key,
                3600,
                json.dumps(workflow)
            )

            # Notify next office
            target_office = steps[next_step].get("office")
            if target_office:
                message = Message(
                    type=MessageType.WORKFLOW,
                    priority=MessagePriority.HIGH,
                    sender_office="workflow_engine",
                    target_office=target_office,
                    payload=workflow
                )
                await self.send_message(message)
        else:
            # Workflow complete
            workflow["status"] = "completed"
            workflow["completed_at"] = time.time()

            # Update workflow in Redis
            await self.redis_client.setex(
                workflow_key,
                3600,
                json.dumps(workflow)
            )

            # Broadcast completion
            await self.broadcast_notification(
                sender_office="workflow_engine",
                event_type="workflow_completed",
                data={
                    "workflow_id": workflow_id,
                    "results": [step.get("result") for step in steps]
                }
            )

    async def get_office_queue(self, office_id: str) -> Optional[asyncio.Queue]:
        """Get the message queue for an office"""
        return self.office_queues.get(office_id)

    async def _listen_for_messages(self):
        """Background task to listen for messages"""
        while self._running:
            try:
                message = await self.pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )

                if message:
                    await self._process_message(message)

            except Exception as e:
                print(f"Error in message listener: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, redis_message: Dict[str, Any]):
        """Process a received message"""
        try:
            # Parse message
            data = redis_message.get("data")
            if isinstance(data, str):
                message = self._deserialize_message(data)
            else:
                return

            # Check if it's a response to a pending request
            if message.type == MessageType.RESPONSE and message.correlation_id:
                if message.correlation_id in self.pending_responses:
                    future = self.pending_responses[message.correlation_id]
                    future.set_result(message)
                    return

            # Route to office handler
            if message.target_office and message.target_office in self.office_handlers:
                handlers = self.office_handlers[message.target_office]
                handler = handlers.get(message.type)

                if handler:
                    # Execute handler
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)

                # Add to office queue
                if message.target_office in self.office_queues:
                    queue = self.office_queues[message.target_office]
                    if not queue.full():
                        await queue.put(message)

            # Handle broadcasts
            elif message.type == MessageType.BROADCAST:
                # Deliver to all offices
                for office_id, queue in self.office_queues.items():
                    if not queue.full():
                        await queue.put(message)

        except Exception as e:
            print(f"Error processing message: {e}")

    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self._running:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)

                # Send heartbeat for each registered office
                for office_id in self.office_queues.keys():
                    heartbeat = Message(
                        type=MessageType.HEARTBEAT,
                        sender_office=office_id,
                        payload={
                            "timestamp": time.time(),
                            "queue_size": self.office_queues[office_id].qsize()
                        }
                    )
                    await self.redis_client.publish(
                        "unity:system:heartbeat",
                        self._serialize_message(heartbeat)
                    )

            except Exception as e:
                print(f"Error in heartbeat: {e}")

    async def _track_message(self, message: Message):
        """Track message metrics"""
        # Increment counters
        await self.redis_client.hincrby(
            "unity:metrics:messages",
            f"{message.sender_office}:sent",
            1
        )
        if message.target_office:
            await self.redis_client.hincrby(
                "unity:metrics:messages",
                f"{message.target_office}:received",
                1
            )

    def _serialize_message(self, message: Message) -> str:
        """Serialize a message for Redis"""
        return json.dumps({
            "id": message.id,
            "type": message.type.value,
            "priority": message.priority.value,
            "sender_office": message.sender_office,
            "target_office": message.target_office,
            "payload": message.payload,
            "correlation_id": message.correlation_id,
            "timestamp": message.timestamp,
            "ttl_seconds": message.ttl_seconds,
            "require_ack": message.require_ack,
            "retry_count": message.retry_count,
            "max_retries": message.max_retries
        })

    def _deserialize_message(self, data: str) -> Message:
        """Deserialize a message from Redis"""
        msg_dict = json.loads(data)
        return Message(
            id=msg_dict["id"],
            type=MessageType(msg_dict["type"]),
            priority=MessagePriority(msg_dict["priority"]),
            sender_office=msg_dict["sender_office"],
            target_office=msg_dict.get("target_office"),
            payload=msg_dict["payload"],
            correlation_id=msg_dict.get("correlation_id"),
            timestamp=msg_dict["timestamp"],
            ttl_seconds=msg_dict.get("ttl_seconds", 300),
            require_ack=msg_dict.get("require_ack", False),
            retry_count=msg_dict.get("retry_count", 0),
            max_retries=msg_dict.get("max_retries", 3)
        )

    async def close(self):
        """Clean up connections"""
        self._running = False

        if self.listener_task:
            self.listener_task.cancel()

        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        if self.pubsub:
            await self.pubsub.close()

        if self.redis_client:
            await self.redis_client.close()


# Office-specific message handler
class OfficeMessageHandler:
    """Base class for office-specific message handlers"""

    def __init__(self, office_id: str, office_type: str, router: MessageRouter):
        self.office_id = office_id
        self.office_type = office_type
        self.router = router
        self.handlers = {
            MessageType.REQUEST: self.handle_request,
            MessageType.NOTIFICATION: self.handle_notification,
            MessageType.WORKFLOW: self.handle_workflow,
            MessageType.MEMORY_SHARE: self.handle_memory_share,
            MessageType.ERROR: self.handle_error
        }

    async def initialize(self):
        """Initialize the office handler"""
        await self.router.register_office(
            self.office_id,
            self.office_type,
            self.handlers
        )

    async def handle_request(self, message: Message):
        """Handle incoming requests"""
        action = message.payload.get("action")
        params = message.payload.get("params", {})

        try:
            # Process the request based on action
            result = await self.process_action(action, params)

            # Send response
            await self.router.send_response(
                message,
                {"result": result},
                success=True
            )
        except Exception as e:
            # Send error response
            await self.router.send_response(
                message,
                {"error": str(e)},
                success=False
            )

    async def handle_notification(self, message: Message):
        """Handle incoming notifications"""
        event_type = message.payload.get("event_type")
        data = message.payload.get("data", {})
        await self.process_notification(event_type, data)

    async def handle_workflow(self, message: Message):
        """Handle workflow steps"""
        workflow_id = message.payload.get("workflow_id")
        current_step = message.payload.get("current_step")
        steps = message.payload.get("steps", [])

        if current_step < len(steps):
            step = steps[current_step]
            result = await self.process_workflow_step(workflow_id, step)

            # Advance workflow
            await self.router.advance_workflow(workflow_id, result)

    async def handle_memory_share(self, message: Message):
        """Handle memory sharing requests"""
        memory_data = message.payload
        await self.process_memory_share(memory_data)

    async def handle_error(self, message: Message):
        """Handle error messages"""
        error = message.payload.get("error")
        print(f"Error received in {self.office_id}: {error}")

    # Methods to be overridden by specific office implementations
    async def process_action(self, action: str, params: Dict[str, Any]) -> Any:
        """Process a specific action - override in subclass"""
        raise NotImplementedError

    async def process_notification(self, event_type: str, data: Dict[str, Any]):
        """Process a notification - override in subclass"""
        pass

    async def process_workflow_step(self, workflow_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """Process a workflow step - override in subclass"""
        return {"status": "completed"}

    async def process_memory_share(self, memory_data: Dict[str, Any]):
        """Process shared memory - override in subclass"""
        pass