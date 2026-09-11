from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.core.models import HistoryMessage


def history_to_messages(history: list[HistoryMessage]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for message in history[-6:]:
        if message.role == "user":
            messages.append(HumanMessage(content=message.content))
        else:
            messages.append(AIMessage(content=message.content))
    return messages
