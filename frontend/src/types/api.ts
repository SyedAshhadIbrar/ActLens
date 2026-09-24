export type LanguageCode = "en" | "fr" | "nl";
export type WorkspaceMode = "ask" | "classify" | "find" | "compare" | "explain" | "gap";

export interface HistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export interface Citation {
  label: string;
  excerpt: string;
  source_file: string;
  source_url?: string | null;
  score?: number | null;
}

export interface ChunkMeta {
  chunk_id: string;
  text: string;
  article?: string | null;
  recital?: string | null;
  annex?: string | null;
  source_file: string;
  page?: number | null;
  language?: string | null;
  citation_label?: string | null;
  structure_path?: string | null;
  source_url?: string | null;
  score?: number | null;
}

export interface ChatResponse {
  answer: string;
  language: LanguageCode;
  citations: Citation[];
  retrieved_chunks: ChunkMeta[];
  agent: string;
}

export interface UploadResponse {
  filename: string;
  char_count: number;
  text: string;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  index_ready: boolean;
  chunk_count: number;
  supported_languages: string[];
  agents?: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  retrievedChunks?: ChunkMeta[];
  agent?: string;
}
