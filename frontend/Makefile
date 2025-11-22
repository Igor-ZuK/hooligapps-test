.PHONY: install test test-watch test-coverage generate-types build dev

# Load .env.local if exists (for local development settings)
# This file is gitignored and should contain: NPM_PATH="/path/to/npm"
ifneq ($(wildcard .env.local),)
    include .env.local
    export NPM_PATH
endif

# NPM path detection:
# 1. Use NPM_PATH environment variable if set (for local development, e.g., PyCharm's npm)
# 2. Try system npm
# 3. Fallback to Docker (only if frontend container is running)
# For local development with PyCharm, create frontend/.env.local (gitignored) with:
#   NPM_PATH="/Users/job/Library/Application Support/JetBrains/PyCharm2025.2/node/versions/20.19.5/bin/npm"
NPM := $(shell \
	if [ -n "$(NPM_PATH)" ] && [ -f "$(NPM_PATH)" ]; then \
		echo "$(NPM_PATH)"; \
	elif command -v npm >/dev/null 2>&1; then \
		echo "npm"; \
	elif docker-compose ps frontend 2>/dev/null | grep -q "Up"; then \
		echo "docker-compose exec frontend npm"; \
	else \
		echo "npm"; \
	fi \
)

# Install dependencies
install:
	$(NPM) install

# Run tests
test:
	$(NPM) run test

# Run tests in watch mode
test-watch:
	$(NPM) run test -- --watch

# Run tests with coverage
test-coverage:
	$(NPM) run test:coverage

# Generate TypeScript types from Swagger
generate-types:
	@echo "Generating types from Swagger..."
	@if docker-compose ps backend | grep -q "Up"; then \
		$(NPM) run generate-types; \
	else \
		echo "Backend is not running. Please start it first: docker-compose up backend"; \
		exit 1; \
	fi

# Build for production
build:
	$(NPM) run build

# Run development server
dev:
	$(NPM) run dev

