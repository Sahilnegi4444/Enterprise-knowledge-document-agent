import asyncio
import time
from typing import List, Dict, Any, Tuple
from app.tools.registry import tool_registry
from app.schemas.agent import ToolExecutionLog
from app.schemas.planner import PlannerOutput
from app.core.logging import logger

class Router:
    """Dynamic Tool Router. Responsible for resolving and executing tools specified by the Planner."""
    
    async def execute_plan(self, plan: PlannerOutput) -> Tuple[List[ToolExecutionLog], Dict[str, Any]]:
        """
        Executes all tools specified in the plan concurrently (using asyncio.gather)
        to maximize performance, particularly for I/O bound RAG and web search operations.
        
        :param plan: The PlannerOutput schema containing steps.
        :return: A tuple containing (execution logs list, aggregated dictionary of outputs).
        """
        logger.info("Router: Resolving and executing plan steps.")
        
        execution_logs: List[ToolExecutionLog] = []
        aggregated_outputs: Dict[str, Any] = {}
        
        tasks = []
        active_steps = []
        
        # Resolve tools from the registry and prepare coroutines
        for step in plan.execution_plan:
            tool_name = step.tool
            tool_inputs = step.inputs
            
            try:
                tool = tool_registry.get_tool(tool_name)
                # Queue for concurrent async execution
                tasks.append(self._run_tool_monitored(tool, tool_inputs))
                active_steps.append((tool_name, tool_inputs))
            except Exception as e:
                logger.error(f"Router: Resolution failed for tool '{tool_name}': {e}")
                execution_logs.append(ToolExecutionLog(
                    tool_name=tool_name,
                    inputs=tool_inputs,
                    success=False,
                    message=f"Registry lookup/initialization failed: {str(e)}"
                ))
                
        if not tasks:
            logger.info("Router: No executable tools scheduled in the plan.")
            return execution_logs, aggregated_outputs
            
        # Run all scheduled tools concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (tool_name, tool_inputs), result in zip(active_steps, results):
            if isinstance(result, Exception):
                logger.error(f"Router: Tool '{tool_name}' crashed during execution: {result}")
                execution_logs.append(ToolExecutionLog(
                    tool_name=tool_name,
                    inputs=tool_inputs,
                    success=False,
                    message=f"Runtime Exception: {str(result)}"
                ))
                aggregated_outputs[tool_name] = {"success": False, "error": str(result), "results": []}
            else:
                success = result.get("success", False)
                message = "Success" if success else result.get("error", "Unknown tool error")
                
                execution_logs.append(ToolExecutionLog(
                    tool_name=tool_name,
                    inputs=tool_inputs,
                    success=success,
                    message=f"Completed. {message}"
                ))
                aggregated_outputs[tool_name] = result
                
        logger.info("Router: Finished executing all planned tools.")
        return execution_logs, aggregated_outputs

    async def _run_tool_monitored(self, tool: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to run a tool, logs performance metrics."""
        start_time = time.time()
        logger.info(f"Router: Starting tool '{tool.name}' execution.")
        try:
            result = await tool.execute(inputs)
            duration = time.time() - start_time
            logger.info(f"Router: Tool '{tool.name}' completed in {duration:.4f}s.")
            return result
        except Exception as e:
            logger.error(f"Router: Tool '{tool.name}' execution handler failed: {e}")
            raise

# Global router instance
router = Router()
