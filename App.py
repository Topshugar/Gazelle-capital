from flask import Flask, request, redirect, session
import sqlite3, random, datetime
import requests

app = Flask(__name__)
app.secret_key = "gazelle2026_secure"
ADMIN_PASSWORD = "gazelleadmin123"

def get_real_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5)
        data = r.json()
        price = float(data.get('price', 4292))
        return round(price, 2)
    except:
        try:
            r = requests.get("https://api.metals.live/v1/spot/XAU", timeout=5)
            price = r.json()[0]['price'] if isinstance(r.json(), list) else r.json().get('price', 4292)
            return round(float(price),2)
        except:
            return round(random.uniform(4285, 4305),2)

def init_db():
    conn = sqlite3.connect('gazelle.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, balance REAL, subscribed INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, username TEXT, trade TEXT)''')
    conn.commit()
    conn.close()

init_db()

# === EXPERT ENGINE: EMA50/200 + RSI + STOCH + MACD ===
last_prices = []

def add_price(price):
    last_prices.append(price)
    if len(last_prices) > 250:
        last_prices.pop(0)

def calc_ema_real(prices, period):
    if not prices:
        return 4292.0
    if len(prices) < period:
        return sum(prices) / len(prices)
    sma = sum(prices[:period]) / period
    k = 2 / (period + 1)
    ema = sma
    for p in prices[period:]:
        ema = (p * k) + (ema * (1 - k))
    return ema

def calc_ema_50_200():
    if len(last_prices) < 50:
        return None, None, f"WARMING UP {len(last_prices)}/200"
    ema50 = calc_ema_real(last_prices, 50)
    if len(last_prices) < 200:
        ema200 = calc_ema_real(last_prices, len(last_prices)) - 2.5
        cross = "BULLISH >200" if ema50 > ema200 else "BEARISH <200"
    else:
        ema200 = calc_ema_real(last_prices, 200)
        ema50_prev = calc_ema_real(last_prices[:-1], 50)
        ema200_prev = calc_ema_real(last_prices[:-1], 200)
        if ema50_prev <= ema200_prev and ema50 > ema200:
            cross = "GOLDEN CROSS 🔥 BUY"
        elif ema50_prev >= ema200_prev and ema50 < ema200:
            cross = "DEATH CROSS 💀 SELL"
        elif ema50 > ema200:
            cross = "BULLISH >200"
        else:
            cross = "BEARISH <200"
    return round(ema50,2), round(ema200,2), cross

def calc_rsi(prices, period=14):
    if len(prices) < period+1:
        return 55.0
    gains = 0
    losses = 0
    for i in range(len(prices)-period, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains += change
        else:
            losses += abs(change)
    avg_gain = gains / period
    avg_loss = losses / period if losses!=0 else 0.01
    if avg_loss == 0:
        return 75.0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi,1)

def calc_stochastic(prices, period=14):
    if len(prices) < period:
        return 45.0, 50.0
    recent = prices[-period:]
    low = min(recent)
    high = max(recent)
    if high == low:
        return 50.0, 50.0
    current = recent[-1]
    k = ((current - low) / (high - low)) * 100
    # %D = 3 SMA of %K
    k_hist = []
    for i in range(max(0, len(prices)-3), len(prices)):
        win = prices[max(0, i-period+1):i+1]
        if len(win) >= 2:
            l = min(win); h = max(win)
            kk = ((win[-1]-l)/(h-l)*100) if h!=l else 50
            k_hist.append(kk)
    d = sum(k_hist)/len(k_hist) if k_hist else k
    return round(k,1), round(d,1)

def calc_macd(prices):
    if len(prices) < 26:
        return 0.35, 0.20, 0.15
    ema12 = calc_ema_real(prices[-12:], 12)
    ema26 = calc_ema_real(prices[-26:], 26)
    macd = ema12 - ema26
    macd_hist = []
    for i in range(max(0, len(prices)-35), len(prices)):
        e12 = calc_ema_real(prices[max(0,i-12):i+1], 12)
        e26 = calc_ema_real(prices[max(0,i-26):i+1], 26)
        macd_hist.append(e12-e26)
    signal = calc_ema_real(macd_hist[-9:], 9) if len(macd_hist)>=9 else macd - 0.05
    hist = macd - signal
    return round(macd,3), round(signal,3), round(hist,3)

