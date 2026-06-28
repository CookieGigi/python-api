.PHONY: install dev dev-with-logs tests watch-logs traefik

install:
	uv sync

dev:
	PYTHONPATH=src uv run fastapi dev --reload-dir src/ --host 127.0.0.1 --port 8000

dev-with-logs:
	@mkdir -p logs
	PYTHONPATH=src uv run fastapi dev --reload-dir src/ 2>&1 | tee logs/app.log

tests:
	uv run --no-env-file pytest

watch-logs:
	@mkdir -p logs
	lnav logs/app.log

traefik:
	traefik --configFile=./traefik/traefik.yml
