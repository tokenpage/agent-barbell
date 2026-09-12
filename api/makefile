install:
	@ pip install uv
	@ uv sync --active --all-extras

install-updates:
	@ pip install uv
	@ uv sync --active --upgrade --refresh --all-extras

list-outdated: install
	@ uv pip list -o

lint-check:
	@ uv run --active lint-check ./*.py ./agent_barbell ./scripts

lint-check-ci:
	@ uv run --active lint-check ./*.py ./agent_barbell ./scripts --output-file lint-check-results.json --output-format annotations

lint-fix:
	@ uv run --active lint-check --fix ./*.py ./agent_barbell ./scripts

type-check:
	@ uv run --active type-check --mypy ./*.py ./agent_barbell ./scripts

type-check-ci:
	@ uv run --active type-check --mypy ./*.py ./agent_barbell ./scripts --output-file type-check-results.json --output-format annotations

security-check:
	@ uv run --active security-check ./*.py ./agent_barbell ./scripts

security-check-ci:
	@ uv run --active security-check ./*.py ./agent_barbell ./scripts --output-file security-check-results.json --output-format annotations

build:
	@ echo "Not Supported"

start:
	@ uv run --active uvicorn application:app --host 0.0.0.0 --port 5100 --no-access-log --reload

start-prod:
	@ uv run --active uvicorn application:app --host 0.0.0.0 --port 5100 --no-access-log

test:
	@ uv run --active pytest tests/ -v

clean:
	@ rm -rf ./.mypy_cache ./__pycache__ ./build ./dist

.PHONY: *
