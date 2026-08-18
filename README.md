# Mexa.Digital

## Project Vision
Mexa.Digital aims to streamline digital services, ensuring an efficient and user-friendly experience for clients and stakeholders.

## Architecture
The project is structured into two main components: Backend powered by FastAPI and PostgreSQL, and a Frontend using React.

## Modules
- **Backend:** API services for data manipulation and management.
- **Frontend:** User interface for interaction with the services.
- **Database:** PostgreSQL for data storage.

## Setup Instructions
1. Clone the repository
2. Set up your environment using the `.env.example` file.
3. Install dependencies as specified in the `requirements.txt` file.

## Backend activo

La aplicación completa vive en `backend/app`. En Render debe iniciarse con:

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## OCR de vales

El primer flujo OCR está disponible bajo `/vales-resguardo/ocr`:

- `POST /analizar`: guarda la imagen, evita duplicados por hash y produce una propuesta.
- `GET /{analisis_id}`: consulta la lectura y su estado.
- `POST /{analisis_id}/confirmar`: crea el vale únicamente después de revisión humana.

Estados: `SUBIDO`, `PROCESANDO`, `REQUIERE_REVISION`, `CONFIRMADO` y `RECHAZADO`.

La implementación local usa Tesseract cuando está instalado. Si no está disponible,
el análisis permanece en `REQUIERE_REVISION` y puede completarse manualmente. La
escritura manuscrita siempre debe verificarse antes de confirmar.

## Trabajadores y usuarios

`Trabajador` es el receptor operativo de EPP, consumibles o herramientas y no
necesita iniciar sesión. `Usuario` representa a administradores, almacenistas y
supervisores con acceso al sistema.

## MEXA Formularios

El motor documental configurable está disponible en:

```text
http://127.0.0.1:8000/formularios-app
```

Permite crear un formato, agregar campos de texto, número, fecha, teléfono,
selección o párrafo, capturar registros y abrir una versión imprimible que el
navegador puede guardar como PDF. También prepara un mensaje de WhatsApp cuando
el formato contiene un campo cuya clave incluye `telefono`.

Para preparar una demostración escolar con datos ficticios:

```bash
cd backend
../.venv/bin/python -m scripts.crear_demo_formularios
../.venv/bin/uvicorn app.main:app --reload
```

Credenciales de la demostración:

```text
Usuario: demo@mexa.com
Contraseña: MEXA-demo-2026
```
## MEXA Escolar: constancias verificables

El módulo escolar permite solicitar constancias a partir del padrón de alumnos.
El pago solamente habilita el proceso: el documento debe pasar por revisión y
autorización humana antes de poder imprimirse o compartirse.

Flujo implementado:

1. `POST /escolar/constancias`
2. `PATCH /escolar/constancias/{id}/pago`
3. `POST /escolar/constancias/{id}/revisar`
4. `POST /escolar/constancias/{id}/autorizar`
5. `GET /escolar/constancias/{id}/documento`
6. `POST /escolar/constancias/{id}/entregar`

Cada documento autorizado contiene un folio y un QR que apunta a
`GET /escolar/verificar/{token}`. La consulta pública protege el nombre y la
matrícula del alumno. Las solicitudes de original pueden marcarse como listas
para recoger sin perder el registro digital.

### Primer acceso en Render sin Shell

Configura estas variables privadas en el servicio antes de desplegar:

- `MEXA_BOOTSTRAP_EMAIL`
- `MEXA_BOOTSTRAP_PASSWORD` (mínimo 12 caracteres)

El build ejecuta `python -m scripts.crear_demo_formularios`. La carga es
idempotente: crea el administrador, un grupo y un alumno ficticio únicamente
si todavía no existen. La contraseña nunca se guarda en GitHub.
