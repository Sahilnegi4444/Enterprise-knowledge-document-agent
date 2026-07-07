from pydantic import BaseModel, Field
from typing import List

class ReflectionReport(BaseModel):
    passed: bool = Field(..., description="True if the document is ready for generation, False if it needs revision")
    score: float = Field(..., description="Quality score from 1.0 to 10.0")
    completeness: str = Field(..., description="Details on check against goals and planner validation checklist")
    grammar: str = Field(..., description="Check for grammar, typos, and enterprise tone")
    consistency: str = Field(..., description="Check for internal contradictions or redundant content")
    suggestions: List[str] = Field(default_factory=list, description="Bullet list of concrete revisions if passed is False")
