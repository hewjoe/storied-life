#!/bin/bash

# Frontend nvm wrapper script
# This script ensures commands are run with the correct Node.js version

set -e

# Source nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Navigate to frontend directory
cd "$(dirname "$0")/.."

# Use the Node.js version specified in .nvmrc
if [ -f ".nvmrc" ]; then
    nvm use
else
    echo "Warning: .nvmrc file not found, using default Node.js version"
fi

# Execute the passed command
exec "$@"
