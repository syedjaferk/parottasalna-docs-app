"""BONUS (MCP intro) - LangChain agent consuming tools from an MCP server."""
import asyncio
from pathlib import Path

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from model import model


async def main():
    client = MultiServerMCPClient(
        {
            "utils": {
                "transport": "stdio",
                "command": "python",
                "args": [str(Path(__file__).parent / "mcp_server.py")],
            }
        }
    )
    tools = await client.get_tools()          # tools discovered from the server
    print("Discovered:", [t.name for t in tools])

    agent = create_agent(model, tools)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Add 21 and 21, then reverse the word 'parottasalna'."}]}
    )
    for m in result["messages"]:
        m.pretty_print()


asyncio.run(main())
