from app.config import settings
from app.core.providers.anthropic_provider import AnthropicLLMProvider
from app.core.providers.base import EmbeddingProvider, LLMProvider
from app.core.providers.gemini_provider import GeminiEmbeddingProvider, GeminiLLMProvider
from app.core.providers.hf_embedding_provider import HFEmbeddingProvider
from app.core.providers.ollama_provider import OllamaEmbeddingProvider, OllamaLLMProvider
from app.core.providers.openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider

_LLM_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAILLMProvider,
    "anthropic": AnthropicLLMProvider,
    "gemini": GeminiLLMProvider,
    "google": GeminiLLMProvider,
    "ollama": OllamaLLMProvider,
}

_EMBEDDING_REGISTRY: dict[str, type[EmbeddingProvider]] = {
    "hf": HFEmbeddingProvider,
    "huggingface": HFEmbeddingProvider,
    "openai": OpenAIEmbeddingProvider,
    "gemini": GeminiEmbeddingProvider,
    "google": GeminiEmbeddingProvider,
    "ollama": OllamaEmbeddingProvider,
}


def get_llm_provider() -> LLMProvider:
    provider_name = settings.llm_provider.lower()
    if provider_name not in _LLM_REGISTRY:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}. "
            f"Available: {list(_LLM_REGISTRY.keys())}"
        )
    return _LLM_REGISTRY[provider_name]()


def get_embedding_provider() -> EmbeddingProvider:
    provider_name = settings.embedding_provider.lower()
    if provider_name not in _EMBEDDING_REGISTRY:
        raise ValueError(
            f"Unknown embedding provider: {provider_name}. "
            f"Available: {list(_EMBEDDING_REGISTRY.keys())}"
        )
    return _EMBEDDING_REGISTRY[provider_name]()
