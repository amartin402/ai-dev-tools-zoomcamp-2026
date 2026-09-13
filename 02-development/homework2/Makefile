.PHONY: backend-install backend-run backend-test install run test

backend-install:
	uv sync --directory backend

backend-run:
	uv run --directory backend uvicorn app.main:app --reload

backend-test:
	uv run --directory backend pytest

install: backend-install

run: backend-run

test: backend-test
