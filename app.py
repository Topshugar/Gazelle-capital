import os, random
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v10_final_fixed"

users = {
    "admin@gazelle.com": {"password": "admin123", "vip": True, "equity": 5000, "mt_account": {"login": "123456", "server": "Exness-MT5Real", "type": "MT5"}, "bot_active": True}
}

def sig_data(s):
    sig = random.choice(["BUY","SELL","HOLD"])
    chg = random.uniform(-1.5,1.8)
    conf = random.randint(82,96)
    trend = random.choice(["BULLISH","BEARISH"])
    price = round(random.uniform(1.08, 3050), 4 if len(s)==6 and s!="XAUUSD" else 2)
    return {"symbol":s,"price":price,"signal":sig,"chg":chg,"conf":conf,"trend":trend,"updated":datetime.utcnow().strftime("%H:%M")}

def lot_calc(eq):
    eq=float(eq)
    if eq<500: rp=0.5
    elif eq<2000: rp=1.0
    else: rp=1.5
    risk=eq*(rp/100)
    lot=max(0.01,round(risk/15,2))
    return {"lot":lot,"risk":round(risk,2),"rp":rp}

FREE_PAIRS = ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY"]
VIP_ASSETS = ["XAUUSD","USOIL","UKOIL","XPTUSD","XAGUSD"]

