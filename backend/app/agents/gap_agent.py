from app.agents.base import AgentContext, AgentResult
from app.agents.langchain.gap_runner import run_gap_agent
from app.pipeline.rag import RAGPipeline


class GapAnalysisAgent:
    def __init__(self, pipeline: RAGPipeline, llm=None) -> None:
        self._pipeline = pipeline

    async def run(self, context: AgentContext) -> AgentResult:
        return await run_gap_agent(context, self._pipeline)
