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
