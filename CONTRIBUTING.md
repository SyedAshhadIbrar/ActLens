# Contributing to ActLens

Thanks for helping improve ActLens. Contributions should preserve the project's
core goal: answers must be grounded in retrieved EU AI Act text and accompanied
by inspectable evidence.

## Development setup

1. Fork and clone the repository.
2. Copy `.env.example` to `.env`.
3. Create a Python 3.11 virtual environment.
4. Install the backend with development dependencies:

   ```bash
   cd backend
   pip install -e ".[dev]"
   ```

5. Install the frontend:

   ```bash
   cd frontend
   npm ci
   ```

See [README.md](README.md) for ingestion and startup instructions.

## Before opening a pull request

Run the backend checks:

```bash
cd backend
ruff check app tests
pytest
```

Run the frontend build:

```bash
cd frontend
npm run build
```

If retrieval behavior changes, include or update evaluation cases under
`evals/` and report the before-and-after metrics.

## Pull request guidelines

- Keep changes focused and explain the user-facing impact.
- Add tests for new behavior and bug fixes.
- Do not commit `.env`, credentials, indexes, model caches, or private documents.
- Document configuration changes in `.env.example`.
- Do not claim legal correctness without an appropriate evaluation.
- Clearly identify generated output as compliance support, not legal advice.

## Reporting problems

Use a GitHub issue for reproducible bugs and feature proposals. For
vulnerabilities or accidental credential exposure, follow
[SECURITY.md](SECURITY.md) instead of opening a public issue.
