import pytest
from unittest.mock import patch, AsyncMock
from app.services.reflection_service import reflection_service
from app.schemas.reflection import ReflectionReport
from app.schemas.agent import AgentRequest
from app.services.agent_orchestrator import agent_orchestrator

@pytest.mark.asyncio
async def test_reflection_grading_mock():
    document_data = {
        "title": "Business Proposal: Project Alpha",
        "metadata": {"author": "Tester"},
        "sections": [
            {
                "heading": "1. Executive Summary",
                "paragraphs": ["Content paragraph."],
                "bullets": [],
                "tables": [],
                "references": []
            }
        ]
    }
    
    report = await reflection_service.reflect(
        document=document_data,
        checklist=["Include Executive Summary"],
        user_request="Create business proposal for Project Alpha"
    )
    
    assert isinstance(report, ReflectionReport)
    assert report.passed is True
    assert report.score >= 5.0

@pytest.mark.asyncio
async def test_reflection_correction_loop():
    # Setup mock reports where the first reflect audit returns passed=False, and the second returns passed=True
    report_fail = ReflectionReport(
        passed=False,
        score=5.0,
        completeness="Missing timeline section.",
        grammar="OK",
        consistency="OK",
        suggestions=["Add a project timeline chapter."]
    )
    report_pass = ReflectionReport(
        passed=True,
        score=9.0,
        completeness="All sections included.",
        grammar="OK",
        consistency="OK",
        suggestions=[]
    )
    
    # We will patch reflection_service.reflect to return fail then pass
    with patch.object(
        reflection_service, 
        "reflect", 
        side_effect=[report_fail, report_pass]
    ) as mock_reflect, patch(
        "app.services.content_generator.content_generator.generate_document",
        new_callable=AsyncMock
    ) as mock_gen:
        # Mock generator return value
        from app.schemas.content import StructuredDocument
        mock_doc = StructuredDocument(
            title="Business Proposal",
            metadata={},
            sections=[]
        )
        mock_gen.return_value = mock_doc
        
        request = AgentRequest(prompt="Create proposal")
        
        # Run orchestrator
        response = await agent_orchestrator.process_request(request)
        
        # Verify it called mock_gen TWICE (once initially, once for correction)
        assert mock_gen.call_count == 2
        # Verify it called mock_reflect TWICE
        assert mock_reflect.call_count == 2
        assert response.success is True
