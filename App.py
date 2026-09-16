from flask import Flask, render_template_string
import random, datetime

app = Flask(__name__)
app.secret_key = "gazelle2026"

BALANCE = 100.0
trades = []

HTML_DASH = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#000;color:#fff;font-family:Arial;padding:15px;margin:0}
.card{background:#151515;border:1px solid #222;padding:15px;border-radius:10px;margin:10px 0}
.gold{color:gold} .green{color:#00ff88}
.btn{background:gold;color:#000;padding:12px;border:none;border-radius:8px;font-weight:bold;width:100%}
h1{color:gold;text-align:center}
</style></head><body>
<h1>GAZELLE DASHBOARD</h1>
<p style="text-align:center;color:#888;">Demo Simulation | Bot Trading Live</p>
<div class="card">
<p>Demo Balance</p>
<h1 class="green">${{balance}}</h1>
<p style="font-size:12px;color:#777;">Started: $100 | 2% risk per trade | XAUUSD</p>
</div>
<div class="card">
<h3 class="gold">Live Bot Trades Today</h3>
{% for t in trades %}
<p style="font-size:13px;">{{t}}</p>
{% endfor %}
<p style="font-size:11px;color:#555;">Refresh to see new trade - will connect to MT5 later</p>
</div>
<div class="card">
<h3>If This Was Real</h3>
<p>Profit: ${{profit}} | Your Share (30%): ${{investor_share}}</p>
<p style="font-size:11px;color:#aaa;">In real copy trading, this profit would be in YOUR MT5 account.</p>
<button class="btn">Subscribe to Real Signal (Coming Soon)</button>
</div>
<div style="text-align:center;padding:20px;"><a href="/" style="color:#555;font-size:12px;">Back to Company Site</a></div>
</body></html>
"""

@app.route('/')
def home():
    return render_template_string("""
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{background:#000;color:#fff;font-family:Arial;text-align:center;padding:40px} h1{color:gold} .btn{background:gold;padding:15px 30px;border:none;border-radius:8px;font-weight:bold}</style></head>
    <body><h1>GAZELLE CAPITAL</h1><p>Algorithmic Gold Trading Company</p><p style="color:#888;font-size:13px;">Lagos | Copy Trading | 30% Performance Fee</p><br><a href="/dashboard"><button class="btn">View Live Bot Dashboard</button></a>
    <p style="color:#555;margin-top:20px;font-size:12px;">Simulation Mode - No Real Money</p></body></html>
    """)

@app.route('/dashboard')
def dashboard():
    global BALANCE
    change = random.choice([1.5, 2.0, -0.8, 2.5])
    BALANCE = round(BALANCE * (1 + change/100), 2)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    trades.insert(0, f"[{now}] XAUUSD BUY +{change}% -> Balance ${BALANCE}")
    profit = round(BALANCE - 100, 2)
    investor_share = round(profit * 0.3, 2)
    return render_template_string(HTML_DASH, balance=BALANCE, trades=trades[:5], profit=profit, investor_share=investor_share)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
