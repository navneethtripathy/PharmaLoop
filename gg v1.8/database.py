import sqlite3
from flask import g
from config import Config

def get_db():
    """Get database connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize all database tables with correct defaults"""
    db = sqlite3.connect(Config.DATABASE)
    cursor = db.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        organization_type TEXT NOT NULL,
        organization_name TEXT NOT NULL,
        location TEXT NOT NULL,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Medicine inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        batch_number TEXT NOT NULL,
        current_stock INTEGER NOT NULL,
        avg_monthly_usage INTEGER NOT NULL,
        days_to_expiry INTEGER NOT NULL,
        manufacture_date TEXT,
        expiry_date TEXT NOT NULL,
        hospital_type INTEGER DEFAULT 0,
        surplus INTEGER DEFAULT 0,
        surplus_probability REAL DEFAULT 0.0,
        status TEXT DEFAULT 'SAFE',
        location TEXT NOT NULL,
        price_per_unit REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    # ⭐ DEMAND RECORDS - Updated with clinic_population DEFAULT 1500
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demand_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        past_month_usage INTEGER NOT NULL,
        clinic_population INTEGER DEFAULT 1500,
        disease_index REAL DEFAULT 0.5,
        season INTEGER DEFAULT 0,
        urgency_level INTEGER DEFAULT 1,
        pincode TEXT NOT NULL,
        predicted_demand REAL DEFAULT 0.0,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    """)
    
    # Redistribution matches table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS redistribution_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        demand_id INTEGER NOT NULL,
        donor_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        surplus_probability REAL NOT NULL,
        predicted_demand REAL NOT NULL,
        days_to_expiry INTEGER NOT NULL,
        distance_km REAL NOT NULL,
        redistribution_score REAL NOT NULL,
        decision TEXT NOT NULL,
        discount_percent REAL DEFAULT 0.0,
        original_price REAL DEFAULT 0.0,
        discounted_price REAL DEFAULT 0.0,
        transfer_cost REAL DEFAULT 0.0,
        net_profit REAL DEFAULT 0.0,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id),
        FOREIGN KEY (demand_id) REFERENCES demand_records(id),
        FOREIGN KEY (donor_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )
    """)
    
    # Transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        donor_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        original_value REAL NOT NULL,
        discount_applied REAL NOT NULL,
        final_amount REAL NOT NULL,
        status TEXT DEFAULT 'PENDING',
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES redistribution_matches(id),
        FOREIGN KEY (donor_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )
    """)
    
    db.commit()
    db.close()
    print("✅ Database initialized successfully")
    print("   📊 Tables: users, medicines, demand_records, redistribution_matches, transactions")