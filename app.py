import os
import random
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v5_2026_final"

users = {
    "admin@gazelle.com": {
        "password": "admin123",
        "vip": True,
        "equity": 5000,
        "mt_account": {"login": "123456", "server": "Exness-MT5Real", "type": "MT5"},
        "bot_active": True
    }
}

def calculate_signal(symbol):
    rsi = random.randint(25, 75)
    alligator_status = random.choice(["ALIGNED_BULL", "ALIGNED_BEAR", "SLEEPING"])
    bb_position = random.choice(["LOWER_TOUCH", "UPPER_TOUCH", "MIDDLE"])
    signal = "HOLD"
    if bb_position == "LOWER_TOUCH" and rsi < 40 and alligator_status == "ALIGNED_BULL":
        signal = "BUY"
    elif bb_position == "UPPER_TOUCH" and rsi > 60 and alligator_status == "ALIGNED_BEAR":
        signal = "SELL"
    return {
        "symbol": symbol,
        "price": round(random.uniform(1.08, 3000), 2),
        "rsi": rsi,
        "alligator": alligator_status,
        "bb": bb_position,
        "signal": signal,
        "sl": 1.5,
        "tp": 2.5,
        "timeframe": "1D",
        "updated": datetime.utcnow().strftime("%Y-%m-%d")
    }

def calculate_lot(equity, sl_distance_usd=15):
    equity = float(equity)
    if equity < 500:
        risk_percent = 0.5
        max_trades = 1
    elif equity < 2000:
        risk_percent = 1.0
        max_trades = 2
    else:
        risk_percent = 1.5
        max_trades = 3
    risk_amount = equity * (risk_percent / 100)
    lot = risk_amount / max(sl_distance_usd, 1)
    lot = max(0.01, round(lot, 2))
    return {"lot": lot, "risk_amount": round(risk_amount, 2), "risk_percent": risk_percent, "max_trades": max_trades}

FREE_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "GBPJPY"]
VIP_ASSETS = ["XAUUSD", "USOIL", "UKOIL", "XPTUSD", "XAGUSD"]

HTML_BASE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://s3.tradingview.com/tv.js"></script><style>body{font-family:Inter,sans-serif;background:#f6f7f9;margin:0;color:#0a1931}.nav{background:#0a1931;padding:14px 20px;display:flex;justify-content:space-between;color:white}.nav a{color:#f7c948;text-decoration:none;margin-left:15px}.card{background:white;border-radius:16px;padding:18px;margin:12px;box-shadow:0 4px 12px rgba(0,0,0,0.06)}.btn{background:#0a1931;color:#f7c948;padding:10px 18px;border-radius:10px;border:none;cursor:pointer}.btn-gold{background:#f7c948;color:#0a1931;font-weight:700}.badge{padding:4px 8px;border-radius:6px;font-size:12px}.badge-buy{background:#d1fae5;color:#065f46}.badge-sell{background:#fee2e2;color:#991b1b}.blur{filter:blur(6px);pointer-events:none}</style></head><body><div class="nav"><div>🦌 Gazelle Capital</div><div><a href="/">Home</a><a href="/signals">Signals</a><a href="/analysis">Analysis</a><a href="/bot">Bot</a>{% if 'user' in session %}<a href="/logout">Logout</a>{% else %}<a href="/login">Login</a>{% endif %}</div></div>{{content|safe}}</body></html>"""

@app.route("/")
def home():
    user = users.get(session.get("user"))
    vip = user and user.get("vip")
    free_signals = [calculate_signal(s) for s in FREE_PAIRS[:3]]
    content = f"<div class='card'><h2>{'VIP Dashboard 🦌' if vip else 'Free Forex Alerts (1D Swing)'} - RSI+Alligator+BB</h2></div>"
    for sig in free_signals:
        content += f"<div class='card'><b>{sig['symbol']}</b> <span class='badge'>{sig['signal']}</span> RSI:{sig['rsi']} Alligator:{sig['alligator']}</div>"
    if not vip:
        content += "<div class='card' style='border:2px solid #f7c948'><h3>Unlock VIP Swing Bot - Equity Based</h3><p>Gold, US Oil WTI, UK Brent, Platinum, Silver XAG auto-trade based on YOUR equity.</p><a href='https://flutterwave.com/pay/msjgnmx4gehc' class='btn btn-gold'>Subscribe $10/mo</a><br><br><a href='/activate-vip'>I have paid - Activate</a></div>"
    else:
        eq = user.get("equity", 1000)
        content += f"<div class='card'><h3>Equity: ${eq} | Mature Risk Active</h3></div>"
        for sym in VIP_ASSETS:
            sig = calculate_signal(sym)
            lot = calculate_lot(eq)
            content += f"<div class='card'><b>{sym} VIP</b> {sig['signal']} @ {sig['price']} | Lot for you: {lot['lot']} Risk ${lot['risk_amount']}</div>"
    return render_template_string(HTML_BASE, content=content)

