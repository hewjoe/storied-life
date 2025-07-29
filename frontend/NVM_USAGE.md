# Frontend Node.js Version Management with nvm

This project uses [nvm (Node Version Manager)](https://github.com/nvm-sh/nvm) to manage Node.js versions for the frontend, similar to how the backend uses `uv` for Python version management.

## Why nvm?

- **Consistent Development Environment**: Ensures all developers use the same Node.js version
- **Easy Version Switching**: Switch between Node.js versions for different projects
- **Version Lock**: The `.nvmrc` file locks the Node.js version for this project
- **CI/CD Consistency**: Same version used in development, Docker, and CI/CD

## Setup

### 1. Install nvm

If you don't have nvm installed:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# Restart your terminal or run:
source ~/.bashrc
```

### 2. Setup Frontend Environment

```bash
# Quick setup (from project root)
make nvm-setup

# Or install just the Node.js version
make nvm-install

# Or manually (from frontend directory)
cd frontend
./scripts/setup-dev.sh
```

### 3. Check nvm Setup

```bash
# From project root
make nvm-check
```

## Usage

### Development Commands

```bash
# Using Makefile (recommended - handles both nvm and Docker fallback)
make lint-frontend      # Lint with nvm or Docker fallback
make format-frontend    # Format with nvm or Docker fallback  
make test-frontend      # Test with nvm or Docker fallback

# Using npm scripts with nvm
cd frontend
npm run dev:nvm         # Start dev server with correct Node.js version
npm run build:nvm       # Build with correct Node.js version
npm run test:nvm        # Test with correct Node.js version
npm run lint:nvm        # Lint with correct Node.js version

# Using nvm directly
cd frontend
nvm use                 # Switch to project Node.js version
npm run dev             # Standard npm commands
```

### Docker Development

The Docker containers also use nvm to ensure consistency:

```bash
# Development container with nvm
make start-dev

# Production build with nvm
make build-frontend
```

## File Structure

```
frontend/
├── .nvmrc                    # Node.js version specification
├── scripts/
│   ├── setup-dev.sh         # Setup development environment
│   └── nvm-exec.sh          # Execute commands with correct Node.js version
├── Dockerfile               # Production build with nvm
├── Dockerfile.dev           # Development container with nvm
└── package.json             # npm scripts with nvm support
```

## Node.js Version

- **Current Version**: `20.11.0` (specified in `.nvmrc`)
- **Minimum Version**: `>=18.0.0` (specified in `package.json`)

## Troubleshooting

### nvm command not found

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

### Wrong Node.js version

```bash
cd frontend
nvm use              # Switch to correct version
nvm install          # Install if not available
```

### Development server not starting

```bash
cd frontend
nvm use              # Ensure correct Node.js version
rm -rf node_modules  # Clean install
npm install
npm run dev
```

## Integration with Backend

Just like the backend uses `uv` for Python environment management:

```bash
# Backend with uv
cd backend
uv run pytest
uv run python main.py

# Frontend with nvm  
cd frontend
nvm use
npm run test
npm run dev
```

Both tools ensure consistent, reproducible development environments across the team.
