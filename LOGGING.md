# Logging and Audit Trail Documentation

## Overview

Mexa Core uses a comprehensive structured logging system with JSON formatting, request tracking, and database audit logs for compliance, debugging, and security monitoring.

## Logging Levels

### When to Use Each Level

- **DEBUG**: Detailed diagnostic information useful during development
  - Variable values, function entry/exit
  - Database queries
  - Internal state changes

- **INFO**: General informational messages about application progress
  - Request start/end
  - Successful operations
  - Resource creation/updates

- **WARNING**: Indicates something unexpected but not critical
  - Deprecated API usage
  - Resource not found (404s)
  - Recoverable errors

- **ERROR**: Error events that may still allow the app to continue
  - Database errors
  - Failed validations
  - Unhandled exceptions

- **CRITICAL**: Very severe error events that may cause the app to abort
  - Database connection failures
  - Critical service unavailability

## Log Storage

### File Locations

All logs are stored in the `logs/` directory at the application root:

- **logs/mexa.log**: All log entries at DEBUG level and above (rotating, 10MB max, 10 backups)
- **logs/mexa-error.log**: Only ERROR and CRITICAL entries (rotating, 10MB max, 10 backups)
- **STDOUT**: INFO level and above (for Docker and development)

### Log Rotation

Both log files use rotating file handlers:
- Maximum size: 10MB per file
- Backup count: 10 files
- Old files are numbered: mexa.log.1, mexa.log.2, etc.

## JSON Log Format

All logs are formatted as JSON for easy parsing and analysis.

### Example Log Entry

```json
{
  "timestamp": "2024-02-14T01:52:42.123Z",
  "level": "INFO",
  "logger": "app.routes.epp",
  "module": "epp",
  "function": "create_epp",
  "line": 25,
  "message": "EPP resource created",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "epp_id": 123,
  "data": {"name": "Safety Helmet", "description": "Hard hat"}
}
```

### Standard Fields

