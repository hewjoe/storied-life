#!/bin/bash

# Storied Life Application Stack Management
# This script manages the application services (Frontend, Backend, App Database, etc.)

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
Storied Life Application Stack Management

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    up          Start the application stack
    down        Stop the application stack
    restart     Restart the application stack
    logs        Show logs from application services
    status      Show status of application services
    clean       Remove application volumes (WARNING: Data loss!)

Options:
    --dev       Use development configuration
    --build     Force rebuild of images
    --detach    Run in detached mode (default)
    --follow    Follow logs (only with logs command)

Examples:
    $0 up                   # Start production application
    $0 up --dev             # Start development application
    $0 down --dev           # Stop development application
    $0 logs --follow        # Follow application logs
    $0 restart --dev        # Restart development application

Notes:
    - Make sure infrastructure stack is running first!
    - Use scripts/infrastructure.sh to manage shared services

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
    COMPOSE_FILE="docker-compose.dev.yml"
    ENV_SUFFIX="Development"
    PROJECT_NAME="storied-life-app-dev"
else
    COMPOSE_FILE="docker-compose.yml"
    ENV_SUFFIX="Production"
    PROJECT_NAME="storied-life-app"
fi

# Change to project root
cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f .env ]; then
    log_warning ".env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Check if infrastructure networks exist
check_networks() {
    if [ "$DEV_MODE" = true ]; then
        INFRA_NETWORK="storied-life-infra-dev"
        APP_NETWORK="storied-life-dev"
    else
        INFRA_NETWORK="storied-life-infra"
        APP_NETWORK="storied-life"
    fi
    
    if ! docker network ls | grep -q "$INFRA_NETWORK"; then
        log_warning "Infrastructure network '$INFRA_NETWORK' not found."
        log_warning "Please start the infrastructure stack first using:"
        if [ "$DEV_MODE" = true ]; then
            log_warning "  scripts/infrastructure.sh up --dev"
        else
            log_warning "  scripts/infrastructure.sh up"
        fi
        return 1
    fi
    return 0
}

# Execute command
case $COMMAND in
    up)
        log_info "Starting $ENV_SUFFIX application stack..."
        if ! check_networks; then
            exit 1
        fi
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up $DETACH_FLAG $BUILD_FLAG
        if [ "$?" -eq 0 ]; then
            log_success "$ENV_SUFFIX application stack started successfully!"
            log_info "Services available:"
            if [ "$DEV_MODE" = true ]; then
                log_info "  - Frontend: https://remember.storied-life.me"
                log_info "  - Backend API: https://api.storied-life.me"
                log_info "  - Application PostgreSQL: localhost:5432"
                log_info "  - Application Redis: localhost:6379"
            else
                log_info "  - Frontend: https://remember.storied-life.me"
                log_info "  - Backend API: https://api.storied-life.me"
            fi
        else
            log_error "Failed to start $ENV_SUFFIX application stack"
            exit 1
        fi
        ;;
    down)
        log_info "Stopping $ENV_SUFFIX application stack..."
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
        if [ "$?" -eq 0 ]; then
            log_success "$ENV_SUFFIX application stack stopped successfully!"
        else
            log_error "Failed to stop $ENV_SUFFIX application stack"
            exit 1
        fi
        ;;
    restart)
        log_info "Restarting $ENV_SUFFIX application stack..."
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up $DETACH_FLAG $BUILD_FLAG
        if [ "$?" -eq 0 ]; then
            log_success "$ENV_SUFFIX application stack restarted successfully!"
        else
            log_error "Failed to restart $ENV_SUFFIX application stack"
            exit 1
        fi
        ;;
    logs)
        log_info "Showing $ENV_SUFFIX application stack logs..."
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs $FOLLOW_FLAG
        ;;
    status)
        log_info "$ENV_SUFFIX application stack status:"
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
        ;;
    clean)
        log_warning "This will remove all application volumes and data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Stopping and removing $ENV_SUFFIX application stack..."
            docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v --remove-orphans
            log_success "$ENV_SUFFIX application stack cleaned!"
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
