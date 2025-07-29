-- Authentik Development Database Initialization
-- This script sets up the Authentik development database with required extensions

-- Create extensions required by Authentik
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Set up proper permissions for Authentik user
GRANT ALL PRIVILEGES ON DATABASE authentik_dev TO authentik_dev;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO authentik_dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO authentik_dev;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO authentik_dev;

-- Grant future object privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO authentik_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO authentik_dev;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO authentik_dev;
