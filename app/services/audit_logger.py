import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any
from app.schemas.planner import PlannerOutput
from app.schemas.reflection import ReflectionReport
from app.schemas.agent import ToolExecutionLog
from app.core.logging import logger

class AuditLogger:
    """Service to persist generated Word documents and write system telemetry audits to a JSON database file."""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
        self.docs_dir = os.path.join(self.workspace_root, "generated_docs")
        self.log_dir = os.path.join(self.workspace_root, "data", "logs")
        self.audit_file = os.path.join(self.log_dir, "execution_audit.json")

    def log_execution(
        self,
        prompt: str,
        plan: PlannerOutput,
        execution_logs: List[ToolExecutionLog],
        reflection_report: ReflectionReport,
        docx_base64: str,
        duration: float
    ) -> str:
        """
        Decodes base64 document and saves it locally. Records execution metrics
        such as query, intent, tool outcomes, and latency to the JSON log file.
        
        :return: Path to the saved document.
        """
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        iso_timestamp = datetime.now().isoformat()
        
        # 1. Ensure folders exist
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 2. Save generated DOCX file
        intent_sanitized = plan.intent.replace(" ", "_").replace("/", "_")
        doc_filename = f"{intent_sanitized}_{timestamp_str}.docx"
        doc_path = os.path.join(self.docs_dir, doc_filename)
        
        try:
            doc_bytes = base64.b64decode(docx_base64)
            with open(doc_path, "wb") as f:
                f.write(doc_bytes)
            logger.info(f"AuditLogger: Saved document file to '{doc_path}'")
        except Exception as e:
            logger.error(f"AuditLogger: Failed to save DOCX file: {e}")
            doc_path = "FAILED_TO_SAVE"
            
        # 3. Formulate JSON audit log record
        record = {
            "timestamp": iso_timestamp,
            "query": prompt,
            "intent": plan.intent,
            "goal": plan.goal,
            "latency_seconds": round(duration, 4),
            "tools_executed": [
                {
                    "tool_name": log.tool_name,
                    "inputs": log.inputs,
                    "success": log.success,
                    "message": log.message
                }
                for log in execution_logs
            ],
            "reflection_score": reflection_report.score,
            "reflection_passed": reflection_report.passed,
            "document_path": doc_path
        }
        
        # 4. Append record to audit log JSON file
        audit_data = []
        if os.path.exists(self.audit_file):
            try:
                with open(self.audit_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        audit_data = json.loads(content)
                        if not isinstance(audit_data, list):
                            audit_data = [audit_data]
            except Exception as e:
                logger.error(f"AuditLogger: Failed to read existing audit log file: {e}. Rewriting index.")
                audit_data = []
                
        audit_data.append(record)
        
        try:
            with open(self.audit_file, "w", encoding="utf-8") as f:
                json.dump(audit_data, f, indent=2)
            logger.info(f"AuditLogger: Append execution record to '{self.audit_file}' successfully.")
        except Exception as e:
            logger.error(f"AuditLogger: Failed to write audit log record: {e}")
            
        return doc_path

# Global audit logger instance
audit_logger = AuditLogger()
