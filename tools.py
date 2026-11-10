
from datetime import datetime
import requests
from urllib.parse import quote

# 1. Define actual Python functions
def get_time_now():
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_weather_for_city(city):
    """Returns the current weather for a specific city."""

    url = f"https://wttr.in/{quote(city)}"
    try:
        response = requests.get(
            url,
            params={"format": 3},
            timeout=10
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        return "Weather service request timed out."
    except requests.exceptions.RequestException as e:
        return f"Unable to fetch weather: {e}"


# 2. Register Python functions
TOOLS = {
    "get_time_now": get_time_now,
    "get_weather_for_city": get_weather_for_city
}


# 3. Define parameters for each function
TOOL_PARAMETERS = {
    "get_time_now": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    },

    "get_weather_for_city": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city for which weather information is requested."
            }
        },
        "required": ["city"],
        "additionalProperties": False
    }
}


# 4. Convert Python functions into OpenAI tool schemas
tools = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": func.__doc__ or "",
            "parameters": TOOL_PARAMETERS[name],
            "strict": True
        }
    }
    for name, func in TOOLS.items()
]
