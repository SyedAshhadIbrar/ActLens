from app.agents.base import AgentContext, AgentResult
from app.agents.gap_agent import GapAnalysisAgent
from app.agents.rag_agent import RAGAgent
from app.core.providers.base import LLMProvider
from app.pipeline.rag import RAGPipeline


class AgentOrchestrator:
    def __init__(self, pipeline: RAGPipeline, llm: LLMProvider) -> None:
        self._rag_agent = RAGAgent(pipeline)
        self._gap_agent = GapAnalysisAgent(pipeline, llm)

    async def run(self, context: AgentContext) -> AgentResult:
        if context.mode == "gap" or context.document_text:
            return await self._gap_agent.run(context)
        return await self._rag_agent.run(context)
