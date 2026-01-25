import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "app.db"

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    # Workers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        employee_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)

    # Vales
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_no TEXT NOT NULL,
        employee_name TEXT NOT NULL,
        comment TEXT,
        signed_physical INTEGER NOT NULL DEFAULT 0,
        safety_engineer TEXT,
        photo_path TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVO', -- ACTIVO, PARCIAL, CERRADO
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        closed_at TEXT,
        FOREIGN KEY(employee_no) REFERENCES workers(employee_no)
    );
    """)

    # Vale items (mixed)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vale_id INTEGER NOT NULL,
        kind TEXT NOT NULL, -- HERRAMIENTA, EPP, CONSUMIBLE
        item_name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        origin_location TEXT NOT NULL, -- SC-16, MC-06, etc.
        motive TEXT NOT NULL, -- PRESTAMO, TRASPASO, ENTREGA, CONSUMO
        tool_state TEXT, -- EN_USO, DEVUELTA (solo para HERRAMIENTA)
        returned_at TEXT,
        note TEXT,
        FOREIGN KEY(vale_id) REFERENCES vales(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
