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

## MEXA Formularios

El motor configurable está disponible en `/formularios-app`. Permite crear formatos, agregar campos, capturar registros, imprimir o guardar como PDF y preparar mensajes de WhatsApp.

Para cargar la demostración escolar:

```bash
cd backend
python -m scripts.crear_demo_formularios
uvicorn app.main:app --reload
```

Credenciales demo: `demo@mexa.com` / `MEXA-demo-2026`.


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

La pantalla administrativa está disponible en `/escolar-app`.
Cada documento autorizado contiene un folio y un QR que apunta a
`GET /escolar/verificar/{token}`. La consulta pública protege el nombre y la
matrícula del alumno.
