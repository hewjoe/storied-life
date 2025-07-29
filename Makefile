# Storied Life Project Makefile - Separated Stack Architecture
# ==============================================================
# 
# Available commands:
#   make help          - Show this help message
#   make setup         - Initial project setup
#   
#   # Complete Stack Management
#   make start         - Start both infrastructure and application stacks
#   make stop          - Stop both stacks
#   make restart       - Restart both stacks
#   make logs          - Show logs from all services
#   make status        - Show status of all services
#   make clean         - Clean up all containers, images, and volumes
#   
#   # Development Commands
#   make dev           - Start development environment (both stacks)
#   make dev-stop      - Stop development environment
#   make dev-logs      - Show development logs
#   
#   # Infrastructure Stack Commands
#   make infra-start   - Start infrastructure stack only
#   make infra-stop    - Stop infrastructure stack only
#   make infra-logs    - Show infrastructure logs
#   
#   # Application Stack Commands
#   make app-start     - Start application stack only (requires infrastructure)
#   make app-stop      - Stop application stack only
#   make app-logs      - Show application logs
#   
#   # Development and Testing
#   make build         - Build all Docker images
#   make lint          - Lint all code (backend + frontend)
#   make format        - Format all code (backend + frontend)
#   make security      - Run security scans on all code
#   make test          - Run all tests (backend + frontend)

