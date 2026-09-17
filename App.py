from flask import Flask, request, redirect, session
import sqlite3, random, datetime, os
import requests

app = Flask(__name__)
app.secret_key = "gazelle2026_secure"
ADMIN_PASSWORD = "gazelleadmin123"

def get_real_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=3)
        price = float(r.json().get('price', 4292))
        return round(price, 2)
    except:
        return round(random.uniform(4285, 4305),2)

def init_db():
    conn = sqlite3.connect('gazelle.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, balance REAL, subscribed INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, username TEXT, trade TEXT)''')
    conn.commit()
    conn.close()

init_db()

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
            cross = "GOLDEN CROSS BUY"
        elif ema50_prev >= ema200_prev and ema50 < ema200:
            cross = "DEATH CROSS SELL"
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
.btn-login{border:1px solid gold;color:gold;background:transparent;padding:8px 18px;border-radius:20px;font-weight:bold;font-size:13px;text-decoration:none}
.btn-signup{background:gold;color:#000;padding:8px 18px;border-radius:20px;font-weight:bold;font-size:13px;text-decoration:none}
.box{background:#151515;border:1px solid #222;padding:20px;border-radius:12px;width:100%;max-width:420px;margin:12px auto;box-sizing:border-box}
input{width:100%;padding:14px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#000;color:#fff;box-sizing:border-box;font-size:16px}
button{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:100%;font-size:16px;cursor:pointer}
h1{color:gold;text-align:center} h2{color:gold}
a{color:gold;text-decoration:none}
.hero{max-width:800px;margin:0 auto;padding:15px;text-align:center}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;margin:15px 0}
.stat{background:#111;border:1px solid #222;border-radius:10px;padding:10px}
.stat h2{margin:0;color:#00ff88;font-size:14px}
.stat p{margin:4px 0 0 0;color:#888;font-size:9px}
</style>
"""

@app.route('/')
def home():
    gold = get_real_gold_price()
    add_price(gold)
    ema50, ema200, cross = calc_ema_50_200()
    macd, signal, hist = calc_macd(last_prices)
    rsi = calc_rsi(last_prices)
    stoch_k, stoch_d = calc_stochastic(last_prices)
    ema50_txt = ema50 if ema50 else 0
    ema200_txt = ema200 if ema200 else 0

    html = """
    <html><head>""" + CSS + """</head><body>
    <div class='navbar'><div class='logo'>GAZELLE</div><div><a href='/login' class='btn-login'>Login</a> <a href='/register' class='btn-signup'>Sign Up</a></div></div>
    <div style='background:#111;padding:8px;text-align:center;font-size:11px;color:#ccc'>XAUUSD $""" + str(gold) + """ | """ + cross + """ | RSI """ + str(rsi) + """ | STOCH """ + str(stoch_k) + """/""" + str(stoch_d) + """ | MACD """ + str(hist) + """</div>
    <div class='hero'>
        <h1>GAZELLE CAPITAL</h1>
        <p style='color:#00ff88;font-size:12px;font-weight:bold'>EMA50/200 + RSI + STOCH + MACD - M30/M1 Day Trading</p>
        <div class='stats'>
            <div class='stat'><h2>$""" + str(gold) + """</h2><p>XAUUSD</p></div>
            <div class='stat'><h2>""" + str(rsi) + """</h2><p>RSI</p></div>
            <div class='stat'><h2>""" + str(stoch_k) + """/""" + str(stoch_d) + """</h2><p>STOCH</p></div>
            <div class='stat'><h2>""" + str(hist) + """</h2><p>MACD Hist</p></div>
        </div>
        <div class='box' style='border:2px solid gold'>
            <h2>EMA50 """ + str(ema50_txt) + """ / EMA200 """ + str(ema200_txt) + """</h2>
            <p style='color:gold'>""" + cross + """</p>
            <a href='/register'><button>Create Free Account</button></a>
            <p style='font-size:10px;color:#666;margin-top:10px'>Have account? <a href='/login'>Login</a></p>
        </div>
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
            c.execute("INSERT INTO users (username,email,password,balance,subscribed) VALUES (?,?,?,?,0)", (u,e,p,100))
            conn.commit(); conn.close()
            session['user']=u; session['email']=e
            return redirect('/dashboard')
        except:
            return "<html><head>" + CSS + "</head><body><div class='box'><h2>Taken</h2><a href='/register'>Try again</a></div></body></html>"
    return "<html><head>" + CSS + "</head><body><div class='box'><h2>Create Account</h2><form method='post'><input name='username' placeholder='Username' required><input name='email' type='email' placeholder='Email' required><input name='password' type='password' placeholder='Password' required><button>Create Account</button></form><a href='/login'>Login</a></div></body></html>"

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
        return "<html><head>" + CSS + "</head><body><div class='box'><h2>Wrong login</h2><a href='/master-reset'><button style='background:#ff4444'>Master Reset</button></a><br><br><a href='/login'>Try again</a></div></body></html>"
    return "<html><head>" + CSS + "</head><body><div class='box'><h2>Login</h2><form method='post'><input name='username' placeholder='Username or Email' required><input name='password' type='password' placeholder='Password' required><button>Login</button></form><a href='/forgot'>Forgot?</a> | <a href='/master-reset'>Master Reset</a><br><br><a href='/register'>Register</a></div></body></html>"

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
            return "<html><head>" + CSS + "</head><body><div class='box'><h2>Fixed!</h2><a href='/login'><button>Login</button></a></div></body></html>"
        else:
            username = email.split('@')[0]
            try:
                c.execute("INSERT INTO users (username,email,password,balance,subscribed) VALUES (?,?,?,?,0)", (username,email,new_pass,100))
                conn.commit(); conn.close()
                return "<html><head>" + CSS + "</head><body><div class='box'><h2>New Account!</h2><a href='/login'><button>Login</button></a></div></body></html>"
            except:
                conn.close()
                return "<html><head>" + CSS + "</head><body><div class='box'><h2>Taken</h2><a href='/master-reset'>Try again</a></div></body></html>"
    return "<html><head>" + CSS + "</head><body><div class='box'><h2>Master Reset</h2><form method='post'><input name='email' type='email' placeholder='Email' required><input name='new_password' type='password' placeholder='New Password' required><button>Reset / Create</button></form><a href='/login'>Back</a></div></body></html>"

@app.route('/google-login')
def google_login():
    return "<html><head>" + CSS + "</head><body><div class='box'><h2>Google Login</h2><form method='post' action='/google-callback'><input name='email' type='email' placeholder='your@gmail.com' required><button>Continue</button></form><a href='/login'>Back</a></div></body></html>"

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
            return "<html><head>" + CSS + "</head><body><div class='box'><h2>Reset</h2><form method='post' action='/reset-password'><input type='hidden' name='email' value='" + email + "'><input name='new_password' type='password' placeholder='New Password' required><button>Reset</button></form></div></body></html>"
        return "<html><head>" + CSS + "</head><body><div class='box'><h2>Not found</h2><a href='/master-reset'><button>Master Reset</button></a></div></body></html>"
    return "<html><head>" + CSS + "</head><body><div class='box'><h2>Forgot</h2><form method='post'><input name='email' type='email' placeholder='Email' required><button>Find</button></form><a href='/master-reset'>Master Reset Instead</a><br><br><a href='/login'>Back</a></div></body></html>"

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form['email']; new_pass = request.form['new_password']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", (new_pass, email))
    conn.commit(); conn.close()
    return "<html><head>" + CSS + "</head><body><div class='box'><h2>Reset OK!</h2><a href='/login'><button>Login</button></a></div></body></html>"

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
        else:
            return "<html><head>" + CSS + "</head><body><div class='box'><h2>Wrong</h2><a href='/admin'>Try</a></div></body></html>"
    if not session.get('admin'):
        return "<html><head>" + CSS + "</head><body><div class='box'><h2>Admin</h2><form method='post'><input name='password' type='password' placeholder='Password' required><button>Login</button></form></div></body></html>"
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT id, username, email, balance FROM users ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    rows = "".join(["<tr><td>" + str(u[0]) + "</td><td>" + str(u[1]) + "</td><td>" + str(u[2]) + "</td><td>$" + str(u[3]) + "</td></tr>" for u in users])
    return "<html><head>" + CSS + "</head><body style='display:block'><div style='max-width:700px;margin:20px auto;padding:15px'><h1>ADMIN</h1><div class='box' style='max-width:700px'><table style='width:100%;border-collapse:collapse'><tr><th>ID</th><th>User</th><th>Email</th><th>Bal</th></tr>" + rows + "</table><a href='/'>Home</a></div></div></body></html>"

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

    if ema50 is None:
        m30_trend = "WARMING UP"
        bias = "Need " + str(len(last_prices)) + "/200"
        allowed = ["BUY"]
    else:
        if ema50 > ema200:
            if rsi < 70 and stoch_k > stoch_d and macd > signal:
                m30_trend = "BULLISH CONFIRMED"
                bias = "BUY ONLY"
                allowed = ["BUY"]
            elif rsi >= 70:
                m30_trend = "OVERBOUGHT"
                bias = "WAIT RSI " + str(rsi)
                allowed = []
            else:
                m30_trend = "WAITING"
                bias = "WAIT STOCH"
                allowed = []
        else:
            if rsi > 30 and stoch_k < stoch_d and macd < signal:
                m30_trend = "BEARISH CONFIRMED"
                bias = "SELL ONLY"
                allowed = ["SELL"]
            else:
                m30_trend = "WAITING"
                bias = "WAIT"
                allowed = []

    if not allowed:
        direction = "NO TRADE"
        change = 0
        tp_info = "RSI " + str(rsi) + " STOCH " + str(stoch_k) + "/" + str(stoch_d) + " MACD " + str(macd)
        status = "WAIT"
    else:
        direction = allowed[0]
        win = random.random() < 0.84
        if win:
            change = random.uniform(0.8, 1.7)
            tp_info = "TP1 HIT TP2 HIT"
            status = "WIN"
        else:
            change = random.uniform(-0.5, -0.2)
            tp_info = "SL HIT"
            status = "LOSS"

    if change!= 0:
        bal = round(bal * (1 + change/100), 2)
        c.execute("UPDATE users SET balance=? WHERE username=?", (bal, u))

    now = datetime.datetime.now().strftime("%H:%M:%S")
    trade = "[" + now + "] " + status + " " + cross_status + " EMA50 " + str(ema50) + "/200 " + str(ema200) + " RSI " + str(rsi) + " STOCH " + str(stoch_k) + "/" + str(stoch_d) + " MACD " + str(macd) + "/" + str(signal) + " H:" + str(hist) + " | M30:" + m30_trend + " M1 " + direction + " @ $" + str(gold_price) + " " + str(round(change,2)) + "% -> $" + str(bal)
    if change!= 0:
        c.execute("INSERT INTO trades VALUES (NULL,?,?)", (u, trade))
        conn.commit()
    c.execute("SELECT trade FROM trades WHERE username=? ORDER BY id DESC LIMIT 10", (u,))
    trades = c.fetchall()
    conn.close()

    trades_html = "".join(["<p style='font-size:9px;margin:6px 0;padding:8px;background:#111;border-left:3px solid #00ff88;border-radius:4px;word-break:break-all'>" + t[0] + "</p>" for t in trades])

    page = """
    <html><head>""" + CSS + """</head><body style='display:block'>
    <div style='max-width:500px;margin:15px auto'>
        <h1 style='text-align:center'>4-INDICATOR EXPERT</h1>
        <p style='text-align:center;color:#888'>$""" + str(gold_price) + """ | """ + now + """</p>
        <div class='box'><p style='font-size:10px'>EMA50 """ + str(ema50) + """ / EMA200 """ + str(ema200) + """<br>RSI """ + str(rsi) + """ STOCH """ + str(stoch_k) + """/""" + str(stoch_d) + """ MACD """ + str(hist) + """</p><p style='color:gold;font-size:11px'>""" + cross_status + """ - """ + bias + """</p></div>
        <div class='box'><h2 style='color:#00ff88;font-size:32px;margin:0'>$""" + str(bal) + """</h2><p>""" + m30_trend + """ | """ + direction + """</p></div>
        <div class='box'><h3 style='color:gold'>Trade Log</h3>""" + trades_html + """</div>
        <div class='box'><a href='/logout'>Logout</a> | <a href='/'>Home</a></div>
    </div></body></html>
    """
    return page

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 
