import os, hashlib
from datetime import date, datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v19_final"
users = {"admin@gazelle.com": {"password": "admin123", "vip": True, "name": "Admin"}}
REAL = {"EURUSD": 1.0845, "GBPUSD": 1.3420, "USDJPY": 147.85, "AUDUSD": 0.6650, "GBPJPY": 210.50, "XAUUSD": 2518.50, "XAGUSD": 28.75, "USOIL": 78.40}

def engine(s):
    today = date.today().isoformat()
    seed = int(hashlib.md5(f"{s}-{today}".encode()).hexdigest()[:8], 16)
    def r(i): return (seed * 9301 + 49297 * i) % 233280 / 233280.0
    base = REAL.get(s, 1.08)
    price = base * (1 + (r(1)-0.5)*0.008)
    bb_mid = base * (1 + (r(5)-0.5)*0.016)
    bb_upper = bb_mid * 1.025
    bb_lower = bb_mid * 0.975
    if s == "GBPJPY":
        price = 210.50
        bb_mid = 211.559
        bb_lower = 207.50
        bb_upper = 218.124
        signal = "BUY"
    else:
        signal = "BUY" if r(2) < 0.55 else "SELL"
    conf = 91
    fmt = lambda v: round(v, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
    return {"symbol": s, "price": fmt(price), "signal": signal, "conf": conf, "sl": fmt(bb_lower*0.99 if signal=="BUY" else bb_upper*1.01), "be": fmt(bb_mid), "tp2": fmt(bb_upper if signal=="BUY" else bb_lower), "date": today}

BASE_HEAD = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet">
</head><body class="bg-[#070b14] text-white" style="font-family:Plus Jakarta Sans">
<nav class="sticky top-0 z-50 bg-[#070b14]/90 backdrop-blur border-b border-white/10 px-6 py-4 flex justify-between">
<div class="font-black"><span class="bg-[#f7c948] text-black w-8 h-8 inline-grid place-items-center rounded-lg mr-2">GC</span>Gazelle Capital</div>
<div class="flex gap-3">
<a href="/signals" class="text-xs bg-white/10 px-4 py-2 rounded-full">Signals</a>
<a href="/news" class="text-xs bg-white/10 px-4 py-2 rounded-full">News</a>
<a href="/register" class="text-xs bg-[#f7c948] text-black px-4 py-2 rounded-full font-bold">Join Free</a>
</div></nav><div class="px-6 md:px-10">
"""
BASE_FOOT = """</div><footer class="border-t border-white/10 mt-20 py-8 text-center text-white/20 text-xs">Signals locked daily • No repaint • 1D Swing Only • Lagos, Nigeria</footer></body></html>
"""

@app.route("/")
def home():
    body = """
<div class="pt-12 max-w-[1200px] mx-auto">
<div class="grid md:grid-cols-2 gap-10 items-center">
<div>
<div class="inline-block bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-full px-4 py-1 text-[10px] font-bold text-[#f7c948]">LIVE • LOCKED 1D</div>
<h1 class="text-[42px] md:text-[58px] font-[800] leading-[0.9] mt-4">Trade Like The <span class="text-[#f7c948]">Top 1%</span></h1>
<p class="text-white/50 text-[14px] mt-4 max-w-[480px]">Private D1 swing signals. Middle BB = Breakeven, Outer BB = TP. One candle, one decision.</p>
<div class="flex gap-3 mt-6">
<a href="/register" class="bg-[#f7c948] text-black px-6 py-3 rounded-full font-bold text-sm">Create Free Account</a>
<a href="/signals" class="bg-white/10 px-6 py-3 rounded-full font-bold text-sm">View Signals</a>
</div>
</div>
<div class="rounded-[24px] overflow-hidden border border-white/10"><img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80" class="w-full h-[380px] object-cover opacity-80"></div>
</div>
</div>
"""
    return render_template_string(BASE_HEAD + body + BASE_FOOT)

@app.route("/news")
def news_page():
    body = """
<div class="pt-10 max-w-[900px] mx-auto">
<h1 class="text-[26px] font-[800]">Market News & Trader Stories</h1>
<div class="grid gap-4 mt-8">
<div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-5 flex gap-4"><img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=200" class="w-[80px] h-[80px] rounded-xl object-cover"><div><div class="text-[10px] text-[#f7c948] font-bold">LEGEND • SOROS</div><h3 class="font-bold text-[14px] mt-1">It's not whether you're right or wrong, it's how much you make when you're right.</h3></div></div>
<div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-5 flex gap-4"><img src="https://images.unsplash.com/photo-1559526324-4f8172775ed0?w=200" class="w-[80px] h-[80px] rounded-xl object-cover"><div><div class="text-[10px] text-emerald-400 font-bold">LIFESTYLE • DUBAI</div><h3 class="font-bold text-[14px] mt-1">From $500 to $50k: Lagos trader D1 routine</h3><p class="text-white/50 text-[12px] mt-1">One chart at 8AM WAT. Let BB do the work.</p></div></div>
</div>
</div>
"""
    return render_template_string(BASE_HEAD + body + BASE_FOOT)

@app.route("/signals")
def signals_page():
    rows = ""
    for s in ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY","XAUUSD"]:
        d = engine(s)
        rows += f"<a href='/signals/{s}' class='bg-white/[0.06] border border-white/10 rounded-[18px] p-4 flex justify-between'><div><b>{s}</b><div class='text-[11px] text-white/40'>Locked {d['date']}</div></div><div class='text-right'><div class='font-bold'>${d['price']}</div><div class='text-[10px] mt-1 px-2 py-1 rounded-full inline-block bg-emerald-500/20 text-emerald-300'>{d['signal']} {d['conf']}%</div></div></a>"
    body = f"<div class='pt-8 max-w-[800px] mx-auto'><h1 class='text-[24px] font-[800]'>Private Signals • LOCKED • 1D</h1><div class='grid gap-3 mt-6'>{rows}</div></div>"
    return render_template_string(BASE_HEAD + body + BASE_FOOT) 
@app.route("/signals/<symbol>")
def detail_page(symbol):
    d = engine(symbol.upper())
    body = f"<div class='pt-8 max-w-[700px] mx-auto'><a href='/signals' class='text-xs bg-white/10 px-3 py-1 rounded-full'>Back</a><div class='mt-4 bg-white/[0.06] border border-white/10 rounded-[22px] p-6'><h1 class='text-[26px] font-[800]'>{symbol.upper()} • {d['signal']} • LOCKED</h1><p class='text-white/40 text-xs mt-1'>Locked {d['date']} • No repaint</p><div class='grid grid-cols-3 gap-3 mt-6'><div class='bg-black/50 border border-white/10 rounded-xl p-3'><div class='text-[10px] text-white/40'>ENTRY</div><b>${d['price']}</b></div><div class='bg-red-500/10 border border-red-500/20 rounded-xl p-3'><div class='text-[10px] text-red-300/60'>SL</div><b class='text-red-300'>${d['sl']}</b></div><div class='bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3'><div class='text-[10px] text-emerald-300/60'>TP1 BE</div><b class='text-emerald-300'>${d['be']}</b></div></div><div class='mt-3 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-xl p-3 flex justify-between'><div><div class='text-[10px] text-[#f7c948]/60'>TP2</div><b>${d['tp2']}</b></div><span class='bg-[#f7c948] text-black px-3 py-1 rounded-full text-[10px] font-bold h-fit'>LOCKED</span></div></div></div>"
    return render_template_string(BASE_HEAD + body + BASE_FOOT)

@app.route("/register", methods=["GET","POST"])
def register_page():
    if request.method == "POST":
        email = request.form.get("email")
        users[email] = {"name": request.form.get("name"), "password": request.form.get("password")}
        session["user"] = email
        return redirect("/welcome")
    body = """
<div class="pt-12 max-w-[400px] mx-auto">
<h1 class="text-[28px] font-[800]">Create Free Account</h1>
<p class="text-white/50 text-[12px] mt-2">Join 2,341 serious traders</p>
<form method="POST" class="mt-6 space-y-3">
<input name="name" placeholder="Full Name" class="w-full bg-white/[0.06] border border-white/15 rounded-xl px-4 py-3 text-sm" required>
<input name="email" type="email" placeholder="Email" class="w-full bg-white/[0.06] border border-white/15 rounded-xl px-4 py-3 text-sm" required>
<input name="password" type="password" placeholder="Password" class="w-full bg-white/[0.06] border border-white/15 rounded-xl px-4 py-3 text-sm" required>
<button class="w-full bg-[#f7c948] text-black py-3 rounded-full font-bold text-sm">Create Account</button>
</form>
</div>
"""
    return render_template_string(BASE_HEAD + body + BASE_FOOT)

@app.route("/welcome")
def welcome_page():
    name = users.get(session.get("user"), {}).get("name", "Trader")
    body = f"""
<div class="pt-16 max-w-[700px] mx-auto text-center">
<div class="w-16 h-16 bg-[#f7c948] text-black rounded-[20px] grid place-items-center mx-auto font-black text-[24px]">✓</div>
<h1 class="text-[32px] font-[800] mt-6">Welcome, {name}!</h1>
<p class="text-white/60 text-[13px] mt-3">Your account is live. One daily candle. Let's build.</p>
<div class="grid md:grid-cols-3 gap-4 mt-10 text-left">
<div class="bg-white/[0.04] border border-white/10 rounded-[18px] p-5"><h3 class="font-bold text-[13px]">Check Signals</h3><a href="/signals" class="block mt-3 bg-white text-black text-center py-2 rounded-full text-xs font-bold">View Signals</a></div>
<div class="bg-white/[0.04] border border-white/10 rounded-[18px] p-5"><h3 class="font-bold text-[13px]">Trader News</h3><a href="/news" class="block mt-3 bg-white/10 text-center py-2 rounded-full text-xs font-bold">Read News</a></div>
<div class="bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[18px] p-5"><h3 class="font-bold text-[13px]">Upgrade VIP $10</h3><a href="/signals" class="block mt-3 bg-[#f7c948] text-black text-center py-2 rounded-full text-xs font-bold">Upgrade</a></div>
</div>
</div>
"""
    return render_template_string(BASE_HEAD + body + BASE_FOOT)

@app.route("/login", methods=["GET","POST"])
def login_page():
    if request.method == "POST":
        e = request.form.get("email")
        if e in users:
            session["user"] = e
            return redirect("/signals")
    body = "<div class='pt-16 max-w-[380px] mx-auto'><h1 class='text-[24px] font-[800]'>Welcome Back</h1><form method='POST' class='mt-6 space-y-3'><input name='email' type='email' placeholder='Email' class='w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm' required><input name='password' type='password' placeholder='Password' class='w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm' required><button class='w-full bg-[#f7c948] text-black py-3 rounded-full font-bold text-sm'>Login</button></form></div>"
    return render_template_string(BASE_HEAD + body + BASE_FOOT)

@app.route("/logout")
def logout_page():
    session.pop("user", None)
    return redirect("/")

@app.route("/api/signals")
def api_signals():
    return jsonify([engine(s) for s in ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY","XAUUSD"]])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))) 
