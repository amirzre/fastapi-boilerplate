.PHONY: install
install: ## Install dependencies
	poetry install

.PHONY: run
run: start

.PHONY: start
start: ## Starts the server
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	poetry run python3 main.py

.PHONY: migrate
migrate: ## Run the migrations
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	poetry run alembic upgrade head

.PHONY: rollback
rollback: ## Rollback migrations one level
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	poetry run alembic downgrade -1

.PHONY: reset-database
reset-database: ## Rollback all migrations
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	poetry run alembic downgrade base

.PHONY: generate-migration 
generate-migration: ## Generate a new migration
	$(eval include .env) 
	$(eval export $(sh sed 's/=.*//' .env)) 

	@read -p "Enter migration message: " message; \
	poetry run alembic revision --autogenerate -m "$$message"

.PHONY: celery-worker
celery-worker: ## Start celery worker
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	poetry run celery -A worker worker -l info


.PHONY: format
format: ## Run code formatter
	poetry run ruff format

.PHONY: lint
lint: ## Run code linter
	poetry run ruff check --fix

.PHONY: check-lockfile
check-lockfile: ## Compares lock file with pyproject.toml
	poetry lock --check

.PHONY: test
test: ## Run the test suite
	$(eval include .env)
	$(eval export $(sh sed 's/=.*//' .env))

	poetry run pytest -vv -s --cache-clear ./

.PHONY: help
help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@echo "install            	Install dependencies"
	@echo "run                	Start the server"
	@echo "start              	Starts the server"
	@echo "migrate            	Run the migrations"
	@echo "rollback           	Rollback migrations one level"
	@echo "reset-database     	Rollback all migrations"
	@echo "generate-migration 	Generate a new migration"
	@echo "celery-worker      	Start celery worker"
	@echo "format             	Run code formatter"
	@echo "lint               	Run code linter"
	@echo "check-lockfile     	Compares lock file with pyproject.toml"
	@echo "test               	Run the test suite"
	@echo ""
	@echo "For more information, run 'make <command>'"