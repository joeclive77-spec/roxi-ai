# Security Policy

## Reporting a vulnerability

If you discover a security issue in Roxi AI, **please do not open a public issue.**
Email the maintainers directly at **[email protected]** (or open a private
security advisory on the repository if GitHub is enabled for it).

Include:
- A description of the vulnerability and its impact
- Reproduction steps or a minimal proof-of-concept
- The affected component(s) (backend, mobile, docs)
- Any suggested mitigations if you have them

You can expect:
- An acknowledgement within **72 hours**
- A status update within **7 days**
- A coordinated disclosure timeline agreed before any public release

## Secrets

- **Never** commit API keys, tokens, or credentials.
- Use `backend/.env` locally (already git-ignored); inject secrets via your
  platform's secret manager in production.
- Rotate any key that has been exposed in a public place.

## Supported versions

Only the latest commit on `main` is actively supported with security fixes.
Older commits are best-effort.

## Acknowledgements

We appreciate responsible disclosure. Reporters will be credited (unless they
prefer anonymity) in the release notes once the fix ships.
