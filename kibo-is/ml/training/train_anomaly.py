import os
import pickle
from sklearn.ensemble import IsolationForest
from prepare_data import fetch_telemetry_data, generate_mock_data

def train():
    print("Fetching telemetry data...")
    df = fetch_telemetry_data()
    if df.empty:
        print("Database empty or unavailable. Using mock data.")
        df, _, _ = generate_mock_data()
    
    # Simple feature extraction
    X = df[['value']].values
    
    print(f"Training Isolation Forest on {len(X)} records...")
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    
    # Ensure directory exists
    os.makedirs('../core/ml/models', exist_ok=True)
    model_path = '../core/ml/models/anomaly_detector.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
