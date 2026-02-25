# LangGraph CLI and App Guide

This document explains how to use `langgraph_cli.py` and what each LangGraph app folder does.

## 0) Detailed Run Notes (GitHub-Ready)

These steps are intended for a fresh clone.

### Prerequisites
- Python `3.9+` (recommended `3.10` or `3.11`)
- An OpenAI API key
- An OpenWeather API key

### Clone and enter project
```bash
git clone <your-repo-url>
cd hybrid_standalone
```

### Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies
The LangGraph apps and CLI share the same dependency set:
```bash
pip install -r langgraph_explicit_fastapi/requirements.txt
```

### Configure environment
Option A: export variables directly in shell:
```bash
export OPENAI_API_KEY="..."
export OPENWEATHER_API_KEY="..."
export OPENAI_MODEL="gpt-4o-mini"   # optional
```

Option B: keep values in a `.env` file and pass path using `ENV_FILE` or `--env-file`:
```bash
export ENV_FILE="/absolute/path/to/.env"
```

### Run CLI quickly
```bash
python langgraph_cli.py --mode both --env-file /absolute/path/to/.env --question "Tell me a joke about Python"
```

### Start FastAPI apps
Terminal 1 (explicit):
```bash
cd langgraph_explicit_fastapi
uvicorn app:app --reload --host 0.0.0.0 --port 8101
```

Terminal 2 (react):
```bash
cd langgraph_react_fastapi
uvicorn app:app --reload --host 0.0.0.0 --port 8102
```

Swagger pages:
- `http://127.0.0.1:8101/docs`
- `http://127.0.0.1:8102/docs`

### Common issues
- `ImportError: cannot import name 'IncEx' from pydantic.main`:
  - Cause: FastAPI/Pydantic version mismatch in current Python environment.
  - Fix:
  ```bash
  pip install "fastapi>=0.115" "pydantic>=2.7" "uvicorn>=0.30"
  ```
  - Or run with a clean project venv (`.venv`) as shown above.
- `OPENAI_API_KEY not found` or `OPENWEATHER_API_KEY not found`:
  - Ensure env variables are exported or pass `--env-file` / `ENV_FILE`.

## 1) `langgraph_cli.py` Functionality

`langgraph_cli.py` runs the LangGraph workflows directly from terminal, without starting FastAPI.

### Supported modes
- `explicit`: runs only the explicit-node graph
- `react`: runs only the ReAct-style graph
- `both`: runs both and prints both outputs

### Environment loading
- You can pass your env file path with `--env-file`.
- The script sets `ENV_FILE` before importing graph modules.
- Required env vars:
  - `OPENAI_API_KEY`
  - `OPENWEATHER_API_KEY`
- Optional:
  - `OPENAI_MODEL` (default `gpt-4o-mini`)

### Run examples

Single question:
```bash
python langgraph_cli.py --mode both --env-file /absolute/path/to/.env --question "What's the weather in Tokyo?"
```

Interactive session:
```bash
python langgraph_cli.py --mode explicit --env-file /absolute/path/to/.env
python langgraph_cli.py --mode react --env-file /absolute/path/to/.env
python langgraph_cli.py --mode both --env-file /absolute/path/to/.env
```

Exit interactive mode with `exit` or `quit`.

## 2) What `langgraph_explicit_fastapi` Does

Folder: `langgraph_explicit_fastapi/`

This app mirrors the notebook's **explicit node design**:
- A `router_node` classifies each user request into `weather` or `joke`.
- LangGraph conditional edges route execution to:
  - `weather_node`, or
  - `joke_node`.
- Each terminal node writes `final_answer` into state.

Key files:
- `core.py`: graph logic, node functions, environment loading
- `app.py`: FastAPI wrapper (`/chat`, `/health`)
- `requirements.txt`

Behavior summary:
- Deterministic graph topology.
- Explicit control over routing and node boundaries.
- Good when you want transparent, fixed workflow steps.

## 3) What `langgraph_react_fastapi` Does

Folder: `langgraph_react_fastapi/`

This app mirrors the notebook's **ReAct-style single node** pattern:
- One `react_node` receives message history.
- The model decides whether to call tools:
  - `get_weather(city)`
  - `tell_joke(topic)`
- Tool results are appended as tool messages.
- The model then generates a final assistant response.

Key files:
- `core.py`: ReAct graph, tool schemas, tool execution
- `app.py`: FastAPI wrapper (`/chat`, `/health`)
- `requirements.txt`

Behavior summary:
- Flexible model-driven tool selection.
- Single-node orchestration with internal tool-call loop.
- Good when you want adaptable behavior with fewer explicit branches.

## 4) FastAPI Docs URLs

Explicit app:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8101
```
Swagger: `http://127.0.0.1:8101/docs`

ReAct app:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8102
```
Swagger: `http://127.0.0.1:8102/docs`

## 5) Helper Script: `run_langgraph_cli.sh`

File: `run_langgraph_cli.sh`

This is a convenience wrapper around `langgraph_cli.py`.

What it does:
- Validates mode (`explicit`, `react`, `both`)
- Builds and runs the correct `python langgraph_cli.py ...` command
- Passes `ENV_FILE` to CLI if you set it in shell
- If you pass a question, it runs once; if not, it starts interactive mode

Usage:
```bash
./run_langgraph_cli.sh [mode] [question]
```

Examples:
```bash
ENV_FILE=/absolute/path/to/.env ./run_langgraph_cli.sh both "What's the weather in Tokyo?"
ENV_FILE=/absolute/path/to/.env ./run_langgraph_cli.sh explicit
ENV_FILE=/absolute/path/to/.env ./run_langgraph_cli.sh react
```

You can also use env vars instead of positional args:
```bash
ENV_FILE=/absolute/path/to/.env MODE=both QUESTION="Tell me a joke about Python" ./run_langgraph_cli.sh
```

## 6) Quick Command Matrix

Install once:
```bash
pip install -r langgraph_explicit_fastapi/requirements.txt
```

Run CLI (one-shot):
```bash
python langgraph_cli.py --mode explicit --env-file /absolute/path/to/.env --question "weather in Cairo"
python langgraph_cli.py --mode react --env-file /absolute/path/to/.env --question "tell me a joke about tests"
python langgraph_cli.py --mode both --env-file /absolute/path/to/.env --question "weather in Tokyo"
```

Run CLI (interactive):
```bash
python langgraph_cli.py --mode explicit --env-file /absolute/path/to/.env
python langgraph_cli.py --mode react --env-file /absolute/path/to/.env
python langgraph_cli.py --mode both --env-file /absolute/path/to/.env
```

Run helper wrapper:
```bash
ENV_FILE=/absolute/path/to/.env ./run_langgraph_cli.sh both "weather in Charlotte"
ENV_FILE=/absolute/path/to/.env ./run_langgraph_cli.sh explicit
ENV_FILE=/absolute/path/to/.env ./run_langgraph_cli.sh react
```
