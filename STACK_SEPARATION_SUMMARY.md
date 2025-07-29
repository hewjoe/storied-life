# Storied Life - Stack Separation Migration Summary

## Overview
The Storied Life project has been successfully refactored to separate infrastructure and application concerns into independent stacks. This provides better separation of concerns, easier maintenance, and more flexible deployment options.

## Files Created

### Infrastructure Stack Configurations
- `infrastructure-compose.yml` - Production infrastructure stack
- `infrastructure-compose.dev.yml` - Development infrastructure stack

### Database Initialization Scripts
- `infrastructure/authentik/init/01-init-authentik.sql` - Authentik production database initialization
- `infrastructure/authentik/init/01-init-authentik-dev.sql` - Authentik development database initialization

### Management Scripts
- `scripts/infrastructure.sh` - Infrastructure stack management
- `scripts/application.sh` - Application stack management  
- `scripts/stack.sh` - Complete stack management (both infrastructure and application)

### Documentation
- `ARCHITECTURE.md` - Comprehensive architecture documentation
- `STACK_SEPARATION_SUMMARY.md` - This summary document

## Files Modified

### Docker Compose Files
- `docker-compose.yml` - Updated to remove infrastructure services, use separate application database
- `docker-compose.dev.yml` - Updated for development environment with separate databases

### Configuration Files
- `env.example` - Added new environment variables for separated databases and Redis instances
- `database/init/01-init.sql` - Updated comments to clarify this is for application database only
- `Makefile` - Updated to use new stack management scripts

## New Environment Variables

### Application Database
```env
# Production
APP_POSTGRES_DB=storied_life_app
APP_POSTGRES_USER=storied_app
APP_POSTGRES_PASSWORD=your-app-postgres-password

# Development
APP_POSTGRES_DB_DEV=storied_life_app_dev
APP_POSTGRES_USER_DEV=storied_app_dev
APP_POSTGRES_PASSWORD_DEV=your-app-dev-postgres-password
```

### Authentik Database
```env
# Production
AUTHENTIK_POSTGRES_DB=authentik
AUTHENTIK_POSTGRES_USER=authentik
AUTHENTIK_POSTGRES_PASSWORD=your-authentik-postgres-password

# Development
AUTHENTIK_POSTGRES_DB_DEV=authentik_dev
AUTHENTIK_POSTGRES_USER_DEV=authentik_dev
AUTHENTIK_POSTGRES_PASSWORD_DEV=your-authentik-dev-postgres-password
```

### Redis Instances
```env
# Application Redis
APP_REDIS_PASSWORD=your-app-redis-password
APP_REDIS_PASSWORD_DEV=your-app-dev-redis-password

# Authentik Redis
AUTHENTIK_REDIS_PASSWORD=your-authentik-redis-password
AUTHENTIK_REDIS_PASSWORD_DEV=your-authentik-dev-redis-password
```

## Architecture Changes

### Before (Single Stack)
```
docker-compose.yml
├── traefik
├── authentik-server
├── authentik-worker
├── frontend
├── backend
├── postgres (shared)
└── redis (shared)
```

### After (Separated Stacks)

#### Infrastructure Stack
```
infrastructure-compose.yml
├── traefik
├── authentik-server
├── authentik-worker
├── authentik-postgres
└── authentik-redis
```

#### Application Stack
```
docker-compose.yml
├── frontend
├── backend
├── postgres (app-specific)
└── redis (app-specific)
```

## Network Configuration

### Infrastructure Network
- **Name**: `storied-life-infra` (prod) / `storied-life-infra-dev` (dev)
- **Services**: Traefik, Authentik components, Authentik database, Authentik Redis

### Application Network
- **Name**: `storied-life` (prod) / `storied-life-dev` (dev)  
- **Services**: Frontend, Backend, Application database, Application Redis

### Cross-Network Communication
- Traefik participates in both networks to route traffic to application services
- Infrastructure services are completely isolated from application services

## Port Mappings (Development)

| Service | Host Port | Container Port | Purpose |
|---------|-----------|----------------|---------|
| Traefik | 80, 443 | 80, 443 | Reverse proxy |
| App PostgreSQL | 5432 | 5432 | Application database |
| App Redis | 6379 | 6379 | Application cache |
| Authentik PostgreSQL | 5434 | 5432 | Authentik database |
| Authentik Redis | 6380 | 6379 | Authentik cache |

## Usage Examples

### Starting Everything
```bash
# Complete stack (production)
make start
# or
./scripts/stack.sh up

# Complete stack (development)
make dev
# or  
./scripts/stack.sh up --dev
```

### Starting Individual Stacks
```bash
# Infrastructure only
make infra-start
# or
./scripts/infrastructure.sh up

# Application only (requires infrastructure)
make app-start
# or
./scripts/application.sh up
```

### Management Commands
```bash
# Show status of all services
make status

# Show logs from all services
make logs

# Stop everything
make stop

# Clean all data (WARNING: Data loss!)
make clean
```

## Migration Steps

For existing deployments, follow these steps:

1. **Backup existing data**:
   ```bash
   docker compose exec postgres pg_dump -U storied storied_life > backup.sql
   ```

2. **Stop current stack**:
   ```bash
   docker compose down
   ```

3. **Update environment file**:
   ```bash
   # Add new environment variables to .env
   cp env.example env.new
   # Merge your existing .env with new variables from env.new
   ```

4. **Start infrastructure stack**:
   ```bash
   ./scripts/infrastructure.sh up --dev
   ```

5. **Start application stack**:
   ```bash
   ./scripts/application.sh up --dev
   ```

6. **Import data** (if needed):
   ```bash
   # Copy backup into container and import
   docker cp backup.sql storied-life-app-postgres-dev:/tmp/
   docker compose -f docker-compose.dev.yml exec postgres psql -U storied_app_dev -d storied_life_app_dev -f /tmp/backup.sql
   ```

## Benefits Achieved

1. **Separation of Concerns**: Infrastructure and application services are completely independent
2. **Data Isolation**: Authentication and application data are stored in separate databases
3. **Independent Scaling**: Each stack can be scaled independently
4. **Easier Maintenance**: Infrastructure updates don't affect application data
5. **Environment Flexibility**: Different configurations for development and production
6. **Better Security**: Reduced attack surface through service isolation
7. **Simplified Debugging**: Issues can be isolated to specific stacks

## Backward Compatibility

- Legacy environment variables are preserved for compatibility
- Existing scripts and workflows continue to work through the updated Makefile
- Database migration path is provided for existing data

## Next Steps

1. Update any CI/CD pipelines to use the new stack management scripts
2. Update deployment documentation to reference the new architecture
3. Consider implementing health checks and monitoring for each stack
4. Plan for production rollout with proper testing of the separated stacks

## Support

For questions or issues with the new architecture:
1. Review the `ARCHITECTURE.md` documentation
2. Check logs from individual stacks using the management scripts
3. Verify all environment variables are properly configured
4. Ensure networks are properly configured between stacks
