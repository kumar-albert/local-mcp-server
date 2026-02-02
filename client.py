import asyncio
import ollama
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
import json


MODEL = "llama3.1"

class MCPClient:
    def __init__(self):
        self.session: ClientSession = None
        self.tools = []
        self.exit_stack = AsyncExitStack()


    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.strip().lower() == '':
                    continue
                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print(response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"]
        )
        # Connect to MCP server
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()
        self.tools = await self.session.list_tools()

    async def process_query(self, query: str) -> str:
        system_prompt = f"""
You are an AI agent.
You have access to tools.

TOOLS:
{self.tools}

If a tool is needed, respond ONLY with json in the format   :
{{"tool": "tool_name", "arguments": {...}}}
"""
        user_prompt = query # "What is the weather today in TX?"
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )

        content = response["message"]["content"]

        # If tool requested
        if content.startswith("{"):
            call = json.loads(content)

            result = await self.session.call_tool(
                call["tool"],
                call["arguments"]
            )
        else:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": """
Extract json from this text and return as json only. Do not include any other text.
"""},
                    {"role": "user", "content": content},
                ]
            )
            content = response["message"]["content"]
            call = json.loads(content)

            result = await self.session.call_tool(
                call["tool"],
                call["arguments"]
            )

        return result.structuredContent['result']

async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())
