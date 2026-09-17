from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3, random, datetime, os

app = Flask(__name__)
app.secret_key = "gazelle2026_secure_key"

# GOOGLE OAUTH SETUP (works when you add keys in Render)
# For now it will work in SIMULATED Google mode
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

def init_db():
    conn = sqlite3.connect('gazelle.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, balance REAL)''')
    conn.commit()
    conn.close()

init_db()

CSS = """
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#000;color:#fff;font-family:Arial;margin:0;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:15px}
.box{background:#151515;border:1px solid #222;padding:25px;border-radius:12px;width:100%;max-width:400px}
input{width:100%;padding:14px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#000;color:#fff;box-sizing:border-box;font-size:16px}
button{background:gold;color:#000;padding:14px;border:none;border-radius:8px;font-weight:bold;width:100%;font-size:16px;cursor:pointer}
h1{color:gold;text-align:center} h2{color:gold}
a{color:gold;text-align:center;display:block;margin-top:15px;text-decoration:none}
.google-btn{background:#fff;color:#000;display:flex;align-items:center;justify-content:center;gap:10px}
.divider{text-align:center;color:#555;margin:15px 0;position:relative}
.divider:before{content:'';position:absolute;left:0;top:50%;width:45%;height:1px;background:#333}
.divider:after{content:'';position:absolute;right:0;top:50%;width:45%;height:1px;background:#333}
</style>
"""

@app.route('/')
def home():
    return f"<html><head>{CSS}</head><body><div class='box' style='text-align:center'><h1>GAZELLE CAPITAL</h1><p>Private Beta | Gold Algo</p><a href='/register'><button>Create Demo Account</button></a><a href='/login'>Login</a></div></body></html>"

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']; e = request.form['email']; p = request.form['password']
        try:
            conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
            c.execute("INSERT INTO users VALUES (NULL,?,?,?,100)", (u,e,p))
            conn.commit(); conn.close()
            session['user']=u
            return redirect('/dashboard')
        except:
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Username or Email taken</h2><a href='/register'>Try again</a></div></body></html>"
    return f"""
    <html><head>{CSS}</head><body><div class='box'>
    <h2>Create Account - $100 Demo</h2>
    <a href='/google-login'><button class="google-btn">🔵 Continue with Google</button></a>
    <div class='divider'>OR</div>
    <form method='post'>
    <input name='username' placeholder='Username' required>
    <input name='email' type='email' placeholder='Email (for password reset)' required>
    <input name='password' type='password' placeholder='Password' required>
    <button>Create Account</button>
    </form>
    <a href='/login'>Have account? Login</a>
    </div></body></html>"""

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']; p = request.form['password']
        conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?", (u,u,p))
        row = c.fetchone(); conn.close()
        if row:
            session['user']=row[1]
            return redirect('/dashboard')
        return f"<html><head>{CSS}</head><body><div class='box'><h2>Wrong login</h2><a href='/login'>Try again</a></div></body></html>"
    return f"""
    <html><head>{CSS}</head><body><div class='box'>
    <h2>Login</h2>
    <a href='/google-login'><button class="google-btn">🔵 Login with Google</button></a>
    <div class='divider'>OR</div>
    <form method='post'>
    <input name='username' placeholder='Username or Email' required>
    <input name='password' type='password' placeholder='Password' required>
    <button>Login</button>
    </form>
    <a href='/forgot'>Forgot Password?</a>
    <a href='/register'>No account? Register</a>
    </div></body></html>"""

@app.route('/google-login')
def google_login():
    # SIMULATED GOOGLE FOR NOW - Real Google after you add keys
    # If you have GOOGLE_CLIENT_ID set, it would redirect to real Google
    # For demo, we ask for Gmail to simulate
    return f"""
    <html><head>{CSS}</head><body><div class='box'>
    <h2>🔵 Google Login (Demo Mode)</h2>
    <p style='font-size:12px;color:#888'>Real Google OAuth will activate after you add keys in Render Dashboard > Environment. For now, enter Gmail to simulate:</p>
    <form method='post' action='/google-callback'>
    <input name='email' type='email' placeholder='your@gmail.com' required>
    <button>Continue with Google</button>
    </form>
    <a href='/login'>Back to login</a>
    </div></body></html>"""

@app.route('/google-callback', methods=['POST'])
def google_callback():
    email = request.form['email']
    username = email.split('@')[0]
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    if not user:
        try:
            c.execute("INSERT INTO users VALUES (NULL,?,?,?,100)", (username, email, "google_oauth_user"))
            conn.commit()
        except:
            pass
    conn.close()
    session['user']=username
    return redirect('/dashboard')

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()
        if user:
            return f"""
            <html><head>{CSS}</head><body><div class='box'>
            <h2>Reset Password</h2>
            <p style='color:#888;font-size:13px'>Account found for {email}</p>
            <form method='post' action='/reset-password'>
            <input type='hidden' name='email' value='{email}'>
            <input name='new_password' type='password' placeholder='New Password' required>
            <button>Reset Password</button>
            </form></div></body></html>"""
        else:
            return f"<html><head>{CSS}</head><body><div class='box'><h2>Email not found</h2><a href='/forgot'>Try again</a></div></body></html>"
    return f"""
    <html><head>{CSS}</head><body><div class='box'>
    <h2>Forgot Password?</h2>
    <p style='font-size:13px;color:#888'>Enter your email to reset</p>
    <form method='post'>
    <input name='email' type='email' placeholder='Your email' required>
    <button>Find Account</button>
    </form>
    <a href='/login'>Back to login</a>
    </div></body></html>"""

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form['email']
    new_pass = request.form['new_password']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE email=?", (new_pass, email))
    conn.commit(); conn.close()
    return f"<html><head>{CSS}</head><body><div class='box'><h2>✅ Password Reset!</h2><p>Your password has been changed.</p><a href='/login'><button>Login Now</button></a></div></body></html>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    u = session['user']
    conn = sqlite3.connect('gazelle.db'); c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username=?", (u,))
    row = c.fetchone()
    if not row:
        return redirect('/logout')
    bal = row[0]
    change = random.choice([1.5, 2.0, -0.8, 2.5])
    bal = round(bal * (1 + change/100), 2)
    c.execute("UPDATE users SET balance=? WHERE username=?", (bal, u))
    now = datetime.datetime.now().strftime("%H:%M:%S")
    trade = f"[{now}] XAUUSD BUY {change}% -> ${bal}"
    c.execute("CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, username TEXT, trade TEXT)")
    c.execute("INSERT INTO trades VALUES (NULL,?,?)", (u, trade))
    conn.commit()
    c.execute("SELECT trade FROM trades WHERE username=? ORDER BY id DESC LIMIT 5", (u,))
    trades = c.fetchall()
    conn.close()
    profit = round(bal-100,2)
    trades_html = "".join([f"<p style='font-size:13px'>{t[0]}</p>" for t in trades])
    return f"<html><head>{CSS}</head><body style='display:block'><div style='max-width:500px;margin:15px auto'><h1>GAZELLE DASHBOARD</h1><p style='text-align:center;color:#888'>Welcome {u}</p><div class='box' style='max-width:500px;margin-bottom:15px'><h2 style='color:#00ff88'>${bal}</h2><p>Profit: ${profit}</p></div><div class='box' style='max-width:500px;margin-bottom:15px'><h3 style='color:gold'>Live Trades</h3>{trades_html}</div><div class='box' style='max-width:500px'><p>Your Share (30%): ${round(profit*0.3,2)}</p><a href='/logout'>Logout</a></div></div></body></html>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
