from typing import Dict, Any, List, Tuple
from app.schemas.planner import PlannerOutput
from app.core.logging import logger

class ContextBuilder:
    """Consolidates tool outputs, planner instructions, and user requests into structured text context."""
    
    def build_context(
        self,
        user_request: str,
        plan: PlannerOutput,
        tool_outputs: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Builds distinct, clean text sections for RAG context, Search context, and Assumptions.
        Reduces overlapping data and cleans formatting.
        
        :return: A tuple of (rag_context_str, search_context_str, assumptions_str)
        """
        logger.info("ContextBuilder: Consolidating gathered intelligence.")
        
        # 1. Format Assumptions
        assumptions_list = plan.assumptions or []
        assumptions_str = "\n".join(f"- {a}" for a in assumptions_list) if assumptions_list else "None specified."
        
        # 2. Format RAG results
        rag_output = tool_outputs.get("rag_tool", {})
        rag_results = rag_output.get("results", []) if isinstance(rag_output, dict) else []
        
        rag_chunks = []
        seen_contents = set()
        for idx, item in enumerate(rag_results):
            content = item.get("content", "").strip()
            # De-duplicate chunks with identical content
            if not content or content in seen_contents:
                continue
            seen_contents.add(content)
            
            meta = item.get("metadata", {})
            doc_type = meta.get("document_type", "General")
            section = meta.get("section", "Unknown Section")
            source = meta.get("source_file", "KB File")
            
            chunk_str = f"Source: {source} | Doc Type: {doc_type} | Section: {section}\nContent:\n{content}"
            rag_chunks.append(chunk_str)
            
        rag_context_str = "\n\n---\n\n".join(rag_chunks) if rag_chunks else "No relevant enterprise templates or guidelines found."
        
        # 3. Format Web Search results
        search_output = tool_outputs.get("search_tool", {})
        search_results = search_output.get("results", []) if isinstance(search_output, dict) else []
        
        search_chunks = []
        for idx, item in enumerate(search_results):
            title = item.get("title", "No Title").strip()
            url = item.get("url", "")
            content = item.get("content", "").strip()
            if not content:
                continue
                
            search_str = f"Title: {title}\nURL: {url}\nExcerpt: {content}"
            search_chunks.append(search_str)
            
        search_context_str = "\n\n---\n\n".join(search_chunks) if search_chunks else "No real-time search results retrieved."
        
        logger.info("ContextBuilder: Intelligence consolidation finished.")
        return rag_context_str, search_context_str, assumptions_str

# Global context builder instance
context_builder = ContextBuilder()
