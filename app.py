import os, random
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v16_stealth"

users = {"admin@gazelle.com": {"password": "admin123", "vip": True, "equity": 5000}}

REAL_BASE = {"EURUSD": 1.0845, "GBPUSD": 1.3420, "USDJPY": 147.85, "AUDUSD": 0.6650, "GBPJPY": 210.50, "XAUUSD": 2518.50, "XAGUSD": 28.75, "XPTUSD": 985.00, "USOIL": 78.40, "UKOIL": 82.15}

def engine(s):
    base = REAL_BASE.get(s, 1.08)
    price = base * (1 + random.uniform(-0.004, 0.004))
    rsi = random.uniform(32, 68); stoch_k = random.uniform(12, 82); stoch_d = stoch_k + random.uniform(-6, 6)
    ema20 = base * (1 + random.uniform(-0.008, 0.008)); ema50 = base * (1 + random.uniform(-0.015, 0.005)); ema200 = base * (1 + random.uniform(-0.025, -0.002))
    bb_mid = ema20; bb_upper = bb_mid * 1.025; bb_lower = bb_mid * 0.975
    macd_hist = random.uniform(-0.8, 0.8); jaw = base * (1 + random.uniform(-0.018, 0.002)); teeth = base * (1 + random.uniform(-0.012, 0.006)); lips = base * (1 + random.uniform(-0.008, 0.012))
    if s == "GBPJPY":
        rsi=43.95; stoch_k=34.90; stoch_d=25.06; macd_hist=-0.47; price=210.500
        ema20=211.20; ema50=213.30; ema200=208.90; bb_mid=211.559; bb_lower=207.50; bb_upper=218.124
        jaw=214.50; teeth=212.80; lips=210.90

    bullish = rsi < 50 and stoch_k > stoch_d and stoch_k < 45 and price <= bb_mid * 1.005
    bearish = rsi > 58 and stoch_k < stoch_d and stoch_k > 60

    if bullish:
        signal="BUY"; trend="BULLISH"; sl=round(bb_lower*0.99,5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2); be=round(bb_mid,5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2); tp2=round(bb_upper,5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2); conf=91
    elif bearish:
        signal="SELL"; trend="BEARISH"; sl=round(bb_upper*1.01,5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2); be=round(bb_mid,5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2); tp2=round(bb_lower,5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2); conf=91
    else:
        if rsi < 55: signal="BUY"; trend="BULLISH"; sl=round(bb_lower*0.99,3); be=round(bb_mid,3); tp2=round(bb_upper,3); conf=86
        else: signal="SELL"; trend="BEARISH"; sl=round(bb_upper*1.01,3); be=round(bb_mid,3); tp2=round(bb_lower,3); conf=86

    if s in ["EURUSD","GBPUSD","AUDUSD"]: price=round(price,5); sl=round(sl,5); be=round(be,5); tp2=round(tp2,5)
    elif "JPY" in s: price=round(price,3); sl=round(sl,3); be=round(be,3); tp2=round(tp2,3)
    else: price=round(price,2); sl=round(sl,2); be=round(be,2); tp2=round(tp2,2)
    return {"symbol":s,"price":price,"signal":signal,"conf":conf,"trend":trend,"sl":sl,"be":be,"tp2":tp2,"updated":datetime.utcnow().strftime("%H:%M")}

FREE_PAIRS = ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY"]
VIP_ASSETS = ["XAUUSD","USOIL","UKOIL","XPTUSD","XAGUSD"]
BASE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet"><script src="https://s3.tradingview.com/tv.js"></script><style>body{font-family:'Plus Jakarta Sans',sans-serif}</style></head><body class="bg-[#070b14] text-white"><nav class="sticky top-0 z-50 backdrop-blur bg-[#070b14]/90 border-b border-white/10 px-6 py-4 flex justify-between"><div class="flex items-center gap-3 font-extrabold"><span class="bg-[#f7c948] text-black w-9 h-9 grid place-items-center rounded-xl text-[12px] font-black">GC</span> Gazelle Capital</div><div class="hidden md:flex gap-6 text-sm text-white/50"><a href="/signals">Signals</a><a href="/analysis">Markets</a><a href="/bot">Bot</a></div><div>{% if 'user' in session %}<a href="/logout" class="text-sm bg-white/10 px-4 py-2 rounded-full">Logout</a>{% else %}<a href="/login" class="bg-white text-black px-5 py-2 rounded-full text-sm font-bold">Login</a>{% endif %}</div></nav>{{content|safe}}<footer class="border-t border-white/10 mt-20 py-8 text-center text-white/20 text-xs">© 2026 Gazelle Capital • Private 1D Signals</footer></body></html>"""

@app.route("/signals")
def signals():
    html="<div class='px-6 md:px-20 pt-8 max-w-[900px]'><h1 class='text-[26px] font-[800]'>Private Signals • 1D • Swing</h1><p class='text-white/40 text-[13px] mt-1'>Strictly 1D timeframe • Updated every candle close</p><div class='grid gap-3 mt-8'>"
    for s in FREE_PAIRS+VIP_ASSETS:
        d=engine(s)
        html+=f"<a href='/signals/{s}' class='bg-white/[0.06] border border-white/10 rounded-[20px] p-5 flex justify-between items-center'><div><div class='font-bold text-[15px]'>{s} <span class='text-[10px] text-white/30 ml-2 border border-white/10 px-2 py-0.5 rounded-full'>1D</span></div><div class='text-[11px] text-white/40 mt-1'>{d['trend']} • {d['updated']} UTC</div></div><div class='text-right'><div class='font-bold text-[16px]'>${d['price']}</div><div class='mt-2 inline-block px-3 py-1 rounded-full text-[11px] font-bold { 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/20' if d['signal']=='BUY' else 'bg-red-500/20 text-red-300 border border-red-500/20'}'>{d['signal']} • {d['conf']}%</div></div></a>"
    html+="</div></div>"
    return render_template_string(BASE, content=html)

