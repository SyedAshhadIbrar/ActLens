import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.agents.orchestrator import AgentOrchestrator
from app.api.routes import agents, chat, health, ingest
from app.config import settings
from app.core.providers.registry import get_embedding_provider, get_llm_provider
from app.ingestion.indexer import Indexer
from app.pipeline.rag import RAGPipeline

logger = logging.getLogger("actlens.api")


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
        expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    @app.middleware("http")
    async def request_observability(request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        started = perf_counter()
        response = await call_next(request)
        elapsed_ms = (perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
        logger.info(
            "request_completed method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.exception(
            "request_failed method=%s path=%s request_id=%s",
            request.method,
            request.url.path,
            request_id,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected server error occurred.",
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(agents.router)
    app.include_router(ingest.router)

    return app


app = create_app()
