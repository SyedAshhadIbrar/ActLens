from typing import Literal

from pydantic import BaseModel, Field

LanguageCode = Literal["en", "fr", "nl"]
WorkspaceMode = Literal["ask", "classify", "find", "compare", "explain", "gap"]


class ChunkMeta(BaseModel):
    chunk_id: str
    text: str
    article: str | None = None
    recital: str | None = None
    annex: str | None = None
    source_file: str
    page: int | None = None
    language: str | None = None
    citation_label: str | None = None
    structure_path: str | None = None
    source_url: str | None = None
    score: float | None = None


class Citation(BaseModel):
    label: str = Field(description="e.g. 'Art. 6(2) AI Act' or 'Recital 12'")
    excerpt: str
    source_file: str
    source_url: str | None = None
    score: float | None = None


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=4000)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    language: LanguageCode = Field(
        default="en",
        description="Response language: en (English), fr (French), nl (Dutch)",
    )
    mode: WorkspaceMode = Field(
        default="ask",
        description="Workspace mode: ask, classify, find, compare, explain",
    )
    history: list[HistoryMessage] = Field(
        default_factory=list,
        max_length=8,
        description="Recent conversation turns for follow-up context",
    )
    document_text: str | None = Field(
        default=None,
        max_length=12000,
        description="Uploaded policy or internal document for gap analysis",
    )
    document_name: str | None = Field(default=None, max_length=255)


class ChatResponse(BaseModel):
    answer: str
    language: LanguageCode
    citations: list[Citation]
    retrieved_chunks: list[ChunkMeta]
    agent: str = "rag"


class UploadResponse(BaseModel):
    filename: str
    char_count: int
    text: str


class IngestResponse(BaseModel):
    status: str
    files_processed: int
    chunks_added: int
    chunks_updated: int
    chunks_unchanged: int


class DocumentInfo(BaseModel):
    source_file: str
    chunk_count: int
    last_indexed: str | None = None


class DocumentsResponse(BaseModel):
    documents: list[DocumentInfo]
    total_chunks: int


class HealthResponse(BaseModel):
    status: str
    app_name: str
    llm_provider: str
    embedding_provider: str
    index_ready: bool
    chunk_count: int
    supported_languages: list[str]
    agents: list[str] = Field(default_factory=lambda: ["rag", "gap_analysis"])