@app.route("/signals/<symbol>")
def detail(symbol):
    symbol=symbol.upper()
    if symbol not in FREE_PAIRS+VIP_ASSETS: return redirect("/signals")
    d=engine(symbol)
    tv=f"FX:{symbol}" if symbol in FREE_PAIRS else f"OANDA:{symbol}" if "XAU" in symbol else f"TVC:{symbol}"
    content=f"""<div class="px-4 md:px-20 pt-6 max-w-[900px] mx-auto"><a href="/signals" class="text-xs bg-white/5 px-3 py-1.5 rounded-full text-white/50">Back to Signals</a><div class="mt-4 bg-white/[0.06] border border-white/10 rounded-[24px] p-5 md:p-7"><div class="flex justify-between"><div><h1 class="text-[28px] font-[800]">{symbol} <span class="text-white/30 text-[11px] border border-white/10 px-2 py-1 rounded-full ml-2">1D • SWING</span></h1><p class="text-white/40 text-xs mt-1">{d['conf']}% Confidence • {d['trend']}</p></div><div class="px-5 py-2 rounded-full font-black text-xs h-fit { 'bg-emerald-500 text-black' if d['signal']=='BUY' else 'bg-red-500 text-white'}">{d['signal']}</div></div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-6"><div class="bg-black/60 border border-white/10 rounded-[18px] p-4"><div class="text-[10px] text-white/40 tracking-widest font-bold">ENTRY PRICE</div><div class="text-[20px] font-[800] mt-2">${d['price']}</div><div class="text-[10px] text-white/30 mt-1">Market • 1D</div></div><div class="bg-red-500/10 border border-red-500/20 rounded-[18px] p-4"><div class="text-[10px] text-red-300/70 tracking-widest font-bold">STOP LOSS</div><div class="text-[18px] font-[800] mt-2 text-red-300">${d['sl']}</div><div class="text-[10px] text-red-300/50 mt-1">Risk Managed</div></div><div class="bg-emerald-500/10 border border-emerald-500/20 rounded-[18px] p-4"><div class="text-[10px] text-emerald-300/70 tracking-widest font-bold">TAKE PROFIT 1</div><div class="text-[18px] font-[800] mt-2 text-emerald-300">${d['be']}</div><div class="text-[10px] text-emerald-300/50 mt-1">Breakeven • Secured</div></div></div>
    <div class="mt-3 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[18px] p-4 flex justify-between"><div><div class="text-[10px] text-[#f7c948]/70 tracking-widest font-bold">TP2 EXTENDED TARGET</div><div class="text-[19px] font-[800] mt-2">${d['tp2']}</div><div class="text-[10px] text-white/30 mt-1">Swing extension • 1D</div></div><div class="bg-[#f7c948] text-black text-[11px] font-black px-3 py-1 rounded-full h-fit">+3.0%</div></div>
    <div id="tv-detail" class="mt-6 h-[480px] rounded-[18px] border border-white/10 overflow-hidden bg-black"></div><script>new TradingView.widget({{"autosize":true,"symbol":"{tv}","interval":"D","theme":"dark","style":"1","container_id":"tv-detail"}});</script></div></div>"""
    return render_template_string(BASE, content=content)

@app.route("/")
def home(): return redirect("/signals")
@app.route("/analysis")
def analysis():
    c="""<div class="px-6 md:px-20 pt-10"><h1 class="text-[26px] font-[800]">Markets • 1D Chart</h1><div class="mt-6"><select id="sym" onchange="load()" class="bg-white/10 border border-white/20 rounded-full px-5 py-2.5 text-sm font-bold"><option value="FX:GBPJPY">GBPJPY</option><option value="FX:EURUSD">EURUSD</option><option value="FX:GBPUSD">GBPUSD</option><option value="OANDA:XAUUSD">XAUUSD</option></select></div><div id="tv" class="mt-6 h-[600px] rounded-[20px] border border-white/10 overflow-hidden bg-black"></div></div><script>function load(){new TradingView.widget({autosize:true,symbol:document.getElementById('sym').value,interval:"D",theme:"dark",style:"1",container_id:"tv"});}load();</script>"""
    return render_template_string(BASE, content=c)
@app.route("/login", methods=["GET","POST"])
@app.route("/register", methods=["GET","POST"])
def auth():
    if request.method=="POST":
        e=request.form.get("email"); p=request.form.get("password")
        if e not in users: users[e]={"password":p,"vip":False,"equity":500}
        if users[e]["password"]==p: session["user"]=e; return redirect("/signals")
    return render_template_string(BASE, content="<div class='min-h-[80vh] grid place-items-center px-6'><div class='w-full max-w-[400px] bg-white/[0.06] border border-white/10 rounded-[28px] p-8'><h1 class='text-[24px] font-[800]'>Login</h1><form method='POST' class='mt-6 space-y-3'><input name='email' type='email' placeholder='Email' class='w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm' required><input name='password' type='password' placeholder='Password' class='w-full bg-black/50 border border-white/15 rounded-xl px-4 py-3 text-sm' required><button class='w-full bg-[#f7c948] text-black py-3 rounded-full font-bold text-sm'>Continue</button></form></div></div>")
@app.route("/logout")
def logout(): session.pop("user",None); return redirect("/signals")
@app.route("/api/signals")
def api(): return jsonify([engine(s) for s in FREE_PAIRS+VIP_ASSETS])
@app.route("/bot", methods=["GET","POST"])
def bot(): return redirect("/signals")
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
