"""
MCP Client Manager

Manages connection to MCP search server (Brave Search).
Note: Memory is now handled by ChromaDB vector service (see services/memory_service.py)
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client, StdioServerParameters

logger = logging.getLogger(__name__)

class MCPClientManager:
    """Manages MCP server connections and tool calls."""

    def __init__(self):
        self.search_session: Optional[ClientSession] = None
        self.search_context = None
        self.initialized = False

    async def initialize(self):
        """Initialize connection to MCP search server."""
        if self.initialized:
            return

        logger.info("Initializing MCP search client...")

        try:
            # Connect to search server only
            await self._connect_search_server()

            self.initialized = True
            logger.info("✅ MCP search client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MCP search client: {e}")
            # Continue without MCP if initialization fails
            self.initialized = False

    async def _connect_search_server(self):
        """Connect to the Brave Search MCP server."""
        try:
            server_script = Path(__file__).parent / "servers" / "search_server.py"

            if not server_script.exists():
                logger.warning(f"Search server script not found: {server_script}")
                self.search_session = None
                self.search_context = None
                return

            # Create server parameters
            server_params = StdioServerParameters(
                command="python3",
                args=[str(server_script)],
                env=None
            )

            # Store the context manager and enter it
            self.search_context = stdio_client(server_params)
            read_stream, write_stream = await self.search_context.__aenter__()
            self.search_session = ClientSession(read_stream, write_stream)

            # Initialize the session
            await self.search_session.__aenter__()

            # Complete the MCP initialization handshake
            await self.search_session.initialize()

            logger.info("✅ Connected to search MCP server")

        except Exception as e:
            logger.warning(f"⚠️  Could not connect to search server (web search disabled): {e}")
            logger.warning("   This is OK - the app will work without web search")
            self.search_session = None
            self.search_context = None


    async def web_search(self, query: str, count: int = 3, api_key: Optional[str] = None) -> Optional[str]:
        """
        Perform a web search using Brave Search.

        Args:
            query: Search query
            count: Number of results (1-10)
            api_key: Brave Search API key (from user settings)

        Returns:
            Search results as formatted text, or None if search failed/unavailable
        """
        if not self.search_session:
            logger.debug("Search session not available - returning None")
            return None

        if not api_key:
            logger.warning("⚠️  No API key provided for web search")
            return None

        # Log search request for safety/transparency
        logger.info("=" * 60)
        logger.info("WEB SEARCH REQUEST (sent to Brave)")
        logger.info(f"Query: {query}")
        logger.info(f"Result count: {count}")
        logger.info("=" * 60)

        try:
            result = await self.search_session.call_tool(
                "brave_web_search",
                arguments={"query": query, "count": count, "api_key": api_key}
            )

            if result and result.content:
                # Extract text from the result
                if hasattr(result.content[0], 'text'):
                    response_text = result.content[0].text
                    # Check if it's an error message about missing API key
                    if "BRAVE_API_KEY not configured" in response_text:
                        logger.warning("⚠️  Brave API key not configured - skipping search")
                        return None
                    return response_text
                return str(result.content[0])

            return None

        except Exception as e:
            logger.warning(f"⚠️  Web search failed (continuing without search): {e}")
            return None


    async def shutdown(self):
        """Clean shutdown of MCP search session."""
        try:
            if self.search_session:
                await self.search_session.__aexit__(None, None, None)
            if self.search_context:
                await self.search_context.__aexit__(None, None, None)

            logger.info("MCP search session closed")

        except Exception as e:
            logger.error(f"Error during MCP shutdown: {e}")

# Global instance
_mcp_client: Optional[MCPClientManager] = None

def get_mcp_client() -> MCPClientManager:
    """Get or create the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClientManager()
    return _mcp_client

async def initialize_mcp():
    """Initialize the global MCP client."""
    client = get_mcp_client()
    await client.initialize()

async def shutdown_mcp():
    """Shutdown the global MCP client."""
    if _mcp_client:
        await _mcp_client.shutdown()
