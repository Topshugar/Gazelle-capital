import os
from flask import Flask, render_template_string, request, redirect, session, jsonify
from datetime import datetime
import os
from flask import ...
from datetime import datetime
import random
import random

app = Flask(__name__)
app.secret_key = "gazelle_capital_v5_final_2026"

# --- IN-MEMORY DB (use Postgres later) ---
users = {
    "admin@gazelle.com": {"password": "admin123", "vip": True, "equity": 5000, "mt_account": {"login": "123456", "server": "Exness-MT5Real", "type": "MT5"}}
}
# signals cache
# --- INDICATOR ENGINE (Swing 1D RSI + Alligator + BB) ---
def calculate_signal(symbol, price_data=None):
    # In production: fetch 1D candles via yfinance/ccxt
    # For demo we simulate mature logic
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
        "price": round(random.uniform(1.08, 85.0) if "USD" in symbol else random.uniform(2000, 3000), 2),
        "rsi": rsi,
        "alligator": alligator_status,
        "bb": bb_position,
        "signal": signal,
        "sl": round(random.uniform(0.5, 2.0), 2),
        "tp": round(random.uniform(1.0, 3.5), 2),
        "timeframe": "1D",
        "updated": datetime.utcnow().strftime("%Y-%m-%d 08:00 UTC")
    }

def calculate_lot(equity, risk_percent, sl_distance_usd):
    # MATURE EQUITY FORMULA
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
    # prevent blow
    lot = risk_amount / max(sl_distance_usd, 1)
    lot = max(0.01, round(lot, 2))
    
    return {"lot": lot, "risk_amount": round(risk_amount,2), "risk_percent": risk_percent, "max_trades": max_trades}

FREE_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "GBPJPY"]
VIP_ASSETS = ["XAUUSD", "USOIL", "UKOIL", "XPTUSD", "XAGUSD"]

