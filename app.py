import os, hashlib
from datetime import date
from flask import Flask, render_template_string, request, redirect, session, jsonify
app = Flask(__name__)
app.secret_key = "gazelle_v22_fixed"
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
        price=210.50; bb_mid=211.559; bb_lower=207.50; bb_upper=218.124; sig="BUY"; reason="BoJ dovish + UK wage 6.2% supports GBP. Safe-haven flow favors GBP vs JPY."
    elif s == "USDJPY":
        sig="BUY" if r(2)<0.5 else "SELL"; reason="US CPI sticky 3.2%, Fed hawkish pause."
    elif s == "XAUUSD":
        sig="BUY"; reason="Central bank buying + real yield drop. Gold $2518."
    elif s == "EURUSD":
        sig="SELL" if r(2)<0.5 else "BUY"; reason="ECB dovish vs Fed hold. Weak German PMI."
    elif s == "GBPUSD":
        sig="BUY"; reason="UK labor tight, BoE higher for longer."
    else:
        sig="BUY" if r(2)<0.55 else "SELL"; reason="AUD supported by China stimulus."
    fmt = lambda v: round(v, 5 if s in ["EURUSD","GBPUSD","AUDUSD"] else 3 if "JPY" in s else 2)
    return {"symbol":s,"price":fmt(price),"signal":sig,"conf":91,"sl":fmt(bb_lower*0.99 if sig=="BUY" else bb_upper*1.01),"be":fmt(bb_mid),"tp2":fmt(bb_upper if sig=="BUY" else bb_lower),"date":today,"reason":reason}
HEAD = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800&display=swap" rel="stylesheet"><style>body{font-family:Inter,sans-serif}</style></head>
<body class="bg-[#f8fafc] text-[#0f172a]">
<nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200 px-6 py-3.5 flex justify-between items-center">
<div class="flex items-center gap-2.5 font-[800]"><span class="bg-[#2563eb] text-white w-8 h-8 grid place-items-center rounded-lg text-[11px]">GC</span> Gazelle Capital</div>
<div class="flex gap-3"><a href="/login" class="text-[13px] font-[600] px-4 py-2">Log in</a><a href="/register" class="bg-[#0f172a] text-white px-5 py-2.5 rounded-full text-[13px] font-[700]">Get Started</a></div>
</nav><div>
"""
FOOT = """</div><footer class="border-t mt-24 py-10 text-center text-slate-400 text-[12px] bg-white">© 2026 Gazelle Capital</footer></body></html>"""
