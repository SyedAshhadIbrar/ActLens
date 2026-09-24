interface SuggestionChipsProps {
  suggestions: string[];
  onSelect: (text: string) => void;
}

export function SuggestionChips({ suggestions, onSelect }: SuggestionChipsProps) {
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {suggestions.map((text) => (
        <button
          key={text}
          type="button"
          onClick={() => onSelect(text)}
          className="max-w-full rounded-full border border-line bg-white px-3 py-2 text-left text-xs font-medium leading-snug text-ink shadow-sm transition hover:border-accent/30 hover:bg-accent-soft/40 sm:max-w-[min(100%,28rem)] sm:px-4 sm:text-sm"
        >
          {text}
        </button>
      ))}
    </div>
  );
}
