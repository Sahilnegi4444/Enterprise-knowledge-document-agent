import pytest
from app.tools.registry import tool_registry
from app.router.router import router
from app.schemas.planner import PlannerOutput, PlanStep
from app.core.exceptions import ToolExecutionException

def test_tool_registry_operations():
    tools = tool_registry.list_tools()
    assert "rag_tool" in tools
    assert "search_tool" in tools
    assert "reflection_tool" in tools
    assert "document_tool" in tools
    
    with pytest.raises(ToolExecutionException):
        tool_registry.get_tool("non_existent_tool")

@pytest.mark.asyncio
async def test_router_execution_success():
    # Construct a plan
    plan = PlannerOutput(
        goal="Test running tools",
        intent="SOP",
        assumptions=["None"],
        execution_plan=[
            PlanStep(step=1, tool="rag_tool", inputs={"query": "SOP template"}, reason="Fetch template"),
            PlanStep(step=2, tool="search_tool", inputs={"query": "latest standards"}, reason="Web lookups")
        ],
        required_tools=["rag_tool", "search_tool"],
        validation_checklist=["Check 1"],
        expected_output="Outline"
    )
    
    logs, outputs = await router.execute_plan(plan)
    
    assert len(logs) == 2
    assert logs[0].tool_name == "rag_tool"
    assert logs[0].success is True
    assert logs[1].tool_name == "search_tool"
    assert logs[1].success is True
    
    assert "rag_tool" in outputs
    assert "search_tool" in outputs
    assert outputs["rag_tool"]["success"] is True
    assert outputs["search_tool"]["success"] is True

@pytest.mark.asyncio
async def test_router_execution_with_missing_tool():
    plan = PlannerOutput(
        goal="Test running missing tool",
        intent="SOP",
        assumptions=["None"],
        execution_plan=[
            PlanStep(step=1, tool="invalid_tool_name", inputs={}, reason="Invalid")
        ],
        required_tools=["invalid_tool_name"],
        validation_checklist=["Check 1"],
        expected_output="Outline"
    )
    
    logs, outputs = await router.execute_plan(plan)
    assert len(logs) == 1
    assert logs[0].success is False
    assert "Resolution failed" in logs[0].message or "lookup" in logs[0].message
