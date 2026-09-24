from fastapi import APIRouter, HTTPException, Request

from app.config import SUPPORTED_LANGUAGES, settings
from app.core.models import HealthResponse
from app.ingestion.indexer import Indexer

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    indexer: Indexer = request.app.state.indexer
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        llm_provider=settings.llm_provider,
        embedding_provider=settings.embedding_provider,
        index_ready=indexer.is_ready(),
        chunk_count=indexer.get_chunk_count(),
        supported_languages=list(SUPPORTED_LANGUAGES),
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check(request: Request) -> HealthResponse:
    response = await health_check(request)
    if not response.index_ready:
        raise HTTPException(
            status_code=503,
            detail="The retrieval index is not ready. Run ingestion before serving traffic.",
        )
    return response
