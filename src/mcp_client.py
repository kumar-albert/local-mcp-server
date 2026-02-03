from contextlib import AsyncExitStack
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from typing import Optional


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    
    async def connect_server(self) -> ClientSession:
        read_stream, write_stream, get_session_id = await self.exit_stack.enter_async_context(
            streamablehttp_client(url="http://localhost:8000/mcp")
        )
        self.session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await self.session.initialize()
        return self.session
    
    async def call_tool(self, tool_name: str, tool_args: dict):
        if self.session is None:
            raise Exception("Session not initialized. Call connect_server() first.")
        
        result = await self.session.call_tool(
            tool_name,
            tool_args
        )
        return result
    
    async def list_tools(self) -> list[str]:
        if self.session is None:
            raise Exception("Session not initialized. Call connect_server() first.")
        
        response = await self.session.list_tools()
        methods = []
        for tool in response.tools:
            methods.append(f"{tool.name}({', '.join(tool.inputSchema['properties'].keys())})")
        return methods