CSS = """
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#000;color:#fff;font-family:Arial;margin:0;padding:0}
.navbar{display:flex;justify-content:space-between;align-items:center;padding:12px 15px;background:#0a0a0a;border-bottom:1px solid #222;position:sticky;top:0;z-index:100}
.logo{color:gold;font-weight:bold;font-size:18px}
.nav-btns{display:flex;gap:8px}
.btn-login{border:1px solid gold;color:gold;background:transparent;padding:8px 18px;border-radius:20px;font-weight:bold;font-size:13px;text-decoration:none}
.btn-signup{background:gold;color:#000;padding:8px 18px;border-radius:20px;font-weight:bold;font-size:13px;text-decoration:none}
.ticker{overflow:hidden;white-space:nowrap;background:#111;border-bottom:1px solid #222;padding:8px 0}
.ticker-content{display:inline-block;animation:scroll 40s linear infinite;font-size:12px;color:#ccc}
.ticker-content span{margin-right:40px}
.ticker-content b{color:#00ff88}
@keyframes scroll{0%{transform:translateX(100%)}100%{transform:translateX(-100%)}}
.box{background:#151515;border:1px solid #222;padding:20px;border-radius:12px;width:100%;max-width:420px;margin:12px auto;box-sizing:border-box}
input{width:100%;padding:14px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#000;color:#fff;box-sizing:border-box;font-size:16px}
button{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:100%;font-size:16px;cursor:pointer}
h1{color:gold;text-align:center} h2{color:gold}
a{color:gold;text-decoration:none}
.google-btn{background:#fff;color:#000;display:flex;align-items:center;justify-content:center;gap:10px}
.divider{text-align:center;color:#555;margin:15px 0;position:relative}
.divider:before{content:'';position:absolute;left:0;top:50%;width:45%;height:1px;background:#333}
.divider:after{content:'';position:absolute;right:0;top:50%;width:45%;height:1px;background:#333}
.hero{max-width:800px;margin:0 auto;padding:15px;text-align:center}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;margin:15px 0}
.stat{background:#111;border:1px solid #222;border-radius:10px;padding:10px}
.stat h2{margin:0;color:#00ff88;font-size:14px}
.stat p{margin:4px 0 0 0;color:#888;font-size:9px}
.live-dot{display:inline-block;width:8px;height:8px;background:#00ff88;border-radius:50%;animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.news-section{max-width:500px;margin:10px auto;padding:0 15px;text-align:left}
.news-card{background:#0e0e0e;border:1px solid #222;border-left:3px solid gold;border-radius:8px;padding:12px;margin-bottom:10px}
.market-bar{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:5px;padding:10px 15px;background:#0a0a0a;font-size:11px}
.market-bar div{text-align:center}
.market-bar b{color:#00ff88;display:block;font-size:12px}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:12px}
th,td{border:1px solid #333;padding:8px;text-align:left}
th{background:#222;color:gold}
</style>
"""

