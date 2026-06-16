"""
Test script to verify ML pipeline
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def test_pipeline():
    print("=" * 60)
    print("🧪 Testing PharmaLoop ML Pipeline")
    print("=" * 60)
    
    # Test 1: Import model functions
    print("\n1️⃣ Testing model imports...")
    try:
        from ml_models.models.model1 import run_model1
        from ml_models.models.model2 import run_model2
        from ml_models.models.model3 import run_model3
        print("✅ All model functions imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test 2: Test Model 1
    print("\n2️⃣ Testing Model 1 (Surplus Prediction)...")
    try:
        import pandas as pd
        test_df = pd.DataFrame([{
            'current_stock': 500,
            'avg_monthly_usage': 100,
            'days_to_expiry': 30,
            'hospital_type': 1
        }])
        result = run_model1(test_df)
        print(f"✅ Model 1 result: {result[0]:.3f} surplus probability")
    except Exception as e:
        print(f"❌ Model 1 failed: {e}")
    
    # Test 3: Test Model 2
    print("\n3️⃣ Testing Model 2 (Demand Forecasting)...")
    try:
        test_df = pd.DataFrame([{
            'past_month_usage': 200,
            'clinic_population': 5000,
            'disease_index': 0.7,
            'season': 1
        }])
        result = run_model2(test_df)
        print(f"✅ Model 2 result: {result[0]:.2f} predicted demand")
    except Exception as e:
        print(f"❌ Model 2 failed: {e}")
    
    # Test 4: Test Model 3
    print("\n4️⃣ Testing Model 3 (Redistribution Scoring)...")
    try:
        score, decision = run_model3(0.8, 300, 25, 50)
        print(f"✅ Model 3 result: Score={score:.3f}, Decision={decision}")
    except Exception as e:
        print(f"❌ Model 3 failed: {e}")
    
    # Test 5: Test integrated runner
    print("\n5️⃣ Testing integrated model runner...")
    try:
        from ml_models.model_runner import ml_models
        print("✅ Model runner loaded successfully")
    except Exception as e:
        print(f"❌ Model runner failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ML Pipeline testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()
