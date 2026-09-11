from abc import ABC, abstractmethod
from typing import Literal

EmbedInputType = Literal["query", "document"]


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a completion from system + user prompts."""


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(
        self,
        texts: list[str],
        *,
        input_type: EmbedInputType = "document",
    ) -> list[list[float]]:
        """Embed a batch of texts into vectors."""