from typing import Dict, Any
from app.tools.base import BaseTool
from app.rag.vector_store import vector_store
from app.config.settings import settings
from app.core.logging import logger

class RAGTool(BaseTool):
    """Tool to query internal enterprise documents, templates, and guidelines."""
    
    @property
    def name(self) -> str:
        return "rag_tool"
        
    @property
    def description(self) -> str:
        return "Searches internal database for business/technical document templates and formatting guidelines."
        
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query_text = inputs.get("query")
        if not query_text:
            logger.warning("RAGTool: Missing 'query' parameter in inputs.")
            return {"success": False, "error": "Missing input parameter: 'query'", "results": []}
            
        # Optional metadata filtering
        doc_type = inputs.get("document_type")
        category = inputs.get("category")
        
        metadata_filter = {}
        if doc_type:
            metadata_filter["document_type"] = doc_type
        if category:
            metadata_filter["category"] = category
            
        if not metadata_filter:
            metadata_filter = None
            
        try:
            logger.info(f"RAGTool running query: '{query_text}' (filter: {metadata_filter})")
            results = vector_store.query(
                query_text=query_text,
                top_k=settings.RAG_TOP_K,
                metadata_filter=metadata_filter
            )
            
            return {
                "success": True,
                "results": results
            }
        except Exception as e:
            logger.error(f"RAGTool failed: {e}")
            return {
                "success": False,
                "error": f"Internal database error: {str(e)}",
                "results": []  # Fallback gracefully
            }
