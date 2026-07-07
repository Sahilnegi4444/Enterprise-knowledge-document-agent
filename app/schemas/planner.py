from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PlanStep(BaseModel):
    step: int = Field(..., description="The sequence order of the step")
    tool: str = Field(..., description="The name of the tool to execute")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="The inputs for the tool execution")
    reason: str = Field(..., description="The reason why this tool and these inputs are selected")

class PlannerOutput(BaseModel):
    goal: str = Field(..., description="The goal formulated from user prompt")
    intent: str = Field(..., description="The classified document category")
    assumptions: List[str] = Field(default_factory=list, description="Contextual assumptions")
    execution_plan: List[PlanStep] = Field(default_factory=list, description="List of structured execution steps")
    required_tools: List[str] = Field(default_factory=list, description="Unique names of tools that will run")
    validation_checklist: List[str] = Field(default_factory=list, description="Specific elements to verify in self-reflection")
    expected_output: str = Field(..., description="Visual outline of the target sections")