.PHONY: help build start stop restart logs clean lint format security test dev setup infra-start infra-stop infra-logs app-start app-stop app-logs dev-stop dev-logs status health

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN = \033[36m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
RESET = \033[0m

# Stack management scripts
STACK_SCRIPT = ./scripts/stack.sh
INFRA_SCRIPT = ./scripts/infrastructure.sh
APP_SCRIPT = ./scripts/application.sh

# =================================
# Help
# =================================

help: ## Show this help message
	@echo "$(CYAN)Storied Life Project Commands - Separated Stack Architecture$(RESET)"
	@echo "================================================================"
	@echo ""
	@echo "$(YELLOW)Architecture:$(RESET)"
	@echo "  Infrastructure Stack: Traefik, Authentik, Authentik DB, Authentik Redis"
	@echo "  Application Stack:    Frontend, Backend, App DB, App Redis"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Quick Start:$(RESET)"
	@echo "  1. cp env.example .env && edit .env"
	@echo "  2. make setup"
	@echo "  3. make dev"

# =================================
# Complete Stack Management
# =================================

start: ## Start both infrastructure and application stacks (production)
	@echo "$(CYAN)Starting complete Storied Life stack...$(RESET)"
	$(STACK_SCRIPT) up

stop: ## Stop both stacks
	@echo "$(CYAN)Stopping complete Storied Life stack...$(RESET)"
	$(STACK_SCRIPT) down

restart: ## Restart both stacks
	@echo "$(CYAN)Restarting complete Storied Life stack...$(RESET)"
	$(STACK_SCRIPT) restart

logs: ## Show logs from all services
	@echo "$(CYAN)Showing logs from all services...$(RESET)"
	$(STACK_SCRIPT) logs

status: ## Show status of all services
	@echo "$(CYAN)Showing status of all services...$(RESET)"
	$(STACK_SCRIPT) status

clean: ## Clean up all containers, images, and volumes (WARNING: Data loss!)
	@echo "$(RED)Cleaning up all data...$(RESET)"
	$(STACK_SCRIPT) clean

# =================================
# Development Environment
# =================================

dev: ## Start development environment (both stacks)
	@echo "$(CYAN)Starting development environment...$(RESET)"
	$(STACK_SCRIPT) up --dev

dev-stop: ## Stop development environment
	@echo "$(CYAN)Stopping development environment...$(RESET)"
	$(STACK_SCRIPT) down --dev

dev-logs: ## Show development logs
	@echo "$(CYAN)Showing development logs...$(RESET)"
	$(STACK_SCRIPT) logs --dev

# =================================
# Infrastructure Stack Management
# =================================

infra-start: ## Start infrastructure stack only
	@echo "$(CYAN)Starting infrastructure stack...$(RESET)"
	$(INFRA_SCRIPT) up

infra-stop: ## Stop infrastructure stack only
	@echo "$(CYAN)Stopping infrastructure stack...$(RESET)"
	$(INFRA_SCRIPT) down

infra-logs: ## Show infrastructure logs
	@echo "$(CYAN)Showing infrastructure logs...$(RESET)"
	$(INFRA_SCRIPT) logs

# =================================
# Application Stack Management
# =================================

app-start: ## Start application stack only (requires infrastructure)
	@echo "$(CYAN)Starting application stack...$(RESET)"
	$(APP_SCRIPT) up

app-stop: ## Stop application stack only
	@echo "$(CYAN)Stopping application stack...$(RESET)"
	$(APP_SCRIPT) down

app-logs: ## Show application logs
	@echo "$(CYAN)Showing application logs...$(RESET)"
	$(APP_SCRIPT) logs

# =================================
# Docker Build & Management
# =================================

build: ## Build all Docker images
	@echo "$(CYAN)Building all Docker images...$(RESET)"
	$(STACK_SCRIPT) up --build
	@echo "$(GREEN)Application started successfully!$(RESET)"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost/api"
	@echo "Traefik Dashboard: http://localhost:8080"

start-dev: ## Start development environment
	@echo "$(CYAN)Starting development environment...$(RESET)"
	docker compose -f $(COMPOSE_DEV_FILE) up -d
	@echo "$(GREEN)Development environment started!$(RESET)"

stop: ## Stop the application stack
	@echo "$(CYAN)Stopping application stack...$(RESET)"
	docker compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)Application stopped.$(RESET)"

stop-dev: ## Stop development environment
	@echo "$(CYAN)Stopping development environment...$(RESET)"
	docker compose -f $(COMPOSE_DEV_FILE) down

restart: ## Restart the application stack
	@echo "$(CYAN)Restarting application stack...$(RESET)"
	$(MAKE) stop
	$(MAKE) start

restart-dev: ## Restart development environment
	@echo "$(CYAN)Restarting development environment...$(RESET)"
	$(MAKE) stop-dev
	$(MAKE) start-dev

logs: ## Show logs from all services
	docker compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## Show backend logs only
	docker compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend: ## Show frontend logs only
	docker compose -f $(COMPOSE_FILE) logs -f frontend

# =================================
# Development Commands
# =================================

dev: ## Start development environment with live reload
	@echo "$(CYAN)Starting development environment...$(RESET)"
	$(MAKE) start-dev
	@echo "$(GREEN)Development environment ready!$(RESET)"
	@echo "Frontend (dev): http://localhost:3001"
	@echo "Backend (dev): http://localhost:3002"

nvm-setup: ## Setup nvm environment for frontend development
	@echo "$(CYAN)Setting up nvm environment for frontend...$(RESET)"
	@if [ -d "frontend" ]; then \
		cd frontend && ./scripts/setup-dev.sh; \
	else \
		echo "$(YELLOW)Frontend directory not found$(RESET)"; \
	fi

nvm-install: ## Install the required Node.js version specified in .nvmrc
	@echo "$(CYAN)Installing required Node.js version...$(RESET)"
	@if [ -d "frontend" ]; then \
		if [ -s "$$HOME/.nvm/nvm.sh" ] || [ -s "/usr/local/share/nvm/nvm.sh" ] || [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then \
			cd frontend && \
			export NVM_DIR="$$HOME/.nvm"; \
			[ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh"; \
			[ -s "/usr/local/share/nvm/nvm.sh" ] && . "/usr/local/share/nvm/nvm.sh"; \
			[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"; \
			if [ -f ".nvmrc" ]; then \
				NODE_VERSION=$$(cat .nvmrc); \
				echo "Installing Node.js $$NODE_VERSION..."; \
				nvm install "$$NODE_VERSION" && \
				nvm use "$$NODE_VERSION" && \
				echo "$(GREEN)Node.js $$NODE_VERSION installed and activated$(RESET)"; \
			else \
				echo "$(RED).nvmrc file not found$(RESET)"; \
			fi; \
		else \
			echo "$(RED)nvm is not installed$(RESET)"; \
			echo "Install nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"; \
		fi; \
	else \
		echo "$(YELLOW)Frontend directory not found$(RESET)"; \
	fi

nvm-check: ## Check nvm and Node.js version for frontend
	@echo "$(CYAN)Checking nvm and Node.js versions...$(RESET)"
	@if [ -d "frontend" ]; then \
		cd frontend && \
		if [ -s "$$HOME/.nvm/nvm.sh" ] || [ -s "/usr/local/share/nvm/nvm.sh" ] || [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then \
			echo "$(GREEN)nvm is installed$(RESET)"; \
			export NVM_DIR="$$HOME/.nvm"; \
			[ -s "$$NVM_DIR/nvm.sh" ] && . "$$NVM_DIR/nvm.sh"; \
			[ -s "/usr/local/share/nvm/nvm.sh" ] && . "/usr/local/share/nvm/nvm.sh"; \
			[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"; \
			if [ -f ".nvmrc" ]; then \
				NODE_VERSION=$$(cat .nvmrc); \
				echo "Required Node.js version: $$NODE_VERSION"; \
				if nvm ls 2>/dev/null | grep -q "$$NODE_VERSION"; then \
					echo "$(GREEN)Required Node.js version is installed$(RESET)"; \
					CURRENT_VERSION=$$(nvm current 2>/dev/null || echo "none"); \
					echo "Currently using: $$CURRENT_VERSION"; \
					if [ "$$CURRENT_VERSION" = "v$$NODE_VERSION" ]; then \
						echo "$(GREEN)Correct version is active$(RESET)"; \
					else \
						echo "$(YELLOW)Switch to correct version with 'nvm use' in frontend directory$(RESET)"; \
					fi; \
				else \
					echo "$(YELLOW)Required Node.js version is not installed. Run 'make nvm-setup'$(RESET)"; \
				fi; \
			else \
				echo "$(YELLOW).nvmrc file not found$(RESET)"; \
			fi; \
		else \
			echo "$(RED)nvm is not installed$(RESET)"; \
			echo "Install nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"; \
			echo "Then restart your terminal and try again."; \
		fi; \
	else \
		echo "$(YELLOW)Frontend directory not found$(RESET)"; \
	fi

shell-backend: ## Open shell in backend container
	docker compose -f $(COMPOSE_FILE) run --rm backend bash

shell-frontend: ## Open shell in frontend container
	docker compose -f $(COMPOSE_FILE) run --rm frontend sh

# Convenience commands for running specific tools
backend-shell-interactive: ## Open interactive shell in backend container with dev dependencies
	docker compose -f $(COMPOSE_FILE) build backend
	docker compose -f $(COMPOSE_FILE) run --rm -it backend bash

frontend-shell-interactive: ## Open interactive shell in frontend container with dev dependencies
	docker compose -f $(COMPOSE_FILE) build frontend
	docker compose -f $(COMPOSE_FILE) run --rm -it frontend sh

# Run arbitrary commands in containers
backend-run: ## Run a command in backend container (usage: make backend-run CMD="python --version")
	@if [ -z "$(CMD)" ]; then \
		echo "$(RED)Please specify a command with CMD='your-command'$(RESET)"; \
		echo "Example: make backend-run CMD='python --version'"; \
	else \
		docker compose -f $(COMPOSE_FILE) build backend && \
		docker compose -f $(COMPOSE_FILE) run --rm backend $(CMD); \
	fi

frontend-run: ## Run a command in frontend container (usage: make frontend-run CMD="npm --version")
	@if [ -z "$(CMD)" ]; then \
		echo "$(RED)Please specify a command with CMD='your-command'$(RESET)"; \
		echo "Example: make frontend-run CMD='npm --version'"; \
	else \
		docker compose -f $(COMPOSE_FILE) build frontend && \
		docker compose -f $(COMPOSE_FILE) run --rm frontend $(CMD); \
	fi

# =================================
# Code Quality
# =================================

lint: lint-backend lint-frontend ## Lint all code (backend + frontend)

lint-backend: ## Lint backend code
	@echo "$(CYAN)Linting backend code...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run ruff check app/ tests/ && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run black --check app/ tests/ && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run isort --check-only app/ tests/ && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run mypy app/ || true; \
	else \
		echo "$(YELLOW)Backend directory not found, skipping...$(RESET)"; \
	fi

lint-frontend: ## Lint frontend code
	@echo "$(CYAN)Linting frontend code...$(RESET)"
	@if [ -d "frontend" ]; then \
		if [ -s "$$HOME/.nvm/nvm.sh" ] || [ -s "/usr/local/share/nvm/nvm.sh" ] || [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then \
			if [ -f "frontend/.nvmrc" ]; then \
				echo "$(CYAN)Using nvm for consistent Node.js version...$(RESET)"; \
				cd frontend && ./scripts/nvm-exec.sh npm run lint && ./scripts/nvm-exec.sh npm run type-check; \
			else \
				echo "$(YELLOW)nvm available but .nvmrc not found, using Docker...$(RESET)"; \
				docker compose -f $(COMPOSE_FILE) build frontend && \
				docker compose -f $(COMPOSE_FILE) run --rm frontend npm run lint && \
				docker compose -f $(COMPOSE_FILE) run --rm frontend npm run type-check; \
			fi; \
		else \
			echo "$(YELLOW)nvm not available, using Docker...$(RESET)"; \
			docker compose -f $(COMPOSE_FILE) build frontend && \
			docker compose -f $(COMPOSE_FILE) run --rm frontend npm run lint && \
			docker compose -f $(COMPOSE_FILE) run --rm frontend npm run type-check; \
		fi; \
	else \
		echo "$(YELLOW)Frontend directory not found, skipping...$(RESET)"; \
	fi

format: format-backend format-frontend ## Format all code (backend + frontend)

format-backend: ## Format backend code
	@echo "$(CYAN)Formatting backend code...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run black app/ tests/ && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run isort app/ tests/; \
	else \
		echo "$(YELLOW)Backend directory not found, skipping...$(RESET)"; \
	fi

format-frontend: ## Format frontend code
	@echo "$(CYAN)Formatting frontend code...$(RESET)"
	@if [ -d "frontend" ]; then \
		if [ -s "$$HOME/.nvm/nvm.sh" ] || [ -s "/usr/local/share/nvm/nvm.sh" ] || [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then \
			if [ -f "frontend/.nvmrc" ]; then \
				echo "$(CYAN)Using nvm for consistent Node.js version...$(RESET)"; \
				cd frontend && ./scripts/nvm-exec.sh npm run format; \
			else \
				echo "$(YELLOW)nvm available but .nvmrc not found, using Docker...$(RESET)"; \
				docker compose -f $(COMPOSE_FILE) build frontend && \
				docker compose -f $(COMPOSE_FILE) run --rm frontend npm run format; \
			fi; \
		else \
			echo "$(YELLOW)nvm not available, using Docker...$(RESET)"; \
			docker compose -f $(COMPOSE_FILE) build frontend && \
			docker compose -f $(COMPOSE_FILE) run --rm frontend npm run format; \
		fi; \
	else \
		echo "$(YELLOW)Frontend directory not found, skipping...$(RESET)"; \
	fi

# =================================
# Security Scans
# =================================

security: security-backend security-frontend security-docker ## Run all security scans

security-backend: ## Run security scan on backend code
	@echo "$(CYAN)Running security scan on backend...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run bandit -r app/ -f json -o bandit-report.json || true && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run safety check --json --output safety-report.json || true && \
		echo "$(GREEN)Backend security scan completed. Reports: backend/bandit-report.json, backend/safety-report.json$(RESET)"; \
	else \
		echo "$(YELLOW)Backend directory not found, skipping...$(RESET)"; \
	fi

security-frontend: ## Run security scan on frontend code
	@echo "$(CYAN)Running security scan on frontend...$(RESET)"
	@if [ -d "frontend" ]; then \
		docker compose -f $(COMPOSE_FILE) build frontend && \
		docker compose -f $(COMPOSE_FILE) run --rm frontend npm audit --audit-level moderate || true && \
		docker compose -f $(COMPOSE_FILE) run --rm frontend npx audit-ci --moderate || true; \
	else \
		echo "$(YELLOW)Frontend directory not found, skipping...$(RESET)"; \
	fi

security-docker: ## Run security scan on Docker images
	@echo "$(CYAN)Running Docker security scan...$(RESET)"
	@if command -v trivy >/dev/null 2>&1; then \
		trivy image storied-life-backend:latest || true; \
		trivy image storied-life-frontend:latest || true; \
	else \
		echo "$(YELLOW)Trivy not installed on host. Running in container...$(RESET)"; \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
			aquasec/trivy:latest image storied-life-backend:latest || true; \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
			aquasec/trivy:latest image storied-life-frontend:latest || true; \
	fi

# =================================
# Testing
# =================================

test: test-backend test-frontend ## Run all tests (backend + frontend)

test-backend: ## Run backend tests
	@echo "$(CYAN)Running backend tests...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term && \
		echo "$(GREEN)Backend tests completed. Coverage report: backend/htmlcov/index.html$(RESET)"; \
	else \
		echo "$(YELLOW)Backend directory not found, skipping...$(RESET)"; \
	fi

test-backend-unit: ## Run backend unit tests only
	@echo "$(CYAN)Running backend unit tests...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run pytest tests/ -v -m "unit" --tb=short; \
	else \
		echo "$(YELLOW)Backend directory not found, skipping...$(RESET)"; \
	fi

test-backend-integration: ## Run backend integration tests only
	@echo "$(CYAN)Running backend integration tests...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run pytest tests/ -v -m "integration" --tb=short; \
	else \
		echo "$(YELLOW)Backend directory not found, skipping...$(RESET)"; \
	fi

test-frontend: ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(RESET)"
	@if [ -d "frontend" ]; then \
		if [ -s "$$HOME/.nvm/nvm.sh" ] || [ -s "/usr/local/share/nvm/nvm.sh" ] || [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then \
			if [ -f "frontend/.nvmrc" ]; then \
				echo "$(CYAN)Using nvm for consistent Node.js version...$(RESET)"; \
				cd frontend && ./scripts/nvm-exec.sh npm run test:coverage; \
			else \
				echo "$(YELLOW)nvm available but .nvmrc not found, using Docker...$(RESET)"; \
				docker compose -f $(COMPOSE_FILE) build frontend && \
				docker compose -f $(COMPOSE_FILE) run --rm frontend npm run test:coverage; \
			fi; \
		else \
			echo "$(YELLOW)nvm not available, using Docker...$(RESET)"; \
			docker compose -f $(COMPOSE_FILE) build frontend && \
			docker compose -f $(COMPOSE_FILE) run --rm frontend npm run test:coverage; \
		fi; \
	else \
		echo "$(YELLOW)Frontend directory not found, skipping...$(RESET)"; \
	fi

test-frontend-unit: ## Run frontend unit tests only
	@echo "$(CYAN)Running frontend unit tests...$(RESET)"
	@if [ -d "frontend" ]; then \
		if [ -s "$$HOME/.nvm/nvm.sh" ] || [ -s "/usr/local/share/nvm/nvm.sh" ] || [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then \
			if [ -f "frontend/.nvmrc" ]; then \
				echo "$(CYAN)Using nvm for consistent Node.js version...$(RESET)"; \
				cd frontend && ./scripts/nvm-exec.sh npm run test; \
			else \
				echo "$(YELLOW)nvm available but .nvmrc not found, using Docker...$(RESET)"; \
				docker compose -f $(COMPOSE_FILE) build frontend && \
				docker compose -f $(COMPOSE_FILE) run --rm frontend npm run test; \
			fi; \
		else \
			echo "$(YELLOW)nvm not available, using Docker...$(RESET)"; \
			docker compose -f $(COMPOSE_FILE) build frontend && \
			docker compose -f $(COMPOSE_FILE) run --rm frontend npm run test; \
		fi; \
	else \
		echo "$(YELLOW)Frontend directory not found, skipping...$(RESET)"; \
	fi

test-frontend-e2e: ## Run frontend end-to-end tests
	@echo "$(CYAN)Running frontend E2E tests...$(RESET)"
	@if [ -d "frontend" ]; then \
		docker compose -f $(COMPOSE_FILE) build frontend && \
		docker compose -f $(COMPOSE_FILE) run --rm frontend npm run test:e2e; \
	else \
		echo "$(YELLOW)Frontend directory not found, skipping...$(RESET)"; \
	fi

# =================================
# Setup & Installation
# =================================

setup: ## Initial project setup
	@echo "$(CYAN)Setting up Storied Life project...$(RESET)"
	@if [ ! -f .env ]; then \
		cp env.example .env && \
		echo "$(GREEN)Created .env file from env.example$(RESET)"; \
		echo "$(YELLOW)Please edit .env file with your configuration$(RESET)"; \
	fi
	@echo "$(CYAN)Making scripts executable...$(RESET)"
	@chmod +x scripts/*.sh
	@echo "$(GREEN)Setup completed!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Edit .env file with your configuration"
	@echo "  2. Run 'make dev' to start development environment"
	@echo "  3. See ARCHITECTURE.md for detailed documentation"
	@echo "1. Edit .env file with your configuration"
	@echo "2. Run 'make start' to start the application"

install-backend-deps: ## Install backend dependencies
	@echo "$(CYAN)Building backend image with dependencies...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_FILE) build backend; \
	fi

install-frontend-deps: ## Install frontend dependencies
	@echo "$(CYAN)Building frontend image with dependencies...$(RESET)"
	@if [ -d "frontend" ]; then \
		docker compose -f $(COMPOSE_FILE) build frontend; \
	fi

# =================================
# Database Management
# =================================

db-migrate: ## Run database migrations
	@echo "$(CYAN)Running database migrations...$(RESET)"
	docker compose -f $(COMPOSE_DEV_FILE) build backend
	docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run alembic upgrade head

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "$(RED)WARNING: This will delete all database data!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose -f $(COMPOSE_FILE) down -v
	docker volume rm storied-life_postgres-data storied-life_neo4j-data storied-life_redis-data || true
	$(MAKE) start

# =================================
# Cleanup
# =================================

clean: ## Clean up containers, images, and volumes
	@echo "$(CYAN)Cleaning up Docker resources...$(RESET)"
	docker compose -f $(COMPOSE_FILE) down -v 
	docker compose -f $(COMPOSE_DEV_FILE) down -v || true
	docker system prune -f
	@echo "$(GREEN)Cleanup completed.$(RESET)"

clean-images: ## Remove all project Docker images
	@echo "$(CYAN)Removing project Docker images...$(RESET)"
	docker images | grep storied-life | awk '{print $$3}' | xargs docker rmi -f || true

clean-volumes: ## Remove all project Docker volumes
	@echo "$(CYAN)Removing project Docker volumes...$(RESET)"
	docker volume ls | grep storied-life | awk '{print $$2}' | xargs docker volume rm || true

clean-all: clean clean-images clean-volumes ## Complete cleanup (containers, images, volumes)

# =================================
# Monitoring & Health Checks
# =================================

status: ## Show status of all services
	@echo "$(CYAN)Service Status:$(RESET)"
	docker compose -f $(COMPOSE_FILE) ps

health: ## Run health checks
	@echo "$(CYAN)Running health checks...$(RESET)"
	@curl -f http://localhost:3001/ > /dev/null || echo "$(RED)Frontend health check failed$(RESET)"
	@curl -f http://localhost:8001/health || echo "$(RED)Backend health check failed$(RESET)"

# =================================
# Documentation
# =================================

docs: ## Generate and serve documentation
	@echo "$(CYAN)Serving documentation...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm -p 8000:8000 backend uv run mkdocs serve --dev-addr=0.0.0.0:8000; \
	else \
		echo "$(YELLOW)Backend directory not found$(RESET)"; \
	fi

docs-build: ## Build documentation
	@echo "$(CYAN)Building documentation...$(RESET)"
	@if [ -d "backend" ]; then \
		docker compose -f $(COMPOSE_DEV_FILE) build backend && \
		docker compose -f $(COMPOSE_DEV_FILE) run --rm backend uv run mkdocs build; \
	else \
		echo "$(YELLOW)Backend directory not found$(RESET)"; \
	fi
