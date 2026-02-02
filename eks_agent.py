import asyncio
import json
import ollama
from contextlib import AsyncExitStack

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"

SYSTEM_PROMPT = """
You are a DevOps monitoring agent.

You can call tools using JSON only.

Available tools:
1. list_clusters()
2. get_cpu_usage(cluster)
3. send_alert(message)

Rules:
- If CPU > 70, send alert.
- Decide one action at a time.
- When finished, respond with:
  {"action": "done", "summary": "..."}
- Tool call format:
  {"action": "tool", "name": "<tool_name>", "args": {...}}
"""


async def connect_server():
    serverParams = StdioServerParameters(
        command="python3",
        args=["eks_server.py"]
    )
    asyncExitStack = AsyncExitStack()
    stdio_transport = await asyncExitStack.enter_async_context(stdio_client(serverParams))
    client = await asyncExitStack.enter_async_context(ClientSession(stdio_transport[0], stdio_transport[1]))
    await client.initialize()
    return client



def call_llama(prompt: str) -> dict:
    model_output = ollama.generate(
        model=MODEL,
        prompt=prompt,
    )
    text = model_output.response
    print(text)
    print("===========")
    try:
        return json.loads(text)
    except:
        json_response = ollama.generate(
            model=MODEL,
            prompt=f"""
    You are a JSON extraction engine.

    Task:
    Extract the JSON object from the input text.

    Rules:
    - Return ONLY valid JSON.
    - Do NOT include explanations or markdown.
    - If no JSON exists, return {{}}.

    Input:
    {prompt}
    """)
        return json.loads(json_response.response)



async def run_agent(user_input: str):

    conversation = f"""
SYSTEM:
{SYSTEM_PROMPT}

USER:
{user_input}
"""
    
    while True:
        llm_response = call_llama(conversation)
        # Done
        if llm_response["action"] == "done":
            print("✅ Final Summary:")
            print(llm_response["summary"])
            break

        # Tool call
        if llm_response["action"] == "tool":
            tool_name = llm_response["name"]
            tool_args = llm_response.get("args", {})
            client = await connect_server()

            result = await client.call_tool(
                tool_name, tool_args
            )

            tool_output = result.content[0].text

            conversation += f"""
TOOL_CALL:
{tool_name}({tool_args})

TOOL_RESULT:
{tool_output}
"""
            
async def main():
    await run_agent(
        "Check CPU usage of all clusters and alert if high"
    )
asyncio.run(
    main()
)
