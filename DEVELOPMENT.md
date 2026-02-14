# Development Guide

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mexadigital/mexa-core.git
   cd mexa-core
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Create logs directory:
   ```bash
   mkdir -p logs
   ```

## Running the Application

### Development Server

```bash
# Set environment variables
export FLASK_APP=app
export FLASK_ENV=development
export LOG_LEVEL=DEBUG

# Run Flask development server
python -m flask run --host=0.0.0.0 --port=5000
```

Or use the provided run script:

```python
# run.py
from app import create_app

if __name__ == '__main__':
    app = create_app({'DEBUG': True})
    app.run(host='0.0.0.0', port=5000)
```

```bash
python run.py
```

## Logging in Development

### Viewing Logs

#### Tail Main Log File
```bash
# View all logs in real-time
tail -f logs/mexa.log | jq '.'

# Filter by log level
tail -f logs/mexa.log | jq 'select(.level == "ERROR")'

# Filter by module
tail -f logs/mexa.log | jq 'select(.module == "epp")'
```

#### Tail Error Log File
```bash
# View only errors
tail -f logs/mexa-error.log | jq '.'
```

#### View STDOUT (Console)
When running the development server, INFO level and above logs are also printed to the console with JSON formatting.

### Setting Log Level

Control verbosity with the `LOG_LEVEL` environment variable:

```bash
# Maximum verbosity (recommended for development)
export LOG_LEVEL=DEBUG

# Normal verbosity
export LOG_LEVEL=INFO

# Minimal verbosity
export LOG_LEVEL=WARNING
```

### Analyzing Logs

#### Count Requests by Endpoint
```bash
grep '"message": "Request completed"' logs/mexa.log | jq -r '.path' | sort | uniq -c
```

#### Find Slow Requests
```bash
grep '"duration"' logs/mexa.log | jq 'select(.duration > 0.5) | {path, duration, request_id}'
```

#### Track a Specific Request
```bash
# Get request_id from response header
REQUEST_ID=$(curl -s -D - http://localhost:5000/api/epp/1 | grep X-Request-ID | awk '{print $2}' | tr -d '\r')

# View all logs for that request
grep "$REQUEST_ID" logs/mexa.log | jq '.'
```

## Working with Audit Logs

### Querying Audit Logs

#### Using Python
```python
from app.utils.audit import get_audit_logs

# Get recent audit logs
logs = get_audit_logs(limit=10)
for log in logs:
    print(f"{log.action} {log.resource_type} {log.resource_id}")

# Filter by resource type
epp_logs = get_audit_logs(resource_type='epp', limit=20)

# Filter by action
deletions = get_audit_logs(action='delete', limit=50)
```

#### Using SQL (psql)
```bash
# Connect to database
psql $DATABASE_URL

# Recent audit logs
SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;

# Count by action type
SELECT action, COUNT(*) FROM audit_logs GROUP BY action;

# View a specific resource's history
SELECT action, old_values, new_values, created_at 
FROM audit_logs 
WHERE resource_type = 'epp' AND resource_id = 1
ORDER BY created_at;
```

#### Using Python REPL
```python
from app.database import SessionLocal
from app.models.audit_log import AuditLog

db = SessionLocal()

# Get all audit logs
audit_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()

# Print them
for log in audit_logs:
    print(f"{log.created_at}: {log.action} {log.resource_type} {log.resource_id}")

# Filter by user
user_logs = db.query(AuditLog).filter_by(user_id=123).all()

# Close session
db.close()
```

### Correlating Requests Across Logs

Every request has a unique request_id that appears in:
1. Application logs (logs/mexa.log)
2. Error logs (logs/mexa-error.log)
3. Audit log database records
4. Response headers (X-Request-ID)

#### Example Correlation Flow

1. **Make a request and capture request_id:**
   ```bash
   curl -i -X POST http://localhost:5000/api/epp \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Item", "description": "Test"}' \
     | grep X-Request-ID
   ```

2. **Find in application logs:**
   ```bash
   REQUEST_ID="your-request-id-here"
   grep "$REQUEST_ID" logs/mexa.log | jq '.'
   ```

3. **Find in audit logs:**
   ```python
   from app.database import SessionLocal
   from app.models.audit_log import AuditLog
   
   db = SessionLocal()
   audit = db.query(AuditLog).filter_by(request_id=REQUEST_ID).first()
   print(audit.to_dict())
   db.close()
   ```

4. **Trace the complete flow:**
   ```bash
   # Request entry
   grep "$REQUEST_ID" logs/mexa.log | jq 'select(.message == "Request started")'
   
   # Business logic
   grep "$REQUEST_ID" logs/mexa.log | jq 'select(.message | contains("created"))'
   
   # Request exit
   grep "$REQUEST_ID" logs/mexa.log | jq 'select(.message == "Request completed")'
   ```

## Database Management

### Migrations

When you add or modify models:

1. Create the migration:
   ```bash
   # If using Alembic (recommended for production)
   alembic revision --autogenerate -m "Add new field"
   ```

2. Apply the migration:
   ```bash
   alembic upgrade head
   ```

### Manual Table Creation

The application automatically creates tables on startup via `Base.metadata.create_all()` in `app/__init__.py`.

To manually create tables:

```python
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
```

### Resetting Database

```bash
# Drop all tables (careful!)
psql $DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Recreate tables
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest test/

# Run specific test file
python -m pytest test/test_logging.py

# Run with verbose output
python -m pytest test/test_logging.py -v

# Run specific test
python -m pytest test/test_logging.py::TestLogging::test_request_id_generation -v
```

