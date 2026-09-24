import type {
  ChatResponse,
  HealthResponse,
  HistoryMessage,
  LanguageCode,
  UploadResponse,
  WorkspaceMode,
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/v1/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? "Upload failed");
  }
  return res.json();
}

export async function sendChat(
  query: string,
  language: LanguageCode,
  options?: {
    mode?: WorkspaceMode;
    history?: HistoryMessage[];
    documentText?: string | null;
    documentName?: string | null;
  }
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      language,
      mode: options?.mode ?? "ask",
      history: options?.history ?? [],
      document_text: options?.documentText ?? null,
      document_name: options?.documentName ?? null,
    }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = body.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg ?? String(item)).join("; ")
          : `Request failed (${res.status})`;
    throw new Error(message);
  }

  return res.json();
}
