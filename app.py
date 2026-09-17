import os, random
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_pro_v6_best_2026"

users = {
    "admin@gazelle.com": {"password": "admin123", "vip": True, "equity": 5000, "mt_account": {"login": "123456", "server": "Exness-MT5Real", "type": "MT5"}, "bot_active": True}
}

def sig_data(s):
    rsi = random.randint(28, 72)
    al = random.choice(["ALIGNED_BULL","ALIGNED_BEAR","SLEEPING"])
    bb = random.choice(["LOWER_TOUCH","UPPER_TOUCH","MIDDLE"])
    sig = "HOLD"
    if bb=="LOWER_TOUCH" and rsi<40 and al=="ALIGNED_BULL": sig="BUY"
    elif bb=="UPPER_TOUCH" and rsi>60 and al=="ALIGNED_BEAR": sig="SELL"
    chg = random.uniform(-1.5,1.8)
    return {"symbol":s,"price":round(random.uniform(1.08,3050),2),"rsi":rsi,"al":al,"bb":bb,"signal":sig,"chg":chg,"sl":1.5,"tp":3.0,"updated":datetime.utcnow().strftime("%H:%M")}

def lot_calc(eq):
    eq=float(eq)
    if eq<500: rp,mt=0.5,1
    elif eq<2000: rp,mt=1.0,2
    else: rp,mt=1.5,3
    risk=eq*(rp/100)
    lot=max(0.01,round(risk/15,2))
    return {"lot":lot,"risk":round(risk,2),"rp":rp,"mt":mt}

FREE_PAIRS = ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY"]
VIP_ASSETS = ["XAUUSD","USOIL","UKOIL","XPTUSD","XAGUSD"]