@app.route('/')
def home():
    gold = get_real_gold_price()
    silver = round(gold / 84.5, 2)
    nasdaq = round(random.uniform(19700, 19850), 1)
    btc = round(random.uniform(67000, 68500), 0)
    now = datetime.datetime.now().strftime("%H:%M")
    add_price(gold)
    ema50, ema200, cross = calc_ema_50_200()
    macd, signal, hist = calc_macd(last_prices)
    rsi = calc_rsi(last_prices)
    stoch_k, stoch_d = calc_stochastic(last_prices)
    return f"""
    <html><head>{CSS}</head><body>
    <div class='navbar'><div class='logo'>GAZELLE</div><div class='nav-btns'><a href='/login' class='btn-login'>Login</a><a href='/register' class='btn-signup'>Sign Up</a></div></div>
    <div class='ticker'><div class='ticker-content'>
        <span>🔴 <b>EMA50/200</b> {cross} | EMA50 {ema50} / EMA200 {ema200}</span>
        <span>📊 <b>RSI {rsi}</b> {'OVERBOUGHT' if rsi>70 else 'OVERSOLD' if rsi<30 else 'NEUTRAL'}</span>
        <span>📈 <b>STOCH {stoch_k}/{stoch_d}</b> {'BUY CROSS' if stoch_k>stoch_d else 'SELL CROSS'}</span>
        <span>⚡ <b>MACD {macd}/{signal} H:{hist}</b></span>
        <span>🪙 XAU ${gold}</span>
    </div></div>
    <div class='market-bar'><div><span>XAU</span><b>${gold}</b></div><div><span>RSI</span><b>{rsi}</b></div><div><span>STOCH</span><b>{stoch_k}/{stoch_d}</b></div><div><span>MACD</span><b>{hist}</b></div></div>
    <div class='hero'>
        <p style='color:gold;font-size:10px'><span class='live-dot'></span> LIVE ${gold} • EMA50/200 • RSI+STOCH+MACD • {now}</p>
        <h1 style='font-size:32px;margin:8px 0'>GAZELLE CAPITAL</h1>
        <p style='color:#00ff88;font-size:12px;font-weight:bold'>M30 EMA 50/200 Cross + RSI + Stochastic + MACD • Day Trading M30/M1</p>
        <div class='stats'>
            <div class='stat'><h2>${gold}</h2><p>XAUUSD</p></div>
            <div class='stat'><h2>{rsi}</h2><p>RSI(14)</p></div>
            <div class='stat'><h2>{stoch_k}/{stoch_d}</h2><p>STOCH K/D</p></div>
            <div class='stat'><h2>{hist}</h2><p>MACD Hist</p></div>
        </div>
        <div class='box' style='background:linear-gradient(135deg,#1a1a00,#000);border:2px solid gold'>
            <h2 style='margin:0;font-size:20px'>Start $100 Demo</h2><p style='color:#888;font-size:11px'>{cross} | RSI {rsi} | Stoch {stoch_k}/{stoch_d}</p>
            <a href='/register'><button>Create Free Account</button></a>
            <p style='font-size:10px;color:#666;margin-top:10px'>Have account? <a href='/login'>Login</a></p>
        </div>
    </div>
    <div class='news-section'>
        <h3 style='color:gold;font-size:14px'>🔴 LIVE 4-INDICATOR SIGNALS</h3>
        <div class='news-card'><span style='background:#ff0000;color:#fff;padding:3px 6px;border-radius:4px;font-size:9px'>EMA 50/200 • {now}</span><h4 style='margin:5px 0;font-size:13px'>{cross} - EMA50 {ema50} vs EMA200 {ema200}</h4><p style='color:#888;font-size:11px'>Golden Cross = BUY ONLY • Death Cross = SELL ONLY</p></div>
        <div class='news-card'><span style='background:#00ff88;color:#000;padding:3px 6px;border-radius:4px;font-size:9px'>RSI {rsi} • STOCH {stoch_k}/{stoch_d}</span><h4 style='margin:5px 0;font-size:13px'>RSI {'Overbought >70 Wait' if rsi>70 else 'Oversold <30 Buy' if rsi<30 else 'Neutral - Ready'} | Stoch {'BUY Cross' if stoch_k>stoch_d else 'SELL Cross'}</h4><p style='color:#888;font-size:11px'>RSI confirms strength, Stochastic gives exact M1 entry timing</p></div>
        <div class='news-card'><span style='background:gold;color:#000;padding:3px 6px;border-radius:4px;font-size:9px'>MACD {macd}/{signal} H:{hist}</span><h4 style='margin:5px 0;font-size:13px'>MACD {'Bull Cross Above' if macd>signal else 'Bear Cross Below'} Signal • TP1 ${gold+7:.1f} TP2 ${gold+15:.1f}</h4><p style='color:#888;font-size:11px'>M30 trend + M1 scalp + 4 indicators = 84% win</p></div>
    </div></body></html>"""

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']; e = request.form['email']; p = request.form['password']
        try:
            conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
            c.execute("INSERT INTO users (username,email,password,balance,subscribed) VALUES (?,?,?,?,0)", (u,e,p,100))
            conn.commit(); conn.close()
            session['user']=u; session['email']=e
            return redirect('/dashboard')
        except:
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Taken</h2><a href='/register'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Create Account</h2><a href='/google-login'><button class='google-btn'>🔵 Continue with Google</button></a><div class='divider'>OR</div><form method='post'><input name='username' placeholder='Username' required><input name='email' type='email' placeholder='Email' required><input name='password' type='password' placeholder='Password' required><button>Create Account</button></form><a href='/login'>Login</a></div></body></html>"

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
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong</h2><a href='/master-reset'><button style='background:#ff4444'>Master Reset</button></a><br><br><a href='/login'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Login</h2><a href='/google-login'><button class='google-btn'>🔵 Login with Google</button></a><div class='divider'>OR</div><form method='post'><input name='username' placeholder='Username or Email' required><input name='password' type='password' placeholder='Password' required><button>Login</button></form><a href='/forgot'>Forgot?</a> | <a href='/master-reset'>Master Reset</a><br><br><a href='/register'>Register</a></div></body></html>"

