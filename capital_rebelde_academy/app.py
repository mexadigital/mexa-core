import sqlite3, os, hmac, hashlib, secrets, base64, json, time
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = os.getenv("ACADEMY_DB", "/tmp/capital_rebelde_academy.db")
APP_SECRET = os.getenv("APP_SECRET", "capital-rebelde-dev-secret")
STARTING_CASH = 100000.0
DEMO_PRICES = {"SPY": 650.00, "QQQ": 590.00}

app = FastAPI(title="Capital Rebelde Academy API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

class AuthIn(BaseModel):
    email: str
    password: str
    name: str | None = None

class OrderIn(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str = "MARKET"
    limit_price: float | None = None
    stop_price: float | None = None


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT UNIQUE NOT NULL,name TEXT NOT NULL,password_hash TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS accounts(user_id INTEGER PRIMARY KEY,cash REAL NOT NULL DEFAULT 100000,FOREIGN KEY(user_id) REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS positions(user_id INTEGER NOT NULL,symbol TEXT NOT NULL,quantity REAL NOT NULL DEFAULT 0,avg_price REAL NOT NULL DEFAULT 0,PRIMARY KEY(user_id,symbol));
        CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,symbol TEXT NOT NULL,side TEXT NOT NULL,quantity REAL NOT NULL,price REAL NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,symbol TEXT NOT NULL,side TEXT NOT NULL,quantity REAL NOT NULL,order_type TEXT NOT NULL,limit_price REAL,stop_price REAL,status TEXT NOT NULL DEFAULT 'PENDING',filled_price REAL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,filled_at TEXT);
        """)

@app.on_event("startup")
def startup():
    init_db()


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150000)
    return base64.urlsafe_b64encode(salt + dk).decode()


def verify_password(password, stored):
    raw = base64.urlsafe_b64decode(stored.encode())
    salt, expected = raw[:16], raw[16:]
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150000)
    return hmac.compare_digest(actual, expected)


def make_token(uid):
    payload = base64.urlsafe_b64encode(json.dumps({"uid": uid, "exp": int(time.time()) + 604800}).encode()).decode().rstrip("=")
    sig = hmac.new(APP_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return payload + "." + sig


def parse_token(token):
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
        raise HTTPException(401, "Sesión inválida o vencida")


def current_user(auth):
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(401, "Inicia sesión")
    return parse_token(auth.split(" ", 1)[1])


def execute_fill(con, uid, symbol, side, qty, price):
    cash = float(con.execute("SELECT cash FROM accounts WHERE user_id=?", (uid,)).fetchone()[0])
    row = con.execute("SELECT quantity,avg_price FROM positions WHERE user_id=? AND symbol=?", (uid, symbol)).fetchone()
    oldq, olda = (float(row[0]), float(row[1])) if row else (0.0, 0.0)
    if side == "BUY":
        cost = qty * price
        if cost > cash:
            raise HTTPException(400, "Saldo insuficiente")
        newq = oldq + qty
        newa = ((oldq * olda) + cost) / newq
        cash -= cost
    else:
        if qty > oldq:
            raise HTTPException(400, "No tienes suficientes títulos")
        newq = oldq - qty
        newa = olda if newq > 0 else 0
        cash += qty * price
    con.execute("UPDATE accounts SET cash=? WHERE user_id=?", (cash, uid))
    con.execute("INSERT INTO positions(user_id,symbol,quantity,avg_price) VALUES(?,?,?,?) ON CONFLICT(user_id,symbol) DO UPDATE SET quantity=excluded.quantity,avg_price=excluded.avg_price", (uid, symbol, newq, newa))
    con.execute("INSERT INTO trades(user_id,symbol,side,quantity,price) VALUES(?,?,?,?,?)", (uid, symbol, side, qty, price))


def should_fill(order_type, side, market, limit_price, stop_price):
    if order_type == "MARKET": return True
    if order_type == "LIMIT":
        return market <= limit_price if side == "BUY" else market >= limit_price
    if order_type == "STOP":
        return market >= stop_price if side == "BUY" else market <= stop_price
    return False


def process_pending_for_user(uid):
    with connect() as con:
        rows = con.execute("SELECT * FROM orders WHERE user_id=? AND status='PENDING' ORDER BY id", (uid,)).fetchall()
        for o in rows:
            market = DEMO_PRICES.get(o["symbol"])
            if market is None:
                continue
            if should_fill(o["order_type"], o["side"], market, o["limit_price"], o["stop_price"]):
                try:
                    execute_fill(con, uid, o["symbol"], o["side"], float(o["quantity"]), float(market))
                    con.execute("UPDATE orders SET status='FILLED',filled_price=?,filled_at=CURRENT_TIMESTAMP WHERE id=?", (market, o["id"]))
                except HTTPException:
                    con.execute("UPDATE orders SET status='REJECTED',filled_at=CURRENT_TIMESTAMP WHERE id=?", (o["id"],))

@app.get("/")
def root():
    return {"app": "Capital Rebelde Academy", "status": "online", "version": "0.2.0"}

@app.get("/health")
def health():
    return {"ok": True, "app": "Capital Rebelde Academy", "version": "0.2.0"}

@app.get("/quotes")
def quotes():
    return {"mode": "demo", "quotes": [{"symbol": s, "price": p} for s, p in DEMO_PRICES.items()]}

@app.post("/auth/register")
def register(data: AuthIn):
    email = data.email.strip().lower()
    name = (data.name or email.split("@")[0]).strip()[:80]
    if len(data.password) < 6:
        raise HTTPException(400, "La contraseña debe tener al menos 6 caracteres")
    try:
        with connect() as con:
            cur = con.execute("INSERT INTO users(email,name,password_hash) VALUES(?,?,?)", (email, name, hash_password(data.password)))
            uid = cur.lastrowid
            con.execute("INSERT INTO accounts(user_id,cash) VALUES(?,?)", (uid, STARTING_CASH))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Ese correo ya está registrado")
    return {"token": make_token(uid), "user": {"id": uid, "email": email, "name": name}}

@app.post("/auth/login")
def login(data: AuthIn):
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE email=?", (data.email.strip().lower(),)).fetchone()
    if not row or not verify_password(data.password, row["password_hash"]):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {"token": make_token(row["id"]), "user": {"id": row["id"], "email": row["email"], "name": row["name"]}}

@app.get("/portfolio")
def portfolio(authorization: str | None = Header(default=None)):
    uid = current_user(authorization)
    process_pending_for_user(uid)
    with connect() as con:
        cash = float(con.execute("SELECT cash FROM accounts WHERE user_id=?", (uid,)).fetchone()[0])
        positions = con.execute("SELECT * FROM positions WHERE user_id=? AND quantity>0 ORDER BY symbol", (uid,)).fetchall()
        trades = con.execute("SELECT symbol,side,quantity,price,created_at FROM trades WHERE user_id=? ORDER BY id DESC LIMIT 30", (uid,)).fetchall()
        orders = con.execute("SELECT id,symbol,side,quantity,order_type,limit_price,stop_price,status,filled_price,created_at,filled_at FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 50", (uid,)).fetchall()
    out = []
    market_value = 0.0
    for r in positions:
        price = DEMO_PRICES.get(r["symbol"], r["avg_price"])
        value = r["quantity"] * price
        market_value += value
        out.append({"symbol": r["symbol"], "quantity": r["quantity"], "avg_price": r["avg_price"], "price": price, "value": value, "pnl": value - r["quantity"] * r["avg_price"]})
    return {"cash": cash, "market_value": market_value, "equity": cash + market_value, "positions": out, "trades": [dict(r) for r in trades], "orders": [dict(r) for r in orders], "mode": "demo"}

@app.post("/orders")
def place_order(data: OrderIn, authorization: str | None = Header(default=None)):
    uid = current_user(authorization)
    symbol = data.symbol.upper().strip()
    side = data.side.upper().strip()
    order_type = data.order_type.upper().strip()
    qty = float(data.quantity)
    if symbol not in DEMO_PRICES:
        raise HTTPException(400, "Instrumento no disponible en esta V1")
    if side not in {"BUY", "SELL"} or qty <= 0:
        raise HTTPException(400, "Orden inválida")
    if order_type not in {"MARKET", "LIMIT", "STOP"}:
        raise HTTPException(400, "Tipo de orden inválido")
    if order_type == "LIMIT" and (data.limit_price is None or data.limit_price <= 0):
        raise HTTPException(400, "Indica un precio límite válido")
    if order_type == "STOP" and (data.stop_price is None or data.stop_price <= 0):
        raise HTTPException(400, "Indica un precio stop válido")
    market = DEMO_PRICES[symbol]
    with connect() as con:
        if side == "SELL":
            row = con.execute("SELECT quantity FROM positions WHERE user_id=? AND symbol=?", (uid, symbol)).fetchone()
            held = float(row[0]) if row else 0.0
            if qty > held:
                raise HTTPException(400, "No tienes suficientes títulos")
        if order_type == "MARKET":
            execute_fill(con, uid, symbol, side, qty, market)
            cur = con.execute("INSERT INTO orders(user_id,symbol,side,quantity,order_type,status,filled_price,filled_at) VALUES(?,?,?,?,?,'FILLED',?,CURRENT_TIMESTAMP)", (uid, symbol, side, qty, order_type, market))
            return {"ok": True, "order_id": cur.lastrowid, "status": "FILLED", "message": f"Orden MARKET ejecutada: {side} {qty:g} {symbol} @ ${market:,.2f} demo"}
        cur = con.execute("INSERT INTO orders(user_id,symbol,side,quantity,order_type,limit_price,stop_price,status) VALUES(?,?,?,?,?,?,?,'PENDING')", (uid, symbol, side, qty, order_type, data.limit_price, data.stop_price))
        oid = cur.lastrowid
    process_pending_for_user(uid)
    with connect() as con:
        row = con.execute("SELECT status,filled_price FROM orders WHERE id=?", (oid,)).fetchone()
    if row["status"] == "FILLED":
        return {"ok": True, "order_id": oid, "status": "FILLED", "message": f"Orden {order_type} ejecutada @ ${row['filled_price']:,.2f} demo"}
    return {"ok": True, "order_id": oid, "status": "PENDING", "message": f"Orden {order_type} enviada y pendiente"}

@app.delete("/orders/{order_id}")
def cancel_order(order_id: int, authorization: str | None = Header(default=None)):
    uid = current_user(authorization)
    with connect() as con:
        row = con.execute("SELECT status FROM orders WHERE id=? AND user_id=?", (order_id, uid)).fetchone()
        if not row:
            raise HTTPException(404, "Orden no encontrada")
        if row["status"] != "PENDING":
            raise HTTPException(400, "Solo puedes cancelar órdenes pendientes")
        con.execute("UPDATE orders SET status='CANCELLED' WHERE id=?", (order_id,))
    return {"ok": True, "message": "Orden cancelada"}
