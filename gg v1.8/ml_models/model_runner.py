"""
ML Models Runner - Integrates all 3 models with Flask
Uses your existing model1.py, model2.py, model3.py
"""

import joblib
import pandas as pd
import os
from pathlib import Path

# Get paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / 'saved_models'

class MLModels:
    """
    Wrapper for PharmaLoop ML Models
    Model 1: Surplus Prediction (Classification) - model1.py
    Model 2: Demand Forecasting (Regression) - model2.py  
    Model 3: Redistribution Scoring (Rule-based) - model3.py
    """
    
    def __init__(self):
        """Load pre-trained models"""
        self.surplus_model = None
        self.demand_model = None
        
        try:
            surplus_path = MODELS_DIR / 'surplus_model.pkl'
            demand_path = MODELS_DIR / 'demand_model.pkl'
            
            if surplus_path.exists():
                self.surplus_model = joblib.load(surplus_path)
                print(f"✅ Surplus model loaded from {surplus_path}")
            else:
                print(f"⚠️ Surplus model not found at {surplus_path}")
            
            if demand_path.exists():
                self.demand_model = joblib.load(demand_path)
                print(f"✅ Demand model loaded from {demand_path}")
            else:
                print(f"⚠️ Demand model not found at {demand_path}")
                
        except Exception as e:
            print(f"⚠️ Error loading ML models: {e}")
    
    def predict_surplus(self, medicines_df):
        """
        Model 1: Surplus Prediction - Uses your model1.py logic
        """
        if self.surplus_model is None:
            return [0.5] * len(medicines_df)
        
        try:
            X = medicines_df[[
                "current_stock",
                "avg_monthly_usage",
                "days_to_expiry",
                "hospital_type"
            ]]
            
            probs = self.surplus_model.predict_proba(X)[:, 1]
            return probs
            
        except Exception as e:
            print(f"⚠️ Error in surplus prediction: {e}")
            return [0.5] * len(medicines_df)
    
    def predict_demand(self, demand_df):
        """
        Model 2: Demand Forecasting - Uses your model2.py logic
        Note: Your model2.py only uses past_month_usage, but we'll use all features
        """
        if self.demand_model is None:
            return [100] * len(demand_df)
        
        try:
            # Use all features for better prediction
            X = demand_df[[
                "past_month_usage",
                "clinic_population",
                "disease_index",
                "season"
            ]]
            
            preds = self.demand_model.predict(X)
            return preds
            
        except Exception as e:
            print(f"⚠️ Error in demand prediction: {e}")
            return [100] * len(demand_df)
    
    def calculate_redistribution_score(self, surplus_prob, demand, expiry, distance=50):
        """
        Model 3: Redistribution Scoring - Uses your model3.py logic
        """
        try:
            demand_score = demand / 500
            expiry_urgency = 1 - (expiry / 180)
            distance_penalty = distance / 200
            
            score = (
                0.4 * surplus_prob +
                0.3 * demand_score +
                0.2 * expiry_urgency -
                0.1 * distance_penalty
            )
            
            decision = "SEND" if score > 0.5 else "HOLD"
            return score, decision
            
        except Exception as e:
            print(f"⚠️ Error in redistribution scoring: {e}")
            return 0.5, "HOLD"
    
    def calculate_discount(self, days_to_expiry, surplus_prob, distance_km):
        """
        Calculate dynamic discount based on urgency
        """
        try:
            if days_to_expiry <= 15:
                expiry_discount = 40
            elif days_to_expiry <= 30:
                expiry_discount = 30
            elif days_to_expiry <= 60:
                expiry_discount = 20
            else:
                expiry_discount = 10
            
            surplus_discount = surplus_prob * 15
            distance_penalty = (distance_km / 200) * 5
            
            total_discount = expiry_discount + surplus_discount - distance_penalty
            total_discount = max(10, min(total_discount, 40))
            
            return round(total_discount, 2)
            
        except Exception as e:
            print(f"⚠️ Error calculating discount: {e}")
            return 15.0
    
    def calculate_profitability(self, quantity, price_per_unit, discount_percent, 
                               distance_km, days_to_expiry):
        """
        Calculate net profitability of redistribution
        """
        try:
            original_value = quantity * price_per_unit
            discounted_value = original_value * (1 - discount_percent / 100)
            
            DISTANCE_COST_PER_KM = 5
            HANDLING_COST = 50
            transfer_cost = (distance_km * DISTANCE_COST_PER_KM) + HANDLING_COST
            
            wastage_risk = 1.0 if days_to_expiry < 30 else 0.5
            potential_loss = original_value * wastage_risk
            
            net_profit = discounted_value + (potential_loss * 0.5) - transfer_cost
            
            return {
                'original_value': round(original_value, 2),
                'discounted_value': round(discounted_value, 2),
                'transfer_cost': round(transfer_cost, 2),
                'potential_loss_avoided': round(potential_loss * 0.5, 2),
                'net_profit': round(net_profit, 2),
                'is_profitable': net_profit > 0
            }
            
        except Exception as e:
            print(f"⚠️ Error calculating profitability: {e}")
            return {
                'original_value': 0,
                'discounted_value': 0,
                'transfer_cost': 0,
                'potential_loss_avoided': 0,
                'net_profit': 0,
                'is_profitable': False
            }

# Global instance
ml_models = MLModels()
