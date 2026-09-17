# Gazelle Capital 🦌 - XAUUSD Simulated Bot

Live: `gazelle-capital.onrender.com` (Render)

Flask app for XAUUSD (Gold) live price + EMA 50/200 + RSI 14 simulation. Demo $100 account. Users can store any MT5 broker credentials for future VPS execution.

> ⚠️ **DISCLAIMER: SIMULATED / DEMO ONLY** - Currently all trades are simulated in Python (random outcome for forward testing). No real MT5 orders yet. Not financial advice. Experimental project from Abuja.

### Strategy (Transparent)
- `get_real_gold_price()` = fetches XAU from gold-api.com
- `calc_signal_logic()`:
    - EMA50 vs EMA200
    - RSI 14 filter
    - BUY if EMA50>EMA200 and RSI 40-68
    - SELL if EMA50<EMA200 and RSI 32-60
    - else WAITING

### Stack
- Flask, SQLite (`gazelle.db`), Requests
- Monetag (ID: 727e5ecd172c1a11978ca9da5f525f7e) + `quge5.com` tag
- Render hosting, `sw.js`

### Phases
**Phase 1 NOW - Monetag on Demo (current)**
Free demo keeps users on page longer = more ad revenue to fund domain+VPS.

**Phase 2 - Real Trading**
Buy domain + Contabo VPS ($6/mo) + run `MetaTrader5` Python lib to execute `/api/signal` for VIPs.

**Phase 3 - Pricing with Flutterwave**
- FREE: Demo $100 sim
- VIP ₦5k/month: 1 MT5, 0.05 lot max
- PRO ₦12k/month: Unlimited, alerts

### Run Locally
```bash
pip install flask requests
python App.py
