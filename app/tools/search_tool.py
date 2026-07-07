from typing import Dict, Any, List
import httpx
from app.tools.base import BaseTool
from app.config.settings import settings
from app.core.logging import logger
from app.core.retry import async_retry

class SearchTool(BaseTool):
    """Tool to search the web using Tavily Search API for real-time market data or guidelines."""
    
    @property
    def name(self) -> str:
        return "search_tool"
        
    @property
    def description(self) -> str:
        return "Searches the web via Tavily to retrieve up-to-date facts, statistics, and industry standards."
        
    @async_retry(retries=3, delay=1.0, backoff=2.0)
    async def _call_tavily(self, query: str) -> Dict[str, Any]:
        """Performs async HTTP post to Tavily API with retry safety."""
        api_key = settings.TAVILY_API_KEY
        
        if not api_key or api_key == "mock_tavily_api_key":
            logger.info("SearchTool: Running in MOCK mode due to missing/mock API key.")
            return {
                "results": [
                    {
                        "title": f"Latest Trends in {query}",
                        "url": "https://example.com/trends",
                        "content": f"Industry standards for {query} indicate a transition to event-driven architectures. Microservice coupling should be minimized, and caching headers should align with performance models."
                    },
                    {
                        "title": f"Best Practices for {query}",
                        "url": "https://example.com/best-practices",
                        "content": f"Security protocols require encrypting traffic in transit using TLS 1.3. Service SLAs should guarantee 99.99% availability with automatic failover."
                    }
                ]
            }
            
        logger.info(f"SearchTool: Performing live Tavily search for: '{query}'")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic"
                }
            )
            if response.status_code != 200:
                logger.error(f"SearchTool: Tavily API returned status {response.status_code}. Response: {response.text}")
            response.raise_for_status()
            return response.json()

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query")
        if not query:
            logger.warning("SearchTool: Missing 'query' parameter.")
            return {"success": False, "error": "Missing input parameter: 'query'", "results": []}
            
        try:
            data = await self._call_tavily(query)
            raw_results = data.get("results", [])
            
            results = []
            for item in raw_results:
                results.append({
                    "title": item.get("title", "No Title"),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })
                
            return {
                "success": True,
                "results": results
            }
        except Exception as e:
            logger.error(f"SearchTool failed: {e}")
            return {
                "success": False,
                "error": f"Web search client failed: {str(e)}",
                "results": []  # Fallback gracefully
            }