Every log entry includes:
- `timestamp`: ISO 8601 formatted timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger`: Name of the logger (typically module name)
- `module`: Python module name
- `function`: Function where log was generated
- `line`: Line number in source code
- `message`: Human-readable message

### Context Fields

Additional context fields when available:
- `request_id`: Unique identifier for the request
- `user_id`: Authenticated user ID
- `endpoint`: API endpoint path
- `status_code`: HTTP response status
- `duration`: Request processing time in seconds
- `ip_address`: Client IP address
- `error_type`: Exception class name
- `stack_trace`: Full stack trace for errors

## Request Tracking

### Request ID Flow

1. **Generation**: Each request receives a unique UUID request ID
2. **Header Accept**: Custom `X-Request-ID` header is respected if provided
3. **Storage**: Stored in Flask's `g.request_id` for the request lifecycle
4. **Propagation**: Included in all log entries during the request
5. **Response**: Added to response headers as `X-Request-ID`

### Request Lifecycle Logging

#### Request Entry
```json
{
  "timestamp": "2024-02-14T01:52:42.100Z",
  "level": "INFO",
  "message": "Request started",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/epp",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

#### Request Exit
```json
{
  "timestamp": "2024-02-14T01:52:42.250Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/epp",
  "status_code": 201,
  "duration": 0.150,
  "ip_address": "192.168.1.100"
}
```

## Audit Logs

### Database Schema

The `audit_logs` table stores all critical system actions:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Primary key |
| request_id | String(36) | Request UUID (unique, indexed) |
| user_id | Integer (FK) | User who performed action (nullable, indexed) |
| action | String(50) | Action type (indexed) |
| resource_type | String(50) | Resource type (indexed) |
| resource_id | Integer | Resource ID (nullable, indexed) |
| old_values | JSON | State before change |
| new_values | JSON | State after change |
| endpoint | String(255) | API endpoint |
| method | String(10) | HTTP method |
| ip_address | String(45) | Client IP |
| created_at | DateTime | Timestamp (indexed) |

### Action Types

Common actions tracked:
- `create`: Resource creation
- `update`: Resource modification
- `delete`: Resource deletion
- `login_success`: Successful authentication
- `login_failed`: Failed authentication attempt
- `adjust_stock`: Inventory adjustments

### Resource Types

- `epp`: Equipment/EPP resources
- `consumable`: Consumable items
- `usuario`: User accounts
- `producto`: Products
- `vale`: Vouchers

## Common Audit Queries

### Find All Actions by a User

```python
from app.utils.audit import get_audit_logs

# Get all actions by user ID 123
audit_logs = get_audit_logs(user_id=123, limit=50)
```

SQL equivalent:
```sql
SELECT * FROM audit_logs 
WHERE user_id = 123 
ORDER BY created_at DESC 
LIMIT 50;
```

### Find All Changes to a Specific Resource

```python
# Get all changes to EPP resource ID 456
audit_logs = get_audit_logs(resource_type='epp', resource_id=456)
```

SQL equivalent:
```sql
SELECT * FROM audit_logs 
WHERE resource_type = 'epp' AND resource_id = 456 
ORDER BY created_at DESC;
```

### Find All Failed Login Attempts

```python
# Get all failed login attempts
audit_logs = get_audit_logs(action='login_failed', limit=100)
```

SQL equivalent:
```sql
SELECT * FROM audit_logs 
WHERE action = 'login_failed' 
ORDER BY created_at DESC 
LIMIT 100;
```

### Find All Actions from a Specific IP

```sql
SELECT * FROM audit_logs 
WHERE ip_address = '192.168.1.100' 
ORDER BY created_at DESC;
```

### Find All Deletions in the Last 24 Hours

```sql
SELECT * FROM audit_logs 
WHERE action = 'delete' 
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

### Trace a Complete Request

```python
from app.database import SessionLocal
from app.models.audit_log import AuditLog

db = SessionLocal()
request_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'

# Get all audit logs for a specific request
audit_logs = db.query(AuditLog).filter_by(request_id=request_id).all()
```

SQL equivalent:
```sql
SELECT * FROM audit_logs 
WHERE request_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
ORDER BY created_at;
```

Then search application logs:
```bash
grep "a1b2c3d4-e5f6-7890-abcd-ef1234567890" logs/mexa.log
```

## Debugging Guide

### Finding Errors

#### View Recent Errors
```bash
tail -f logs/mexa-error.log | jq '.'
```

#### Search for Specific Error
```bash
grep "DatabaseError" logs/mexa-error.log | jq '.'
```

#### Count Errors by Type
```bash
grep '"level": "ERROR"' logs/mexa.log | jq -r '.error_type' | sort | uniq -c
```

### Tracing Requests

#### Get Request ID from Response
```bash
curl -i http://localhost:5000/api/epp/1
# Look for X-Request-ID header
```

#### Find All Logs for Request
```bash
REQUEST_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
grep "$REQUEST_ID" logs/mexa.log | jq '.'
```

#### Measure Request Duration
```bash
REQUEST_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
grep "$REQUEST_ID" logs/mexa.log | jq 'select(.duration) | .duration'
```

### Performance Analysis

#### Find Slow Requests (>1 second)
```bash
grep '"duration"' logs/mexa.log | jq 'select(.duration > 1) | {request_id, path, duration}'
```

#### Average Request Duration by Endpoint
```bash
grep '"duration"' logs/mexa.log | jq -r '"\(.path) \(.duration)"' | awk '{sum[$1]+=$2; count[$1]++} END {for (path in sum) print path, sum[path]/count[path]}'
```

### Monitoring User Activity

#### Recent Actions by User
```sql
SELECT action, resource_type, resource_id, created_at 
FROM audit_logs 
WHERE user_id = 123 
ORDER BY created_at DESC 
LIMIT 20;
```

#### Most Active Users
```sql
SELECT user_id, COUNT(*) as action_count 
FROM audit_logs 
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY user_id 
ORDER BY action_count DESC 
LIMIT 10;
```

### Security Monitoring

#### Multiple Failed Logins from Same IP
```sql
SELECT ip_address, COUNT(*) as attempts 
FROM audit_logs 
WHERE action = 'login_failed' 
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY ip_address 
HAVING COUNT(*) > 5 
ORDER BY attempts DESC;
```

#### Recent Deletions
```sql
SELECT user_id, resource_type, resource_id, old_values, created_at 
FROM audit_logs 
WHERE action = 'delete' 
ORDER BY created_at DESC 
LIMIT 50;
```

## Production Best Practices

### Configuration

1. **Set LOG_LEVEL Environment Variable**
   ```bash
   export LOG_LEVEL=INFO  # Use INFO or WARNING in production
   ```

2. **Monitor Log File Size**
   - Logs rotate automatically at 10MB
   - Monitor disk space usage
   - Consider archiving old logs

3. **Database Maintenance**
   - Archive old audit logs periodically
   - Consider partitioning by date for large tables
   - Index maintenance for performance

### Security

1. **Sensitive Data**
   - Never log passwords or tokens
   - Redact sensitive fields in old_values/new_values
   - Consider encryption for stored audit logs

2. **Access Control**
   - Restrict access to log files
   - Implement audit log viewing permissions
   - Protect against log injection attacks

3. **Retention**
   - Define retention policies (e.g., 90 days)
   - Comply with data protection regulations
   - Implement automated archival

### Performance

1. **Async Logging** (future enhancement)
   - Consider queuing for high-traffic scenarios
   - Use separate log processing service

2. **Batch Inserts** (future enhancement)
   - Batch audit log inserts for better performance
   - Use background workers

3. **Monitoring**
   - Set up alerts for high error rates
   - Monitor log processing delays
   - Track audit log table growth

## Troubleshooting

### Logs Not Appearing

1. Check logs directory exists and is writable:
   ```bash
   ls -la logs/
   ```

2. Check LOG_LEVEL configuration:
   ```bash
   echo $LOG_LEVEL
   ```

3. Verify logging is initialized:
   ```python
   import logging
   logging.getLogger().handlers  # Should show 3 handlers
   ```

### Audit Logs Not Created

1. Check database connection
2. Verify audit_logs table exists
3. Check for errors in logs/mexa-error.log
4. Audit failures are logged but don't break the app

### JSON Parsing Errors

1. Ensure using `jq` for JSON parsing:
   ```bash
   tail logs/mexa.log | jq '.'
   ```

2. Check for corrupted log files:
   ```bash
   head -1 logs/mexa.log | jq '.'
   ```

## Integration Examples

### Adding Audit Logging to New Routes

```python
from app.utils.audit import log_audit
import logging

logger = logging.getLogger(__name__)

@app.route('/api/myresource', methods=['POST'])
def create_resource():
    data = request.json
    resource = create_my_resource(data)
    
    # Log audit trail
    log_audit(
        action='create',
        resource_type='myresource',
        resource_id=resource.id,
        new_values=data
    )
    
    # Log to application logs
    logger.info(
        'Resource created',
        extra={'resource_id': resource.id, 'type': 'myresource'}
    )
    
    return jsonify(resource.to_dict()), 201
```

### Custom Context Fields

```python
from flask import g

# Add custom context in route
@app.before_request
def add_user_context():
    if current_user.is_authenticated:
        g.user_id = current_user.id

# Will be automatically captured by log_audit()
```

### Querying Audit Logs in Views

```python
from app.utils.audit import get_audit_logs

@app.route('/api/audit-logs')
def list_audit_logs():
    resource_type = request.args.get('resource_type')
    action = request.args.get('action')
    
    audit_logs = get_audit_logs(
        resource_type=resource_type,
        action=action,
        limit=50
    )
    
    return jsonify([log.to_dict() for log in audit_logs])
```
