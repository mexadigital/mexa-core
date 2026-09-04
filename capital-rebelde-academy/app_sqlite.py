import sqlite3, os, hmac, hashlib, secrets, base64, json, time
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = os.getenv("ACADEMY_DB", "/tmp/capital_rebelde_academy.db")
APP_SECRET = os.getenv("APP_SECRET", "capital-rebelde-dev-secret")
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
        """)

@app.on_event("startup")
def startup(): init_db()

def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150000)
    return base64.urlsafe_b64encode(salt + dk).decode()

def verify_password(password, stored):
    raw = base64.urlsafe_b64decode(stored.encode()); salt, expected = raw[:16], raw[16:]
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 150000)
    return hmac.compare_digest(actual, expected)

def make_token(uid):
    payload = base64.urlsafe_b64encode(json.dumps({"uid":uid,"exp":int(time.time())+604800}).encode()).decode().rstrip("=")
    sig = hmac.new(APP_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return payload+"."+sig

def parse_token(token):
    try:
        payload,sig=token.split(".",1); expected=hmac.new(APP_SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig,expected): raise ValueError
        padded=payload+"="*(-len(payload)%4); data=json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
        if data["exp"]<time.time(): raise ValueError
        return int(data["uid"])
    except Exception: raise HTTPException(401,"Sesión inválida o vencida")

def current_user(auth):
    if not auth or not auth.lower().startswith("bearer "): raise HTTPException(401,"Inicia sesión")
    return parse_token(auth.split(" ",1)[1])

@app.get("/")
def root(): return {"app":"Capital Rebelde Academy","status":"online","version":"0.1.0"}
@app.get("/health")
def health(): return {"ok":True,"app":"Capital Rebelde Academy","version":"0.1.0"}
@app.get("/quotes")
def quotes(): return {"mode":"demo","quotes":[{"symbol":s,"price":p} for s,p in DEMO_PRICES.items()]}

@app.post("/auth/register")
def register(data:AuthIn):
    email=data.email.strip().lower(); name=(data.name or email.split("@")[0]).strip()[:80]
    if len(data.password)<6: raise HTTPException(400,"La contraseña debe tener al menos 6 caracteres")
    try:
        with connect() as con:
            cur=con.execute("INSERT INTO users(email,name,password_hash) VALUES(?,?,?)",(email,name,hash_password(data.password))); uid=cur.lastrowid
            con.execute("INSERT INTO accounts(user_id,cash) VALUES(?,?)",(uid,STARTING_CASH))
    except sqlite3.IntegrityError: raise HTTPException(409,"Ese correo ya está registrado")
    return {"token":make_token(uid),"user":{"id":uid,"email":email,"name":name}}

@app.post("/auth/login")
def login(data:AuthIn):
    with connect() as con: row=con.execute("SELECT * FROM users WHERE email=?",(data.email.strip().lower(),)).fetchone()
    if not row or not verify_password(data.password,row["password_hash"]): raise HTTPException(401,"Correo o contraseña incorrectos")
    return {"token":make_token(row["id"]),"user":{"id":row["id"],"email":row["email"],"name":row["name"]}}

@app.get("/me")
def me(authorization:str|None=Header(default=None)):
    uid=current_user(authorization)
    with connect() as con: row=con.execute("SELECT id,email,name,created_at FROM users WHERE id=?",(uid,)).fetchone()
    if not row: raise HTTPException(404,"Usuario no encontrado")
    return dict(row)

@app.get("/portfolio")
def portfolio(authorization:str|None=Header(default=None)):
    uid=current_user(authorization)
    with connect() as con:
        cash=float(con.execute("SELECT cash FROM accounts WHERE user_id=?",(uid,)).fetchone()[0])
        positions=con.execute("SELECT * FROM positions WHERE user_id=? AND quantity>0 ORDER BY symbol",(uid,)).fetchall()
        trades=con.execute("SELECT symbol,side,quantity,price,created_at FROM trades WHERE user_id=? ORDER BY id DESC LIMIT 30",(uid,)).fetchall()
    out=[]; mv=0
    for r in positions:
        p=DEMO_PRICES.get(r["symbol"],r["avg_price"]); value=r["quantity"]*p; mv+=value
        out.append({"symbol":r["symbol"],"quantity":r["quantity"],"avg_price":r["avg_price"],"price":p,"value":value,"pnl":value-r["quantity"]*r["avg_price"]})
    return {"cash":cash,"market_value":mv,"equity":cash+mv,"positions":out,"trades":[dict(r) for r in trades],"mode":"demo"}

@app.post("/trade")
def trade(data:TradeIn,authorization:str|None=Header(default=None)):
    uid=current_user(authorization); symbol=data.symbol.upper().strip(); side=data.side.upper().strip(); qty=float(data.quantity)
    if symbol not in DEMO_PRICES: raise HTTPException(400,"Instrumento no disponible en esta V1")
    if side not in {"BUY","SELL"} or qty<=0: raise HTTPException(400,"Orden inválida")
    price=DEMO_PRICES[symbol]
    with connect() as con:
        cash=float(con.execute("SELECT cash FROM accounts WHERE user_id=?",(uid,)).fetchone()[0])
        row=con.execute("SELECT quantity,avg_price FROM positions WHERE user_id=? AND symbol=?",(uid,symbol)).fetchone(); oldq,olda=(row[0],row[1]) if row else (0.0,0.0)
        if side=="BUY":
            cost=qty*price
            if cost>cash: raise HTTPException(400,"Saldo insuficiente")
            newq=oldq+qty; newa=((oldq*olda)+cost)/newq; cash-=cost
        else:
            if qty>oldq: raise HTTPException(400,"No tienes suficientes títulos")
            newq=oldq-qty; newa=olda if newq>0 else 0; cash+=qty*price
        con.execute("UPDATE accounts SET cash=? WHERE user_id=?",(cash,uid))
        con.execute("INSERT INTO positions(user_id,symbol,quantity,avg_price) VALUES(?,?,?,?) ON CONFLICT(user_id,symbol) DO UPDATE SET quantity=excluded.quantity,avg_price=excluded.avg_price",(uid,symbol,newq,newa))
        con.execute("INSERT INTO trades(user_id,symbol,side,quantity,price) VALUES(?,?,?,?,?)",(uid,symbol,side,qty,price))
    return {"ok":True,"message":f"{side} {qty:g} {symbol} @ ${price:,.2f} (demo)"}
