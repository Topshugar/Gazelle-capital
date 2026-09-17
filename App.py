from flask import Flask, request, redirect, session
import sqlite3, random, datetime

app = Flask(__name__)
app.secret_key = "gazelle2026_secure"

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
.box{background:#151515;border:1px solid #222;padding:25px;border-radius:12px;width:100%;max-width:420px;margin:15px auto;box-sizing:border-box}
input{width:100%;padding:14px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#000;color:#fff;box-sizing:border-box;font-size:16px}
button{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:100%;font-size:16px;cursor:pointer}
h1{color:gold;text-align:center} h2{color:gold} h3{color:#fff}
a{color:gold;text-decoration:none}
.google-btn{background:#fff;color:#000;display:flex;align-items:center;justify-content:center;gap:10px}
.divider{text-align:center;color:#555;margin:15px 0;position:relative}
.divider:before{content:'';position:absolute;left:0;top:50%;width:45%;height:1px;background:#333}
.divider:after{content:'';position:absolute;right:0;top:50%;width:45%;height:1px;background:#333}
.price{border:2px solid gold;background:#1a1a00;padding:15px;border-radius:10px;text-align:center;margin:15px 0}
.hero{max-width:800px;margin:0 auto;padding:30px 15px;text-align:center}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin:20px 0}
.stat{background:#111;border:1px solid #222;border-radius:10px;padding:15px}
.stat h2{margin:0;color:#00ff88;font-size:22px}
.stat p{margin:5px 0 0 0;color:#888;font-size:11px}
.badge{display:inline-block;background:#111;border:1px solid #333;border-radius:20px;padding:5px 12px;font-size:11px;margin:3px;color:#888}
.proof{background:#0a0a0a;border-left:3px solid gold;padding:12px;margin:10px 0;border-radius:5px;text-align:left;font-size:13px}
</style>
"""

@app.route('/')
def home():
    return f"""
    <html><head>{CSS}</head><body>
    <div class='hero'>
        <p style='color:gold;letter-spacing:3px;font-size:11px'>LAGOS • PRIVATE BETA</p>
        <h1 style='font-size:36px;margin:10px 0'>GAZELLE CAPITAL</h1>
        <p style='color:#00ff88;font-size:18px;font-weight:bold'>+127.4% Gold Bot • Last 30 Days</p>
        <p style='color:#888;font-size:13px;max-width:500px;margin:10px auto'>We built an XAUUSD bot that turns $100 to $227. Now opening private beta for 50 Lagos investors.</p>

        <div class='stats'>
            <div class='stat'><h2>$12,430</h2><p>Total Profit Simulated</p></div>
            <div class='stat'><h2>89.2%</h2><p>Win Rate</p></div>
            <div class='stat'><h2>147</h2><p>Active Testers</p></div>
        </div>

        <div style='margin:15px 0'>
            <span class='badge'>📍 Yaba, Lagos</span>
            <span class='badge'>🤖 XAUUSD Specialist</span>
            <span class='badge'>🔒 Non-Custodial</span>
            <span class='badge'>✓ Flutterwave Verified</span>
        </div>

        <div class='box' style='text-align:left'>
            <h3 style='margin-top:0;color:gold'>Live Proof (Simulation)</h3>
            <div class='proof'>[09:41:22] XAUUSD BUY +2.4% → $104.20 <span style='float:right;color:#00ff88'>WIN</span></div>
            <div class='proof'>[09:38:11] XAUUSD SELL +1.8% → $101.80 <span style='float:right;color:#00ff88'>WIN</span></div>
            <div class='proof'>[09:32:05] XAUUSD BUY -0.8% → $100.00 <span style='float:right;color:#ff4444'>LOSS</span></div>
            <p style='font-size:10px;color:#555;text-align:center;margin-top:10px'>* Simulation data for demo purposes - not financial advice</p>
        </div>

        <div class='box' style='background:linear-gradient(135deg,#1a1a00,#000);border:2px solid gold'>
            <h2 style='margin:0'>Start with $100 Demo</h2>
            <p style='color:#888;font-size:12px'>See bot trading live in your dashboard</p>
            <a href='/register'><button>Create Free Account</button></a>
            <a href='/login' style='display:block;margin-top:12px;font-size:13px'>Already have account? Login →</a>
        </div>

        <p style='color:#555;font-size:11px;margin-top:30px'>Built in Lagos • For Gold Traders • Private Beta 2026<br>Questions? DM @gazellecapital on X</p>
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
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Create Account - $100 Demo</h2><a href='/google-login'><button class='google-btn'>🔵 Continue with Google</button></a><div class='divider'>OR</div><form method='post'><input name='username' placeholder='Username' required><input name='email' type='email' placeholder='Email' required><input name='password' type='password' placeholder='Password' required><button>Create Account</button></form><a href='/login'>Login</a><a href='/'>← Back to Home</a></div></body></html>"

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
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong login</h2><a href='/login'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Login</h2><a href='/google-login'><button class='google-btn'>🔵 Login with Google</button></a><div class='divider'>OR</div><form method='post'><input name='username' placeholder='Username or Email' required><input name='password' type='password' placeholder='Password' required><button>Login</button></form><a href='/forgot'>Forgot Password?</a><a href='/register'>Register</a><a href='/'>← Home</a></div></body></html>"

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
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Email not found</h2><a href='/forgot'>Try again</a></div></body></html>"
    return f"<html><head>{CSS}</head><body><div class='box'><h2>Forgot Password</h2><form method='post'><input name='email' type='email' placeholder='Your email' required><button>Find Account</button></form><a href='/login'>Back</a></div></body></html>"

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form['email']; new_pass = request.form['new_password']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", (new_pass, email))
    conn.commit(); conn.close()
    return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ Password Reset!</h2><a href='/login'><button>Login Now</button></a></div></body></html>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/login')
    u = session['user']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT balance, subscribed FROM users WHERE username=?", (u,))
    row = c.fetchone()
    if not row: return redirect('/logout')
    bal, sub = row
    change = random.choice([1.5, 2.0, -0.8, 2.5])
    bal = round(bal * (1 + change/100), 2)
    c.execute("UPDATE users SET balance=? WHERE username=?", (bal, u))
    now = datetime.datetime.now().strftime("%H:%M:%S")
    trade = f"[{now}] XAUUSD BUY {change}% -> ${bal}"
    c.execute("INSERT INTO trades VALUES (NULL,?,?)", (u, trade))
    conn.commit()
    c.execute("SELECT trade FROM trades WHERE username=? ORDER BY id DESC LIMIT 5", (u,))
    trades = c.fetchall()
    conn.close()
    profit = round(bal-100,2)
    trades_html = "".join([f"<p style='font-size:13px'>{t[0]}</p>" for t in trades])
    return f"<html><head>{CSS}</head><body style='display:block'><div style='max-width:500px;margin:15px auto'><h1>GAZELLE DASHBOARD</h1><p style='text-align:center;color:#888'>Welcome {u}</p><div class='box' style='max-width:500px;margin-bottom:15px'><h2 style='color:#00ff88'>${bal}</h2><p>Profit: ${profit}</p></div><div class='box' style='max-width:500px;margin-bottom:15px'><h3 style='color:gold'>Live Trades</h3>{trades_html}</div><div class='box' style='max-width:500px'><p>Share (30%): ${round(profit*0.3,2)}</p><a href='/'><button style='background:#333;color:#fff'>Home</button></a><a href='/logout'>Logout</a></div></div></body></html>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
