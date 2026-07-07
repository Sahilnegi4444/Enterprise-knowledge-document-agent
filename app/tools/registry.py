from typing import Dict, List
from app.tools.base import BaseTool
from app.core.exceptions import ToolExecutionException
from app.core.logging import logger

class ToolRegistry:
    """Registry to manage and dynamically look up all executable tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        
    def register(self, tool: BaseTool) -> None:
        """Registers a tool in the registry."""
        if tool.name in self._tools:
            logger.warning(f"Overwriting registered tool: {tool.name}")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
        
    def get_tool(self, name: str) -> BaseTool:
        """Retrieves a tool by name. Raises ToolExecutionException if missing."""
        tool = self._tools.get(name)
        if not tool:
            raise ToolExecutionException(
                tool_name=name,
                message="Tool not found in registry."
            )
        return tool
        
    def list_tools(self) -> List[str]:
        """Returns list of registered tool names."""
        return list(self._tools.keys())

# Global registry instance
tool_registry = ToolRegistry()
