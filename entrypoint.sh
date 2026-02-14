#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p /app/logs
chmod 755 /app/logs

# Run database migrations if needed
# python manage.py db upgrade

# Execute the main command
exec "$@"
