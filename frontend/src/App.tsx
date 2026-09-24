import { useCallback, useEffect, useState } from "react";
import { checkHealth, sendChat } from "./api/client";
import { ResizableWorkspace } from "./components/layout/ResizableWorkspace";
import { TopNav } from "./components/layout/TopNav";
import type {
  ChatMessage,
  Citation,
  ChunkMeta,
  HistoryMessage,
  LanguageCode,
} from "./types/api";

function createId() {
  return crypto.randomUUID();
}

function toHistory(messages: ChatMessage[]): HistoryMessage[] {
  return messages.slice(-8).map((message) => ({
    role: message.role,
    content: message.content,
  }));
}

export default function App() {
  const [language, setLanguage] = useState<LanguageCode>("en");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState(true);
  const [indexReady, setIndexReady] = useState(false);
  const [documentName, setDocumentName] = useState<string | null>(null);
  const [documentText, setDocumentText] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [retrievedChunks, setRetrievedChunks] = useState<ChunkMeta[]>([]);

  useEffect(() => {
    checkHealth()
      .then((health) => {
        setBackendOnline(true);
        setIndexReady(health.index_ready);
      })
      .catch(() => {
        setBackendOnline(false);
        setIndexReady(false);
      });
  }, []);

  const handleNewConversation = () => {
    setMessages([]);
    setInput("");
    setSelectedCitation(null);
    setRetrievedChunks([]);
    setDocumentName(null);
    setDocumentText(null);
    setError(null);
  };

  const handleSelectCitation = useCallback((citation: Citation) => {
    setSelectedCitation(citation);
  }, []);

  const handleSelectPassage = useCallback((chunk: ChunkMeta) => {
    setSelectedCitation({
      label: chunk.citation_label ?? chunk.article ?? "Provision",
      excerpt: chunk.text,
      source_file: chunk.source_file,
      source_url: chunk.source_url,
      score: chunk.score,
    });
  }, []);

  const submitQuery = useCallback(
    async (query: string) => {
      const trimmed = query.trim();
      if (!trimmed || loading) return;
      if (!indexReady) {
        setError(
          backendOnline
            ? "Index not ready. Run python scripts/ingest.py, then refresh."
            : "Backend not reachable. Start uvicorn on port 8000, then refresh."
        );
        return;
      }
      if (documentText && !documentName) {
        setError("Attach a document to check compliance.");
        return;
      }

      const mode = documentText ? "gap" : "ask";

      setError(null);
      setInput("");
      setLoading(true);

      const userMessage: ChatMessage = {
        id: createId(),
        role: "user",
        content: trimmed,
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await sendChat(trimmed, language, {
          mode,
          history: toHistory(messages),
          documentText,
          documentName,
        });
        const assistantMessage: ChatMessage = {
          id: createId(),
          role: "assistant",
          content: response.answer,
          citations: response.citations,
          retrievedChunks: response.retrieved_chunks,
          agent: response.agent,
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setRetrievedChunks(response.retrieved_chunks);
        setSelectedCitation(response.citations[0] ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Something went wrong");
      } finally {
        setLoading(false);
      }
    },
    [backendOnline, documentName, documentText, indexReady, language, loading, messages]
  );

  const handleSelectSuggestion = (text: string) => {
    setInput(text);
    if (text.endsWith("?") || text.length > 30) {
      submitQuery(text);
    }
  };

  return (
    <div className="flex h-screen min-h-0 flex-col overflow-hidden supports-[height:100dvh]:h-dvh">
      <TopNav
        language={language}
        onLanguageChange={setLanguage}
        onNewConversation={handleNewConversation}
      />

      {error && (
        <div className="shrink-0 border-b border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 sm:px-5">
          {error}
        </div>
      )}

      <ResizableWorkspace
        messages={messages}
        language={language}
        input={input}
        loading={loading}
        indexReady={indexReady}
        backendOnline={backendOnline}
        documentName={documentName}
        selectedCitationLabel={selectedCitation?.label}
        selectedCitation={selectedCitation}
        retrievedChunks={retrievedChunks}
        onInputChange={setInput}
        onSubmit={() => submitQuery(input)}
        onSelectCitation={handleSelectCitation}
        onSelectSuggestion={handleSelectSuggestion}
        onSelectPassage={handleSelectPassage}
        onDocumentUploaded={(name, text) => {
          setDocumentName(name);
          setDocumentText(text);
          setError(null);
        }}
        onDocumentClear={() => {
          setDocumentName(null);
          setDocumentText(null);
        }}
      />
    </div>
  );
}
