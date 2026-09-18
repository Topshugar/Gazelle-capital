import os, random
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v13_no_emoji"

users = {"admin@gazelle.com": {"password": "admin123", "vip": True, "equity": 5000, "mt_account": {"login": "123456", "server": "Exness-MT5Real", "type": "MT5"}, "bot_active": True}}

REAL_BASE = {
    "EURUSD": 1.0845, "GBPUSD": 1.3420, "USDJPY": 147.85,
    "AUDUSD": 0.6650, "GBPJPY": 198.45, "XAUUSD": 2518.50,
    "XAGUSD": 28.75, "XPTUSD": 985.00, "USOIL": 78.40, "UKOIL": 82.15,
}

def sig_data(s):
    base = REAL_BASE.get(s, 1.08)
    jitter = random.uniform(-0.004, 0.004)
    price = base * (1 + jitter)
    if s in ["EURUSD","GBPUSD","AUDUSD"]: price = round(price, 5)
    elif s in ["USDJPY","GBPJPY"]: price = round(price, 3)
    else: price = round(price, 2)
    return {"symbol":s,"price":price,"signal":random.choice(["BUY","SELL","HOLD"]),"chg":round(random.uniform(-0.8,1.2),2),"conf":random.randint(86,96),"trend":random.choice(["BULLISH","BEARISH"]),"updated":datetime.utcnow().strftime("%H:%M")}

def lot_calc(eq):
    eq=float(eq); rp=0.5 if eq<500 else 1.0 if eq<2000 else 1.5
    return {"lot":max(0.01,round(eq*(rp/100)/15,2)),"rp":rp}

FREE_PAIRS = ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY"]
VIP_ASSETS = ["XAUUSD","USOIL","UKOIL","XPTUSD","XAGUSD"]

BASE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet"><script src="https://s3.tradingview.com/tv.js"></script><style>body{font-family:'Plus Jakarta Sans',sans-serif}</style></head><body class="bg-[#070b14] text-white"><nav class="sticky top-0 z-50 backdrop-blur-xl bg-[#070b14]/90 border-b border-white/10 px-6 py-4 flex justify-between items-center"><div class="flex items-center gap-3 font-extrabold"><span class="bg-[#f7c948] text-black w-9 h-9 grid place-items-center rounded-xl font-black text-[12px]">GC</span> Gazelle Capital</div><div class="hidden md:flex gap-6 text-sm text-white/60"><a href="/">Home</a><a href="/signals">Signals</a><a href="/analysis">Markets</a><a href="/bot">Bot</a></div><div>{% if 'user' in session %}<a href="/logout" class="text-sm bg-white/10 px-4 py-2 rounded-full">Logout</a>{% else %}<a href="/login" class="bg-white text-black px-5 py-2 rounded-full text-sm font-bold">Login</a>{% endif %}</div></nav>{{content|safe}}</body></html>"""

@app.route("/")
def home():
    cards=""
    for s in FREE_PAIRS[:4]:
        d=sig_data(s); col="text-emerald-400" if d["chg"]>0 else "text-red-400"
        cards+=f"<a href='/signals/{s}' class='bg-white/[0.06] border border-white/10 rounded-[20px] p-5'><div class='flex justify-between text-xs'><span class='font-bold'>{s}</span><span class='{col}'>{d['chg']:+.2f}%</span></div><div class='text-lg font-extrabold mt-2'>${d['price']}</div><div class='mt-2 text-[10px] px-2 py-1 bg-white/10 rounded-full inline-block'>{d['signal']}</div></a>"
    content=f"<div class='px-6 md:px-20 pt-12'><div class='grid lg:grid-cols-2 gap-10'><div><h1 class='text-[42px] md:text-[60px] font-[800] leading-[0.9]'>Trade <span class='text-[#f7c948]'>Gold & Oil</span><br>on Autopilot</h1><p class='text-white/60 mt-4'>Real prices • Click for TP/SL • 1D</p><a href='/signals' class='inline-block mt-6 bg-[#f7c948] text-black px-8 py-3 rounded-full font-bold text-sm'>View Live Signals</a></div><div class='grid grid-cols-2 gap-4'>{cards}</div></div></div>"
    return render_template_string(BASE, content=content)

