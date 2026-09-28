# Project for Agents

This repository is optimized to be understood by AI Agents.

## What is this project?
A reference application demonstrating how to build a complete web app using **Agnara** as the core logic engine, accompanied by Starlette (web), SQLAlchemy (DB), and Jinja2 (templates).

## Architecture
Strict layered architecture. See `docs/ARCHITECTURE.md`.
- **Web**: `app/web/`
- **Capabilities**: `app/capabilities/`
- **Domain Contracts**: `app/domain/`
- **Infrastructure**: `app/infrastructure/`

## How to Run (Docker)
```bash
docker compose up --build
```
Access at `http://localhost:8000`.

## How to Test
```bash
uv run pytest
```

## Hard Rules (Never Break These)
1. **Business logic belongs in Agnara capabilities.**
2. **Web routes must not duplicate domain logic.**
3. **UI code (or web routes) must not query the database directly.**
4. **Repository implementations belong in infrastructure.**
5. **Capabilities depend on repository contracts (Protocols), not SQLAlchemy.**
6. **Never import private Agnara APIs.**
7. **Every behavior change requires tests.**

## How to add a capability
1. Create a function in `app/capabilities/`.
2. Decorate it with `@app.capability()`.
3. Add any required repository contracts to its signature.
4. If exposing via HTTP directly, mount it in `app/main.py`.
