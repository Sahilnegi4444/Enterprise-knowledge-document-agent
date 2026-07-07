from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class AgentRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="The business request or instructions for the document generation",
        examples=["Create a technical design for our database migration. We need to migrate from PostgreSQL to DynamoDB. Discuss schema mapping, cost estimation, and migration steps."]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional execution parameters or context metadata",
        examples=[{"author": "Sahil", "version": "1.0.0"}]
    )

class ToolExecutionLog(BaseModel):
    tool_name: str = Field(..., description="Name of the tool executed")
    inputs: Dict[str, Any] = Field(..., description="Inputs provided to the tool")
    success: bool = Field(..., description="Whether the tool execution succeeded")
    message: str = Field(..., description="Detailed message or log from execution")

class AgentResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the request completed successfully")
    goal: str = Field(..., description="The parsed goal statement formulated by the planner")
    intent: str = Field(..., description="The classified document category (e.g. Technical Design, Proposal)")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made by the planning system")
    tools_executed: List[ToolExecutionLog] = Field(default_factory=list, description="Logs of tools chosen and executed")
    reflection_report: Dict[str, Any] = Field(..., description="Results of self-reflection quality check")
    docx_base64: str = Field(..., description="Base64-encoded bytes of the generated .docx file")
    message: str = Field(..., description="Summary message of the operation status")
