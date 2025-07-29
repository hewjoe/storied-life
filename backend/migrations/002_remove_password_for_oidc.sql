-- Migration: Remove password_hash column for OIDC-only authentication
-- Date: 2025-07-29
-- Description: Removes password_hash column as we're moving to full OIDC authentication
--              No password storage needed when using external identity providers

-- Remove password_hash column from users table
ALTER TABLE users 
DROP COLUMN password_hash;

-- Add comment to document the change
COMMENT ON TABLE users IS 'User accounts managed via OIDC authentication - no password storage required';
