from flask import Flask, render_template_string, request, redirect, session, url_for
import random, datetime, os

app = Flask(__name__)
app.secret_key = "gazelle2026_secret_key_lagos"

# SIMULATED DATABASE - in real version we use MongoDB/Postgres
# For now, users are stored in memory (resets when Render sleeps - that's okay for demo)
users_db = {} # email : {password, balance, joined}
trades_global = []

# HTML TEMPLATES
HOME_HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#000;color:#fff;font-family:Arial;text-align:center;padding:20px;margin:0}
.card{background:#151515;border:1px solid #222;padding:20px;border-radius:12px;margin:20px auto;max-width:400px}
.gold{color:gold}.green{color:#00ff88}
.btn{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:100%;cursor:pointer;margin:5px 0}
input{width:90%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #333;background:#111;color:#fff}
h1{color:gold} a{color:gold;text-decoration:none}
</style></head><body>
<h1>GAZELLE CAPITAL</h1>
<p>Algorithmic Gold Trading | Lagos, Nigeria</p>
<p style="color:#888;font-size:12px;">SIMULATION PHASE - No Real Money</p>
<div class="card">
<h3>Create Demo Account</h3>
<p style="font-size:12px;color:#aaa;">Get $100 simulated funds instantly</p>
<a href="/register"><button class="btn">Register Free</button></a>
<a href="/login"><button class="btn" style="background:#222;color:#fff;border:1px solid gold;">Login</button></a>
</div>
<div class="card" style="font-size:12px;color:#777;">
<p>Bot: XAUUSD | Risk: 2% | Performance Fee: 30%</p>
<p>After simulation, real copy trading via your own MT5.</p>
</div>
</body></html>
"""

REGISTER_HTML = """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#000;color:#fff;font-family:Arial;text-align:center;padding:20px}.card{background:#151515;padding:20px;border-radius:12px;max-width:400px;margin:auto} input{width:90%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #333;background:#111;color:#fff}.btn{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:95%} a{color:gold}</style></head>
<body><h1 style="color:gold;">Register</h1>
<div class="card">
<form method="POST">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button class="btn">Create Account + Get $100 Demo</button>
</form>
<p style="font-size:12px;margin-top:15px;"><a href="/login">Already have account? Login</a></p>
</div></body></html>
"""

LOGIN_HTML = """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{background:#000;color:#fff;font-family:Arial;text-align:center;padding:20px}.card{background:#151515;padding:20px;border-radius:12px;max-width:400px;margin:auto} input{width:90%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #333;background:#111;color:#fff}.btn{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:95%} a{color:gold}</style></head>
<body><h1 style="color:gold;">Login</h1>
<div class="card">
<form method="POST">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button class="btn">Login to Dashboard</button>
</form>
<p style="font-size:12px;margin-top:15px;color:#ff5555;">{{msg}}</p>
<p style="font-size:12px;margin-top:15px;"><a href="/register">No account? Register</a></p>
</div></body></html>
"""

DASH_HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#000;color:#fff;font-family:Arial;padding:15px;margin:0}
.card{background:#151515;border:1px solid #222;padding:15px;border-radius:10px;margin:10px 0}
.gold{color:gold}.green{color:#00ff88}
.btn{background:gold;color:#000;padding:12px;border:none;border-radius:8px;font-weight:bold;width:100%;margin:5px 0}
h1{color:gold;text-align:center}.small{font-size:11px;color:#777}
</style></head><body>
<h1>GAZELLE DASHBOARD</h1>
<p style="text-align:center;color:#888;">Welcome {{email}} | Demo Account</p>
<div class="card">
<p>Demo Balance</p>
<h1 class="green">${{balance}}</h1>
<p class="small">Started: $100 | Joined: {{joined}} | Bot: XAUUSD 2% risk</p>
</div>
<div class="card">
<h3 class="gold">Live Bot Trades</h3>
{% for t in trades %}
<p style="font-size:12px;">{{t}}</p>
{% endfor %}
</div>
<div class="card">
<h3>Your Simulated Profit</h3>
<p>Profit: ${{profit}} | Your Share (30% demo): ${{investor_share}}</p>
<p class="small">In real version, this would be in YOUR MT5 account (Exness/XM).</p>
<button class="btn">Subscribe to Real Signal - Coming Soon</button>
<a href="/logout"><button class="btn" style="background:#222;color:#fff;">Logout</button></a>
</div>
<div style="text-align:center;padding:10px;"><a href="/" style="color:#555;font-size:11px;">© 2026 Gazelle Capital - Simulation Only</a></div>
</body></html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password']
        if email in users_db:
            return "Email already exists. <a href='/login'>Login</a>"
        users_db[email] = {
            "password": password,
            "balance": 100.0,
            "joined": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        session['email'] = email
        return redirect('/dashboard')
    return render_template_string(REGISTER_HTML)

@app.route('/login', methods=['GET','POST'])
def login():
    msg = ""
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password']
        user = users_db.get(email)
        if user and user['password'] == password:
            session['email'] = email
            return redirect('/dashboard')
        else:
            msg = "Wrong email or password"
    return render_template_string(LOGIN_HTML, msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect('/login')
    email = session['email']
    user = users_db.get(email)
    if not user:
        return redirect('/login')

    # Simulate a trade on each refresh
    change = random.choice([1.5, 2.0, -0.8, 2.5, 1.2, -0.5])
    user['balance'] = round(user['balance'] * (1 + change/100), 2)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    trades_global.insert(0, f"[{now}] XAUUSD BUY +{change}% -> Demo Balance ${user['balance']}")

    profit = round(user['balance'] - 100, 2)
    investor_share = round(profit * 0.3, 2) if profit > 0 else 0
    return render_template_string(DASH_HTML, email=email, balance=user['balance'], joined=user['joined'], trades=trades_global[:5], profit=profit, investor_share=investor_share)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 
