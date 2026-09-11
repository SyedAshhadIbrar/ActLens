from app.agents.base import AgentContext, AgentResult
from app.agents.langchain.rag_runner import run_rag_agent
from app.pipeline.rag import RAGPipeline


class RAGAgent:
    def __init__(self, pipeline: RAGPipeline) -> None:
        self._pipeline = pipeline

    async def run(self, context: AgentContext) -> AgentResult:
        return await run_rag_agent(context, self._pipeline)
