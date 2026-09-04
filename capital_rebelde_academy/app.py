import sqlite3, os, hmac, hashlib, secrets, base64, json, time, urllib.request, urllib.parse
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH=os.getenv('ACADEMY_DB','/tmp/capital_rebelde_academy.db')
APP_SECRET=os.getenv('APP_SECRET','capital-rebelde-dev-secret')
STARTING_CASH=100000.0
SYMBOLS=['SPY','QQQ','AAPL','MSFT','NVDA','TSLA','AVGO','AMZN','META','GOOGL','AMD','SMCI','SOXX','TQQQ','SOXL']
FALLBACK={'SPY':650.0,'QQQ':590.0,'AAPL':230.0,'MSFT':500.0,'NVDA':180.0,'TSLA':340.0,'AVGO':360.0,'AMZN':220.0,'META':750.0,'GOOGL':220.0,'AMD':180.0,'SMCI':50.0,'SOXX':300.0,'TQQQ':100.0,'SOXL':40.0}
CACHE={}
CACHE_TTL=20

app=FastAPI(title='Capital Rebelde Academy API',version='0.3.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['*'],allow_headers=['*'])

class AuthIn(BaseModel):
    email:str; password:str; name:str|None=None
class OrderIn(BaseModel):
    symbol:str; side:str; quantity:float; order_type:str='MARKET'; limit_price:float|None=None; stop_price:float|None=None

def connect():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT UNIQUE NOT NULL,name TEXT NOT NULL,password_hash TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS accounts(user_id INTEGER PRIMARY KEY,cash REAL NOT NULL DEFAULT 100000);
        CREATE TABLE IF NOT EXISTS positions(user_id INTEGER NOT NULL,symbol TEXT NOT NULL,quantity REAL NOT NULL DEFAULT 0,avg_price REAL NOT NULL DEFAULT 0,PRIMARY KEY(user_id,symbol));
        CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,symbol TEXT NOT NULL,side TEXT NOT NULL,quantity REAL NOT NULL,price REAL NOT NULL,order_type TEXT NOT NULL DEFAULT 'MARKET',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,symbol TEXT NOT NULL,side TEXT NOT NULL,quantity REAL NOT NULL,order_type TEXT NOT NULL,limit_price REAL,stop_price REAL,status TEXT NOT NULL DEFAULT 'PENDING',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,filled_at TEXT,fill_price REAL);
        ''')
        for ddl in ["ALTER TABLE trades ADD COLUMN order_type TEXT NOT NULL DEFAULT 'MARKET'","ALTER TABLE orders ADD COLUMN fill_price REAL"]:
            try:c.execute(ddl)
            except:pass
@app.on_event('startup')
def startup():init_db()

def hash_password(p,salt=None):
    salt=salt or secrets.token_bytes(16); dk=hashlib.pbkdf2_hmac('sha256',p.encode(),salt,150000); return base64.urlsafe_b64encode(salt+dk).decode()
def verify_password(p,s):
    raw=base64.urlsafe_b64decode(s.encode()); salt,exp=raw[:16],raw[16:]; act=hashlib.pbkdf2_hmac('sha256',p.encode(),salt,150000); return hmac.compare_digest(act,exp)
def make_token(uid):
    payload=base64.urlsafe_b64encode(json.dumps({'uid':uid,'exp':int(time.time())+604800}).encode()).decode().rstrip('='); sig=hmac.new(APP_SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest(); return payload+'.'+sig
def parse_token(t):
    try:
        p,s=t.split('.',1); exp=hmac.new(APP_SECRET.encode(),p.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(s,exp):raise ValueError
        d=json.loads(base64.urlsafe_b64decode((p+'='*(-len(p)%4)).encode()).decode())
        if d['exp']<time.time():raise ValueError
        return int(d['uid'])
    except:raise HTTPException(401,'Sesión inválida o vencida')
def current_user(a):
    if not a or not a.lower().startswith('bearer '):raise HTTPException(401,'Inicia sesión')
    return parse_token(a.split(' ',1)[1])

def market_quote(symbol):
    symbol=symbol.upper()
    now=time.time()
    if symbol in CACHE and now-CACHE[symbol]['cached_at']<CACHE_TTL:return CACHE[symbol]
    try:
        url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(symbol)+'?interval=1m&range=1d'
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 CapitalRebeldeAcademy/0.3'})
        with urllib.request.urlopen(req,timeout=5) as r:d=json.loads(r.read().decode())
        res=d['chart']['result'][0]; meta=res['meta']; closes=res['indicators']['quote'][0]['close']; ts=res.get('timestamp',[])
        vals=[(t,p) for t,p in zip(ts,closes) if p is not None]
        if not vals:raise ValueError
        t,p=vals[-1]; q={'symbol':symbol,'price':round(float(p),4),'timestamp':t,'source':'market-derived beta','delayed':True,'cached_at':now}
    except Exception:
        q={'symbol':symbol,'price':FALLBACK.get(symbol,100.0),'timestamp':int(now),'source':'fallback demo','delayed':True,'cached_at':now}
    CACHE[symbol]=q; return q

def execute(uid,symbol,side,qty,price,otype='MARKET',order_id=None):
    with connect() as c:
        cash=float(c.execute('SELECT cash FROM accounts WHERE user_id=?',(uid,)).fetchone()[0]); row=c.execute('SELECT quantity,avg_price FROM positions WHERE user_id=? AND symbol=?',(uid,symbol)).fetchone(); oldq,olda=(float(row[0]),float(row[1])) if row else (0.0,0.0)
        if side=='BUY':
            cost=qty*price
            if cost>cash:return False,'Saldo insuficiente'
            newq=oldq+qty; newa=((oldq*olda)+cost)/newq; cash-=cost
        else:
            if qty>oldq:return False,'No tienes suficientes títulos'
            newq=oldq-qty; newa=olda if newq>0 else 0; cash+=qty*price
        c.execute('UPDATE accounts SET cash=? WHERE user_id=?',(cash,uid)); c.execute('INSERT INTO positions(user_id,symbol,quantity,avg_price) VALUES(?,?,?,?) ON CONFLICT(user_id,symbol) DO UPDATE SET quantity=excluded.quantity,avg_price=excluded.avg_price',(uid,symbol,newq,newa)); c.execute('INSERT INTO trades(user_id,symbol,side,quantity,price,order_type) VALUES(?,?,?,?,?,?)',(uid,symbol,side,qty,price,otype))
        if order_id:c.execute("UPDATE orders SET status='FILLED',filled_at=CURRENT_TIMESTAMP,fill_price=? WHERE id=? AND user_id=?",(price,order_id,uid))
    return True,'filled'

def should_fill(o,price):
    typ=o['order_type']; side=o['side']
    if typ=='LIMIT':return price<=o['limit_price'] if side=='BUY' else price>=o['limit_price']
    if typ=='STOP':return price>=o['stop_price'] if side=='BUY' else price<=o['stop_price']
    return False

def process_pending(uid):
    with connect() as c:orders=c.execute("SELECT * FROM orders WHERE user_id=? AND status='PENDING' ORDER BY id",(uid,)).fetchall()
    for o in orders:
        price=market_quote(o['symbol'])['price']
        if should_fill(o,price):execute(uid,o['symbol'],o['side'],float(o['quantity']),price,o['order_type'],o['id'])

@app.get('/')
def root():return {'app':'Capital Rebelde Academy','status':'online','version':'0.3.0'}
@app.get('/health')
def health():return {'ok':True,'version':'0.3.0','market_mode':'market-derived beta'}
@app.get('/quotes')
def quotes(symbols:str|None=None):
    syms=[s.strip().upper() for s in (symbols.split(',') if symbols else SYMBOLS) if s.strip().upper() in SYMBOLS]
    return {'mode':'market-derived beta','quotes':[{k:v for k,v in market_quote(s).items() if k!='cached_at'} for s in syms]}

@app.post('/auth/register')
def register(d:AuthIn):
    email=d.email.strip().lower(); name=(d.name or email.split('@')[0]).strip()[:80]
    if len(d.password)<6:raise HTTPException(400,'La contraseña debe tener al menos 6 caracteres')
    try:
        with connect() as c:cur=c.execute('INSERT INTO users(email,name,password_hash) VALUES(?,?,?)',(email,name,hash_password(d.password))); uid=cur.lastrowid; c.execute('INSERT INTO accounts(user_id,cash) VALUES(?,?)',(uid,STARTING_CASH))
    except sqlite3.IntegrityError:raise HTTPException(409,'Ese correo ya está registrado')
    return {'token':make_token(uid),'user':{'id':uid,'email':email,'name':name}}
@app.post('/auth/login')
def login(d:AuthIn):
    with connect() as c:r=c.execute('SELECT * FROM users WHERE email=?',(d.email.strip().lower(),)).fetchone()
    if not r or not verify_password(d.password,r['password_hash']):raise HTTPException(401,'Correo o contraseña incorrectos')
    return {'token':make_token(r['id']),'user':{'id':r['id'],'email':r['email'],'name':r['name']}}

@app.get('/portfolio')
def portfolio(authorization:str|None=Header(default=None)):
    uid=current_user(authorization); process_pending(uid)
    with connect() as c:
        cash=float(c.execute('SELECT cash FROM accounts WHERE user_id=?',(uid,)).fetchone()[0]); pos=c.execute('SELECT * FROM positions WHERE user_id=? AND quantity>0 ORDER BY symbol',(uid,)).fetchall(); trades=c.execute('SELECT symbol,side,quantity,price,order_type,created_at FROM trades WHERE user_id=? ORDER BY id DESC LIMIT 50',(uid,)).fetchall(); orders=c.execute("SELECT id,symbol,side,quantity,order_type,limit_price,stop_price,status,created_at,filled_at,fill_price FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 50",(uid,)).fetchall()
    out=[]; mv=0.0
    for r in pos:
        q=market_quote(r['symbol']); price=q['price']; val=r['quantity']*price; mv+=val; out.append({'symbol':r['symbol'],'quantity':r['quantity'],'avg_price':r['avg_price'],'price':price,'value':val,'pnl':val-r['quantity']*r['avg_price']})
    return {'cash':cash,'market_value':mv,'equity':cash+mv,'positions':out,'trades':[dict(x) for x in trades],'orders':[dict(x) for x in orders],'mode':'market-derived beta'}

@app.post('/orders')
def place(d:OrderIn,authorization:str|None=Header(default=None)):
    uid=current_user(authorization); s=d.symbol.upper().strip(); side=d.side.upper().strip(); typ=d.order_type.upper().strip(); qty=float(d.quantity)
    if s not in SYMBOLS:raise HTTPException(400,'Instrumento no disponible todavía')
    if side not in {'BUY','SELL'} or typ not in {'MARKET','LIMIT','STOP'} or qty<=0:raise HTTPException(400,'Orden inválida')
    price=market_quote(s)['price']
    if typ=='MARKET':
        ok,msg=execute(uid,s,side,qty,price,typ)
        if not ok:raise HTTPException(400,msg)
        return {'ok':True,'status':'FILLED','message':f'{side} {qty:g} {s} @ ${price:,.2f}'}
    if typ=='LIMIT' and (d.limit_price is None or d.limit_price<=0):raise HTTPException(400,'Falta precio límite')
    if typ=='STOP' and (d.stop_price is None or d.stop_price<=0):raise HTTPException(400,'Falta precio stop')
    with connect() as c:cur=c.execute('INSERT INTO orders(user_id,symbol,side,quantity,order_type,limit_price,stop_price,status) VALUES(?,?,?,?,?,?,?,?)',(uid,s,side,qty,typ,d.limit_price,d.stop_price,'PENDING')); oid=cur.lastrowid
    process_pending(uid)
    with connect() as c:o=c.execute('SELECT status,fill_price FROM orders WHERE id=?',(oid,)).fetchone()
    return {'ok':True,'order_id':oid,'status':o['status'],'fill_price':o['fill_price'],'message':f'Orden {typ} {o["status"]}'}

@app.delete('/orders/{order_id}')
def cancel(order_id:int,authorization:str|None=Header(default=None)):
    uid=current_user(authorization)
    with connect() as c:cur=c.execute("UPDATE orders SET status='CANCELED' WHERE id=? AND user_id=? AND status='PENDING'",(order_id,uid))
    if cur.rowcount==0:raise HTTPException(404,'Orden no encontrada o ya ejecutada')
    return {'ok':True,'message':'Orden cancelada'}
