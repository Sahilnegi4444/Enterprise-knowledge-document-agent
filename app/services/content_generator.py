import os
import json
from typing import Dict, Any, List, Optional
from app.core.llm import llm_client
from app.schemas.content import StructuredDocument
from app.core.logging import logger
from app.core.exceptions import LLMException

class ContentGenerator:
    """Service to invoke the LLM with consolidated context and generate a structured JSON document."""
    
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "..", "prompts", "generator_v1.txt")
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt_template = f.read()
        except Exception as e:
            logger.error(f"ContentGenerator: Failed to read generator prompt from {prompt_path}: {e}")
            self.system_prompt_template = "You are the Content Generator. Output the structured JSON."

    async def generate_document(
        self,
        user_request: str,
        planner_output_json: str,
        rag_context: str,
        search_context: str,
        assumptions: str,
        revisions: Optional[List[str]] = None
    ) -> StructuredDocument:
        """
        Calls the LLM to generate the document content.
        Supports applying revision suggestions from self-reflection loop.
        """
        logger.info("ContentGenerator: Generating structured document content.")
        
        system_prompt = (
            self.system_prompt_template
            .replace("{user_request}", user_request)
            .replace("{planner_output}", planner_output_json)
            .replace("{rag_context}", rag_context)
            .replace("{search_context}", search_context)
            .replace("{assumptions}", assumptions)
        )
        
        user_message = "Please generate the structured document JSON now."
        
        # Append revision directions if this is a correction loop iteration
        if revisions:
            revision_bullets = "\n".join(f"- {r}" for r in revisions)
            user_message += f"\n\nCRITICAL REVISION REQUEST:\nYour previous attempt failed the self-reflection audit. You must revise the content to address these feedback points:\n{revision_bullets}\n\nMaintain the exact same JSON format and output the entire document with corrections."
            logger.info(f"ContentGenerator: Injecting {len(revisions)} revision points into instructions.")
            
        try:
            response_str = await llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_message,
                response_format={"type": "json_object"},
                model_role="generator"
            )
            
            data = json.loads(response_str)
            document = StructuredDocument(**data)
            logger.info("ContentGenerator: Structured document content created successfully.")
            return document
        except Exception as e:
            logger.error(f"ContentGenerator: Content generation call failed or output malformed: {e}")
            raise LLMException(f"Content generation stage failed: {str(e)}")

# Global content generator instance
content_generator = ContentGenerator()
