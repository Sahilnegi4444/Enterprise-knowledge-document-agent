from typing import Dict, Any
import base64
from app.tools.base import BaseTool
from app.core.logging import logger

class DocumentTool(BaseTool):
    """Tool to compile structured document JSON schemas into styled DOCX binaries."""
    
    @property
    def name(self) -> str:
        return "document_tool"
        
    @property
    def description(self) -> str:
        return "Compiles structured document JSON model into a professionally-formatted Microsoft Word (.docx) file."
        
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        document_data = inputs.get("document_data")
        if not document_data:
            logger.warning("DocumentTool: Missing 'document_data' in inputs.")
            return {"success": False, "error": "Missing input parameter: 'document_data'", "docx_base64": ""}
            
        try:
            logger.info("DocumentTool: Generating DOCX byte stream from JSON schema.")
            # Lazy import to avoid circular dependency
            from app.document.docx_generator import docx_generator
            
            docx_bytes = docx_generator.generate(document_data)
            base64_string = base64.b64encode(docx_bytes).decode("utf-8")
            
            return {
                "success": True,
                "docx_base64": base64_string
            }
        except Exception as e:
            logger.error(f"DocumentTool failed during docx compilation: {e}")
            return {
                "success": False,
                "error": f"Failed to compile Word document: {str(e)}",
                "docx_base64": ""
            }
