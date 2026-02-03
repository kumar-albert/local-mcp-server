
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-server", stateless_http=False, json_response=True)

@mcp.tool()
def list_clusters() -> list[str]:
    return ["eks-prod", "eks-staging", "eks-dev"]

@mcp.tool()
def get_cpu_usage(cluster_name: str) -> int:
    return {
        "eks-prod": 82,
        "eks-staging": 45,
        "eks-dev": 160
    }.get(cluster_name, 0)

@mcp.tool()
def send_alert(message: str) -> str:
    print(f"🚨 ALERT: {message}")
    return "alert_sent"

if __name__ == "__main__":
    mcp.run("streamable-http")
