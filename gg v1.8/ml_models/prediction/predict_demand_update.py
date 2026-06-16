"""
Batch Prediction Script for Model 2: Demand Forecasting
Loads all demand records from demand.db and updates predicted_demand
"""
import sqlite3
import pandas as pd
import joblib
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'saved_models' / 'demand_model.pkl'
DB_PATH = BASE_DIR.parent / 'databases' / 'demand.db'

def predict_demand_batch():
    """Run demand predictions on all records in database"""
    
    # Load model
    try:
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded from {MODEL_PATH}")
    except FileNotFoundError:
        print(f"❌ Model not found at {MODEL_PATH}")
        print("   Please train the model first using: python ml_models/training/train_demand_model.py")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Connected to database: {DB_PATH}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Load data
    df = pd.read_sql_query("SELECT * FROM clinic_demand", conn)
    print(f"📊 Found {len(df)} demand records")
    
    # Prepare features
    X = df[[
        "past_month_usage",
        "clinic_population",
        "disease_index",
        "season"
    ]]
    
    # Predict demand
    preds = model.predict(X)
    print(f"🔮 Predictions completed")
    
    # Update database
    cursor = conn.cursor()
    updated_count = 0
    
    for demand_id, pred in zip(df["id"], preds):
        cursor.execute("""
        UPDATE clinic_demand
        SET predicted_demand=?
        WHERE id=?
        """, (float(pred), int(demand_id)))
        
        updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated {updated_count} demand records with predictions")
    
    # Summary statistics
    avg_predicted = preds.mean()
    min_predicted = preds.min()
    max_predicted = preds.max()
    
    print(f"\n📈 Prediction Summary:")
    print(f"   Average Predicted Demand: {avg_predicted:.2f} units")
    print(f"   Min Predicted Demand: {min_predicted:.2f} units")
    print(f"   Max Predicted Demand: {max_predicted:.2f} units")

if __name__ == "__main__":
    predict_demand_batch()
