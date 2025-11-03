"""
Brave Search MCP Server

Provides web search capability using Brave Search API.
The AI can use this when it doesn't know information about current events,
factual questions, or topics outside its training data.
"""

import asyncio
import os
from typing import Any
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
search_server = Server("brave-search")

# Get API key from environment
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")

# Check if API key is available
if not BRAVE_API_KEY:
    logger.warning("⚠️  BRAVE_API_KEY not set - web search will be disabled")
    logger.warning("   Set BRAVE_API_KEY in .env to enable web search")
    SEARCH_AVAILABLE = False
else:
    SEARCH_AVAILABLE = True
    logger.info(f"✅ Brave Search API key found (length: {len(BRAVE_API_KEY)})")

@search_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available search tools."""
    return [
        Tool(
            name="brave_web_search",
            description="Search the web using Brave Search. Use this when the user asks about current events, factual information, or topics you're uncertain about. Returns recent, relevant web results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (what to search for)"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to return (1-10, default 3)",
                        "default": 3
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Brave Search API key (optional, can be provided from user settings)"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@search_server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[TextContent]:
    """Handle tool execution requests."""

    if name != "brave_web_search":
        raise ValueError(f"Unknown tool: {name}")

    # Get API key from arguments (user settings) or fall back to env variable
    api_key = arguments.get("api_key") or BRAVE_API_KEY

    if not api_key:
        return [TextContent(
            type="text",
            text="Error: BRAVE_API_KEY not configured. Please add your API key in Settings."
        )]

    query = arguments.get("query")
    count = min(arguments.get("count", 3), 10)

    if not query:
        raise ValueError("Missing required argument: query")

    # Log what is being sent to Brave for safety/transparency
    logger.info("=" * 60)
    logger.info("BRAVE SEARCH REQUEST")
    logger.info(f"Query: {query}")
    logger.info(f"Count: {count}")
    logger.info("=" * 60)

    try:
        # Call Brave Search API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": api_key
                },
                params={
                    "q": query,
                    "count": count
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

        # Extract results
        results = data.get("web", {}).get("results", [])

        if not results:
            return [TextContent(
                type="text",
                text=f"No results found for: {query}"
            )]

        # Format results
        formatted_results = []
        for idx, result in enumerate(results[:count], 1):
            title = result.get("title", "No title")
            description = result.get("description", "No description")
            url = result.get("url", "")

            formatted_results.append(
                f"{idx}. {title}\n   {description}\n   URL: {url}"
            )

        result_text = f"Search results for '{query}':\n\n" + "\n\n".join(formatted_results)

        return [TextContent(
            type="text",
            text=result_text
        )]

    except httpx.HTTPStatusError as e:
        logger.error(f"Brave API error: {e}")
        return [TextContent(
            type="text",
            text=f"Search failed: {str(e)}"
        )]
    except Exception as e:
        logger.error(f"Search error: {e}")
        return [TextContent(
            type="text",
            text=f"Search error: {str(e)}"
        )]

async def main():
    """Run the search MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await search_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="brave-search",
                server_version="1.0.0",
                capabilities=search_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())