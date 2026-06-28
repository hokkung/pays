.PHONY: dev

dev:
	uv sync --extra dev && uv run alembic upgrade head && uv run uvicorn app.main:app --reload