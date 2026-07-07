from fastapi import APIRouter, HTTPException, status
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent_orchestrator import agent_orchestrator
from app.core.exceptions import (
    RequestValidationException, 
    LLMException, 
    DocxGenerationException,
    AgentException
)
from app.core.logging import logger

router = APIRouter()

@router.post(
    "/agent", 
    response_model=AgentResponse, 
    status_code=status.HTTP_200_OK,
    summary="Process natural language requests to plan and generate styled DOCX business documents."
)
async def run_agent(request: AgentRequest):
    """
    Executes the autonomous agent pipeline.
    
    1. Validates request payload and checks for prompt injection.
    2. Detects document intent.
    3. Plans execution strategy (uses RAG and/or Web Search tools concurrently).
    4. Gathers context, generates structured JSON, and self-reflects.
    5. Outputs a professionally styled DOCX file encoded in Base64.
    """
    logger.info("API: Received request at POST /agent.")
    
    try:
        response = await agent_orchestrator.process_request(request)
        return response
        
    except RequestValidationException as ve:
        logger.warning(f"API: Client validation failed: {ve.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": ve.message, "details": ve.details}
        )
        
    except LLMException as le:
        logger.error(f"API: LLM generation error: {le.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "LLMError", "message": le.message, "details": le.details}
        )
        
    except DocxGenerationException as de:
        logger.error(f"API: Document compilation failed: {de.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DocxGenerationError", "message": de.message, "details": de.details}
        )
        
    except AgentException as ae:
        logger.error(f"API: Generic Agent error: {ae.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "AgentRuntimeError", "message": ae.message, "details": ae.details}
        )
        
    except Exception as e:
        logger.error(f"API: Unhandled exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalServerError", "message": "An unexpected error occurred.", "details": str(e)}
        )
