#!/bin/bash

# Frontend development setup script with nvm
# This script ensures the correct Node.js version is used for development

set -e

# Colors for output
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

echo -e "${CYAN}Frontend Development Setup${RESET}"
echo "=================================="

# Check if nvm is installed
if ! command -v nvm &> /dev/null; then
    echo -e "${RED}nvm is not installed. Please install nvm first:${RESET}"
    echo "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash"
    echo "Then restart your terminal and run this script again."
    exit 1
fi

# Source nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Navigate to frontend directory
cd "$(dirname "$0")"

# Check if .nvmrc exists
if [ ! -f ".nvmrc" ]; then
    echo -e "${RED}.nvmrc file not found!${RESET}"
    exit 1
fi

NODE_VERSION=$(cat .nvmrc)
echo -e "${CYAN}Using Node.js version: ${NODE_VERSION}${RESET}"

# Install and use the specified Node.js version
echo -e "${CYAN}Installing Node.js ${NODE_VERSION}...${RESET}"
nvm install "$NODE_VERSION"
nvm use "$NODE_VERSION"

# Verify Node.js version
CURRENT_NODE_VERSION=$(node --version)
echo -e "${GREEN}Active Node.js version: ${CURRENT_NODE_VERSION}${RESET}"

# Install dependencies
echo -e "${CYAN}Installing dependencies...${RESET}"
npm install

echo -e "${GREEN}Frontend development environment is ready!${RESET}"
echo ""
echo -e "${YELLOW}Available commands:${RESET}"
echo "  npm run dev        - Start development server"
echo "  npm run build      - Build for production"
echo "  npm run test       - Run tests"
echo "  npm run lint       - Lint code"
echo "  npm run format     - Format code"
echo ""
echo -e "${YELLOW}To start development server:${RESET}"
echo "  npm run dev"
