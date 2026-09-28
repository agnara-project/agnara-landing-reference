.PHONY: install dev test lint format docker docker-down admin-password

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

docker:
	docker compose up --build

docker-down:
	docker compose down

admin-password:
	uv run python scripts/create_admin_hash.py
