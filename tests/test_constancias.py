import unittest
from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_current_user
from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.models.escolar import Alumno, GrupoEscolar, SolicitudConstancia
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.services.constancias import (
    construir_folio,
    nombre_protegido,
    validar_transicion,
)


class ConstanciasTest(unittest.TestCase):
    def test_construye_folio_identificable(self):
        folio = construir_folio(
            organizacion_id=12,
            consecutivo=35,
            ahora=datetime(2026, 8, 18, tzinfo=timezone.utc),
        )
        self.assertEqual(folio, "MEXA-0012-202608-000035")

    def test_flujo_exige_revision_antes_de_autorizar(self):
        validar_transicion("SOLICITADA", "EN_REVISION")
        validar_transicion("EN_REVISION", "AUTORIZADA")
        with self.assertRaises(HTTPException):
            validar_transicion("SOLICITADA", "AUTORIZADA")

    def test_no_permite_modificar_documento_entregado(self):
        with self.assertRaises(HTTPException):
            validar_transicion("ENTREGADA", "CANCELADA")

    def test_protege_nombre_en_consulta_publica(self):
        self.assertEqual(nombre_protegido("ANA LOPEZ DIAZ"), "A*** L*** D***")


class FlujoConstanciaApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.Session = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(cls.engine)
        db = cls.Session()
        organizacion = Organizacion(
            nombre="Colegio Demostración",
            rfc="DEM010101AAA",
            tipo="escolar",
        )
        db.add(organizacion)
        db.flush()
        cls.usuario = Usuario(
            organizacion_id=organizacion.id,
            nombre="Directora Demo",
            email="direccion@example.test",
            hashed_password="no-se-usa",
            rol="admin",
            activo="si",
        )
        db.add(cls.usuario)
        db.flush()
        grupo = GrupoEscolar(
            organizacion_id=organizacion.id,
            nombre="3° A",
            grado="Tercero",
            ciclo_escolar="2026-2027",
        )
        db.add(grupo)
        db.flush()
        alumno = Alumno(
            organizacion_id=organizacion.id,
            grupo_id=grupo.id,
            matricula="CSC-0001",
            nombre_completo="ALUMNA DE PRUEBA",
            telefono_tutor="5219510000000",
        )
        db.add(alumno)
        db.commit()
        cls.alumno_id = alumno.id
        cls.usuario_id = cls.usuario.id
        db.close()

        def override_db():
            session = cls.Session()
            try:
                yield session
            finally:
                session.close()

        def override_user():
            session = cls.Session()
            try:
                return session.get(Usuario, cls.usuario_id)
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = override_user
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        cls.engine.dispose()

    def test_configuracion_institucional_se_guarda(self):
        respuesta = self.client.patch(
            "/escolar/configuracion",
            json={
                "nombre": "Colegio Demostración",
                "cct": "20PES0000X",
                "domicilio": "Salina Cruz, Oaxaca",
                "telefono": "9710000000",
                "correo_institucional": "control@example.test",
                "logo_url": None,
                "firmante_nombre": "DIRECTORA DE PRUEBA",
                "firmante_cargo": "Directora General",
                "ciclo_escolar_actual": "2026-2027",
                "color_primario": "#173A5E",
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["cct"], "20PES0000X")

        consulta = self.client.get("/escolar/configuracion")
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json()["firmante_cargo"], "Directora General")

    def test_padron_permite_alta_cambio_de_grupo_y_baja_reversible(self):
        grupo = self.client.post(
            "/escolar/grupos",
            json={
                "nombre": "4° B",
                "grado": "Cuarto",
                "ciclo_escolar": "2026-2027",
            },
        )
        self.assertEqual(grupo.status_code, 201)

        alumno = self.client.post(
            "/escolar/alumnos",
            json={
                "grupo_id": grupo.json()["id"],
                "matricula": "CSC-0002",
                "nombre_completo": "ALUMNO DE PADRON",
                "nombre_tutor": "TUTOR DE PRUEBA",
                "telefono_tutor": "9710000001",
            },
        )
        self.assertEqual(alumno.status_code, 201)
        self.assertEqual(alumno.json()["nombre_tutor"], "TUTOR DE PRUEBA")

        actualizado = self.client.patch(
            f"/escolar/alumnos/{alumno.json()['id']}",
            json={"telefono_tutor": "9710000099", "estado": "inactivo"},
        )
        self.assertEqual(actualizado.status_code, 200)
        self.assertEqual(actualizado.json()["estado"], "inactivo")

        inactivos = self.client.get("/escolar/alumnos?estado=inactivo")
        self.assertEqual(inactivos.status_code, 200)
        self.assertIn("CSC-0002", [item["matricula"] for item in inactivos.json()])

        reactivado = self.client.patch(
            f"/escolar/alumnos/{alumno.json()['id']}",
            json={"estado": "activo"},
        )
        self.assertEqual(reactivado.json()["estado"], "activo")

    def test_solicitud_no_se_emite_solo_por_pagar(self):
        creada = self.client.post(
            "/escolar/constancias",
            json={
                "alumno_id": self.alumno_id,
                "motivo": "Beca",
                "medio_entrega": "digital",
                "monto": 100,
            },
        )
        self.assertEqual(creada.status_code, 201)
        solicitud = creada.json()
        self.assertEqual(solicitud["estado"], "PAGO_PENDIENTE")

        pagada = self.client.patch(
            f"/escolar/constancias/{solicitud['id']}/pago",
            json={"estado_pago": "PAGADO", "referencia_pago": "CAJA-01"},
        )
        self.assertEqual(pagada.status_code, 200)
        self.assertEqual(pagada.json()["estado"], "SOLICITADA")

        documento_antes = self.client.get(
            f"/escolar/constancias/{solicitud['id']}/documento"
        )
        self.assertEqual(documento_antes.status_code, 409)

        revisada = self.client.post(
            f"/escolar/constancias/{solicitud['id']}/revisar"
        )
        self.assertEqual(revisada.json()["estado"], "EN_REVISION")
        autorizada = self.client.post(
            f"/escolar/constancias/{solicitud['id']}/autorizar"
        )
        self.assertEqual(autorizada.json()["estado"], "AUTORIZADA")

        documento = self.client.get(
            f"/escolar/constancias/{solicitud['id']}/documento"
        )
        self.assertEqual(documento.status_code, 200)
        self.assertIn("CONSTANCIA DE ESTUDIOS", documento.text)
        self.assertIn("ALUMNA DE PRUEBA", documento.text)
        self.assertIn("20PES0000X", documento.text)
        self.assertIn("DIRECTORA DE PRUEBA", documento.text)
        self.assertIn("Directora General", documento.text)

        session = self.Session()
        token = session.execute(
            select(SolicitudConstancia.token_verificacion)
        ).scalar_one()
        session.close()
        verificacion = self.client.get(f"/escolar/verificar/{token}")
        self.assertEqual(verificacion.status_code, 200)
        self.assertIn("Documento válido", verificacion.text)
        self.assertIn("A*** D*** P***", verificacion.text)

        datos = self.client.get(f"/escolar/verificar/{token}/datos")
        self.assertEqual(datos.status_code, 200)
        self.assertTrue(datos.json()["valida"])
        self.assertEqual(datos.json()["cct"], "20PES0000X")


if __name__ == "__main__":
    unittest.main()
