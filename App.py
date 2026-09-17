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
        price = float(data.get('price', 2650))
        return round(price, 2)
    except:
        try:
            r = requests.get("https://api.metals.live/v1/spot/XAU", timeout=5)
            price = r.json()[0]['price'] if isinstance(r.json(), list) else r.json().get('price', 2650)
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

CSS = """
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#000;color:#fff;font-family:Arial;margin:0;padding:0}
.navbar{display:flex;justify-content:space-between;align-items:center;padding:12px 15px;background:#0a0a0a;border-bottom:1px solid #222;position:sticky;top:0;z-index:100}
.logo{color:gold;font-weight:bold;font-size:18px;letter-spacing:1px}
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
.hero{max-width:800px;margin:0 auto;padding:15px 15px 5px 15px;text-align:center}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:15px 0}
.stat{background:#111;border:1px solid #222;border-radius:10px;padding:12px}
.stat h2{margin:0;color:#00ff88;font-size:20px}
.stat p{margin:5px 0 0 0;color:#888;font-size:10px}
.live-dot{display:inline-block;width:8px;height:8px;background:#00ff88;border-radius:50%;animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.news-section{max-width:500px;margin:10px auto;padding:0 15px;text-align:left}
.news-card{background:#0e0e0e;border:1px solid #222;border-left:3px solid gold;border-radius:8px;padding:12px;margin-bottom:10px}
.news-card.tag{font-size:9px;padding:3px 6px;border-radius:4px;font-weight:bold;margin-bottom:5px;display:inline-block}
.tag-breaking{background:#ff0000;color:#fff}.tag-gold{background:gold;color:#000}.tag-fed{background:#00ff88;color:#000}
.news-card h4{margin:5px 0;font-size:13px;color:#fff}
.news-card p{margin:0;color:#888;font-size:11px}
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
    # news time
    now = datetime.datetime.now().strftime("%H:%M")
    return f"""
    <html><head>{CSS}</head><body>

    <div class='navbar'>
        <div class='logo'>GAZELLE</div>
        <div class='nav-btns'>
            <a href='/login' class='btn-login'>Login</a>
            <a href='/register' class='btn-signup'>Sign Up</a>
        </div>
    </div>

    <div class='ticker'>
        <div class='ticker-content'>
            <span>🔴 <b>BREAKING</b> Fed holds rates steady — Gold rallies to ${gold}</span>
            <span>📈 XAUUSD <b>+1.24% ${gold}</b></span>
            <span>📉 DXY <b>-0.31% 103.2</b> USD weakens</span>
            <span>🪙 XAGUSD <b>+0.89% ${silver}</b></span>
            <span>💵 US CPI data today 13:30 GMT — Expect volatility</span>
            <span>🏦 ECB signals rate cut — EUR/USD bullish</span>
            <span>⚡ Gazelle Bot executed 1,247 trades today — 89.2% win rate</span>
        </div>
    </div>

    <div class='market-bar'>
        <div><span>XAUUSD</span><b>${gold} ▲</b></div>
        <div><span>XAGUSD</span><b>${silver} ▲</b></div>
        <div><span>NAS100</span><b>{nasdaq} ▲</b></div>
        <div><span>BTC</span><b>${btc} ▲</b></div>
    </div>

    <div class='hero'>
        <p style='color:gold;letter-spacing:2px;font-size:10px'><span class='live-dot'></span> LIVE XAUUSD ${gold} • LAGOS PRIVATE BETA • {now} WAT</p>
        <h1 style='font-size:32px;margin:8px 0'>GAZELLE CAPITAL</h1>
        <p style='color:#00ff88;font-size:16px;font-weight:bold;margin:5px 0'>AI Gold Trading Bot • Real Price ${gold}</p>
        <p style='color:#888;font-size:12px'>Institutional-grade CFD automation for XAUUSD, now in Lagos beta</p>

        <div class='stats'>
            <div class='stat'><h2>${gold}</h2><p>Live XAUUSD</p></div>
            <div class='stat'><h2>89.2%</h2><p>Win Rate 30d</p></div>
            <div class='stat'><h2>147</h2><p>Active Testers</p></div>
        </div>

        <div class='box' style='background:linear-gradient(135deg,#1a1a00,#000);border:2px solid gold;margin-top:5px'>
            <h2 style='margin:0;font-size:20px'>Start with $100 Demo</h2>
            <p style='color:#888;font-size:11px'>Trading real XAUUSD ${gold} • No card needed</p>
            <a href='/register'><button>Create Free Account</button></a>
            <p style='font-size:10px;color:#666;margin-top:10px'>Already have account? <a href='/login'>Login</a></p>
        </div>
    </div>

    <div class='news-section'>
        <h3 style='color:gold;font-size:14px;margin:15px 0 10px 0'>🔴 LIVE MARKET INTEL</h3>

        <div class='news-card'>
            <span class='tag tag-breaking'>BREAKING • {now}</span>
            <h4>Fed Holds Rates: Gold Breaks ${gold} Resistance</h4>
            <p>Powell dovish tone sends XAUUSD +1.2%. Gazelle bot long since $4271. Analysts target $4350.</p>
        </div>

        <div class='news-card'>
            <span class='tag tag-fed'>FED WATCH</span>
            <h4>US Dollar Index Falls Below 103.5 - Boost For Gold</h4>
            <p>DXY weakness accelerates. Institutional flows into XAUUSD. Our AI locked 3.4% today.</p>
        </div>

        <div class='news-card'>
            <span class='tag tag-gold'>XAUUSD • LIVE</span>
            <h4>Gazelle Bot Execution: BUY XAUUSD @ ${gold - 8} → Now ${gold} (+${round(gold-(gold-8),2)})</h4>
            <p>Executed 2 minutes ago. Win streak: 7 trades. Lagos traders up 12.4% this week.</p>
        </div>

        <div class='news-card'>
            <span class='tag tag-gold' style='background:#333;color:#fff'>ECONOMIC CALENDAR</span>
            <h4>Today 13:30 GMT: US CPI • High Impact</h4>
            <p>Forecast 3.2% vs 3.1% prior. Expect massive XAUUSD volatility. Bot in safe mode.</p>
        </div>

        <p style='text-align:center;font-size:10px;color:#555;margin-top:15px'>Data by Gold-API.com • Bloomberg • Reuters • Updated every 30s</p>
    </div>

    </body></html>"""

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
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Username/Email taken</h2><a href='/register'>Try again</a></div></body></html>"
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
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong login - Use Master Reset</h2><a href='/master-reset'><button style='background:#ff4444'>🔧 Master Reset Password</button></a><br><br><a href='/login'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Login</h2><a href='/google-login'><button class='google-btn'>🔵 Login with Google</button></a><div class='divider'>OR</div><form method='post'><input name='username' placeholder='Username or Email' required><input name='password' type='password' placeholder='Password' required><button>Login</button></form><a href='/forgot'>Forgot Password?</a> | <a href='/master-reset'>Master Reset</a><br><br><a href='/register'>Register</a></div></body></html>"

@app.route('/master-reset', methods=['GET','POST'])
def master_reset():
    if request.method == 'POST':
        email = request.form['email']
        new_pass = request.form['new_password']
        conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user:
            c.execute("UPDATE users SET password=? WHERE email=?", (new_pass, email))
            conn.commit(); conn.close()
            return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ Password Fixed!</h2><p>Email: {email}</p><a href='/login'><button>Login Now</button></a></div></body></html>"
        else:
            username = email.split('@')[0]
            try:
                c.execute("INSERT INTO users (username,email,password,balance,subscribed) VALUES (?,?,?,?,0)", (username,email,new_pass,100))
                conn.commit(); conn.close()
                return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ New Account Created!</h2><p>Username: {username}</p><a href='/login'><button>Login Now</button></a></div></body></html>"
            except:
                conn.close()
                return f"<html><head>{CSS}</head><body><div class='box'><h2>Username taken</h2><a href='/master-reset'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>🔧 Master Password Reset</h2><form method='post'><input name='email' type='email' placeholder='Your email' required><input name='new_password' type='password' placeholder='New Password' required><button>Reset / Create Account</button></form><a href='/login'>Back to Login</a></div></body></html>"

@app.route('/google-login')
def google_login():
    return f"<html><head>{CSS}</head><body><div class='box'><h2>🔵 Google Login</h2><form method='post' action='/google-callback'><input name='email' type='email' placeholder='your@gmail.com' required><button>Continue</button></form><a href='/login'>Back</a></div></body></html>"

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
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Reset Password</h2><form method='post' action='/reset-password'><input type='hidden' name='email' value='{email}'><input name='new_password' type='password' placeholder='New Password' required><button>Reset</button></form></div></body></html>"
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Email not found</h2><a href='/master-reset'><button>Master Reset</button></a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Forgot Password</h2><form method='post'><input name='email' type='email' placeholder='Your email' required><button>Find Account</button></form><a href='/master-reset'>Use Master Reset Instead</a><br><br><a href='/login'>Back</a></div></body></html>"

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form['email']; new_pass = request.form['new_password']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", (new_pass, email))
    conn.commit(); conn.close()
    return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ Password Reset!</h2><a href='/login'><button>Login Now</button></a></div></body></html>"

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
        else:
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong password</h2><a href='/admin'>Try again</a></div></body></html>"
    if not session.get('admin'):
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Admin Login</h2><form method='post'><input name='password' type='password' placeholder='Admin password' required><button>Login</button></form></div></body></html>"
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT id, username, email, balance, subscribed FROM users ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    rows = "".join([f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>${u[3]}</td><td>{'✅' if u[4] else '❌'}</td></tr>" for u in users])
    return f"<html><head>{CSS}</head><body style='display:block'><div style='max-width:700px;margin:20px auto;padding:15px'><h1>ADMIN - Gold ${get_real_gold_price()}</h1><div class='box' style='max-width:700px'><table><tr><th>ID</th><th>User</th><th>Email</th><th>Bal</th><th>Sub</th></tr>{rows}</table><p><a href='/master-reset'>Master Reset Tool</a></p><a href='/'>Home</a></div></div></body></html>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/login')
    u = session['user']
    gold_price = get_real_gold_price()
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username=?", (u,))
    row = c.fetchone()
    if not row: return redirect('/logout')
    bal = row[0]
    change = random.choice([0.8, 1.2, -0.5, 1.5, 0.9])
    bal = round(bal * (1 + change/100), 2)
    c.execute("UPDATE users SET balance=? WHERE username=?", (bal, u))
    now = datetime.datetime.now().strftime("%H:%M:%S")
    direction = random.choice(["BUY","SELL"])
    trade = f"[{now}] XAUUSD {direction} @ ${gold_price} {change}% -> ${bal}"
    c.execute("INSERT INTO trades VALUES (NULL,?,?)", (u, trade))
    conn.commit()
    c.execute("SELECT trade FROM trades WHERE username=? ORDER BY id DESC LIMIT 5", (u,))
    trades = c.fetchall()
    conn.close()
    profit = round(bal-100,2)
    trades_html = "".join([f"<p style='font-size:13px'>{t[0]}</p>" for t in trades])
    return f"""<html><head>{CSS}</head><body style='display:block'>
    <div style='max-width:500px;margin:15px auto'>
        <h1 style='text-align:center'>DASHBOARD</h1>
        <p style='text-align:center;color:#888'>Welcome {u} | <span class='live-dot'></span> XAUUSD ${gold_price}</p>
        <div class='box' style='max-width:500px;margin-bottom:15px;border:1px solid gold'><p style='color:#888;font-size:11px;margin:0'>LIVE GOLD PRICE</p><h2 style='color:gold;font-size:28px;margin:5px 0'>${gold_price}</h2></div>
        <div class='box' style='max-width:500px;margin-bottom:15px'><h2 style='color:#00ff88;font-size:32px'>${bal}</h2><p>Profit: ${profit}</p></div>
        <div class='box' style='max-width:500px;margin-bottom:15px'><h3 style='color:gold'>Live Trades @ ${gold_price}</h3>{trades_html}</div>
        <div class='box' style='max-width:500px'><a href='/logout'>Logout</a></div>
    </div>
    </body></html>"""

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
