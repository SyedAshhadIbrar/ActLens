from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from langchain_google_genai.chat_models import (
    GoogleAuthenticationError,
    GoogleRateLimitError,
)

from app.api.routes.agents import upload_document
from app.api.routes.chat import _llm_http_error
from app.api.routes.ingest import ingest_documents
from app.config import settings


@pytest.mark.asyncio
async def test_upload_rejects_file_over_byte_limit(monkeypatch):
    monkeypatch.setattr(settings, "max_upload_bytes", 4)
    upload = UploadFile(filename="policy.txt", file=BytesIO(b"12345"))

    with pytest.raises(HTTPException) as exc_info:
        await upload_document(upload)

    assert exc_info.value.status_code == 413


@pytest.mark.asyncio
async def test_ingest_api_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(settings, "enable_ingest_api", False)

    with pytest.raises(HTTPException) as exc_info:
        await ingest_documents(request=object())

    assert exc_info.value.status_code == 403


@pytest.mark.parametrize(
    ("provider_error", "expected_status"),
    [
        (GoogleAuthenticationError("invalid key"), 401),
        (GoogleRateLimitError("quota exceeded"), 429),
    ],
)
def test_langchain_gemini_errors_map_to_actionable_http_status(
    provider_error,
    expected_status,
):
    mapped = _llm_http_error(provider_error)

    assert mapped.status_code == expected_status
    assert "invalid key" not in mapped.detail
    assert "quota exceeded" not in mapped.detail
