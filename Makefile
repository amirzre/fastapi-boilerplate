.PHONY: install
install: ## Install dependencies
	uv sync


.PHONY: run
run: start

.PHONY: start
start: ## Starts the server
	uv run python3 main.py


.PHONY: migrate
migrate: ## Run the migrations
	uv run alembic upgrade head


.PHONY: rollback
rollback: ## Rollback migrations one level
	uv run alembic downgrade -1


.PHONY: reset-database
reset-database: ## Rollback all migrations
	uv run alembic downgrade base


.PHONY: generate-migration
generate-migration: ## Generate a new migration
	read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"


.PHONY: celery-worker
celery-worker: ## Start celery worker
	uv run celery -A worker worker -l info


.PHONY: format
format: ## Run code formatter
	uv run ruff format


.PHONY: lint
lint: ## Run code linter
	uv run ruff check --fix


.PHONY: check-lockfile
check-lockfile: ## Compares lock file with pyproject.toml
	uv lock --check


.PHONY: test
test: ## Run the test suite
	uv run pytest -vv -s --cache-clear ./


.PHONY: help
help: ## Show each command usage
	@echo "Usage:"
	@grep -E '^[[:alnum:]_-]+:.*##' $(MAKEFILE_LIST) | \
		sed -E 's/^([[:alnum:]_-]+):.*##[[:space:]]*(.*)$$/\1|\2/' | \
		awk -F"|" '{ printf "  %-20s %s\n", $$1, $$2 }'
