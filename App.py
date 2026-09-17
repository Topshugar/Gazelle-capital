from flask import Flask, request, redirect, session, render_template_string
import os

app = Flask(__name__)
app.secret_key = "gazelle-flw-2026-v2"

PAY_LINK = "https://flutterwave.com/pay/msjgnmx4gehc"

BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<script src="https://s3.tradingview.com/tv.js"></script>
<style>
*{font-family:'Inter',system-ui;box-sizing:border-box}
body{margin:0;background:#fff;color:#0a1931;padding-bottom:90px}
.top{padding:14px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #f0f0f0;position:sticky;top:0;background:#fff;z-index:10}
.logo{display:flex;align-items:center;gap:10px;font-weight:800;font-size:20px}
.logo-icon{width:32px;height:32px;background:#0a1931;color:#f7c948;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:900}
.search{margin:14px 16px;background:#f8f8f9;border:1px solid #e8e8ea;border-radius:12px;padding:12px 14px;display:flex;gap:10px}
.search input{border:none;outline:none;background:transparent;width:100%;font-size:14px}
.tabs{margin:16px;display:flex;gap:10px}
.tab{padding:10px 20px;border-radius:24px;font-weight:700;border:none;font-size:14px;text-decoration:none}
.tab-active{background:#0a1931;color:#fff}
.tab-inactive{background:#eeeeef;color:#8a8a8a}
.card{margin:16px;border-radius:16px;padding:18px}
.card-mint{border:1.5px solid #b7e1c5;background:#eef9f1}
.card-white{border:1px solid #eee;background:#fff;box-shadow:0 2px 12px rgba(0,0,0,0.04)}
.btn-dark{display:block;text-align:center;background:#0a1931;color:white;padding:14px;border-radius:10px;font-weight:700;text-decoration:none;margin-top:14px}
.btn-gold{display:block;text-align:center;background:#f7c948;color:#000;padding:15px;border-radius:12px;font-weight:800;text-decoration:none}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;display:flex;justify-content:space-around;padding:10px 0 18px}
.nav-item{text-align:center;font-size:11px;color:#999;text-decoration:none}
.nav-item.active{color:#0a1931;font-weight:700}
.signal-row{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #f5f5f5;font-size:13px}
.badge{padding:4px 10px;border-radius:12px;font-size:11px;font-weight:700}
.badge-buy{background:#eef9f1;color:#0a7a2f}
</style>
</head>
<body>
<div class="top">
  <div class="logo"><div class="logo-icon">G</div> Gazelle VIP</div>
  <a href="/account" style="background:#eee;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none">👤</a>
</div>
<div class="search"><span>🔍</span><input placeholder="Search signals, pairs, analysis"></div>
<div class="tabs">
  <a href="/" class="tab {{ 'tab-active' if page=='signals' else 'tab-inactive' }}">Signals</a>
  <a href="/analysis" class="tab {{ 'tab-active' if page=='analysis' else 'tab-inactive' }}">Analysis</a>
  <a href="/account" class="tab {{ 'tab-active' if page=='account' else 'tab-inactive' }}">Account</a>
</div>
{{ content | safe }}
<div class="bottom-nav">
  <a href="/" class="nav-item {{ 'active' if page=='signals' else '' }}">🏠<br>Home</a>
  <a href="/analysis" class="nav-item {{ 'active' if page=='analysis' else '' }}">📊<br>Portfolio</a>
  <a href="/account" class="nav-item {{ 'active' if page=='account' else '' }}">👤<br>Account</a>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    vip = request.args.get('vip') or session.get('vip')
    if vip:
        content = """
        <div class="card card-mint">
          <div style="display:flex;gap:12px">
            <div style="background:#b7e1c5;min-width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800">✓</div>
            <div><h2>Account activated<br>successfully</h2><p>Welcome Temitope, your VIP is live. Daily signals at 8am UTC.</p></div>
          </div>
          <a href="/analysis" class="btn-dark">View Live Gold Chart</a>
        </div>
        <div class="card card-white">
          <h2>Today's Signals</h2>
          <div class="signal-row"><span>XAUUSD BUY 2035 → 2055</span><span class="badge badge-buy">+120 pips</span></div>
          <div class="signal-row"><span>BTCUSD SELL 67k</span><span class="badge badge-buy">Running</span></div>
        </div>
        """
    else:
        content = f"""
        <div class="card card-white" style="text-align:center">
          <h2>Welcome to Gazelle for Business 👋</h2>
          <p>Clean Flutterwave-style trading dashboard</p>
        </div>
        <div class="card card-white">
          <h2>VIP Access - $10/month</h2>
          <p style="margin:10px 0">Daily verified signals + live chart + prop firm plan</p>
          <a href="{PAY_LINK}" class="btn-gold">Subscribe - $10/month</a>
          <p style="font-size:10px;color:#aaa;text-align:center;margin-top:8px">Secured by Flutterwave • Link: msjgnmx4gehc</p>
        </div>
        """
    return render_template_string(BASE_HTML, content=content, page='signals')

@app.route('/analysis')
def analysis():
    content = """
    <div class="card card-white">
      <h2>Live XAUUSD Chart</h2>
      <p>Real TradingView - Lagos time</p>
      <div id="tradingview_gold" style="height:380px;margin-top:12px;border-radius:12px;overflow:hidden"></div>
      <script>
        new TradingView.widget({
          "autosize": true,
          "symbol": "OANDA:XAUUSD",
          "interval": "60",
          "timezone": "Africa/Lagos",
          "theme": "light",
          "style": "1",
          "locale": "en",
          "container_id": "tradingview_gold"
        });
      </script>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, page='analysis')

@app.route('/account')
def account():
    content = f"""
    <div class="card card-white">
      <h2>Account</h2>
      <div style="margin-top:12px"><div class="signal-row"><span>Plan</span><span>$10/month</span></div><div class="signal-row"><span>Next bill</span><span>Oct 17</span></div></div>
      <a href="{PAY_LINK}" class="btn-dark">Manage on Flutterwave</a>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, page='account')

@app.route('/dashboard')
def dashboard():
    session['vip'] = True
    return redirect("/?vip=1")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port) 
