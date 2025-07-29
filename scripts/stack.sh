#!/bin/bash

# Storied Life Complete Stack Management
# This script manages both infrastructure and application stacks

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
Storied Life Complete Stack Management

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    up          Start both infrastructure and application stacks
    down        Stop both stacks
    restart     Restart both stacks
    logs        Show logs from all services
    status      Show status of all services
    clean       Remove all volumes (WARNING: Data loss!)
    
    infra-up    Start only infrastructure stack
    infra-down  Stop only infrastructure stack
    app-up      Start only application stack (requires infrastructure)
    app-down    Stop only application stack

Options:
    --dev       Use development configuration
    --build     Force rebuild of images
    --follow    Follow logs (only with logs command)

Examples:
    $0 up                   # Start everything (production)
    $0 up --dev             # Start everything (development)
    $0 infra-up --dev       # Start only infrastructure (dev)
    $0 app-up --dev         # Start only application (dev)
    $0 logs --follow        # Follow all logs
    $0 status               # Show status of all services

Architecture:
    Infrastructure Stack:   Traefik, Authentik, Authentik DB, Authentik Redis
    Application Stack:      Frontend, Backend, App DB, App Redis

EOF
}

# Parse command line arguments
COMMAND=""
DEV_MODE=false
BUILD_FLAG=""
FOLLOW_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        up|down|restart|logs|status|clean|infra-up|infra-down|app-up|app-down)
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
        --follow)
            FOLLOW_FLAG="--follow"
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

# Change to project root
cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f .env ]; then
    log_warning ".env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Helper functions to call individual scripts
call_infrastructure() {
    local cmd="$1"
    local args=""
    [ "$DEV_MODE" = true ] && args="$args --dev"
    [ -n "$BUILD_FLAG" ] && args="$args $BUILD_FLAG"
    [ -n "$FOLLOW_FLAG" ] && args="$args $FOLLOW_FLAG"
    
    "$SCRIPT_DIR/infrastructure.sh" "$cmd" $args
}

call_application() {
    local cmd="$1"
    local args=""
    [ "$DEV_MODE" = true ] && args="$args --dev"
    [ -n "$BUILD_FLAG" ] && args="$args $BUILD_FLAG"
    [ -n "$FOLLOW_FLAG" ] && args="$args $FOLLOW_FLAG"
    
    "$SCRIPT_DIR/application.sh" "$cmd" $args
}

# Execute command
case $COMMAND in
    up)
        log_info "Starting complete Storied Life stack..."
        call_infrastructure "up"
        sleep 5  # Give infrastructure time to start
        call_application "up"
        log_success "Complete Storied Life stack started successfully!"
        ;;
    down)
        log_info "Stopping complete Storied Life stack..."
        call_application "down" || true  # Don't fail if app is already down
        call_infrastructure "down" || true  # Don't fail if infra is already down
        log_success "Complete Storied Life stack stopped successfully!"
        ;;
    restart)
        log_info "Restarting complete Storied Life stack..."
        call_application "down" || true
        call_infrastructure "down" || true
        sleep 2
        call_infrastructure "up"
        sleep 5
        call_application "up"
        log_success "Complete Storied Life stack restarted successfully!"
        ;;
    logs)
        log_info "Showing logs from all services..."
        if [ -n "$FOLLOW_FLAG" ]; then
            # For follow, we need to run both in parallel
            call_infrastructure "logs" &
            INFRA_PID=$!
            call_application "logs" &
            APP_PID=$!
            # Wait for both processes
            wait $INFRA_PID $APP_PID
        else
            call_infrastructure "logs"
            echo "--- Application Stack Logs ---"
            call_application "logs"
        fi
        ;;
    status)
        log_info "Complete Storied Life stack status:"
        echo "=== Infrastructure Stack ==="
        call_infrastructure "status"
        echo ""
        echo "=== Application Stack ==="
        call_application "status"
        ;;
    clean)
        log_warning "This will remove ALL volumes and data from both stacks!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cleaning complete Storied Life stack..."
            call_application "clean" || true
            call_infrastructure "clean" || true
            log_success "Complete Storied Life stack cleaned!"
        else
            log_info "Clean operation cancelled."
        fi
        ;;
    infra-up)
        call_infrastructure "up"
        ;;
    infra-down)
        call_infrastructure "down"
        ;;
    app-up)
        call_application "up"
        ;;
    app-down)
        call_application "down"
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
