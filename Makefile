.PHONY: install dev

install:
	uv sync

dev:
	uv run fastapi dev
