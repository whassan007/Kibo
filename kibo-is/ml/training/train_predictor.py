import os
import pickle
from statsmodels.tsa.arima.model import ARIMA
from prepare_data import fetch_risk_history, generate_mock_data

def train():
    print("Fetching risk history data...")
    df = fetch_risk_history()
    if df.empty:
        print("Database empty or unavailable. Using mock data.")
        _, df, _ = generate_mock_data()
    
    # Sort and set index
    df = df.sort_values('date')
    df.set_index('date', inplace=True)
    
    print(f"Training ARIMA model on {len(df)} records...")
    # Simple ARIMA (1,1,1) for demonstration
    model = ARIMA(df['risk_score'], order=(1, 1, 1))
    fitted_model = model.fit()
    
    os.makedirs('../core/ml/models', exist_ok=True)
    model_path = '../core/ml/models/risk_predictor.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump(fitted_model, f)
        
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
