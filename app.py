from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'gazelle-secret-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gazelle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    tier = db.Column(db.String(20), default='FREE')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error":"User exists"}), 400
    user = User(username=data['username'], password=generate_password_hash(data['password']))
    db.session.add(user)
    db.session.commit()
    return jsonify({"ok":True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        session['user'] = user.username
        session['tier'] = user.tier
        return jsonify({"ok":True, "tier":user.tier})
    return jsonify({"error":"Wrong login"}), 401

@app.route('/api/signals')
def signals():
    return jsonify([
        {"pair":"GBPUSD","action":"SELL","entry":"1.2870","sl":"1.2900","tp":"1.2820","accuracy":"85%","tier":"FREE"},
        {"pair":"XAUUSD","action":"BUY","entry":"2025.50","sl":"2015","tp":"2045","accuracy":"92%","tier":"VIP"},
        {"pair":"EURUSD","action":"BUY","entry":"1.0850","sl":"1.0820","tp":"1.0900","accuracy":"88%","tier":"VVIP"}
    ])

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port) 
