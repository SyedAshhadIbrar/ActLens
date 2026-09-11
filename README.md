# ActLens: EU AI Act RAG Assistant

A production-oriented Retrieval-Augmented Generation (RAG) assistant for querying the EU AI Act with verifiable source citations.

**Detailed documentation:** [docs/PROJECT.md](docs/PROJECT.md)

## Features

- **Hybrid Search** — Semantic (ChromaDB) + keyword (BM25) with Reciprocal Rank Fusion
- **Cross-Encoder Re-ranking** — Refines retrieval results for relevance
- **Structured Multilingual Dataset** — Pre-chunked EU AI Act from [Hugging Face](https://huggingface.co/datasets/jeroenherczeg/eu-ai-act) with article/recital/annex metadata and citation labels
- **Adaptive Chunking** — Article/recital/annex-aware splitting for local PDF/HTML files
- **Incremental Indexing** — Only re-embeds changed chunks on re-ingest
- **Verifiable Citations** — Every answer cites specific articles, recitals, or annexes
- **Pluggable LLM Providers** — OpenAI, Anthropic, Google Gemini, or Ollama via environment config

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- At least one LLM provider configured (OpenAI API key, Anthropic API key, or local Ollama)

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env with your API keys and provider choice
```

### 2. Ingest the EU AI Act

By default, ActLens ingests the structured multilingual dataset from Hugging Face:

```bash
python scripts/ingest.py
```

Index multiple languages:

```bash
python scripts/ingest.py --languages en,nl,fr,de
```

Or ingest local PDF/HTML files from EUR-Lex instead:

```bash
# Download from https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689
# Place files in data/raw/, then:
python scripts/ingest.py --source files
```

### 3. Start with Docker

```bash
docker-compose up --build
```

### 4. Or run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
cd ..
python scripts/ingest.py
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Query the API

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the obligations for high-risk AI systems under Article 6?", "language": "en"}'
```

French example:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Quelles sont les obligations pour les systèmes IA à haut risque?", "language": "fr"}'
```

Supported languages: `en` (English), `fr` (French), `nl` (Dutch).

OpenAPI docs: http://localhost:8000/docs

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the UI proxies API calls to the backend.

Or with Docker (frontend on port 5173):

```bash
docker-compose up --build
```

## Project Structure

```
ActLens/
├── backend/          # FastAPI RAG backend
│   └── app/
│       ├── api/          # REST routes
│       ├── core/         # Config, models, LLM providers
│       ├── ingestion/    # HF dataset, document loading, chunking, indexing
│       ├── retrieval/    # Hybrid search (vector + BM25)
│       ├── processing/   # Context preparation
│       ├── ranking/      # Cross-encoder re-ranking
│       ├── generation/   # Answer generation with citations
│       └── pipeline/     # Full RAG orchestration
├── frontend/         # React chat UI (Vite + Tailwind)
│   └── src/
│       ├── components/layout/     # TopNav, LeftSidebar
│       ├── components/workspace/  # Chat + empty state
│       └── components/inspector/  # Evidence inspector panel
├── data/raw/         # Optional local PDF/HTML files
├── scripts/          # CLI tools (ingest)
└── storage/          # Chroma, BM25, and HF cache (gitignored)
```

## API Endpoints

| Method | Path                | Description                    |
|--------|---------------------|--------------------------------|
| GET    | `/health`           | Health check + index status    |
| POST   | `/api/v1/chat`      | Query → answer with citations  |
| POST   | `/api/v1/ingest`    | Trigger document indexing      |
| GET    | `/api/v1/documents` | List indexed sources           |

## Environment Variables

See [`.env.example`](.env.example) for all configuration options. Key settings:

| Variable          | Description                          | Default    |
|-------------------|--------------------------------------|------------|
| `DATA_SOURCE`     | `hf`, `files`, or `both`             | `hf`       |
| `HF_DATASET_ID`   | Hugging Face dataset repo            | `jeroenherczeg/eu-ai-act` |
| `HF_DATASET_LANGUAGES` | Comma-separated ISO codes (`en`, `fr`, `nl`) | `en,fr,nl` |
| `LLM_PROVIDER`    | `openai`, `anthropic`, `gemini`, or `ollama` | `gemini`   |
| `EMBEDDING_PROVIDER` | `hf` (local, free), `openai`, `gemini`, or `ollama` | `hf` |
| `HF_EMBEDDING_MODEL` | sentence-transformers model on Hugging Face | `intfloat/multilingual-e5-small` |
| `GOOGLE_API_KEY`  | Google AI Studio API key (for Gemini) | —          |
| `GEMINI_MODEL`    | Gemini chat model                    | `gemini-3.6-flash` |
| `RETRIEVAL_TOP_K` | Candidates from hybrid search        | `20`       |
| `RERANK_TOP_N`    | Chunks after re-ranking              | `5`        |

## License

MIT
