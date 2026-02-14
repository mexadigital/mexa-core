#!/bin/bash
# backend/entrypoint.sh

set -e

echo "🚀 MEXA Starting..."

# 1. Validar y asignar defaults a DATABASE_HOST/PORT
DATABASE_HOST="${DATABASE_HOST:-db}"
DATABASE_PORT="${DATABASE_PORT:-5432}"

echo "📡 Database Config:"
echo "   HOST: $DATABASE_HOST"
echo "   PORT: $DATABASE_PORT"

# 2. Crear directorio de logs
mkdir -p /app/logs
echo "✅ Logs directory ready"

# 3. Esperar a que PostgreSQL esté lista
echo "⏳ Waiting for PostgreSQL at $DATABASE_HOST:$DATABASE_PORT..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
  if nc -z $DATABASE_HOST $DATABASE_PORT 2>/dev/null; then
    echo "✅ PostgreSQL ready"
    break
  fi
  
  attempt=$((attempt + 1))
  echo "   Attempt $attempt/$max_attempts..."
  sleep 1
done

if [ $attempt -eq $max_attempts ]; then
  echo "❌ PostgreSQL not available after $max_attempts attempts"
  exit 1
fi

# 4. Ejecutar migraciones Alembic
echo "🔄 Running database migrations..."
cd /app

if alembic upgrade head; then
  echo "✅ Migrations completed successfully"
else
  echo "❌ Migration failed"
  exit 1
fi

# 5. Mostrar versión actual
alembic current

# 6. Iniciar aplicación Flask
echo "🎯 Starting Flask application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
