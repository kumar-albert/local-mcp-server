from mcp.server.fastmcp import FastMCP

mcp = FastMCP("eks-monitor")

@mcp.tool()
def list_clusters() -> list[str]:
    return ["eks-prod", "eks-staging"]

@mcp.tool()
def get_cpu_usage(cluster: str) -> int:
    return {
        "eks-prod": 82,
        "eks-staging": 45
    }.get(cluster, 0)

@mcp.tool()
def send_alert(message: str) -> str:
    print(f"🚨 ALERT: {message}")
    return "alert_sent"

if __name__ == "__main__":
    mcp.run()
