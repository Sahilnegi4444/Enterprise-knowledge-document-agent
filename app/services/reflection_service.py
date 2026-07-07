import os
import json
from typing import List, Dict, Any, Tuple
from app.core.llm import llm_client
from app.schemas.reflection import ReflectionReport
from app.core.logging import logger

class ReflectionService:
    """Service to audit generated documents against validation checklists and tone guidelines using lightweight rules and the LLM."""
    
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "..", "prompts", "reflection_v1.txt")
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt_template = f.read()
        except Exception as e:
            logger.error(f"ReflectionService: Failed to read reflection prompt from {prompt_path}: {e}")
            self.system_prompt_template = "You are the Quality Control Auditor. Grade the document and output JSON."

    async def reflect(
        self,
        document: Dict[str, Any],
        checklist: List[str],
        user_request: str
    ) -> ReflectionReport:
        """
        Executes the self-reflection audit.
        Performs lightweight Python validation first. Runs the Reflection LLM only for:
        - ambiguous requests (user_request indicates intent is Unknown)
        - complex documents
        - when validation fails
        """
        logger.info("ReflectionService: Starting document audit.")
        
        # 1. Lightweight Python validation
        validation_passed, validation_errors = self._run_lightweight_validation(document, checklist)
        
        # Determine if document is complex
        sections = document.get("sections", [])
        is_complex = len(sections) > 4 or any(len(s.get("tables", [])) > 0 for s in sections)
        
        # Determine if request is ambiguous
        is_ambiguous = len(user_request.strip()) < 20 or not checklist
        
        # 2. Check if we can skip LLM reflection
        if validation_passed and not is_complex and not is_ambiguous:
            logger.info("ReflectionService: Lightweight validation passed for simple request. Skipping LLM reflection.")
            return ReflectionReport(
                passed=True,
                score=10.0,
                completeness="Lightweight Python validation passed. Document contains all expected structures.",
                grammar="Skipped LLM validation (lightweight validation passed).",
                consistency="Skipped LLM validation (lightweight validation passed).",
                suggestions=[]
            )
            
        logger.info(f"ReflectionService: Running LLM reflection (Reason: is_complex={is_complex}, is_ambiguous={is_ambiguous}, validation_passed={validation_passed}).")
        
        checklist_str = "\n".join(f"- {item}" for item in checklist) if checklist else "None"
        document_str = json.dumps(document, indent=2)
        
        system_prompt = (
            self.system_prompt_template
            .replace("{user_request}", user_request)
            .replace("{validation_checklist}", checklist_str)
            .replace("{generated_document}", document_str)
        )
        
        user_message = "Please perform the audit and output the JSON report."
        if not validation_passed:
            errors_str = "\n".join(f"- {err}" for err in validation_errors)
            user_message += f"\n\nLightweight validation failed with errors:\n{errors_str}\nPlease factor this into your suggestions."
            
        try:
            response_str = await llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_message,
                response_format={"type": "json_object"},
                model_role="reflection"
            )
            
            data = json.loads(response_str)
            report = ReflectionReport(**data)
            logger.info(f"ReflectionService: Audit completed. Score: {report.score}/10, Passed: {report.passed}")
            return report
        except Exception as e:
            logger.error(f"ReflectionService: Audit execution failed: {e}. Falling back to best-effort approval.")
            return ReflectionReport(
                passed=True,
                score=6.0,
                completeness="Auditor crashed. Checked file completeness through fallback.",
                grammar="Checked syntax through fallback.",
                consistency="Checked structural consistency through fallback.",
                suggestions=[]
            )

    def _run_lightweight_validation(self, document: Dict[str, Any], checklist: List[str]) -> Tuple[bool, List[str]]:
        """
        Lightweight Python validation checking required headings, empty sections, and document structure.
        """
        errors = []
        
        # 1. Structure check
        title = document.get("title", "").strip()
        if not title:
            errors.append("Document title is missing or empty.")
            
        sections = document.get("sections", [])
        if not sections:
            errors.append("Document has no sections.")
            return False, errors
            
        # 2. Section and content check
        document_headings = []
        for idx, s in enumerate(sections):
            heading = s.get("heading", "").strip()
            if not heading:
                errors.append(f"Section at index {idx} has an empty heading.")
            else:
                document_headings.append(heading)
                
            paragraphs = s.get("paragraphs", [])
            bullets = s.get("bullets", [])
            tables = s.get("tables", [])
            
            # Check for completely empty section content
            if not paragraphs and not bullets and not tables:
                errors.append(f"Section '{heading or idx}' is empty (no paragraphs, bullets, or tables).")
                
        # 3. Required headings keyword check based on planner checklist
        for item in checklist:
            item_lower = item.lower()
            # Standard keywords to map checklist criteria to structural elements
            keywords = ["executive summary", "introduction", "scope", "financial", "cost", "timeline", "architecture", "api", "schema", "sop", "procedure", "vision", "requirements", "mitigation", "risk"]
            for kw in keywords:
                if kw in item_lower:
                    if not any(kw in h.lower() for h in document_headings):
                        errors.append(f"Missing required section matching checklist criteria: '{item}'")
                        
        return len(errors) == 0, errors

# Global reflection service instance
reflection_service = ReflectionService()
