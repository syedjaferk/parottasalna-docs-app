# tools.py (Session 5 version) - Session 4's tools + a notebook the agent can write in
import ast
import operator
from datetime import datetime

import requests

# ---------------------------------------------------------------- 1. The real functions
CITIES = {"chennai": (13.08, 80.27), "delhi": (28.61, 77.21), "london": (51.51, -0.13),
          "mumbai": (19.08, 72.88), "bengaluru": (12.97, 77.59)}

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg, ast.Mod: operator.mod}


def _eval(node):
    """Safely evaluate a maths expression (numbers and + - * / ** % only)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / ** % are allowed")


def calculator(expression):
    """Calculate a maths expression such as '(12 + 8) * 3'."""
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except (ValueError, SyntaxError, ZeroDivisionError) as error:
        return f"Error: {error}"


def get_weather(city):
    """Current temperature and wind for a city (Open-Meteo, no key needed)."""
    if city.lower() not in CITIES:
        return f"Error: I only know these cities: {', '.join(CITIES)}"
    lat, lon = CITIES[city.lower()]
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", timeout=15,
                         params={"latitude": lat, "longitude": lon, "current_weather": "true"})
        r.raise_for_status()
        now = r.json()["current_weather"]
    except requests.RequestException as error:
        return f"Error: could not reach the weather service ({error.__class__.__name__})"
    return f"{city.title()}: {now['temperature']} °C, wind {now['windspeed']} km/h"


NOTES_FILE = "notes.txt"


def save_note(text):
    """Remember something by writing it into notes.txt (kept even after the program stops)."""
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    return "Saved."


def read_notes():
    """Read everything saved in notes.txt."""
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() or "(no notes yet)"
    except FileNotFoundError:
        return "(no notes yet)"


def get_time():
    """The current date and time on this computer."""
    return datetime.now().strftime("%A, %d %B %Y, %H:%M")


# ---------------------------------------------------------------- 2. The descriptions (the AI reads these)
TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Do exact maths. Use it for ANY calculation instead of guessing.",
        "parameters": {"type": "object",
                       "properties": {"expression": {"type": "string", "description": "e.g. '(12 + 8) * 3'"}},
                       "required": ["expression"]}}},
    {"type": "function", "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Known cities: chennai, delhi, london, mumbai, bengaluru.",
        "parameters": {"type": "object",
                       "properties": {"city": {"type": "string", "description": "city name in lowercase"}},
                       "required": ["city"]}}},
    {"type": "function", "function": {
        "name": "save_note",
        "description": "Save a short note to remember it later, e.g. a user preference or a to-do.",
        "parameters": {"type": "object",
                       "properties": {"text": {"type": "string", "description": "the note to save"}},
                       "required": ["text"]}}},
    {"type": "function", "function": {
        "name": "read_notes",
        "description": "Read all saved notes. Use it when the user asks what you remember or what is on their list.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "get_time",
        "description": "Get the current date and time.",
        "parameters": {"type": "object", "properties": {}}}},
]

# ---------------------------------------------------------------- 3. A phone book: name -> function
TOOL_FUNCTIONS = {"calculator": calculator, "get_weather": get_weather, "get_time": get_time,
                  "save_note": save_note, "read_notes": read_notes}
