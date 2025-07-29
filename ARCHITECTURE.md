# Storied Life - Separated Stack Architecture

This document describes the new separated stack architecture for Storied Life, which provides better separation of concerns between infrastructure and application services.

## Architecture Overview

The system is now split into two independent stacks:

### Infrastructure Stack
- **Traefik**: Reverse proxy and SSL termination
- **Authentik**: Authentication service
- **Authentik PostgreSQL**: Database for Authentik
- **Authentik Redis**: Cache for Authentik

### Application Stack
- **Frontend**: React/TypeScript application
- **Backend**: FastAPI Python application
- **Application PostgreSQL**: Database for application data
- **Application Redis**: Cache for application

## Benefits

1. **Separation of Concerns**: Infrastructure services can be managed independently from application services
2. **Independent Scaling**: Each stack can be scaled independently
3. **Data Isolation**: Application and authentication data are completely separate
4. **Easier Maintenance**: Infrastructure updates don't affect application data
5. **Environment Flexibility**: Different configurations for development and production

## Quick Start

### Prerequisites
1. Docker and Docker Compose installed
2. Copy `env.example` to `.env` and configure all variables
3. Ensure proper DNS/hosts entries for domains

### Starting Everything
```bash
# Start both infrastructure and application stacks (production)
./scripts/stack.sh up

# Start both stacks in development mode
./scripts/stack.sh up --dev
```

### Starting Individual Stacks
```bash
# Start only infrastructure
./scripts/infrastructure.sh up

# Start only application (infrastructure must be running first)
./scripts/application.sh up

# Development versions
./scripts/infrastructure.sh up --dev
./scripts/application.sh up --dev
```

## Environment Variables

The new architecture requires additional environment variables in your `.env` file:

### Application Database (Production)
```env
APP_POSTGRES_DB=storied_life_app
APP_POSTGRES_USER=storied_app
APP_POSTGRES_PASSWORD=your-app-postgres-password
```

### Application Database (Development)
```env
APP_POSTGRES_DB_DEV=storied_life_app_dev
APP_POSTGRES_USER_DEV=storied_app_dev
APP_POSTGRES_PASSWORD_DEV=your-app-dev-postgres-password
```

### Authentik Database (Production)
```env
AUTHENTIK_POSTGRES_DB=authentik
AUTHENTIK_POSTGRES_USER=authentik
AUTHENTIK_POSTGRES_PASSWORD=your-authentik-postgres-password
```

### Authentik Database (Development)
```env
AUTHENTIK_POSTGRES_DB_DEV=authentik_dev
AUTHENTIK_POSTGRES_USER_DEV=authentik_dev
AUTHENTIK_POSTGRES_PASSWORD_DEV=your-authentik-dev-postgres-password
```

### Application Redis (Production)
```env
APP_REDIS_PASSWORD=your-app-redis-password
```

### Application Redis (Development)
```env
APP_REDIS_PASSWORD_DEV=your-app-dev-redis-password
```

### Authentik Redis (Production)
```env
AUTHENTIK_REDIS_PASSWORD=your-authentik-redis-password
```

### Authentik Redis (Development)
```env
AUTHENTIK_REDIS_PASSWORD_DEV=your-authentik-dev-redis-password
```

## File Structure

```
storied-life/
├── docker-compose.yml              # Application stack (production)
├── docker-compose.dev.yml          # Application stack (development)
├── infrastructure-compose.yml      # Infrastructure stack (production)
├── infrastructure-compose.dev.yml  # Infrastructure stack (development)
├── database/
│   └── init/
│       └── 01-init.sql             # Application database initialization
├── infrastructure/
│   └── authentik/
│       └── init/
│           ├── 01-init-authentik.sql     # Authentik production DB init
│           └── 01-init-authentik-dev.sql # Authentik development DB init
└── scripts/
    ├── stack.sh                    # Complete stack management
    ├── infrastructure.sh           # Infrastructure stack management
    └── application.sh              # Application stack management
```

## Management Scripts

### Complete Stack Management (`scripts/stack.sh`)
```bash
# Start everything
./scripts/stack.sh up [--dev] [--build]

# Stop everything
./scripts/stack.sh down [--dev]

# Restart everything
./scripts/stack.sh restart [--dev] [--build]

# Show all logs
./scripts/stack.sh logs [--follow]

# Show status of all services
./scripts/stack.sh status

# Clean all data (WARNING: Data loss!)
./scripts/stack.sh clean [--dev]
```

### Infrastructure Stack Management (`scripts/infrastructure.sh`)
```bash
# Start infrastructure
./scripts/infrastructure.sh up [--dev] [--build]

# Stop infrastructure
./scripts/infrastructure.sh down [--dev]

# Show infrastructure logs
./scripts/infrastructure.sh logs [--follow]

# Show infrastructure status
./scripts/infrastructure.sh status
```

