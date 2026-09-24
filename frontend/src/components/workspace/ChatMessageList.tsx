import type { ChatMessage, Citation } from "../../types/api";
import { AssistantMessage } from "./AssistantMessage";
import { UserMessage } from "./UserMessage";

interface ChatMessageListProps {
  messages: ChatMessage[];
  onSelectCitation: (citation: Citation) => void;
  selectedCitationLabel?: string | null;
  loading: boolean;
}

export function ChatMessageList({
  messages,
  onSelectCitation,
  selectedCitationLabel,
  loading,
}: ChatMessageListProps) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 pb-4 sm:gap-6">
      {messages.map((message) =>
        message.role === "user" ? (
          <UserMessage key={message.id} content={message.content} />
        ) : (
          <AssistantMessage
            key={message.id}
            content={message.content}
            citations={message.citations ?? []}
            agent={message.agent}
            onSelectCitation={onSelectCitation}
            selectedCitationLabel={selectedCitationLabel}
          />
        )
      )}

      {loading && (
        <div className="flex gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-navy text-sm font-bold text-white">
            A
          </div>
          <div className="rounded-2xl border border-line bg-white px-4 py-3 text-sm text-muted shadow-panel sm:px-5 sm:py-4">
            Retrieving context and drafting answer...
          </div>
        </div>
      )}
    </div>
  );
}
