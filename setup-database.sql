-- HomeChefs AI PostgreSQL Database Setup
-- Run this script to set up the production database

-- Create database (run as postgres user)
CREATE DATABASE homechefs_db;

-- Create application user
CREATE USER homechefs_user WITH PASSWORD 'secure_password_change_this';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE homechefs_db TO homechefs_user;

-- Grant connection privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO homechefs_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO homechefs_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO homechefs_user;

-- Connect to the database and enable extensions
\c homechefs_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set ownership
REASSIGN OWNED BY homechefs_user TO homechefs_user;

-- Show setup completion
SELECT 'HomeChefs AI database setup completed!' as status;

-- Test connection
\dt homechefs_user.*;
