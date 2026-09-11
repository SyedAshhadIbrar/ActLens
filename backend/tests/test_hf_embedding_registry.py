def test_hf_registered_as_embedding_provider():
    from app.core.providers.registry import _EMBEDDING_REGISTRY

    assert "hf" in _EMBEDDING_REGISTRY
    assert _EMBEDDING_REGISTRY["hf"] is _EMBEDDING_REGISTRY["huggingface"]
