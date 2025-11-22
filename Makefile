.PHONY: help up down build restart logs migrate test test-backend test-frontend clean

.DEFAULT_GOAL := help

# Colors for output
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help: ## Show this help message
	@echo '${YELLOW}Usage:${RESET}'
	@echo '  make [target]'
	@echo ''
	@echo '${YELLOW}Available targets:${RESET}'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${GREEN}%-20s${RESET} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services (db, backend, frontend) with migrations
	@echo "${GREEN}Starting all services...${RESET}"
	docker-compose up -d db
	@echo "${YELLOW}Waiting for database to be ready...${RESET}"
	@sleep 5
	docker-compose up -d backend
	@echo "${YELLOW}Waiting for backend to be ready...${RESET}"
	@sleep 3
	@echo "${GREEN}Running migrations...${RESET}"
	docker-compose exec backend poetry run alembic upgrade head
	docker-compose up -d frontend
	@echo "${GREEN}All services are up!${RESET}"
	@echo "${YELLOW}Backend: http://localhost:8000${RESET}"
	@echo "${YELLOW}Frontend: http://localhost:3000${RESET}"

down: ## Stop all services
	@echo "${GREEN}Stopping all services...${RESET}"
	docker-compose down

build: ## Build all Docker images
	@echo "${GREEN}Building Docker images...${RESET}"
	docker-compose build

restart: ## Restart all services
	@echo "${GREEN}Restarting all services...${RESET}"
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

migrate: ## Run database migrations
	@echo "${GREEN}Running migrations...${RESET}"
	docker-compose exec backend poetry run alembic upgrade head

migrate-down: ## Rollback last migration (usage: make migrate-down num=1)
	@if [ -z "$(num)" ]; then \
		echo "${YELLOW}Usage: make migrate-down num=1${RESET}"; \
		exit 1; \
	fi
	@echo "${GREEN}Rolling back migration...${RESET}"
	docker-compose exec backend poetry run alembic downgrade head-$(num)

makemigrations: ## Create new migration (usage: make makemigrations name=migration_name)
	@if [ -z "$(name)" ]; then \
		echo "${YELLOW}Usage: make makemigrations name=migration_name${RESET}"; \
		exit 1; \
	fi
	@echo "${GREEN}Creating migration: $(name)...${RESET}"
	docker-compose exec backend poetry run alembic revision -m $(name) --autogenerate

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "${GREEN}Running backend tests...${RESET}"
	cd backend && make test

test-frontend: ## Run frontend tests
	@echo "${GREEN}Running frontend tests...${RESET}"
	cd frontend && make test

test-backend-watch: ## Run backend tests in watch mode
	cd backend && make test-watch

test-frontend-watch: ## Run frontend tests in watch mode
	cd frontend && make test-watch

generate-types: ## Generate TypeScript types from Swagger
	@echo "${GREEN}Generating TypeScript types from Swagger...${RESET}"
	cd frontend && make generate-types

clean: ## Remove all containers, volumes, and images
	@echo "${YELLOW}This will remove all containers, volumes, and images. Are you sure? [y/N]${RESET}"
	@read -r REPLY; \
	if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		docker-compose down -v --rmi all; \
		echo "${GREEN}Cleanup complete!${RESET}"; \
	else \
		echo "${YELLOW}Cancelled.${RESET}"; \
	fi

