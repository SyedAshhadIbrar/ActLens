from langchain_core.output_parsers import StrOutputParser

from app.agents.base import AgentContext, AgentResult
from app.agents.langchain.llm import get_chat_model
from app.agents.langchain.messages import history_to_messages
from app.agents.langchain.prompts import LANGUAGE_NAMES, rag_prompt
from app.core.models import ChatResponse, ChunkMeta
from app.generation.answer import _extract_citations
from app.pipeline.rag import RAGPipeline
from app.processing.context import prepare_context


async def run_rag_agent(context: AgentContext, pipeline: RAGPipeline) -> AgentResult:
    reranked = await pipeline.retrieve_ranked(context.query, language=context.language)
    act_context, selected_chunks = prepare_context(reranked)

    llm = get_chat_model()
    chain = rag_prompt(context.language, context.mode) | llm | StrOutputParser()
    answer = await chain.ainvoke(
        {
            "context": act_context,
            "query": context.query,
            "language_name": LANGUAGE_NAMES.get(context.language, "English"),
            "history": history_to_messages(context.history),
        }
    )

    citations = _extract_citations(selected_chunks)
    chunk_metas = [
        ChunkMeta(
            chunk_id=chunk.chunk_id,
            text=chunk.text[:800],
            article=chunk.article,
            recital=chunk.recital,
            annex=chunk.annex,
            source_file=chunk.source_file,
            page=chunk.page,
            language=chunk.language,
            citation_label=chunk.citation_label,
            structure_path=chunk.structure_path,
            source_url=chunk.source_url,
            score=score,
        )
        for chunk, score in reranked
    ]

    response = ChatResponse(
        answer=answer,
        language=context.language,
        citations=citations,
        retrieved_chunks=chunk_metas,
    )
    return AgentResult(response=response, agent="rag")