### Running Tests with Coverage

```bash
# Install coverage
pip install coverage pytest-cov

# Run with coverage
python -m pytest test/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Database

Tests use the same database as development by default. For isolation, consider:

1. Using a separate test database:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/mexa_test_db"
   python -m pytest test/
   ```

2. Using transactions that rollback after each test (already implemented in test_logging.py)

## Debugging

### Using Python Debugger (pdb)

Add a breakpoint in your code:

```python
import pdb; pdb.set_trace()
```

Or use the built-in `breakpoint()` function (Python 3.7+):

```python
breakpoint()
```

### Logging Debug Information

```python
import logging
logger = logging.getLogger(__name__)

def my_function(data):
    logger.debug('Function called', extra={'data': data})
    
    result = process(data)
    
    logger.debug('Processing complete', extra={'result': result})
    return result
```

### Viewing Request Context

```python
from flask import g, request

@app.route('/debug')
def debug_view():
    return {
        'request_id': g.request_id if hasattr(g, 'request_id') else None,
        'user_id': g.user_id if hasattr(g, 'user_id') else None,
        'ip_address': g.ip_address if hasattr(g, 'ip_address') else None,
        'path': request.path,
        'method': request.method
    }
```

## Code Quality

### Linting

```bash
# Install linting tools
pip install flake8 black

# Run linter
flake8 app/ test/

# Auto-format code
black app/ test/
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Run type checker
mypy app/
```

## Docker Development

### Building the Image

```bash
docker build -t mexa-core .
```

### Running with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Access logs directory
docker-compose exec app ls -la logs/

# Stop services
docker-compose down
```

### Accessing Logs in Docker

```bash
# Tail logs from running container
docker-compose exec app tail -f logs/mexa.log | jq '.'

# Copy logs from container
docker cp mexa-core_app_1:/app/logs ./local-logs/
```

## Common Development Tasks

### Adding a New Route with Audit Logging

1. Create the route in `app/routes/`:
   ```python
   from flask import Blueprint, request, jsonify
   import logging
   from app.utils.audit import log_audit
   
   logger = logging.getLogger(__name__)
   myroute_bp = Blueprint('myroute', __name__)
   
   @myroute_bp.route('/myresource', methods=['POST'])
   def create_resource():
       data = request.json
       
       # Your business logic here
       resource_id = save_resource(data)
       
       # Log audit
       log_audit(
           action='create',
           resource_type='myresource',
           resource_id=resource_id,
           new_values=data
       )
       
       # Log to application logs
       logger.info('Resource created', extra={'resource_id': resource_id})
       
       return jsonify({'id': resource_id}), 201
   ```

2. Register blueprint in `app/__init__.py`:
   ```python
   from app.routes.myroute import myroute_bp
   app.register_blueprint(myroute_bp, url_prefix='/api')
   ```

3. Test the route:
   ```bash
   curl -X POST http://localhost:5000/api/myresource \
     -H "Content-Type: application/json" \
     -d '{"name": "Test"}'
   ```

4. Verify audit log:
   ```python
   from app.utils.audit import get_audit_logs
   logs = get_audit_logs(resource_type='myresource', limit=1)
   print(logs[0].to_dict())
   ```

### Adding Custom Log Context

```python
from flask import g

@app.before_request
def add_custom_context():
    # Add custom fields to g object
    g.tenant_id = get_tenant_from_request()
    g.user_role = get_user_role()

# These will be automatically available in your route handlers
@app.route('/api/myroute')
def my_route():
    logger.info(
        'Custom context example',
        extra={
            'tenant_id': g.tenant_id if hasattr(g, 'tenant_id') else None,
            'user_role': g.user_role if hasattr(g, 'user_role') else None
        }
    )
```

## Troubleshooting

### Import Errors

If you get import errors, ensure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. PYTHONPATH includes the project root: `export PYTHONPATH=$PYTHONPATH:$(pwd)`

### Database Connection Errors

1. Check DATABASE_URL environment variable:
   ```bash
   echo $DATABASE_URL
   ```

2. Verify PostgreSQL is running:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. Check logs for connection errors:
   ```bash
   grep "DatabaseError" logs/mexa-error.log
   ```

### Logs Not Appearing

1. Check logs directory exists and is writable:
   ```bash
   ls -la logs/
   mkdir -p logs
   chmod 755 logs
   ```

2. Verify LOG_LEVEL:
   ```bash
   echo $LOG_LEVEL
   ```

3. Check handler configuration:
   ```python
   import logging
   print(logging.getLogger().handlers)
   ```

## Best Practices

1. **Always use structured logging with `extra={}`**
   ```python
   # Good
   logger.info('User logged in', extra={'user_id': user.id, 'ip': request.remote_addr})
   
   # Avoid
   logger.info(f'User {user.id} logged in from {request.remote_addr}')
   ```

2. **Use appropriate log levels**
   - DEBUG for detailed diagnostic info
   - INFO for general informational messages
   - WARNING for unexpected but recoverable events
   - ERROR for error conditions

3. **Don't log sensitive data**
   - Never log passwords, tokens, or API keys
   - Redact sensitive fields before logging

4. **Use audit logging for business events**
   - Call `log_audit()` for all CRUD operations
   - Include old_values and new_values for updates
   - Track user_id when available

5. **Use request_id for correlation**
   - Include request_id in all logs
   - Use it to trace requests across services
   - Return it in error responses for support

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [JSON Logger](https://github.com/madzak/python-json-logger)
- [LOGGING.md](LOGGING.md) - Comprehensive logging guide
