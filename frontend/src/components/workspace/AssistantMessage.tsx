import { Copy, ExternalLink } from "lucide-react";
import ReactMarkdown from "react-markdown";
import type { Citation } from "../../types/api";
import { formatAnswerWithCitations } from "../../lib/export";

interface AssistantMessageProps {
  content: string;
  citations: Citation[];
  agent?: string;
  onSelectCitation: (citation: Citation) => void;
  selectedCitationLabel?: string | null;
}

export function AssistantMessage({
  content,
  citations,
  agent,
  onSelectCitation,
  selectedCitationLabel,
}: AssistantMessageProps) {
  const copyResponse = async () => {
    await navigator.clipboard.writeText(content);
  };

  const copyWithCitations = async () => {
    await navigator.clipboard.writeText(formatAnswerWithCitations(content, citations));
  };

  return (
    <div className="flex gap-3">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-navy text-sm font-bold text-white">
        A
      </div>

      <div className="min-w-0 flex-1 rounded-2xl border border-line bg-white p-5 shadow-panel">
        {agent && (
          <div className="mb-3">
            <span className="rounded-full bg-canvas px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-muted">
              {agent.replace(/_/g, " ")}
            </span>
          </div>
        )}
        <div className="markdown-body">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        {citations.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {citations.map((citation, index) => (
              <button
                key={`${citation.label}-${citation.source_file}-${index}`}
                type="button"
                onClick={() => onSelectCitation(citation)}
                className={`inline-flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs font-medium transition ${
                  selectedCitationLabel === citation.label
                    ? "border-accent bg-accent-soft text-accent"
                    : "border-line bg-canvas text-ink hover:border-accent/30"
                }`}
              >
                <span className="text-muted">§</span>
                {citation.label}
              </button>
            ))}
          </div>
        )}

        <div className="mt-4 flex flex-wrap items-center gap-4 border-t border-line pt-4 text-sm">
          <button
            type="button"
            onClick={copyWithCitations}
            className="inline-flex items-center gap-2 font-medium text-accent hover:text-navy"
          >
            <Copy className="h-4 w-4" />
            Copy with citations
          </button>
          <button
            type="button"
            onClick={copyResponse}
            className="inline-flex items-center gap-2 font-medium text-muted hover:text-ink"
          >
            Copy answer only
          </button>
          {citations[0]?.source_url && (
            <a
              href={citations[0].source_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 font-medium text-accent hover:text-navy"
            >
              <ExternalLink className="h-4 w-4" />
              View on EUR-Lex
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
