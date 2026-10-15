# weather_summary.py - call a public web API, read the JSON, print a clean summary
# Uses Open-Meteo: free, no key needed.
import sys

import requests

CITIES = {                       # latitude, longitude
    "chennai": (13.08, 80.27),
    "delhi": (28.61, 77.21),
    "london": (51.51, -0.13),
}
URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city):
    """Return a dict like {'city': 'chennai', 'temperature_c': 31.2, 'wind_kmh': 12.0}."""
    lat, lon = CITIES[city.lower()]
    params = {"latitude": lat, "longitude": lon, "current_weather": "true"}
    response = requests.get(URL, params=params, timeout=15)   # never wait forever
    response.raise_for_status()                               # stop on 4xx / 5xx errors
    now = response.json()["current_weather"]
    return {"city": city, "temperature_c": now["temperature"], "wind_kmh": now["windspeed"]}


if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else "chennai"
    if city.lower() not in CITIES:
        print(f"I only know these cities: {', '.join(CITIES)}")
        sys.exit(1)
    try:
        info = get_weather(city)
    except requests.RequestException as error:
        print("Could not get the weather:", error)
        sys.exit(1)
    print(f"Weather in {info['city'].title()}: {info['temperature_c']} °C, wind {info['wind_kmh']} km/h")
