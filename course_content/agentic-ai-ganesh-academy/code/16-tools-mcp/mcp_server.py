"""BONUS (MCP intro) - a tiny MCP server exposing tools over stdio."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("utils")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


if __name__ == "__main__":
    mcp.run(transport="stdio")
