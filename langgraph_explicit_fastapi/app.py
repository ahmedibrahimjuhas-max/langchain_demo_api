from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from .core import graph
except ImportError:
    from core import graph


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    method: Literal["explicit"]
    intent: Literal["weather", "joke"]
    answer: str
    city: Optional[str] = None
    topic: Optional[str] = None


app = FastAPI(title="LangGraph Explicit Nodes API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = graph.invoke(
        {
            "user_input": question,
            "intent": "joke",
            "city": None,
            "topic": None,
            "final_answer": None,
        }
    )

    return ChatResponse(
        method="explicit",
        intent=result["intent"],
        answer=result.get("final_answer") or "No answer generated.",
        city=result.get("city"),
        topic=result.get("topic"),
    )
