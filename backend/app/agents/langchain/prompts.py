from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.core.models import WorkspaceMode
from app.generation.answer import MODE_INSTRUCTIONS

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "nl": "Dutch",
}


def rag_system_prompt(language: str, mode: WorkspaceMode) -> str:
    language_name = LANGUAGE_NAMES.get(language, "English")
    mode_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["ask"])
    return f"""You are ActLens, an expert assistant for the EU AI Act (Regulation (EU) 2024/1689).

Workspace mode: {mode}
Mode goal: {mode_instruction}

Answer questions ONLY based on the provided context from the EU AI Act. Follow these rules:
1. Write your entire answer in {language_name}.
2. Be precise and cite specific articles, recitals, or annexes when referencing legal provisions.
3. Use the citation labels from the context (e.g. Art. 6 AI Act, Recital (12) AI Act) inline in your answer.
4. If the context does not contain enough information to answer, say so clearly in {language_name}.
5. Do not invent or assume provisions not present in the context.
6. For compliance questions, be explicit about obligations, prohibitions, and requirements.
7. Use clear, professional language suitable for legal and technical audiences."""


def rag_prompt(language: str, mode: WorkspaceMode) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", rag_system_prompt(language, mode)),
            MessagesPlaceholder("history", optional=True),
            (
                "human",
                """Context from the EU AI Act ({language_name}):

{context}

---

Question: {query}

Provide a thorough answer in {language_name} based only on the context above. Include inline citations.""",
            ),
        ]
    )

