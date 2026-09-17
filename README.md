# Gazelle Capital 🦌 — XAUUSD Strategy Lab

> **⚠️ DISCLAIMER: SIMULATED / EDUCATIONAL ONLY**
> All trades shown are simulated Python calculations for forward-testing. No real MT5 orders are executed in the current version. No profit guarantee. Not financial advice. Trading Gold/Forex is high risk. This is an experimental project from Abuja.

## Table of Contents
1. What is this?
2. Strategy (Transparent)
3. Features
4. Tech Stack
5. How It Works
6. Run Locally
7. Environment Variables
8. Security Notes
9. Roadmap
10. Pricing (Future)
11. Admin
12. Limitations
13. License

### 1. What is this?
Gazelle Capital is a Flask web app that shows live XAUUSD price and simulates a bot using EMA + RSI. Users get a free $100 demo account, watch live signals, and can pre-save MT5 broker details for future VPS execution.

We are in **Demo Phase** — test logic first before real money.

### 2. Strategy (Transparent)
Located in `calc_signal_logic()`:

- Price source: live XAUUSD REST API with fallback
- Buffer: last 250 prices
- EMA50 vs EMA200 for trend
- RSI 14 for filter
- BUY if EMA50>EMA200 and RSI 40-68
- SELL if EMA50<EMA200 and RSI 32-60
- Else WAITING

No hidden AI. Fully open logic.

### 3. Features
- Live XAUUSD ticker
- Demo auth (register/login)
- $100 demo balance simulation
- Trade log with timestamps
- Multi-broker MT5 form (XM, HFM, Exness, Deriv, FBS, OctaFX, Other)
- Risk selector (0.01 to 0.20 lot) for future use
- VIP flag system
- Admin dashboard
- Secure private API for VPS bot
- Retention UI (keep tab open to watch sim)
- Ad-ready but compliant (no fake income claims)

### 4. Tech Stack
- Python, Flask, SQLite (dev), Requests
- Inline CSS black/gold theme
- Hosting: Render
- Future: Windows Forex VPS + MetaTrader5 Python + Postgres + Flutterwave

### 5. How It Works
Browser -> Flask -> get_real_gold_price() -> add_price() buffer -> calc_signal_logic() -> simulate balance change -> save to trades table -> if VIP, credentials saved for future VPS execution via private API.

### 6. Run Locally
```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
python App.py
