from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime

class BaseOffice:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tools = {}
        self._load_config()
        self._initialize_tools()

    def _load_config(self):
        config_path = Path(__file__).parent / "config.json"
        with config_path.open("r") as f:
            self.config = json.load(f)

    def _initialize_tools(self):
        for tool_name, tool_config in self.config["tools"].items():
            tool_class = tool_config["class"]
            tool_instance = tool_class(**tool_config["params"])
            self.tools[tool_name] = tool_instance

    def can_execute_tool(self, tool_name: str) -> bool:
        return tool_name in self.tools

    def execute_tool(self, tool_name: str, *args, **kwargs):
        if self.can_execute_tool(tool_name):
            tool_instance = self.tools[tool_name]
            return tool_instance.execute(*args, **kwargs)
        else:
            raise ValueError(f"Tool {tool_name} not found")

    def process_request(self, request: Dict[str, Any]) -> Any:
        tool_name = request["tool"]
        args = request.get("args", [])
        kwargs = request.get("kwargs", {})
        return self.execute_tool(tool_name, *args, **kwargs)
