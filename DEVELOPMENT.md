# MEXA - Guía de Desarrollo

## Inicio Rápido con Docker

### 1. Iniciar servicios
```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL en puerto 5432
- Redis en puerto 6379
- Backend Flask en puerto 5000
- Celery Worker
- Celery Beat

### 2. Inicializar base de datos
```bash
# Crear tablas y datos iniciales
docker-compose exec backend python init_db.py

# O crear migración (si es necesario)
docker-compose exec backend flask db migrate -m "Description"
docker-compose exec backend flask db upgrade
```

### 3. Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo base de datos
docker-compose logs -f db
```

### 4. Detener servicios
```bash
docker-compose down

# Eliminar también volúmenes (CUIDADO: borra datos)
docker-compose down -v
```

## Desarrollo Local (sin Docker)

### Backend

#### Requisitos
- Python 3.11+
- PostgreSQL 15+
- Redis

#### Setup
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tus configuraciones locales

# Inicializar base de datos
python init_db.py

# Ejecutar servidor de desarrollo
flask run
# O con hot reload:
export FLASK_ENV=development
flask run --reload
```

#### Crear migraciones
```bash
# Generar migración automática
flask db migrate -m "Description of changes"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade
```

### Frontend

#### Requisitos
- Node.js 18+
- npm o yarn

#### Setup
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar .env
cp .env.example .env

# Ejecutar en desarrollo
npm run dev
```

La aplicación estará disponible en http://localhost:3000

#### Build para producción
```bash
npm run build
```

Los archivos se generarán en `frontend/dist/`

## Credenciales de Desarrollo

**Admin:**
- Usuario: `carlos`
- Password: `admin123`

**Usuario:**
- Usuario: `jefe`  
- Password: `jefe123`

⚠️ **NUNCA usar estas credenciales en producción!**
