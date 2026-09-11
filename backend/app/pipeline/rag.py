from app.core.models import ChatResponse, ChunkMeta, HistoryMessage, WorkspaceMode
from app.core.providers.base import EmbeddingProvider, LLMProvider
from app.generation.answer import generate_answer
from app.processing.context import prepare_context
from app.ranking.reranker import CrossEncoderReranker
from app.retrieval.bm25_index import BM25Index
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.vector_store import VectorStore


class RAGPipeline:
    def __init__(
        self,
        llm_provider: LLMProvider,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore | None = None,
        bm25_index: BM25Index | None = None,
        reranker: CrossEncoderReranker | None = None,
    ) -> None:
        self._llm = llm_provider
        self._vector_store = vector_store or VectorStore()
        self._bm25_index = bm25_index or BM25Index()
        self._retriever = HybridRetriever(
            self._vector_store, self._bm25_index, embedding_provider
        )
        self._reranker = reranker or CrossEncoderReranker()

    async def retrieve_ranked(
        self,
        user_query: str,
        language: str = "en",
    ) -> list:
        retrieved = await self._retriever.retrieve(user_query, language=language)
        return self._reranker.rerank(user_query, retrieved)

    async def retrieve_for_query(
        self,
        user_query: str,
        language: str = "en",
        top_n: int = 2,
    ) -> list:
        reranked = await self.retrieve_ranked(user_query, language=language)
        return reranked[:top_n]

    async def query(
        self,
        user_query: str,
        language: str = "en",
        mode: WorkspaceMode = "ask",
        history: list[HistoryMessage] | None = None,
    ) -> ChatResponse:
        reranked = await self.retrieve_ranked(user_query, language=language)
        context, selected_chunks = prepare_context(reranked)
        answer, citations = await generate_answer(
            self._llm,
            user_query,
            context,
            selected_chunks,
            language=language,
            mode=mode,
            history=history,
        )

        chunk_metas = [
            ChunkMeta(
                chunk_id=c.chunk_id,
                text=c.text[:800],
                article=c.article,
                recital=c.recital,
                annex=c.annex,
                source_file=c.source_file,
                page=c.page,
                language=c.language,
                citation_label=c.citation_label,
                structure_path=c.structure_path,
                source_url=c.source_url,
                score=score,
            )
            for c, score in reranked
        ]

        return ChatResponse(
            answer=answer,
            language=language,
            citations=citations,
            retrieved_chunks=chunk_metas,
        )
