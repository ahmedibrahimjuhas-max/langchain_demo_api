# LangGraph Explicit Nodes FastAPI

This app replicates the **explicit-node** approach from `langgraph_explicit_vs_react.ipynb`:
- `router_node` classifies user input into `weather` or `joke`
- conditional edge routes to `weather_node` or `joke_node`
- each terminal node writes `final_answer`

No LangChain agent/tool abstractions are used. It uses:
- `langgraph` for graph orchestration
- `openai` SDK for LLM calls
- `requests` for OpenWeather API

## Files
- `app.py`: FastAPI app + LangGraph explicit flow
- `requirements.txt`: dependencies

## Environment
Set these in your env file:
- `OPENAI_API_KEY`
- `OPENWEATHER_API_KEY`
- optional: `OPENAI_MODEL` (default: `gpt-4o-mini`)

## Run
```bash
cd langgraph_explicit_fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ENV_FILE="/absolute/path/to/your/.env"
uvicorn app:app --reload --host 0.0.0.0 --port 8101
```

## Test
```bash
curl -X POST http://localhost:8101/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the weather in Tokyo?"}'
```

```bash
curl -X POST http://localhost:8101/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Tell me a joke about Python programmers"}'
```

Health check:
```bash
curl http://localhost:8101/health
```