### Application Stack Management (`scripts/application.sh`)
```bash
# Start application (infrastructure must be running)
./scripts/application.sh up [--dev] [--build]

# Stop application
./scripts/application.sh down [--dev]

# Show application logs
./scripts/application.sh logs [--follow]

# Show application status
./scripts/application.sh status
```

## Development vs Production

### Development Environment
- Uses separate databases and Redis instances
- Exposes database and Redis ports for direct access
- Uses development-specific container names
- Hot reloading for frontend
- Volume mounts for live code editing

### Production Environment
- Isolated services without exposed ports
- Production-optimized containers
- SSL termination via Traefik
- Separate networks for security

## Port Mappings

### Development Environment
| Service | Host Port | Container Port | Description |
|---------|-----------|----------------|-------------|
| Traefik | 80, 443 | 80, 443 | Reverse proxy |
| Frontend | - | 3001 | React dev server (via Traefik) |
| Backend | - | 8001 | FastAPI server (via Traefik) |
| App PostgreSQL | 5432 | 5432 | Application database |
| App Redis | 6379 | 6379 | Application cache |
| Authentik PostgreSQL | 5434 | 5432 | Authentik database |
| Authentik Redis | 6380 | 6379 | Authentik cache |

### Production Environment
All services are accessed through Traefik reverse proxy. No direct port access except for Traefik (80, 443).

## Database Separation

### Application Database
- **Purpose**: Stores application data (users, legacies, stories, etc.)
- **Schema**: Defined in `database/init/01-init.sql`
- **Access**: Via application backend only

### Authentik Database
- **Purpose**: Stores authentication data (users, sessions, configurations)
- **Schema**: Managed by Authentik automatically
- **Access**: Via Authentik services only

## Networks

### Infrastructure Network
- **Name**: `storied-life-infra` (production) / `storied-life-infra-dev` (development)
- **Services**: Traefik, Authentik, Authentik DB, Authentik Redis

### Application Network
- **Name**: `storied-life` (production) / `storied-life-dev` (development)
- **Services**: Frontend, Backend, Application DB, Application Redis
- **Cross-network**: Traefik participates in both networks to route traffic

## Migration from Old Architecture

If you're migrating from the old single-stack architecture:

1. **Backup your data**:
   ```bash
   docker compose exec postgres pg_dump -U storied storied_life > backup.sql
   ```

2. **Stop old stack**:
   ```bash
   docker compose down
   ```

3. **Update environment variables** in `.env` file with new variables

4. **Start new infrastructure**:
   ```bash
   ./scripts/infrastructure.sh up --dev
   ```

5. **Import data to new application database**:
   ```bash
   # After starting application stack
   docker compose -f docker-compose.dev.yml exec postgres psql -U storied_app_dev -d storied_life_app_dev -f /path/to/backup.sql
   ```

6. **Start application stack**:
   ```bash
   ./scripts/application.sh up --dev
   ```

## Troubleshooting

### Infrastructure not starting
- Check that all required environment variables are set
- Ensure Docker has enough resources
- Check logs: `./scripts/infrastructure.sh logs`

### Application can't connect to infrastructure
- Ensure infrastructure stack is running first
- Check network connectivity between stacks
- Verify Traefik routing configuration

### Database connection issues
- Verify database credentials in `.env`
- Check database initialization logs
- Ensure databases are healthy: `./scripts/stack.sh status`

### SSL/Certificate issues
- Ensure certificates are properly placed in `traefik/certs/`
- Check Traefik configuration in `traefik/config/`
- Verify domain DNS resolution

## Backup and Recovery

### Application Data
```bash
# Backup application database
docker compose -f docker-compose.yml exec postgres pg_dump -U storied_app storied_life_app > app_backup.sql

# Restore application database
docker compose -f docker-compose.yml exec postgres psql -U storied_app -d storied_life_app -f /path/to/app_backup.sql
```

### Authentik Data
```bash
# Backup Authentik database
docker compose -f infrastructure-compose.yml exec authentik-postgres pg_dump -U authentik authentik > authentik_backup.sql

# Restore Authentik database
docker compose -f infrastructure-compose.yml exec authentik-postgres psql -U authentik -d authentik -f /path/to/authentik_backup.sql
```

## Security Considerations

1. **Network Isolation**: Infrastructure and application services are properly isolated
2. **Database Separation**: Authentication and application data are completely separate
3. **Access Control**: Only necessary ports are exposed in development
4. **SSL Termination**: All traffic is encrypted via Traefik
5. **Environment Variables**: Sensitive data is managed via environment variables

## Support

For issues related to the separated stack architecture:
1. Check the troubleshooting section above
2. Review logs from both stacks
3. Ensure all environment variables are properly configured
4. Verify network connectivity between stacks
