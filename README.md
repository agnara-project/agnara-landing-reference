# Agnara Landing Reference

A professional, deployable reference implementation of a web application using **Agnara** as its core logic engine.

## What is this?
This project demonstrates how to build a real-world web application where Agnara owns the business logic and capabilities, while standard web technologies (Starlette, Jinja2, HTML/CSS/JS) handle presentation.

It includes:
- A modern SaaS landing page.
- A functional contact form with progressive enhancement (AJAX).
- A protected Admin dashboard with Argon2 authentication.
- SQLite database persistence with SQLAlchemy.

## Architecture
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/AGNARA.md](docs/AGNARA.md) for detailed architectural guidelines.

## Quick Start (Docker)

The easiest way to run the project is using Docker.

1. Clone the repository.
2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
3. Generate an admin password hash and add it to `.env`:
   ```bash
   # If you have uv/python installed locally:
   uv run python scripts/create_admin_hash.py
   # Or run a temporary container to generate it
   ```
4. Start the application:
   ```bash
   docker compose up --build
   ```
5. Open `http://localhost:8000` for the landing page.
6. Open `http://localhost:8000/admin` for the admin panel.

## Development (Local)

1. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
2. Start the dev server:
   ```bash
   make dev
   ```
3. Run tests:
   ```bash
   make test
   ```
4. Run linters:
   ```bash
   make lint
   make format
   ```
