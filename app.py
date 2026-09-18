import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import requests as req_lib

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gazelle_secret_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gazelle.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    tier = db.Column(db.String(20), default='FREE')
    vip_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Signal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(20), default='FOREX')
    action = db.Column(db.String(10))
    entry = db.Column(db.Float)
    sl = db.Column(db.Float)
    tp1 = db.Column(db.Float)
    tp2 = db.Column(db.Float)
    tp3 = db.Column(db.Float)
    timeframe = db.Column(db.String(10), default='H1')
    trade_type = db.Column(db.String(20), default='Day')
    status = db.Column(db.String(20), default='Active')
    confidence = db.Column(db.Integer, default=85)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(80), default='Admin')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String(20))
    username = db.Column(db.String(80))
    message = db.Column(db.Text)
    is_vvip_only = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not Signal.query.first():
        demo_signals = [
            Signal(pair='EURUSD', category='FOREX', action='BUY', entry=1.0845, sl=1.0820, tp1=1.0860, tp2=1.0880, tp3=1.0900, timeframe='H1', trade_type='Day', status='Active', confidence=82),
            Signal(pair='GBPUSD', category='FOREX', action='SELL', entry=1.2650, sl=1.2680, tp1=1.2630, tp2=1.2600, tp3=1.2570, timeframe='H4', trade_type='Swing', status='Active', confidence=78),
            Signal(pair='XAUUSD', category='GOLD', action='BUY', entry=2035.50, sl=2028.00, tp1=2045.00, tp2=2055.00, tp3=2070.00, timeframe='H1', trade_type='Scalp', status='Active', confidence=90),
            Signal(pair='BTCUSD', category='CRYPTO', action='BUY', entry=43250.00, sl=42500.00, tp1=44000.00, tp2=45000.00, tp3=46500.00, timeframe='D1', trade_type='Swing', status='TP Hit', confidence=88),
            Signal(pair='US30', category='INDICES', action='SELL', entry=38500.00, sl=38700.00, tp1=38300.00, tp2=38000.00, tp3=37500.00, timeframe='H4', trade_type='Day', status='Active', confidence=84),
        ]
        db.session.bulk_save_objects(demo_signals)
        db.session.commit()

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def is_vip(user):
    if not user: return False
    if user.tier in ['VIP','VVIP']:
        if user.vip_expiry and user.vip_expiry > datetime.utcnow():
            return True
    return False

def is_vvip(user):
    if not user: return False
    if user.tier == 'VVIP' and user.vip_expiry and user.vip_expiry > datetime.utcnow():
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/me')
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({'logged': False})
    return jsonify({
        'logged': True,
        'username': user.username,
        'tier': user.tier,
        'is_vip': is_vip(user),
        'is_vvip': is_vvip(user),
        'vip_expiry': user.vip_expiry.strftime('%Y-%m-%d') if user.vip_expiry else None
    })

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username taken'}), 400
    u = User(username=data['username'], email=data.get('email'), password=data['password'])
    db.session.add(u)
    db.session.commit()
    session['user_id'] = u.id
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    u = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not u:
        return jsonify({'error': 'Invalid'}), 401
    session['user_id'] = u.id
    return jsonify({'success': True})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/signals')
def api_signals():
    user = get_current_user()
    vip = is_vip(user)
    signals = Signal.query.order_by(Signal.created_at.desc()).all()
    result = []
    for s in signals:
        locked = False
        if s.category!= 'FOREX' and not vip:
            locked = True
        result.append({
            'id': s.id, 'pair': s.pair, 'category': s.category,
            'action': s.action, 'entry': s.entry, 'sl': s.sl,
            'tp1': s.tp1, 'tp2': s.tp2, 'tp3': s.tp3,
            'timeframe': s.timeframe, 'trade_type': s.trade_type,
            'status': s.status, 'confidence': s.confidence,
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
            'created_by': s.created_by, 'locked': locked
        })
    total = Signal.query.count()
    tp_hit = Signal.query.filter_by(status='TP Hit').count()
    win_rate = round((tp_hit/total*100) if total>0 else 0, 1)
    return jsonify({'signals': result, 'stats': {'total': total, 'tp_hit': tp_hit, 'win_rate': win_rate}})

