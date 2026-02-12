# MEXA API Documentation

Base URL: `http://localhost:5000/api`

All endpoints except `/auth/login` and `/auth/register` require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Authentication

### POST /auth/register
Register a new user (admin only in production)

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "nombre_completo": "string",
  "rol": "admin|usuario"
}
```

**Response (201):**
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "rol": "admin|usuario"
  }
}
```

### POST /auth/login
Login and get JWT token

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "message": "Login exitoso",
  "access_token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "rol": "admin|usuario"
  }
}
```

### GET /auth/me
Get current user information

**Response (200):**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "nombre_completo": "string",
  "rol": "admin|usuario",
  "activo": true
}
```

## Vales (Daily Records)

### GET /vales
Get all vales with optional filters

**Query Parameters:**
- `fecha_inicio` (YYYY-MM-DD): Start date filter
- `fecha_fin` (YYYY-MM-DD): End date filter
- `disciplina`: Filter by discipline (Civil|Mecánica|Eléctrica)
- `satelite`: Filter by satellite (#1|#2|#3)
- `producto_id`: Filter by product ID

**Response (200):**
```json
[
  {
    "id": 1,
    "usuario_id": 1,
    "usuario": "carlos",
    "producto_id": 1,
    "producto": "Casco",
    "disciplina": "Civil",
    "satelite": "#1",
    "cantidad_salida": 5,
    "stock_actual": 95,
    "observaciones": "string",
    "fecha": "2024-02-12",
    "created_at": "2024-02-12T10:30:00"
  }
]
```

### POST /vales
Create a new vale

**Request:**
```json
{
  "producto_id": 1,
  "disciplina": "Civil|Mecánica|Eléctrica",
  "satelite": "#1|#2|#3",
  "cantidad_salida": 5,
  "stock_actual": 95,
  "observaciones": "optional string",
  "fecha": "2024-02-12" // optional, defaults to today
}
```

**Response (201):**
```json
{
  "message": "Vale creado exitosamente",
  "vale": { /* vale object */ }
}
```

### GET /vales/:id
Get a specific vale

**Response (200):**
```json
{
  "id": 1,
  "usuario_id": 1,
  "producto_id": 1,
  "disciplina": "Civil",
  "satelite": "#1",
  "cantidad_salida": 5,
  "stock_actual": 95,
  "observaciones": "string",
  "fecha": "2024-02-12",
  "created_at": "2024-02-12T10:30:00"
}
```

### PUT /vales/:id
Update a vale (owner or admin only)

**Request:** Same as POST, all fields optional

**Response (200):**
```json
{
  "message": "Vale actualizado exitosamente",
  "vale": { /* vale object */ }
}
```

### DELETE /vales/:id
Delete a vale (owner or admin only)

**Response (200):**
```json
{
  "message": "Vale eliminado exitosamente"
}
```

## Productos

### GET /productos
Get all active products

**Response (200):**
```json
[
  {
    "id": 1,
    "nombre": "Casco",
    "descripcion": "Casco de seguridad",
    "categoria": "EPP",
    "unidad_medida": "unidad",
    "stock_minimo": 20,
    "activo": true,
    "created_at": "2024-02-12T10:00:00"
  }
]
```

### POST /productos
Create a new product (admin only)

**Request:**
```json
{
  "nombre": "string",
  "descripcion": "string",
  "categoria": "string",
  "unidad_medida": "unidad",
  "stock_minimo": 10
}
```

**Response (201):**
```json
{
  "message": "Producto creado exitosamente",
  "producto": { /* producto object */ }
}
```

### PUT /productos/:id
Update a product (admin only)

**Request:** Same as POST, all fields optional

**Response (200):**
```json
{
  "message": "Producto actualizado exitosamente",
  "producto": { /* producto object */ }
}
```

### DELETE /productos/:id
Soft delete a product (admin only)

**Response (200):**
```json
{
  "message": "Producto eliminado exitosamente"
}
```

## Dashboard

### GET /dashboard/consumo-hoy
Get today's consumption by discipline

**Response (200):**
```json
{
  "Civil": 15,
  "Mecánica": 10,
  "Eléctrica": 8,
  "Total": 33
}
```

### GET /dashboard/stock-actual
Get current stock for all products

**Response (200):**
```json
[
  {
    "producto_id": 1,
    "producto_nombre": "Casco",
    "stock_actual": 95,
    "stock_minimo": 20,
    "alerta": false
  }
]
```

### GET /dashboard/consumo-7-dias
Get consumption for last 7 days by discipline

**Response (200):**
```json
{
  "dates": ["2024-02-06", "2024-02-07", ...],
  "Civil": [10, 15, 12, ...],
  "Mecánica": [8, 10, 9, ...],
  "Eléctrica": [5, 7, 6, ...]
}
```

### GET /dashboard/consumo-satelite-7-dias
Get consumption for last 7 days by satellite

**Response (200):**
```json
{
  "dates": ["2024-02-06", "2024-02-07", ...],
  "#1": [10, 12, 11, ...],
  "#2": [8, 9, 10, ...],
  "#3": [5, 6, 5, ...]
}
```

### GET /dashboard/historico-30-dias
Get historical records for last 30 days

**Response (200):**
```json
[
  { /* vale object */ },
  ...
]
```

## Reportes

### GET /reportes/diario
Generate daily report (placeholder - Phase 2)

**Response (200):**
```json
{
  "message": "Reporte diario - En desarrollo"
}
```

### GET /reportes/semanal
Generate weekly report (placeholder - Phase 2)

**Response (200):**
```json
{
  "message": "Reporte semanal - En desarrollo"
}
```

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "error": "Error message describing what went wrong"
}
```

**401 Unauthorized:**
```json
{
  "error": "Credenciales inválidas" | "Token expired"
}
```

**403 Forbidden:**
```json
{
  "error": "No tiene permisos para realizar esta acción"
}
```

**404 Not Found:**
```json
{
  "error": "Recurso no encontrado"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Error interno del servidor"
}
```
