
import os
import sqlite3
from pathlib import Path

# =========================
# Database path (local / cloud)
# =========================
# Local  : data/app.db
# Render : /var/data/app.db  (with Persistent Disk + DB_DIR=/var/data)
DB_DIR = Path(os.getenv("DB_DIR", "data"))
DB_PATH = DB_DIR / "app.db"


# =========================
# Connection
# =========================
def get_conn() -> sqlite3.Connection:
    """
    Returns a SQLite connection.
    Creates the DB directory automatically if it doesn't exist.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# =========================
# Init DB (tables)
# =========================
def init_db() -> None:
    """
    Creates all tables if they don't exist.
    Safe to run multiple times.
    """
    conn = get_conn()
    cur = conn.cursor()

    # -------------------------------------------------
    # WORKERS (ICA / employees)
    # -------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        employee_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """)

    # -------------------------------------------------
    # VALES (ICA legacy flow)
    # -------------------------------------------------
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

    # -------------------------------------------------
    # VALE ITEMS (mixed: herramienta / epp / consumible)
    # -------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vale_id INTEGER NOT NULL,
        kind TEXT NOT NULL, -- HERRAMIENTA, EPP, CONSUMIBLE
        item_name TEXT NOT NULL,
        qty INTEGER NOT NULL,
        origin_location TEXT NOT NULL, -- SC-16, M-06, etc.
        motive TEXT NOT NULL, -- PRESTAMO, TRASPASO, ENTREGA, CONSUMO
        tool_state TEXT, -- EN_USO, DEVUELTA (solo