@app.route("/signals")
def signals_page():
    user = users.get(session.get("user"))
    vip = user and user.get("vip")
    content = "<div class='card'><h2>Signals - 1D Swing</h2></div><h3 style='margin-left:12px'>Free Forex (Alert Only)</h3>"
    for s in FREE_PAIRS:
        sig = calculate_signal(s)
        content += f"<div class='card'><b>{s}</b> {sig['signal']} @ {sig['price']} RSI {sig['rsi']}</div>"
    content += "<h3 style='margin-left:12px'>VIP Metals & Oil (Auto Trade Equity Based)</h3>"
    blur = "" if vip else "blur"
    for s in VIP_ASSETS:
        sig = calculate_signal(s)
        content += f"<div class='card {blur}'><b>{s}</b> {sig['signal']} SL {sig['sl']}% TP {sig['tp']}%</div>"
    return render_template_string(HTML_BASE, content=content)

@app.route("/analysis")
def analysis():
    content = """<div class="card"><h2>Analysis - 1D</h2><select id="pairSelect" onchange="loadChart()"><option value="FX:EURUSD">EURUSD Free</option><option value="OANDA:XAUUSD">Gold VIP</option><option value="TVC:USOIL">US Oil VIP</option><option value="TVC:UKOIL">UK Brent VIP</option><option value="OANDA:XPTUSD">Platinum VIP</option><option value="OANDA:XAGUSD">Silver VIP</option></select><div id="tvchart" style="height:500px;margin-top:10px"></div></div><script>function loadChart(){let sym=document.getElementById('pairSelect').value; new TradingView.widget({autosize:true,symbol:sym,interval:"D",theme:"light",container_id:"tvchart",studies:["RSI@tv-basicstudies","BollingerBands@tv-basicstudies"]});}loadChart();</script>"""
    return render_template_string(HTML_BASE, content=content)

@app.route("/bot", methods=["GET", "POST"])
def bot():
    if "user" not in session:
        return redirect("/login")
    user = users[session["user"]]
    if request.method == "POST":
        user["mt_account"] = {"login": request.form.get("mt_login"), "server": request.form.get("mt_server"), "type": request.form.get("mt_type")}
        user["equity"] = float(request.form.get("equity", 1000))
        user["bot_active"] = True
    vip = user.get("vip")
    eq = user.get("equity", 1000)
    content = f"<div class='card'><h2>Bot - Equity Based ${eq}</h2><p>Status: {'ACTIVE' if user.get('bot_active') else 'STOPPED'}</p></div>"
    if vip:
        content += f"<div class='card'><h3>Connect MT4/MT5</h3><form method='POST'><input name='mt_login' placeholder='MT Login' required><input name='mt_server' placeholder='Server e.g Exness-MT5Real' required><select name='mt_type'><option>MT5</option><option>MT4</option></select><input name='equity' type='number' value='{eq}'><button class='btn btn-gold'>Save & Start</button></form></div>"
        for sym in VIP_ASSETS:
            sig = calculate_signal(sym)
            lot = calculate_lot(eq)
            content += f"<div class='card'>{sym} {sig['signal']} Lot {lot['lot']} Risk ${lot['risk_amount']} ({lot['risk_percent']}%)</div>"
    else:
        content += "<div class='card'><a href='https://flutterwave.com/pay/msjgnmx4gehc' class='btn btn-gold'>Become VIP $10</a></div>"
    return render_template_string(HTML_BASE, content=content)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users[request.form["email"]] = {"password": request.form["password"], "vip": False, "equity": 500, "bot_active": False}
        session["user"] = request.form["email"]
        return redirect("/")
    return render_template_string(HTML_BASE, content="<div class='card'><h2>Register</h2><form method='POST'><input name='email' placeholder='Email' required><br><br><input name='password' type='password' required><br><br><button class='btn'>Register Free</button></form></div>")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pw = request.form["password"]
        if email in users and users[email]["password"] == pw:
            session["user"] = email
            return redirect("/")
    return render_template_string(HTML_BASE, content="<div class='card'><h2>Login</h2><form method='POST'><input name='email' placeholder='Email' required><br><br><input name='password' type='password' required><br><br><button class='btn'>Login</button></form></div>")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/activate-vip")
def activate_vip():
    if "user" in session:
        users[session["user"]]["vip"] = True
    return redirect("/bot")

@app.route("/api/signals")
def api_signals():
    return jsonify([calculate_signal(s) for s in FREE_PAIRS + VIP_ASSETS])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
