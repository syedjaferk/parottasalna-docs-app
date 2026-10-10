"""
3. External API Tools - wrap a REST API as a tool.
Uses Open-Meteo (free, no API key): geocoding + weather forecast.

Golden rules for API tools:
  - always set a timeout
  - catch errors and return a readable message (never crash the agent)
  - return SMALL, clean data (not the whole JSON blob)
"""

import requests
from langchain.agents import create_agent
from langchain.tools import tool
from model import model

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@tool
def get_coordinates(city: str) -> str:
    """Find the latitude and longitude of a city by name."""
    try:
        r = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10)
        r.raise_for_status()
        results = r.json().get("results")
        if not results:
            return f"City '{city}' not found."
        top = results[0]
        return (
            f"{top['name']}, {top.get('country', '')}: "
            f"latitude={top['latitude']}, longitude={top['longitude']}"
        )
    except requests.RequestException as e:
        return f"Geocoding API error: {e}"


@tool
def get_current_weather(latitude: float, longitude: float) -> str:
    """Get current weather (temperature in C, wind speed in km/h) for coordinates."""
    try:
        r = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
            },
            timeout=10,
        )
        r.raise_for_status()
        cur = r.json()["current"]
        return (
            f"Temperature: {cur['temperature_2m']} C, "
            f"Humidity: {cur['relative_humidity_2m']}%, "
            f"Wind: {cur['wind_speed_10m']} km/h"
        )
    except requests.RequestException as e:
        return f"Weather API error: {e}"


agent = create_agent(
    model,
    tools=[get_coordinates, get_current_weather],
    system_prompt=(
        "You are a weather assistant. First find coordinates for the city, "
        "then fetch the weather. Answer briefly."
    ),
)

if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "How is the weather in Gampole right now?"}
            ]
        }
    )
    for m in result["messages"]:
        m.pretty_print()
