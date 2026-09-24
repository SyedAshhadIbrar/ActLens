import { CheckCircle2, ExternalLink } from "lucide-react";
import { useState } from "react";
import type { ChunkMeta, Citation } from "../../types/api";
import { articleBadge, cn } from "../../lib/utils";

type InspectorTab = "citation" | "passages";

interface EvidenceInspectorProps {
  citation: Citation | null;
  passages: ChunkMeta[];
  language: string;
  sourceCount: number;
  onSelectPassage: (chunk: ChunkMeta) => void;
}

function titleFromCitation(citation: Citation): string {
  if (citation.label.toLowerCase().includes("risk management")) {
    return "Risk management system";
  }
  return citation.label.replace(/AI Act/i, "").trim();
}

function matchingPassage(citation: Citation | null, passages: ChunkMeta[]): ChunkMeta | undefined {
  if (!citation) return undefined;
  return passages.find(
    (passage) =>
      passage.citation_label === citation.label ||
      passage.article === citation.label ||
      passage.chunk_id === citation.source_file
  );
}

export function EvidenceInspector({
  citation,
  passages,
  language,
  sourceCount,
  onSelectPassage,
}: EvidenceInspectorProps) {
  const [tab, setTab] = useState<InspectorTab>("citation");
  const activePassage = matchingPassage(citation, passages);
  const fullExcerpt = activePassage?.text ?? citation?.excerpt;

  if (!citation && passages.length === 0) {
    return (
      <aside className="flex h-full min-h-0 min-w-0 flex-col bg-white lg:border-l lg:border-line">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-sm font-semibold text-ink">Evidence inspector</h2>
        </div>
        <div className="flex flex-1 items-center justify-center p-6 text-center text-sm text-muted">
          Run a compliance review to inspect retrieved provisions and EUR-Lex sources here.
        </div>
      </aside>
    );
  }

  const related = passages
    .filter((chunk) => chunk.citation_label && chunk.citation_label !== citation?.label)
    .slice(0, 4);

  return (
    <aside className="flex h-full min-h-0 min-w-0 flex-col bg-white lg:border-l lg:border-line">
      <div className="border-b border-line px-5 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-ink">Evidence inspector</h2>
          <span className="rounded-full bg-badge-bg px-2.5 py-0.5 text-xs font-medium text-badge">
            {sourceCount} source{sourceCount === 1 ? "" : "s"}
          </span>
        </div>

        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={() => setTab("citation")}
            className={cn(
              "rounded-full px-3 py-1.5 text-xs font-medium",
              tab === "citation"
                ? "bg-navy text-white"
                : "bg-canvas text-muted hover:text-ink"
            )}
          >
            Citation details
          </button>
          <button
            type="button"
            onClick={() => setTab("passages")}
            className={cn(
              "rounded-full px-3 py-1.5 text-xs font-medium",
              tab === "passages"
                ? "bg-navy text-white"
                : "bg-canvas text-muted hover:text-ink"
            )}
          >
            Retrieved passages
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-5">
        {tab === "citation" && citation && (
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-badge-bg px-2 py-1 text-[11px] font-bold tracking-wide text-badge">
                {articleBadge(citation.label)}
              </span>
              <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">
                {language.toUpperCase()} · EU AI Act
              </span>
            </div>

            <h3 className="mt-4 text-2xl font-semibold tracking-tight text-ink">
              {titleFromCitation(citation)}
            </h3>
            <p className="mt-1 text-sm text-muted">{citation.label} · Regulation (EU) 2024/1689</p>

            <div className="mt-5">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">
                Structure path
              </p>
              <div className="mt-2 rounded-xl border border-line bg-canvas px-3 py-2 font-mono text-sm text-ink">
                {activePassage?.structure_path ?? "—"}
              </div>
            </div>

            <div className="mt-5">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">
                Source text
              </p>
              <blockquote className="mt-2 rounded-xl border border-accent/20 bg-accent-soft/30 px-4 py-3 text-sm leading-7 text-ink whitespace-pre-wrap">
                {fullExcerpt}
              </blockquote>
            </div>

            {citation.source_url && (
              <a
                href={citation.source_url}
                target="_blank"
                rel="noreferrer"
                className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-line bg-white px-4 py-3 text-sm font-medium text-ink shadow-sm hover:bg-canvas"
              >
                Open official text on EUR-Lex
                <ExternalLink className="h-4 w-4" />
              </a>
            )}

            {related.length > 0 && (
              <div className="mt-6">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">
                  Related provisions
                </p>
                <div className="mt-3 space-y-2">
                  {related.map((chunk) => (
                    <button
                      key={chunk.chunk_id}
                      type="button"
                      onClick={() => onSelectPassage(chunk)}
                      className="block w-full rounded-lg border border-transparent px-1 py-1 text-left text-sm text-accent hover:border-line hover:bg-canvas"
                    >
                      {chunk.citation_label ?? chunk.article ?? chunk.chunk_id}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {tab === "passages" && (
          <div className="space-y-4">
            {passages.map((chunk) => (
              <button
                key={chunk.chunk_id}
                type="button"
                onClick={() => onSelectPassage(chunk)}
                className="block w-full rounded-xl border border-line bg-canvas p-4 text-left transition hover:border-accent/30 hover:bg-white"
              >
                <div className="text-xs font-semibold text-accent">
                  {chunk.citation_label ?? chunk.article ?? "Provision"}
                </div>
                <p className="mt-2 text-sm leading-6 text-ink/85 whitespace-pre-wrap">{chunk.text}</p>
                {chunk.score != null && (
                  <p className="mt-2 text-xs text-muted">Relevance score: {chunk.score.toFixed(3)}</p>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-line px-5 py-4">
        <div className="flex items-start gap-2 text-xs leading-5 text-muted">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-badge" />
          <p>
            Grounded in {sourceCount} retrieved source{sourceCount === 1 ? "" : "s"}. Not legal advice —{" "}
            <a
              href={
                citation?.source_url ??
                "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689"
              }
              target="_blank"
              rel="noreferrer"
              className="font-medium text-accent hover:text-navy"
            >
              verify on EUR-Lex
            </a>
          </p>
        </div>
      </div>
    </aside>
  );
}
