import os
import pickle
from sentence_transformers import SentenceTransformer
from prepare_data import fetch_historical_controls, generate_mock_data

def train():
    print("Fetching historical controls data...")
    df = fetch_historical_controls()
    if df.empty:
        print("Database empty or unavailable. Using mock data.")
        _, _, df = generate_mock_data()
    
    print(f"Generating embeddings for {len(df)} controls...")
    # Use a small, fast model for CPU inference
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Combine title and description for rich semantic embedding
    texts = (df['title'] + ". " + df['description']).tolist()
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Store both the model name and the computed embeddings/metadata
    recommender_data = {
        'model_name': 'all-MiniLM-L6-v2',
        'controls': df.to_dict('records'),
        'embeddings': embeddings
    }
    
    os.makedirs('../core/ml/models', exist_ok=True)
    model_path = '../core/ml/models/control_recommender.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump(recommender_data, f)
        
    print(f"Model and embeddings saved to {model_path}")

if __name__ == "__main__":
    train()