@app.route('/api/news')
def api_news():
    news = [
        {'time': '08:30', 'pair': 'USD', 'event': 'CPI Data', 'impact': 'HIGH', 'forecast': '3.2%', 'previous': '3.1%'},
        {'time': '10:00', 'pair': 'EUR', 'event': 'ECB Speech', 'impact': 'MED', 'forecast': '-', 'previous': '-'},
        {'time': '13:30', 'pair': 'GOLD', 'event': 'Fed Interest Rate', 'impact': 'HIGH', 'forecast': '5.5%', 'previous': '5.5%'},
        {'time': '15:00', 'pair': 'GBP', 'event': 'GDP m/m', 'impact': 'MED', 'forecast': '0.2%', 'previous': '0.1%'},
    ]
    return jsonify(news)

@app.route('/api/comments', methods=['GET','POST'])
def api_comments():
    if request.method == 'POST':
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Login required'}), 401
        data = request.json
        msg = data.get('message','').strip()
        if len(msg) < 3:
            return jsonify({'error': 'Too short'}), 400
        banned = ['fuck', 'scam', 'http://', 'https://']
        if any(b in msg.lower() for b in banned):
            return jsonify({'error': 'Comment must be strictly on topic'}), 400
        c = Comment(pair=data.get('pair','GENERAL'), username=user.username, message=msg, is_vvip_only=data.get('is_vvip_only', False) and is_vvip(user))
        db.session.add(c)
        db.session.commit()
        return jsonify({'success': True})
    user = get_current_user()
    vvip = is_vvip(user)
    comments = Comment.query.order_by(Comment.created_at.desc()).limit(100).all()
    result = []
    for c in comments:
        if c.is_vvip_only and not vvip:
            continue
        result.append({'pair': c.pair, 'username': c.username, 'message': c.message, 'time': c.created_at.strftime('%H:%M'), 'vvip': c.is_vvip_only})
    return jsonify(result)

@app.route('/api/calculate-risk', methods=['POST'])
def api_risk():
    data = request.json
    balance = float(data.get('balance', 1000))
    risk_percent = float(data.get('risk_percent', 2))
    sl_pips = float(data.get('sl_pips', 20))
    risk_money = balance * risk_percent / 100
    lot = round(risk_money / (sl_pips * 10), 2) if sl_pips>0 else 0
    return jsonify({'risk_money': risk_money, 'lot_size': lot})

@app.route('/api/leaderboard')
def api_leaderboard():
    leaders = db.session.query(Signal.created_by, db.func.count(Signal.id)).filter(Signal.status=='TP Hit').group_by(Signal.created_by).order_by(db.func.count(Signal.id).desc()).limit(5).all()
    return jsonify([{'username': l[0], 'wins': l[1]} for l in leaders])

@app.route('/api/admin/add-signal', methods=['POST'])
def api_add_signal():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Admin only'}), 403
    data = request.json
    s = Signal(
        pair=data['pair'].upper(), category=data.get('category','FOREX'),
        action=data['action'], entry=float(data['entry']), sl=float(data['sl']),
        tp1=float(data['tp1']), tp2=float(data.get('tp2', data['tp1'])),
        tp3=float(data.get('tp3', data['tp1'])), timeframe=data.get('timeframe','H1'),
        trade_type=data.get('trade_type','Day'), status='Active',
        confidence=int(data.get('confidence', 85)), created_by=user.username
    )
    db.session.add(s)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/vip/verify', methods=['POST'])
def api_vip_verify():
    data = request.json
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Login first'}), 401
    tier = data.get('tier', 'VIP')
    days = 30
    user.tier = tier
    user.vip_expiry = datetime.utcnow() + timedelta(days=days)
    db.session.commit()
    return jsonify({'success': True, 'tier': tier, 'expiry': user.vip_expiry.strftime('%Y-%m-%d')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
