# LangGraph ReAct Node FastAPI

This app replicates the **ReAct-node** approach from `langgraph_explicit_vs_react.ipynb`:
- a single `react_node` receives message history
- LLM decides whether to call tools (`get_weather`, `tell_joke`)
- tool calls are executed
- LLM produces final answer

No LangChain agent/tool abstractions are used. It uses:
- `langgraph` for graph orchestration
- `openai` SDK function-calling for tool decisions
- `requests` for OpenWeather API

## Files
- `app.py`: FastAPI app + LangGraph ReAct flow
- `requirements.txt`: dependencies

## Environment
Set these in your env file:
- `OPENAI_API_KEY`
- `OPENWEATHER_API_KEY`
- optional: `OPENAI_MODEL` (default: `gpt-4o-mini`)

## Run
```bash
cd langgraph_react_fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ENV_FILE="/absolute/path/to/your/.env"
uvicorn app:app --reload --host 0.0.0.0 --port 8102
```

## Test
```bash
curl -X POST http://localhost:8102/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the weather in Charlotte?"}'
```

```bash
curl -X POST http://localhost:8102/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Tell me a joke about debugging"}'
```

Health check:
```bash
curl http://localhost:8102/health
```
