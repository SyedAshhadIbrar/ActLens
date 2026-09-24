from fastapi import APIRouter, HTTPException, Request
from google.genai.errors import ClientError
from langchain_google_genai.chat_models import (
    GoogleAuthenticationError,
    GoogleContextOverflowError,
    GoogleGenerativeAIError,
    GoogleInvalidRequestError,
    GoogleModelNotFoundError,
    GooglePermissionDeniedError,
    GoogleRateLimitError,
)

from app.agents.base import AgentContext
from app.agents.orchestrator import AgentOrchestrator
from app.core.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])


def _llm_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, GoogleAuthenticationError):
        return HTTPException(
            status_code=401,
            detail="Gemini authentication failed. Check GOOGLE_API_KEY and restart the backend.",
        )
    if isinstance(exc, GooglePermissionDeniedError):
        return HTTPException(
            status_code=403,
            detail="Gemini denied this request. Check the key and model permissions.",
        )
    if isinstance(exc, GoogleRateLimitError):
        return HTTPException(
            status_code=429,
            detail="Gemini rate limit exceeded. Wait a moment and try again.",
        )
    if isinstance(exc, GoogleModelNotFoundError):
        return HTTPException(
            status_code=502,
            detail=(
                "The configured Gemini model is unavailable. "
                "Check GEMINI_MODEL and restart the backend."
            ),
        )
    if isinstance(exc, (GoogleContextOverflowError, GoogleInvalidRequestError)):
        return HTTPException(
            status_code=400,
            detail="The language model rejected the request or context size.",
        )
    if isinstance(exc, GoogleGenerativeAIError):
        return HTTPException(
            status_code=502,
            detail="The Gemini service request failed.",
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
                    "The configured Gemini model is unavailable. "
                    "Check GEMINI_MODEL and restart the backend."
                ),
            )
        if exc.code == 429:
            return HTTPException(
                status_code=429,
                detail="Gemini rate limit exceeded. Wait a moment and try again.",
            )
    return HTTPException(status_code=502, detail="The language model request failed.")


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
    except (ClientError, GoogleGenerativeAIError) as exc:
        raise _llm_http_error(exc) from exc
    response = result.response
    response.agent = result.agent
    return response
