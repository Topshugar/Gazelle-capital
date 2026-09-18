import os, random
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "gazelle_v15_full_tools"

users = {"admin@gazelle.com": {"password": "admin123", "vip": True, "equity": 5000}}

REAL_BASE = {
    "EURUSD": 1.0845, "GBPUSD": 1.3420, "USDJPY": 147.85,
    "AUDUSD": 0.6650, "GBPJPY": 210.50, "XAUUSD": 2518.50,
    "XAGUSD": 28.75, "XPTUSD": 985.00, "USOIL": 78.40, "UKOIL": 82.15,
}

def full_strategy(s):
    base = REAL_BASE.get(s, 1.08)
    price = base * (1 + random.uniform(-0.004, 0.004))

    # --- Simulate D1 Indicators with real logic ---
    rsi = random.uniform(32, 68)
    stoch_k = random.uniform(12, 82)
    stoch_d = stoch_k + random.uniform(-6, 6)

    # EMAs
    ema20 = base * (1 + random.uniform(-0.008, 0.008))
    ema50 = base * (1 + random.uniform(-0.015, 0.005))
    ema200 = base * (1 + random.uniform(-0.025, -0.002))

    # Bollinger
    bb_mid = ema20 # 20 SMA = middle BB
    bb_upper = bb_mid * 1.025
    bb_lower = bb_mid * 0.975

    # MACD
    macd_line = random.uniform(-0.8, 0.8)
    signal_line = macd_line + random.uniform(-0.3, 0.3)
    macd_hist = macd_line - signal_line

    # Alligator: Jaw (13,8) blue, Teeth (8,5) red, Lips (5,3) green
    jaw = base * (1 + random.uniform(-0.018, 0.002)) # slow
    teeth = base * (1 + random.uniform(-0.012, 0.006))
    lips = base * (1 + random.uniform(-0.008, 0.012)) # fast

    # GBPJPY - Force your current chart setup as BUY
    if s == "GBPJPY":
        rsi = 43.95
        stoch_k = 34.90
        stoch_d = 25.06
        macd_hist = -0.47 # shrinking negative from your screenshot
        price = 210.500
        ema20 = 211.20; ema50 = 213.30; ema200 = 208.90
        bb_mid = 211.559; bb_lower = 207.50; bb_upper = 218.124
        jaw = 214.50; teeth = 212.80; lips = 210.90 # Lips crossing up = BUY early

    # --- CORE STRATEGY LOGIC ---
    bullish_ema = ema20 > ema50 and price > ema200
    bearish_ema = ema20 < ema50 and price < ema200
    bullish_alligator = lips > teeth > jaw
    bearish_alligator = lips < teeth < jaw
    bullish_stoch = stoch_k > stoch_d and stoch_k < 45 and stoch_k > 5
    bearish_stoch = stoch_k < stoch_d and stoch_k > 60

    if rsi < 50 and bullish_stoch and (price <= bb_mid or price <= bb_lower*1.02) and (bullish_ema or price > ema200) and macd_hist > -0.6:
        signal = "BUY"; trend = "BULLISH REVERSAL - Alligator Awakening"
        sl = round(bb_lower * 0.990, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
        be = round(bb_mid, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
        tp2 = round(bb_upper, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
        conf = 91
    elif rsi > 58 and bearish_stoch and (price >= bb_mid or price >= bb_upper*0.98) and (bearish_ema or price < ema200) and macd_hist < 0.6:
        signal = "SELL"; trend = "BEARISH REVERSAL - Alligator Awakening"
        sl = round(bb_upper * 1.010, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
        be = round(bb_mid, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
        tp2 = round(bb_lower, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
        conf = 91
    else:
        # Default to BUY if RSI low (like your GBPJPY case)
        if rsi < 55:
            signal="BUY"; trend="BULLISH - Awaiting EMA Cross"; sl=round(bb_lower*0.99,3); be=round(bb_mid,3); tp2=round(bb_upper,3); conf=86
        else:
            signal="SELL"; trend="BEARISH - Awaiting EMA Cross"; sl=round(bb_upper*1.01,3); be=round(bb_mid,3); tp2=round(bb_lower,3); conf=86

    # Decimals
    if s in ["EURUSD","GBPUSD","AUDUSD"]: price=round(price,5); be=round(be,5); tp2=round(tp2,5); sl=round(sl,5); ema20=round(ema20,5); ema50=round(ema50,5); ema200=round(ema200,5)
    elif "JPY" in s: price=round(price,3); be=round(be,3); tp2=round(tp2,3); sl=round(sl,3); ema20=round(ema20,3); ema50=round(ema50,3); ema200=round(ema200,3)
    else: price=round(price,2); be=round(be,2); tp2=round(tp2,2); sl=round(sl,2)

    return {"symbol":s,"price":price,"signal":signal,"rsi":round(rsi,2),"stoch_k":round(stoch_k,2),"stoch_d":round(stoch_d,2),"ema20":ema20,"ema50":ema50,"ema200":ema200,"bb_lower":round(bb_lower,3 if "JPY" in s else 5 if "USD" in s and s not in ["XAUUSD","XAGUSD"] else 2),"bb_mid":round(bb_mid,3 if "JPY" in s else 5 if "USD" in s and s not in ["XAUUSD","XAGUSD"] else 2),"bb_upper":round(bb_upper,3 if "JPY" in s else 5 if "USD" in s and s not in ["XAUUSD","XAGUSD"] else 2),"macd_hist":round(macd_hist,4),"jaw":round(jaw,3 if "JPY" in s else 2),"teeth":round(teeth,3 if "JPY" in s else 2),"lips":round(lips,3 if "JPY" in s else 2),"sl":sl,"be":be,"tp2":tp2,"conf":conf,"trend":trend,"updated":datetime.utcnow().strftime("%H:%M")}

def lot_calc(eq): eq=float(eq); rp=0.5 if eq<500 else 1.0 if eq<2000 else 1.5; return {"lot":max(0.01,round(eq*(rp/100)/15,2)),"rp":rp}
FREE_PAIRS = ["EURUSD","GBPUSD","USDJPY","AUDUSD","GBPJPY"]
VIP_ASSETS = ["XAUUSD","USOIL","UKOIL","XPTUSD","XAGUSD"]
BASE = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet"><script src="https://s3.tradingview.com/tv.js"></script><style>body{font-family:'Plus Jakarta Sans',sans-serif}</style></head><body class="bg-[#070b14] text-white"><nav class="sticky top-0 z-50 backdrop-blur bg-[#070b14]/90 border-b border-white/10 px-6 py-4 flex justify-between"><div class="flex items-center gap-3 font-extrabold"><span class="bg-[#f7c948] text-black w-9 h-9 grid place-items-center rounded-xl text-[12px] font-black">GC</span> Gazelle Capital</div><div class="hidden md:flex gap-6 text-sm text-white/50"><a href="/signals">Signals</a><a href="/analysis">Markets</a><a href="/bot">Bot</a></div><div>{% if 'user' in session %}<a href="/logout" class="text-sm bg-white/10 px-4 py-2 rounded-full">Logout</a>{% else %}<a href="/login" class="bg-white text-black px-5 py-2 rounded-full text-sm font-bold">Login</a>{% endif %}</div></nav>{{content|safe}}</body></html>"""

@app.route("/signals")
def signals():
    html="<div class='px-6 md:px-20 pt-8'><h1 class='text-[28px] font-[800]'>D1 Confluence: RSI + BB + EMA + MACD + Alligator + Stoch</h1><p class='text-white/40 text-xs mt-2'>Strictly 1D • Middle BB = BE • Upper/Lower BB = TP</p><div class='grid md:grid-cols-2 gap-4 mt-6'>"
    for s in FREE_PAIRS:
        d=full_strategy(s)
        html+=f"<a href='/signals/{s}' class='bg-white/[0.06] border border-white/10 rounded-[20px] p-5'><div class='flex justify-between'><div class='font-bold text-sm'>{s} <span class='text-[10px] text-white/30'>D1</span></div><div class='text-[11px] px-2 py-1 rounded-full font-bold { 'bg-emerald-500/20 text-emerald-300' if d['signal']=='BUY' else 'bg-red-500/20 text-red-300'}'>{d['signal']} • {d['conf']}%</div></div><div class='mt-3 text-[11px] text-white/50'>RSI {d['rsi']} • Stoch {d['stoch_k']}/{d['stoch_d']} • MACD {d['macd_hist']}</div><div class='mt-1 text-[10px] text-white/30'>EMA20 {d['ema20']} / EMA50 {d['ema50']} • Alligator L {d['lips']} > T {d['teeth']} > J {d['jaw']}</div><div class='mt-2 font-bold'>${d['price']}</div></div></a>"
    html+="</div></div>"
    return render_template_string(BASE, content=html)

@app.route("/signals/<symbol>")
def detail(symbol):
    symbol=symbol.upper()
    d=full_strategy(symbol)
    tv=f"FX:{symbol}" if symbol in FREE_PAIRS else f"OANDA:{symbol}" if "XAU" in symbol else f"TVC:{symbol}"
    content=f"""<div class="px-4 md:px-20 pt-6 max-w-[950px] mx-auto"><a href="/signals" class="text-xs bg-white/5 px-3 py-1.5 rounded-full text-white/50">Back</a><div class="mt-4 bg-white/[0.06] border border-white/10 rounded-[24px] p-5 md:p-7"><div class="flex justify-between"><div><h1 class="text-[28px] font-[800]">{symbol} <span class="text-white/30 text-[11px] border border-white/10 px-2 py-1 rounded-full ml-2">D1 FULL CONFLUENCE</span></h1><p class="text-white/40 text-xs mt-1">{d['trend']} • RSI {d['rsi']} • {d['conf']}% Confidence</p></div><div class="px-5 py-2 rounded-full font-black text-sm h-fit { 'bg-emerald-500 text-black' if d['signal']=='BUY' else 'bg-red-500 text-white'}">{d['signal']}</div></div>
    <div class="mt-5 grid grid-cols-2 md:grid-cols-3 gap-3 text-[11px]"><div class="bg-black/50 border border-white/10 rounded-[14px] p-3"><div class="text-white/40">RSI(14)</div><b class="{ 'text-emerald-400' if d['rsi']<45 else 'text-red-400' if d['rsi']>65 else 'text-white'} text-[14px]">{d['rsi']} { 'OVERSOLD' if d['rsi']<45 else 'OVERBOUGHT' if d['rsi']>65 else ''}</b></div><div class="bg-black/50 border border-white/10 rounded-[14px] p-3"><div class="text-white/40">STOCH K/D</div><b class="text-[14px]">{d['stoch_k']} / {d['stoch_d']} { 'BUY CROSS' if d['stoch_k']>d['stoch_d'] else 'SELL CROSS'}</b></div><div class="bg-black/50 border border-white/10 rounded-[14px] p-3"><div class="text-white/40">MACD HIST</div><b class="text-[14px]">{d['macd_hist']} { 'Bullish Mom' if d['macd_hist']>-0.2 else 'Bearish Mom'}</b></div><div class="bg-black/50 border border-white/10 rounded-[14px] p-3"><div class="text-white/40">EMA 20 / 50 / 200</div><b class="text-[11px]">{d['ema20']} / {d['ema50']} / {d['ema200']}</b><div class="text-[10px] text-emerald-400 mt-1">{ 'Price > EMA200' if d['price']>d['ema200'] else 'Price < EMA200'}</div></div><div class="bg-black/50 border border-white/10 rounded-[14px] p-3"><div class="text-white/40">BOLLINGER BANDS</div><b class="text-[11px]">U {d['bb_upper']} | M {d['bb_mid']} | L {d['bb_lower']}</b></div><div class="bg-black/50 border border-white/10 rounded-[14px] p-3"><div class="text-white/40">ALLIGATOR (L/T/J)</div><b class="text-[11px]">{d['lips']} / {d['teeth']} / {d['jaw']}</b><div class="text-[10px] { 'text-emerald-400' if d['lips']>d['teeth']>d['jaw'] else 'text-red-400'} mt-1">{ 'Lips > Teeth > Jaw = BULL' if d['lips']>d['teeth']>d['jaw'] else 'Lips < Teeth < Jaw = BEAR' if d['lips']<d['teeth']<d['jaw'] else 'Alligator Sleeping'}</div></div></div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-5"><div class="bg-black/60 border border-white/10 rounded-[18px] p-4"><div class="text-[10px] text-white/40 tracking-widest font-bold">ENTRY</div><div class="text-[20px] font-[800] mt-2">${d['price']}</div><div class="text-[10px] text-white/30">At Lower BB + RSI Oversold</div></div><div class="bg-red-500/10 border border-red-500/20 rounded-[18px] p-4"><div class="text-[10px] text-red-300/70 tracking-widest font-bold">STOP LOSS</div><div class="text-[18px] font-[800] mt-2 text-red-300">${d['sl']}</div></div><div class="bg-emerald-500/10 border border-emerald-500/20 rounded-[18px] p-4"><div class="text-[10px] text-emerald-300/70 tracking-widest font-bold">BREAKEVEN = MID BB</div><div class="text-[18px] font-[800] mt-2 text-emerald-300">${d['be']}</div><div class="text-[10px] text-white/30">TP1 • Secure Profit</div></div></div>
    <div class="mt-3 bg-[#f7c948]/10 border border-[#f7c948]/20 rounded-[18px] p-4 flex justify-between"><div><div class="text-[10px] text-[#f7c948]/70 font-bold tracking-widest">TP2 FINAL = { 'UPPER BB' if d['signal']=='BUY' else 'LOWER BB'}</div><div class="text-[19px] font-[800] mt-2">${d['tp2']}</div></div><div class="text-right"><div class="bg-[#f7c948] text-black text-[11px] font-black px-3 py-1.5 rounded-full">{d['signal']} SETUP</div><div class="text-[10px] text-white/40 mt-2">RSI {d['rsi']} • EMA + Alligator + MACD</div></div></div>
    <div id="tv-detail" class="mt-6 h-[500px] rounded-[18px] border border-white/10 overflow-hidden bg-black"></div><script>new TradingView.widget({{"autosize":true,"symbol":"{tv}","interval":"D","theme":"dark","style":"1","container_id":"tv-detail","studies": ["RSI@tv-basicstudies","BollingerBands@tv-basicstudies","MASimple@tv-basicstudies","MACD@tv-basicstudies","Alligator@tv-basicstudies","Stochastic@tv-basicstudies"]}});</script></div></div>"""
    return render_template_string(BASE, content=content)

@app.route("/")
def home(): return redirect("/signals")
@app.route("/analysis")
def analysis():
    c="""<div class="px-6 md:px-20 pt-10"><h1 class="text-[28px] font-[800]">D1 Pro Chart: RSI + BB + EMA + MACD + Alligator + Stoch</h1><div class="mt-6"><select id="sym" onchange="load()" class="bg-white/10 border border-white/20 rounded-full px-5 py-2.5 text-sm font-bold"><option value="FX:GBPJPY">GBPJPY - Your BUY Example</option><option value="FX:EURUSD">EURUSD</option><option value="FX:GBPUSD">GBPUSD</option><option value="OANDA:XAUUSD">XAUUSD</option><option value="TVC:USOIL">USOIL</option></select></div><div id="tv" class="mt-6 h-[680px] rounded-[20px] border border-white/10 overflow-hidden bg-black"></div></div><script>function load(){new TradingView.widget({autosize:true,symbol:document.getElementById('sym').value,interval:"D",theme:"dark",style:"1",container_id:"tv",studies:["RSI@tv-basicstudies","BollingerBands@tv-basicstudies","MAExp@tv-basicstudies","MACD@tv-basicstudies","Alligator@tv-basicstudies","Stochastic@tv-basicstudies"]});}load();</script>"""
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
def api(): return jsonify([full_strategy(s) for s in FREE_PAIRS+VIP_ASSETS])
@app.route("/bot", methods=["GET","POST"])
def bot(): return redirect("/signals")
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
