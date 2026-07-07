from fastapi import FastAPI
from app.api.routes import router as agent_router
from app.rag.kb_manager import KBManager
from app.core.logging import logger
import os

app = FastAPI(
    title="Enterprise Knowledge & Documentation Agent API",
    description="Autonomous AI Agent capable of document intent detection, dynamic planning, RAG, Web Search, and Word (.docx) compilation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Connect routing
app.include_router(agent_router)

@app.on_event("startup")
async def startup_event():
    """Triggers on server startup to bootstrap and ingest standard knowledge base documents."""
    logger.info("FastAPI: Application startup sequence initiated.")
    
    # Locate knowledge base path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "knowledge_base"))
    
    try:
        total_chunks = KBManager.ingest_kb_directory(kb_dir)
        logger.info(f"FastAPI: Bootstrap RAG complete. Ingested {total_chunks} chunks.")
    except Exception as e:
        logger.error(f"FastAPI: Failed to bootstrap RAG on startup: {e}. System will run with fallback storage.")
