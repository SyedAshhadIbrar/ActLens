import type { Citation } from "../types/api";

export function formatAnswerWithCitations(answer: string, citations: Citation[]): string {
  const lines = [answer.trim(), "", "## Sources"];
  for (const citation of citations) {
    lines.push(`- **${citation.label}**`);
    lines.push(`  > ${citation.excerpt}`);
    if (citation.source_url) {
      lines.push(`  ${citation.source_url}`);
    }
  }
  lines.push("", "_Not legal advice. Verify on EUR-Lex._");
  return lines.join("\n");
}
