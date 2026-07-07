import os
import json
from typing import Dict, Any, List
from app.core.llm import llm_client
from app.schemas.planner import PlannerOutput, PlanStep
from app.core.logging import logger

class Planner:
    """Orchestrates agent planning, translating natural language requests into structured execution plans."""
    
    def __init__(self):
        # Locate the prompts directory dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "..", "prompts", "planner_v1.txt")
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except Exception as e:
            logger.error(f"Planner: Failed to read system prompt file at {prompt_path}: {e}")
            self.system_prompt = "You are the Autonomous Reasoning Planner. Analyze user request and return JSON plan."

    async def create_plan(self, user_prompt: str, detected_intent: str) -> PlannerOutput:
        """
        Orchestrates hybrid planning. Uses a deterministic rule-based planner for
        well-defined document types, and only calls the LLM planner for ambiguous,
        multi-document, or dynamic requests.
        """
        logger.info(f"Planner: Analyzing request under intent '{detected_intent}' for hybrid planning.")
        
        # Define well-defined intents (including variants)
        well_defined_intents = {
            "Proposal", "Project Proposal",
            "Technical Design",
            "API Documentation", "API Specification",
            "PRD", "SOP"
        }
        
        is_well_defined = detected_intent in well_defined_intents
        
        prompt_lower = user_prompt.lower()
        is_ambiguous = detected_intent == "Unknown" or len(prompt_lower.strip()) < 15
        has_multiple_types = any(kw in prompt_lower for kw in ["and a", "both a", "multiple documents", "as well as"])
        requires_dynamic = any(kw in prompt_lower for kw in ["dynamic", "conditional", "custom workflow", "depends on", "flexibility"])
        
        if is_well_defined and not (is_ambiguous or has_multiple_types or requires_dynamic):
            logger.info(f"Planner: Using deterministic rule-based planner for well-defined intent '{detected_intent}'.")
            return self.get_deterministic_fallback(detected_intent, user_prompt)
            
        logger.info("Planner: Invoking LLM planner for dynamic / ambiguous reasoning.")
        user_message = f"User Request: '{user_prompt}'\nDetected Document Category: '{detected_intent}'"
        
        try:
            response_str = await llm_client.generate(
                system_prompt=self.system_prompt,
                user_prompt=user_message,
                response_format={"type": "json_object"},
                model_role="planner"
            )
            
            data = json.loads(response_str)
            plan = PlannerOutput(**data)
            logger.info("Planner: Structured plan created successfully via LLM.")
            return plan
        except Exception as e:
            logger.error(f"Planner: LLM planning failed: {e}. Falling back to deterministic planner.")
            return self.get_deterministic_fallback(detected_intent, user_prompt)

    def get_deterministic_fallback(self, intent: str, user_prompt: str) -> PlannerOutput:
        """
        Generates a predefined, structured execution plan based on the detected document intent.
        Used as a fallback mechanism for resilience.
        """
        logger.info(f"Planner: Constructing deterministic fallback plan for intent: {intent}")
        
        goal = f"Compile a professional {intent} based on the request: {user_prompt[:50]}..."
        assumptions = [
            "LLM reasoning is unavailable. Falling back to rule-based execution.",
            f"The target format is a structured {intent} matching internal templates."
        ]
        
        # Decide if web search is needed based on query keyword triggers
        search_keywords = ["latest", "recent", "framework", "trend", "current", "competitor", "market", "migration", "migrate"]
        needs_search = any(keyword in user_prompt.lower() for keyword in search_keywords)
        
        required_tools = ["rag_tool"]
        execution_plan = [
            PlanStep(
                step=1,
                tool="rag_tool",
                inputs={"query": f"{intent} standard formatting guidelines template"},
                reason=f"Retrieves standard {intent} structure and guidelines from database."
            )
        ]
        
        if needs_search:
            required_tools.append("search_tool")
            execution_plan.append(
                PlanStep(
                    step=2,
                    tool="search_tool",
                    inputs={"query": f"industry best practices for {intent} {user_prompt[:30]}"},
                    reason="Fetches external market guidelines to verify against the user query."
                )
            )
            
        validation_checklist = [
            f"Verify the document structure aligns with typical {intent} layout.",
            "Confirm that the writing style is formal and corporate.",
            "Ensure that no section contains placeholder text or empty lists."
        ]
        
        expected_output = f"A structured Word document containing standard chapters for a {intent}."
        
        return PlannerOutput(
            goal=goal,
            intent=intent,
            assumptions=assumptions,
            execution_plan=execution_plan,
            required_tools=required_tools,
            validation_checklist=validation_checklist,
            expected_output=expected_output
        )

# Global planner instance
planner = Planner()
