from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os

class AnomalyDetector:
    def __init__(self, model_path: str = None):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = StandardScaler()
        if model_path and os.path.exists(model_path):
            self.load(model_path)
            
    def _extract_features(self, metrics_data):
        # Expected structure: list of dicts with risk_avg, risk_critical_count, assessment_count, dsar_count
        return [
            [
                d.get('risk_avg', 0.0),
                d.get('risk_critical_count', 0),
                d.get('assessment_count', 0),
                d.get('dsar_count', 0)
            ] for d in metrics_data
        ]
    
    def train(self, historical_metrics):
        features = self._extract_features(historical_metrics)
        scaled = self.scaler.fit_transform(features)
        self.model.fit(scaled)
    
    def predict(self, today_metrics):
        features = self._extract_features([today_metrics])
        scaled = self.scaler.transform(features)
        score = self.model.score_samples(scaled)[0]  # -1 to 1
        is_anomaly = score < -0.5
        return {'score': float(score), 'is_anomaly': bool(is_anomaly)}

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler}, f)

    def load(self, path: str):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
