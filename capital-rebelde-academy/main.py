import os, hmac, hashlib, secrets, base64, json, time
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg

APP_SECRET = os.getenv("APP_SECRET", "change-me")
DATABASE_URL = os.getenv("DATABASE_URL")
STARTING_CASH = 100000.0
DEMO_PRICES = {"SPY": 650.00, "QQQ": 590.00}

app = FastAPI(title="Capital Rebelde Academy API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

class AuthIn(BaseModel):
    email: str
    password: str
    name: str | None = None

class TradeIn(BaseModel):
    symbol: str
    side: str
    quantity: float


def db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(DATABASE_URL)


def init_db():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    cash NUMERIC(18,2) NOT NULL DEFAULT 100000.00
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    symbol TEXT NOT NULL,
                    quantity NUMERIC(18,6) NOT NULL DEFAULT 0,
                    avg_price NUMERIC(18,6) NOT NULL DEFAULT 0,
                    PRIMARY KEY(user_id, symbol)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity NUMERIC(18,6) NOT NULL,
                    price NUMERIC(18,6) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
        conn.commit()

@app.on_event("startup")
def startup():
    init_db()


def hash_password(password: str, salt: bytes | None = None):
    salt = salt or secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150000)
    return base64.urlsafe_b64encode(salt + dk).decode()


def verify_password(password: str, stored: str):
    raw = base64.urlsafe_b64decode(stored.encode())
    salt, expected = raw[:16], raw[16:]
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150000)
    return hmac.compare_digest(actual, expected)


def make_token(user_id: int):
    payload = base64.urlsafe_b64encode(json.dumps({"uid": user_id, "exp": int(time.time()) + 86400 * 7}).encode()).decode().rstrip("=")
    sig = hmac.new(APP_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return payload + "." + sig


def parse_token(token: str):
    try:
        payload, sig = token.split(".", 1)
        expected = hmac.new(APP_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise ValueError
        padded = payload + "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
        if data["exp"] < time.time():
            raise ValueError
        return int(data["uid"])
    except Exception:
        raise HTTPException(status_code=401, detail="Sesión inválida o vencida")


def current_user(authorization: str | None):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Inicia sesión")
    return parse_token(authorization.split(" ", 1)[1])

@app.get("/health")
def health():
    return {"ok": True, "app": "Capital Rebelde Academy", "version": "0.1.0"}

@app.get("/quotes")
def quotes():
    return {"mode": "demo", "quotes": [{"symbol": s, "price": p} for s, p in DEMO_PRICES.items()]}

@app.post("/auth/register")
def register(data: AuthIn):
    email = data.email.strip().lower()
    if len(data.password) < 6:
        raise HTTPException(400, "La contraseña debe tener al menos 6 caracteres")
    name = (data.name or email.split("@")[0]).strip()[:80]
    try:
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users(email,name,password_hash) VALUES(%s,%s,%s) RETURNING id", (email, name, hash_password(data.password)))
                uid = cur.fetchone()[0]
                cur.execute("INSERT INTO accounts(user_id,cash) VALUES(%s,%s)", (uid, STARTING_CASH))
            conn.commit()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, "Ese correo ya está registrado")
    return {"token": make_token(uid), "user": {"id": uid, "email": email, "name": name}}

@app.post("/auth/login")
def login(data: AuthIn):
    email = data.email.strip().lower()
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,email,name,password_hash FROM users WHERE email=%s", (email,))
            row = cur.fetchone()
    if not row or not verify_password(data.password, row[3]):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {"token": make_token(row[0]), "user": {"id": row[0], "email": row[1], "name": row[2]}}

@app.get("/me")
def me(authorization: str | None = Header(default=None)):
    uid = current_user(authorization)
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,email,name,created_at FROM users WHERE id=%s", (uid,))
            u = cur.fetchone()
    return {"id": u[0], "email": u[1], "name": u[2], "created_at": u[3]}

@app.get("/portfolio")
def portfolio(authorization: str | None = Header(default=None)):
    uid = current_user(authorization)
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT cash FROM accounts WHERE user_id=%s", (uid,))
            cash = float(cur.fetchone()[0])
            cur.execute("SELECT symbol,quantity,avg_price FROM positions WHERE user_id=%s AND quantity > 0 ORDER BY symbol", (uid,))
            positions = cur.fetchall()
            cur.execute("SELECT symbol,side,quantity,price,created_at FROM trades WHERE user_id=%s ORDER BY id DESC LIMIT 30", (uid,))
            trades = cur.fetchall()
    pos = []
    market_value = 0.0
    for symbol, qty, avg in positions:
        qty, avg = float(qty), float(avg)
        price = DEMO_PRICES.get(symbol, avg)
        value = qty * price
        market_value += value
        pos.append({"symbol": symbol, "quantity": qty, "avg_price": avg, "price": price, "value": value, "pnl": value - qty * avg})
    return {"cash": cash, "market_value": market_value, "equity": cash + market_value, "positions": pos,
            "trades": [{"symbol":r[0],"side":r[1],"quantity":float(r[2]),"price":float(r[3]),"created_at":r[4]} for r in trades], "mode":"demo"}

@app.post("/trade")
def trade(data: TradeIn, authorization: str | None = Header(default=None)):
    uid = current_user(authorization)
    symbol = data.symbol.upper().strip()
    side = data.side.upper().strip()
    qty = float(data.quantity)
    if symbol not in DEMO_PRICES:
        raise HTTPException(400, "Instrumento no disponible en esta V1")
    if side not in {"BUY", "SELL"} or qty <= 0:
        raise HTTPException(400, "Orden inválida")
    price = DEMO_PRICES[symbol]
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT cash FROM accounts WHERE user_id=%s FOR UPDATE", (uid,))
            cash = float(cur.fetchone()[0])
            cur.execute("SELECT quantity,avg_price FROM positions WHERE user_id=%s AND symbol=%s FOR UPDATE", (uid, symbol))
            row = cur.fetchone()
            old_qty, old_avg = (float(row[0]), float(row[1])) if row else (0.0, 0.0)
            if side == "BUY":
                cost = qty * price
                if cost > cash + 1e-9:
                    raise HTTPException(400, "Saldo insuficiente")
                new_qty = old_qty + qty
                new_avg = ((old_qty * old_avg) + cost) / new_qty
                cash -= cost
            else:
                if qty > old_qty + 1e-9:
                    raise HTTPException(400, "No tienes suficientes títulos")
                new_qty = old_qty - qty
                new_avg = old_avg if new_qty > 0 else 0.0
                cash += qty * price
            cur.execute("UPDATE accounts SET cash=%s WHERE user_id=%s", (cash, uid))
            cur.execute("INSERT INTO positions(user_id,symbol,quantity,avg_price) VALUES(%s,%s,%s,%s) ON CONFLICT(user_id,symbol) DO UPDATE SET quantity=EXCLUDED.quantity,avg_price=EXCLUDED.avg_price", (uid, symbol, new_qty, new_avg))
            cur.execute("INSERT INTO trades(user_id,symbol,side,quantity,price) VALUES(%s,%s,%s,%s,%s)", (uid, symbol, side, qty, price))
        conn.commit()
    return {"ok": True, "message": f"{side} {qty:g} {symbol} @ ${price:,.2f} (demo)"}
