import { ChevronDown, Plus } from "lucide-react";
import type { LanguageCode } from "../../types/api";
import { LANGUAGE_LABELS } from "../../data/workspace";
import { cn } from "../../lib/utils";

interface TopNavProps {
  language: LanguageCode;
  onLanguageChange: (lang: LanguageCode) => void;
  onNewConversation: () => void;
}

export function TopNav({ language, onLanguageChange, onNewConversation }: TopNavProps) {
  return (
    <header className="flex h-[52px] shrink-0 items-center justify-between gap-3 border-b border-line bg-white px-3 sm:px-5">
      <div className="flex min-w-0 items-center gap-2.5">
        <img
          src="/logo.png"
          alt="ActLens"
          className="h-9 w-9 shrink-0 rounded-lg object-cover"
        />
        <div className="min-w-0">
          <div className="text-sm font-semibold text-ink sm:text-[15px]">ActLens</div>
          <div className="hidden truncate text-xs text-muted sm:block">
            EU AI Act compliance · cited answers
          </div>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={onNewConversation}
          className="inline-flex items-center gap-1.5 rounded-full border border-line bg-white px-3 py-1.5 text-xs font-medium text-ink hover:bg-canvas sm:text-sm"
        >
          <Plus className="h-4 w-4" />
          <span className="hidden sm:inline">New chat</span>
        </button>

        <div className="relative">
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value as LanguageCode)}
            className={cn(
              "appearance-none rounded-lg border border-line bg-white py-1.5 pl-2 pr-7 text-xs font-medium text-ink sm:pl-3 sm:pr-8 sm:text-sm",
              "focus:outline-none focus:ring-2 focus:ring-accent/20"
            )}
            aria-label="Language"
          >
            {(Object.keys(LANGUAGE_LABELS) as LanguageCode[]).map((code) => (
              <option key={code} value={code}>
                {LANGUAGE_LABELS[code]}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
        </div>
      </div>
    </header>
  );
}
