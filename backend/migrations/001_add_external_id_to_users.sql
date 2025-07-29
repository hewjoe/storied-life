-- Migration: Add external_id column to users table for OIDC support
-- Date: 2024
-- Description: Adds external_id field to store OIDC subject claim (sub) for user identification

-- Add external_id column to users table
ALTER TABLE users 
ADD COLUMN external_id VARCHAR(255) NULL;

-- Create index on external_id for performance
CREATE INDEX idx_users_external_id ON users(external_id);

-- Add comment to document the purpose
COMMENT ON COLUMN users.external_id IS 'OIDC subject claim (sub) for external identity provider integration'; 