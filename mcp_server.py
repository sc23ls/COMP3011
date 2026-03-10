from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("forex-analytics")
API_BASE_URL = "http://127.0.0.1:8000"


def call_api(endpoint: str, params: dict):
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            timeout=10
        )
        response.raise_for_status()
    except requests.Timeout:
        return {"error": "API request timed out"}
    except requests.RequestException as exc:
        return {"error": f"API request failed: {exc}"}

    try:
        return response.json()
    except ValueError:
        return {"error": "API response was not valid JSON"}


@mcp.tool()
def convert_currency(base: str, target: str, amount: float):
    """Convert currency using the API"""
    return call_api(
        "/convert",
        {"base": base, "target": target, "amount": amount}
    )


@mcp.tool()
def detect_trend(base: str, target: str):
    """Detect FX trend"""
    return call_api(
        "/trend",
        {"base": base, "target": target}
    )


@mcp.tool()
def calculate_volatility(base: str, target: str):
    """Calculate FX volatility"""
    return call_api(
        "/volatility",
        {"base": base, "target": target}
    )


if __name__ == "__main__":
    mcp.run()
