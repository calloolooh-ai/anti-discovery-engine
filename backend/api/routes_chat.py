"""
Chat endpoint — graph-aware Q&A via Groq.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    graph_data: dict | None = None
    gaps: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest) -> ChatResponse:
    from core.chat import chat

    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    reply = await chat(messages, body.graph_data, body.gaps)
    return ChatResponse(reply=reply)
