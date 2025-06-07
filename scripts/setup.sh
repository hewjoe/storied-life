#!/bin/bash

# Storied Life - Project Setup Script
# This script sets up the development environment

set -e

echo "🌟 Setting up Storied Life development environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

# # Check Docker Compose
# if ! command -v docker-compose &> /dev/null; then
#     echo "❌ Docker Compose is required but not installed. Please install Docker Compose first."
#     exit 1
# fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Copy environment file
echo "📝 Setting up environment configuration..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env file with your actual configuration values"
else
    echo "ℹ️  .env file already exists, skipping..."
fi

# Setup backend
echo "🐍 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements.dev.txt

cd ..

# Setup frontend
echo "⚛️  Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "ℹ️  node_modules already exists, running npm ci..."
    npm ci
fi

cd ..

# Start development databases
echo "🗄️  Starting development databases..."
docker compose -f docker-compose.dev.yml up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Check database health
echo "🔍 Checking database health..."
docker compose -f docker-compose.dev.yml ps

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Visit http://localhost:5173 to see the application"
echo ""
echo "🔧 Useful commands:"
echo "- Stop databases: docker-compose -f docker-compose.dev.yml down"
echo "- View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "- Reset databases: docker-compose -f docker-compose.dev.yml down -v"
echo ""
echo "📖 For more information, see README.md" 