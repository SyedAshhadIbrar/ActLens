from fastapi import APIRouter, HTTPException, Query, Request

from app.config import settings
from app.core.models import DocumentInfo, DocumentsResponse, IngestResponse

router = APIRouter(prefix="/api/v1", tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: Request,
    source: str | None = Query(
        default=None,
        description="Data source: hf (Hugging Face dataset), files (local), or both",
    ),
) -> IngestResponse:
    if not settings.enable_ingest_api:
        raise HTTPException(
            status_code=403,
            detail="API ingestion is disabled. Use scripts/ingest.py or set ENABLE_INGEST_API=true.",
        )
    indexer = request.app.state.indexer
    stats = await indexer.ingest(source)
    return IngestResponse(
        status="completed",
        files_processed=stats["files_processed"],
        chunks_added=stats["chunks_added"],
        chunks_updated=stats["chunks_updated"],
        chunks_unchanged=stats["chunks_unchanged"],
    )


@router.get("/documents", response_model=DocumentsResponse)
async def list_documents(request: Request) -> DocumentsResponse:
    indexer = request.app.state.indexer
    docs, total = indexer.get_document_list()
    return DocumentsResponse(
        documents=[DocumentInfo(**d) for d in docs],
        total_chunks=total,
    )
