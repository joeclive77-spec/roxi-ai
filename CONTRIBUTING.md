# Contributing to Roxi AI

Thanks for your interest in contributing. This project aims to stay small,
focused, and easy to read — every change should make that truer, not less.

## Development setup

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Mobile
```bash
cd mobile
npm install
npx expo start
```

### Tests
```bash
cd backend
python -m pytest
```

## Workflow

1. Fork the repo and create a topic branch (`feat/...`, `fix/...`, `docs/...`).
2. Make your change. Keep commits small and self-contained.
3. Run the test suite and any relevant linters.
4. Open a pull request against `main` with:
   - A short, imperative title ("Add X", not "Added X")
   - A summary of the *why*, not just the *what*
   - Linked issues, if any
5. Address review feedback in additional commits — squash on merge.

## Coding conventions

- **Python**: type hints, `pydantic` for config and schemas, async I/O for network calls.
- **JavaScript / React Native**: ES modules, named exports, no default exports for utilities.
- **Commits**: imperative mood, present tense ("Add", "Fix", "Refactor").
- **Secrets**: never commit `.env` or any real API key. Placeholders only.

## Code of conduct

Be respectful. Assume good faith. No harassment, no personal attacks. Violations
can be reported via the same channel as security issues.

## License

By contributing, you agree that your contributions will be licensed under the
MIT License (see [LICENSE](LICENSE)).
