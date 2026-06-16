"""
Model 2: Demand Forecasting Function
Lightweight wrapper for real-time inference in Flask
"""
import joblib
import pandas as pd
from pathlib import Path

# Load model once at module import
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'saved_models' / 'demand_model.pkl'

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Model 2 (Demand) loaded")
except Exception as e:
    print(f"⚠️ Model 2 not loaded: {e}")
    model = None

def run_model2(df):
    """
    Predict medicine demand for clinics
    
    Args:
        df: DataFrame with columns:
            - past_month_usage
            - clinic_population (optional, defaults to 1000)
            - disease_index (optional, defaults to 0.5)
            - season (optional, defaults to 0)
    
    Returns:
        Array of predicted demand quantities
    """
    if model is None:
        print("⚠️ Model not loaded, returning default values")
        return [100] * len(df)
    
    try:
        # Ensure all required columns exist
        if 'clinic_population' not in df.columns:
            df['clinic_population'] = 1000
        if 'disease_index' not in df.columns:
            df['disease_index'] = 0.5
        if 'season' not in df.columns:
            df['season'] = 0
        
        X = df[[
            "past_month_usage",
            "clinic_population",
            "disease_index",
            "season"
        ]]
        
        preds = model.predict(X)
        return preds
    
    except Exception as e:
        print(f"⚠️ Prediction error: {e}")
        return [100] * len(df)
