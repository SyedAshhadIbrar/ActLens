from app.core.models import Citation, HistoryMessage, WorkspaceMode
from app.core.providers.base import LLMProvider
from app.ingestion.chunker import Chunk, chunk_label

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "nl": "Dutch",
}

MODE_INSTRUCTIONS: dict[WorkspaceMode, str] = {
    "ask": "Answer compliance questions with precise legal citations.",
    "classify": (
        "Help classify whether the described AI system may be prohibited, high-risk, "
        "limited-risk, or minimal-risk. List applicable articles and outstanding unknowns."
    ),
    "find": (
        "Locate and summarize the exact EU AI Act provisions requested. "
        "Lead with the primary article, recital, or annex."
    ),
    "compare": (
        "Compare the requested provisions side by side. "
        "Highlight obligations, scope differences, and overlaps."
    ),
    "explain": (
        "Explain the legal requirements in plain language for a non-lawyer product or "
        "compliance audience while keeping citations accurate."
    ),
}


def _system_prompt(language: str, mode: WorkspaceMode) -> str:
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


def _format_history(history: list[HistoryMessage]) -> str:
    if not history:
        return ""
    lines = ["Recent conversation:"]
    for message in history[-6:]:
        speaker = "User" if message.role == "user" else "Assistant"
        lines.append(f"{speaker}: {message.content}")
    return "\n".join(lines)


def _build_user_prompt(
    query: str,
    context: str,
    language: str,
    history: list[HistoryMessage],
) -> str:
    language_name = LANGUAGE_NAMES.get(language, "English")
    history_block = _format_history(history)
    history_section = f"\n\n{history_block}\n" if history_block else ""
    return f"""Context from the EU AI Act ({language_name}):

{context}
{history_section}
---

Question: {query}

Provide a thorough answer in {language_name} based only on the context above. Include inline citations."""


def _extract_citations(chunks: list[Chunk]) -> list[Citation]:
    citations: list[Citation] = []
    seen_labels: set[str] = set()

    for chunk in chunks:
        label = chunk_label(chunk)
        if label in seen_labels:
            continue
        seen_labels.add(label)

        excerpt = chunk.text[:500] + ("..." if len(chunk.text) > 500 else "")
        citations.append(
            Citation(
                label=label,
                excerpt=excerpt,
                source_file=chunk.source_file,
                source_url=chunk.source_url,
            )
        )

    return citations


async def generate_answer(
    llm: LLMProvider,
    query: str,
    context: str,
    source_chunks: list[Chunk],
    language: str = "en",
    mode: WorkspaceMode = "ask",
    history: list[HistoryMessage] | None = None,
) -> tuple[str, list[Citation]]:
    user_prompt = _build_user_prompt(query, context, language, history or [])
    answer = await llm.generate(_system_prompt(language, mode), user_prompt)
    citations = _extract_citations(source_chunks)
    return answer, citations
