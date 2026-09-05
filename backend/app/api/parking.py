from datetime import datetime, timezone
from decimal import Decimal
import math

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import hash_password
from app.db.database import get_db
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.models.parking import ParkingBano, ParkingCliente, ParkingCorte, ParkingMovimiento, ParkingTarifa, ParkingTurno

router = APIRouter(prefix="/parking", tags=["Capital Parking"])
MAX_CAPACIDAD = 23
DEFAULT_TARIFAS = {"auto": Decimal("20.00"), "moto": Decimal("10.00"), "camioneta": Decimal("25.00")}


def now_utc():
    return datetime.now(timezone.utc)


def normalizar_fecha(valor: datetime) -> datetime:
    return valor if valor.tzinfo is not None else valor.replace(tzinfo=timezone.utc)


def org_id(user: Usuario) -> int:
    return user.organizacion_id


def parking_org(db: Session):
    return db.query(Organizacion).filter(Organizacion.nombre == "Capital Parking").first()


def ensure_tarifas(db: Session, organizacion_id: int):
    existentes = {t.tipo_vehiculo.lower(): t for t in db.query(ParkingTarifa).filter(ParkingTarifa.organizacion_id == organizacion_id, ParkingTarifa.activa.is_(True)).all()}
    changed = False
    for tipo, precio in DEFAULT_TARIFAS.items():
        if tipo not in existentes:
            db.add(ParkingTarifa(organizacion_id=organizacion_id, nombre=tipo.capitalize(), tipo_vehiculo=tipo, precio_hora=precio, tolerancia_minutos=5, activa=True))
            changed = True
    if changed:
        db.commit()


def tarifa_activa(db: Session, organizacion_id: int, tipo: str) -> ParkingTarifa:
    ensure_tarifas(db, organizacion_id)
    tarifa = db.query(ParkingTarifa).filter(ParkingTarifa.organizacion_id == organizacion_id, ParkingTarifa.tipo_vehiculo == tipo.lower(), ParkingTarifa.activa.is_(True)).first()
    if not tarifa:
        raise HTTPException(400, "No existe tarifa activa para ese vehículo")
    return tarifa


def turno_abierto(db: Session, organizacion_id: int) -> ParkingTurno | None:
    return db.query(ParkingTurno).filter(ParkingTurno.organizacion_id == organizacion_id, ParkingTurno.estado == "abierto").order_by(ParkingTurno.id.desc()).first()


def calc_importe(entrada: datetime, salida: datetime, tarifa: ParkingTarifa) -> tuple[int, Decimal]:
    entrada = normalizar_fecha(entrada)
    salida = normalizar_fecha(salida)
    minutos = max(0, math.floor((salida - entrada).total_seconds() / 60))
    tolerancia = int(tarifa.tolerancia_minutos or 5)
    horas = 1 if minutos <= 60 + tolerancia else 1 + math.ceil((minutos - (60 + tolerancia)) / 60)
    return minutos, Decimal(tarifa.precio_hora) * horas


def movimiento_dict(m: ParkingMovimiento):
    return {"id": m.id, "placa": m.placa, "tipo_vehiculo": m.tipo_vehiculo, "entrada_at": m.entrada_at, "salida_real_at": m.salida_real_at, "cierre_sistema_at": m.cierre_sistema_at, "minutos_cobrados": m.minutos_cobrados, "importe": float(m.importe or 0), "estado": m.estado, "nota": m.nota, "motivo_sin_estacionarse": m.motivo_sin_estacionarse, "creado_por": m.creado_por}


def agregar_nota(m: ParkingMovimiento, texto: str | None):
    if not texto:
        return
    m.nota = " | ".join([x for x in [m.nota, texto] if x])


class SetupIn(BaseModel):
    nombre: str = "Administrador"
    email: str
    password: str


class AbrirTurnoIn(BaseModel):
    fondo_inicial: float = 0
    nota: str | None = None


class EntradaIn(BaseModel):
    placa: str | None = None
    tipo_vehiculo: str
    nombre_cliente: str | None = None
    telefono: str | None = None
    distinguido: bool = False
    nota: str | None = None
    entrada_real_at: datetime | None = None
    motivo_correccion: str | None = None


class CorregirEntradaIn(BaseModel):
    entrada_real_at: datetime
    motivo_correccion: str


class SalidaIn(BaseModel):
    salida_real_at: datetime | None = None
    motivo_correccion: str | None = None
    nota: str | None = None


