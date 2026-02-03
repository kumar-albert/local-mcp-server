import json
import os
from src.mcp_client import MCPClient
from src.utils import extract_json
from src.aws_bedrock import think_with_bedrock

mcpClient = MCPClient()
async def run_agent():
    await mcpClient.connect_server()

    SYSTEM_PROMPT = """
    You are a DevOps monitoring agent.

    You can call tools using JSON only.

    Available tools:
    1. list_clusters() -> list[str]: Lists all EKS clusters.
    2. get_cpu_usage(cluster_name: str) -> int: Gets the CPU usage for a specific cluster.
    3. send_alert(message: str) -> str: Sends an alert message.

    Rules:
    - Monitor CPU usage of all clusters.
    - If CPU > 70, send alert.
    - Decide one action at a time and each cluster separately.
    - Use tools to get data and send alerts.
    - Think step-by-step.
    - When finished, respond with:
    {"action": "done", "summary": "..."}
    - Tool call format:
    {"action": "tool", "name": "<tool_name>", "args": {...}}
    - Always return a valid JSON for single tool.
    - revalidate the output json with json.loads() and return it.
    """

    conversation = [
        {
            "role": "user",
            "content": [{"text": SYSTEM_PROMPT}],
        }
    ]
    
    while True:
        llm_response = think_with_bedrock(conversation)
        conversation.append({
            "role": "assistant",
            "content": [{"text": json.dumps(llm_response)}]
        })
        # Done
        if llm_response["action"] == "done":
            print("✅ Final Summary:")
            print(llm_response["summary"])
            os._exit(0)
 
        # Tool call
        if llm_response["action"] == "tool":
            tool_name = llm_response["name"]
            tool_args = llm_response.get("args", {})

            result = await mcpClient.call_tool(
                tool_name, tool_args
            )

            tool_output = json.loads(json.dumps(result.structuredContent))

            conversation.append({
                "role": "user",
                "content": [{"text": f"{tool_name}({tool_args}) called and result is: {tool_output}"}]
            })
            
async def start_agent():
    await run_agent()