@app.route("/signals")
def signals():
    u=users.get(session.get("user")); vip=u and u.get("vip")
    html="<div class='px-6 md:px-20 pt-8'><h1 class='text-[28px] font-[800]'>Signals • Real Prices • 1D</h1><div class='grid md:grid-cols-2 gap-4 mt-6'>"
    for s in FREE_PAIRS:
        d=sig_data(s)
        html+=f"<a href='/signals/{s}' class='bg-white/[0.06] border border-white/10 rounded-[20px] p-5 flex justify-between'><div><div class='font-bold text-sm'>{s} <span class='text-[10px] text-white/30'>1D</span></div><div class='text-[11px] text-white/40 mt-1'>{d['trend']} • {d['conf']}%</div></div><div class='text-right'><div class='font-bold text-[16px]'>${d['price']}</div><div class='text-[10px] mt-2 px-3 py-1 rounded-full bg-white/10'>{d['signal']}</div></div></a>"
    html+="</div>"
    html+=f"<h2 class='mt-10 text-xs font-bold tracking-widest text-[#f7c948]'>VIP • {'UNLOCKED' if vip else 'LOCKED'}</h2><div class='grid md:grid-cols-2 gap-4 mt-4'>"
    for s in VIP_ASSETS:
        d=sig_data(s); lt=lot_calc(u.get("equity",1000) if u else 1000); blur="" if vip else "blur-[6px] opacity-40"
        html+=f"<div class='bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[20px] p-5 {blur}'><b class='text-sm'>{s}</b><div class='mt-1 text-sm'>${d['price']} • {d['signal']} • Lot {lt['lot']}</div></div>"
    html+="</div>"
    if not vip: html+="<div class='mt-8 bg-[#f7c948] text-black rounded-[20px] p-5 text-center'><a href='https://flutterwave.com/pay/msjgnmx4gehc' class='bg-black text-[#f7c948] px-6 py-2.5 rounded-full text-sm font-bold'>Subscribe $10</a> <a href='/activate-vip' class='ml-3 underline text-sm'>I paid</a></div></div>"
    return render_template_string(BASE, content=html)

@app.route("/signals/<symbol>")
def signal_detail(symbol):
    symbol=symbol.upper()
    if symbol not in FREE_PAIRS+VIP_ASSETS: return redirect("/signals")
    d=sig_data(symbol); price=d["price"]
    def calc(pct, add=True):
        f=1+pct/100 if add else 1-pct/100
        return round(price*f, 5 if symbol in ["EURUSD","GBPUSD","AUDUSD"] else 3 if symbol in ["USDJPY","GBPJPY"] else 2)
    if d["signal"]=="BUY": sl=calc(1.5,False); tp1=calc(1.5,True); tp2=calc(3.0,True)
    elif d["signal"]=="SELL": sl=calc(1.5,True); tp1=calc(1.5,False); tp2=calc(3.0,False)
    else: sl=calc(1.5,False); tp1=calc(1.5,True); tp2=calc(3.0,True)
    tv=f"FX:{symbol}" if symbol in FREE_PAIRS else f"OANDA:{symbol}" if "XAU" in symbol or "XPT" in symbol or "XAG" in symbol else f"TVC:{symbol}"
    content=f"""<div class="px-4 md:px-20 pt-6 max-w-[900px] mx-auto"><a href="/signals" class="text-xs text-white/50 bg-white/5 px-3 py-1.5 rounded-full">Back</a><div class="mt-4 bg-white/[0.06] border border-white/10 rounded-[24px] p-5 md:p-7"><div class="flex justify-between"><div><h1 class="text-[28px] font-[800]">{symbol} <span class="text-white/30 text-[11px] border border-white/10 px-2 py-1 rounded-full ml-2">1D</span></h1><p class="text-white/40 text-xs mt-1">{d['conf']}% • {d['trend']}</p></div><div class="px-4 py-2 rounded-full font-bold text-xs h-fit { 'bg-emerald-500/20 text-emerald-300' if d['signal']=='BUY' else 'bg-red-500/20 text-red-300' if d['signal']=='SELL' else 'bg-white/10'}">{d['signal']}</div></div><div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-6"><div class="bg-black/60 border border-white/10 rounded-[18px] p-4"><div class="text-[10px] text-white/40 font-bold tracking-widest">ENTRY</div><div class="text-[20px] font-[800] mt-2">${price}</div></div><div class="bg-red-500/10 border border-red-500/20 rounded-[18px] p-4"><div class="text-[10px] text-red-300/70 font-bold tracking-widest">STOP LOSS</div><div class="text-[18px] font-[800] mt-2 text-red-300">${sl}</div></div><div class="bg-emerald-500/10 border border-emerald-500/20 rounded-[18px] p-4"><div class="text-[10px] text-emerald-300/70 font-bold tracking-widest">TP1</div><div class="text-[18px] font-[800] mt-2 text-emerald-300">${tp1}</div></div></div><div class="mt-3 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[18px] p-4 flex justify-between"><div><div class="text-[10px] text-[#f7c948]/70 font-bold tracking-widest">TP2 EXTENDED</div><div class="text-[18px] font-bold mt-2">${tp2}</div></div><div class="bg-[#f7c948] text-black text-[10px] font-bold px-3 py-1 rounded-full h-fit">+3.0%</div></div><div id="tv-detail" class="mt-6 h-[420px] rounded-[18px] border border-white/10 overflow-hidden bg-black"></div><script>new TradingView.widget({{"autosize":true,"symbol":"{tv}","interval":"D","theme":"dark","style":"1","container_id":"tv-detail"}});</script></div></div>"""
    return render_template_string(BASE, content=content)

