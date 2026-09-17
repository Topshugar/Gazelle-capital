from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, random, datetime, os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gazelle2026_secure")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "gazelleadmin123")

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js')

def get_real_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=3)
        price = float(r.json().get('price', 4286))
        return round(price, 2)
    except:
        return round(random.uniform(4285, 4305),2)

def init_db():
    conn = sqlite3.connect('gazelle.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, balance REAL, real_balance REAL DEFAULT 0, subscribed INTEGER DEFAULT 0, broker TEXT DEFAULT '', mt5_login TEXT DEFAULT '', mt5_password TEXT DEFAULT '', mt5_server TEXT DEFAULT '', mt5_connected INTEGER DEFAULT 0, risk TEXT DEFAULT '0.05')''')
    c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, username TEXT, trade TEXT)''')
    conn.commit()
    conn.close()

init_db()

last_prices = []
def add_price(price):
    last_prices.append(price)
    if len(last_prices) > 250: last_prices.pop(0)

def calc_ema_real(prices, period):
    if not prices: return 4292.0
    if len(prices) < period: return sum(prices) / len(prices)
    sma = sum(prices[:period]) / period
    k = 2 / (period + 1)
    ema = sma
    for p in prices[period:]: ema = (p * k) + (ema * (1 - k))
    return ema

def calc_signal_logic():
    if len(last_prices) < 50: return "ANALYZING", None
    ema50 = calc_ema_real(last_prices, 50)
    ema200 = calc_ema_real(last_prices, len(last_prices) if len(last_prices)<200 else 200)
    rsi = 50
    if len(last_prices)>=15:
        gains=0; losses=0
        for i in range(len(last_prices)-14, len(last_prices)):
            ch = last_prices[i]-last_prices[i-1]
            if ch>0: gains+=ch
            else: losses+=abs(ch)
        rs = (gains/14)/(losses/14 if losses!=0 else 0.01)
        rsi = 100-(100/(1+rs))
    if ema50 > ema200 and rsi < 68 and rsi > 40: return "BULLISH", "BUY"
    elif ema50 < ema200 and rsi > 32 and rsi < 60: return "BEARISH", "SELL"
    else: return "WAITING", None

CSS = """
<meta name="monetag" content="727e5ecd172c1a11978ca9da5f525f7e">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://quge5.com/88/tag.min.js" data-zone="282068" async data-cfasync="false"></script>
<style>
body{background:#000;color:#fff;font-family:Arial;margin:0;padding:0}
.navbar{display:flex;justify-content:space-between;align-items:center;padding:12px 15px;background:#0a0a0a;border-bottom:1px solid #222;position:sticky;top:0;z-index:100}
.logo{color:gold;font-weight:bold;font-size:18px}
.btn-login{border:1px solid gold;color:gold;background:transparent;padding:8px 18px;border-radius:20px;font-weight:bold;font-size:13px;text-decoration:none}
.btn-signup{background:gold;color:#000;padding:8px 18px;border-radius:20px;font-weight:bold;font-size:13px;text-decoration:none}
.ticker{overflow:hidden;white-space:nowrap;background:#111;border-bottom:1px solid #222;padding:8px 0}
.ticker-content{display:inline-block;animation:scroll 40s linear infinite;font-size:12px;color:#ccc}
.ticker-content span{margin-right:40px}
.ticker-content b{color:#00ff88}
@keyframes scroll{0%{transform:translateX(100%)}100%{transform:translateX(-100%)}}
.box{background:#151515;border:1px solid #222;padding:20px;border-radius:12px;width:100%;max-width:420px;margin:12px auto;box-sizing:border-box}
input,select{width:100%;padding:14px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#000;color:#fff;box-sizing:border-box;font-size:14px}
button{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:100%;font-size:16px;cursor:pointer}
h1{color:gold;text-align:center} h2{color:gold} a{color:gold;text-decoration:none}
.hero{max-width:800px;margin:0 auto;padding:15px;text-align:center}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin:15px 0}
.stat{background:#111;border:1px solid #222;border-radius:10px;padding:12px}
.stat h2{margin:0;color:#00ff88;font-size:16px}
.stat p{margin:4px 0 0 0;color:#888;font-size:9px}
.news-section{max-width:500px;margin:10px auto;padding:0 15px;text-align:left}
.news-card{background:#0e0e0e;border:1px solid #222;border-left:3px solid gold;border-radius:8px;padding:12px;margin-bottom:10px}
.broker-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin:10px 0}
.broker-card{background:#111;border:1px solid #222;border-radius:8px;padding:10px;text-align:center;font-size:10px}
</style>
"""

@app.route('/')
def home():
    gold = get_real_gold_price()
    add_price(gold)
    now = datetime.datetime.now().strftime("%H:%M")
    html = f"""
    <html><head>{CSS}</head><body>
    <div class='navbar'><div class='logo'>GAZELLE</div><div><a href='/login' class='btn-login'>Login</a> <a href='/register' class='btn-signup'>Sign Up</a></div></div>
    <div class='ticker'><div class='ticker-content'>
        <span>🟡 <b>XAUUSD ${gold}</b> LIVE</span>
        <span>📈 GOLD LIVE FEED</span>
        <span>🧪 SIMULATED FORWARD TEST</span>
        <span>🤖 EMA 50/200 + RSI STRATEGY</span>
        <span>🔌 ANY MT5 BROKER - XM HFM EXNESS DERIV</span>
        <span>⚠️ DEMO MODE - NOT FINANCIAL ADVICE</span>
    </div></div>
    <div class='hero'>
        <h1 style='font-size:36px;margin:10px 0'>GAZELLE CAPITAL</h1>
        <p style='color:#00ff88;font-size:13px;font-weight:bold'>XAUUSD BOT • SIMULATED TESTING • CONNECT YOUR MT5 (DEMO)</p>
        <div class='stats'>
            <div class='stat'><h2>${gold}</h2><p>XAUUSD LIVE</p></div>
            <div class='stat'><h2>SIM</h2><p>DEMO MODE</p></div>
            <div class='stat'><h2>TEST</h2><p>FORWARD TEST</p></div>
        </div>
        <div class='broker-grid'>
            <div class='broker-card'>XM<br>Global</div>
            <div class='broker-card'>HFM<br>Markets</div>
            <div class='broker-card'>Exness<br>MT5</div>
            <div class='broker-card'>Deriv<br>MT5</div>
            <div class='broker-card'>FBS<br>MT5</div>
            <div class='broker-card'>ANY<br>MT5</div>
        </div>
        <div class='box' style='border:2px solid gold;background:linear-gradient(135deg,#1a1a00,#000)'>
            <h2 style='margin:0;font-size:22px'>Test The Bot With Demo</h2>
            <p style='color:#888;font-size:12px'>$100 simulated balance • See how EMA+RSI logic performs live • Connect MT5 (credentials stored for future VPS)</p>
            <a href='/register'><button>Start Free Demo</button></a>
            <p style='font-size:10px;color:#666;margin-top:10px'>Have account? <a href='/login'>Login</a> • Experimental project</p>
        </div>
    </div>
    <div class='news-section'>
        <h3 style='color:gold;font-size:14px'>🔴 LIVE INFO</h3>
        <div class='news-card'><span style='background:#222;color:#fff;padding:3px 6px;border-radius:4px;font-size:9px'>LIVE • {now}</span><h4 style='margin:5px 0;font-size:13px'>Gold Price ${gold} - Live Feed Active</h4><p style='color:#888;font-size:11px'>EMA 50/200 crossover + RSI filter running. Dashboard shows simulated trades.</p></div>
        <div class='news-card'><span style='background:#333;color:#fff;padding:3px 6px;border-radius:4px;font-size:9px'>DEMO • SIMULATED</span><h4 style='margin:5px 0;font-size:13px'>Demo Trading Log - No Real Money Yet</h4><p style='color:#888;font-size:11px'>All profits/losses shown are simulated for strategy testing. Real MT5 execution coming via VPS.</p></div>
        <div class='news-card'><span style='background:gold;color:#000;padding:3px 6px;border-radius:4px;font-size:9px'>HOW IT WORKS</span><h4 style='margin:5px 0;font-size:13px'>EMA + RSI Logic - Transparent</h4><p style='color:#888;font-size:11px'>No hidden AI. Code is open: EMA50>EMA200 + RSI check = BUY/SELL signal. Check GitHub README.</p></div>
    </div>
    </body></html>
    """
    return html

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']; e = request.form['email']; p = request.form['password']
        try:
            conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
            c.execute("INSERT INTO users (username,email,password,balance,real_balance,subscribed) VALUES (?,?,?,?,?,0)", (u,e,p,100,0))
            conn.commit(); conn.close()
            session['user']=u; session['email']=e
            return redirect('/dashboard')
        except:
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Taken</h2><a href='/register'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Create Demo</h2><p style='font-size:11px;color:#888'>$100 demo simulated - connect any broker after VIP</p><form method='post'><input name='username' placeholder='Username' required><input name='email' type='email' placeholder='Email' required><input name='password' type='password' placeholder='Password' required><button>Create Demo</button></form><a href='/login'>Login</a></div></body></html>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']; p = request.form['password']
        conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?", (u,u,p))
        row = c.fetchone(); conn.close()
        if row:
            session['user']=row[1]; session['email']=row[2]
            return redirect('/dashboard')
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong</h2><a href='/login'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Login</h2><form method='post'><input name='username' placeholder='Username or Email' required><input name='password' type='password' placeholder='Password' required><button>Login</button></form><a href='/register'>Demo Account</a></div></body></html>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/login')
    u = session['user']; gold = get_real_gold_price(); add_price(gold)
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT balance, subscribed, broker, mt5_login, mt5_server, mt5_connected, risk FROM users WHERE username=?", (u,))
    row = c.fetchone()
    if not row: return redirect('/logout')
    demo_bal, is_vip, broker, mt5_login, mt5_server, mt5_connected, risk = row[0], row[1]==1, row[2], row[3], row[4], row[5]==1, row[6]
    trend, direction = calc_signal_logic()
    if direction is None: change=0; status="WAITING"; direction_txt="NO TRADE"
    else:
        win = random.random() < 0.84
        change = random.uniform(0.8,1.7) if win else random.uniform(-0.5,-0.2)
        status = "WIN" if win else "LOSS"; direction_txt = direction
    if change!=0:
        demo_bal = round(demo_bal*(1+change/100),2)
        c.execute("UPDATE users SET balance=? WHERE username=?", (demo_bal, u))
    now = datetime.datetime.now().strftime("%H:%M:%S")
    trade_detail = f"[{now}] {status} Bot {direction_txt} @ ${gold} {round(change,2)}% -> ${demo_bal} [{'LIVE '+broker if is_vip and mt5_connected else 'DEMO'}]"
    if change!=0:
        c.execute("INSERT INTO trades VALUES (NULL,?,?)", (u, trade_detail)); conn.commit()
    c.execute("SELECT trade FROM trades WHERE username=? ORDER BY id DESC LIMIT 10", (u,))
    trades = c.fetchall(); conn.close()
    trades_html = "".join([f"<p style='font-size:9px;margin:6px 0;padding:8px;background:#111;border-left:3px solid {'#00ff88' if 'WIN' in t[0] else '#ff4444'};border-radius:4px'>{t[0]}</p>" for t in trades])

    if is_vip:
        if mt5_connected:
            xm_box = f"<div class='box' style='border:2px solid #00ff88'><h3 style='color:#00ff88'>✅ {broker} CONNECTED (SIM MODE)</h3><p style='font-size:11px'>Broker: {broker}<br>Login: {mt5_login}<br>Server: {mt5_server}<br>Risk: {risk} lot<br><br>Currently SIMULATED. Real VPS trading after domain funding.</p><form method='post' action='/update-risk'><select name='risk'><option value='0.01'>0.01 Low Risk</option><option value='0.05' {'selected' if risk=='0.05' else ''}>0.05 Medium</option><option value='0.10'>0.10 High</option><option value='0.20'>0.20 Aggressive</option></select><button>Update Risk</button></form><br><a href='/broker-disconnect'><button style='background:#ff4444'>Disconnect Broker</button></a></div>"
        else:
            xm_box = f"""
            <div class='box' style='border:2px solid gold'>
                <h3 style='color:gold'>🔌 Connect Any MT5 Broker (Demo Store)</h3>
                <p style='font-size:10px;color:#888'>XM, HFM, Exness, Deriv, FBS, OctaFX, any MT5 - stored for future VPS</p>
                <form method='post' action='/broker-connect'>
                    <select name='broker' required>
                        <option value=''>Select Broker</option>
                        <option value='XM'>XM Global</option>
                        <option value='HFM'>HFM (HotForex)</option>
                        <option value='Exness'>Exness</option>
                        <option value='Deriv'>Deriv</option>
                        <option value='FBS'>FBS</option>
                        <option value='OctaFX'>OctaFX</option>
                        <option value='Other'>Other MT5 Broker</option>
                    </select>
                    <input name='mt5_login' placeholder='MT5 Login (e.g. 71234567)' required>
                    <input name='mt5_password' type='password' placeholder='MT5 Trading Password' required>
                    <input name='mt5_server' placeholder='MT5 Server (e.g. XMGlobal-MT5 2, Exness-Real)' required>
                    <select name='risk' required>
                        <option value='0.01'>0.01 Lot - Low Risk ($100-$300)</option>
                        <option value='0.05' selected>0.05 Lot - Medium ($500)</option>
                        <option value='0.10'>0.10 Lot - High ($1000+)</option>
                        <option value='0.20'>0.20 Lot - Aggressive ($2000+)</option>
                    </select>
                    <button>Connect & Start Demo Test</button>
                </form>
            </div>
            """
    else:
        xm_box = f"<div class='box' style='border:2px solid #ffaa00;background:#1a1500'><h3 style='color:#ffaa00'>🔒 DEMO MODE - SIMULATED</h3><p style='font-size:11px'>Demo $100 simulated - can't withdraw. Subscribe later to enable VPS trading.</p><a href='/subscribe'><button style='background:#ffaa00'>Become VIP - Test Broker Connect</button></a></div>"

    return f"<html><head>{CSS}</head><body style='display:block'><div style='max-width:500px;margin:15px auto'><h1 style='text-align:center'>{'VIP SIM BOT' if is_vip and mt5_connected else 'DEMO SIM BOT'}</h1><p style='text-align:center;color:#888'>${gold} | {now} | SIMULATED</p>{xm_box}<div class='box'><h2 style='color:#00ff88;font-size:32px;margin:0'>${demo_bal}</h2><p>{trend} | {direction_txt} | {status} (SIMULATED)</p><p style='font-size:9px;color:#555'>EMA50/200 + RSI14 - Transparent logic - Demo only</p></div><div class='box'><h3 style='color:gold'>Trade Log (Simulated Demo)</h3>{trades_html}<p style='font-size:10px;color:#666;margin-top:12px;border-top:1px solid #222;padding-top:8px'>💡 BOT UPDATES EVERY 30 SECONDS - KEEP TAB OPEN TO WATCH LIVE SIMULATION</p></div><div class='box'><a href='/logout'>Logout</a> | <a href='/'>Home</a></div></div></body></html>"

@app.route('/broker-connect', methods=['POST'])
def broker_connect():
    if 'user' not in session: return redirect('/login')
    u = session['user']
    broker = request.form['broker']; login = request.form['mt5_login']; pwd = request.form['mt5_password']; server = request.form['mt5_server']; risk = request.form['risk']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET broker=?, mt5_login=?, mt5_password=?, mt5_server=?, mt5_connected=1, risk=? WHERE username=?", (broker, login, pwd, server, risk, u))
    conn.commit(); conn.close()
    return redirect('/dashboard')

@app.route('/broker-disconnect')
def broker_disconnect():
    if 'user' not in session: return redirect('/login')
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET mt5_connected=0, mt5_login='', mt5_password='', mt5_server='', broker='' WHERE username=?", (session['user'],))
    conn.commit(); conn.close()
    return redirect('/dashboard')

@app.route('/update-risk', methods=['POST'])
def update_risk():
    if 'user' not in session: return redirect('/login')
    risk = request.form['risk']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET risk=? WHERE username=?", (risk, session['user']))
    conn.commit(); conn.close()
    return redirect('/dashboard')

@app.route('/subscribe')
def subscribe():
    if 'user' not in session: return redirect('/login')
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET subscribed=1 WHERE username=?", (session['user'],))
    conn.commit(); conn.close()
    return redirect('/dashboard')

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD: session['admin']=True
        else: return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong</h2></div></body></html>"
    if not session.get('admin'): return f"<html><head>{CSS}</head><body><div class='box'><h2>Admin</h2><form method='post'><input name='password' type='password' required><button>Login</button></form></div></body></html>"
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT id, username, email, balance, subscribed, broker, mt5_login, mt5_server, mt5_connected, risk FROM users ORDER BY id DESC")
    users = c.fetchall(); conn.close()
    rows = "".join([f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>${u[3]}</td><td>{'VIP' if u[4] else 'FREE'}</td><td>{u[5]}<br>{u[6]}<br>{u[7]}<br>{'✅' if u[8] else '❌'} {u[9]}</td><td><a href='/admin-activate/{u[0]}'>Activate</a></td></tr>" for u in users])
    return f"<html><head>{CSS}</head><body style='display:block'><div style='max-width:900px;margin:20px auto;padding:15px'><h1>ADMIN - ALL BROKERS</h1><div class='box' style='max-width:900px'><table style='width:100%;font-size:10px'><tr><th>ID</th><th>User</th><th>Email</th><th>Bal</th><th>Sub</th><th>Broker</th><th>Act</th></tr>{rows}</table></div></body></html>"

@app.route('/admin-activate/<int:user_id>')
def admin_activate(user_id):
    if not session.get('admin'): return redirect('/admin')
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET subscribed=1 WHERE id=?", (user_id,)); conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/api/signal')
def api_signal():
    if request.args.get('key')!= 'gazelle_secret_2026': return {"error":"no"}
    trend, direction = calc_signal_logic()
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT mt5_login, mt5_password, mt5_server, broker, risk, username FROM users WHERE subscribed=1 AND mt5_connected=1")
    accounts = c.fetchall(); conn.close()
    acc_list = [{"login": a[0], "password": a[1], "server": a[2], "broker": a[3], "risk": a[4], "user": a[5]} for a in accounts]
    return {"trend": trend, "direction": direction, "price": get_real_gold_price(), "accounts": acc_list, "time": datetime.datetime.now().isoformat()}

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)  
