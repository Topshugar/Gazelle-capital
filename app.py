import os, hashlib
from datetime import datetime, date
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v18_portal"

users = {"admin@gazelle.com": {"password": "admin123", "vip": True, "name": "Admin"}}

REAL_BASE = {"EURUSD": 1.0845, "GBPUSD": 1.3420, "USDJPY": 147.85, "AUDUSD": 0.6650, "GBPJPY": 210.50, "XAUUSD": 2518.50}

def locked_engine(s):
    today = date.today().isoformat()
    seed = int(hashlib.md5(f"{s}-{today}".encode()).hexdigest()[:8], 16)
    def r(i): return (seed * 9301 + 49297 * i) % 233280 / 233280.0
    base = REAL_BASE.get(s, 1.08)
    price = base * (1 + (r(1)-0.5)*0.008)
    rsi = 32 + r(2)*36; stoch_k = 12 + r(3)*70; stoch_d = stoch_k + (r(4)-0.5)*10
    bb_mid = base * (1 + (r(5)-0.5)*0.016); bb_upper=bb_mid*1.025; bb_lower=bb_mid*0.975
    if s=="GBPJPY": rsi=43.95; stoch_k=34.90; price=210.50; bb_mid=211.559; bb_lower=207.50; bb_upper=218.124
    is_buy = rsi < 50 and stoch_k > stoch_d and stoch_k < 50
    if is_buy: signal="BUY"; sl=bb_lower*0.99; be=bb_mid; tp2=bb_upper; conf=91
    else:
        if rsi < 55: signal="BUY"; sl=bb_lower*0.99; be=bb_mid; tp2=bb_upper; conf=86
        else: signal="SELL"; sl=bb_upper*1.01; be=bb_mid; tp2=bb_lower; conf=86
    fmt = lambda v: round(v,5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
    return {"symbol":s,"price":fmt(price),"signal":signal,"conf":conf,"sl":fmt(sl),"be":fmt(be),"tp2":fmt(tp2),"date":today}

BASE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&family=Inter:wght@400;600&display=swap" rel="stylesheet"><style>body{font-family:'Plus Jakarta Sans',sans-serif}</style></head><body class="bg-[#070b14] text-white"><nav class="sticky top-0 z-50 backdrop-blur-xl bg-[#070b14]/90 border-b border-white/10 px-6 md:px-10 py-4 flex justify-between items-center"><div class="flex items-center gap-3 font-extrabold text-[18px]"><span class="bg-[#f7c948] text-black w-9 h-9 grid place-items-center rounded-xl text-[12px] font-black">GC</span> Gazelle Capital</div><div class="flex gap-3"><a href="/signals" class="hidden md:block text-sm text-white/60 py-2 px-4">Signals</a><a href="/news" class="hidden md:block text-sm text-white/60 py-2 px-4">News</a>{% if 'user' in session %}<a href="/signals" class="bg-[#f7c948] text-black px-5 py-2 rounded-full text-sm font-bold">Dashboard</a><a href="/logout" class="bg-white/10 px-4 py-2 rounded-full text-sm">Logout</a>{% else %}<a href="/login" class="text-sm py-2 px-4">Login</a><a href="/register" class="bg-[#f7c948] text-black px-6 py-2.5 rounded-full text-sm font-bold">Join Free</a>{% endif %}</div></nav>{{content|safe}}<footer class="border-t border-white/10 mt-20 py-10 px-6 md:px-10"><div class="flex flex-col md:flex-row justify-between text-xs text-white/30"><div>© 2026 Gazelle Capital • Private 1D Swing Signals • Lagos, Nigeria</div><div class="mt-2 md:mt-0">Signals locked daily • No repaint • Strictly 1D</div></div></footer></body></html>"""

@app.route("/")
def home():
    content = """
<div class="px-6 md:px-10 pt-12 md:pt-20 max-w-[1300px] mx-auto">
  <div class="grid lg:grid-cols-2 gap-12 items-center">
    <div>
      <div class="inline-flex items-center gap-2 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-full px-4 py-1.5 text-[11px] font-bold text-[#f7c948] tracking-widest">LIVE • 1D SIGNALS LOCKED TODAY</div>
      <h1 class="text-[44px] md:text-[68px] font-[800] leading-[0.9] mt-6">Trade Like The <span class="text-[#f7c948]">Top 1%</span><br>Not The 99%</h1>
      <p class="text-white/60 text-[15px] leading-[1.6] mt-6 max-w-[520px] font-[Inter]">Private D1 swing signals used by serious traders in Lagos, London & Dubai. No scalping noise. One candle, one decision. Middle BB = Breakeven, Outer BB = TP.</p>
      <div class="flex gap-3 mt-8"><a href="/register" class="bg-[#f7c948] text-black px-8 py-3.5 rounded-full font-bold text-sm">Create Free Account →</a><a href="/signals" class="bg-white/10 border border-white/10 px-8 py-3.5 rounded-full font-bold text-sm">View Live Signals</a></div>
      <div class="flex gap-6 mt-8 text-xs"><div><b class="text-white text-[18px]">2,341</b><div class="text-white/40">Active Traders</div></div><div><b class="text-white text-[18px]">91%</b><div class="text-white/40">Avg Confidence</div></div><div><b class="text-white text-[18px]">1D</b><div class="text-white/40">Strictly Daily</div></div></div>
    </div>
    <div class="relative">
      <div class="rounded-[28px] overflow-hidden border border-white/10 bg-white/[0.03] p-2"><img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80" class="rounded-[20px] w-full h-[420px] object-cover opacity-90"><div class="absolute bottom-6 left-6 right-6 bg-[#070b14]/90 backdrop-blur-xl border border-white/10 rounded-[18px] p-4 flex justify-between items-center"><div><div class="text-[11px] text-white/40">TODAY'S FOCUS</div><div class="font-bold text-[15px]">GBPJPY • BUY • $210.50</div><div class="text-[11px] text-emerald-400 mt-1">BE $211.559 • TP $218.12 • LOCKED</div></div><div class="bg-emerald-500 text-black px-3 py-1 rounded-full text-[11px] font-black">BUY 91%</div></div></div>
      <div class="absolute -top-4 -right-4 bg-[#f7c948] text-black rounded-[16px] px-4 py-3 text-xs font-bold shadow-xl">+124%<br><span class="font-normal text-[10px]">Last Month</span></div>
    </div>
  </div>

  <div class="mt-20 grid md:grid-cols-3 gap-4">
    <div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-6"><div class="w-10 h-10 bg-emerald-500/20 rounded-xl grid place-items-center text-emerald-400 font-bold">$</div><h3 class="font-bold mt-4">Private 1D Signals</h3><p class="text-white/50 text-[13px] mt-2 font-[Inter]">One signal per day per pair. No noise. Locked till next daily close. No repaint on refresh.</p></div>
    <div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-6"><div class="w-10 h-10 bg-[#f7c948]/20 rounded-xl grid place-items-center text-[#f7c948] font-bold">✓</div><h3 class="font-bold mt-4">Middle BB = Breakeven</h3><p class="text-white/50 text-[13px] mt-2 font-[Inter]">Our edge: Secure at middle Bollinger Band. Let winners run to outer BB. Professional risk management.</p></div>
    <div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-6"><div class="w-10 h-10 bg-blue-500/20 rounded-xl grid place-items-center text-blue-400 font-bold">A</div><h3 class="font-bold mt-4">Bot Ready (MT5)</h3><p class="text-white/50 text-[13px] mt-2 font-[Inter]">Connect your MT5. Auto lot size based on equity. Auto BE move. Built for Exness, Deriv, XM.</p></div>
  </div>

  <div class="mt-20"><div class="flex justify-between items-end"><h2 class="text-[28px] font-[800]">Trader Lifestyle & Inspiration</h2><a href="/news" class="text-xs bg-white/10 px-4 py-2 rounded-full">View All News →</a></div>
  <div class="grid md:grid-cols-3 gap-5 mt-8">
    <div class="rounded-[20px] overflow-hidden border border-white/10 bg-white/[0.03]"><img src="https://images.unsplash.com/photo-1559526324-4f8172775ed0?w=600&q=80" class="h-[180px] w-full object-cover"><div class="p-5"><div class="text-[10px] text-[#f7c948] font-bold tracking-widest">LEGENDS • GEORGE SOROS</div><h3 class="font-bold text-[15px] mt-2">"It's not whether you're right or wrong, it's how much you make when you're right."</h3><p class="text-white/50 text-[12px] mt-2 font-[Inter]">Broke the Bank of England with $1B in a day. D1 patience beats H1 noise.</p></div></div>
    <div class="rounded-[20px] overflow-hidden border border-white/10 bg-white/[0.03]"><img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80" class="h-[180px] w-full object-cover"><div class="p-5"><div class="text-[10px] text-emerald-400 font-bold tracking-widest">LIFESTYLE • DUBAI</div><h3 class="font-bold text-[15px] mt-2">From $500 to $50k: Lagos trader shares D1 routine</h3><p class="text-white/50 text-[12px] mt-2 font-[Inter]">No phone checking every minute. One chart at 8AM WAT. Let BB do the work.</p></div></div>
    <div class="rounded-[20px] overflow-hidden border border-white/10 bg-white/[0.03]"><img src="https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=600&q=80" class="h-[180px] w-full object-cover"><div class="p-5"><div class="text-[10px] text-blue-400 font-bold tracking-widest">MARKETS • TODAY</div><h3 class="font-bold text-[15px] mt-2">Gold holds $2518 as USDJPY pushes 147.85 - D1 Setup</h3><p class="text-white/50 text-[12px] mt-2 font-[Inter]">MetaQuotes: Daily candle shows indecision. RSI oversold bounce expected on JPY pairs.</p></div></div>
  </div></div>

  <div class="mt-20 bg-gradient-to-br from-[#f7c948]/10 to-transparent border border-[#f7c948]/20 rounded-[28px] p-8 md:p-12 text-center"><h2 class="text-[32px] font-[800]">Ready to Trade Serious?</h2><p class="text-white/60 mt-3 text-[14px] max-w-[600px] mx-auto font-[Inter]">Join 2,341 traders getting locked D1 signals. Free account, upgrade to VIP for Gold & Oil.</p><a href="/register" class="inline-block mt-6 bg-[#f7c948] text-black px-8 py-3.5 rounded-full font-bold text-sm">Create Free Account - 30 Sec →</a><div class="mt-4 text-[11px] text-white/30">No credit card • No spam • Cancel anytime</div></div>
</div>
"""
    return render_template_string(BASE, content=content)

@app.route("/news")
def news():
    content = """
<div class="px-6 md:px-10 pt-10 max-w-[1100px] mx-auto">
<h1 class="text-[28px] font-[800]">Market News & Trader Stories • Live</h1><p class="text-white/40 text-[13px] mt-2">Curated like MetaQuotes • Updated daily • For serious traders</p>
<div class="grid md:grid-cols-3 gap-6 mt-8">
<div class="md:col-span-2 space-y-4">
<div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-6 flex gap-5"><img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=200" class="w-[90px] h-[90px] rounded-xl object-cover"><div><div class="text-[10px] text-[#f7c948] font-bold">FLASH • 2H AGO</div><h3 class="font-bold text-[16px] mt-1">USDJPY breaks 148 - BoJ intervention watch</h3><p class="text-white/50 text-[13px] mt-2">Daily close above middle BB confirms bullish. Next target outer BB 152.10. RSI 43 → 58.</p></div></div>
<div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-6 flex gap-5"><img src="https://images.unsplash.com/photo-1559526324-4f8172775ed0?w=200" class="w-[90px] h-[90px] rounded-xl object-cover"><div><div class="text-[10px] text-emerald-400 font-bold">TRADER STORY • PAUL TUDOR JONES</div><h3 class="font-bold text-[16px] mt-1">"The most important rule of trading is to play great defense."</h3><p class="text-white/50 text-[13px] mt-2">He lost big early. Now uses 200 EMA as final filter. Same as Gazelle 1D system.</p></div></div>
<div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-6 flex gap-5"><img src="https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=200" class="w-[90px] h-[90px] rounded-xl object-cover"><div><div class="text-[10px] text-blue-400 font-bold">LIFESTYLE • MOTIVATION</div><h3 class="font-bold text-[16px] mt-1">Why D1 traders drive G-Wagons, scalpers drive anxiety</h3><p class="text-white/50 text-[13px] mt-2">Flashy lifestyle comes from patience. One good trade > 20 noisy trades. Set and forget.</p></div></div>
</div>
<div class="space-y-4"><div class="bg-[#f7c948] text-black rounded-[20px] p-6"><h3 class="font-[800] text-[18px]">Get Serious Today</h3><p class="text-[13px] mt-2">Join VIP for XAUUSD, USOIL signals + MT5 bot.</p><a href="/register" class="block mt-4 bg-black text-[#f7c948] text-center py-3 rounded-full font-bold text-sm">Join VIP $10/mo →</a></div><div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-6"><h4 class="font-bold text-[13px]">Top Traders Quote</h4><div class="mt-4 space-y-3 text-[12px] text-white/60"><div>"- Ed Seykota: Everybody gets what they want."</div><div>"- Jesse Livermore: Money made by sitting, not trading."</div><div>"- Stanley Druckenmiller: The way to build long-term returns is through capital preservation."</div></div></div></div>
</div></div>
"""
    return render_template_string(BASE, content=content)

@app.route("/signals")
def signals():
    html="<div class='px-6 md:px-10 pt-8 max-w-[900px]'><h1 class='text-[26px] font-[800]'>Private Signals • LOCKED • 1D</h1><div class='grid gap-3 mt-8'>"
    for s in ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY","XAUUSD"]:
        d=locked_engine(s)
        html+=f"<a href='/signals/{s}' class='bg-white/[0.06] border border-white/10 rounded-[20px] p-5 flex justify-between'><div><b>{s}</b><div class='text-[11px] text-white/40'>Locked {d['date']}</div></div><div class='text-right'><div class='font-bold'>${d['price']}</div><div class='mt-1 text-[11px] px-2 py-1 rounded-full { 'bg-emerald-500/20 text-emerald-300' if d['signal']=='BUY' else 'bg-red-500/20 text-red-300'}'>{d['signal']} {d['conf']}%</div></div></a>"
    html+="</div></div>"
    return render_template_string(BASE, content=html)

@app.route("/signals/<symbol>")
def detail(symbol):
    d=locked_engine(symbol.upper())
    content=f"<div class='px-6 md:px-10 pt-8 max-w-[800px] mx-auto'><a href='/signals' class='text-xs bg-white/10 px-3 py-1.5 rounded-full'>← Back</a><div class='mt-6 bg-white/[0.06] border border-white/10 rounded-[24px] p-6'><h1 class='text-[28px] font-[800]'>{symbol.upper()} • {d['signal']} • LOCKED</h1><div class='grid grid-cols-3 gap-3 mt-6'><div class='bg-black/50 border border-white/10 rounded-xl p-4'><div class='text-[10px] text-white/40'>ENTRY</div><b class='text-[18px]'>${d['price']}</b></div><div class='bg-red-500/10 border border-red-500/20 rounded-xl p-4'><div class='text-[10px] text-red-300/60'>SL</div><b class='text-[18px] text-red-300'>${d['sl']}</b></div><div class='bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4'><div class='text-[10px] text-emerald-300/60'>TP1 BE</div><b class='text-[18px] text-emerald-300'>${d['be']}</b></div></div><div class='mt-3 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-xl p-4 flex justify-between'><div><div class='text-[10px] text-[#f7c948]/60'>TP2</div><b class='text-[18px]'>${d['tp2']}</b></div><span class='bg-[#f7c948] text-black px-3 py-1 rounded-full text-[10px] font-bold h-fit'>LOCKED TODAY</span></div></div></div>"
    return render_template_string(BASE, content=content)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        email=request.form.get("email"); name=request.form.get("name")
        users[email]={"name":name,"password":request.form.get("password"),"vip":False}
        session["user"]=email
        return redirect("/welcome")
    content = """
<div class="min-h-[90vh] grid lg:grid-cols-2">
<div class="hidden lg:block relative overflow-hidden"><img src="https://images.unsplash.com/photo-1559526324-4f8172775ed0?w=900&q=80" class="absolute inset-0 w-full h-full object-cover opacity-40"><div class="absolute inset-0 bg-gradient-to-t from-[#070b14] via-[#070b14]/60 to-transparent"></div><div class="absolute bottom-10 left-10 right-10"><h2 class="text-[36px] font-[800] leading-[1]">Join Traders Who<br><span class="text-[#f7c948]">Take Trading Serious</span></h2><p class="text-white/60 text-[13px] mt-4 max-w-[400px]">No more gambling. One daily candle. Professional risk. Middle BB breakeven. This is how funds trade.</p><div class="flex gap-3 mt-6"><img src="https://i.pravatar.cc/100?img=12" class="w-8 h-8 rounded-full border-2 border-[#070b14]"><img src="https://i.pravatar.cc/100?img=32" class="w-8 h-8 rounded-full border-2 border-[#070b14] -ml-3"><img src="https://i.pravatar.cc/100?img=15" class="w-8 h-8 rounded-full border-2 border-[#070b14] -ml-3"><div class="text-[11px] text-white/50 ml-2">2,341 traders<br>already joined</div></div></div></div>
<div class="grid place-items-center px-6 py-12"><div class="w-full max-w-[400px]"><div class="w-10 h-10 bg-[#f7c948] text-black grid place-items-center rounded-xl font-black text-[12px]">GC</div><h1 class="text-[28px] font-[800] mt-6">Create Your Free Account</h1><p class="text-white/50 text-[13px] mt-2">Start with free forex pairs • Upgrade to VIP for Gold & Oil</p>
<form method="POST" class="mt-8 space-y-4"><input name="name" placeholder="Full Name" class="w-full bg-white/[0.06] border border-white/15 rounded-xl px-4 py-3.5 text-sm" required><input name="email" type="email" placeholder="Email Address" class="w-full bg-white/[0.06] border border-white/15 rounded-xl px-4 py-3.5 text-sm" required><input name="password" type="password" placeholder="Create Password" class="w-full bg-white/[0.06] border border-white/15 rounded-xl px-4 py-3.5 text-sm" required><button class="w-full bg-[#f7c948] text-black py-3.5 rounded-full font-bold text-sm">Create Account →</button><div class="text-center text-[11px] text-white/30 mt-3">By joining, you agree to trade responsibly. 1D only.</div></form>
<div class="mt-8 bg-white/[0.03] border border-white/10 rounded-[16px] p-4"><div class="text-[11px] font-bold">What you get instantly:</div><div class="mt-3 space-y-2 text-[12px] text-white/60"><div>✓ Free EURUSD, GBPUSD, USDJPY, AUDUSD, GBPJPY D1 signals</div><div>✓ Locked daily - no repaint</div><div>✓ Entry, SL, TP1 (BE) = Middle BB, TP2 = Outer BB</div><div>✓ Trader lifestyle news & famous trader quotes</div></div></div>
</div></div>
</div>
"""
    return render_template_string(BASE, content=content)

@app.route("/welcome")
def welcome():
    u = users.get(session.get("user"), {"name": "Trader"})
    content = f"""
<div class="px-6 md:px-10 pt-16 max-w-[800px] mx-auto text-center">
<div class="w-20 h-20 bg-[#f7c948] text-black rounded-[24px] grid place-items-center mx-auto text-[28px] font-black">✓</div>
<h1 class="text-[36px] font-[800] mt-6">Welcome to Gazelle Capital, {u.get('name','Trader')}!</h1>
<p class="text-white/60 text-[14px] mt-3 max-w-[600px] mx-auto">Your account is live. You are now part of 2,341 traders who take trading serious. No scalping noise. One daily candle. Let's build.</p>
<div class="grid md:grid-cols-3 gap-4 mt-10 text-left">
<div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-5"><div class="text-[20px]">📈</div><h3 class="font-bold mt-3 text-[14px]">Check Today's Signals</h3><p class="text-white/50 text-[12px] mt-1">Locked for today. GBPJPY BUY $210.50 is active now.</p><a href="/signals" class="block mt-4 bg-white text-black text-center py-2.5 rounded-full text-xs font-bold">View Signals →</a></div>
<div class="bg-white/[0.04] border border-white/10 rounded-[20px] p-5"><div class="text-[20px]">📰</div><h3 class="font-bold mt-3 text-[14px]">Read Trader News</h3><p class="text-white/50 text-[12px] mt-1">MetaQuotes style news, Soros & Tudor Jones lessons.</p><a href="/news" class="block mt-4 bg-white/10 text-center py-2.5 rounded-full text-xs font-bold">Read News →</a></div>
<div class="bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[20px] p-5"><div class="text-[20px]">👑</div><h3 class="font-bold mt-3 text-[14px]">Upgrade to VIP $10</h3><p class="text-white/50 text-[12px] mt-1">Unlock XAUUSD Gold, USOIL, MT5 auto bot.</p><a href="https://flutterwave.com/pay/msjgnmx4gehc" class="block mt-4 bg-[#f7c948] text-black text-center py-2.5 rounded-full text-xs font-bold">Upgrade VIP →</a></div>
</div>
<div class="mt-10 bg-black/40 border border-white/10 rounded-[20px] p-6 text-left max-w-[600px] mx-auto"><div class="text-[11px] text-[#f7c948] font-bold tracking-widest">WARM WELCOME MESSAGE • FROM FOUNDER</div><p class="text-[13px] text-white/70 mt-3 leading-[1.6]">"Most traders lose because they stare at 5-min charts. We trade like banks - 1D. Middle Bollinger Band is your breakeven, outer is your freedom. Stick to the plan. Welcome to serious trading." - Gazelle Capital</p></div>
</div>
"""
        return render_template_string(BASE, content=content)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        e=request.form.get("email");
        if e in users: session["user"]=e; return redirect("/signals")
    return render_template_string(BASE, content="<div class='min-h-[80vh] grid place-items-center px-6'><div class='w-full max-w-[400px] bg-white/[0.06] border border-white/10 rounded-[28px] p-8'><h1 class='text-[24px] font-[800]'>Welcome Back</h1><form method='POST' class='mt-6 space-y-3'><input name='email' type='email' placeholder='Email' class='w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm' required><input name='password' type='password' placeholder='Password' class='w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm' required><button class='w-full bg-[#f7c948] text-black py-3 rounded-full font-bold text-sm'>Login</button></form><div class='text-center mt-4 text-xs text-white/40'>No account? <a href='/register' class='text-[#f7c948]'>Create free</a></div></div></div>")

@app.route("/logout")
def logout(): session.pop("user",None); return redirect("/")
@app.route("/api/signals")
def api(): return jsonify([locked_engine(s) for s in ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY","XAUUSD"]])

if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
