.PHONY: install dev

install:
	uv sync

dev:
	PYTHONPATH=src uv run fastapi dev
