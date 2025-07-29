# Authentik Configuration for Storied Life

This directory contains configuration files and data for Authentik, the identity provider used by Storied Life.

## Directory Structure

```
authentik/
├── README.md                      # This file
├── media/                         # Authentik media files (logos, etc.)
├── custom-templates/              # Custom Authentik templates
└── docker-compose.override.yml    # Example Traefik integration
```

## Setup Instructions

### 1. Initial Authentik Setup

1. Start the services:
   ```bash
   docker-compose up -d authentik-server authentik-worker
   ```

2. Access Authentik admin interface:
   - URL: `https://auth.projecthewitt.info/if/admin/`
   - Default credentials: `akadmin` / `password` (change immediately)

### 2. Configure Social Providers

In the Authentik admin interface:

1. **Google OAuth2**:
   - Navigate to Directory → Providers → Create
   - Select "OAuth2/OpenID Provider"
   - Configure Google OAuth2 settings

2. **Microsoft OAuth2**:
   - Similar process for Microsoft Azure AD

3. **Facebook OAuth2**:
   - Configure Facebook app credentials

### 3. Create Application

1. Navigate to Applications → Create
2. Name: "Storied Life"
3. Slug: "storied-life"
4. Provider: Select your configured provider
5. Launch URL: `https://your-domain.com`

### 4. Configure Outpost

1. Navigate to Outposts → Create
2. Name: "Traefik Forward Auth"
3. Type: "Proxy"
4. Service Connection: Docker
5. Configuration:
   ```yaml
   authentik_host: https://auth.projecthewitt.info
   external_host: https://your-domain.com
   ```

### 5. Group Configuration

Create groups for permission management:

1. **storied-life-users**: Standard users
2. **storied-life-admins**: System administrators
3. **storied-life-family-admins**: Family group administrators

## Environment Variables

Required environment variables (add to `.env`):

```bash
# Authentik Configuration
AUTHENTIK_HOST=auth.projecthewitt.info
AUTHENTIK_SECRET_KEY=your-authentik-secret-key-change-this

# Database (shared with main app)
POSTGRES_USER=storied
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=storied_life
```

## Traefik Integration

The application uses Traefik forward auth to integrate with Authentik. When configured properly:

1. Unauthenticated users are redirected to Authentik
2. After authentication, Authentik passes user info via headers:
   - `X-authentik-email`
   - `X-authentik-name`
   - `X-authentik-groups`
   - `X-authentik-username`

## Customization

### Custom Templates

Place custom templates in `custom-templates/`:
- Login pages
- Email templates
- Password reset forms

### Media Files

Place custom logos and images in `media/`:
- Application logos
- Background images
- Custom styling assets

## Backup and Recovery

### Database Backup
```bash
# Backup Authentik data (included in main PostgreSQL backup)
docker exec storied-life-postgres pg_dump -U storied storied_life > authentik_backup.sql
```

### Media Backup
```bash
# Backup media files
tar -czf authentik_media_backup.tar.gz authentik/media/
```

## Troubleshooting

### Common Issues

1. **Authentication loop**:
   - Check Traefik forward auth configuration
   - Verify Authentik outpost is running
   - Confirm DNS resolution

2. **Headers not received**:
   - Check Traefik middleware configuration
   - Verify outpost configuration in Authentik
   - Test with curl and manual headers

3. **User not created**:
   - Check backend logs for errors
   - Verify email format in headers
   - Confirm database connectivity

### Debug Commands

```bash
# Check Authentik logs
docker logs storied-life-authentik-server

# Check worker logs
docker logs storied-life-authentik-worker

# Test authentication headers
curl -H "X-authentik-email: test@example.com" \
     -H "X-authentik-name: Test User" \
     http://localhost:8001/api/v1/auth/status
```

## Security Notes

- Always use HTTPS in production
- Regularly update Authentik to latest version
- Monitor authentication logs for suspicious activity
- Use strong secrets for all configuration
- Backup configuration and secrets securely

## Migration from Authelia

If migrating from the previous Authelia setup:

1. Export user data from Authelia
2. Configure Authentik with same users/groups
3. Update Traefik configuration
4. Test authentication flows
5. Decommission Authelia services

For more information, see the main [AUTH.md](../AUTH.md) documentation. 