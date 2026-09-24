import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.core.models import UploadResponse
from app.ingestion.loader import load_document

router = APIRouter(prefix="/api/v1", tags=["agents"])

SUPPORTED_UPLOAD_SUFFIXES = {".pdf", ".txt", ".md", ".html", ".htm"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_UPLOAD_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    content = await file.read(settings.max_upload_bytes + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_bytes}-byte upload limit.",
        )

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        document = load_document(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    text = document.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    if len(text) > settings.max_upload_chars:
        text = text[: settings.max_upload_chars]

    return UploadResponse(
        filename=file.filename or "document",
        char_count=len(text),
        text=text,
    )
