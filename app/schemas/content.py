from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Table(BaseModel):
    headers: List[str] = Field(default_factory=list, description="Column names for the table")
    rows: List[List[str]] = Field(default_factory=list, description="List of rows, where each row matches header length")

class Section(BaseModel):
    heading: str = Field(..., description="Primary heading for this section (e.g. '1. Introduction')")
    subheading: Optional[str] = Field(None, description="Optional secondary heading (e.g. '1.1 Problem Statement')")
    paragraphs: List[str] = Field(default_factory=list, description="Prose content paragraphs")
    bullets: List[str] = Field(default_factory=list, description="Bullet list items")
    tables: List[Table] = Field(default_factory=list, description="Tabular data structures")
    references: List[str] = Field(default_factory=list, description="Citations, links or document references")

class StructuredDocument(BaseModel):
    title: str = Field(..., description="Main title of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generic metadata key-value store (e.g. Author, Version, Date)")
    sections: List[Section] = Field(..., description="Hierarchical list of document sections")
