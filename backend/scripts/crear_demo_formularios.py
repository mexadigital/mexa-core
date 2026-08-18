"""Crea datos ficticios para probar MEXA Formularios y Escolar.

Las credenciales se leen del entorno para no guardar contraseñas en GitHub:
    MEXA_BOOTSTRAP_EMAIL
    MEXA_BOOTSTRAP_PASSWORD
"""

import os

from app.core.security import hash_password
from app.db.base import Base
from app.db.database import SessionLocal, engine
from app.models.formulario import CampoFormulario, Formulario
from app.models.escolar import Alumno, GrupoEscolar
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario


def crear_demo() -> None:
    demo_email = os.getenv("MEXA_BOOTSTRAP_EMAIL", "").strip().lower()
    demo_password = os.getenv("MEXA_BOOTSTRAP_PASSWORD", "")
    if not demo_email or not demo_password:
        print("Demo omitida: faltan MEXA_BOOTSTRAP_EMAIL y/o MEXA_BOOTSTRAP_PASSWORD")
        return
    if len(demo_password) < 12:
        raise ValueError("MEXA_BOOTSTRAP_PASSWORD debe tener al menos 12 caracteres")

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

        usuario = db.query(Usuario).filter(Usuario.email == demo_email).first()
        if not usuario:
            usuario = Usuario(
                organizacion_id=organizacion.id,
                nombre="Auxiliar Demo",
                email=demo_email,
                hashed_password=hash_password(demo_password),
                rol="admin",
                activo="si",
            )
            db.add(usuario)

        grupo = (
            db.query(GrupoEscolar)
            .filter(
                GrupoEscolar.organizacion_id == organizacion.id,
                GrupoEscolar.nombre == "3° A",
                GrupoEscolar.ciclo_escolar == "2026-2027",
            )
            .first()
        )
        if not grupo:
            grupo = GrupoEscolar(
                organizacion_id=organizacion.id,
                nombre="3° A",
                grado="Tercero",
                ciclo_escolar="2026-2027",
            )
            db.add(grupo)
            db.flush()

        alumno = (
            db.query(Alumno)
            .filter(
                Alumno.organizacion_id == organizacion.id,
                Alumno.matricula == "MEXA-DEMO-001",
            )
            .first()
        )
        if not alumno:
            db.add(
                Alumno(
                    organizacion_id=organizacion.id,
                    grupo_id=grupo.id,
                    matricula="MEXA-DEMO-001",
                    nombre_completo="ALUMNO DE DEMOSTRACIÓN",
                    telefono_tutor=None,
                )
            )

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
        print(f"Usuario administrador preparado: {demo_email}")
        print("Contraseña leída de forma privada desde Render")
        print("Pantalla: http://127.0.0.1:8000/formularios-app")
    finally:
        db.close()


if __name__ == "__main__":
    crear_demo()