class SinEstacionarseIn(BaseModel):
    motivo: str
    nota: str | None = None


class BanoIn(BaseModel):
    tipo_cliente: str = "externo"
    movimiento_id: int | None = None
    nota: str | None = None


class CerrarTurnoIn(BaseModel):
    efectivo_cierre: float | None = None
    nota: str | None = None


@router.get("/setup-status")
def setup_status(db: Session = Depends(get_db)):
    org = parking_org(db)
    if not org:
        return {"configured": False}
    exists = db.query(Usuario).filter(Usuario.organizacion_id == org.id, Usuario.activo == "si").first()
    return {"configured": bool(exists)}


@router.post("/setup")
def setup(data: SetupIn, db: Session = Depends(get_db)):
    org = parking_org(db)
    if org:
        existing = db.query(Usuario).filter(Usuario.organizacion_id == org.id, Usuario.activo == "si").first()
        if existing:
            raise HTTPException(409, "Capital Parking ya tiene un usuario administrador")
    email = data.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Correo inválido")
    if len(data.password) < 8:
        raise HTTPException(400, "La contraseña debe tener al menos 8 caracteres")
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(409, "Ese correo ya está registrado en MEXA")
    if not org:
        org = Organizacion(nombre="Capital Parking", rfc="CAPITAL-PARKING-LOCAL", plan="starter", tipo="control")
        db.add(org)
        db.flush()
    user = Usuario(organizacion_id=org.id, nombre=data.nombre.strip() or "Administrador", email=email, hashed_password=hash_password(data.password), rol="admin", activo="si")
    db.add(user)
    db.commit()
    ensure_tarifas(db, org.id)
    return {"ok": True, "email": email, "message": "Acceso inicial creado. Ya puedes iniciar sesión."}