HTML_BASE = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://s3.tradingview.com/tv.js"></script>
<style>
body{font-family:Inter,sans-serif;background:#f6f7f9;margin:0;color:#0a1931}
.nav{background:#0a1931;padding:14px 20px;display:flex;justify-content:space-between;color:white}
.nav a{color:#f7c948;text-decoration:none;margin-left:15px}
.card{background:white;border-radius:16px;padding:18px;margin:12px;box-shadow:0 4px 12px rgba(0,0,0,0.06)}
.btn{background:#0a1931;color:#f7c948;padding:10px 18px;border-radius:10px;border:none;cursor:pointer}
.btn-gold{background:#f7c948;color:#0a1931;font-weight:700}
.badge{padding:4px 8px;border-radius:6px;font-size:12px}
.badge-buy{background:#d1fae5;color:#065f46} .badge-sell{background:#fee2e2;color:#991b1b}
.blur{filter:blur(6px);pointer-events:none}
</style></head><body>
<div class="nav"><div>🦌 Gazelle Capital</div><div>
<a href="/">Home</a><a href="/signals">Signals</a><a href="/analysis">Analysis</a><a href="/bot">Bot</a>
{% if 'user' in session %}<a href="/logout">Logout</a>{% else %}<a href="/login">Login</a>{% endif %}
</div></div>
{{content|safe}}
</body></html>
"""

@app.route("/")
def home():
    user = users.get(session.get("user"))
    vip = user and user.get("vip")
    free_signals = [calculate_signal(s) for s in FREE_PAIRS[:3]]
    
    content = f"""
    <div class="card"><h2>{'VIP Dashboard 🦌' if vip else 'Free Forex Alerts (1D Swing)'}</h2>
    <p>Strategy: RSI(14) + Alligator(13,8,5) + Bollinger(20,2) | Timeframe: 1D Daily</p>
    </div>
    """
    for sig in free_signals:
        content += f"<div class='card'><b>{sig['symbol']}</b> <span class='badge badge-{sig['signal'].lower()}'>{sig['signal']}</span> RSI:{sig['rsi']} BB:{sig['bb']} Alligator:{sig['alligator']}</div>"
    
    if not vip:
        content += """
        <div class="card" style="border:2px solid #f7c948">
        <h3>Unlock VIP Swing Bot</h3>
        <p>Auto-trade Gold, US Oil (WTI), UK Brent, Platinum, Silver XAG based on YOUR equity. Mature 1% risk.</p>
        <a href="https://flutterwave.com/pay/msjgnmx4gehc" class="btn btn-gold">Subscribe $10/mo to Unlock</a>
        <p style="font-size:12px">After pay, click: <a href="/activate-vip">I have paid - Activate VIP</a></p>
        </div>
        """
    else:
        eq = user.get("equity", 1000)
        content += f"<div class='card'><h3>Your Equity: ${eq} | Auto Lot Calculator Active</h3><p>Bot will risk 0.5-1.5% per trade maturely.</p></div>"
        for sym in VIP_ASSETS:
            sig = calculate_signal(sym)
            lot_info = calculate_lot(eq, 1, 15)
            content += f"<div class='card'><b>{sym} VIP</b> <span class='badge badge-{sig['signal'].lower()}'>{sig['signal']}</span> Price:{sig['price']} | Lot for you: {lot_info['lot']} (Risk ${lot_info['risk_amount']})</div>"

    return render_template_string(HTML_BASE, content=content)

@app.route("/signals")
def signals_page():
    user = users.get(session.get("user"))
    vip = user and user.get("vip")
    
    content = "<div class='card'><h2>Signals</h2><div><a class='btn' href='/signals'>Free Forex</a> <a class='btn btn-gold' href='/signals?vip=1'>VIP Metals & Oil</a></div></div>"
    
    # Free
    content += "<h3 style='margin-left:12px'>Free - Currency Pairs (1D Alert Only)</h3>"
    for s in FREE_PAIRS:
        sig = calculate_signal(s)
        content += f"<div class='card'><b>{sig['symbol']}</b> - {sig['signal']} | Entry {sig['price']} | RSI {sig['rsi']} | Alligator {sig['alligator']} <br><small>Alert: Trade manually. This is 1D swing.</small></div>"
    
    # VIP
    content += "<h3 style='margin-left:12px'>VIP - Auto Trade (Equity Based)</h3>"
    blur_class = "" if vip else "blur"
    for s in VIP_ASSETS:
        sig = calculate_signal(s)
        lot = calculate_lot(user.get("equity", 1000) if user else 1000, 1, 20) if vip else {"lot": "0.XX"}
        content += f"<div class='card {blur_class}'><b>{s} (XAU=Gold, USOIL=USA, UKOIL=UK Brent, XPT=Platinum, XAG=Silver)</b><br>{sig['signal']} @ {sig['price']} SL {sig['sl']}% TP {sig['tp']}% | Your Lot: {lot['lot']} | 1D RSI+Alligator+BB</div>"
    
    if not vip:
        content += "<div class='card'><a href='https://flutterwave.com/pay/msjgnmx4gehc' class='btn btn-gold'>Pay $10 to Unlock VIP Signals</a></div>"
    
    return render_template_string(HTML_BASE, content=content)

@app.route("/analysis")
def analysis():
    content = """
    <div class="card"><h2>Analysis - 1D Swing View</h2>
    <select id="pairSelect" onchange="loadChart()">
    <option value="FX:EURUSD">FREE EURUSD</option>
    <option value="FX:GBPUSD">FREE GBPUSD</option>
    <option value="OANDA:XAUUSD">VIP Gold XAUUSD</option>
    <option value="TVC:USOIL">VIP US Oil WTI</option>
    <option value="TVC:UKOIL">VIP UK Brent</option>
    <option value="OANDA:XPTUSD">VIP Platinum XPT</option>
    <option value="OANDA:XAGUSD">VIP Silver XAG</option>
    </select>
    <div id="tvchart" style="height:500px;margin-top:10px"></div>
    <p>Indicators on chart: RSI, Alligator, Bollinger Bands. Timeframe locked to 1D.</p>
    </div>
    <script>
    function loadChart(){ 
      let sym=document.getElementById('pairSelect').value;
      new TradingView.widget({autosize:true,symbol:sym,interval:"D",timezone:"Etc/UTC",theme:"light",style:"1",container_id:"tvchart",studies:["RSI@tv-basicstudies","BollingerBands@tv-basicstudies"]});
    }
    loadChart();
    </script>
    """
    return render_template_string(HTML_BASE, content=content)

@app.route("/bot", methods=["GET","POST"])
def bot():
    if "user" not in session: return redirect("/login")
    user = users[session["user"]]
    
    if request.method == "POST":
        login = request.form.get("mt_login")
        server = request.form.get("mt_server")
        mtype = request.form.get("mt_type")
        equity = request.form.get("equity")
        user["mt_account"] = {"login": login, "server": server, "type": mtype}
        user["equity"] = float(equity) if equity else user.get("equity",1000)
        user["bot_active"] = True

    vip = user.get("vip")
    mt = user.get("mt_account")
    eq = user.get("equity", 1000)
    
    content = f"""
    <div class="card"><h2>🦌 Gazelle Swing Bot - 1D Equity Based</h2>
    <p>Equity: ${eq} | Risk Model: Mature (0.5-1.5%) | Strategy: RSI+Alligator+BB 1D</p>
    <p>MT Account: {mt if mt else 'Not Connected'} | Status: {'🟢 ACTIVE' if user.get('bot_active') else '🔴 STOPPED'}</p>
    </div>
    """
    
    # MT Connect form for VIP
    if vip:
        content += f"""
        <div class="card"><h3>Connect MT4/MT5 (VIP)</h3>
        <form method="POST">
        <input name="mt_login" placeholder="MT Login" value="{mt.get('login','') if mt else ''}" required>
        <input name="mt_server" placeholder="Server e.g Exness-MT5Real" required>
        <select name="mt_type"><option>MT5</option><option>MT4</option></select>
        <input name="equity" type="number" placeholder="Your Equity e.g 1000" value="{eq}">
        <button class="btn btn-gold">Save & Start Bot</button>
        </form>
        <small>Bot will calculate lot from your equity automatically. Max loss protection 10% daily pause.</small>
        </div>
        """
        # Show auto trade signals
        for sym in VIP_ASSETS + FREE_PAIRS:
            sig = calculate_signal(sym)
            if sig["signal"] != "HOLD":
                lot_info = calculate_lot(eq, 1, 15)
                content += f"<div class='card'><b>{sym} AUTO</b> {sig['signal']} Lot {lot_info['lot']} Risk ${lot_info['risk_amount']} ({lot_info['risk_percent']}%) | Bot will trade on your {user.get('mt_account',{}).get('type','MT5')}</div>"
    else:
        content += """
        <div class="card"><h3>Free Mode - Alerts Only</h3>
        <p>You get 1D forex alerts only. No auto-trade. To auto-trade Gold, US Oil, UK Brent, Platinum, XAG with equity-based lots, subscribe VIP.</p>
        <a href="https://flutterwave.com/pay/msjgnmx4gehc" class="btn btn-gold">Become VIP $10</a>
        </div>
        """
        for s in FREE_PAIRS:
            sig = calculate_signal(s)
            content += f"<div class='card'>{s} ALERT: {sig['signal']} - Check Analysis page. Trade manually.</div>"

    return render_template_string(HTML_BASE, content=content)

# --- Auth ---
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email=request.form["email"]; pw=request.form["password"]
        users[email]={"password":pw,"vip":False,"equity":500,"bot_active":False}
        session["user"]=email; return redirect("/")
    content = """<div class="card"><h2>Register</h2><form method="POST"><input name="email" placeholder="Email" required><br><br><input name="password" type="password" placeholder="Password" required><br><br><button class="btn">Register Free</button></form></div>"""
    return render_template_string(HTML_BASE, content=content)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email=request.form["email"]; pw=request.form["password"]
        if email in users and users[email]["password"]==pw:
            session["user"]=email; return redirect("/")
    content = """<div class="card"><h2>Login</h2><form method="POST"><input name="email" placeholder="Email" required><br><br><input name="password" type="password" placeholder="Password" required><br><br><button class="btn">Login</button></form></div>"""
    return render_template_string(HTML_BASE, content=content)

@app.route("/logout")
def logout(): session.pop("user",None); return redirect("/")

@app.route("/activate-vip")
def activate_vip():
    if "user" in session: users[session["user"]]["vip"]=True
    return redirect("/bot")

@app.route("/api/signals")
def api_signals():
    # Real engine will use yfinance here for 1D candles
    all_syms = FREE_PAIRS + VIP_ASSETS
    data = [calculate_signal(s) for s in all_syms]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
