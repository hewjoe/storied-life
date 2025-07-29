# UV Migration Guide

This document explains the migration from pip/requirements.txt to uv for Python package management in the Storied Life backend.

## What Changed

### Package Management
- **Before**: Used `pip` with `requirements.txt` and `requirements.dev.txt`
- **After**: Uses `uv` with `pyproject.toml` and `uv.lock`

### Benefits of UV
- **Faster**: Up to 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution
- **Modern**: Uses Python packaging standards (PEP 517, PEP 621)
- **Better caching**: Global cache across projects
- **Unified**: Single tool for project management

## Files Added/Modified

### New Files
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Lock file for reproducible builds
- `.uvignore` - Files to ignore during uv operations
- `migrate_to_uv.sh` - Migration helper script

### Modified Files
- `Dockerfile` - Updated to use uv
- `Dockerfile.dev` - Updated to use uv
- `Makefile` - Updated commands to use `uv run`

## Development Workflow

### Installing Dependencies
```bash
# Install all dependencies
uv sync

# Add a new dependency
uv add fastapi

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove package-name
```

### Running Commands
```bash
# Run Python commands
uv run python main.py
uv run pytest
uv run black app/
uv run mypy app/

# Run with environment
uv run --env-file .env python main.py
```

### Docker Development
The Dockerfiles have been updated to use uv:

```bash
# Build backend image
make build-backend

# Run backend tests
make test-backend

# Run backend linting
make lint-backend
```

## Migration Checklist

- [x] Create `pyproject.toml` with all dependencies
- [x] Generate `uv.lock` file
- [x] Update Dockerfiles to use uv
- [x] Update Makefile commands
- [x] Create `.uvignore` file
- [x] Test Docker builds
- [ ] Run full test suite
- [ ] Update CI/CD pipelines (if applicable)
- [ ] Remove old requirements files (after verification)

## Troubleshooting

### Lock File Issues
If you encounter issues with the lock file:
```bash
# Regenerate lock file
uv lock --upgrade

# Force refresh
rm uv.lock && uv lock
```

### Docker Build Issues
If Docker builds fail:
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
make build-backend
```

### Dependency Conflicts
If you have dependency conflicts:
```bash
# Check dependency tree
uv tree

# Update specific package
uv add package-name --upgrade
```

## Rollback Plan

If you need to rollback to the old system:
1. Restore `requirements.txt` and `requirements.dev.txt` from backups
2. Revert Dockerfile changes
3. Revert Makefile changes
4. Remove uv-specific files

The backup files are available as:
- `requirements.txt.backup`
- `requirements.dev.txt.backup`
