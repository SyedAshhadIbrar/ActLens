from app.config import SUPPORTED_LANGUAGES, settings
from app.core.models import HealthResponse
from app.ingestion.indexer import Indexer

from fastapi import APIRouter, Request

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
