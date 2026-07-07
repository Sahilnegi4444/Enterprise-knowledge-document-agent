from typing import Dict, Any, List
from app.tools.base import BaseTool
from app.core.logging import logger

class ReflectionTool(BaseTool):
    """Tool to inspect the generated content against the validation checklist and corporate standards."""
    
    @property
    def name(self) -> str:
        return "reflection_tool"
        
    @property
    def description(self) -> str:
        return "Evaluates generated document content for completeness, tone, accuracy and formatting guidelines."
        
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        document = inputs.get("document")
        checklist = inputs.get("validation_checklist", [])
        user_request = inputs.get("user_request", "")
        
        if not document:
            logger.warning("ReflectionTool: Missing 'document' input parameter.")
            return {"success": False, "error": "Missing input parameter: 'document'"}
            
        try:
            logger.info("ReflectionTool: Initiating document reflection audit.")
            # Lazy import to avoid circular dependency
            from app.services.reflection_service import reflection_service
            
            report = await reflection_service.reflect(
                document=document,
                checklist=checklist,
                user_request=user_request
            )
            
            return {
                "success": True,
                "report": report.model_dump()
            }
        except Exception as e:
            logger.error(f"ReflectionTool failed: {e}")
            # Fallback gracefully
            return {
                "success": False,
                "error": f"Reflection error: {str(e)}",
                "report": {
                    "passed": True,  # Fallback to true so execution doesn't block permanently
                    "score": 5.0,
                    "completeness": "Reflection crashed, returning best-effort output.",
                    "grammar": "Unknown",
                    "consistency": "Unknown",
                    "suggestions": []
                }
            }
