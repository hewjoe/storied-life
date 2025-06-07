# Docker Development Guide

This guide explains how to develop Storied Life using a fully containerized environment, keeping your development machine clean of project-specific dependencies.

## 🐳 Quick Start

```bash
# Start the complete development environment
chmod +x scripts/dev-containerized.sh
./scripts/dev-containerized.sh
```

## 🏗️ Architecture

### Development Services

The containerized development environment includes:

- **Frontend** (`storied-life-dev-frontend`): React/Vite app with hot reloading
- **Backend** (`storied-life-dev-backend`): FastAPI with auto-reload
- **PostgreSQL** (`storied-life-dev-postgres`): Primary database
- **Neo4j** (`storied-life-dev-neo4j`): Graph database
- **Redis** (`storied-life-dev-redis`): Cache and sessions
- **LiteLLM** (`storied-life-dev-litellm`): AI proxy service
- **MailHog** (`storied-life-dev-mailhog`): Email testing

### Port Mappings

| Service | Internal Port | External Port | URL |
|---------|---------------|---------------|-----|
| Frontend | 3000 | 3000 | http://localhost:3000 |
| Backend | 8000 | 8001 | http://localhost:8001 |
| PostgreSQL | 5432 | 5433 | localhost:5433 |
| Neo4j | 7474/7687 | 7474/7687 | http://localhost:7474 |
| Redis | 6379 | 6379 | localhost:6379 |
| LiteLLM | 4000 | 4000 | http://localhost:4000 |
| MailHog | 8025 | 8025 | http://localhost:8025 |

## 🔄 Development Workflow

### Hot Reloading

Both frontend and backend support hot reloading:

- **Frontend**: Changes to `src/` files trigger automatic rebuilds
- **Backend**: Changes to `app/` or `main.py` trigger automatic restarts

### Volume Mounts

Source code is mounted as volumes for instant updates:

```yaml
Frontend volumes:
- ./frontend/src:/app/src
- ./frontend/public:/app/public
- Configuration files

Backend volumes:
- ./backend/app:/app/app
- ./backend/main.py:/app/main.py
- ./data/uploads:/app/uploads
```

## 🛠️ Common Tasks

### Viewing Logs

```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Last 100 lines
docker-compose -f docker-compose.dev.yml logs --tail=100 backend
```

### Restarting Services

```bash
# Restart single service
docker-compose -f docker-compose.dev.yml restart backend
docker-compose -f docker-compose.dev.yml restart frontend

# Restart all services
docker-compose -f docker-compose.dev.yml restart
```

### Shell Access

```bash
# Backend shell
docker exec -it storied-life-dev-backend bash

# Frontend shell
docker exec -it storied-life-dev-frontend sh

# Database shell
docker exec -it storied-life-dev-postgres psql -U storied_dev -d storied_life_dev
```

### Installing Dependencies

#### Frontend Dependencies
```bash
# Shell into frontend container
docker exec -it storied-life-dev-frontend sh

# Install new package
npm install <package-name>

# Or update package.json locally and rebuild
docker-compose -f docker-compose.dev.yml build frontend
docker-compose -f docker-compose.dev.yml up -d frontend
```

#### Backend Dependencies
```bash
# Update requirements.txt locally, then rebuild
docker-compose -f docker-compose.dev.yml build backend
docker-compose -f docker-compose.dev.yml up -d backend
```

### Database Operations

#### PostgreSQL
```bash
# Connect to database
docker exec -it storied-life-dev-postgres psql -U storied_dev -d storied_life_dev

# Run SQL file
docker exec -i storied-life-dev-postgres psql -U storied_dev -d storied_life_dev < your-file.sql

# Backup database
docker exec storied-life-dev-postgres pg_dump -U storied_dev storied_life_dev > backup.sql
```

#### Neo4j
```bash
# Access Neo4j browser
open http://localhost:7474

# Credentials: neo4j/dev_password_123
```

## 🐛 Debugging

### Common Issues

#### Port Conflicts
If ports are already in use:
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8001

# Stop conflicting services or change ports in docker-compose.dev.yml
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

#### Container Build Issues
```bash
# Clean rebuild
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
```

### Health Checks

All services include health checks. Check status:
```bash
docker-compose -f docker-compose.dev.yml ps
```

### Performance Optimization

#### macOS/Windows Users
For better file watching performance on macOS/Windows:

1. **Use .dockerignore files** to exclude unnecessary files
2. **Consider using Docker Desktop's** file sharing optimizations
3. **For intensive development**, consider hybrid mode (databases in Docker, apps local)

#### Linux Users
File watching should work optimally out of the box.

## 🔄 Switching Between Modes

### From Local to Containerized
```bash
# Stop local services
# Then start containerized
./scripts/dev-containerized.sh
```

### From Containerized to Local
```bash
# Stop containers
docker-compose -f docker-compose.dev.yml down

# Start only databases
docker-compose -f docker-compose.dev.yml up -d postgres neo4j redis litellm mailhog

# Start apps locally
cd backend && source venv/bin/activate && uvicorn main:app --reload
cd frontend && npm run dev
```

## 🧪 Testing

### Running Tests in Containers
```bash
# Backend tests
docker exec -it storied-life-dev-backend pytest

# Frontend tests
docker exec -it storied-life-dev-frontend npm test
```

## 🚀 Production Deployment

The production configuration uses:
- Multi-stage builds for optimization
- Traefik reverse proxy
- SSL certificates
- Security hardening

```bash
# Deploy to production
docker-compose up -d
```

## 📝 Tips

1. **Use IDE Docker integration** for debugging
2. **Keep source code on host** for better IDE support
3. **Use volume mounts** for instant updates
4. **Monitor resource usage** with `docker stats`
5. **Regular cleanup** with `docker system prune`

## 🆘 Troubleshooting

### Reset Everything
```bash
# Nuclear option - removes all data
docker-compose -f docker-compose.dev.yml down -v
docker system prune -a
./scripts/dev-containerized.sh
```

### Logs Location
- Container logs: `docker-compose -f docker-compose.dev.yml logs`
- Individual service logs: Available through Docker Desktop or CLI

### Getting Help
- Check service health: `docker-compose -f docker-compose.dev.yml ps`
- Inspect containers: `docker inspect <container-name>`
- Check resource usage: `docker stats` 