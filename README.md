# Mexa.Digital

## Project Vision
Mexa.Digital aims to streamline digital services, ensuring an efficient and user-friendly experience for clients and stakeholders.

## Architecture
The project is structured into two main components: Backend powered by FastAPI and PostgreSQL, and a Frontend using React.

## Modules
- **Backend:** API services for data manipulation and management.
- **Frontend:** User interface for interaction with the services.
- **Database:** PostgreSQL for data storage with Alembic migrations.

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Docker (optional)

### Setup with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/mexadigital/mexa-core.git
   cd mexa-core
   ```

2. Start services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

   This will:
   - Start PostgreSQL database
   - Run database migrations automatically
   - Start the FastAPI application

3. Access the application:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mexadigital/mexa-core.git
   cd mexa-core
   ```

2. Set up environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure database:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. Create database:
   ```bash
   createdb mexa_db
   ```

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Database Migrations

This project uses Alembic for database migrations. See [MIGRATIONS.md](MIGRATIONS.md) for detailed guide.

### Common Commands

```bash
# Check migration status
alembic current

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## Documentation

- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup and workflows
- [MIGRATIONS.md](MIGRATIONS.md) - Comprehensive migration guide

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```