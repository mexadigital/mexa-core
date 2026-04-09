@router.post("/", response_model=MovimientoOut)
def crear_movimiento(
    data: MovimientoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    producto = db.query(Producto).filter(
        Producto.id == data.producto_id,
        Producto.organizacion_id == user["organizacion_id"]
    ).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad inválida")

    if data.tipo == "salida":
        if producto.cantidad < data.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        producto.cantidad -= data.cantidad

    elif data.tipo == "entrada":
        producto.cantidad += data.cantidad

    else:
        raise HTTPException(status_code=400, detail="Tipo inválido")

    movimiento = Movimiento(
        organizacion_id=user["organizacion_id"],
        producto_id=data.producto_id,
        tipo=data.tipo,
        cantidad=data.cantidad,
        usuario=user["sub"]
    )

    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)

    return movimiento
