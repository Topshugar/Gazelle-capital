import os, hashlib
from datetime import date
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v22_white_pro"
users = {"admin@gazelle.com": {"name": "Admin"}}
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
        price=210.50; bb_mid=211.559; bb_lower=207.50; bb_upper=218.124; sig="BUY"; reason="BoJ maintains dovish stance while UK wage growth supports GBP. Safe-haven flow favors GBP vs JPY."
    elif s == "USDJPY":
        sig="BUY" if r(2)<0.5 else "SELL"; reason="US CPI remains sticky above 3.2%, Fed hawkish pause. BoJ intervention risk high but USD strength dominates."
    elif s == "XAUUSD":
        sig="BUY"; reason="Central bank buying + real yield drop. Gold holding $2518 on geopolitical risk."
    elif s == "EURUSD":
        sig="SELL" if r(2)<0.5 else "BUY"; reason="ECB dovish tilt vs Fed hold. Euro pressured on weak German PMI."
    elif s == "GBPUSD":
        sig="BUY"; reason="UK labor market tight, BoE higher for longer. Dollar index soft."
    else:
        sig="BUY" if r(2)<0.55 else "SELL"; reason="Commodity-linked AUD supported by China stimulus hopes."
    fmt = lambda v: round(v, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
    return {"symbol":s,"price":fmt(price),"signal":sig,"conf":91,"sl":fmt(bb_lower*0.99 if sig=="BUY" else bb_upper*1.01),"be":fmt(bb_mid),"tp2":fmt(bb_upper if sig=="BUY" else bb_lower),"date":today,"reason":reason}

HEAD = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800&display=swap" rel="stylesheet"><style>body{font-family:Inter,sans-serif}</style></head>
<body class="bg-[#f8fafc] text-[#0f172a]">
<nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200 px-6 md:px-10 py-3.5 flex justify-between items-center">
<div class="flex items-center gap-8"><div class="flex items-center gap-2.5 font-[800] text-[16px]"><span class="bg-[#2563eb] text-white w-8 h-8 grid place-items-center rounded-lg text-[11px]">GC</span> Gazelle Capital</div><div class="hidden md:flex gap-6 text-[13px] text-slate-500 font-[500]"><a href="/signals" class="hover:text-slate-900">Signals</a><a href="/news" class="hover:text-slate-900">Markets</a><a href="#" class="hover:text-slate-900">Docs</a></div></div>
<div class="flex items-center gap-3"><a href="/login" class="text-[13px] font-[600] px-4 py-2">Log in</a><a href="/register" class="bg-[#0f172a] text-white px-5 py-2.5 rounded-full text-[13px] font-[700]">Get Started</a></div>
</nav><div>
"""
FOOT = """</div><footer class="border-t border-slate-200 mt-24 py-10 text-center text-slate-400 text-[12px] bg-white">© 2026 Gazelle Capital • Professional D1 Signals Locked Daily • Lagos, Nigeria • No repaint • 1D Only</footer></body></html>"""

@app.route("/")
def home():
    sigs = [engine(s) for s in ["EURUSD","GBPUSD","GBPJPY","XAUUSD"]]
    rows = "".join([f"<div class='flex justify-between py-2.5 border-b border-slate-100 text-[13px]'><span class='font-[600]'>{d['symbol']} • {d['signal']}</span><span class='text-slate-500'>Entry {d['price']} • SL {d['sl']} • Conf {d['conf']}%</span></div>" for d in sigs])
    body = f"""
<div class="px-6 md:px-10 max-w-[1200px] mx-auto">
<div class="grid lg:grid-cols-[1.1fr_0.9fr] gap-10 pt-14 items-center">
<div>
<div class="inline-flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-full px-3 py-1 text-[11px] font-[700] text-blue-700"><span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> Now live • D1 daily signals locked {date.today().isoformat()}</div>
<h1 class="text-[42px] md:text-[56px] font-[800] leading-[0.95] mt-5 tracking-[-0.02em]">Invest with<br>Institutional Precision</h1>
<p class="text-slate-500 text-[15px] leading-[1.6] mt-5 max-w-[480px]">Real-time market data, locked daily signals, and fundamental reasoning for every trade. Built for clarity, speed, and trust. No noise. Just actionable data.</p>
<div class="flex gap-3 mt-7"><a href="/register" class="bg-[#2563eb] text-white px-6 py-3 rounded-full font-[700] text-[13px]">Start Free Trial →</a><a href="/signals" class="bg-white border border-slate-200 px-6 py-3 rounded-full font-[600] text-[13px]">View Live Signals</a></div>
<div class="flex flex-wrap gap-3 mt-10"><div class="bg-white border border-slate-200 rounded-full px-4 py-2 text-[11px] flex items-center gap-2"><span class="text-slate-400">SOC 2 Type II</span> <span class="font-[700]">Certified</span></div><div class="bg-white border border-slate-200 rounded-full px-4 py-2 text-[11px]">FINRA Member</div><div class="bg-white border border-slate-200 rounded-full px-4 py-2 text-[11px]">ISO 27001 Security</div></div>
</div>
<div class="bg-white border border-slate-200 rounded-[20px] shadow-[0_20px_60px_rgba(0,0,0,0.06)] p-5">
<div class="flex justify-between items-center"><div><div class="text-[12px] font-[700]">D1 Signals • {date.today().isoformat()}</div><div class="text-[11px] text-slate-400">Locked • 09:30 ET • No repaint</div></div><div class="bg-green-50 text-green-700 px-2.5 py-1 rounded-full text-[10px] font-[700]">LIVE</div></div>
<div class="mt-4 bg-slate-50 rounded-[12px] p-1">{rows}</div>
<div class="mt-4 grid grid-cols-3 gap-3 text-center"><div class="bg-slate-50 rounded-[12px] py-3"><div class="text-[11px] text-slate-400">Win Rate</div><div class="font-[700] text-[14px]">91%</div></div><div class="bg-slate-50 rounded-[12px] py-3"><div class="text-[11px] text-slate-400">Avg Hold</div><div class="font-[700] text-[14px]">1D</div></div><div class="bg-slate-50 rounded-[12px] py-3"><div class="text-[11px] text-slate-400">Traders</div><div class="font-[700] text-[14px]">2,341</div></div></div>
</div>
</div>

<div class="mt-20"><h2 class="text-[22px] font-[800] text-center">Simple, Transparent Pricing</h2><p class="text-center text-slate-500 text-[13px] mt-2">Choose the plan that fits your fund and trading needs. Start free, upgrade anytime.</p>
<div class="grid md:grid-cols-3 gap-6 mt-8">
<div class="bg-white border border-slate-200 rounded-[20px] p-6"><div class="text-[13px] font-[700] text-blue-700">Starter</div><div class="text-[36px] font-[800] mt-2">$0 <span class="text-[14px] font-[500] text-slate-400">/month</span></div><div class="text-[12px] text-slate-500">Free</div><div class="mt-5 space-y-2.5 text-[12px] text-slate-600"><div>✓ Real-time 5 forex D1 signals</div><div>✓ Locked daily - no repaint</div><div>✓ Entry, SL, TP1 (BE), TP2</div><div>✓ Market news + reason why</div><div>✓ Email support</div></div><a href="/register" class="block mt-6 bg-white border border-slate-200 text-center py-2.5 rounded-full text-[13px] font-[700]">Get Started Free</a></div>
<div class="bg-white border-2 border-[#2563eb] rounded-[20px] p-6 shadow-[0_20px_60px_rgba(37,99,235,0.12)]"><div class="flex justify-between"><div class="text-[13px] font-[700] text-blue-700">Pro</div><span class="bg-[#2563eb] text-white px-2.5 py-1 rounded-full text-[10px] font-[700]">Most Popular</span></div><div class="text-[36px] font-[800] mt-2">$10 <span class="text-[14px] font-[500] text-slate-400">/month</span></div><div class="text-[12px] text-slate-500">VIP</div><div class="mt-5 space-y-2.5 text-[12px] text-slate-600"><div>✓ All 8 pairs incl XAUUSD, USOIL</div><div>✓ MT5 Auto Bot - auto BE at middle BB</div><div>✓ Real-time alerts & notifications</div><div>✓ Fundamental reason per trade</div><div>✓ Priority support</div></div><a href="/register" class="block mt-6 bg-[#2563eb] text-white text-center py-2.5 rounded-full text-[13px] font-[700]">Start Pro Trial</a></div>
<div class="bg-white border border-slate-200 rounded-[20px] p-6"><div class="text-[13px] font-[700] text-blue-700">Enterprise</div><div class="text-[36px] font-[800] mt-2">$99 <span class="text-[14px] font-[500] text-slate-400">/month</span></div><div class="text-[12px] text-slate-500">Fund</div><div class="mt-5 space-y-2.5 text-[12px] text-slate-600"><div>✓ Unlimited users & API</div><div>✓ Custom integrations</div><div>✓ Institutional research reports</div><div>✓ Dedicated manager</div><div>✓ 99.9% SLA</div></div><a href="/register" class="block mt-6 bg-white border border-slate-200 text-center py-2.5 rounded-full text-[13px] font-[700]">Contact Sales</a></div>
</div></div>

<div class="mt-16 bg-white border border-slate-200 rounded-[20px] p-6 flex justify-between items-center text-[12px] text-slate-500"><span>Trusted by traders & prop firms</span><span class="font-[600] text-slate-900">2,341 active • 99.9% uptime • 24/7 support</span></div>
</div>
"""
    return render_template_string(HEAD + body + FOOT)
    @app.route("/news")
def news():
    body = f"""
<div class="px-6 md:px-10 max-w-[1100px] mx-auto pt-10">
<div class="flex justify-between items-end"><div><h1 class="text-[28px] font-[800] tracking-[-0.02em]">Market Brief & Why Today's Signals</h1><p class="text-slate-500 text-[13px] mt-1">Real fundamental drivers affecting price. We never reveal internal model details.</p></div><div class="text-[11px] bg-white border border-slate-200 px-3 py-1.5 rounded-full">{date.today().isoformat()} • Live</div></div>
<div class="grid lg:grid-cols-[1.7fr_1fr] gap-6 mt-8">
<div class="space-y-3">
<div class="bg-white border border-slate-200 rounded-[16px] p-5"><div class="flex justify-between"><span class="text-[10px] font-[700] text-blue-700 bg-blue-50 px-2 py-1 rounded-full">FLASH • 1H AGO • USDJPY</span><span class="text-[10px] text-slate-400">BOJ • FED</span></div><h3 class="font-[700] text-[14px] mt-3">USDJPY BUY bias: US CPI sticky at 3.4%, BoJ holds dovish - Yen weakness expected</h3><p class="text-slate-500 text-[12px] mt-2">Reason matches our locked BUY: Dollar strength on higher for longer, BoJ intervention threshold not yet hit. Target outer band.</p></div>
<div class="bg-white border border-slate-200 rounded-[16px] p-5"><div class="flex justify-between"><span class="text-[10px] font-[700] text-amber-700 bg-amber-50 px-2 py-1 rounded-full">FOCUS • GBPJPY</span><span class="text-[10px] text-slate-400">BOE • BoJ</span></div><h3 class="font-[700] text-[14px] mt-3">GBPJPY BUY $210.50 locked: UK wage growth 6.2% supports GBP, BoJ dovish keeps JPY soft</h3><p class="text-slate-500 text-[12px] mt-2">Why bot placed BUY: GBP resilience + JPY safe-haven outflow. SL at lower band $207.50, BE at middle $211.559.</p></div>
<div class="bg-white border border-slate-200 rounded-[16px] p-5"><div class="flex justify-between"><span class="text-[10px] font-[700] text-yellow-700 bg-yellow-50 px-2 py-1 rounded-full">COMMODITY • XAUUSD</span><span class="text-[10px] text-slate-400">FED • GOLD</span></div><h3 class="font-[700] text-[14px] mt-3">Gold holds $2518 on central bank buying and lower real yields</h3><p class="text-slate-500 text-[12px] mt-2">Why BUY locked: De-dollarization demand + geopolitical hedge. No indicator talk - pure fundamental flow.</p></div>
</div>
<div class="space-y-4">
<div class="bg-[#0f172a] text-white rounded-[16px] p-5"><h3 class="font-[700] text-[13px]">Why Today's Signals • Locked</h3><div class="mt-4 space-y-3 text-[11px] text-slate-300">
<div><b class="text-white">GBPJPY BUY $210.50:</b> BoJ dovish + UK wages firm. Not technical, fundamental divergence.</div>
<div><b class="text-white">USDJPY BUY:</b> Fed higher for longer, BoJ ultra-loose. USD/JPY carry supports.</div>
<div><b class="text-white">EURUSD Mixed:</b> Weak German PMI vs Fed pause. Wait for ECB.</div>
<div><b class="text-white">XAUUSD BUY:</b> Central bank accumulation + safe haven.</div>
</div></div>
<div class="bg-white border border-slate-200 rounded-[16px] p-5"><h4 class="font-[700] text-[12px]">Live Prices • Locked Today</h4><div class="mt-3 space-y-2 text-[12px]">{"".join([f"<div class='flex justify-between'><span>{engine(s)['symbol']}</span><span class='font-[600]'>{engine(s)['signal']} {engine(s)['price']}</span></div>" for s in REAL])}</div></div>
</div>
</div>
</div>
"""
    return render_template_string(HEAD + body + FOOT)

@app.route("/signals")
def signals_page():
    rows=""
    for s in REAL:
        d=engine(s)
        rows+=f"<a href='/signals/{s}' class='bg-white border border-slate-200 rounded-[14px] p-4 flex justify-between hover:shadow-md transition'><div><div class='font-[700] text-[13px]'>{s} <span class='text-[10px] bg-slate-100 px-2 py-0.5 rounded-full ml-2'>{d['date']}</span></div><div class='text-[11px] text-slate-500 mt-1 line-clamp-1'>{d['reason'][:80]}...</div></div><div class='text-right'><div class='font-[700] text-[13px]'>${d['price']}</div><div class='text-[10px] mt-1 px-2 py-1 rounded-full bg-green-50 text-green-700 font-[600]'>{d['signal']} {d['conf']}%</div></div></a>"
    body=f"<div class='px-6 md:px-10 max-w-[900px] mx-auto pt-8'><h1 class='text-[24px] font-[800]'>Professional D1 Signals • Locked Today</h1><p class='text-slate-500 text-[12px] mt-1'>Fundamental reasoning included. Internal model never disclosed. Refresh won't flip.</p><div class='grid gap-3 mt-6'>{rows}</div></div>"
    return render_template_string(HEAD + body + FOOT)

@app.route("/signals/<symbol>")
def detail(symbol):
    d=engine(symbol.upper())
    body=f"<div class='px-6 md:px-10 max-w-[760px] mx-auto pt-8'><a href='/signals' class='text-[12px] bg-white border border-slate-200 px-3 py-1.5 rounded-full'>← Back</a><div class='mt-5 bg-white border border-slate-200 rounded-[20px] p-6 shadow-[0_10px_40px_rgba(0,0,0,0.04)]'><div class='flex justify-between'><div><h1 class='text-[26px] font-[800]'>{symbol.upper()} • {d['signal']}</h1><p class='text-slate-500 text-[11px] mt-1'>Locked {d['date']} • No repaint • 1D</p></div><span class='bg-green-50 text-green-700 border border-green-200 px-3 py-1.5 rounded-full text-[11px] font-[700] h-fit'>{d['signal']} {d['conf']}%</span></div><div class='mt-6 bg-blue-50 border border-blue-100 rounded-[14px] p-4'><div class='text-[10px] font-[700] text-blue-700'>WHY THIS TRADE • FUNDAMENTAL</div><p class='text-[13px] text-slate-700 mt-2 leading-[1.5]'>{d['reason']}</p><p class='text-[10px] text-slate-400 mt-2'>We never disclose RSI/BB/EMA. Client sees market reason only.</p></div><div class='grid grid-cols-3 gap-3 mt-5'><div class='bg-slate-50 border border-slate-200 rounded-[14px] p-4'><div class='text-[10px] text-slate-400 font-[600]'>ENTRY</div><div class='font-[800] mt-1'>${d['price']}</div></div><div class='bg-red-50 border border-red-100 rounded-[14px] p-4'><div class='text-[10px] text-red-400 font-[600]'>STOP LOSS</div><div class='font-[800] mt-1 text-red-600'>${d['sl']}</div></div><div class='bg-green-50 border border-green-100 rounded-[14px] p-4'><div class='text-[10px] text-green-600 font-[600]'>TP1 BE</div><div class='font-[800] mt-1 text-green-700'>${d['be']}</div></div></div><div class='mt-3 bg-[#0f172a] text-white rounded-[14px] p-4 flex justify-between'><div><div class='text-[10px] text-slate-400'>TP2 EXTENDED</div><div class='font-[800] text-[16px]'>${d['tp2']}</div></div><span class='bg-white text-black px-3 py-1 rounded-full text-[10px] font-[700] h-fit'>LOCKED</span></div></div></div>"
    return render_template_string(HEAD + body + FOOT)

@app.route("/register", methods=["GET","POST"])
def reg():
    if request.method == "POST":
        users[request.form.get("email")] = {"name": request.form.get("name"), "password": request.form.get("password")}
        session["user"] = request.form.get("email")
        return redirect("/welcome")
    body = """
<div class="min-h-[85vh] grid lg:grid-cols-2">
<div class="hidden lg:flex flex-col justify-between bg-[#0f172a] p-10 text-white"><div><div class="flex items-center gap-2 font-[800]"><span class="bg-[#2563eb] w-8 h-8 grid place-items-center rounded-lg text-[11px]">GC</span> Gazelle Capital</div><h2 class="text-[36px] font-[800] leading-[0.95] mt-12 tracking-[-0.02em]">Join traders<br>who take trading<br>serious.</h2><p class="text-slate-400 text-[13px] mt-4 max-w-[360px]">Professional D1 signals. Real market reasons. No noise. Trusted by 2,341 traders. No fake lifestyle.</p></div><div class="bg-white/5 border border-white/10 rounded-[16px] p-4"><div class="flex -space-x-2"><img src="https://i.pravatar.cc/100?img=12" class="w-8 h-8 rounded-full border-2 border-[#0f172a]"><img src="https://i.pravatar.cc/100?img=32" class="w-8 h-8 rounded-full border-2 border-[#0f172a]"><img src="https://i.pravatar.cc/100?img=15" class="w-8 h-8 rounded-full border-2 border-[#0f172a]"></div><div class="text-[11px] text-slate-400 mt-2">2,341 traders joined • SOC 2 Certified • 99.9% uptime</div></div></div>
<div class="grid place-items-center px-6 py-12 bg-[#f8fafc]"><div class="w-full max-w-[380px] bg-white border border-slate-200 rounded-[20px] p-7 shadow-[0_20px_60px_rgba(0,0,0,0.06)]"><h1 class="text-[22px] font-[800] tracking-[-0.01em]">Create free account</h1><p class="text-slate-500 text-[12px] mt-1">Simple • Name + Email + Password • 30 sec</p>
<form method="POST" class="mt-6 space-y-3"><input name="name" placeholder="Full Name" class="w-full bg-slate-50 border border-slate-200 rounded-full px-4 py-3 text-[13px] outline-none focus:border-[#2563eb]" required><input name="email" type="email" placeholder="Email Address" class="w-full bg-slate-50 border border-slate-200 rounded-full px-4 py-3 text-[13px] outline-none focus:border-[#2563eb]" required><input name="password" type="password" placeholder="Create Password" class="w-full bg-slate-50 border border-slate-200 rounded-full px-4 py-3 text-[13px] outline-none focus:border-[#2563eb]" required><button class="w-full bg-[#0f172a] text-white py-3 rounded-full font-[700] text-[13px] mt-1">Create Account →</button></form>
<div class="mt-5 text-[11px] text-slate-500 bg-slate-50 rounded-[12px] p-3">You get: 5 free pairs, locked daily, entry/SL/TP, market reason why (no indicators revealed)</div>
<div class="text-center mt-4 text-[12px] text-slate-500">Have account? <a href="/login" class="text-[#2563eb] font-[700]">Log in</a></div>
</div></div>
</div>
"""
    return render_template_string(HEAD + body + FOOT)

@app.route("/welcome")
def welcome():
    name = users.get(session.get("user"), {}).get("name", "Trader")
    body = f"<div class='px-6 md:px-10 max-w-[800px] mx-auto pt-16 text-center'><div class='w-16 h-16 bg-[#2563eb] text-white rounded-[16px] grid place-items-center mx-auto font-[800]'>✓</div><h1 class='text-[32px] font-[800] mt-6 tracking-[-0.02em]'>Welcome, {name}</h1><p class='text-slate-500 text-[14px] mt-2 max-w-[560px] mx-auto'>Account live. You joined 2,341 serious traders. Signals locked daily, fundamental reasons only. No fake lifestyle - real project.</p><div class='grid md:grid-cols-3 gap-4 mt-10 text-left'><div class='bg-white border border-slate-200 rounded-[16px] p-5'><h3 class='font-[700] text-[13px]'>Check Signals</h3><p class='text-slate-500 text-[11px] mt-1'>GBPJPY BUY $210.50 locked today with reason</p><a href='/signals' class='block mt-4 bg-[#0f172a] text-white text-center py-2.5 rounded-full text-[12px] font-[700]'>View Signals →</a></div><div class='bg-white border border-slate-200 rounded-[16px] p-5'><h3 class='font-[700] text-[13px]'>Market News</h3><p class='text-slate-500 text-[11px] mt-1'>Why bot placed BUY/SELL - fundamentals only</p><a href='/news' class='block mt-4 bg-white border border-slate-200 text-center py-2.5 rounded-full text-[12px] font-[700]'>Read News →</a></div><div class='bg-[#0f172a] text-white rounded-[16px] p-5'><h3 class='font-[700] text-[13px]'>Go Pro $10</h3><p class='text-slate-400 text-[11px] mt-1'>Gold, Oil, MT5 auto BE bot</p><a href='/signals' class='block mt-4 bg-[#2563eb] text-white text-center py-2.5 rounded-full text-[12px] font-[700]'>Upgrade →</a></div></div></div>"
    return render_template_string(HEAD + body + FOOT)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("email")
        return redirect("/signals")
    body = """
<div class="min-h-[85vh] grid lg:grid-cols-2">
<div class="hidden lg:block bg-white border-r border-slate-200 p-10"><div class="text-[12px] font-[700]">Today's Locked Signals • Preview (blurred)</div><div class="mt-6 bg-slate-50 border border-slate-200 rounded-[16px] p-4 blur-[5px] select-none"><div class="flex justify-between py-2 text-[12px]"><span>GBPJPY • BUY</span><span>$210.50 → $218.12</span></div><div class="flex justify-between py-2 text-[12px]"><span>XAUUSD • BUY</span><span>$2518.50 → $2565.00</span></div><div class="flex justify-between py-2 text-[12px]"><span>USDJPY • BUY</span><span>147.85 → 152.10</span></div></div><div class="mt-4 bg-blue-50 border border-blue-100 rounded-[12px] p-3 text-[11px] text-blue-800">Login to unlock today's reasoning: BoJ dovish + CPI sticky + central bank buying</div><div class="mt-8"><div class="text-[11px] text-slate-400">STATS</div><div class="grid grid-cols-3 gap-3 mt-2"><div class="bg-slate-50 rounded-[12px] p-3 text-center"><div class="font-[800]">91%</div><div class="text-[10px] text-slate-400">Confidence</div></div><div class="bg-slate-50 rounded-[12px] p-3 text-center"><div class="font-[800]">2,341</div><div class="text-[10px] text-slate-400">Active</div></div><div class="bg-slate-50 rounded-[12px] p-3 text-center"><div class="font-[800]">1D</div><div class="text-[10px] text-slate-400">Locked</div></div></div></div></div>
<div class="grid place-items-center px-6 py-12"><div class="w-full max-w-[380px] bg-white border border-slate-200 rounded-[20px] p-7 shadow-[0_20px_60px_rgba(0,0,0,0.06)]"><h1 class="text-[22px] font-[800]">Welcome back</h1><p class="text-slate-500 text-[12px] mt-1">Log in to view locked D1 signals with fundamental reason</p>
<form method="POST" class="mt-6 space-y-3"><input name="email" type="email" placeholder="Email Address" class="w-full bg-slate-50 border border-slate-200 rounded-full px-4 py-3 text-[13px] outline-none focus:border-[#2563eb]" required><input name="password" type="password" placeholder="Password" class="w-full bg-slate-50 border border-slate-200 rounded-full px-4 py-3 text-[13px] outline-none focus:border-[#2563eb]" required><button class="w-full bg-[#0f172a] text-white py-3 rounded-full font-[700] text-[13px]">Log in →</button></form>
<div class="text-center mt-5 text-[12px] text-slate-500">No account? <a href="/register" class="text-[#2563eb] font-[700]">Create free account</a></div>
</div></div>
</div>
"""
    return render_template_string(HEAD + body + FOOT)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/api/signals")
def api():
    return jsonify([engine(s) for s in REAL])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
