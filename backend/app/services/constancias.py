from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException


ESTADOS_FINALES = {"ENTREGADA", "CANCELADA"}


def nuevo_token_verificacion() -> str:
    return uuid4().hex


def construir_folio(organizacion_id: int, consecutivo: int, ahora=None) -> str:
    ahora = ahora or datetime.now(timezone.utc)
    return f"MEXA-{organizacion_id:04d}-{ahora:%Y%m}-{consecutivo:06d}"


def validar_transicion(estado_actual: str, estado_nuevo: str) -> None:
    permitidas = {
        "PAGO_PENDIENTE": {"SOLICITADA", "CANCELADA"},
        "SOLICITADA": {"EN_REVISION", "CANCELADA"},
        "EN_REVISION": {"AUTORIZADA", "CANCELADA"},
        "AUTORIZADA": {"LISTA_PARA_RECOGER", "ENTREGADA", "CANCELADA"},
        "LISTA_PARA_RECOGER": {"ENTREGADA", "CANCELADA"},
        "ENTREGADA": set(),
        "CANCELADA": set(),
    }
    if estado_nuevo not in permitidas.get(estado_actual, set()):
        raise HTTPException(
            status_code=409,
            detail=f"No se puede cambiar de {estado_actual} a {estado_nuevo}",
        )


def nombre_protegido(nombre: str) -> str:
    partes = [parte for parte in nombre.split() if parte]
    return " ".join(f"{parte[0]}***" for parte in partes)
