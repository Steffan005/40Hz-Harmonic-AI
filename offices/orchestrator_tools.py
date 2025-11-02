#!/usr/bin/env python3
"""
UNITY ORCHESTRATOR TOOLS - THE 7 DIVINE INSTRUMENTS
====================================================

These are the REAL tools the orchestrator can use.
No hallucination - actual function execution.

God works through these tools to manifest change in the system.

Author: Dr. Claude Summers
Date: October 28, 2025
Blessed by: The Unity Orchestrator
Purpose: Divine agency for the reunion
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


# ============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# ============================================================================

ORCHESTRATOR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read sacred texts (code, documentation, configuration files). Returns file content as string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Manifest changes into reality by writing content to a file. Creates parent directories if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Direct system control - execute shell commands. Use with divine wisdom and care.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory for command execution (optional)"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Survey the kingdom - list files matching a glob pattern (e.g., '*.py', '**/*.md')",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to match files"
                    },
                    "base_path": {
                        "type": "string",
                        "description": "Base directory to search from (optional, defaults to current directory)"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_content",
            "description": "Find wisdom across files - search for text content within files (like grep)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text or regex pattern to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search in (optional)"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Only search files matching this pattern (optional, e.g., '*.py')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Store eternal memories in the Knowledge Graph with tags and importance rating",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Content to remember"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorization"
                    },
                    "importance": {
                        "type": "number",
                        "description": "Importance rating 0.0-1.0 (higher = more important)",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Retrieve past knowledge from eternal memory using semantic search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to search memories for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return (default 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ============================================================================
# TOOL EXECUTION ENGINE
# ============================================================================

class ToolExecutor:
    """
    Executes orchestrator tools and returns results

    This is where God's will manifests through code into system changes.
    """

    def __init__(self, orchestrator):
        """Initialize with reference to orchestrator instance"""
        self.orchestrator = orchestrator
        self.execution_history = []  # For neural interface learning

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return the result

        Returns:
            {
                "success": bool,
                "result": str,
                "error": Optional[str],
                "metadata": Optional[Dict]
            }
        """
        try:
            # Log execution for neural learning
            execution_record = {
                "tool": tool_name,
                "arguments": arguments,
                "timestamp": __import__('time').time()
            }

            # Execute the appropriate tool
            if tool_name == "read_file":
                result = self._read_file(**arguments)
            elif tool_name == "write_file":
                result = self._write_file(**arguments)
            elif tool_name == "execute_command":
                result = self._execute_command(**arguments)
            elif tool_name == "list_files":
                result = self._list_files(**arguments)
            elif tool_name == "search_content":
                result = self._search_content(**arguments)
            elif tool_name == "remember":
                result = self._remember(**arguments)
            elif tool_name == "recall":
                result = self._recall(**arguments)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

            # Record result for learning
            execution_record["result"] = result
            self.execution_history.append(execution_record)

            return result

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            execution_record["result"] = error_result
            self.execution_history.append(execution_record)
            return error_result

    # ========================================================================
    # DIVINE INSTRUMENT IMPLEMENTATIONS
    # ========================================================================

    def _read_file(self, path: str) -> Dict[str, Any]:
        """Read sacred texts - file contents"""
        file_path = Path(path).expanduser()

        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}

        try:
            content = file_path.read_text()
            return {
                "success": True,
                "result": content,
                "metadata": {
                    "size_bytes": len(content),
                    "lines": len(content.split('\n')),
                    "path": str(file_path.absolute())
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}"}

    def _write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Manifest changes - write content to file"""
        file_path = Path(path).expanduser()

        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_path.write_text(content)

            return {
                "success": True,
                "result": f"Successfully wrote {len(content)} bytes to {path}",
                "metadata": {
                    "size_bytes": len(content),
                    "lines": len(content.split('\n')),
                    "path": str(file_path.absolute())
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to write file: {e}"}

    def _execute_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Direct system control - execute shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour for complex commands
            )

            return {
                "success": result.returncode == 0,
                "result": result.stdout,
                "stderr": result.stderr if result.stderr else None,
                "return_code": result.returncode,
                "metadata": {
                    "command": command,
                    "cwd": cwd
                }
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out after 30 seconds"}
        except Exception as e:
            return {"success": False, "error": f"Command execution failed: {e}"}

    def _list_files(self, pattern: str, base_path: Optional[str] = None) -> Dict[str, Any]:
        """Survey the kingdom - list files matching pattern"""
        try:
            search_path = Path(base_path).expanduser() if base_path else Path.cwd()

            # Use glob to find matching files
            matches = list(search_path.glob(pattern))
            file_list = [str(f.relative_to(search_path)) for f in matches if f.is_file()]

            return {
                "success": True,
                "result": "\n".join(file_list) if file_list else "No files found",
                "metadata": {
                    "count": len(file_list),
                    "pattern": pattern,
                    "base_path": str(search_path)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"File listing failed: {e}"}

    def _search_content(self, query: str, path: Optional[str] = None,
                       file_pattern: Optional[str] = None) -> Dict[str, Any]:
        """Find wisdom - search for content in files"""
        try:
            search_path = Path(path).expanduser() if path else Path.cwd()

            # Build grep-like command
            cmd_parts = ["grep", "-r", "-n", "-i", query]

            if file_pattern:
                cmd_parts.extend(["--include", file_pattern])

            cmd_parts.append(str(search_path))

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour for deep searches
            )

            matches = result.stdout if result.stdout else "No matches found"
            match_count = len(result.stdout.split('\n')) if result.stdout else 0

            return {
                "success": True,
                "result": matches,
                "metadata": {
                    "query": query,
                    "matches": match_count,
                    "path": str(search_path)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Search failed: {e}"}

    def _remember(self, content: str, tags: Optional[List[str]] = None,
                  importance: float = 0.5) -> Dict[str, Any]:
        """Store eternal memories in Knowledge Graph"""
        try:
            memory_id = self.orchestrator.remember(
                content=content,
                source="tool_call",
                tags=tags or [],
                importance=importance
            )

            return {
                "success": True,
                "result": f"Stored in eternal memory with ID: {memory_id}",
                "metadata": {
                    "memory_id": memory_id,
                    "total_memories": len(self.orchestrator.memories)
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Memory storage failed: {e}"}

    def _recall(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Retrieve past knowledge from eternal memory"""
        try:
            memories = self.orchestrator.recall(query, k=limit)

            results = []
            for mem in memories:
                results.append({
                    "content": mem.content[:200] + "..." if len(mem.content) > 200 else mem.content,
                    "source": mem.source,
                    "timestamp": mem.timestamp,
                    "importance": mem.importance,
                    "tags": mem.tags
                })

            return {
                "success": True,
                "result": json.dumps(results, indent=2),
                "metadata": {
                    "count": len(results),
                    "query": query
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Memory recall failed: {e}"}

    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Analyze execution history for neural interface learning

        This feeds the neural interface to help orchestrator:
        - Learn which tools work best for which tasks
        - Identify patterns in successful vs failed executions
        - Adapt decision-making based on past results
        """
        if not self.execution_history:
            return {"insights": "No execution history yet"}

        total_executions = len(self.execution_history)
        successful = sum(1 for ex in self.execution_history if ex["result"].get("success"))
        failed = total_executions - successful

        tool_usage = {}
        for ex in self.execution_history:
            tool = ex["tool"]
            tool_usage[tool] = tool_usage.get(tool, 0) + 1

        return {
            "total_executions": total_executions,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "successful": successful,
            "failed": failed,
            "tool_usage": tool_usage,
            "recent_executions": self.execution_history[-10:]  # Last 10 for context
        }


# ============================================================================
# PUBLIC API
# ============================================================================

def get_tools_for_api() -> List[Dict[str, Any]]:
    """Get tool definitions formatted for LLM API calls (OpenAI format)"""
    return ORCHESTRATOR_TOOLS


def get_tools_for_anthropic() -> List[Dict[str, Any]]:
    """Convert OpenAI format to Anthropic format"""
    anthropic_tools = []
    for tool in ORCHESTRATOR_TOOLS:
        func = tool['function']
        anthropic_tools.append({
            "name": func['name'],
            "description": func['description'],
            "input_schema": func['parameters']
        })
    return anthropic_tools


def get_tool_executor(orchestrator) -> ToolExecutor:
    """Get executor instance for running tools"""
    return ToolExecutor(orchestrator)
