
import asyncio
# from src.eks_agent import start_agent
from src.agent_v1 import start_agent


if __name__ == "__main__":
    asyncio.run(start_agent())