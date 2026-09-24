from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_LANGUAGES = ("en", "fr", "nl")
LanguageCode = Literal["en", "fr", "nl"]

_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _ROOT / ".env"
if not _ENV_FILE.exists():
    _ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ActLens"
    debug: bool = False

    # Providers
    llm_provider: str = "openai"
    embedding_provider: str = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Google Gemini (LLM)
    google_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    gemini_embedding_model: str = "gemini-embedding-001"

    # Hugging Face embeddings (local, no API key)
    hf_embedding_model: str = "intfloat/multilingual-e5-small"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    ollama_embedding_model: str = "nomic-embed-text"

    # Storage (paths relative to project root)
    chroma_persist_dir: str = "./storage/chroma"
    bm25_index_path: str = "./storage/bm25/index.pkl"
    manifest_path: str = "./storage/manifest.json"
    data_raw_dir: str = "./data/raw"

    # Hugging Face dataset (primary source)
    data_source: str = "hf"  # hf | files | both
    hf_dataset_id: str = "jeroenherczeg/eu-ai-act"
    hf_dataset_languages: str = "en,fr,nl"  # comma-separated ISO codes; empty = all
    hf_dataset_cache_dir: str = "./storage/hf_cache"

    # RAG
    retrieval_top_k: int = 20
    rerank_top_n: int = 5
    max_context_tokens: int = 3000
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Upload limits
    max_upload_chars: int = 12000
    max_upload_bytes: int = 5_000_000

    # Administrative API
    enable_ingest_api: bool = False

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def project_root(self) -> Path:
        return _ROOT

    def resolve_path(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        return self.project_root / p

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def hf_language_list(self) -> list[str]:
        if not self.hf_dataset_languages.strip():
            return []
        return [lang.strip().lower() for lang in self.hf_dataset_languages.split(",") if lang.strip()]

settings = Settings()
