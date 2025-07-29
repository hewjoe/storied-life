#!/bin/bash

# Migration script from requirements.txt to uv
# This script helps transition the backend from pip to uv

set -e

echo "🔄 Migrating backend from pip to uv..."

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the backend directory."
    exit 1
fi

# Backup old requirements files
if [ -f "requirements.txt" ]; then
    echo "📦 Backing up requirements.txt to requirements.txt.backup"
    cp requirements.txt requirements.txt.backup
fi

if [ -f "requirements.dev.txt" ]; then
    echo "📦 Backing up requirements.dev.txt to requirements.dev.txt.backup"
    cp requirements.dev.txt requirements.dev.txt.backup
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "📥 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Generate lock file if it doesn't exist
if [ ! -f "uv.lock" ]; then
    echo "🔒 Generating uv.lock file..."
    uv lock
fi

# Create virtual environment and sync dependencies
echo "🏗️  Creating virtual environment and installing dependencies..."
uv sync

echo "✅ Migration complete!"
echo ""
echo "📋 Summary of changes:"
echo "   - Created pyproject.toml with all dependencies"
echo "   - Generated uv.lock file for reproducible builds"
echo "   - Created .uvignore file for uv operations"
echo "   - Updated Dockerfiles to use uv"
echo "   - Updated Makefile commands to use 'uv run'"
echo ""
echo "🚀 Next steps:"
echo "   1. Test the Docker build: make build-backend"
echo "   2. Run tests: make test-backend"
echo "   3. If everything works, you can remove the old requirements files:"
echo "      rm requirements.txt.backup requirements.dev.txt.backup"
echo ""
echo "💡 Development workflow with uv:"
echo "   - Add dependencies: uv add <package>"
echo "   - Add dev dependencies: uv add --dev <package>"
echo "   - Run commands: uv run <command>"
echo "   - Sync dependencies: uv sync"
