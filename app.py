from flask import Flask, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'gazelle-2026-lagos-final'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gazelle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# YOUR SAVED FLUTTERWAVE KEY
FLW_PUB_KEY = "FLWPUBK-680c2f65a0795c23ac1ad8f6aabe4e4c-X"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    tier = db.Column(db.String(20), default='FREE')
    email = db.Column(db.String(120))

@app.route('/')
def home():
    logged_in = 'user_id' in session
    username = session.get('username', '')
    tier = session.get('tier', 'FREE')
    return render_template('index.html', logged_in=logged_in, username=username, tier=tier, flw_key=FLW_PUB_KEY)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error":"User exists"}), 400
    user = User(username=data['username'], password_hash=generate_password_hash(data['password']))
    db.session.add(user)
    db.session.commit()
    return jsonify({"ok":True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['tier'] = user.tier
        return jsonify({"ok":True, "username":user.username, "tier":user.tier})
    return jsonify({"error":"Wrong password"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/verify-flutterwave', methods=['POST'])
def verify_flw():
    # After Flutterwave payment, upgrade to VIP $10
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user.tier = 'VIP'
        session['tier'] = 'VIP'
        db.session.commit()
        return jsonify({"ok":True, "tier":"VIP"})
    return jsonify({"error":"Not logged in"}), 401

@app.route('/api/signals')
def signals():
    current_tier = session.get('tier', 'FREE')
    all_signals = [
        {"pair":"GBPUSD","action":"SELL","entry":"1.2870","sl":"1.2900","tp":"1.2820","accuracy":"85%","tier":"FREE"},
        {"pair":"XAUUSD","action":"BUY","entry":"2025.50","sl":"2015","tp":"2045","accuracy":"92%","tier":"VIP"},
        {"pair":"EURUSD","action":"BUY","entry":"1.0850","sl":"1.0820","tp":"1.0900","accuracy":"88%","tier":"VVIP"}
    ]
    return jsonify({"signals": all_signals, "user_tier": current_tier})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port) 
