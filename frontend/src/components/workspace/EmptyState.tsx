import type { LanguageCode } from "../../types/api";
import { SUGGESTIONS } from "../../data/workspace";
import { SuggestionChips } from "./SuggestionChips";

interface EmptyStateProps {
  language: LanguageCode;
  setupPending?: boolean;
  onSelectSuggestion: (text: string) => void;
}

export function EmptyState({
  language,
  setupPending = false,
  onSelectSuggestion,
}: EmptyStateProps) {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center px-2 pt-8 text-center sm:pt-12">
      <img src="/logo.png" alt="" className="mb-5 h-16 w-16 rounded-2xl object-cover shadow-panel" />

      {!setupPending && (
        <>
          <h1 className="text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
            EU AI Act compliance
          </h1>
          <p className="mt-3 text-sm leading-6 text-muted sm:text-[15px]">
            Ask questions about the regulation, or attach your policy to see if it
            meets EU AI Act requirements — with cited sources.
          </p>
        </>
      )}

      <div className={setupPending ? "mt-4" : "mt-8"}>
        <SuggestionChips
          suggestions={SUGGESTIONS[language]}
          onSelect={onSelectSuggestion}
        />
      </div>
    </div>
  );
}
