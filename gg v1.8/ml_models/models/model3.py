"""
Model 3: Redistribution Scoring Function
Rule-based scoring system for redistribution decisions
"""

def run_model3(surplus_prob, demand, expiry, distance=50):
    """
    Calculate redistribution score and decision
    
    Args:
        surplus_prob: Surplus probability (0-1)
        demand: Predicted demand quantity
        expiry: Days to expiry
        distance: Distance in kilometers (default: 50)
    
    Returns:
        tuple: (score, decision)
            - score: Redistribution score (0-1)
            - decision: "SEND" or "HOLD"
    """
    try:
        # Normalize features
        demand_score = demand / 500
        expiry_urgency = 1 - (expiry / 180)
        distance_penalty = distance / 200
        
        # Weighted scoring formula
        score = (
            0.4 * surplus_prob +      # 40% weight on surplus
            0.3 * demand_score +       # 30% weight on demand
            0.2 * expiry_urgency -     # 20% weight on urgency
            0.1 * distance_penalty     # 10% penalty for distance
        )
        
        # Decision threshold
        decision = "SEND" if score > 0.5 else "HOLD"
        
        return score, decision
    
    except Exception as e:
        print(f"⚠️ Scoring error: {e}")
        return 0.5, "HOLD"


def calculate_discount(days_to_expiry, surplus_prob, distance_km):
    """
    Calculate dynamic discount percentage
    
    Args:
        days_to_expiry: Days until medicine expires
        surplus_prob: Surplus probability (0-1)
        distance_km: Distance in kilometers
    
    Returns:
        Discount percentage (10-40%)
    """
    try:
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
        
        # Reduce discount for long distances (maintain profitability)
        distance_penalty = (distance_km / 200) * 5
        
        total_discount = expiry_discount + surplus_discount - distance_penalty
        
        # Clamp between 10% and 40%
        total_discount = max(10, min(total_discount, 40))
        
        return round(total_discount, 2)
    
    except Exception as e:
        print(f"⚠️ Discount calculation error: {e}")
        return 15.0
