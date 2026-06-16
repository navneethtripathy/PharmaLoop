"""
Train Model 2: Demand Forecasting (Regression)
"""
import sqlite3
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR.parent / 'databases' / 'demand.db'
MODEL_PATH = BASE_DIR / 'saved_models' / 'demand_model.pkl'

MODEL_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM clinic_demand", conn)

X = df[[
    "past_month_usage",
    "clinic_population",
    "disease_index",
    "season"
]]

y = df["next_month_demand"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

joblib.dump(model, MODEL_PATH)

conn.close()

print(f"✅ Demand model trained & saved to {MODEL_PATH}")
print(f"   Training R² score: {model.score(X_train, y_train):.2%}")
print(f"   Testing R² score: {model.score(X_test, y_test):.2%}")
