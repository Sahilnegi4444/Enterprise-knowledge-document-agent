from app.tools.registry import tool_registry
from app.tools.rag_tool import RAGTool
from app.tools.search_tool import SearchTool
from app.tools.reflection_tool import ReflectionTool
from app.tools.document_tool import DocumentTool

# Automatically register default toolset on startup
tool_registry.register(RAGTool())
tool_registry.register(SearchTool())
tool_registry.register(ReflectionTool())
tool_registry.register(DocumentTool())

__all__ = [
    "tool_registry",
    "RAGTool",
    "SearchTool",
    "ReflectionTool",
    "DocumentTool"
]