@app.route("/analysis")
def analysis():
    content="""<div class="px-6 md:px-20 pt-10"><h1 class="text-[28px] font-[800]">Markets • 1D Live Chart</h1><div class="mt-6"><select id="sym" onchange="load()" class="bg-white/10 border border-white/20 rounded-full px-5 py-2.5 text-sm font-bold"><option value="FX:EURUSD">EURUSD</option><option value="FX:GBPUSD">GBPUSD</option><option value="FX:USDJPY">USDJPY</option><option value="OANDA:XAUUSD">XAUUSD Gold</option><option value="TVC:USOIL">USOIL</option></select></div><div id="tv" class="mt-6 h-[600px] rounded-[20px] border border-white/10 overflow-hidden bg-black"></div></div><script>function load(){new TradingView.widget({autosize:true,symbol:document.getElementById('sym').value,interval:"D",theme:"dark",style:"1",container_id:"tv"});}load();</script>"""
    return render_template_string(BASE, content=content)

@app.route("/bot", methods=["GET","POST"])
def bot():
    if "user" not in session: return redirect("/login")
    user=users[session["user"]]
    if request.method=="POST": user["mt_account"]={"login":request.form.get("mt_login"),"server":request.form.get("mt_server")}; user["equity"]=float(request.form.get("equity",1000))
    eq=user.get("equity",1000); lt=lot_calc(eq)
    html=f"<div class='px-6 md:px-20 pt-10'><h1 class='text-[28px] font-[800]'>Bot Control</h1><div class='mt-6 bg-white/[0.06] border border-white/10 rounded-[20px] p-6'><div class='flex justify-between text-sm'><span class='text-white/50'>Equity</span><b>${eq}</b></div><div class='flex justify-between text-sm mt-2'><span class='text-white/50'>Lot</span><b>{lt['lot']}</b></div></div><form method='POST' class='mt-6 space-y-3'><input name='mt_login' placeholder='MT Login' class='w-full bg-black/60 border border-white/15 rounded-xl px-4 py-3 text-sm' required><input name='mt_server' placeholder='Server' class='w-full bg-black/60 border border-white/15 rounded-xl px-4 py-3 text-sm' required><input name='equity' type='number' value='{eq}' class='w-full bg-black/60 border border-white/15 rounded-xl px-4 py-3 text-sm'><button class='w-full bg-[#f7c948] text-black py-3 rounded-full font-bold text-sm'>Save</button></form></div>"
    return render_template_string(BASE, content=html)

@app.route("/login", methods=["GET","POST"])
@app.route("/register", methods=["GET","POST"])
def auth():
    if request.method=="POST":
        e=request.form.get("email"); p=request.form.get("password")
        if e not in users: users[e]={"password":p,"vip":False,"equity":500}
        if users[e]["password"]==p: session["user"]=e; return redirect("/")
    content=f"""<div class="min-h-[80vh] grid place-items-center px-6"><div class="w-full max-w-[400px] bg-white/[0.06] border border-white/10 rounded-[28px] p-8"><div class="w-10 h-10 bg-[#f7c948] text-black grid place-items-center rounded-xl font-black text-[12px]">GC</div><h1 class="text-[24px] font-[800] mt-4">{"Welcome Back" if request.path=="/login" else "Create Account"}</h1><form method="POST" class="mt-6 space-y-3"><input name="email" type="email" placeholder="Email" class="w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm" required><input name="password" type="password" placeholder="Password" class="w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm" required><button class="w-full bg-[#f7c948] text-black py-3 rounded-full font-bold text-sm">Continue</button></form></div></div>"""
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
