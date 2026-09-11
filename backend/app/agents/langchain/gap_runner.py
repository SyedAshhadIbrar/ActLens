from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import AgentContext, AgentResult
from app.agents.langchain.llm import get_chat_model, supports_tool_calling
from app.agents.langchain.prompts import LANGUAGE_NAMES
from app.agents.langchain.tools import make_search_tool
from app.core.models import ChatResponse, ChunkMeta
from app.generation.answer import _extract_citations
from app.pipeline.rag import RAGPipeline
from app.processing.context import deduplicate_chunks, prepare_context

GAP_TOPIC_QUERIES = (
    "risk management system requirements",
    "human oversight obligations",
    "transparency and documentation requirements",
    "data governance and quality",
    "conformity assessment obligations",
)

GAP_SYSTEM_PROMPT = """You are ActLens gap-analysis agent for the EU AI Act.
Compare an internal policy document against EU AI Act provisions retrieved via tools.
Cite articles inline. Do not invent requirements.
Use the search_eu_ai_act tool whenever you need legal provisions."""


def _gap_user_input(context: AgentContext) -> str:
    document = context.document_text or ""
    doc_name = context.document_name or "uploaded policy"
    return f"""Internal document: {doc_name}

DOCUMENT TEXT:
{document[:12000]}

Reviewer focus: {context.query}

Return:
1. Executive summary
2. Covered areas (with article citations)
3. Gaps and missing obligations
4. Recommended next actions
5. Items needing legal review"""


def _extract_agent_answer(result: dict) -> str:
    messages = result.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            content = message.content
            return content if isinstance(content, str) else str(content)
    return ""


async def _collect_gap_chunks(context: AgentContext, pipeline: RAGPipeline) -> list:
    merged_chunks: list = []
    search_queries = [context.query, *GAP_TOPIC_QUERIES]
    for search_query in search_queries:
        merged_chunks.extend(
            await pipeline.retrieve_for_query(
                search_query, language=context.language, top_n=2
            )
        )
    return deduplicate_chunks(merged_chunks)


async def _run_tool_agent(context: AgentContext, pipeline: RAGPipeline) -> tuple[str, list]:
    llm = get_chat_model()
    search_tool = make_search_tool(pipeline, context.language)
    agent = create_agent(
        llm,
        tools=[search_tool],
        system_prompt=GAP_SYSTEM_PROMPT,
    )
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=_gap_user_input(context))]}
    )
    answer = _extract_agent_answer(result)
    deduped = await _collect_gap_chunks(context, pipeline)
    return answer, deduped


async def _run_chain_fallback(context: AgentContext, pipeline: RAGPipeline) -> tuple[str, list]:
    deduped = await _collect_gap_chunks(context, pipeline)
    act_context, _ = prepare_context(deduped, max_tokens=2800)
    language_name = LANGUAGE_NAMES.get(context.language, "English")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You are ActLens gap-analysis agent for the EU AI Act.
Compare an internal policy document against retrieved EU AI Act provisions.
Write in {language_name}. Cite articles inline. Do not invent requirements.""",
            ),
            ("human", "{user_input}\n\nEU AI ACT CONTEXT:\n{context}"),
        ]
    )
    chain = prompt | get_chat_model() | StrOutputParser()
    answer = await chain.ainvoke(
        {
            "user_input": _gap_user_input(context),
            "context": act_context,
        }
    )
    return answer, deduped


async def run_gap_agent(context: AgentContext, pipeline: RAGPipeline) -> AgentResult:
    if not context.document_text:
        raise ValueError("Gap analysis requires an uploaded policy document")

    if supports_tool_calling():
        answer, deduped = await _run_tool_agent(context, pipeline)
    else:
        answer, deduped = await _run_chain_fallback(context, pipeline)

    citations = _extract_citations([chunk for chunk, _ in deduped])
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
        for chunk, score in deduped[:8]
    ]

    response = ChatResponse(
        answer=answer,
        language=context.language,
        citations=citations,
        retrieved_chunks=chunk_metas,
    )
    return AgentResult(response=response, agent="gap_analysis")
