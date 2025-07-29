#!/bin/bash

# Storied Life Infrastructure Stack Management
# This script manages the shared infrastructure services (Traefik, Authentik, etc.)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
Storied Life Infrastructure Stack Management

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    up          Start the infrastructure stack
    down        Stop the infrastructure stack
    restart     Restart the infrastructure stack
    logs        Show logs from infrastructure services
    status      Show status of infrastructure services
    clean       Remove infrastructure volumes (WARNING: Data loss!)

Options:
    --dev       Use development configuration
    --build     Force rebuild of images
    --detach    Run in detached mode (default)
    --follow    Follow logs (only with logs command)

Examples:
    $0 up                   # Start production infrastructure
    $0 up --dev             # Start development infrastructure
    $0 down --dev           # Stop development infrastructure
    $0 logs --follow        # Follow infrastructure logs
    $0 restart --dev        # Restart development infrastructure

EOF
}

# Parse command line arguments
COMMAND=""
DEV_MODE=false
BUILD_FLAG=""
DETACH_FLAG="-d"
FOLLOW_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        up|down|restart|logs|status|clean)
            COMMAND="$1"
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --detach)
            DETACH_FLAG="-d"
            shift
            ;;
        --follow)
            FOLLOW_FLAG="-f"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set compose file based on environment
if [ "$DEV_MODE" = true ]; then
    COMPOSE_FILE="infrastructure-compose.dev.yml"
    ENV_SUFFIX="Development"
    PROJECT_NAME="storied-life-infra-dev"
else
    COMPOSE_FILE="infrastructure-compose.yml"
    ENV_SUFFIX="Production"
    PROJECT_NAME="storied-life-infra"
fi

# Change to project root
cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f .env ]; then
    log_warning ".env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Execute command
case $COMMAND in
    up)
        log_info "Starting $ENV_SUFFIX infrastructure stack..."
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up $DETACH_FLAG $BUILD_FLAG
        if [ "$?" -eq 0 ]; then
            log_success "$ENV_SUFFIX infrastructure stack started successfully!"
            log_info "Services available:"
            if [ "$DEV_MODE" = true ]; then
                log_info "  - Traefik Dashboard: https://traefik.storied-life.me"
                log_info "  - Authentik: https://auth.storied-life.me"
                log_info "  - Authentik PostgreSQL: localhost:5434"
                log_info "  - Authentik Redis: localhost:6380"
            else
                log_info "  - Traefik Dashboard: https://traefik.storied-life.me"
                log_info "  - Authentik: https://auth.storied-life.me"
            fi
        else
            log_error "Failed to start $ENV_SUFFIX infrastructure stack"
            exit 1
        fi
        ;;
    down)
        log_info "Stopping $ENV_SUFFIX infrastructure stack..."
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
        if [ "$?" -eq 0 ]; then
            log_success "$ENV_SUFFIX infrastructure stack stopped successfully!"
        else
            log_error "Failed to stop $ENV_SUFFIX infrastructure stack"
            exit 1
        fi
        ;;
    restart)
        log_info "Restarting $ENV_SUFFIX infrastructure stack..."
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up $DETACH_FLAG $BUILD_FLAG
        if [ "$?" -eq 0 ]; then
            log_success "$ENV_SUFFIX infrastructure stack restarted successfully!"
        else
            log_error "Failed to restart $ENV_SUFFIX infrastructure stack"
            exit 1
        fi
        ;;
    logs)
        log_info "Showing $ENV_SUFFIX infrastructure stack logs..."
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs $FOLLOW_FLAG
        ;;
    status)
        log_info "$ENV_SUFFIX infrastructure stack status:"
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
        ;;
    clean)
        log_warning "This will remove all infrastructure volumes and data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Stopping and removing $ENV_SUFFIX infrastructure stack..."
            docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v --remove-orphans
            log_success "$ENV_SUFFIX infrastructure stack cleaned!"
        else
            log_info "Clean operation cancelled."
        fi
        ;;
    "")
        log_error "No command specified"
        show_help
        exit 1
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
