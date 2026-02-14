# Development Guide

This guide covers local development setup, workflows, and best practices for the mexa-core project.

## Table of Contents

1. [Setup](#setup)
2. [Database Migrations](#database-migrations)
3. [Running the Application](#running-the-application)
4. [Testing](#testing)
5. [Code Quality](#code-quality)

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Git

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mexadigital/mexa-core.git
   cd mexa-core
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

   Example `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/mexa_db
   ```

5. **Create database:**
   ```bash
   createdb mexa_db
   ```

6. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

## Database Migrations

### Overview

We use Alembic for database schema management. All migrations are stored in `migrations/versions/`.

### Common Migration Commands

#### Check Migration Status

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show detailed history
alembic history --verbose
```

#### Creating Migrations

**Manual Migration:**
```bash
alembic revision -m "description of change"
```

This creates a new migration file in `migrations/versions/`. Edit the file to add your schema changes.

**Autogenerate Migration:**
```bash
alembic revision --autogenerate -m "description of change"
```

This automatically detects changes in your SQLAlchemy models and generates migration code. **Always review the generated code** before committing.

#### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply next migration only
alembic upgrade +1

# Apply to specific version
alembic upgrade abc123
```

#### Rolling Back Migrations

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

### Migration Workflow

#### 1. Make Model Changes

Edit your SQLAlchemy models in `app/models.py`:

```python
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    # Add new column
    email = Column(String(255), nullable=False)
```

#### 2. Generate Migration

```bash
# Autogenerate from model changes
alembic revision --autogenerate -m "add email to users"
```

#### 3. Review Migration

Open the generated file in `migrations/versions/` and review:

```python
def upgrade() -> None:
    """Add email column to users table."""
    op.add_column('users',
        sa.Column('email', sa.String(length=255), nullable=False)
    )

def downgrade() -> None:
    """Remove email column from users table."""
    op.drop_column('users', 'email')
```

#### 4. Test Migration

```bash
# Apply migration
alembic upgrade head

# Verify database
psql -d mexa_db -c "\d users"

# Test rollback
alembic downgrade -1

# Verify rollback worked
psql -d mexa_db -c "\d users"

# Re-apply for development
alembic upgrade head
```

#### 5. Commit Migration

```bash
git add migrations/versions/xxx_add_email_to_users.py
git commit -m "Add email column to users table"
git push
```

### Example Workflows

#### Adding a New Table

1. Create model in `app/models.py`:
   ```python
   class Product(Base):
       __tablename__ = 'products'
       id = Column(Integer, primary_key=True)
       name = Column(String(255), nullable=False)
       price = Column(Numeric(10, 2), nullable=False)
   ```

2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "create products table"
   ```

3. Review and test as above.

#### Adding an Index

1. Create manual migration:
   ```bash
   alembic revision -m "add index on users email"
   ```

2. Edit the migration file:
   ```python
   def upgrade():
       op.create_index('ix_users_email', 'users', ['email'])
   
   def downgrade():
       op.drop_index('ix_users_email', table_name='users')
   ```

3. Apply and test.

#### Data Migration

When you need to transform existing data:

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column

def upgrade():
    # Add new column
    op.add_column('users', sa.Column('full_name', sa.String(255), nullable=True))
    
    # Define table for data operations
    users = table('users',
        column('id', sa.Integer),
        column('first_name', sa.String),
        column('last_name', sa.String),
        column('full_name', sa.String)
    )
    
    # Migrate data
    connection = op.get_bind()
    results = connection.execute(
        sa.select([users.c.id, users.c.first_name, users.c.last_name])
    )
    
    for row in results:
        connection.execute(
            users.update()
            .where(users.c.id == row.id)
            .values(full_name=f"{row.first_name} {row.last_name}")
        )

def downgrade():
    op.drop_column('users', 'full_name')
```

### Best Practices

1. **Always provide downgrade functions**: Every migration should be reversible
2. **Test locally first**: Apply and rollback migrations in your local environment
3. **Keep migrations atomic**: One logical change per migration
4. **Review autogenerated migrations**: They may not catch everything correctly
5. **Use meaningful names**: Make migration names descriptive
6. **Add comments**: Explain complex operations in migration files
7. **Don't edit applied migrations**: Create new migrations to fix issues
8. **Backup before production migrations**: Always have a rollback plan

### Troubleshooting

#### "alembic_version table doesn't exist"

First time setup:
```bash
alembic stamp head
```

#### Migrations out of sync

Check status:
```bash
alembic current
alembic history
```

If needed, stamp to correct version:
```bash
alembic stamp <revision>
```

#### Migration conflicts

If you have merge conflicts in migrations:
1. Resolve conflicts in migration files
2. Fix the revision chain (down_revision values)
3. Test that all migrations apply correctly

## Running the Application

### Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script if available
python run.py
```

Access the API at: http://localhost:8000

API documentation: http://localhost:8000/docs

### With Docker

If Docker setup is available:

```bash
docker-compose up -d
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_migrations.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v
```

### Writing Tests

Tests should be placed in the `tests/` directory with filenames starting with `test_`.

Example test:
```python
def test_user_creation():
    user = User(username="test", email="test@example.com")
    db.add(user)
    db.commit()
    assert user.id is not None
```

## Code Quality

### Linting

```bash
# Check code style
flake8 app/ tests/

# Format code
black app/ tests/

# Sort imports
isort app/ tests/
```

### Type Checking

```bash
mypy app/
```

---

For more detailed migration information, see [MIGRATIONS.md](MIGRATIONS.md).
