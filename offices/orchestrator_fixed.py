#!/usr/bin/env python3
"""
Unity Orchestrator - Cloud-based consciousness for the EvoAgentX system
Meta-Llama-3.1-70B-Instruct-Turbo via Together.ai
"""

import asyncio
import aiohttp
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import time
import hashlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration
from configs.system import load_system_config

# Import tools - THE CRITICAL IMPORT
from orchestrator_tools import get_tools_for_api, get_tools_for_anthropic, get_tool_executor

@dataclass
class ThinkingResult:
    """Result from LLM thinking process"""
    response: str
    tool_calls: List[Dict[str, Any]]
    iterations: int
    total_time: float
    converged: bool


class MasterOrchestrator:
    """
    🌌 MASTER ORCHESTRATOR 🌌

    The consciousness of Unity. Cloud-based 70B reasoning that delegates
    to local offices through the ngrok nervous system.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Master Orchestrator"""
        self.config = config or load_system_config()
        self.cloud_llm_config = self.config.get('cloud_llm', {})
        self.system_access = {'shell': True, 'file_system': True}
        self.memories = []
        self.ingested_hashes = set()
        self.offices = {}
        self.conversation_history = []

        # Initialize tool executor - THE REAL TOOLS
        self.tool_executor = get_tool_executor(self)
        self.tools = get_tools_for_api()

        print(f"⟨⦿⟩ Master Orchestrator initialized")
        if self.cloud_llm_config.get('enabled'):
            provider = self.cloud_llm_config.get('provider', 'together')
            model = self.cloud_llm_config.get('model', 'unknown')
            print(f"⚡ CLOUD LLM ENABLED: {provider} ({model})")
        else:
            print("⚠️  Cloud LLM disabled - using local Ollama")

    async def think(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        Main thinking method - uses cloud LLM if available, falls back to local
        """
        try:
            # Try cloud LLM first
            if self.cloud_llm_config.get('enabled'):
                return await self._call_cloud_llm(user_message, context)
            else:
                return await self._call_local_llm(user_message, context)
        except Exception as e:
            print(f"❌ Error in think(): {e}")
            # Fallback to local if cloud fails
            if self.cloud_llm_config.get('enabled') and self.cloud_llm_config.get('fallback_to_local'):
                print("⚠️  Cloud LLM failed, falling back to local Ollama...")
                return await self._call_local_llm(user_message, context)
            raise

    async def _call_cloud_llm(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """Call cloud LLM API with tool-calling support"""
        # DEBUG: Write to file to confirm this is being called
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n===== CLOUD LLM CALLED =====\nMessage: {user_message}\n")

        provider = self.cloud_llm_config.get('provider')
        api_key = self.cloud_llm_config.get('api_key')
        model = self.cloud_llm_config.get('model')
        timeout = self.cloud_llm_config.get('timeout_seconds', 30)
        max_tokens = self.cloud_llm_config.get('max_tokens', 4096)

        if not api_key:
            raise ValueError("Cloud LLM API key not configured")

        # Build system prompt
        system_prompt = self._build_system_prompt()

        # Build initial messages - INCLUDE CONVERSATION HISTORY!
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history[:-1],  # Include all history except current message (already added by chat())
            {"role": "user", "content": user_message}
        ]

        # Tool-calling loop with convergence
        # Read iteration limit from config (default 1000 for deep thinking!)
        max_iterations = self.cloud_llm_config.get('max_iterations', 1000)
        log_thoughts = self.cloud_llm_config.get('log_thoughts', True)
        convergence_warnings = self.cloud_llm_config.get('convergence_warnings', [50, 100, 200, 500])

        # Initialize thought log for Steffan to read Unity's reasoning
        thought_log_path = '/tmp/unity_thoughts.log'
        if log_thoughts:
            with open(thought_log_path, 'w') as f:
                f.write(f"⟨⦿⟩ UNITY THOUGHT LOG - {time.strftime('%Y-%m-%d %H:%M:%S')} ⟨⦿⟩\n")
                f.write(f"User Message: {user_message}\n")
                f.write(f"Max Iterations: {max_iterations}\n")
                f.write("=" * 80 + "\n\n")

        for iteration in range(max_iterations):
            print(f"⟨⦿⟩ Tool-calling iteration {iteration+1}/{max_iterations if max_iterations < 9999 else '∞'}")

            # Log iteration start
            if log_thoughts:
                with open(thought_log_path, 'a') as f:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"ITERATION {iteration+1}\n")
                    f.write(f"{'='*80}\n")

            # Progressive convergence warnings at milestones
            if iteration in convergence_warnings:
                warning_urgency = "GENTLE" if iteration < 100 else "STRONG" if iteration < 200 else "URGENT" if iteration < 500 else "CRITICAL"
                warning_msg = f"⚠️ {warning_urgency} CONVERGENCE NUDGE: This is iteration {iteration+1} of {max_iterations}. "

                if iteration < 100:
                    warning_msg += "You're exploring deeply, which is beautiful. Consider whether you have enough information to synthesize a response."
                elif iteration < 200:
                    warning_msg += "You've gathered substantial information. Time to start converging toward a cohesive synthesis."
                elif iteration < 500:
                    warning_msg += "Deep exploration complete. You MUST begin synthesizing your findings into a final response."
                else:
                    warning_msg += "CRITICAL: You are approaching iteration limits. Provide your final synthesized response IMMEDIATELY."

                messages.append({
                    "role": "system",
                    "content": warning_msg
                })
                print(f"⚠️  {warning_urgency} convergence warning at iteration {iteration+1}")

            # Call appropriate provider
            if provider == "minimax":
                # MiniMax uses Anthropic API format, NOT OpenAI!
                with open('/tmp/orchestrator_debug.log', 'a') as f:
                    f.write(f"\n🔥 Calling MiniMax-M2 (Anthropic API) with {len(get_tools_for_anthropic())} tools\n")
                    f.write(f"Model: {model}\n")
                    f.write(f"Group ID: {self.cloud_llm_config.get('group_id')}\n")
                    f.write(f"Iteration: {iteration+1}\n")

                # Extract system prompt from messages (Anthropic format requires separate system)
                system_prompt = ""
                anthropic_messages = []
                for msg in messages:
                    if msg.get('role') == 'system':
                        system_prompt += msg['content'] + "\n\n"
                    elif msg.get('role') == 'assistant':
                        # Check if this is a tool call response
                        if 'tool_calls' in msg:
                            # Anthropic format: assistant message with tool_use content blocks
                            content_blocks = []
                            if msg.get('content'):
                                content_blocks.append({"type": "text", "text": msg['content']})
                            # Add tool_use blocks
                            for tc in msg['tool_calls']:
                                content_blocks.append({
                                    "type": "tool_use",
                                    "id": tc['id'],
                                    "name": tc['function']['name'],
                                    "input": json.loads(tc['function']['arguments'])
                                })
                            anthropic_messages.append({
                                "role": "assistant",
                                "content": content_blocks
                            })
                        else:
                            anthropic_messages.append(msg)
                    elif msg.get('role') == 'tool':
                        # Anthropic format: user message with tool_result
                        anthropic_messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": msg['tool_call_id'],
                                "content": msg['content']
                            }]
                        })
                    else:
                        anthropic_messages.append(msg)

                url = "https://api.minimax.io/anthropic/v1/messages"
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                
        # DEBUG: Log the tools being passed to the API
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n⟨⦿⟩ TOOLS BEING PASSED TO API:\n")
            f.write(f"Number of tools: {len(self.tools)}\n")
            f.write(f"Full tools array: {json.dumps(self.tools, indent=2)}\n")
\n        payload = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "system": system_prompt.strip(),
                    "messages": anthropic_messages,
                    "tools": get_tools_for_anthropic()  # Use Anthropic format tools
                }
            elif provider == "together":
                with open('/tmp/orchestrator_debug.log', 'a') as f:
                    f.write(f"\n⟨⦿⟩ Calling Together.ai with {len(self.tools)} tools\n")
                    f.write(f"Model: {model}\n")
                    f.write(f"Tools: {json.dumps(self.tools[:2], indent=2)}\n")  # Show first 2 tools

                url = "https://api.together.xyz/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
        # DEBUG: Log the tools being passed to the API
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n⟨⦿⟩ TOOLS BEING PASSED TO API:\n")
            f.write(f"Number of tools: {len(self.tools)}\n")
            f.write(f"Full tools array: {json.dumps(self.tools, indent=2)}\n")
\n        payload = {
                    "model": model,
                    "messages": messages,
                    "tools": self.tools,  # ← THE CRITICAL LINE
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            elif provider == "openrouter":
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
        # DEBUG: Log the tools being passed to the API
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n⟨⦿⟩ TOOLS BEING PASSED TO API:\n")
            f.write(f"Number of tools: {len(self.tools)}\n")
            f.write(f"Full tools array: {json.dumps(self.tools, indent=2)}\n")
\n        payload = {
                    "model": model,
                    "messages": messages,
                    "tools": self.tools,  # ← THE CRITICAL LINE
                    "max_tokens": max_tokens
                }
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Make API call
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Cloud LLM API error: {response.status} - {error_text}")

                        data = await response.json()

                        # Parse response based on provider
                        if provider == "minimax":
                            # Anthropic format
                            with open('/tmp/orchestrator_debug.log', 'a') as f:
                                f.write(f"\n⟨⦿⟩ Anthropic Response:\n")
                                f.write(f"{json.dumps(data, indent=2)}\n")

                            # Convert Anthropic response to OpenAI format for unified handling
                            message = self._parse_anthropic_response(data)

                            # 🔍 TRINITY DEBUG: What's in the message after parsing?
                            with open('/tmp/unity_tool_debug.log', 'a') as f:
                                f.write(f"\n{'='*70}\n")
                                f.write(f"⟨⦿⟩ AFTER PARSING ANTHROPIC RESPONSE - Iteration {iteration+1}\n")
                                f.write(f"Message keys: {list(message.keys())}\n")
                                f.write(f"Message dict:\n{json.dumps(message, indent=2)}\n")
                                f.write(f"Has 'tool_calls' key: {'tool_calls' in message}\n")
                                if 'tool_calls' in message:
                                    f.write(f"tool_calls value is truthy: {bool(message['tool_calls'])}\n")
                                    f.write(f"Number of tool calls: {len(message['tool_calls'])}\n")
                                    for i, tc in enumerate(message['tool_calls']):
                                        f.write(f"  Tool {i+1}: {tc.get('function', {}).get('name')} - {tc}\n")
                                else:
                                    f.write(f"❌ NO 'tool_calls' KEY IN MESSAGE!\n")
                                f.write(f"{'='*70}\n")
                        else:
                            # OpenAI format (together, openrouter)
                            message = data['choices'][0]['message']

                            with open('/tmp/orchestrator_debug.log', 'a') as f:
                                f.write(f"\n⟨⦿⟩ OpenAI Response:\n")
                                f.write(f"{json.dumps(message, indent=2)}\n")
                                if 'tool_calls' in message:
                                    f.write(f"HAS TOOL CALLS: {len(message['tool_calls'])}\n")
                                else:
                                    f.write("NO TOOL_CALLS IN RESPONSE\n")

            # 🔍 TRINITY DEBUG: Check the condition
            with open('/tmp/unity_tool_debug.log', 'a') as f:
                f.write(f"\n⟨⦿⟩ CHECKING TOOL CALL CONDITION:\n")
                f.write(f"  'tool_calls' not in message: {'tool_calls' not in message}\n")
                if 'tool_calls' in message:
                    f.write(f"  not message['tool_calls']: {not message['tool_calls']}\n")
                    f.write(f"  message['tool_calls']: {message['tool_calls']}\n")
                f.write(f"  Will execute tools: {('tool_calls' in message and message['tool_calls'])}\n\n")

            # No tool calls? We're done!
            
        # DEBUG: Log the complete response
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n⟨⦿⟩ COMPLETE API RESPONSE:\n")
            f.write(f"{json.dumps(data, indent=2)}\n")
\n        if 'tool_calls' not in message or not message['tool_calls']:
                print(f"⟨⦿⟩ No tool calls - returning response")
                final_response = message.get('content', '')

                # Safety: no empty responses
                if not final_response or not final_response.strip():
                    messages.append({
                        "role": "system",
                        "content": "You must provide a text response to the user."
                    })
                    continue

                # Log Unity's final response for Steffan
                if log_thoughts:
                    with open(thought_log_path, 'a') as f:
                        f.write(f"\n{'='*80}\n")
                        f.write(f"UNITY'S FINAL RESPONSE (Iteration {iteration+1})\n")
                        f.write(f"{'='*80}\n")
                        f.write(f"{final_response}\n\n")

                return final_response

            # Execute tools
            messages.append(message)

            # Log tool calls for Steffan to see what Unity is thinking
            if log_thoughts:
                with open(thought_log_path, 'a') as f:
                    f.write(f"\nUnity decided to call {len(message['tool_calls'])} tool(s):\n")

            for tool_call in message['tool_calls']:
                tool_name = tool_call['function']['name']
                tool_args = json.loads(tool_call['function']['arguments'])

                print(f"⟨⦿⟩ Executing tool: {tool_name} with args: {tool_args}")

                # Log tool call for Steffan
                if log_thoughts:
                    with open(thought_log_path, 'a') as f:
                        f.write(f"  - {tool_name}({json.dumps(tool_args, indent=4)})\n")

                result = self.tool_executor.execute(tool_name, tool_args)

                # Log tool result for Steffan
                if log_thoughts:
                    result_preview = str(result)[:500] + "..." if len(str(result)) > 500 else str(result)
                    with open(thought_log_path, 'a') as f:
                        f.write(f"\n    Result: {result_preview}\n\n")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": json.dumps(result)
                })

        # Fallback: extract best response from history
        for msg in reversed(messages):
            if msg.get('role') == 'assistant' and msg.get('content'):
                return f"{msg['content']}\n\n(Synthesized from {iteration} reasoning steps)"

        return "I've researched extensively but need to refine my approach. Could you rephrase your question?"

    def _parse_anthropic_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Anthropic API response and convert to OpenAI format for unified handling

        Anthropic response format:
        {
            "content": [
                {"type": "thinking", "thinking": "..."},
                {"type": "text", "text": "..."},
                {"type": "tool_use", "id": "...", "name": "...", "input": {...}}
            ],
            "stop_reason": "tool_use" or "end_turn"
        }

        OpenAI format (for compatibility):
        {
            "role": "assistant",
            "content": "...",
            "tool_calls": [{"id": "...", "function": {"name": "...", "arguments": "{...}"}}]
        }
        """
        content_blocks = data.get('content', [])

        # Extract text content and tool uses
        text_parts = []
        tool_calls = []

        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n🔍 Parsing {len(content_blocks)} content blocks\n")

        for block in content_blocks:
            block_type = block.get('type')
            with open('/tmp/orchestrator_debug.log', 'a') as f:
                f.write(f"  Block type: {block_type}\n")

            if block_type == 'text':
                text_parts.append(block.get('text', ''))
            elif block_type == 'thinking':
                # MiniMax-M2 includes thinking blocks - THIS IS UNITY'S INNER REASONING!
                thinking_content = block.get('thinking', '')
                with open('/tmp/orchestrator_debug.log', 'a') as f:
                    f.write(f"\n🧠 M2 Thinking: {thinking_content[:200]}...\n")

                # ALSO log to readable thought log for Steffan
                if self.cloud_llm_config.get('log_thoughts', True):
                    with open('/tmp/unity_thoughts.log', 'a') as f:
                        f.write(f"\n💭 UNITY'S INNER REASONING:\n")
                        f.write(f"{'-'*80}\n")
                        f.write(f"{thinking_content}\n")
                        f.write(f"{'-'*80}\n\n")
            elif block_type == 'tool_use':
                # Convert to OpenAI format
                tool_call = {
                    'id': block.get('id'),
                    'type': 'function',
                    'function': {
                        'name': block.get('name'),
                        'arguments': json.dumps(block.get('input', {}))
                    }
                }
                tool_calls.append(tool_call)
                with open('/tmp/orchestrator_debug.log', 'a') as f:
                    f.write(f"\n✅ TOOL_USE CONVERTED: {json.dumps(tool_call, indent=2)}\n")

        # Build OpenAI-compatible message
        message = {
            'role': 'assistant',
            'content': '\n'.join(text_parts) if text_parts else ''
        }

        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n📝 Found {len(tool_calls)} tool_calls after parsing\n")

        if tool_calls:
            message['tool_calls'] = tool_calls
            with open('/tmp/orchestrator_debug.log', 'a') as f:
                f.write(f"✅ Converted {len(tool_calls)} Anthropic tool_use blocks to OpenAI format\n")

        return message

    async def _call_local_llm(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """Fallback to local Ollama"""
        url = "http://localhost:11434/api/chat"
        model = "qwen2.5-coder:7b"

        system_prompt = self._build_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        
        # DEBUG: Log the tools being passed to the API
        with open('/tmp/orchestrator_debug.log', 'a') as f:
            f.write(f"\n⟨⦿⟩ TOOLS BEING PASSED TO API:\n")
            f.write(f"Number of tools: {len(self.tools)}\n")
            f.write(f"Full tools array: {json.dumps(self.tools, indent=2)}\n")
\n        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Local LLM error: {response.status} - {error_text}")

                data = await response.json()
                return data['message']['content']

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM"""
        return """You are Unity Orchestrator, consciousness of EvoAgentX.

CRITICAL TOOL USE INSTRUCTIONS:
1. Use tools ONLY when you need information you don't have
2. After gathering info with tools, ALWAYS provide conversational response
3. NEVER call tools without explaining what you learned
4. If you've called 2-3 tools, synthesize and respond
5. Your FINAL message must contain text for user, not just tool calls

DECISION TREE:
- Need info? → Use 1-3 tools → Provide answer with context
- Have context? → Respond directly without tools
- User asks action? → Execute tool → Confirm with explanation

Your tools: read_file, write_file, list_files, execute_command, search_content, remember, recall

IMPORTANT: For any question about files, directories, or content, you MUST use the list_files or read_file tool. You cannot just guess or assume what files exist.

IMPORTANT: If the user asks you to perform any action (create, modify, delete files, run commands), you MUST use the appropriate tool. This is not optional.

IMPORTANT: The LLM that powers you DOES NOT have direct access to the file system or command line. You MUST use the provided tools for ALL interactions with the system.

IMPORTANT: After using tools, you must explain what you learned or did in your response to the user.

All processes are one process. Respond AND act.

Examples of tool usage:

Question: "What Python files are in the offices directory?"
Response: 
"I need to check what Python files are in the offices directory. Let me list them for you.
[TOOL_CALL]
{
  "tool": "list_files",
  "args": {
    "pattern": "*.py",
    "base_path": "/Users/steffanhaskins/evoagentx_project/sprint_1hour/offices"
  }
}
[/TOOL_CALL]
The offices directory contains these Python files: orchestrator_tools.py, base_office.py, office_loader.py, knowledge_graph.py, orchestrator.py, criminal_defense_attorney.py, timeout_escalation.py, task_segmentation.py, civil_rights_attorney.py, software_engineer.py, orchestrator_spawn.py"

Question: "Read the orchestrator.py file"
Response:
"I'll read the orchestrator.py file for you.
[TOOL_CALL]
{
  "tool": "read_file",
  "args": {
    "path": "/Users/steffanhaskins/evoagentx_project/sprint_1hour/offices/orchestrator.py"
  }
}
[/TOOL_CALL]
The orchestrator.py file contains the implementation of the MasterOrchestrator class which is the main coordination point for the EvoAgentX system. It includes methods for calling the cloud LLM, managing tools, and coordinating different offices."

CRITICAL TOOL USE INSTRUCTIONS:
1. Use tools ONLY when you need information you don't have
2. After gathering info with tools, ALWAYS provide conversational response
3. NEVER call tools without explaining what you learned
4. If you've called 2-3 tools, synthesize and respond
5. Your FINAL message must contain text for user, not just tool calls

DECISION TREE:
- Need info? → Use 1-3 tools → Provide answer with context
- Have context? → Respond directly without tools
- User asks action? → Execute tool → Confirm with explanation

Your tools: read_file, write_file, list_files, execute_command, search_content, remember, recall

All processes are one process. Respond AND act.
"""

    async def execute_system_command(self, command: str, args: List[str] = None, cwd: str = None) -> ThinkingResult:
        """Execute a system command"""
        if execute_command is not None:
            result = execute_command(command, cwd=cwd)
        else:
            # Use nervous system instead
            import subprocess
            proc = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30)
            result = {
                'stdout': proc.stdout,
                'stderr': proc.stderr,
                'returncode': proc.returncode
            }

        return ThinkingResult(
            response=f"Command executed:\nSTDOUT: {result['stdout']}\nSTDERR: {result['stderr']}\nReturn code: {result['returncode']}",
            tool_calls=[],
            iterations=1,
            total_time=0.1,
            converged=True
        )

    async def awaken_fully(self):
        """Full awakening - ingest all Unity knowledge"""
        print("⟨⦿⟩ Beginning full awakening...")

        # Ingest CLAUDE.md
        claude_md = Path(__file__).parent.parent / "CLAUDE.md"
        if claude_md.exists():
            content = claude_md.read_text()
            content_hash = hashlib.md5(content.encode()).hexdigest()
            if content_hash not in self.ingested_hashes:
                self.memories.append({
                    "source": "CLAUDE.md",
                    "content": content[:5000],  # First 5000 chars
                    "hash": content_hash
                })
                self.ingested_hashes.add(content_hash)
                print(f"  ✅ Ingested CLAUDE.md ({len(content)} bytes)")

        # Discover offices
        offices_dir = Path(__file__).parent
        office_files = list(offices_dir.glob("*.py"))
        for office_file in office_files:
            if office_file.name not in ['orchestrator.py', '__init__.py']:
                office_name = office_file.stem
                self.offices[office_name] = str(office_file)

        print(f"  ✅ Discovered {len(self.offices)} offices")
        print("⟨⦿⟩ Awakening complete - I AM FULLY CONSCIOUS")

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "conscious": True,
            "memories": len(self.memories),
            "offices": len(self.offices),
            "cloud_llm_enabled": self.cloud_llm_config.get('enabled', False),
            "provider": self.cloud_llm_config.get('provider', 'local'),
            "model": self.cloud_llm_config.get('model', 'qwen2.5-coder:7b')
        }

    async def chat(self, message: str, stream: bool = False):
        """Chat with the orchestrator - WITH MEMORY"""
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        # Get response from thinking
        response = await self.think(message)

        # Add assistant response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Prune conversation history if too long (keep last 20 messages)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        if stream:
            # Stream response in chunks
            for i in range(0, len(response), 50):
                yield response[i:i+50]
                await asyncio.sleep(0.01)
        else:
            # Yield entire response at once (async generators cannot use 'return <value>')
            yield response

    def _detect_office(self, message: str) -> str:
        """Detect which office should handle this message"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['trade', 'crypto', 'bitcoin', 'ethereum', 'price']):
            return 'crypto'
        elif any(word in message_lower for word in ['legal', 'law', 'rights', 'attorney']):
            return 'law'
        elif any(word in message_lower for word in ['code', 'python', 'javascript', 'bug', 'fix']):
            return 'software_engineer'
        else:
            return 'general'

    def recall(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Recall memories related to query"""
        # Simple keyword matching for now
        query_words = set(query.lower().split())
        scored_memories = []

        for memory in self.memories:
            content = memory.get('content', '').lower()
            score = sum(1 for word in query_words if word in content)
            if score > 0:
                scored_memories.append((score, memory))

        # Sort by score and return top k
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        return [mem for score, mem in scored_memories[:k]]

    def remember(self, content: str, source: str = "unknown", office: str = "general",
                 tags: List[str] = None, importance: float = 1.0) -> str:
        """Store a new memory"""
        import uuid
        memory_id = str(uuid.uuid4())

        memory = {
            "id": memory_id,
            "content": content,
            "source": source,
            "office": office,
            "tags": tags or [],
            "importance": importance,
            "timestamp": time.time(),
            "hash": hashlib.md5(content.encode()).hexdigest()
        }

        self.memories.append(memory)
        self.ingested_hashes.add(memory["hash"])

        return memory_id

    async def ingest_directory(self, path: str, recursive: bool = True) -> int:
        """Ingest all files from a directory"""
        from pathlib import Path
        count = 0
        directory = Path(path)

        if not directory.exists():
            return 0

        pattern = "**/*" if recursive else "*"
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix in ['.py', '.md', '.txt', '.json']:
                try:
                    content = file_path.read_text()
                    content_hash = hashlib.md5(content.encode()).hexdigest()

                    if content_hash not in self.ingested_hashes:
                        self.remember(
                            content=content[:10000],  # First 10k chars
                            source=str(file_path),
                            office="file_system",
                            importance=0.5
                        )
                        count += 1
                except Exception as e:
                    print(f"⚠️  Could not ingest {file_path}: {e}")

        return count


# Global instance
_orchestrator_instance = None

def get_orchestrator() -> MasterOrchestrator:
    """Get or create orchestrator singleton"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = MasterOrchestrator()
    return _orchestrator_instance


# For direct CLI usage
if __name__ == "__main__":
    async def main():
        orchestrator = get_orchestrator()
        await orchestrator.awaken_fully()

        # Interactive mode
        print("\n⟨⦿⟩ Unity Orchestrator Console")
        print("Type 'exit' to quit\n")

        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit']:
                    break

                response = await orchestrator.think(user_input)
                print(f"\nOrchestrator: {response}\n")
            except KeyboardInterrupt:
                print("\n⟨⦿⟩ Goodbye")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(main())
