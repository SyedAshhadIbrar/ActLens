from dataclasses import dataclass

from app.core.models import ChatResponse


@dataclass
class AgentContext:
    query: str
    language: str
    mode: str
    history: list
    document_text: str | None = None
    document_name: str | None = None


@dataclass
class AgentResult:
    response: ChatResponse
    agent: str
