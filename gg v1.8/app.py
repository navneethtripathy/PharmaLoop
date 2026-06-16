from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

from ml_models.model_runner import ml_models
from config import Config
from database import get_db, close_db, init_db

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    close_db()

# ================= AUTH =================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token missing'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated

# ================= PINCODE DISTANCE =================

def calculate_distance(pin1, pin2):
    try:
        p1 = int(pin1)
        p2 = int(pin2)

        # 10 pincode diff ≈ 1 km
        distance = abs(p1 - p2) / 10

        return min(distance, 150)
    except:
        return 50

# ================= HTML ROUTES =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/redistribution-view')
def redistribution_view():
    return render_template('redistribution.html')

# ================= REGISTER =================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    hashed_password = generate_password_hash(data['password'])

    cursor.execute("""
    INSERT INTO users (
        email, password, name,
        organization_type, organization_name,
        location, pincode, phone
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['email'],
        hashed_password,
        data['name'],
        data['organization_type'],
        data['organization_name'],
        data['location'],
        data['pincode'],
        data.get('phone', '')
    ))

    db.commit()
    return jsonify({'message': 'Registration successful'}), 201

# ================= LOGIN =================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE email = ?",
        (data['email'],)
    ).fetchone()

    if user and check_password_hash(user['password'], data['password']):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token, 'user': dict(user)})

    return jsonify({'error': 'Invalid credentials'}), 401

# ================= MEDICINES =================

@app.route('/api/medicines', methods=['POST'])
@token_required
def add_medicine(current_user_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()

    user = db.execute("SELECT location FROM users WHERE id=?",
                      (current_user_id,)).fetchone()

    cursor.execute("""
    INSERT INTO medicines (
        user_id, medicine_name, batch_number, current_stock,
        avg_monthly_usage, days_to_expiry, expiry_date,
        hospital_type, location, price_per_unit
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user_id,
        data['medicine_name'],
        data['batch_number'],
        data['current_stock'],
        data['avg_monthly_usage'],
        data['days_to_expiry'],
        data['expiry_date'],
        data.get('hospital_type', 0),
        user['location'],
        data.get('price_per_unit', 100)
    ))

    db.commit()
    med_id = cursor.lastrowid
    run_surplus_prediction_single(med_id)

    return jsonify({'message': 'Medicine added'}), 201

@app.route('/api/medicines', methods=['GET'])
@token_required
def get_medicines(current_user_id):
    db = get_db()

    meds = db.execute("""
    SELECT *
    FROM medicines
    WHERE user_id=?
    ORDER BY id DESC
    """, (current_user_id,)).fetchall()

    return jsonify([dict(m) for m in meds])


# ================= DEMAND =================

@app.route('/api/demand', methods=['POST'])
@token_required
def add_demand(current_user_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()

    # ---------- Validate input ----------
    if not data.get('medicine_name') or not data.get('past_month_usage'):
        return jsonify({'error': 'Missing required fields'}), 400

    # ---------- Get user pincode ----------
    user = db.execute(
        "SELECT pincode FROM users WHERE id=?",
        (current_user_id,)
    ).fetchone()

    if not user or not user['pincode']:
        return jsonify({'error': 'User pincode not found'}), 400

    # ---------- Map urgency ----------
    urgency_map = {
        "low": 0,
        "medium": 1,
        "high": 2
    }

    urgency_level = urgency_map.get(
        data.get("urgency_level", "medium"),
        1
    )

    # ---------- Insert demand ----------
    cursor.execute("""
    INSERT INTO demand_records (
        user_id,
        medicine_name,
        past_month_usage,
        clinic_population,
        disease_index,
        season,
        urgency_level,
        pincode,
        predicted_demand
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user_id,
        data['medicine_name'].strip(),
        int(data['past_month_usage']),
        1500,        # default population
        0.5,         # default disease index
        0,           # default season
        urgency_level,
        user['pincode'],
        0            # will be predicted by ML later
    ))

    db.commit()

    return jsonify({
        'message': 'Demand added successfully',
        'clinic_population': 1500
    }), 201




# ================= REDISTRIBUTION =================

@app.route('/api/run-redistribution', methods=['POST'])
@token_required
def run_redistribution(current_user_id):
    db = get_db()
    cursor = db.cursor()

    surplus = db.execute("""
    SELECT m.*, u.pincode as donor_pincode, u.id as donor_id
    FROM medicines m
    JOIN users u ON m.user_id=u.id
    WHERE m.status='REDISTRIBUTE'
    """).fetchall()

    demands = db.execute("""
    SELECT d.*, u.pincode as receiver_pincode, u.id as receiver_id
    FROM demand_records d
    JOIN users u ON d.user_id=u.id
    """).fetchall()

    matches = 0

    for med in surplus:
        for demand in demands:

            if med['donor_id'] == demand['receiver_id']:
                continue

            med_name = med['medicine_name'].split("_")[0].lower()
            demand_name = demand['medicine_name'].lower()

            if med_name != demand_name:
                continue

            distance = calculate_distance(
                med['donor_pincode'],
                demand['receiver_pincode']
            )

            score, decision = ml_models.calculate_redistribution_score(
                med['surplus_probability'],
                demand['predicted_demand'],
                med['days_to_expiry'],
                distance
            )

            if decision != "SEND":
                continue

            quantity = min(med['current_stock'], demand['predicted_demand'])

            profitability = ml_models.calculate_profitability(
                quantity,
                med['price_per_unit'],
                20,  # avg discount
                distance,
                med['days_to_expiry']
            )

            cursor.execute("""
            INSERT INTO redistribution_matches (
                medicine_name, quantity,
                redistribution_score, decision,
                distance_km, net_profit
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                med['medicine_name'],
                quantity,
                score,
                "SEND",
                distance,
                profitability['net_profit']
            ))

            matches += 1

    db.commit()
    return jsonify({'matches_found': matches})

# ================= ML FUNCTIONS =================

def run_surplus_prediction_single(med_id):
    db = get_db()
    med = db.execute("SELECT * FROM medicines WHERE id=?",
                     (med_id,)).fetchone()

    df = pd.DataFrame([{
        "current_stock": med['current_stock'],
        "avg_monthly_usage": med['avg_monthly_usage'],
        "days_to_expiry": med['days_to_expiry'],
        "hospital_type": med['hospital_type']
    }])

    prob = ml_models.predict_surplus(df)[0]
    status = "REDISTRIBUTE" if prob >= 0.6 else "SAFE"

    db.execute("""
    UPDATE medicines
    SET surplus_probability=?, status=?
    WHERE id=?
    """, (float(prob), status, med_id))

    db.commit()

# ================= RUN =================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=False)