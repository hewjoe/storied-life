-- Storied Life Application Database Initialization
-- This script sets up the initial database structure for the application
-- (separate from Authentik which has its own database)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create custom types
CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');
CREATE TYPE legacy_status AS ENUM ('active', 'archived', 'private');
CREATE TYPE story_status AS ENUM ('draft', 'pending', 'approved', 'rejected');
CREATE TYPE visibility_level AS ENUM ('public', 'family', 'private');

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    profile_image_url TEXT,
    bio TEXT,
    external_id VARCHAR(255), -- OIDC subject claim for external identity provider
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create legacies table
CREATE TABLE IF NOT EXISTS legacies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    birth_date DATE,
    death_date DATE,
    profile_image_url TEXT,
    cover_image_url TEXT,
    status legacy_status DEFAULT 'active',
    visibility visibility_level DEFAULT 'public',
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create stories table
CREATE TABLE IF NOT EXISTS stories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    legacy_id UUID NOT NULL REFERENCES legacies(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status story_status DEFAULT 'pending',
    visibility visibility_level DEFAULT 'public',
    story_date DATE,
    tags TEXT[],
    media_urls TEXT[],
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create legacy_members table (for access control)
CREATE TABLE IF NOT EXISTS legacy_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    legacy_id UUID NOT NULL REFERENCES legacies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- admin, moderator, member
    invited_by UUID REFERENCES users(id),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(legacy_id, user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_external_id ON users(external_id);
CREATE INDEX IF NOT EXISTS idx_legacies_created_by ON legacies(created_by);
CREATE INDEX IF NOT EXISTS idx_legacies_status ON legacies(status);
CREATE INDEX IF NOT EXISTS idx_stories_legacy_id ON stories(legacy_id);
CREATE INDEX IF NOT EXISTS idx_stories_author_id ON stories(author_id);
CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status);
CREATE INDEX IF NOT EXISTS idx_stories_tags ON stories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_stories_content_search ON stories USING GIN(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_legacy_members_legacy_id ON legacy_members(legacy_id);
CREATE INDEX IF NOT EXISTS idx_legacy_members_user_id ON legacy_members(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_legacies_updated_at BEFORE UPDATE ON legacies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stories_updated_at BEFORE UPDATE ON stories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (managed via OIDC authentication)
-- Note: This is a placeholder admin user. Real users will be created via OIDC flow.
INSERT INTO users (email, username, full_name, role, email_verified, external_id)
VALUES (
    'admin@storiedlife.local',
    'admin',
    'System Administrator',
    'admin',
    true,
    'system-admin-placeholder' -- Will be replaced when real admin logs in via OIDC
) ON CONFLICT (email) DO NOTHING; 