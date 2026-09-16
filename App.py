from flask import Flask, render_template_string, request, redirect, session
import sqlite3, os, random, datetime

app = Flask(__name__)
app.secret_key = "gazelle2026_production_key_change_later"

# INIT DB - PERMANENT STORAGE
def init_db():
    conn = sqlite3.connect('gazelle.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, balance REAL, profit REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (id INTEGER PRIMARY KEY, username TEXT, trade TEXT, time TEXT)''')
    conn.commit()
    conn.close()

init_db()

HTML_HOME = """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#000;color:#fff;font-family:Arial;text-align:center;padding:40px} h1{color:gold}.btn{background:gold;padding:15px 30px;border:none;border-radius:8px;font-weight:bold;color:#000}</style></head>
<body><h1>GAZELLE CAPITAL</h1><p>Algorithmic Gold Trading Company</p><p style="color:#888;font-size:13px">Lagos | Private Beta - Simulation Phase</p><br>
<a href="/register"><button class="btn">Create Demo Account - Free $100</button></a><br><br>
<a href="/login" style="color:gold">Already have account? Login</a>
<p style="color:#555;margin-top:20px;font-size:12px">Simulation Mode - No Real Money</p></body></html>
"""

HTML_DASH = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#000;color:#fff;font-family:Arial;padding:15px;margin:0}
.card{background:#151515;border:1px solid #222;padding:15px;border-radius:10px;margin:10px 0}
.gold{color:gold}.green{color:#00ff88}.btn{background:gold;color:#000;padding:12px;border:none;border-radius:8px;font-weight:bold;width:100%}
</style></head><body>
<h1 style="color:gold;text-align:center">GAZELLE DASHBOARD</h1>
<p style="text-align:center;color:#888">Welcome {{user}} | Demo Simulation</p>
<div class="card"><p>Demo Balance</p><h1 class="green">${{balance}}</h1>
<p style="font-size:12px;color:#777">Started: $100 | 2% risk per trade | XAUUSD | Profit: ${{profit}}</p></div>
<div class="card"><h3 class="gold">Live Bot Trades</h3>{% for t in trades %}<p style="font-size:13px">{{t}}</p>{% endfor %}</div>
<div class="card"><h3>Your Share (30%)</h3><p>${{share}}</p><p style="font-size:11px;color:#aaa">In real copy trading, this would be in YOUR MT5 account.</p>
<button class="btn">Subscribe to Real Signal (Coming Soon)</button></div>
<div style="text-align:center;padding:20px"><a href="/logout" style="color:#555">Logout</a></div></body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_HOME)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']; p = request.form['password']
        try:
            conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
            c.execute("INSERT INTO users (username,password,balance,profit) VALUES (?,?,100,0)", (u,p))
            conn.commit(); conn.close()
            session['user']=u
            return redirect('/dashboard')
        except:
            return "Username exists, try another"
    return '<form method="post" style="background:#000;color:#fff;padding:40px"><h2 style="color:gold">Register - Get $100 Demo</h2><input name="username" placeholder="Username" required><br><br><input name="password" type="password" placeholder="Password" required><br><br><button style="background:gold;padding:10px">Create Account</button></form>'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']; p = request.form['password']
        conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone(); conn.close()
        if user:
            session['user']=u
            return redirect('/dashboard')
        return "Wrong login"
    return '<form method="post" style="background:#000;color:#fff;padding:40px"><h2 style="color:gold">Login</h2><input name="username" placeholder="Username" required><br><br><input name="password" type="password" placeholder="Password" required><br><br><button style="background:gold;padding:10px">Login</button></form>'

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    u = session['user']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username=?", (u,))
    row = c.fetchone()
    bal = row[0] if row else 100
    # Simulate new trade
    change = random.choice([1.5, 2.0, -0.8, 2.5])
    bal = round(bal * (1 + change/100), 2)
    c.execute("UPDATE users SET balance=? WHERE username=?", (bal, u))
    now = datetime.datetime.now().strftime("%H:%M:%S")
    trade_text = f"[{now}] XAUUSD BUY {change}% -> ${bal}"
    c.execute("INSERT INTO trades (username, trade, time) VALUES (?,?,?)", (u, trade_text, now))
    conn.commit()
    c.execute("SELECT trade FROM trades WHERE username=? ORDER BY id DESC LIMIT 5", (u,))
    trades = [r[0] for r in c.fetchall()]
    conn.close()
    profit = round(bal - 100, 2)
    share = round(profit * 0.3, 2)
    return render_template_string(HTML_DASH, user=u, balance=bal, trades=trades, profit=profit, share=share)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
