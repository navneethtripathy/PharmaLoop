"""
Batch Prediction Script for Model 1: Surplus Prediction
Loads all medicines from medicine.db and updates surplus probability & status
"""
import sqlite3
import pandas as pd
import joblib
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'saved_models' / 'surplus_model.pkl'
DB_PATH = BASE_DIR.parent / 'databases' / 'medicine.db'

def predict_surplus_batch():
    """Run surplus predictions on all medicines in database"""
    
    # Load model
    try:
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded from {MODEL_PATH}")
    except FileNotFoundError:
        print(f"❌ Model not found at {MODEL_PATH}")
        print("   Please train the model first using: python ml_models/training/trainmodel-1.py")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Connected to database: {DB_PATH}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Load data
    df = pd.read_sql_query("SELECT * FROM medicine_batches", conn)
    print(f"📊 Found {len(df)} medicine records")
    
    # Prepare features
    X = df[[
        "current_stock",
        "avg_monthly_usage",
        "days_to_expiry",
        "hospital_type"
    ]]
    
    # Predict probabilities
    probs = model.predict_proba(X)[:, 1]
    print(f"🔮 Predictions completed")
    
    # Update database
    cursor = conn.cursor()
    updated_count = 0
    
    for med_id, prob in zip(df["id"], probs):
        status = "REDISTRIBUTE" if prob >= 0.6 else "SAFE"
        
        cursor.execute("""
        UPDATE medicine_batches
        SET surplus_probability=?, status=?
        WHERE id=?
        """, (float(prob), status, int(med_id)))
        
        updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated {updated_count} medicine records with surplus predictions")
    
    # Summary statistics
    redistribute_count = sum(1 for p in probs if p >= 0.6)
    safe_count = len(probs) - redistribute_count
    
    print(f"\n📈 Summary:")
    print(f"   REDISTRIBUTE: {redistribute_count} medicines ({redistribute_count/len(probs)*100:.1f}%)")
    print(f"   SAFE: {safe_count} medicines ({safe_count/len(probs)*100:.1f}%)")

if __name__ == "__main__":
    predict_surplus_batch()
