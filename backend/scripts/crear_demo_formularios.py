"""Crea datos ficticios para probar MEXA Formularios localmente.

Ejecutar desde la carpeta backend:
    ../.venv/bin/python -m scripts.crear_demo_formularios
"""

from app.core.security import hash_password
from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.models.formulario import CampoFormulario, Formulario
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario


DEMO_EMAIL = "demo@mexa.com"
DEMO_PASSWORD = "MEXA-demo-2026"


def crear_demo() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        organizacion = (
            db.query(Organizacion)
            .filter(Organizacion.rfc == "MEXA-DEMO-001")
            .first()
        )
        if not organizacion:
            organizacion = Organizacion(
                nombre="Institución Educativa Demo",
                rfc="MEXA-DEMO-001",
                plan="free",
                tipo="control",
            )
            db.add(organizacion)
            db.flush()

        usuario = db.query(Usuario).filter(Usuario.email == DEMO_EMAIL).first()
        if not usuario:
            usuario = Usuario(
                organizacion_id=organizacion.id,
                nombre="Auxiliar Demo",
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                rol="admin",
                activo="si",
            )
            db.add(usuario)

        formulario = (
            db.query(Formulario)
            .filter(
                Formulario.organizacion_id == organizacion.id,
                Formulario.nombre == "Registro de calificaciones",
            )
            .first()
        )
        if not formulario:
            formulario = Formulario(
                organizacion_id=organizacion.id,
                nombre="Registro de calificaciones",
                descripcion="Demostración configurable para instituciones educativas",
            )
            db.add(formulario)
            db.flush()

        if not formulario.campos:
            definiciones = [
                ("matricula", "Matrícula", "texto", True),
                ("nombre_alumno", "Nombre del alumno", "texto", True),
                ("grupo", "Grupo", "texto", True),
                ("materia", "Materia", "texto", True),
                ("periodo", "Periodo", "seleccion", True),
                ("calificacion", "Calificación", "numero", True),
                ("telefono_tutor", "Teléfono del tutor", "telefono", False),
                ("observaciones", "Observaciones", "parrafo", False),
            ]
            for orden, (clave, etiqueta, tipo, obligatorio) in enumerate(definiciones):
                db.add(
                    CampoFormulario(
                        formulario_id=formulario.id,
                        clave=clave,
                        etiqueta=etiqueta,
                        tipo=tipo,
                        obligatorio=obligatorio,
                        orden=orden,
                        opciones="Primer parcial,Segundo parcial,Tercer parcial"
                        if clave == "periodo"
                        else None,
                    )
                )

        db.commit()
        print("Demo preparada correctamente")
        print(f"Usuario: {DEMO_EMAIL}")
        print(f"Contraseña: {DEMO_PASSWORD}")
        print("Pantalla: http://127.0.0.1:8000/formularios-app")
    finally:
        db.close()


if __name__ == "__main__":
    crear_demo()
