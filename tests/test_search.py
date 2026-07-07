import pytest
from app.tools.search_tool import SearchTool

@pytest.mark.asyncio
async def test_search_tool_mock():
    tool = SearchTool()
    assert tool.name == "search_tool"
    assert "web" in tool.description.lower()
    
    # Test execution in mock mode (which is forced in conftest.py env vars)
    res = await tool.execute({"query": "FastAPI async performance"})
    assert res["success"] is True
    assert len(res["results"]) > 0
    assert "tavily" in res["results"][0]["url"] or "example" in res["results"][0]["url"]
    assert len(res["results"][0]["content"]) > 0

@pytest.mark.asyncio
async def test_search_tool_missing_query():
    tool = SearchTool()
    res = await tool.execute({})
    assert res["success"] is False
    assert "missing" in res["error"].lower()
