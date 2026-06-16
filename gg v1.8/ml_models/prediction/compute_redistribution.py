"""
Batch Scoring Script for Model 3: Redistribution Scoring
Loads redistribution scenarios from routes.db and computes scores & decisions
"""
import sqlite3
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR.parent / 'databases' / 'routes.db'

def compute_redistribution_scores():
    """Compute redistribution scores for all scenarios"""
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Connected to database: {DB_PATH}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Load data
    df = pd.read_sql_query("SELECT * FROM redistribution", conn)
    print(f"📊 Found {len(df)} redistribution scenarios")
    
    # Normalize features
    df["demand_score"] = df["predicted_demand"] / df["predicted_demand"].max()
    df["expiry_urgency"] = 1 - (df["days_to_expiry"] / 180)
    df["distance_penalty"] = df["distance_km"] / 200
    
    # Calculate redistribution score using Model 3 formula
    df["redistribution_score"] = (
        0.4 * df["surplus_probability"] +
        0.3 * df["demand_score"] +
        0.2 * df["expiry_urgency"] -
        0.1 * df["distance_penalty"]
    )
    
    print(f"🔮 Redistribution scores computed")
    
    # Update database
    cursor = conn.cursor()
    updated_count = 0
    
    for _, row in df.iterrows():
        decision = "SEND" if row["redistribution_score"] > 0.5 else "HOLD"
        
        cursor.execute("""
        UPDATE redistribution
        SET redistribution_score=?, decision=?
        WHERE id=?
        """, (float(row["redistribution_score"]), decision, int(row["id"])))
        
        updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated {updated_count} redistribution scenarios")
    
    # Summary statistics
    send_count = sum(1 for score in df["redistribution_score"] if score > 0.5)
    hold_count = len(df) - send_count
    avg_score = df["redistribution_score"].mean()
    
    print(f"\n📈 Redistribution Summary:")
    print(f"   SEND: {send_count} scenarios ({send_count/len(df)*100:.1f}%)")
    print(f"   HOLD: {hold_count} scenarios ({hold_count/len(df)*100:.1f}%)")
    print(f"   Average Score: {avg_score:.3f}")

if __name__ == "__main__":
    compute_redistribution_scores()
