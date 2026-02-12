# MEXA v1.0 - Sistema de Gestión de EPP y Consumibles

Sistema completo para automatizar el registro y gestión de Equipos de Protección Personal (EPP) y consumibles para ICA FLUOR.

## 🎯 Características

- **Vale Digital**: Formulario rápido para registrar consumo diario
- **Dashboard en Vivo**: Visualización de consumo por disciplina y satélite
- **Histórico**: Tabla con últimos 30 días de registros
- **Stock Actual**: Monitoreo de inventario con alertas
- **Autenticación**: Sistema de login con roles (admin/usuario)

## 🏗️ Arquitectura

### Backend
- **Framework**: Flask 3.0
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy
- **Autenticación**: JWT (Flask-JWT-Extended)
- **Task Queue**: Celery + Redis (para reportes automáticos - Fase 2)

### Frontend
- **Framework**: React 18 + Vite
- **Estilos**: TailwindCSS
- **Gráficas**: Chart.js + react-chartjs-2
- **Routing**: React Router
- **HTTP Client**: Axios

## 🚀 Instalación y Configuración

### Prerequisitos
- Docker y Docker Compose
- Node.js 18+ (para desarrollo frontend)
- Python 3.11+ (para desarrollo backend)

### Instalación con Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone https://github.com/mexadigital/mexa-core.git
cd mexa-core
```

2. **Configurar variables de entorno**
```bash
# Backend
cp backend/.env.example backend/.env
# Editar backend/.env con tus configuraciones

# Frontend
cp frontend/.env.example frontend/.env
```

3. **Iniciar servicios con Docker Compose**
```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL (puerto 5432)
- Redis (puerto 6379)
- Backend Flask (puerto 5000)
- Celery Worker y Beat

4. **Inicializar la base de datos**
```bash
docker-compose exec backend python init_db.py
```

Esto creará:
- Tablas de la base de datos
- Usuarios por defecto (carlos/admin123 y jefe/jefe123)
- Catálogo de productos EPP inicial

5. **Instalar e iniciar el frontend**
```bash
cd frontend
npm install
npm run dev
```

La aplicación estará disponible en:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

### Instalación Manual (Desarrollo)

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env

# Inicializar base de datos
python init_db.py

# Ejecutar aplicación
flask run
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build
```

## 📊 Modelos de Datos

### Usuario
- username, email, password_hash
- rol (admin/usuario)
- timestamps

### Producto
- nombre, descripcion, categoria
- unidad_medida, stock_minimo
- timestamps

### Vale (Registro Diario)
- usuario_id, producto_id
- disciplina (Civil/Mecánica/Eléctrica)
- satelite (#1/#2/#3)
- cantidad_salida, stock_actual
- observaciones, fecha
- timestamps

## 🔐 Credenciales por Defecto

**Admin:**
- Usuario: `carlos`
- Contraseña: `admin123`

**Usuario:**
- Usuario: `jefe`
- Contraseña: `jefe123`

⚠️ **IMPORTANTE**: Cambiar estas contraseñas en producción!

## 📱 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Usuario actual
- `POST /api/auth/change-password` - Cambiar contraseña

### Vales
- `GET /api/vales` - Listar vales (con filtros opcionales)
- `POST /api/vales` - Crear vale
- `GET /api/vales/:id` - Obtener vale
- `PUT /api/vales/:id` - Actualizar vale
- `DELETE /api/vales/:id` - Eliminar vale

### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto (admin)
- `PUT /api/productos/:id` - Actualizar producto (admin)
- `DELETE /api/productos/:id` - Eliminar producto (admin)

### Dashboard
- `GET /api/dashboard/consumo-hoy` - Consumo de hoy por disciplina
- `GET /api/dashboard/stock-actual` - Stock actual de productos
- `GET /api/dashboard/consumo-7-dias` - Consumo últimos 7 días
- `GET /api/dashboard/consumo-satelite-7-dias` - Consumo por satélite
- `GET /api/dashboard/historico-30-dias` - Histórico 30 días

## 🗺️ Roadmap

### ✅ Fase 1 (Actual)
- ✅ Setup Docker + PostgreSQL + Redis
- ✅ Modelos de datos (Usuario, Producto, Vale)
- ✅ API REST completa
- ✅ Frontend con React + TailwindCSS
- ✅ Dashboard con gráficas
- ✅ Autenticación JWT

### 📅 Fase 2 (Próximamente)
- Celery tasks para reportes automáticos
- Reportes diarios (email + PDF)
- Reportes semanales (email + PDF)
- Alertas de stock bajo
- Integración WhatsApp (Twilio)

### 📅 Fase 3 (Futuro)
- Deploy en Render
- Pruebas automatizadas
- Optimizaciones de rendimiento
- Exportación de datos (Excel)

## 🧪 Testing

```bash
# Backend tests (cuando estén implementados)
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📄 Licencia

Privado - ICA FLUOR

## 👥 Autor

Mexa Digital - Sistema desarrollado para ICA FLUOR