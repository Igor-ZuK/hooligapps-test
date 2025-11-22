.PHONY: install install-dev test linter migrate migrate-down makemigrations

# Install dependencies
install:
	python -m ensurepip --upgrade; \
	pip install --upgrade setuptools --no-cache; \
	pip install "poetry==2.2.1" --no-cache; \
	poetry config virtualenvs.create false; \
	if [ "$(mode)" = "stand" ]; then \
		poetry install --only main; \
	else \
		poetry install; \
	fi

# Install dependencies with dev tools
install-dev:
	make install
	@if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then \
		pre-commit install; \
	else \
		echo "Skipping pre-commit install (git not available or not in a git repository)"; \
	fi

# Run tests
test:
	docker-compose stop db
	docker-compose --file tests/infra/docker-compose.yml stop db_test
	docker-compose --file tests/infra/docker-compose.yml up -d db_test
	DEBUG=True poetry run pytest -vv --cov=project/ --cov-report xml $(path)
	docker-compose --file tests/infra/docker-compose.yml stop db_test

# Run linter
linter:
	poetry run ruff format .
	poetry run ruff check . --fix
	poetry run mypy . --config-file pyproject.toml

# Run migrations
migrate:
	poetry run alembic upgrade head

# Rollback migrations
migrate-down:
	poetry run alembic downgrade head-$(num)

# Create new migration
makemigrations:
	poetry run alembic revision -m $(name) --autogenerate
