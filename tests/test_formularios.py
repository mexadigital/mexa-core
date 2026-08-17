import unittest

from pydantic import ValidationError

from app.schemas.formulario import CampoCreate


class CampoFormularioTest(unittest.TestCase):
    def test_acepta_clave_simple_y_limpia_opciones(self):
        campo = CampoCreate(
            clave="estado_tramite",
            etiqueta="Estado del trámite",
            tipo="seleccion",
            opciones="Pendiente,  Aprobado, Rechazado",
        )

        self.assertEqual(campo.clave, "estado_tramite")
        self.assertEqual(campo.opciones, "Pendiente,Aprobado,Rechazado")

    def test_rechaza_clave_con_espacios(self):
        with self.assertRaises(ValidationError):
            CampoCreate(
                clave="Nombre del alumno",
                etiqueta="Nombre del alumno",
            )

    def test_calificacion_puede_ser_numero(self):
        campo = CampoCreate(
            clave="calificacion",
            etiqueta="Calificación",
            tipo="numero",
            obligatorio=True,
        )

        self.assertEqual(campo.tipo, "numero")
        self.assertTrue(campo.obligatorio)


if __name__ == "__main__":
    unittest.main()
