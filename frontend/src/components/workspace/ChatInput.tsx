import { ArrowUp, Paperclip, X } from "lucide-react";
import type { LanguageCode } from "../../types/api";
import { PLACEHOLDERS } from "../../data/workspace";
import { uploadDocument } from "../../api/client";
import { cn } from "../../lib/utils";

const MAX_LENGTH = 2000;

interface ChatInputProps {
  value: string;
  language: LanguageCode;
  loading: boolean;
  documentName: string | null;
  onChange: (value: string) => void;
  onDocumentUploaded: (name: string, text: string) => void;
  onDocumentClear: () => void;
  onSubmit: () => void;
}

export function ChatInput({
  value,
  language,
  loading,
  documentName,
  onChange,
  onDocumentUploaded,
  onDocumentClear,
  onSubmit,
}: ChatInputProps) {
  const canSend = value.trim().length > 0 && !loading;
  const placeholder = documentName
    ? PLACEHOLDERS[language].check
    : PLACEHOLDERS[language].ask;

  const handleFile = async (file: File) => {
    const uploaded = await uploadDocument(file);
    onDocumentUploaded(uploaded.filename, uploaded.text);
  };

  return (
    <div className="shrink-0 border-t border-line bg-canvas px-3 py-3 sm:px-5 sm:py-4">
      <div className="mx-auto w-full max-w-3xl">
        {documentName && (
          <div className="mb-2 flex items-center justify-between rounded-lg border border-badge/30 bg-badge-bg px-3 py-2 text-xs sm:text-sm">
            <span className="truncate font-medium text-ink">{documentName}</span>
            <button
              type="button"
              onClick={onDocumentClear}
              className="ml-2 shrink-0 rounded-full p-1 text-muted hover:bg-white hover:text-ink"
              aria-label="Remove document"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        <div className="rounded-2xl border border-line bg-white p-3 shadow-input sm:rounded-[28px] sm:p-4">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value.slice(0, MAX_LENGTH))}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (canSend) onSubmit();
              }
            }}
            rows={2}
            placeholder={placeholder}
            className="w-full resize-none bg-transparent text-sm leading-6 text-ink placeholder:text-muted focus:outline-none sm:text-[15px] sm:leading-7"
          />

          <div className="mt-2 flex items-center justify-between gap-2 sm:mt-3">
            <label
              className="flex h-8 cursor-pointer items-center gap-1.5 rounded-full px-2 text-xs font-medium text-muted hover:bg-canvas hover:text-ink sm:text-sm"
              title="Attach your policy or AI documentation"
            >
              <Paperclip className="h-4 w-4" />
              <span className="hidden sm:inline">Check document</span>
              <input
                type="file"
                accept=".pdf,.txt,.md,.html,.htm"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) handleFile(file).catch(() => undefined);
                  event.target.value = "";
                }}
              />
            </label>

            <button
              type="button"
              disabled={!canSend}
              onClick={onSubmit}
              className={cn(
                "flex h-9 w-9 items-center justify-center rounded-full transition sm:h-10 sm:w-10",
                canSend ? "bg-accent text-white hover:bg-navy" : "bg-line text-muted"
              )}
              aria-label="Send message"
            >
              <ArrowUp className="h-5 w-5" />
            </button>
          </div>
        </div>

        <p className="mt-2 text-center text-xs text-muted">
          Ask about the EU AI Act, or attach a document to check compliance. Not legal advice.
        </p>
      </div>
    </div>
  );
}