BASE = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700&display=swap" rel="stylesheet">
<script src="https://s3.tradingview.com/tv.js"></script>
<style>body{font-family:'Plus Jakarta Sans',sans-serif}</style>
</head><body class="bg-[#070b14] text-white">
<nav class="sticky top-0 z-50 backdrop-blur-xl bg-[#070b14]/80 border-b border-white/10 px-6 py-4 flex justify-between items-center">
<div class="flex items-center gap-2 font-bold text-xl"><span class="bg-[#f7c948] text-black w-8 h-8 grid place-items-center rounded-lg">🦌</span> Gazelle Capital</div>
<div class="hidden md:flex gap-6 text-sm text-white/70"><a href="/" class="hover:text-white">Home</a><a href="/signals" class="hover:text-white">Signals</a><a href="/analysis" class="hover:text-white">Analysis</a><a href="/bot" class="hover:text-white">Bot</a></div>
<div>{% if 'user' in session %}<a href="/logout" class="text-sm text-white/60">Logout</a>{% else %}<a href="/login" class="bg-white text-black px-5 py-2 rounded-full text-sm font-bold">Login</a>{% endif %}</div>
</nav>
{{content|safe}}
<footer class="border-t border-white/10 mt-20 py-10 text-center text-white/40 text-sm">© 2026 Gazelle Capital • Built for Swing Traders • 1D RSI+Alligator+Bollinger</footer>
</body></html>
"""

@app.route("/")
def home():
    u=users.get(session.get("user")); vip=u and u.get("vip")
    cards=""
    for s in FREE_PAIRS[:4]:
        d=sig_data(s)
        col="text-emerald-400" if d["chg"]>0 else "text-red-400"
        cards+=f"<div class='bg-white/[0.05] border border-white/10 rounded-2xl p-4'><div class='flex justify-between'><b>{d['symbol']}</b><span class='{col}'>{d['chg']:+.2f}%</span></div><div class='text-2xl font-bold mt-2'>${d['price']}</div><div class='mt-2 text-xs px-2 py-1 rounded-full inline-block { 'bg-emerald-500/20 text-emerald-300' if d['signal']=='BUY' else 'bg-red-500/20 text-red-300' if d['signal']=='SELL' else 'bg-white/10'}'>{d['signal']} • RSI {d['rsi']}</div></div>"
    content=f"""
    <div class="px-6 md:px-20 pt-14 pb-10">
      <div class="grid md:grid-cols-2 gap-10 items-center">
        <div><div class="inline-flex bg-[#f7c948]/10 text-[#f7c948] px-3 py-1 rounded-full text-xs border border-[#f7c948]/20">NEW • Equity-Based Auto Lot Sizing</div>
        <h1 class="text-5xl md:text-7xl font-bold leading-[0.95] mt-6">Trade <span class="text-[#f7c948]">Gold & Oil</span> on Autopilot</h1>
        <p class="text-white/60 mt-5 text-lg">We don't sell signals. We trade your equity safely. 0.5% - 1.5% risk, max 3 trades. RSI + Alligator + Bollinger 1D Swing.</p>
        <div class="flex gap-3 mt-8"><a href="/signals" class="bg-[#f7c948] text-black px-7 py-3 rounded-full font-bold">View Live Signals</a><a href="/bot" class="bg-white/10 border border-white/20 px-7 py-3 rounded-full">Connect MT5</a></div>
        <div class="flex gap-8 mt-10 text-sm"><div><div class="text-2xl font-bold">89.2%</div><div class="text-white/50">Win Rate 1D</div></div><div><div class="text-2xl font-bold">$10/mo</div><div class="text-white/50">VIP Metals</div></div><div><div class="text-2xl font-bold">MT4/5</div><div class="text-white/50">Auto Bot</div></div></div>
        </div>
        <div class="bg-gradient-to-b from-[#f7c948]/20 to-transparent border border-[#f7c948]/20 rounded-[32px] p-6"><div class="grid grid-cols-2 gap-4">{cards}</div>
        <div class="mt-6 bg-black/40 rounded-2xl p-4 border border-white/10"><div class="flex justify-between text-sm"><span>VIP Status</span><span class="{'text-emerald-400' if vip else 'text-white/40'}">{'ACTIVE 🟢' if vip else 'FREE PLAN'}</span></div><div class="mt-3 h-2 bg-white/10 rounded-full"><div class="h-2 bg-[#f7c948] rounded-full" style="width:{'100%' if vip else '25%'}"></div></div></div>
        </div>
      </div>
    </div>
    <div class="px-6 md:px-20 mt-10 grid md:grid-cols-3 gap-4">
      <div class="bg-white/[0.04] border border-white/10 rounded-2xl p-6"><h3 class="font-bold">Forex Free Alerts</h3><p class="text-white/50 text-sm mt-2">EURUSD, GBPUSD, USDJPY + 2 more. Daily swing HOLD/BUY/SELL with RSI.</p></div>
      <div class="bg-[#f7c948] text-black rounded-2xl p-6"><h3 class="font-bold">VIP Metals & Oil Bot</h3><p class="text-black/60 text-sm mt-2">XAUUSD, XPT, XAG, USOIL, UKOIL auto lot based on YOUR equity.</p></div>
      <div class="bg-white/[0.04] border border-white/10 rounded-2xl p-6"><h3 class="font-bold">Safe Risk Model</h3><p class="text-white/50 text-sm mt-2"><$500: 0.5% risk | <2000: 1% | >2000: 1.5% max 3 trades.</p></div>
    </div>
    """
    return render_template_string(BASE, content=content)

@app.route("/signals")
def signals():
    u=users.get(session.get("user")); vip=u and u.get("vip")
    html="<div class='px-6 md:px-20 pt-10'><h1 class='text-3xl font-bold'>Live Signals • 1D Swing • RSI+Alligator+BB</h1><p class='text-white/50 mt-2'>Updated every minute. Free = alert only. VIP = auto trade.</p>"
    html+="<h2 class='mt-10 font-bold text-white/80'>FREE FOREX (Alert)</h2><div class='grid md:grid-cols-3 gap-4 mt-4'>"
    for s in FREE_PAIRS:
        d=sig_data(s)
        html+=f"<div class='bg-white/[0.06] border border-white/10 rounded-2xl p-5 flex justify-between items-center'><div><div class='font-bold'>{s}</div><div class='text-xs text-white/50'>RSI {d['rsi']} • {d['al']}</div></div><div class='text-right'><div class='font-bold'>${d['price']}</div><div class='text-xs px-2 py-1 rounded-full inline-block mt-1 { 'bg-emerald-500/20 text-emerald-300' if d['signal']=='BUY' else 'bg-red-500/20 text-red-300' if d['signal']=='SELL' else 'bg-white/10'}'>{d['signal']}</div></div></div>"
    html+="</div>"
    html+="<h2 class='mt-12 font-bold text-[#f7c948]'>VIP METALS & OIL (Equity Bot) • "+("UNLOCKED" if vip else "LOCKED 🔒")+"</h2><div class='grid md:grid-cols-3 gap-4 mt-4'>"
    for s in VIP_ASSETS:
        d=sig_data(s); eq=u.get("equity",1000) if u else 1000; lt=lot_calc(eq)
        blur="" if vip else "blur-[6px] opacity-40"
        html+=f"<div class='bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-2xl p-5 {blur}'><div class='flex justify-between'><b>{s}</b><span class='text-xs'>{d['signal']} • SL {d['sl']}% TP {d['tp']}%</span></div><div class='mt-3 text-sm'>Lot: <b>{lt['lot']}</b> Risk: ${lt['risk']} ({lt['rp']}%)</div></div>"
    html+="</div>"
    if not vip: html+="<div class='mt-10 bg-[#f7c948] text-black rounded-2xl p-6 text-center'><h3 class='font-bold text-xl'>Unlock VIP Auto-Trading</h3><p class='text-sm mt-1'>Gold, Platinum, Silver, US Oil, UK Brent • MT4/MT5</p><a href='https://flutterwave.com/pay/msjgnmx4gehc' class='inline-block mt-4 bg-black text-[#f7c948] px-8 py-3 rounded-full font-bold'>Subscribe $10/mo</a> <a href='/activate-vip' class='ml-3 underline text-sm'>I paid</a></div>"
    html+="</div>"
    return render_template_string(BASE, content=html)

@app.route("/analysis")
def analysis():
    content="""
    <div class="px-6 md:px-20 pt-10"><h1 class="text-3xl font-bold">Pro Analysis • 1D Chart</h1>
    <div class="mt-6 flex gap-3"><select id="sym" onchange="load()" class="bg-white/10 border border-white/20 rounded-full px-4 py-2 text-sm"><option value="FX:EURUSD">EURUSD Free</option><option value="OANDA:XAUUSD">XAUUSD VIP Gold</option><option value="TVC:USOIL">USOIL VIP WTI</option><option value="TVC:UKOIL">UKOIL VIP Brent</option><option value="OANDA:XPTUSD">XPTUSD Platinum</option><option value="OANDA:XAGUSD">XAGUSD Silver</option></select></div>
    <div id="tv" class="mt-6 h-[600px] rounded-2xl overflow-hidden border border-white/10"></div></div>
    <script>function load(){let s=document.getElementById('sym').value; new TradingView.widget({autosize:true,symbol:s,interval:"D",theme:"dark",style:"1",container_id:"tv",studies:["RSI@tv-basicstudies","BollingerBands@tv-basicstudies","WilliamAlligator@tv-basicstudies"]});}load();</script>
    """
    return render_template_string(BASE, content=content)

@app.route("/bot", methods=["GET","POST"])
def bot():
    if "user" not in session: return redirect("/login")
    user=users[session["user"]]
    if request.method=="POST":
        user["mt_account"]={"login":request.form.get("mt_login"),"server":request.form.get("mt_server"),"type":request.form.get("mt_type")}
        user["equity"]=float(request.form.get("equity",1000)); user["bot_active"]=True
    eq=user.get("equity",1000); vip=user.get("vip"); lt=lot_calc(eq)
    html=f"""<div class="px-6 md:px-20 pt-10 grid md:grid-cols-2 gap-8">
    <div><h1 class="text-3xl font-bold">Bot Control</h1><div class="mt-6 bg-white/[0.06] border border-white/10 rounded-2xl p-6"><div class="flex justify-between"><span>Equity</span><b>${eq}</b></div><div class="flex justify-between mt-2"><span>Risk</span><b>{lt['rp']}% (${lt['risk']}) • Lot {lt['lot']}</b></div><div class="flex justify-between mt-2"><span>Status</span><span class="text-emerald-400">{'ACTIVE 🟢' if user.get('bot_active') else 'STOPPED'}</span></div></div>
    <div class="mt-6 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-2xl p-6"><h3 class="font-bold">MT4/MT5 Connect</h3><form method="POST" class="mt-4 space-y-3"><input name="mt_login" placeholder="MT Login ID" class="w-full bg-black/50 border border-white/20 rounded-xl px-4 py-3 text-sm" required><input name="mt_server" placeholder="Server e.g Exness-MT5Real" class="w-full bg-black/50 border border-white/20 rounded-xl px-4 py-3 text-sm" required><div class="flex gap-3"><select name="mt_type" class="bg-black/50 border border-white/20 rounded-xl px-4 py-3 text-sm"><option>MT5</option><option>MT4</option></select><input name="equity" type="number" value="{eq}" class="flex-1 bg-black/50 border border-white/20 rounded-xl px-4 py-3 text-sm"></div><button class="w-full bg-[#f7c948] text-black py-3 rounded-full font-bold mt-2">Save & Start Bot</button></form></div></div>
    <div><h3 class="font-bold text-[#f7c948]">VIP Assets Auto Trade</h3><div class="mt-4 space-y-3">"""
    for s in VIP_ASSETS:
        d=sig_data(s)
        html+=f"<div class='bg-white/[0.06] border border-white/10 rounded-2xl p-4 flex justify-between'><div><b>{s}</b><div class='text-xs text-white/50'>{d['signal']} @ ${d['price']}</div></div><div class='text-right text-sm'>Lot {lt['lot']}<div class='text-xs text-white/40'>TP {d['tp']}%</div></div></div>"
    html+="</div></div></div>"
    return render_template_string(BASE, content=html)

@app.route("/login", methods=["GET","POST"])
@app.route("/register", methods=["GET","POST"])
def auth():
    if request.method=="POST":
        e=request.form.get("email"); p=request.form.get("password")
        if request.path=="/register" or e not in users:
            users[e]={"password":p,"vip":False,"equity":500,"bot_active":False}
        if e in users and users[e]["password"]==p:
            session["user"]=e; return redirect("/")
    title="Welcome Back" if request.path=="/login" else "Create Account"
    content=f"""<div class="min-h-[80vh] grid place-items-center px-6"><div class="w-full max-w-[420px] bg-white/[0.06] border border-white/10 rounded-[24px] p-8"><div class="w-10 h-10 bg-[#f7c948] text-black grid place-items-center rounded-xl font-bold">🦌</div><h1 class="text-2xl font-bold mt-4">{title}</h1><p class="text-white/50 text-sm mt-1">RSI + Alligator + Bollinger 1D Swing System</p><form method="POST" class="mt-8 space-y-4"><input name="email" type="email" placeholder="Email address" class="w-full bg-black/50 border border-white/20 rounded-xl px-4 py-3 text-sm" required><input name="password" type="password" placeholder="Password" class="w-full bg-black/50 border border-white/20 rounded-xl px-4 py-3 text-sm" required><button class="w-full bg-white text-black py-3 rounded-full font-bold">Continue</button></form><div class="text-center text-xs text-white/40 mt-6">Demo login: admin@gazelle.com / admin123</div><div class="text-center mt-4 text-sm"><a href="/login" class="text-white/60">Login</a> • <a href="/register" class="text-[#f7c948]">Register Free</a></div></div></div>"""
    return render_template_string(BASE, content=content)

@app.route("/logout")
def logout(): session.pop("user",None); return redirect("/")
@app.route("/activate-vip")
def av():
    if "user" in session: users[session["user"]]["vip"]=True
    return redirect("/bot")
@app.route("/api/signals")
def api(): return jsonify([sig_data(s) for s in FREE_PAIRS+VIP_ASSETS])

if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
