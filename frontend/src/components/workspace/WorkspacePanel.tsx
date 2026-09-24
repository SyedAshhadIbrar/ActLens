import type { ChatMessage, Citation, LanguageCode } from "../../types/api";
import { SUGGESTIONS } from "../../data/workspace";
import { ChatInput } from "./ChatInput";
import { ChatMessageList } from "./ChatMessageList";
import { EmptyState } from "./EmptyState";
import { SetupRequired } from "./SetupRequired";
import { SuggestionChips } from "./SuggestionChips";

interface WorkspacePanelProps {
  messages: ChatMessage[];
  language: LanguageCode;
  input: string;
  loading: boolean;
  indexReady: boolean;
  backendOnline: boolean;
  documentName: string | null;
  selectedCitationLabel?: string | null;
  onDocumentUploaded: (name: string, text: string) => void;
  onDocumentClear: () => void;
  onInputChange: (value: string) => void;
  onSubmit: () => void;
  onSelectCitation: (citation: Citation) => void;
  onSelectSuggestion: (text: string) => void;
}

export function WorkspacePanel({
  messages,
  language,
  input,
  loading,
  indexReady,
  backendOnline,
  documentName,
  selectedCitationLabel,
  onDocumentUploaded,
  onDocumentClear,
  onInputChange,
  onSubmit,
  onSelectCitation,
  onSelectSuggestion,
}: WorkspacePanelProps) {
  const hasMessages = messages.length > 0;
  const followUpSuggestions = SUGGESTIONS[language].slice(1);

  return (
    <main className="flex h-full min-h-0 min-w-0 flex-col bg-canvas">
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-3 py-4 sm:px-6">
        {!indexReady && (
          <div className="mx-auto mb-4 max-w-3xl">
            <SetupRequired backendOnline={backendOnline} />
          </div>
        )}

        {!hasMessages ? (
          <EmptyState
            language={language}
            setupPending={!indexReady}
            onSelectSuggestion={onSelectSuggestion}
          />
        ) : (
          <>
            <ChatMessageList
              messages={messages}
              onSelectCitation={onSelectCitation}
              selectedCitationLabel={selectedCitationLabel}
              loading={loading}
            />

            {!loading && followUpSuggestions.length > 0 && (
              <div className="mx-auto mb-4 flex w-full max-w-3xl justify-center">
                <SuggestionChips
                  suggestions={followUpSuggestions}
                  onSelect={onSelectSuggestion}
                />
              </div>
            )}
          </>
        )}
      </div>

      <ChatInput
        value={input}
        language={language}
        loading={loading}
        documentName={documentName}
        onChange={onInputChange}
        onDocumentUploaded={onDocumentUploaded}
        onDocumentClear={onDocumentClear}
        onSubmit={onSubmit}
      />
    </main>
  );
}
