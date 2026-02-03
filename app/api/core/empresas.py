from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import get_conn

router = APIRouter()

class EmpresaCrear(BaseModel):
    nombre: str = Field(min_length=2)
    giro: str = "OTRO"              # OBRA_INDUSTRIAL, TIENDA_ABARROTES, TIENDA_CHINA, etc.
    giro_otro: str | None = None


@router.get("")
def listar_empresas():
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            id,
            name AS nombre,
            industry AS giro,
            industry_other AS giro_otro,
            is_active
        FROM companies
        WHERE is_active = 1
        ORDER BY id;
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("")
def crear_empresa(payload: EmpresaCrear):
    conn = get_conn()
    try:
        try:
            cur = conn.execute(
                """
                INSERT INTO companies (name, industry, industry_other)
                VALUES (?, ?, ?);
                """,
                (payload.nombre, payload.giro, payload.giro_otro)
            )
            conn.commit()
        except Exception:
            raise HTTPException(status_code=409, detail="La empresa ya existe")

        empresa_id = cur.lastrowid
        row = conn.execute("""
            SELECT
                id,
                name AS nombre,
                industry AS giro,
                industry_other AS giro_otro,
                is_active
            FROM companies
            WHERE id = ?;
        """, (empresa_id,)).fetchone()

        return dict(row)
    finally:
        conn.close()

