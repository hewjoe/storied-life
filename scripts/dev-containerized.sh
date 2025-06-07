#!/bin/bash

# Storied Life - Containerized Development Environment
# This script starts the complete development environment in Docker containers

set -e

echo "🚀 Starting Storied Life Development Environment (Containerized)"
echo "================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check for Docker Compose (support both v1 and v2)
DOCKER_COMPOSE=""
if command -v docker-compose > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose and try again."
    exit 1
fi

echo "📦 Using Docker Compose: $DOCKER_COMPOSE"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 No .env file found. Creating from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   You can run: nano .env"
    read -p "Press Enter to continue once you've configured .env..."
fi

# Create data directory for uploads if it doesn't exist
mkdir -p data/uploads

echo "🏗️  Building development containers..."
$DOCKER_COMPOSE -f docker-compose.dev.yml build

echo "🚀 Starting all services..."
$DOCKER_COMPOSE -f docker-compose.dev.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Wait for database to be ready
echo "🗄️  Waiting for PostgreSQL to be ready..."
until docker exec storied-life-dev-postgres pg_isready -U storied_dev -d storied_life_dev > /dev/null 2>&1; do
    sleep 2
done

echo "✅ All services are ready!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend:    http://localhost:3001"
echo "   Backend API: http://localhost:8001"
echo "   API Docs:    http://localhost:8001/docs"
echo "   PostgreSQL:  localhost:5433 (storied_dev/dev_password_123)"
echo "   Neo4j:       http://localhost:7474 (neo4j/dev_password_123)"
echo "   Redis:       localhost:6379"
echo "   LiteLLM:     http://localhost:4001"
echo "   MailHog:     http://localhost:8025"
echo ""
echo "🛠️  Development Features:"
echo "   ✅ Hot reloading enabled for both frontend and backend"
echo "   ✅ Source code mounted as volumes for instant updates"
echo "   ✅ Development dependencies included"
echo "   ✅ Email testing with MailHog"
echo ""
echo "📚 Useful commands:"
echo "   View logs:           $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f"
echo "   Stop services:       $DOCKER_COMPOSE -f docker-compose.dev.yml down"
echo "   Restart a service:   $DOCKER_COMPOSE -f docker-compose.dev.yml restart <service>"
echo "   Shell into backend:  docker exec -it storied-life-dev-backend bash"
echo "   Shell into frontend: docker exec -it storied-life-dev-frontend sh"
echo ""
echo "🎉 Development environment is ready!" 