BASE = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet">
<script src="https://s3.tradingview.com/tv.js"></script>
<style>body{font-family:'Plus Jakarta Sans',sans-serif}</style>
</head><body class="bg-[#070b14] text-white antialiased">
<nav class="sticky top-0 z-50 backdrop-blur-xl bg-[#070b14]/90 border-b border-white/10 px-6 md:px-10 py-4 flex justify-between items-center">
<div class="flex items-center gap-3 font-extrabold text-[20px]"><span class="bg-[#f7c948] text-black w-9 h-9 grid place-items-center rounded-xl">🦌</span> Gazelle Capital</div>
<div class="hidden md:flex gap-8 text-[14px] text-white/60 font-semibold"><a href="/" class="hover:text-white">Home</a><a href="/signals" class="hover:text-white">Signals</a><a href="/analysis" class="hover:text-white">Markets</a><a href="/bot" class="hover:text-white">Bot</a></div>
<div>{% if 'user' in session %}<a href="/logout" class="text-sm bg-white/10 px-4 py-2 rounded-full">Logout</a>{% else %}<a href="/login" class="bg-white text-black px-6 py-2.5 rounded-full text-sm font-extrabold">Login</a>{% endif %}</div>
</nav>
{{content|safe}}
<footer class="border-t border-white/10 mt-24 py-10 text-center text-white/30 text-[13px]">© 2026 Gazelle Capital • Private Trading Infrastructure</footer>
</body></html>
"""

@app.route("/")
def home():
    u=users.get(session.get("user")); vip=u and u.get("vip")
    cards=""
    for s in FREE_PAIRS[:4]:
        d=sig_data(s)
        col="text-emerald-400" if d["chg"]>0 else "text-red-400"
        cards+=f"<a href='/signals/{s}' class='bg-white/[0.06] border border-white/10 rounded-[20px] p-5 hover:border-white/20 transition'><div class='flex justify-between text-[13px]'><span class='font-bold tracking-widest'>{d['symbol']}</span><span class='{col} font-bold'>{d['chg']:+.2f}%</span></div><div class='text-[22px] font-extrabold mt-3'>${d['price']}</div><div class='mt-3 flex gap-2'><span class='text-[11px] px-2.5 py-1 rounded-full font-bold { 'bg-emerald-500/15 text-emerald-300' if d['signal']=='BUY' else 'bg-red-500/15 text-red-300' if d['signal']=='SELL' else 'bg-white/10'}'>{d['signal']}</span><span class='text-[11px] text-white/40'>{d['conf']}%</span></div></a>"
    content=f"""<div class="px-6 md:px-10 lg:px-20 pt-12"><div class="grid lg:grid-cols-2 gap-12 items-center"><div><div class="inline-flex bg-[#f7c948]/10 text-[#f7c948] px-3.5 py-1.5 rounded-full text-[11px] font-bold tracking-widest border border-[#f7c948]/20">PRIVATE ACCESS • 1D TIMEFRAME</div><h1 class="text-[44px] md:text-[68px] font-[800] leading-[0.9] tracking-[-0.03em] mt-7">Trade <span class="text-[#f7c948]">Gold & Oil</span><br>on Autopilot</h1><p class="text-white/60 mt-6 text-[17px] max-w-[520px]">Click any pair to see BUY/SELL with TP/SL on daily chart. Equity-protected lot sizing.</p><div class="flex gap-3 mt-8"><a href="/signals" class="bg-[#f7c948] text-black px-8 py-3.5 rounded-full font-extrabold text-sm">View Signals (Click for TP/SL)</a></div></div><div class="bg-gradient-to-b from-[#f7c948]/15 to-transparent border border-[#f7c948]/20 rounded-[32px] p-7"><div class="grid grid-cols-2 gap-4">{cards}</div></div></div></div>"""
    return render_template_string(BASE, content=content)

@app.route("/signals")
def signals():
    u=users.get(session.get("user")); vip=u and u.get("vip")
    html="<div class='px-6 md:px-10 lg:px-20 pt-10'><h1 class='text-[30px] font-[800]'>Private Signal Feed • 1D</h1><p class='text-white/50 mt-2 text-sm'>Click any Forex pair to view BUY/SELL with TP & SL • Daily timeframe</p>"
    html+="<h2 class='mt-12 font-extrabold text-[13px] tracking-widest text-white/60'>FREE FOREX • CLICK FOR TP/SL</h2><div class='grid md:grid-cols-3 gap-4 mt-4'>"
    for s in FREE_PAIRS:
        d=sig_data(s)
        html+=f"<a href='/signals/{s}' class='bg-white/[0.06] hover:bg-white/[0.08] border border-white/10 rounded-[20px] p-5 flex justify-between items-center'><div><div class='font-extrabold tracking-widest text-sm'>{s} <span class='text-[10px] text-white/30'>1D →</span></div><div class='text-[11px] text-white/40 mt-1'>{d['trend']} • {d['conf']}%</div></div><div class='text-right'><div class='font-bold'>${d['price']}</div><div class='text-[11px] px-2.5 py-1 rounded-full inline-block mt-2 font-bold { 'bg-emerald-500/15 text-emerald-300' if d['signal']=='BUY' else 'bg-red-500/15 text-red-300' if d['signal']=='SELL' else 'bg-white/10'}'>{d['signal']}</div></div></a>"
    html+="</div>"
    html+="<h2 class='mt-14 font-extrabold text-[13px] tracking-widest text-[#f7c948]'>VIP • "+("UNLOCKED" if vip else "LOCKED 🔒")+"</h2><div class='grid md:grid-cols-3 gap-4 mt-4'>"
    for s in VIP_ASSETS:
        d=sig_data(s); eq=u.get("equity",1000) if u else 1000; lt=lot_calc(eq); blur="" if vip else "blur-[7px] opacity-40"
        html+=f"<div class='bg-[#f7c948]/[0.08] border border-[#f7c948]/20 rounded-[20px] p-5 {blur}'><b class='text-sm tracking-widest'>{s}</b><div class='mt-2 text-[13px]'>Lot {lt['lot']} • {d['signal']}</div></div>"
    html+="</div>"
    if not vip: html+="<div class='mt-12 bg-[#f7c948] text-black rounded-[24px] p-8 text-center'><h3 class='font-extrabold text-[20px]'>Unlock VIP TP/SL</h3><a href='https://flutterwave.com/pay/msjgnmx4gehc' class='inline-block mt-4 bg-black text-[#f7c948] px-10 py-3 rounded-full font-extrabold text-sm'>Subscribe $10</a> <a href='/activate-vip' class='ml-3 underline text-sm font-bold'>I paid</a></div></div>"
    return render_template_string(BASE, content=html)

@app.route("/signals/<symbol>")
def signal_detail(symbol):
    symbol=symbol.upper()
    if symbol not in FREE_PAIRS+VIP_ASSETS: return redirect("/signals")
    d=sig_data(symbol)
    price=d["price"]
    if d["signal"]=="BUY":
        sl=round(price*0.985,4); tp1=round(price*1.015,4); tp2=round(price*1.03,4)
    elif d["signal"]=="SELL":
        sl=round(price*1.015,4); tp1=round(price*0.985,4); tp2=round(price*0.97,4)
    else:
        sl=round(price*0.985,4); tp1=round(price*1.015,4); tp2=round(price*1.03,4)
    tv_sym = f"FX:{symbol}" if len(symbol)==6 else f"OANDA:{symbol}" if "XAU" in symbol or "XPT" in symbol or "XAG" in symbol else f"TVC:{symbol}"
    content=f"""
    <div class="px-6 md:px-20 pt-8 max-w-[900px] mx-auto">
      <a href="/signals" class="text-sm text-white/50 hover:text-white">← Back</a>
      <div class="mt-6 bg-white/[0.06] border border-white/10 rounded-[28px] p-7 md:p-8">
        <div class="flex justify-between"><div><h1 class="text-[34px] font-[800]">{symbol} <span class="text-white/40 text-[14px] font-bold tracking-widest">1D</span></h1><p class="text-white/50 text-sm">Daily Swing • Updated {d['updated']} UTC • {d['conf']}% Confidence</p></div><div class="text-right"><div class="px-4 py-2 rounded-full font-extrabold text-sm { 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' if d['signal']=='BUY' else 'bg-red-500/20 text-red-300 border border-red-500/30' if d['signal']=='SELL' else 'bg-white/10'}">{d['signal']}</div><div class="text-[11px] text-white/40 mt-2">{d['trend']}</div></div></div>
        <div class="grid grid-cols-3 gap-4 mt-8">
          <div class="bg-black/50 border border-white/10 rounded-[16px] p-4"><div class="text-[10px] tracking-widest text-white/40">ENTRY</div><div class="text-[19px] font-extrabold mt-1">${price}</div></div>
          <div class="bg-red-500/10 border border-red-500/20 rounded-[16px] p-4"><div class="text-[10px] tracking-widest text-red-300/60">STOP LOSS</div><div class="text-[18px] font-extrabold text-red-300 mt-1">${sl}</div><div class="text-[10px] text-white/40">-1.5% • 1D</div></div>
          <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-[16px] p-4"><div class="text-[10px] tracking-widest text-emerald-300/60">TAKE PROFIT 1</div><div class="text-[18px] font-extrabold text-emerald-300 mt-1">${tp1}</div><div class="text-[10px] text-white/40">+1.5% • 1D</div></div>
        </div>
        <div class="mt-4 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[16px] p-4 flex justify-between"><div><div class="text-[10px] tracking-widest text-[#f7c948]/60">TP2 EXTENDED TARGET</div><div class="text-[18px] font-bold mt-1">${tp2}</div></div><div class="text-right text-[11px] text-white/50">Swing target<br>+3.0% on 1D</div></div>
        <div id="tv-detail" class="mt-7 h-[460px] rounded-[16px] overflow-hidden border border-white/10"></div>
        <script>new TradingView.widget({{autosize:true,symbol:"{tv_sym}",interval:"D",theme:"dark",style:"1",container_id:"tv-detail"}});</script>
        <div class="mt-6 flex gap-3"><a href="/bot" class="flex-1 bg-[#f7c948] text-black py-3.5 rounded-full font-extrabold text-sm text-center">Auto-Trade on MT5</a><a href="/signals" class="flex-1 bg-white/10 border border-white/15 py-3.5 rounded-full font-bold text-sm text-center">Back to Signals</a></div>
      </div>
    </div>
    """
    return render_template_string(BASE, content=content)

@app.route("/analysis")
def analysis():
    content="""<div class="px-6 md:px-20 pt-10"><h1 class="text-[28px] font-[800]">Markets • 1D</h1><div class="mt-6"><select id="sym" onchange="load()" class="bg-white/10 border border-white/20 rounded-full px-5 py-2.5 text-sm font-bold"><option value="FX:EURUSD">EURUSD</option><option value="OANDA:XAUUSD">XAUUSD Gold</option><option value="TVC:USOIL">USOIL</option><option value="TVC:UKOIL">UKOIL Brent</option><option value="OANDA:XPTUSD">XPTUSD</option><option value="OANDA:XAGUSD">XAGUSD</option></select></div><div id="tv" class="mt-6 h-[620px] rounded-[20px] border border-white/10 overflow-hidden"></div></div><script>function load(){let s=document.getElementById('sym').value; new TradingView.widget({autosize:true,symbol:s,interval:"D",theme:"dark",style:"1",container_id:"tv"});}load();</script>"""
    return render_template_string(BASE, content=content)

@app.route("/bot", methods=["GET","POST"])
def bot():
    if "user" not in session: return redirect("/login")
    user=users[session["user"]]
    if request.method=="POST":
        user["mt_account"]={"login":request.form.get("mt_login"),"server":request.form.get("mt_server"),"type":request.form.get("mt_type")}
        user["equity"]=float(request.form.get("equity",1000)); user["bot_active"]=True
    eq=user.get("equity",1000); lt=lot_calc(eq)
    html=f"""<div class="px-6 md:px-20 pt-10 grid lg:grid-cols-2 gap-10"><div><h1 class="text-[28px] font-[800]">Bot Control • 1D</h1><div class="mt-6 bg-white/[0.06] border border-white/10 rounded-[20px] p-6 text-sm space-y-2"><div class="flex justify-between"><span class="text-white/50">Equity</span><b>${eq}</b></div><div class="flex justify-between"><span class="text-white/50">Risk</span><b>{lt['rp']}% • Lot {lt['lot']}</b></div></div><div class="mt-6 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[20px] p-6"><h3 class="font-extrabold">Connect MT4/MT5</h3><form method="POST" class="mt-4 space-y-3"><input name="mt_login" placeholder="MT Login" class="w-full bg-black/60 border border-white/15 rounded-xl px-4 py-3.5 text-sm" required><input name="mt_server" placeholder="Server" class="w-full bg-black/60 border border-white/15 rounded-xl px-4 py-3.5 text-sm" required><div class="flex gap-3"><select name="mt_type" class="bg-black/60 border border-white/15 rounded-xl px-4 py-3.5 text-sm"><option>MT5</option><option>MT4</option></select><input name="equity" type="number" value="{eq}" class="flex-1 bg-black/60 border border-white/15 rounded-xl px-4 py-3.5 text-sm"></div><button class="w-full bg-[#f7c948] text-black py-3.5 rounded-full font-extrabold text-sm">Save & Start</button></form></div></div><div><h3 class="font-extrabold text-[#f7c948] text-sm tracking-widest">VIP AUTO</h3><div class="mt-4 space-y-3">"""
    for s in VIP_ASSETS:
        d=sig_data(s)
        html+=f"<div class='bg-white/[0.06] border border-white/10 rounded-[20px] p-4 flex justify-between'><div><b class='text-sm'>{s}</b><div class='text-[11px] text-white/40'>{d['signal']} • {d['conf']}%</div></div><div class='text-right text-sm font-bold'>${d['price']}<div class='text-[11px] text-white/40'>Lot {lt['lot']}</div></div></div>"
    html+="</div></div></div>"
    return render_template_string(BASE, content=html)

@app.route("/login", methods=["GET","POST"])
@app.route("/register", methods=["GET","POST"])
def auth():
    if request.method=="POST":
        e=request.form.get("email"); p=request.form.get("password")
        if e not in users: users[e]={"password":p,"vip":False,"equity":500,"bot_active":False}
        if e in users and users[e]["password"]==p:
            session["user"]=e; return redirect("/")
    is_login = request.path=="/login"
    title="Welcome Back" if is_login else "Create Account"
    content=f"""<div class="min-h-[80vh] grid place-items-center px-6"><div class="w-full max-w-[420px] bg-white/[0.06] border border-white/10 rounded-[28px] p-8"><div class="w-11 h-11 bg-[#f7c948] text-black grid place-items-center rounded-xl font-extrabold">🦌</div><h1 class="text-[26px] font-[800] mt-5">{title}</h1><p class="text-white/50 text-[13px] mt-2">Private trading infrastructure • 1D timeframe</p><form method="POST" class="mt-8 space-y-4"><input name="email" type="email" placeholder="Email" class="w-full bg-black/50 border border-white/15 rounded-[14px] px-4 py-3.5 text-[14px]" required><input name="password" type="password" placeholder="Password" class="w-full bg-black/50 border border-white/15 rounded-[14px] px-4 py-3.5 text-[14px]" required><button class="w-full bg-[#f7c948] text-black py-3.5 rounded-full font-extrabold text-sm">Continue</button></form><div class="text-center mt-6 text-[13px]"><a href="/login" class="{'text-white' if is_login else 'text-white/40'}">Login</a> <span class="text-white/20 mx-2">•</span> <a href="/register" class="{'text-[#f7c948]' if not is_login else 'text-white/40'}">Register Free</a></div></div></div>"""
    return render_template_string(BASE, content=content)

@app.route("/logout")
def logout(): session.pop("user",None); return redirect("/")
@app.route("/activate-vip")
def av():
    if "user" in session: users[session["user"]]["vip"]=True
    return redirect("/signals")
@app.route("/api/signals")
def api(): return jsonify([sig_data(s) for s in FREE_PAIRS+VIP_ASSETS])

if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
