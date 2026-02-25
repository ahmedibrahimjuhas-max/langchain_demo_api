from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from .core import graph
except ImportError:
    from core import graph


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    method: str = "react"
    answer: str
    tool_calls: list[str]


app = FastAPI(title="LangGraph ReAct Node API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = graph.invoke({"messages": [{"role": "user", "content": question}]})

    answer = None
    tool_calls: list[str] = []

    for msg in result["messages"]:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for call in msg["tool_calls"]:
                tool_calls.append(call["function"]["name"])

    for msg in reversed(result["messages"]):
        if msg.get("role") == "assistant" and msg.get("content"):
            candidate = str(msg["content"]).strip()
            if candidate:
                answer = candidate
                break

    return ChatResponse(answer=answer or "No answer generated.", tool_calls=tool_calls)
