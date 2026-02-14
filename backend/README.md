# MEXA Backend

Backend service for MEXA Core with structured logging and audit trail support.

## Features

- Flask-based REST API
- PostgreSQL database with Alembic migrations
- Structured logging with audit trail
- UUID-based request tracking
- Docker support

## Database Migrations

The backend uses Alembic for database migrations:

1. **v001_initial_schema.py**: Creates initial usuarios and vales tables
2. **v002_add_request_id_to_vales.py**: Adds request_id with UNIQUE constraint to vales table
3. **v003_add_usuarios_indexes.py**: Adds additional indexes for performance
4. **v004_create_audit_logs_table.py**: Creates audit_logs table with proper indexing

## Setup

### Using Docker Compose (Recommended)

```bash
# Clean start
docker-compose down -v

# Build and start
docker-compose up --build

# View logs
docker-compose logs -f backend
```

### Manual Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_NAME=mexa_db
export DATABASE_USER=mexa_user
export DATABASE_PASSWORD=mexa_pass

# Run migrations
alembic upgrade head

# Start application
python app.py
```

## Environment Variables

- `DATABASE_HOST`: PostgreSQL host (default: db)
- `DATABASE_PORT`: PostgreSQL port (default: 5432)
- `DATABASE_NAME`: Database name (default: mexa_db)
- `DATABASE_USER`: Database user (default: mexa_user)
- `DATABASE_PASSWORD`: Database password (default: mexa_pass)
- `LOG_LEVEL`: Logging level (default: INFO)
- `FLASK_APP`: Flask application entry point (default: app.py)

## API Endpoints

- `GET /`: Health check
- `GET /health`: Detailed health status

## Database Schema

### usuarios
- id (PK)
- username (unique)
- email (unique)
- password_hash
- created_at
- updated_at

### vales
- id (PK)
- user_id (FK -> usuarios)
- request_id (UUID, unique)
- amount
- description
- created_at

### audit_logs
- id (PK)
- request_id (UUID, indexed)
- user_id (FK -> usuarios, nullable)
- action
- resource_type
- resource_id
- old_values (JSON)
- new_values (JSON)
- endpoint
- method
- ip_address
- created_at (server default: now())

## Testing Migrations

```bash
# Check current version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Test database
docker-compose exec db psql -U mexa_user -d mexa_db

# In psql:
\dt                    -- List tables
\d vales              -- Describe vales table
\d audit_logs         -- Describe audit_logs table
SELECT * FROM alembic_version;  -- Check migration version
```

## pgcrypto Extension

The migrations automatically enable the PostgreSQL `pgcrypto` extension, which provides:
- `gen_random_uuid()` function for UUID generation
- Cryptographic functions for security features

This ensures migrations work on clean PostgreSQL instances without seed data.
