import os, hashlib
from datetime import date
from flask import Flask, render_template_string, request, redirect, session, jsonify
app = Flask(__name__)
app.secret_key = "gazelle_v23_vip"
users = {"admin@gazelle.com": {"name": "Admin"}}
REAL = {"EURUSD": 1.0845, "GBPUSD": 1.3420, "USDJPY": 147.85, "AUDUSD": 0.6650, "GBPJPY": 210.50, "XAUUSD": 2518.50, "XAGUSD": 28.75, "USOIL": 78.40}
FREE_PAIRS = ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY"]
VIP_PAIRS = ["XAUUSD","XAGUSD","USOIL"]
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
        price=210.50; bb_mid=211.559; bb_lower=207.50; bb_upper=218.124; sig="BUY"; reason="BoJ dovish + UK wage 6.2% supports GBP."
    elif s == "USDJPY":
        sig="BUY" if r(2)<0.5 else "SELL"; reason="US CPI sticky 3.2%."
    elif s == "XAUUSD":
        sig="BUY"; reason="Central bank buying + real yield drop."
    elif s == "EURUSD":
        sig="SELL" if r(2)<0.5 else "BUY"; reason="ECB dovish vs Fed hold."
    elif s == "GBPUSD":
        sig="BUY"; reason="UK labor tight."
    else:
        sig="BUY" if r(2)<0.55 else "SELL"; reason="AUD supported by China."
    fmt = lambda v: round(v, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
    return {"symbol":s,"price":fmt(price),"signal":sig,"conf":91,"sl":fmt(bb_lower*0.99 if sig=="BUY" else bb_upper*1.01),"be":fmt(bb_mid),"tp2":fmt(bb_upper if sig=="BUY" else bb_lower),"date":today,"reason":reason}
HEAD = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800&display=swap" rel="stylesheet"><style>body{font-family:Inter,sans-serif}</style></head><body class="bg-[#f8fafc] text-[#0f172a]"><nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200 px-6 py-3.5 flex justify-between items-center"><div class="flex items-center gap-2.5 font-[800]"><span class="bg-[#2563eb] text-white w-8 h-8 grid place-items-center rounded-lg text-[11px]">GC</span> Gazelle Capital</div><div class="flex gap-3"><a href="/login" class="text-[13px] font-[600] px-4 py-2">Log in</a><a href="/register" class="bg-[#0f172a] text-white px-5 py-2.5 rounded-full text-[13px] font-[700]">Get Started</a></div></nav><div>"""
FOOT = """</div><footer class="border-t mt-24 py-10 text-center text-slate-400 text-[12px] bg-white">© 2026 Gazelle Capital</footer></body></html>"""
@app.route("/")
def home():
    sigs = [engine(s) for s in ["EURUSD","GBPUSD","GBPJPY","XAUUSD"]]
    rows = "".join([f"<div class='flex justify-between py-2.5 border-b text-[13px]'><span class='font-[600]'>{d['symbol']} {d['signal']}</span><span class='text-slate-500'>Entry {d['price']} SL {d['sl']}</span></div>" for d in sigs])
    body = f"""<div class="px-6 max-w-[1200px] mx-auto"><div class="grid lg:grid-cols-[1.1fr_0.9fr] gap-10 pt-14"><div><div class="bg-blue-50 border border-blue-100 rounded-full px-3 py-1 text-[11px] font-[700] text-blue-700 inline-flex">Now live {date.today().isoformat()}</div><h1 class="text-[42px] font-[800] leading-[0.95] mt-5">Invest with<br>Institutional Precision</h1><p class="text-slate-500 text-[15px] mt-5">Forex FREE. Gold/Oil VIP + Bot auto-trades for you.</p><div class="flex gap-3 mt-7"><a href="/register" class="bg-[#2563eb] text-white px-6 py-3 rounded-full font-[700] text-[13px]">Start Free Trial</a><a href="/signals" class="bg-white border px-6 py-3 rounded-full font-[600] text-[13px]">View Signals</a></div></div><div class="bg-white border rounded-[20px] p-5"><div class="font-[700] text-[12px]">D1 Signals {date.today().isoformat()} LIVE</div><div class="mt-4 bg-slate-50 rounded-[12px] p-1">{rows}</div></div></div><div class="mt-20"><h2 class="text-[22px] font-[800] text-center">Simple Pricing</h2><div class="grid md:grid-cols-3 gap-6 mt-8"><div class="bg-white border rounded-[20px] p-6"><div class="font-[700] text-blue-700">Starter FREE</div><div class="text-[14px] text-slate-500">All Forex pairs free</div><div class="text-[36px] font-[800]">$0</div><a href="/register" class="block mt-6 bg-white border text-center py-2.5 rounded-full text-[13px] font-[700]">Get Started Free</a></div><div class="bg-white border-2 border-[#2563eb] rounded-[20px] p-6"><div class="font-[700] text-blue-700">Pro $10 - VIP + BOT</div><div class="text-[14px] text-slate-500">XAU XAG OIL + bot trades for you</div><div class="text-[36px] font-[800]">$10</div><a href="/register" class="block mt-6 bg-[#2563eb] text-white text-center py-2.5 rounded-full text-[13px] font-[700]">Start Pro</a></div><div class="bg-white border rounded-[20px] p-6"><div class="font-[700] text-blue-700">Enterprise</div><div class="text-[36px] font-[800]">$99</div><a href="/register" class="block mt-6 bg-white border text-center py-2.5 rounded-full text-[13px] font-[700]">Contact Sales</a></div></div></div></div>"""
    return render_template_string(HEAD + body + FOOT)
@app.route("/news")
def news():
    body = f"""<div class="px-6 max-w-[1100px] mx-auto pt-10"><h1 class="text-[28px] font-[800]">Market Brief</h1><p class="text-slate-500 text-[13px]">Forex FREE, Commodities VIP</p><div class="mt-8 space-y-3"><div class="bg-white border rounded-[16px] p-5"><h3 class="font-[700] text-[14px]">GBPJPY BUY $210.50 FREE FOREX</h3><p class="text-slate-500 text-[12px] mt-2">BoJ dovish + UK wage 6.2%</p></div><div class="bg-white border rounded-[16px] p-5"><h3 class="font-[700] text-[14px]">XAUUSD Gold $2518 VIP + BOT</h3></div></div></div>"""
    return render_template_string(HEAD + body + FOOT)
@app.route("/signals")
def signals_page():
    free_rows=""; vip_rows=""
    for s in REAL:
        d=engine(s)
        card = f"<div class='bg-white border rounded-[14px] p-4 flex justify-between'><div><div class='font-[700]'>{s}</div><div class='text-[11px] text-slate-500'>{d['reason'][:50]}...</div></div><div><div class='font-[700]'>${d['price']}</div><div class='text-[10px] bg-green-50 text-green-700 px-2 py-1 rounded-full'>{d['signal']}</div></div></div>"
        if s in FREE_PAIRS:
            free_rows+=f"<a href='/signals/{s}'>{card}</a>"
        else:
            if "user" not in session:
                vip_rows+=f"<div class='relative bg-white border rounded-[14px] p-4 flex justify-between overflow-hidden'><div class='blur-[4px]'>{card}</div><a href='/register' class='absolute inset-0 bg-white/70 grid place-items-center'><span class='bg-[#0f172a] text-white px-4 py-2 rounded-full text-[11px] font-[700]'>VIP - Unlock $10</span></a></div>"
            else:
                vip_rows+=f"<a href='/signals/{s}'>{card}</a>"
    body=f"<div class='px-6 max-w-[900px] mx-auto pt-8'><h1 class='text-[24px] font-[800]'>Signals</h1><div class='mt-6'><h2 class='text-[12px] font-[700] text-green-700'>FREE FOREX</h2><div class='grid gap-3 mt-3'>{free_rows}</div><h2 class='text-[12px] font-[700] text-[#2563eb] mt-8'>VIP + BOT (XAU XAG OIL) - $10</h2><div class='grid gap-3 mt-3'>{vip_rows}</div></div></div>"
    return render_template_string(HEAD + body + FOOT)
@app.route("/signals/<symbol>")
def detail(symbol):
    sym = symbol.upper(); d=engine(sym)
    if sym in VIP_PAIRS and "user" not in session:
        body=f"<div class='px-6 max-w-[600px] mx-auto pt-16 text-center'><div class='bg-white border rounded-[20px] p-8'><h1 class='text-[22px] font-[800]'>{sym} VIP Only $10</h1><p class='text-[13px] text-slate-500 mt-3'>Gold/Silver/Oil + Bot is for Pro only.</p><a href='/register' class='block mt-6 bg-[#2563eb] text-white py-3 rounded-full font-[700]'>Upgrade $10</a></div></div>"
        return render_template_string(HEAD + body + FOOT)
    bot_btn = f"<a href='/bot' class='block mt-4 bg-[#2563eb] text-white text-center py-3 rounded-full font-[700] text-[13px]'>Activate Bot for {sym}</a>" if sym in VIP_PAIRS else ""
    body=f"<div class='px-6 max-w-[760px] mx-auto pt-8'><a href='/signals' class='text-[12px] bg-white border px-3 py-1.5 rounded-full'>Back</a><div class='mt-5 bg-white border rounded-[20px] p-6'><h1 class='text-[26px] font-[800]'>{sym} {d['signal']} {'FREE' if sym in FREE_PAIRS else 'VIP'}</h1><p class='text-[13px] mt-2'>{d['reason']}</p><div class='grid grid-cols-3 gap-3 mt-5'><div class='bg-slate-50 border rounded-[14px] p-4'><div class='text-[10px]'>ENTRY</div><div class='font-[800]'>${d['price']}</div></div><div class='bg-red-50 border rounded-[14px] p-4'><div class='text-[10px]'>SL</div><div class='font-[800]'>${d['sl']}</div></div><div class='bg-green-50 border rounded-[14px] p-4'><div class='text-[10px]'>BE</div><div class='font-[800]'>${d['be']}</div></div></div>{bot_btn}</div></div>"
    return render_template_string(HEAD + body + FOOT)
@app.route("/bot")
def bot():
    if "user" not in session:
        return redirect("/register")
    body="<div class='px-6 max-w-[700px] mx-auto pt-10'><h1 class='text-[26px] font-[800]'>VIP Bot Auto-Trade</h1><p class='text-[13px] text-slate-500 mt-2'>Bot will trade XAU XAG USOIL for you</p><div class='bg-[#0f172a] text-white rounded-[16px] p-5 mt-6'><div class='text-[12px]'>Bot: ACTIVE for Pro $10</div></div></div>"
    return render_template_string(HEAD + body + FOOT)
@app.route("/register", methods=["GET","POST"])
def reg():
    if request.method == "POST":
        users[request.form.get("email")] = {"name": request.form.get("name")}
        session["user"] = request.form.get("email")
        return redirect("/welcome")
    body = """<div class="min-h-[85vh] grid place-items-center px-6 py-12 bg-[#f8fafc]"><div class="w-full max-w-[380px] bg-white border rounded-[20px] p-7"><h1 class="text-[22px] font-[800]">Create free account</h1><form method="POST" class="mt-6 space-y-3"><input name="name" placeholder="Full Name" class="w-full bg-slate-50 border rounded-full px-4 py-3 text-[13px]" required><input name="email" type="email" placeholder="Email" class="w-full bg-slate-50 border rounded-full px-4 py-3 text-[13px]" required><input name="password" type="password" placeholder="Password" class="w-full bg-slate-50 border rounded-full px-4 py-3 text-[13px]" required><button class="w-full bg-[#0f172a] text-white py-3 rounded-full font-[700]">Create Account</button></form></div></div>"""
    return render_template_string(HEAD + body + FOOT)
@app.route("/welcome")
def welcome():
    name = users.get(session.get("user"), {}).get("name", "Trader")
    body = f"<div class='px-6 max-w-[800px] mx-auto pt-16 text-center'><h1 class='text-[32px] font-[800]'>Welcome, {name}</h1><p class='text-[13px] text-slate-500'>Forex FREE unlocked. Upgrade to unlock VIP Bot.</p><div class='grid md:grid-cols-3 gap-4 mt-10'><a href='/signals' class='bg-white border rounded-[16px] p-5'>Free Forex</a><a href='/bot' class='bg-[#2563eb] text-white rounded-[16px] p-5'>VIP Bot $10</a><a href='/news' class='bg-white border rounded-[16px] p-5'>Market News</a></div></div>"
    return render_template_string(HEAD + body + FOOT)
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("email")
        return redirect("/signals")
    body = """<div class="min-h-[85vh] grid place-items-center px-6 py-12"><div class="w-full max-w-[380px] bg-white border rounded-[20px] p-7"><h1 class="text-[22px] font-[800]">Welcome back</h1><form method="POST" class="mt-6 space-y-3"><input name="email" type="email" placeholder="Email" class="w-full bg-slate-50 border rounded-full px-4 py-3 text-[13px]" required><input name="password" type="password" placeholder="Password" class="w-full bg-slate-50 border rounded-full px-4 py-3 text-[13px]" required><button class="w-full bg-[#0f172a] text-white py-3 rounded-full font-[700]">Log in</button></form></div></div>"""
    return render_template_string(HEAD + body + FOOT)
@app.route("/logout")
def logout():
    session.pop("user", None); return redirect("/")
@app.route("/api/signals")
def api():
    return jsonify([engine(s) for s in REAL])
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
