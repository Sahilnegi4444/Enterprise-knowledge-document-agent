from typing import Dict, Any, List
import time
from app.schemas.agent import AgentRequest, AgentResponse, ToolExecutionLog
from app.services.validation_service import validation_service
from app.services.intent_detector import intent_detector
from app.planner.planner import planner
from app.router.router import router
from app.services.context_builder import context_builder
from app.services.content_generator import content_generator
from app.services.reflection_service import reflection_service
from app.tools.registry import tool_registry
from app.core.logging import logger, log_step
from app.core.exceptions import AgentException, DocxGenerationException

class AgentOrchestrator:
    """Core orchestrator that coordinates validation, intent detection, planning, tool routing, generation, reflection, and document assembly."""
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        start_time = time.time()
        log_step("Request received", "START", f"Prompt: {request.prompt[:100]}...")
        
        # 1. Validation
        try:
            validation_service.validate(request.model_dump())
            log_step("Validation complete", "SUCCESS")
        except AgentException as ae:
            log_step("Validation complete", "FAILED", ae.message)
            raise
            
        # 2. Intent Detection
        intent = intent_detector.detect_intent(request.prompt)
        log_step("Intent detection complete", "SUCCESS", f"Detected: {intent}")
        
        # 3. Planning
        log_step("Planner started", "RUNNING")
        plan = await planner.create_plan(request.prompt, intent)
        log_step("Planner completed", "SUCCESS", f"Goal: {plan.goal}")
        
        # 4. Tool Execution & Routing
        log_step("Tool execution", "RUNNING", f"Selected tools: {plan.required_tools}")
        execution_logs, tool_outputs = await router.execute_plan(plan)
        log_step("Tool execution", "SUCCESS", f"Ran {len(execution_logs)} tools.")
        
        # 5. Context Building
        rag_context, search_context, assumptions_str = context_builder.build_context(
            user_request=request.prompt,
            plan=plan,
            tool_outputs=tool_outputs
        )
        
        # 6. Content Generation
        log_step("Generation started", "RUNNING")
        document = await content_generator.generate_document(
            user_request=request.prompt,
            planner_output_json=plan.model_dump_json(),
            rag_context=rag_context,
            search_context=search_context,
            assumptions=assumptions_str
        )
        log_step("Generation completed", "SUCCESS")
        
        # 7. Self-Reflection Audit Loop (max 1 retry loop)
        log_step("Reflection started", "RUNNING")
        reflection_report = await reflection_service.reflect(
            document=document.model_dump(),
            checklist=plan.validation_checklist,
            user_request=request.prompt
        )
        
        # If audit fails and recommendations are present, trigger a correction iteration
        if not reflection_report.passed and reflection_report.suggestions:
            logger.info("AgentOrchestrator: Document failed initial reflection check. Initiating correction loop.")
            
            # Re-generate with suggestions
            document = await content_generator.generate_document(
                user_request=request.prompt,
                planner_output_json=plan.model_dump_json(),
                rag_context=rag_context,
                search_context=search_context,
                assumptions=assumptions_str,
                revisions=reflection_report.suggestions
            )
            
            # Re-audit
            reflection_report = await reflection_service.reflect(
                document=document.model_dump(),
                checklist=plan.validation_checklist,
                user_request=request.prompt
            )
            
        log_step("Reflection completed", "SUCCESS", f"Passed: {reflection_report.passed} | Score: {reflection_report.score}")
        
        # 8. Document Generation (DOCX base64 compilation via Tool Registry)
        log_step("Document generated", "RUNNING")
        try:
            document_tool = tool_registry.get_tool("document_tool")
            doc_result = await document_tool.execute({"document_data": document.model_dump()})
            docx_base64 = doc_result.get("docx_base64", "")
            
            if not doc_result.get("success", False) or not docx_base64:
                raise DocxGenerationException(
                    "Document generator tool completed but failed to compile binary stream."
                )
                
            log_step("Document generated", "SUCCESS")
        except Exception as e:
            log_step("Document generated", "FAILED", str(e))
            raise DocxGenerationException(f"Word document rendering pipeline failed: {str(e)}")
            
        # 9. API Response compilation and Telemetry Audit Logging
        duration = time.time() - start_time
        
        try:
            from app.services.audit_logger import audit_logger
            audit_logger.log_execution(
                prompt=request.prompt,
                plan=plan,
                execution_logs=execution_logs,
                reflection_report=reflection_report,
                docx_base64=docx_base64,
                duration=duration
            )
        except Exception as audit_err:
            logger.error(f"AgentOrchestrator: Telemetry logger failed: {audit_err}")
            
        message = f"Process completed successfully in {duration:.2f}s."
        log_step("Response sent", "SUCCESS", message)
        
        return AgentResponse(
            success=True,
            goal=plan.goal,
            intent=plan.intent,
            assumptions=plan.assumptions,
            tools_executed=execution_logs,
            reflection_report=reflection_report.model_dump(),
            docx_base64=docx_base64,
            document_data=document.model_dump(),
            message=message
        )

# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()
