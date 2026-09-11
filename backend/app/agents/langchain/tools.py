from langchain_core.tools import StructuredTool

from app.pipeline.rag import RAGPipeline
from app.processing.context import prepare_context


def make_search_tool(pipeline: RAGPipeline, language: str) -> StructuredTool:
    async def search_eu_ai_act(query: str) -> str:
        """Search the indexed EU AI Act for provisions related to the query."""
        chunks = await pipeline.retrieve_for_query(query, language=language, top_n=3)
        context, _ = prepare_context(chunks, max_tokens=1200)
        if not context.strip():
            return "No matching EU AI Act provisions found."
        return context

    return StructuredTool.from_function(
        coroutine=search_eu_ai_act,
        name="search_eu_ai_act",
        description=(
            "Search the EU AI Act knowledge base for articles, recitals, and annex "
            "sections relevant to a compliance topic or obligation."
        ),
    )