@router.get("/dashboard")
def dashboard(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    ensure_tarifas(db, oid)
    turno = turno_abierto(db, oid)
    activos = db.query(ParkingMovimiento).filter(ParkingMovimiento.organizacion_id == oid, ParkingMovimiento.estado == "dentro").order_by(ParkingMovimiento.entrada_at.asc()).all()
    historial = db.query(ParkingMovimiento).filter(ParkingMovimiento.organizacion_id == oid, ParkingMovimiento.estado != "dentro").order_by(ParkingMovimiento.id.desc()).limit(100).all()
    tarifas = db.query(ParkingTarifa).filter(ParkingTarifa.organizacion_id == oid, ParkingTarifa.activa.is_(True)).order_by(ParkingTarifa.id.asc()).all()
    banos_turno = db.query(ParkingBano).filter(ParkingBano.turno_id == turno.id).count() if turno else 0
    return {
        "usuario": {"id": current_user.id, "nombre": current_user.nombre, "email": current_user.email, "rol": current_user.rol},
        "capacidad": MAX_CAPACIDAD,
        "ocupados": len(activos),
        "disponibles": max(0, MAX_CAPACIDAD - len(activos)),
        "turno": None if not turno else {"id": turno.id, "operador": turno.nombre_operador, "apertura_at": turno.apertura_at, "fondo_inicial": float(turno.fondo_inicial or 0), "estado": turno.estado},
        "tarifas": [{"id": t.id, "tipo": t.tipo_vehiculo, "precio_hora": float(t.precio_hora), "tolerancia_minutos": t.tolerancia_minutos} for t in tarifas],
        "activos": [movimiento_dict(m) for m in activos],
        "historial": [movimiento_dict(m) for m in historial],
        "banos_turno": banos_turno,
    }


@router.post("/turnos/abrir")
def abrir_turno(data: AbrirTurnoIn, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    actual = turno_abierto(db, oid)
    if actual:
        return {"ok": True, "turno_id": actual.id, "mensaje": "Ya existe un turno abierto"}
    t = ParkingTurno(organizacion_id=oid, usuario_id=current_user.id, nombre_operador=current_user.nombre, fondo_inicial=Decimal(str(data.fondo_inicial or 0)), nota=data.nota, estado="abierto")
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"ok": True, "turno_id": t.id}


@router.post("/entradas")
def entrada(data: EntradaIn, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    turno = turno_abierto(db, oid)
    if not turno:
        raise HTTPException(400, "Primero abre un turno")
    ocupados = db.query(ParkingMovimiento).filter(ParkingMovimiento.organizacion_id == oid, ParkingMovimiento.estado == "dentro").count()
    if ocupados >= MAX_CAPACIDAD:
        raise HTTPException(409, "Estacionamiento lleno")
    tipo = data.tipo_vehiculo.lower().strip()
    if tipo not in DEFAULT_TARIFAS:
        raise HTTPException(400, "Tipo de vehículo inválido")
    tarifa_activa(db, oid, tipo)
    sistema = now_utc()
    entrada_real = normalizar_fecha(data.entrada_real_at) if data.entrada_real_at else sistema
    if entrada_real > sistema:
        raise HTTPException(400, "La hora de entrada no puede estar en el futuro")
    diferencia = abs((sistema - entrada_real).total_seconds()) / 60
    if diferencia > 2 and not (data.motivo_correccion or "").strip():
        raise HTTPException(400, "La corrección de hora de entrada requiere motivo")
    placa = (data.placa or "SIN PLACA").strip().upper()
    cliente = None
    if placa != "SIN PLACA":
        cliente = db.query(ParkingCliente).filter(ParkingCliente.organizacion_id == oid, ParkingCliente.placa == placa, ParkingCliente.activo.is_(True)).first()
    if not cliente and (data.nombre_cliente or data.distinguido or placa != "SIN PLACA"):
        cliente = ParkingCliente(organizacion_id=oid, nombre=data.nombre_cliente, telefono=data.telefono, placa=None if placa == "SIN PLACA" else placa, tipo_vehiculo=tipo, distinguido=data.distinguido, activo=True)
        db.add(cliente)
        db.flush()
    elif cliente:
        if data.nombre_cliente:
            cliente.nombre = data.nombre_cliente
        if data.telefono:
            cliente.telefono = data.telefono
        cliente.distinguido = bool(data.distinguido or cliente.distinguido)
        cliente.tipo_vehiculo = tipo
    m = ParkingMovimiento(organizacion_id=oid, turno_id=turno.id, cliente_id=cliente.id if cliente else None, placa=placa, tipo_vehiculo=tipo, entrada_at=entrada_real, estado="dentro", nota=data.nota, creado_por=current_user.nombre)
    if data.entrada_real_at and diferencia > 2:
        agregar_nota(m, f"Entrada corregida: {data.motivo_correccion.strip()}")
    db.add(m)
    db.commit()
    db.refresh(m)
    return movimiento_dict(m)


@router.post("/movimientos/{movimiento_id}/corregir-entrada")
def corregir_entrada(movimiento_id: int, data: CorregirEntradaIn, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    m = db.query(ParkingMovimiento).filter(ParkingMovimiento.id == movimiento_id, ParkingMovimiento.organizacion_id == oid, ParkingMovimiento.estado == "dentro").first()
    if not m:
        raise HTTPException(404, "Movimiento activo no encontrado")
    motivo = (data.motivo_correccion or "").strip()
    if not motivo:
        raise HTTPException(400, "Escribe el motivo de la corrección")
    entrada_real = normalizar_fecha(data.entrada_real_at)
    sistema = now_utc()
    if entrada_real > sistema:
        raise HTTPException(400, "La hora de entrada no puede estar en el futuro")
    anterior = m.entrada_at
    m.entrada_at = entrada_real
    agregar_nota(m, f"Entrada corregida de {anterior} a {entrada_real}: {motivo}")
    db.commit()
    db.refresh(m)
    return movimiento_dict(m)


@router.post("/movimientos/{movimiento_id}/salida")
def salida(movimiento_id: int, data: SalidaIn, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    m = db.query(ParkingMovimiento).filter(ParkingMovimiento.id == movimiento_id, ParkingMovimiento.organizacion_id == oid).first()
    if not m or m.estado != "dentro":
        raise HTTPException(404, "Movimiento activo no encontrado")
    sistema = now_utc()
    salida_real = normalizar_fecha(data.salida_real_at) if data.salida_real_at else sistema
    if salida_real > sistema:
        raise HTTPException(400, "La hora de salida no puede estar en el futuro")
    if salida_real < normalizar_fecha(m.entrada_at):
        raise HTTPException(400, "La salida no puede ser anterior a la entrada")
    diferencia = abs((sistema - salida_real).total_seconds()) / 60
    if diferencia > 2 and not (data.motivo_correccion or "").strip():
        raise HTTPException(400, "La corrección de hora requiere motivo")
    tarifa = tarifa_activa(db, oid, m.tipo_vehiculo)
    minutos, importe = calc_importe(m.entrada_at, salida_real, tarifa)
    m.salida_real_at = salida_real
    m.cierre_sistema_at = sistema
    m.minutos_cobrados = minutos
    m.importe = importe
    m.estado = "cerrado"
    notas = [x for x in [m.nota, data.nota, f"Salida corregida: {data.motivo_correccion}" if data.motivo_correccion else None] if x]
    m.nota = " | ".join(notas) if notas else None
    db.commit()
    db.refresh(m)
    return movimiento_dict(m)


@router.post("/movimientos/{movimiento_id}/sin-estacionarse")
def sin_estacionarse(movimiento_id: int, data: SinEstacionarseIn, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    m = db.query(ParkingMovimiento).filter(ParkingMovimiento.id == movimiento_id, ParkingMovimiento.organizacion_id == oid, ParkingMovimiento.estado == "dentro").first()
    if not m:
        raise HTTPException(404, "Movimiento activo no encontrado")
    if not data.motivo.strip():
        raise HTTPException(400, "Escribe el motivo")
    ahora = now_utc()
    m.salida_real_at = ahora
    m.cierre_sistema_at = ahora
    m.minutos_cobrados = 0
    m.importe = Decimal("0")
    m.estado = "sin_estacionarse"
    m.motivo_sin_estacionarse = data.motivo.strip()
    m.nota = data.nota or m.nota
    db.commit()
    return movimiento_dict(m)


@router.post("/banos")
def registrar_bano(data: BanoIn, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    turno = turno_abierto(db, oid)
    if not turno:
        raise HTTPException(400, "Primero abre un turno")
    tipo = data.tipo_cliente.lower().strip()
    if tipo not in {"externo", "estacionamiento"}:
        raise HTTPException(400, "Tipo de cliente inválido")
    importe = Decimal("0.00") if tipo == "estacionamiento" else Decimal("5.00")
    if data.movimiento_id:
        mov = db.query(ParkingMovimiento).filter(ParkingMovimiento.id == data.movimiento_id, ParkingMovimiento.organizacion_id == oid).first()
        if not mov:
            raise HTTPException(404, "Vehículo no encontrado")
    b = ParkingBano(organizacion_id=oid, turno_id=turno.id, movimiento_id=data.movimiento_id, tipo_cliente=tipo, importe=importe, nota=data.nota)
    db.add(b)
    db.commit()
    db.refresh(b)
    return {"ok": True, "id": b.id, "importe": float(b.importe), "tipo_cliente": b.tipo_cliente}


@router.post("/turnos/cerrar")
def cerrar_turno(data: CerrarTurnoIn, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    oid = org_id(current_user)
    turno = turno_abierto(db, oid)
    if not turno:
        raise HTTPException(400, "No hay turno abierto")
    activos = db.query(ParkingMovimiento).filter(ParkingMovimiento.organizacion_id == oid, ParkingMovimiento.estado == "dentro").count()
    if activos:
        raise HTTPException(409, f"No puedes cerrar: quedan {activos} vehículo(s) dentro")
    movs = db.query(ParkingMovimiento).filter(ParkingMovimiento.turno_id == turno.id).all()
    banos = db.query(ParkingBano).filter(ParkingBano.turno_id == turno.id).all()
    total_est = sum((Decimal(m.importe or 0) for m in movs), Decimal("0"))
    total_banos = sum((Decimal(b.importe or 0) for b in banos), Decimal("0"))
    total = total_est + total_banos
    corte = db.query(ParkingCorte).filter(ParkingCorte.turno_id == turno.id).first()
    if not corte:
        corte = ParkingCorte(organizacion_id=oid, turno_id=turno.id, total_estacionamiento=total_est, total_banos=total_banos, total_efectivo=total, total_otros=Decimal("0"), total=total, nota=data.nota)
        db.add(corte)
    turno.cierre_at = now_utc()
    turno.efectivo_cierre = None if data.efectivo_cierre is None else Decimal(str(data.efectivo_cierre))
    turno.estado = "cerrado"
    if data.nota:
        turno.nota = data.nota
    db.commit()
    return {"ok": True, "turno_id": turno.id, "total_estacionamiento": float(total_est), "total_banos": float(total_banos), "total": float(total), "efectivo_cierre": None if turno.efectivo_cierre is None else float(turno.efectivo_cierre)}
