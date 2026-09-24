# Security policy

## Supported versions

ActLens is currently a pre-1.0 portfolio project. Security fixes are applied to
the latest commit on the `main` branch.

## Reporting a vulnerability

Do not open a public issue for vulnerabilities, exposed credentials, or private
document leaks. Use GitHub's private vulnerability reporting feature for this
repository. If that feature is unavailable, contact the repository owner
privately.

Include:

- A description of the issue and its impact
- Reproduction steps
- Affected endpoints or files
- Any suggested mitigation

Do not include real API keys, access tokens, or private documents.

## Deployment warning

The current application is designed for trusted local evaluation. It does not
yet provide authentication, authorization, tenant isolation, or a durable audit
log. Do not expose it directly to the public internet or process confidential
documents without adding those controls and reviewing the selected LLM
provider's data-handling terms.

## Credential hygiene

- Store provider keys only in `.env` or a deployment secret manager.
- Never expose provider credentials through Vite environment variables.
- Rotate a credential immediately if it appears in a commit, log, screenshot,
  issue, or chat transcript.
- Keep generated indexes and uploaded source documents out of version control.
