class ProductoBase(BaseModel):
    organizacion_id: int   # 👈 obligatorio ahora

    nombre: str
    codigo: Optional[str] = None
    tipo: str = "consumible"
    cantidad: int = 0
    ubicacion: Optional[str] = None
    precio: Optional[float] = None
