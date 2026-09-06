.PHONY: venv install install-api install-web dev dev-api dev-web \
        test test-api lint lint-api typecheck typecheck-api \
        migrate seed import-xlsx db-up db-down clean

venv:
	cd api && python -m venv .venv

install: install-api install-web

install-api:
	cd api && python -m venv .venv
	cd api && .venv/Scripts/python -m pip install --upgrade pip setuptools wheel
	cd api && .venv/Scripts/python -m pip install -r requirements.txt -r requirements-dev.txt

install-web:
	cd web && npm ci

db-up:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	cd api && .venv/Scripts/python -m alembic upgrade head

seed:
	cd api && .venv/Scripts/python -m scripts.seed

import-xlsx:
	cd api && .venv/Scripts/python -m scripts.import_xlsx $(XLSX)

dev: dev-api

dev-api:
	cd api && .venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

dev-web:
	cd web && npm run dev

test: test-api

test-api:
	cd api && .venv/Scripts/python -m pytest -q

lint: lint-api

lint-api:
	cd api && .venv/Scripts/python -m ruff check .

typecheck: typecheck-api

typecheck-api:
	cd api && .venv/Scripts/python -m mypy app

clean:
	rm -rf api/.venv web/node_modules web/.next
