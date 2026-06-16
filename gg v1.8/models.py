import joblib
import pandas as pd
import math
from config import Config

class MLModels:
    def __init__(self):
        try:
            self.surplus_model = joblib.load("surplus_model.pkl")
            self.demand_model = joblib.load("demand_model.pkl")
            print("✅ ML Models loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
            self.surplus_model = None
            self.demand_model = None
    
    def predict_surplus(self, medicines_df):
        """Model 1: Surplus Prediction"""
        if self.surplus_model is None:
            return [0.5] * len(medicines_df)
        
        X = medicines_df[[
            "current_stock",
            "avg_monthly_usage",
            "days_to_expiry",
            "hospital_type"
        ]]
        
        probs = self.surplus_model.predict_proba(X)[:, 1]
        return probs
    
    def predict_demand(self, demand_df):
        """Model 2: Demand Forecasting"""
        if self.demand_model is None:
            return [100] * len(demand_df)
        
        X = demand_df[[
            "past_month_usage",
            "clinic_population",
            "disease_index",
            "season"
        ]]
        
        preds = self.demand_model.predict(X)
        return preds
    
    def calculate_redistribution_score(self, surplus_prob, demand, expiry, distance):
        """Model 3: Redistribution Scoring"""
        demand_score = min(demand / 500, 1.0)
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
    
    def calculate_discount(self, days_to_expiry, surplus_prob, distance_km):
        """Calculate dynamic discount based on urgency and logistics"""
        # Base discount on expiry urgency
        if days_to_expiry <= 15:
            expiry_discount = 40
        elif days_to_expiry <= 30:
            expiry_discount = 30
        elif days_to_expiry <= 60:
            expiry_discount = 20
        else:
            expiry_discount = 10
        
        # Additional discount for high surplus probability
        surplus_discount = surplus_prob * 15
        
        # Reduce discount for long distances (to maintain profitability)
        distance_penalty = (distance_km / 200) * 5
        
        total_discount = expiry_discount + surplus_discount - distance_penalty
        total_discount = max(Config.MIN_DISCOUNT_PERCENT, 
                            min(total_discount, Config.MAX_DISCOUNT_PERCENT))
        
        return round(total_discount, 2)
    
    def calculate_profitability(self, quantity, price_per_unit, discount_percent, 
                               distance_km, days_to_expiry):
        """Calculate net profitability of redistribution"""
        original_value = quantity * price_per_unit
        discounted_value = original_value * (1 - discount_percent / 100)
        
        # Transfer costs
        transfer_cost = (distance_km * Config.DISTANCE_COST_PER_KM + 
                        Config.HANDLING_COST)
        
        # Wastage cost if not redistributed
        wastage_risk = 1.0 if days_to_expiry < 30 else 0.5
        potential_loss = original_value * wastage_risk
        
        # Net profit = Revenue from sale + Avoided loss - Transfer cost
        net_profit = discounted_value + (potential_loss * 0.5) - transfer_cost
        
        return {
            'original_value': round(original_value, 2),
            'discounted_value': round(discounted_value, 2),
            'transfer_cost': round(transfer_cost, 2),
            'net_profit': round(net_profit, 2),
            'is_profitable': net_profit > 0
        }

# Global instance
ml_models = MLModels()
