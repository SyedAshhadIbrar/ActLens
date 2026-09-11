from langchain_core.messages import AIMessage, HumanMessage

from app.agents.langchain.messages import history_to_messages
from app.core.models import HistoryMessage


def test_history_to_messages_maps_roles():
    history = [
        HistoryMessage(role="user", content="What is Article 9?"),
        HistoryMessage(role="assistant", content="Article 9 covers risk management."),
    ]
    messages = history_to_messages(history)
    assert len(messages) == 2
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    assert messages[0].content == "What is Article 9?"
