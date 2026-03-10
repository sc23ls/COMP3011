from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("forex-analytics")


@mcp.tool()
def convert_currency(base: str, target: str, amount: float):
    """Convert currency using the API"""

    r = requests.get(
        "http://127.0.0.1:8000/convert",
        params={"base": base, "target": target, "amount": amount}
    )

    return r.json()


@mcp.tool()
def detect_trend(base: str, target: str):
    """Detect FX trend"""

    r = requests.get(
        "http://127.0.0.1:8000/trend",
        params={"base": base, "target": target}
    )

    return r.json()


@mcp.tool()
def calculate_volatility(base: str, target: str):
    """Calculate FX volatility"""

    r = requests.get(
        "http://127.0.0.1:8000/volatility",
        params={"base": base, "target": target}
    )

    return r.json()


if __name__ == "__main__":
    mcp.run()