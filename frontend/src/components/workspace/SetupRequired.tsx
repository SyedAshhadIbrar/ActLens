import { AlertCircle, Server } from "lucide-react";

interface SetupRequiredProps {
  backendOnline: boolean;
}

export function SetupRequired({ backendOnline }: SetupRequiredProps) {
  if (!backendOnline) {
    return (
      <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900">
        <div className="flex items-center gap-2 font-medium">
          <AlertCircle className="h-4 w-4 shrink-0" />
          Backend not running on port 8000
        </div>
        <details className="mt-2 text-xs text-red-800">
          <summary className="cursor-pointer">Show start command</summary>
          <pre className="mt-2 overflow-x-auto rounded-lg bg-white/80 px-3 py-2">
            cd backend{"\n"}.venv\Scripts\uvicorn app.main:app --reload --port 8000
          </pre>
        </details>
      </div>
    );
  }

  return (
    <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
      <div className="flex items-center gap-2 font-medium">
        <Server className="h-4 w-4 shrink-0" />
        Index not built yet — run ingest once, then refresh
      </div>
      <details className="mt-2 text-xs text-amber-900">
        <summary className="cursor-pointer">Show setup steps</summary>
        <pre className="mt-2 overflow-x-auto rounded-lg bg-white/80 px-3 py-2">
          cp .env.example .env{"\n"}# add OPENAI_API_KEY{"\n"}python scripts/ingest.py
        </pre>
      </details>
    </div>
  );
}
