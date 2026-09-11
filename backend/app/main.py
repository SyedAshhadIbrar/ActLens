from contextlib import asynccontextmanager

from app.config import settings
from app.core.providers.registry import get_embedding_provider, get_llm_provider
from app.ingestion.indexer import Indexer
from app.pipeline.rag import RAGPipeline
from app.agents.orchestrator import AgentOrchestrator
from app.api.routes import agents, chat, health, ingest

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.retrieval.bm25_index import BM25Index
    from app.retrieval.vector_store import VectorStore

    embedding = get_embedding_provider()
    llm = get_llm_provider()
    vector_store = VectorStore()
    bm25_index = BM25Index()

    indexer = Indexer(embedding, vector_store=vector_store, bm25_index=bm25_index)
    indexer.load_indexes()
    pipeline = RAGPipeline(
        llm, embedding, vector_store=vector_store, bm25_index=bm25_index
    )
    orchestrator = AgentOrchestrator(pipeline, llm)

    app.state.indexer = indexer
    app.state.pipeline = pipeline
    app.state.orchestrator = orchestrator

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="EU AI Act RAG Assistant with hybrid retrieval and verifiable citations",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(agents.router)
    app.include_router(ingest.router)

    return app


app = create_app()
