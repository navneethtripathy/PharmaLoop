"""
Model 1: Surplus Prediction Function
Lightweight wrapper for real-time inference in Flask
"""
import joblib
import pandas as pd
from pathlib import Path

# Load model once at module import
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'saved_models' / 'surplus_model.pkl'

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Model 1 (Surplus) loaded")
except Exception as e:
    print(f"⚠️ Model 1 not loaded: {e}")
    model = None

def run_model1(df):
    """
    Predict surplus probability for medicines
    
    Args:
        df: DataFrame with columns:
            - current_stock
            - avg_monthly_usage
            - days_to_expiry
            - hospital_type
    
    Returns:
        Array of surplus probabilities (0-1)
    """
    if model is None:
        print("⚠️ Model not loaded, returning default values")
        return [0.5] * len(df)
    
    try:
        X = df[[
            "current_stock",
            "avg_monthly_usage",
            "days_to_expiry",
            "hospital_type"
        ]]
        
        probs = model.predict_proba(X)[:, 1]
        return probs
    
    except Exception as e:
        print(f"⚠️ Prediction error: {e}")
        return [0.5] * len(df)
