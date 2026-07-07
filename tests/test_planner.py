import pytest
from unittest.mock import patch
from app.planner.planner import planner
from app.schemas.planner import PlannerOutput
from app.core.exceptions import LLMException

@pytest.mark.asyncio
async def test_planner_creation_mock():
    # Test LLM planning (which triggers the mock response in LLMClient because of key)
    plan = await planner.create_plan("Create a Business Proposal for Project Alpha", "Proposal")
    assert isinstance(plan, PlannerOutput)
    assert plan.intent == "Proposal"
    assert "rag_tool" in plan.required_tools
    assert len(plan.execution_plan) > 0

@pytest.mark.asyncio
async def test_planner_deterministic_fallback():
    # Force generator failure to test fallback mechanism
    with patch("app.core.llm.llm_client.generate", side_effect=LLMException("Inference failure")):
        plan = await planner.create_plan(
            "Create a database Migration Guide from PG to DynamoDB", 
            "Migration Guide"
        )
        assert isinstance(plan, PlannerOutput)
        assert plan.intent == "Migration Guide"
        assert "rag_tool" in plan.required_tools
        assert "LLM reasoning is unavailable" in plan.assumptions[0]
        # Since 'Migration Guide' has 'migrate' which matches keyword triggers, search_tool is also added
        assert "search_tool" in plan.required_tools