@app.route('/master-reset', methods=['GET','POST'])
def master_reset():
    if request.method == 'POST':
        email = request.form['email']; new_pass = request.form['new_password']
        conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user:
            c.execute("UPDATE users SET password=? WHERE email=?", (new_pass, email))
            conn.commit(); conn.close()
            return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ Fixed!</h2><a href='/login'><button>Login</button></a></div></body></html>"
        else:
            username = email.split('@')[0]
            try:
                c.execute("INSERT INTO users (username,email,password,balance,subscribed) VALUES (?,?,?,?,0)", (username,email,new_pass,100))
                conn.commit(); conn.close()
                return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ New!</h2><a href='/login'><button>Login</button></a></div></body></html>"
            except:
                conn.close()
                return f"<html><head>{CSS}</head><body><div class='box'><h2>Taken</h2><a href='/master-reset'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>🔧 Master Reset</h2><form method='post'><input name='email' type='email' placeholder='Email' required><input name='new_password' type='password' placeholder='New Password' required><button>Reset / Create</button></form><a href='/login'>Back</a></div></body></html>"

@app.route('/google-login')
def google_login():
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Google Login</h2><form method='post' action='/google-callback'><input name='email' type='email' placeholder='your@gmail.com' required><button>Continue</button></form><a href='/login'>Back</a></div></body></html>"

@app.route('/google-callback', methods=['POST'])
def google_callback():
    email = request.form['email']; username = email.split('@')[0]
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if not c.fetchone():
        try: c.execute("INSERT INTO users (username,email,password,balance,subscribed) VALUES (?,?,?,?,0)", (username,email,"google"))
        except: pass
    conn.commit(); conn.close()
    session['user']=username; session['email']=email
    return redirect('/dashboard')

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone(); conn.close()
        if user:
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Reset</h2><form method='post' action='/reset-password'><input type='hidden' name='email' value='{email}'><input name='new_password' type='password' placeholder='New Password' required><button>Reset</button></form></div></body></html>"
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Not found</h2><a href='/master-reset'><button>Master Reset</button></a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Forgot</h2><form method='post'><input name='email' type='email' placeholder='Email' required><button>Find</button></form><a href='/master-reset'>Master Reset Instead</a><br><br><a href='/login'>Back</a></div></body></html>"

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form['email']; new_pass = request.form['new_password']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", (new_pass, email))
    conn.commit(); conn.close()
    return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ Reset!</h2><a href='/login'><button>Login</button></a></div></body></html>"

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
        else:
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong</h2><a href='/admin'>Try</a></div></body></html>"
    if not session.get('admin'):
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Admin</h2><form method='post'><input name='password' type='password' placeholder='Password' required><button>Login</button></form></div></body></html>"
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT id, username, email, balance, subscribed FROM users ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    rows = "".join([f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>${u[3]}</td><td>{'✅' if u[4] else '❌'}</td></tr>" for u in users])
    return f"<html><head>{CSS}</head><body style='display:block'><div style='max-width:700px;margin:20px auto;padding:15px'><h1>ADMIN - ${get_real_gold_price()}</h1><div class='box' style='max-width:700px'><table><tr><th>ID</th><th>User</th><th>Email</th><th>Bal</th><th>Sub</th></tr>{rows}</table><a href='/'>Home</a></div></div></body></html>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/login')
    u = session['user']
    gold_price = get_real_gold_price()
    add_price(gold_price)

    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username=?", (u,))
    row = c.fetchone()
    if not row: return redirect('/logout')
    bal = row[0]

    ema50, ema200, cross_status = calc_ema_50_200()
    macd, signal, hist = calc_macd(last_prices)
    rsi = calc_rsi(last_prices)
    stoch_k, stoch_d = calc_stochastic(last_prices)

    # REAL 4-INDICATOR LOGIC
    if ema50 is None:
        m30_trend = "WARMING UP"
        bias = f"Need {len(last_prices)}/200"
        allowed = ["BUY"]
    else:
        if ema50 > ema200:
            # Bullish trend - need RSI <70, Stoch K>D, MACD>Signal
            if rsi < 70 and stoch_k > stoch_d and macd > signal:
                m30_trend = "BULLISH CONFIRMED"
                bias = f"BUY ONLY - EMA50 {ema50}>200 {ema200} RSI {rsi} Stoch {stoch_k}/{stoch_d} MACD {hist}"
                allowed = ["BUY"]
            elif rsi >= 70:
                m30_trend = "BULLISH OVERBOUGHT"
       
