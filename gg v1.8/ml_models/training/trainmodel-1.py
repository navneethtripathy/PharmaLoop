"""
Train Model 1: Surplus Prediction (Classification)
"""
import sqlite3
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR.parent / 'databases' / 'medicine.db'
MODEL_PATH = BASE_DIR / 'saved_models' / 'surplus_model.pkl'

MODEL_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM medicine_batches", conn)

X = df[[
    "current_stock",
    "avg_monthly_usage",
    "days_to_expiry",
    "hospital_type"
]]

y = df["surplus"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

joblib.dump(model, MODEL_PATH)

conn.close()

print(f"✅ Model trained & saved to {MODEL_PATH}")
print(f"   Training accuracy: {model.score(X_train, y_train):.2%}")
print(f"   Testing accuracy: {model.score(X_test, y_test):.2%}")
