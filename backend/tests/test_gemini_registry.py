def test_gemini_registered_as_provider():
    from app.core.providers.registry import _EMBEDDING_REGISTRY, _LLM_REGISTRY

    assert "gemini" in _LLM_REGISTRY
    assert "google" in _LLM_REGISTRY
    assert _LLM_REGISTRY["gemini"] is _LLM_REGISTRY["google"]
    assert "gemini" in _EMBEDDING_REGISTRY
