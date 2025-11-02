class ToolExecutor:
    def __init__(self, office):
        self.office = office

    def execute_tool(self, tool_name, *args, **kwargs):
        # Check office permissions
        if not PermissionManager.can_execute(self.office, tool_name):
            return {
                "success": False,
                "error": f"{self.office} lacks execute permission for {tool_name}"
            }

        try:
            # Execute tool
            tool = getattr(self.office, tool_name)
            result = tool(*args, **kwargs)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
