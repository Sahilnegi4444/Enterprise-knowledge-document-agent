from typing import Dict, Any

class BaseTool:
    """Abstract Base Class for all tools registered in the Agent System."""
    
    @property
    def name(self) -> str:
        """Unique identifier of the tool."""
        raise NotImplementedError
        
    @property
    def description(self) -> str:
        """Clear description of tool usage for documentation and routing."""
        raise NotImplementedError
        
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tool with structured inputs.
        
        :param inputs: A dictionary of key-value inputs as specified by the planner.
        :return: A dictionary of results or output data.
        """
        raise NotImplementedError
