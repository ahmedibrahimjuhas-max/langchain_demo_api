import json
import os
import operator
from pathlib import Path
from typing import Annotated, Any, TypedDict

import requests
from dotenv import load_dotenv
from openai import OpenAI

from langgraph.graph import END, StateGraph


BASE_DIR = Path(__file__).resolve().parent


def load_environment() -> None:
    env_file = os.getenv("ENV_FILE")
    if env_file:
        load_dotenv(env_file, override=False)
        return
    load_dotenv(BASE_DIR / ".env", override=False)
    load_dotenv(override=False)


load_environment()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Set it in ENV_FILE or environment.")
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found. Set it in ENV_FILE or environment.")

client = OpenAI(api_key=OPENAI_API_KEY)


class ReactState(TypedDict):
    messages: Annotated[list[dict[str, Any]], operator.add]


def get_weather(city: str) -> str:
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"},
        timeout=20,
    )
    payload = response.json()
    if response.status_code != 200:
        details = payload.get("message", "Unknown error") if isinstance(payload, dict) else str(payload)
        return f"Weather lookup failed for '{city}': {details}"

    return (
        f"{city}: {payload['weather'][0]['description']}, "
        f"{payload['main']['temp']} deg C, humidity {payload['main']['humidity']}%."
    )


def tell_joke(topic: str) -> str:
    result = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.8,
        messages=[
            {"role": "system", "content": "Tell one short clean joke."},
            {"role": "user", "content": f"Topic: {topic}"},
        ],
    )
    return (result.choices[0].message.content or "").strip()


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetch the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example Tokyo or Charlotte",
                    }
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tell_joke",
            "description": "Generate a short joke about a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Joke topic, for example Python programmers",
                    }
                },
                "required": ["topic"],
                "additionalProperties": False,
            },
        },
    },
]


def execute_tool(name: str, arguments_json: str) -> str:
    try:
        args = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return "Tool call had invalid JSON arguments."

    if name == "get_weather":
        city = (args.get("city") or "").strip()
        if not city:
            return "Please provide a city for weather lookup."
        return get_weather(city)

    if name == "tell_joke":
        topic = (args.get("topic") or "general").strip() or "general"
        return tell_joke(topic)

    return f"Unknown tool: {name}"


def react_node(state: ReactState) -> ReactState:
    messages = state["messages"]

    first = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.3,
        messages=messages,
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
    )

    assistant_message = first.choices[0].message
    assistant_payload: dict[str, Any] = {
        "role": "assistant",
        "content": assistant_message.content or "",
    }

    tool_calls = assistant_message.tool_calls or []
    if tool_calls:
        assistant_payload["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in tool_calls
        ]

    new_messages: list[dict[str, Any]] = [assistant_payload]

    if not tool_calls:
        return {"messages": new_messages}

    for call in tool_calls:
        result = execute_tool(call.function.name, call.function.arguments)
        new_messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            }
        )

    second = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.3,
        messages=messages + new_messages,
    )
    final_text = second.choices[0].message.content or ""
    new_messages.append({"role": "assistant", "content": final_text})

    return {"messages": new_messages}


builder = StateGraph(ReactState)
builder.add_node("react_node", react_node)
builder.set_entry_point("react_node")
builder.add_edge("react_node", END)
graph = builder.compile()
