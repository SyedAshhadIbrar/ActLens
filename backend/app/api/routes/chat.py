from app.agents.base import AgentContext
from app.agents.orchestrator import AgentOrchestrator
from app.core.models import ChatRequest, ChatResponse

from fastapi import APIRouter, HTTPException, Request
from google.genai.errors import ClientError
from langchain_google_genai.chat_models import GoogleModelNotFoundError

router = APIRouter(prefix="/api/v1", tags=["chat"])


def _llm_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, GoogleModelNotFoundError):
        return HTTPException(
            status_code=502,
            detail=(
                f"Gemini model not available: {exc}. "
                "Set GEMINI_MODEL=gemini-3.6-flash in .env and restart the backend."
            ),
        )
    if isinstance(exc, ClientError):
        if exc.code == 401:
            return HTTPException(
                status_code=401,
                detail="Gemini API key rejected. Check GOOGLE_API_KEY in .env.",
            )
        if exc.code == 404:
            return HTTPException(
                status_code=502,
                detail=(
                    f"Gemini model unavailable ({exc}). "
                    "Try GEMINI_MODEL=gemini-3.6-flash in .env."
                ),
            )
        if exc.code == 429:
            return HTTPException(
                status_code=429,
                detail="Gemini rate limit exceeded. Wait a moment and try again.",
            )
    return HTTPException(status_code=502, detail=f"LLM request failed: {exc}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    indexer = request.app.state.indexer
    if not indexer.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Index not ready. Run ingestion first via POST /api/v1/ingest.",
        )

    if body.mode == "gap" and not body.document_text:
        raise HTTPException(
            status_code=400,
            detail="Gap analysis requires an uploaded document.",
        )

    orchestrator: AgentOrchestrator = request.app.state.orchestrator
    context = AgentContext(
        query=body.query,
        language=body.language,
        mode=body.mode,
        history=body.history,
        document_text=body.document_text,
        document_name=body.document_name,
    )
    try:
        result = await orchestrator.run(context)
    except (ClientError, GoogleModelNotFoundError) as exc:
        raise _llm_http_error(exc) from exc
    response = result.response
    response.agent = result.agent
    return response
